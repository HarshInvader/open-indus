"""The four spelling-variation tests. Each takes a list of distinct texts (tuples) and
returns per-item statistics, so the identical code runs on synthetic controls and on
Indus dev / held-out."""
import math
from collections import Counter, defaultdict

import numpy as np
from scipy.stats import hypergeom, poisson

from common import bh, ed_le1, edit1_pairs, n_independent, one_two_pairs, poscls


def collapse(events, keyf, ctxf):
    """Keep one event per cluster of near-identical contexts (edit distance <=1)
    within each key. Removes near-copy families counted many times."""
    g = defaultdict(list)
    for e in events:
        g[keyf(e)].append(e)
    out = []
    for k, evs in g.items():
        reps = []
        for e in evs:
            c = ctxf(e)
            if not any(ed_le1(c, ctxf(r)) for r in reps):
                reps.append(e)
        out += reps
    return out


# =========================================================== T1 complements
def t1_events(texts, excluded, orient):
    _, ind = edit1_pairs(texts, minlen=2)
    ev = []
    for short, long, pos in ind:
        if len(short) < 2:
            continue
        x = long[pos]
        if excluded(x, pos):
            continue
        if orient == "prev":
            host = long[pos - 1] if pos > 0 else None
        else:
            host = long[pos + 1] if pos < len(long) - 1 else None
        if host is None:
            continue
        ev.append((x, host, poscls(pos, len(long)), short))
    return collapse(ev, lambda e: (e[0], e[1], e[2]), lambda e: e[3])


def t1_complements(texts, excluded, orient, nperm=20000, minev=4, seed=0):
    ev = t1_events(texts, excluded, orient)
    rng = np.random.default_rng(seed)
    if not ev:
        return {"n_events": 0, "items": []}
    xs = sorted({e[0] for e in ev}); hs = sorted({e[1] for e in ev})
    xi = {x: i for i, x in enumerate(xs)}; hi = {h: i for i, h in enumerate(hs)}
    X = np.array([xi[e[0]] for e in ev]); Hh = np.array([hi[e[1]] for e in ev])
    strata = defaultdict(list)
    for k, e in enumerate(ev):
        strata[e[2]].append(k)
    strata = [np.array(v) for v in strata.values()]
    nx = np.bincount(X, minlength=len(xs))

    def stat(Xl):
        M = np.zeros((len(xs), len(hs)))
        np.add.at(M, (Xl, Hh), 1)
        return (M ** 2).sum(1) / np.maximum(nx, 1), M
    obs, M = stat(X)
    test = [i for i in range(len(xs)) if nx[i] >= minev]
    ge = np.zeros(len(xs))
    for _ in range(nperm):
        Xp = X.copy()
        for s in strata:
            Xp[s] = X[s][rng.permutation(len(s))]
        st, _ = stat(Xp)
        ge += st >= obs - 1e-9
    p = (ge + 1) / (nperm + 1)
    items = []
    for i in test:
        row = M[i]; top = np.argsort(-row)[:3]
        items.append({"sign": xs[i], "n": int(nx[i]), "stat": float(obs[i]), "p": float(p[i]),
                      "top_hosts": [(hs[j], int(row[j])) for j in top if row[j] > 0]})
    return {"n_events": len(ev), "items": items}


# =========================================================== T2 transitivity
def frames(texts, minlen=3):
    F = defaultdict(set); meta = {}
    for t in texts:
        if len(t) < minlen:
            continue
        for i in range(len(t)):
            k = (t[:i], t[i + 1:])
            F[k].add(t[i])
            meta[k] = ((t[i - 1] if i else "^"), (t[i + 1] if i < len(t) - 1 else "$"), poscls(i, len(t)))
    keys = [k for k in F if len(F[k]) >= 2]
    return [(k, F[k], meta[k]) for k in keys]


def pair_contexts(fr):
    P = defaultdict(set)
    for k, fill, (l, r, s) in fr:
        f = sorted(fill)
        for a in range(len(f)):
            for b in range(a + 1, len(f)):
                P[(f[a], f[b])].add((l, r, s))
    return {k: len(v) for k, v in P.items()}


