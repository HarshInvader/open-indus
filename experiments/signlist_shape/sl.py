"""Shared machinery for the shape + context sign-list experiment (prereg: docs/prereg/signlist_shape_context.md).

shape_matrix(paths)        -> (names, D_hog, D_chamfer)   distances between sign drawings
context_sim(seqs, pool)    -> cosine similarity of PPMI left/right-neighbour vectors (training texts only)
ClassLM                    -> class-based interpolated Kneser-Ney n-gram; every model is scored on the FINE
                              sign tokens (P(class | history) * P(sign | class)), so lists of different
                              sizes are compared on the same tokens
greedy(...)                -> one pass over candidate merges, accept a merge if 5-fold CV log-likelihood on
                              the training texts goes up
Image preprocessing follows experiments/protocuneiform/s1_freeze.py (ink mask, first exemplar, size-normalise),
re-implemented here so no other folder is touched.
"""
import math, random
from collections import Counter, defaultdict
import numpy as np
import cv2
from PIL import Image

NORM = 64
D_KN = 0.75
BOS, EOS, UNK = "<s>", "</s>", "<unk>"


# ----------------------------------------------------------------------------- shape
def ink_of(path):
    im = Image.open(path)
    if im.mode in ("RGBA", "LA"):
        a = np.array(im.convert("RGBA")).astype(float)
        return (a[..., 3] > 127) & (a[..., :3].mean(-1) < 128)
    return np.array(im.convert("L")) < 128


def first_exemplar(ink):
    """Englund's PC JPGs often stack 2-4 exemplars vertically; keep the first band (rule from s1_freeze.py)."""
    rows = ink.any(1)
    bands, cur = [], None
    for y, r in enumerate(rows):
        if r and cur is None:
            cur = y
        if not r and cur is not None:
            bands.append((cur, y)); cur = None
    if cur is not None:
        bands.append((cur, len(rows)))
    merged = []
    for b in bands:
        if merged and b[0] - merged[-1][1] < 4:
            merged[-1] = (merged[-1][0], b[1])
        else:
            merged.append(b)
    big = [b for b in merged if b[1] - b[0] >= 8]
    if len(big) >= 2:
        def width(b):
            xs = np.nonzero(ink[b[0]:b[1]].any(0))[0]
            return xs.max() - xs.min() + 1
        hs = [b[1] - b[0] for b in big]; ws = [width(b) for b in big]
        if min(hs) / max(hs) > 0.5 and min(ws) / max(ws) > 0.6:
            out = np.zeros_like(ink); out[big[0][0]:big[0][1]] = ink[big[0][0]:big[0][1]]
            return out
    return ink


def norm_mask(ink, size=NORM):
    ys, xs = np.nonzero(ink)
    if len(ys) == 0:
        return np.zeros((size, size), np.uint8)
    crop = ink[ys.min():ys.max() + 1, xs.min():xs.max() + 1].astype(np.uint8) * 255
    h, w = crop.shape
    inner = size - 8
    s = inner / max(h, w)
    nh, nw = max(1, int(round(h * s))), max(1, int(round(w * s)))
    r = (cv2.resize(crop, (nw, nh), interpolation=cv2.INTER_AREA) > 60).astype(np.uint8) * 255
    out = np.zeros((size, size), np.uint8)
    y0, x0 = (size - nh) // 2, (size - nw) // 2
    out[y0:y0 + nh, x0:x0 + nw] = r
    return out


def hog(img, cell=8, bins=9):
    """plain numpy HOG (cv2 5.x has no HOGDescriptor): unsigned gradients, 8-px cells, 2x2-cell blocks, L2."""
    g = img.astype(float)
    gx = np.zeros_like(g); gy = np.zeros_like(g)
    gx[:, 1:-1] = g[:, 2:] - g[:, :-2]; gy[1:-1, :] = g[2:, :] - g[:-2, :]
    mag = np.hypot(gx, gy); ang = (np.degrees(np.arctan2(gy, gx)) % 180)
    b = np.minimum((ang / (180 / bins)).astype(int), bins - 1)
    nc = g.shape[0] // cell
    H = np.zeros((nc, nc, bins))
    for i in range(nc):
        for j in range(nc):
            sl_ = (slice(i * cell, (i + 1) * cell), slice(j * cell, (j + 1) * cell))
            H[i, j] = np.bincount(b[sl_].ravel(), mag[sl_].ravel(), bins)
    out = []
    for i in range(nc - 1):
        for j in range(nc - 1):
            v = H[i:i + 2, j:j + 2].ravel()
            out.append(v / (np.linalg.norm(v) + 1e-6))
    return np.concatenate(out)


