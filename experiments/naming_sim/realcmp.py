"""Model-free comparison of real name lists (and Indus) at matched sample size.

Pair distance d(A, B): for n = min(nA, nB, NCAP), mean statistics of A and of B over B_REP subsamples of n
distinct types each; d = sqrt(mean over the 6 PRIMARY statistics of ((mA - mB) / s_k)^2), where s_k is the
across-system SD of the real-list means at NCAP (fixed once in calib, real lists only, Indus excluded).
NaN statistics (e.g. no one-element names -> standalone undefined) are skipped for that pair.

  calib : real lists only. (i) leave-one-out nearest neighbour: does each list's nearest list belong to its
          family (Germanic: old_english, old_high_german, old_norse, germanic_pooled excluded; Chinese: given/full;
          South Asian: sanskrit, sangam)? (ii) distribution of nearest-neighbour distances among real lists.
  indus : (pre-registered, docs/prereg/naming_sim.md) Indus dev (NCAP = 800) and held-out (NCAP = 423) vs every
          list; rank; nearest-neighbour distance vs the real-list NN distribution.
Usage: .venv/bin/python -I experiments/naming_sim/realcmp.py calib|indus
"""
import sys, json
from pathlib import Path
from itertools import combinations
from multiprocessing import Pool
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import stats as S, names as N

PRIMARY = ["len1", "standalone", "both_orders", "hfi", "pol_ex", "both_pos"]
LISTS = ["old_english", "old_high_german", "old_norse", "greek", "sanskrit", "egyptian", "ur3", "chinese_given",
         "chinese_full", "plains", "sangam"]
FAMILY = {"old_english": "germanic", "old_high_german": "germanic", "old_norse": "germanic",
          "chinese_given": "chinese", "chinese_full": "chinese", "sanskrit": "south_asian", "sangam": "south_asian"}
B_REP = 40
_cache = {}


def types_of(nm):
    if nm not in _cache:
        if nm.startswith("indus_"):
            from fit import indus
            _cache[nm] = indus(nm.split("_", 1)[1])
        else:
            _cache[nm] = N.load(nm)
    return _cache[nm]


def mean_stats(nm, n, seed=0):
    t, c = types_of(nm)
    n = min(n, len(t))
    rows = S.bootstrap(t, n, B_REP if len(t) > n else 1, np.random.default_rng(seed), c)
    return {k: float(np.nanmean([r[k] for r in rows])) if not all(np.isnan(r[k]) for r in rows) else np.nan for k in S.KEYS}


def _ms(a):
    return a, mean_stats(*a)


def distance(ma, mb, s):
    z = [((ma[k] - mb[k]) / s[k]) ** 2 for k in PRIMARY if not (np.isnan(ma[k]) or np.isnan(mb[k]))]
    return float(np.sqrt(np.mean(z))), len(z)


def scales(ncap=800):
    f = HERE / "realcmp_scales.json"
    if f.exists():
        return json.loads(f.read_text())
    with Pool(2) as p:
        ms = {a[0]: m for a, m in p.map(_ms, [(nm, ncap) for nm in LISTS])}
    s = {k: float(np.nanstd([ms[nm][k] for nm in LISTS])) for k in PRIMARY}
    f.write_text(json.dumps(dict(scales=s, means_at_cap=ms), indent=1))
    return json.loads(f.read_text())


def size(nm):
    return len(types_of(nm)[0])


