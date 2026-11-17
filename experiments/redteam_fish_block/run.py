"""Red team of reg_findspot F3 (ticked fish cluster by block). Pre-reg: docs/prereg/redteam_fish_block.md

Run: .venv/bin/python experiments/redteam_fish_block/run.py   (writes run.log via stdout redirect, results.json)
"""
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from patsy import dmatrix
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from corpus.load import m77_lines, icit_texts  # noqa: E402

OUT = Path(__file__).resolve().parent
SEED = 20261115
NPERM = 10000
TF = {"M60", "M66", "M68", "M71", "M73"}
PF = {"M59", "M65", "M67", "M70", "M72"}
rng = np.random.default_rng(SEED)
R = {}


def log(*a):
    print(*a, flush=True)


# ---------------- data ----------------
d = pd.read_csv(ROOT / "experiments/reg_findspot/findspots.csv", dtype={"block": str, "room": str})
d = d[d.signs_all.notna() & (d.signs_all != "")].reset_index(drop=True)
d["sset"] = d.signs_all.str.split().apply(set)
d["seq"] = d.seq_side0.fillna("").str.split().apply(lambda s: [x for x in s if x != "|"])
d["tf"] = d.sset.apply(lambda s: bool(s & TF)).astype(float)
d["pf"] = d.sset.apply(lambda s: bool(s & PF)).astype(float)
d["dep"] = -d.depth  # ft below datum, positive


def units_A(df, minn=8, streets=True, other=True):
    u = np.where(df.block.notna(), df.block, np.where(df.kind == "street", "street", None)).astype(object)
    cnt = pd.Series(u[pd.notna(u)]).value_counts()
    big = set(cnt[cnt >= minn].index) - {"street"}
    out = []
    for x in u:
        if x is None:
            out.append(None)
        elif x == "street":
            out.append("street" if streets else None)
        elif x in big:
            out.append(x)
        else:
            out.append("other" if other else None)
    return np.array(out, object)


def gstat(feat, lab, nu):
    n1 = np.bincount(lab, weights=feat, minlength=nu)
    n = np.bincount(lab, minlength=nu).astype(float)
    p = feat.mean()
    e1, e0 = n * p, n * (1 - p)
    n0 = n - n1
    with np.errstate(divide="ignore", invalid="ignore"):
        g = np.where(n1 > 0, n1 * np.log(n1 / e1), 0).sum() + np.where(n0 > 0, n0 * np.log(n0 / e0), 0).sum()
    return 2 * g


def chi2stat(feat, lab, nu):
    n1 = np.bincount(lab, weights=feat, minlength=nu)
    n = np.bincount(lab, minlength=nu).astype(float)
    p = feat.mean()
    e1, e0 = n * p, n * (1 - p)
    m = n > 0
    return (((n1 - e1) ** 2 / e1)[m].sum() + (((n - n1) - e0) ** 2 / e0)[m].sum())


def maxres(feat, lab, nu):
    n1 = np.bincount(lab, weights=feat, minlength=nu)
    n = np.bincount(lab, minlength=nu).astype(float)
    e = n * feat.mean()
    return np.max((n1 - e) / np.sqrt(np.maximum(e, 1e-9)))


def perm_within(lab, strata, n):
    groups = [np.where(strata == s)[0] for s in np.unique(strata)]
    out = np.empty((n, len(lab)), dtype=lab.dtype)
    for r in range(n):
        x = lab.copy()
        for g in groups:
            if len(g) > 1:
                x[g] = lab[g][rng.permutation(len(g))]
        out[r] = x
    return out


def ptest(df, feat_col="tf", minn=8, streets=True, other=True, strata_col="band5", stat=gstat, nperm=NPERM,
          strat_stat=None):
    u = units_A(df, minn, streets, other)
    m = np.array([x is not None for x in u])
    lab = pd.factorize(u[m])[0]
    f = df[feat_col].to_numpy(float)[m]
    if strata_col is None:
        st = np.zeros(m.sum(), int)
    else:
        st = pd.factorize(df[strata_col].fillna(-1).to_numpy()[m])[0]
    nu = lab.max() + 1
    if strat_stat:  # sum of per-stratum G
        def S(l):
            return sum(gstat(f[st == s], pd.factorize(l[st == s])[0], nu) if f[st == s].sum() > 0 else 0
                       for s in np.unique(st))
    else:
        def S(l):
            return stat(f, l, nu)
    obs = S(lab)
    P = perm_within(lab, st, nperm)
    null = np.array([S(P[r]) for r in range(nperm)])
    p = (1 + (null >= obs - 1e-9).sum()) / (1 + nperm)
    return dict(stat=float(obs), null_mean=float(null.mean()), p=float(p), n=int(m.sum()), n_feat=int(f.sum()),
                n_units=int(nu))


