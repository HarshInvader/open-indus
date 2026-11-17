"""Confirmatory F1 and F3 of docs/prereg/reg_harappa.md (Harappa, Vats 1940 squares).

Statistics, nulls and planted-power code are imported unchanged from experiments/reg_findspot/test.py.
Run: .venv/bin/python experiments/reg_harappa/test.py   (log test.log via tee, output results.json)
Pass --explore to also run the exploratory variants (seals only, mound level, leave-one-out).
"""
import itertools
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments/reg_findspot"))
import test as RF  # noqa: E402  (reg_findspot/test.py: elements, pair_sims, perm_labels, tstat_many, two_sided, holm, bh, gstat_counts)

OUT = Path(__file__).resolve().parent
SEED = 20261116
NPERM, NPERM_POW, NPLANT = 10000, 1000, 200
FEATURES = dict(RF.FEATURES)
FEATURES.update({"M342": {"M342"}, "M99": {"M99"}, "M162": {"M162"}})
ORDER = ["TICKED_FISH", "M267", "M293", "M391", "NUMERAL", "M342", "M99", "M162"]
ELS = ("opener", "closer", "core", "whole")


def load(seals_only=False):
    d = pd.read_csv(OUT / "findspots.csv", dtype={"big_square": str})
    d = d[d.signs_all.notna() & (d.signs_all != "") & d.big_square.notna()].copy()
    d = d.sort_values("serial").drop_duplicates(["big_square", "seq_all"], keep="first")  # families
    if seals_only:
        d = d[d.object_type == "seal"]
    d = d.reset_index(drop=True)
    d["seq"] = d.seq_side0.fillna("").str.split()
    d["sset"] = d.signs_all.str.split().apply(set)
    d["mound"] = d.mound.fillna("none")
    d["sub_key"] = d.big_square + "/" + d.sub_square.astype(int).astype(str)
    return d


def f1_level(d, strat_cols, unitcol, rng, slotdist, do_power=True, band="band5"):
    x = d[d[band].notna()].copy()
    x["stratum"] = x[strat_cols[0]].astype(str) + "|" + x[band].astype(int).astype(str)
    x = x[x.groupby("stratum")[unitcol].transform("nunique") >= 2].reset_index(drop=True)
    lab = pd.factorize(x[unitcol])[0]
    strata = pd.factorize(x.stratum)[0]
    pi, pj = [], []
    for s in np.unique(strata):
        idx = np.where(strata == s)[0]
        for a, b in itertools.combinations(idx, 2):
            if x.seq[a] == x.seq[b]:
                continue
            pi.append(a)
            pj.append(b)
    pi, pj = np.array(pi), np.array(pj)
    el = [RF.elements(s) for s in x.seq]
    ops, cls, cores = [e[0] for e in el], [e[1] for e in el], [e[2] for e in el]
    wholes = list(x.sset)
    sims = RF.pair_sims(ops, cls, cores, wholes, pi, pj)
    same_obs = lab[pi] == lab[pj]
    P = RF.perm_labels(lab, strata, NPERM, rng)
    S = P[:, pi] == P[:, pj]
    res = {"n_families": len(x), "n_units": int(lab.max() + 1), "n_strata": int(strata.max() + 1),
           "same_pairs": int(same_obs.sum()), "diff_pairs": int((~same_obs).sum())}
    for e, sim in sims.items():
        v = ~np.isnan(sim)
        obs = RF.tstat_many(same_obs[None, :], sim)[0]
        null = RF.tstat_many(S, sim)
        p, pu, pl = RF.two_sided(obs, null)
        res[e] = dict(T=float(obs), mean_same=float(np.nanmean(sim[same_obs & v])) if (same_obs & v).any() else None,
                      mean_diff=float(np.nanmean(sim[~same_obs & v])), null_mean=float(null.mean()),
                      null_95=[float(np.quantile(null, .025)), float(np.quantile(null, .975))],
                      p_two=p, p_upper=pu, p_lower=pl, n_same_valid=int((same_obs & v).sum()))
        loo = []
        for u in np.unique(lab[pi][same_obs]):
            m = (lab[pi] != u) & (lab[pj] != u)
            loo.append(RF.tstat_many(same_obs[None, m], sim[m])[0])
        res[e]["loo_T_range"] = [float(min(loo)), float(max(loo))] if loo else None
    if not do_power:
        return res
    Sp = S[:NPERM_POW]
    units = np.unique(lab)
    for q in (0.25, 0.5):
        for e in ELS:
            hits = 0
            for _ in range(NPLANT):
                o2, c2 = list(ops), list(cls)
                k2 = [None if c is None else set(c) for c in cores]
                w2 = [set(w) for w in wholes]
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
                s2 = RF.pair_sims(o2, c2, k2, w2, pi, pj)[e]
                obs = RF.tstat_many(same_obs[None, :], s2)[0]
                null = RF.tstat_many(Sp, s2)
                if RF.two_sided(obs, null)[0] <= 0.05 / 8:
                    hits += 1
            res[e][f"power_q{q}"] = hits / NPLANT
    return res


