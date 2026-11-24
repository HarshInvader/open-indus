"""Shape-only power calculator for the sizing census (prereg docs/prereg/sizing_census.md, sealed).

One entry: power(family, shape, effect, alpha) for families A1, A2a, A2b, A3 and B as the prereg defines them.
Inputs are shapes only (counts, class sizes, marginal prevalences, m, alpha, the plant's definition); never a result.
This file never opens sealed.json, and never opens anchor_ceiling truth labels.

Run from the repo root (NWORK workers, default 4; the prereg asks for `nice -n 20`):
  nice -n 20 .venv/bin/python -I experiments/sizing_census/calc.py kill      # seed 20261125 -> kill.json
  nice -n 20 .venv/bin/python -I experiments/sizing_census/calc.py census    # seed 20261126 -> census.csv, census.json
  nice -n 20 .venv/bin/python -I experiments/sizing_census/calc.py curve     # seed 20261127 -> curve.json, u_rows.csv
  .venv/bin/python -I experiments/sizing_census/calc.py selftest             # made-up shapes only; writes nothing
Shapes are read from shapes.json (written by shapes.py). Census gates read adoption.json ({"adopted": [...]},
written after compare.py) if it exists; otherwise the gate column says "pending adoption".

Code-level definitions fixed with this file's hash:
- A1: n counts rows; p0 = c_g / n; target count in A = ceil(n_A (p0 + delta)) (for an odds-ratio effect: the smallest
  count whose A-vs-rest odds ratio reaches the target); feasible iff target <= min(n_A, c_g); p_B = (c_g - target)/n_B.
  Test one-sided at alpha / m: the pooled two-proportion z (normal-approximation power, closed form) when every
  null-expected cell is >= 5, else exact one-sided Fisher on 2,000 simulated tables (x_A ~ Bin(n_A, p_A),
  x_B ~ Bin(n_B, p_B)). Power = mean over feasible candidate signs (uniform draw); a rung with feasible share
  < 0.75 is not counted. Shapes flagged bound="upper" (marginal not in the repo) take n_A = n // 2 if unknown and
  the power-maximising c_g; their power is an upper bound.
- A2a: 2,000 samples x ~ Bin(n, p1); pass = exact binomial upper p < alpha / m and x / n >= bar (if any) and n >= min_n.
- A2b: 2,000 samples; per stratum reference positives ~ Bin(ref_n, r), target positives ~ Bin(n_t, min(1, R r));
  target stratum sizes multinomial on the shares (or fixed counts when the shape lists target_n); reference sizes
  fixed (ref_fixed) or multinomial. p = exact stratified hypergeometric (harp_pack score.strat_hyper), tail as the
  route's test; ratio bar on O/E from the drawn reference rates ("oe", m342/C6) or harp_pack's smoothed RR ("rr").
- A3: 2,000 draws x 999 permutations; Gaussian copula at latent rho; value margin the route's own (ties kept);
  rows = n / (1 - dup_share), duplicate rows join random units, share the unit's value, and the unit's measure is
  the median of its rows; units dealt to n_strata equal strata; ranks within strata (score.within_ranks);
  p two-sided, values permuted within stratum. A draw with fewer than min_pos positive values, or n < min_n, fails.
- B: 2,000 simulated word sets (anchor_ceiling v2 supervised gate, rung A3). Words take (dev, held) document counts
  from the shape's pool / rest lists; fields take their size and pool count; a set is redrawn until every field has
  >= 3 scoreable words (v2 rule). Each draw: documents get S, K, P from the base rates; a word's documents are drawn
  without replacement with probability proportional to a words-per-document value resampled from the shape; the
  picture plant is anchor_ceiling kill.planted_pics (unchanged); profiles core2.profiles (unchanged); dev gate =
  leave-one-word-out nearest true-field centroid; held = true-field dev centroids, core.assign (cosine). Scoring is
  core.score_draw / core.supervised_control, re-implemented here with the permutation null vectorised (same rng
  stream, same rules; `selftest` checks agreement against the core functions). Recovered = passed in >= need draws.
- MDE: coarse grid then bisection (delta to 0.005, rho to 0.01, R to 0.01, A2a rate to 0.005, OR to 0.1).
  n needed: smallest scale k (all counts x k; for a fixed reference corpus only the target sample) with power >= 0.8,
  searched on {1/64 .. 64} then bisected on the integer count.
"""
import csv, json, math, os, sys, time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path
import numpy as np
from scipy.stats import norm, hypergeom, binom
from scipy.optimize import linear_sum_assignment
from sklearn.metrics import adjusted_rand_score

HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "experiments/anchor_ceiling"))
import core as K            # noqa: E402  anchor_ceiling core (unchanged)
import core2 as C2          # noqa: E402  anchor_ceiling v2 core (unchanged)
import kill as K1           # noqa: E402  anchor_ceiling v1 kill: planted_pics (unchanged)
import experiments.harp_pack.score as HS  # noqa: E402  strat_hyper, within_ranks, _rr (unchanged)

NWORK = int(os.environ.get("NWORK", "4"))
SEED_KILL, SEED_CENSUS, SEED_CURVE = 20261125, 20261126, 20261127
NSIM = 2000          # A1 Fisher tables, A2 samples, A3 draws, B word sets
NPERM_A3 = 999
TARGET = 0.8
FEAS_MIN = 0.75
LB_DELTA, LB_NAMES = 0.23, (0.07, 0.11)
CURVE_D = (2, 3, 5, 8, 12, 20)
CURVE_PROP = [("place", 25), ("admin", 14), ("land", 8), ("occupation", 8), ("person", 5)]
CURVE_NPLANT, CURVE_TEST = 20, 0.30
_POOL = None


def _rng(*k):
    return np.random.default_rng([int(x) for x in k])


# =================================================================== A1
def _a1_target(n, nA, c, kind, val):
    nB = n - nA
    if kind == "delta":
        t = math.ceil(nA * (c / n + val) - 1e-9)
    else:                                                     # odds ratio
        t = None
        for x in range(0, min(nA, c) + 1):
            a, b = x, c - x
            if b > nB: continue
            num, den = a * (nB - b), (nA - a) * b
            orr = (math.inf if num > 0 else 0.0) if den == 0 else num / den
            if orr >= val - 1e-12: t = x; break
        if t is None: return None
    if t > min(nA, c) or c - t > nB or t < 0: return None
    return t