def bh(ps):
    ps = np.asarray(ps, float); n = len(ps); o = np.argsort(ps); adj = np.empty(n); mm = 1.0
    for r in range(n - 1, -1, -1):
        mm = min(mm, ps[o[r]] * n / (r + 1)); adj[o[r]] = mm
    return adj


def holm(ps):
    ps = np.asarray(ps, float); o = np.argsort(ps); adj = np.empty(len(ps)); run = 0
    for r, i in enumerate(o):
        run = max(run, (len(ps) - r) * ps[i]); adj[i] = min(1, run)
    return adj


# ---------------- baseline ----------------
log("== baseline reproduction")
base = ptest(d)
R["baseline"] = base
log(base)

# ---------------- A1 depth ----------------
log("== A1 depth")
dd = d[d.dep.notna()]
# TF vs depth
X = sm.add_constant(dd.dep.to_numpy())
fit = sm.Logit(dd.tf.to_numpy(), X).fit(disp=0)
slope = fit.params[1]
null = []
y = dd.tf.to_numpy()
for _ in range(NPERM):
    null.append(np.corrcoef(rng.permutation(y), dd.dep)[0, 1])
r_obs = np.corrcoef(y, dd.dep)[0, 1]
null = np.array(null)
p_dep = (1 + (np.abs(null) >= abs(r_obs)).sum()) / (1 + NPERM)
tf_dep = dd[dd.tf == 1].dep
R["A1_tf_depth"] = dict(logit_slope_per_ft=float(slope), r_pointbiserial=float(r_obs), p_two=float(p_dep),
                        tf_depth_median=float(tf_dep.median()), all_depth_median=float(dd.dep.median()),
                        mannwhitney_p=float(stats.mannwhitneyu(tf_dep, dd[dd.tf == 0].dep).pvalue),
                        rate_by_band5={str(int(k)): [int(v.tf.sum()), int(len(v))] for k, v in dd.groupby("band5")})
log(R["A1_tf_depth"])
# M77 MD seals overall
L = pd.DataFrame(m77_lines())
L["lev"] = pd.to_numeric(L.level, errors="coerce")
md = L[(L.site == "Mohenjodaro") & (L.object_type == "seal")].groupby("text_no").agg(
    signs=("signs", lambda s: set(x for l in s for x in l)), lev=("lev", "first"), locus=("locus", "first")).reset_index()
md["tf"] = md.signs.apply(lambda s: bool(s & TF)).astype(float)
m2 = md[md.lev.notna()]
rr = stats.spearmanr(m2.lev.abs(), m2.tf)
R["A1_tf_depth_M77_MD"] = dict(n=int(len(m2)), n_tf=int(m2.tf.sum()), spearman=float(rr.statistic), p=float(rr.pvalue),
                               tf_median_depth=float(m2[m2.tf == 1].lev.abs().median()),
                               all_median_depth=float(m2.lev.abs().median()))
log(R["A1_tf_depth_M77_MD"])
# depth by block
uA = units_A(d)
d["uA"] = uA
g = d[d.uA.notna() & d.dep.notna()].groupby("uA")
R["A1_block_depth"] = {k: dict(n=int(len(v)), median=float(v.dep.median()), q25=float(v.dep.quantile(.25)),
                               q75=float(v.dep.quantile(.75)), tf=int(v.tf.sum())) for k, v in g}
R["A1_block_depth_KW_p"] = float(stats.kruskal(*[v.dep.to_numpy() for _, v in g]).pvalue)
for k, v in sorted(R["A1_block_depth"].items(), key=lambda kv: kv[1]["median"]):
    log(f"  unit {k:6s} n={v['n']:3d} depth med {v['median']:.1f} IQR {v['q25']:.1f}-{v['q75']:.1f} tf={v['tf']}")
