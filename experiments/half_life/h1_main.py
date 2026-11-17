"""Half-life: P1-P4, persistence deficit, sensitivity and planted power (docs/prereg/half_life.md).
Run: cd experiments/half_life && ../../.venv/bin/python h1_main.py
"""
from hl_lib import *

rng = np.random.default_rng(20261115)
ROLE = lexicon_roles()
PRIMARY = ["HAR", "MD", "DHO", "KAL", "LOT", "HAR_VATS"]


def cls(x):
    return ROLE.get(x, (None, "UNM"))[1]


def sign_items(u):
    return u["signs"]


def class_strings(u, want):
    out = set()
    for r in runs(list(u["seq"])):
        cur = []
        for x in r + [None]:
            if x is not None and cls(x) == want:
                cur.append(x)
            else:
                if cur: out.add(want + ":" + "-".join(cur))
                cur = []
    return out


def string_items(u):
    return class_strings(u, "CORE") | class_strings(u, "FRAME")


def item_class(x):
    if ":" in x: return x.split(":")[0]
    return cls(x)


def drift_table(datasets, items_of, min_n, nperm):
    """rows: (dataset, item, class, n, D, Gobs, p_exact, shift)."""
    rows = []
    for k, U in datasets.items():
        if not U: continue
        items, Gobs, null, nn, C, E = drift_scores(U, items_of, nperm, rng, min_n=min_n)
        T = max(u["period"] for u in U) + 1
        rel = np.arange(T) / max(T - 1, 1)
        for i, x in enumerate(items):
            D = (Gobs[i] - null[:, i].mean()) / nn[i]
            p = (1 + (null[:, i] >= Gobs[i] - 1e-9).sum()) / (nperm + 1)
            shift = float((C[i] @ rel - E[i] @ rel) / nn[i])
            rows.append(dict(ds=k, item=x, cls=item_class(x), n=int(nn[i]), D=float(D), G=float(Gobs[i]), p=float(p), shift=shift))
    return rows


def contrast(rows, a="CORE", b="FRAME", nshuf=10000, nbins=5):
    """S = mean D(a) - mean D(b); null shuffles labels within dataset x frequency quintile."""
    R = [r for r in rows if r["cls"] in (a, b)]
    if not R or not any(r["cls"] == a for r in R) or not any(r["cls"] == b for r in R): return None
    D = np.array([r["D"] for r in R]); L = np.array([r["cls"] == a for r in R])
    strata = np.empty(len(R), dtype=object)
    for k in set(r["ds"] for r in R):
        idx = np.array([i for i, r in enumerate(R) if r["ds"] == k])
        ns = np.array([R[i]["n"] for i in idx])
        q = np.quantile(ns, np.linspace(0, 1, nbins + 1)[1:-1]) if len(idx) >= nbins else []
        b_ = np.searchsorted(q, ns, side="right")
        for i, bb in zip(idx, b_): strata[i] = f"{k}|{bb}"
    S = D[L].mean() - D[~L].mean()
    groups = [np.where(strata == s)[0] for s in np.unique(strata)]
    null = np.empty(nshuf)
    for j in range(nshuf):
        Lp = L.copy()
        for g in groups: Lp[g] = L[g][rng.permutation(len(g))]
        null[j] = D[Lp].mean() - D[~Lp].mean()
    p1 = (1 + (null >= S).sum()) / (nshuf + 1)
    p2 = (1 + (np.abs(null - null.mean()) >= abs(S - null.mean())).sum()) / (nshuf + 1)
    bs = [rng.choice(D[L], L.sum()).mean() - rng.choice(D[~L], (~L).sum()).mean() for _ in range(2000)]
    return dict(S=float(S), p_one=float(p1), p_two=float(p2), null_mean=float(null.mean()), null_sd=float(null.std()),
                n_a=int(L.sum()), n_b=int((~L).sum()), meanD_a=float(D[L].mean()), meanD_b=float(D[~L].mean()),
                ci95=[float(np.quantile(bs, .025)), float(np.quantile(bs, .975))])


