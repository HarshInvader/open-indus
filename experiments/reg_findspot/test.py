"""Confirmatory tests F1-F3 of docs/prereg/reg_findspot.md.

Run: .venv/bin/python experiments/reg_findspot/test.py   (log: test.log, output: test.json)
"""
import itertools
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parent
SEED = 20261114
NPERM = 10000
NPERM_POW = 1000
NPLANT = 200

NUMERAL = {f"M{i}" for i in range(86, 122)} - {"M90", "M92", "M93"}
TICKED = {"M60", "M66", "M68", "M71", "M73"}
FEATURES = {"M267": {"M267"}, "M293": {"M293"}, "M391": {"M391"}, "NUMERAL": NUMERAL, "TICKED_FISH": TICKED}


def load():
    d = pd.read_csv(OUT / "findspots.csv", dtype={"block": str, "room": str})
    d = d[d.signs_all.notna() & (d.signs_all != "")].reset_index(drop=True)
    d["seq"] = d.seq_side0.fillna("").str.split()
    d["sset"] = d.signs_all.str.split().apply(set)
    d["room"] = d.room.astype(str).str.replace(r"\.0$", "", regex=True)
    d.loc[d.room_key.notna(), "room_key"] = d.block + "/" + d.house.fillna("-") + "/" + d.room
    return d


def elements(seq):
    s = [x for x in seq if x != "|"]
    op = s[0] if s and s[0] != "#" else None
    cl = s[-1] if s and s[-1] != "#" else None
    core = set(x for x in s[1:-1] if x != "#") if len(s) >= 3 else None
    return op, cl, core


def jacc(a, b):
    if not a or not b:
        return np.nan
    return len(a & b) / len(a | b)


def pair_sims(ops, cls, cores, wholes, pi, pj):
    o = np.array([np.nan if ops[i] is None or ops[j] is None else float(ops[i] == ops[j]) for i, j in zip(pi, pj)])
    c = np.array([np.nan if cls[i] is None or cls[j] is None else float(cls[i] == cls[j]) for i, j in zip(pi, pj)])
    k = np.array([np.nan if cores[i] is None or cores[j] is None else jacc(cores[i], cores[j]) for i, j in zip(pi, pj)])
    w = np.array([jacc(wholes[i], wholes[j]) for i, j in zip(pi, pj)])
    return {"opener": o, "closer": c, "core": k, "whole": w}


def perm_labels(lab, strata, n, rng):
    """n permutations of lab within strata -> array (n, len(lab))."""
    out = np.empty((n, len(lab)), dtype=lab.dtype)
    groups = [np.where(strata == s)[0] for s in np.unique(strata)]
    for r in range(n):
        x = lab.copy()
        for g in groups:
            x[g] = lab[g][rng.permutation(len(g))]
        out[r] = x
    return out


def tstat_many(S, sim):
    """S: (n, P) bool same-unit matrix; sim: (P,) with nan -> T per row."""
    v = ~np.isnan(sim)
    s = np.where(v, sim, 0.0)
    Sf = S[:, v].astype(float)
    sv = s[v]
    n_same = Sf.sum(1)
    n_diff = v.sum() - n_same
    m_same = (Sf @ sv) / np.maximum(n_same, 1)
    m_diff = ((1 - Sf) @ sv) / np.maximum(n_diff, 1)
    return m_same - m_diff


def two_sided(obs, null):
    pu = (1 + (null >= obs - 1e-12).sum()) / (1 + len(null))
    pl = (1 + (null <= obs + 1e-12).sum()) / (1 + len(null))
    return min(1.0, 2 * min(pu, pl)), pu, pl


def holm(ps):
    ps = np.asarray(ps, float)
    o = np.argsort(ps)
    adj = np.empty_like(ps)
    run = 0
    for r, i in enumerate(o):
        run = max(run, (len(ps) - r) * ps[i])
        adj[i] = min(1, run)
    return adj


def bh(ps):
    ps = np.asarray(ps, float)
    n = len(ps)
    o = np.argsort(ps)
    adj = np.empty_like(ps)
    m = 1.0
    for r in range(n - 1, -1, -1):
        i = o[r]
        m = min(m, ps[i] * n / (r + 1))
        adj[i] = m
    return adj


