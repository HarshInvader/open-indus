"""CONFIRMATORY run for docs/prereg/slot_novelty.md (held-out + ICIT new sites). Do not edit after hashing
without a logged amendment.
usage: .venv/bin/python experiments/slot_novelty/confirm.py
"""
import numpy as np
from collections import Counter
from sn_lib import (indus_seals, icit_newsite_seals, common_set, t2_pooled_ci, pooled_label, t2_windows,
                    swap_null, bigram_null, plant_template, BigramChain, SLOTS, dump, HERE, strata)

CFG = dict(share_single=0.50, ratio_single=1.5, ratio_even=1.5)
K = 8
rng = np.random.default_rng(20261115)
out = {"cfg": CFG, "K": K}


def strip(r):
    d = {k: v for k, v in r.items() if k != "per_stratum"}
    d["per_stratum"] = {L: {s: dict(P=x[s]["P"], share=x[s]["share"], frac_novel_from_rare=x[s]["frac_novel_from_rare"],
                                    content_novel_rate=x[s]["content_novel_rate"]) for s in SLOTS} | {"N": x["N"]}
                        for L, x in r["per_stratum"].items()}
    return d


def t2(name, texts, common):
    r = t2_pooled_ci(texts, common, rng, B=1000)
    lab = pooled_label(r, CFG)
    h2b = (r["low"] == "closer" and r["ratio_minOM_over_closer"] >= 1.5 and r["ci_ratio_minOM_over_closer"][0] > 1.0)
    h2c = (r["top"] in ("opener", "medial") and r["second"] in ("opener", "medial") and r["ratio_top_second"] < 1.5)
    w = t2_windows(texts, common, rng)
    h2d = (w["interior"]["frac_novel_common"] > w["start"]["frac_novel_common"]
           and w["interior"]["frac_novel_common"] > w["end"]["frac_novel_common"])
    d = strip(r); d.update(label=lab, H2b_closer_closed=bool(h2b), H2c_opener_medial_equal=bool(h2c),
                           windows=w, H2d_interior_combos=bool(h2d), n_texts=len(texts))
    print(f"\n== T2 {name} n={len(texts)} N_pooled={r['N']}")
    print("  P", {s: round(r['P'][s], 3) for s in SLOTS}, "CI", {s: [round(x, 3) for x in r['ci_P_sub'][s]] for s in SLOTS})
    print("  share", {s: round(r['share'][s], 2) for s in SLOTS}, "top", r["top"], "t/2", round(r["ratio_top_second"], 2),
          [round(x, 2) for x in r["ci_ratio_top_second"]], "max/min", round(r["ratio_max_min"], 2),
          [round(x, 2) for x in r["ci_ratio_max_min"]])
    print("  minOM/closer", round(r["ratio_minOM_over_closer"], 2), [round(x, 2) for x in r["ci_ratio_minOM_over_closer"]])
    print("  LABEL", lab, "| H2b", h2b, "| H2c", h2c, "| H2d", h2d)
    print("  windows", {k: (round(v['novel_rate'], 2), round(v['frac_novel_common'], 2)) for k, v in w.items()})
    for L, x in r["per_stratum"].items():
        print(f"   L={L} N={x['N']} " + " ".join(f"{s[:3]} P={x[s]['P']:.2f} rare={x[s]['frac_novel_from_rare']:.2f}" for s in SLOTS))
    return d


# ---------------- T2
com_m77 = common_set(indus_seals("dev") + indus_seals("heldout"))  # rarity defined on all M77 seals
out["T2_heldout_all"] = t2("held-out, all sites (PRIMARY)", indus_seals("heldout", min_len=3), com_m77)
out["T2_heldout_MD"] = t2("held-out, Mohenjo-daro", indus_seals("heldout", "Mohenjodaro", 3), com_m77)
icit = icit_newsite_seals(3)
out["T2_icit_newsites"] = t2("ICIT seals from sites absent from M77", icit, common_set(icit_newsite_seals()))

# ---------------- T3
for site in ("Mohenjodaro", "Harappa"):
    T = indus_seals("heldout", site, 3)
    a = swap_null(T, K, rng, n=2000)
    b = bigram_null(T, K, rng, n=1000)
    sens = {f"K{k}": swap_null(T, k, rng, n=1000) for k in (4, 16)}
    out[f"T3_heldout_{site}"] = dict(swap=a, bigram=b, swap_sensK=sens)
    print(f"\n== T3 held-out {site} n={len(T)}: I={a['I_obs']:.4f} swap null {a['I_null_mean']:.4f}+-{a['I_null_sd']:.4f} "
          f"excess={a['excess']:+.4f} z={a['z']:+.2f} p={a['p']:.4f} | bigram null {b['I_null_mean']:.4f} p={b['p']:.4f} | "
          + " ".join(f"{k}: z={v['z']:+.2f} p={v['p']:.3f}" for k, v in sens.items()))
T = icit_newsite_seals(3)
a = swap_null(T, K, rng, n=1000)
out["T3_icit_newsites_pooled"] = a
print(f"== T3 ICIT new sites pooled n={len(T)}: excess={a['excess']:+.4f} z={a['z']:+.2f} p={a['p']:.4f}")
# Holm over the two primary site tests
ps = sorted([(out[f"T3_heldout_{s}"]["swap"]["p"], s) for s in ("Mohenjodaro", "Harappa")])
holm = {}
m = len(ps); run = 0
for i, (p, s) in enumerate(ps):
    run = max(run, min(1.0, (m - i) * p)); holm[s] = run
out["T3_holm"] = holm
print("Holm", holm)

# ---------------- T3 power (dev data only, held-out sizes)
pw = {}
for site, n in (("Mohenjodaro", len(indus_seals("heldout", "Mohenjodaro", 3))),
                ("Harappa", len(indus_seals("heldout", "Harappa", 3)))):
    D = indus_seals("dev", site, 3)
    for f in (0.0, 0.25, 0.5, 0.75):
        hits = 0; R = 100; ex = []
        for _ in range(R):
            ii = rng.choice(len(D), min(n, len(D)), replace=False)
            P = plant_template([D[i] for i in ii], f, rng)
            rr = swap_null(P, K, rng, n=200)
            hits += rr["p"] < 0.05; ex.append(rr["excess"])
        pw[f"{site}_n{n}_f{f}"] = dict(power=hits / R, mean_excess_bits=float(np.mean(ex)))
        print(f"POWER {site} n={n} f={f}: {hits/R:.2f} (mean excess {np.mean(ex):+.4f} bits)")
out["T3_power"] = pw
dump(out, HERE / "confirm.json")