# ---------------- persistence deficit (rarefied survival) ----------------
def recurrence(U, P, m, classes, reps, rng_):
    T = P.max() + 1
    out = {c: [] for c in classes}
    byp = [np.where(P == t)[0] for t in range(T)]
    for _ in range(reps):
        pres = []
        for t in range(T):
            s = rng_.choice(byp[t], m, replace=False)
            pres.append(set().union(*[U[i]["signs"] for i in s]))
        for c in classes:
            num = den = 0
            for t in range(T - 1):
                a = {x for x in pres[t] if cls(x) == c}
                den += len(a); num += len(a & pres[t + 1])
            out[c].append(num / den if den else np.nan)
    return {c: float(np.nanmean(v)) for c, v in out.items()}


def persistence(datasets, classes=("CORE", "FRAME", "NUM"), reps=50, nnull=40, nboot=60):
    res = {}
    for k, U in datasets.items():
        P = np.array([u["period"] for u in U]); OT = np.array([u["ot"] for u in U])
        m = min(Counter(P).values())
        if m < 8: continue
        obs = recurrence(U, P, m, classes, reps, rng)
        nul = [recurrence(U, P[strat_perm_idx(OT, rng)], m, classes, 5, rng) for _ in range(nnull)]
        nm = {c: float(np.nanmean([d[c] for d in nul])) for c in classes}
        boots = []
        for _ in range(nboot):
            idx = np.concatenate([rng.choice(np.where(P == t)[0], (P == t).sum()) for t in range(P.max() + 1)])
            Ub = [U[i] for i in idx]; Pb = P[idx]
            o = recurrence(Ub, Pb, m, classes, 5, rng)
            boots.append({c: o[c] - nm[c] for c in classes})
        res[k] = {c: dict(obs=obs[c], null=nm[c], deficit=obs[c] - nm[c],
                          ci95=[float(np.nanquantile([b[c] for b in boots], .025)), float(np.nanquantile([b[c] for b in boots], .975))])
                  for c in classes}
        res[k]["m_per_period"] = int(m)
        res[k]["core_minus_frame_deficit"] = res[k]["CORE"]["deficit"] - res[k]["FRAME"]["deficit"]
        cf = [b["CORE"] - b["FRAME"] for b in boots]
        res[k]["core_minus_frame_ci95"] = [float(np.nanquantile(cf, .025)), float(np.nanquantile(cf, .975))]
    return res


# ---------------- P3 cross-site chronology ----------------
def shifts(U, P, min_n=5):
    OT = np.array([u["ot"] for u in U]); T = P.max() + 1
    rel = P / max(T - 1, 1)
    exp_ot = {o: rel[OT == o].mean() for o in np.unique(OT)}
    resid = rel - np.array([exp_ot[o] for o in OT])
    acc = defaultdict(list)
    for i, u in enumerate(U):
        for x in u["signs"]: acc[x].append(resid[i])
    return {x: float(np.mean(v)) for x, v in acc.items() if len(v) >= min_n}


def p3(datasets, pairs, nperm=2000):
    from scipy.stats import spearmanr
    base = {k: np.array([u["period"] for u in datasets[k]]) for k in set(sum(map(list, pairs), []))}
    OTs = {k: np.array([u["ot"] for u in datasets[k]]) for k in base}

    def corr(Pd):
        sh = {k: shifts(datasets[k], Pd[k]) for k in base}
        out = {}
        for a, b in pairs:
            com = sorted(set(sh[a]) & set(sh[b]))
            if len(com) < 10: out[(a, b)] = (np.nan, len(com)); continue
            out[(a, b)] = (spearmanr([sh[a][x] for x in com], [sh[b][x] for x in com]).correlation, len(com))
        return out
    obs = corr(base)
    zobs = np.nanmean([np.arctanh(v[0]) for v in obs.values()])
    nullz, nullpair = [], defaultdict(list)
    for _ in range(nperm):
        Pd = {k: base[k][strat_perm_idx(OTs[k], rng)] for k in base}
        c = corr(Pd)
        nullz.append(np.nanmean([np.arctanh(v[0]) for v in c.values()]))
        for kk, v in c.items(): nullpair[kk].append(v[0])
    nullz = np.array(nullz)
    res = {"pooled_z": float(zobs), "pooled_r": float(np.tanh(zobs)), "p_one": float((1 + (nullz >= zobs).sum()) / (nperm + 1)), "pairs": {}}
    for kk, (r, n) in obs.items():
        nl = np.array(nullpair[kk])
        res["pairs"][f"{kk[0]}~{kk[1]}"] = dict(rho=float(r), n_shared=n, p_one=float((1 + (nl >= r).sum()) / (nperm + 1)))
    return res


