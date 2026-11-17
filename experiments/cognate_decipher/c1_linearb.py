"""Control (a): real Linear B vs Greek. Does word-level matching recover known sign values, and does Greek
beat wrong-language lexicons, a shuffled lexicon and a shuffled corpus?

L1 (Luo et al. 2019 setting): the 919 Linear B words that have a Greek cognate; lexicon = their Greek forms.
L2: same words; lexicon = 10k most frequent Homeric word types (cognates NOT injected).
L3: all distinct complete DAMOS words (most have no cognate in the lexicon); lexicon = Homer 10k.
Wrong lexicons are random type samples of equal size from Latin (Caesar), Sanskrit (MW + sa.wiki),
Finnish (fi.wiki), Sumerian (lexicon), Tamil (ta.wiki).
"""
import json, sys, time, random
import numpy as np
import data, common as C

OUT = C.HERE / "out"; OUT.mkdir(exist_ok=True)
WRONG = ["lat", "san", "fin", "sux", "tam"]


def wrong_lex(lang, n, rng):
    return C.sample_lex(C.types_of(C.L()[lang]["K1"]), n, rng, maxsyl=10)


def run(cond, words_sy, gr_lex, gold_fn, restarts, seed, log):
    W, true, T = data.lb_problem(words_sy)
    S = len(T.id); wc = [1] * len(W)
    rng = np.random.default_rng(seed)
    res = {}
    gold = gold_fn(W, gr_lex) if gold_fn else None
    t = time.time()
    r = C.search(W, wc, gr_lex, S, true=true, restarts=restarts, seed=seed, gold=gold)
    res["greek"] = C.strip(r)
    log(f"[{cond} n={len(W)}] greek score/tok={r['score_tok']:.3f} acc={r['acc_tok']:.3f} cons={r['acc_cons_tok']:.3f} "
        f"oracle/tok={r['oracle_score'] / r['ntok']:.3f} oracle_acc={r['oracle_acc_tok']:.3f} "
        f"cog={r.get('cognate_acc')} ({time.time() - t:.0f}s)")
    for lang in WRONG:
        lx = wrong_lex(lang, len(gr_lex), rng)
        r = C.search(W, wc, lx, S, true=true, restarts=restarts, seed=seed + 1, oracle=False)
        res[lang] = C.strip(r)
        log(f"   {lang}: score/tok={r['score_tok']:.3f} acc={r['acc_tok']:.3f}")
    lx = C.shuffle_lex(gr_lex, rng)
    r = C.search(W, wc, lx, S, true=true, restarts=restarts, seed=seed + 2, oracle=False)
    res["greek_lexshuf"] = C.strip(r); log(f"   greek_lexshuf: score/tok={r['score_tok']:.3f} acc={r['acc_tok']:.3f}")
    Wsh = C.shuffle_words(W, rng)
    r = C.search(Wsh, wc, gr_lex, S, restarts=restarts, seed=seed + 3, oracle=False)
    res["corpus_shuf"] = C.strip(r); log(f"   corpus_shuf: score/tok={r['score_tok']:.3f}")
    return res


def main():
    restarts = int(sys.argv[1]) if len(sys.argv) > 1 else 24
    logf = open(OUT / "c1_linearb.log", "a")

    def log(s):
        print(s, flush=True); logf.write(s + "\n"); logf.flush()
    cg = data.lb_cognates()
    gr_forms = sorted(set(g for _, G in cg for g in G))
    gr_lex = data.lex_values(gr_forms)
    gl_index = {tuple(v): i for i, v in enumerate(gr_lex)}
    homer, _ = data.homer_types(10000)
    hom_lex = data.lex_values(homer)
    hl_index = {tuple(v): i for i, v in enumerate(hom_lex)}
    cog_of = {w: G for w, G in cg}

    def gold_factory(index, words_sy):
        def g(W, lex):
            out = []
            for w in words_sy:
                G = cog_of.get(w, set())
                out.append({index[tuple(v)] for v in data.lex_values(sorted(G)) if tuple(v) in index})
            return out
        return g
    results = {}
    rng = random.Random(0)
    allcog = [w for w, _ in cg]
    cover = np.mean([any(tuple(v) in hl_index for v in data.lex_values(sorted(G))) for _, G in cg])
    log(f"Homer-10k lexicon contains a cognate form for {cover:.3f} of the 919 LB words")
    results["homer_cognate_coverage"] = float(cover)
    for n in (230, 460, 919):
        ws = allcog if n == 919 else rng.sample(allcog, n)
        results[f"L1_n{n}"] = run("L1", ws, gr_lex, gold_factory(gl_index, ws), restarts, n, log)
    for n in (460, 919):
        ws = allcog if n == 919 else rng.sample(allcog, n)
        results[f"L2_n{n}"] = run("L2", ws, hom_lex, gold_factory(hl_index, ws), restarts, n + 7, log)
    dw = sorted(data.damos_words())
    for n in (1780, len(dw)):
        ws = dw if n == len(dw) else rng.sample(dw, n)
        results[f"L3_n{n}"] = run("L3", ws, hom_lex, gold_factory(hl_index, ws), restarts, n + 11, log)
        json.dump(results, open(OUT / "c1_linearb.json", "w"), indent=1, default=float)
    json.dump(results, open(OUT / "c1_linearb.json", "w"), indent=1, default=float)


if __name__ == "__main__":
    main()
