"""Word-level cognate decipherment (Snyder, Barzilay & Knight 2010; Luo, Cao & Barzilay 2019 style), CPU.

Objects
  words    distinct inscription words (tuples of sign ids 0..S-1), e.g. segments of texts
  lexicon  entries of a candidate language, each a sequence of value ids (0..NV-1, the shared
           101-value CV/C/V alphabet of experiments/decipherability/langdata.py)

Channel (generative direction lexicon word -> written word)
  each lexicon value b is either not written (prob Pdel[b]; final consonants, cluster members) or
  written by one sign s with prob P(s|b). Signs may also be inserted (logogram / determinative /
  complement noise) with prob eps_ins. Score of a pair = Viterbi log-likelihood ratio
      LLR(w, l) = max_align  sum log P(s|b) - log Pu(s)   [substitutions]
                           + sum log Pdel(b)               [unwritten lexicon values]
                           + sum log eps_ins               [inserted signs]
  > 0 means "l explains w better than the sign unigram null".
  A cognate (sound-change) kernel spreads alignment counts to phonetically close values
  (same consonant / same vowel and same place of articulation), so a sign aligned with 'ka'
  in matched pairs also gets some probability for 'ki', 'ga', ... (related-language tolerance).

Objective
  maximum-weight ONE-TO-ONE matching between words and lexicon entries (unmatched = 0),
  i.e. Snyder/Luo's bipartite matching constraint. Solved exactly on the top-k candidates per
  word with scipy's sparse min-weight full bipartite matching (one dummy column per word).

Learning: hard EM. (1) score all word x entry pairs (numba), (2) matching, (3) re-estimate
P(s|b), Pdel from Viterbi alignments of matched pairs, repeat. Random restarts; the restart with
the best final matching score is the 'blind' result. 'oracle' = same EM started from the true key.
"""
import numpy as np
from numba import njit, prange
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import min_weight_full_bipartite_matching
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments/decipherability"))
from langdata import VALUES, VIDX, CONS, VOWS, syllabify  # noqa: E402

NV = len(VALUES)
LOGO = NV
PLACE = {c: g for g, cs in {"lab": "pbmv", "den": "tdnslr", "pal": "cjy", "vel": "kgh"}.items() for c in cs}


def _cv(v):
    s = VALUES[v]
    if s in VOWS: return None, s
    if len(s) == 1: return s, None
    return s[0], s[1]


def similarity(sig_v=0.15, sig_c=0.15, sig_cv=0.0):
    """Cognate kernel over values: 1 on the diagonal, sig_v for same consonant/other vowel,
    sig_c for same vowel and same place of articulation, also bare C <-> CV with same C."""
    K = np.eye(NV)
    cv = [_cv(v) for v in range(NV)]
    for a in range(NV):
        ca, va = cv[a]
        for b in range(NV):
            if a == b: continue
            cb, vb = cv[b]
            if ca is not None and ca == cb:
                K[a, b] = sig_v                      # same consonant, different / no vowel
            elif va is not None and va == vb and ca is not None and cb is not None and PLACE[ca] == PLACE[cb]:
                K[a, b] = sig_c
            elif va is not None and va == vb and (ca is None or cb is None):
                K[a, b] = sig_cv                     # V <-> CV with same vowel
    return K


def pack(seqs):
    off = np.zeros(len(seqs) + 1, np.int64)
    off[1:] = np.cumsum([len(s) for s in seqs])
    flat = np.array([x for s in seqs for x in s], np.int64) if off[-1] else np.zeros(0, np.int64)
    return flat, off


@njit(cache=True)
def _llr(w, l, A, Dl, ins):
    n = len(w); m = len(l)
    D = np.empty((n + 1, m + 1))
    D[0, 0] = 0.0
    for j in range(1, m + 1): D[0, j] = D[0, j - 1] + Dl[l[j - 1]]
    for i in range(1, n + 1):
        D[i, 0] = D[i - 1, 0] + ins
        for j in range(1, m + 1):
            a = D[i - 1, j - 1] + A[w[i - 1], l[j - 1]]
            b = D[i, j - 1] + Dl[l[j - 1]]
            c = D[i - 1, j] + ins
            x = a if a > b else b
            D[i, j] = x if x > c else c
    return D[n, m]


