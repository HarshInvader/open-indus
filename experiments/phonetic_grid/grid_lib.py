"""Automated Kober-triplet / Ventris-grid method.

A text is a tuple of opaque sign ids. The method:

1. Kober families. Two distinct texts that share a stem (longest common prefix of >= MIN_STEM signs)
   and then diverge, each leaving at most MAX_TAIL signs after the divergent ("bridge") sign, form a
   Kober pair. In a CV syllabary writing consonant-final stems + vowel-initial endings, the two
   bridge signs share the stem-final consonant (ko-no-SO / ko-no-SI-jo).
2. Consonant graph G_C: edge (a, b) weighted by the number of distinct stems on which a and b alternate.
3. Vowel profile: for every bridge occurrence in a Kober family, the tail that follows it (empty or the
   remaining 1..MAX_TAIL signs). Signs that sit in the same paradigm slot (same tail) across many stems
   share the ending vowel (Ventris: -si-jo, -ti-jo, -ri-jo all have /i/).
4. Grid: spectral clustering of G_C into K_c rows; agglomerative clustering of vowel profiles into
   K_v columns with a cannot-link penalty for signs already placed in the same row (one sign per cell).

direction='start' runs the same method on reversed texts (prefix alternation).
"""
from collections import Counter, defaultdict
import random
import numpy as np
from sklearn.cluster import SpectralClustering, AgglomerativeClustering
from sklearn.metrics import adjusted_rand_score
import networkx as nx

MIN_STEM = 2
MAX_TAIL = 1


def kober(texts, direction="end", min_stem=MIN_STEM, max_tail=MAX_TAIL, weight="count"):
    """Return (edges Counter{(a,b): n_stems}, slots list of (stem, bridge, tail), families dict)."""
    T = [tuple(t) if direction == "end" else tuple(reversed(t)) for t in texts]
    T = list(dict.fromkeys(T))  # distinct only
    fam = defaultdict(set)  # stem -> set of (bridge, tail)
    for t in T:
        n = len(t)
        for k in range(min_stem, n):
            tail = t[k + 1:]
            if len(tail) > max_tail:
                continue
            fam[t[:k]].add((t[k], tail))
    edges = Counter()
    slots = []
    families = {}
    for stem, ents in fam.items():
        bridges = {b for b, _ in ents}
        if len(bridges) < 2:
            continue
        # a stem only counts if the divergence happens here: entries must differ in bridge
        families[stem] = ents
        for b, tl in ents:
            slots.append((stem, b, tl))
        bl = sorted(bridges)
        w = 1.0
        if weight in ("norm", "lennorm"):
            w /= (len(bl) - 1)          # a formula stem with 10 continuations must not dominate
        if weight in ("len", "lennorm"):
            w *= (len(stem) - 1)        # longer shared stems are better evidence of one lexeme
        for i in range(len(bl)):
            for j in range(i + 1, len(bl)):
                edges[(bl[i], bl[j])] += w
    return edges, slots, families


PARAMS = dict(min_stem=MIN_STEM, max_tail=MAX_TAIL, weight="count")


def set_params(**kw):
    PARAMS.update(kw)


def stats(texts, direction="end", **kw):
    kw = {**PARAMS, **kw}
    edges, slots, fams = kober(texts, direction, **kw)
    n_alt = len(fams)
    n_trip = sum(1 for e in fams.values() if len({b for b, _ in e}) >= 3)
    G = graph(edges)
    w = Counter()
    for (a, b), c in edges.items():
        w[a] += c; w[b] += c
    tot = sum(w.values()) or 1
    top10 = sum(c for _, c in w.most_common(10)) / tot
    Q = modularity(G)
    return dict(alt_stems=n_alt, triplets=n_trip, edges=len(edges), edge_weight=sum(edges.values()),
                nodes=G.number_of_nodes(), top10_share=round(top10, 3), modularity=round(Q, 3))


def graph(edges, min_w=1):
    G = nx.Graph()
    for (a, b), c in edges.items():
        if c >= min_w:
            G.add_edge(a, b, weight=c)
    return G


def modularity(G, seed=0):
    if G.number_of_edges() < 2:
        return 0.0
    comms = nx.community.louvain_communities(G, weight="weight", seed=seed)
    return nx.community.modularity(G, comms, weight="weight")