def pairwise(names_a, names_b, ncap):
    jobs = set()
    for a in names_a:
        for b in names_b:
            if a != b:
                n = min(size(a), size(b), ncap)
                jobs.add((a, n)); jobs.add((b, n))
    with Pool(2) as p:
        ms = dict(p.map(_ms, sorted(jobs)))
    return ms


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "calib"
    sc = scales()["scales"]
    if mode == "calib":
        ms = pairwise(LISTS, LISTS, 800)
        D = {}
        for a, b in combinations(LISTS, 2):
            n = min(size(a), size(b), 800)
            D[(a, b)] = D[(b, a)] = distance(ms[(a, n)], ms[(b, n)], sc)[0]
        out = {"scales": sc, "nn": {}, "matrix": {f"{a}|{b}": round(v, 3) for (a, b), v in D.items() if a < b}}
        hits = tot = 0
        for a in LISTS:
            others = sorted([(D[(a, b)], b) for b in LISTS if b != a])
            nn = others[0]
            fam = FAMILY.get(a)
            ok = fam is not None and FAMILY.get(nn[1]) == fam
            if fam:
                tot += 1; hits += ok
            rank_rel = next((i + 1 for i, (_, b) in enumerate(others) if fam and FAMILY.get(b) == fam), None)
            out["nn"][a] = dict(nearest=nn[1], d=round(nn[0], 3), family=fam, nearest_is_family=bool(ok),
                                rank_of_first_relative=rank_rel, order=[(b, round(d, 2)) for d, b in others[:4]])
            print(f"{a:16s} nearest {nn[1]:16s} d={nn[0]:.2f}  family {fam}  first relative at rank {rank_rel}  "
                  f"next: {[(b, round(d, 2)) for d, b in others[1:4]]}")
        nnd = [v["d"] for v in out["nn"].values()]
        out["family_nn_hits"] = [hits, tot]
        out["nn_dist"] = dict(min=min(nnd), median=float(np.median(nnd)), max=max(nnd))
        # chance rate of a family hit: for each family member, share of other lists in its family
        ch = np.mean([sum(FAMILY.get(b) == FAMILY[a] for b in LISTS if b != a) / (len(LISTS) - 1) for a in LISTS if a in FAMILY])
        out["family_hit_chance"] = float(ch)
        print("family NN hits", hits, "/", tot, "chance per list", round(ch, 3), "NN distances", out["nn_dist"])
        json.dump(out, open(HERE / "realcmp_calib.json", "w"), indent=1)
    else:
        out = {}
        calib = json.load(open(HERE / "realcmp_calib.json"))
        for split, cap in (("dev", 800), ("heldout", 423)):
            ind = f"indus_{split}"
            ms = pairwise([ind], LISTS, cap)
            rows = []
            for b in LISTS:
                n = min(size(ind), size(b), cap)
                d, k = distance(ms[(ind, n)], ms[(b, n)], sc)
                z = {q: round((ms[(ind, n)][q] - ms[(b, n)][q]) / sc[q], 2) for q in PRIMARY}
                rows.append(dict(system=b, n=n, d=round(d, 3), n_stats=k, z=z,
                                 indus={q: round(ms[(ind, n)][q], 3) for q in PRIMARY},
                                 ref={q: round(ms[(b, n)][q], 3) for q in PRIMARY}))
            rows.sort(key=lambda r: r["d"])
            # leave-one-statistic-out nearest system
            loso = {}
            for q in PRIMARY:
                keep = [x for x in PRIMARY if x != q]
                dd = []
                for r in rows:
                    zz = [r["z"][x] ** 2 for x in keep if not np.isnan(r["z"][x])]
                    dd.append((float(np.sqrt(np.mean(zz))), r["system"]))
                loso[q] = sorted(dd)[0][1]
            out[split] = dict(ranking=rows, loso_nearest=loso, nn_d=rows[0]["d"], real_nn_max=calib["nn_dist"]["max"],
                              real_nn_median=calib["nn_dist"]["median"])
            print(f"== Indus {split}")
            for r in rows:
                print(f"  {r['system']:16s} n={r['n']:4d} d={r['d']:.2f} z={r['z']}")
            print("  LOSO nearest:", loso, " Indus NN d", rows[0]["d"], "real NN max", calib["nn_dist"]["max"])
        json.dump(out, open(HERE / "realcmp_indus.json", "w"), indent=1)
