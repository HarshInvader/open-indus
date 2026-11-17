"""Part A calibration: nearest-neighbour distances AMONG real name lists under the merge and sym variants
(so the 'typical/peripheral/outlier' thresholds are re-derived for the transformed lists, not borrowed from
raw naming_sim). n = min(800, nA, nB); 20 subsamples per list.  -> partA_calib.json"""
import sys, json
from pathlib import Path
from itertools import combinations
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C


def ms(a):
    nm, v, n = a
    q = C.indus_profile("dev"); rng = np.random.default_rng(5)
    t, _ = C.N.load(nm)
    if v == "sym":
        t, _ = C.edge_strip(t)
    rows = []
    for _ in range(20):
        s = C.sample_types(t, min(n, len(t)), rng)
        s = C.merge_inventory(s, q, rng)
        rows.append(C.S.compute(s, rng, None, 20))
    return a, C.mean_of(rows, C.PRIMARY6)


if __name__ == "__main__":
    sizes = {}
    for nm in C.NAME_LISTS:
        t, _ = C.N.load(nm); sizes[(nm, "merge")] = len(t); sizes[(nm, "sym")] = len(C.edge_strip(t)[0])
    out = {}
    for v in ("merge", "sym"):
        jobs = set()
        for a, b in combinations(C.NAME_LISTS, 2):
            n = min(800, sizes[(a, v)], sizes[(b, v)]); jobs |= {(a, v, n), (b, v, n)}
        with Pool(2) as p:
            M = dict(p.map(ms, sorted(jobs)))
        nn = {}
        for a in C.NAME_LISTS:
            d = []
            for b in C.NAME_LISTS:
                if a == b: continue
                n = min(800, sizes[(a, v)], sizes[(b, v)])
                d.append((C.distance(M[(a, v, n)], M[(b, v, n)], C.NS_SCALES, C.PRIMARY6), b))
            nn[a] = min(d)
        dd = [x[0] for x in nn.values()]
        out[v] = dict(nn={a: [round(x[0], 3), x[1]] for a, x in nn.items()}, median=float(np.median(dd)), max=float(max(dd)))
        print(v, out[v], flush=True)
    json.dump(out, open(C.HERE / "partA_calib.json", "w"), indent=1)
