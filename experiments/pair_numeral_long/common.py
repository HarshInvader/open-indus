"""Shared helpers for pair_numeral_long (F1 pair graph, F2 numeral distributions, F6 long-text parse).

Read-only reuse of other areas' code:
  * experiments/core_semantics/cs_data.py  (name cores = frozen typology definition; reference name corpora)
  * experiments/typology/corpora.py         (Chinese names)
  * experiments/functional_reading/fr.py    (stroke numeral tables, frozen grammar)
Unit everywhere: distinct texts (dev_heldout(version=2)).
Run scripts from the repo root.
"""
import sys, json
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
for p in (ROOT, ROOT / "experiments" / "core_semantics", ROOT / "experiments" / "typology",
          ROOT / "experiments" / "functional_reading"):
    sys.path.insert(0, str(p))
import os
import corpus.load as _CL
if os.environ.get("PNL_DRYRUN"):   # code check only: 'held-out' = last quarter of dev; real held-out never read
    _orig = _CL.dev_heldout
    def _dry(texts=None, version=2):
        d, _ = _orig(texts, version); k = len(d) * 3 // 4
        return d[:k], d[k:]
    _CL.dev_heldout = _dry
from corpus.load import dev_heldout, runs, icit_texts, m77_texts, distinct  # noqa


def nsig(t):
    return sum(1 for s in t["seq"] if s not in ("|", "#"))


# =============================================================== F1: pair graphs
def indus_pair_types(split):
    """Adjacent sign pairs inside name cores, counted once per distinct text -> Counter{(a,b): n_texts}."""
    import cs_data
    occ = cs_data.indus_occurrences(split)
    seen, pairs = set(), Counter()
    for o in occ:
        c = o["core"]
        for a, b in zip(c, c[1:]):
            k = (o["text"], a, b)
            if k in seen:
                continue
            seen.add(k)
            pairs[(a, b)] += 1
    return pairs


def ref_pairs(name, seed=0):
    """Reference two-element name corpora -> list of distinct (first, second) pair types."""
    import cs_data, corpora as TY
    if name == "sanskrit":
        two, _ = cs_data.sanskrit_names(); return list(two)
    if name == "ur3":
        two, _ = cs_data.ur3_names(); return list(two)
    if name == "chinese_given":          # two-character given names (binome-like, one inventory)
        two, _ = cs_data.chinese_given(); return list(two)
    if name == "chinese_clan":           # surname + first given character (clan + given)
        d = TY.chinese_names(given_only=False)
        return list({(c[0], c[1]) for c in d})
    raise KeyError(name)


def _zipf(n, a=1.0):
    p = 1 / np.arange(1, n + 1) ** a
    return p / p.sum()


def sim_pairs(kind, n_types, rng, q=1.0):
    """Simulated pair-type sets of exactly n_types distinct types.
    emblem_x_name : emblem inventory (40) -> individual inventory (200), fixed order (two inventories, directed)
    blazon        : field tincture -> charge, charge -> tincture (7 tinctures, 120 charges): two inventories that
                    alternate, tinctures in both positions (undirected bipartite, weak direction)
    compound      : one inventory (150), random pairs, each pair type with its own fixed order (lexicalised)
    mix           : a share q of types drawn as emblem_x_name, the rest as compound (calibration curve)."""
    out = set()
    pe, pn, pc = _zipf(40), _zipf(200), _zipf(150)
    tinct = _zipf(7, 1.2); charge = _zipf(120)
    while len(out) < n_types:
        k = kind
        if kind == "mix":
            k = "emblem_x_name" if rng.random() < q else "compound"
        if k == "emblem_x_name":
            out.add((f"E{rng.choice(40, p=pe)}", f"N{rng.choice(200, p=pn)}"))
        elif k == "blazon":
            t, c = f"T{rng.choice(7, p=tinct)}", f"C{rng.choice(120, p=charge)}"
            out.add((t, c) if rng.random() < 0.5 else (c, t))
        elif k == "compound":
            a, b = rng.choice(150, 2, p=pc, replace=False)
            out.add((f"X{a}", f"X{b}"))
    return list(out)


def degrees(edges):
    o, i = Counter(), Counter()
    for a, b in edges:
        o[a] += 1; i[b] += 1
    return o, i


