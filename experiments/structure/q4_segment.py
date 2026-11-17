"""Q4. Unsupervised segmentation into recurring units.

Method A: Goldwater-style Dirichlet-process unigram word model, Gibbs sampling over boundaries with annealing.
Method B: PMI boundaries (boundary where PMI(left,right) < 0, counts from the training texts).
Method C: branching-entropy rise (Tanaka-Ishii): boundary after position i if H(next | s_{i-1..i}) > H(next | s_{i-1}).
Agreement: boundary F1 between methods vs a null that places the same number of boundaries at random in each run.
Held-out: bits/sign on held-out runs under the word model learned on dev (forward algorithm, marginal over
segmentations) vs sign-unigram, sign-bigram, and the same word model trained on within-run shuffled dev.
Site stability: top segments Mohenjo-daro vs Harappa against a site-label permutation null.
"""
import math
import random
import sys
from collections import Counter, defaultdict

import numpy as np

from common import Bigram, distinct, icit_texts, m77_split, m77_texts, runs, save_json, site_norm

LMAX = 6


class DPSeg:
    def __init__(self, rs, alpha=20.0, pstop=0.5, seed=0):
        self.rs = [r for r in rs if r]
        self.alpha = alpha; self.p = pstop
        self.rng = random.Random(seed)
        sc = Counter(s for r in self.rs for s in r)
        n = sum(sc.values())
        self.psign = {s: c / n for s, c in sc.items()}
        self.punk = 0.5 / n
        # init: random boundaries
        self.b = [[self.rng.random() < 0.5 for _ in range(len(r) - 1)] for r in self.rs]
        self.cnt = Counter(); self.N = 0
        for i in range(len(self.rs)):
            for w in self.words(i):
                self.cnt[w] += 1; self.N += 1

    def P0(self, w):
        pr = self.p * (1 - self.p) ** (len(w) - 1)
        for s in w:
            pr *= self.psign.get(s, self.punk)
        return pr

    def words(self, i):
        r = self.rs[i]; out = []; st = 0
        for j, bb in enumerate(self.b[i]):
            if bb:
                out.append(tuple(r[st:j + 1])); st = j + 1
        out.append(tuple(r[st:]))
        return out

    def pw(self, w, extra=0):
        return (self.cnt[w] + extra + self.alpha * self.P0(w)) / (self.N + self.alpha)

    def sweep(self, temp=1.0):
        for i in self.rng.sample(range(len(self.rs)), len(self.rs)):
            r = self.rs[i]
            for j in range(len(r) - 1):
                # find word span around boundary j (between r[j] and r[j+1])
                L = j
                while L > 0 and not self.b[i][L - 1]:
                    L -= 1
                R = j + 1
                while R < len(r) - 1 and not self.b[i][R]:
                    R += 1
                w1 = tuple(r[L:j + 1]); w2 = tuple(r[j + 1:R + 1]); w12 = tuple(r[L:R + 1])
                if self.b[i][j]:
                    self.cnt[w1] -= 1; self.cnt[w2] -= 1; self.N -= 2
                else:
                    self.cnt[w12] -= 1; self.N -= 1
                p_no = self.pw(w12)
                p_yes = self.pw(w1) * (self.cnt[w2] + (w1 == w2) + self.alpha * self.P0(w2)) / (self.N + 1 + self.alpha)
                if temp != 1.0:
                    p_no, p_yes = p_no ** (1 / temp), p_yes ** (1 / temp)
                yes = self.rng.random() < p_yes / (p_yes + p_no)
                self.b[i][j] = yes
                if yes:
                    self.cnt[w1] += 1; self.cnt[w2] += 1; self.N += 2
                else:
                    self.cnt[w12] += 1; self.N += 1

    def fit(self, iters=150):
        for it in range(iters):
            temp = max(1.0, 5.0 * (1 - it / (0.7 * iters)) + 1.0 * (it / (0.7 * iters))) if it < 0.7 * iters else 1.0
            self.sweep(temp)
        return self

    def lexicon(self):
        return Counter({w: c for w, c in self.cnt.items() if c > 0})

    def boundaries(self):
        return [b[:] for b in self.b]


def fwd_bits(r, lex, N, alpha, P0):
    """log2 P(run) under a unigram word model (marginalising segmentations)."""
    a = [0.0] + [-math.inf] * len(r)
    for i in range(1, len(r) + 1):
        terms = []
        for j in range(max(0, i - LMAX), i):
            w = tuple(r[j:i])
            p = (lex.get(w, 0) + alpha * P0(w)) / (N + alpha)
            terms.append(a[j] + math.log2(p))
        m = max(terms)
        a[i] = m + math.log2(sum(2 ** (t - m) for t in terms))
    return a[-1]


def word_model_bits(train_lex, psign_runs, test_runs, alpha=20.0, pstop=0.5):
    sc = Counter(s for r in psign_runs for s in r); n = sum(sc.values()); V = len(sc) + 1
    ps = {s: (c + 0.5) / (n + 0.5 * V) for s, c in sc.items()}; unk = 0.5 / (n + 0.5 * V)
    def P0(w):
        pr = pstop * (1 - pstop) ** (len(w) - 1)
        for s in w:
            pr *= ps.get(s, unk)
        return pr
    N = sum(train_lex.values())
    tot = sum(fwd_bits(r, train_lex, N, alpha, P0) for r in test_runs)
    return -tot / sum(map(len, test_runs))


