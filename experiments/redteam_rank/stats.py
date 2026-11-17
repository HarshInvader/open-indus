import numpy as np
import collections as C


def nbin(n):
    return min(n, 7)


def strata_key(t, kind):
    if kind == "base":           # their control: site x sign count x lines
        return (t["site"], nbin(t["nsign"]), min(t["lines"], 2))
    if kind == "site":
        return (t["site"],)
    if kind == "glyph":          # site x glyph-total quintile x lines (no sign count)
        return (t["site"], t["_gq"], min(t["lines"], 2))
    if kind == "glyph+n":        # site x sign count x glyph tercile within count x lines
        return (t["site"], nbin(t["nsign"]), t["_gq3"], min(t["lines"], 2))
    if kind == "linew":          # site x longest-line width quintile x lines
        return (t["site"], t["_lq"], min(t["lines"], 2))
    if kind == "base+emb":
        return (t["site"], nbin(t["nsign"]), min(t["lines"], 2), t["emb"])
    if kind == "base+mult":
        return (t["site"], nbin(t["nsign"]), min(t["lines"], 2), min(t["n_obj"], 2))
    if kind == "base+phase":
        return (t["site"], nbin(t["nsign"]), min(t["lines"], 2), t["period"] + "/" + t["phase"])
    if kind == "base+emb+mult":
        return (t["site"], nbin(t["nsign"]), min(t["lines"], 2), t["emb"], min(t["n_obj"], 2))
    raise KeyError(kind)


def add_quantiles(T):
    g = np.array([t["glyph_total"] for t in T]); l = np.array([t["linew_max"] for t in T])
    gq = np.searchsorted(np.quantile(g, [.2, .4, .6, .8]), g)
    lq = np.searchsorted(np.quantile(l, [.2, .4, .6, .8]), l)
    for t, a, b in zip(T, gq, lq):
        t["_gq"], t["_lq"] = int(a), int(b)
    # glyph tercile within sign count
    byn = C.defaultdict(list)
    for i, t in enumerate(T):
        byn[nbin(t["nsign"])].append(i)
    for n, idx in byn.items():
        v = np.array([T[i]["glyph_total"] for i in idx])
        q = np.searchsorted(np.quantile(v, [1 / 3, 2 / 3]), v) if len(v) > 3 else np.zeros(len(v), int)
        for i, a in zip(idx, q):
            T[i]["_gq3"] = int(a)


def strata_test(T, x, kind="base", y="la", nperm=4000, seed=0):
    """x: 0/1 array over T. Outcome residualised within strata; carriers' mean residual.
    Returns effect (fractional change), z vs within-strata permutation null, one-sided p's, n."""
    rng = np.random.default_rng(seed)
    keys = [strata_key(t, kind) for t in T]
    yv = np.array([t[y] for t in T])
    groups = C.defaultdict(list)
    for i, k in enumerate(keys):
        groups[k].append(i)
    res = np.zeros(len(T)); inf = np.zeros(len(T), bool)
    for k, idx in groups.items():
        if len(idx) < 2:
            continue
        idx = np.array(idx)
        if x[idx].sum() == 0 or x[idx].sum() == len(idx):
            continue  # stratum carries no contrast
        res[idx] = yv[idx] - yv[idx].mean(); inf[idx] = True
    idx = np.where(inf)[0]
    if x[idx].sum() == 0:
        return dict(n=0)
    xi = x[idx].astype(float); ri = res[idx]
    obs = (ri * xi).sum() / xi.sum()
    # within-strata permutation
    gl = C.defaultdict(list)
    for j, i in enumerate(idx):
        gl[keys[i]].append(j)
    gl = [np.array(v) for v in gl.values()]
    null = np.empty(nperm)
    xp = xi.copy()
    for b in range(nperm):
        for g in gl:
            xp[g] = xi[g][rng.permutation(len(g))]
        null[b] = (ri * xp).sum() / xp.sum()
    z = (obs - null.mean()) / null.std()
    return dict(n=int(xi.sum()), n_inf=int(len(idx)), eff=float(np.expm1(obs)), z=float(z),
                p_lo=float((1 + (null <= obs).sum()) / (nperm + 1)),
                p_hi=float((1 + (null >= obs).sum()) / (nperm + 1)))


def ols_test(T, x, covars, fe, y="la", nperm=2000, seed=0, strata="base"):
    """y ~ FE + covars + x. Permute x within strata (site x nsign x lines)."""
    rng = np.random.default_rng(seed)
    n = len(T)
    cols = [np.ones(n)]
    for f in fe:
        lv = sorted(set(f(t) for t in T))
        for l in lv[1:]:
            cols.append(np.array([f(t) == l for t in T], float))
    for c in covars:
        cols.append(np.array([c(t) for t in T], float))
    Z = np.column_stack(cols)
    yv = np.array([t[y] for t in T])
    # residualise y and x on Z
    P = Z @ np.linalg.pinv(Z)
    ry = yv - P @ yv
    def coef(xv):
        rx = xv - P @ xv
        return (rx @ ry) / (rx @ rx)
    obs = coef(x.astype(float))
    keys = [strata_key(t, strata) for t in T]
    gl = C.defaultdict(list)
    for i, k in enumerate(keys):
        gl[k].append(i)
    gl = [np.array(v) for v in gl.values() if len(v) > 1]
    null = np.empty(nperm); xp = x.astype(float).copy()
    for b in range(nperm):
        for g in gl:
            xp[g] = x[g][rng.permutation(len(g))]
        null[b] = coef(xp)
    z = (obs - null.mean()) / null.std()
    return dict(n=int(x.sum()), eff=float(np.expm1(obs)), z=float(z),
                p_lo=float((1 + (null <= obs).sum()) / (nperm + 1)),
                p_hi=float((1 + (null >= obs).sum()) / (nperm + 1)))


def group_S(T, mask, kind="base", y="la", nperm=4000, seed=0, signs=None):
    from data import DEV_SIGN
    signs = signs or DEV_SIGN
    Ts = [t for t, m in zip(T, mask) if m]
    out = {}; zs = []
    for f, sg in signs.items():
        x = np.array([t[f] for t in Ts])
        r = strata_test(Ts, x, kind, y, nperm, seed)
        out[f] = r
        zs.append(sg * r.get("z", 0.0))
    S = float(np.sum(zs) / np.sqrt(len(zs)))
    from scipy.stats import norm
    return S, float(norm.sf(S)), out
