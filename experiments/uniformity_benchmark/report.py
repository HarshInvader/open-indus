"""Summarise draws.jsonl + calib.json into results.json, applying the frozen prereg rules.
    .venv/bin/python -I experiments/uniformity_benchmark/report.py
"""
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
NAME_BEARING = ["ur3_umma_girsu", "ur3_pd_nippur", "lat_britannia_germania"]
INDUS = dict(site_auc=0.49, site_null_q95=0.56, time_md_auc=0.61)

D = defaultdict(list)
for l in open(HERE / "draws.jsonl"):
    r = json.loads(l)
    D[(r["pair"], r["variant"], r["design"])].append(r)

calib = json.load(open(HERE / "calib.json")) if (HERE / "calib.json").exists() else None
if calib:
    qs = np.array(sorted(float(q) for q in calib))
    mu = np.maximum.accumulate(np.array([calib[str(q) if str(q) in calib else repr(q)]["mean_auc"] for q in qs]))


def q_of(a):
    if not calib:
        return None
    if a <= mu[0]:
        return 0.0
    if a >= mu[-1]:
        return f">{qs[-1]}"
    return float(np.interp(a, mu, qs))


S = {}
for (pair, v, d), rows in sorted(D.items()):
    a = np.array([r["auc"] for r in rows if r["auc"] is not None])
    n0 = np.array([r["null_auc"] for r in rows if r["null_auc"] is not None])
    failed = sum(r["auc"] is None for r in rows)
    if len(a) == 0:
        S[f"{pair}|{v}|{d}"] = dict(n_draws=len(rows), failed=failed); continue
    med = float(np.median(a))
    S[f"{pair}|{v}|{d}"] = dict(
        n_draws=len(rows), failed=failed, median_auc=med, lo=float(np.percentile(a, 2.5)), hi=float(np.percentile(a, 97.5)),
        null_mean=float(n0.mean()), null_q95=float(np.quantile(n0, 0.95)),
        p=float((1 + (n0 >= med).sum()) / (len(n0) + 1)), share_ge_065=float((a >= 0.65).mean()),
        draws_with_bin_fill=int(sum(r["short"] > 0 for r in rows)), mean_bin_fill=float(np.mean([r["short"] for r in rows])),
        planted_q=q_of(med), n_feat_mean=float(np.mean([r["n_feat"] for r in rows if r.get("n_feat")])))


def med(pair, v="whole", d="balanced"):
    return S.get(f"{pair}|{v}|{d}", {}).get("median_auc")


pred = {
    "P1_umma_girsu_whole_ge_080": med("ur3_umma_girsu") is not None and med("ur3_umma_girsu") >= 0.80,
    "P1_umma_girsu_frame_ge_065": (med("ur3_umma_girsu", "frame_removed") or 0) >= 0.65,
    "P2_uruk_ge_070": (med("pc_uruk4_uruk3") or 0) >= 0.70,
    "P3_latin_050_065": med("lat_britannia_germania") is not None and 0.50 <= med("lat_britannia_germania") <= 0.65,
    "added_pd_nippur_frame_ge_065": (med("ur3_pd_nippur", "frame_removed") or 0) >= 0.65,
}
reach = [p for p in NAME_BEARING if (med(p, "frame_removed") or 0) >= 0.65]
lw, lf = S.get("lat_britannia_germania|whole|balanced", {}), S.get("lat_britannia_germania|frame_removed|balanced", {})
kill = dict(
    K1_fewer_than_two_name_pairs=len(reach) < 2, name_pairs_reaching=reach,
    K2_latin_frame_ge_065=(med("lat_britannia_germania", "frame_removed") or 0) >= 0.65,
    K3_latin_at_chance=bool(lw and lf and lw["median_auc"] < lw["null_q95"] and lf["median_auc"] < lf["null_q95"]),
)
refs = sorted([(k, s["median_auc"]) for k, s in S.items() if "|balanced" in k and "median_auc" in s], key=lambda x: x[1])
rank = dict(indus_site=INDUS["site_auc"], below=[k for k, m in refs if m < INDUS["site_auc"]],
            above=[k for k, m in refs if m >= INDUS["site_auc"]], indus_time_md=INDUS["time_md_auc"])
out = dict(summary=S, predictions=pred, kill=kill, indus_rank=rank, indus=INDUS,
           indus_planted_q=q_of(INDUS["site_auc"]), calib=calib)
json.dump(out, open(HERE / "results.json", "w"), indent=1)
for k, s in S.items():
    print(k, {a: (round(b, 3) if isinstance(b, float) else b) for a, b in s.items()})
print(json.dumps(pred)); print(json.dumps(kill)); print(json.dumps(rank)); print("indus q", out["indus_planted_q"])
