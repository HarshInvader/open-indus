import sys, json; sys.path.insert(0, "experiments/redteam_chrono")
from rc_lib import *
from collections import Counter
from scipy.stats import spearmanr
NP = 2000
H = dataset_harp(); V = dataset_vats()
out = {}
def run(key, A, B, **kw):
    r = compare(A, B, nperm=NP, **kw)
    out[key] = {k: r[k] for k in ("n", "rho", "p")}
    print("%-60s n=%3d rho=%+.3f p=%.4f" % (key, r["n"], r["rho"], r["p"]), flush=True)
    return r
sel = lambda D, f: [u for u in D if f(u)]
# what are M77 Harappa 'sealing'? match identical texts to HARP types
hk = defaultdict(Counter)
for u in H: hk[" ".join(signs_of(u["seq"]))][u["type"]] += 1
m = Counter()
for u in V:
    k = " ".join(signs_of(u["seq"]))
    for t in hk.get(k, {}): m[(u["type"], t)] += 1
print("VATS type x HARP type of identical texts:", dict(m))
out["type_match"] = {str(k): v for k, v in m.items()}
tabH = lambda u: u["type"].startswith("tab")
run("HARP tablets ~ VATS all", Shift(sel(H, tabH)), Shift(V))
run("HARP non-tablets ~ VATS all", Shift(sel(H, lambda u: not tabH(u))), Shift(V), nmin=3)
run("HARP all ~ VATS seals", Shift(H), Shift(sel(V, lambda u: u["type"] == "seal")))
run("HARP all ~ VATS sealing", Shift(H), Shift(sel(V, lambda u: u["type"] == "sealing")))
run("HARP all ~ VATS tablet", Shift(H), Shift(sel(V, lambda u: u["type"] == "tablet")))
run("HARP all ~ VATS tablet+sealing", Shift(H), Shift(sel(V, lambda u: u["type"] in ("tablet", "sealing"))))
# combined within-type agreement: matched pairs, joint null (sum of rhos)
pairs = [("seal", lambda u: u["type"] == "seal", lambda u: u["type"] == "seal", 3),
         ("tablet", tabH, lambda u: u["type"] in ("tablet", "sealing"), 5)]
rng = np.random.default_rng(1)
tot_obs, nulls = 0, np.zeros(NP)
for name, fh, fv, nm in pairs:
    A, B = Shift(sel(H, fh)), Shift(sel(V, fv))
    r = compare(A, B, nperm=1, nmin=nm)
    ia = {s: i for i, s in enumerate(A.signs)}; ib = {s: i for i, s in enumerate(B.signs)}
    ai = np.array([ia[s] for s in r["signs"]]); bi = np.array([ib[s] for s in r["signs"]])
    tot_obs += r["rho"] * len(ai)
    for k in range(NP):
        nulls[k] += spearmanr(A.shifts(A.perm_rel(rng))[ai], B.shifts(B.perm_rel(rng))[bi])[0] * len(ai)
    print(" within", name, r["n"], round(r["rho"], 3))
p = (1 + np.sum(nulls >= tot_obs)) / (NP + 1)
print("matched within-type n-weighted rho sum %.2f, p=%.4f" % (tot_obs, p))
out["within_type_combined"] = dict(stat=float(tot_obs), p=float(p))
# shared families: same signs, with vs without
U = H + V; fU = families(U); sh = set(fU[:len(H)]) & set(fU[len(H):])
H2 = [u for u, f in zip(H, fU[:len(H)]) if f not in sh]; V2 = [u for u, f in zip(V, fU[len(H):]) if f not in sh]
r2 = run("drop shared families", Shift(H2), Shift(V2))
run("full data, same signs as drop-shared", Shift(H), Shift(V), signs=set(r2["signs"]))
run("drop shared families, nmin 3", Shift(H2), Shift(V2), nmin=3)
print("units in shared families: HARP %d/%d, VATS %d/%d" % (len(H) - len(H2), len(H), len(V) - len(V2), len(V)))
out["shared_family_units"] = [len(H) - len(H2), len(V) - len(V2)]
# the shared families themselves: where do they sit in time in each excavation?
fam_rel = defaultdict(lambda: [[], []])
for u, f in zip(H, fU[:len(H)]):
    if f in sh: fam_rel[f][0].append(u["rel"])
for u, f in zip(V, fU[len(H):]):
    if f in sh: fam_rel[f][1].append(u["rel"])
a = [np.mean(x[0]) for x in fam_rel.values()]; b = [np.mean(x[1]) for x in fam_rel.values()]
rf = spearmanr(a, b)
print("shared families: mean rel HARP vs VATS rho=%.3f p=%.4f n=%d" % (rf[0], rf[1], len(a)))
out["shared_family_time_agreement"] = dict(rho=float(rf[0]), p=float(rf[1]), n=len(a))
json.dump(out, open("experiments/redteam_chrono/r4.json", "w"), indent=1)
