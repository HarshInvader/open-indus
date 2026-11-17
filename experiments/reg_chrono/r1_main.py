"""reg_chrono pre-registered run: T1 sign/class trends, T2 opener vs closer turnover, T3 markers, T4 power.

.venv/bin/python experiments/reg_chrono/r1_main.py [--smoke] [--kind primary|block|mic|m77int|har_seal|har_nonseal]
--smoke shuffles rel globally before anything (code check only, outcome-free).
"""
import sys, json, argparse
from collections import Counter, defaultdict
import numpy as np
from scipy.stats import spearmanr, norm
sys.path.insert(0, __import__("os").path.dirname(__file__))
from rlib import (datasets, Perm, trend_stat, two_sided_p, bh, holm, role_map, ROLES, MARKERS, HERE)

ap = argparse.ArgumentParser()
ap.add_argument("--smoke", action="store_true")
ap.add_argument("--kind", default="primary")
ap.add_argument("--nperm", type=int, default=10000)
ap.add_argument("--nplant", type=int, default=200)
args = ap.parse_args()

MIN_SIGN = 8          # carrier units per sign per dataset for T1b
MIN_MARK = 5          # carrier units for a marker test
SEED = 20261114
rng = np.random.default_rng(SEED)

if args.kind in ("har_seal", "har_nonseal"):
    base = datasets("primary")["HAR_EH"]
    keep = (lambda u: u["type"] == "seal") if args.kind == "har_seal" else (lambda u: u["type"] != "seal")
    DS = {f"HAR_EH_{args.kind}": [u for u in base if keep(u)]}
else:
    DS = datasets(args.kind)

if args.smoke:
    for us in DS.values():
        r = rng.permutation([u["rel"] for u in us])
        for u, x in zip(us, r):
            u["rel"] = float(x)

RM = role_map()


def presence(units, items):
    return np.array([[1.0 if it in set(u["signs"]) else 0.0 for it in items] for u in units])


def zscore(obs, null):
    sd = null.std(0)
    sd[sd == 0] = np.inf
    return (obs - null.mean(0)) / sd


out = dict(kind=args.kind, smoke=args.smoke, nperm=args.nperm, datasets={})
sign_tests = []  # (ds, sign, n, obs, z, p)
class_tests = []
marker_tests = []
PM = {}

for name, us in DS.items():
    P = Perm(us, seed=SEED + len(name))
    NULL = P.perms(args.nperm)
    PM[name] = (P, NULL)
    res = dict(n_units=len(us), areas=dict(Counter(u["area"] for u in us)), types=dict(Counter(u["type"] for u in us)))
    # ---------------- T1a/T1b per-sign
    cnt = Counter(s for u in us for s in set(u["signs"]))
    signs = sorted([s for s, c in cnt.items() if c >= MIN_SIGN], key=lambda s: (-cnt[s], s))
    X = presence(us, signs)
    obs = trend_stat(X, P.cent)
    null = trend_stat(X, NULL)
    z = zscore(obs, null)
    p = two_sided_p(obs, null)
    # omnibus: sum z^2 vs its permutation distribution
    znull = zscore(null, null)
    om_obs = float((z ** 2).sum())
    om_null = (znull ** 2).sum(1)
    om_p = float((1 + (om_null >= om_obs).sum()) / (1 + len(om_null)))
    res["T1a_omnibus"] = dict(n_signs=len(signs), stat=om_obs, null_mean=float(om_null.mean()),
                              null_q95=float(np.quantile(om_null, 0.95)), p=om_p)
    for s, n_, o, zz, pp in zip(signs, X.sum(0), obs, z, p):
        sign_tests.append(dict(ds=name, sign=s, n=int(n_), shift=float(o), z=float(zz), p=float(pp)))
    res["_z"] = {s: float(zz) for s, zz in zip(signs, z)}
    # ---------------- T1c role classes (token share per text) + length
    C = np.zeros((len(us), len(ROLES)))
    for i, u in enumerate(us):
        for s in u["signs"]:
            r = RM.get(s, "NOUN")
            if r in ROLES:
                C[i, ROLES.index(r)] += 1
        C[i] /= max(1, len(u["signs"]))
    cobs = trend_stat(C, P.cent)
    cnull = trend_stat(C, NULL)
    cp = two_sided_p(cobs, cnull)
    cz = zscore(cobs, cnull)
    for r_, o, zz, pp, nn in zip(ROLES, cobs, cz, cp, (C > 0).sum(0)):
        if nn >= MIN_MARK:
            class_tests.append(dict(ds=name, cls=r_, n_texts=int(nn), shift=float(o), z=float(zz), p=float(pp)))
    L = np.array([len(u["signs"]) for u in us], float)
    lobs = float(np.corrcoef(L, P.cent)[0, 1])
    lnull = np.array([np.corrcoef(L, c)[0, 1] for c in NULL[:2000]])
    lp = float((1 + (np.abs(lnull) >= abs(lobs)).sum()) / (1 + len(lnull)))
    class_tests.append(dict(ds=name, cls="LENGTH", n_texts=len(us), shift=lobs, z=lobs / lnull.std(), p=lp))
    # ---------------- T3 markers
    for mk, fn in MARKERS.items():
        x = np.array([[1.0 if fn(u["signs"]) else 0.0] for u in us])
        n_ = int(x.sum())
        if n_ < MIN_MARK:
            marker_tests.append(dict(ds=name, marker=mk, n=n_, tested=False))
            continue
        o = trend_stat(x, P.cent)
        nl = trend_stat(x, NULL)
        marker_tests.append(dict(ds=name, marker=mk, n=n_, tested=True, shift=float(o[0]),
                                 z=float(zscore(o, nl)[0]), p=float(two_sided_p(o, nl)[0])))
    out["datasets"][name] = res

