"""Genres from scratch (board #34, N2). Shared library: four unsupervised genre models,
K selection by family CV, association tests, stability.  Prereg: docs/prereg/genres_from_scratch.md

Units are dicts from glib.unit_from: runs=[(tuple signs, bos, eos)], signs=tuple, full=bool, + labels.
No model function ever reads a label field.
"""
import math
import random
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from scipy.special import logsumexp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments/grammar"))
import glib  # noqa: E402  (read-only import: families, make_runs, unit_from)

LN2 = math.log(2)
LDA_ITERS = 30


# ------------------------------------------------------------------ encoding
class Enc:
    """train-vocab encoder: signs with count>=2 in train -> 0..V-1, UNK=V"""

    def __init__(self, units, min_count=2):
        c = Counter(x for u in units for r, _, _ in u["runs"] for x in r)
        self.vocab = sorted(w for w, n in c.items() if n >= min_count)
        self.idx = {w: i for i, w in enumerate(self.vocab)}
        self.V = len(self.vocab) + 1  # incl UNK
        self.UNK = self.V - 1

    def enc(self, run):
        return [self.idx.get(x, self.UNK) for x in run]


# ------------------------------------------------------------------ base class
class Mixture:
    name = "base"

    def fit(self, units, K, seed=0, restarts=3, iters=60):
        best = None
        for r in range(restarts):
            m = self._fit_once(units, K, seed * 101 + r, iters)
            if best is None or m[0] > best[0]:
                best = m
        self.params = best[1]
        self.K = K
        return self

    def unit_comp_ll(self, units):  # (N, K) log p(unit | k)
        raise NotImplementedError

    def loglik(self, units):  # per-unit log p (nats)
        L = self.unit_comp_ll(units) + np.log(self.params["pi"])[None, :]
        return logsumexp(L, axis=1)

    def posterior(self, units):
        L = self.unit_comp_ll(units) + np.log(self.params["pi"])[None, :]
        return np.exp(L - logsumexp(L, axis=1, keepdims=True))

    def assign(self, units):
        return self.posterior(units).argmax(1)


def _rand_resp(N, K, rng):
    return rng.dirichlet(np.ones(K) * 0.5, size=N)


# ------------------------------------------------------------------ 1. mixture of bigrams
class BG(Mixture):
    name = "BG"
    beta, gamma = 2.0, 20.0

    def _events(self, units):
        V = self.enc.V
        BOS, EOS = V, V  # row index V = BOS ; col index V = EOS
        pr, nx, uu, ut, uunit = [], [], [], [], []
        for i, u in enumerate(units):
            for run, bos, eos in u["runs"]:
                s = self.enc.enc(run)
                if bos:
                    pr.append(BOS); nx.append(s[0]); uu.append(i)
                else:
                    ut.append(s[0]); uunit.append(i)
                for a, b in zip(s, s[1:]):
                    pr.append(a); nx.append(b); uu.append(i)
                if eos:
                    pr.append(s[-1]); nx.append(EOS); uu.append(i)
        return (np.array(pr), np.array(nx), np.array(uu), np.array(ut, dtype=int), np.array(uunit, dtype=int))

    def _mstep(self, ev, R, N):
        pr, nx, uu, ut, uunit = ev
        V, K = self.enc.V, R.shape[1]
        W = R[uu]  # (E, K)
        P = np.empty((K, V + 1, V + 1))
        uni = np.empty((K, V))
        for k in range(K):
            C = np.zeros((V + 1, V + 1))
            np.add.at(C, (pr, nx), W[:, k])
            col = C.sum(0)
            q = (col + self.gamma * self.g) / (col.sum() + self.gamma)
            P[k] = (C + self.beta * q[None, :]) / (C.sum(1, keepdims=True) + self.beta)
            cu = col[:V] + np.bincount(ut, weights=R[uunit, k], minlength=V)
            uni[k] = (cu + self.gamma * self.g[:V] / self.g[:V].sum()) / (cu.sum() + self.gamma)
        pi = (R.sum(0) + 1e-3) / (N + K * 1e-3)
        return dict(lP=np.log(P), lU=np.log(uni), pi=pi)

    def _cll(self, ev, prm, N):
        pr, nx, uu, ut, uunit = ev
        K = len(prm["pi"])
        out = np.zeros((N, K))
        for k in range(K):
            out[:, k] = np.bincount(uu, weights=prm["lP"][k][pr, nx], minlength=N)
            if len(ut):
                out[:, k] += np.bincount(uunit, weights=prm["lU"][k][ut], minlength=N)
        return out

    def _fit_once(self, units, K, seed, iters):
        rng = np.random.default_rng(seed)
        self.enc = Enc(units)
        ev = self._events(units)
        V = self.enc.V
        col = np.bincount(ev[1], minlength=V + 1).astype(float) + 0.5
        self.g = col / col.sum()
        N = len(units)
        R = _rand_resp(N, K, rng)
        last = -np.inf
        for it in range(iters):
            prm = self._mstep(ev, R, N)
            L = self._cll(ev, prm, N) + np.log(prm["pi"])[None, :]
            tot = logsumexp(L, axis=1)
            R = np.exp(L - tot[:, None])
            ll = tot.sum()
            if ll - last < 1e-4 * N:
                break
            last = ll
        return ll, prm

    def unit_comp_ll(self, units):
        return self._cll(self._events(units), self.params, len(units))


