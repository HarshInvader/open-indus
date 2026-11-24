"""Tablet picture x text, whole objects, class level (prereg docs/prereg/tablet_pic_text.md).
Run from the repo root:
  .venv/bin/python -I experiments/tablet_pic_text/run.py rows   # label/text-only counts (no association statistic)
  .venv/bin/python -I experiments/tablet_pic_text/run.py gate   # label reliability gate (labels only)
  .venv/bin/python -I experiments/tablet_pic_text/run.py kill   # plants on block-permuted labels + false alarms -> kill.json
  .venv/bin/python -I experiments/tablet_pic_text/run.py main   # refuses unless kill.json band is 'powered'

Code-level definitions fixed with this file's seal:
- side text = the side's signs with '|' and '#' removed; segments = runs split at '#' (after removing '|').
- object text = tuple of side texts in side order; flattened sequence = sides concatenated.
- a broken object joins a text type if every segment of every side is a contiguous run inside some side of
  exactly one complete text type of the same site and ICIT type.
- families: union-find over text types on the flattened sequence (identical; edit distance <= 1 with both >= 4;
  a >= 4-sign flattened text contiguous inside the other).
- eligible classes come from the gate result (GATE below): a class failing kappa >= 0.6 is merged into 'rest'.
- with one eligible class the model is binary (class vs rest); the AUC is that class's one-vs-rest AUC.
"""
import csv, json, os, sys, warnings
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path
import numpy as np

warnings.filterwarnings("ignore")
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from corpus.load import icit_texts  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.model_selection import StratifiedGroupKFold  # noqa: E402
from sklearn.metrics import roc_auc_score  # noqa: E402

TYPE = "TAB:B"
MAP = {}
for c, codes in {"bovine": "Bull1 Bull1:I Bull1:S Bull1:U Bull Bull2 Gaur Zebu",
                 "figure": "Scene Anth",
                 "geometric": "Cros Xcrs Maze Tri4 Xhch Crs T Swas T-A-T Box Strokes",
                 "other_animal": "Rhin Goat Goat:4 Goat:6 Elep Bird",
                 "aquatic": "Fish Turt", "plant": "Pipal"}.items():
    for k in codes.split(): MAP[k] = c
MIN_ROWS, MIN_VOC, KAPPA_BAR = 15, 5, 0.6
CV_SEED, NULL_SEED, PLANT_SEED, FA_A_SEED, FA_B_SEED = 20261124, 1, 3, 4, 5
NNULL, NDRAW, NFA, BAR_P = 1000, 40, 400, 0.025
DELTAS = (0.05, 0.10, 0.20, 0.40)
GATE_FILE = HERE / "gate.json"


# ------------------------------------------------------------------ rows
def strip(seq): return tuple(s for s in seq if s not in ("|", "#"))


def segs(seq):
    out, cur = [], []
    for s in seq:
        if s == "|": continue
        if s == "#":
            if cur: out.append(tuple(cur))
            cur = []
        else: cur.append(s)
    if cur: out.append(tuple(cur))
    return out


def contig(a, b):
    n = len(a); return any(b[i:i + n] == a for i in range(len(b) - n + 1)) if n <= len(b) else False


def objects():
    by = defaultdict(list)
    for r in icit_texts():
        if r["type"] != TYPE or r["symbol"] not in MAP: continue
        if not strip(r["seq"]): continue                       # empty-sign record dropped
        n, side = r["id"].split(".")
        by[n].append((int(side), r))
    out = []
    for n, rs in by.items():
        rs.sort(key=lambda x: x[0]); r0 = rs[0][1]
        out.append(dict(n=n, site=r0["site"], material=r0["material"], cls=MAP[r0["symbol"]],
                        text=tuple(strip(r["seq"]) for _, r in rs),
                        segs=[segs(r["seq"]) for _, r in rs],
                        complete=all(r["complete"] and "#" not in r["seq"] for _, r in rs)))
    return out


