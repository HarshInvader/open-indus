"""DEV ONLY exploration + controls (no held-out data touched).
usage: .venv/bin/python experiments/slot_novelty/dev_explore.py [t2|t3|all]
"""
import sys
import numpy as np
from collections import Counter
from sn_lib import (indus_seals, ur3_legends, strata, common_set, t2_stratum, shuffle_within,
                    swap_null, bigram_null, plant_template, BigramChain, oc_mi, SLOTS, dump, HERE)

rng = np.random.default_rng(1)
what = sys.argv[1] if len(sys.argv) > 1 else "all"
out = {}


def show_t2(name, texts, common):
    print(f"\n== T2 {name}  (n={len(texts)})")
    res = {}
    for k, T in strata(texts).items():
        if len(T) < 20:
            continue
        r = t2_stratum(T, common, rng)
        res[k] = r
        print(f" L={k:3s} N={r['N']:4d} " + "  ".join(
            f"{s[:3]} P={r[s]['P']:.2f} sh={r[s]['share']:.2f} rare={r[s]['frac_novel_from_rare']:.2f} cont={r[s]['content_novel_rate']:.2f}"
            for s in SLOTS) + f"  top={r['top']} t/2={r['ratio_top_second']:.2f} max/min={r['ratio_max_min']:.2f}")
    return res


if what in ("t2", "all"):
    dev = indus_seals("dev", min_len=3)
    com = common_set(indus_seals("dev"))
    out["t2_dev_all"] = show_t2("Indus dev all sites", dev, com)
    out["t2_dev_md"] = show_t2("Indus dev MD", indus_seals("dev", "Mohenjodaro", 3), com)
    out["t2_dev_hp"] = show_t2("Indus dev Harappa", indus_seals("dev", "Harappa", 3), com)
    out["t2_dev_shuffled"] = show_t2("NEG control: dev, signs shuffled within text", shuffle_within(dev, rng), com)
    # Ur III positional (word level), matched N per stratum to Indus dev
    U = ur3_legends()
    words = [tuple(u["words"]) for u in U]
    comw = common_set(words)
    out["t2_ur3_words"] = show_t2("POS control: Ur III legends, word level, positional slots", words, comw)
    # matched N
    idx = rng.choice(len(words), 1000, replace=False)
    out["t2_ur3_words_n1000"] = show_t2("Ur III word level, n=1000", [words[i] for i in idx], comw)
    # Ur III with words mapped to Indus inventory (homography, Indus Zipf profile)
    ind_c = Counter(s for t in indus_seals("dev") for s in t)
    syms, w = zip(*ind_c.items()); w = np.array(w, float); w /= w.sum()
    wc = Counter(x for t in words for x in t)
    # rank-matched: frequent words get frequent symbols (random draw weighted by profile)
    mp = {x: syms[rng.choice(len(syms), p=w)] for x, _ in wc.most_common()}
    merged = [tuple(mp[x] for x in t) for t in words]
    out["t2_ur3_merged"] = show_t2("Ur III words merged to Indus inventory", [merged[i] for i in idx], common_set(merged))
    # Ur III labelled slots at sign level
    print("\n== Ur III labelled slots, sign level (one random sign per slot per legend; N matched)")
    signs_all = [tuple(u["signs"]) for u in U]
    coms = common_set(signs_all)
    lab = {}
    for sl in ("OWNER", "TITLE", "KIN", "FATHER", "SERV", "LORD", "EPITHET"):
        toks, cont = [], []
        for u in U:
            ss = [g for g, l in zip(u["signs"], u["sign_slots"]) if l == sl]
            if ss:
                toks.append(ss[rng.integers(len(ss))]); cont.append(tuple(ss))
        lab[sl] = (toks, cont)
    Nm = 300
    lr = {}
    for sl, (toks, cont) in lab.items():
        if len(toks) < Nm:
            continue
        ii = rng.choice(len(toks), Nm, replace=False)
        t = [toks[i] for i in ii]; c = [cont[i] for i in ii]
        cc = Counter(t); n1 = sum(v == 1 for v in cc.values())
        ccont = Counter(c); nov = [k for k, v in ccont.items() if v == 1]
        rare = sum(any(x not in coms for x in k) for k in nov)
        lr[sl] = dict(N=Nm, P=n1 / Nm, content_novel=len(nov) / Nm, frac_rare=rare / max(1, len(nov)), n_legends=len(toks))
        print(f" {sl:8s} legends={len(toks):5d} P_sign={n1/Nm:.2f} content_novel={len(nov)/Nm:.2f} frac_novel_rare={rare/max(1,len(nov)):.2f}")
    out["t2_ur3_labelled"] = lr

if what in ("t3", "all"):
    print("\n== T3 dev")
    for site in ("Mohenjodaro", "Harappa"):
        T = indus_seals("dev", site, 3)
        for K in (4, 8, 16):
            a = swap_null(T, K, rng, n=300)
            b = bigram_null(T, K, rng, n=300)
            out[f"t3_dev_{site}_K{K}"] = dict(swap=a, bigram=b)
            print(f" {site} n={len(T)} K={K}: I={a['I_obs']:.3f} swap null {a['I_null_mean']:.3f}+-{a['I_null_sd']:.3f} p={a['p']:.3f} | bigram null {b['I_null_mean']:.3f}+-{b['I_null_sd']:.3f} p={b['p']:.3f}")
    # size check: data drawn from fitted chain -> swap test should be null
    T = indus_seals("dev", "Mohenjodaro", 3)
    ch = BigramChain(T)
    ps = []
    for r in range(40):
        sim = [ch.sample(len(t), rng) for t in T]
        ps.append(swap_null(sim, 8, rng, n=100)["p"])
    ps = np.array(ps)
    print(f" SIZE: swap test on chain-generated data, P(p<0.05)={np.mean(ps<0.05):.2f} (40 reps)")
    out["t3_size_chain"] = dict(rate=float(np.mean(ps < 0.05)), reps=40)
    # Ur III positive control (word level)
    U = ur3_legends()
    words = [tuple(u["words"]) for u in U if 3 <= len(u["words"]) <= 8]
    idx = rng.choice(len(words), 600, replace=False)
    sub = [words[i] for i in idx]
    a = swap_null(sub, 8, rng, n=300)
    print(f" Ur III words n=600: I={a['I_obs']:.3f} null {a['I_null_mean']:.3f}+-{a['I_null_sd']:.3f} p={a['p']:.3f}")
    out["t3_ur3_n600"] = a
    # planted power at held-out-like sizes (from dev only)
    for site, n in (("Mohenjodaro", 220), ("Harappa", 30), ("Harappa", 140)):
        T = indus_seals("dev", site, 3)
        for f in (0.0, 0.25, 0.5):
            hits = 0; R = 40
            for r in range(R):
                ii = rng.choice(len(T), min(n, len(T)), replace=False)
                P = plant_template([T[i] for i in ii], f, rng)
                hits += swap_null(P, 8, rng, n=100)["p"] < 0.05
            print(f" POWER {site} n={n} f={f}: {hits/R:.2f}")
            out[f"t3_power_{site}_n{n}_f{f}"] = hits / R

dump(out, HERE / f"dev_{what}.json")
