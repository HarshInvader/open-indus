"""One experimental cell = one planted corpus (language, genre, token budget, logogram share, replicate),
deciphered under several language models, each on the real corpus and on frequency-matched shuffles."""
import numpy as np, random, time
from functools import lru_cache
import langdata as LD
from decipher import (LM, phonotactic_lm, make_script, compact, shuffle_corpus, Corpus, anneal,
                      accuracy, NV, LOGO)

LANGS = ["san", "tam", "sux", "lat", "fin"]
_L = None


def L():
    global _L
    if _L is None: _L = LD.load()
    return _L


def planted(lang, genre, ntok, logo, rep):
    """returns seqs (compact sign ids), true values, word texts used, oracle-genre texts, logo share"""
    rng = random.Random(1000 * rep + hash((lang, genre)) % 997)
    d = L()[lang]
    if genre == "names":
        pool = LD.name_texts(lang, L(), min(ntok // 2 + 3000, 120000), rng)
        rng.shuffle(pool)
        # oracle knowledge: disjoint same-genre texts (second half of pool, up to 6000)
        half = len(pool) // 2
        texts_all, oracle = pool[:max(half, len(pool) - 6000)], pool[max(half, len(pool) - 6000):]
    else:
        words = d["prose"]; n = len(words)
        cut = int(n * 0.75)
        oracle = LD._sentences_to_texts(words[cut:], rng)
        texts_all = LD._sentences_to_texts(words[:cut], rng)
        rng.shuffle(texts_all)
    srng = np.random.default_rng(rep * 7919 + 13)
    rr = random.Random(rep)
    # select texts until token budget: encode with logograms chosen on the candidate set
    seqs, true, share = make_script(texts_all, logo, rr, prose=(genre == "prose"))
    out, used, tok = [], [], 0
    for i, q in enumerate(seqs):
        if tok >= ntok: break
        out.append(q); tok += len(q)
        if genre == "names": used.append(texts_all[i])
    seqs, true = compact(out, true)
    return seqs, true, oracle, share


def build_lms(lang, genre, q, oracle, kinds):
    aligned = genre == "names"
    d = L()
    lms = {}
    for k in kinds:
        if k == "K0": lms[k] = LM(oracle, q, aligned, name=f"{lang}:oracle")
        elif k == "K1": lms[k] = LM(d[lang]["K1"], q, aligned, name=f"{lang}:K1")
        elif k == "K2":
            if d[lang]["K2"]: lms[k] = LM(d[lang]["K2"], q, aligned, name=f"{lang}:K2")
        elif k == "K3": lms[k] = phonotactic_lm(d[lang]["K1"], q, aligned)
        elif k.startswith("W:"):
            w = k[2:]; lms[k] = LM(d[w]["K1"], q, aligned, name=f"{w}:K1")
        elif k.startswith("R:"):
            w = k[2:]
            if d[w]["K2"]: lms[k] = LM(d[w]["K2"], q, aligned, name=f"{w}:K2")
    return lms


def run_cell(lang, genre, ntok, logo, rep, kinds=("K0", "K1", "K2", "K3", "WRONG"), nshuf=3,
             sweeps=150, restarts=4, anchors=(), anchor_mode="name"):
    t0 = time.time()
    seqs, true, oracle, share = planted(lang, genre, ntok, logo, rep)
    q = share
    kinds = list(kinds)
    if "WRONG" in kinds:
        kinds.remove("WRONG"); kinds += [f"W:{w}" for w in LANGS if w != lang] + [f"R:{w}" for w in LANGS if w != lang]
    lms = build_lms(lang, genre, q, oracle, kinds)
    corp = Corpus(seqs)
    rng = np.random.default_rng(rep * 31 + 5)
    shufs = [Corpus(shuffle_corpus(seqs, rng), S=corp.S) for _ in range(nshuf)]
    res = dict(lang=lang, genre=genre, ntok_target=ntok, ntok=corp.ntok, ntexts=len(seqs), logo=logo,
               logo_share=share, S=corp.S, n_syl_signs=int(((true >= 0) & (true < NV)).sum()),
               mean_len=corp.ntok / len(seqs), rep=rep, lms={})
    for k, lm in lms.items():
        key, sc = anneal(corp, lm, rng, sweeps=sweeps, restarts=restarts)
        tsc = corp.score(true, lm)
        acc_tok, acc_typ = accuracy(key, true, corp.c)
        acc5 = accuracy(key, true, corp.c, minc=5)[1]
        sh = [anneal(s, lm, rng, sweeps=100, restarts=2)[1] for s in shufs]
        r = dict(best=sc, true=tsc, acc_tok=acc_tok, acc_typ=acc_typ, acc_typ5=acc5, shuf=sh,
                 z=(sc - np.mean(sh)) / (np.std(sh, ddof=1) + 1e-9) if len(sh) > 1 else None,
                 gain=(sc - np.mean(sh)) / corp.ntok)
        if not k[:2] in ("W:", "R:"):
            # true-language LMs: is the true key (or its local optimum) the best key we can find?
            pkey, psc = anneal(corp, lm, rng, sweeps=0, restarts=1, init_key=true)
            r.update(true_polished=psc, acc_true_polished=accuracy(pkey, true, corp.c)[0],
                     search_gap=sc - psc,                          # <0: blind search missed a better key
                     acc_max=acc_tok if sc >= psc else accuracy(pkey, true, corp.c)[0],
                     wrong_beats_true=bool(sc > tsc + 1e-6 and acc_tok < 0.5),
                     spurious_beats_polished=bool(sc > psc + 1e-6 and acc_tok < 0.5))
        res["lms"][k] = r
    # anchors: clamp K true sign values, re-run under K1/K2/K3 (no shuffles needed)
    if anchors:
        res["anchors"] = {}
        syl = np.where((true >= 0) & (true < NV))[0]
        arng = np.random.default_rng(rep + 99)
        for K in anchors:
            if anchor_mode == "name":
                # signs drawn as they occur in running text (a bilingual name gives frequent-ish signs)
                p = corp.c[syl] / corp.c[syl].sum()
                pick = arng.choice(syl, size=min(K, len(syl)), replace=False, p=p)
            else:
                pick = syl[np.argsort(-corp.c[syl])][:K]
            fixed = {int(a): int(true[a]) for a in pick}
            res["anchors"][K] = {}
            for k in ("K1", "K2", "K3"):
                if k not in lms: continue
                key, sc = anneal(corp, lms[k], rng, sweeps=sweeps, restarts=restarts, fixed=fixed)
                free = np.ones(len(true), bool); free[list(fixed)] = False
                syl_free = free & (true >= 0) & (true < NV)
                accf = float((corp.c[syl_free] * (key[syl_free] == true[syl_free])).sum() / corp.c[syl_free].sum())
                res["anchors"][K][k] = dict(acc_tok=accuracy(key, true, corp.c)[0], acc_free_tok=accf)
    res["secs"] = time.time() - t0
    return res


if __name__ == "__main__":
    import json, sys
    r = run_cell("lat", "names", 10000, 0.0, 0, kinds=("K0", "K1", "K3", "W:san"), nshuf=2, sweeps=60, restarts=2)
    for k, v in r["lms"].items():
        print(k, {a: (round(b, 3) if isinstance(b, float) else b) for a, b in v.items() if a != "shuf"})
    print({k: v for k, v in r.items() if k != "lms"})
