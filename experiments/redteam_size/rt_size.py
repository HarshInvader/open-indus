"""redteam_size: red team of space_and_sealing T4 + reg_size omission order.
Pre-registered in docs/prereg/redteam_size.md. Imports T4/reg_size code read-only.
Run: .venv/bin/python experiments/redteam_size/rt_size.py [--smoke]  -> results.json, rt_size.log (stdout)"""
import json, math, sys, itertools
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments/reg_size"))
import rs_lib as L  # noqa: E402
from rs_lib import PRIMARY_T4, CLASSES  # noqa: E402
from corpus.build import _close  # noqa: E402
from corpus.load import icit_texts, m77_texts  # noqa: E402

SMOKE = "--smoke" in sys.argv
NSIM = 200 if SMOKE else 1000
NPERM = 2000 if SMOKE else 10000
LN2 = math.log(2)
K = len(PRIMARY_T4)
CI = {k: i for i, k in enumerate(PRIMARY_T4)}
P_FULL = {"jar", "other_closer", "post_closer"}
P_NOJAR = {"other_closer", "post_closer"}
OUT = {}


def log(*a):
    print(*a, flush=True)


def rho(a, b):
    return float(spearmanr(a, b).correlation)


def holm(ps):
    ps = np.asarray(ps, float); o = np.argsort(ps); m = len(ps); adj = np.empty(m); run = 0
    for r, i in enumerate(o):
        run = max(run, (m - r) * ps[i]); adj[i] = min(1, run)
    return adj


def keep_multi(rows):
    c = Counter(r["stratum"] for r in rows)
    return [r for r in rows if c[r["stratum"]] >= 2]


# ---------------- data ----------------
T4 = L.t4_objects()
t4rows = [dict(r) for r in T4[0]]
for r in t4rows:
    r["lab"] = [next((c for c, ws in CLASSES.items() if s in ws), "core") for s in r["signs"]]
    r["canon"] = L.canon_seq(r["signs"])
new0, _ = L.build_new_set(set(L.PRIMARY_SOURCES), t4=T4)
newrows = [dict(r) for r in new0]
for r in newrows:
    r["lab"] = [L.M_CLASS.get(s, "core") for s in r["signs"]]
    r["canon"] = L.canon_seq(r["signs"])
for rows in (t4rows, newrows):
    for r in rows:
        assert len(r["lab"]) == r["length"]
        cc = Counter(r["lab"])
        assert all(cc.get(k, 0) == r["cls"][k] for k in PRIMARY_T4)
if SMOKE:
    srng = np.random.default_rng(99)
    for rows in (t4rows, newrows):
        a = [r["log_area"] for r in rows]; srng.shuffle(a)
        for r, v in zip(rows, a):
            r["log_area"] = v
t4rows = keep_multi(t4rows); newrows = keep_multi(newrows)
log(f"T4 {len(t4rows)} texts; new {len(newrows)} texts")


# ---------------- estimator ----------------
def design(rows):
    strata = [r["stratum"] for r in rows]
    x = np.array([r["log_area"] for r in rows], float)
    g = defaultdict(list)
    for i, s in enumerate(strata):
        g[s].append(i)
    for idx in g.values():
        x[idx] -= x[idx].mean()
    return x, g


def slopes(x, Y):
    Y = np.asarray(Y, float)
    return x @ (Y - Y.mean(0)) / (x ** 2).sum() * LN2


def share_Y(labs):
    return np.array([[sum(1 for l in lab if l == k) / len(lab) for k in PRIMARY_T4] for lab in labs])


def pres_Y(labs):
    return np.array([[1.0 if k in lab else 0.0 for k in PRIMARY_T4] for lab in labs])


def count_closers(labs, P):
    return np.array([[sum(1 for l in lab if l in P)] for lab in labs])