def rows():
    obs = objects()
    types = defaultdict(list)                                  # (site, text) -> objects
    for o in obs:
        if o["complete"]: types[(o["site"], o["text"])].append(o)
    dropped = joined = 0
    for o in obs:
        if o["complete"]: continue
        hits = [k for k in types if k[0] == o["site"] and
                all(any(contig(sg, side) for side in k[1]) for side_segs in o["segs"] for sg in side_segs)]
        if len(hits) == 1: types[hits[0]].append(o); joined += 1
        else: dropped += 1
    R = sorted({(site, text, o["cls"]) for (site, text), os_ in types.items() for o in os_})
    meta = {}
    for (site, text), os_ in types.items():
        for o in os_:
            meta.setdefault((site, text, o["cls"]), []).append(o)
    rows_ = [dict(site=s, text=t, cls=c, flat=tuple(x for side in t for x in side), nsides=len(t),
                  material=Counter(o["material"] for o in meta[(s, t, c)]).most_common(1)[0][0]) for s, t, c in R]
    return rows_, dict(objects=len(obs), complete=sum(o["complete"] for o in obs), broken_dropped=dropped,
                       broken_joined=joined, types=len(types))


def ed1(a, b):
    if abs(len(a) - len(b)) > 1: return False
    if len(a) == len(b): return sum(x != y for x, y in zip(a, b)) <= 1
    if len(a) > len(b): a, b = b, a
    return any(b[:i] + b[i + 1:] == a for i in range(len(b)))


def families(R):
    par = list(range(len(R)))
    def f(i):
        while par[i] != i: par[i] = par[par[i]]; i = par[i]
        return i
    for i in range(len(R)):
        for j in range(i + 1, len(R)):
            a, b = R[i]["flat"], R[j]["flat"]
            if a == b or (min(len(a), len(b)) >= 4 and (ed1(a, b) or contig(a, b) or contig(b, a))):
                par[f(i)] = f(j)
    roots = {}
    return np.array([roots.setdefault(f(i), len(roots)) for i in range(len(R))])


def lenbin(n): return "1-2" if n <= 2 else ("3-4" if n <= 4 else "5+")


def strata(R, extra=None):
    sc = Counter(r["site"] for r in R)
    site = [r["site"] if sc[r["site"]] >= 5 else "other" for r in R]
    return np.array([f"{s}|{lenbin(len(r['flat']))}" + (f"|{extra(r)}" if extra else "") for s, r in zip(site, R)])


def features(R):
    items = []
    for r in R:
        it = {f"s:{g}" for g in r["flat"]}
        for side in r["text"]:
            it.add(f"i:{side[0]}"); it.add(f"f:{side[-1]}")
            it |= {f"b:{a}_{b}" for a, b in zip(side, side[1:])}
        items.append(it)
    c = Counter(x for it in items for x in it)
    voc = sorted(x for x, n in c.items() if n >= MIN_VOC)
    return np.array([[x in it for x in voc] for it in items], dtype=float), voc, [set(r["flat"]) for r in R]


# ------------------------------------------------------------------ statistic
def oof_auc(X, y, groups, elig):
    """Pooled out-of-fold one-vs-rest AUC, macro over eligible classes. y: array of class names."""
    cv = StratifiedGroupKFold(5, shuffle=True, random_state=CV_SEED)
    classes = sorted(set(y)); P = np.zeros((len(y), len(classes)))
    for tr, te in cv.split(X, y, groups):
        if len(set(y[tr])) < len(classes): return np.nan
        m = LogisticRegression(C=0.3, max_iter=2000, class_weight="balanced").fit(X[tr], y[tr])
        P[te] = m.predict_proba(X[te])
    return float(np.mean([roc_auc_score(y == c, P[:, classes.index(c)]) for c in elig]))


def strat_perm(y, st, rng):
    yy = y.copy()
    for s in np.unique(st):
        idx = np.where(st == s)[0]; yy[idx] = y[rng.permutation(idx)]
    return yy


def block_perm(y, fam, st, rng):
    """Swap whole family label vectors among same-size families within the stratum of the family's first row."""
    yy = y.copy(); members = defaultdict(list)
    for i, f in enumerate(fam): members[f].append(i)       # rows are ordered by site, then text
    grp = defaultdict(list)
    for f, idx in members.items(): grp[(len(idx), st[idx[0]])].append(f)
    for fs in grp.values():
        perm = rng.permutation(len(fs))
        for f, g in zip(fs, [fs[k] for k in perm]):
            yy[members[f]] = y[members[g]]
    return yy


def pval(obs, null):
    null = np.asarray(null); return float((1 + (null >= obs).sum()) / (1 + len(null)))


# ------------------------------------------------------------------ shared state
S = {}


