"""Simulated logo-syllabic script + count-based decipherment search.

Model (generative, as in Knight et al. 2006 / Ravi & Knight 2008/2011):
  value stream ~ syllable-bigram LM of the candidate language (with word boundaries and a LOGO token)
  each sign token is emitted by its value; the key k: sign -> value is deterministic and many-to-one
  log P(signs | k) = sum_{a,b} C[a,b] * logT[k(a), k(b)]  +  sum_s c_s log c_s - sum_v c_v log c_v
The second term is the maximum-likelihood channel P(sign | value); it penalises homophony.
Search: tempered Gibbs / simulated annealing over k with exact per-sign conditional scores
(all candidate values at once, O(V^2) per sign), several restarts, final greedy (ICM) polish.
"""
import numpy as np
from collections import Counter
from langdata import VALUES, VIDX, syllabify, CONS, VOWS

NV = len(VALUES)          # 101 syllable values
LOGO = NV                 # 101
BND = NV + 1              # 102 (BOS as row, EOS as column)
VT = NV + 2
NCAND = NV + 1            # a sign may take any syllable value or LOGO


# ---------------- language models ----------------
def _counts_from_texts(texts, weights=None):
    """texts: list of word lists (normalized words). Returns start, within, end, uni counts."""
    st = np.zeros(NV); wi = np.zeros((NV, NV)); en = np.zeros(NV); uni = np.zeros(NV)
    for ti, t in enumerate(texts):
        w8 = 1.0 if weights is None else weights[ti]
        for w in t:
            s = [VIDX[x] for x in syllabify(w)]
            if not s: continue
            st[s[0]] += w8; en[s[-1]] += w8
            for x in s: uni[x] += w8
            for a, b in zip(s, s[1:]): wi[a, b] += w8
    return st, wi, en, uni


class LM:
    """Syllable-bigram LM over written values, words concatenated without dividers.
    P(v'|v) = (1-e_v) Pin(v'|v) + e_v (1-q) Pstart(v');  P(LOGO|v) = e_v q;  after LOGO a new word starts.
    aligned=True: text boundaries are word boundaries (names). False: lines cut anywhere (prose)."""

    def __init__(self, texts, q=0.0, aligned=True, alpha=0.05, name=""):
        st, wi, en, uni = _counts_from_texts(texts)
        self.name = name; self.q = q; self.aligned = aligned
        self.from_counts(st, wi, en, uni, alpha)

    def from_counts(self, st, wi, en, uni, alpha):
        q = min(max(self.q, 1e-3), 0.95)
        pst = (st + alpha) / (st + alpha).sum()
        punis = (uni + alpha) / (uni + alpha).sum()
        e = (en + alpha) / (uni + 2 * alpha)                  # P(word ends after v)
        pin = (wi + alpha * punis[None, :] * 20) ; pin /= pin.sum(1, keepdims=True)
        T = np.zeros((VT, VT))
        T[:NV, :NV] = (1 - e)[:, None] * pin + (e * (1 - q))[:, None] * pst[None, :]
        T[:NV, LOGO] = e * q
        T[LOGO, :NV] = (1 - q) * pst; T[LOGO, LOGO] = q
        if self.aligned:
            T[BND, :NV] = (1 - q) * pst; T[BND, LOGO] = q
            eta = 0.4                                         # P(text ends | word ended); a constant guess
            T[:NV, :NV] = (1 - e)[:, None] * pin + (e * (1 - q) * (1 - eta))[:, None] * pst[None, :]
            T[:NV, LOGO] = e * q * (1 - eta); T[:NV, BND] = e * eta
            T[LOGO, :NV] *= (1 - eta); T[LOGO, LOGO] *= (1 - eta); T[LOGO, BND] = eta
        else:
            stat = (1 - q) * punis
            T[BND, :NV] = stat; T[BND, LOGO] = q
            T[:NV, BND] = 1.0; T[LOGO, BND] = 1.0             # EOS is a constant (lines cut anywhere)
        T[BND, BND] = 1e-12
        self.logT = np.log(np.maximum(T, 1e-12))
        self.uni = punis
        return self


