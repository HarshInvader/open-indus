"""Power vs share of texts that carry no paradigm (uninflected unrelated vocabulary), at Indus dev size."""
import sys, json, itertools
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import corpora as C, grid_lib as G
best = json.load(open(HERE / "out/controls.json"))["best"]
G.set_params(min_stem=best["min_stem"], max_tail=best["max_tail"], weight=best.get("weight", "count"))
rows = []
for N, lg, pn in itertools.product([1317], [0.0, 0.3], [0.0, 0.25, 0.5, 0.75, 0.9]):
    rs = []
    for sd in range(3):
        t, tc, tv, info = C.synthetic(N, logo_share=lg, seed=sd, p_noise=pn)[:4]
        e = G.evaluate(t, tc, tv); rs.append(e)
        if sd == 0:
            obs = G.stats(t, "end"); nd = G.null_stats(t, "block", n=30, seed=1)
            qz = (obs["modularity"] - nd["modularity"][0]) / (nd["modularity"][1] + 1e-9)
            az = (obs["alt_stems"] - nd["alt_stems"][0]) / (nd["alt_stems"][1] + 1e-9)
    m = lambda k: round(float(np.nanmean([r[k] for r in rs])), 3)
    row = dict(N=N, logo=lg, p_noise=pn, ari_cons=m("ari_cons"), ari_cons_louvain=m("ari_cons_louvain"), ari_vow=m("ari_vow"),
               coverage=m("coverage"), edge_prec=m("edge_prec_cons"), edge_base=m("edge_base_cons"),
               end_alt_z_block=round(az, 2), end_modularity_z_block=round(qz, 2))
    rows.append(row); print(row, flush=True)
json.dump(rows, open(HERE / "out/sweep_noise.json", "w"), indent=1)