# ------------------------------------------------------------------ 2. mixture of HMMs
class HMM(Mixture):
    name = "HMM"
    S = 4
    a_em, a_tr = 5.0, 0.5

    def _pad(self, units):
        runs, ru, bos, eos = [], [], [], []
        for i, u in enumerate(units):
            for r, b, e in u["runs"]:
                runs.append(self.enc.enc(r)); ru.append(i); bos.append(b); eos.append(e)
        T = max(len(r) for r in runs)
        X = np.zeros((len(runs), T), dtype=int)
        M = np.zeros((len(runs), T), dtype=bool)
        for j, r in enumerate(runs):
            X[j, :len(r)] = r; M[j, :len(r)] = True
        lens = M.sum(1)
        return X, M, lens, np.array(ru), np.array(bos), np.array(eos)

    def _fb(self, d, st, B, A, end, need_post):
        """scaled forward-backward for one component; returns per-run loglik and expected counts"""
        X, M, lens, ru, bos, eos = d
        n, T = X.shape
        S = self.S
        E = B[:, X].transpose(1, 2, 0)  # (n, T, S)
        al = np.zeros((n, T, S)); c = np.zeros((n, T))
        a = st[None, :] * E[:, 0]
        c[:, 0] = a.sum(1); al[:, 0] = a / c[:, 0:1]
        for t in range(1, T):
            a = (al[:, t - 1] @ A) * E[:, t]
            s = a.sum(1)
            m = M[:, t]
            c[:, t] = np.where(m, s, 1.0)
            al[:, t] = np.where(m[:, None], a / np.where(m, s, 1.0)[:, None], al[:, t - 1])
        last = al[np.arange(n), lens - 1]
        endf = np.where(eos[:, None], end[None, :], 1.0)
        zl = (last * endf).sum(1)
        ll = np.log(c).sum(1) + np.log(zl)
        if not need_post:
            return ll, None
        be = np.ones((n, T, S))
        be[np.arange(n), lens - 1] = endf / zl[:, None]
        for t in range(T - 2, -1, -1):
            m = M[:, t + 1]
            b = ((E[:, t + 1] * be[:, t + 1]) @ A.T) / c[:, t + 1:t + 2]
            be[:, t] = np.where(m[:, None], b, be[:, t])
        gam = al * be * M[:, :, None]
        # xi summed over t
        xi = np.zeros((n, S, S))
        for t in range(1, T):
            m = M[:, t]
            if not m.any():
                break
            x = al[:, t - 1, :, None] * A[None] * (E[:, t] * be[:, t])[:, None, :] / c[:, t][:, None, None]
            xi += x * m[:, None, None]
        return ll, (gam, xi, last * endf / zl[:, None])

    def _fit_once(self, units, K, seed, iters):
        rng = np.random.default_rng(seed)
        self.enc = Enc(units)
        d = self._pad(units)
        X, M, lens, ru, bos, eos = d
        V, S, N = self.enc.V, self.S, len(units)
        g = np.bincount(X[M], minlength=V) + 0.5
        self.g = g / g.sum()
        st = rng.dirichlet(np.ones(S), size=K)
        A = rng.dirichlet(np.ones(S) * 2, size=(K, S))
        end = rng.uniform(0.1, 0.4, size=(K, S))
        B = np.array([[rng.dirichlet(self.g * 50 + 0.01) for _ in range(S)] for _ in range(K)])
        pi = np.ones(K) / K
        last = -np.inf
        for it in range(iters):
            lls, posts = [], []
            for k in range(K):
                At = A[k] * (1 - end[k])[:, None]
                ll, p = self._fb(d, st[k], B[k], At, end[k], True)
                lls.append(np.bincount(ru, weights=ll, minlength=N)); posts.append(p)
            L = np.stack(lls, 1) + np.log(pi)[None]
            tot = logsumexp(L, 1)
            R = np.exp(L - tot[:, None])
            llsum = tot.sum()
            for k in range(K):
                gam, xi, fin = posts[k]
                w = R[ru, k]
                gw = gam * w[:, None, None]
                st_c = (gw[:, 0] * bos[:, None]).sum(0) + self.a_tr
                st[k] = st_c / st_c.sum()
                tr = (xi * w[:, None, None]).sum(0)
                en = (fin * (w * eos)[:, None]).sum(0)
                tot_out = tr.sum(1) + en
                end[k] = (en + self.a_tr) / (tot_out + 2 * self.a_tr)
                A[k] = (tr + self.a_tr) / (tr.sum(1, keepdims=True) + S * self.a_tr)
                em = np.zeros((S, V))
                for s in range(S):
                    em[s] = np.bincount(X[M], weights=gw[:, :, s][M], minlength=V)
                B[k] = (em + self.a_em * self.g[None]) / (em.sum(1, keepdims=True) + self.a_em)
            pi = (R.sum(0) + 1e-3) / (N + K * 1e-3)
            if llsum - last < 1e-4 * N:
                break
            last = llsum
        return llsum, dict(st=st.copy(), A=A.copy(), end=end.copy(), B=B.copy(), pi=pi)

    def unit_comp_ll(self, units):
        d = self._pad(units)
        p = self.params
        out = []
        for k in range(len(p["pi"])):
            At = p["A"][k] * (1 - p["end"][k])[:, None]
            ll, _ = self._fb(d, p["st"][k], p["B"][k], At, p["end"][k], False)
            out.append(np.bincount(d[3], weights=ll, minlength=len(units)))
        return np.stack(out, 1)