@njit(parallel=True, cache=True)
def score_topk(wf, wo, lf, lo, A, Dl, ins, k, maxratio):
    Nw = len(wo) - 1; Nl = len(lo) - 1
    bi = np.full((Nw, k), -1, np.int64); bs = np.full((Nw, k), -1e9)
    for i in prange(Nw):
        w = wf[wo[i]:wo[i + 1]]; n = len(w)
        for j in range(Nl):
            l = lf[lo[j]:lo[j + 1]]; m = len(l)
            if m > maxratio * n + 2 or n > maxratio * m + 2: continue
            s = _llr(w, l, A, Dl, ins)
            if s > bs[i, k - 1]:
                p = k - 1
                while p > 0 and bs[i, p - 1] < s:
                    bs[i, p] = bs[i, p - 1]; bi[i, p] = bi[i, p - 1]; p -= 1
                bs[i, p] = s; bi[i, p] = j
    return bi, bs


@njit(cache=True)
def _align_counts(w, l, A, Dl, ins, sub, dele):
    """Viterbi backtrace; add substitution counts sub[s,b] and deletion counts dele[b] (dele[NV+b] = kept)."""
    n = len(w); m = len(l)
    D = np.empty((n + 1, m + 1)); B = np.zeros((n + 1, m + 1), np.int64)
    D[0, 0] = 0.0
    for j in range(1, m + 1): D[0, j] = D[0, j - 1] + Dl[l[j - 1]]; B[0, j] = 1
    for i in range(1, n + 1):
        D[i, 0] = D[i - 1, 0] + ins; B[i, 0] = 2
        for j in range(1, m + 1):
            a = D[i - 1, j - 1] + A[w[i - 1], l[j - 1]]
            b = D[i, j - 1] + Dl[l[j - 1]]
            c = D[i - 1, j] + ins
            if a >= b and a >= c: D[i, j] = a; B[i, j] = 0
            elif b >= c: D[i, j] = b; B[i, j] = 1
            else: D[i, j] = c; B[i, j] = 2
    i, j = n, m
    nins = 0
    while i > 0 or j > 0:
        op = B[i, j]
        if op == 0:
            sub[w[i - 1], l[j - 1]] += 1.0; i -= 1; j -= 1
        elif op == 1:
            dele[l[j - 1]] += 1.0; j -= 1
        else:
            nins += 1; i -= 1
    return nins


def match(bi, bs, Nl):
    """Exact max-weight one-to-one matching on candidate edges with positive score."""
    Nw, k = bi.shape
    ok = (bi >= 0) & (bs > 0)
    C = (bs[ok].max() if ok.any() else 0.0) + 1.0
    rows, cols, vals = [], [], []
    r_idx = np.repeat(np.arange(Nw), k).reshape(Nw, k)
    rows.append(r_idx[ok]); cols.append(bi[ok]); vals.append(C - bs[ok])
    rows.append(np.arange(Nw)); cols.append(Nl + np.arange(Nw)); vals.append(np.full(Nw, C))
    rows = np.concatenate(rows); cols = np.concatenate(cols); vals = np.concatenate(vals)
    M = csr_matrix((vals, (rows, cols)), shape=(Nw, Nl + Nw))
    r, c = min_weight_full_bipartite_matching(M)
    out = np.full(Nw, -1, np.int64)
    sc = np.zeros(Nw)
    for ri, ci in zip(r, c):
        if ci < Nl:
            out[ri] = ci
            sc[ri] = C - M[ri, ci]
    return out, sc


def greedy_match(bi, bs):
    """many-to-one: each word takes its best entry (no matching constraint)"""
    out = np.where(bs[:, 0] > 0, bi[:, 0], -1)
    return out, np.maximum(bs[:, 0], 0)


