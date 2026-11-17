"""Step 2 (pre-registered, docs/prereg/naming_sim.md): rank real naming systems by fit to Indus name cores.

Inputs: sims_n800.npz / sims_n423.npz (identify.py: each system's fitted generator at the Indus frequency
profile), Indus dev types (n = 800) and held-out types (n = 423).
  1. Indus statistics: mean over 20 seeds of stats.compute (seeds only affect the pol_ex / cls_self nulls).
  2. Per system: Mahalanobis D^2 of Indus vs the system's simulated distribution on the 6 PRIMARY statistics
     (Ledoit-Wolf covariance); goodness-of-fit p = share of the system's own simulations with D^2 >= Indus D^2.
  3. ABC rejection: pooled reference table standardised; k = 50 nearest simulations to Indus; posterior =
     share per system (equal prior: equal R per system).
  4. Leave-one-statistic-out ABC and GOF.
  5. Same on held-out (n = 423) as validation.
  6. Secondary: 7 statistics incl. cls_self, among systems with a definable lexical class.
Usage: .venv/bin/python -I experiments/naming_sim/score.py -> score.json
"""
import sys, json
from pathlib import Path
import numpy as np
from sklearn.covariance import LedoitWolf

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import stats as S
from identify import PRIMARY, SYSTEMS
from fit import indus

K = 50


def indus_stats(split):
    t, c = indus(split)
    rows = [S.compute(t, np.random.default_rng(s), set(c), 30) for s in range(20)]
    return {k: float(np.nanmean([r[k] for r in rows])) for k in S.KEYS}, len(t)


def load(n):
    d = np.load(HERE / f"sims_n{n}.npz", allow_pickle=True)
    return d["X"], d["y"]


def gof(X, y, obs, keys):
    ix = [S.KEYS.index(k) for k in keys]
    o = np.array([obs[k] for k in keys])
    out = {}
    for s in SYSTEMS:
        Z = X[y == s][:, ix]
        Z = Z[~np.isnan(Z).any(1)]
        if len(Z) < 20:
            continue
        lw = LedoitWolf().fit(Z)
        P = lw.precision_; mu = lw.location_
        d_obs = float((o - mu) @ P @ (o - mu))
        d_sim = np.einsum("ij,jk,ik->i", Z - mu, P, Z - mu)
        z = (o - Z.mean(0)) / Z.std(0)
        out[s] = dict(D2=round(d_obs, 1), p=float((np.sum(d_sim >= d_obs) + 1) / (len(d_sim) + 1)),
                      z={k: round(float(v), 1) for k, v in zip(keys, z)})
    return out


def abc(X, y, obs, keys, k=K):
    ix = [S.KEYS.index(q) for q in keys]
    Z = X[:, ix]; ok = ~np.isnan(Z).any(1); Z, yy = Z[ok], y[ok]
    mu, sd = Z.mean(0), Z.std(0)
    o = (np.array([obs[q] for q in keys]) - mu) / sd
    d = (((Z - mu) / sd - o) ** 2).sum(1)
    nn = yy[np.argsort(d)[:k]]
    post = {s: float(np.mean(nn == s)) for s in sorted(set(yy))}
    # how far is Indus from its nearest simulations, relative to typical sim-to-nearest distances
    return dict(posterior={s: v for s, v in sorted(post.items(), key=lambda x: -x[1]) if v > 0},
                nn_dist_indus=float(np.sqrt(np.sort(d)[0])),
                nn_dist_median_sim=float(np.median([np.sqrt(np.sort((((Z - mu) / sd - (Z[i] - mu) / sd) ** 2).sum(1))[1])
                                                    for i in np.random.default_rng(0).choice(len(Z), 200, replace=False)])))


def block(n, obs):
    X, y = load(n)
    r = dict(indus=obs, gof=gof(X, y, obs, PRIMARY), abc=abc(X, y, obs, PRIMARY))
    r["loso"] = {}
    for k in PRIMARY:
        keys = [q for q in PRIMARY if q != k]
        g = gof(X, y, obs, keys)
        best = max(g, key=lambda s: g[s]["p"])
        a = abc(X, y, obs, keys)
        r["loso"][k] = dict(abc_top=list(a["posterior"].items())[:3], best_gof=best, best_gof_p=g[best]["p"],
                            n_fit_005=int(sum(v["p"] >= 0.05 for v in g.values())))
    cls_sys = [s for s in SYSTEMS if not np.isnan(X[y == s, S.KEYS.index("cls_self")]).all()]
    m = np.isin(y, cls_sys)
    r["with_class"] = dict(systems=cls_sys, gof=gof(X[m], y[m], obs, PRIMARY + ["cls_self"]),
                           abc=abc(X[m], y[m], obs, PRIMARY + ["cls_self"]))
    return r


if __name__ == "__main__":
    out = {}
    for split, n in (("dev", 800), ("heldout", 423)):
        obs, nt = indus_stats(split)
        assert nt == n, (split, nt)
        out[split] = block(n, obs)
        b = out[split]
        print(f"== {split} (n={n}) Indus:", {k: round(v, 3) for k, v in obs.items()})
        for s, g in sorted(b["gof"].items(), key=lambda x: x[1]["D2"]):
            print(f"  {s:16s} D2={g['D2']:8.1f} p={g['p']:.3f} z={g['z']}")
        print("  ABC posterior:", b["abc"]["posterior"], "nn dist Indus", round(b["abc"]["nn_dist_indus"], 2),
              "vs sims", round(b["abc"]["nn_dist_median_sim"], 2))
        for k, v in b["loso"].items():
            print(f"  LOSO -{k:12s} abc {v['abc_top']} best gof {v['best_gof']} p={v['best_gof_p']:.3f} n_fit {v['n_fit_005']}")
        print("  with class:", {s: (g["D2"], round(g["p"], 3)) for s, g in b["with_class"]["gof"].items()},
              b["with_class"]["abc"]["posterior"])
    json.dump(out, open(HERE / "score.json", "w"), indent=1)
