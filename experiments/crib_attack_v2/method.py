"""Crib attack v2 (task #26, H10): simulator with real text lengths + exact-match search.

Simulated script: CV syllabary (values = all CV values of all lists) + N_FRAME frame signs
(Zipf) + N_LOGO logograms.  A name text carries one planted name spelled in CV, each name sign
misread (replaced by a uniformly random sign) with prob `misread`; the remaining slots of the
real length are filled with frame signs (split before/after at random).  A name-free text is
frame+logogram signs.  Text lengths are the real lengths (see LENGTHS in run_grid.py).

Score E(key) = number of texts that contain, as a contiguous window, an EXACT full spelling of
>= 3 signs from the attacker's list.  Search = simulated annealing on E with constructive moves
(force a window of a text to read as a list spelling, evicting conflicting assignments) and
random un-assign moves.  Anchors: `anchors` = {sign: value} fixed for the whole search; no other
sign may take an anchored value.
"""
import numpy as np

N_FRAME, N_LOGO = 12, 40
KMIN = 3


def zipf_p(n, a=1.0):
    w = 1.0 / np.arange(1, n + 1) ** a
    return w / w.sum()


def make_corpus(lengths, name_units, values, rng, write_cv, p_name=0.75, misread=0.2):
    nv = len(values); vid = {v: i for i, v in enumerate(values)}
    perm = rng.permutation(nv)
    nsigns = nv + N_FRAME + N_LOGO
    true_key = -np.ones(nsigns, dtype=np.int32); true_key[perm] = np.arange(nv)
    frame = nv + np.arange(N_FRAME); logo = nv + N_FRAME + np.arange(N_LOGO)
    pf, pl = zipf_p(N_FRAME), zipf_p(N_LOGO)
    texts, flags = [], []
    for L in lengths:
        body = None
        if rng.random() < p_name:
            for _ in range(50):
                sp = write_cv(name_units[rng.integers(len(name_units))], rng)
                if sp and 2 <= len(sp) <= L and all(x in vid for x in sp):
                    body = [int(perm[vid[x]]) for x in sp]; break
        if body is not None:
            body = [int(rng.integers(nsigns)) if rng.random() < misread else s for s in body]
            nf = L - len(body)
            fr = [int(x) for x in rng.choice(frame, size=nf, p=pf)]
            nb = int(rng.integers(nf + 1))
            texts.append(fr[:nb] + body + fr[nb:]); flags.append(True)
        else:
            pool = np.concatenate([frame, logo]); p = np.concatenate([pf, pl]) / 2
            texts.append([int(x) for x in rng.choice(pool, size=L, p=p)]); flags.append(False)
    return dict(texts=texts, true_key=true_key, nsigns=nsigns, name_text=flags, perm=perm)


def shuffle_texts(texts, rng):
    toks = np.concatenate([np.asarray(t) for t in texts]); rng.shuffle(toks)
    out, i = [], 0
    for t in texts:
        out.append(toks[i:i + len(t)].tolist()); i += len(t)
    return out


class NameIndex:
    def __init__(self, spellings, vid):
        by = {}
        for sp in spellings:
            if len(sp) >= KMIN:
                by.setdefault(len(sp), []).append([vid[x] for x in sp])
        self.by_k = {k: np.array(v, dtype=np.int32) for k, v in sorted(by.items())}
        self.sets = {k: {tuple(x) for x in v} for k, v in by.items()}


