"""Follow-up (after the frozen run; exploratory unless noted): weaker planted effects for P1 power,
which signs drive P3, and P3 within object type (seals only / tablets only)."""
import h1_main as H
from hl_lib import *
from scipy.stats import spearmanr
rng = np.random.default_rng(7); H.rng = rng
R = {}
D = build_icit(); D["HAR_VATS"] = build_m77_depth("Harappa"); D["MD_M77"] = build_m77_depth("Mohenjodaro")
prim = {k: D[k] for k in H.PRIMARY}

# 1. power curve at weaker effects (and the minimum detectable effect for the observed S scale)
pw = {}
for f, m in [(0.2, 0.2), (0.3, 0.3), (0.5, 0.2), (0.5, 0.1), (1.0, 0.1)]:
    hits, Ss = [], []
    for rep in range(60):
        pl = H.plant(prim, f, m, rng)
        c = H.contrast(H.drift_table(pl, H.sign_items, 5, 200), nshuf=1000)
        hits.append(c["p_one"] < 0.05); Ss.append(c["S"])
    pw[f"f={f},m={m}"] = dict(power=float(np.mean(hits)), mean_S=float(np.mean(Ss)))
    print("power", f, m, pw[f"f={f},m={m}"], flush=True)
R["P1_power_weak"] = pw

# 2. drivers of P3 (HAR vs HAR_VATS)
def sh(U):
    P = np.array([u["period"] for u in U]); return H.shifts(U, P), P
a, _ = sh(D["HAR"]); b, _ = sh(D["HAR_VATS"]); c_, _ = sh(D["MD"])
com = sorted(set(a) & set(b))
rows = sorted([(x, H.cls(x), H.ROLE.get(x, ("?",))[0], round(a[x], 3), round(b[x], 3), round(c_.get(x, np.nan), 3)) for x in com], key=lambda r: -(r[3] + r[4]))
print("signs shared HAR & HAR_VATS: sign class role shift_HAR shift_VATS shift_MD")
for r in rows[:10] + [("...",)] + rows[-10:]: print("  ", r)
R["P3_drivers_late"] = rows[:10]; R["P3_drivers_early"] = rows[-10:]
# leave-one-out robustness of rho
rhos = []
for x in com:
    cc = [y for y in com if y != x]
    rhos.append(spearmanr([a[y] for y in cc], [b[y] for y in cc]).correlation)
R["P3_HAR_VATS_loo_min_rho"] = float(min(rhos)); print("LOO min rho", min(rhos))
# by class
for k in ("CORE", "FRAME", "NUM"):
    cc = [x for x in com if H.cls(x) == k]
    if len(cc) >= 8:
        r = spearmanr([a[y] for y in cc], [b[y] for y in cc]).correlation
        R[f"P3_HAR_VATS_rho_{k}"] = dict(rho=float(r), n=len(cc)); print("rho within", k, len(cc), round(r, 3))

# 3. P3 within object type (exploratory)
for ot in ("seal", "tablet"):
    sub = {}
    for k in ("HAR", "HAR_VATS", "MD"):
        U = [u for u in D[k] if u["ot"] == ot]
        ps = sorted(set(u["period"] for u in U)); mp = {p: i for i, p in enumerate(ps)}
        sub[k] = [dict(u, period=mp[u["period"]]) for u in U]
    print(ot, {k: len(v) for k, v in sub.items()})
    pairs = [("HAR", "HAR_VATS")] + ([("HAR", "MD"), ("HAR_VATS", "MD")] if ot == "seal" else [])
    try:
        res = H.p3(sub, pairs, nperm=1000); R[f"P3_{ot}_only"] = res; print("  P3", ot, res)
    except Exception as e:
        print("  P3", ot, "failed", e)
json.dump(R, open(OUT / "results_followup.json", "w"), indent=1, default=float)
