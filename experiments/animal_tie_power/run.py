"""Power of the Indus 'animal not named in the text' tests, plus a Linear B effect size at Indus shape.
Prereg docs/prereg/animal_tie_power.md.
Run: .venv/bin/python -I experiments/animal_tie_power/run.py kill   # Linear B, words, subsample 0, binary AUC
     .venv/bin/python -I experiments/animal_tie_power/run.py full   # Leg A (Indus plants) + Leg B (Linear B)
     .venv/bin/python -I experiments/animal_tie_power/run.py shape  # data shape only, no test statistic
"""
import json, re, sys, random, warnings
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path
import numpy as np

warnings.filterwarnings("ignore")
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments/context"))
import q1_animal as Q                                   # featurize, cv_score, build: reused unchanged
from common import (m77_texts, m77_animal, M_SHORT, M_TALL, JAR_M, strat_perm, strat_hyper_matrix, signs)  # noqa
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score

SEED = 20261127
NNULL_A, NDRAW, NNULL_B, NSUB = 1000, 40, 100, 20
DELTAS = (0.05, 0.10, 0.20, 0.40, 0.80)
TARGETS = ("non_unicorn", "shorthorn_bull", "elephant", "tiger")
T2_CLASSES = ("shorthorn_bull", "zebu", "elephant")    # F14 rule: non-unicorn animals with >= 20 texts
LB_SIZES = (78, 45, 34, 15, 12, 10, 10)
LB_LADDER = (0.0, 0.10, 0.20, 0.35, 0.50)


# ------------------------------------------------------------------ statistics (q1 logic)
def auc_bin(X, yb, seed=0):
    skf = StratifiedKFold(5, shuffle=True, random_state=seed); p = np.zeros(len(yb))
    for tr, te in skf.split(X, yb):
        m = LogisticRegression(C=0.3, max_iter=2000, class_weight="balanced").fit(X[tr], yb[tr])
        p[te] = m.predict_proba(X[te])[:, 1]
    return roc_auc_score(yb, p)


def bal_multi(X, y, seed=0):
    return Q.cv_score(X, y, seed=seed)[0]


def pval(obs, null):
    null = np.asarray(null); return float((1 + (null >= obs).sum()) / (len(null) + 1))


def t2_strata(items):
    """F14 strata: site x min(length, 7), strata with >= 5 texts kept."""
    key = [(site, min(len(signs(s)), 7)) for s, _, site in items]
    c = Counter(key); keep = [i for i, k in enumerate(key) if c[k] >= 5]
    return keep, np.array([f"{key[i][0]}|{key[i][1]}" for i in keep])


def t2_family(items, y, classes, keep, strata, min_doc=15, min_obs=5):
    """All (animal, sign) tests of the F14 family; returns list of (p_hi, animal, sign, obs)."""
    seqs = [set(signs(items[i][0])) for i in keep]
    doc = Counter(g for s in seqs for g in s); sg = sorted(g for g, n in doc.items() if n >= min_doc)
    X = np.array([[g in s for g in sg] for s in seqs], dtype=float)
    yk = np.asarray(y)[keep]; cl = list(classes)
    yi = np.array([cl.index(a) if a in cl else len(cl) for a in yk])
    obs, exp, p_hi, _ = strat_hyper_matrix(X, yi, strata, len(cl) + 1)
    return [(float(p_hi[a, b]), cl[a], sg[b], int(obs[a, b])) for a in range(len(cl)) for b in range(len(sg))
            if obs[a, b] >= min_obs]


# ------------------------------------------------------------------ Leg A: Indus seals, label-swap plants
def indus_items():
    seals = [t for t in m77_texts() if t["object_type"] == "seal"]
    items, conf = Q.build(seals, m77_animal, "fs80", M_SHORT, M_TALL, JAR_M)
    c = Counter(a for _, a, _ in items); keep = {a for a, n in c.items() if n >= 10}
    return [it for it in items if it[1] in keep], conf


A = {}


def initA():
    items, _ = indus_items()
    X, vocab, bigr, cols = Q.featurize(items, short=M_SHORT, tall=M_TALL, jar=JAR_M)
    A.update(items=items, X=X, y=np.array([a for _, a, _ in items]), site=np.array([s for _, _, s in items]),
             sets=[set(signs(s)) for s, _, _ in items])
    A["keep"], A["strata"] = t2_strata(items)