def features(mask):
    blur = cv2.GaussianBlur(mask, (5, 5), 1.5)
    h = hog(blur)
    h /= (np.linalg.norm(h) + 1e-9)
    dt = cv2.distanceTransform((mask == 0).astype(np.uint8), cv2.DIST_L2, 3)
    pts = np.argwhere(mask > 0)
    if len(pts) > 400:
        pts = pts[np.linspace(0, len(pts) - 1, 400).astype(int)]
    return h, dt, pts


def shape_matrix(masks):
    """masks: list of normalised masks -> (D_hog cosine distance, D_chamfer symmetric mean px)."""
    F = [features(m) for m in masks]
    H = np.array([f[0] for f in F])
    Dh = 1 - H @ H.T
    n = len(masks)
    Dc = np.zeros((n, n))
    for i in range(n):
        dti = F[i][1]
        for j in range(n):
            if i == j:
                continue
            pj = F[j][2]
            Dc[i, j] = dti[pj[:, 0], pj[:, 1]].mean() if len(pj) else 99
    Dc = (Dc + Dc.T) / 2
    return Dh, Dc


def pct_sim(D):
    """distance matrix -> percentile similarity over off-diagonal pairs (1 = most similar pair)."""
    n = len(D)
    iu = np.triu_indices(n, 1)
    v = D[iu]
    order = v.argsort().argsort()
    p = 1 - order / max(1, len(v) - 1)
    S = np.zeros_like(D, dtype=float)
    S[iu] = p; S[(iu[1], iu[0])] = p
    np.fill_diagonal(S, 1)
    return S


def perturb(mask_img, rng):
    """fake-variant drawing: random affine (rot +-10 deg, scale 0.85-1.15 per axis, shear +-0.15) + stroke change."""
    h, w = mask_img.shape
    a = math.radians(rng.uniform(-10, 10))
    sx, sy, sh = rng.uniform(0.85, 1.15), rng.uniform(0.85, 1.15), rng.uniform(-0.15, 0.15)
    R = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
    A = R @ np.array([[sx, sh], [0, sy]])
    c = np.array([w / 2, h / 2])
    M = np.hstack([A, (c - A @ c)[:, None]])
    out = cv2.warpAffine(mask_img.astype(np.uint8) * 255, M, (w, h)) > 60
    k = np.ones((3, 3), np.uint8)
    if rng.random() < 0.5:
        out = cv2.dilate(out.astype(np.uint8), k) > 0
    else:
        er = cv2.erode(out.astype(np.uint8), k) > 0
        out = er if er.sum() > 0.3 * out.sum() else out
    return out


# ----------------------------------------------------------------------------- context
def context_sim(seqs, pool, alpha=0.75):
    """PPMI over left- and right-neighbour features (with boundaries), cosine similarity among pool signs."""
    idx = {s: i for i, s in enumerate(pool)}
    feats = {}
    rows, cols, vals = [], [], []
    cnt = Counter()
    for q in seqs:
        p = [BOS] + q + [EOS]
        for k in range(1, len(p) - 1):
            s = p[k]
            if s not in idx:
                continue
            cnt[(s, "L:" + p[k - 1])] += 1
            cnt[(s, "R:" + p[k + 1])] += 1
    for (s, f) in cnt:
        feats.setdefault(f, len(feats))
    M = np.zeros((len(pool), len(feats)))
    for (s, f), c in cnt.items():
        M[idx[s], feats[f]] = c
    tot = M.sum()
    pw = M.sum(1, keepdims=True) / tot
    pc = M.sum(0) ** alpha; pc = pc / pc.sum()
    with np.errstate(divide="ignore", invalid="ignore"):
        pmi = np.log((M / tot) / (pw * pc[None, :]))
    P = np.where(M > 0, np.maximum(pmi, 0), 0)
    P /= (np.linalg.norm(P, axis=1, keepdims=True) + 1e-9)
    return P @ P.T


