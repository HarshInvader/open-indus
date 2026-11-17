"""Slot fingerprints and slot-to-slot alignment (shared by controls and the Indus run).

A corpus is a list of texts {"toks": [...], "slots": [...]} with one slot label per token.
A slot RUN is a maximal stretch of consecutive tokens with the same label; its FILLER is the token
tuple. All fingerprint features are label-free (they never look at what the tokens are, only at
equality between tokens), so relabelling signs leaves them unchanged.
"""
import math, random
from collections import Counter, defaultdict
import numpy as np
from scipy.optimize import linear_sum_assignment

FEATURES = ["occ", "pos", "first", "last", "len", "ttr100", "top1", "H100", "zipf", "short_ret",
            "recur", "share", "alone", "maxlift", "minlift"]
MIN_RUNS = 30          # a slot needs >= 30 runs in the sample to get a fingerprint
MIN_OCC = 0.02         # ... and to occur in >= 2% of texts
K_OCC = 100            # fixed number of runs for inventory measures


def runs(text):
    out = []; cur = None
    for t, s in zip(text["toks"], text["slots"]):
        if cur and cur[0] == s: cur[1].append(t)
        else:
            cur = [s, [t]]; out.append(cur)
    return [(s, tuple(f)) for s, f in out]


def _inventory(fillers, rng, k=K_OCC, reps=5):
    ttr, top1s, H = [], [], []
    for _ in range(reps):
        smp = rng.sample(fillers, k) if len(fillers) >= k else [rng.choice(fillers) for _ in range(k)]
        c = Counter(smp); n = len(smp)
        ttr.append(len(c) / n)
        p = np.array(list(c.values())) / n
        H.append(float(-(p * np.log2(p)).sum() / math.log2(k)))
    c = Counter(fillers)
    top1 = c.most_common(1)[0][1] / len(fillers)
    return float(np.mean(ttr)), top1, float(np.mean(H))


def _zipf(fillers):
    f = np.array(sorted(Counter(fillers).values(), reverse=True)[:50], float)
    if len(f) < 5: return 3.0
    r = np.arange(1, len(f) + 1)
    b = np.polyfit(np.log(r), np.log(f), 1)[0]
    return float(min(3.0, -b))


def fingerprints(texts, seed=0, min_runs=MIN_RUNS, min_occ=MIN_OCC):
    """returns {slot: np.array(len(FEATURES))}"""
    rng = random.Random(seed)
    R = [runs(t) for t in texts]
    N = len(R)
    present = defaultdict(int); nr = defaultdict(int); fill = defaultdict(list)
    posv = defaultdict(list); firstc = defaultdict(int); lastc = defaultdict(int)
    recur = defaultdict(int); alone = defaultdict(int)
    short_present = defaultdict(int); n_short = 0
    unit_slots = defaultdict(set)
    pair = Counter()
    for rr in R:
        labs = [s for s, _ in rr]; S = set(labs)
        short = len(rr) <= 2
        n_short += short
        for s in S:
            present[s] += 1
            if labs.count(s) >= 2: recur[s] += 1
            if len(S) == 1: alone[s] += 1
            if short: short_present[s] += 1
        for a in S:
            for b in S:
                if a < b: pair[(a, b)] += 1
        for j, (s, f) in enumerate(rr):
            nr[s] += 1; fill[s].append(f)
            for u in f: unit_slots[u].add(s)
            if len(rr) >= 2:
                posv[s].append(j / (len(rr) - 1))
                firstc[s] += (j == 0); lastc[s] += (j == len(rr) - 1)
    keep = [s for s in present if nr[s] >= min_runs and present[s] / N >= min_occ]
    out = {}
    for s in keep:
        occ = present[s] / N
        npos = len(posv[s])
        ttr, top1, H = _inventory(fill[s], rng)
        toks = [u for f in fill[s] for u in f]
        share = sum(len(unit_slots[u]) > 1 for u in toks) / len(toks)
        lifts = []
        for o in keep:
            if o == s: continue
            pab = pair[tuple(sorted((s, o)))] / N
            lifts.append(math.log(max(pab, 0.05 * occ * present[o] / N) / (occ * present[o] / N)))
        sr = (short_present[s] / max(n_short, 1)) / occ
        v = [occ, np.mean(posv[s]) if npos else 0.5,
             firstc[s] / npos if npos else 0.0, lastc[s] / npos if npos else 0.0,
             math.log(np.mean([len(f) for f in fill[s]])), ttr, top1, H, _zipf(fill[s]),
             math.log(max(sr, 0.05)), recur[s] / present[s], share, alone[s] / present[s],
             max(lifts) if lifts else 0.0, min(lifts) if lifts else 0.0]
        out[s] = np.array(v, float)
    return out


def subsample(texts, n, rng):
    return texts if len(texts) <= n else rng.sample(texts, n)


def standardize(fps_list):
    """z-score every feature over the pooled slots of all corpora given"""
    M = np.vstack([v for fp in fps_list for v in fp.values()])
    mu, sd = M.mean(0), M.std(0); sd[sd == 0] = 1
    return [{k: (v - mu) / sd for k, v in fp.items()} for fp in fps_list], (mu, sd)


def dist_matrix(A, B):
    a = sorted(A); b = sorted(B)
    D = np.array([[np.linalg.norm(A[x] - B[y]) / math.sqrt(len(FEATURES)) for y in b] for x in a])
    return a, b, D


def align(A, B, dummy=None):
    """Hungarian matching of slots of A onto slots of B. With dummy=c, each A-slot may stay
    unmatched at cost c. returns list of (a, b or None, d), mean matched distance"""
    a, b, D = dist_matrix(A, B)
    if dummy is not None:
        D2 = np.hstack([D, np.full((len(a), len(a)), dummy)])
    else:
        D2 = D
    r, c = linear_sum_assignment(D2)
    pairs = []
    for i, j in zip(r, c):
        pairs.append((a[i], b[j] if j < len(b) else None, float(D2[i, j])))
    matched = [d for _, y, d in pairs if y is not None]
    return pairs, (float(np.mean(matched)) if matched else float("nan")), (a, b, D)


def column_perm_null(A, B, n=2000, seed=0):
    """null for the optimal mean matched distance: permute each feature independently among A's
    slots (breaks which slot owns which values, keeps every feature's distribution)"""
    rng = np.random.default_rng(seed)
    keys = sorted(A); M = np.vstack([A[k] for k in keys])
    out = []
    for _ in range(n):
        P = M.copy()
        for j in range(P.shape[1]): P[:, j] = rng.permutation(P[:, j])
        _, m, _ = align({k: P[i] for i, k in enumerate(keys)}, B)
        out.append(m)
    return np.array(out)