# ------------------------------------------------------------------ 3. latent class model on formula features
class LCA(Mixture):
    name = "LCA"
    a = 2.0

    @staticmethod
    def feats(u):
        runs = u["runs"]
        first_ok = runs[0][1]
        last_ok = runs[-1][2]
        r0, r1 = runs[0][0], runs[-1][0]
        f = [None] * 5
        if first_ok:
            f[0] = r0[0]
            f[1] = r0[1] if len(r0) > 1 else ("<END>" if last_ok else None)
        if last_ok:
            f[3] = r1[-1]
            f[2] = r1[-2] if len(r1) > 1 else ("<BEG>" if first_ok else None)
        if u["full"]:
            n = len(u["signs"])
            f[4] = str(min(n, 7))
        return f

    def _code(self, units):
        F = np.full((len(units), 5), -1, dtype=int)
        for i, u in enumerate(units):
            for j, x in enumerate(self.feats(u)):
                if x is not None:
                    F[i, j] = self.cats[j].get(x, self.cats[j]["<UNK>"])
        return F

    def _fit_once(self, units, K, seed, iters):
        rng = np.random.default_rng(seed)
        raw = [self.feats(u) for u in units]
        self.cats = []
        for j in range(5):
            c = Counter(r[j] for r in raw if r[j] is not None)
            keep = sorted(w for w, n in c.items() if n >= 2)
            d = {w: i for i, w in enumerate(keep)}
            d["<UNK>"] = len(keep)
            self.cats.append(d)
        F = self._code(units)
        N = len(units)
        self.g = []
        for j in range(5):
            m = F[:, j] >= 0
            c = np.bincount(F[m, j], minlength=len(self.cats[j])) + 0.5
            self.g.append(c / c.sum())
        R = _rand_resp(N, K, rng)
        last = -np.inf
        for it in range(iters):
            prm = self._m(F, R, N)
            L = self._cll(F, prm) + np.log(prm["pi"])[None]
            tot = logsumexp(L, 1)
            R = np.exp(L - tot[:, None])
            ll = tot.sum()
            if ll - last < 1e-4 * N:
                break
            last = ll
        return ll, prm

    def _m(self, F, R, N):
        K = R.shape[1]
        th = []
        for j in range(5):
            m = F[:, j] >= 0
            C = np.stack([np.bincount(F[m, j], weights=R[m, k], minlength=len(self.cats[j])) for k in range(K)])
            th.append(np.log((C + self.a * self.g[j][None]) / (C.sum(1, keepdims=True) + self.a)))
        return dict(th=th, pi=(R.sum(0) + 1e-3) / (N + K * 1e-3))

    def _cll(self, F, prm):
        K = len(prm["pi"])
        out = np.zeros((F.shape[0], K))
        for j in range(5):
            m = F[:, j] >= 0
            out[m] += prm["th"][j][:, F[m, j]].T
        return out

    def unit_comp_ll(self, units):
        return self._cll(self._code(units), self.params)