def polarization(edges, kmin=3):
    """Sum|out-in| / sum(out+in) over signs with total degree >= kmin (distinct pair types, self-loops dropped)."""
    edges = [e for e in edges if e[0] != e[1]]
    o, i = degrees(edges)
    num = den = 0
    for s in set(o) | set(i):
        d = o[s] + i[s]
        if d >= kmin:
            num += abs(o[s] - i[s]); den += d
    return num / den if den else np.nan


def pos_entropy(edges, kmin=3):
    """Degree-weighted mean binary entropy of (first, second) position per sign."""
    edges = [e for e in edges if e[0] != e[1]]
    o, i = degrees(edges)
    h = w = 0
    for s in set(o) | set(i):
        d = o[s] + i[s]
        if d >= kmin:
            p = o[s] / d
            hh = 0 if p in (0, 1) else -(p * np.log2(p) + (1 - p) * np.log2(1 - p))
            h += d * hh; w += d
    return h / w if w else np.nan


def both_share(edges, kmin=3, lo=0.2, hi=0.8):
    edges = [e for e in edges if e[0] != e[1]]
    o, i = degrees(edges)
    S = [s for s in set(o) | set(i) if o[s] + i[s] >= kmin]
    return np.mean([lo <= o[s] / (o[s] + i[s]) <= hi for s in S]) if S else np.nan


def _cut_search(edges, directed, rng, restarts=8, iters=None):
    """Local search for a 2-partition maximising (directed: edges F->S) / (undirected: edges across)."""
    edges = [e for e in edges if e[0] != e[1]]
    nodes = sorted({s for e in edges for s in e})
    ix = {s: k for k, s in enumerate(nodes)}
    E = np.array([(ix[a], ix[b]) for a, b in edges])
    n = len(nodes)
    nb_out = defaultdict(list); nb_in = defaultdict(list)
    for a, b in E:
        nb_out[a].append(b); nb_in[b].append(a)
    best = 0
    for r in range(restarts):
        if directed and r == 0:   # start from degree direction
            o, i = Counter(E[:, 0]), Counter(E[:, 1])
            side = np.array([o[k] >= i[k] for k in range(n)], int)   # 1 = first
        else:
            side = rng.integers(0, 2, n)
        improved = True
        while improved:
            improved = False
            for v in rng.permutation(n):
                # gain of flipping v
                if directed:
                    def score_v(sv):
                        sc = 0
                        for w in nb_out[v]: sc += (sv == 1 and side[w] == 0)
                        for w in nb_in[v]: sc += (side[w] == 1 and sv == 0)
                        return sc
                else:
                    def score_v(sv):
                        return sum(side[w] != sv for w in nb_out[v]) + sum(side[w] != sv for w in nb_in[v])
                if score_v(1 - side[v]) > score_v(side[v]):
                    side[v] = 1 - side[v]; improved = True
        if directed:
            sc = np.sum((side[E[:, 0]] == 1) & (side[E[:, 1]] == 0))
        else:
            sc = np.sum(side[E[:, 0]] != side[E[:, 1]])
        best = max(best, sc)
    return best / len(E)


def dicut(edges, rng):
    return _cut_search(edges, True, rng)


def maxcut(edges, rng):
    return _cut_search(edges, False, rng)


def orient_null(edges, rng):
    """Same undirected pairs, orientation of each pair type randomised."""
    return [(a, b) if rng.random() < 0.5 else (b, a) for a, b in edges]


def swap_null(edges, rng, nswap=None, directed=True):
    """Degree-preserving edge swaps (directed: keeps every in- and out-degree). No self-loops, no duplicates
    (for directed, a->b and b->a may coexist)."""
    E = [tuple(e) for e in edges if e[0] != e[1]]
    S = set(E)
    m = len(E); nswap = nswap or 10 * m
    for _ in range(nswap):
        i, j = rng.integers(0, m, 2)
        (a, b), (c, d) = E[i], E[j]
        if not directed and rng.random() < 0.5:
            c, d = d, c
        if a == d or c == b or len({a, b, c, d}) < 4 and (a == c or b == d):
            continue
        n1, n2 = (a, d), (c, b)
        if n1 in S or n2 in S:
            continue
        if not directed and ((d, a) in S or (b, c) in S):
            continue
        S.discard(E[i]); S.discard(E[j]); S.add(n1); S.add(n2)
        E[i], E[j] = n1, n2
    return E


