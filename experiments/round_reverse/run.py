"""Round-seal reversal (Fable 5.2 plan 11, candidate 6). Prereg: docs/prereg/round_reverse.md

    .venv/bin/python -I experiments/round_reverse/run.py sizes          # set sizes only, no scores
    board/run.sh env PYTHONHASHSEED=0 .venv/bin/python -I experiments/round_reverse/run.py run

Units, order models (KN, Wells class grammar, positional), permutation excess d and the format matcher are
copied from experiments/redteam_round_seal_format/run.py (board #41) without change, so the forward numbers
reproduce #41. New here: every round text is also scored read backwards, with format features recomputed
on the reversed text, and a planted direction-error control on square seals.
"""
import sys, json, csv, itertools, time, math, re
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "experiments/context"), str(ROOT / "experiments/grammar"), str(ROOT)]
import q4_gulf as Q  # noqa
import glib  # noqa
from corpus.load import icit_texts  # noqa

MODE = sys.argv[1] if len(sys.argv) > 1 else "sizes"
T0 = time.time()
log = lambda *a: print(f"[{time.time() - T0:6.0f}s]", *a, flush=True)
rng = np.random.default_rng(41)
NDRAW = 10000
ROUND = ("SEAL:C", "SEAL:CY")
NOT_SEALS = {"1387.1", "1388.1", "1388.2"}
NUM = set(glib.NUM["ICIT"])
SC = list(csv.DictReader(open(ROOT / "experiments/grammar/sign_classes.csv")))


def wset(lab):
    out = set()
    for r in SC:
        if r["final_class"] != lab: continue
        out |= {w for w in re.split(r"[;\s]+", r["wells_signs"]) if w.startswith("W")}
    return out


OPEN, CLOSE = wset("opener"), wset("closer")
GW = json.load(open(ROOT / "experiments/grammar/classes_wells.json"))


def mk(raw_seq, **kw):
    raw = [s for s in raw_seq if s != "|"]
    sg = [s for s in raw if s.startswith("W")]
    return dict(seq=sg, L=len(sg), first_ok=bool(raw) and raw[0] != "#", last_ok=bool(raw) and raw[-1] != "#", raw=raw, **kw)


seen, units = set(), []
for t in icit_texts():
    site, tp = t["site"], t["type"]
    if not tp.startswith("SEAL") or t["id"] in NOT_SEALS: continue
    grp = "abroad" if site in glib.FOREIGN else "unprov" if site == "Unknown" else "home"
    u = mk(t["seq"], id=t["id"], site=site, grp=grp, type=tp, round=tp in ROUND,
           complete=bool(t["complete"]) and "#" not in t["seq"])
    if u["L"] == 0: continue
    k = (grp, " ".join(u["seq"]))
    if k in seen: continue
    seen.add(k); units.append(u)
rkeys = {" ".join(u["seq"]) for u in units if u["round"]}
rnd = [u for u in units if u["round"]]
sq = [u for u in units if not u["round"] and u["grp"] == "home" and " ".join(u["seq"]) not in rkeys]


def reversed_unit(u):
    v = mk(list(reversed(u["raw"])), **{k: u[k] for k in ("id", "site", "grp", "type", "round", "complete")})
    v["rev"] = True
    return v


rnd_rev = [reversed_unit(u) for u in rnd]
R = dict(n_round=len(rnd), n_square=len(sq),
         n_round_scorable=sum(u["L"] >= 2 for u in rnd),
         n_round_last_ok=sum(u["last_ok"] for u in rnd), n_round_first_ok=sum(u["first_ok"] for u in rnd),
         by_grp=dict(Counter(u["grp"] for u in rnd)),
         n_palindrome=sum(u["seq"] == u["seq"][::-1] for u in rnd if u["L"] >= 2))
log(R)
if MODE == "sizes":
    sys.exit(0)

# ---------------- order models (as #41) ----------------
home_all, seen2 = [], set()
for t in icit_texts():
    s = [x for x in Q.clean(t["seq"]) if x.startswith("W")]
    if not s or t["site"] in glib.FOREIGN or t["site"] == "Unknown": continue
    k = " ".join(s)
    if k in seen2: continue
    seen2.add(k); home_all.append(s)
hidx = {" ".join(s): i for i, s in enumerate(home_all)}
N = len(home_all); perm_i = rng.permutation(N); fold = np.zeros(N, int)
for f in range(10): fold[perm_i[f::10]] = f
GCLS = dict(zip(GW["words"], GW["cls"])); K = GW["K"]