# ------------------------------------------------------------------ 4. topic model (LDA) over signs + pairs
class LDA(Mixture):
    name = "LDA"

    @staticmethod
    def doc(u):
        toks = []
        for r, _, _ in u["runs"]:
            toks += list(r)
            toks += [f"{a}_{b}" for a, b in zip(r, r[1:])]
        return toks

    def _X(self, units):
        from scipy.sparse import csr_matrix
        rows, cols = [], []
        for i, u in enumerate(units):
            for t in self.doc(u):
                j = self.voc.get(t)
                if j is not None:
                    rows.append(i); cols.append(j)
        return csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(len(units), len(self.voc)))

    def fit(self, units, K, seed=0, restarts=1, iters=None):
        iters = iters or LDA_ITERS
        from sklearn.decomposition import LatentDirichletAllocation
        c = Counter(t for u in units for t in self.doc(u))
        self.voc = {w: i for i, w in enumerate(sorted(w for w, n in c.items() if n >= 2))}
        X = self._X(units)
        self.m = LatentDirichletAllocation(n_components=K, learning_method="batch", max_iter=iters,
                                           random_state=seed, n_jobs=1).fit(X)
        self.K = K
        th = self.m.transform(X)
        self.params = dict(pi=th.mean(0))
        return self

    def heldout_score(self, units):
        """per-text variational bound on held-out texts (nats/text), comparable across K"""
        X = self._X(units)
        n_words = X.sum()
        perp = self.m.perplexity(X)
        return -math.log(perp) * n_words / len(units)

    def posterior(self, units):
        th = self.m.transform(self._X(units))
        return th

    def loglik(self, units):
        raise NotImplementedError


MODELS = {"BG": BG, "HMM": HMM, "LCA": LCA, "LDA": LDA}


# ------------------------------------------------------------------ splits / K selection
def family_split(units, frac=0.25, seed=34):
    fam = glib.families(units)
    ids = sorted(set(fam))
    rng = random.Random(seed); rng.shuffle(ids)
    n_ho = int(round(frac * len(units)))
    ho_f, cnt = set(), Counter(fam)
    tot = 0
    for f in ids:
        if tot >= n_ho:
            break
        ho_f.add(f); tot += cnt[f]
    tr = [u for u, f in zip(units, fam) if f not in ho_f]
    te = [u for u, f in zip(units, fam) if f in ho_f]
    return tr, te


