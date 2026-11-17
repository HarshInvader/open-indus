"""Red team of board task #1 (foreign texts break Indus order). Pre-registered: docs/prereg/redteam_foreign_order.md.

Copies the model set-up of experiments/foreign_corpus/score.py (read only; nothing imported from that folder).
Run: .venv/bin/python -I experiments/redteam_foreign/attack.py
"""
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import binomtest, mannwhitneyu

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
G = ROOT / "experiments/grammar"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(G))
from glib import ClassBigram, m77_units, icit_devlike, family_folds, unit_from  # noqa
from step1_classes_seeds import SEED_W  # noqa

rng = np.random.default_rng(20261117)
CW = json.load(open(G / "classes_wells.json"))
KW, AW = CW["K"], CW["alpha"]
gram = lambda units: ClassBigram(KW, alpha=AW).fit(units, init=SEED_W, restarts=5)

BR = json.load(open(ROOT / "sources/shaunmortal_indus/data/bridge_WM.json"))
W2M = {f"W{int(k):03d}": [f"M{m}" for m in v["M"]] for k, v in BR.items()}
M2W = defaultdict(list)
for w, ms in W2M.items():
    for m in ms:
        M2W[m].append(w)
m2w = lambda seq: [s if s in "|#" else (M2W.get(s) or ["#"])[0] for s in seq]

ho = m77_units("heldout")
wl = icit_devlike(ho)
fo = family_folds(wl, 5, 0)
models, fold_of = [], {}
cv_all = {}
for f in range(5):
    tr = [u for u, q in zip(wl, fo) if q != f]
    g = gram(tr); models.append(g)
    for u, q in zip(wl, fo):
        if q == f:
            a, n = g.unit_logp(u); cv_all[u["key"]] = -a / n; fold_of[u["key"]] = f
GW = gram(wl)
native = [u for u in wl if u["register"] == "seal" and u["key"] in cv_all]


def make_pool(units):
    by = defaultdict(list)
    for u in units:
        by[(min(len(u["signs"]), 6), u["full"])].append(cv_all[u["key"]])
    return {k: np.array(v) for k, v in by.items()}


POOL_SEAL = make_pool(native)
POOL_ALL = make_pool([u for u in wl if u["key"] in cv_all])


def unit(seq):
    seq = ["#" if s == "?" else s for s in seq if s]
    return unit_from(seq, "#" not in seq)


def score(u, model=GW, pool=POOL_SEAL, shift=0.0):
    a, n = model.unit_logp(u); b = -a / n - shift
    key = (min(len(u["signs"]), 6), u["full"])
    ref = pool.get(key, pool.get((key[0], not key[1])))
    return float(b), float((1 + (ref >= b).sum()) / (len(ref) + 1))


def scorable(u):
    return u["runs"] and max(len(x[0]) for x in u["runs"]) >= 2


rows = {r["id"]: r for r in csv.DictReader(open(ROOT / "experiments/foreign_corpus/foreign_corpus.csv"))}
fr = []
for r in rows.values():
    if int(r["n_legible"]) < 2:
        continue
    seq = r["seq_wells"].split("-")
    u = unit(seq)
    if not scorable(u):
        continue
    b, p = score(u)
    fr.append(dict(id=r["id"], seq=seq, u=u, bits=b, p=p, region=r["region"], conf=r["reading_confidence"],
                   verified=r["verified_against_image"], origin=r["seq_origin"]))
F = {x["id"]: x for x in fr}
res = {"n_scored": len(fr), "n_flag_base": sum(x["p"] < 0.05 for x in fr)}
print("base", res)

# ---------------- T1 direction + T2 alternative readings
variants = defaultdict(list)  # id -> list of (label, p)
for x in fr:
    variants[x["id"]].append(("as corpus", x["p"]))
for i in ("SUSA-02", "BAHRAIN-01", "FAILAKA-01"):
    seq = list(reversed(F[i]["seq"]))
    variants[i].append(("reversed", score(unit(seq))[1]))
alt = {"UR-02": "M171-M387-M97-M341-M107", "UR-05": "M175-M12-M182",
       "SUSA-02": "M173-M10-M97-M121-M185-M97-M297-M57"}
for i, ms in alt.items():
    seq = m2w(ms.split("-"))
    u = unit(seq)
    if scorable(u):
        variants[i].append(("M77 reading " + "-".join(seq), score(u)[1]))
        if i == "SUSA-02":
            variants[i].append(("M77 reading reversed", score(unit(list(reversed(seq))))[1]))
res["T1T2_variants"] = {k: v for k, v in variants.items() if len(v) > 1}
surv = {x["id"]: all(p < 0.05 for _, p in variants[x["id"]]) for x in fr}
res["T1T2_survivors"] = sorted(k for k, v in surv.items() if v)
res["T1T2_n_survivors"] = len(res["T1T2_survivors"])
res["T1T2_binom_p"] = binomtest(res["T1T2_n_survivors"], len(fr), 0.05, alternative="greater").pvalue
# reversal calibration on natives
rev_flag = []
for u in native:
    if len(u["signs"]) >= 3:
        m = models[fold_of[u["key"]]]
        rev_flag.append(score(unit(list(reversed(u["signs"]))) if u["full"] else unit(list(reversed(u["signs"]))), m)[1] < 0.05)
res["T1_native_reversed_flag_rate"] = float(np.mean(rev_flag)); res["T1_native_reversed_n"] = len(rev_flag)

