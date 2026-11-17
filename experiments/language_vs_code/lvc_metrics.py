"""Candidate language-vs-code discriminators, each standardised against a structure-preserving null
computed on the same sample. All functions take a list of texts (lists of sign tokens).

D1a edge_ldd   MI(first sign; last sign) in texts of length >= 3, z vs doublet-preserving shuffle
               (Altschul-Erickson Eulerian shuffle of the whole corpus with text separators: keeps every
               adjacent pair count, incl. which signs start and end texts). Excess = dependency between
               opener and closer that adjacent transitions do not explain.
D1b skip_cmi   I(X_i; X_i+2 | X_i+1) pooled over all trigrams, z vs the same doublet shuffle.
D2a mal_surp   Menzerath analogue: Spearman(text length, mean unigram surprisal of its signs), z vs
               token permutation across texts (lengths kept). Negative = longer texts use 'smaller'
               (more frequent) signs.
D2b mal_seg    Menzerath on induced segments: Spearman(#segments, mean segment length), z vs token
               permutation re-segmented. Negative = more segments -> shorter segments.
D3  open_edge  log(types per token in text interiors / types per token at text edges), equal token
               samples. >0 = open interior vocabulary inside closed frame slots. (raw effect; null ~0)
D3b heaps      Heaps exponent of the sign inventory over the sample (slope of log types vs log tokens
               in the second half of a random text order).
D4  abbrev     Zipf's law of abbreviation on induced segments: Spearman(segment-type frequency,
               length in signs), z vs token permutation re-segmented.
D5  repeat     log(share of texts with a repeated sign / same share under token permutation).
"""
import math, random
from collections import Counter, defaultdict
import numpy as np
from scipy.stats import spearmanr


# ---------------- nulls ----------------
def doublet_shuffle(texts, rng):
    """Uniform random Eulerian circuit over the multigraph of adjacent pairs (separator '#')."""
    SEP = "\x00SEP"
    seq = [SEP]
    for t in texts:
        seq += list(t) + [SEP]
    out_edges = defaultdict(list)
    for a, b in zip(seq, seq[1:]):
        out_edges[a].append(b)
    root = SEP
    # Wilson's algorithm on reversed sense: choose for each v != root a last out-edge forming an
    # arborescence directed toward root.
    in_tree = {root}; nxt = {}
    for u in list(out_edges):
        cur = u
        while cur not in in_tree:
            nxt[cur] = rng.randrange(len(out_edges[cur]))
            cur = out_edges[cur][nxt[cur]]
        cur = u
        while cur not in in_tree:
            in_tree.add(cur)
            cur = out_edges[cur][nxt[cur]]
    order = {}
    for v, es in out_edges.items():
        idx = list(range(len(es)))
        if v != root:
            last = nxt[v]; idx.remove(last); rng.shuffle(idx); idx.append(last)
        else:
            rng.shuffle(idx)
        order[v] = [es[i] for i in idx]
    ptr = defaultdict(int); cur = root; walk = [root]
    total = len(seq) - 1
    for _ in range(total):
        e = order[cur][ptr[cur]]; ptr[cur] += 1; walk.append(e); cur = e
    res, t = [], []
    for s in walk[1:]:
        if s == SEP:
            if t: res.append(t)
            t = []
        else:
            t.append(s)
    return res


def token_perm(texts, rng):
    toks = [s for t in texts for s in t]; rng.shuffle(toks)
    out, i = [], 0
    for t in texts:
        out.append(toks[i:i + len(t)]); i += len(t)
    return out


# ---------------- raw statistics ----------------
def _mi(pairs):
    n = len(pairs)
    if n == 0: return 0.0
    cxy = Counter(pairs); cx = Counter(a for a, _ in pairs); cy = Counter(b for _, b in pairs)
    return sum(c / n * math.log2(c * n / (cx[a] * cy[b])) for (a, b), c in cxy.items())


def edge_mi(texts):
    return _mi([(t[0], t[-1]) for t in texts if len(t) >= 3])


def skip_cmi(texts):
    tri = [(t[i], t[i + 1], t[i + 2]) for t in texts for i in range(len(t) - 2)]
    n = len(tri)
    if n == 0: return 0.0
    cxyz = Counter(tri); cxz = Counter((a, b) for a, b, _ in tri); cyz = Counter((b, c) for _, b, c in tri)
    cz = Counter(b for _, b, _ in tri)
    return sum(c / n * math.log2(c * cz[b] / (cxz[(a, b)] * cyz[(b, cc)])) for (a, b, cc), c in cxyz.items())


def mal_surp(texts):
    cnt = Counter(s for t in texts for s in t); N = sum(cnt.values())
    L, S = [], []
    for t in texts:
        if len(t) >= 2:
            L.append(len(t)); S.append(np.mean([-math.log2(cnt[s] / N) for s in t]))
    return spearmanr(L, S)[0] if len(set(L)) > 1 else 0.0


