import sys, json; sys.path.insert(0, "experiments/redteam_chrono")
from rc_lib import *
NP = 2000
H = dataset_harp(); V = dataset_vats()
out = {}
def run(key, A, B, **kw):
    r = compare(A, B, nperm=NP, **kw)
    out[key] = {k: r[k] for k in ("n", "rho", "p")}
    print("%-55s n=%3d rho=%+.3f p=%.4f" % (key, r["n"], r["rho"], r["p"]), flush=True)
    return r
T = lambda u: u["type"]
base = run("base type-strat", Shift(H), Shift(V))
# ---- A1 object type
sel = lambda D, f: [u for u in D if f(u)]
run("A1 seals only", Shift(sel(H, lambda u: u["type"] == "seal")), Shift(sel(V, lambda u: u["type"] == "seal")), nmin=3)
run("A1 tablets only (HARP tab_* / VATS tablet)", Shift(sel(H, lambda u: u["type"].startswith("tab"))), Shift(sel(V, lambda u: u["type"] == "tablet")))
run("A1 HARP incised only / VATS tablet", Shift(sel(H, lambda u: u["type"] == "tab_incised")), Shift(sel(V, lambda u: u["type"] == "tablet")))
run("A1 HARP moulded only / VATS tablet+sealing", Shift(sel(H, lambda u: u["type"] == "tab_moulded")), Shift(sel(V, lambda u: u["type"] in ("tablet", "sealing"))))
run("A1 HARP tablets / VATS sealing", Shift(sel(H, lambda u: u["type"].startswith("tab"))), Shift(sel(V, lambda u: u["type"] == "sealing")))
run("A1 HARP tablets / VATS seal", Shift(sel(H, lambda u: u["type"].startswith("tab"))), Shift(sel(V, lambda u: u["type"] == "seal")))
run("A1 HARP fine type (SEAL:S etc) strat", Shift(H, strat=lambda u: u["fine"]), Shift(V))
run("A1 no type strat (raw)", Shift(H, strat=lambda u: 0), Shift(V, strat=lambda u: 0))
# ---- A2 families
for name, D in [("H", H), ("V", V)]:
    pass
fH = families(H); fV = families(V)
from collections import Counter
cH, cV = Counter(fH), Counter(fV)
print("families: HARP %d units -> %d families; VATS %d -> %d" % (len(H), len(cH), len(V), len(cV)))
out["families"] = dict(harp_units=len(H), harp_fam=len(cH), vats_units=len(V), vats_fam=len(cV))
wH = [1 / cH[f] for f in fH]; wV = [1 / cV[f] for f in fV]
run("A2 family-weighted (1/family size)", Shift(H, weight=wH), Shift(V, weight=wV))
# one unit per family: keep first, rel = mean rel of family
def collapse(D, fam):
    g = defaultdict(list)
    for u, f in zip(D, fam): g[f].append(u)
    res = []
    for f, us in g.items():
        u = dict(us[0]); u["rel"] = float(np.mean([x["rel"] for x in us])); res.append(u)
    return res
HC, VC = collapse(H, fH), collapse(V, fV)
run("A2 one unit per family (mean rel)", Shift(HC), Shift(VC))
famsH = set(fH); famsV = set(fV)
# shared families across datasets (by identical family root is not comparable; recompute on union)
U = H + V; fU = families(U)
fh = set(fU[:len(H)]); fv = set(fU[len(H):]); sh = fh & fv
print("families shared across excavations:", len(sh))
out["shared_families"] = len(sh)
H2 = [u for u, f in zip(H, fU[:len(H)]) if f not in sh]; V2 = [u for u, f in zip(V, fU[len(H):]) if f not in sh]
run("A2 drop shared families (both datasets)", Shift(H2), Shift(V2))
hs = {" ".join(signs_of(u["seq"])) for u in H} & {" ".join(signs_of(u["seq"])) for u in V}
run("A2 drop shared identical texts", Shift([u for u in H if " ".join(signs_of(u["seq"])) not in hs]), Shift([u for u in V if " ".join(signs_of(u["seq"])) not in hs]))
# ---- A3 area
print("HARP area x rel:", Counter((u["area"], u["rel"]) for u in H))
run("A3 HARP strat type x area", Shift(H, strat=lambda u: (u["type"], u["area"])), Shift(V, strat=lambda u: (u["type"], u["area"])))
run("A3 HARP strat type x trench", Shift(H, strat=lambda u: (u["type"], u["trench"])), Shift(V, strat=lambda u: (u["type"], u["area"])))
for a in ["E", "ET", "F"]:
    run("A3 HARP area %s only" % a, Shift([u for u in H if u["area"] == a]), Shift(V), nmin=4)
# ---- A4 vats mapping
run("A4 VATS absolute depth (all loci pooled)", Shift(H), Shift(dataset_vats(absolute=True)))
run("A4 VATS loci min 30 objs", Shift(H), Shift(dataset_vats(min_obj=30)))
VS = dataset_vats_strata()
print("Vats strata (ICIT) units", len(VS), Counter((u["area"], u["stratum"]) for u in VS))
run("A4 HARP ~ ICIT Vats strata (within area)", Shift(H), Shift(VS), nmin=4)
run("A4 HARP ~ ICIT Vats strata (global)", Shift(H), Shift(dataset_vats_strata(within_area=False)), nmin=4)
run("A4 VATS M77 ~ ICIT Vats strata (same excavation)", Shift(V), Shift(VS), nmin=4)
# ---- A5 selection/null
for nm in (3, 8, 10, 15):
    run("A5 nmin=%d" % nm, Shift(H), Shift(V), nmin=nm)
lb = lambda u: min(len(signs_of(u["seq"])), 5)
run("A5 null strat type x length", Shift(H, strat=lambda u: (u["type"], lb(u))), Shift(V, strat=lambda u: (u["type"], lb(u))))
json.dump(out, open("experiments/redteam_chrono/r2.json", "w"), indent=1)
