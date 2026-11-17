"""Is the within-type null (seals 0.10, tablets 0.23) a type effect or just lost units?
Subsample random units (any type) to the same counts and recompute rho."""
import sys, json; sys.path.insert(0, "experiments/redteam_chrono")
from rc_lib import *
H = dataset_harp(); V = dataset_vats()
rng = np.random.default_rng(5)
res = {}
tabH = [u for u in H if u["type"].startswith("tab")]
tsV = [u for u in V if u["type"] in ("tablet", "sealing")]
sH = [u for u in H if u["type"] == "seal"]; sV = [u for u in V if u["type"] == "seal"]
for name, nh, nv, nm in [("tablet-sized", len(tabH), len(tsV), 5), ("seal-sized", len(sH), len(sV), 3)]:
    rh = []
    for k in range(200):
        a = [H[i] for i in rng.choice(len(H), nh, replace=False)]
        b = [V[i] for i in rng.choice(len(V), nv, replace=False)]
        r = compare(Shift(a), Shift(b), nperm=1, nmin=nm)
        if r["n"] >= 6: rh.append(r["rho"])
    rh = np.array(rh)
    print(name, nh, nv, "random-subsample rho mean %.3f, 5-95%% %.3f..%.3f" % (rh.mean(), *np.percentile(rh, [5, 95])))
    res[name] = dict(nH=nh, nV=nv, mean=float(rh.mean()), q05=float(np.percentile(rh, 5)), q95=float(np.percentile(rh, 95)))
json.dump(res, open("experiments/redteam_chrono/r5.json", "w"), indent=1)
