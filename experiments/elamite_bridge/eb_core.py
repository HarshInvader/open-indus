"""Shared code for the elamite_bridge tests.

Metric D (neighbour diversity): for every sign with >= MIN_TOK tokens in a set of break-free runs,
D = log(number of distinct left+right neighbour types, text edges excluded) minus the value predicted
from log(token count) by an OLS fit over all signs with >= MIN_TOK tokens in the same corpus.
Syllabograms combine with many partners; logograms in short-label writing tend to sit in fixed
company (numerals, a measure sign, a closer), so syllabograms should have higher D.
"""
import json, math, random
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
MIN_TOK = 10


def neighbour_stats(runs):
    tok = Counter(); nb = defaultdict(set)
    for r in runs:
        for i, s in enumerate(r):
            tok[s] += 1
            if i > 0: nb[s].add(("L", r[i - 1]))
            if i < len(r) - 1: nb[s].add(("R", r[i + 1]))
    return tok, nb


def diversity_residuals(runs, min_tok=MIN_TOK):
    tok, nb = neighbour_stats(runs)
    signs = [s for s in tok if tok[s] >= min_tok]
    x = np.array([math.log(tok[s]) for s in signs])
    y = np.array([math.log(len(nb[s]) + 1) for s in signs])
    A = np.vstack([x, np.ones_like(x)]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    res = y - A @ coef
    return {s: float(r) for s, r in zip(signs, res)}, tok


def auc(pos, neg):
    """P(random pos > random neg), ties 0.5."""
    if not pos or not neg: return float("nan")
    wins = 0.0
    for p in pos:
        for n in neg:
            wins += 1.0 if p > n else 0.5 if p == n else 0.0
    return wins / (len(pos) * len(neg))


def set_vs_rest_perm(D, test, n_perm=20000, seed=1, tok=None, strata=None):
    """One-sided permutation p for mean D of `test` signs > mean D of a random same-size set.
    If strata (dict sign -> stratum) is given, random sets are drawn matching the test set's
    stratum counts (frequency matching)."""
    rng = random.Random(seed)
    test = [s for s in test if s in D]
    if not test: return float("nan"), float("nan"), 0
    obs = float(np.mean([D[s] for s in test]))
    pool = list(D)
    if strata:
        by = defaultdict(list)
        for s in pool: by[strata[s]].append(s)
        need = Counter(strata[s] for s in test)
    ge = 0
    for _ in range(n_perm):
        if strata:
            pick = []
            for k, c in need.items(): pick += rng.sample(by[k], c)
        else:
            pick = rng.sample(pool, len(test))
        if np.mean([D[s] for s in pick]) >= obs - 1e-12: ge += 1
    return obs, (ge + 1) / (n_perm + 1), len(test)


def freq_strata(tok, signs, n_bins=5):
    """Quantile bins of log frequency over `signs`."""
    vals = sorted(math.log(tok[s]) for s in signs)
    cuts = [vals[int(len(vals) * k / n_bins)] for k in range(1, n_bins)]
    return {s: sum(math.log(tok[s]) >= c for c in cuts) for s in signs}


def jl(path):
    return [json.loads(l) for l in open(path, encoding="utf-8")]
