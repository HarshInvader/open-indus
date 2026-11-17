"""Bench Pierson's May 2026 key (K185) and the public v4 key (K161). Prereg: docs/prereg/bench_pierson.md.
Run: .venv/bin/python -I experiments/bench_pierson/run.py [--quick]"""
import csv
import json
import random
import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (KEYS, Bench, dev_heldout, distinct, fit_key, freq_bins, lexicon, lm_bigrams, load_k161,  # noqa
                    load_k185, markov_corpus, permute_key, runs, shuffle_corpus, tamil_lemmas)

QUICK = "--quick" in sys.argv
NPERM = 200 if QUICK else 1000
ITERS = 800 if QUICK else 3000
RESTARTS = 3
SCORES = ["S1", "S2", "S3"]
OUT = Path(__file__).resolve().parent / "out"
OUT.mkdir(exist_ok=True)

lex = lexicon()
bi_raw, logp, floor = lm_bigrams()
dev, ho = dev_heldout(version=2)
dev_runs = [r for t in dev for r in runs(t["seq"])]
ho_runs = [r for t in ho for r in runs(t["seq"])]
res = {"n_dev_texts": len(dev), "n_heldout_texts": len(ho), "lexicon_size": len(lex), "nperm": NPERM, "fit_iters": ITERS}


def perm_test(runs_, key, bins, rng, tag):
    b = Bench(runs_, lex, bi_raw, logp, floor)
    out = {}
    for w in SCORES:
        obs = b.score(key, w)
        null = np.array([b.score(permute_key(key, bins, rng), w) for _ in range(NPERM)])
        p = (1 + (null >= obs).sum()) / (NPERM + 1)
        out[w] = {"obs": obs, "null_mean": float(null.mean()), "null_sd": float(null.std()),
                  "z": float((obs - null.mean()) / (null.std() or 1)), "p": float(p)}
        print(tag, w, json.dumps(out[w]), flush=True)
    return out


def n2(runs_dev, runs_ho, key, rng, tag):
    corpora = {"dev_real": runs_dev, "dev_unigram": shuffle_corpus(runs_dev, rng), "dev_markov": markov_corpus(runs_dev, rng)}
    out = {}
    for w in SCORES:
        out[w] = {"key_on_dev": Bench(runs_dev, lex, bi_raw, logp, floor).score(key, w),
                  "key_on_heldout": Bench(runs_ho, lex, bi_raw, logp, floor).score(key, w)}
        for cname, cr in corpora.items():
            fits, ho_scores = [], []
            for _ in range(RESTARTS):
                b = Bench(cr, lex, bi_raw, logp, floor)
                start = permute_key(key, [list(key)], rng)
                fk, v = fit_key(b, start, w, rng, ITERS)
                fits.append(v)
                if cname == "dev_real":
                    ho_scores.append(Bench(runs_ho, lex, bi_raw, logp, floor).score(fk, w))
            out[w][cname] = {"fitted_scores": fits, "median": float(np.median(fits))}
            if ho_scores:
                out[w][cname]["fitted_on_dev_scored_on_heldout"] = ho_scores
        print(tag, w, json.dumps(out[w]), flush=True)
    return out


def coverage_check(key):
    allr = dev_runs + ho_runs
    toks = [s for r in allr for s in r]
    f = Counter(toks)
    cov = sum(f[s] for s in key) / len(toks)
    topk = sum(c for _, c in f.most_common(len(key))) / len(toks)
    rng = random.Random(1)
    sh = [s for r in shuffle_corpus(allr, rng) for s in r]
    covsh = sum(s in key for s in sh) / len(sh)
    return {"n_keyed_signs": len(key), "token_coverage_m77_distinct": cov, "coverage_top_same_number_of_signs": topk,
            "coverage_on_token_shuffled_corpus": covsh, "n_tokens": len(toks)}


def uniform_artefact(key):
    pins = {s: v[0][0] for s, v in key.items()}
    upper = {(chr(65 + i), chr(65 + j)) for i in range(26) for j in range(26)}
    lower = {(chr(97 + i), chr(97 + j)) for i in range(26) for j in range(26)}
    allr = dev_runs + ho_runs
    pairs = [(pins[a], pins[b]) for r in allr for a, b in zip(r, r[1:]) if a in pins and b in pins]
    return {"pairs": len(pairs), "uniform_uppercase_hit_rate": sum(p in upper for p in pairs) / len(pairs),
            "uniform_lowercase_hit_rate": sum(p in lower for p in pairs) / len(pairs),
            "share_pins_with_diacritic_or_nonascii": sum(not ('a' <= v <= 'z') for v in pins.values()) / len(pins),
            "lm_bigram_set_size_latin": len({p for p in bi_raw if p[0].isascii() and p[1].isascii()})}


def planted(rng):
    """Tamil Treebank lemma sequences, one sign per lemma type, cut to Indus run lengths."""
    lem = tamil_lemmas()
    seqs = []
    for r in csv.DictReader(open(KEYS / "kee2u_tamil_morpheme_seqs.csv")):
        s = [lem[int(x)] for x in r["morpheme_ids_ws_joined"].split() if int(x) in lem]
        if s:
            seqs.append(s)
    lens = [len(r) for r in dev_runs if len(r) >= 2]
    chunks = []
    for s in seqs:
        i = 0
        while i < len(s) - 1:
            L = rng.choice(lens); chunks.append(s[i:i + L]); i += L
    words = Counter(w for c in chunks for w in c)
    sign_of = {w: f"T{i}" for i, (w, _) in enumerate(words.most_common())}
    corpus = [[sign_of[w] for w in c] for c in chunks]
    nkey = 200
    key = {sign_of[w]: [w] for w, _ in words.most_common(nkey)}
    rng.shuffle(corpus)
    n_ho = len(ho)
    p_ho, p_dev = corpus[:n_ho], corpus[n_ho:]
    toks = [s for c in corpus for s in c]
    info = {"n_chunks": len(corpus), "n_types": len(words), "keyed": nkey,
            "coverage": sum(s in key for s in toks) / len(toks)}
    print("planted", info, flush=True)
    bins = freq_bins(p_dev, list(key))
    return info, perm_test(p_ho, key, bins, rng, "planted-heldout"), n2(p_dev, p_ho, key, rng, "planted-N2")


if __name__ == "__main__":
    rng = random.Random(20261117)
    res["planted"] = dict(zip(["info", "N1_heldout", "N2"], planted(rng)))
    for name, key in [("K185", load_k185()), ("K161", load_k161())]:
        r = {"coverage": coverage_check(key), "uniform_baseline": uniform_artefact(key)}
        print(name, r, flush=True)
        bins = freq_bins(dev_runs, list(key))
        r["N1_heldout"] = perm_test(ho_runs, key, bins, rng, name + "-heldout")
        r["N1_dev"] = perm_test(dev_runs, key, bins, rng, name + "-dev")
        if name == "K185" or not QUICK:
            r["N2"] = n2(dev_runs, ho_runs, key, rng, name + "-N2")
        res[name] = r
        json.dump(res, open(OUT / ("bench_quick.json" if QUICK else "bench.json"), "w"), indent=1, ensure_ascii=False)
    print("done")
