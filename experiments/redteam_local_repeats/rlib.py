"""Shared models for redteam_local_repeats: interpolated trigram (exact length via SIR) and positional slot bigram.
The global bigram N2 is imported read-only from experiments/redteam_identifiers/c1.py.
"""
import os, sys
from collections import Counter, defaultdict
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
for p in ("experiments/identifiers", "experiments/redteam_identifiers", "experiments/local_repeats"):
    sys.path.insert(0, os.path.join(ROOT, p))
sys.path.insert(0, ROOT)

OPEN = {"W817", "W861", "W820"}
NUM = {"W003", "W004", "W016", "W005", "W006", "W007", "W008", "W009", "W010", "W011", "W012", "W013", "W014", "W015", "W017"}


def is_formula(t):
    return len(t) == 4 and t[0] in OPEN and t[1] == "W002" and t[2] in NUM and t[3] == "W390"


class Trigram:
    """P(c|a,b) = l3*ML3 + l2*ML2(c|b) + l1*ML1(c); symbols include END. Start padding '<s>'."""

    def __init__(self, D, V, lam=(0.6, 0.3, 0.1)):
        self.V = list(V); self.n = len(V); self.ix = {s: i for i, s in enumerate(V)}
        self.END = self.n; self.BOS = self.n + 1
        n = self.n
        self.c3 = defaultdict(Counter); self.c2 = defaultdict(Counter); c1 = np.full(n + 1, 0.01)
        for t in D:
            ids = [self.BOS, self.BOS] + [self.ix[s] for s in t] + [self.END]
            for i in range(2, len(ids)):
                a, b, c = ids[i - 2], ids[i - 1], ids[i]
                self.c3[(a, b)][c] += 1; self.c2[b][c] += 1; c1[c] += 1
        self.p1 = c1 / c1.sum(); self.lam = lam; self.cache = {}

    def dist(self, a, b):
        k = (a, b)
        if k in self.cache: return self.cache[k]
        l3, l2, l1 = self.lam
        p = l1 * self.p1.copy()
        w2 = l2; w3 = l3
        if b in self.c2:
            C = self.c2[b]; tot = sum(C.values()); v = np.zeros(self.n + 1)
            for c, x in C.items(): v[c] = x / tot
            p2 = v
        else:
            p2 = None; w2 = 0
        if k in self.c3:
            C = self.c3[k]; tot = sum(C.values()); v = np.zeros(self.n + 1)
            for c, x in C.items(): v[c] = x / tot
            p3 = v
        else:
            p3 = None; w3 = 0
        if p2 is not None: p = p + w2 * p2
        if p3 is not None: p = p + w3 * p3
        p = p / p.sum()
        self.cache[k] = p
        return p

    def logp(self, t):
        ids = [self.BOS, self.BOS] + [self.ix[s] for s in t] + [self.END]
        return float(sum(np.log(self.dist(ids[i - 2], ids[i - 1])[ids[i]]) for i in range(2, len(ids))))

    def _draw(self, ctx_a, ctx_b, rng):
        """draw one non-END sign per row; return signs and P(not END) per row"""
        out = np.empty(len(ctx_a), int); pne = np.empty(len(ctx_a))
        keys = ctx_a.astype(np.int64) * (self.n + 2) + ctx_b
        for k in np.unique(keys):
            rows = np.where(keys == k)[0]; a, b = divmod(int(k), self.n + 2)
            p = self.dist(a, b); q = p[:self.n]; s = q.sum()
            cdf = np.cumsum(q / s)
            out[rows] = np.minimum(np.searchsorted(cdf, rng.random(len(rows))), self.n - 1); pne[rows] = s
        return out, pne

    def sample(self, lengths, rng, K=20):
        lengths = np.asarray(lengths); res = [None] * len(lengths)
        for L in np.unique(lengths):
            idx = np.where(lengths == L)[0]; m = len(idx) * K
            a = np.full(m, self.BOS); b = np.full(m, self.BOS); w = np.ones(m); seqs = []
            for pos in range(L):
                s, pne = self._draw(a, b, rng); w *= pne; seqs.append(s); a, b = b, s
            keys = a.astype(np.int64) * (self.n + 2) + b; pend = np.empty(m)
            for k in np.unique(keys):
                rows = np.where(keys == k)[0]; aa, bb = divmod(int(k), self.n + 2); pend[rows] = self.dist(aa, bb)[self.END]
            w *= pend
            arr = np.stack(seqs, 1).reshape(len(idx), K, L); W = w.reshape(len(idx), K)
            W = W / W.sum(1, keepdims=True); cw = np.cumsum(W, 1)
            pick = np.minimum((cw < rng.random(len(idx))[:, None]).sum(1), K - 1)
            for j, i in enumerate(idx): res[i] = tuple(self.V[x] for x in arr[j, pick[j]])
        return res