def perm_p(rows, Y, nperm=NPERM, seed=1):
    x, g = design(rows)
    obs = slopes(x, Y)
    rng = np.random.default_rng(seed)
    n = len(x); Yc = np.asarray(Y, float) - np.asarray(Y, float).mean(0); sxx = (x ** 2).sum()
    null = np.empty((nperm, Yc.shape[1]))
    for b in range(nperm):
        p = np.arange(n)
        for idx in g.values():
            idx = np.array(idx); p[idx] = rng.permutation(idx)
        null[b] = x[p] @ Yc / sxx * LN2
    p2 = ((np.abs(null) >= np.abs(obs) - 1e-12).sum(0) + 1) / (nperm + 1)
    return obs, p2, null


# ---------------- A1 nulls ----------------
def template_pools(rows, lmin=6):
    lens = np.array([r["length"] for r in rows]); sites = [r["site"] for r in rows]
    pools = []
    for i, r in enumerate(rows):
        need = max(r["length"], lmin) if lmin else r["length"]
        same = [j for j in range(len(rows)) if lens[j] >= need and sites[j] == r["site"]]
        if len(same) < 10:
            same = [j for j in range(len(rows)) if lens[j] >= need]
        if not same:
            same = [j for j in range(len(rows)) if lens[j] >= r["length"]]
        pools.append(np.array(same))
    return pools


def thin(lab, L_, P, rng):
    if P is None:
        return [lab[j] for j in rng.choice(len(lab), L_, replace=False)]
    prot = [l for l in lab if l in P]; rest = [l for l in lab if l not in P]
    if len(prot) >= L_:
        return [prot[j] for j in rng.choice(len(prot), L_, replace=False)]
    return prot + [rest[j] for j in rng.choice(len(rest), L_ - len(prot), replace=False)]


def simulate(rows, P, nsim, seed, lmin=6):
    rng = np.random.default_rng(seed)
    pools = template_pools(rows, lmin)
    x, _ = design(rows)
    S, PR, CN = [], [], []
    for _ in range(nsim):
        labs = []
        for i, r in enumerate(rows):
            t = rows[int(rng.choice(pools[i]))]["lab"]
            labs.append(thin(t, r["length"], P, rng))
        S.append(slopes(x, share_Y(labs))); PR.append(slopes(x, pres_Y(labs)))
        CN.append(slopes(x, count_closers(labs, P_FULL))[0])
    return np.array(S), np.array(PR), np.array(CN)


def vs_null(obs, null):
    mu, sd = null.mean(0), null.std(0)
    p = ((np.abs(null - mu) >= np.abs(obs - mu) - 1e-12).sum(0) + 1) / (len(null) + 1)
    return mu, sd, p


def exact_rho_p(a, b):
    """one-sided exact permutation p of Spearman rho over all orderings of b"""
    r0 = rho(a, b); ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
    n = len(a); cnt = tot = 0
    for perm in itertools.permutations(range(n)):
        rr = 1 - 6 * np.sum((ra - rb[list(perm)]) ** 2) / (n * (n * n - 1))
        cnt += rr >= r0 - 1e-12; tot += 1
    return r0, cnt / tot


