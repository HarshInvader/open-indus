"""Small discrete HMM (Baum-Welch, scaled forward-backward, length-batched)
with an optional left-to-right ('profile' / slot-template) topology, plus an
interpolated Kneser-Ney bigram baseline. Every text ends with an explicit end
transition so likelihoods are proper distributions over whole texts."""
from collections import Counter, defaultdict

import numpy as np


class Vocab:
    def __init__(self, texts, min_count=2):
        c = Counter(s for t in texts for s in t)
        self.itos = ["<unk>"] + sorted(s for s, n in c.items() if n >= min_count)
        self.stoi = {s: i for i, s in enumerate(self.itos)}

    def enc(self, t):
        return [self.stoi.get(s, 0) for s in t]

    def __len__(self):
        return len(self.itos)


def batches(texts):
    by = defaultdict(list)
    for t in texts:
        by[len(t)].append(t)
    return {L: np.array(v, int) for L, v in by.items()}


class HMM:
    """K hidden states. start pi (K), trans A (K x K), end e (K), emissions B (K x V).
    topology='ergodic' or 'lr' (state j reachable from i only if j>i; selfloop
    optional)."""

    def __init__(self, K, V, topology="ergodic", selfloop=False, seed=0, emis_prior=0.05):
        rng = np.random.default_rng(seed)
        self.K, self.V, self.top, self.selfloop = K, V, topology, selfloop
        self.mask = np.ones((K, K))
        if topology == "lr":
            self.mask = np.triu(np.ones((K, K)), k=0 if selfloop else 1)
        self.A = rng.random((K, K)) * self.mask
        self.e = rng.random(K) + 0.5
        z = self.A.sum(1) + self.e
        self.A /= z[:, None]; self.e /= z
        self.pi = rng.random(K) + (np.linspace(2, 0.1, K) if topology == "lr" else 0)
        self.pi /= self.pi.sum()
        self.B = rng.random((K, V)) + 0.1
        self.B /= self.B.sum(1, keepdims=True)
        self.prior = emis_prior

    def _fb(self, X):
        N, L = X.shape
        K = self.K
        Bx = self.B[:, X].transpose(1, 2, 0)  # N x L x K
        al = np.zeros((N, L, K)); c = np.zeros((N, L + 1))
        a = self.pi[None] * Bx[:, 0]
        c[:, 0] = a.sum(1); al[:, 0] = a / c[:, :1]
        for t in range(1, L):
            a = (al[:, t - 1] @ self.A) * Bx[:, t]
            c[:, t] = a.sum(1); al[:, t] = a / c[:, t:t + 1]
        fin = al[:, -1] @ self.e
        c[:, L] = fin
        ll = np.log(c).sum(1)
        be = np.zeros((N, L, K))
        be[:, -1] = self.e[None] / fin[:, None]
        for t in range(L - 2, -1, -1):
            be[:, t] = ((be[:, t + 1] * Bx[:, t + 1]) @ self.A.T) / c[:, t + 1:t + 2]
        return al, be, c, Bx, ll

    def loglik(self, data):
        tot = 0.0
        for L, X in data.items():
            tot += self._fb(X)[-1].sum()
        return tot

    def fit(self, data, iters=150, tol=1e-4):
        prev = -np.inf
        for it in range(iters):
            sA = np.zeros((self.K, self.K)); se = np.zeros(self.K); spi = np.zeros(self.K)
            sB = np.zeros((self.K, self.V)) + self.prior
            ll = 0.0
            for L, X in data.items():
                al, be, c, Bx, lls = self._fb(X)
                ll += lls.sum()
                g = al * be  # N x L x K posteriors (scaled so rows sum to 1)
                g /= g.sum(2, keepdims=True)
                spi += g[:, 0].sum(0)
                se += g[:, -1].sum(0)
                for t in range(L):
                    np.add.at(sB.T, X[:, t], g[:, t])
                for t in range(L - 1):
                    xi = al[:, t][:, :, None] * self.A[None] * (Bx[:, t + 1] * be[:, t + 1])[:, None, :] / c[:, t + 1][:, None, None]
                    sA += xi.sum(0)
            sA *= self.mask
            z = sA.sum(1) + se + 1e-12
            self.A = sA / z[:, None]; self.e = se / z
            self.pi = spi / spi.sum()
            self.B = sB / sB.sum(1, keepdims=True)
            if ll - prev < tol * abs(ll):
                break
            prev = ll
        return ll

    def viterbi(self, x):
        x = np.asarray(x)
        lA = np.log(self.A + 1e-300); lB = np.log(self.B + 1e-300)
        d = np.log(self.pi + 1e-300) + lB[:, x[0]]
        bp = []
        for t in range(1, len(x)):
            m = d[:, None] + lA
            bp.append(m.argmax(0)); d = m.max(0) + lB[:, x[t]]
        d = d + np.log(self.e + 1e-300)
        s = [int(d.argmax())]
        for b in reversed(bp):
            s.append(int(b[s[-1]]))
        return s[::-1]

    def n_params(self):
        return int(self.mask.sum() + self.K * 2 + self.K * (self.V - 1))


class KNBigram:
    def __init__(self, texts, V, d=0.75):
        self.V, self.d = V, d
        self.c = defaultdict(Counter)
        for t in texts:
            prev = "S"
            for s in list(t) + ["E"]:
                self.c[prev][s] += 1; prev = s
        cont = Counter()
        for a, cc in self.c.items():
            for b in cc:
                cont[b] += 1
        tot = sum(cont.values())
        self.pc = {b: n / tot for b, n in cont.items()}
        self.floor = 1.0 / (V + 1)

    def p(self, a, b):
        pc = 0.9 * self.pc.get(b, 0) + 0.1 * self.floor
        cc = self.c.get(a)
        if not cc:
            return pc
        n = sum(cc.values())
        return max(cc.get(b, 0) - self.d, 0) / n + self.d * len(cc) / n * pc

    def loglik(self, texts):
        tot = 0.0
        for t in texts:
            prev = "S"
            for s in list(t) + ["E"]:
                tot += np.log(self.p(prev, s)); prev = s
        return tot


def unigram_ll(train, test, V):
    c = Counter(s for t in train for s in list(t) + ["E"])
    n = sum(c.values())
    return sum(np.log((c.get(s, 0) + 0.5) / (n + 0.5 * (V + 1))) for t in test for s in list(t) + ["E"])