log("  KW p", R["A1_block_depth_KW_p"])
# finer strata
d["band3"] = np.floor(d.dep / 3)
d["band2"] = np.floor(d.dep / 2)
d["band1"] = np.floor(d.dep / 1)
d["dec"] = pd.qcut(d.dep, 10, labels=False, duplicates="drop")
A1 = {}
for sc in ("band3", "band2", "band1", "dec"):
    A1[sc] = ptest(d, strata_col=sc)
A1["within_band5_sumG"] = ptest(d, strat_stat=True)
# spline covariate parametric bootstrap
mA = d.uA.notna() & d.dep.notna()
x = d[mA]
B = dmatrix("cr(dep, df=3)", {"dep": x.dep.to_numpy()}, return_type="dataframe")
lf = sm.Logit(x.tf.to_numpy(), B).fit(disp=0)
pr = lf.predict(B)
lab = pd.factorize(x.uA)[0]; nu = lab.max() + 1
obs = gstat(x.tf.to_numpy(), lab, nu)
sims = []
for _ in range(NPERM):
    ys = (rng.random(len(pr)) < pr).astype(float)
    sims.append(gstat(ys, lab, nu) if ys.sum() > 0 else 0)
sims = np.array(sims)
A1["spline_param_boot"] = dict(stat=float(obs), null_mean=float(sims.mean()),
                               p=float((1 + (sims >= obs - 1e-9).sum()) / (1 + NPERM)), n=int(len(x)))
# logistic: block fixed effect LR test with depth spline covariate
Xf = pd.concat([B, pd.get_dummies(x.uA, drop_first=True).astype(float).set_index(B.index)], axis=1)
try:
    lf2 = sm.Logit(x.tf.to_numpy(), Xf).fit(disp=0, method="bfgs", maxiter=2000)
    A1["logit_LR_block_given_spline"] = dict(LR=float(2 * (lf2.llf - lf.llf)), df=int(Xf.shape[1] - B.shape[1]),
                                             p_asym=float(stats.chi2.sf(2 * (lf2.llf - lf.llf), Xf.shape[1] - B.shape[1])))
except Exception as e:  # separation
    A1["logit_LR_block_given_spline"] = str(e)
R["A1"] = A1
for k, v in A1.items():
    log(" ", k, v)

# ---------------- A2 batches ----------------
log("== A2 batches / families")


def edit(a, b):
    m, n = len(a), len(b)
    D = np.arange(n + 1)
    for i in range(1, m + 1):
        prev, D[0] = D[0], i
        for j in range(1, n + 1):
            cur = D[j]
            D[j] = min(D[j] + 1, D[j - 1] + 1, prev + (a[i - 1] != b[j - 1]))
            prev = cur
    return int(D[n])


def tf_bigrams(seq):
    return {(seq[i - 1] if i > 0 else "^", s) for i, s in enumerate(seq) if s in TF}


v12 = d[(d.house_key == "12/V") & (d.tf == 1)]
A2 = {"house12V": [dict(serial=int(r.serial), room=r.room_key, depth=float(r.depth), seq=" ".join(r.seq),
                        dims=None) for r in v12.itertuples()]}
s12 = list(v12.seq)
A2["house12V_pairwise_edit"] = [[edit(a, b) for b in s12] for a in s12]
A2["house12V_tf_bigrams"] = [sorted(map(list, tf_bigrams(s))) for s in s12]
log(A2)


def families(df, strict):
    keep = np.ones(len(df), bool)
    nfam = 0
    fams = []
    for u, grp in df[df.tf == 1].groupby("uA"):
        idx = list(grp.index)
        parent = {i: i for i in idx}

        def f(i):
            while parent[i] != i:
                i = parent[i]
            return i
        for a in idx:
            for b in idx:
                if a < b:
                    sa, sb = df.seq[a], df.seq[b]
                    link = edit(sa, sb) <= 1 or (strict and (tf_bigrams(sa) & tf_bigrams(sb)))
                    if link:
                        parent[f(a)] = f(b)
        cl = {}
        for i in idx:
            cl.setdefault(f(i), []).append(i)
        for c in cl.values():
            nfam += 1
            if len(c) > 1:
                fams.append([(u, " ".join(df.seq[i])) for i in c])
            c = sorted(c, key=lambda i: (-(df.depth[i] if pd.notna(df.depth[i]) else -1e9)))  # shallowest first
            for i in c[1:]:
                keep[df.index.get_loc(i)] = False
    return keep, nfam, fams


