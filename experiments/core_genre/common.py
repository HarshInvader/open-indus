"""Shared code for core_genre (red team of naming_sim + genre comparison).

Statistics are the FROZEN naming_sim definitions (experiments/naming_sim/stats.py, imported, not copied).
Unit = distinct type (tuple of elements). Indus cores = naming_sim/core_semantics definition (fit.indus).

Helpers
  indus_cores(split)            naming_sim target (functional-grammar cores)
  indus_texts(split, ...)       grammar-free alternatives (whole texts, numerals dropped, edge-stripped segments)
  merge_inventory(types, q, rng, slot_preserving=False)
                                map the elements of a sample onto len(q) classes whose token-frequency profile
                                matches the profile q (Indus dev core signs), randomly (homography / rebus model)
  mean_stats(types, n, B, seed, cls, length_mix=None)
"""
import sys, json
from pathlib import Path
from collections import Counter
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments" / "naming_sim"))
sys.path.insert(0, str(ROOT / "experiments" / "core_semantics"))
sys.path.insert(0, str(ROOT / "experiments" / "typology"))
import stats as S          # noqa  frozen naming_sim statistics
import names as N          # noqa  naming_sim real lists

PRIMARY6 = ["len1", "standalone", "both_orders", "hfi", "pol_ex", "both_pos"]
PRIMARY5 = ["standalone", "both_orders", "hfi", "pol_ex", "both_pos"]
NS_SCALES = json.load(open(ROOT / "experiments/naming_sim/realcmp_scales.json"))["scales"]
NAME_LISTS = ["old_english", "old_high_german", "old_norse", "greek", "sanskrit", "egyptian", "ur3",
              "chinese_given", "chinese_full", "plains", "sangam"]


def indus_cores(split="dev"):
    from fit import indus
    return indus(split)


def numeral_signs():
    import pandas as pd
    lex = pd.read_csv(ROOT / "experiments/functional_reading/lexicon.csv")
    lex = lex[lex["kind"] == "sign"]
    return {r.item for r in lex.itertuples() if str(r.roles).startswith("NUMERAL")}


def _dev_ho(split):
    from corpus.load import dev_heldout
    d, h = dev_heldout(version=2)
    return {"dev": d, "heldout": h}[split]


def indus_texts(split="dev", mode="whole"):
    """Grammar-free 'cores'. Texts with a break '#' are dropped; line breaks '|' removed.
    mode: whole   = whole distinct text
          nonum   = whole text with numeral signs deleted
          edge    = numerals and positional frame signs removed, text split at them into segments
                    (frame sign = >= 10 occurrences in dev texts of length >= 2 and >= 50% of them text-initial
                    or >= 50% text-final; derived from DEV only, no grammar)
          top10   = numerals and the 10 most frequent dev signs removed, split into segments
    """
    num = numeral_signs()
    texts = [[s for s in t["seq"] if s != "|"] for t in _dev_ho(split) if "#" not in t["seq"]]
    texts = [t for t in texts if t]
    if mode == "whole":
        return sorted({tuple(t) for t in texts})
    if mode == "nonum":
        return sorted({tuple(s for s in t if s not in num) for t in texts} - {()})
    dev = [[s for s in t["seq"] if s != "|"] for t in _dev_ho("dev") if "#" not in t["seq"]]
    if mode == "edge":
        occ, ini, fin = Counter(), Counter(), Counter()
        for t in dev:
            if len(t) < 2:
                continue
            for i, s in enumerate(t):
                occ[s] += 1; ini[s] += i == 0; fin[s] += i == len(t) - 1
        drop = {s for s in occ if occ[s] >= 10 and (ini[s] / occ[s] >= .5 or fin[s] / occ[s] >= .5)} | num
    elif mode == "top10":
        f = Counter(s for t in dev for s in t if s not in num)
        drop = {s for s, _ in f.most_common(10)} | num
    else:
        raise ValueError(mode)
    segs = set()
    for t in texts:
        cur = []
        for s in t + [None]:
            if s is None or s in drop:
                if cur:
                    segs.add(tuple(cur))
                cur = []
            else:
                cur.append(s)
    return sorted(segs), sorted(drop - num)


def indus_profile(split="dev"):
    """Token-frequency profile (descending shares) of Indus core signs."""
    t, _ = indus_cores(split)
    f = np.array(sorted(Counter(e for x in t for e in x).values(), reverse=True), float)
    return f / f.sum()


