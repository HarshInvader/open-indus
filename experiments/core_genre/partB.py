"""Part B: which real genre do the Indus core statistics resemble? Pre-registered in docs/prereg/core_genre.md.

Variants (all with the frozen naming_sim statistics and distance; numeral tokens removed; units 1..8 elements):
  V1 raw   Indus grammar cores        vs each system's whole units, own inventory
  V2 merge Indus grammar cores        vs whole units merged onto the Indus core-sign frequency profile (286 classes)
  V3 sym   Indus edge segments (grammar-free frame stripping) vs each system's edge segments (same rule), merged
Matched n = min(n_system, n_indus, cap), cap 800 (dev) / 423 (held-out). B paired subsamples.
Distance = RMS over the 6 PRIMARY statistics of z-differences, z scaled by naming_sim realcmp_scales (fixed);
sensitivity: scales = SD of the reference-system means in that variant (calib).

  calib : reference systems only (no Indus). Per variant: means at n = min(800, size); pairwise distances at matched
          n; nearest-neighbour distribution (median, max) -> partB_calib.json
  score : Indus dev + held-out vs every reference, rankings, bootstrap category comparisons -> partB_score.json
Usage: .venv/bin/python -I experiments/core_genre/partB.py calib|score
"""
import sys, json
from pathlib import Path
from itertools import combinations
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C
import genres as G

KEYS = C.PRIMARY6
SC = C.NS_SCALES
VARIANTS = ["raw", "merge", "sym"]
SYSTEMS = list(G.GENRES) + list(G.CODES) + C.NAME_LISTS
B_CAL, B_SC = 15, 30
_u = {}


def units(nm, v):
    k = (nm, v)
    if k not in _u:
        if nm.startswith("indus_"):
            sp = nm.split("_", 1)[1]
            _u[k] = C.indus_cores(sp)[0] if v != "sym" else C.indus_texts(sp, "edge")[0]
        else:
            t = G.load(nm)
            _u[k] = C.edge_strip(t)[0] if v == "sym" else t
    return _u[k]


def draw(nm, v, n, rng, q):
    s = C.sample_types(units(nm, v), n, rng)
    if v in ("merge", "sym") and not nm.startswith("indus_"):
        s = C.merge_inventory(s, q, rng)
    return s


def reps(a):
    nm, v, n, B, seed = a
    q = C.indus_profile("dev")
    rng = np.random.default_rng(seed)
    rows = [C.S.compute(draw(nm, v, n, rng, q), rng, None, 15) for _ in range(B)]
    return a, rows


def calib():
    jobs, pairs = set(), []
    for v in VARIANTS:
        for a, b in combinations(SYSTEMS, 2):
            n = min(800, len(units(a, v)), len(units(b, v)))
            if n < 100:
                continue
            pairs.append((v, a, b, n)); jobs |= {(a, v, n, B_CAL, 3), (b, v, n, B_CAL, 3)}
    with Pool(2) as p:
        R = dict(p.map(reps, sorted(jobs)))
    M = {k[:3]: C.mean_of(r, KEYS) for k, r in R.items()}
    out = {}
    for v in VARIANTS:
        D = {}
        for (vv, a, b, n) in pairs:
            if vv != v:
                continue
            D[(a, b)] = D[(b, a)] = C.distance(M[(a, v, n)], M[(b, v, n)], SC, KEYS)
        nn = {}
        for a in SYSTEMS:
            d = sorted((D[(a, b)], b) for b in SYSTEMS if (a, b) in D and np.isfinite(D[(a, b)]))
            if d:
                nn[a] = dict(d=round(d[0][0], 3), nearest=d[0][1], group_of_nearest=G.GROUP[d[0][1]],
                             next=[(b, round(x, 2)) for x, b in d[1:4]])
        dd = [x["d"] for x in nn.values()]
        at800 = {a: M[(a, v, min(800, len(units(a, v))))] for a in SYSTEMS if (a, v, min(800, len(units(a, v)))) in M}
        pooled = {k: float(np.nanstd([m[k] for m in at800.values()])) for k in KEYS}
        grp_hits = sum(1 for a, x in nn.items() if x["group_of_nearest"] == G.GROUP[a])
        out[v] = dict(nn=nn, nn_median=float(np.median(dd)), nn_max=float(max(dd)), pooled_scales=pooled,
                      group_nn_hits=[grp_hits, len(nn)], means_at_cap={a: C.rnd(m) for a, m in at800.items()},
                      sizes={a: len(units(a, v)) for a in SYSTEMS})
        print(v, "NN median", round(out[v]["nn_median"], 3), "max", round(out[v]["nn_max"], 3),
              "group hits", grp_hits, "/", len(nn), flush=True)
        for a in SYSTEMS:
            if a in nn:
                print(f"   {a:15s} {G.GROUP[a]:5s} -> {nn[a]['nearest']:15s} {nn[a]['d']}", flush=True)
    json.dump(out, open(C.HERE / "partB_calib.json", "w"), indent=1, ensure_ascii=False)