# BH across all sign tests (one family), BH across class tests, Holm across tested markers
q = bh([t["p"] for t in sign_tests]) if sign_tests else []
for t, qq in zip(sign_tests, q):
    t["q"] = float(qq)
q = bh([t["p"] for t in class_tests]) if class_tests else []
for t, qq in zip(class_tests, q):
    t["q"] = float(qq)
tm = [t for t in marker_tests if t["tested"]]
for t, qq in zip(tm, holm([t["p"] for t in tm])):
    t["holm"] = float(qq)

# replication across sites for any q<0.05 sign/class
names = list(DS)


def lookup(tests, key, val, ds):
    for t in tests:
        if t["ds"] == ds and t[key] == val:
            return t


for tests, key in ((sign_tests, "sign"), (class_tests, "cls"), (marker_tests, "marker")):
    for t in tests:
        if len(names) == 2 and t.get("p") is not None:
            other = lookup(tests, key, t[key], names[1 - names.index(t["ds"])])
            if other and other.get("p") is not None:
                t["other_site_z"] = other["z"]
                # one-sided p in same direction ~ half the two-sided p if same sign
                t["replicates"] = bool(np.sign(other["z"]) == np.sign(t["z"]) and other["p"] / 2 < 0.05)

out["T1b_signs"] = sorted(sign_tests, key=lambda t: t["p"])
out["T1c_classes"] = class_tests
out["T3_markers"] = marker_tests
out["n_tests"] = dict(T1b=len(sign_tests), T1c=len(class_tests), T3=len(tm))

# ---------------- T1d cross-site agreement of per-sign z
if len(names) == 2:
    za, zb = out["datasets"][names[0]]["_z"], out["datasets"][names[1]]["_z"]
    shared = sorted(set(za) & set(zb))
    if len(shared) >= 8:
        rho = spearmanr([za[s] for s in shared], [zb[s] for s in shared])[0]
        # null: permuted z of dataset B (from its permutation matrix), 2000 draws
        P_b, N_b = PM[names[1]]
        us_b = DS[names[1]]
        Xb = presence(us_b, shared)
        nb = trend_stat(Xb, N_b[:2000])
        zb_null = zscore(nb, trend_stat(Xb, N_b))
        rn = np.array([spearmanr([za[s] for s in shared], r)[0] for r in zb_null])
        out["T1d_crosssite"] = dict(n_shared=len(shared), rho=float(rho),
                                    p_one_sided=float((1 + (rn >= rho).sum()) / (1 + len(rn))))
    # half_life Harappa markers -> MD_FEM (direction prediction)
    late, early = ["M127", "M387", "M197", "M341", "M72", "M293"], ["M12", "M375", "M205", "M347"]
    md = names[0]
    us = DS[md]
    P, NULL = PM[md]
    items = [s for s in late + early]
    X = presence(us, items)
    have = X.sum(0) > 0
    w = np.array([1.0 / max(1, have[:len(late)].sum())] * len(late) + [-1.0 / max(1, have[len(late):].sum())] * len(early))
    w = w * have
    zo = zscore(trend_stat(X, P.cent), trend_stat(X, NULL))
    zn = zscore(trend_stat(X, NULL), trend_stat(X, NULL))
    zo = np.nan_to_num(zo)
    zn = np.nan_to_num(zn)
    so, sn = float(zo @ w), zn @ w
    out["T1e_halflife_markers_on_MD"] = dict(n_carriers={s: int(c) for s, c in zip(items, X.sum(0))}, stat=so,
                                             p_one_sided=float((1 + (sn >= so).sum()) / (1 + len(sn))))