# ---------------- planted power ----------------
def plant(datasets, f, mprob, rng_):
    out = {}
    for k, U in datasets.items():
        U = [dict(u, signs=set(u["signs"])) for u in U]
        n = Counter(x for u in U for x in u["signs"])
        cores = [x for x, c in n.items() if c >= 5 and cls(x) == "CORE"]
        chosen = set(x for x in cores if rng_.random() < f)
        T = max(u["period"] for u in U) + 1
        by = defaultdict(list)
        for i, u in enumerate(U): by[(u["period"], u["ot"])].append(i)
        for s in chosen:
            h = rng_.integers(T)
            for i, A in enumerate(U):
                if s not in A["signs"] or A["period"] == h or rng_.random() >= mprob: continue
                pool = by.get((h, A["ot"]), [])
                if not pool: continue
                for _ in range(10):
                    B = U[pool[rng_.integers(len(pool))]]
                    cand = [y for y in B["signs"] if y not in chosen and y not in A["signs"]]
                    if s in B["signs"] or not cand: continue
                    y = cand[rng_.integers(len(cand))]
                    A["signs"].discard(s); A["signs"].add(y); B["signs"].discard(y); B["signs"].add(s)
                    break
        out[k] = [dict(u, signs=frozenset(u["signs"])) for u in U]
    return out


