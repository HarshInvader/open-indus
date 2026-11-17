"""Paired bootstrap CIs for language identification by word-level matching.

For a fixed corpus, each lexicon's best matching gives a per-word score vector (0 if unmatched).
Statistic: (sum of true-lexicon word scores - sum of a rival's) / tokens, resampling words (paired), 2000x.
Cases: Linear B words (919 with cognates) vs Homer-10k and wrong lexicons; planted Sanskrit / Tamil 10k tokens
vs K1 / K2 natural and wrong lexicons. Rivals are compared after subtracting each lexicon's score on a
sign-shuffled corpus (gain), the bootstrap on the real-corpus part only (shuffle score is a constant).
"""
import json, random, sys
import numpy as np
import common as C, data
import c2_planted as P
from c1_linearb import wrong_lex

OUT = C.HERE / "out"


def boot(a, b, ntok, B=2000, seed=0):
    rng = np.random.default_rng(seed)
    d = np.asarray(a) - np.asarray(b)
    n = len(d)
    bs = np.array([d[rng.integers(0, n, n)].sum() / ntok for _ in range(B)])
    return float(d.sum() / ntok), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def compare(name, W, wc, S, lexicons, ref, restarts, log, true=None):
    sc, gain = {}, {}
    ntok = float(sum(len(w) * c for w, c in zip(W, wc)))
    Wsh = C.shuffle_words(W, np.random.default_rng(9))
    for k, lx in lexicons.items():
        r = C.search(W, wc, lx, S, true=true, restarts=restarts, seed=1, oracle=False)
        rs = C.search(Wsh, wc, lx, S, restarts=max(restarts // 2, 4), seed=2, oracle=False)
        sc[k] = r["_word_scores"]; gain[k] = rs["score_tok"]
        log(f"[{name}] {k}: score/tok={r['score_tok']:.3f} shuf/tok={rs['score_tok']:.3f} acc={r.get('acc_tok')}")
    out = {}
    for k in lexicons:
        if k == ref: continue
        d, lo, hi = boot(sc[ref], sc[k], ntok)
        g = d - (gain[ref] - gain[k])
        out[k] = dict(diff_tok=d, ci=[lo, hi], gain_diff_tok=g, gain_ci=[lo - (gain[ref] - gain[k]), hi - (gain[ref] - gain[k])])
        log(f"   {ref} - {k}: raw {d:+.3f} [{lo:+.3f},{hi:+.3f}]  gain-adjusted {g:+.3f}")
    return dict(ntok=ntok, score_tok={k: float(np.sum(v) / ntok) for k, v in sc.items()},
                shuf_tok=gain, vs=out)


def main():
    restarts = int(sys.argv[1]) if len(sys.argv) > 1 else 16
    logf = open(OUT / "c4_bootstrap.log", "a")

    def log(s):
        print(s, flush=True); logf.write(s + "\n"); logf.flush()
    res = {}
    cg = data.lb_cognates()
    W, true, T = data.lb_problem([w for w, _ in cg])
    homer, _ = data.homer_types(10000)
    hom = data.lex_values(homer)
    rng = np.random.default_rng(0)
    lex = {"greek_homer": hom}
    for lg in ["lat", "san", "fin", "sux", "tam"]: lex[lg] = wrong_lex(lg, len(hom), rng)
    res["linb_L2"] = compare("LinB-L2", W, [1] * len(W), len(T.id), lex, "greek_homer", restarts, log, true)
    json.dump(res, open(OUT / "c4_bootstrap.json", "w"), indent=1, default=float)
    for lang in ("san", "tam"):
        texts, true, wforms, logos, share = P.plant(lang, 10000, 0.0, 0)
        W, wc = P.units(texts, "gold")
        forms = sorted(set(wforms.values()))
        other = "tam" if lang == "san" else "san"
        lex = {k: P.build_lex(k, lang, forms, random.Random(0)) for k in ["K2", "K1", "W:lat", "W:fin", "W:sux", f"R:{other}"]}
        res[f"{lang}_K2"] = compare(f"{lang}-10k", W, wc, len(true), lex, "K2", restarts, log, true)
        json.dump(res, open(OUT / "c4_bootstrap.json", "w"), indent=1, default=float)


if __name__ == "__main__":
    main()
