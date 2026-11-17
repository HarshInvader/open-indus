"""Exploratory (not pre-registered) follow-ups for local_repeats.
E1 locality: share of same-text pairs at one site vs random pairs of >=4-sign seals.
E2 formula decomposition: how much of the 4-5 sign excess is the 'opener + M99 + short numeral + M161' formula?
   Re-uses redteam_identifiers' N2 bigram null (imported read-only).
E3 period using merged-corpus 'time' (HARP-equivalent periods incl. Vats objects) instead of ICIT period.
usage: .venv/bin/python experiments/local_repeats/lr_explore.py [nsim]
"""
import sys, os, json, itertools
from collections import Counter, defaultdict
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, os.path.join(ROOT, "experiments/redteam_identifiers"))
sys.path.insert(0, os.path.join(ROOT, "experiments/local_repeats"))
NSIM = int(sys.argv[1]) if len(sys.argv) > 1 else 500
sys.argv = sys.argv[:1] + ["10"]  # lr.py reads argv[1] as nperm; we do not need its tests here
import c1  # noqa  (read-only import of the red-team null)
import lr  # noqa
HERE = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(7)
out = {}

# ---- E1 locality
L4 = [o for o in lr.SEALS if len(o["text"]) >= 4]
sc = Counter(o["site"] for o in L4); n = sum(sc.values())
same_rand = sum(v * (v - 1) for v in sc.values()) / (n * (n - 1))
fam_pairs = [p for p in lr.pairs]
obs_same = np.mean([p["cat"] != "X" for p in fam_pairs])
fam_single_site = np.mean([len(f["sites"]) == 1 for f in lr.families])
# expected share of families confined to one site if objects were placed at random sites (same family sizes)
sites_arr = np.array([o["site"] for o in L4])
sims = []
for _ in range(10000):
    perm = rng.permutation(sites_arr)
    k = 0; ss = 0; nf = 0
    for f in lr.families:
        s = perm[k:k + f["n"]]; k += f["n"]; ss += len(set(s)) == 1; nf += 1
    sims.append(ss / nf)
sims = np.array(sims)
out["E1_locality"] = dict(n_pairs=len(fam_pairs), share_pairs_same_site=float(obs_same), random_pair_same_site=float(same_rand),
                          share_families_one_site=float(fam_single_site), random_families_one_site_mean=float(sims.mean()),
                          p_more_local=float((1 + (sims >= fam_single_site).sum()) / (len(sims) + 1)))
print("E1", out["E1_locality"])

# ---- E2 formula decomposition
OPEN = {"W817", "W861", "W820"}; NUM = {"W003", "W004", "W016", "W005", "W006", "W007", "W008", "W009", "W010",
                                         "W011", "W012", "W013", "W014", "W015", "W017"}
def formula(t):
    return len(t) == 4 and t[0] in OPEN and t[1] == "W002" and t[2] in NUM and t[3] == "W390"
D = c1.distinct_corpus(c1.ALL); V = sorted({s for t in D for s in t})
g = c1.Bigram(D, V); g.prepare(max(len(t) for t in c1.texts))
lengths = [len(t) for t in c1.texts]
def stats(T):
    c = Counter(T)
    rep = [t for t, k in c.items() if k > 1 and 4 <= len(t) <= 5]
    return dict(all=sum(c[t] for t in rep), formula=sum(c[t] for t in rep if formula(t)),
                other=sum(c[t] for t in rep if not formula(t)), formula_texts_any=sum(formula(t) for t in T))
obs = stats(c1.texts); S = [stats(g.sample(lengths, rng)) for _ in range(NSIM)]
res = {"observed": obs}
for k in obs:
    a = np.array([s[k] for s in S], float)
    res[k] = dict(mean=float(a.mean()), lo=float(np.percentile(a, 2.5)), hi=float(np.percentile(a, 97.5)),
                  p_ge=float((1 + (a >= obs[k]).sum()) / (len(a) + 1)))
out["E2_formula"] = res
print("E2", json.dumps(res))

# ---- E3 merged 'time' as period
def tkey(x): return x["time"] if lr.known(x["time"]) else None
dated = []
for p in lr.pairs:
    if p["cat"] == "X": continue
    a, b = tkey(p["a"]), tkey(p["b"])
    if a and b: dated.append(dict(text=p["text"], a=p["a"]["cisi"], b=p["b"]["cisi"], ta=a, tb=b, same=a == b))
out["E3_time"] = dict(n_dated_same_site_pairs=len(dated), pairs=dated)
print("E3", out["E3_time"])
json.dump(out, open(os.path.join(HERE, "explore.json"), "w"), indent=1, default=float)

# ---- E1b per-pair match rates within vs between sites (>=4-sign seals; 4-5 and 6+ pooled)
from collections import Counter as _C
ns = _C(o["site"] for o in L4)
within = sum(1 for p in lr.pairs if p["cat"] != "X"); between = sum(1 for p in lr.pairs if p["cat"] == "X")
poss_w = sum(v * (v - 1) / 2 for v in ns.values()); poss_b = n * (n - 1) / 2 - poss_w
pp = _C()
for p in lr.pairs: pp[tuple(sorted((p["a"]["site"], p["b"]["site"])))] += 1
out["E1b_pair_rates"] = dict(n_by_site=dict(ns.most_common(8)), within_pairs=within, between_pairs=between,
                             rate_within=within / poss_w, rate_between=between / poss_b, ratio_between_over_within=(between / poss_b) / (within / poss_w),
                             pairs_by_site_pair={" / ".join(k): v for k, v in pp.items()})
print("E1b", out["E1b_pair_rates"])
json.dump(out, open(os.path.join(HERE, "explore.json"), "w"), indent=1, default=float)

# ---- E4 genre control for T1/T2: null pool restricted to square seals (SEAL:S), and to square unicorn seals for T1
lr.NPERM = 10000
sq = lambda i: i["type"] == "SEAL:S"
out["E4_T1_square_unicorn"] = lr.perm_test(lambda i: lr.dims_ok(i) and sq(i) and i["symbol"].startswith("Bull1"),
                                           lambda a, b: lr.dims_cmp(a, b)[1], lambda v: float(np.median(v)))
out["E4_T1_square"] = lr.perm_test(lambda i: lr.dims_ok(i) and sq(i), lambda a, b: lr.dims_cmp(a, b)[1], lambda v: float(np.median(v)))
out["E4_T2_square_base"] = lr.perm_test(lambda i: lr.sym_known(i["symbol"]) and sq(i),
                                        lambda a, b: float(a["symbol"].split(":")[0] == b["symbol"].split(":")[0]), lambda v: float(np.mean(v)))
out["E4_T2_square_full"] = lr.perm_test(lambda i: lr.sym_known(i["symbol"]) and sq(i),
                                        lambda a, b: float(a["symbol"] == b["symbol"]), lambda v: float(np.mean(v)))
for k in [k for k in out if k.startswith("E4")]: print(k, out[k])
json.dump(out, open(os.path.join(HERE, "explore.json"), "w"), indent=1, default=float)
