"""T2: do frame signs, ladder position or title count track STATUS measured on the object?

Unit: distinct texts on square seals (SEAL:S) with a measured face (mean log area of all
objects carrying the text). Control: site x length (1..7+) x lines (1, 2+) strata; the
residual of log area from its stratum mean is the outcome. Inference: the residual vector
is permuted within strata (keeps feature co-occurrence), N_PERM times.

Tests
  pos  positive control: log area rises with text length within site (slope, permutation)
  feat per frame feature (>= MINC carriers): mean residual carriers - non-carriers
  glob global: sum over features of z^2 (does any frame sign track size?)
  lad  text ladder score (mean normalised ICIT-dev ladder position of its frame signs) vs residual
  cnt  number of distinct frame features vs residual
  emb  rare emblem (non-unicorn animal) vs residual; none vs residual
  mat  material: non-steatite vs steatite on all seal types (feature profile; area)
Power: minimum detectable effect (80% power, two-sided alpha 0.05) per feature.
Usage: t2_status.py dev|heldout
"""
import json, math, random, sys
from collections import Counter, defaultdict
import numpy as np
sys.path.insert(0, __import__("os").path.dirname(__file__))
from common import seal_table, strata, resid_by_strata, FRAME, HERE

N_PERM = 4000
MINC = 8


def perm_within(st, rng):
    g = defaultdict(list)
    for i, s in enumerate(st):
        g[s].append(i)
    idx = np.arange(len(st))
    for s, ii in g.items():
        ii = np.array(ii)
        idx[ii] = rng.permutation(ii)
    return idx


def analyse(split):
    rows = [r for r in seal_table(split) if r["log_area"] is not None]
    st = strata(rows)
    y = np.array([r["log_area"] for r in rows])
    res = np.array(resid_by_strata(list(y), st))
    sd = res.std()
    rng = np.random.default_rng(2026)
    perms = [perm_within(st, rng) for _ in range(N_PERM)]
    out = dict(split=split, n_texts=len(rows), resid_sd=float(sd))

    # positive control: length slope within site x lines strata
    st_site = strata(rows, with_length=False)
    L = np.array([min(r["length"], 10) for r in rows], float)
    yr = np.array(resid_by_strata(list(y), st_site)); Lr = np.array(resid_by_strata(list(L), st_site))
    slope = float((yr * Lr).sum() / (Lr * Lr).sum())
    null = []
    rng2 = np.random.default_rng(1)
    for _ in range(2000):
        p = perm_within(st_site, rng2)
        null.append((yr[p] * Lr).sum() / (Lr * Lr).sum())
    out["pos_length_slope"] = dict(slope_log_area_per_sign=slope, pct_per_sign=100 * (math.exp(slope) - 1),
                                   p=float((1 + sum(abs(x) >= abs(slope) for x in null)) / 2001))

    # per-feature
    feats = {}
    for f in FRAME:
        x = np.array([f in r["feats"] for r in rows])
        n1 = int(x.sum()); n0 = len(x) - n1
        if n1 < MINC:
            continue
        d = res[x].mean() - res[~x].mean()
        nd = np.array([res[p][x].mean() - res[p][~x].mean() for p in perms])
        se = nd.std()
        feats[f] = dict(n=n1, delta_log=float(d), pct=100 * (math.exp(d) - 1), z=float(d / se),
                        p=float((1 + (np.abs(nd) >= abs(d)).sum()) / (1 + N_PERM)),
                        mde_pct=100 * (math.exp(2.8 * se) - 1))
    out["features"] = feats
    # global
    F = list(feats)
    X = np.array([[f in r["feats"] for f in F] for r in rows])
    def zsum(rv):
        t = 0.0
        for j, f in enumerate(F):
            x = X[:, j]
            t += ((rv[x].mean() - rv[~x].mean()) / (sd * math.sqrt(1 / x.sum() + 1 / (~x).sum()))) ** 2
        return t
    obs = zsum(res); nz = [zsum(res[p]) for p in perms[:1000]]
    out["global"] = dict(stat=obs, null_mean=float(np.mean(nz)), n_features=len(F),
                         p=float((1 + sum(v >= obs for v in nz)) / 1001))

    # ladder score
    lad = json.load(open(HERE / "t1_dev.json"))["ICIT"]["order"]
    pos = {f: i / (len(lad) - 1) for i, f in enumerate(lad)}
    sc = np.array([np.mean([pos[f] for f in r["feats"] if f in pos]) if r["feats"] & set(pos) else np.nan for r in rows])
    m = ~np.isnan(sc)
    def corr(a, b):
        a = a - a.mean(); b = b - b.mean()
        return float((a * b).sum() / math.sqrt((a * a).sum() * (b * b).sum()))
    # rank-transform both (Spearman), permutation within strata on the subset
    from scipy.stats import rankdata
    st_m = [s for s, k in zip(st, m) if k]
    rr = rankdata(res[m]); ss = rankdata(sc[m])
    # recompute residual within the subset strata for honesty
    res_m = np.array(resid_by_strata(list(y[m]), st_m)); rr = rankdata(res_m)
    obs = corr(rr, ss)
    nl = []
    for _ in range(N_PERM):
        p = perm_within(st_m, rng)
        nl.append(corr(rr[p], ss))
    out["ladder"] = dict(n=int(m.sum()), spearman=obs, p=float((1 + sum(abs(v) >= abs(obs) for v in nl)) / (1 + N_PERM)),
                         mde_rho=float(2.8 * np.std(nl)))
    # within-TITLE ladder: earliest title-class position among title signs
    t1b = json.load(open(HERE / "t1b_dev.json"))["ICIT"]["TITLE"]["order"]
    tpos = {f: i / (len(t1b) - 1) for i, f in enumerate(t1b)}
    sc2 = np.array([np.mean([tpos[f] for f in r["feats"] if f in tpos]) if r["feats"] & set(tpos) else np.nan for r in rows])
    m2 = ~np.isnan(sc2); st2 = [s for s, k in zip(st, m2) if k]
    r2 = rankdata(np.array(resid_by_strata(list(y[m2]), st2))); s2 = rankdata(sc2[m2])
    obs2 = corr(r2, s2); nl2 = [corr(r2[perm_within(st2, rng)], s2) for _ in range(N_PERM)]
    out["ladder_title"] = dict(n=int(m2.sum()), spearman=obs2,
                               p=float((1 + sum(abs(v) >= abs(obs2) for v in nl2)) / (1 + N_PERM)),
                               mde_rho=float(2.8 * np.std(nl2)))
    # title count
    cnt = np.array([len(r["feats"]) for r in rows], float)
    obs3 = corr(rankdata(res), rankdata(cnt))
    nl3 = [corr(rankdata(res[p]), rankdata(cnt)) for p in perms[:2000]]
    out["frame_count"] = dict(spearman=obs3, p=float((1 + sum(abs(v) >= abs(obs3) for v in nl3)) / 2001),
                              mde_rho=float(2.8 * np.std(nl3)))
    # emblem
    emb = {}
    for lab, test in (("rare_animal", lambda e: e not in ("unicorn", "none", "unknown", "other")),
                      ("none", lambda e: e == "none"),
                      ("gaur", lambda e: e == "gaur"), ("zebu", lambda e: e == "zebu"),
                      ("elephant", lambda e: e == "elephant"), ("rhino", lambda e: e == "rhino"),
                      ("tiger", lambda e: e == "tiger")):
        x = np.array([test(r["emblem"]) for r in rows])
        if x.sum() < 5:
            continue
        d = res[x].mean() - res[~x].mean()
        nd = np.array([res[p][x].mean() - res[p][~x].mean() for p in perms[:2000]])
        emb[lab] = dict(n=int(x.sum()), pct=100 * (math.exp(d) - 1),
                        p=float((1 + (np.abs(nd) >= abs(d)).sum()) / 2001), mde_pct=100 * (math.exp(2.8 * nd.std()) - 1))
    out["emblem_area"] = emb
    # material on square seals (area)
    x = np.array([r["material"] not in ("steatite", "unknown") for r in rows])
    if x.sum() >= 3:
        d = res[x].mean() - res[~x].mean()
        nd = np.array([res[p][x].mean() - res[p][~x].mean() for p in perms[:2000]])
        out["material_area"] = dict(n=int(x.sum()), mats=dict(Counter(r["material"] for r, k in zip(rows, x) if k)),
                                    pct=100 * (math.exp(d) - 1), p=float((1 + (np.abs(nd) >= abs(d)).sum()) / 2001),
                                    mde_pct=100 * (math.exp(2.8 * nd.std()) - 1))
    return out


