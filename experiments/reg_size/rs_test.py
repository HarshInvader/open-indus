"""reg_size: frozen replication test of space_and_sealing T4 on register-measured seals whose texts
were not in T4. Pre-registered in docs/prereg/reg_size.md.
Run: .venv/bin/python experiments/reg_size/rs_test.py            -> results.json, rs_test.log (stdout)
     .venv/bin/python experiments/reg_size/rs_test.py --smoke    (area shuffled; pipeline check only)"""
import json, math, sys
from collections import Counter, defaultdict
import numpy as np
from scipy.stats import spearmanr
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import rs_lib as L
from rs_lib import PRIMARY_T4, HERE, ROOT

SMOKE = "--smoke" in sys.argv
NPERM = 10000
LN2 = math.log(2)
RNG = np.random.default_rng(20261114)
T4J = json.load(open(ROOT / "experiments/space_and_sealing/t4.json"))
T4S = np.array([T4J["P2_share_slopes"][k]["slope_per_doubling"] for k in PRIMARY_T4])
KEY3 = {"connective": +1, "other_closer": -1, "post_closer": -1}
OUT = dict(t4_reference_slopes={k: float(v) for k, v in zip(PRIMARY_T4, T4S)})


def log(*a):
    print(*a, flush=True)


def keep_multi(rows, key="stratum"):
    c = Counter(r[key] for r in rows)
    return [r for r in rows if c[r[key]] >= 2]


def centre(x, strata):
    x = np.asarray(x, float).copy(); g = defaultdict(list)
    for i, s in enumerate(strata):
        g[s].append(i)
    for idx in g.values():
        x[idx] -= x[idx].mean()
    return x, g


def perms(g, n, nperm, rng):
    P = np.tile(np.arange(n), (nperm, 1))
    for idx in g.values():
        idx = np.array(idx)
        if len(idx) > 1:
            P[:, idx] = idx[np.argsort(rng.random((nperm, len(idx))), axis=1)]
    return P


def share_matrix(rows):
    return np.array([[r["cls"][k] / r["length"] for k in PRIMARY_T4] for r in rows])


def slope_test(rows, Y, nperm=NPERM, rng=RNG):
    x, g = centre([r["log_area"] for r in rows], [r["stratum"] for r in rows])
    Y = np.asarray(Y, float); Yc = Y - Y.mean(0); sxx = (x ** 2).sum()
    obs = x @ Yc / sxx
    null = (x[perms(g, len(x), nperm, rng)] @ Yc) / sxx
    p2 = ((np.abs(null) >= np.abs(obs) - 1e-12).sum(0) + 1) / (nperm + 1)
    ppos = ((null >= obs - 1e-12).sum(0) + 1) / (nperm + 1)
    pneg = ((null <= obs + 1e-12).sum(0) + 1) / (nperm + 1)
    return obs * LN2, null * LN2, p2, ppos, pneg


def holm(ps):
    ps = np.asarray(ps, float); o = np.argsort(ps); m = len(ps); adj = np.empty(m); run = 0
    for r, i in enumerate(o):
        run = max(run, (m - r) * ps[i]); adj[i] = min(1, run)
    return adj


def rho(a, b):
    return float(spearmanr(a, b).correlation)


