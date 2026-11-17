"""Shared helpers for experiments/internal_phonetics.

Texts are DISTINCT sequences from corpus.load.dev_heldout(version=2) (family split),
line breaks '|' removed, texts with a break '#' dropped (a break fakes indels).
Reading order as transcribed (first sign = first read). "Reversed" analyses reverse
every text.
"""
import json, math, random, sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from corpus.load import dev_heldout  # noqa: E402

OUT = Path(__file__).resolve().parent


def clean(seq):
    if "#" in seq:
        return None
    s = tuple(x for x in seq if x != "|")
    return s if s else None


def load_split():
    dev, ho = dev_heldout(version=2)
    D = sorted({c for t in dev if (c := clean(t["seq"]))})
    H = sorted({c for t in ho if (c := clean(t["seq"]))} - set(D))
    return D, H


def save_results(key, obj):
    p = OUT / "results.json"
    d = json.load(open(p)) if p.exists() else {}
    d[key] = obj
    json.dump(d, open(p, "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))


# ------------------------------------------------------------- edit pairs
def edit1_pairs(texts, minlen=2):
    """All edit-distance-1 pairs. Returns (subs, indels):
    subs: list of (t1, t2, pos) with t1[pos] != t2[pos], same length
    indels: list of (short, long, pos) with long = short[:pos] + (x,) + short[pos:]"""
    texts = [t for t in texts if len(t) >= minlen]
    S = set(texts)
    subs, indels = [], []
    # substitutions via wildcard keys
    bucket = defaultdict(list)
    for t in texts:
        for i in range(len(t)):
            bucket[(t[:i], t[i + 1:], len(t))].append((t, i))
    for k, v in bucket.items():
        if len(v) > 1:
            for a in range(len(v)):
                for b in range(a + 1, len(v)):
                    subs.append((v[a][0], v[b][0], v[a][1]))
    # insertions: delete one sign from long, look up short
    for t in texts:
        seen = set()
        for i in range(len(t)):
            s = t[:i] + t[i + 1:]
            if s in S and len(s) >= minlen - 1 and (s, i) not in seen:
                # canonical position: leftmost deletion position giving s
                seen.add((s, i))
        # collapse runs of identical signs (deleting either copy gives same short)
        got = {}
        for s, i in sorted(seen, key=lambda z: z[1]):
            if s not in got:
                got[s] = i
        for s, i in got.items():
            indels.append((s, t, i))
    return subs, indels


def one_two_pairs(texts, minctx=2):
    """Pairs where one sign A in text u stands where two adjacent signs B C stand in
    text t, everything else identical, with >=1 shared context sign.
    Returns list of (u, t, j, A, (B, C))."""
    texts = list(set(texts))
    keyBC = defaultdict(list)
    for t in texts:
        for i in range(len(t) - 1):
            keyBC[(t[:i], t[i + 2:])].append((t, i))
    out = []
    for u in texts:
        for j in range(len(u)):
            k = (u[:j], u[j + 1:])
            if len(k[0]) + len(k[1]) < minctx:
                continue
            for t, i in keyBC.get(k, []):
                A, BC = u[j], t[i:i + 2]
                if A in BC:   # plain insertion, not a 1<->2 correspondence
                    continue
                out.append((u, t, j, A, BC))
    return out


def families(texts, extra_pairs=()):
    """Connected components of the edit-distance-1 graph, optionally plus extra
    (a, b) links. Returns dict text -> family id."""
    texts = sorted(set(texts))
    idx = {t: i for i, t in enumerate(texts)}
    parent = list(range(len(texts)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    subs, indels = edit1_pairs(texts, minlen=1)
    links = [(a, b) for a, b, _ in subs] + [(a, b) for a, b, _ in indels] + list(extra_pairs)
    for a, b in links:
        if a in idx and b in idx:
            parent[find(idx[a])] = find(idx[b])
    return {t: find(idx[t]) for t in texts}


def poscls(i, n):
    if n == 1:
        return "solo"
    return "I" if i == 0 else ("F" if i == n - 1 else "M")


def bh(pvals):
    p = np.asarray(pvals, float); n = len(p)
    if n == 0:
        return p
    o = np.argsort(p); q = np.empty(n)
    run = 1.0
    for r, i in enumerate(o[::-1]):
        k = n - r
        run = min(run, p[i] * n / k); q[i] = run
    return q


# ------------------------------------------------------------- image similarity
_IMG = {}


def glyph_vec(sign, size=48, blur=2.0):
    """Normalised, bbox-cropped, blurred drawing vector of a Mahadevan sign."""
    key = (sign, size, blur)
    if key in _IMG:
        return _IMG[key]
    from PIL import Image, ImageFilter
    im = Image.open(ROOT / f"data/sign_images/{sign}.png").convert("RGBA")
    bg = Image.new("RGBA", im.size, "white"); bg.alpha_composite(im)
    g = np.asarray(bg.convert("L"), float)
    ink = g < 128
    ys, xs = np.where(ink)
    if len(ys) == 0:
        v = np.zeros(size * size); _IMG[key] = v; return v
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    h, w = y1 - y0, x1 - x0; m = max(h, w)
    canvas = np.zeros((m, m)); oy, ox = (m - h) // 2, (m - w) // 2
    canvas[oy:oy + h, ox:ox + w] = ink[y0:y1, x0:x1]
    im2 = Image.fromarray((canvas * 255).astype(np.uint8)).resize((size, size), Image.BILINEAR)
    im2 = im2.filter(ImageFilter.GaussianBlur(blur))
    v = np.asarray(im2, float).ravel()
    v = v - v.mean(); v = v / (np.linalg.norm(v) + 1e-9)
    _IMG[key] = v
    return v


def glyph_sim(a, b):
    return float(glyph_vec(a) @ glyph_vec(b))


def n_independent(contexts):
    """Number of clusters among context strings when strings within edit distance 1
    of each other (single linkage) are merged: a count of independent families."""
    cs = list(set(contexts))
    parent = list(range(len(cs)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    for i in range(len(cs)):
        for j in range(i + 1, len(cs)):
            if ed_le1(cs[i], cs[j]):
                parent[find(i)] = find(j)
    return len({find(i) for i in range(len(cs))})


def ed_le1(a, b):
    if a == b:
        return True
    la, lb = len(a), len(b)
    if abs(la - lb) > 1:
        return False
    if la == lb:
        return sum(x != y for x, y in zip(a, b)) <= 1
    if la > lb:
        a, b = b, a
    for i in range(len(b)):
        if b[:i] + b[i + 1:] == a:
            return True
    return False


class Bigram:
    """Bigram (order-1 Markov) generator fitted on texts; samples texts of an exact
    length using backward messages, until n distinct texts are produced. The null
    corpus has the same lengths, sign frequencies and adjacencies but no
    within-legend spelling variation."""

    def __init__(self, texts):
        self.V = sorted({s for t in texts for s in t})
        self.ix = {s: i for i, s in enumerate(self.V)}
        n = len(self.V)
        self.S, self.E = n, n + 1           # start, end
        C = np.zeros((n + 2, n + 2))
        for t in texts:
            prev = self.S
            for s in t:
                C[prev, self.ix[s]] += 1; prev = self.ix[s]
            C[prev, self.E] += 1
        self.P = C / np.maximum(C.sum(1, keepdims=True), 1)
        self.lengths = [len(t) for t in texts]
        self._beta = {}

    def beta(self, L):
        # beta[k][i] = P(complete in exactly k more signs then END | current state i)
        if L in self._beta:
            return self._beta[L]
        n = len(self.V)
        b = [self.P[:, self.E].copy()]
        for k in range(1, L + 1):
            b.append(self.P[:, :n] @ b[-1][:n])
        self._beta[L] = b
        return b

    def sample(self, n_distinct, rng):
        out, seen = [], set()
        n = len(self.V)
        tries = 0
        while len(out) < n_distinct and tries < n_distinct * 50:
            tries += 1
            L = self.lengths[rng.integers(len(self.lengths))]
            b = self.beta(L)
            st, t = self.S, []
            ok = True
            for k in range(L, 0, -1):
                w = self.P[st, :n] * b[k - 1][:n]
                if w.sum() <= 0:
                    ok = False; break
                st = rng.choice(n, p=w / w.sum()); t.append(self.V[st])
            if ok:
                t = tuple(t)
                if t not in seen:
                    seen.add(t); out.append(t)
        return out