A1 = {}
DS = {"T4": t4rows, "new": newrows}
obs_s = {}
for name, rows in DS.items():
    x, _ = design(rows)
    labs = [r["lab"] for r in rows]
    o_s, p_s, _ = perm_p(rows, share_Y(labs), seed=11)
    o_p, p_p, _ = perm_p(rows, pres_Y(labs), seed=12)
    o_c, p_c, _ = perm_p(rows, count_closers(labs, P_FULL), seed=13)
    o_l, p_l, _ = perm_p(rows, [[r["length"]] for r in rows], seed=14)
    obs_s[name] = o_s
    d = dict(n=len(rows), length_slope=float(o_l[0]),
             closer_count_dist=dict(Counter(int(c) for c in count_closers(labs, P_FULL)[:, 0])),
             obs_share={k: float(o_s[i]) for k, i in CI.items()},
             obs_share_p_areaperm={k: float(p_s[i]) for k, i in CI.items()},
             obs_presence={k: float(o_p[i]) for k, i in CI.items()},
             obs_presence_p_areaperm={k: float(p_p[i]) for k, i in CI.items()},
             obs_closer_count_slope=float(o_c[0]), obs_closer_count_p=float(p_c[0]), nulls={})
    log(f"\n=== A1 {name}: n={len(rows)} length {o_l[0]:+.2f}/doubling; closers per text {d['closer_count_dist']}")
    log(f"  closer count (jar+other+post) per text vs area: {o_c[0]:+.3f}/doubling p={p_c[0]:.3g}")
    for lbl, P, lmin, seed in [("N1_uniform", None, 6, 21), ("N2_protect_closers", P_FULL, 6, 22),
                               ("N2b_protect_nonjar", P_NOJAR, 6, 23),
                               ("N1_any_template", None, 0, 24), ("N2_any_template", P_FULL, 0, 25)]:
        S, PR, CN = simulate(rows, P, NSIM, seed, lmin)
        mu, sd, p = vs_null(o_s, S); muP, sdP, pP = vs_null(o_p, PR)
        cn_mu, cn_sd = float(CN.mean()), float(CN.std())
        ph = holm(p)
        d["nulls"][lbl] = dict(
            share_mean={k: float(mu[i]) for k, i in CI.items()}, share_sd={k: float(sd[i]) for k, i in CI.items()},
            share_p={k: float(p[i]) for k, i in CI.items()}, share_holm={k: float(ph[i]) for k, i in CI.items()},
            resid={k: float(o_s[i] - mu[i]) for k, i in CI.items()},
            presence_mean={k: float(muP[i]) for k, i in CI.items()}, presence_p={k: float(pP[i]) for k, i in CI.items()},
            closer_count_mean=cn_mu, closer_count_sd=cn_sd,
            rho_nullmean_vs_obs=rho(mu, o_s), _draws=S)
        log(f"  [{lbl}] rho(null mean, observed) = {rho(mu, o_s):+.2f}; closer-count slope null {cn_mu:+.3f} (sd {cn_sd:.3f})")
        for k, i in CI.items():
            log(f"    {k:13s} obs {o_s[i]:+.4f}  null {mu[i]:+.4f} (sd {sd[i]:.4f})  resid {o_s[i]-mu[i]:+.4f}  "
                f"p={p[i]:.3g} Holm={ph[i]:.3g} | presence obs {o_p[i]:+.3f} null {muP[i]:+.3f} p={pP[i]:.3g}")
    A1[name] = d

# mechanical replication rho and residual order replication
t4obs = obs_s["T4"]
newobs = obs_s["new"]
rho_obs, p_exact_obs = exact_rho_p(newobs, t4obs)
A1["replication_rho_observed"] = rho_obs
A1["replication_rho_exact_p"] = p_exact_obs
for lbl in ["N1_uniform", "N2_protect_closers", "N2b_protect_nonjar"]:
    Dn = A1["new"]["nulls"][lbl]["_draws"]
    rr = np.array([rho(t4obs, s) for s in Dn])
    A1[f"mech_rho_{lbl}"] = dict(median=float(np.median(rr)), q025=float(np.quantile(rr, .025)),
                                 q975=float(np.quantile(rr, .975)), P_ge_obs=float(np.mean(rr >= rho_obs - 1e-12)),
                                 P_ge_05=float(np.mean(rr >= 0.5)))
    rT4 = np.array([A1["T4"]["nulls"][lbl]["resid"][k] for k in PRIMARY_T4])
    rNew = np.array([A1["new"]["nulls"][lbl]["resid"][k] for k in PRIMARY_T4])
    r_res, p_res = exact_rho_p(rNew, rT4)
    noise = Dn - Dn.mean(0)
    rr2 = np.array([rho(rT4, s) for s in noise])
    A1[f"resid_rho_{lbl}"] = dict(rho=r_res, exact_p=p_res, parametric_p=float(np.mean(rr2 >= r_res - 1e-12)),
                                  resid_T4=dict(zip(PRIMARY_T4, map(float, rT4))),
                                  resid_new=dict(zip(PRIMARY_T4, map(float, rNew))))
    log(f"\n[{lbl}] replication rho expected from mechanics alone (T4 obs vs new-set null draws): "
        f"median {np.median(rr):+.2f} [{np.quantile(rr,.025):+.2f},{np.quantile(rr,.975):+.2f}], "
        f"P(rho>={rho_obs:.2f})={np.mean(rr>=rho_obs-1e-12):.3f}")
    log(f"  residual order T4 vs new: rho={r_res:+.2f} exact p={p_res:.3g} parametric p={np.mean(rr2>=r_res-1e-12):.3g}")