def segment(texts, min_count=3, min_pmi=2.0):
    cnt = Counter(s for t in texts for s in t); N = sum(cnt.values())
    bg = Counter((a, b) for t in texts for a, b in zip(t, t[1:]))
    join = {p for p, c in bg.items() if c >= min_count and math.log2(c * N / (cnt[p[0]] * cnt[p[1]])) >= min_pmi}
    segs = []
    for t in texts:
        cur, ts = [t[0]], []
        for a, b in zip(t, t[1:]):
            if (a, b) in join: cur.append(b)
            else: ts.append(tuple(cur)); cur = [b]
        ts.append(tuple(cur)); segs.append(ts)
    return segs


def mal_seg(texts, segs=None):
    segs = segs or segment(texts)
    n = [len(s) for s in segs if len(s) >= 1]
    m = [np.mean([len(x) for x in s]) for s in segs if len(s) >= 1]
    return spearmanr(n, m)[0] if len(set(n)) > 1 and len(set(m)) > 1 else 0.0


def abbrev(texts, segs=None):
    segs = segs or segment(texts)
    c = Counter(x for s in segs for x in s)
    f = [v for v in c.values()]; l = [len(k) for k in c]
    return spearmanr(f, l)[0] if len(set(l)) > 1 else 0.0


def open_edge(texts, rng, reps=20):
    edge = [s for t in texts if len(t) >= 3 for s in (t[0], t[-1])]
    inner = [s for t in texts if len(t) >= 3 for s in t[1:-1]]
    m = min(len(edge), len(inner))
    if m < 20: return float("nan")
    v = []
    for _ in range(reps):
        a = len(set(rng.sample(inner, m))); b = len(set(rng.sample(edge, m)))
        v.append(math.log(a / b))
    return float(np.mean(v))


def heaps(texts, rng):
    t = list(texts); rng.shuffle(t)
    seen, xs, ys, n = set(), [], [], 0
    for x in t:
        for s in x:
            n += 1; seen.add(s)
        xs.append(n); ys.append(len(seen))
    h = len(xs) // 2
    return float(np.polyfit(np.log(xs[h:]), np.log(ys[h:]), 1)[0])


def rep_share(texts):
    T = [t for t in texts if len(t) >= 2]
    return np.mean([len(set(t)) < len(t) for t in T])


# ---------------- standardised battery ----------------
def _z(x, null):
    null = np.asarray(null, float); sd = null.std(ddof=1)
    return float((x - null.mean()) / sd) if sd > 0 else 0.0


def battery(texts, seed=0, K=20):
    rng = random.Random(seed)
    out = {}
    e, s = edge_mi(texts), skip_cmi(texts)
    ne, ns = [], []
    for _ in range(K):
        d = doublet_shuffle(texts, rng); ne.append(edge_mi(d)); ns.append(skip_cmi(d))
    out["edge_ldd"] = _z(e, ne); out["edge_ldd_excess_bits"] = e - float(np.mean(ne))
    out["skip_cmi"] = _z(s, ns); out["skip_cmi_excess_bits"] = s - float(np.mean(ns))
    segs = segment(texts)
    ms, mg, ab, rp = mal_surp(texts), mal_seg(texts, segs), abbrev(texts, segs), rep_share(texts)
    nms, nmg, nab, nrp = [], [], [], []
    for _ in range(K):
        p = token_perm(texts, rng); sp = segment(p)
        nms.append(mal_surp(p)); nmg.append(mal_seg(p, sp)); nab.append(abbrev(p, sp)); nrp.append(rep_share(p))
    out["mal_surp"] = _z(ms, nms); out["mal_surp_rho"] = ms
    out["mal_seg"] = _z(mg, nmg); out["mal_seg_rho"] = mg
    out["abbrev"] = _z(ab, nab); out["abbrev_rho"] = ab
    out["repeat"] = float(math.log((rp + 1e-3) / (np.mean(nrp) + 1e-3)))
    out["open_edge"] = open_edge(texts, rng)
    out["heaps"] = heaps(texts, rng)
    out["seg_share_multi"] = float(np.mean([len(x) > 1 for s in segs for x in s]))
    return out


METRICS = ["edge_ldd", "skip_cmi", "mal_surp", "mal_seg", "open_edge", "heaps", "abbrev", "repeat"]


# ---------------- length-matched sampling ----------------
def matched_sample(texts, target_lengths, rng):
    """Sample len(target_lengths) distinct texts whose lengths match target_lengths (nearest length
    used when a length bin runs out)."""
    by = defaultdict(list)
    for i, t in enumerate(texts): by[len(t)].append(i)
    for v in by.values(): rng.shuffle(v)
    out = []
    for L in target_lengths:
        for d in [0, 1, -1, 2, -2, 3, -3, 4, -4, 5, -5, 6, -6, 8, -8, 10, 12, 15, 20, 30, 50]:
            if by.get(L + d):
                out.append(texts[by[L + d].pop()]); break
    return out


if __name__ == "__main__":
    # unit test: doublet shuffle preserves pair counts
    rng = random.Random(1)
    T = [["a", "b", "c"], ["b", "c", "a", "b"], ["c"], ["a", "a", "b"]]
    D = doublet_shuffle(T, rng)
    def pairs(X):
        s = ["\x00SEP"] + [y for t in X for y in t + ["\x00SEP"]]
        return Counter(zip(s, s[1:]))
    assert pairs(T) == pairs(D), (T, D)
    print("doublet shuffle ok", D)
