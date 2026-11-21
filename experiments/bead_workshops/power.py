"""Rough planted power for a later fish-in-workshop test. Sign-blind: uses only an
assumed fish base rate (0.30 of texts) and hypothetical enrichments, never joined counts.

Two approximations:
  binom  - one-sided exact binomial test of k fish texts in n workshop texts vs p0=0.30.
  clustered - simulation in which texts in a unit share a unit-level fish rate
              (beta, intra-unit correlation rho), which a density-matched permutation
              null would face; n split over the coded units' sizes.
Run: .venv/bin/python -I experiments/bead_workshops/power.py
"""
import json
from pathlib import Path

import numpy as np
from scipy.stats import binom

HERE = Path(__file__).resolve().parent
P0, ALPHA = 0.30, 0.05
rng = np.random.default_rng(20261121)


def crit(n):
    # smallest k with P(X>=k | p0) <= alpha
    for k in range(n + 1):
        if binom.sf(k - 1, n, P0) <= ALPHA:
            return k
    return n + 1


def power_binom(n, rr):
    k = crit(n)
    return float(binom.sf(k - 1, n, min(P0 * rr, 1.0))) if k <= n else 0.0


def power_clustered(sizes, rr, rho=0.1, reps=4000):
    sizes = np.array([s for s in sizes if s > 0])
    n = sizes.sum()
    k = crit(n)
    # beta with mean p and intra-class correlation rho: a+b = 1/rho - 1
    def draw(p):
        ab = 1 / rho - 1
        ps = rng.beta(p * ab, (1 - p) * ab, size=(reps, len(sizes)))
        return rng.binomial(sizes, ps).sum(1)
    # critical value calibrated under the clustered null, not the naive binomial
    null = draw(P0)
    kc = np.quantile(null, 1 - ALPHA, method="higher") + 1
    alt = draw(min(P0 * rr, 0.99))
    return float((alt >= kc).mean()), int(k), int(kc)


scen = {
    # unit sizes are inscribed-object counts (not distinct texts) from bead_units.csv
    "primary (high+medium, new sites): 4 units, 3 with texts": [26, 3, 3, 0],
    "Mohenjo-daro all coded joinable: 7 units, 6 with texts": [26, 30, 9, 4, 3, 1, 0],
    "all new coded incl. low: 15 units, 12 with texts": [26, 30, 9, 4, 3, 1, 0, 143, 38, 30, 6, 4, 3, 0, 0],
    "hypothetical 100 texts in 10 units": [10] * 10,
    "hypothetical 200 texts in 20 units": [10] * 20,
}
out = {}
for name, sizes in scen.items():
    n = sum(sizes)
    row = {"n_objects": n, "n_units": sum(1 for s in sizes if s > 0)}
    for rr in (1.5, 2.0):
        pc, k, kc = power_clustered(sizes, rr)
        row[f"binom_power_{rr}x"] = round(power_binom(n, rr), 3)
        row[f"clustered_power_{rr}x_rho0.1"] = round(pc, 3)
    out[name] = row
    print(name, row)

# smallest n (independent texts) for 80% power
for rr in (1.5, 2.0):
    n = 5
    while power_binom(n, rr) < 0.8:
        n += 1
    out[f"n_for_80pct_binom_{rr}x"] = n
    print(f"n for 80% power at {rr}x (independent texts):", n)

json.dump(out, open(HERE / "power.json", "w"), indent=1)
