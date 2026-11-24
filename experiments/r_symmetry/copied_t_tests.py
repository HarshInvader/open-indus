"""Verbatim copies of the tablet_archives statistic functions (prereg r_symmetry "Code plan": t_tests.py runs its
whole analysis at import, so the functions are copied, not imported). Source: experiments/tablet_archives/t_tests.py
at commit 592193f. Function bodies are unchanged; the module globals they read (rng, NPLANT, NPERM_PLANT, tier1,
dep1, marg, tier3, X3, top15) are set by setup() from r_symmetry/run.py instead of t_tests' import-time code.
"""
import numpy as np

rng = np.random.default_rng(20261114)          # t_tests.py line 12
NPERM = 10000                                  # t_tests.py line 13
NPLANT, NPERM_PLANT = 200, 1000                # t_tests.py line 14
tier1 = dep1 = marg = tier3 = X3 = top15 = None


def setup(**kw):
    """Set the module globals the copied functions read (t_tests computes them at import, lines 113-134, 168)."""
    globals().update(kw)


# ---- t_tests.py lines 50-52
def codes(xs):
    u = {v: i for i, v in enumerate(sorted(set(xs)))}
    return np.array([u[x] for x in xs])


# ---- t_tests.py lines 55-63
def perm_matrix(strata, R):
    """R within-stratum permutations as index arrays: tiers_perm = tiers[P[r]] keeps each tier in its stratum."""
    s = codes(strata).astype(float)
    base = np.argsort(s, kind='stable')
    keys = s[None, :] + rng.random((R, len(s))) * 0.5
    order = np.argsort(keys, axis=1)  # within-stratum random order, strata grouped like base
    P = np.empty_like(order)
    P[:, base] = order
    return P


# ---- t_tests.py lines 66-67
def onehot(t):
    return (t[:, None] == np.array([2, 3, 4])[None, :]).astype(float)


# ---- t_tests.py lines 71-75
def g_table(O):
    E = O.sum(-1, keepdims=True) * O.sum(-2, keepdims=True) / O.sum((-1, -2), keepdims=True)
    with np.errstate(divide='ignore', invalid='ignore'):
        t = np.where(O > 0, O * np.log(O / E), 0.0)
    return 2 * t.sum((-1, -2))


# ---- t_tests.py lines 78-82
def t1_stat(dep, T):  # T: (R, n) tiers
    nd = dep.max() + 1
    idx = dep[None, :] * 3 + (T - 2)
    O = np.stack([np.bincount(row, minlength=nd * 3) for row in idx]).reshape(len(T), nd, 3).astype(float)
    return g_table(O)


# ---- t_tests.py lines 94-99
def t3_stat(X, T):
    Y = np.stack([onehot(t) for t in T])  # R,n,3
    O1 = np.einsum('ns,rnk->rsk', X, Y)
    O0 = Y.sum(1)[:, None, :] - O1
    O = np.stack([O1, O0], axis=2)  # r,s,2,3
    return g_table(O).sum(1)


# ---- t_tests.py lines 102-110
def perm_p(stat_fn, tiers, strata, R, alt='greater'):
    obs = stat_fn(tiers[None, :])[0]
    P = perm_matrix(strata, R)
    null = np.concatenate([stat_fn(tiers[P[i:i + 500]]) for i in range(0, R, 500)])
    if alt == 'greater':
        p = (np.sum(null >= obs - 1e-12) + 1) / (R + 1)
    else:
        p = (np.sum(null <= obs + 1e-12) + 1) / (R + 1)
    return float(obs), float(p), null


# ---- t_tests.py lines 140-146
def power(make_planted, stat_fn, strata, alt):
    hits = 0
    for _ in range(NPLANT):
        t = make_planted()
        _, p, _ = perm_p(stat_fn, t, strata, NPERM_PLANT, alt)
        hits += p < 0.01
    return hits / NPLANT


# ---- t_tests.py lines 149-155
def plant_t1():
    t = tier1.copy()
    for d in np.unique(dep1):
        pr = rng.dirichlet(3 * marg)
        m = dep1 == d
        t[m] = rng.choice([2, 3, 4], size=m.sum(), p=pr)
    return t


# ---- t_tests.py lines 171-179
def plant_t3():
    t = tier3.copy()
    pref = rng.choice([2, 3, 4], size=len(top15))
    for i in range(len(t)):
        for j, f in enumerate(top15):
            if X3[i, f]:
                t[i] = pref[j] if rng.random() < 0.7 else rng.choice([2, 3, 4], p=marg)
                break
    return t