# ---------------- F1 ----------------
def f1_level(d, unitcol, rng, slotdist, include_identical=False, band="band5", do_power=True):
    x = d[d[unitcol].notna() & d[band].notna() & d.block.notna()].copy()
    x["stratum"] = x.block + "|" + x[band].astype(int).astype(str)
    keep = x.groupby("stratum")[unitcol].transform("nunique") >= 2
    x = x[keep].reset_index(drop=True)
    lab = pd.factorize(x[unitcol])[0]
    strata = pd.factorize(x.stratum)[0]
    pi, pj = [], []
    for s in np.unique(strata):
        idx = np.where(strata == s)[0]
        for a, b in itertools.combinations(idx, 2):
            if not include_identical and x.seq[a] == x.seq[b]:
                continue
            pi.append(a)
            pj.append(b)
    pi, pj = np.array(pi), np.array(pj)
    el = [elements(s) for s in x.seq]
    ops, cls, cores = [e[0] for e in el], [e[1] for e in el], [e[2] for e in el]
    wholes = list(x.sset)
    sims = pair_sims(ops, cls, cores, wholes, pi, pj)
    same_obs = lab[pi] == lab[pj]
    P = perm_labels(lab, strata, NPERM, rng)
    S = P[:, pi] == P[:, pj]
    res = {"n_seals": len(x), "n_units": int(lab.max() + 1), "n_strata": int(strata.max() + 1),
           "same_pairs": int(same_obs.sum()), "diff_pairs": int((~same_obs).sum())}
    for e, sim in sims.items():
        v = ~np.isnan(sim)
        obs = tstat_many(same_obs[None, :], sim)[0]
        null = tstat_many(S, sim)
        p, pu, pl = two_sided(obs, null)
        res[e] = dict(T=float(obs), mean_same=float(np.nanmean(sim[same_obs & v])) if (same_obs & v).any() else None,
                      mean_diff=float(np.nanmean(sim[~same_obs & v])), null_mean=float(null.mean()),
                      null_sd=float(null.std()), null_95=[float(np.quantile(null, .025)), float(np.quantile(null, .975))],
                      p_two=p, p_upper=pu, p_lower=pl, n_same_valid=int((same_obs & v).sum()))
        # leave-one-unit-out range of T
        loo = []
        for u in np.unique(lab[pi][same_obs]):
            m = (lab[pi] != u) & (lab[pj] != u)
            loo.append(tstat_many(same_obs[None, m], sim[m])[0])
        res[e]["loo_T_range"] = [float(min(loo)), float(max(loo))] if loo else None
    if not do_power:
        return res
    # power: planted household signatures (reuse null permutations, first NPERM_POW)
    Sp = S[:NPERM_POW]
    units = np.unique(lab)
    for q in (0.25, 0.5):
        for e in ("opener", "closer", "core", "whole"):
            hits = 0
            for _ in range(NPLANT):
                o2, c2, k2, w2 = list(ops), list(cls), [None if c is None else set(c) for c in cores], [set(w) for w in wholes]
                slot = {"opener": "op", "closer": "cl", "core": "med", "whole": "med"}[e]
                sig = {u: rng.choice(slotdist[slot][0], p=slotdist[slot][1]) for u in units}
                for i in range(len(x)):
                    if rng.random() >= q:
                        continue
                    g = sig[lab[i]]
                    if e == "opener" and o2[i] is not None:
                        o2[i] = g
                    elif e == "closer" and c2[i] is not None:
                        c2[i] = g
                    elif e in ("core", "whole") and k2[i]:
                        old = rng.choice(sorted(k2[i]))
                        k2[i] = (k2[i] - {old}) | {g}
                        w2[i] = (w2[i] - {old}) | {g}
                s2 = pair_sims(o2, c2, k2, w2, pi, pj)[e]
                obs = tstat_many(same_obs[None, :], s2)[0]
                null = tstat_many(Sp, s2)
                if two_sided(obs, null)[0] <= 0.05 / 8:
                    hits += 1
            res[e][f"power_q{q}"] = hits / NPLANT
    return res


def slot_distributions(d):
    from collections import Counter
    op, cl, med = Counter(), Counter(), Counter()
    for s in d.seq:
        o, c, k = elements(s)
        if o: op[o] += 1
        if c: cl[c] += 1
        if k: med.update(k)
    def dist(cn):
        k = sorted(cn)
        p = np.array([cn[x] for x in k], float)
        return k, p / p.sum()
    return {"op": dist(op), "cl": dist(cl), "med": dist(med)}