def a1_sign_power(n, nA, c, kind, val, a_t, rng, nsim=NSIM):
    """power for one tie sign; None if infeasible. Returns (power, realised effect, test used)."""
    t = _a1_target(n, nA, c, kind, val)
    if t is None: return None
    nB = n - nA; pA = t / nA; pB = (c - t) / nB if nB else 0.0
    real = pA - c / n
    exp_min = min(nA * c / n, nA * (n - c) / n, nB * c / n, nB * (n - c) / n)
    if exp_min < 5:
        xA = rng.binomial(nA, pA, nsim); xB = rng.binomial(nB, pB, nsim)
        p = hypergeom.sf(xA - 1, n, xA + xB, nA)
        return float(np.mean(p < a_t)), real, "fisher"
    z = norm.ppf(1 - a_t); pbar = c / n
    se0 = math.sqrt(pbar * (1 - pbar) * (1 / nA + 1 / nB)); se1 = math.sqrt(pA * (1 - pA) / nA + pB * (1 - pB) / nB)
    d = pA - pB
    if se1 == 0: return (1.0 if d > z * se0 else 0.0), real, "z"
    return float(norm.cdf((d - z * se0) / se1)), real, "z"


def power_a1(shape, effect, alpha, seed, nsim=NSIM):
    kind, val = effect
    n = int(shape["n"]); m = int(shape.get("m") or 1); a_t = alpha / m
    upper = shape.get("bound") == "upper"
    nA = shape.get("n_A"); nA = n // 2 if nA is None else int(nA)
    if n <= 1 or nA <= 0 or nA >= n:
        return dict(power=0.0, feasible_share=0.0, counted=False, note="degenerate shape")
    cs = list(range(1, n)) if (upper and not shape.get("c_g")) else [int(c) for c in shape["c_g"]]
    res = []
    for i, c in enumerate(cs):
        r = a1_sign_power(n, nA, c, kind, val, a_t, _rng(seed, i), nsim)
        res.append(r)
    feas = [r for r in res if r is not None]
    if upper:
        if not feas: return dict(power=0.0, feasible_share=0.0, counted=False, bound="upper")
        j = max(range(len(res)), key=lambda i: -1 if res[i] is None else res[i][0])
        return dict(power=res[j][0], feasible_share=1.0, counted=True, bound="upper", best_c_g=cs[j],
                    realised=res[j][1], n_A=nA)
    share = len(feas) / len(cs) if cs else 0.0
    if not feas: return dict(power=0.0, feasible_share=0.0, counted=False)
    return dict(power=float(np.mean([r[0] for r in feas])), feasible_share=share, counted=share >= FEAS_MIN,
                realised=float(np.mean([r[1] for r in feas])), n_feasible=len(feas), n_candidates=len(cs),
                fisher_share=float(np.mean([r[2] == "fisher" for r in feas])))


# =================================================================== A2
def power_a2a(shape, p1, alpha, seed, nsim=NSIM):
    n = int(shape["n"]); m = int(shape.get("m") or 1)
    if n <= 0 or n < int(shape.get("min_n") or 0):
        return dict(power=0.0, note=f"n = {n} below minimum n {shape.get('min_n')}")
    x = _rng(seed).binomial(n, min(1.0, p1), nsim)
    ok = binom.sf(x - 1, n, shape["p0"]) < alpha / m
    if shape.get("bar") is not None: ok &= x / n >= shape["bar"] - 1e-12
    return dict(power=float(ok.mean()))


def power_a2b(shape, R, alpha, seed, nsim=NSIM):
    rng = _rng(seed); m = int(shape.get("m") or 1); a_t = alpha / m
    st = shape["strata"]; n = int(shape["n"])
    rate = np.array([s["ref_rate"] for s in st])
    fixed_t = all("target_n" in s for s in st)
    if fixed_t:
        base = np.array([s["target_n"] for s in st], float); tot = base.sum()
        nt_fixed = np.round(base * (n / tot)).astype(int) if tot else base.astype(int)
    else:
        sh = np.array([s["target_share"] for s in st], float); sh /= sh.sum()
    if shape.get("ref_fixed", True):
        rn_fixed = np.array([s["ref_n"] for s in st], int)
    else:
        rsh = np.array([s["ref_share"] for s in st], float); rsh /= rsh.sum()
        ref_tot = int(round(shape["ref_n_total"] * shape.get("_ref_scale", 1.0)))
    hits = 0
    for _ in range(nsim):
        nt = nt_fixed if fixed_t else rng.multinomial(n, sh)
        rn = rn_fixed if shape.get("ref_fixed", True) else rng.multinomial(ref_tot, rsh)
        s1 = rng.binomial(rn, rate); p1 = rng.binomial(nt, np.minimum(1.0, R * rate))
        A, _, pu, pl = HS.strat_hyper([(a + b, c + d, b, d) for a, b, c, d in zip(rn, nt, s1, p1)])
        p = pu if shape["tail"] == "upper" else pl
        if shape["ratio"] == "oe":
            E = sum(b * c / a for a, b, c in zip(rn, nt, s1) if a > 0)
            eff = A / E if E > 0 else float("nan")
        else:
            eff = HS._rr(int(p1.sum()), int(nt.sum()), int(s1.sum()), int(rn.sum()))
        bar_ok = (eff >= shape["bar"]) if shape["tail"] == "upper" else (eff <= shape["bar"])
        hits += bool(p < a_t and bar_ok)
    return dict(power=hits / nsim)


# =================================================================== A3
def _a3_draw(shape, rho, a_t, rng):
    n = int(shape["n"])
    vals = np.array([float(v) for v in shape["v_margin"]]); pr = np.array(list(shape["v_margin"].values()), float)
    order = np.argsort(vals); vals, pr = vals[order], pr[order]; cum = np.cumsum(pr) / pr.sum()
    d = float(shape.get("dup_share") or 0.0)
    extra = int(round(n * d / (1 - d))) if d > 0 else 0
    unit = np.concatenate([np.arange(n), rng.integers(0, n, extra)]) if extra else np.arange(n)
    z1 = rng.standard_normal(n)
    z2 = rho * z1[unit] + math.sqrt(1 - rho * rho) * rng.standard_normal(len(unit))
    meas = z2[:n].copy()
    if extra:
        for u in np.unique(unit[n:]):
            meas[u] = float(np.median(z2[unit == u]))
    V = vals[np.minimum(np.searchsorted(cum, norm.cdf(z1)), len(vals) - 1)]
    if (V > 0).sum() < int(shape.get("min_pos") or 0): return False
    S = max(1, min(int(shape.get("n_strata") or 1), n))
    lab = rng.permutation(np.arange(n) % S)
    groups = [np.where(lab == s)[0] for s in range(S)]
    rm = HS.within_ranks(meas, groups); rv = HS.within_ranks(V, groups)
    if rv.std() == 0 or rm.std() == 0: return False
    obs = float(np.corrcoef(rv, rm)[0, 1])
    perm = np.empty((NPERM_A3, n))
    for g in groups:
        perm[:, g] = rng.permuted(np.tile(rv[g], (NPERM_A3, 1)), axis=1)
    pc = perm - perm.mean(1, keepdims=True); mc = rm - rm.mean()
    null = (pc @ mc) / (np.sqrt((pc * pc).sum(1)) * math.sqrt((mc * mc).sum()))
    p = (1 + np.sum(np.abs(null) >= abs(obs) - 1e-12)) / (1 + NPERM_A3)
    return bool(p < a_t)


