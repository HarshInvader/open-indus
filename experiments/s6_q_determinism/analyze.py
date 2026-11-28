"""Summarise the S6 sweeps into results.json.  Run after sweep.py A, B and C:

    .venv/bin/python -I experiments/s6_q_determinism/analyze.py
"""
import json
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
R = {k: json.load(open(HERE / "runs" / f"{k}.json")) for k in "ABC"}


def rng_of(runs, row, col):
    v = np.array([float(r["ledger"][row][col]) for r in runs if r["ledger"][row][col] != ""])
    return dict(min=float(v.min()), median=float(np.median(v)), max=float(v.max()), n=len(v))


out = {}
for k, runs in R.items():
    d = {c: rng_of(runs, "lr_gulf", c) for c in ("p_value", "q_global", "q_hier", "q_all")}
    d["other_lr_p"] = {row: rng_of(runs, row, "p_value") for row in sorted(runs[0]["ledger"])
                       if row.startswith("lr_") and row != "lr_gulf" and runs[0]["ledger"][row]["p_value"] != ""}
    d["distinct_v2_reruns_outputs"] = len({r["v2_reruns_sha256"] for r in runs})
    d["F_statistic_sets"] = sorted({json.dumps([r["F"]["foreign_mean_pct"], r["F"]["native_matched_mean"],
                                                r["F"]["pool_sizes"]]) for r in runs})
    if k == "C":
        d["p_mc95_widest"] = max((r["F"]["p_mc95"] for r in runs), key=lambda x: x[1] - x[0])
    out[k] = d

A, B, C = out["A"], out["B"], out["C"]
out["verdicts"] = {
    "H1_F_statistic_hash_free": dict(
        passed=len(A["F_statistic_sets"]) == 1,
        detail="foreign_mean_pct, native_matched_mean and pool sizes identical in all 20 Run A outputs"),
    "H2_byte_identical_under_hash_seeds": dict(passed=B["distinct_v2_reruns_outputs"] == 1,
                                              detail=f"{B['distinct_v2_reruns_outputs']} distinct output(s) over 3 hash seeds"),
    "H3_q_all_ratio_below_1_5": dict(passed=C["q_all"]["max"] / C["q_all"]["min"] < 1.5,
                                     ratio_after=round(C["q_all"]["max"] / C["q_all"]["min"], 3),
                                     ratio_before=round(A["q_all"]["max"] / A["q_all"]["min"], 3)),
}
json.dump(out, open(HERE / "results.json", "w"), indent=1)
print(json.dumps(out["verdicts"], indent=1))
for k in "ABC":
    print(k, {c: (round(out[k][c]["min"], 6), round(out[k][c]["max"], 6)) for c in ("p_value", "q_global", "q_hier", "q_all")})
for row in A["other_lr_p"]:
    print(row, "A", (A["other_lr_p"][row]["min"], A["other_lr_p"][row]["max"]),
          "C", (C["other_lr_p"][row]["min"], C["other_lr_p"][row]["max"]))
