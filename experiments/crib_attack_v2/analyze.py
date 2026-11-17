"""Summarise out/grid.jsonl by the pre-registered rules (docs/prereg/crib_attack_v2_planted.md)."""
import json, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from run_grid import ATT_LISTS, NS, ANCHORS  # noqa

rows = [json.loads(l) for l in open(HERE / "out" / "grid.jsonl")]
cell = defaultdict(lambda: defaultdict(list))
for r in rows:
    cell[(r["list"], r["n"], r["a"])][r["kind"]].append(r)

out = []
for t in ATT_LISTS:
    for n in NS:
        for a in ANCHORS:
            c = cell.get((t, n, a))
            if not c or not c["shuffle"] or not c["planted"]:
                continue
            q95 = float(np.quantile([r["E"] for r in c["shuffle"]], 0.95))
            pl, wl = c["planted"], c["wronglang"]
            prec = [r["n_correct"] / r["n_used"] if r["n_used"] else 0.0 for r in pl]
            rec = [r["n_correct"] / r["n_syl"] if r["n_syl"] else 0.0 for r in pl]
            d = dict(list=t, n=n, a=a, n_shuffle=len(c["shuffle"]), n_planted=len(pl), n_wrong=len(wl),
                     null_E_med=float(np.median([r["E"] for r in c["shuffle"]])), null_q95=q95,
                     planted_E_med=float(np.median([r["E"] for r in pl])),
                     true_E_med=float(np.median([r["E_true"] for r in pl])),
                     matchable_med=float(np.median([r["n_matchable"] for r in pl])),
                     power=float(np.mean([r["E"] > q95 for r in pl])),
                     fpr=float(np.mean([r["E"] > q95 for r in wl])) if wl else None,
                     unicity=bool(np.median([r["E_true"] for r in pl]) > q95),
                     true_beats_q95_frac=float(np.mean([r["E_true"] > q95 for r in pl])),
                     search_ge_true=float(np.mean([r["E"] >= r["E_true"] for r in pl])),
                     prec_med=float(np.median(prec)), rec_med=float(np.median(rec)),
                     correct_med=float(np.median([r["n_correct"] for r in pl])))
            d["passes"] = bool(d["power"] >= 0.8 and (d["fpr"] is not None and d["fpr"] <= 0.2) and d["prec_med"] >= 0.5)
            out.append(d)

json.dump(out, open(HERE / "out" / "summary.json", "w"), indent=1)
hdr = "| list | n | a | null med | null q95 | planted E med | true E med | power | FPR | unicity (true>q95 share) | prec med | rec med | pass |"
print(hdr); print("|" + "---|" * 13)
for d in out:
    print(f"| {d['list']} | {d['n']} | {d['a']} | {d['null_E_med']:.0f} | {d['null_q95']:.1f} | {d['planted_E_med']:.1f} | "
          f"{d['true_E_med']:.1f} | {d['power']:.2f} | {d['fpr'] if d['fpr'] is None else round(d['fpr'], 2)} | "
          f"{'yes' if d['unicity'] else 'no'} ({d['true_beats_q95_frac']:.2f}) | {d['prec_med']:.2f} | {d['rec_med']:.2f} | "
          f"{'PASS' if d['passes'] else '-'} |")
go = [d for d in out if d["passes"] and d["n"] in (20, 41, 49) and d["a"] <= 3]
print("\nrows", len(rows), "cells", len(out), "passing cells", sum(d["passes"] for d in out))
print("GO for #17" if go else "NO-GO for #17 (no passing cell with n in 20/41/49 and a<=3)")
