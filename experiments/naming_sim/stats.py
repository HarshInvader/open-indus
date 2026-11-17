"""Target statistics for a sample of distinct name types (tuples of elements). Unit = distinct name type.

Definitions (frozen in docs/prereg/naming_sim.md):
  len1        share of types with exactly one element                       (typology 'len-1 cores')
  len3p       share of types with three or more elements
  standalone  share of element tokens in types of length >= 2 whose element also occurs as a one-element
              type in the same sample                                        (typology 'standalone_tok')
  both_orders among unordered adjacent element pairs (from all types, AA dropped), share attested in both
              orders. Type-based version of 'recurring pairs keep fixed order' (core_semantics 'both orders,
              matched n'); token incidence is not available for most name lists.
  hfi         HFI_prod on two-element types: share whose second element is the more productive one
              (core_semantics/h1_head.metrics). 0.5 = no head direction.
  pol_ex      polarization excess on two-element types (pair_numeral_long/common.polarization vs the
              orientation null): 0 = one stock with free slot use, ~1 = two disjoint stocks.
  both_pos    share of elements (degree >= 3 in two-element types) used in both positions (0.2-0.8 first share).
  tpt         distinct elements per element token (inventory productivity).
  cls_self    log((obs+0.5)/(exp+0.5)) of class-internal pairs among adjacent pair types touching a lexical
              class (Indus: fish family; references: animal elements), exp under a shuffle of element tokens
              across pair positions. NaN if the class has < 10 pair types.
"""
import sys
from pathlib import Path
from collections import Counter
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT / "experiments" / "pair_numeral_long", ROOT / "experiments" / "core_semantics"):
    sys.path.insert(0, str(p))

KEYS = ["len1", "len3p", "standalone", "both_orders", "hfi", "pol_ex", "both_pos", "tpt", "cls_self"]
HUB = 4


def _degrees(edges):
    o, i = Counter(), Counter()
    for a, b in edges:
        o[a] += 1; i[b] += 1
    return o, i


def polarization(edges, kmin=3):
    edges = [e for e in edges if e[0] != e[1]]
    o, i = _degrees(edges)
    num = den = 0
    for s in set(o) | set(i):
        d = o[s] + i[s]
        if d >= kmin:
            num += abs(o[s] - i[s]); den += d
    return num / den if den else np.nan


def both_share(edges, kmin=3, lo=0.2, hi=0.8):
    edges = [e for e in edges if e[0] != e[1]]
    o, i = _degrees(edges)
    S = [s for s in set(o) | set(i) if o[s] + i[s] >= kmin]
    return float(np.mean([lo <= o[s] / (o[s] + i[s]) <= hi for s in S])) if S else np.nan


def pol_excess(two, rng, nnull=30):
    p = polarization(two)
    if np.isnan(p):
        return np.nan
    pn = np.mean([polarization([(a, b) if rng.random() < .5 else (b, a) for a, b in two]) for _ in range(nnull)])
    return float((p - pn) / (1 - pn)) if pn < 1 else np.nan


def hfi(two):
    two = [t for t in two if t[0] != t[1]]
    prod = Counter()
    for a, b in two:
        prod[a] += 1; prod[b] += 1
    w = [1 if prod[b] > prod[a] else 0 for a, b in two if prod[a] != prod[b]]
    return float(np.mean(w)) if w else np.nan


def cls_self(pairs, cls, rng, nnull=50):
    if not cls:
        return np.nan
    pairs = [p for p in pairs if p[0] != p[1]]
    touch = [p for p in pairs if p[0] in cls or p[1] in cls]
    if len(touch) < 10:
        return np.nan
    obs = sum(1 for a, b in touch if a in cls and b in cls) / len(touch)
    toks = [x for p in pairs for x in p]
    ex = []
    for _ in range(nnull):
        rng.shuffle(toks)
        sh = list(zip(toks[0::2], toks[1::2]))
        t2 = [p for p in sh if p[0] in cls or p[1] in cls]
        ex.append(sum(1 for a, b in t2 if a in cls and b in cls) / max(1, len(t2)))
    return float(np.log((obs * 100 + 0.5) / (np.mean(ex) * 100 + 0.5)))


def compute(types, rng, cls=None, nnull=30):
    types = [tuple(t) for t in types]
    one = {t[0] for t in types if len(t) == 1}
    long_ = [t for t in types if len(t) >= 2]
    tok = [s for t in long_ for s in t]
    alltok = [s for t in types for s in t]
    pairs = set()
    for t in long_:
        for a, b in zip(t, t[1:]):
            if a != b:
                pairs.add((a, b))
    und = Counter(frozenset(p) for p in pairs)
    two = sorted({t for t in types if len(t) == 2 and t[0] != t[1]})
    return dict(
        len1=sum(len(t) == 1 for t in types) / len(types),
        len3p=sum(len(t) >= 3 for t in types) / len(types),
        standalone=float(np.mean([s in one for s in tok])) if tok else np.nan,
        both_orders=float(np.mean([v == 2 for v in und.values()])) if und else np.nan,
        hfi=hfi(two),
        pol_ex=pol_excess(two, rng, nnull),
        both_pos=both_share(two),
        tpt=len(set(alltok)) / len(alltok),
        cls_self=cls_self(sorted(pairs), cls, rng, max(10, nnull)),
    )


def bootstrap(types, n, B, rng, cls=None):
    """B subsamples of n distinct types without replacement (n capped at the list size)."""
    types = list(types)
    n = min(n, len(types))
    rows = []
    for _ in range(B):
        idx = rng.choice(len(types), n, replace=False)
        rows.append(compute([types[k] for k in idx], rng, cls))
    return rows


def summarise(rows):
    out = {}
    for k in KEYS:
        v = np.array([r[k] for r in rows], float); v = v[~np.isnan(v)]
        out[k] = None if len(v) == 0 else dict(mean=round(float(v.mean()), 3), lo=round(float(np.percentile(v, 2.5)), 3),
                                               hi=round(float(np.percentile(v, 97.5)), 3), sd=round(float(v.std()), 4))
    return out