def curveball(sets, strata_idx, rng, steps_mult=5):
    sets = [set(s) for s in sets]
    for idx in strata_idx:
        if len(idx) < 2:
            continue
        for _ in range(steps_mult * len(idx)):
            a, b = rng.choice(idx, 2, replace=False)
            A, B = sets[a], sets[b]
            ua, ub = list(A - B), list(B - A)
            if not ua or not ub:
                continue
            pool = ua + ub; rng.shuffle(pool)
            na = len(ua)
            sets[a] = (A & B) | set(pool[:na]); sets[b] = (A & B) | set(pool[na:])
    return sets


def t2_transitivity(texts, nnull=500, seed=0, kmin=2):
    rng = np.random.default_rng(seed)
    fr = frames(texts)
    obs = pair_contexts(fr)
    sets = [f for _, f, _ in fr]
    st = defaultdict(list)
    for i, (_, _, (l, r, s)) in enumerate(fr):
        st[s].append(i)
    st = [np.array(v) for v in st.values()]
    tested = [k for k, v in obs.items() if v >= kmin]
    ge = Counter(); n_multi_null = []; lam = Counter()
    for _ in range(nnull):
        ns = curveball(sets, st, rng)
        frn = [(fr[i][0], ns[i], fr[i][2]) for i in range(len(fr))]
        nk = pair_contexts(frn)
        n_multi_null.append(sum(1 for v in nk.values() if v >= kmin))
        for k in tested:
            lam[k] += nk.get(k, 0)
            if nk.get(k, 0) >= obs[k]:
                ge[k] += 1
    p_emp = {k: (ge[k] + 1) / (nnull + 1) for k in tested}
    # smoothed tail: Poisson with the null mean (permutation resolution alone cannot pass BH)
    p = {k: max(float(poisson.sf(obs[k] - 1, max(lam[k] / nnull, 1e-3))), 1e-12) for k in tested}
    q = dict(zip(tested, bh([p[k] for k in tested]))) if tested else {}
    n_multi = sum(1 for v in obs.values() if v >= kmin)
    return {"n_frames": len(fr), "n_pairs": len(obs), "n_multi_obs": n_multi,
            "n_multi_null_mean": float(np.mean(n_multi_null)), "n_multi_null_sd": float(np.std(n_multi_null)),
            "p_global": float((1 + sum(x >= n_multi for x in n_multi_null)) / (1 + nnull)),
            "pairs": {"%s|%s" % k: {"k": obs[k], "p": p[k], "p_emp": p_emp[k], "lam": lam[k] / nnull, "q": float(q[k])}
                      for k in tested},
            "all_k": {"%s|%s" % k: v for k, v in obs.items()}}


# =========================================================== T3 ligatures
def t3_events(texts):
    ev = one_two_pairs(texts, minctx=2)
    ev = [(A, BC, poscls(j, len(u)), u[:j] + ("_",) + u[j + 1:]) for u, t, j, A, BC in ev]
    # dedupe identical (A,BC,context)
    ev = list({(a, bc, s, c) for a, bc, s, c in ev})
    return collapse(ev, lambda e: (e[0], e[1]), lambda e: e[3])


def t3_ligatures(texts, minfam=2):
    ev = t3_events(texts)
    by_s = defaultdict(list)
    for e in ev:
        by_s[e[2]].append(e)
    trip = Counter((e[0], e[1]) for e in ev)
    res = []
    for (a, bc), k in trip.items():
        if k < minfam:
            continue
        # distribution of count under within-stratum permutation of A labels:
        # sum over strata of independent hypergeometrics, via convolution
        dist = np.array([1.0])
        for s, es in by_s.items():
            N = len(es); K = sum(1 for e in es if e[0] == a); n = sum(1 for e in es if e[1] == bc)
            if K == 0 or n == 0:
                continue
            pmf = hypergeom.pmf(np.arange(0, min(K, n) + 1), N, K, n)
            dist = np.convolve(dist, pmf)
        p = float(dist[k:].sum()) if k < len(dist) else 0.0
        res.append({"A": a, "B": bc[0], "C": bc[1], "k": k, "p": max(p, 1e-300),
                    "n_A": sum(1 for e in ev if e[0] == a), "n_BC": sum(1 for e in ev if e[1] == bc)})
    q = bh([r["p"] for r in res])
    for r, qq in zip(res, q):
        r["q"] = float(qq)
    res.sort(key=lambda r: r["p"])
    return {"n_events": len(ev), "n_triples_tested": len(res), "items": res}