dU = d[d.uA.notna()].copy()
for strict in (False, True):
    keep, nfam, fams = families(dU, strict)
    sub = dU[keep]
    res = ptest(sub)
    res.update(n_families=nfam, merged=fams)
    A2["collapse_strict" if strict else "collapse_editdist"] = res
    log(" strict" if strict else " edit<=1", res)
# global (not per-unit) duplicates check among all 21 TF texts
tft = d[d.tf == 1]
A2["all_tf_pairs_edit_le1"] = [(int(a.serial), int(b.serial), " ".join(a.seq), " ".join(b.seq))
                               for i, a in enumerate(tft.itertuples()) for b in list(tft.itertuples())[i + 1:]
                               if edit(a.seq, b.seq) <= 1]
A2["tf_bigram_counts"] = Counter(" ".join(b) for s in tft.seq for b in tf_bigrams(s)).most_common(10)
log(" pairs edit<=1:", A2["all_tf_pairs_edit_le1"], A2["tf_bigram_counts"])
R["A2"] = A2

# ---------------- A3 ----------------
log("== A3 multiplicity / variants / LOO / OCR")
t = json.load(open(ROOT / "experiments/reg_findspot/test.json"))
e = json.load(open(ROOT / "experiments/reg_findspot/explore.json"))
ps21 = [t["F1"][lv][el]["p_two"] for lv in ("house", "room") for el in ("opener", "closer", "core", "whole")]
ps21 += [t["F2"]["p_same_block"], t["F2"]["p_same_house"], t["F2"]["p_ddepth"]]
f3keys = list(t["F3"]["tests"])
ps21 += [t["F3"]["tests"][k]["p"] for k in f3keys]
i_tf = 11 + f3keys.index("TICKED_FISH|A_block")
psall = ps21 + [x["p_block"] for x in e["E2_scan"]] + [x["p_house"] for x in e["E2_scan"]] + \
    [e["E1_ticked_block_without_12V"][1], e["E1_plain_fish_block"][1]]
A3 = {"n21": len(ps21), "bh21": float(bh(ps21)[i_tf]), "holm21": float(holm(ps21)[i_tf]),
      "nall": len(psall), "bh_all": float(bh(psall)[i_tf]), "holm_all": float(holm(psall)[i_tf]),
      "bonf_all": min(1, base["p"] * len(psall))}
log(A3)
var = {}
var["pearson_chi2"] = ptest(d, stat=chi2stat)
var["max_std_residual"] = ptest(d, stat=maxres)
for mn in (5, 15, 20):
    var[f"minblock_{mn}"] = ptest(d, minn=mn)
var["no_streets"] = ptest(d, streets=False)
var["no_other"] = ptest(d, other=False)
var["no_depth_strata"] = ptest(d, strata_col=None)
A3["variants"] = var
for k, v in var.items():
    log(" ", k, v)
# LOHO
loho = {}
for h in sorted(d[(d.tf == 1) & d.house_key.notna()].house_key.unique()):
    loho[h] = ptest(d[d.house_key != h], nperm=5000)["p"]
A3["LOHO"] = loho
lobo = {}
for u in sorted(set(d.uA.dropna())):
    lobo[u] = ptest(d[d.uA != u], nperm=5000)["p"]
A3["LOBO"] = lobo
log(" LOHO", loho)
log(" LOBO", lobo)
A3["LOHO_max"] = max(loho.values()); A3["LOBO_max"] = max(lobo.values())
# drop both 12/V and block 12 entirely already in LOBO; drop 12/V + next top house
# OCR
junk = d.parse_flags.fillna("").str.contains("block_junk_stripped")
A3["ocr_junk_tf_serials"] = [int(s) for s in d[junk & (d.tf == 1)].serial]
A3["ocr_drop_junk"] = ptest(d[~junk])
d2 = d.copy()
d2.loc[junk & d2.findspot_raw.str.contains(r"area: i 3 /"), "block"] = "13"
d2.loc[junk & d2.findspot_raw.str.contains(r"area: I 9 /"), "block"] = "19"
d2.loc[junk & d2.findspot_raw.str.contains(r"area: i 1 7 /"), "block"] = "17"
A3["ocr_reassign_i_as_1"] = ptest(d2)
# all OCR-repaired house numerals among TF seals
A3["tf_parse_flags"] = {int(r.serial): r.parse_flags for r in d[d.tf == 1].itertuples() if pd.notna(r.parse_flags)}
log(" OCR", A3["ocr_junk_tf_serials"], A3["ocr_drop_junk"], A3["ocr_reassign_i_as_1"], A3["tf_parse_flags"])
R["A3"] = A3