def consonant_rows(edges, K, min_w=1, seed=0):
    G = graph(edges, min_w)
    nodes = sorted(G.nodes())
    if len(nodes) < max(K, 3):
        return {}
    A = nx.to_numpy_array(G, nodelist=nodes, weight="weight")
    A = A + 1e-3  # weak global link so the spectral embedding is defined on disconnected graphs
    np.fill_diagonal(A, 0)
    K = min(K, len(nodes) - 1)
    lab = SpectralClustering(n_clusters=K, affinity="precomputed", random_state=seed,
                             assign_labels="discretize").fit_predict(A)
    return dict(zip(nodes, lab))


def vowel_profiles(slots, texts=None, direction="end", use_dist=False):
    """Profile over tails following each bridge sign inside Kober families.
    If use_dist, also add corpus-wide penultimate->final transitions and final-position counts."""
    prof = defaultdict(Counter)
    for stem, b, tl in slots:
        prof[b][tl if tl else ("<END>",)] += 1
    if use_dist and texts is not None:
        for t in texts:
            t = tuple(t) if direction == "end" else tuple(reversed(t))
            if len(t) >= 2:
                prof[t[-2]][(t[-1],)] += 0.5
            if t:
                prof[t[-1]][("<END>",)] += 0.5
    return prof


def vowel_cols(prof, K, rows=None, signs=None, penalty=0.5):
    signs = sorted(signs if signs is not None else prof)
    signs = [s for s in signs if sum(prof[s].values()) > 0]
    if len(signs) < K + 1:
        return {}
    feats = sorted({f for s in signs for f in prof[s]})
    fi = {f: i for i, f in enumerate(feats)}
    X = np.zeros((len(signs), len(feats)))
    for i, s in enumerate(signs):
        for f, c in prof[s].items():
            X[i, fi[f]] = c
    # tf-idf style down-weighting of the ubiquitous <END> feature
    df = (X > 0).sum(0)
    X = X * np.log(1 + len(signs) / np.maximum(df, 1))
    X = X / np.maximum(np.linalg.norm(X, axis=1, keepdims=True), 1e-9)
    D = 1 - X @ X.T
    if rows:
        for i, a in enumerate(signs):
            for j, b in enumerate(signs):
                if i != j and a in rows and b in rows and rows[a] == rows[b]:
                    D[i, j] += penalty
    np.fill_diagonal(D, 0)
    D = np.clip(D, 0, None)
    lab = AgglomerativeClustering(n_clusters=K, metric="precomputed", linkage="average").fit_predict(D)
    return dict(zip(signs, lab))


def ari(part, truth):
    keys = [s for s in part if s in truth]
    if len(keys) < 3:
        return float("nan"), len(keys)
    return adjusted_rand_score([truth[s] for s in keys], [part[s] for s in keys]), len(keys)


def edge_precision(edges, truth, min_w=1):
    """Share of alternation edges joining two signs with the same true label, and the base rate
    among all pairs of the signs that appear in the graph."""
    E = [(a, b) for (a, b), c in edges.items() if c >= min_w and a in truth and b in truth]
    if not E:
        return float("nan"), float("nan"), 0
    prec = np.mean([truth[a] == truth[b] for a, b in E])
    nodes = sorted({x for e in E for x in e})
    lab = Counter(truth[s] for s in nodes)
    n = len(nodes)
    base = sum(c * (c - 1) for c in lab.values()) / max(n * (n - 1), 1)
    return float(prec), float(base), len(E)


def louvain_rows(edges, min_w=1, seed=0):
    G = graph(edges, min_w)
    if G.number_of_edges() < 2:
        return {}
    comms = nx.community.louvain_communities(G, weight="weight", seed=seed)
    return {s: i for i, c in enumerate(comms) for s in c}


def run_grid(texts, K_c, K_v, direction="end", min_w=1, use_dist=False, seed=0):
    edges, slots, fams = kober(texts, direction, **PARAMS)
    rows = consonant_rows(edges, K_c, min_w=min_w, seed=seed)
    prof = vowel_profiles(slots, texts, direction, use_dist=use_dist)
    cols = vowel_cols(prof, K_v, rows=rows, signs=list(rows)) if rows else {}
    return dict(edges=edges, slots=slots, families=fams, rows=rows, cols=cols)