def score():
    cal = json.load(open(C.HERE / "partB_calib.json"))
    res = {}
    for sp, cap in (("dev", 800), ("heldout", 423)):
        ind = f"indus_{sp}"
        for v in VARIANTS:
            jobs = []
            for nm in SYSTEMS:
                n = min(cap, len(units(nm, v)), len(units(ind, v)))
                if n < 100:
                    continue
                jobs += [(nm, v, n, B_SC, 21), (ind, v, n, B_SC, 22)]
            with Pool(2) as p:
                R = dict(p.map(reps, sorted(set(jobs))))
            rows, boot = [], {}
            for nm in SYSTEMS:
                n = min(cap, len(units(nm, v)), len(units(ind, v)))
                if n < 100:
                    continue
                ra, rb = R[(ind, v, n, B_SC, 22)], R[(nm, v, n, B_SC, 21)]
                ma, mb = C.mean_of(ra, KEYS), C.mean_of(rb, KEYS)
                d = C.distance(ma, mb, SC, KEYS)
                dp = C.distance(ma, mb, cal[v]["pooled_scales"], KEYS)
                # bootstrap: replicate-level means of Indus vs system (resample replicates with replacement)
                rng = np.random.default_rng(99)
                bd = []
                for _ in range(200):
                    ia = rng.integers(0, B_SC, B_SC); ib = rng.integers(0, B_SC, B_SC)
                    bd.append(C.distance(C.mean_of([ra[i] for i in ia], KEYS), C.mean_of([rb[i] for i in ib], KEYS), SC, KEYS))
                boot[nm] = np.array(bd)
                rows.append(dict(system=nm, group=G.GROUP[nm], n=n, d=d, d_pooled=dp,
                                 ci=[float(np.percentile(bd, 2.5)), float(np.percentile(bd, 97.5))],
                                 z={k: (ma[k] - mb[k]) / SC[k] for k in KEYS}, indus=ma, ref=mb))
            rows.sort(key=lambda r: r["d"])
            nearest = rows[0]["system"]
            # bootstrap share nearest; category comparison
            names = [r["system"] for r in rows]
            stack = np.vstack([boot[x] for x in names])
            share_nearest = {x: float(np.mean(np.argmin(stack, 0) == i)) for i, x in enumerate(names)}
            best = {g: np.min(np.vstack([boot[x] for x in names if G.GROUP[x] == g]), 0) for g in ("genre", "code", "name")}
            cat = {"genre_lt_name": float(np.mean(best["genre"] < best["name"])),
                   "code_lt_name": float(np.mean(best["code"] < best["name"])),
                   "genre_lt_code": float(np.mean(best["genre"] < best["code"]))}
            within = [r["system"] for r in rows if r["ci"][0] <= rows[0]["ci"][1]]
            loso = {}
            for q in KEYS:
                keep = [k for k in KEYS if k != q]
                dd = sorted((float(np.sqrt(np.nanmean([r["z"][k] ** 2 for k in keep]))), r["system"]) for r in rows)
                loso[q] = dd[0][1]
            dnn = rows[0]["d"]
            lab = "typical" if dnn <= cal[v]["nn_median"] else ("peripheral" if dnn <= cal[v]["nn_max"] else "outlier")
            best_by_group = {g: next(r for r in rows if r["group"] == g)["system"] for g in ("genre", "code", "name")}
            res[f"{sp}_{v}"] = dict(ranking=C.rnd(rows), nearest=nearest, share_nearest=C.rnd(share_nearest),
                                    tied_with_nearest=within, category=C.rnd(cat), loso_nearest=loso, label=lab,
                                    nn_d=round(dnn, 3), ref_nn_median=cal[v]["nn_median"], ref_nn_max=cal[v]["nn_max"],
                                    best_by_group=best_by_group,
                                    nearest_pooled=min(rows, key=lambda r: r["d_pooled"])["system"])
            print(f"== {sp} {v}: label {lab} d_NN {dnn:.2f} (ref median {cal[v]['nn_median']:.2f}, max {cal[v]['nn_max']:.2f}) "
                  f"cat {C.rnd(cat)} best {best_by_group}", flush=True)
            for r in rows[:8]:
                print(f"   {r['system']:15s} {r['group']:5s} n={r['n']:4d} d={r['d']:.2f} [{r['ci'][0]:.2f},{r['ci'][1]:.2f}] "
                      f"pooled={r['d_pooled']:.2f} nearest-share={share_nearest[r['system']]:.2f}", flush=True)
    json.dump(res, open(C.HERE / "partB_score.json", "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    {"calib": calib, "score": score}[sys.argv[1]]()