# ---------------- T2 opener vs closer turnover (stratified G, deep vs shallow halves)
def slot_arrays(us):
    ok = [i for i, u in enumerate(us) if "#" not in u["seq"] and len([s for s in u["seq"] if s != "|"]) >= 2]
    first, last = [], []
    for i in ok:
        s = [x for x in us[i]["seq"] if x != "|"]
        first.append(s[0]); last.append(s[-1])
    return np.array(ok), first, last


def G_strat(codes, strata, half):
    """sum over strata of G for 2 x K table (half x code)."""
    G = 0.0
    for st in np.unique(strata):
        m = strata == st
        c, h = codes[m], half[m]
        K = c.max() + 1
        tab = np.zeros((2, K))
        np.add.at(tab, (h, c), 1)
        tab = tab[:, tab.sum(0) > 0]
        E = tab.sum(1, keepdims=True) * tab.sum(0, keepdims=True) / tab.sum()
        nz = tab > 0
        G += 2 * (tab[nz] * np.log(tab[nz] / E[nz])).sum()
    return G


def halves(rel, strata):
    h = np.zeros(len(rel), int)
    for st in np.unique(strata):
        m = np.where(strata == st)[0]
        h[m] = (rel[m] > np.median(rel[m])).astype(int)
    return h


def t2(us, P, nperm, first=None, last=None, idx=None):
    if idx is None:
        idx, first, last = slot_arrays(us)
    strata = np.array([us[i]["stratum"] for i in idx])
    fc = np.unique(first, return_inverse=True)[1]
    lc = np.unique(last, return_inverse=True)[1]
    rel = P.rel[idx]
    h = halves(rel, strata)
    go, gc = G_strat(fc, strata, h), G_strat(lc, strata, h)
    no, nc = [], []
    for _ in range(nperm):
        r = P.perm_rel()[idx]
        hh = halves(r, strata)
        no.append(G_strat(fc, strata, hh)); nc.append(G_strat(lc, strata, hh))
    no, nc = np.array(no), np.array(nc)
    zo, zc = (go - no.mean()) / no.std(), (gc - nc.mean()) / nc.std()
    zno, znc = (no - no.mean()) / no.std(), (nc - nc.mean()) / nc.std()
    D, Dn = zo - zc, zno - znc
    return dict(n_texts=len(idx), n_open_types=int(fc.max() + 1), n_close_types=int(lc.max() + 1),
                G_open=float(go), G_open_null=float(no.mean()), p_open=float((1 + (no >= go).sum()) / (1 + nperm)),
                G_close=float(gc), G_close_null=float(nc.mean()), p_close=float((1 + (nc >= gc).sum()) / (1 + nperm)),
                z_open=float(zo), z_close=float(zc), D=float(D),
                p_D_two_sided=float((1 + (np.abs(Dn) >= abs(D)).sum()) / (1 + nperm)))


out["T2_open_close"] = {}
for name, us in DS.items():
    P, _ = PM[name]
    out["T2_open_close"][name] = t2(us, P, 2000)