def cv_curve(name, units, Ks, folds=5, seed=0, restarts=3):
    """family k-fold CV; returns {K: per-text held-out loglik array (aligned to units order)} or fold scores for LDA"""
    fold = glib.family_folds(units, k=folds, seed=seed)
    res = {}
    for K in Ks:
        if name == "LDA":
            sc = []
            for f in range(folds):
                tr = [u for u, z in zip(units, fold) if z != f]
                te = [u for u, z in zip(units, fold) if z == f]
                m = LDA().fit(tr, K, seed=seed)
                sc.append(m.heldout_score(te))
            res[K] = np.array(sc)
        else:
            ll = np.zeros(len(units))
            for f in range(folds):
                idx = [i for i, z in enumerate(fold) if z == f]
                tr = [u for u, z in zip(units, fold) if z != f]
                m = MODELS[name]().fit(tr, K, seed=seed * 7 + f, restarts=restarts)
                ll[idx] = m.loglik([units[i] for i in idx])
            res[K] = ll
    return res


def pick_K(res):
    """1-SE rule on paired differences against the best K"""
    Ks = sorted(res)
    means = {K: float(np.mean(res[K])) for K in Ks}
    best = max(Ks, key=lambda K: means[K])
    for K in Ks:
        d = res[best] - res[K]
        se = float(np.std(d, ddof=1) / math.sqrt(len(d))) if len(d) > 1 else 0.0
        if means[best] - means[K] <= se:
            return K, means, best
    return best, means, best


# ------------------------------------------------------------------ association tests
def gain(gd, yd, gh, yh, K, labels):
    """held-out bits/text gained by P(label|genre) (fit on dev) over the dev base rate"""
    L = len(labels)
    li = {l: i for i, l in enumerate(labels)}
    yd_i = np.array([li[y] for y in yd]); yh_i = np.array([li[y] for y in yh])
    C = np.zeros((K, L)) + 0.5
    np.add.at(C, (np.asarray(gd), yd_i), 1)
    Pg = np.log2(C / C.sum(1, keepdims=True))
    base = np.log2((np.bincount(yd_i, minlength=L) + 0.5) / (len(yd_i) + 0.5 * L))
    return Pg, base, yh_i


def g_stat(Pg, base, gh, yh_i):
    return float(np.mean(Pg[gh, yh_i] - base[yh_i]))


def assoc_test(gd, yd, gh, yh, K, nperm=2000, seed=0, strata=None):
    labels = sorted(set(yd) | set(yh))
    Pg, base, yh_i = gain(gd, yd, gh, yh, K, labels)
    gh = np.asarray(gh)
    obs = g_stat(Pg, base, gh, yh_i)
    rng = np.random.default_rng(seed)
    null = np.empty(nperm)
    if strata is None:
        for b in range(nperm):
            null[b] = g_stat(Pg, base, gh, rng.permutation(yh_i))
    else:
        strata = np.asarray(strata)
        groups = [np.where(strata == s)[0] for s in set(strata)]
        for b in range(nperm):
            y = yh_i.copy()
            for gi in groups:
                y[gi] = y[rng.permutation(gi)]
            null[b] = g_stat(Pg, base, gh, y)
    p = (1 + np.sum(null >= obs)) / (nperm + 1)
    return dict(G=obs, p=float(p), null_mean=float(null.mean()), null_q95=float(np.quantile(null, 0.95)))


def nmi(a, b):
    from sklearn.metrics import normalized_mutual_info_score
    return float(normalized_mutual_info_score(a, b))


def ari(a, b):
    from sklearn.metrics import adjusted_rand_score
    return float(adjusted_rand_score(a, b))