# ---------------- F2 ----------------
def is_plus1(long, short):
    if len(long) != len(short) + 1:
        return False
    for i in range(len(long)):
        if long[:i] + long[i + 1:] == short:
            return True
    return False


def f2(d, rng):
    seqs = [[s for s in q if s != "|"] for q in d.seq]
    pairs = []
    for a, b in itertools.combinations(range(len(d)), 2):
        A, B = seqs[a], seqs[b]
        if "#" in A or "#" in B:
            continue
        kind = None
        if A == B and len(A) >= 3:
            kind = "identical"
        elif len(A) == len(B) + 1 and len(B) >= 3 and is_plus1(A, B):
            kind = "plus1"
        elif len(B) == len(A) + 1 and len(A) >= 3 and is_plus1(B, A):
            kind = "plus1"
        if kind:
            pairs.append((a, b, kind))
    blk = d.block.where(d.block.notna(), None).to_numpy(object)
    hk = d.house_key.where(d.house_key.notna(), None).to_numpy(object)
    rk = d.room_key.where(d.room_key.notna(), None).to_numpy(object)
    dep = d.depth.to_numpy(float)
    pi = np.array([p[0] for p in pairs])
    pj = np.array([p[1] for p in pairs])

    def stats(perm):
        b, h, r, z = blk[perm], hk[perm], rk[perm], dep[perm]
        sb = sum(1 for i, j in zip(pi, pj) if b[i] is not None and b[i] == b[j])
        sh = sum(1 for i, j in zip(pi, pj) if h[i] is not None and h[i] == h[j])
        sr = sum(1 for i, j in zip(pi, pj) if r[i] is not None and r[i] == r[j])
        dd = np.abs(z[pi] - z[pj])
        return sb, sh, sr, float(np.nanmean(dd))
    ident = np.arange(len(d))
    obs = stats(ident)
    null = np.array([stats(rng.permutation(len(d))) for _ in range(NPERM)])
    pa = (1 + (null[:, 0] >= obs[0]).sum()) / (1 + NPERM)
    pb = (1 + (null[:, 1] >= obs[1]).sum()) / (1 + NPERM)
    pr = (1 + (null[:, 2] >= obs[2]).sum()) / (1 + NPERM)
    pc = two_sided(obs[3], null[:, 3])[0]
    # smallest count reaching p<0.05
    def minsig(col):
        for k in range(0, len(pairs) + 1):
            if (1 + (null[:, col] >= k).sum()) / (1 + NPERM) < 0.05:
                return k
        return None
    detail = []
    for a, b, kind in pairs:
        detail.append(dict(kind=kind, serials=[int(d.serial[a]), int(d.serial[b])],
                           m77=[int(d.m77_text_no[a]), int(d.m77_text_no[b])],
                           seqs=[" ".join(seqs[a]), " ".join(seqs[b])],
                           findspots=[d.findspot_raw[a], d.findspot_raw[b]],
                           blocks=[blk[a], blk[b]], houses=[hk[a], hk[b]], rooms=[rk[a], rk[b]],
                           depths=[None if np.isnan(dep[a]) else dep[a], None if np.isnan(dep[b]) else dep[b]]))
    sameblk = [x for x in detail if x["blocks"][0] is not None and x["blocks"][0] == x["blocks"][1]
               and None not in x["depths"]]
    dd_same = [abs(x["depths"][0] - x["depths"][1]) for x in sameblk]
    return dict(n_pairs=len(pairs), n_identical=sum(p[2] == "identical" for p in pairs),
                n_plus1=sum(p[2] == "plus1" for p in pairs),
                same_block=obs[0], same_block_null_mean=float(null[:, 0].mean()), p_same_block=pa,
                min_count_sig_block=minsig(0),
                same_house=obs[1], same_house_null_mean=float(null[:, 1].mean()), p_same_house=pb,
                min_count_sig_house=minsig(1),
                same_room=obs[2], same_room_null_mean=float(null[:, 2].mean()), p_same_room_exploratory=pr,
                mean_abs_ddepth=obs[3], ddepth_null_mean=float(np.nanmean(null[:, 3])), p_ddepth=pc,
                same_block_ddepths=dd_same,
                median_same_block_ddepth=float(np.median(dd_same)) if dd_same else None,
                pairs=detail)


