import sys, json; sys.path.insert(0, "experiments/redteam_chrono")
from rc_lib import *
from collections import Counter
from scipy.stats import spearmanr, norm
H = dataset_harp(); V = dataset_vats(); U = H + V; fU = families(U)
fH, fV = fU[:len(H)], fU[len(H):]
rng = np.random.default_rng(11); NP = 2000
out = {}
# number of distinct families carrying each marker, per excavation
r6 = json.load(open("experiments/redteam_chrono/r6.json"))
def nfam(D, F, s):
    return len({f for u, f in zip(D, F) if s in signs_of(u["seq"])})
print("marker  famsH famsV  (families carrying the sign; z)")
fam_counts = {}
for r in r6["markers"][:12]:
    s = r["sign"]; a, b = nfam(H, fH, s), nfam(V, fV, s)
    fam_counts[s] = [a, b]
    print("%-5s %3d %3d  z=%+.2f" % (s, a, b, r["z"]))
out["marker_family_counts"] = fam_counts
# markers re-estimated with one unit per (family, period, type)
def fd(D, F):
    seen = {}
    for u, f in zip(D, F):
        seen.setdefault((f, u["rel"], u["type"]), u)
    return list(seen.values())
A, B = Shift(fd(H, fH)), Shift(fd(V, fV))
def zs(S):
    obs = S.shifts(); nul = np.array([S.shifts(S.perm_rel(rng)) for _ in range(NP)])
    return obs, (obs - nul.mean(0)) / np.maximum(nul.std(0), 1e-9)
oa, za = zs(A); ob, zb = zs(B)
ia = {s: i for i, s in enumerate(A.signs)}; ib = {s: i for i, s in enumerate(B.signs)}
rows = []
for s in A.signs:
    if s in ib and A.n[ia[s]] >= 5 and B.n[ib[s]] >= 5:
        z = (za[ia[s]] + zb[ib[s]]) / np.sqrt(2)
        rows.append(dict(sign=s, nH=int(A.n[ia[s]]), nV=int(B.n[ib[s]]), zH=float(za[ia[s]]), zV=float(zb[ib[s]]), z=float(z), p=float(2 * norm.sf(abs(z)))))
ps = np.array([r["p"] for r in rows]); o = np.argsort(ps); q = np.empty(len(ps))
q[o] = np.minimum.accumulate((ps[o] * len(ps) / np.arange(1, len(ps) + 1))[::-1])[::-1]
for r, qq in zip(rows, q): r["q"] = float(min(qq, 1))
rows.sort(key=lambda r: r["p"])
print("\nfamily-block markers (n = family-period units)")
for r in rows[:12]:
    print("%-5s %3d %3d zH %+.1f zV %+.1f z %+.2f p %.4f q %.3f" % (r["sign"], r["nH"], r["nV"], r["zH"], r["zV"], r["z"], r["p"], r["q"]))
out["family_block_markers"] = rows
# text-level prediction excluding shared families from the test set AND training set
sh = set(fH) & set(fV)
H2 = [u for u, f in zip(H, fH) if f not in sh]; V2 = [u for u, f in zip(V, fV) if f not in sh]
def predict(Dtest, Strain, nmin=5):
    it = {s: i for i, s in enumerate(Strain.signs)}; shf = Strain.shifts()
    xs, ys, ts = [], [], []
    for u in Dtest:
        v = [shf[it[s]] for s in set(signs_of(u["seq"])) if s in it and Strain.n[it[s]] >= nmin]
        if v: xs.append(np.mean(v)); ys.append(u["rel"]); ts.append(u["type"])
    xs, ys = np.array(xs), np.array(ys)
    grp = defaultdict(list)
    for k, t in enumerate(ts): grp[t].append(k)
    grp = [np.array(g) for g in grp.values()]
    def stat(y):
        e = y.copy()
        for g in grp: e[g] = y[g] - y[g].mean()
        return spearmanr(xs, e)[0]
    obs = stat(ys); nul = []
    for _ in range(NP):
        y = ys.copy()
        for g in grp: y[g] = y[rng.permutation(g)]
        nul.append(stat(y))
    return len(xs), float(obs), float((1 + np.sum(np.array(nul) >= obs)) / (NP + 1))
for lab, Dt, St in (("VATS->HARP texts, no shared families", H2, Shift(V2)), ("HARP->VATS texts, no shared families", V2, Shift(H2))):
    n, r, p = predict(Dt, St)
    print("%s: n=%d rho=%+.3f p=%.4f" % (lab, n, r, p)); out[lab] = dict(n=n, rho=r, p=p)
json.dump(out, open("experiments/redteam_chrono/r7.json", "w"), indent=1)