def merge_inventory(types, q, rng, slot_preserving=False):
    """Map the elements of `types` onto K = len(q) classes. Elements are taken in descending token frequency and
    each goes to a class drawn with probability proportional to its remaining capacity (capacity_k = q_k * total
    tokens), so the merged profile follows q. slot_preserving: elements are first split by slot preference in
    two-element types (first share > 0.8 / < 0.2 / other) and merged only within their group (capacities split
    in proportion to group token mass). Returns distinct merged types (tuples of 'c<k>')."""
    types = [tuple(t) for t in types]
    f = Counter(e for t in types for e in t)
    tot = sum(f.values())
    K = len(q)
    if not slot_preserving:
        groups = {"all": list(f)}
    else:
        o, i = Counter(), Counter()
        for t in types:
            if len(t) == 2 and t[0] != t[1]:
                o[t[0]] += 1; i[t[1]] += 1
        groups = {"first": [], "second": [], "other": []}
        for e in f:
            d = o[e] + i[e]
            g = "other" if d == 0 else ("first" if o[e] / d > .8 else ("second" if o[e] / d < .2 else "other"))
            groups[g].append(e)
    mapping = {}
    # allot classes to groups in proportion to token mass (at least 1 each if non-empty)
    gm = {g: sum(f[e] for e in es) for g, es in groups.items() if es}
    order = sorted(gm, key=lambda g: -gm[g])
    alloc = {g: max(1, int(round(K * gm[g] / tot))) for g in order}
    while sum(alloc.values()) > K:
        g = max(alloc, key=lambda x: alloc[x]); alloc[g] -= 1
    while sum(alloc.values()) < K:
        g = order[0]; alloc[g] += 1
    start = 0
    for g in order:
        k = alloc[g]
        qq = np.array(q[start:start + k]) if not slot_preserving else rng.permutation(q)[:k]
        qq = qq / qq.sum()
        cap = qq * gm[g]
        es = sorted(groups[g], key=lambda e: -f[e])
        for e in es:
            w = np.clip(cap, 0, None)
            if w.sum() <= 0:
                w = qq.copy()
            j = rng.choice(k, p=w / w.sum())
            cap[j] -= f[e]
            mapping[e] = f"{g[0]}{start + j}"
        start += k
    return sorted({tuple(mapping[e] for e in t) for t in types})


def strata(types, Lmax=None):
    by = {1: [], 2: [], 3: [], 4: []}
    for t in types:
        L = len(t)
        if Lmax and L > Lmax:
            continue
        by[min(L, 4)].append(t)
    return by


def length_counts(types, n):
    by = strata(types)
    tot = sum(len(v) for v in by.values())
    c = {L: int(round(n * len(by[L]) / tot)) for L in by}
    c[2] += n - sum(c.values())
    return c


def sample_types(types, n, rng, counts=None, Lmax=None):
    """n distinct types; if counts given (dict length-stratum -> count), stratified to those counts.
    Returns None if the system cannot supply them."""
    types = list(types)
    if counts is None:
        if len(types) < n:
            return None
        idx = rng.choice(len(types), n, replace=False)
        return [types[k] for k in idx]
    by = strata(types, Lmax)
    out = []
    for L, c in counts.items():
        if len(by[L]) < c:
            return None
        idx = rng.choice(len(by[L]), c, replace=False)
        out += [by[L][k] for k in idx]
    return out


def feasible_n(types, counts_share, Lmax=None):
    by = strata(types, Lmax)
    return min((len(by[L]) / s if s > 0 else np.inf) for L, s in counts_share.items())


def rows_stats(types, n, B, seed, cls=None, counts=None, Lmax=None, nnull=20):
    rng = np.random.default_rng(seed)
    rows = []
    for _ in range(B):
        s = sample_types(types, n, rng, counts, Lmax)
        if s is None:
            return None
        rows.append(S.compute(s, rng, cls, nnull))
    return rows


def mean_of(rows, keys=None):
    keys = keys or S.KEYS
    out = {}
    for k in keys:
        v = np.array([r[k] for r in rows], float)
        out[k] = float(np.nanmean(v)) if np.isfinite(v).any() else np.nan
    return out


def distance(ma, mb, sc, keys):
    z = [((ma[k] - mb[k]) / sc[k]) ** 2 for k in keys if np.isfinite(ma[k]) and np.isfinite(mb[k])]
    return float(np.sqrt(np.mean(z))) if z else np.nan


def jl_types(path, Lmax=17):
    out = set()
    for l in open(path, encoding="utf-8"):
        s = tuple(json.loads(l)["seq"])
        if 1 <= len(s) <= Lmax:
            out.add(s)
    return sorted(out)


def rnd(x, d=3):
    if isinstance(x, dict):
        return {k: rnd(v, d) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [rnd(v, d) for v in x]
    if isinstance(x, (float, np.floating)):
        return None if not np.isfinite(x) else round(float(x), d)
    return x


def edge_strip(types, drop_extra=(), minocc=10, share=.5):
    """Grammar-free frame stripping, the same rule as indus_texts(mode='edge'), applied to any system's own units:
    an element is a positional frame element if it occurs >= minocc times in units of length >= 2 and >= share of
    those occurrences are unit-initial or >= share unit-final. Frame elements (and drop_extra) are removed and
    units are split at them. Returns (segments, frame_elements)."""
    occ, ini, fin = Counter(), Counter(), Counter()
    for t in types:
        if len(t) < 2:
            continue
        for i, s in enumerate(t):
            occ[s] += 1; ini[s] += i == 0; fin[s] += i == len(t) - 1
    drop = {s for s in occ if occ[s] >= minocc and (ini[s] / occ[s] >= share or fin[s] / occ[s] >= share)}
    drop |= set(drop_extra)
    segs = set()
    for t in types:
        cur = []
        for s in list(t) + [None]:
            if s is None or s in drop:
                if cur:
                    segs.add(tuple(cur))
                cur = []
            else:
                cur.append(s)
    return sorted(segs), sorted(drop - set(drop_extra))