# ---------------- F3 ----------------
def gstat_counts(feat, lab, nunits):
    n1 = np.bincount(lab, weights=feat, minlength=nunits)
    n = np.bincount(lab, minlength=nunits).astype(float)
    p = feat.sum() / len(feat)
    e1, e0 = n * p, n * (1 - p)
    n0 = n - n1
    with np.errstate(divide="ignore", invalid="ignore"):
        g = np.where(n1 > 0, n1 * np.log(n1 / e1), 0).sum() + np.where(n0 > 0, n0 * np.log(n0 / e0), 0).sum()
    return 2 * g


def f3(d, rng):
    feats = {k: d.sset.apply(lambda s, v=v: bool(s & v)).to_numpy(float) for k, v in FEATURES.items()}
    # level A
    unitA = np.where(d.block.notna(), d.block, np.where(d.kind == "street", "street", None))
    cnt = pd.Series(unitA).value_counts()
    big = set(cnt[(cnt >= 8)].index) - {"street"}
    uA = np.array([None if u is None else (u if u in big or u == "street" else "other") for u in unitA], object)
    mA = np.array([u is not None for u in uA])
    bandA = d.band5.fillna(-1).to_numpy()[mA]
    labA = pd.factorize(uA[mA])[0]
    # level B
    hk = d.house_key.to_numpy(object)
    hc = pd.Series(hk[pd.notna(hk)]).value_counts()
    okh = set(hc[hc >= 3].index)
    mB = np.array([h in okh for h in hk]) & d.band5.notna().to_numpy()
    labB = pd.factorize(hk[mB])[0]
    strB = pd.factorize(d.block.to_numpy(object)[mB] + "|" + d.band5.to_numpy()[mB].astype(str))[0]
    PA = perm_labels(labA, bandA, NPERM, rng)
    PB = perm_labels(labB, strB, NPERM, rng)
    out = {"levelA_units": {str(k): int(v) for k, v in pd.Series(uA[mA]).value_counts().items()},
           "levelA_n": int(mA.sum()), "levelB_n": int(mB.sum()), "levelB_houses": int(labB.max() + 1), "tests": {}}
    for k, f in feats.items():
        for lvl, m, lab, P in (("A_block", mA, labA, PA), ("B_house", mB, labB, PB)):
            fx = f[m]
            nu = lab.max() + 1
            obs = gstat_counts(fx, lab, nu)
            null = np.array([gstat_counts(fx, P[r], nu) for r in range(NPERM)])
            p = (1 + (null >= obs - 1e-9).sum()) / (1 + NPERM)
            # top unit
            n1 = np.bincount(lab, weights=fx, minlength=nu)
            n = np.bincount(lab, minlength=nu)
            names = pd.factorize(uA[mA] if lvl == "A_block" else hk[mB])[1]
            exp = n * fx.mean()
            top = int(np.argmax((n1 - exp) / np.sqrt(np.maximum(exp, 1e-9))))
            out["tests"][f"{k}|{lvl}"] = dict(G=float(obs), null_mean=float(null.mean()), p=float(p),
                                              n_feature=int(fx.sum()), n=int(len(fx)),
                                              top_unit=str(names[top]), top_obs=int(n1[top]), top_exp=float(exp[top]),
                                              top_n=int(n[top]))
    ks = list(out["tests"])
    q = bh([out["tests"][k]["p"] for k in ks])
    for k, qq in zip(ks, q):
        out["tests"][k]["q_bh"] = float(qq)
    # power: plant 3x M267 enrichment in one unit
    f = feats["M267"]
    for lvl, m, lab, P, minn in (("A_block", mA, labA, PA, 20), ("B_house", mB, labB, PB, 6)):
        fx0 = f[m]
        nu = lab.max() + 1
        n = np.bincount(lab, minlength=nu)
        elig = np.where(n >= minn)[0]
        base = fx0.mean()
        hits = 0
        for _ in range(NPLANT):
            u = rng.choice(elig)
            fx = fx0.copy()
            idx = np.where(lab == u)[0]
            target = min(len(idx), int(round(3 * base * len(idx))))
            off = idx[fx[idx] == 0]
            need = max(0, target - int(fx[idx].sum()))
            if need:
                fx[rng.choice(off, size=min(need, len(off)), replace=False)] = 1
            obs = gstat_counts(fx, lab, nu)
            null = np.array([gstat_counts(fx, P[r], nu) for r in range(NPERM_POW)])
            if (1 + (null >= obs - 1e-9).sum()) / (1 + NPERM_POW) <= 0.005:
                hits += 1
        out[f"power_M267_3x_{lvl}"] = hits / NPLANT
    return out


