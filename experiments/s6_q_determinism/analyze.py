"""Summarise the S6 sweeps into results.json.  Run after sweep.py A, B and C:

    .venv/bin/python -I experiments/s6_q_determinism/analyze.py
"""
import json
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
R = {k: json.load(open(HERE / "runs" / f"{k}.json")) for k in "ABCD" if (HERE / "runs" / f"{k}.json").exists()}


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
    d["lr_fr_lex"] = {c: rng_of(runs, "lr_fr_lex", c) for c in ("p_value", "q_global", "q_hier", "q_all")}
    if k in ("C", "D"):
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
if "D" in out:
    D = out["D"]["lr_fr_lex"]
    out["verdicts"]["H4_lr_fr_lex_ratio_below_1_5 (S6b)"] = dict(
        passed=D["p_value"]["max"] / D["p_value"]["min"] < 1.5, ratio_after=round(D["p_value"]["max"] / D["p_value"]["min"], 3),
        ratio_before=round(out["C"]["lr_fr_lex"]["p_value"]["max"] / out["C"]["lr_fr_lex"]["p_value"]["min"], 3))
    out["verdicts"]["H5_lr_fr_lex_q_global_below_0_05 (S6b, descriptive)"] = dict(
        all_seeds=D["q_global"]["max"] < 0.05, no_seed=D["q_global"]["min"] >= 0.05, range=[D["q_global"]["min"], D["q_global"]["max"]])
json.dump(out, open(HERE / "results.json", "w"), indent=1)
print(json.dumps(out["verdicts"], indent=1))
for k in "ABC":
    print(k, {c: (round(out[k][c]["min"], 6), round(out[k][c]["max"], 6)) for c in ("p_value", "q_global", "q_hier", "q_all")})
for row in A["other_lr_p"]:
    print(row, "A", (A["other_lr_p"][row]["min"], A["other_lr_p"][row]["max"]),
          "C", (C["other_lr_p"][row]["min"], C["other_lr_p"][row]["max"]))