def graph_stats(edges, rng, nnull=200, kmin=3):
    """Observed metrics, each with its null: POL/H/both vs orientation null; DICUT vs directed swaps;
    MAXCUT vs undirected swaps.  Excess = (obs - null)/(1 - null) for POL, DICUT, MAXCUT."""
    edges = [e for e in edges if e[0] != e[1]]
    obs = dict(pol=polarization(edges, kmin), H=pos_entropy(edges, kmin), both=both_share(edges, kmin),
               dicut=dicut(edges, rng), maxcut=maxcut(edges, rng), n_edges=len(edges),
               n_nodes=len({s for e in edges for s in e}))
    npol = np.array([polarization(orient_null(edges, rng), kmin) for _ in range(nnull)])
    nH = np.array([pos_entropy(orient_null(edges, rng), kmin) for _ in range(nnull)])
    nn = max(20, nnull // 10)
    ndc = np.array([dicut(swap_null(edges, rng), rng) for _ in range(nn)])
    nmc = np.array([maxcut(swap_null(edges, rng, directed=False), rng) for _ in range(nn)])
    out = dict(obs)
    for k, arr, hi in (("pol", npol, True), ("H", nH, False), ("dicut", ndc, True), ("maxcut", nmc, True)):
        m = float(arr.mean())
        p = (np.sum(arr >= obs[k]) + 1) / (len(arr) + 1) if hi else (np.sum(arr <= obs[k]) + 1) / (len(arr) + 1)
        out[k + "_null"] = m; out[k + "_null_sd"] = float(arr.std()); out[k + "_p"] = float(p)
        if k != "H":
            out[k + "_excess"] = (obs[k] - m) / (1 - m) if m < 1 else np.nan
    return out


def order_rule_accuracy(train_edges_counter, test_counter, kmin=3, margin=0.0):
    """Predict order of test pair types not seen (either order) in train from train out-shares.
    Returns (n_correct, n_scored, details)."""
    tr = [e for e in train_edges_counter if e[0] != e[1]]
    o, i = degrees(tr)
    trs = set(tr) | {(b, a) for a, b in tr}
    corr = n = 0; det = []
    for (a, b), c in test_counter.items():
        if a == b or (a, b) in trs:
            continue
        da, db = o[a] + i[a], o[b] + i[b]
        if da < kmin or db < kmin:
            continue
        pa, pb = o[a] / da, o[b] / db
        if abs(pa - pb) <= margin:
            continue
        n += 1; ok = pa > pb; corr += ok
        det.append((a, b, round(pa, 2), round(pb, 2), bool(ok)))
    return corr, n, det


# =============================================================== F2: numerals
def stroke_tables():
    import fr
    short = dict(fr.SHORT)            # M99/M101 (short-2, connective) already excluded upstream
    tall = dict(fr.TALL)
    return short, tall


def numeral_contexts(texts):
    """For each distinct text, numeral sign followed/preceded by a non-numeral sign inside a break-free run.
    Returns list of dicts: cls ('S' short / 'T' tall), value, numsign, head (sign after), prev (sign before),
    cluster (True if the numeral is adjacent to another numeral), text index, site, object_type."""
    short, tall = stroke_tables()
    out = []
    for ti, t in enumerate(texts):
        for r in runs(t["seq"]):
            for k, s in enumerate(r):
                if s in short:
                    cls, v = "S", short[s]
                elif s in tall:
                    cls, v = "T", tall[s]
                else:
                    continue
                nxt = r[k + 1] if k + 1 < len(r) else "$"
                prv = r[k - 1] if k > 0 else "^"
                isnum = lambda x: x in short or x in tall
                out.append(dict(cls=cls, value=v, numsign=s, head=nxt if not isnum(nxt) else None,
                                prev=prv if not isnum(prv) else None, cluster=isnum(nxt) or isnum(prv),
                                ti=ti, site=t.get("site"), object_type=t.get("object_type")))
    return out
