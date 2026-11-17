"""EXPLORATORY (not pre-registered). How much mould/batch clustering would a rotating closed series need
to look as uneven as the copper types? Batches are issued uniformly over K types (rotation); each batch
survives with a size drawn from a geometric law with mean m; draw batches until N objects. Report median
Gini and median observed S for each (K, m), against observed full table (N=178, S=37, Gini 0.549) and core
table (N=163, S=22, Gini 0.419)."""
import json, numpy as np
from pathlib import Path
OUT = Path(__file__).resolve().parent
rng = np.random.default_rng(7)
def gini(x):
    x = np.sort(np.asarray(x, float)); n = len(x)
    return float((2*np.arange(1, n+1)-n-1).dot(x)/(n*x.sum()))
res = {}
for N, label in ((178, "full"), (163, "core")):
    for K in (12, 13, 27, 28):
        for m in (1, 2, 4, 8, 12, 16):
            gs, ss = [], []
            for _ in range(2000):
                c = np.zeros(K); tot = 0
                while tot < N:
                    b = min(rng.geometric(1/m), N-tot); c[rng.integers(K)] += b; tot += b
                c = c[c > 0]; gs.append(gini(c)); ss.append(len(c))
            res[f"{label}_K{K}_m{m}"] = dict(gini_median=float(np.median(gs)), gini_95=[float(np.percentile(gs,2.5)), float(np.percentile(gs,97.5))], S_median=float(np.median(ss)))
            print(label, K, m, res[f"{label}_K{K}_m{m}"])
p = OUT/"results.json"; R = json.load(open(p)); R["exploratory_batch_clustering"] = res; json.dump(R, open(p, "w"), indent=1)