log(f"\nobserved replication rho={rho_obs:+.3f}, exact 8! one-sided p={p_exact_obs:.4f}")

# A1 verdict
n2 = "N2_protect_closers"
Kc = {}
for k in ["other_closer", "post_closer"]:
    Kc[k] = all(A1[d]["nulls"][n2]["share_p"][k] < 0.05 and
                np.sign(A1[d]["nulls"][n2]["resid"][k]) == np.sign(A1[d]["obs_share"][k]) for d in DS)
Kpass = any(Kc.values())
Opass = A1[f"resid_rho_{n2}"]["rho"] >= 0.5 and A1[f"resid_rho_{n2}"]["exact_p"] < 0.05
A1["verdict_components"] = dict(K_closer_beyond_N2=Kc, K=Kpass, O_resid_order_replicates=Opass)
A1["verdict"] = "survives" if Kpass and Opass else ("fails" if not (Kpass or Opass) else "weakened")
log(f"A1 verdict components {A1['verdict_components']} -> {A1['verdict']}")

# ---------------- A2 ----------------
A2 = {}
allr = [("T4", i, r) for i, r in enumerate(t4rows)] + [("new", i, r) for i, r in enumerate(newrows)]
par = list(range(len(allr)))


def fnd(a):
    while par[a] != a:
        par[a] = par[par[a]]; a = par[a]
    return a


cans = [list(r["canon"]) for _, _, r in allr]
for a in range(len(allr)):
    for b in range(a + 1, len(allr)):
        if cans[a] == cans[b] or _close(cans[a], cans[b]):
            par[fnd(a)] = fnd(b)
fam = [fnd(a) for a in range(len(allr))]
t4fams = {fam[a] for a, (s, _, _) in enumerate(allr) if s == "T4"}
newfam = [fam[a] for a, (s, _, _) in enumerate(allr) if s == "new"]
shared = [f in t4fams for f in newfam]
A2["n_families"] = len(set(fam)); A2["new_in_T4_family"] = int(sum(shared))
A2["new_family_sizes"] = dict(Counter(Counter(newfam).values()))
disj = [r for r, s in zip(newrows, shared) if not s]
disj = keep_multi(disj)
xd, _ = design(disj)
od = slopes(xd, share_Y([r["lab"] for r in disj]))
rd, pd = exact_rho_p(od, t4obs)
A2["family_disjoint"] = dict(n=len(disj), rho=rd, exact_p=pd, slopes=dict(zip(PRIMARY_T4, map(float, od))))
log(f"\n=== A2: {A2['n_families']} families over T4+new; {sum(shared)}/{len(newrows)} new texts share a family with T4")
log(f"  family-disjoint new set n={len(disj)}: rho={rd:+.2f} exact p={pd:.3g}; slopes " +
    str({k: round(float(v), 4) for k, v in zip(PRIMARY_T4, od)}))
# residual order on family-disjoint set (vs N2 computed for that set)
Sd, _, _ = simulate(disj, P_FULL, NSIM, 31)
rdis = od - Sd.mean(0)
rT4 = np.array([A1["T4"]["nulls"][n2]["resid"][k] for k in PRIMARY_T4])
A2["family_disjoint_resid_rho"] = dict(zip(["rho", "exact_p"], exact_rho_p(rdis, rT4)))
log(f"  family-disjoint residual (vs N2) rho with T4 residual: {A2['family_disjoint_resid_rho']}")
# cluster bootstrap
t4fam = [fam[a] for a, (s, _, _) in enumerate(allr) if s == "T4"]


def clus_boot(rows, fams, rng, by_site):
    groups = defaultdict(list)
    for i, (r, f) in enumerate(zip(rows, fams)):
        groups[(r["site"] if by_site else 0, f)].append(i)
    keys = list(groups); out = []
    bysite = defaultdict(list)
    for k in keys:
        bysite[k[0]].append(k)
    for s, ks in bysite.items():
        for j in rng.integers(0, len(ks), len(ks)):
            out.extend(groups[ks[j]])
    return [rows[i] for i in out]