def f3_setup(d):
    feats = {k: d.sset.apply(lambda s, v=FEATURES[k]: bool(s & v)).to_numpy(float) for k in ORDER}
    band = d.band5.fillna(-1).to_numpy()
    cnt = d.big_square.value_counts()
    big = set(cnt[cnt >= 8].index)
    uA = np.array([b if b in big else "other_" + m for b, m in zip(d.big_square, d.mound)], object)
    labA = pd.factorize(uA)[0]
    strA = pd.factorize(d.mound.to_numpy(object) + "|" + band.astype(str))[0]
    sc = d.sub_key.value_counts()
    okb = set(sc[sc >= 3].index)
    mB = np.array([k in okb for k in d.sub_key]) & d.band5.notna().to_numpy()
    labB = pd.factorize(d.sub_key.to_numpy(object)[mB])[0]
    strB = pd.factorize(d.big_square.to_numpy(object)[mB] + "|" + band[mB].astype(str))[0]
    namesA = pd.factorize(uA)[1]
    namesB = pd.factorize(d.sub_key.to_numpy(object)[mB])[1]
    return feats, dict(A_bigsquare=(np.ones(len(d), bool), labA, strA, namesA, 20, 15),
                       B_subsquare=(mB, labB, strB, namesB, 6, 5))


def f3(d, rng, do_power=True, nperm=NPERM):
    feats, levels = f3_setup(d)
    out = {"tests": {}, "levels": {}}
    perms = {}
    for lvl, (m, lab, st, names, mn3, mn4) in levels.items():
        perms[lvl] = RF.perm_labels(lab, st, nperm, rng)
        out["levels"][lvl] = dict(n=int(m.sum()), units=int(lab.max() + 1), strata=int(st.max() + 1),
                                  unit_sizes={str(names[i]): int(c) for i, c in enumerate(np.bincount(lab))})
    for k in ORDER:
        f = feats[k]
        for lvl, (m, lab, st, names, mn3, mn4) in levels.items():
            fx = f[m]
            nu = lab.max() + 1
            P = perms[lvl]
            obs = RF.gstat_counts(fx, lab, nu)
            null = np.array([RF.gstat_counts(fx, P[r], nu) for r in range(nperm)])
            p = (1 + (null >= obs - 1e-9).sum()) / (1 + nperm)
            n1 = np.bincount(lab, weights=fx, minlength=nu)
            n = np.bincount(lab, minlength=nu)
            exp = n * fx.mean()
            top = int(np.argmax((n1 - exp) / np.sqrt(np.maximum(exp, 1e-9)))) if fx.sum() else 0
            r = dict(G=float(obs), null_mean=float(null.mean()), p=float(p), n_feature=int(fx.sum()), n=int(len(fx)),
                     top_unit=str(names[top]), top_obs=int(n1[top]), top_exp=float(exp[top]), top_n=int(n[top]))
            if do_power:
                r.update(power_3x=plant(fx, lab, P, rng, "3x", mn3), power_md_cluster=plant(fx, lab, P, rng, "md4", mn4))
            out["tests"][f"{k}|{lvl}"] = r
    ks = list(out["tests"])
    for kk, qq in zip(ks, RF.bh([out["tests"][kk]["p"] for kk in ks])):
        out["tests"][kk]["q_bh"] = float(qq)
    return out