def evaluate(texts, truth_c, truth_v, K_c=None, K_v=None, direction="end", seed=0, min_w=1):
    """Run the full method on texts with known consonant / vowel labels for syllabograms."""
    syl = [s for s in truth_c]
    freq = Counter(s for t in texts for s in t)
    present = [s for s in syl if freq[s] >= 5]
    # oracle K = number of true classes among the signs that actually enter the alternation graph
    e0, _, _ = kober(texts, direction, **PARAMS)
    nodes = set(graph(e0, min_w).nodes())
    K_c = K_c or max(2, len({truth_c[s] for s in nodes if s in truth_c}))
    K_v = K_v or max(2, len({truth_v[s] for s in nodes if s in truth_v}))
    g = run_grid(texts, K_c, K_v, direction, seed=seed, min_w=min_w)
    ac, nc = ari(g["rows"], truth_c)
    al, _ = ari(louvain_rows(g["edges"], min_w, seed), truth_c)
    av, nv = ari(g["cols"], truth_v)
    pc, bc, ne = edge_precision(g["edges"], truth_c, min_w)
    pv, bv, _ = edge_precision(g["edges"], truth_v, min_w)
    return dict(ari_cons=ac, ari_cons_louvain=al, ari_vow=av, covered=nc, syllabograms=len(present),
                coverage=nc / max(len(present), 1), edge_prec_cons=pc, edge_base_cons=bc,
                edge_prec_vow=pv, edge_base_vow=bv, n_edges=ne, alt_stems=len(g["families"]))


# ---------------------------------------------------------------- nulls
def shuffle_final(texts, rng):
    """Permute the last sign among texts of the same length (keeps stems, lengths, final-sign marginals)."""
    by = defaultdict(list)
    for i, t in enumerate(texts):
        by[len(t)].append(i)
    out = [list(t) for t in texts]
    for L, idx in by.items():
        fin = [texts[i][-1] for i in idx]
        rng.shuffle(fin)
        for i, f in zip(idx, fin):
            out[i][-1] = f
    return [tuple(t) for t in out]


def shuffle_end_block(texts, rng, k=2):
    """Permute the last-k block (bridge + tail) among texts of the same length."""
    by = defaultdict(list)
    for i, t in enumerate(texts):
        if len(t) > k:
            by[len(t)].append(i)
    out = [tuple(t) for t in texts]
    for L, idx in by.items():
        blk = [texts[i][-k:] for i in idx]
        rng.shuffle(blk)
        for i, b in zip(idx, blk):
            out[i] = tuple(texts[i][:-k]) + tuple(b)
    return out


def bigram_null(texts, rng):
    """Order-1 Markov resample with matched length distribution (start/end aware)."""
    trans = defaultdict(Counter)
    for t in texts:
        prev = "<S>"
        for s in t:
            trans[prev][s] += 1
            prev = s
    keys = {}
    for k, v in trans.items():
        w = np.array(list(v.values()), float)
        keys[k] = (list(v), np.cumsum(w) / w.sum())
    out = []
    for t in texts:
        L = len(t); seq = []; prev = "<S>"
        for _ in range(L):
            if prev not in keys:
                prev = "<S>"
            opts, cum = keys[prev]
            s = opts[min(int(np.searchsorted(cum, rng.random())), len(opts) - 1)]
            seq.append(s); prev = s
        out.append(tuple(seq))
    return out


def null_stats(texts, kind, n=50, seed=1, direction="end"):
    rng = random.Random(seed)
    res = []
    for _ in range(n):
        if kind == "final":
            nt = shuffle_final(texts, rng) if direction == "end" else [tuple(reversed(x)) for x in shuffle_final([tuple(reversed(t)) for t in texts], rng)]
        elif kind == "block":
            nt = shuffle_end_block(texts, rng) if direction == "end" else [tuple(reversed(x)) for x in shuffle_end_block([tuple(reversed(t)) for t in texts], rng)]
        else:
            nt = bigram_null(texts, rng)
        nt = list(dict.fromkeys(nt))
        res.append(stats(nt, direction))
    keys = res[0].keys()
    return {k: (float(np.mean([r[k] for r in res])), float(np.std([r[k] for r in res]))) for k in keys}