rng = np.random.default_rng(41)
bt = []
for _ in range(NSIM):
    a = keep_multi(clus_boot(t4rows, t4fam, rng, False)); b = keep_multi(clus_boot(newrows, newfam, rng, True))
    xa, _ = design(a); xb, _ = design(b)
    bt.append(rho(slopes(xa, share_Y([r["lab"] for r in a])), slopes(xb, share_Y([r["lab"] for r in b]))))
bt = np.array(bt)
A2["cluster_bootstrap_rho"] = dict(median=float(np.nanmedian(bt)), q025=float(np.nanquantile(bt, .025)),
                                   q975=float(np.nanquantile(bt, .975)), P_ge_05=float(np.nanmean(bt >= 0.5)))
log(f"  family cluster bootstrap rho: {A2['cluster_bootstrap_rho']}")
# double counting
dup = []
for i, r in enumerate(newrows):
    for t in t4rows:
        if t["site"] == r["site"] and abs(t["log_area"] - r["log_area"]) < 0.03 and \
                (list(t["canon"]) == list(r["canon"]) or _close(list(t["canon"]), list(r["canon"]))):
            dup.append(i); break
A2["probable_same_object"] = len(dup)
nd = keep_multi([r for i, r in enumerate(newrows) if i not in set(dup)])
xn, _ = design(nd)
on = slopes(xn, share_Y([r["lab"] for r in nd]))
A2["without_probable_dups"] = dict(zip(["rho", "exact_p"], exact_rho_p(on, t4obs)))
A2["without_probable_dups"]["n"] = len(nd)
log(f"  probable same objects (same site, area within 3%, text close): {len(dup)}; without them rho/p {A2['without_probable_dups']}")
A2["verdict"] = ("survives" if rd >= 0.5 and pd < 0.05 and A2["cluster_bootstrap_rho"]["P_ge_05"] >= 0.8 else
                 "fails" if rd < 0.5 and A2["cluster_bootstrap_rho"]["P_ge_05"] < 0.5 else "weakened")
log(f"A2 verdict -> {A2['verdict']}")

# ---------------- A3 ----------------
A3 = {}
# T4 seal type per text: modal ICIT symbol over its objects
symmap = defaultdict(list)
for t in icit_texts():
    if t["type"] == "SEAL:S" and L.is_steatite(t["material"]) and L.num(t["width_mm"]) * L.num(t["height_mm"]) > 20:
        symmap[" ".join(t["seq"])].append(t["symbol"])


def symcat_icit(s):
    s = (s or "").strip()
    if s.startswith("Bull1"):
        return "unicorn"
    if s == "None":
        return "none"
    if s in ("-", "?", ""):
        return "unknown"
    return "animal"


for r in t4rows:
    r["sym"] = Counter(symcat_icit(s) for s in symmap[r["key"]]).most_common(1)[0][0]
m77 = L.m77_seal_index()
for r in newrows:
    fs = m77[r["text_no"]]["fs80"]
    r["sym"] = "unicorn" if fs == 13 else "none" if fs == 0 else "unknown" if fs == 999 else "animal"
A3["sym_counts"] = {"T4": dict(Counter(r["sym"] for r in t4rows)), "new": dict(Counter(r["sym"] for r in newrows))}
# ICIT material for new-set objects
icit = L.icit_by_id()
for r in newrows:
    mats = [icit[i]["material"] for i in r["icit_ids"] if i in icit]
    r["steatite"] = bool(mats) and all(L.is_steatite(m) for m in mats)