def nullA(args):
    i, kind = args
    rng = np.random.default_rng(SEED + 31 * i + (1 if kind == "multi" else 0))
    yp = strat_perm(A["y"], A["site"], rng)
    return kind, (auc_bin(A["X"], (yp == "unicorn").astype(int), seed=i + 1) if kind == "bin" else bal_multi(A["X"], yp, seed=i + 1))


def plant(y, target, delta, rng):
    """Swap labels within site so that a fraction (natural + delta) of class-A texts carry tie sign g."""
    isA = (y != "unicorn") if target == "non_unicorn" else (y == target)
    nA = int(isA.sum()); sets, site = A["sets"], A["site"]
    doc = Counter(g for s in sets for g in s)
    cands = [g for g, n in doc.items() if n >= 5]
    for _ in range(50):
        g = cands[rng.integers(len(cands))]
        has = np.array([g in s for s in sets]); r0 = (has & isA).sum() / nA
        need = int(np.ceil(min(1.0, r0 + delta) * nA)) - int((has & isA).sum())
        yy = y.copy(); ok = 0
        a_list = [i for i in rng.permutation(len(y)) if isA[i] and not has[i]]
        pool = defaultdict(list)
        for i in rng.permutation(len(y)):
            if (not isA[i]) and has[i]:
                pool[site[i]].append(i)
        for i in a_list:
            if ok >= need:
                break
            if pool[site[i]]:
                j = pool[site[i]].pop(); yy[i], yy[j] = yy[j], yy[i]; ok += 1
        if ok >= need:
            return yy, g, float(r0)
    return None, None, None


def drawA(args):
    target, delta, d = args
    rng = np.random.default_rng(SEED + 1000 * TARGETS.index(target) + int(delta * 100) * 50 + d)
    yy, g, r0 = plant(A["y"], target, delta, rng)
    if yy is None:
        return dict(target=target, delta=delta, d=d, feasible=False)
    out = dict(target=target, delta=delta, d=d, feasible=True, sign=g, natural=r0)
    if target == "non_unicorn":
        out["auc_bin"] = auc_bin(A["X"], (yy == "unicorn").astype(int))
    else:
        out["bal_multi"] = bal_multi(A["X"], yy)
        if target in T2_CLASSES:
            fam = t2_family(A["items"], yy, T2_CLASSES, A["keep"], A["strata"])
            out["t2_min_p"] = min(p for p, *_ in fam) if fam else 1.0
            out["t2_planted_p"] = min([p for p, a, s, o in fam if a == target and s == g] or [1.0])
    return out


# ------------------------------------------------------------------ Leg B: Linear B at Indus shape
WORD = re.compile(r"^[a-z*0-9₂₃]+(-[a-z*0-9₂₃]+)+$|^[a-z]{1,3}$")
LOGO = re.compile(r"^([A-Z]{2,})([:+;].*)?$")


def lb_lines():
    by_tab = defaultdict(list)
    for l in open(ROOT / "sources/paragorth_Indus-/other-scripts/linear-a/data/damos_items.jsonl"):
        r = json.loads(l); h = r.get("heading") or ""; c = r.get("content") or ""
        if not h:
            continue
        site = h.split()[0]; site = site if site in ("KN", "PY") else "other"
        for ln in c.split("\n"):
            toks = [t.strip(",'/[]") for t in ln.split()]
            w = [t for t in toks if WORD.match(t) and "-" in t]
            lg = [LOGO.match(t).group(1) for t in toks if LOGO.match(t)]
            if w and lg:
                by_tab[r["id"]].append((site, tuple(w), lg[0]))
    return by_tab


def lb_classes(by_tab):
    modal = Counter(Counter(x[2] for x in v).most_common(1)[0][0] for v in by_tab.values())
    return [c for c, _ in modal.most_common(8)]


def lb_subsample(by_tab, classes, k):
    rng = random.Random(SEED + 7 * k)
    pick = {t: v[rng.randrange(len(v))] for t, v in sorted(by_tab.items())}
    per = defaultdict(list)
    for t, (site, w, lab) in pick.items():
        if lab in classes:
            per[lab].append((t, site, w))
    out = [(s, w, classes[0]) for _, s, w in per[classes[0]]]
    for c, n in zip(classes[1:], LB_SIZES):
        v = per[c][:]; rng.shuffle(v); out += [(s, w, c) for _, s, w in v[:n]]
    return out