def plant(fx0, lab, P, rng, kind, minn):
    nu = lab.max() + 1
    n = np.bincount(lab, minlength=nu)
    elig = np.where(n >= minn)[0]
    if len(elig) == 0:
        return None
    base = fx0.mean()
    hits = 0
    for _ in range(NPLANT):
        u = rng.choice(elig)
        fx = fx0.copy()
        idx = np.where(lab == u)[0]
        off = idx[fx[idx] == 0]
        if kind == "3x":
            target = min(len(idx), int(round(3 * base * len(idx))))
            need = max(0, target - int(fx[idx].sum()))
        else:
            need = 4
        if need and len(off):
            fx[rng.choice(off, size=min(need, len(off)), replace=False)] = 1
        obs = RF.gstat_counts(fx, lab, nu)
        null = np.array([RF.gstat_counts(fx, P[r], nu) for r in range(NPERM_POW)])
        if (1 + (null >= obs - 1e-9).sum()) / (1 + NPERM_POW) <= 0.05 / 16:
            hits += 1
    return hits / NPLANT


def verdict_f3(t):
    pw = [x for x in (t.get("power_3x"), t.get("power_md_cluster")) if x is not None]
    if t["q_bh"] < 0.05:
        return "concentrated"
    if not pw or max(pw) < 0.5:
        return "inconclusive (power<0.5)"
    if max(pw) >= 0.8:
        return "null; plant excluded"
    return "null (power 0.5-0.8)"