def material_profile(split):
    """All seal types, no area needed: does any frame feature differ on non-steatite seals?"""
    rows = seal_table(split, types=("SEAL:S", "SEAL:R", "SEAL", "SEAL:C", "SEAL:CY", "SEAL:L"))
    rows = [r for r in rows if r["material"] != "unknown"]
    st = [(r["site"], r["type"], min(r["length"], 7)) for r in rows]
    x = np.array([r["material"] not in ("steatite",) for r in rows])
    rng = np.random.default_rng(5)
    out = dict(n=len(rows), n_rare=int(x.sum()), mats=dict(Counter(r["material"] for r in rows)), features={})
    for f in FRAME:
        y = np.array([f in r["feats"] for r in rows], float)
        if y.sum() < MINC:
            continue
        obs = y[x].sum()
        exp_ = []
        for _ in range(2000):
            p = perm_within(st, rng)
            exp_.append(y[p][x].sum())
        exp_ = np.array(exp_)
        out["features"][f] = dict(obs=int(obs), exp=float(exp_.mean()),
                                  p=float((1 + (np.abs(exp_ - exp_.mean()) >= abs(obs - exp_.mean())).sum()) / 2001))
    return out


if __name__ == "__main__":
    split = sys.argv[1]
    o = analyse(split)
    o["material_profile"] = material_profile(split)
    json.dump(o, open(HERE / f"t2_{split}.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in o.items() if k not in ("features", "material_profile")}, indent=1))
    for f, v in sorted(o["features"].items(), key=lambda kv: kv[1]["p"]):
        print(f, v)
    mp = o["material_profile"]
    print("material profile n", mp["n"], "rare", mp["n_rare"], mp["mats"])
    for f, v in sorted(mp["features"].items(), key=lambda kv: kv[1]["p"])[:8]:
        print(" ", f, v)
