"""Summarise out/<cond>.json into results.json and a printed table (rules from the prereg)."""
import json, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
summ = {}
for f in sorted((HERE / "out").glob("*.json")):
    R = json.load(open(f)); cond = f.stem; summ[cond] = {}
    print(f"\n== {cond}")
    print(" n | null S q95 | plant S med | S_true med | power S | FPR S | null E q95 | power E | FPR E | prec | recall | recall(rep>=2) | S>=S_true")
    for n in sorted({r["n"] for r in R}):
        g = lambda k: [r for r in R if r["n"] == n and r["kind"] == k]
        nu, pl, wl = g("shuffle"), g("planted"), g("wronglang")
        q = float(np.percentile([r["S"] for r in nu], 95)); qe = float(np.percentile([r["E"] for r in nu], 95))
        pw = np.mean([r["S"] > q for r in pl]); fp = np.mean([r["S"] > q for r in wl])
        pwe = np.mean([r["E"] > qe for r in pl]); fpe = np.mean([r["E"] > qe for r in wl])
        prec = np.median([r["n_correct"] / max(1, r["n_assigned"]) for r in pl])
        rec = np.median([r["n_correct"] / max(1, r["n_syl_present"]) for r in pl])
        rec2 = np.median([r["n_correct_rep2"] / max(1, r["n_syl_rep2"]) for r in pl])
        adq = np.mean([r["S"] >= r["S_true"] for r in pl])
        st = float(np.median([r["S_true"] for r in pl])); sm = float(np.median([r["S"] for r in pl]))
        et = float(np.median([r["E_true"] for r in pl]))
        works = bool(pw >= 0.8 and fp <= 0.2 and prec >= 0.5)
        d = dict(n=n, null_S_q95=q, planted_S_med=sm, S_true_med=st, power_S=pw, fpr_S=fp, null_E_q95=qe,
                 E_true_med=et, power_E=pwe, fpr_E=fpe, precision_med=prec, recall_med=rec, recall_rep2_med=rec2,
                 search_adequacy=adq, unicity_S_true_gt_null_q95=bool(st > q), works=works,
                 n_runs=dict(planted=len(pl), wronglang=len(wl), shuffle=len(nu)),
                 null_S_mean_per_text=float(np.mean([r["S"] for r in nu]) / n))
        summ[cond][n] = d
        print(f"{n:3d} | {q:9.1f} | {sm:11.1f} | {st:10.1f} | {pw:7.2f} | {fp:5.2f} | {qe:10.1f} | {pwe:7.2f} | {fpe:5.2f} | {prec:4.2f} | {rec:6.2f} | {rec2:14.2f} | {adq:.2f}  E_true med {et}  works={works}")
json.dump(summ, open(HERE / "results.json", "w"), indent=1, default=float)