# ---------------- T4 planted power
power = {}
for name, us in DS.items():
    P, NULL = PM[name]
    NL = NULL[:2000]
    m_signs = out["datasets"][name]["T1a_omnibus"]["n_signs"]
    m_all = len(sign_tests)
    rel = P.rel
    pw = {}
    # (a) single planted sign
    for n_ in (10, 20, 40):
        for OR in (2, 3, 5):
            beta = np.log(OR) * 1.5
            hit_nom = hit_bonf = 0
            for k in range(args.nplant):
                key = rng.random(len(us)) ** (1.0 / np.exp(beta * rel))  # Efraimidis-Spirakis
                car = np.argsort(-key)[:n_]
                x = np.zeros((len(us), 1)); x[car] = 1
                o = trend_stat(x, P.cent); nl = trend_stat(x, NL)
                pp = two_sided_p(o, nl)[0]
                hit_nom += pp < 0.05
                hit_bonf += pp < 0.05 / m_all
            pw[f"sign_n{n_}_OR{OR}"] = dict(nominal=hit_nom / args.nplant, bonferroni_all=hit_bonf / args.nplant)
    # (b) omnibus: 20% of tested signs get OR-trend (random direction), carriers redrawn, n kept
    cnt = Counter(s for u in us for s in set(u["signs"]))
    signs = sorted([s for s, c in cnt.items() if c >= MIN_SIGN], key=lambda s: (-cnt[s], s))
    X0 = presence(us, signs)
    NLo = NULL[:1000]
    for OR in (1.5, 2, 3):
        beta = np.log(OR) * 1.5
        hits = 0
        nrep = 50
        for k in range(nrep):
            X = X0.copy()
            sel = rng.choice(len(signs), max(1, int(0.2 * len(signs))), replace=False)
            for j in sel:
                n_ = int(X0[:, j].sum())
                b = beta * rng.choice([-1, 1])
                key = rng.random(len(us)) ** (1.0 / np.exp(b * rel))
                X[:, j] = 0; X[np.argsort(-key)[:n_], j] = 1
            o = trend_stat(X, P.cent); nl = trend_stat(X, NLo)
            z = zscore(o, nl); zn = zscore(nl, nl)
            s_o, s_n = (z ** 2).sum(), (zn ** 2).sum(1)
            hits += ((1 + (s_n >= s_o).sum()) / (1 + len(s_n))) < 0.05
        pw[f"omnibus_20pct_OR{OR}"] = hits / nrep
    # (c) markers: planted trend at each marker's own n
    for t in marker_tests:
        if t["ds"] == name and t["tested"]:
            for OR in (2, 3):
                beta = np.log(OR) * 1.5
                hit = 0
                for k in range(args.nplant):
                    key = rng.random(len(us)) ** (1.0 / np.exp(beta * rel))
                    x = np.zeros((len(us), 1)); x[np.argsort(-key)[:t["n"]]] = 1
                    pp = two_sided_p(trend_stat(x, P.cent), trend_stat(x, NL))[0]
                    hit += pp < 0.05 / max(1, len(tm))
                pw[f"marker_{t['marker']}_OR{OR}_holmworst"] = hit / args.nplant
    # (d) T2 slot turnover plants: shallow-half tokens of q of the slot's types replaced by new variants w.p. f
    idx, first, last = slot_arrays(us)
    strata = np.array([us[i]["stratum"] for i in idx])
    h = halves(P.rel[idx], strata)
    for slot in ("open", "close"):
        for (qf, f) in ((0.3, 0.5), (0.5, 0.5), (0.3, 0.3)):
            hits = 0
            nrep = 40
            for k in range(nrep):
                src = list(first if slot == "open" else last)
                types = [t_ for t_, c in Counter(src).items() if c >= 3]
                chosen = set(rng.choice(types, max(1, int(qf * len(types))), replace=False))
                new = [s + "'" if (s in chosen and h[i] == 1 and rng.random() < f) else s for i, s in enumerate(src)]
                fr, la = (new, last) if slot == "open" else (first, new)
                r = t2(us, P, 300, first=fr, last=la, idx=idx)
                good = (r["D"] > 0) if slot == "open" else (r["D"] < 0)
                hits += good and r["p_D_two_sided"] < 0.05
            pw[f"T2_{slot}_q{qf}_f{f}"] = hits / nrep
    power[name] = pw
out["T4_power"] = power

for res in out["datasets"].values():
    res.pop("_z", None)
tag = ("smoke_" if args.smoke else "") + args.kind
json.dump(out, open(HERE / f"r1_{tag}.json", "w"), indent=1)
# compact print
print(json.dumps({k: v for k, v in out.items() if k not in ("T1b_signs",)}, indent=1)[:12000])
print("top signs:")
for t in out["T1b_signs"][:15]:
    print(t)
