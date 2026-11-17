"""fish_marshall: does the ticked-fish block clustering replicate on Marshall 1931 seals?
Pre-registration: docs/prereg/fish_marshall.md (+ amendment A1). Input: register.csv (register.py), prose_findspots.csv.
Run: .venv/bin/python experiments/fish_marshall/test.py  (writes results.json, test.log via stdout)
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from corpus.load import m77_lines  # noqa: E402

SEED = 20261115
NPERM = 10000
TF = {"M60", "M66", "M68", "M71", "M73"}
PF = {"M59", "M65", "M67", "M70", "M72"}
rng = np.random.default_rng(SEED)
OUT = {}


def log(*a):
    print(*a, flush=True)


# ---------------- data ----------------
R = pd.read_csv(HERE / "register.csv", dtype={"serial": str, "block_icit": str})
L = pd.DataFrame(m77_lines())
L = L[(L.text_no >= 1000) & (L.text_no < 2000)].sort_values(["text_no", "side", "line"])
seqs = L.groupby("text_no").signs.apply(lambda s: [x for l in s for x in l])
d = R[R.reliable & (R.object_type == "seal") & (R.site == "Mohenjodaro")].copy()
d["seq"] = d.text_no.map(seqs)
d = d[d.seq.apply(lambda s: isinstance(s, list) and len(s) > 0)].reset_index(drop=True)
d["sset"] = d.seq.apply(set)
d["tf"] = d.sset.apply(lambda s: bool(s & TF)).astype(float)
d["pf"] = d.sset.apply(lambda s: bool(s & PF)).astype(float)
d["depth"] = d.m77_depth.where(d.m77_depth.notna(), d.depth_B)
d["band5"] = np.floor(d.depth / 5)
d["stratum"] = d.area + "|" + d.band5.fillna(-1).astype(int).astype(str)
d["fnum"] = pd.to_numeric(d.field.str.extract(r"(\d+)")[0], errors="coerce")

# prose findspots (route b) for seals without an ICIT block
P = pd.read_csv(HERE / "prose_findspots.csv")
P = P[P.block.notna() & ~P.conflict]
pmap = {r.key: f"{(r.area or '')}{'-' + r.section if isinstance(r.section, str) else ''}/{int(float(r.block))}"
        for r in P.itertuples()}
d["block_prose"] = d.key.map(pmap)
# conflict between ICIT and prose block -> drop from U_block
conf = d.block_unit_icit.notna() & d.block_prose.notna() & (
    d.block_unit_icit.str.split("/").str[-1] != d.block_prose.str.split("/").str[-1])
d["block_raw"] = np.where(conf, None, d.block_unit_icit.where(d.block_unit_icit.notna(), d.block_prose))
OUT["n_seals_reliable"] = int(len(d))
OUT["n_tf"] = int(d.tf.sum())
OUT["n_pf"] = int(d.pf.sum())
OUT["icit_prose_block_conflicts"] = int(conf.sum())
log("reliable Marshall seals", len(d), "TF", int(d.tf.sum()), "PF", int(d.pf.sum()))


def pool_units(raw, area, minn=8):
    raw = pd.Series(raw, dtype=object)
    cnt = raw.value_counts()
    out = []
    for u, a in zip(raw, area):
        if u is None or (isinstance(u, float) and np.isnan(u)):
            out.append(None)
        elif cnt[u] >= minn:
            out.append(u)
        else:
            out.append(f"other-{a}")
    return np.array(out, dtype=object)


d["U_block"] = pool_units(d.block_raw.where(d.block_raw.notna(), None), d.area)


def fn_units(df, by_prefix=True, size=25):
    u = np.array([None] * len(df), dtype=object)
    for a, g in df[df.fnum.notna()].groupby("area"):
        key = [g.prefix, g.fnum] if by_prefix else [g.fnum]
        g = g.sort_values(["prefix", "fnum"] if by_prefix else ["fnum"])
        idx = list(g.index)
        n = len(idx)
        k = max(1, n // size)
        bounds = [i * size for i in range(k)] + [n]
        if n - bounds[-2] < 13 and k > 1:
            bounds = bounds[:-2] + [n]
        for j in range(len(bounds) - 1):
            for i in idx[bounds[j]:bounds[j + 1]]:
                u[df.index.get_loc(i)] = f"{a}#fn{j}"
    return u


d["U_fn"] = fn_units(d)
d["U_fn_numonly"] = fn_units(d, by_prefix=False)


# ---------------- statistic ----------------
def gstat(feat, lab, nu):
    n1 = np.bincount(lab, weights=feat, minlength=nu)
    n = np.bincount(lab, minlength=nu).astype(float)
    p = feat.mean()
    e1, e0 = n * p, n * (1 - p)
    n0 = n - n1
    with np.errstate(divide="ignore", invalid="ignore"):
        g = np.where(n1 > 0, n1 * np.log(n1 / e1), 0).sum() + np.where(n0 > 0, n0 * np.log(n0 / e0), 0).sum()
    return 2 * g


def perm_matrix(lab, strata, n):
    groups = [np.where(strata == s)[0] for s in np.unique(strata)]
    out = np.empty((n, len(lab)), dtype=lab.dtype)
    for r in range(n):
        x = lab.copy()
        for g in groups:
            if len(g) > 1:
                x[g] = lab[g][rng.permutation(len(g))]
        out[r] = x
    return out


def ptest(df, unit_col, feat_col="tf", nperm=NPERM, P=None):
    m = df[unit_col].notna().to_numpy()
    sub = df[m]
    lab = pd.factorize(sub[unit_col])[0]
    f = sub[feat_col].to_numpy(float)
    st = pd.factorize(sub.stratum)[0]
    nu = lab.max() + 1
    obs = gstat(f, lab, nu)
    if P is None:
        P = perm_matrix(lab, st, nperm)
    null = np.array([gstat(f, P[r], nu) for r in range(len(P))])
    p = (1 + (null >= obs - 1e-9).sum()) / (1 + len(P))
    tab = sub.groupby(unit_col)[feat_col].agg(["sum", "count"])
    return dict(G=float(obs), null_mean=float(null.mean()), p=float(p), n=int(m.sum()), n_feat=int(f.sum()),
                n_units=int(nu), units={k: [int(r["sum"]), int(r["count"])] for k, r in tab.iterrows()})


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


def feat_bigrams(seq, S):
    return {(seq[i - 1] if i > 0 else "^", s) for i, s in enumerate(seq) if s in S}


def collapse(df, unit_col, feat_col, S):
    """Family collapse within unit (redteam A2b strict): keep the shallowest seal of each family."""
    keep = np.ones(len(df), bool)
    fams = []
    sub = df[df[unit_col].notna() & (df[feat_col] == 1)]
    for u, grp in sub.groupby(unit_col):
        idx = list(grp.index)
        parent = {i: i for i in idx}

        def f(i):
            while parent[i] != i:
                i = parent[i]
            return i
        for a in idx:
            for b in idx:
                if a < b and (edit(df.seq[a], df.seq[b]) <= 1 or feat_bigrams(df.seq[a], S) & feat_bigrams(df.seq[b], S)):
                    parent[f(a)] = f(b)
        cl = {}
        for i in idx:
            cl.setdefault(f(i), []).append(i)
        for c in cl.values():
            if len(c) > 1:
                fams.append([(u, " ".join(df.seq[i])) for i in c])
            c = sorted(c, key=lambda i: (df.depth[i] if pd.notna(df.depth[i]) else 1e9))
            for i in c[1:]:
                keep[df.index.get_loc(i)] = False
    return df[keep], fams


# ---------------- decision rule ----------------
blk = d[d.U_block.notna()]
real_units = blk[~blk.U_block.str.startswith("other-")].U_block.value_counts()
rule = dict(n_block_seals=int(len(blk)), n_block_tf=int(blk.tf.sum()), n_units_ge8=int((real_units >= 8).sum()))
rule["U_block_primary"] = bool(rule["n_block_seals"] >= 120 and rule["n_block_tf"] >= 6 and rule["n_units_ge8"] >= 4)
PRIMARY = "U_block" if rule["U_block_primary"] else "U_fn"
SECOND = "U_fn" if PRIMARY == "U_block" else "U_block"
OUT["decision_rule"] = rule
OUT["primary_units"] = PRIMARY
log("decision rule", rule, "-> PRIMARY", PRIMARY)

# ---------------- primary ----------------
fam_d, fams = collapse(d, PRIMARY, "tf", TF)
OUT["tf_families_merged"] = fams
prim = ptest(fam_d, PRIMARY)
prim_raw = ptest(d, PRIMARY)
OUT["primary_family"] = prim
OUT["primary_noncollapsed"] = prim_raw
log("PRIMARY family-level", {k: v for k, v in prim.items() if k != "units"})
log("  units (tf, n):", prim["units"])
log("PRIMARY non-collapsed", {k: v for k, v in prim_raw.items() if k != "units"})

# ---------------- S1 plain fish ----------------
pf_d, pf_fams = collapse(d, PRIMARY, "pf", PF)
OUT["S1_plainfish_family"] = ptest(pf_d, PRIMARY, "pf")
OUT["S1_plainfish_noncollapsed"] = ptest(d, PRIMARY, "pf")
log("S1 plain fish family", {k: v for k, v in OUT["S1_plainfish_family"].items() if k != "units"})

# ---------------- S2 leave-one-unit-out ----------------
lobo = {}
for u in sorted(set(fam_d[(fam_d.tf == 1) & fam_d[PRIMARY].notna()][PRIMARY])):
    sub = fam_d[fam_d[PRIMARY] != u]
    lobo[u] = ptest(sub, PRIMARY, nperm=2000)["p"]
OUT["S2_leave_one_unit_out"] = lobo
OUT["S2_max_p"] = max(lobo.values()) if lobo else None
OUT["S2_min_p"] = min(lobo.values()) if lobo else None
log("S2 LOBO", lobo)

# ---------------- S3 other unit definition ----------------
sd, _ = collapse(d, SECOND, "tf", TF)
OUT["S3_" + SECOND + "_family"] = ptest(sd, SECOND)
if PRIMARY == "U_fn" or SECOND == "U_fn":
    nd, _ = collapse(d, "U_fn_numonly", "tf", TF)
    OUT["S3_U_fn_numonly_family"] = ptest(nd, "U_fn_numonly")
log("S3", SECOND, {k: v for k, v in OUT["S3_" + SECOND + "_family"].items() if k != "units"})

# ---------------- S4 area level ----------------
d["band_only"] = d.band5.fillna(-1).astype(int).astype(str)
tmp = d.copy(); tmp["stratum"] = tmp.band_only; tmp["area_u"] = tmp.area
OUT["S4_area_level"] = ptest(tmp, "area_u")
log("S4 area", {k: v for k, v in OUT["S4_area_level"].items()})

# ---------------- S5 Fisher combination (exploratory) ----------------
p_fem = 0.0056
chi = -2 * (np.log(prim["p"]) + np.log(p_fem))
OUT["S5_fisher_with_FEM_family_p"] = float(stats.chi2.sf(chi, 4))

# ---------------- power ----------------


def power(df, unit_col, mode, nplant=200, nperm=2000):
    m = df[unit_col].notna().to_numpy()
    sub = df[m]
    lab = pd.factorize(sub[unit_col])[0]; nu = lab.max() + 1
    f0 = sub.tf.to_numpy(float); st = pd.factorize(sub.stratum)[0]
    n = np.bincount(lab, minlength=nu)
    elig = np.where(n >= 15)[0]
    if not len(elig):
        return None
    P = perm_matrix(lab, st, nperm)
    hits = 0
    for _ in range(nplant):
        uu = rng.choice(elig); f = f0.copy(); idx = np.where(lab == uu)[0]; off = idx[f[idx] == 0]
        if mode == "plus4":
            need = 4
        else:
            target = min(len(idx), int(round(6 * max(f0.mean(), 1e-9) * len(idx))))
            need = target - int(f[idx].sum())
        if need > 0:
            f[rng.choice(off, min(need, len(off)), replace=False)] = 1
        o = gstat(f, lab, nu)
        nl = np.array([gstat(f, P[r], nu) for r in range(nperm)])
        hits += (1 + (nl >= o - 1e-9).sum()) / (1 + nperm) <= 0.05
    return hits / nplant


OUT["power_plus4_block_sized"] = power(fam_d, PRIMARY, "plus4")
OUT["power_x6_rate"] = power(fam_d, PRIMARY, "x6")
log("power +4:", OUT["power_plus4_block_sized"], " x6:", OUT["power_x6_rate"])

# ---------------- exploratory (not pre-registered): why is power low? ----------------
# Depth bands inside an area largely coincide with blocks, so within-stratum permutation can barely move a seal
# between blocks. Re-run with strata = area only to show how much the depth-band constraint costs.
ao = fam_d.copy(); ao["stratum"] = ao.area
OUT["X_area_only_strata_family"] = {k: v for k, v in ptest(ao, PRIMARY).items() if k != "units"}
OUT["X_power_plus4_area_only_strata"] = power(ao, PRIMARY, "plus4")
sub = fam_d[fam_d[PRIMARY].notna()]
OUT["X_frac_seals_in_single_unit_strata"] = float(
    sub.stratum.map(sub.groupby("stratum")[PRIMARY].nunique()).eq(1).mean())
log("X area-only strata", OUT["X_area_only_strata_family"], "power +4", OUT["X_power_plus4_area_only_strata"])

# ---------------- verdict ----------------
p = prim["p"]
pw = OUT["power_plus4_block_sized"] or 0
if p < 0.05:
    v = "REPLICATED"
elif pw >= 0.5:
    v = "NOT REPLICATED (informative)"
else:
    v = "INCONCLUSIVE"
if len(d) < 100:
    v = "INCONCLUSIVE"
OUT["verdict"] = v
log("VERDICT", v)

# descriptive: TF seals list
OUT["tf_seals"] = d[d.tf == 1][["serial", "key", "area", "U_block", "U_fn", "icit_block_house", "icit_room",
                                "depth"]].astype(str).to_dict("records")
d.drop(columns=["seq", "sset"]).to_csv(HERE / "analysis_table.csv", index=False)
json.dump(OUT, open(HERE / "results.json", "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
log("done")
