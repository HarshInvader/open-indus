import sys, json; sys.path.insert(0, "experiments/redteam_chrono")
from rc_lib import *
from collections import Counter
from scipy.stats import spearmanr, norm
NP = 2000
H = dataset_harp(); V = dataset_vats()
A, B = Shift(H), Shift(V)
out = {}
rng = np.random.default_rng(7)
def zs(S, nperm=NP):
    obs = S.shifts(); nul = np.array([S.shifts(S.perm_rel(rng)) for _ in range(nperm)])
    return obs, (obs - nul.mean(0)) / np.maximum(nul.std(0), 1e-9), nul
oa, za, na = zs(A); ob, zb, nb = zs(B)
ia = {s: i for i, s in enumerate(A.signs)}; ib = {s: i for i, s in enumerate(B.signs)}
shared = [s for s in A.signs if s in ib and A.n[ia[s]] >= 5 and B.n[ib[s]] >= 5]
# per-sign markers: Stouffer z of the two independent excavations, two-sided p, BH
rows = []
for s in shared:
    z1, z2 = za[ia[s]], zb[ib[s]]
    zc = (z1 + z2) / np.sqrt(2)
    rows.append(dict(sign=s, nH=int(A.n[ia[s]]), nV=int(B.n[ib[s]]), shiftH=float(oa[ia[s]]), shiftV=float(ob[ib[s]]),
                     zH=float(z1), zV=float(z2), z=float(zc), p=float(2 * norm.sf(abs(zc)))))
ps = np.array([r["p"] for r in rows]); o = np.argsort(ps); q = np.empty(len(ps))
q[o] = np.minimum.accumulate((ps[o] * len(ps) / np.arange(1, len(ps) + 1))[::-1])[::-1]
for r, qq in zip(rows, q): r["q"] = float(min(qq, 1))
rows.sort(key=lambda r: r["p"])
print("sign  nH nV  shiftH shiftV  zH   zV   z    p     q")
for r in rows[:20]:
    print("%-5s %3d %3d %+.3f %+.3f %+.1f %+.1f %+.2f %.4f %.3f" % (r["sign"], r["nH"], r["nV"], r["shiftH"], r["shiftV"], r["zH"], r["zV"], r["z"], r["p"], r["q"]))
out["markers"] = rows
# Harappa consensus direction vector (mean z) for cross-site tests
cons = {r["sign"]: (r["zH"] + r["zV"]) / 2 for r in rows}
# ---- cross-site
sites = {"MD_icit": dataset_icit_md(), "MD_m77": dataset_md_m77(), "KAL": dataset_kal(), "LOT": dataset_lot(), "DHO": dataset_dho(),
         "VATS_strata_icit": dataset_vats_strata()}
from collections import Counter
cs = {}
for name, D in sites.items():
    S = Shift(D)
    print("\n%s units %d rel x type %s" % (name, len(D), dict(Counter((u['rel'], u['type']) for u in D).most_common(8))))
    iS = {s: i for i, s in enumerate(S.signs)}
    for nm in (5, 3):
        sig = [s for s in cons if s in iS and S.n[iS[s]] >= nm]
        if len(sig) >= 6: break
    idx = np.array([iS[s] for s in sig]); cv = np.array([cons[s] for s in sig])
    obs = spearmanr(cv, S.shifts()[idx])[0]
    nul = np.array([spearmanr(cv, S.shifts(S.perm_rel(rng))[idx])[0] for _ in range(NP)])
    p = (1 + np.sum(nul >= obs)) / (NP + 1)
    # sign agreement among strong Harappa markers (|cons z| >= 1.5)
    strong = [k for k, s in enumerate(sig) if abs(cv[k]) >= 1.5]
    agree = sum(np.sign(cv[k]) == np.sign(S.shifts()[idx][k]) for k in strong)
    print("  Harappa consensus vs %s: n=%d (nmin %d) rho=%+.3f p=%.4f; strong markers same direction %d/%d" % (name, len(sig), nm, obs, p, agree, len(strong)))
    cs[name] = dict(n=len(sig), nmin=nm, rho=float(obs), p=float(p), strong_agree=int(agree), strong_n=len(strong), units=len(D))
    # also pairwise HARP and VATS separately
    for lab, X in (("HARP", A), ("VATS", B)):
        r = compare(X, S, nperm=1000, nmin=nm)
        cs[name][lab] = {k: r[k] for k in ("n", "rho", "p")}
        print("   %s ~ %s: n=%s rho=%+.3f p=%.4f" % (lab, name, r["n"], r["rho"], r["p"]))
out["crosssite"] = cs
# pooled (independent sites only: MD_icit, KAL, LOT, DHO) Stouffer of one-sided p
zz = [norm.isf(cs[k]["p"]) for k in ("MD_icit", "KAL", "LOT", "DHO")]
w = [np.sqrt(cs[k]["n"]) for k in ("MD_icit", "KAL", "LOT", "DHO")]
zp = float(np.dot(w, zz) / np.sqrt(np.dot(w, w)))
print("\npooled other-site Stouffer (weights sqrt n) z=%.2f p=%.4f" % (zp, norm.sf(zp)))
out["crosssite_pooled"] = dict(z=zp, p=float(norm.sf(zp)), sites=["MD_icit", "KAL", "LOT", "DHO"])
# ---- text-level prediction: score each HARP text by VATS shifts (and vice versa), within type
def predict(Dtest, Strain, nmin=5):
    it = {s: i for i, s in enumerate(Strain.signs)}; sh = Strain.shifts()
    xs, ys, ts = [], [], []
    for u in Dtest:
        v = [sh[it[s]] for s in set(signs_of(u["seq"])) if s in it and Strain.n[it[s]] >= nmin]
        if v: xs.append(np.mean(v)); ys.append(u["rel"]); ts.append(u["type"])
    xs, ys = np.array(xs), np.array(ys)
    # within-type residual correlation, null = permute rel within type
    def stat(y):
        e = y.copy()
        for t in set(ts):
            g = np.array([k for k, tt in enumerate(ts) if tt == t]); e[g] = y[g] - y[g].mean()
        return spearmanr(xs, e)[0]
    obs = stat(ys); grp = defaultdict(list)
    for k, t in enumerate(ts): grp[t].append(k)
    nul = []
    for _ in range(NP):
        y = ys.copy()
        for g in grp.values(): g = np.array(g); y[g] = y[rng.permutation(g)]
        nul.append(stat(y))
    return len(xs), float(obs), float((1 + np.sum(np.array(nul) >= obs)) / (NP + 1))
for lab, Dt, St in (("VATS->HARP texts", H, B), ("HARP->VATS texts", V, A)):
    n, r, p = predict(Dt, St)
    print("%s: n=%d rho=%+.3f p=%.4f" % (lab, n, r, p)); out[lab] = dict(n=n, rho=r, p=p)
json.dump(out, open("experiments/redteam_chrono/r6.json", "w"), indent=1)