def main():
    R = {}
    D = build_icit()
    D["HAR_VATS"] = build_m77_depth("Harappa")
    D["MD_M77"] = build_m77_depth("Mohenjodaro")
    prim = {k: D[k] for k in PRIMARY}

    # ---- P1 sign level
    rows = drift_table(prim, sign_items, 5, 1000)
    R["P1_sign"] = contrast(rows)
    R["per_class_meanD"] = {c: dict(n=len([r for r in rows if r["cls"] == c]), meanD=float(np.mean([r["D"] for r in rows if r["cls"] == c])))
                            for c in ("CORE", "FRAME", "NUM", "UNM") if any(r["cls"] == c for r in rows)}
    R["P1_by_dataset"] = {}
    for k in PRIMARY:
        R["P1_by_dataset"][k] = contrast([r for r in rows if r["ds"] == k], nshuf=2000)
    print("P1 sign-level:", R["P1_sign"]); print("  per class", R["per_class_meanD"])
    for k, v in R["P1_by_dataset"].items():
        if v: print(f"  {k}: S={v['S']:+.4f} core {v['meanD_a']:+.4f} (n={v['n_a']}) frame {v['meanD_b']:+.4f} (n={v['n_b']}) p1={v['p_one']:.3f} p2={v['p_two']:.3f}")

    # ---- P2 string level
    srows = drift_table(prim, string_items, 3, 1000)
    R["P2_string"] = contrast(srows)
    print("P2 string-level:", R["P2_string"])
    R["P2_desc"] = {}
    for k in PRIMARY:
        for c in ("CORE", "FRAME"):
            per = defaultdict(set)
            for u in prim[k]:
                for s in class_strings(u, c): per[s].add(u["period"])
            R["P2_desc"][f"{k}|{c}"] = dict(n_strings=len(per), share_multi_period=float(np.mean([len(v) > 1 for v in per.values()])) if per else None)
    print("  string desc", R["P2_desc"])

    ps = [R["P1_sign"]["p_one"], R["P2_string"]["p_one"]]
    o = np.argsort(ps); holm = [0, 0]
    holm[o[0]] = min(1, 2 * ps[o[0]]); holm[o[1]] = min(1, max(holm[o[0]], ps[o[1]]))
    R["holm_P1_P2"] = holm
    print("Holm P1,P2:", holm)

    # ---- persistence deficit
    R["persistence"] = persistence(prim)
    for k, v in R["persistence"].items():
        print(f"  persistence {k} (m={v['m_per_period']}): " + " ".join(f"{c} obs {v[c]['obs']:.3f} null {v[c]['null']:.3f} def {v[c]['deficit']:+.3f} [{v[c]['ci95'][0]:+.3f},{v[c]['ci95'][1]:+.3f}]" for c in ("CORE", "FRAME", "NUM")) + f" | core-frame {v['core_minus_frame_deficit']:+.3f} {v['core_minus_frame_ci95']}")

    # ---- P3
    pairs = [("HAR", "HAR_VATS"), ("HAR", "MD"), ("HAR_VATS", "MD")]
    R["P3"] = p3(D, pairs)
    print("P3:", R["P3"])
    R["P3_secondary_MD_M77"] = p3(D, [("HAR", "HAR_VATS"), ("HAR", "MD_M77"), ("HAR_VATS", "MD_M77")], nperm=1000)
    print("P3 (MD_M77):", R["P3_secondary_MD_M77"])

    # ---- P4 period-restricted signs
    rows4 = drift_table(prim, sign_items, 5, 5000)
    q = bh([r["p"] for r in rows4])
    for r, qq in zip(rows4, q): r["q"] = float(qq)
    byitem = defaultdict(dict)
    for r in rows4: byitem[r["item"]][r["ds"]] = r
    hits = []
    for r in sorted(rows4, key=lambda r: r["p"]):
        if r["q"] >= 0.10: continue
        rep = {k: dict(shift=round(v["shift"], 3), p=round(v["p"], 4)) for k, v in byitem[r["item"]].items() if k != r["ds"]}
        hits.append(dict(ds=r["ds"], sign=r["item"], cls=r["cls"], role=ROLE.get(r["item"], ("?",))[0], n=r["n"], p=r["p"], q=r["q"], shift=round(r["shift"], 3), other_datasets=rep))
    R["P4"] = dict(n_tests=len(rows4), hits_q10=hits, n_q05=int((q < 0.05).sum()), min_p=float(min(r["p"] for r in rows4)))
    print(f"P4: {len(rows4)} tests, {R['P4']['n_q05']} q<0.05")
    for h in hits: print("  ", h)
    R["P4_counts"] = {}
    for h in hits:
        U = prim[h["ds"]]; T = max(u["period"] for u in U) + 1
        c = [sum(1 for u in U if u["period"] == t and h["sign"] in u["signs"]) for t in range(T)]
        tot = [sum(1 for u in U if u["period"] == t) for t in range(T)]
        R["P4_counts"][f"{h['ds']}|{h['sign']}"] = dict(counts=c, period_sizes=tot)
        print("    counts", h["ds"], h["sign"], c, "of", tot)
    R["P4_power"] = {}
    m_tests = len(rows4)
    for k in PRIMARY:
        P = np.array([u["period"] for u in prim[k]]); share = max(Counter(P).values()) / len(P); smin = min(Counter(P).values()) / len(P)
        need_small = next((n for n in range(1, 200) if smin ** n <= 0.05 / m_tests), None)
        need_large = next((n for n in range(1, 400) if share ** n <= 0.05 / m_tests), None)
        R["P4_power"][k] = dict(period_sizes=sorted(Counter(P).items()), n_needed_if_all_in_smallest_period=need_small, n_needed_if_all_in_largest_period=need_large)
    print("P4 power:", R["P4_power"])

    # ---- sensitivity
    sens = {}
    seal = {k: [u for u in v if u["ot"] == "seal"] for k, v in prim.items()}
    seal = {k: v for k, v in seal.items() if len(set(u["period"] for u in v)) >= 2 and len(v) >= 30}
    for k, v in seal.items():
        ps_ = sorted(set(u["period"] for u in v)); mp = {p: i for i, p in enumerate(ps_)}
        seal[k] = [dict(u, period=mp[u["period"]]) for u in v]
    R["seal_datasets"] = {k: len(v) for k, v in seal.items()}
    sens["seals_only"] = contrast(drift_table(seal, sign_items, 5, 1000), nshuf=5000)
    alt = dict(prim); alt["MD"] = D["MD_M77"]
    sens["MD_M77_for_MD"] = contrast(drift_table(alt, sign_items, 5, 1000), nshuf=5000)
    h2 = dict(prim); h2["HAR"] = [dict(u, period=0 if u["period"] == 0 else 1) for u in prim["HAR"] if u["period"] != 1]
    sens["HAR_3B_vs_3C"] = contrast(drift_table(h2, sign_items, 5, 1000), nshuf=5000)
    sens["n_ge_10"] = contrast([r for r in rows if r["n"] >= 10], nshuf=5000)
    sens["string_seals_only"] = contrast(drift_table(seal, string_items, 3, 1000), nshuf=5000)
    sens["string_MD_M77_for_MD"] = contrast(drift_table(alt, string_items, 3, 1000), nshuf=5000)
    R["sensitivity"] = sens
    for k, v in sens.items():
        if v: print(f"  sens {k}: S={v['S']:+.4f} p1={v['p_one']:.3f} p2={v['p_two']:.3f} (core {v['n_a']}, frame {v['n_b']})")

    R["top_drift"] = {c: sorted([dict(ds=r["ds"], item=r["item"], n=r["n"], D=round(r["D"], 4), p=r["p"], shift=round(r["shift"], 3))
                                 for r in rows if r["cls"] == c], key=lambda d: -d["D"])[:8] for c in ("CORE", "FRAME", "NUM")}
    R["top_drift_strings"] = {c: sorted([dict(ds=r["ds"], item=r["item"], n=r["n"], D=round(r["D"], 4), p=r["p"], shift=round(r["shift"], 3))
                                         for r in srows if r["cls"] == c], key=lambda d: -d["D"])[:8] for c in ("CORE", "FRAME")}
    json.dump(R, open(OUT / "results.json", "w"), indent=1, default=float)

    # ---- planted power for P1
    pw = {}
    for f, mprob in [(0.5, 0.5), (1.0, 0.5), (0.5, 1.0)]:
        hitsP = []; Ss = []
        for rep in range(100):
            pl = plant(prim, f, mprob, rng)
            c = contrast(drift_table(pl, sign_items, 5, 200), nshuf=1000)
            hitsP.append(c["p_one"] < 0.05); Ss.append(c["S"])
        pw[f"f={f},m={mprob}"] = dict(power=float(np.mean(hitsP)), mean_S=float(np.mean(Ss)))
        print("power", f, mprob, pw[f"f={f},m={mprob}"])
    R["P1_power"] = pw

    json.dump(R, open(OUT / "results.json", "w"), indent=1, default=float)
    with open(OUT / "drift_signs.csv", "w") as fh:
        w = csv.writer(fh); w.writerow(["dataset", "sign", "class", "role", "n", "D", "G", "p_exact", "q_bh", "shift"])
        for r in sorted(rows4, key=lambda r: (r["ds"], r["p"])):
            w.writerow([r["ds"], r["item"], r["cls"], ROLE.get(r["item"], ("",))[0], r["n"], round(r["D"], 4), round(r["G"], 2), r["p"], round(r["q"], 4), round(r["shift"], 3)])


if __name__ == "__main__":
    main()