# ----------------------------------------------------------------------------- class LM
class ClassLM:
    """Interpolated Kneser-Ney over classes (order 2 or 3) + emission P(sign | class) (add-0.5)."""

    def __init__(self, cls, order=3):
        self.cls, self.order = cls, order

    def c(self, s):
        return self.cls.get(s, s)

    def fit(self, seqs):
        o = self.order
        self.sign_n = Counter(s for q in seqs for s in q)
        self.cls_n = Counter(); self.cls_k = Counter()
        for s, n in self.sign_n.items():
            self.cls_n[self.c(s)] += n
        for s in self.sign_n:
            self.cls_k[self.c(s)] += 1
        ng = [Counter() for _ in range(o + 1)]
        for q in seqs:
            p = [BOS] * (o - 1) + [self.c(s) for s in q] + [EOS]
            for k in range(o - 1, len(p)):
                for n in range(1, o + 1):
                    ng[n][tuple(p[k - n + 1:k + 1])] += 1
        self.top = ng[o]
        self.ctx_tot = Counter(); self.ctx_types = Counter()
        for g, c in self.top.items():
            self.ctx_tot[g[:-1]] += c; self.ctx_types[g[:-1]] += 1
        # continuation counts for lower orders
        self.cont = [None] + [Counter() for _ in range(o - 1)]
        for n in range(2, o + 1):
            for g in ng[n]:
                self.cont[n - 1][g[1:]] += 1
        self.cont_ctx_tot = [None] + [Counter() for _ in range(o - 1)]
        self.cont_ctx_types = [None] + [Counter() for _ in range(o - 1)]
        for n in range(1, o):
            for g, c in self.cont[n].items():
                self.cont_ctx_tot[n][g[:-1]] += c; self.cont_ctx_types[n][g[:-1]] += 1
        self.V = len({g[0] for g in ng[1]}) + 1
        self.cache = {}
        return self

    def p_lower(self, n, g):
        """continuation-based KN probability of g[-1] given g[:-1], len(g) == n (n < order)."""
        key = (n, g)
        if key in self.cache:
            return self.cache[key]
        if n == 1:
            tot = self.cont_ctx_tot[1][()]
            r = (self.cont[1][g] + 1.0) / (tot + self.V)
        else:
            h = g[:-1]
            tot = self.cont_ctx_tot[n][h]
            low = self.p_lower(n - 1, g[1:])
            if tot == 0:
                r = low
            else:
                r = max(self.cont[n][g] - D_KN, 0) / tot + D_KN * self.cont_ctx_types[n][h] / tot * low
        self.cache[key] = r
        return r

    def p_class(self, g):
        h = g[:-1]
        tot = self.ctx_tot[h]
        low = self.p_lower(self.order - 1, g[1:])
        if tot == 0:
            return low
        return max(self.top[g] - D_KN, 0) / tot + D_KN * self.ctx_types[h] / tot * low

    def score(self, seqs):
        """-> (sum log P over scored tokens incl. EOS, n scored). Signs unseen in training are context only."""
        o = self.order
        ll, n = 0.0, 0
        for q in seqs:
            p = [BOS] * (o - 1) + [self.c(s) if s in self.sign_n else UNK for s in q] + [EOS]
            raw = [None] * (o - 1) + list(q) + [EOS]
            for k in range(o - 1, len(p)):
                if p[k] == UNK:
                    continue
                g = tuple(p[k - o + 1:k + 1])
                lp = math.log(self.p_class(g))
                if raw[k] != EOS:
                    c = p[k]
                    lp += math.log((self.sign_n[raw[k]] + 0.5) / (self.cls_n[c] + 0.5 * self.cls_k[c]))
                ll += lp; n += 1
        return ll, n