def replication(rows, label, nperm=NPERM, full=True):
    rows = keep_multi(rows)
    res = dict(n=len(rows), n_obj=int(sum(r.get("n_obj", 1) for r in rows)),
               by_site=dict(Counter(r["site"] for r in rows)))
    o1, _, _, pp1, _ = slope_test(rows, [[r["length"]] for r in rows], nperm)
    res["P1_signs_per_doubling"] = float(o1[0]); res["P1_p_one_sided"] = float(pp1[0])
    o, null, p2, ppos, pneg = slope_test(rows, share_matrix(rows), nperm)
    sd = null.std(0)
    res["slopes"] = {k: float(v) for k, v in zip(PRIMARY_T4, o)}
    res["mde80"] = {k: float(2.8 * v) for k, v in zip(PRIMARY_T4, sd)}
    res["p_two_sided"] = {k: float(v) for k, v in zip(PRIMARY_T4, p2)}
    dir_p = [float(ppos[PRIMARY_T4.index(k)] if s > 0 else pneg[PRIMARY_T4.index(k)]) for k, s in KEY3.items()]
    res["directional_p"] = dict(zip(KEY3, dir_p)); res["directional_holm"] = dict(zip(KEY3, map(float, holm(dir_p))))
    res["R1_signs"] = {k: bool(np.sign(res["slopes"][k]) == s) for k, s in KEY3.items()}
    res["R1_pass"] = all(res["R1_signs"].values())
    r_obs = rho(o, T4S)
    r_null = np.array([rho(null[i], T4S) for i in range(min(nperm, 5000))])
    res["R2_rho"] = r_obs; res["R2_p_one_sided"] = float(((r_null >= r_obs - 1e-12).sum() + 1) / (len(r_null) + 1))
    res["R2_pass"] = bool(r_obs >= 0.5)
    res["P1_pass"] = bool(res["P1_p_one_sided"] < 0.05)
    if not res["P1_pass"]:
        v = "uninterpretable (positive control fails)"
    elif res["R1_pass"] and res["R2_pass"]:
        v = "replicated"
    elif res["R1_pass"] or res["R2_pass"]:
        v = "partial"
    else:
        v = "not replicated"
    res["verdict"] = v
    res["order_dropped_first_to_kept"] = sorted(PRIMARY_T4, key=lambda k: -res["slopes"][k])
    # heterogeneity vs T4 (descriptive): z per class using this set's null SD and T4's null SD
    t4sd = np.array([T4J["P2_share_slopes"][k]["null_sd_per_doubling"] for k in PRIMARY_T4])
    res["z_diff_vs_T4"] = {k: float((o[i] - T4S[i]) / math.hypot(sd[i], t4sd[i])) for i, k in enumerate(PRIMARY_T4)}
    log(f"\n[{label}] n={res['n']} texts ({res['n_obj']} objects) {res['by_site']}")
    log(f"  P1 length: {res['P1_signs_per_doubling']:+.2f} signs/doubling, one-sided p={res['P1_p_one_sided']:.4g}")
    for k in PRIMARY_T4:
        log(f"  {k:13s} new {res['slopes'][k]:+.4f} (MDE {res['mde80'][k]:.4f}, p2={res['p_two_sided'][k]:.3g})"
            f"   T4 {OUT['t4_reference_slopes'][k]:+.4f}   z_diff {res['z_diff_vs_T4'][k]:+.2f}")
    log(f"  R1 signs {res['R1_signs']} -> {res['R1_pass']}; directional p {res['directional_p']} Holm {res['directional_holm']}")
    log(f"  R2 rho vs T4 = {r_obs:+.2f} (one-sided perm p={res['R2_p_one_sided']:.3g}) -> {res['R2_pass']}")
    log(f"  verdict: {v};  order: {' > '.join(res['order_dropped_first_to_kept'])}")
    return res


T4 = L.t4_objects()
if SMOKE:  # pipeline check only: area shuffled across every row before any statistic
    _b = L.build_new_set
    _srng = np.random.default_rng(99)

    def _shuf(rows):
        a = [r["log_area"] for r in rows]; _srng.shuffle(a)
        return [dict(r, log_area=v) for r, v in zip(rows, a)]

    def _build(*a, **k):
        r, au = _b(*a, **k)
        return _shuf(r), au
    L.build_new_set = _build
    T4 = (_shuf(T4[0]), T4[1])
PRIM = set(L.PRIMARY_SOURCES)
rows, audit = L.build_new_set(PRIM, t4=T4)
OUT["audit_primary"] = audit
OUT["primary"] = replication(rows, "PRIMARY: FEM + EH, texts not in T4, site strata")

# ---------------- sensitivities (reported, not decisive) ----------------
S = {}
r_e1, _ = L.build_new_set(PRIM, t4=T4, exclude="edit1")
S["edit1_excluded"] = replication(r_e1, "s1 also drop texts within 1 edit of a T4 text", 4000)
r_mic, _ = L.build_new_set(PRIM | {"Marshall1931_MIC"}, t4=T4)
S["plus_MIC"] = replication(r_mic, "s2 + Marshall MIC", 4000)
r_all, _ = L.build_new_set(PRIM | set(L.SENS_SOURCES), t4=T4)
S["plus_MIC_CE"] = replication(r_all, "s3 + Marshall MIC + Mackay CE", 4000)
r_an, _ = L.build_new_set(PRIM, t4=T4, require_animal=True)
S["animal_seals_only"] = replication(r_an, "s4 animal seals only (E4)", 4000)
# s5 site x depth tercile strata (depth is the only time proxy in the registers)
r5 = []
for site in {r["site"] for r in rows}:
    sub = [r for r in rows if r["site"] == site and r["depth"] is not None]
    if len(sub) < 6:
        continue
    q = np.quantile([r["depth"] for r in sub], [1 / 3, 2 / 3])
    for r in sub:
        r5.append(dict(r, stratum=f"{site}#d{int(np.digitize(r['depth'], q))}"))
