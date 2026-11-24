"""anchor_ceiling v2 core (prereg docs/prereg/anchor_ceiling_v2.md). Imports core.py unchanged.

- profiles: per anchor variable, share(v) = (count + ALPHA*base) / (n + ALPHA), x = log(share/base); base from dev
  documents only, over dev-observed values; each variable block unit-normalised; blocks concatenated.
- cluster: 'kmeans' (n_init 20, random_state 0) or 'ward', k = 6 fixed.
- held-out words -> nearest cluster centroid by cosine (core.assign).
- scoring: core.score_draw with the fixed field list (a field with < 3 held-out words in a draw is unscored there).
"""
import sys
from pathlib import Path
import numpy as np
from collections import Counter
from scipy.cluster.hierarchy import linkage, fcluster
from sklearn.cluster import KMeans
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import core as K  # noqa: E402

ALPHA = 2.0
FIELDS = ["admin", "land", "occupation", "person", "place"]
KCL = len(FIELDS) + 1


def profiles(docs, words, rung, A, dev):
    blocks = []
    wi = {w: i for i, w in enumerate(words)}
    n = np.zeros(len(words))
    for d in docs:
        for w in d["words"]:
            if w in wi: n[wi[w]] += 1
    for v in K.RUNGS[rung]:
        vals = sorted({A[v][d["id"]] for d in dev}); vi = {x: j for j, x in enumerate(vals)}
        base = np.zeros(len(vals))
        for d in dev: base[vi[A[v][d["id"]]]] += 1
        base /= len(dev)
        cnt = np.zeros((len(words), len(vals)))
        for d in docs:
            j = vi.get(A[v][d["id"]])
            if j is None: continue
            for w in d["words"]:
                if w in wi: cnt[wi[w], j] += 1
        share = (cnt + ALPHA * base[None, :]) / (n[:, None] + ALPHA)
        X = np.log(share / base[None, :])
        nrm = np.linalg.norm(X, axis=1, keepdims=True); nrm[nrm == 0] = 1
        blocks.append(X / nrm)
    return np.hstack(blocks)


def cluster(P, method):
    if method == "kmeans":
        return KMeans(KCL, n_init=20, random_state=0).fit(P).labels_
    if method == "ward":
        return fcluster(linkage(P, method="ward"), t=KCL, criterion="maxclust") - 1
    raise ValueError(method)


def run_rung(dev, held, rung, A, truth_map, method, nperm, rng, supervised=False):
    el, sc, cd = K.eligible(dev, held)
    P = profiles(dev, el, rung, A, dev)
    lab = cluster(P, method)
    Q = profiles(held, sc, rung, A, dev)
    pred = K.assign(Q, P, lab)
    out = K.score_draw(truth_map, FIELDS, sc, pred, cd, nperm, rng)
    out["pair_auc"] = K.pair_auc(el, P, truth_map)
    if supervised:
        out["sup_dev"] = K.supervised_control(el, P, truth_map, FIELDS, cd, nperm, rng)
        # true-field dev centroids assign held-out words
        tl = np.array([truth_map.get(w, "") for w in el])
        fs = [f for f in FIELDS if (tl == f).any()]
        cent = np.array([P[tl == f].mean(0) for f in fs])
        cent = cent / np.maximum(np.linalg.norm(cent, axis=1, keepdims=True), 1e-12)
        Qn = Q / np.maximum(np.linalg.norm(Q, axis=1, keepdims=True), 1e-12)
        predf = np.array([fs[int(np.argmax(r))] for r in Qn @ cent.T])
        out["sup_held"] = K.score_draw(truth_map, FIELDS, sc, predf, cd, nperm, rng)
    return out