def lb_items(sub, coding, drop=frozenset()):
    raw = []
    for site, w, lab in sub:
        ws = [x for x in w if x not in drop]
        if not ws:
            continue
        seq = ws if coding == "words" else [s for x in ws for s in x.split("-")]
        raw.append(dict(seq=seq, lab=lab, site=site))
    return Q.build(raw, lambda a: a, "lab", set(), set(), None)[0]


def drop_set(sub, frac):
    wc = Counter(x for _, w, _ in sub for x in w); tot = sum(wc.values()); out, c = set(), 0
    for x, n in wc.most_common():
        if c / tot >= frac:
            break
        out.add(x); c += n
    return frozenset(out)


def test_b(items, dominant, nnull, seed, stats=("bin", "multi"), permute_labels=False):
    X, _, _, _ = Q.featurize(items, short=set(), tall=set(), jar=None)
    y = np.array([a for _, a, _ in items]); st = np.array([s for _, _, s in items])
    rng = np.random.default_rng(seed)
    if permute_labels:
        y = strat_perm(y, st, rng)
    out = dict(n=len(items), classes=dict(Counter(y)))
    if "bin" in stats:
        yb = (y == dominant).astype(int); o = auc_bin(X, yb)
        nl = [auc_bin(X, strat_perm(yb, st, rng), seed=i + 1) for i in range(nnull)]
        out.update(auc=o, auc_null_mean=float(np.mean(nl)), auc_null_p99=float(np.quantile(nl, .99)), auc_p=pval(o, nl))
    if "multi" in stats:
        o = bal_multi(X, y)
        nl = [bal_multi(X, strat_perm(y, st, rng), seed=i + 1) for i in range(nnull)]
        out.update(bal=o, bal_null_mean=float(np.mean(nl)), bal_p=pval(o, nl))
    if "t2" in stats:
        keep, strata = t2_strata(items)
        mins = [c for c, n in Counter(y).items() if c != dominant and n >= 20]
        fam = t2_family(items, y, mins, keep, strata)
        out.update(t2_ntests=len(fam), t2_min_p=min([p for p, *_ in fam] or [1.0]),
                   t2_pass=bool(fam and min(p for p, *_ in fam) < 0.05 / len(fam)))
    return out


B = {}


def initB():
    initA()
    B["by_tab"] = lb_lines(); B["classes"] = lb_classes(B["by_tab"])


def jobB(args):
    k, coding, frac, kind = args
    sub = lb_subsample(B["by_tab"], B["classes"], k)
    items = lb_items(sub, coding, drop_set(sub, frac) if frac else frozenset())
    stats = ("bin", "multi", "t2") if (frac == 0 and kind == "real") else ("bin",)
    r = test_b(items, B["classes"][0], NNULL_B, SEED + 100 * k + int(frac * 100) + (5 if coding == "syll" else 0),
               stats=stats, permute_labels=(kind == "control"))
    r.update(k=k, coding=coding, frac=frac, kind=kind)
    return r