# ---------------- T3 reference
res["T3_allregister_flags"] = sorted(x["id"] for x in fr if score(x["u"], pool=POOL_ALL)[1] < 0.05)
res["T3_shift018_flags"] = sorted(x["id"] for x in fr if score(x["u"], shift=0.18)[1] < 0.05)
for k in ("T3_allregister_flags", "T3_shift018_flags"):
    n = len(res[k]); res[k + "_n"] = n; res[k + "_binom_p"] = binomtest(n, len(fr), 0.05, alternative="greater").pvalue

# ---------------- T4 bridge calibration
bflag = []
for u in ho:
    if u["register"] != "seal":
        continue
    seq = m2w(list(u["signs"]))
    v = unit_from(seq, u["full"] and "#" not in seq)
    if scorable(v):
        bflag.append(score(v)[1] < 0.05)
res["T4_bridged_native_flag_rate"] = float(np.mean(bflag)); res["T4_n"] = len(bflag)
m77only = [x["id"] for x in fr if x["origin"] != "ICIT"]
res["T4_m77only_scored"] = m77only
res["T4_m77only_flagged"] = [i for i in m77only if F[i]["p"] < 0.05]

# ---------------- T5 provenance
keep = [x for x in fr if x["region"] != "unknown-WA"]
n5 = sum(x["p"] < 0.05 for x in keep)
res["T5"] = dict(n_scored=len(keep), n_flag=n5, binom_p=binomtest(n5, len(keep), 0.05, alternative="greater").pvalue)

# ---------------- T6 misreading control
freq = Counter(s for u in wl for s in u["signs"] if s not in ("#", "|"))
signs = list(freq); w = np.array([freq[s] for s in signs], float); w /= w.sum()
f1 = []
for u in native:
    s = list(u["signs"])
    if len(s) < 3 or not u["full"]:
        continue
    for _ in range(3):
        j = rng.integers(len(s)); t = s.copy()
        new = s[j]
        while new == s[j]:
            new = signs[rng.choice(len(signs), p=w)]
        t[j] = new
        f1.append(score(unit_from(t, True), models[fold_of[u["key"]]])[1] < 0.05)
f1 = float(np.mean(f1)); res["T6_f1_one_misreading_flag_rate"] = f1


def pbinom_tail(probs, k):
    d = np.array([1.0])
    for q in probs:
        d = np.convolve(d, [1 - q, q])
    return float(d[k:].sum())


def is_confirmed(x):
    return x["conf"] == "confirmed"


for label, flagged in (("base", [x for x in fr if x["p"] < 0.05]),
                       ("survivors", [F[i] for i in res["T1T2_survivors"]])):
    probs = [0.05 if is_confirmed(x) else f1 for x in fr]
    res[f"T6_{label}_k"] = len(flagged)
    res[f"T6_{label}_expected"] = float(sum(probs))
    res[f"T6_{label}_p"] = pbinom_tail(probs, len(flagged))

# ---------------- T7 order vs inventory
def qstat(u, model):
    s = list(u["signs"])
    b = -np.divide(*model.unit_logp(u))
    perms = set()
    import itertools, math
    if math.factorial(len(s)) <= 2000:
        cand = [list(p) for p in itertools.permutations(s)]
    else:
        cand = [list(rng.permutation(s)) for _ in range(2000)]
    better = 0; tot = 0
    for p in cand:
        if p == s:
            continue
        v = unit_from(p, u["full"])
        bp = -np.divide(*model.unit_logp(v))
        better += bp < b - 1e-9; tot += 1
    return better / tot if tot else np.nan


nat_q = [qstat(u, models[fold_of[u["key"]]]) for u in native if len(u["signs"]) >= 3 and len(set(u["signs"])) > 1]
nat_q = np.array([q for q in nat_q if not np.isnan(q)])
fq = {x["id"]: qstat(x["u"], GW) for x in fr if len(x["u"]["signs"]) >= 3 and len(set(x["u"]["signs"])) > 1}
res["T7_native_q_median"] = float(np.median(nat_q)); res["T7_native_q90"] = float(np.quantile(nat_q, 0.9))
res["T7_native_n"] = len(nat_q)
flag_q = [fq[i] for i in fq if F[i]["p"] < 0.05]
res["T7_flagged_q"] = {i: round(fq[i], 3) for i in fq if F[i]["p"] < 0.05}
res["T7_flagged_q_median"] = float(np.median(flag_q))
res["T7_mwu_p"] = float(mannwhitneyu(flag_q, nat_q, alternative="greater").pvalue)
res["T7_order_driven"] = sorted(i for i in res["T7_flagged_q"] if fq[i] > res["T7_native_q90"])
res["T7_all_foreign_q"] = {i: round(v, 3) for i, v in fq.items()}

# ---------------- verdict per prereg
a = res["T1T2_binom_p"] < 0.01; b = res["T6_survivors_p"] < 0.01
res["verdict"] = "holds" if a and b else ("weakened" if a else "broken")
res["per_text"] = [{k: x[k] for k in ("id", "bits", "p", "region", "conf", "origin")} for x in fr]
json.dump(res, open(HERE / "results.json", "w"), indent=1, default=float)
print(json.dumps({k: v for k, v in res.items() if k not in ("per_text", "T7_all_foreign_q")}, indent=1, default=float))