def phonotactic_lm(texts, q, aligned, name="phonotactic"):
    """Knowledge = segment (phoneme) bigrams only, no lexicon. Syllable transition probabilities are
    products of segment-bigram probabilities, so no word or morpheme is known."""
    segs = CONS + VOWS + "#"
    si = {c: i for i, c in enumerate(segs)}
    B = np.ones((len(segs), len(segs))) * 0.1
    for t in texts:
        for w in t:
            s = "#" + w + "#"
            for a, b in zip(s, s[1:]): B[si[a], si[b]] += 1
    B /= B.sum(1, keepdims=True)
    def p_val(prev, v):           # P(segments of v | prev segment), then v must be followed appropriately
        p = 1.0; last = prev
        for ch in v:
            p *= B[si[last], si[ch]]; last = ch
        return p
    # synthesize start / within / end "counts" from segment model
    st = np.array([p_val("#", v) for v in VALUES])
    wi = np.array([[p_val(VALUES[a][-1], v) for v in VALUES] for a in range(NV)])
    en = np.array([B[si[v[-1]], si["#"]] for v in VALUES])
    # bare consonant values must be followed by a consonant or boundary: zero those that are followed by vowel
    for b, v in enumerate(VALUES):
        if len(v) == 1 and v in CONS:
            for c in range(NV):
                if VALUES[c][0] in VOWS: wi[b, c] *= 0.0
    lm = LM.__new__(LM); lm.name = name; lm.q = q; lm.aligned = aligned
    # convert to pseudo counts
    tot = wi.sum(1) + en
    wi = wi / tot[:, None] * 1000; en = en / tot * 1000
    uni = wi.sum(1) + en
    return lm.from_counts(st / st.sum() * 1000, wi, en, uni, 0.05)


# ---------------- script simulation ----------------
def make_script(texts, logo_share, rng, prose=False, line_len=(4, 12), max_logos=320):
    """texts: word lists. Most frequent word types become logograms until their token share >= logo_share.
    At most max_logos logogram types (keeps the inventory near Indus's ~420 signs), so the achieved
    share can fall below the target in genres with flat word frequencies.
    Returns sign sequences (list of int lists), true value per sign id, word-token logo share achieved."""
    wc = Counter(w for t in texts for w in t)
    tot = sum(wc.values()); logos, acc = set(), 0
    for w, c in wc.most_common():
        if acc >= logo_share * tot - 1e-9 or len(logos) >= max_logos: break
        logos.add(w); acc += c
    # sign ids: syllable values get shuffled ids; logograms get further ids
    vals = list(range(NV)); rng.shuffle(vals)
    syl_id = {v: i for i, v in enumerate(vals)}
    logo_id = {w: NV + i for i, w in enumerate(sorted(logos))}
    def enc(w):
        return [logo_id[w]] if w in logos else [syl_id[VIDX[x]] for x in syllabify(w)]
    if not prose:
        seqs = [[s for w in t for s in enc(w)] for t in texts]
    else:
        stream = [s for t in texts for w in t for s in enc(w)]
        seqs, i = [], 0
        while i < len(stream):
            k = rng.randint(*line_len); seqs.append(stream[i:i + k]); i += k
    true = np.full(NV + len(logos), -1)
    for v, i in syl_id.items(): true[i] = v
    for w, i in logo_id.items(): true[i] = LOGO
    return seqs, true, acc / max(tot, 1)


def compact(seqs, true=None):
    """relabel used signs 0..S-1"""
    used = sorted({s for q in seqs for s in q})
    m = {s: i for i, s in enumerate(used)}
    seqs2 = [[m[s] for s in q] for q in seqs]
    t2 = None if true is None else np.array([true[s] for s in used])
    return seqs2, t2


def shuffle_corpus(seqs, rng):
    toks = [s for q in seqs for s in q]
    perm = rng.permutation(len(toks))
    toks = [toks[i] for i in perm]
    out, i = [], 0
    for q in seqs:
        out.append(toks[i:i + len(q)]); i += len(q)
    return out


