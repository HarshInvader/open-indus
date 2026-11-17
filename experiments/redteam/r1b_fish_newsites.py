"""Claim 1 add-on: ticked fish on ICIT sites absent from M77 (a genuinely new sample), and
texts ending in a ticked fish vs the jar (closer-slot competition), length-matched."""
from collections import Counter
from scipy.stats import binomtest
from rt_common import icit, m77, save
from r1_fish import texts_of, stats, PAIRS_W
norm = lambda s: s.lower().replace("-", "").replace(" ", "")
m77sites = {norm(t["site"]) for t in m77()} | {"mohenjodaro", "chanhudaro"}
T = texts_of(icit(), lambda r: norm(r["site"]) not in m77sites)
D = {d for _, d in PAIRS_W}
st = stats(T, D)
st["binom_p_vs_shuffle"] = binomtest(st["final"], st["tokens"], st["shuffle_expect"], alternative="greater").pvalue if st["tokens"] else None
st["sites"] = Counter(r["site"] for f, r in T if any(s in D for s in f))
st["n_texts"] = len(T)
print(st)
# jar avoidance: texts containing a ticked fish anywhere vs length-matched texts: jar rate
A = texts_of(icit())
import numpy as np
rng = np.random.default_rng(0)
withf = [f for f, _ in A if any(s in D for s in f)]
byL = {}
for f, _ in A:
    if not any(s in D for s in f): byL.setdefault(min(len(f), 8), []).append(f)
jar_obs = np.mean(["W740" in f for f in withf])
jar_null = [np.mean(["W740" in byL[min(len(f), 8)][rng.integers(len(byL[min(len(f), 8)]))] for f in withf]) for _ in range(2000)]
r = dict(new_sites=st, jar_rate_with_ticked=round(float(jar_obs), 3), jar_rate_matched=round(float(np.mean(jar_null)), 3),
         p=float((1 + sum(x <= jar_obs for x in jar_null)) / 2001))
print(r)
save("r1b_fish_newsites", r)