class GR:
    def __init__(self, texts, a=0.5):
        c = Counter(s for t in texts for s in t)
        self.V = {s for s, n in c.items() if n >= 2 and s in GCLS}
        tr = np.full((K + 1, K + 1), a); em = defaultdict(Counter)
        for t in texts:
            cs = [self.cl(s) for s in t]
            for s, cc in zip(t, cs): em[cc][self.m(s)] += 1
            seq = [K] + cs + [K]
            for x, y in zip(seq, seq[1:]): tr[x, y] += 1
        self.T = tr / tr.sum(1, keepdims=True)
        self.em = {}
        for cc in range(K):
            n = sum(em[cc].values()); vc = sum(1 for w in self.V if GCLS[w] == cc) + 1
            self.em[cc] = (em[cc], n, vc)

    def m(self, s): return s if s in self.V else "<UNK>"
    def cl(self, s): return GCLS[s] if s in self.V else GCLS["<UNK>"]

    def bits(self, t):
        cs = [self.cl(s) for s in t]; lp = 0.0
        for s, cc in zip(t, cs):
            e, n, vc = self.em[cc]; lp += math.log2((e[self.m(s)] + 0.5) / (n + 0.5 * vc))
        seq = [K] + cs + [K]
        for x, y in zip(seq, seq[1:]): lp += math.log2(self.T[x, y])
        return -lp / (len(t) + 1)


class POS:
    def __init__(self, texts):
        self.m = glib.PositionModel(cap=4).fit([dict(runs=[(tuple(t), True, True)]) for t in texts])

    def bits(self, t):
        lp, n = self.m.run_logp(tuple(t), True, True)
        return -lp / n


MODELS = {}
for name, cls in (("KN", Q.KN), ("GR", GR), ("POS", POS)):
    MODELS[name] = ([cls([home_all[i] for i in range(N) if fold[i] != f]) for f in range(10)], cls(home_all))
log("models fitted", N)


def perms(seq, k=200):
    if len(seq) <= 5:
        ps = set(itertools.permutations(seq)); ps.discard(tuple(seq)); ps = [list(p) for p in ps]
        return ps if len(ps) <= k else [ps[i] for i in rng.choice(len(ps), k, replace=False)]
    out = []
    for _ in range(k):
        p = list(rng.permutation(seq))
        if p != list(seq): out.append(p)
    return out


def score(u, key=None):
    """d = bits(text) - mean bits(permutations). key: home-fold lookup key (the forward text), so a home
    text and its reversal are scored by the same out-of-fold model."""
    s = u["seq"]; ps = perms(s) if len(s) >= 2 else []
    k = key if key is not None else " ".join(s)
    for name, (folds, full) in MODELS.items():
        M = folds[fold[hidx[k]]] if (u["grp"] == "home" and k in hidx) else full
        u["d_" + name] = (M.bits(s) - float(np.mean([M.bits(p) for p in ps]))) if ps else np.nan


for u in rnd + sq:
    score(u)
for u, f in zip(rnd_rev, rnd):
    score(u, key=" ".join(f["seq"]))
log("scored")


def feats(u):
    s = u["seq"]
    u["num1"] = u["first_ok"] and bool(s) and s[0] in NUM
    u["op1"] = u["first_ok"] and bool(s) and s[0] in OPEN
    u["clL"] = u["last_ok"] and bool(s) and s[-1] in CLOSE


for u in units + rnd_rev:
    feats(u)
F0 = lambda u: (u["num1"], u["op1"], u["clL"])


def levels(u, fdef):
    f = fdef(u) if fdef else ()
    L = min(u["L"], 9)
    return [(L,) + tuple(f[:j]) for j in range(len(f), -1, -1)]


class Matcher:
    def __init__(self, model, fdef, pool=None):
        pool = sq if pool is None else pool
        self.pool = [u for u in pool if not np.isnan(u["d_" + model])]
        self.vals = np.array([u["d_" + model] for u in self.pool])
        self.fdef = fdef
        self.tab = defaultdict(list)
        for i, u in enumerate(self.pool):
            for k in levels(u, fdef): self.tab[k].append(i)

    def stratum(self, u):
        for j, k in enumerate(levels(u, self.fdef)):
            if len(self.tab.get(k, [])) >= 5: return np.array(self.tab[k]), j
        L = min(u["L"], 9)
        while len(self.tab.get((L,), [])) < 5 and L > 2: L -= 1
        return np.array(self.tab[(L,)]), 99


def excess(sel, model, fdef, ndraw=NDRAW, pool=None):
    sel = [u for u in sel if not np.isnan(u["d_" + model])]
    M = Matcher(model, fdef, pool); st = [M.stratum(u) for u in sel]
    v = np.array([u["d_" + model] for u in sel])
    nm = np.array([M.vals[c].mean() for c, _ in st])
    out = dict(n=len(sel), mean_d=float(v.mean()), excess=float(v.mean() - nm.mean()))
    if ndraw:
        draws = np.stack([M.vals[c[rng.integers(len(c), size=ndraw)]] for c, _ in st]).mean(0)
        out["p"] = float((1 + (draws >= v.mean()).sum()) / (ndraw + 1))
    return out, v, nm