def variant(rows):
    rows = keep_multi(rows)
    x, _ = design(rows)
    o = slopes(x, share_Y([r["lab"] for r in rows]))
    S, _, _ = simulate(rows, P_FULL, max(200, NSIM // 4), 51)
    mu = S.mean(0); sd = S.std(0)
    return rows, o, mu, sd


VAR = {
    "a_plus_sealtype_strata": (lambda r: dict(r, stratum=r["stratum"] + "|" + r["sym"]), lambda r: True),
    "b_unicorn_only": (lambda r: r, lambda r: r["sym"] == "unicorn"),
    "c_site_only_strata": (lambda r: dict(r, stratum=r["site"]), lambda r: True),
    "d_material_FEM_only_new": (lambda r: r, lambda r: r.get("source", "Mackay1938_FEM") == "Mackay1938_FEM"),
}
log("\nnew texts linked to an ICIT steatite object (descriptive): %d" % sum(r["steatite"] for r in newrows))
for vn, (tf, flt) in VAR.items():
    res = {}
    oo = {}
    for name, rows in DS.items():
        if vn == "d_material_FEM_only_new" and name == "T4":
            rr = rows
        elif vn == "c_site_only_strata" and name == "new":
            rr = rows
        else:
            rr = [tf(r) for r in rows if flt(r)]
        rr, o, mu, sd = variant(rr)
        oo[name] = o
        res[name] = dict(n=len(rr), slopes=dict(zip(PRIMARY_T4, map(float, o))),
                         N2_resid={k: float(o[i] - mu[i]) for k, i in CI.items() if k in P_FULL},
                         N2_z={k: float((o[i] - mu[i]) / max(sd[i], 1e-9)) for k, i in CI.items() if k in P_FULL})
    res["rho_T4_new"] = rho(oo["T4"], oo["new"])
    res["rho_exact_p"] = exact_rho_p(oo["new"], oo["T4"])[1]
    A3[vn] = res
    log(f"\n=== A3 {vn}: rho(T4,new)={res['rho_T4_new']:+.2f} (exact p {res['rho_exact_p']:.3g})")
    for name in DS:
        log(f"  {name} n={res[name]['n']}: other_closer {res[name]['slopes']['other_closer']:+.4f} "
            f"post_closer {res[name]['slopes']['post_closer']:+.4f} jar {res[name]['slopes']['jar']:+.4f} "
            f"connective {res[name]['slopes']['connective']:+.4f}; N2 z {{{', '.join(f'{k}: {v:+.2f}' for k, v in res[name]['N2_z'].items())}}}")
# descriptive: area and closer presence by seal type
desc = {}
for name, rows in DS.items():
    desc[name] = {}
    for s in ["unicorn", "animal", "none"]:
        sub = [r for r in rows if r["sym"] == s]
        if sub:
            desc[name][s] = dict(n=len(sub), mean_log_area=float(np.mean([r["log_area"] for r in sub])),
                                 mean_len=float(np.mean([r["length"] for r in sub])),
                                 closer_present=float(np.mean([any(l in P_FULL for l in r["lab"]) for r in sub])))
A3["by_seal_type"] = desc
log("  by seal type: " + json.dumps(desc))
prim = {d: (A1[d]["obs_share"]["other_closer"], A1[d]["obs_share"]["post_closer"]) for d in DS}
vanish = []
for vn in ["a_plus_sealtype_strata", "b_unicorn_only"]:
    v = all(any(A3[vn][d]["slopes"][k] >= 0 or abs(A3[vn][d]["slopes"][k]) < abs(A1[d]["obs_share"][k]) / 3
                for k in ["other_closer", "post_closer"]) for d in DS)
    vanish.append(v)
ok = all(all(A3[vn][d]["slopes"][k] < 0 for d in DS for k in ["other_closer", "post_closer"]) and
         A3[vn]["rho_T4_new"] >= 0.5 for vn in VAR)
A3["verdict"] = "fails" if any(vanish) else ("survives" if ok else "weakened")
log(f"A3 verdict -> {A3['verdict']}")

for d in DS:
    for n in A1[d]["nulls"].values():
        n.pop("_draws", None)
OUT.update(A1=A1, A2=A2, A3=A3, nsim=NSIM, nperm=NPERM, smoke=SMOKE)
if not SMOKE:
    json.dump(OUT, open(HERE / "results.json", "w"), indent=1, default=float)
else:
    log("SMOKE: area shuffled, nothing written")