# ---------------- A4 ----------------
log("== A4 coding")
A4 = {}
fish = d[(d.tf == 1) | (d.pf == 1)]
A4["conditional_on_fish"] = ptest(fish)
A4["n_fish_seals"] = int(len(fish))
log(" cond fish", A4["conditional_on_fish"])
# ICIT coding check
reg = pd.read_csv(ROOT / "experiments/old_registers/registers.csv", dtype=str)
fem = reg[reg.source == "Mackay1938_FEM"][["object_no", "icit_ids"]].dropna()
fem["serial"] = pd.to_numeric(fem.object_no, errors="coerce")
fem = fem.dropna(subset=["serial"]); fem["serial"] = fem.serial.astype(int)
icit = {x["id"]: x for x in icit_texts()}
WTF = {"W226", "W232", "W236", "W241"}
WPF = {"W220", "W231", "W233", "W235", "W240"}
rows = []
for r in fem.itertuples():
    ids = [i.strip() for i in str(r.icit_ids).split(";") if i.strip() in icit]
    if not ids:
        continue
    s = set(icit[ids[0]]["seq"])
    rows.append(dict(serial=r.serial, w_tf=bool(s & WTF), w_pf=bool(s & WPF), w_seq=" ".join(icit[ids[0]]["seq"])))
ic = pd.DataFrame(rows).merge(d[["serial", "tf", "pf", "seq_side0", "uA", "band5", "block", "kind"]], on="serial")
ct = pd.crosstab(ic.tf.astype(bool), ic.w_tf)
both_fish = ic[(ic.tf == 1) | (ic.pf == 1) | ic.w_tf | ic.w_pf]
agree = ((both_fish.tf == 1) == both_fish.w_tf).mean()
A4["icit_linked"] = int(len(ic))
A4["crosstab_M77tf_vs_Wtf"] = {f"{a}|{b}": int(ct.loc[a, b]) if a in ct.index and b in ct.columns else 0
                               for a in (False, True) for b in (False, True)}
A4["agreement_among_fish_seals"] = float(agree)
A4["n_fish_seals_icit"] = int(len(both_fish))
A4["disagreements"] = both_fish[(both_fish.tf == 1) != both_fish.w_tf][["serial", "seq_side0", "w_seq"]].to_dict("records")
ic2 = d.merge(ic[["serial", "w_tf"]], on="serial", how="inner")
ic2["wtf"] = ic2.w_tf.astype(float)
A4["icit_subset_M77coding"] = ptest(ic2, feat_col="tf")
A4["icit_subset_Wcoding"] = ptest(ic2, feat_col="wtf")
log(" ICIT", {k: A4[k] for k in ("icit_linked", "crosstab_M77tf_vs_Wtf", "agreement_among_fish_seals", "n_fish_seals_icit")})
log(" disagreements", A4["disagreements"])
log(" subset M77", A4["icit_subset_M77coding"], " W", A4["icit_subset_Wcoding"])
# contiguity in serial / text no / CISI
ser = d.serial.to_numpy()
tfi = np.where(d.tf == 1)[0]


def nn_gap(pos):
    pos = np.sort(pos)
    g = np.diff(pos)
    return np.mean(np.minimum(np.r_[np.inf, g], np.r_[g, np.inf]))


obs = nn_gap(ser[tfi])
null = np.array([nn_gap(ser[rng.choice(len(d), len(tfi), replace=False)]) for _ in range(NPERM)])
A4["serial_nn_gap"] = dict(obs=float(obs), null_mean=float(null.mean()),
                           p_lower=float((1 + (null <= obs).sum()) / (1 + NPERM)))
cis = reg[reg.source == "Mackay1938_FEM"][["object_no", "cisi"]].dropna()
cis["serial"] = pd.to_numeric(cis.object_no, errors="coerce")
cis = cis.dropna(subset=["serial"]); cis["serial"] = cis.serial.astype(int)
cis["cn"] = pd.to_numeric(cis.cisi.str.extract(r"M-(\d+)")[0], errors="coerce")
cc = d.merge(cis[["serial", "cn"]], on="serial").dropna(subset=["cn"])
ctf = cc[cc.tf == 1].cn.to_numpy()
obs = nn_gap(ctf)
null = np.array([nn_gap(cc.cn.to_numpy()[rng.choice(len(cc), len(ctf), replace=False)]) for _ in range(NPERM)])
A4["cisi_nn_gap"] = dict(n=int(len(cc)), n_tf=int(len(ctf)), cisi=sorted(map(int, ctf)), obs=float(obs),
                         null_mean=float(null.mean()), p_lower=float((1 + (null <= obs).sum()) / (1 + NPERM)))