class Attack:
    def __init__(self, texts, ni, nsigns, nv, rng, anchors=None):
        self.texts = [np.asarray(t, dtype=np.int32) for t in texts]
        self.ni, self.rng, self.nsigns, self.nv = ni, rng, nsigns, nv
        self.anchors = dict(anchors or {})
        self.sign_texts = [[] for _ in range(nsigns)]
        for i, t in enumerate(self.texts):
            for s in set(t.tolist()):
                self.sign_texts[s].append(i)
        self.windows = []
        for t in self.texts:
            L = len(t); w = []
            for k in self.ni.by_k:
                if k <= L:
                    idx = np.arange(L - k + 1)[:, None] + np.arange(k)[None, :]
                    w.append((k, t[idx]))
            self.windows.append(w)
        self.matchable = [i for i, w in enumerate(self.windows) if w]

    def base_key(self):
        key = -np.ones(self.nsigns, dtype=np.int32)
        for s, v in self.anchors.items():
            key[s] = v
        return key

    def text_hit(self, i, key):
        for k, win in self.windows[i]:
            S = self.ni.sets[k]
            for row in key[win].tolist():
                if tuple(row) in S:
                    return 1
        return 0

    def match_window(self, i, key):
        for k, win in self.windows[i]:
            r = key[win]
            hit = (self.ni.by_k[k][:, None, :] == r[None]).all(-1)
            if hit.any():
                return win[np.argwhere(hit)[0][1]]
        return None

    def score(self, key):
        return sum(self.text_hit(i, key) for i in self.matchable)

    def _propose(self, key, hits):
        cand = [i for i in self.matchable if not hits[i]]
        if not cand or self.rng.random() < 0.2:
            cand = self.matchable
        i = cand[self.rng.integers(len(cand))]
        ws = self.windows[i]
        k, win = ws[self.rng.integers(len(ws))]
        o = int(self.rng.integers(win.shape[0])); sg = win[o]
        arr = self.ni.by_k[k]
        # a sign repeated inside the window must take one value
        r = key[sg]
        anch = np.array([s in self.anchors for s in sg.tolist()])
        ok = np.ones(arr.shape[0], bool)
        for j in range(k):
            if anch[j]:
                ok &= arr[:, j] == r[j]
        for a in range(k):
            for b in range(a + 1, k):
                if sg[a] == sg[b]:
                    ok &= arr[:, a] == arr[:, b]
                else:
                    ok &= arr[:, a] != arr[:, b]
        if self.anchors:
            av = np.array(list(self.anchors.values()))
            for j in range(k):
                if not anch[j]:
                    ok &= ~np.isin(arr[:, j], av)
        if not ok.any():
            return None
        m = (arr == r[None]).sum(-1).astype(float)
        conf = ((r[None] >= 0) & (arr != r[None])).sum(-1)
        w = np.where(ok, np.exp(1.0 * m - 1.0 * conf), 0.0)
        n_ = self.rng.choice(w.size, p=w / w.sum())
        return sg, arr[n_]

    def run(self, iters, restarts=3, t0=1.0, t1=0.05):
        best_E, best_key = -1, None
        for _ in range(restarts):
            key = self.base_key()
            owner = -np.ones(self.nv, dtype=np.int32)
            for s, v in self.anchors.items():
                owner[v] = s
            hits = np.zeros(len(self.texts), dtype=np.int32)
            E = 0
            if best_E < 0:
                best_E, best_key = 0, key.copy()
            for it in range(iters):
                T = t0 * (t1 / t0) ** (it / max(1, iters - 1))
                if self.rng.random() < 0.1:
                    a = np.flatnonzero(key >= 0)
                    a = a[[s not in self.anchors for s in a.tolist()]] if self.anchors else a
                    if a.size == 0:
                        continue
                    changes = {int(a[self.rng.integers(a.size)]): -1}
                else:
                    p = self._propose(key, hits)
                    if p is None:
                        continue
                    changes = {int(s): int(v) for s, v in zip(p[0].tolist(), p[1].tolist())}
                old = {}
                for s, v in changes.items():
                    old[s] = key[s]
                    if v >= 0 and owner[v] >= 0 and owner[v] != s:
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
                aff = [i for i in aff if self.windows[i]]
                nq = np.array([self.text_hit(i, newkey) for i in aff], dtype=np.int32)
                d = int(nq.sum() - hits[aff].sum()) if aff else 0
                if d >= 0 or self.rng.random() < np.exp(d / T):
                    for s in old:
                        if key[s] >= 0:
                            owner[key[s]] = -1
                    key = newkey
                    for s, v in changes.items():
                        if v >= 0:
                            owner[v] = s
                    if aff:
                        hits[aff] = nq
                    E += d
                    if E > best_E:
                        best_E, best_key = E, key.copy()
        return best_E, best_key

    def reading(self, key):
        """Signs used in the first exact-match window of each matched text (anchors excluded)."""
        used = set()
        for i in self.matchable:
            w = self.match_window(i, key)
            if w is not None:
                used.update(int(s) for s in w.tolist())
        return sorted(used - set(self.anchors))