S["site_x_depth_strata"] = replication(r5, "s5 site x depth-tercile strata", 4000)
S["single_line"] = replication([r for r in rows if r["n_lines"] == 1], "s6 single-line texts", 4000)
# s7 ICIT Wells text (frozen T4 classes) where the object links to exactly one complete ICIT text
icit = L.icit_by_id()
r7 = []
for r in rows:
    if len(r["icit_ids"]) == 1 and r["icit_ids"][0] in icit:
        it = icit[r["icit_ids"][0]]
        if it["complete"] and "#" not in it["seq"]:
            sg = L.sas_lib.nsigns(it["seq"])
            r = dict(r, signs=sg, length=len(sg), cls=L.sas_lib.classes_of(sg))
    r7.append(r)
S["icit_text_where_linked"] = replication(r7, "s7 ICIT Wells text where linked", 4000)
S["n_icit_text_swapped"] = int(sum(1 for a, b in zip(rows, r7) if a is not b))
OUT["sensitivity"] = S

# ---------------- secondary: combined T4 + new, stability of the order ----------------
T4rows = [dict(r, stratum=r["stratum"]) for r in T4[0]]
comb = T4rows + rows
C = replication(comb, "SECONDARY: combined T4 + new (new objects in their own site strata)")
pc = [C["p_two_sided"][k] for k in PRIMARY_T4]
C["holm_8"] = {k: float(v) for k, v in zip(PRIMARY_T4, holm(pc))}
log("  combined Holm(8):", {k: round(v, 4) for k, v in C["holm_8"].items()})
comb = keep_multi(comb)
x, g = centre([r["log_area"] for r in comb], [r["stratum"] for r in comb])
Y = share_matrix(comb)
point = np.array([C["slopes"][k] for k in PRIMARY_T4])
B = []
rngb = np.random.default_rng(5)
for _ in range(1000):
    idx = np.concatenate([rngb.choice(v, len(v)) for v in g.values()])
    xb, _ = centre(np.array([comb[i]["log_area"] for i in idx]), [comb[i]["stratum"] for i in idx])
    Yb = Y[idx] - Y[idx].mean(0)
    B.append(xb @ Yb / (xb ** 2).sum() * LN2)
B = np.array(B)
ranks = np.argsort(np.argsort(-B, axis=1), axis=1) + 1
stab = dict(
    rank_median={k: float(np.median(ranks[:, i])) for i, k in enumerate(PRIMARY_T4)},
    rank_ci95={k: [int(np.quantile(ranks[:, i], .025)), int(np.quantile(ranks[:, i], .975))] for i, k in enumerate(PRIMARY_T4)},
    sign_kept={k: float(np.mean(np.sign(B[:, PRIMARY_T4.index(k)]) == s)) for k, s in KEY3.items()},
    p_connective_above_both_closer_classes=float(np.mean(
        (B[:, PRIMARY_T4.index("connective")] > B[:, PRIMARY_T4.index("other_closer")]) &
        (B[:, PRIMARY_T4.index("connective")] > B[:, PRIMARY_T4.index("post_closer")]))),
    mean_rho_bootstrap_vs_point=float(np.mean([rho(b, point) for b in B])))
stab["stable"] = bool(stab["mean_rho_bootstrap_vs_point"] >= 0.8 and min(stab["sign_kept"].values()) >= 0.9)
C["stability"] = stab
log("  bootstrap stability:", json.dumps(stab))
OUT["combined"] = C

if not SMOKE:
    json.dump(OUT, open(HERE / "results.json", "w"), indent=1)
else:
    log("\nSMOKE run: area shuffled, nothing written")