def setup():
    R, info = rows()
    gate = json.load(open(GATE_FILE))                          # required: run `gate` first
    lab = np.array([r["cls"] for r in R])
    cnt = Counter(lab)
    elig = sorted(c for c, n in cnt.items() if n >= MIN_ROWS and c not in gate["failed"])
    y = np.array([c if c in elig else "rest" for c in lab])
    X, voc, sets = features(R)
    st = strata(R); fam = families(R)
    doc = Counter(g for s in sets for g in s)
    S.update(R=R, info=info, y=y, X=X, voc=voc, sets=sets, st=st, fam=fam, elig=elig,
             tie=sorted(g for g, n in doc.items() if n >= MIN_VOC), cnt=cnt)


def null_job(i):
    rng = np.random.default_rng([NULL_SEED, i])
    return oof_auc(S["X"], strat_perm(S["y"], S["st"], rng), S["fam"], S["elig"])


def plant(y, A, g, delta, rng):
    isA = y == A; nA = int(isA.sum()); has = np.array([g in s for s in S["sets"]])
    r0 = (has & isA).sum() / nA
    need = int(np.ceil(min(1.0, r0 + delta) * nA)) - int((has & isA).sum())
    yy = y.copy(); ok = 0; pool = defaultdict(list)
    for i in rng.permutation(len(y)):
        if not isA[i] and has[i]: pool[S["st"][i]].append(i)
    for i in rng.permutation(len(y)):
        if ok >= need: break
        if isA[i] and not has[i] and pool[S["st"][i]]:
            j = pool[S["st"][i]].pop(); yy[i], yy[j] = yy[j], yy[i]; ok += 1
    return (yy, float(r0)) if ok >= need else (None, float(r0))


def plant_job(a):
    A, delta, d = a
    rng = np.random.default_rng([PLANT_SEED, S["elig"].index(A), int(round(delta * 100)), d])
    y0 = block_perm(S["y"], S["fam"], S["st"], rng)
    g = S["tie"][rng.integers(len(S["tie"]))]
    yy, r0 = plant(y0, A, g, delta, rng)
    if yy is None: return dict(cls=A, delta=delta, d=d, sign=g, natural=r0, feasible=False)
    has = np.array([g in s for s in S["sets"]]); isA = yy == A
    realised = float((has & isA).sum() / isA.sum()) - r0      # ceil overshoot is recorded, not hidden
    return dict(cls=A, delta=delta, d=d, sign=g, natural=r0, feasible=True, realised=realised,
                auc=oof_auc(S["X"], yy, S["fam"], S["elig"]))


def fa_job(a):
    kind, i = a
    rng = np.random.default_rng([FA_A_SEED if kind == "A" else FA_B_SEED, i])
    yy = strat_perm(S["y"], S["st"], rng) if kind == "A" else block_perm(S["y"], S["fam"], S["st"], rng)
    return kind, oof_auc(S["X"], yy, S["fam"], S["elig"])


# ------------------------------------------------------------------ modes
def mode_rows():
    setup(); R = S["R"]
    sz = Counter(Counter(S["fam"]).values())
    print(json.dumps(dict(S["info"], rows=len(R), families=int(S["fam"].max() + 1), family_sizes=dict(sz),
                          per_class=dict(S["cnt"]), eligible=S["elig"], vocab=len(S["voc"]),
                          vocab_kinds=dict(Counter(v[0] for v in S["voc"])), tie_signs=len(S["tie"]),
                          strata=dict(Counter(S["st"])), sides=dict(Counter(r["nsides"] for r in R))), indent=1))


def mode_gate():
    """figure <-> scene_text consensus (scene or human); bovine has no scene_text code (ungated)."""
    codes = {r["cisi"]: r for r in csv.DictReader(open(ROOT / "experiments/scene_text/scene_codes_objects.csv"))}
    obj = {}
    for r in icit_texts():
        if r["type"] == TYPE and r["symbol"] in MAP: obj.setdefault(r["id"].split(".")[0], (r["cisi"], MAP[r["symbol"]]))
    t = Counter()
    for cisi, c in obj.values():
        if cisi in codes:
            row = codes[cisi]
            t[(c == "figure", row["scene_cons"] == "1" or row["human_cons"] == "1")] += 1
    n = sum(t.values()); a, b, c_, d = t[(True, True)], t[(True, False)], t[(False, True)], t[(False, False)]
    po = (a + d) / n; pe = ((a + b) * (a + c_) + (c_ + d) * (b + d)) / n / n
    k = (po - pe) / (1 - pe)
    out = dict(n=n, both=a, icit_only=b, raters_only=c_, neither=d, kappa_figure=round(k, 3),
               gated=["figure"], ungated=sorted(set(MAP.values()) - {"figure"}),
               failed=["figure"] if k < KAPPA_BAR else [])        # only figure has a scene_text counterpart
    json.dump(out, open(GATE_FILE, "w"), indent=1); print(out)


