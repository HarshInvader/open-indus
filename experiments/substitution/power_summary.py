"""Power curves and Indus upper bounds from power_runs.json.
Detection rule D (fixed here, before held-out): n_sce > 95th percentile of n_sce in the
synthetic p=0 corpora of the same size and multiplicity. Oracle rule O: >=3 planted
equations pass as SCEs and >=2 of them share a spelling sign (what a decipherer needs).
Indus bound: share of planted corpora with n_sce <= Indus dev n_sce (11) = one-sided p
for 'Indus contains a system at rate p'.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import save_results  # noqa: E402

rows = json.load(open(HERE / "power_runs.json"))
res = json.load(open(HERE / "results.json"))
indus_sce = res["dev_sce"]["m77_dev"]["n_sce"]
indus_shared = res["dev_sce"]["m77_dev"]["sce_shared"]

g = defaultdict(list)
for r in rows:
    key = (r["kind"], r.get("n"), r.get("mult_p"), r["p"]) if r["kind"] == "synth" else (r["kind"], 1675, None, r["p"])
    g[key].append(r)
thr = {}
for (kind, n, m, p), rs in g.items():
    if kind == "synth" and p == 0.0:
        thr[(n, m)] = float(np.percentile([r["n_sce"] for r in rs], 95))
thr_indus = thr[(1675, 0.9)]
out = []
for (kind, n, m, p), rs in sorted(g.items(), key=lambda z: (z[0][0], z[0][1] or 0, z[0][2] or 0, z[0][3])):
    t = thr.get((n, m), thr_indus)
    d = dict(kind=kind, n=n, mult_p=m, p=p, runs=len(rs),
             token_share=float(np.mean([r["token_share"] for r in rs])),
             n_sce=float(np.mean([r["n_sce"] for r in rs])), n_sce_sd=float(np.std([r["n_sce"] for r in rs])),
             tp_sce=float(np.mean([r["tp_sce"] for r in rs])), rec=float(np.mean([r["rec"] for r in rs])),
             n_truth=float(np.mean([r["n_truth"] for r in rs])),
             threshold=t,
             power_D=float(np.mean([r["n_sce"] > t for r in rs])),
             power_O=float(np.mean([(r["tp_sce"] >= 3 and r["sys_tp"] >= 2) for r in rs])),
             p_indus_le=float(np.mean([r["n_sce"] <= indus_sce for r in rs])))
    out.append(d)
    print("%-11s n=%s m=%s p=%.2f share=%.2f nSCE=%.1f±%.1f tp=%.1f rec=%.1f/%.0f thr=%.1f powerD=%.2f powerO=%.2f P(nSCE<=Indus)=%.2f" % (
        kind, n, m, p, d["token_share"], d["n_sce"], d["n_sce_sd"], d["tp_sce"], d["rec"], d["n_truth"], t,
        d["power_D"], d["power_O"], d["p_indus_le"]))


def min_p(kind, n, m, key):
    c = sorted([d for d in out if d["kind"] == kind and d["n"] == n and d["mult_p"] == m and d["p"] > 0],
               key=lambda d: d["p"])
    for d in c:
        if d[key] >= 0.8:
            return d["p"], d["token_share"]
    return None, None


summary = dict(indus_dev_n_sce=indus_sce, indus_dev_sce_shared=indus_shared, thresholds={str(k): v for k, v in thr.items()},
               curves=out,
               min_p_80_D_synth1675=min_p("synth", 1675, 0.9, "power_D"),
               min_p_80_O_synth1675=min_p("synth", 1675, 0.9, "power_O"),
               min_p_80_D_synth2300=min_p("synth", 2300, 0.9, "power_D"),
               min_p_80_O_synth2300=min_p("synth", 2300, 0.9, "power_O"),
               min_p_80_D_synth2300_highmult=min_p("synth", 2300, 0.6, "power_D"),
               min_p_80_O_synth2300_highmult=min_p("synth", 2300, 0.6, "power_O"),
               min_p_80_D_indusplant=min_p("indus_plant", 1675, None, "power_D"),
               min_p_80_O_indusplant=min_p("indus_plant", 1675, None, "power_O"))
for k, v in summary.items():
    if k.startswith("min_p") or k.startswith("indus"):
        print(k, v)
save_results("power", summary)
