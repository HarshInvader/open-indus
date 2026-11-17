"""Power of the pre-registered mark-vs-word-ending test (docs/prereg/tn_brahmi_graffiti.md).

Planted answer: one mark sign A goes with the -n name ending at a set odds ratio; the other marks
are spread at random. We count how often the Holm-corrected Fisher test over all mark signs with
>= 3 occurrences finds A at p < 0.05. No real outcome is used: the only real inputs are the share
of -n words (8 of 20 secure sherds = 0.40) and a mark-type spread taken from the TN graffiti base-sign
frequencies at Keeladi (API, aggregate counts), here simplified to 8 types with Zipf weights.

Run: .venv/bin/python -I experiments/tn_brahmi_graffiti/power.py
"""
import json, os
import numpy as np
from scipy.stats import fisher_exact

rng = np.random.default_rng(7)
P_N = 0.40                      # share of words ending in -n among the 20 secure sherds
K = 8                           # number of mark types
w = 1 / np.arange(1, K + 1); w /= w.sum()   # Zipf weights; type 0 is the commonest
SIMS = 1000


def holm_hit(marks, ends_n, target):
    tested = []
    for k in range(K):
        a = marks == k
        if a.sum() < 3:
            continue
        t = [[np.sum(a & ends_n), np.sum(a & ~ends_n)],
             [np.sum(~a & ends_n), np.sum(~a & ~ends_n)]]
        tested.append((fisher_exact(t, alternative="greater")[1], k))
    tested.sort()
    m = len(tested)
    for i, (p, k) in enumerate(tested):
        if p > 0.05 / (m - i):
            return False
        if k == target:
            return True
    return False


def power(n, odds, target):
    hits = 0
    for _ in range(SIMS):
        ends_n = rng.random(n) < P_N
        marks = rng.choice(K, size=n, p=w)
        # plant: on -n words, mark becomes the target with prob giving the wanted odds ratio
        base = w[target]
        p1 = odds * base / (1 - base + odds * base)
        sel = ends_n & (rng.random(n) < p1)
        marks[sel] = target
        if not ends_n.all():
            other = ~ends_n
            # keep the target at its base rate on other words
            marks[other] = rng.choice(K, size=other.sum(), p=w)
        hits += holm_hit(marks, ends_n, target)
    return hits / SIMS


out = {}
for target, label in [(0, "commonest mark (Zipf rank 1)"), (2, "rank-3 mark")]:
    for odds in (3, 10, 1000):
        for n in (20, 30, 60, 120):
            pw = power(n, odds, target)
            out[f"{label}|OR={odds}|n={n}"] = pw
            print(f"{label:30s} OR={odds:<5} n={n:<4} power={pw:.3f}")

# false-positive rate with no planted link
fp = np.mean([holm_hit(rng.choice(K, 20, p=w), rng.random(20) < P_N, 0) for _ in range(SIMS)])
out["null_fpr_n20_target0"] = float(fp)
print("null false-positive rate (n=20, mark 0):", fp)
json.dump(out, open(os.path.join(os.path.dirname(__file__), "power.json"), "w"), indent=1)