def mode_kill():
    nw = int(os.environ.get("NWORK", "4"))
    setup()
    out = dict(eligible=[str(c) for c in S["elig"]], rows=len(S["R"]), per_class={str(k): int(v) for k, v in Counter(S["y"]).items()})
    with Pool(nw, initializer=setup) as P:
        null = P.map(null_job, range(NNULL), chunksize=20)
        null = [x for x in null if not np.isnan(x)]
        out["null"] = dict(n=len(null), mean=float(np.mean(null)), p99=float(np.quantile(null, 0.99)),
                           crit=float(np.quantile(null, 1 - BAR_P)))
        print("null", out["null"], flush=True)
        jobs = [(A, dl, d) for A in S["elig"] for dl in DELTAS for d in range(NDRAW)]
        res = P.map(plant_job, jobs, chunksize=4)
        rungs = {}
        for A in S["elig"]:
            A = str(A); rungs[A] = {}
            for dl in DELTAS:
                rr = [r for r in res if r["cls"] == A and r["delta"] == dl]
                fe = [r for r in rr if r["feasible"] and not np.isnan(r["auc"])]
                ps = [pval(r["auc"], null) for r in fe]
                rungs[A][str(dl)] = dict(feasible=len(fe), counted=len(fe) >= 30,
                                         infeasible=int(sum(not r["feasible"] for r in rr)),
                                         nan_auc=int(sum(bool(r["feasible"] and np.isnan(r["auc"])) for r in rr)),
                                         realised_delta=float(np.mean([r["realised"] for r in fe])) if fe else None,
                                         power=float(np.mean([p < BAR_P for p in ps])) if fe else None,
                                         mean_excess=float(np.mean([r["auc"] for r in fe]) - out["null"]["mean"]) if fe else None)
            ok = [float(dl) for dl, v in rungs[A].items() if v["counted"] and v["power"] >= 0.8]
            rungs[A]["c_star"] = min(ok) if ok else None
        out["plants"] = rungs; out["draws"] = [{k: (v.item() if hasattr(v, "item") else v) for k, v in r.items()} for r in res]
        print("plants", json.dumps(rungs), flush=True)
        fa = P.map(fa_job, [(k, i) for k in "AB" for i in range(NFA)], chunksize=10)
        out["false_alarm"] = {k: dict(n=sum(1 for kk, v in fa if kk == k and not np.isnan(v)),
                                      passes=sum(1 for kk, v in fa if kk == k and not np.isnan(v) and pval(v, null) < BAR_P))
                              for k in "AB"}
        for k in "AB": out["false_alarm"][k]["ok"] = out["false_alarm"][k]["passes"] <= 16
        print("false_alarm", out["false_alarm"], flush=True)
    share = lambda cs: sum(out["per_class"][A] for A in cs) / out["rows"]
    pw = [A for A in S["elig"] if (rungs[A]["c_star"] or 9) <= 0.20]
    gr = [A for A in S["elig"] if (rungs[A]["c_star"] or 9) <= 0.40]
    out["band"] = "powered" if share(pw) >= 0.5 else ("gross" if share(gr) >= 0.5 else "underpowered")
    out["eligible_row_share"] = share(S["elig"])
    print("BAND", out["band"], "eligible row share", round(out["eligible_row_share"], 3), flush=True)
    json.dump(out, open(HERE / "kill.json", "w"), indent=1)


def mode_main():
    k = json.load(open(HERE / "kill.json"))
    if k["band"] not in ("powered", "gross"):
        sys.exit(f"STOP: kill test band is '{k['band']}'; the prereg forbids the real run.")
    sys.exit("main run not implemented in this sealed version; a powered band needs a reviewed addendum.")


if __name__ == "__main__":
    {"rows": mode_rows, "gate": mode_gate, "kill": mode_kill, "main": mode_main}[sys.argv[1]]()