class Model:
    def __init__(self, words, wcount, lexicon, S, kernel=None, alpha=0.5, beta=2.0, eps_ins=0.01,
                 topk=8, maxratio=2.0, one_to_one=True):
        self.words = [np.array(w, np.int64) for w in words]
        self.wf, self.wo = pack(self.words)
        self.lex = [np.array(l, np.int64) for l in lexicon]
        self.lf, self.lo = pack(self.lex)
        self.S = S; self.Nl = len(self.lex)
        c = np.zeros(S)
        for w, n in zip(words, wcount):
            for s in w: c[s] += n
        self.cnt = c
        tc = np.zeros(S)                           # type-level sign counts (words are types)
        for w in words:
            for s in w: tc[s] += 1
        self.pu = (tc + 0.5) / (tc + 0.5).sum()
        self.K = similarity() if kernel is None else kernel
        self.alpha, self.beta, self.lins = alpha, beta, np.log(eps_ins)
        self.topk, self.maxratio, self.one_to_one = topk, maxratio, one_to_one
        bf = np.zeros(NV)
        for l in self.lex:
            for b in l: bf[b] += 1
        self.bfreq = bf / bf.sum()
        self.del_prior = np.array([0.35 if (len(VALUES[v]) == 1 and VALUES[v] in CONS) else
                                   (0.10 if VALUES[v] in VOWS else 0.03) for v in range(NV)])

    # ---- parameters from counts
    def params(self, sub, dele, keep):
        """sub[S,NV] counts; dele[NV], keep[NV] counts. Returns A (log-ratio), Dl."""
        sm = sub @ self.K                           # cognate smoothing: spread counts to close values
        P = (sm + self.alpha * self.pu[:, None]) / (sm.sum(0, keepdims=True) + self.alpha)   # P(s|b)
        A = np.log(P) - np.log(self.pu)[:, None]
        pd = (dele + self.beta * self.del_prior) / (dele + keep + self.beta)
        A = A + np.log1p(-pd)[None, :]              # written with prob 1-pd
        return A, np.log(pd)

    def key_counts(self, key, w8=None):
        """hard key (sign -> value or -1/LOGO) -> pseudo counts"""
        sub = np.zeros((self.S, NV))
        for s, v in enumerate(key):
            if 0 <= v < NV: sub[s, v] = 3.0 * (1.0 if w8 is None else w8[s])
        return sub, np.zeros(NV), np.full(NV, 1.0)

    def step(self, A, Dl):
        bi, bs = score_topk(self.wf, self.wo, self.lf, self.lo, A, Dl, self.lins, self.topk, self.maxratio)
        if self.one_to_one:
            m, sc = match(bi, bs, self.Nl)
        else:
            m, sc = greedy_match(bi, bs)
        return m, sc

    def mstep(self, m, A, Dl):
        sub = np.zeros((self.S, NV)); dele = np.zeros(NV); kept = np.zeros(NV)
        for i, j in enumerate(m):
            if j < 0: continue
            _align_counts(self.words[i], self.lex[j], A, Dl, self.lins, sub, dele)
        kept = sub.sum(0)
        return sub, dele, kept

    def soft_mstep(self, A, Dl, T, rng=None, noise=0.0):
        """soft E-step over top-k candidates (no matching constraint): weights softmax(score/T), null = 0"""
        bi, bs = score_topk(self.wf, self.wo, self.lf, self.lo, A, Dl, self.lins, self.topk, self.maxratio)
        sub = np.zeros((self.S, NV)); dele = np.zeros(NV)
        z = np.concatenate([bs, np.zeros((len(bs), 1))], 1) / T
        if noise > 0 and rng is not None: z = z + rng.gumbel(size=z.shape) * noise
        z -= z.max(1, keepdims=True); p = np.exp(z); p /= p.sum(1, keepdims=True)
        for i in range(len(bi)):
            for c in range(bi.shape[1]):
                if bi[i, c] < 0 or p[i, c] < 0.02: continue
                s1 = np.zeros((self.S, NV)); d1 = np.zeros(NV)
                _align_counts(self.words[i], self.lex[bi[i, c]], A, Dl, self.lins, s1, d1)
                sub += p[i, c] * s1; dele += p[i, c] * d1
        return sub, dele, sub.sum(0)

    def run_soft(self, init_counts, Ts=(8, 6, 4, 3, 2, 1.5, 1.0), rng=None, noise=0.0, iters=10, verbose=False):
        """deterministic annealing warm-up (soft EM), then hard one-to-one EM"""
        sub, dele, keep = init_counts
        for T in Ts:
            A, Dl = self.params(sub, dele, keep)
            sub, dele, keep = self.soft_mstep(A, Dl, T, rng, noise)
        return self.run((sub, dele, keep), iters=iters, verbose=verbose)

    def run(self, init_counts, iters=12, tol=1e-4, verbose=False):
        sub, dele, keep = init_counts
        A, Dl = self.params(sub, dele, keep)
        best = (-1e18, None)
        hist = []
        for it in range(iters):
            m, sc = self.step(A, Dl)
            tot = float(sc.sum())
            hist.append(tot)
            if verbose: print(f"   it{it} score={tot:.1f} matched={int((m >= 0).sum())}", flush=True)
            if tot > best[0]: best = (tot, (m.copy(), sc.copy(), sub.copy(), A.copy(), Dl.copy()))
            sub, dele, keep = self.mstep(m, A, Dl)
            A, Dl = self.params(sub, dele, keep)
            if len(hist) > 2 and abs(hist[-1] - hist[-2]) < tol * max(1, abs(hist[-1])): break
        tot, (m, sc, sub, A, Dl) = best
        return dict(score=tot, match=m, msc=sc, sub=sub, A=A, Dl=Dl, hist=hist)

    def decode(self, sub, A=None):
        """value per sign: argmax of aligned counts (raw); -1 if never aligned"""
        key = np.full(self.S, -1)
        has = sub.sum(1) > 0
        key[has] = sub[has].argmax(1)
        return key

    def random_init(self, rng, mode="freq"):
        """random hard key. mode 'freq': frequency-rank matched with noise (Knight-style init)."""
        if mode == "freq":
            so = np.argsort(-self.cnt + rng.normal(0, 1e-9, self.S))
            vo = np.argsort(-self.bfreq * np.exp(rng.normal(0, 1.0, NV)))
            key = np.empty(self.S, np.int64)
            for r, s in enumerate(so): key[s] = vo[r % NV]
        else:
            key = rng.integers(0, NV, self.S)
        return self.key_counts(key)