# ------------------------------------------------------------------ main
if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "kill"
    if mode == "shape":
        initB(); sub = lb_subsample(B["by_tab"], B["classes"], 0)
        print(dict(indus=dict(Counter(A["y"])), lb_classes=B["classes"], lb_tablets=len(B["by_tab"]),
                   lb_sub0=dict(Counter(l for _, _, l in sub)),
                   lb_items_words=len(lb_items(sub, "words")), lb_items_syll=len(lb_items(sub, "syll"))))
    elif mode == "kill":
        initB(); sub = lb_subsample(B["by_tab"], B["classes"], 0); items = lb_items(sub, "words")
        r = test_b(items, B["classes"][0], 200, SEED, stats=("bin",))
        r["pass"] = bool(r["auc"] > r["auc_null_p99"]); print(json.dumps(r, indent=1))
        json.dump(r, open(HERE / "kill.json", "w"), indent=1)
    elif mode == "full":
        assert json.load(open(HERE / "kill.json"))["pass"], "kill test stopped the study"
        with Pool(4, initializer=initB) as P:
            nulls = P.map(nullA, [(i, k) for k in ("bin", "multi") for i in range(NNULL_A)], chunksize=20)
            NA = {k: np.array([v for kk, v in nulls if kk == k]) for k in ("bin", "multi")}
            draws = P.map(drawA, [(t, d, i) for t in TARGETS for d in DELTAS for i in range(NDRAW)], chunksize=4)
            jobs = [(k, c, f, "real") for k in range(NSUB) for c in ("words", "syll") for f in LB_LADDER]
            jobs += [(k, c, 0.0, "control") for k in range(NSUB) for c in ("words", "syll")]
            legb = P.map(jobB, jobs, chunksize=1)
        initA()
        real = dict(auc_bin=auc_bin(A["X"], (A["y"] == "unicorn").astype(int)), bal_multi=bal_multi(A["X"], A["y"]))
        real["auc_p"] = pval(real["auc_bin"], NA["bin"]); real["bal_p"] = pval(real["bal_multi"], NA["multi"])
        fam = t2_family(A["items"], A["y"], T2_CLASSES, A["keep"], A["strata"]); nt = len(fam)
        real.update(t2_ntests=nt, t2_min_p=min(p for p, *_ in fam), t2_bar=0.05 / nt)
        legA = {}
        for t in TARGETS:
            legA[t] = {}
            for d in DELTAS:
                dd = [x for x in draws if x["target"] == t and x["delta"] == d and x["feasible"]]
                row = dict(feasible=len(dd))
                if dd and t == "non_unicorn":
                    v = [x["auc_bin"] for x in dd]
                    row.update(mean_stat=float(np.mean(v)), power=float(np.mean([pval(x, NA["bin"]) < 0.05 for x in v])))
                elif dd:
                    v = [x["bal_multi"] for x in dd]
                    row.update(mean_stat=float(np.mean(v)), power=float(np.mean([pval(x, NA["multi"]) < 0.05 for x in v])))
                    if t in T2_CLASSES:
                        row["t2_power"] = float(np.mean([x["t2_min_p"] < 0.05 / nt for x in dd]))
                row["natural_mean"] = float(np.mean([x["natural"] for x in dd])) if dd else None
                legA[t][d] = row
            ok = [d for d in DELTAS if legA[t][d].get("power", 0) >= 0.8]; legA[t]["c_star_t1"] = min(ok) if ok else None
            ok2 = [d for d in DELTAS if legA[t][d].get("t2_power", 0) >= 0.8]; legA[t]["c_star_t2"] = min(ok2) if ok2 else None
        summB = {}
        for c in ("words", "syll"):
            summB[c] = {}
            for f in LB_LADDER:
                rr = [x for x in legb if x["coding"] == c and x["frac"] == f and x["kind"] == "real"]
                row = dict(mean_auc=float(np.mean([x["auc"] for x in rr])), pass_auc=sum(x["auc_p"] < 0.05 for x in rr))
                if f == 0:
                    row.update(mean_bal=float(np.mean([x["bal"] for x in rr])), pass_bal=sum(x["bal_p"] < 0.05 for x in rr),
                               t2_pass=sum(x["t2_pass"] for x in rr))
                summB[c][f] = row
            cc = [x for x in legb if x["coding"] == c and x["kind"] == "control"]
            summB[c]["control_pass"] = sum(x["auc_p"] < 0.05 for x in cc)
        # map Linear B AUCs onto the pooled Indus ladder (linear interpolation on mean AUC)
        lad = [(0.0, float(np.mean(NA["bin"])))] + [(d, legA["non_unicorn"][d]["mean_stat"]) for d in DELTAS
                                                     if legA["non_unicorn"][d].get("mean_stat") is not None]
        def to_c(a):
            for (d0, a0), (d1, a1) in zip(lad, lad[1:]):
                if a0 <= a <= a1:
                    return d0 + (d1 - d0) * (a - a0) / (a1 - a0) if a1 > a0 else d0
            return ">0.80" if a > lad[-1][1] else "<0"
        cons = min(("words", "syll"), key=lambda c: summB[c][0.0]["mean_auc"])
        mapping = {f: to_c(summB[cons][f]["mean_auc"]) for f in LB_LADDER}
        out = dict(real_indus=real, null_indus=dict(bin_mean=float(NA["bin"].mean()), bin_p95=float(np.quantile(NA["bin"], .95)),
                                                     multi_mean=float(NA["multi"].mean()), multi_p95=float(np.quantile(NA["multi"], .95))),
                   legA=legA, legB=summB, conservative_coding=cons, lb_to_indus_c=mapping, lb_classes=B.get("classes"),
                   draws=draws, legb_runs=legb)
        print(json.dumps({k: v for k, v in out.items() if k not in ("draws", "legb_runs")}, indent=1, default=str))
        json.dump(out, open(HERE / "full.json", "w"), indent=1, default=str)
