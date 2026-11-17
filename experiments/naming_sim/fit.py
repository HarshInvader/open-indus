"""Fit the generator (gen.py) to each real onomasticon and to Indus dev by simulated minimum distance.

Target for a system = mean statistics of its real list over 30 subsamples of n_fit = min(800, #types) distinct
types. The generator is simulated at the same n_fit with common random numbers (fixed seeds per evaluation,
so the objective is deterministic). Distance = sum over the 9 statistics of ((sim - target)/scale)^2 with a fixed
per-statistic scale (Indus dev bootstrap sd at n=400 / sqrt 2, floor 0.01); NaN target statistics skipped.
Search: 300 random draws -> best 4 -> Nelder-Mead in a transformed (logit/log) space, 250 evals each.
Usage: .venv/bin/python -I experiments/naming_sim/fit.py [system ...|all]   -> fits/<system>.json
"""
import sys, json
from pathlib import Path
from multiprocessing import Pool
import numpy as np
from scipy.optimize import minimize

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import gen, stats as S, names as N

FITS = HERE / "fits"; FITS.mkdir(exist_ok=True)
NFIT = 800
REPS = 3


def indus(split="dev"):
    import cs_data as D
    inc, _ = D.indus_types(split)
    return sorted(inc), set(D.FISH)


def scales():
    f = FITS / "_scales.json"
    if f.exists():
        return json.loads(f.read_text())
    t, c = indus("dev")
    rows = S.bootstrap(t, 400, 200, np.random.default_rng(5), c)
    sc = {k: max(0.01, float(np.nanstd([r[k] for r in rows])) / np.sqrt(2)) for k in S.KEYS}
    f.write_text(json.dumps(sc, indent=1)); return sc


def target(types, cls, rng, B=30):
    n = min(NFIT, len(types))
    rows = S.bootstrap(types, n, B if len(types) > n else 1, rng, cls)
    tg = {k: (float(np.nanmean([r[k] for r in rows])) if not all(np.isnan(r[k]) for r in rows) else np.nan) for k in S.KEYS}
    return tg, n


def _mean(rows):
    return {k: float(np.nanmean([r[k] for r in rows])) if not all(np.isnan(r[k]) for r in rows) else np.nan for k in S.KEYS}


def sim_stats(theta, n, reps=REPS, seed0=0, nnull=10):
    rows = []
    for r in range(reps):
        rng = np.random.default_rng(seed0 + r)
        ty, c = gen.sample(theta, n, rng, V=theta["V"])
        rows.append(S.compute(ty, rng, c, nnull))
    return _mean(rows)


def dist(sim, tg, sc, keys=S.KEYS):
    d = 0.0
    for k in keys:
        if np.isnan(tg[k]):
            continue
        if np.isnan(sim[k]):
            d += 25.0; continue
        d += ((sim[k] - tg[k]) / sc[k]) ** 2
    return d


FREE = gen.PARAMS


def to_x(th, free):
    x = []
    for k in free:
        lo, hi = gen.BOUNDS[k]
        if k in gen.LOG:
            x.append(np.log(th[k]))
        else:
            u = np.clip((th[k] - lo) / (hi - lo), 1e-4, 1 - 1e-4); x.append(np.log(u / (1 - u)))
    return np.array(x)


def to_th(x, free, fixed):
    th = dict(fixed)
    for v, k in zip(x, free):
        lo, hi = gen.BOUNDS[k]
        th[k] = float(np.exp(v)) if k in gen.LOG else float(lo + (hi - lo) / (1 + np.exp(-v)))
    return gen.clip(th)


def fit(types, cls, seed=0, ndraw=400):
    rng = np.random.default_rng(seed)
    sc = scales()
    tg, n = target(types, cls, rng)
    fixed = dict(csh=0.0, kappa=1.0) if np.isnan(tg["cls_self"]) else {}
    free = [k for k in FREE if k not in fixed]
    cand = []
    for i in range(ndraw):
        th = gen.random_theta(rng); th.update(fixed)
        cand.append((dist(sim_stats(th, n, 1, 1000 + i), tg, sc), th))
    cand.sort(key=lambda x: x[0])
    best = (np.inf, None)
    for _, th in cand[:4]:
        f = lambda x: dist(sim_stats(to_th(x, free, fixed), n), tg, sc)
        r = minimize(f, to_x(th, free), method="Nelder-Mead", options=dict(maxfev=250, xatol=1e-3, fatol=0.05))
        if r.fun < best[0]:
            best = (r.fun, to_th(r.x, free, fixed))
    th = best[1]
    # coordinate-grid polish: each parameter over 7 values across its range, 2 sweeps
    fobj = lambda t: dist(sim_stats(t, n), tg, sc)
    cur = fobj(th)
    for sweep in range(2):
        for k in free:
            lo, hi = gen.BOUNDS[k]
            grid = np.exp(np.linspace(np.log(lo), np.log(hi), 7)) if k in gen.LOG else np.linspace(lo, hi, 7)
            for v in grid:
                t2 = gen.clip(dict(th, **{k: float(v)}))
                d = fobj(t2)
                if d < cur:
                    cur, th = d, t2
    fin = sim_stats(th, n, 10, 777, 30)
    return dict(theta=th, n_fit=n, target=tg, fitted_stats=fin, distance=dist(fin, tg, sc), fixed=list(fixed))


def run(name):
    if name == "indus_dev":
        t, c = indus("dev")
    else:
        t, c = N.load(name)
    if len(t) < 60:
        return f"{name} too few types {len(t)}"
    r = fit(t, c, seed=sum(map(ord, name)))
    r["n_types"] = len(t)
    (FITS / f"{name}.json").write_text(json.dumps(r, indent=1, default=float))
    th = r["theta"]
    return (f"{name:16s} n={len(t):5d} d={r['distance']:.1f} " + " ".join(f"{k}={th[k]:.2f}" for k in gen.PARAMS)
            + "\n   target " + str({k: round(v, 3) for k, v in r["target"].items()})
            + "\n   fitted " + str({k: round(v, 3) for k, v in r["fitted_stats"].items()}))


if __name__ == "__main__":
    names = sys.argv[1:] or ["all"]
    if names == ["all"]:
        names = ["indus_dev"] + [k for k in N.SYSTEMS]
    scales()
    with Pool(2) as p:
        for out in p.imap_unordered(run, names):
            print(out, flush=True)