# =========================================================== T4 determinatives
def t4_drops(texts, pairs):
    subs, _ = edit1_pairs(texts, minlen=3)
    ev = [(t1[pos], t2[pos], poscls(pos, len(t1)), t1[:pos] + ("_",) + t1[pos + 1:]) for t1, t2, pos in subs]
    ev = collapse(ev, lambda e: (frozenset(e[:2]), e[2]), lambda e: e[3])
    # partner share by slot (null for "who replaces a sign in this slot")
    part = defaultdict(Counter)
    for a, b, s, _ in ev:
        part[s][a] += 1; part[s][b] += 1
    out = []
    for base, mod in pairs:
        obs = sum(1 for a, b, s, _ in ev if {a, b} == {base, mod})
        E = 0.0; nmod = 0
        for a, b, s, _ in ev:
            if mod in (a, b):
                nmod += 1
                tot = sum(part[s].values()) - part[s][mod]
                E += part[s][base] / tot if tot else 0
        out.append({"base": base, "mod": mod, "obs": obs, "exp": E, "n_mod_subs": nmod,
                    "p_more": float(poisson.sf(obs - 1, E)) if E > 0 else (0.0 if obs else 1.0),
                    "p_never": float(poisson.pmf(0, E)) if obs == 0 else None})
    return out


# ---- T1b: local insertion events (h x y written in one text, h y in another)
def t1_local_events(texts, excluded, orient, wide=0):
    """orient='prev': host h precedes x; the event is (h, x, y) written in one text
    while (h, y) is written in another (x optional between h and y).
    orient='next': host follows x; event (y, x, h) with (y, h) attested.
    wide=1 additionally requires the sign on the far side of the host to match
    (g h x y vs g h y), i.e. a longer shared local context. Text edges (^, $) count
    as signs. One event per distinct (x, h, slot, context)."""
    grams = set()
    for t in texts:
        tt = ("^",) * 2 + t + ("$",) * 2
        for i in range(len(tt) - 2):
            grams.add(tt[i:i + 2]); grams.add(tt[i:i + 3])
    ev = set()
    for t in texts:
        tt = ("^",) * 2 + t + ("$",) * 2
        for i in range(2, len(tt) - 2):
            x = tt[i]
            if excluded(x, i - 2):
                continue
            if orient == "prev":
                g, h, y = tt[i - 2], tt[i - 1], tt[i + 1]
                if h == "^":
                    continue
                short = (g, h, y) if wide else (h, y)
            else:
                y, h, g = tt[i - 1], tt[i + 1], tt[i + 2]
                if h == "$":
                    continue
                short = (y, h, g) if wide else (y, h)
            if short in grams:
                ev.add((x, h, poscls(i - 2, len(t)), short))
    return sorted(ev)


def t1_local(texts, excluded, orient, nperm=5000, minev=5, seed=0, wide=0):
    ev = t1_local_events(texts, excluded, orient, wide)
    rng = np.random.default_rng(seed)
    xs = sorted({e[0] for e in ev}); hs = sorted({e[1] for e in ev})
    xi = {x: i for i, x in enumerate(xs)}; hi = {h: i for i, h in enumerate(hs)}
    X = np.array([xi[e[0]] for e in ev]); Hh = np.array([hi[e[1]] for e in ev])
    strata = defaultdict(list)
    for k, e in enumerate(ev):
        strata[e[2]].append(k)
    strata = [np.array(v) for v in strata.values()]
    nx = np.bincount(X, minlength=len(xs))
    test = np.array([i for i in range(len(xs)) if nx[i] >= minev])

    def stat(Xl):
        M = np.zeros((len(xs), len(hs)))
        np.add.at(M, (Xl, Hh), 1)
        return (M ** 2).sum(1) / np.maximum(nx, 1), M
    obs, M = stat(X)
    ge = np.zeros(len(xs))
    for _ in range(nperm):
        Xp = X.copy()
        for s in strata:
            Xp[s] = X[s][rng.permutation(len(s))]
        st, _ = stat(Xp)
        ge += st >= obs - 1e-9
    p = (ge + 1) / (nperm + 1)
    items = []
    for i in test:
        row = M[i]; top = np.argsort(-row)[:3]
        items.append({"sign": xs[i], "n": int(nx[i]), "stat": float(obs[i]), "p": float(p[i]),
                      "top_hosts": [(hs[j], int(row[j])) for j in top if row[j] > 0]})
    return {"n_events": len(ev), "items": items}
