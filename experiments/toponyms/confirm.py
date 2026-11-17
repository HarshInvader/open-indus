"""Toponym test: discovery -> frozen candidates -> confirmation.

Usage (repo root):
  .venv/bin/python experiments/toponyms/confirm.py dryrun   # D and C both inside discovery data
  .venv/bin/python experiments/toponyms/confirm.py final    # D = ICIT half A / M77 dev, C = ICIT half B / M77 held-out v2

Pre-registration: docs/prereg/toponyms.md (hash in docs/prereg/HASHES.txt).
"""
import sys
from common import *

MODE = sys.argv[1] if len(sys.argv) > 1 else "dryrun"
assert MODE in ("dryrun", "final")
MIN = {1: 5, 2: 4, 3: 4}
EXCL = {"Other sites", "West Asian finds", "Unknown"}
R_ENR, R_TRAV, R_POW = 2000, 5000, 300
BIG = {"Mohenjo-daro", "Harappa", "Mohenjodaro"}


def split_by_family(units, seed):
    ensure_families(units)
    roots = sorted(set(u["family"] for u in units))
    rng = random.Random(seed)
    rng.shuffle(roots)
    h = {r: k % 2 for k, r in enumerate(roots)}
    return [u for u in units if h[u["family"]] == 0], [u for u in units if h[u["family"]] == 1]


def datasets():
    out = {}
    if MODE == "final":
        sp = icit_split()
        out["ICIT"] = (sp["A"], sp["B"])
        out["M77"] = (m77_units("dev"), m77_units("heldout"))
    else:
        out["ICIT"] = split_by_family(icit_split()["A"], 7)
        out["M77"] = split_by_family(m77_units("dev"), 7)
    return out


def discover(D):
    E = collapse(D, "enrich")
    feats, X = feature_matrix(E, MIN)
    sites, obs, exp, p = enrichment(E, X, R=R_ENR)
    rows = []
    for j, f in enumerate(feats):
        for i, s in enumerate(sites):
            if s in EXCL or exp[i, j] <= 0:
                continue
            o, e = obs[i, j], exp[i, j]
            if o >= 3 and o / e >= 2 and p[i, j] < 0.05:
                occ = frozenset(np.where((X[:, j] == 1))[0])
                rows.append((p[i, j], -o / e, f, s, int(o), float(e), occ))
    rows.sort()
    kept, seen = [], set()
    for pp, r, f, s, o, e, occ in rows:
        if (s, occ) in seen:          # identical occurrence set = redundant n-gram
            continue
        seen.add((s, occ))
        kept.append(dict(feature=f, home=s, obs=o, exp=round(e, 2), ratio=round(o / e, 2), p=float(pp)))
    return kept, dict(n_units=len(E), n_features=len(feats),
                      n_tests=int(sum(1 for j in range(len(feats)) for i, s in enumerate(sites)
                                      if s not in EXCL and obs[i, j] >= 3)))


def enrich_replication(C, cands, R=R_ENR, seed=SEED + 1):
    """Pooled sum over candidates of (O_home - E_home) in C; null = site labels permuted
    within medium among C enrich-units."""
    E = collapse(C, "enrich")
    sites, slab = labels(E, "site")
    _, mlab = labels(E, "medium")
    six = {s: i for i, s in enumerate(sites)}
    cc = [c for c in cands if c["home"] in six]
    F = [unit_features(u) for u in E]
    X = np.array([[c["feature"] in fs for c in cc] for fs in F], dtype=np.int32).reshape(len(E), len(cc))
    home = np.array([six[c["home"]] for c in cc], dtype=int)

    def stat(lab):
        S = onehot(lab, len(sites))
        O = (S.T @ X)[home, np.arange(len(cc))]
        return O

    O = stat(slab)
    Ex = np.zeros(len(cc))
    for m in np.unique(mlab):
        ix = mlab == m
        Ex += (onehot(slab[ix], len(sites)).sum(0)[home] * X[ix].sum(0)) / ix.sum()
    obs_stat = float((O - Ex).sum())
    rng = np.random.default_rng(seed)
    null = np.array([float((stat(permute_within(slab, mlab, rng)) - Ex).sum()) for _ in range(R)])
    per = [dict(feature=c["feature"], home=c["home"], n_C=int(X[:, k].sum()), O=int(O[k]), E=round(float(Ex[k]), 2))
           for k, c in enumerate(cc)]
    n_attested = sum(1 for d in per if d["n_C"] > 0)
    return dict(stat=obs_stat, O=int(O.sum()), E=float(Ex.sum()),
                p=float((1 + (null >= obs_stat - 1e-9).sum()) / (R + 1)),
                null_mean=float(null.mean()), null_95=float(np.quantile(null, 0.95)),
                n_cands=len(cc), n_attested=n_attested, per_cand=per,
                ratio=float(O.sum() / Ex.sum()) if Ex.sum() else None), (E, X, slab, mlab, home, Ex, sites)