def _a3_chunk(a):
    shape, rho, a_t, seed, lo, hi = a
    return sum(_a3_draw(shape, rho, a_t, _rng(seed, j)) for j in range(lo, hi))


def power_a3(shape, rho, alpha, seed, nsim=NSIM):
    n = int(shape["n"]); a_t = alpha / int(shape.get("m") or 1)
    if n < max(3, int(shape.get("min_n") or 0)):
        return dict(power=0.0, note=f"n = {n} below minimum n {shape.get('min_n')}")
    step = max(1, nsim // (4 * NWORK))
    jobs = [(shape, rho, a_t, seed, lo, min(nsim, lo + step)) for lo in range(0, nsim, step)]
    hits = sum(_POOL.map(_a3_chunk, jobs) if _POOL else map(_a3_chunk, jobs))
    return dict(power=hits / nsim)


# =================================================================== B: v2 scoring with a vectorised null
def _perms(truth, groups, nperm, rng):
    out = np.empty((nperm, len(truth)), dtype=truth.dtype)
    for k in range(nperm):
        t = truth.copy()
        for g in groups: t[g] = truth[rng.permutation(g)]
        out[k] = t
    return out


def score_draw_fast(truth_map, fields_all, held_words, pred_held, cd, nperm, rng):
    """core.score_draw with the same rules and rng stream; the F1 null is batched (ARI null not needed here)."""
    ws = [w for w in held_words if w in truth_map]
    idx = [held_words.index(w) for w in ws]
    truth = [truth_map[w] for w in ws]; pred = np.asarray(pred_held)[idx]
    nheld = Counter(truth)
    fields = [f for f in fields_all if nheld[f] >= 3]
    keep = [i for i, t in enumerate(truth) if t in fields]
    truth = [truth[i] for i in keep]; pred = pred[keep]; ws = [ws[i] for i in keep]
    if len(fields) < 2:
        return dict(fields=fields, n=len(ws), f1={}, passed={}, ari=float("nan"))
    obs = K.field_f1(truth, pred, fields); ari = adjusted_rand_score(truth, pred)
    ta = np.asarray(truth); bins = K.freq_bins(ws, cd)
    groups = [np.where(bins == b)[0] for b in sorted(set(bins))]
    T = _perms(ta, groups, nperm, rng)
    fi = {f: i for i, f in enumerate(fields)}; cl = sorted(set(pred)); ci = {c: j for j, c in enumerate(cl)}
    Ti = np.vectorize(fi.get)(T); pj = np.array([ci[c] for c in pred])
    OT = np.zeros((nperm, len(truth), len(fields))); np.put_along_axis(OT, Ti[:, :, None], 1.0, axis=2)
    OP = np.zeros((len(truth), len(cl))); OP[np.arange(len(truth)), pj] = 1.0
    Cm = np.einsum("knf,nc->kfc", OT, OP)
    nt = np.array([(ta == f).sum() for f in fields]); pc = OP.sum(0)
    M = np.where(Cm > 0, 2 * Cm / (nt[:, None] + pc[None, :]), 0.0)
    nf1 = {f: np.zeros(nperm) for f in fields}
    for k in range(nperm):
        r, c = linear_sum_assignment(-M[k])
        for i, j in zip(r, c): nf1[fields[i]][k] = M[k, i, j]
    passed = {f: bool(obs[f] >= 0.5 and obs[f] > np.percentile(nf1[f], 95)) for f in fields}
    return dict(fields=fields, n=len(ws), f1=obs, passed=passed, ari=float(ari))


def _loo_predict(X, L, F):
    """batched leave-one-word-out nearest field centroid (cosine); L: (B, n) field indices -> (B, n)."""
    B, n = L.shape
    OH = np.zeros((B, n, F)); np.put_along_axis(OH, L[:, :, None], 1.0, axis=2)
    S = np.einsum("bnf,nd->bfd", OH, X); N = OH.sum(1)
    G = np.einsum("nd,bfd->bnf", X, S); q = (X * X).sum(1)[None, :, None]
    sq = (S * S).sum(2)[:, None, :]
    dot = G - OH * q
    nrm2 = sq - OH * (2 * G - q)
    nrm = np.sqrt(np.maximum(nrm2, 0)); nrm[nrm < 1e-12] = 1.0
    sim = dot / nrm
    sim[(N[:, None, :] - OH) <= 0] = -np.inf
    return np.argmax(sim, axis=2)


def supervised_fast(el, P, truth_map, fields_all, cd, nperm, rng):
    """core.supervised_control with the same rules and rng stream; predictions batched over permutations."""
    ws = [w for w in el if w in truth_map]
    if not ws: return {}
    X = K._unit(P[[el.index(w) for w in ws]]); t = np.array([truth_map[w] for w in ws])
    fields = [f for f in fields_all if (t == f).sum() >= 3]
    keep = np.isin(t, fields); X, t = X[keep], t[keep]; ws = [w for w, k in zip(ws, keep) if k]
    if not fields: return dict(fields=[], f1={}, passed={})
    fi = {f: i for i, f in enumerate(fields)}; ti = np.array([fi[x] for x in t])
    pred = _loo_predict(X, ti[None, :], len(fields))[0]

    def f1(pp, tt, i):
        return ((pp == i) & (tt == i)).sum(-1) * 2 / np.maximum(1, (pp == i).sum(-1) + (tt == i).sum(-1))
    obs = {f: float(f1(pred, ti, i)) for f, i in fi.items()}
    bins = K.freq_bins(ws, cd); groups = [np.where(bins == b)[0] for b in sorted(set(bins))]
    TT = _perms(ti, groups, nperm, rng)
    PP = _loo_predict(X, TT, len(fields))
    null = {f: f1(PP, TT, i) for f, i in fi.items()}
    return dict(fields=fields, f1=obs, passed={f: bool(obs[f] >= 0.5 and obs[f] > np.percentile(null[f], 95))
                                               for f in fields})


# =================================================================== B: simulation
def _b_plant(shape, rng):
    fields = shape["fields"]; pool, rest = shape["words_pool"], shape["words_rest"]
    md, mh, mf = shape["min_dev"], shape["min_held"], shape["min_field_words"]
    for _ in range(100000):
        pp = list(rng.permutation(len(pool))); rr = list(rng.permutation(len(rest)))
        words = {}
        for f, size, npool in fields:
            for i in pp[:npool]: words[f"p{i}"] = (f, *pool[i])
            for i in rr[:size - npool]: words[f"r{i}"] = (f, *rest[i])
            pp, rr = pp[npool:], rr[size - npool:]
        nsc = Counter(f for f, dv, hd in words.values() if dv >= md and hd >= mh)
        if shape["plant_rule"] == "v2":
            if all(nsc[f] >= mf for f, _, _ in fields): return words, True
        else:                                   # curve rule: counts only with >= 3 fields of >= 3 test words
            return words, sum(nsc[f] >= mf for f, _, _ in fields) >= 3
    raise RuntimeError("no scoreable word set")


def _b_draw(shape, words, rng):
    nd, nh = int(shape["n_dev"]), int(shape["n_held"])
    wd = rng.choice(np.asarray(shape["wpd_dev"], float), nd); wh = rng.choice(np.asarray(shape["wpd_held"], float), nh)
    dev = [dict(id=f"d{i}", words=[]) for i in range(nd)]; held = [dict(id=f"h{i}", words=[]) for i in range(nh)]
    for w in sorted(words):
        _, dv, hd = words[w]
        for docs, wt, k in ((dev, wd, dv), (held, wh, hd)):
            k = min(int(k), int((wt > 0).sum()))
            if k > 0:
                for i in rng.choice(len(docs), size=k, replace=False, p=wt / wt.sum()): docs[i]["words"].append(w)
    for d in dev + held: d["words"].sort()
    A = {}
    for v, key in (("S", "site"), ("K", "cls"), ("P", "pic")):
        vals = list(shape["base"][v]); pr = np.array([shape["base"][v][x] for x in vals], float)
        draw = rng.choice(len(vals), size=nd + nh, p=pr / pr.sum())
        A[key] = {d["id"]: vals[j] for d, j in zip(dev + held, draw)}
    for d in dev + held: d["pic"] = A["pic"][d["id"]]
    return dev, held, A


def b_set(shape, seed, j):
    rng = _rng(seed, j)
    words, counted = _b_plant(shape, rng)
    plant = {w: f for w, (f, _, _) in words.items()}
    FIELDS = sorted(f for f, _, _ in shape["fields"])
    md, mh = shape["min_dev"], shape["min_held"]
    pool_ids = {w for w in words if w.startswith("p")}
    res = []
    for k in range(int(shape["ndraw"])):
        rk = _rng(seed, j, k)
        dev, held, A = _b_draw(shape, words, rk)
        cd = K.doc_counts(dev); ch = K.doc_counts(held)
        el = sorted(w for w in words if cd[w] >= md)
        A["pic"] = K1.planted_pics(dev + held, set(el), plant, float(shape["s"]), rk)
        if shape.get("held_in_centroids", True):
            sc = sorted(w for w in el if ch[w] >= mh); cw = el
        else:
            sc = sorted(w for w in pool_ids if ch[w] >= mh); cw = [w for w in el if w not in pool_ids]
        out = {}
        if cw and sc:
            P = C2.profiles(dev, cw, "A3", A, dev)
            if shape.get("dev_gate", True):
                out["dev"] = supervised_fast(cw, P, plant, FIELDS, cd, int(shape["nperm"]), rk)
            Q = C2.profiles(held, sc, "A3", A, dev)
            pred = K.assign(Q, P, np.array([plant[w] for w in cw]))
            out["held"] = score_draw_fast(plant, FIELDS, sc, pred, cd, int(shape["nperm"]), rk)
        res.append(out)
    need = int(shape["need"])
    def rec(key):
        return {f: sum(r.get(key, {}).get("passed", {}).get(f, False) for r in res) >= need for f in FIELDS}
    def scored(key):
        return {f: sum(f in r.get(key, {}).get("passed", {}) for r in res) >= need for f in FIELDS}
    aris = [r["held"]["ari"] for r in res if "held" in r]
    return dict(counted=counted, held_ari=float(np.nanmedian(aris)) if aris and not all(np.isnan(aris)) else float("nan"),
                held_rec=rec("held"), held_scored=scored("held"), dev_rec=rec("dev"))


def _b_chunk(a):
    shape, seed, lo, hi = a
    return [b_set(shape, seed, j) for j in range(lo, hi)]


def power_b(shape, effect, alpha, seed, nsim=NSIM):
    """effect / alpha unused (B's effect is the plant strength s inside the shape; its bars are the v2 bars)."""
    step = max(1, nsim // (4 * NWORK))
    jobs = [(shape, seed, lo, min(nsim, lo + step)) for lo in range(0, nsim, step)]
    sets = [x for ch in (_POOL.map(_b_chunk, jobs) if _POOL else map(_b_chunk, jobs)) for x in ch]
    cs = [x for x in sets if x["counted"]]
    FIELDS = sorted(f for f, _, _ in shape["fields"])
    out = dict(n_sets=len(sets), n_counted=len(cs))
    if not cs: return dict(out, power=None)
    a = [x["held_ari"] for x in cs]
    out["held_median_ari"] = float(np.nanmedian(a)) if not all(np.isnan(a)) else None
    out["held_field_recovery"] = {f: float(np.mean([x["held_rec"][f] for x in cs])) for f in FIELDS}
    out["held_field_recovery_scored"] = {f: (float(np.mean([x["held_rec"][f] for x in cs if x["held_scored"][f]]))
                                             if any(x["held_scored"][f] for x in cs) else None) for f in FIELDS}
    out["held_gate_met"] = bool(out["held_median_ari"] is not None and out["held_median_ari"] >= 0.8
                                and min(out["held_field_recovery"].values()) >= 0.8)
    if shape.get("dev_gate", True):
        out["dev_field_recovery"] = {f: float(np.mean([x["dev_rec"][f] for x in cs])) for f in FIELDS}
        out["dev_gate_met"] = bool(min(out["dev_field_recovery"].values()) >= 0.8)
    out["power"] = float(np.mean([np.mean(list(x["held_rec"].values())) for x in cs]))
    return out


# =================================================================== entry point, searches
def power(family, shape, effect, alpha, seed=0, nsim=NSIM):
    if family == "A1": return power_a1(shape, effect, alpha, seed, nsim)
    if family == "A2a": return power_a2a(shape, effect, alpha, seed, nsim)
    if family == "A2b": return power_a2b(shape, effect, alpha, seed, nsim)
    if family == "A3": return power_a3(shape, effect, alpha, seed, nsim)
    if family == "B": return power_b(shape, effect, alpha, seed, nsim)
    raise ValueError(family)


def _ok(family, r):
    return r.get("power") is not None and r["power"] >= TARGET and (family != "A1" or r.get("counted", False))


def _search(f, grid, tol, start):
    """first grid value passing f, then bisection between it and the previous value (start = the null effect,
    taken as not powered) to tol."""
    prev = start
    for g in grid:
        if f(g):
            lo, hi = prev, g
            while abs(hi - lo) > tol + 1e-12:
                mid = (lo + hi) / 2
                if f(mid): hi = mid
                else: lo = mid
            return hi
        prev = g
    return None


def mde(family, shape, alpha, seed, kind=None, p0=None, tail="upper", nsim=NSIM):
    if family == "A1":
        if kind == "or":
            v = _search(lambda x: _ok("A1", power_a1(shape, ("or", x), alpha, seed, nsim)),
                        [1.0 + 0.5 * i for i in range(1, 200)], 0.1, 1.0)
        else:
            v = _search(lambda x: _ok("A1", power_a1(shape, ("delta", x), alpha, seed, nsim)),
                        [0.05 * i for i in range(1, 21)], 0.005, 0.0)
    elif family == "A2a":
        v = _search(lambda x: _ok("A2a", power_a2a(shape, x, alpha, seed, nsim)),
                    [p0 + 0.05 * i for i in range(1, 21) if p0 + 0.05 * i <= 1.0], 0.005, p0)
    elif family == "A2b":
        if tail == "upper":
            v = _search(lambda x: _ok("A2b", power_a2b(shape, x, alpha, seed, nsim)), [1 + 0.25 * i for i in range(1, 77)], 0.01, 1.0)
        else:
            v = _search(lambda x: _ok("A2b", power_a2b(shape, x, alpha, seed, nsim)), [1 - 0.1 * i for i in range(1, 11)], 0.01, 1.0)
    elif family == "A3":
        v = _search(lambda x: _ok("A3", power_a3(shape, min(x, 0.99), alpha, seed, nsim)),
                    [0.1 * i for i in range(1, 10)] + [0.99], 0.01, 0.0)
    else:
        return None
    return None if v is None else round(v, 4)


def scale_shape(family, shape, k):
    s = dict(shape)
    if family == "A1":
        s["n"] = max(2, int(round(shape["n"] * k)))
        if shape.get("n_A") is not None: s["n_A"] = min(s["n"] - 1, max(1, int(round(shape["n_A"] * k))))
        if shape.get("c_g"): s["c_g"] = [min(s["n"] - 1, max(1, int(round(c * k)))) for c in shape["c_g"]]
        s["n_B"] = s["n"] - (s["n_A"] if s.get("n_A") is not None else s["n"] // 2)
    elif family == "A2b":
        s["n"] = max(1, int(round(shape["n"] * k)))
        if not shape.get("ref_fixed", True): s["_ref_scale"] = k
    else:
        s["n"] = max(1, int(round(shape["n"] * k)))
    return s


def n_needed(family, shape, eff, alpha, seed, nsim=NSIM):
    """smallest count (and multiple of n in hand) with power >= 0.8, up to 64x."""
    n0 = int(shape.get("n") or 0)
    base = n0 if n0 > 0 else max(1, int(shape.get("min_n") or 1))
    b = dict(shape, n=base) if n0 == 0 else shape
    f = lambda k: _ok(family, power(family, scale_shape(family, b, k), eff, alpha, seed, nsim))
    grid = [2.0 ** e for e in range(-6, 7)]
    prev = None
    for g in grid:
        if f(g):
            if prev is None: return dict(count=int(round(base * g)), multiple=(g * base / n0) if n0 else None)
            lo, hi = int(round(base * prev)), int(round(base * g))
            while hi - lo > 1:
                mid = (lo + hi) // 2
                if f(mid / base): hi = mid
                else: lo = mid
            return dict(count=hi, multiple=(hi / n0) if n0 else None)
        prev = g
    return dict(count=None, multiple=None, note="not reached by 64x")


# =================================================================== modes
def load_shapes():
    return json.load(open(HERE / "shapes.json"))


def mode_kill():
    S = load_shapes()["kill"]; out = dict(seed=SEED_KILL, nsim=NSIM, started=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    seed = SEED_KILL
    # case 1: B
    b = dict(S["case1"]); b.pop("diagnostics", None); b.pop("cells", None)
    t0 = time.time(); out["case1"] = power("B", b, None, None, seed=seed); out["case1"]["seconds"] = round(time.time() - t0)
    print("case1", json.dumps(out["case1"]), flush=True)
    # A1 cases
    for i, key in enumerate(("case3", "case4a", "case4b", "case4c")):
        sh = S[key]; cells = []
        for dl in sh["deltas"]:
            r = power("A1", sh, ("delta", dl), sh["alpha"], seed=seed + 10 * i)
            r.update(delta_nominal=dl, grey=dl in sh.get("grey", [])); cells.append(r)
        out[key] = dict(cells=cells, mde_0_8=mde("A1", sh, sh["alpha"], seed + 10 * i), n=sh["n"], n_A=sh["n_A"], m=sh["m"])
        print(key, json.dumps(out[key]), flush=True)
    # case 5a: A2b, C6
    sh = S["case5a"]; cells = []
    for j, c in enumerate(sh["cells"]):
        s = dict(sh, n=c["n"]); r = power("A2b", s, sh["R"], sh["alpha"], seed=seed + 100 + j); r.update(c); cells.append(r)
    out["case5a"] = dict(cells=cells, min_n=n_needed("A2b", dict(sh, n=sh["cells"][0]["n"]), sh["R"], sh["alpha"], seed + 150))
    print("case5a", json.dumps(out["case5a"]), flush=True)
    # case 5b: A3, C9
    sh = S["case5b"]; cells = []
    for j, c in enumerate(sh["cells"]):
        s = dict(sh, n=c["n"], n_strata=c["n_strata"], dup_share=c["dup_share"])
        r = power("A3", s, sh["rho"], sh["alpha"], seed=seed + 200 + j); r.update(c); cells.append(r)
    c0 = sh["cells"][0]
    out["case5b"] = dict(cells=cells, min_n=n_needed("A3", dict(sh, n=c0["n"], n_strata=c0["n_strata"], dup_share=c0["dup_share"]),
                                                     sh["rho"], sh["alpha"], seed + 250))
    print("case5b", json.dumps(out["case5b"]), flush=True)
    out["finished"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    json.dump(out, open(HERE / "kill.json", "w"), indent=1)


def _adopted():
    p = HERE / "adoption.json"
    return set(json.load(open(p))["adopted"]) if p.exists() else None


def mode_census():
    SH = load_shapes(); adopted = _adopted(); rows = []
    for ri, R in enumerate(SH["census"]):
        fam = R["family"]
        if fam in ("none", "C") or not R["states"]:
            rows.append(dict(route=R["route"], name=R["name"], source=R["source"], family=fam, state="as stated",
                             n=R["stated"], effect=R["effect"] if isinstance(R["effect"], str) else json.dumps(R["effect"]),
                             gate="raw n only" if fam == "none" else R.get("verdict", "not sized"),
                             what_adds_rows=R.get("what_adds_rows", "")))
            continue
        for si, st in enumerate(R["states"]):
            seed = SEED_CENSUS + 1000 * R["route"] + 10 * si
            sh = st["shape"]
            row = dict(route=R["route"], name=R["name"], source=R["source"], family=fam, state=st["label"],
                       effect_source=R["effect_source"], what_adds_rows=R.get("what_adds_rows", ""))
            if fam == "B":
                row.update(n=R["stated"], effect="curve d*", gate="needs >= d* documents per sign (curve.json); "
                                                                   "B prediction at this shape: kill.json case1")
                rows.append(row); continue
            if fam == "A1":
                eff = ("or", R["effect"]["OR"]) if "OR" in R["effect"] else ("delta", R["effect"]["delta"])
                r = power("A1", sh, eff, sh["alpha"], seed)
                row.update(n=sh["n"], class_sizes=json.dumps(dict(A=sh.get("n_A"), B=(sh["n"] - sh["n_A"]) if sh.get("n_A") is not None else None)),
                           m=sh.get("m"), alpha=sh["alpha"], effect=f"{eff[0]} {eff[1]}", power_at_effect=r["power"],
                           feasible_share=r.get("feasible_share"), bound=sh.get("bound", ""),
                           MDE_0_8=mde("A1", sh, sh["alpha"], seed, kind=eff[0]))
                if eff[0] == "delta":
                    row["power_LB_names"] = json.dumps({str(d): power("A1", sh, ("delta", d), sh["alpha"], seed)["power"]
                                                        for d in LB_NAMES})
                nn = n_needed("A1", sh, eff, sh["alpha"], seed)
            elif fam == "A2a":
                r = power("A2a", sh, sh["p1"], sh["alpha"], seed)
                row.update(n=sh["n"], m=sh.get("m"), alpha=sh["alpha"], effect=f"p1 {sh['p1']:.4f} vs p0 {sh['p0']:.4f}",
                           power_at_effect=r["power"], MDE_0_8=mde("A2a", sh, sh["alpha"], seed, p0=sh["p0"]) if sh["n"] > 0 else None)
                nn = n_needed("A2a", sh, sh["p1"], sh["alpha"], seed)
            elif fam == "A2b":
                r = power("A2b", sh, sh["R"], sh["alpha"], seed)
                row.update(n=sh["n"], m=sh.get("m"), alpha=sh["alpha"], effect=f"R {sh['R']:.3f} ({sh['tail']}, bar {sh['bar']})",
                           class_sizes=json.dumps(dict(target=sh["n"], reference=sum(s.get("ref_n", 0) for s in sh["strata"])
                                                       if sh.get("ref_fixed", True) else sh.get("ref_n_total"))),
                           power_at_effect=r["power"], MDE_0_8=mde("A2b", sh, sh["alpha"], seed, tail=sh["tail"]) if sh["n"] > 0 else None)
                nn = n_needed("A2b", sh, sh["R"], sh["alpha"], seed)
            elif fam == "A3":
                r = power("A3", sh, sh["rho"], sh["alpha"], seed)
                row.update(n=sh["n"], m=sh.get("m"), alpha=sh["alpha"], effect=f"rho {sh['rho']}", power_at_effect=r["power"],
                           MDE_0_8=mde("A3", sh, sh["alpha"], seed) if sh["n"] >= max(3, sh.get("min_n") or 0) else None)
                nn = n_needed("A3", sh, sh["rho"], sh["alpha"], seed)
            row.update(n_needed=nn.get("count"), n_needed_multiple=nn.get("multiple"))
            powered = r["power"] >= TARGET and (fam != "A1" or r.get("counted", False))
            if adopted is None: row["gate"] = f"pending adoption (would {'pass' if powered else 'STOP by count'})"
            elif fam not in adopted and not (fam in ("A2a", "A2b") and "A2" in adopted):
                for k in ("power_at_effect", "MDE_0_8", "feasible_share", "power_LB_names", "n_needed", "n_needed_multiple"):
                    row.pop(k, None)
                row["gate"] = "raw n only (family not adopted)"
            else: row["gate"] = "pass" if powered else "STOP by count"
            if sh.get("bound") == "upper": row["gate"] += " (upper bound: marginals not in the repo)"
            rows.append(row); print(json.dumps(row), flush=True)
    cols = ["route", "name", "source", "family", "state", "n", "class_sizes", "m", "alpha", "effect", "effect_source",
            "power_at_effect", "MDE_0_8", "feasible_share", "power_LB_names", "n_needed", "n_needed_multiple", "bound",
            "gate", "what_adds_rows"]
    with open(HERE / "census.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, cols, extrasaction="ignore"); w.writeheader(); [w.writerow(r) for r in rows]
    json.dump(dict(seed=SEED_CENSUS, adopted=sorted(adopted) if adopted else None, rows=rows), open(HERE / "census.json", "w"),
              indent=1, default=str)


def _alloc(n, props):
    tot = sum(p for _, p in props); raw = [n * p / tot for _, p in props]; out = [int(math.floor(x)) for x in raw]
    for i in sorted(range(len(raw)), key=lambda i: -(raw[i] - out[i]))[:n - sum(out)]: out[i] += 1
    return [(f, k) for (f, _), k in zip(props, out)]


_CV = {}


def _curve_init():
    if not _CV:
        dev, held = K.draw_docs(0); docs = dev + held
        _CV.update(docs=docs, A=K.anchors_of(docs), cnt=K.doc_counts(docs))
        by = {}
        for i, d in enumerate(docs):
            for w in d["words"]: by.setdefault(w, []).append(i)
        _CV["by"] = by


def curve_plant(a):
    d, s, j = a
    _curve_init(); docs, by, cnt = _CV["docs"], _CV["by"], _CV["cnt"]
    rng = _rng(SEED_CURVE, d, int(round(s * 10)), j)
    E = sorted(w for w, n in cnt.items() if n >= d + 5)
    sizes = _alloc(len(E), CURVE_PROP); perm = list(rng.permutation(E)); plant = {}
    for f, k in sizes:
        for w in perm[:k]: plant[str(w)] = f
        perm = perm[k:]
    A = {v: dict(x) for v, x in _CV["A"].items()}
    A["pic"] = K1.planted_pics(docs, set(E), plant, s, rng)
    test = sorted(str(w) for w in rng.choice(E, size=int(round(CURVE_TEST * len(E))), replace=False))
    kept = {w: set(int(i) for i in rng.choice(by[w], size=d, replace=False)) for w in test}
    side = set().union(*kept.values()) if kept else set()
    tdocs = [dict(id=docs[i]["id"], words=sorted(w for w in test if i in kept[w])) for i in sorted(side)]
    cdocs = [docs[i] for i in range(len(docs)) if i not in side]
    ccnt = K.doc_counts(cdocs); tset = set(test)
    cw = sorted(w for w in E if w not in tset and ccnt[w] >= 5)
    nt = Counter(plant[w] for w in test)
    counted = sum(1 for f, _ in CURVE_PROP if nt[f] >= 3) >= 3
    out = dict(d=d, s=s, plant=j, counted=counted, n_test=len(test), n_centroid_words=len(cw), n_test_docs=len(tdocs))
    if not counted or not cw: return out
    P = C2.profiles(cdocs, cw, "A3", A, cdocs)
    Q = C2.profiles(tdocs, test, "A3", A, cdocs)
    pred = K.assign(Q, P, np.array([plant[w] for w in cw]))
    r = score_draw_fast(plant, sorted(f for f, _ in CURVE_PROP), test, pred, ccnt, 1000, rng)
    out.update(ari=r["ari"], passed=r["passed"], fields=r["fields"])
    return out


def mode_curve():
    SH = load_shapes(); E = {int(k): v for k, v in SH["curve"]["E_d"].items()}
    reach = [d for d in CURVE_D if E[d] >= 30]
    jobs = [(d, s, j) for d in reach for s in (1.0, 0.6) for j in range(CURVE_NPLANT)]
    res = _POOL.map(curve_plant, jobs, chunksize=1)
    out = dict(seed=SEED_CURVE, E_d=E, reachable=reach, rungs={})
    for d in CURVE_D:
        if d not in reach:
            out["rungs"][str(d)] = dict(result="not reachable at this corpus size", E_d=E[d]); continue
        out["rungs"][str(d)] = {}
        for s in (1.0, 0.6):
            rr = [r for r in res if r["d"] == d and r["s"] == s and r["counted"] and "ari" in r]
            fr = {}
            for f, _ in CURVE_PROP:
                sc = [r for r in rr if f in r["passed"]]
                fr[f] = float(np.mean([r["passed"][f] for r in sc])) if sc else None
            med = float(np.nanmedian([r["ari"] for r in rr])) if rr else None
            ok = bool(rr and med is not None and med >= 0.8 and all(v is None or v >= 0.8 for v in fr.values())
                      and any(v is not None for v in fr.values()))
            out["rungs"][str(d)][str(s)] = dict(counted_plants=len(rr), median_ari=med, field_recovery=fr, bar=ok)
    ds = [d for d in reach if out["rungs"][str(d)]["1.0"]["bar"]]
    out["d_star"] = min(ds) if ds else f"> {max(reach) if reach else 'none reachable'}"
    out["d_star_note"] = "lower bound (one exclusive picture value per field is easier than any real tie)"
    print("curve", json.dumps(out["rungs"]), "d*", out["d_star"], flush=True)
    # Family B's predicted curve (printed beside; decides nothing)
    c1 = SH["kill"]["case1"]; cnt = SH["curve"]; pred = {}
    _curve_init(); counts = sorted(_CV["cnt"].values())
    for d in reach:
        Ew = [c for c in counts if c >= d + 5]; ntest = int(round(CURVE_TEST * len(Ew)))
        fields = [[f, k, kp] for (f, k), (_, kp) in zip(_alloc(len(Ew), CURVE_PROP), _alloc(ntest, CURVE_PROP))]
        bs = dict(family="B", n_dev=cnt["n_docs"] - min(ntest * d, cnt["n_docs"] // 2), n_held=min(ntest * d, cnt["n_docs"] // 2),
                  wpd_dev=c1["wpd_dev"] + c1["wpd_held"], wpd_held=c1["wpd_dev"] + c1["wpd_held"], base=c1["base"],
                  fields=fields, words_pool=[[c - d, d] for c in Ew], words_rest=[[c, 0] for c in Ew], s=1.0, ndraw=1,
                  need=1, min_dev=5, min_held=2, min_field_words=3, held_in_centroids=False, dev_gate=False,
                  plant_rule="curve", nperm=1000)
        pred[str(d)] = power("B", bs, None, None, seed=SEED_CURVE + d)
        print("B predicted", d, json.dumps(pred[str(d)]), flush=True)
    out["B_predicted"] = pred
    # U rows
    cen = {}
    cp = HERE / "census.json"
    if cp.exists():
        for r in json.load(open(cp))["rows"]:
            if str(r.get("state", "")).startswith("in hand") or r.get("state") == "as stated":
                cen.setdefault(int(r["route"]), r)
    urows = []
    for uid, u in SH["u_rows"]["rows"].items():
        row = dict(id=uid, rule=u["rule"], tier=u["tier"])
        if u["rule"].startswith("own A1"):
            sh = u.get("shape")
            if isinstance(sh, dict):
                r = power("A1", sh, ("delta", LB_DELTA), sh["alpha"], SEED_CURVE + len(urows))
                nn = n_needed("A1", sh, ("delta", LB_DELTA), sh["alpha"], SEED_CURVE + len(urows))
                row.update(count_in_hand=sh["n"], count_needed=nn.get("count"), power_at_0_23=r["power"])
            else:
                row.update(count_in_hand="shape not tabulated", count_needed="")
        elif u["rule"].startswith("census route"):
            rr = cen.get(int(u["rule"].split()[-1]), {})
            row.update(count_in_hand=rr.get("n", "see census"), count_needed=rr.get("n_needed", rr.get("gate", "")))
        else:
            row.update(count_in_hand="no count rule", count_needed="")
        row["profile_rule"] = f">= {out['d_star']} documents per sign, >= 3 signs per class, if the test needs per-sign profiles"
        urows.append(row)
    out["u_rows"] = urows
    with open(HERE / "u_rows.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, ["id", "tier", "rule", "count_in_hand", "count_needed", "power_at_0_23", "profile_rule"],
                           extrasaction="ignore")
        w.writeheader(); [w.writerow(r) for r in urows]
    json.dump(out, open(HERE / "curve.json", "w"), indent=1, default=str)


# =================================================================== selftest (made-up shapes; prints, writes nothing)
def mode_selftest():
    t0 = time.time()
    a1 = dict(n=40, n_A=10, c_g=[6, 9, 14], m=3)
    print("A1", power("A1", a1, ("delta", 0.2), 0.05, seed=1, nsim=300))
    print("A1 OR", power("A1", a1, ("or", 3.0), 0.05, seed=1, nsim=300))
    print("A1 upper", power("A1", dict(n=30, n_A=None, c_g=None, m=2, bound="upper"), ("delta", 0.3), 0.05, seed=1, nsim=200))
    print("A1 mde", mde("A1", a1, 0.05, 1, nsim=200), "n_needed", n_needed("A1", a1, ("delta", 0.2), 0.05, 1, nsim=200))
    a2a = dict(n=25, p0=0.02, bar=0.08, min_n=10, m=1)
    print("A2a", power("A2a", a2a, 0.2, 0.05, seed=2, nsim=300), "n0 needed", n_needed("A2a", dict(a2a, n=0), 0.2, 0.05, 2, nsim=300))
    a2b = dict(strata=[dict(ref_n=50, ref_rate=0.3, target_share=0.6), dict(ref_n=30, ref_rate=0.6, target_share=0.4)],
               ref_fixed=True, tail="upper", ratio="oe", bar=1.25, m=1, n=60)
    print("A2b", power("A2b", a2b, 1.6, 0.05, seed=3, nsim=200))
    a2l = dict(strata=[dict(ref_rate=0.2, target_share=0.5, ref_share=0.5), dict(ref_rate=0.2, target_share=0.5, ref_share=0.5)],
               ref_fixed=False, ref_n_total=120, tail="lower", ratio="rr", bar=0.5, m=1, n=40)
    print("A2b lower", power("A2b", a2l, 0.25, 0.05, seed=3, nsim=200))
    a3 = dict(n=40, v_margin={"0": 0.5, "1": 0.2, "3": 0.2, "7": 0.1}, min_pos=5, min_n=8, n_strata=4, dup_share=0.05, m=1)
    print("A3", power("A3", a3, 0.5, 0.05, seed=4, nsim=60))
    # B: made-up corpus; also check the fast scorers against core's own functions on one draw
    rng = np.random.default_rng(5)
    bshape = dict(family="B", n_dev=300, n_held=120, wpd_dev=list(rng.integers(0, 6, 300)), wpd_held=list(rng.integers(0, 6, 120)),
                  base=dict(S={"a": 0.5, "b": 0.5}, K={"x": 0.7, "y": 0.3}, P={"none": 0.6, "OVIS": 0.4}),
                  fields=[["f1", 6, 4], ["f2", 5, 3], ["f3", 4, 3]],
                  words_pool=[[int(rng.integers(5, 12)), int(rng.integers(2, 5))] for _ in range(14)],
                  words_rest=[[int(rng.integers(3, 12)), int(rng.integers(0, 2))] for _ in range(10)],
                  s=1.0, ndraw=2, need=2, min_dev=5, min_held=2, min_field_words=3, held_in_centroids=True,
                  dev_gate=True, plant_rule="v2", nperm=60)
    print("B", power("B", bshape, None, None, seed=6, nsim=4))
    words, _ = _b_plant(bshape, _rng(7)); plant = {w: f for w, (f, _, _) in words.items()}; F = ["f1", "f2", "f3"]
    dev, held, A = _b_draw(bshape, words, _rng(8)); cd = K.doc_counts(dev); ch = K.doc_counts(held)
    el = sorted(w for w in words if cd[w] >= 5); A["pic"] = K1.planted_pics(dev + held, set(el), plant, 1.0, _rng(9))
    P = C2.profiles(dev, el, "A3", A, dev); sc = sorted(w for w in el if ch[w] >= 2)
    Q = C2.profiles(held, sc, "A3", A, dev); pred = K.assign(Q, P, np.array([plant[w] for w in el]))
    fa, co = score_draw_fast(plant, F, sc, pred, cd, 80, _rng(10)), K.score_draw(plant, F, sc, pred, cd, 80, _rng(10))
    print("score_draw fast == core:", fa["passed"] == co["passed"], fa["f1"] == co["f1"], abs(fa["ari"] - co["ari"]) < 1e-12)
    fa, co = supervised_fast(el, P, plant, F, cd, 80, _rng(11)), K.supervised_control(el, P, plant, F, cd, 80, _rng(11))
    print("supervised fast == core:", fa["passed"] == co["passed"],
          all(abs(fa["f1"][f] - co["f1"][f]) < 1e-12 for f in co["f1"]))
    print(f"selftest done in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "selftest"
    if mode == "selftest":
        mode_selftest(); sys.exit(0)
    with Pool(NWORK) as P:
        _POOL = P
        {"kill": mode_kill, "census": mode_census, "curve": mode_curve}[mode]()
