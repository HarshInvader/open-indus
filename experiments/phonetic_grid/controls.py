"""Planted-answer controls for the automated Kober/Ventris method.

Stage 1  parameter selection on CONTROL corpora only (never on Indus), then frozen.
Stage 2  main control table (5 seeds): recovery of consonant rows / vowel columns + method on a
         shuffled copy of each control (must collapse to ~0) + label-free structure statistics vs nulls.
Stage 3  power sweeps: corpus size x logogram share x name-repetition (Zipf exponent).

Run: .venv/bin/python experiments/phonetic_grid/controls.py
"""
import sys, json, random, itertools
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import corpora as C
import grid_lib as G

OUT = HERE / "out"; OUT.mkdir(exist_ok=True)


def nanmean(x):
    x = [v for v in x if v == v]
    return float(np.mean(x)) if x else float("nan")


def build(name, seed, N=2300, logo=0.0, zipf=1.0):
    if name == "lb_words":
        return C.linear_b_words(N, seed=seed, logo_share=logo)[:4]
    if name == "lb_lines":
        return C.linear_b_lines(None, seed=seed)[:4]
    if name == "synth":
        return C.synthetic(N, zipf=zipf, logo_share=logo, seed=seed)[:4]
    if name == "synth_prefix":
        return C.synthetic(N, zipf=zipf, logo_share=logo, seed=seed, prefixing=True)[:4]
    if name == "synth_nomorph":
        return C.synthetic(N, zipf=zipf, logo_share=logo, seed=seed, morph=False)[:4]
    if name == "dravidian":
        return C.dravidian(N, zipf=zipf, seed=seed)[:4]
    raise KeyError(name)


def stage1():
    grid = list(itertools.product([2, 3], [0, 1, 2], [1], ["count", "norm", "len", "lennorm"]))
    corpora = {n: build(n, 0) for n in ["lb_words", "lb_lines", "synth", "dravidian"]}
    rows = []
    for ms, mt, mw, wt in grid:
        G.set_params(min_stem=ms, max_tail=mt, weight=wt)
        r = {"min_stem": ms, "max_tail": mt, "min_w": mw, "weight": wt}
        for n, (t, tc, tv, info) in corpora.items():
            e = G.evaluate(t, tc, tv, min_w=mw)
            r[n] = round(e["ari_cons"], 3) if e["ari_cons"] == e["ari_cons"] else 0.0
            r[n + "_cov"] = round(e["coverage"], 2)
        # score = mean ARI x mean coverage, so a setting cannot win by keeping only 5 signs
        r["score"] = round(np.mean([r[n] * r[n + "_cov"] for n in corpora]), 3)
        rows.append(r)
        print(r, flush=True)
    best = max(rows, key=lambda r: r["score"])
    return rows, best


def stage2(best, seeds=range(5)):
    G.set_params(min_stem=best["min_stem"], max_tail=best["max_tail"], weight=best["weight"])
    mw = best["min_w"]
    table = {}
    for name in ["lb_words", "lb_lines", "synth", "dravidian", "synth_prefix", "synth_nomorph"]:
        res = []; resnull = []; st = []
        for sd in seeds:
            t, tc, tv, info = build(name, sd)
            direction = "start" if name == "synth_prefix" else "end"
            e = G.evaluate(t, tc, tv, min_w=mw, direction=direction)
            if name == "synth_prefix":  # prefix alternants share the stem-initial VOWEL: score rows vs vowels
                e2 = G.evaluate(t, tv, tc, min_w=mw, direction="start")
                e["rows_vs_vowel_ari"] = e2["ari_cons"]; e["rows_vs_vowel_prec"] = e2["edge_prec_cons"]; e["rows_vs_vowel_base"] = e2["edge_base_cons"]
            # same method on a shuffled copy (ending blocks permuted within length): must collapse
            rng = random.Random(100 + sd)
            tn = G.shuffle_end_block(t, rng) if direction == "end" else [tuple(reversed(x)) for x in G.shuffle_end_block([tuple(reversed(y)) for y in t], rng)]
            en = G.evaluate(list(dict.fromkeys(tn)), tc, tv, min_w=mw, direction=direction)
            res.append(e); resnull.append(en)
            if sd < 2:
                s_end = G.stats(t, "end"); s_start = G.stats(t, "start")
                n_end = G.null_stats(t, "block", n=30, seed=sd, direction="end")
                n_start = G.null_stats(t, "block", n=30, seed=sd, direction="start")
                st.append(dict(end=s_end, start=s_start, null_end=n_end, null_start=n_start))
        agg = {k: round(nanmean([r[k] for r in res]), 3) for k in res[0]}
        aggn = {k: round(nanmean([r[k] for r in resnull]), 3) for k in ["ari_cons", "ari_cons_louvain", "ari_vow", "edge_prec_cons", "edge_base_cons"]}
        table[name] = dict(info=info, method=agg, on_shuffled=aggn, structure=st,
                           ari_cons_sd=round(float(np.nanstd([r["ari_cons"] for r in res])), 3))
        print(name, info, agg, "SHUF", aggn, flush=True)
    return table


def stage3(best, seeds=range(3)):
    G.set_params(min_stem=best["min_stem"], max_tail=best["max_tail"], weight=best["weight"])
    mw = best["min_w"]
    out = []
    for name in ["synth", "lb_words"]:
        Ns = [300, 600, 1200, 2300, 4600] if name == "synth" else [500, 1000, 2300, 3676]
        logos = [0.0, 0.15, 0.3, 0.5]
        zipfs = [0.6, 1.0, 1.3] if name == "synth" else [None]
        for N, lg, z in itertools.product(Ns, logos, zipfs):
            rs = []
            for sd in seeds:
                t, tc, tv, info = build(name, sd, N=N, logo=lg, zipf=z or 1.0)
                e = G.evaluate(t, tc, tv, min_w=mw)
                e["logo_real"] = info.get("logo_share", lg)
                e["alt_per_text"] = e["alt_stems"] / len(t)
                rs.append(e)
            row = dict(corpus=name, N=N, logo=lg, zipf=z,
                       **{k: round(nanmean([r[k] for r in rs]), 3) for k in ["ari_cons", "ari_cons_louvain", "ari_vow", "coverage", "edge_prec_cons", "edge_base_cons", "logo_real", "alt_per_text"]})
            out.append(row); print(row, flush=True)
    return out


if __name__ == "__main__":
    s1, best = stage1()
    print("BEST", best)
    s2 = stage2(best)
    s3 = stage3(best)
    json.dump(dict(stage1=s1, best=best, stage2=s2, stage3=s3), open(OUT / "controls.json", "w"), indent=1, default=str)
