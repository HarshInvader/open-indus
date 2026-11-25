"""split_witness step 2: planted-power minimum and minimum achievable p. Synthetic splits only.

No real split position is read here, and no cohesion value is computed at any real split.
The pool is ICIT records with no '|' and no '#', complete, >= 2 signs (distinct sequences).

Planted units (two kinds of "true boundary"):
  C  concatenation: text A + text B, two pool texts from different families in the same fold,
     each >= 2 signs, total <= 14. The true boundary is the join (len A). Model-independent.
  A  model-best: a pool text of >= 3 signs; the true boundary is its highest-ESR junction
     (ties broken at random), as in line_breaks power.py mode A.
With probability f a unit's split sits at the true boundary, otherwise it is uniform over the
text's junctions. Each unit is scored by the fold model that excludes its families.

Detection rules reported:
  P   one-sided Monte-Carlo p <= 0.01 under Null 1 (uniform).
  BAR mean percentile >= 0.60 and p <= 0.01 under Null 1 (the Null-1 half of the bar).
Minimum n = smallest n on the grid with power >= 0.80 at f = 0.20 under rule P in BOTH modes,
and false-alarm rate (f = 0) <= 0.05.

Also: minimum achievable p under Null 1 and under Null 2 (median line capacity), estimated
on pseudo-units drawn from the pool, not on real splits.

Run: .venv/bin/python -I experiments/split_witness/power.py
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import sw_lib as S  # noqa: E402

rng = np.random.default_rng(20261125)
GRID = [20, 30, 40, 60, 80, 100, 120, 150, 200, 300]
FS = [0.0, 0.2, 0.3, 0.4]
REPS = 300
NSIM = 2000

fam = S.families()
models = S.fold_models(fam)

pool, seen = [], set()
for t in S.icit_texts():
    s = t["seq"]
    if "|" in s or "#" in s or not t["complete"] or len(s) < 2:
        continue
    k = S.key(s)
    if k in seen:
        continue
    seen.add(k)
    fid = fam[k]
    pool.append(dict(signs=list(s), fid=fid, fold=S.fold_of(fid), type=t["type"],
                     width=S.fnum(t["width_mm"])))
by_fold = defaultdict(list)
for i, p in enumerate(pool):
    by_fold[p["fold"]].append(i)

# --- unit tables: (ranks, true boundary k) ---
def make_C(n_units):
    out = []
    while len(out) < n_units:
        a = pool[int(rng.integers(len(pool)))]
        cand = by_fold[a["fold"]]
        b = pool[cand[int(rng.integers(len(cand)))]]
        if a["fid"] == b["fid"] or len(a["signs"]) + len(b["signs"]) > 14:
            continue
        sg = a["signs"] + b["signs"]
        out.append((S.junction_ranks(models[a["fold"]], sg), len(a["signs"])))
    return out


A_pool = [p for p in pool if len(p["signs"]) >= 3]


def make_A(n_units):
    out = []
    for _ in range(n_units):
        p = A_pool[int(rng.integers(len(A_pool)))]
        r = S.junction_ranks(models[p["fold"]], p["signs"])
        best = np.flatnonzero(r == r.max())
        out.append((r, int(rng.choice(best)) + 1))
    return out


BANK = {"C": make_C(6000), "A": make_A(6000)}


def one_run(mode, n, f):
    idx = rng.integers(0, len(BANK[mode]), n)
    units = [BANK[mode][i] for i in idx]
    rk = [u[0] for u in units]
    ks = []
    for r, kt in units:
        ks.append(kt if rng.random() < f else int(rng.integers(1, len(r) + 1)))
    obs = S.stat(rk, ks)
    p = S.p_uniform(rk, obs, rng, NSIM)
    return obs, p


res = dict(pool_texts=len(pool), n_families=len(set(fam.values())),
           largest_family=max(list(fam.values()).count(x) for x in set(fam.values())),
           reps=REPS, nsim=NSIM, power={})
for mode in ["C", "A"]:
    # how strong is the planted boundary? mean percentile at the true boundary
    res[f"mean_percentile_at_true_boundary_{mode}"] = float(np.mean([u[0][u[1] - 1] for u in BANK[mode]]))
    for n in GRID:
        for f in FS:
            hitP = hitB = 0
            means = []
            for _ in range(REPS):
                obs, p = one_run(mode, n, f)
                means.append(obs)
                hitP += p <= 0.01
                hitB += (p <= 0.01) and (obs >= 0.60)
            res["power"][f"{mode}_n{n}_f{f}"] = dict(P=hitP / REPS, BAR=hitB / REPS,
                                                    mean_stat=float(np.mean(means)))
            print(mode, n, f, hitP / REPS, hitB / REPS, round(float(np.mean(means)), 3), flush=True)


def n_min(rule, f=0.2):
    for n in GRID:
        ok = all(res["power"][f"{m}_n{n}_{'f' + str(f)}"][rule] >= 0.80 for m in ["C", "A"])
        fa = all(res["power"][f"{m}_n{n}_f0.0"][rule] <= 0.05 for m in ["C", "A"])
        if ok and fa:
            return n
    return None


res["n_min_rule_P_f0.2"] = n_min("P")
res["n_min_rule_BAR_f0.2"] = n_min("BAR")
res["n_min_rule_BAR_f0.3"] = n_min("BAR", 0.3)

# --- minimum achievable p, on pseudo-units from the pool (no real splits) ---
# Null 1: the smallest p a set of units can reach is P(null stat >= the largest attainable stat)
# = prod over units of (share of junctions tied at that unit's top rank).
def log10_minp_uniform(units):
    s = 0.0
    for r, _ in units:
        s += np.log10(np.mean(r == r.max()))
    return s


# Null 2 (median capacity): reference = pool texts of the same type, width within 2 mm,
# leaving the unit itself out, >= 10 references. Capacity c = median length. Placement
# k = clip(c, 1, n-1); a half-integer median gives two placements (floor, ceil) at 1/2 each.
# The smallest p = prod over units of the largest placement probability (1 or 1/2).
ref = defaultdict(list)
for p in pool:
    if p["width"] > 5:
        ref[p["type"]].append((p["width"], len(p["signs"])))


def placements_median(typ, width, n, self_len=None):
    rows = [L for w, L in ref.get(typ, []) if abs(w - width) <= 2.0]
    if self_len is not None and self_len in rows:
        rows.remove(self_len)
    if len(rows) < 10:
        return None
    c = float(np.median(rows))
    ks = {int(np.clip(np.floor(c), 1, n - 1)), int(np.clip(np.ceil(c), 1, n - 1))}
    return ks


def placements_dist(typ, width, n, self_len=None):
    """Null 2D (not the bar's null; reported for information): capacity drawn from the
    empirical distribution of reference lengths -> distinct clipped placements with probs."""
    rows = [L for w, L in ref.get(typ, []) if abs(w - width) <= 2.0]
    if self_len is not None and self_len in rows:
        rows.remove(self_len)
    if len(rows) < 10:
        return None
    ks = np.clip(np.array(rows), 1, n - 1)
    vals, cnt = np.unique(ks, return_counts=True)
    return cnt / cnt.sum()


pseudo = [p for p in pool if len(p["signs"]) >= 3]
n_def = 0
lg_med, lg_dist, k_med = [], [], []
for p in pseudo:
    n = len(p["signs"])
    if p["width"] <= 5:
        continue
    pm = placements_median(p["type"], p["width"], n, n)
    if pm is None:
        continue
    n_def += 1
    k_med.append(len(pm))
    lg_med.append(np.log10(1.0 / len(pm)))
    pd = placements_dist(p["type"], p["width"], n, n)
    lg_dist.append(np.log10(pd.max()))
k_med = np.array(k_med)
lg_unif = [np.log10(np.mean(r == r.max())) for r, _ in BANK["A"][:3000]]
res["minimum_achievable_p"] = dict(
    pseudo_units_with_capacity=n_def, pseudo_units_total=len(pseudo),
    share_with_capacity_defined=n_def / len(pseudo),
    null2_median_share_units_with_2_placements=float(np.mean(k_med == 2)),
    null2_median_share_units_with_1_placement=float(np.mean(k_med == 1)),
    null2_median_mean_log10_minp_per_unit=float(np.mean(lg_med)),
    null2_dist_mean_log10_minp_per_unit=float(np.mean(lg_dist)),
    null1_mean_log10_minp_per_unit=float(np.mean(lg_unif)),
)
for n in [29, 60, 100, 150]:
    m = res["minimum_achievable_p"]
    # with the median null each unit has 1 or 2 placements; expected count with 2 placements
    res["minimum_achievable_p"][f"n{n}"] = dict(
        null1_log10_minp=n * m["null1_mean_log10_minp_per_unit"],
        null2_median_expected_units_with_2_placements=n * m["share_with_capacity_defined"]
        * m["null2_median_share_units_with_2_placements"],
        null2_median_log10_minp_expected=n * m["share_with_capacity_defined"]
        * m["null2_median_mean_log10_minp_per_unit"],
        null2_dist_log10_minp_expected=n * m["share_with_capacity_defined"]
        * m["null2_dist_mean_log10_minp_per_unit"],
    )
json.dump(res, open(HERE / "power.json", "w"), indent=1)
print(json.dumps({k: v for k, v in res.items() if k != "power"}, indent=1))
