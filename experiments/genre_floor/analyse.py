"""Summarise out/floor.jsonl per prereg: power per cell, floor per model x kind, headline floor."""
import json, sys, warnings
warnings.filterwarnings("ignore")
from collections import defaultdict
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
recs = [json.loads(l) for l in open(HERE / "out/floor.jsonl")]
cells = defaultdict(list)
for r in recs:
    cells[(r["kind"], r["s"])].append(r)
res = dict(cells={}, floor={}, logit={}, null_fp={})
for (k, s), rs in sorted(cells.items()):
    c = dict(n=len(rs), gain=float(np.mean([r["gain"] for r in rs])), gain_sd=float(np.std([r["gain"] for r in rs])))
    for m in ("HMM", "LCA"):
        c[m] = dict(power=float(np.mean([r[m]["det"] for r in rs])),
                    K2=float(np.mean([r[m]["K"] >= 2 for r in rs])),
                    Kmean=float(np.mean([r[m]["K"] for r in rs])))
    res["cells"][f"{k}_{s}"] = c
for m in ("HMM", "LCA"):
    for nk in ("NULL", "CUN"):
        rs = cells.get((nk, 0.0), [])
        if rs:
            res["null_fp"][f"{m}_{nk}"] = float(np.mean([r[m]["det"] for r in rs]))
    for k in ("VOC", "FORM", "LEN", "MIX", "CUN"):
        ss = sorted(s for kk, s in cells if kk == k and s > 0)
        if not ss:
            continue
        pw = [res["cells"][f"{k}_{s}"][m]["power"] for s in ss]
        g = [res["cells"][f"{k}_{s}"]["gain"] for s in ss]
        fl = None
        for i in range(len(ss)):
            if all(p >= 0.8 for p in pw[i:]):
                fl = g[i]; break
        res["floor"][f"{m}_{k}"] = fl if fl is not None else f">{max(g):.3f}"
        # secondary: logistic fit detection ~ gain
        x = np.array([r["gain"] for s in ss for r in cells[(k, s)]]); y = np.array([r[m]["det"] for s in ss for r in cells[(k, s)]])
        if y.min() != y.max():
            from sklearn.linear_model import LogisticRegression
            lr = LogisticRegression(C=1e4).fit(x[:, None], y)
            b0, b1 = lr.intercept_[0], lr.coef_[0, 0]
            res["logit"][f"{m}_{k}"] = float((np.log(0.8 / 0.2) - b0) / b1) if b1 > 0 else None
        else:
            res["logit"][f"{m}_{k}"] = None
json.dump(res, open(HERE / "summary.json", "w"), indent=1)
print(json.dumps(res, indent=1))
