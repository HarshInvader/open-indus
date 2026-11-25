"""split_witness: shared library (to be frozen with MINIMUM.txt).

Sign space and tokeniser: ICIT (Wells/Fuls) records as built by corpus/build.py icit()
(three-digit Wells numbers -> 'W###', reading order, '/' -> '|' line break, 000/999 -> '#').
N-gram runs come from corpus.load.runs (cut at '|' and '#'), so no bigram is ever counted
across a line break, a face boundary (faces are separate records) or a damage mark.

Cohesion ("binding") measure: the end-start ratio of experiments/line_breaks/lb_lib.py,
    ESR(a,b) = log2 P(</s>|a) + log2 P(b|<s>) - log2 P(b|a),
from lb_lib.Model (interpolated Kneser-Ney bigram, absolute discount D = 0.75, continuation
probability with +0.5 smoothing). Higher ESR = weaker junction (more boundary-like).

Held out by family: distinct flattened ICIT sequences are linked when within one edit (both
>= 4 signs) or when the shorter (>= 3 signs) is a contiguous part of the longer (the
corpus/build.py _close rule used for splits_v2). Connected components are families. Each
family goes to one of K = 10 folds by sha256 of its smallest member key. The model scoring a
unit in fold f is fitted only on ICIT records whose family is not in fold f
(leave-family-out by fold), so no text of the unit's own family is ever in training.
"""
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments" / "line_breaks"))
from corpus.load import icit_texts, runs  # noqa: E402
from corpus.build import _close  # noqa: E402
import lb_lib  # noqa: E402

K_FOLDS = 10


def flat(seq):
    return [s for s in seq if s not in ("|", "#")]


def key(signs):
    return " ".join(signs)


def families(extra_keys=()):
    """Union-find families over distinct flattened ICIT sequences (plus extra keys).
    Returns dict key -> family id (the smallest member key)."""
    keys = sorted({key(flat(t["seq"])) for t in icit_texts() if flat(t["seq"])} | set(extra_keys))
    sg = [k.split() for k in keys]
    parent = list(range(len(keys)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    # index by sign to avoid the full O(n^2) scan: two texts can only be close if they share a sign
    by_sign = defaultdict(set)
    for i, s in enumerate(sg):
        for x in set(s):
            by_sign[x].add(i)
    for i, s in enumerate(sg):
        cand = set()
        for x in set(s):
            cand |= by_sign[x]
        for j in cand:
            if j > i and _close(s, sg[j]):
                ri, rj = find(i), find(j)
                if ri != rj:
                    parent[ri] = rj
    comp = defaultdict(list)
    for i in range(len(keys)):
        comp[find(i)].append(keys[i])
    fam = {}
    for members in comp.values():
        fid = min(members)
        for k in members:
            fam[k] = fid
    return fam


def fold_of(fid):
    return int(hashlib.sha256(f"split_witness:{fid}".encode()).hexdigest()[:8], 16) % K_FOLDS


def fold_models(fam):
    """Fit one lb_lib.Model per fold on distinct ICIT records whose family is not in that fold."""
    recs = []
    seen = set()
    for t in icit_texts():
        if not flat(t["seq"]):
            continue
        s = key(t["seq"])
        if s in seen:
            continue
        seen.add(s)
        recs.append((fold_of(fam[key(flat(t["seq"]))]), t))
    models = {}
    for f in range(K_FOLDS):
        models[f] = lb_lib.Model([t for g, t in recs if g != f])
    return models


def junction_ranks(model, signs):
    """Percentile rank (midrank, 0..1) of ESR at each junction j = 1..n-1 (after sign j)."""
    e = [model.esr(a, b) for a, b in zip(signs, signs[1:])]
    return lb_lib.ranks(e)


def stat(ranks_list, ks):
    return float(np.mean([r[k - 1] for r, k in zip(ranks_list, ks)]))


def p_uniform(ranks_list, obs, rng, nsim=20000):
    """One-sided Monte-Carlo p under Null 1 (split uniform over the text's junctions)."""
    sims = np.zeros(nsim)
    for r in ranks_list:
        sims += r[rng.integers(0, len(r), nsim)]
    sims /= len(ranks_list)
    return float((1 + np.sum(sims >= obs - 1e-12)) / (nsim + 1))


def fnum(x):
    try:
        return float(x)
    except Exception:
        return 0.0