def boot_ratio(vf, nf, vr, nr, B=2000):
    """Bootstrap over texts (paired) of E_rev / E_fwd."""
    out = []
    for _ in range(B):
        b = rng.integers(len(vf), size=len(vf))
        ef = (vf[b] - nf[b]).mean(); er = (vr[b] - nr[b]).mean()
        if ef > 0: out.append(er / ef)
    return [float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))]


# ---------------- main comparison ----------------
RES = {}
for model in MODELS:
    for fname, fd in (("length", None), ("F0", F0)):
        ef, vf, nf = excess(rnd, model, fd)
        er, vr, nr = excess(rnd_rev, model, fd)
        ids = [u["id"] for u in rnd if not np.isnan(u["d_" + model])]
        assert ids == [u["id"] for u in rnd_rev if not np.isnan(u["d_" + model])]
        RES[f"{model}|{fname}"] = dict(forward=ef, reversed=er, ratio_rev_fwd=er["excess"] / ef["excess"] if ef["excess"] else None,
                                       ratio_ci=boot_ratio(vf, nf, vr, nr),
                                       n_texts_lower_when_reversed=int(np.sum(vr < vf)), n=len(vf))
        log(model, fname, json.dumps(RES[f"{model}|{fname}"]))
R["main"] = RES

# per-text table (KN)
R["texts"] = [dict(id=u["id"], grp=u["grp"], seq=" ".join(u["seq"]),
                   **{f"fwd_{m}": (None if np.isnan(u["d_" + m]) else round(float(u["d_" + m]), 3)) for m in MODELS},
                   **{f"rev_{m}": (None if np.isnan(v["d_" + m]) else round(float(v["d_" + m]), 3)) for m in MODELS})
              for u, v in zip(rnd, rnd_rev)]

# ---------------- controls ----------------
# C1 direction sensitivity: square home seals reversed. Excess of reversed squares over forward squares.
sq_s = [u for u in sq if u["L"] >= 2]
sub = [sq_s[i] for i in rng.choice(len(sq_s), 400, replace=False)]
sub_rev = [reversed_unit(u) for u in sub]
for v, u in zip(sub_rev, sub):
    score(v, key=" ".join(u["seq"])); feats(v)
CTRL = {}
for model in MODELS:
    a = np.array([u["d_" + model] for u in sub]); b = np.array([v["d_" + model] for v in sub_rev])
    m = ~np.isnan(a) & ~np.isnan(b)
    CTRL[f"square_reversal_shift_{model}"] = float((b[m] - a[m]).mean())
# C2 planted direction error at round-set size: draw square seals matched to the round set's length
# strata, write them backwards, score; then read them forwards again. A pure direction error shows a large
# forward excess that reversal removes.
ML = Matcher("KN", None)
scor = [u for u in rnd if not np.isnan(u["d_KN"])]
st = [ML.stratum(u)[0] for u in scor]
pl = []
for rep in range(100):
    picks = [ML.pool[c[rng.integers(len(c))]] for c in st]
    bw = [reversed_unit(u) for u in picks]
    for v, u in zip(bw, picks):
        score(v, key=" ".join(u["seq"]))
    for model in ("KN",):
        e_bw = excess(bw, model, None, ndraw=0)[0]["excess"]
        e_fw = excess(picks, model, None, ndraw=0)[0]["excess"]
        pl.append(dict(planted_excess=e_bw, after_reversal=e_fw, ratio=e_fw / e_bw if e_bw > 0 else None))
CTRL["planted_direction_error_KN"] = dict(
    mean_planted_excess=float(np.mean([x["planted_excess"] for x in pl])),
    mean_after_reversal=float(np.mean([x["after_reversal"] for x in pl])),
    share_ratio_below_half=float(np.mean([x["ratio"] is not None and x["ratio"] < 0.5 for x in pl])), reps=len(pl))
R["controls"] = CTRL
log("controls", json.dumps(CTRL))

# ---------------- verdict (rule fixed in prereg) ----------------
p = RES["KN|F0"]
ratio = p["ratio_rev_fwd"]; prev = p["reversed"]["p"]
if CTRL["planted_direction_error_KN"]["share_ratio_below_half"] < 0.8:
    v = "UNINFORMATIVE: the planted direction-error control failed"
elif ratio is not None and ratio < 0.5 and prev >= 0.05:
    v = "DENT: reversal removes most of the off-order; finding #4 is largely a reading-direction effect"
elif ratio is not None and ratio < 0.5:
    v = "PARTIAL: reversal removes more than half, but a significant excess remains"
else:
    v = "NO DENT: reversed round texts are still off-order; direction does not explain finding #4"
R["verdict"] = v
log("VERDICT", v)
json.dump(R, open(OUT / "results.json", "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
log("done")