def unigram_bits(train, test):
    sc = Counter(s for r in train for s in r); n = sum(sc.values()); V = len(sc) + 1
    return -sum(math.log2((sc.get(s, 0) + 0.5) / (n + 0.5 * V)) for r in test for s in r) / sum(map(len, test))


def bigram_bits(train, test):
    bg = Bigram(train)
    tot = 0
    for r in test:
        toks = ["<s>"] + r
        tot += sum(math.log2(bg.p(a, b)) for a, b in zip(toks, toks[1:]))
    return -tot / sum(map(len, test))


def pmi_boundaries(train, test):
    uni = Counter(s for r in train for s in r); big = Counter((a, b) for r in train for a, b in zip(r, r[1:]))
    n1 = sum(uni.values()); n2 = sum(big.values()) or 1
    out = []
    for r in test:
        bs = []
        for a, b in zip(r, r[1:]):
            pab = (big.get((a, b), 0) + 0.1) / (n2 + 0.1 * len(uni) ** 2)
            pmi = math.log2(pab / ((uni.get(a, 0) + 0.5) / n1 * (uni.get(b, 0) + 0.5) / n1))
            bs.append(pmi < 0)
        out.append(bs)
    return out


def be_boundaries(train, test):
    """Branching-entropy rise: boundary after i if H(next|s_{i-1},s_i) > H(next|s_i) (forward) - with min count 3."""
    f1 = defaultdict(Counter); f2 = defaultdict(Counter)
    for r in train:
        rr = r + ["</s>"]
        for i in range(len(r)):
            f1[rr[i]][rr[i + 1]] += 1
            if i > 0:
                f2[(rr[i - 1], rr[i])][rr[i + 1]] += 1
    def H(c):
        n = sum(c.values())
        return -sum(v / n * math.log2(v / n) for v in c.values()) if n else 0
    out = []
    for r in test:
        bs = []
        for i in range(len(r) - 1):
            if i > 0 and sum(f2[(r[i - 1], r[i])].values()) >= 3:
                bs.append(H(f2[(r[i - 1], r[i])]) > H(f1[r[i]]) - 1e-9)
            else:
                # first position: compare H(next|s_i) with the mean H(next|s) over signs
                bs.append(H(f1[r[i]]) > 3.0)
        out.append(bs)
    return out


def f1(b1, b2):
    tp = sum(x and y for a, b in zip(b1, b2) for x, y in zip(a, b))
    p1 = sum(map(sum, b1)); p2 = sum(map(sum, b2))
    return 2 * tp / (p1 + p2) if p1 + p2 else 0


def f1_null(b1, b2, reps=200, seed=0):
    rng = random.Random(seed); out = []
    for _ in range(reps):
        sh = []
        for a in b2:
            a = a[:]; rng.shuffle(a); sh.append(a)
        out.append(f1(b1, sh))
    return float(np.mean(out)), float(np.std(out))


def segs_from_bounds(rs, bs):
    out = Counter()
    for r, b in zip(rs, bs):
        st = 0
        for j, bb in enumerate(b):
            if bb:
                out[tuple(r[st:j + 1])] += 1; st = j + 1
        out[tuple(r[st:])] += 1
    return out


def shuffle_runs(rs, seed=0):
    rng = random.Random(seed); out = []
    for r in rs:
        r = r[:]; rng.shuffle(r); out.append(r)
    return out


def dp_ensemble(rs, n=3, iters=150):
    """Several chains; return the chain-0 model and a boundary-consensus (majority over chains)."""
    models = [DPSeg(rs, seed=s).fit(iters) for s in range(n)]
    cons = []
    for i in range(len(models[0].rs)):
        cons.append([sum(m.b[i][j] for m in models) * 2 > n for j in range(len(models[0].rs[i]) - 1)])
    agree = np.mean([f1(models[a].b, models[b].b) for a in range(n) for b in range(a + 1, n)])
    return models, cons, float(agree)


def multi(lex, k=50):
    return [w for w, c in lex.most_common() if len(w) >= 2][:k]


