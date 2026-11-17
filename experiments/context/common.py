"""Shared helpers for experiments/context. Run scripts from repo root."""
import json, sys, re
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from corpus.load import m77_lines, m77_texts, icit_texts, distinct, dev_heldout, runs  # noqa

OUT = ROOT / "experiments" / "context"
SRC = ROOT / "sources"

STROKES = json.load(open(SRC / "shaunmortal_indus/data/stroke_signs.json"))
M_SHORT = {f"M{k}": v for k, v in STROKES["short"].items() if k not in ("99", "100", "101")}  # 2-short = connective
M_TALL = {f"M{k}": v for k, v in STROKES["tall"].items()}
BRIDGE = json.load(open(SRC / "shaunmortal_indus/data/bridge_WM.json"))
W2M = {f"W{int(k):03d}": [f"M{m}" for m in v["M"]] for k, v in BRIDGE.items()}
# Wells numerals (Wells 1-12 short strokes; 31-35 tall), per Wells sign list conventions + bridge
W_SHORT = {"W001": 1, "W003": 3, "W004": 4, "W005": 5, "W006": 6, "W007": 7, "W013": 3, "W014": 4,
           "W015": 5, "W016": 6, "W017": 7, "W018": 8, "W019": 9, "W055": 12}
W_TALL = {"W031": 1, "W032": 2, "W033": 3, "W034": 4, "W035": 5}
JAR_M, JAR_W = "M342", "W740"


def signs(seq):
    return [s for s in seq if s not in ("|", "#")]


def ngrams(seq, n):
    out = set()
    for r in runs(seq):
        for i in range(len(r) - n + 1):
            out.add(" ".join(r[i:i + n]))
    return out


def bh(pvals):
    p = np.asarray(pvals, float)
    n = len(p)
    if n == 0:
        return p
    o = np.argsort(p)
    q = p[o] * n / np.arange(1, n + 1)
    q = np.minimum.accumulate(q[::-1])[::-1]
    out = np.empty(n); out[o] = np.minimum(q, 1)
    return out


def strat_perm(labels, strata, rng):
    """Permute labels within strata."""
    labels = np.asarray(labels)
    out = labels.copy()
    strata = np.asarray(strata)
    for s in np.unique(strata):
        idx = np.where(strata == s)[0]
        out[idx] = labels[rng.permutation(idx)]
    return out


def lenbin(n):
    return min(n, 8) if n > 0 else 0


def save_json(name, obj):
    path = OUT / "results.json"
    allr = json.load(open(path)) if path.exists() else {}
    allr[name] = obj
    json.dump(allr, open(path, "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))


def m77_fs_desc():
    return {l["fs80"]: l["fs_description"] for l in m77_lines()}


def m77_animal(fs80):
    """Coarse animal class from Mahadevan fs80 code (first 2 digits = motif group)."""
    if fs80 in (11, 12, 13, 14, 15, 16, 17):
        return "unicorn"
    if fs80 in (41, 45, 50):
        return "shorthorn_bull"
    if 21 <= fs80 <= 25:
        return "longhorn_bull"
    if 31 <= fs80 <= 35:
        return "zebu"
    if 61 <= fs80 <= 65:
        return "buffalo"
    if 71 <= fs80 <= 75:
        return "elephant"
    if 91 <= fs80 <= 95:
        return "tiger"
    if 111 <= fs80 <= 113:
        return "rhino"
    if 131 <= fs80 <= 139:
        return "goat_antelope"
    if 141 <= fs80 <= 149:
        return "ox_antelope"
    if 251 <= fs80 <= 253:
        return "composite"
    if 361 <= fs80 <= 362:
        return "gharial"
    return None


def icit_animal(sym):
    s = sym.split(":")[0]
    m = {"Bull1": "unicorn", "Bult": "unicorn", "Gaur": "shorthorn_bull", "Zebu": "zebu", "Elep": "elephant",
         "Rhin": "rhino", "Tigr": "tiger", "Buff": "buffalo", "Gavi": "gharial", "Goat": "goat_antelope",
         "Hare": "hare", "Anth": "anthropomorph"}
    return m.get(s)


def strat_hypergeom_p(x_col, y_bin, strata):
    """Exact stratified test: count of (feature & type) is a sum of independent hypergeometrics,
    one per stratum (= permuting type labels within strata). Returns obs, exp, p_hi, p_lo."""
    from scipy.stats import hypergeom
    obs = int((x_col * y_bin).sum())
    dist = np.array([1.0])
    exp = 0.0
    for s in np.unique(strata):
        m = strata == s
        N = int(m.sum()); K = int(y_bin[m].sum()); n = int(x_col[m].sum())
        if K == 0 or n == 0:
            continue
        k = np.arange(0, min(K, n) + 1)
        pmf = hypergeom.pmf(k, N, K, n)
        dist = np.convolve(dist, pmf)
        exp += n * K / N
    cdf = np.cumsum(dist)
    p_lo = float(min(1, cdf[obs])) if obs < len(cdf) else 1.0
    p_hi = float(min(1, dist[obs:].sum())) if obs < len(dist) else 0.0
    return obs, exp, max(p_hi, 1e-300), max(p_lo, 1e-300)


def strat_hyper_matrix(X, y, strata, ntypes):
    """Vectorised version over all features x types. X: texts x feats (0/1), y: int labels."""
    from scipy.stats import hypergeom
    su, si = np.unique(strata, return_inverse=True)
    S = np.eye(len(su))[si]
    Nn = S.sum(0)                       # per stratum size
    nF = S.T @ X                        # strata x feats
    Y = np.eye(ntypes)[y]
    KT = S.T @ Y                        # strata x types
    obs = Y.T @ X
    exp = KT.T @ (nF / Nn[:, None])
    p_hi = np.ones_like(obs); p_lo = np.ones_like(obs)
    for a in range(ntypes):
        for b in range(X.shape[1]):
            dist = np.array([1.0])
            for s in np.where((KT[:, a] > 0) & (nF[:, b] > 0))[0]:
                K, n, N = int(KT[s, a]), int(nF[s, b]), int(Nn[s])
                dist = np.convolve(dist, hypergeom.pmf(np.arange(min(K, n) + 1), N, K, n))
            o = int(obs[a, b])
            p_hi[a, b] = max(dist[o:].sum(), 1e-300) if o < len(dist) else 1e-300
            p_lo[a, b] = max(dist[:o + 1].sum(), 1e-300)
    return obs, exp, np.minimum(p_hi, 1), np.minimum(p_lo, 1)
