"""Crib attack: find an injective sign -> syllable key under which many texts contain a name
from a candidate list (repeated signs are forced to repeated syllables because the key is a
function). Search = simulated annealing with hypothesis-driven moves.

Text score q(t) = max over (name spelling of length k >= 2, offset) of m = number of name
positions whose sign reads as the name's syllable, counted only if m >= k - tol(k) and m >= 2
(tol = 0 for k = 2, 1 for k >= 3: one misread sign allowed). Corpus score S = sum q(t).
"""
import numpy as np


def tol(k):
    return 0 if k <= 2 else 1


class NameIndex:
    def __init__(self, spellings, values):
        self.values = sorted(values)
        self.vid = {v: i for i, v in enumerate(self.values)}
        by = {}
        for sp in spellings:
            if all(x in self.vid for x in sp):
                by.setdefault(len(sp), []).append([self.vid[x] for x in sp])
        self.by_k = {k: np.array(v, dtype=np.int16) for k, v in sorted(by.items())}
        self.nv = len(self.values)


class Attack:
    def __init__(self, texts, nidx, nsigns, rng):
        self.texts = [np.asarray(t, dtype=np.int32) for t in texts]
        self.ni = nidx; self.rng = rng; self.nsigns = nsigns
        self.sign_texts = [[] for _ in range(nsigns)]
        for i, t in enumerate(self.texts):
            for s in set(t.tolist()):
                self.sign_texts[s].append(i)
        self.windows = []  # per text: list of (k, offs array (W,k) of sign ids)
        for t in self.texts:
            L = len(t); w = []
            for k, arr in self.ni.by_k.items():
                if k <= L:
                    idx = np.arange(L - k + 1)[:, None] + np.arange(k)[None, :]
                    w.append((k, t[idx]))
            self.windows.append(w)

    def text_score(self, i, key):
        best = 0
        for k, win in self.windows[i]:
            r = key[win]                                  # (W,k) values, -1 unassigned
            m = (self.ni.by_k[k][:, None, :] == r[None, :, :]).sum(-1)  # (N,W)
            mx = m.max()
            if mx >= max(2, k - tol(k)) and mx > best:
                best = int(mx)
        return best

    def score(self, key):
        return sum(self.text_score(i, key) for i in range(len(self.texts)))

    def _propose(self, key):
        i = self.rng.integers(len(self.texts))
        ws = self.windows[i]
        if not ws:
            return None
        k, win = ws[self.rng.integers(len(ws))]
        arr = self.ni.by_k[k]
        r = key[win]
        m = (arr[:, None, :] == r[None, :, :]).sum(-1).astype(float)   # (N,W)
        # conflicts: assigned sign whose value differs
        conf = ((r[None, :, :] >= 0) & (arr[:, None, :] != r[None, :, :])).sum(-1)
        w = np.exp(1.5 * m - 1.0 * conf).ravel()
        j = self.rng.choice(w.size, p=w / w.sum())
        n_, o_ = divmod(j, win.shape[0])
        return win[o_], arr[n_]

    def run(self, iters, restarts=3, t0=2.0, t1=0.05):
        best_S, best_key = -1, None
        for _ in range(restarts):
            key = -np.ones(self.nsigns, dtype=np.int32)
            owner = -np.ones(self.ni.nv, dtype=np.int32)
            qs = np.zeros(len(self.texts), dtype=np.int32)
            S = 0
            for it in range(iters):
                T = t0 * (t1 / t0) ** (it / max(1, iters - 1))
                if self.rng.random() < 0.1:
                    a = np.flatnonzero(key >= 0)
                    if a.size == 0:
                        continue
                    s = int(a[self.rng.integers(a.size)])
                    changes = {s: -1}
                else:
                    p = self._propose(key)
                    if p is None:
                        continue
                    sg, vals = p
                    changes, ok = {}, True
                    for s, v in zip(sg.tolist(), vals.tolist()):
                        if changes.get(s, v) != v:
                            ok = False; break
                        changes[s] = v
                    if not ok or len(set(changes.values())) < len(changes):
                        continue
                # apply tentatively
                old = {}
                for s, v in changes.items():
                    old[s] = key[s]
                    if v >= 0 and owner[v] >= 0 and owner[v] != s and owner[v] not in old:
                        old[int(owner[v])] = key[owner[v]]
                newkey = key.copy()
                for s in old:
                    newkey[s] = -1
                for s, v in changes.items():
                    newkey[s] = v
                if np.array_equal(newkey, key):
                    continue
                aff = set()
                for s in old:
                    aff.update(self.sign_texts[s])
                aff = list(aff)
                nq = np.array([self.text_score(i, newkey) for i in aff], dtype=np.int32)
                d = int(nq.sum() - qs[aff].sum())
                if d >= 0 or self.rng.random() < np.exp(d / T):
                    for s in old:
                        if key[s] >= 0:
                            owner[key[s]] = -1
                    key = newkey
                    for s, v in changes.items():
                        if v >= 0:
                            owner[v] = s
                    qs[aff] = nq; S += d
                    if S > best_S:
                        best_S, best_key = S, key.copy()
        return best_S, best_key