def slots(L):
    if L == 1: return ["single"]
    if L == 2: return ["first", "last"]
    if L == 3: return ["first", "mid", "last"]
    return ["first", "second"] + ["mid"] * (L - 4) + ["penult", "last"]


class Slot:
    """positional slot bigram, conditional on length: P(s_i | s_{i-1}, slot_i) = 0.9 ML + 0.1 slot unigram."""

    def __init__(self, D, V, w=0.9):
        self.V = list(V); self.n = len(V); self.ix = {s: i for i, s in enumerate(V)}; self.w = w
        self.uni = defaultdict(lambda: np.full(self.n, 0.01)); self.big = defaultdict(Counter)
        for t in D:
            ids = [self.ix[s] for s in t]
            for i, (s, sl) in enumerate(zip(ids, slots(len(ids)))):
                self.uni[sl][s] += 1
                if i > 0: self.big[(sl, ids[i - 1])][s] += 1
        self.uni = {k: v / v.sum() for k, v in self.uni.items()}; self.cache = {}

    def dist(self, sl, prev):
        k = (sl, prev)
        if k in self.cache: return self.cache[k]
        u = self.uni[sl]
        if prev is None or k not in self.big: p = u
        else:
            C = self.big[k]; tot = sum(C.values()); v = np.zeros(self.n)
            for c, x in C.items(): v[c] = x / tot
            p = self.w * v + (1 - self.w) * u
        cdf = np.cumsum(p / p.sum()); self.cache[k] = (p / p.sum(), cdf)
        return self.cache[k]

    def logp(self, t):
        ids = [self.ix[s] for s in t]; lp = 0.0
        for i, sl in enumerate(slots(len(ids))):
            lp += np.log(self.dist(sl, ids[i - 1] if i else None)[0][ids[i]])
        return float(lp)

    def sample(self, lengths, rng):
        lengths = np.asarray(lengths); res = [None] * len(lengths)
        for L in np.unique(lengths):
            idx = np.where(lengths == L)[0]; prev = np.full(len(idx), -1); seqs = []
            for i, sl in enumerate(slots(L)):
                cur = np.empty(len(idx), int)
                for pv in np.unique(prev):
                    rows = np.where(prev == pv)[0]; cdf = self.dist(sl, None if pv < 0 else int(pv))[1]
                    cur[rows] = np.minimum(np.searchsorted(cdf, rng.random(len(rows))), self.n - 1)
                seqs.append(cur); prev = cur
            arr = np.stack(seqs, 1)
            for j, i in enumerate(idx): res[i] = tuple(self.V[x] for x in arr[j])
        return res


def bigram_logp(g, t, cond=True):
    """log P(t) under c1.Bigram (joint with END); cond=True subtracts log P(length)."""
    ids = [g.ix[s] for s in t]; n = len(g.V)
    lp = np.log(g.st[ids[0]]) + sum(np.log(g.tr[a, b]) for a, b in zip(ids, ids[1:])) + np.log(g.tr[ids[-1], n])
    if cond:
        lp -= np.log((g.st * g.beta[len(t) - 1]).sum())
    return float(lp)


def summ(a, obs):
    a = np.asarray(a, float)
    return dict(mean=float(a.mean()), lo=float(np.percentile(a, 2.5)), hi=float(np.percentile(a, 97.5)),
                p_ge=float((1 + (a >= obs).sum()) / (len(a) + 1)), obs=obs)