def stability(name, units, K, n=20, seed=0, restarts=2):
    fam = glib.families(units)
    ids = sorted(set(fam))
    by = {}
    for i, f in enumerate(fam):
        by.setdefault(f, []).append(i)
    rng = np.random.default_rng(seed)
    assigns = []
    for b in range(n):
        pick = rng.choice(len(ids), size=len(ids), replace=True)
        tr = [units[i] for p in pick for i in by[ids[p]]]
        m = MODELS[name]().fit(tr, K, seed=1000 + b, restarts=restarts)
        assigns.append(m.assign(units))
    a = [ari(assigns[i], assigns[j]) for i in range(n) for j in range(i + 1, n)]
    return dict(median=float(np.median(a)), q10=float(np.quantile(a, 0.1)), q90=float(np.quantile(a, 0.9)))


# ------------------------------------------------------------------ supervised reference
def nb_gain(dev, ho, yd, yh):
    """multinomial NB on sign unigrams+pairs: held-out bits/text over base rate (for placing plants on the real scale)"""
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.naive_bayes import MultinomialNB
    cv = CountVectorizer(analyzer=lambda u: LDA.doc(u), min_df=2)
    Xd = cv.fit_transform(dev); Xh = cv.transform(ho)
    nb = MultinomialNB(alpha=0.5).fit(Xd, yd)
    P = nb.predict_proba(Xh)
    cls = list(nb.classes_)
    labels = sorted(set(yd) | set(yh))
    base = Counter(yd)
    out = []
    for i, y in enumerate(yh):
        pb = (base.get(y, 0) + 0.5) / (len(yd) + 0.5 * len(labels))
        pm = P[i, cls.index(y)] if y in cls else 1e-6
        out.append(math.log2(max(pm, 1e-6)) - math.log2(pb))
    return float(np.mean(out))


# ------------------------------------------------------------------ amendment A1: tilted bigram mixture
class BG2(BG):
    """Components are tilts of one shared bigram model: P_k(b|a) = (C_k(a,b) + beta*P0(b|a)) / (C_k(a) + beta),
    P0 = global bigram backed off to the global unigram.  Added after BG failed the known-answer test (A1)."""
    name = "BG2"
    beta = 80.0  # frozen by amendment A1
    lam = 2.0

    def _mstep(self, ev, R, N):
        pr, nx, uu, ut, uunit = ev
        V, K = self.enc.V, R.shape[1]
        W = R[uu]
        P = np.empty((K, V + 1, V + 1)); uni = np.empty((K, V))
        for k in range(K):
            C = np.zeros((V + 1, V + 1))
            np.add.at(C, (pr, nx), W[:, k])
            P[k] = (C + self.beta * self.P0) / (C.sum(1, keepdims=True) + self.beta)
            cu = C.sum(0)[:V] + np.bincount(ut, weights=R[uunit, k], minlength=V)
            uni[k] = (cu + self.beta * self.U0) / (cu.sum() + self.beta)
        pi = (R.sum(0) + 1e-3) / (N + K * 1e-3)
        return dict(lP=np.log(P), lU=np.log(uni), pi=pi)

    def _fit_once(self, units, K, seed, iters):
        self.enc = Enc(units)
        ev = self._events(units)
        V = self.enc.V
        col = np.bincount(ev[1], minlength=V + 1).astype(float) + 0.5
        self.g = col / col.sum()
        C = np.zeros((V + 1, V + 1)); np.add.at(C, (ev[0], ev[1]), 1.0)
        self.P0 = (C + self.lam * self.g[None]) / (C.sum(1, keepdims=True) + self.lam)
        self.U0 = self.g[:V] / self.g[:V].sum()
        return self._em(units, K, seed, iters, ev)

    def _em(self, units, K, seed, iters, ev):
        rng = np.random.default_rng(seed)
        N = len(units)
        R = _rand_resp(N, K, rng)
        last = -np.inf
        for it in range(iters):
            prm = self._mstep(ev, R, N)
            L = self._cll(ev, prm, N) + np.log(prm["pi"])[None, :]
            tot = logsumexp(L, axis=1)
            R = np.exp(L - tot[:, None])
            ll = tot.sum()
            if ll - last < 1e-4 * N:
                break
            last = ll
        return ll, prm


MODELS["BG2"] = BG2