log(" contiguity", A4["serial_nn_gap"], A4["cisi_nn_gap"])
R["A4"] = A4

# ---------------- A5 replication ----------------
log("== A5 replication")
A5 = {}


def rep_test(df, label):
    # df: columns tf, locus, lev
    df = df.copy()
    df["block"] = df.locus.astype(str)
    df["kind"] = "x"
    df["band5"] = np.floor(df.lev.abs() / 5)
    res = ptest(df, nperm=5000)
    # power: plant x6 rate in one unit with >=15 seals
    u = units_A(df)
    m = np.array([x is not None for x in u])
    lab = pd.factorize(u[m])[0]; nu = lab.max() + 1
    f0 = df.tf.to_numpy(float)[m]; st = pd.factorize(df.band5.fillna(-1).to_numpy()[m])[0]
    n = np.bincount(lab, minlength=nu); elig = np.where(n >= 15)[0]
    P = perm_within(lab, st, 1000)
    hits = 0
    for _ in range(200):
        uu = rng.choice(elig); f = f0.copy(); idx = np.where(lab == uu)[0]
        target = min(len(idx), int(round(6 * f0.mean() * len(idx))))
        need = target - int(f[idx].sum()); off = idx[f[idx] == 0]
        if need > 0:
            f[rng.choice(off, min(need, len(off)), replace=False)] = 1
        o = gstat(f, lab, nu); nl = np.array([gstat(f, P[r], nu) for r in range(1000)])
        hits += (1 + (nl >= o - 1e-9).sum()) / 1001 <= 0.05
    res["power_x6"] = hits / 200
    tab = pd.DataFrame({"u": u[m], "tf": f0}).groupby("u").tf.agg(["sum", "count"])
    res["units"] = {k: [int(r["sum"]), int(r["count"])] for k, r in tab.iterrows()}
    log(" ", label, res)
    return res


allS = L[L.object_type == "seal"].groupby(["text_no", "site"]).agg(
    signs=("signs", lambda s: set(x for l in s for x in l)), lev=("lev", "first"), locus=("locus", "first")).reset_index()
allS["tf"] = allS.signs.apply(lambda s: bool(s & TF)).astype(float)
mdn = allS[(allS.site == "Mohenjodaro") & ~allS.text_no.between(2000, 2999) & allS.locus.notna()]
A5["MD_nonFEM_M77locus"] = rep_test(mdn, "MD non-FEM")
hp = allS[(allS.site == "Harappa") & allS.locus.notna()]
A5["Harappa_M77locus"] = rep_test(hp, "Harappa")
A5["holm"] = list(map(float, holm([A5["MD_nonFEM_M77locus"]["p"], A5["Harappa_M77locus"]["p"]])))
# FEM via M77 locus (sanity: does coarse M77 locus already show it?)
fm = allS[allS.text_no.between(2000, 2999) & allS.locus.notna()]
A5["FEM_M77locus_sanity"] = rep_test(fm, "FEM by M77 locus")
# Chanhu-daro descriptive
ce = reg[reg.source == "Mackay1943_CE"].dropna(subset=["m77_text_no"]).copy()
ce["tn"] = ce.m77_text_no.astype(float).astype(int)
cs = allS.set_index("text_no")
ce["tf"] = ce.tn.map(lambda n: bool(cs.signs.get(n, set()) & TF) if n in cs.index else None)
ce["sq"] = ce.findspot.str.extract(r"(Sq\.\s*\d+/\w)")[0].str.replace(r"\s+", "", regex=True)
A5["Chanhudaro"] = dict(n=int(ce.tf.notna().sum()), n_tf=int((ce.tf == True).sum()),
                        tf_rows=ce[ce.tf == True][["object_no", "findspot", "depth_ft"]].to_dict("records"))
log(" Chanhu-daro", A5["Chanhudaro"])
# Vats: mound only
R["A5"] = A5

json.dump(R, open(OUT / "results.json", "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
log("done")