def enrich_power(pack, ratios=(1.5, 2.0, 3.0), R=R_POW, seed=SEED + 2, alpha=0.00625):
    """Planted answer: move each candidate's off-home occurrences to the home site
    (by swapping site labels with a random non-feature home unit of the same medium)
    until expected home share x ratio; rerun the test with a cheap 300-perm null."""
    E, X, slab, mlab, home, Ex, sites = pack
    rng = np.random.default_rng(seed)
    out = {}
    for r in ratios:
        hits = 0
        for _ in range(R // 10):
            lab = slab.copy()
            for k in range(X.shape[1]):
                occ = np.where(X[:, k] == 1)[0]
                if not len(occ):
                    continue
                target = min(len(occ), int(round(Ex[k] * r)))
                cur = int((lab[occ] == home[k]).sum())
                off = [i for i in occ if lab[i] != home[k]]
                rng.shuffle(off)
                for i in off[:max(0, target - cur)]:
                    pool = np.where((lab == home[k]) & (mlab == mlab[i]) & (X[:, k] == 0))[0]
                    if len(pool):
                        j = rng.choice(pool)
                        lab[i], lab[j] = lab[j], lab[i]
            def st(L):
                S = onehot(L, len(sites))
                return float(((S.T @ X)[home, np.arange(X.shape[1])] - Ex).sum())
            o = st(lab)
            nl = np.array([st(permute_within(lab, mlab, rng)) for _ in range(200)])
            hits += ((1 + (nl >= o - 1e-9).sum()) / 201) <= max(alpha, 1 / 201)
        out[str(r)] = hits / (R // 10)
    return out


def travel_power(T, cands, mobile, ors=(2, 3, 5), R=R_POW, seed=SEED + 3, alpha=0.00625):
    """Planted answer: start from the real media permuted within site (so no real
    signal), then give candidates' off-home units mobile status with odds = OR x site
    odds. Site mobile rates are recomputed from the planted data (the analysis treats
    it as real data). Detection = S1 p <= alpha under null A (200 perms/replicate)."""
    mob0 = np.array([u["medium"] in mobile for u in T], dtype=np.int8)
    sites_arr = np.array([u["site"] for u in T])
    _, slab = labels(T, "site")
    prate0 = site_mobile_rate(T, mobile)
    rng = np.random.default_rng(seed)
    out = {}
    for OR in ors:
        hits = 0
        for _ in range(R // 10):
            mob = permute_within(mob0, slab, rng)
            comp = travel_components(T, cands, mob, prate0)
            for c in comp:
                for i in c["oi"]:
                    p0 = min(max(prate0[T[i]["site"]], 1e-3), 1 - 1e-3)
                    od = OR * p0 / (1 - p0)
                    mob[i] = rng.random() < od / (1 + od)
            pr = {s: float(mob[sites_arr == s].mean()) for s in set(sites_arr)}
            for c in comp:
                c["E_off"] = sum(pr[T[i]["site"]] for i in c["oi"])
                c["E_home"] = sum(pr[T[i]["site"]] for i in c["hi"])
            o = travel_stats(comp, mob)["S1"]
            nl = np.array([travel_stats(comp, permute_within(mob, slab, rng))["S1"] for _ in range(200)])
            hits += ((1 + (nl >= o - 1e-9).sum()) / 201) <= max(alpha, 1 / 201)
        out[str(OR)] = hits / (R // 10)
    return out


def matched_null(T, cands, mobile, R=2000, seed=SEED + 4):
    """Null B: replace each candidate by a random non-candidate feature of similar
    frequency in T (+-50%, >=1 unit), keep the candidate's home site, recompute S1, S2."""
    prate = site_mobile_rate(T, mobile)
    mob = np.array([u["medium"] in mobile for u in T], dtype=np.int8)
    feats, X = feature_matrix(T, 1)
    cnt = X.sum(0)
    fi = {f: j for j, f in enumerate(feats)}
    candf = {c[0] for c in cands}
    obs = travel_stats(travel_components(T, cands, mob, prate), mob)
    rng = np.random.default_rng(seed)
    sites = np.array([u["site"] for u in T])
    pools = []
    for f, h in cands:
        n = cnt[fi[f]] if f in fi else 0
        lo, hi = max(1, int(n * 0.5)), max(2, int(np.ceil(n * 1.5)))
        pools.append([j for j in range(len(feats)) if lo <= cnt[j] <= hi and feats[j] not in candf])
    n1, n2 = np.zeros(R), np.zeros(R)
    for k in range(R):
        S1 = S2 = 0.0
        for (f, h), pool in zip(cands, pools):
            if not pool:
                continue
            j = pool[rng.integers(len(pool))]
            ix = np.where(X[:, j] == 1)[0]
            hi_ = ix[sites[ix] == h]
            oi = ix[sites[ix] != h]
            Eo = sum(prate[T[i]["site"]] for i in oi)
            Eh = sum(prate[T[i]["site"]] for i in hi_)
            oo, oh = mob[oi].sum(), mob[hi_].sum()
            S1 += oo - Eo
            if len(oi) and len(hi_):
                w = len(oi) * len(hi_) / (len(oi) + len(hi_))
                S2 += w * ((oo - Eo) / len(oi) - (oh - Eh) / len(hi_))
        n1[k], n2[k] = S1, S2
    return dict(S1=obs["S1"], S2=obs["S2"],
                p_S1=float((1 + (n1 >= obs["S1"] - 1e-9).sum()) / (R + 1)),
                p_S2=float((1 + (n2 >= obs["S2"] - 1e-9).sum()) / (R + 1)),
                null_S1_mean=float(n1.mean()), null_S2_mean=float(n2.mean()))


def reverse_test(T, R=2000, seed=SEED + 5):
    feats, X = feature_matrix(T, 3)
    obs_hits = reverse_count(T, X, feats)
    _, slab = labels(T, "site")
    _, mlab = labels(T, "medium")
    sites = np.array([u["site"] for u in T])
    rng = np.random.default_rng(seed)
    null = np.zeros(R)
    for k in range(R):
        perm = permute_within(np.arange(len(T)), mlab, rng)
        Tp = [dict(T[i], site=sites[perm[i]]) for i in range(len(T))]
        null[k] = len(reverse_count(Tp, X, feats))
    o = len(obs_hits)
    return dict(count=o, null_mean=float(null.mean()), null_95=float(np.quantile(null, 0.95)),
                p=float((1 + (null >= o).sum()) / (R + 1)),
                hits=[(f, str(s), [str(x) for x in g]) for f, s, g in obs_hits])


def signboard_test(R=5000, seed=SEED + 6):
    """A-priori signs from the Dholavira signboard (ICIT 144.1), full ICIT minus the
    signboard. Pooled Dholavira O-E over the 8 distinct signs, null = site labels
    permuted within medium (site-family units). Plus per-sign and the off-Dholavira
    mobile rate of those signs."""
    U = [u for u in icit_units() if u["id"] != "144.1"]
    E = collapse(U, "enrich")
    sites, slab = labels(E, "site")
    _, mlab = labels(E, "medium")
    d = sites.index("Dholavira")
    signs = sorted(set(SIGNBOARD))
    F = [unit_features(u, (1, 2)) for u in E]
    X = np.array([[s in fs for s in signs] for fs in F], dtype=np.int32)
    Ex = np.zeros(len(signs))
    for m in np.unique(mlab):
        ix = mlab == m
        Ex += (slab[ix] == d).sum() * X[ix].sum(0) / ix.sum()
    O = X[slab == d].sum(0)
    rng = np.random.default_rng(seed)
    null = np.array([float((X[permute_within(slab, mlab, rng) == d].sum(0) - Ex).sum()) for _ in range(R)])
    st = float((O - Ex).sum())
    # signboard bigrams anywhere else
    bis = [" ".join(SIGNBOARD[i:i + 2]) for i in range(len(SIGNBOARD) - 1)]
    bihits = {b: [(u["site"], u["medium"]) for u in U if b in unit_features(u, (2,))] for b in bis}
    per = [dict(sign=s, n=int(X[:, k].sum()), O_dholavira=int(O[k]), E=round(float(Ex[k]), 2)) for k, s in enumerate(signs)]
    return dict(stat=st, O=int(O.sum()), E=float(Ex.sum()),
                p=float((1 + (null >= st - 1e-9).sum()) / (R + 1)),
                p_depleted=float((1 + (null <= st + 1e-9).sum()) / (R + 1)),
                per_sign=per, bigrams_elsewhere=bihits)


def run():
    res = dict(mode=MODE)
    for name, (D, C) in datasets().items():
        print(f"\n===== {name}: D {len(D)} units, C {len(C)} units")
        cands, info = discover(D)
        print("discovery:", info, "candidates:", len(cands))
        for c in cands:
            print("   ", c)
        r = dict(discovery=info, candidates=cands)
        enr, pack = enrich_replication(C, cands)
        print("T1 enrichment replication:", {k: v for k, v in enr.items() if k != "per_cand"})
        r["T1_enrich"] = enr
        r["T1_power"] = enrich_power(pack)
        print("T1 power:", r["T1_power"])
        T = collapse(C, "travel")
        cl = [(c["feature"], c["home"]) for c in cands]
        for mob in ("primary", "broad"):
            tr = travel_test(T, cl, MOBILE[mob], R=R_TRAV)
            print(f"T2 travel [{mob}]:", {k: (round(v, 3) if isinstance(v, float) else v) for k, v in tr.items() if k != "per_cand"})
            r[f"T2_travel_{mob}"] = tr
        r["T2_power_primary"] = travel_power(T, cl, MOBILE["primary"])
        print("T2 power (primary, OR):", r["T2_power_primary"])
        r["T3_matched_null_primary"] = matched_null(T, cl, MOBILE["primary"])
        print("T3 matched null:", r["T3_matched_null_primary"])
        # small-site only candidates (MD/Harappa dominance control)
        cs = [x for x in cl if x[1] not in BIG]
        if cs:
            r["T2s_small_sites_primary"] = {k: v for k, v in travel_test(T, cs, MOBILE["primary"], R=R_TRAV).items() if k != "per_cand"}
            print("T2 small-site candidates:", r["T2s_small_sites_primary"])
        r["T4_reverse"] = reverse_test(T)
        print("T4 reverse:", {k: v for k, v in r["T4_reverse"].items() if k != "hits"})
        for h in r["T4_reverse"]["hits"]:
            print("   ", h)
        res[name] = r
    res["T5_signboard"] = signboard_test()
    print("\nT5 signboard:", res["T5_signboard"])
    jdump(res, HERE / f"confirm_{MODE}.json")


if __name__ == "__main__":
    run()
