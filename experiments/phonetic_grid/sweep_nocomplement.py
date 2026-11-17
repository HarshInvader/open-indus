"""Power when logograms write the WHOLE inflected word (no phonetic complement / spelled ending)."""
import sys, json, itertools
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import corpora as C, grid_lib as G
best = json.load(open(HERE / "out/controls.json"))["best"]
G.set_params(min_stem=best["min_stem"], max_tail=best["max_tail"], weight=best.get("weight", "count"))
rows = []
for N, lg in itertools.product([1317, 2300], [0.0, 0.15, 0.3, 0.5]):
    rs = []
    for sd in range(3):
        t, tc, tv, info = C.synthetic(N, logo_share=lg, seed=sd, complement=False)[:4]
        e = G.evaluate(t, tc, tv); e["logo_real"] = info["logo_share"]; rs.append(e)
    m = lambda k: round(float(np.nanmean([r[k] for r in rs])), 3)
    row = dict(N=N, logo=lg, logo_real=m("logo_real"), ari_cons=m("ari_cons"), ari_cons_louvain=m("ari_cons_louvain"),
               ari_vow=m("ari_vow"), coverage=m("coverage"), edge_prec=m("edge_prec_cons"), edge_base=m("edge_base_cons"))
    rows.append(row); print(row, flush=True)
json.dump(rows, open(HERE / "out/sweep_nocomplement.json", "w"), indent=1)
