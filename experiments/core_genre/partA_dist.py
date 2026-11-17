"""Part A distances: naming_sim distance (RMS z over the 6 primary statistics, naming_sim realcmp_scales) between
Indus cores and each real name list under each red-team variant, at matched n (min(nA, nB, cap); cap 800 dev,
423 held-out). Variants: raw, trunc, merge, merge_slot (A1), edge (A2 control: the grammar-free frame-stripping
rule applied to the NAME lists themselves), edge_merge (both), sym (Indus grammar-free edge segments vs names edge-stripped + merged). Indus target: grammar cores; also Indus edge
segments vs names edge. Reference threshold = naming_sim real-list NN max 1.21 (median 0.87).
Usage: .venv/bin/python -I experiments/core_genre/partA_dist.py -> partA_dist.json"""
import sys, json
from pathlib import Path
from collections import Counter
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C

B = 30
SC = C.NS_SCALES
KEYS = C.PRIMARY6


def variant_sample(types, n, rng, variant, q):
    K = len(q)
    if variant == "trunc":
        f = Counter(e for t in types for e in t)
        top = {e for e, _ in f.most_common(K)}
        pool = [t for t in types if all(e in top for e in t)]
        return C.sample_types(pool, min(n, len(pool)), rng) if len(pool) >= 50 else None
    s = C.sample_types(types, min(n, len(types)), rng)
    if variant in ("merge", "edge_merge", "sym"):
        s = C.merge_inventory(s, q, rng)
    elif variant == "merge_slot":
        s = C.merge_inventory(s, q, rng, slot_preserving=True)
    return s


def job(a):
    nm, variant, split = a
    cap = 800 if split == "dev" else 423
    q = C.indus_profile("dev")
    types, _ = C.N.load(nm)
    if variant.startswith("edge"):
        types, _ = C.edge_strip(types)
    ind = C.indus_cores(split)[0] if variant != "sym" else C.indus_texts(split, "edge")[0]
    if variant == "sym":
        types, _ = C.edge_strip(types)
    n = min(cap, len(types), len(ind))
    rng = np.random.default_rng(11)
    ra, rb = [], []
    for _ in range(B):
        s = variant_sample(types, n, rng, variant, q)
        if s is None:
            return a, None
        rb.append(C.S.compute(s, rng, None, 20))
        ra.append(C.S.compute(C.sample_types(ind, n, rng), rng, None, 20))
    ma, mb = C.mean_of(ra, KEYS), C.mean_of(rb, KEYS)
    dboot = [C.distance(x, y, SC, KEYS) for x, y in zip(ra, rb)]
    return a, dict(n=n, d=C.distance(ma, mb, SC, KEYS), d_boot_lo=float(np.nanpercentile(dboot, 2.5)),
                   z={k: (ma[k] - mb[k]) / SC[k] for k in KEYS}, ref=mb, indus=ma)


if __name__ == "__main__":
    jobs = [(nm, v, sp) for sp in ("dev", "heldout") for nm in C.NAME_LISTS
            for v in ("raw", "trunc", "merge", "merge_slot", "edge", "edge_merge", "sym")]
    with Pool(2) as p:
        out = p.map(job, jobs)
    res = {}
    for (nm, v, sp), r in out:
        res.setdefault(sp, {}).setdefault(v, {})[nm] = C.rnd(r) if r else None
    summ = {}
    for sp in res:
        for v in res[sp]:
            rows = sorted([(r["d"], nm) for nm, r in res[sp][v].items() if r and r["d"] is not None])
            big = sorted([(r["d"], nm) for nm, r in res[sp][v].items() if r and r["d"] is not None and r["n"] >= 400])
            summ[f"{sp}_{v}"] = dict(nearest=rows[:3], nearest_n400=big[:3],
                                     label=("typical" if rows[0][0] <= .87 else "peripheral" if rows[0][0] <= 1.21 else "outlier"),
                                     label_n400=("typical" if big[0][0] <= .87 else "peripheral" if big[0][0] <= 1.21 else "outlier") if big else None)
            print(sp, v, summ[f"{sp}_{v}"], flush=True)
    json.dump(dict(summary=summ, detail=res), open(C.HERE / "partA_dist.json", "w"), indent=1, ensure_ascii=False)
