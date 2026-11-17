"""Typology metrics on a set of distinct name cores (tuples of signs), and matched sampling.

All positional metrics use cores of length >= 2 only.  Unit = distinct core type.
"""
import math
from collections import Counter, defaultdict
import numpy as np

MIN_OCC = 5      # signs with >= MIN_OCC occurrences enter per-sign metrics
MIN_OCC_FLOAT = 3


def _pos(i, L):
    return "I" if i == 0 else ("F" if i == L - 1 else "M")


def chao2(incidence_counts):
    """incidence_counts: list of #sampling units containing each species. Bias-corrected Chao2."""
    c = Counter(incidence_counts)
    S, q1, q2 = len(incidence_counts), c.get(1, 0), c.get(2, 0)
    return S + q1 * (q1 - 1) / (2 * (q2 + 1))


def metrics(cores):
    """cores: list of distinct tuples, all len >= 2."""
    occ = Counter(); posc = defaultdict(Counter); starts = defaultdict(set); ends = defaultdict(set)
    partners = defaultdict(set)
    bigr_cores = defaultdict(set); bstarts = defaultdict(set); bends = defaultdict(set)
    pair_inc = Counter()
    ntok = 0
    for ci, c in enumerate(cores):
        L = len(c); ntok += L
        for i, s in enumerate(c):
            occ[s] += 1; posc[s][_pos(i, L)] += 1
            starts[s].add(i); ends[s].add(L - 1 - i)
            partners[s].update(x for j, x in enumerate(c) if j != i)
        for i in range(L - 1):
            b = c[i:i + 2]
            bigr_cores[b].add(ci); bstarts[b].add(i); bends[b].add(L - 2 - i)
        for pr in {tuple(sorted((c[i], c[j]))) for i in range(L) for j in range(i + 1, L)}:
            pair_inc[pr] += 1
    freq = [s for s in occ if occ[s] >= MIN_OCC]
    H = []; W = []; fixed = 0; ftok = 0
    for s in freq:
        p = np.array(list(posc[s].values()), float); p /= p.sum()
        H.append(-(p * np.log2(p)).sum() / math.log2(3)); W.append(occ[s])
        ftok += occ[s]
        if p.max() >= 0.9:
            fixed += occ[s]
    fl = [s for s in occ if occ[s] >= MIN_OCC_FLOAT]
    float1 = np.mean([len(starts[s]) >= 2 and len(ends[s]) >= 2 for s in fl]) if fl else np.nan
    rb = [b for b in bigr_cores if len(bigr_cores[b]) >= 2]
    float2 = np.mean([len(bstarts[b]) >= 2 and len(bends[b]) >= 2 for b in rb]) if rb else np.nan
    msets = {tuple(sorted(c)) for c in cores}
    pd_ = np.mean([len(partners[s]) / occ[s] for s in freq]) if freq else np.nan
    npairs = len(pair_inc)
    ch = chao2(list(pair_inc.values()))
    V = len(occ)
    return dict(
        H_pos=float(np.average(H, weights=W)) if H else np.nan,
        fixed_share=fixed / ftok if ftok else np.nan,
        float_sign=float(float1),
        float_bigram=float(float2),
        recurring_bigram_share=len(rb) / max(1, len(bigr_cores)),
        anagram=1 - len(msets) / len(cores),
        partner_div=float(pd_),
        types_per_token=V / ntok,
        pair_completeness=npairs / ch if ch else np.nan,
        pair_density=ch / (V * (V - 1) / 2) if V > 1 else np.nan,
        top10_share=sum(n for _, n in occ.most_common(10)) / ntok,
    )


def whole_word_metrics(all_cores):
    """Natural-length sample incl. length-1 cores: share of length-1 cores, and share of sign tokens in
    longer cores whose sign also occurs as a length-1 core (cores built of whole-word elements)."""
    one = {c[0] for c in all_cores if len(c) == 1}
    long_ = [c for c in all_cores if len(c) >= 2]
    tok = [s for c in long_ for s in c]
    allin = np.mean([all(s in one for s in c) for c in long_]) if long_ else np.nan
    return dict(len1_share=sum(len(c) == 1 for c in all_cores) / len(all_cores),
                standalone_tok=float(np.mean([s in one for s in tok])) if tok else np.nan,
                fully_decomposable=float(allin))


def length_strata(cores, cap=5):
    by = defaultdict(list)
    for c in cores:
        by[min(len(c), cap)].append(c)
    return by


def matched_sample(ref_cores, target_lens, rng, cap=5):
    """Draw distinct cores without replacement from ref_cores with the length multiset target_lens
    (lengths capped at `cap`).  Returns None if a stratum is too small."""
    by = length_strata(ref_cores, cap)
    need = Counter(min(L, cap) for L in target_lens)
    out = []
    for L, n in need.items():
        pool = by.get(L, [])
        if len(pool) < n:
            return None
        idx = rng.choice(len(pool), n, replace=False)
        out += [pool[i] for i in idx]
    return out


def max_feasible(ref_cores, target_lens, cap=5):
    by = length_strata(ref_cores, cap)
    need = Counter(min(L, cap) for L in target_lens)
    tot = sum(need.values())
    return min(int(len(by.get(L, [])) / (n / tot)) for L, n in need.items())


def shuffle_across(cores, rng):
    """Permute all sign tokens across cores, keeping core lengths (destroys position/pairing, keeps
    inventory and frequencies)."""
    toks = [s for c in cores for s in c]
    rng.shuffle(toks)
    out, k = [], 0
    for c in cores:
        out.append(tuple(toks[k:k + len(c)])); k += len(c)
    return out


REL = [("H_pos", "H_rel"), ("recurring_bigram_share", "bigram_rel"), ("partner_div", "partner_rel"),
       ("float_sign", "float_rel"), ("anagram", "anagram_rel")]


def metrics_rel(cores, rng, nnull=2):
    m = metrics(cores)
    nulls = [metrics(shuffle_across(cores, rng)) for _ in range(nnull)]
    for k, kr in REL:
        nv = np.nanmean([n[k] for n in nulls])
        m[kr] = m[k] / nv if nv else np.nan
    m["fixed_excess"] = m["fixed_share"] - np.nanmean([n["fixed_share"] for n in nulls])
    return m