def main():
    explore = "--explore" in sys.argv
    rng = np.random.default_rng(SEED)
    d = load()
    sd = RF.slot_distributions(d)
    res = {"n_families": len(d), "type_counts": d.object_type.value_counts().to_dict()}
    print("F1 ...", flush=True)
    res["F1"] = {"A_bigsquare": f1_level(d, ["mound"], "big_square", rng, sd),
                 "B_subsquare": f1_level(d, ["big_square"], "sub_key", rng, sd)}
    keys = [(lv, e) for lv in ("A_bigsquare", "B_subsquare") for e in ELS]
    for tail in ("two", "upper", "lower"):
        adj = RF.holm([res["F1"][lv][e][f"p_{tail}"] for lv, e in keys])
        for (lv, e), a in zip(keys, adj):
            res["F1"][lv][e][f"holm_{tail}"] = float(a)
    for lv in ("A_bigsquare", "B_subsquare"):
        r = res["F1"][lv]
        sig = any(r[e]["holm_upper"] < 0.05 or r[e]["holm_lower"] < 0.05 for e in ELS)
        r["replicates_MD_null"] = (not sig) and any(r[e]["power_q0.5"] >= 0.8 for e in ELS)
        for e in ELS:
            x = r[e]
            x["verdict"] = ("signature" if x["holm_upper"] < 0.05 else "distinctness" if x["holm_lower"] < 0.05 else
                            "no sharing; q=0.25 excluded" if x["power_q0.25"] >= 0.8 else
                            "no sharing; q=0.5 excluded" if x["power_q0.5"] >= 0.8 else "inconclusive")
    print("F3 ...", flush=True)
    res["F3"] = f3(d, rng)
    for k, t in res["F3"]["tests"].items():
        t["verdict"] = verdict_f3(t)
        if k.startswith("TICKED_FISH") and t["verdict"].startswith("inconclusive"):
            t["verdict"] = "untestable (too rare)"
    if explore:
        print("explore ...", flush=True)
        ex = {}
        s = load(seals_only=True)
        sds = RF.slot_distributions(s)
        ex["F1_seals_only"] = {"A_bigsquare": f1_level(s, ["mound"], "big_square", rng, sds, do_power=False),
                               "B_subsquare": f1_level(s, ["big_square"], "sub_key", rng, sds, do_power=False)}
        ex["F3_seals_only"] = f3(s, rng, do_power=False)
        ex["F1_band3"] = {"A_bigsquare": f1_level(d, ["mound"], "big_square", rng, sd, do_power=False, band="band3")}
        # mound level on all linked objects (families = identical text within mound)
        a = pd.read_csv(OUT / "findspots.csv")
        a = a[a.signs_all.notna() & a.mound.notna()].sort_values("serial").drop_duplicates(["mound", "seq_all"])
        a = a.reset_index(drop=True)
        a["sset"] = a.signs_all.str.split().apply(set)
        labM = pd.factorize(a.mound)[0]
        stM = pd.factorize(a.band5.fillna(-1))[0]
        PM = RF.perm_labels(labM, stM, NPERM, rng)
        mres = {"n": len(a), "mounds": a.mound.value_counts().to_dict()}
        for k in ORDER:
            fx = a.sset.apply(lambda z, v=FEATURES[k]: bool(z & v)).to_numpy(float)
            obs = RF.gstat_counts(fx, labM, labM.max() + 1)
            null = np.array([RF.gstat_counts(fx, PM[r], labM.max() + 1) for r in range(NPERM)])
            mres[k] = dict(G=float(obs), null_mean=float(null.mean()), n_feature=int(fx.sum()),
                           p=float((1 + (null >= obs - 1e-9).sum()) / (1 + NPERM)),
                           by_mound={m: [int(fx[a.mound == m].sum()), int((a.mound == m).sum())] for m in a.mound.unique()})
        ex["F3_mound_level"] = mres
        res["explore"] = ex
    json.dump(res, open(OUT / "results.json", "w"), indent=1,
              default=lambda o: o.item() if hasattr(o, "item") else str(o))
    for lv in ("A_bigsquare", "B_subsquare"):
        r = res["F1"][lv]
        print(f"F1 {lv}: n={r['n_families']} units={r['n_units']} strata={r['n_strata']} same={r['same_pairs']} "
              f"diff={r['diff_pairs']} replicates={r['replicates_MD_null']}")
        for e in ELS:
            x = r[e]
            print(f"  {e:7s} same={x['mean_same']:.3f} diff={x['mean_diff']:.3f} T={x['T']:+.4f} p2={x['p_two']:.3f} "
                  f"holm={x['holm_two']:.3f} pu={x['p_upper']:.3f} pl={x['p_lower']:.3f} pow25={x['power_q0.25']} "
                  f"pow50={x['power_q0.5']} loo={x['loo_T_range']} -> {x['verdict']}")
    for k, t in res["F3"]["tests"].items():
        print(f"F3 {k:24s} G={t['G']:.2f} null={t['null_mean']:.2f} p={t['p']:.4f} q={t['q_bh']:.3f} "
              f"feat={t['n_feature']}/{t['n']} top={t['top_unit']} {t['top_obs']}/{t['top_n']} exp {t['top_exp']:.2f} "
              f"pow3x={t.get('power_3x')} powMD={t.get('power_md_cluster')} -> {t['verdict']}")
    if explore:
        ex = res["explore"]
        for lv, r in ex["F1_seals_only"].items():
            print("seals F1", lv, r["n_families"], {e: (round(r[e]["T"], 4), round(r[e]["p_two"], 3)) for e in ELS})
        print("band3 F1", {e: (round(ex['F1_band3']['A_bigsquare'][e]['T'], 4), round(ex['F1_band3']['A_bigsquare'][e]['p_two'], 3)) for e in ELS})
        for k, t in ex["F3_seals_only"]["tests"].items():
            print(f"seals F3 {k:24s} p={t['p']:.4f} feat={t['n_feature']}/{t['n']}")
        for k in ORDER:
            t = ex["F3_mound_level"][k]
            print(f"mound F3 {k:12s} p={t['p']:.4f} {t['by_mound']}")


if __name__ == "__main__":
    main()