def analyse_corpus(train_runs, test_runs, label, iters=150):
    out = {"label": label, "train_runs": len(train_runs), "test_runs": len(test_runs)}
    models, cons, chain_agree = dp_ensemble(train_runs, 3, iters)
    m = models[0]
    out["dp_chain_boundary_F1"] = chain_agree
    lex = m.lexicon()
    rs = m.rs
    pmi_b = pmi_boundaries(train_runs, rs); be_b = be_boundaries(train_runs, rs)
    out["boundary_rate"] = {"DP": float(np.mean([x for b in cons for x in b])), "PMI": float(np.mean([x for b in pmi_b for x in b])),
                            "BE": float(np.mean([x for b in be_b for x in b]))}
    out["agreement_F1"] = {}
    for n1, b1 in (("DP", cons), ("PMI", pmi_b), ("BE", be_b)):
        for n2, b2 in (("DP", cons), ("PMI", pmi_b), ("BE", be_b)):
            if n1 < n2:
                o = f1(b1, b2); mu, sd = f1_null(b1, b2)
                out["agreement_F1"][f"{n1}-{n2}"] = {"F1": o, "null_mean": mu, "null_sd": sd, "z": (o - mu) / sd}
    out["mean_segment_len_DP"] = float(np.mean([len(w) for w, c in lex.items() for _ in range(c)]))
    out["top_multisign_segments_DP"] = [(" ".join(w), c) for w, c in lex.most_common() if len(w) >= 2][:40]
    pmi_lex = segs_from_bounds(rs, pmi_b)
    out["top_multisign_segments_PMI"] = [(" ".join(w), c) for w, c in pmi_lex.most_common() if len(w) >= 2][:40]
    top_dp = set(multi(lex, 50)); top_pmi = set(multi(pmi_lex, 50))
    out["top50_overlap_DP_PMI_jaccard"] = len(top_dp & top_pmi) / len(top_dp | top_pmi)
    # held-out likelihood
    if test_runs:
        b = {}
        b["sign_unigram"] = unigram_bits(train_runs, test_runs)
        b["sign_bigram_KN"] = bigram_bits(train_runs, test_runs)
        b["DP_word_unigram"] = word_model_bits(lex, train_runs, test_runs)
        b["PMI_word_unigram"] = word_model_bits(pmi_lex, train_runs, test_runs)
        # null 1: model trained on shuffled dev (order destroyed), tested on real held-out
        ms = DPSeg(shuffle_runs(train_runs, 1), seed=7).fit(iters)
        b["DP_trained_on_shuffled_dev"] = word_model_bits(ms.lexicon(), train_runs, test_runs)
        # null 2: real model tested on shuffled held-out
        sh = shuffle_runs(test_runs, 2)
        b["DP_real_on_shuffled_heldout"] = word_model_bits(lex, train_runs, sh)
        b["sign_bigram_on_shuffled_heldout"] = bigram_bits(train_runs, sh)
        b["sign_unigram_on_shuffled_heldout"] = unigram_bits(train_runs, sh)
        out["heldout_bits_per_sign"] = b
    out["_lex"] = lex
    out["_boundaries"] = (rs, cons)
    return out


def site_stability(texts_by_site, iters=120, reps=8, k=50):
    """Top-k multi-sign DP segments, MD vs Harappa, vs label-permutation null (pooled texts re-split, same sizes)."""
    md, ha = texts_by_site["Mohenjodaro"], texts_by_site["Harappa"]
    def top(rs, seed):
        return set(multi(DPSeg(rs, seed=seed).fit(iters).lexicon(), k))
    t_md, t_ha = top(md, 0), top(ha, 0)
    obs = len(t_md & t_ha) / len(t_md | t_ha)
    pool = md + ha; rng = random.Random(3); null = []
    for r in range(reps):
        rng.shuffle(pool)
        a, b = pool[:len(md)], pool[len(md):]
        ta, tb = top(a, r + 1), top(b, r + 1)
        null.append(len(ta & tb) / len(ta | tb))
    # also within-site chain variability: MD with two seeds
    t_md2 = top(md, 99)
    return {"jaccard_MD_vs_HA": obs, "null_mean": float(np.mean(null)), "null_sd": float(np.std(null)),
            "null_all": null, "z": (obs - np.mean(null)) / (np.std(null) + 1e-9),
            "seed_jaccard_MD": len(t_md & t_md2) / len(t_md | t_md2),
            "shared": sorted(" ".join(w) for w in t_md & t_ha)[:60],
            "MD_only": sorted(" ".join(w) for w in t_md - t_ha)[:30], "HA_only": sorted(" ".join(w) for w in t_ha - t_md)[:30]}


if __name__ == "__main__":
    dev, ho = m77_split()
    dr = [r for t in dev for r in runs(t["seq"])]
    hr = [r for t in ho for r in runs(t["seq"])]
    res = analyse_corpus(dr, hr, "M77 dev->heldout")
    lex = res.pop("_lex"); rs, cons = res.pop("_boundaries")
    # site stability on all distinct M77 texts
    T = distinct(m77_texts())
    bysite = defaultdict(list)
    for t in T:
        bysite[t["site"]] += runs(t["seq"])
    res["site_stability"] = site_stability(bysite)
    # full-corpus DP lexicon for the sign table (all distinct texts)
    allr = [r for t in T for r in runs(t["seq"])]
    full = DPSeg(allr, seed=0).fit(150)
    flex = full.lexicon()
    res["full_corpus_top_segments"] = [(" ".join(w), c) for w, c in flex.most_common() if len(w) >= 2][:80]
    import json, pickle
    from common import OUT
    pickle.dump({"full_lex": flex, "dev_lex": lex}, open(OUT / "segments.pkl", "wb"))
    save_json("q4_segment_M77", res)
    print(json.dumps({k: v for k, v in res.items() if k not in ("top_multisign_segments_PMI",)}, indent=1, default=str)[:6000])