def main():
    rng = np.random.default_rng(SEED)
    d = load()
    sd = slot_distributions(d)
    res = {"n_text_seals": len(d)}
    print("F1 ...", flush=True)
    res["F1"] = {"house": f1_level(d, "house_key", rng, sd), "room": f1_level(d, "room_key", rng, sd)}
    ps = [res["F1"][lv][e]["p_two"] for lv in ("house", "room") for e in ("opener", "closer", "core", "whole")]
    pu = [res["F1"][lv][e]["p_upper"] for lv in ("house", "room") for e in ("opener", "closer", "core", "whole")]
    pl = [res["F1"][lv][e]["p_lower"] for lv in ("house", "room") for e in ("opener", "closer", "core", "whole")]
    for (lv, e), a, b, c in zip([(lv, e) for lv in ("house", "room") for e in ("opener", "closer", "core", "whole")],
                                holm(ps), holm(pu), holm(pl)):
        res["F1"][lv][e].update(holm_two=float(a), holm_upper=float(b), holm_lower=float(c))
    print("F1 sensitivity ...", flush=True)
    res["F1_sens"] = {"house_incl_identical": f1_level(d, "house_key", rng, sd, include_identical=True, do_power=False),
                      "house_band3": f1_level(d, "house_key", rng, sd, band="band3", do_power=False),
                      "room_band3": f1_level(d, "room_key", rng, sd, band="band3", do_power=False)}
    print("F2 ...", flush=True)
    res["F2"] = f2(d, rng)
    h = holm([res["F2"]["p_same_block"], res["F2"]["p_same_house"], res["F2"]["p_ddepth"]])
    res["F2"]["holm"] = dict(same_block=float(h[0]), same_house=float(h[1]), ddepth=float(h[2]))
    print("F3 ...", flush=True)
    res["F3"] = f3(d, rng)
    json.dump(res, open(OUT / "test.json", "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
    # print summary
    for lv in ("house", "room"):
        r = res["F1"][lv]
        print(f"F1 {lv}: n={r['n_seals']} units={r['n_units']} strata={r['n_strata']} same={r['same_pairs']} diff={r['diff_pairs']}")
        for e in ("opener", "closer", "core", "whole"):
            x = r[e]
            print(f"  {e:7s} same={x['mean_same']:.3f} diff={x['mean_diff']:.3f} T={x['T']:+.4f} null95={x['null_95']} "
                  f"p2={x['p_two']:.3f} holm={x['holm_two']:.3f} pow25={x['power_q0.25']} pow50={x['power_q0.5']} loo={x['loo_T_range']}")
    for k, r in res["F1_sens"].items():
        print("sens", k, {e: (round(r[e]["T"], 4), round(r[e]["p_two"], 3)) for e in ("opener", "closer", "core", "whole")})
    f = res["F2"]
    print(f"F2 pairs={f['n_pairs']} (ident {f['n_identical']}, +1 {f['n_plus1']}); same block {f['same_block']} vs {f['same_block_null_mean']:.2f} p={f['p_same_block']:.3f}; "
          f"same house {f['same_house']} vs {f['same_house_null_mean']:.2f} p={f['p_same_house']:.3f}; room {f['same_room']} vs {f['same_room_null_mean']:.2f}; "
          f"|dd| {f['mean_abs_ddepth']:.2f} vs {f['ddepth_null_mean']:.2f} p={f['p_ddepth']:.3f}; same-block dd {f['same_block_ddepths']}")
    for p in f["pairs"]:
        print("  ", p["kind"], p["seqs"], p["blocks"], p["houses"], p["rooms"], p["depths"])
    for k, t in res["F3"]["tests"].items():
        print(f"F3 {k:22s} G={t['G']:.2f} null={t['null_mean']:.2f} p={t['p']:.4f} q={t['q_bh']:.3f} n_feat={t['n_feature']}/{t['n']} top={t['top_unit']} {t['top_obs']}/{t['top_n']} exp {t['top_exp']:.2f}")
    print("F3 power", res["F3"]["power_M267_3x_A_block"], res["F3"]["power_M267_3x_B_house"])


if __name__ == "__main__":
    main()