# ---------------- search ----------------
class Corpus:
    def __init__(self, seqs, S=None):
        S = S or (max(s for q in seqs for s in q) + 1)
        self.S = S; B = S
        C = Counter()
        for q in seqs:
            if not q: continue
            C[(B, q[0])] += 1; C[(q[-1], B)] += 1
            for a, b in zip(q, q[1:]): C[(a, b)] += 1
        self.C = C
        self.c = np.zeros(S)
        for q in seqs:
            for s in q: self.c[s] += 1
        outn = [[] for _ in range(S + 1)]; inn = [[] for _ in range(S + 1)]
        self.selfc = np.zeros(S)
        for (a, b), n in C.items():
            if a == b and a < S: self.selfc[a] = n; continue
            outn[a].append((b, n)); inn[b].append((a, n))
        self.out_i = [np.array([b for b, _ in l], dtype=int) for l in outn]
        self.out_n = [np.array([n for _, n in l], dtype=float) for l in outn]
        self.in_i = [np.array([b for b, _ in l], dtype=int) for l in inn]
        self.in_n = [np.array([n for _, n in l], dtype=float) for l in inn]
        self.ntok = int(self.c.sum())
        self.A = np.array([a for (a, b) in C]); self.Bi = np.array([b for (a, b) in C])
        self.N = np.array([n for n in C.values()], dtype=float)

    def score(self, key, lm):
        k = np.append(key, BND)
        lmsc = float((self.N * lm.logT[k[self.A], k[self.Bi]]).sum())
        cv = np.bincount(key, weights=self.c, minlength=NCAND)
        ch = float((self.c * np.log(np.maximum(self.c, 1e-300))).sum() - (cv[cv > 0] * np.log(cv[cv > 0])).sum())
        return lmsc + ch


def xlogx(x):
    return np.where(x > 0, x * np.log(np.maximum(x, 1e-300)), 0.0)


def anneal(corp, lm, rng, sweeps=150, restarts=4, T0=(3.0, 0.5), T1=0.01, fixed=None, init_key=None, per_token=True):
    """returns best key (np.array S) and its score"""
    S = corp.S; logT = lm.logT
    LT = logT[:NCAND, :]          # candidate x as prev: row
    LTc = logT[:, :NCAND]         # candidate x as next: col
    diagT = np.diag(logT)[:NCAND]
    fixed = fixed or {}
    best_key, best_sc = None, -np.inf
    order_base = np.arange(S)
    free = np.array([a for a in order_base if a not in fixed])
    for r in range(restarts):
        if init_key is not None and r == 0:
            key = np.array(init_key, dtype=int)
        elif r == 0:
            # frequency-rank init: signs by frequency -> values by LM unigram rank (LOGO for the tail)
            key = np.empty(S, dtype=int)
            rk = np.argsort(-corp.c); vr = np.argsort(-lm.uni)
            for j, a in enumerate(rk): key[a] = vr[j] if j < NV else LOGO
        else:
            key = rng.integers(0, NCAND, S)
        for a, v in fixed.items(): key[a] = v
        kb = np.append(key, BND)
        cv = np.bincount(key, weights=corp.c, minlength=NCAND).astype(float)
        nsw = sweeps
        t0r = T0 if np.isscalar(T0) else T0[r % len(T0)]
        for sw in range(nsw + 3):
            T = t0r * (T1 / t0r) ** (sw / max(nsw - 1, 1)) if sw < nsw else 0.0
            for a in rng.permutation(free):
                ca = corp.c[a]
                if ca == 0: continue
                cur = kb[a]
                ao = np.bincount(kb[corp.out_i[a]], weights=corp.out_n[a], minlength=VT)
                ai = np.bincount(kb[corp.in_i[a]], weights=corp.in_n[a], minlength=VT)
                sc = LT @ ao + ai @ LTc + corp.selfc[a] * diagT
                cv[cur] -= ca
                sc += xlogx(cv) - xlogx(cv + ca)
                if T > 0:
                    z = sc / (T * (ca if per_token else 1.0)); z -= z.max(); p = np.exp(z); p /= p.sum()
                    new = rng.choice(NCAND, p=p)
                else:
                    new = int(np.argmax(sc))
                cv[new] += ca; kb[a] = new
        key = kb[:S].copy()
        s = corp.score(key, lm)
        if s > best_sc: best_sc, best_key = s, key
    return best_key, best_sc


def accuracy(key, true, c, minc=1):
    syl = (true >= 0) & (true < NV) & (c >= minc)
    if syl.sum() == 0: return float("nan"), float("nan")
    tok = float((c[syl] * (key[syl] == true[syl])).sum() / c[syl].sum())
    typ = float((key[syl] == true[syl]).mean())
    return tok, typ
