"""Power of the confirmatory bangle-oval test as a function of new-sample size n.

H1: oval (M373/M374 = W790) on p1 of new bangle texts; p1 = 0.15 (pre-registered effect,
close to the discovery rate 6/41 = 0.146) and a pessimistic p1 = 0.08 (L2 pass bar).
H0: p0 = 0.0106 = share of distinct non-bangle ICIT texts at the bangle sites carrying W790
(baselines.json; MD 0.0096, Harappa 0.0106).
Primary pass rule (docs/prereg/bangle_oval.md): observed share >= 0.15 AND one-sided exact
binomial p < 0.05 vs p0. Also reported: the binomial test alone, and the L2 rule (share >= 0.08,
p < 0.05). Workshop test power: Fisher MD vs Harappa when one site has rate p1 and the other
p0-ish (0.01).
Run: .venv/bin/python experiments/bangle_oval/b1_power.py
"""
import json
import math
from pathlib import Path

import numpy as np
from scipy.stats import binom, fisher_exact

OUT = Path(__file__).resolve().parent
P0 = json.load(open(OUT / "baselines.json"))["nonbangle_baseline"]["ALL"]["share"]


def crit(n, share_bar):
    """smallest k with k/n >= share_bar and P(X>=k | p0) < 0.05"""
    for k in range(n + 1):
        if k / n >= share_bar - 1e-12 and binom.sf(k - 1, n, P0) < 0.05:
            return k
    return None


rows = []
for n in (1, 2, 4, 6, 10, 15, 20, 30, 41, 60, 100):
    r = {"n": n}
    for name, bar in (("prereg_15", 0.15), ("L2_08", 0.08), ("binom_only", 0.0)):
        k = crit(n, bar)
        r[name + "_k"] = k
        for p1 in (0.15, 0.08):
            r[f"{name}_power_p{int(p1*100)}"] = round(float(binom.sf(k - 1, n, p1)), 3) if k else 0.0
    # probability of seeing zero ovals under H1 (how often a true effect looks null)
    r["P_zero_given_p15"] = round((1 - 0.15) ** n, 3)
    rows.append(r)

# n needed for 80% power under each rule
need = {}
for name, bar in (("prereg_15", 0.15), ("L2_08", 0.08), ("binom_only", 0.0)):
    for p1 in (0.15, 0.08):
        for n in range(1, 400):
            k = crit(n, bar)
            if k and binom.sf(k - 1, n, p1) >= 0.8:
                need[f"{name}_p{int(p1*100)}"] = n
                break

# workshop test: oval rate 0.15 at one site vs 0.01 at the other, equal n per site, Fisher one-sided
rng = np.random.default_rng(1)
work = {}
for n_site in (5, 10, 20, 40):
    hits = 0
    for _ in range(2000):
        a = rng.binomial(n_site, 0.15)
        b = rng.binomial(n_site, 0.01)
        hits += fisher_exact([[a, n_site - a], [b, n_site - b]], alternative="greater")[1] < 0.05
    work[n_site] = round(hits / 2000, 3)

res = {"p0": P0, "table": rows, "n_for_80pct_power": need, "workshop_fisher_power_per_site_n": work}
json.dump(res, open(OUT / "power.json", "w"), indent=1)
for r in rows:
    print(r)
print(need)
print(work)
