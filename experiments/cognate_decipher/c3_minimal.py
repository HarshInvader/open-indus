"""Minimal conditions: what kind of lexicon lets word-level matching work at Indus size?

Planted Sanskrit and Tamil names, 10k tokens, gold word segments, no logograms (best case).
Lexicon = 5000 entries; a fraction p of the corpus's word types is present in the lexicon, transformed by
  regular  : a systematic value map applied to a fraction of the 101 values (sound change, consistent)
  irregular: independent random edits per value (substitute / delete / insert) at rate e
             (stands in for morphology, conditional change, lexical drift)
The rest of the lexicon is filled with other true-language types. Also: the same lexicons against a
sign-shuffled corpus, and the K2 natural lexicon for reference (from c2).
Linear B real-data analogue: Homer-10k lexicon with a fraction p of the true Greek cognate forms injected.
"""
import json, sys, time, random
import numpy as np
import common as C, wm, data
import c2_planted as P

OUT = C.HERE / "out"


def mutate(v, e, rng, regmap):
    out = []
    for x in v:
        x = regmap.get(x, x)
        r = rng.random()
        if r < e / 3:
            continue                                   # deletion
        elif r < 2 * e / 3:
            x = rng.randrange(wm.NV)                   # substitution
        out.append(x)
        if rng.random() < e / 3: out.append(rng.randrange(wm.NV))   # insertion
    return out or v


def make_regmap(frac, rng):
    """systematic sound change on a fraction of values: same-consonant vowel shift or same-place consonant shift"""
    K = wm.similarity(1, 1, 0)
    vals = list(range(wm.NV)); rng.shuffle(vals)
    m = {}
    for v in vals[:int(frac * wm.NV)]:
        nb = [b for b in range(wm.NV) if b != v and K[v, b] > 0]
        if nb: m[v] = rng.choice(nb)
    return m


def lexicon(lang, forms, p, e, regfrac, seed):
    rng = random.Random(seed)
    regmap = make_regmap(regfrac, rng)
    ct = list(forms); rng.shuffle(ct)
    inj = [mutate(v, e, rng, regmap) for v in C.wm_lex(ct[:int(round(p * len(ct)))])]
    freq, hw = P.k1_types(lang)
    fill = C.wm_lex([w for w in freq + hw if w not in set(forms)][:4 * P.NLEX])
    r = np.random.default_rng(seed)
    idx = r.choice(len(fill), max(P.NLEX - len(inj), 0), replace=False)
    return inj + [fill[i] for i in idx], regmap


def main():
    restarts = int(sys.argv[1]) if len(sys.argv) > 1 else 16
    logf = open(OUT / "c3_minimal.log", "a")

    def log(s):
        print(s, flush=True); logf.write(s + "\n"); logf.flush()
    res = []
    for lang in ("san", "tam"):
        texts, true, wforms, logos, share = P.plant(lang, 10000, 0.0, 0)
        W, wc = P.units(texts, "gold"); S = len(true)
        forms = sorted(set(wforms.values()))
        for p, e, reg in [(1.0, 0.0, 0.3), (1.0, 0.1, 0.0), (1.0, 0.2, 0.0), (1.0, 0.3, 0.0), (1.0, 0.2, 0.3),
                          (0.5, 0.1, 0.3), (0.5, 0.2, 0.0), (0.3, 0.0, 0.0), (0.3, 0.1, 0.0)]:
            lex, regmap = lexicon(lang, forms, p, e, reg, 7)
            # truth under the regular change: a sign's 'readable' value is the shifted one
            true_reg = np.array([regmap.get(t, t) if 0 <= t < wm.NV else t for t in true])
            t0 = time.time()
            r = C.search(W, wc, lex, S, true=true_reg, restarts=restarts, seed=1, oracle=True)
            Wsh = C.shuffle_words(W, np.random.default_rng(3))
            rs = C.search(Wsh, wc, lex, S, restarts=max(restarts // 2, 4), seed=3, oracle=False)
            row = dict(lang=lang, p=p, e=e, regfrac=reg, nunits=len(W), **{k: v for k, v in C.strip(r).items()
                       if k not in ("restart_scores",)}, shuf_score_tok=rs["score_tok"])
            row["gain_tok"] = row["score_tok"] - rs["score_tok"]
            res.append(row)
            log(f"[{lang} p={p} e={e} reg={reg}] acc={r['acc_tok']:.3f} cons={r['acc_cons_tok']:.3f} "
                f"score/tok={r['score_tok']:.3f} shuf={rs['score_tok']:.3f} oracle_acc={r['oracle_acc_tok']:.3f} "
                f"oracle/tok={r['oracle_score'] / r['ntok']:.3f} wrong>or={r['wrong_beats_oracle']} t={time.time() - t0:.0f}s")
            json.dump(res, open(OUT / "c3_minimal.json", "w"), indent=1, default=float)
    # Linear B real-data coverage curve
    cg = data.lb_cognates()
    homer, _ = data.homer_types(10000)
    hom = data.lex_values(homer)
    hset = {tuple(v) for v in hom}
    W, true, T = data.lb_problem([w for w, _ in cg])
    rng = random.Random(5)
    for p in (0.25, 0.5, 0.75):
        inj = []
        for w, G in cg:
            if rng.random() < p:
                vs = data.lex_values(sorted(G))
                if vs and tuple(vs[0]) not in hset: inj.append(vs[0])
        lex = inj + hom[:max(10000 - len(inj), 0)]
        cov = np.mean([any(tuple(v) in {tuple(x) for x in lex[:len(inj)]} | hset for v in data.lex_values(sorted(G)))
                       for w, G in cg]) if False else None
        r = C.search(W, [1] * len(W), lex, len(T.id), true=true, restarts=restarts, seed=2, oracle=True)
        row = dict(lang="linb", p=p, n_injected=len(inj), **{k: v for k, v in C.strip(r).items() if k != "restart_scores"})
        res.append(row)
        log(f"[LinB Homer10k + {len(inj)} cognates (p={p})] acc={r['acc_tok']:.3f} cons={r['acc_cons_tok']:.3f} "
            f"oracle_acc={r['oracle_acc_tok']:.3f} wrong>or={r['wrong_beats_oracle']}")
        json.dump(res, open(OUT / "c3_minimal.json", "w"), indent=1, default=float)


if __name__ == "__main__":
    main()