def accuracy(key, true, cnt, lenient=None):
    """token-weighted share of syllabic signs whose decoded value equals the true value.
    lenient: function(v_hat, v_true)->bool for partial credit variants."""
    syl = (true >= 0) & (true < NV)
    if lenient is None:
        ok = key == true
    else:
        ok = np.array([lenient(a, b) if (a >= 0 and b >= 0 and b < NV) else False for a, b in zip(key, true)])
    tok = float((cnt[syl] * ok[syl]).sum() / max(cnt[syl].sum(), 1e-9))
    typ = float(ok[syl].mean()) if syl.any() else 0.0
    return tok, typ


def cons_ok(a, b):
    ca, _ = _cv(a); cb, _ = _cv(b)
    return ca == cb


def decipher(words, wcount, lexicon, S, true=None, restarts=6, iters=12, seed=0, oracle=True,
             verbose=False, **kw):
    """Blind EM restarts (+ oracle start from the true key). Returns summary dict."""
    M = Model(words, wcount, lexicon, S, **kw)
    rng = np.random.default_rng(seed)
    runs = []
    for r in range(restarts):
        init = M.random_init(rng, "freq" if r % 2 == 0 else "uniform")
        runs.append(M.run(init, iters=iters, verbose=verbose))
    best = max(runs, key=lambda x: x["score"])
    out = dict(score=best["score"], n_matched=int((best["match"] >= 0).sum()),
               restart_scores=[r["score"] for r in runs], ntok=float(M.cnt.sum()), nwords=len(words),
               nlex=len(lexicon), _best=best, _model=M)
    if true is not None:
        key = M.decode(best["sub"])
        out["acc_tok"], out["acc_typ"] = accuracy(key, true, M.cnt)
        out["acc_cons_tok"] = accuracy(key, true, M.cnt, cons_ok)[0]
        out["restart_acc"] = [accuracy(M.decode(r["sub"]), true, M.cnt)[0] for r in runs]
        if oracle:
            orc = M.run(M.key_counts(np.where(true < NV, true, -1)), iters=iters)
            ok_ = M.decode(orc["sub"])
            out["oracle_score"] = orc["score"]
            out["oracle_acc_tok"] = accuracy(ok_, true, M.cnt)[0]
            out["oracle_n_matched"] = int((orc["match"] >= 0).sum())
            # true key held fixed (no re-estimation): score of the planted answer itself
            A, Dl = M.params(*M.key_counts(np.where(true < NV, true, -1)))
            m0, sc0 = M.step(A, Dl)
            out["truekey_score"] = float(sc0.sum())
            out["wrong_beats_oracle"] = bool(out["score"] > out["oracle_score"] + 1e-6 and out["acc_tok"] < 0.5)
            out["_oracle"] = orc
    return out