def score_per_text(cls, train, test, order=3):
    m = ClassLM(cls, order).fit(train)
    return [m.score([q])[0] for q in test]


# ----------------------------------------------------------------------------- partitions
class UF:
    def __init__(self):
        self.p = {}

    def find(self, x):
        self.p.setdefault(x, x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]; x = self.p[x]
        return x

    def union(self, a, b):
        self.p[self.find(a)] = self.find(b)

    def mapping(self, signs):
        return {s: self.find(s) for s in signs}

    def copy(self):
        u = UF(); u.p = dict(self.p); return u


def folds(n_items, k=5, seed=0):
    idx = list(range(n_items)); random.Random(seed).shuffle(idx)
    return [idx[i::k] for i in range(k)]


class CVScorer:
    """5-fold CV log-likelihood of a partition on training sequences (fixed scored-token set per fold)."""

    def __init__(self, seqs, k=5, order=3, seed=0):
        self.order = order
        F = folds(len(seqs), k, seed)
        self.splits = []
        for f in F:
            fs = set(f)
            tr = [seqs[i] for i in range(len(seqs)) if i not in fs]
            te = [seqs[i] for i in f]
            self.splits.append((tr, te))

    def __call__(self, cls):
        tot = 0.0
        for tr, te in self.splits:
            tot += ClassLM(cls, self.order).fit(tr).score(te)[0]
        return tot


def greedy(seqs, candidates, base_cls=None, max_cands=300, order=3, log=None):
    """candidates: list of (a, b, score) in priority order. One pass; accept if CV LL rises.
    Returns (accepted list of (a, b, dLL), final mapping dict over all signs in seqs)."""
    signs = sorted({s for q in seqs for s in q})
    uf = UF()
    if base_cls:
        for s, c in base_cls.items():
            if s != c:
                uf.union(s, c)
    cv = CVScorer(seqs, order=order)
    cur = cv(uf.mapping(signs))
    acc = []
    for a, b, sc in candidates[:max_cands]:
        if uf.find(a) == uf.find(b):
            continue
        u2 = uf.copy(); u2.union(a, b)
        new = cv(u2.mapping(signs))
        d = new - cur
        if d > 0:
            uf, cur = u2, new
            acc.append((a, b, d, sc))
            if log:
                log(f"  accept {a}+{b} dLL={d:.2f} score={sc:.3f}")
    return acc, uf.mapping(signs)


def candidate_pairs(pool, S_shape, S_ctx, mode="both", k=5):
    """pairs that are top-k neighbours by the gating similarity, ranked by the mode's score."""
    n = len(pool)
    gate = S_shape if mode in ("both", "shape") else S_ctx
    cand = set()
    for i in range(n):
        o = np.argsort(-gate[i]); o = [j for j in o if j != i][:k]
        for j in o:
            cand.add((min(i, j), max(i, j)))
    out = []
    for i, j in cand:
        if mode == "both":
            sc = S_shape[i, j] + S_ctx[i, j]
        elif mode == "shape":
            sc = S_shape[i, j]
        else:
            sc = S_ctx[i, j]
        out.append((pool[i], pool[j], float(sc)))
    out.sort(key=lambda x: -x[2])
    return out


def pair_prf(mapping, pool, truth_key):
    """pairwise precision/recall over pool signs: truth_key(s) gives the true group id."""
    pool = list(pool)
    tp = fp = fn = 0
    for i in range(len(pool)):
        for j in range(i + 1, len(pool)):
            a, b = pool[i], pool[j]
            same_p = mapping.get(a, a) == mapping.get(b, b)
            same_t = truth_key(a) == truth_key(b)
            tp += same_p and same_t; fp += same_p and not same_t; fn += same_t and not same_p
    prec = tp / (tp + fp) if tp + fp else float("nan")
    rec = tp / (tp + fn) if tp + fn else float("nan")
    return {"tp": tp, "fp": fp, "fn": fn, "precision": prec, "recall": rec}
