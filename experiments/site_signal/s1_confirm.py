"""T5 site signal, pre-registered run (docs/prereg/site_signal.md).

  .venv/bin/python experiments/site_signal/s1_confirm.py dryrun   # site labels shuffled first (code check)
  .venv/bin/python experiments/site_signal/s1_confirm.py final
"""
import sys
import time
from collections import Counter, defaultdict
from math import radians, sin, cos, asin, sqrt

import numpy as np
from scipy.stats import fisher_exact

import lib

MODE = sys.argv[1] if len(sys.argv) > 1 else "dryrun"
R_MAIN = int(sys.argv[2]) if len(sys.argv) > 2 else 1000      # permutations for P1-P4
R_SEC = int(sys.argv[3]) if len(sys.argv) > 3 else 500        # permutations for secondary analyses
POWER_REPS = int(sys.argv[4]) if len(sys.argv) > 4 else 100
MD, HA = "Mohenjo-daro", "Harappa"
rng0 = np.random.default_rng(lib.SEED)
OUT = {"mode": MODE}
t0 = time.time()


def log(*a):
    print(*a, flush=True)


def load(variant="strict"):
    E = lib.eligible_icit(variant)
    if MODE == "dryrun":  # destroy any real site signal, keep everything else
        sites = [t["site"] for t in E]
        perm = np.random.default_rng(1).permutation(len(E))
        for t, j in zip(E, perm):
            t["site"] = sites[j]
    return E


def binary_test(texts, slot, amap, strata=None, R=R_MAIN, model="nb", seed=lib.SEED):
    """MD (1) vs Harappa (0) CV AUC with permutation p (site labels permuted within strata)."""
    X, vocab = lib.design(texts, amap, slot)
    y = np.array([1 if t["site"] == MD else 0 for t in texts])
    g = np.array([t["fam"] for t in texts])
    keep = np.asarray(X.sum(1)).ravel() > 0
    X, y, g = X[keep], y[keep], g[keep]
    st = np.zeros(len(y), int) if strata is None else np.asarray(strata)[keep]
    P = lib.oof_scores(X, y, g, model=model, classes=[0, 1], seed=seed)
    obs = lib.auc(y, P[:, 1])
    ba = lib.bal_acc(y, P, [0, 1])
    rng = np.random.default_rng(seed + 7)
    null = np.empty(R)
    for r in range(R):
        yp = lib.permute_within(y, st, rng)
        Pp = lib.oof_scores(X, yp, g, model=model, classes=[0, 1], seed=seed + r + 1, reps=1)
        null[r] = lib.auc(yp, Pp[:, 1])
    p = (1 + np.sum(null >= obs)) / (R + 1)
    return dict(auc=obs, bal_acc=ba, p=p, null_mean=null.mean(), null_q95=np.quantile(null, 0.95),
                n=int(len(y)), n_md=int(y.sum()), n_h=int(len(y) - y.sum()), n_feat=X.shape[1]), null


def transfer_test(texts, amap, slot="medial", R=R_MAIN, seed=lib.SEED):
    """Train on one period band, test on the other (both directions); mean AUC; null permutes site
    within band."""
    from sklearn.naive_bayes import BernoulliNB
    X, vocab = lib.design(texts, amap, slot)
    y = np.array([1 if t["site"] == MD else 0 for t in texts])
    b = np.array([lib.band(t) for t in texts])
    keep = np.asarray(X.sum(1)).ravel() > 0
    X, y, b = X[keep], y[keep], b[keep]

    def stat(yy):
        out = []
        for tr, te in (("earlier", "late"), ("late", "earlier")):
            itr, ite = b == tr, b == te
            clf = BernoulliNB(alpha=1.0, fit_prior=False).fit(X[itr], yy[itr])
            out.append(lib.auc(yy[ite], clf.predict_proba(X[ite])[:, list(clf.classes_).index(1)]))
        return out
    obs = stat(y)
    rng = np.random.default_rng(seed + 11)
    null = np.array([np.mean(stat(lib.permute_within(y, b, rng))) for _ in range(R)])
    p = (1 + np.sum(null >= np.mean(obs))) / (R + 1)
    return dict(auc_earlier_to_late=obs[0], auc_late_to_earlier=obs[1], auc_mean=float(np.mean(obs)),
                p=p, null_mean=null.mean(), null_q95=np.quantile(null, 0.95), n=int(len(y)),
                cells=Counter(zip(y.tolist(), b.tolist())).most_common())


def multisite_test(texts, sites, amap, slot="all", R=R_MAIN, seed=lib.SEED):
    T = [t for t in texts if t["site"] in sites]
    X, vocab = lib.design(T, amap, slot)
    y = np.array([t["site"] for t in T])
    g = np.array([t["fam"] for t in T])
    P = lib.oof_scores(X, y, g, classes=sites, seed=seed)
    obs = lib.bal_acc(y, P, sites)
    rng = np.random.default_rng(seed + 13)
    null = np.empty(R)
    for r in range(R):
        yp = y[rng.permutation(len(y))]
        null[r] = lib.bal_acc(yp, lib.oof_scores(X, yp, g, classes=sites, seed=seed + r + 1, reps=1), sites)
    p = (1 + np.sum(null >= obs)) / (R + 1)
    # pairwise AUCs (descriptive)
    pair = {}
    for i, a in enumerate(sites):
        for c in sites[i + 1:]:
            m = (y == a) | (y == c)
            s = P[m, sites.index(a)] / (P[m, sites.index(a)] + P[m, sites.index(c)] + 1e-12)
            pair[a + "|" + c] = lib.auc((y[m] == a).astype(int), s)
    return dict(bal_acc=obs, chance=1 / len(sites), p=p, null_mean=null.mean(), null_q95=np.quantile(null, 0.95),
                n=dict(Counter(y.tolist())), pairwise_auc=pair)


def holm(ps):
    k = len(ps); order = np.argsort(ps); adj = np.empty(k); run = 0
    for r, i in enumerate(order):
        run = max(run, min(1, (k - r) * ps[i])); adj[i] = run
    return adj


A0, A1, A2 = (lib.allograph_map(l) for l in ("A0", "A1", "A2"))
E = load("strict")
MH = [t for t in E if t["site"] in (MD, HA)]
MH3 = [t for t in MH if len(t["signs"]) >= 3]
DATED3 = [t for t in MH3 if lib.band(t) is not None]
log("sizes", len(E), len(MH), len(MH3), len(DATED3))

# ------------------------------------------------------------------ P1-P4
res = {}
res["P1"], nullP1 = binary_test(MH, "all", A0)
log("P1", res["P1"])
res["P2"], nullP2 = binary_test(DATED3, "medial", A1, strata=[lib.band(t) for t in DATED3])
log("P2", res["P2"])
res["P3"] = transfer_test(DATED3, A1)
log("P3", res["P3"])
sites30 = [s for s, c in Counter(t["site"] for t in E).most_common() if c >= 30 and s != "Unknown"]
res["P4"] = multisite_test(E, sites30, A1)
log("P4", res["P4"])
ps = [res[k]["p"] for k in ("P1", "P2", "P3", "P4")]
for k, a in zip(("P1", "P2", "P3", "P4"), holm(ps)):
    res[k]["p_holm"] = a
OUT["confirmatory"] = res

# ------------------------------------------------------------------ power for P2 (planted local stock)
def plant(texts, q, rng, stock):
    out = []
    for t in texts:
        t2 = dict(t)
        if t["site"] == MD or len(t["signs"]) < 3:
            out.append(t2); continue
        sg = list(t["signs"])
        for i in range(1, len(sg) - 1):
            if rng.random() < q:
                sg[i] = stock[rng.integers(len(stock))]
        # rebuild runs with same line lengths
        runs, k = [], 0
        for r in t["runs"]:
            runs.append(sg[k:k + len(r)]); k += len(r)
        t2["signs"], t2["runs"] = sg, runs
        out.append(t2)
    return out


medial_freq = Counter(s for t in DATED3 for s in t["signs"][1:-1])
common = sorted(s for s, c in medial_freq.items() if c >= 5)
power = {}
thr = res["P2"]["null_q95"]
for q in (0.1, 0.2, 0.3):
    hits, aucs = 0, []
    rng = np.random.default_rng(lib.SEED + int(q * 100))
    for rep in range(POWER_REPS):
        T = [dict(t) for t in DATED3]
        bands = [lib.band(t) for t in T]
        sites = np.array([t["site"] for t in T])
        bands_a = np.array(bands)
        sp = sites.copy()
        for bb in np.unique(bands_a):  # null world: site permuted within band
            ix = np.where(bands_a == bb)[0]; sp[ix] = sites[rng.permutation(ix)]
        for t, s in zip(T, sp):
            t["site"] = s
        stock = list(rng.choice(common, size=20, replace=False))
        T = plant(T, q, rng, stock)
        X, _ = lib.design(T, A1, "medial")
        y = np.array([1 if t["site"] == MD else 0 for t in T])
        keep = np.asarray(X.sum(1)).ravel() > 0
        P = lib.oof_scores(X[keep], y[keep], np.array([t["fam"] for t in T])[keep], classes=[0, 1], reps=1,
                           seed=lib.SEED + rep)
        a = lib.auc(y[keep], P[:, 1]); aucs.append(a); hits += a >= thr
    power[str(q)] = dict(power=hits / POWER_REPS, mean_auc=float(np.mean(aucs)))
    log("power q", q, power[str(q)])
OUT["power_P2"] = dict(threshold_auc=thr, stock_size=20, levels=power,
                       note="null world (site permuted within band) + Harappa medial tokens replaced by a 20-sign stock with prob q")

# ------------------------------------------------------------------ verdict (rule fixed in prereg)
P1ok = res["P1"]["p_holm"] < 0.05
P2ok = res["P2"]["p_holm"] < 0.05
P3ok = res["P3"]["p"] < 0.05
pw = power["0.2"]["power"]
if P2ok:
    verdict = "SUPPORT" + (" (place: transfers across period bands)" if P3ok else " (does not transfer across bands: place vs time unresolved)")
elif not P1ok and pw >= 0.8:
    verdict = "REFUTE (homogeneous pool at stated power)"
elif P1ok:
    verdict = "SITE SIGNAL OUTSIDE THE OPEN SLOT (P1 passes, P2 fails)"
else:
    verdict = "INCONCLUSIVE"
OUT["verdict"] = verdict
log("VERDICT", verdict)

# ------------------------------------------------------------------ secondary: slots x allograph level
sec = {}
for lvname, am in (("A0", A0), ("A1", A1), ("A2", A2)):
    for slot in ("opener", "closer", "frame", "medial", "all"):
        r, _ = binary_test(MH3, slot, am, R=R_SEC, seed=lib.SEED + 100)
        sec[f"{lvname}_{slot}"] = r
        log("slot", lvname, slot, round(r["auc"], 3), r["p"])
# period-stratified slot comparison (A1)
for slot in ("opener", "closer", "frame", "all"):
    r, _ = binary_test(DATED3, slot, A1, strata=[lib.band(t) for t in DATED3], R=R_SEC, seed=lib.SEED + 200)
    sec[f"A1_{slot}_banded"] = r
    log("banded", slot, round(r["auc"], 3), r["p"])
# logistic sensitivity for P2
r, _ = binary_test(DATED3, "medial", A1, strata=[lib.band(t) for t in DATED3], R=200, model="lr", seed=lib.SEED + 300)
sec["P2_logistic"] = r
log("P2 logistic", r)
OUT["secondary_slots"] = sec

# within-site time yardstick (A1): earlier vs late inside each site
yard = {}
for s in (MD, HA):
    T = [t for t in DATED3 if t["site"] == s]
    for t in T:
        t["_site_bak"] = t["site"]; t["site"] = MD if lib.band(t) == "late" else HA
    for slot in ("medial", "all"):
        r, _ = binary_test(T, slot, A1, R=R_SEC, seed=lib.SEED + 400)
        yard[f"{s}_{slot}"] = r
        log("time yardstick", s, slot, round(r["auc"], 3), r["p"])
    for t in T:
        t["site"] = t.pop("_site_bak")
OUT["time_yardstick"] = yard

# ------------------------------------------------------------------ drivers (medial, A1, all MH3)
X, vocab = lib.design(MH3, A1, "medial")
y = np.array([1 if t["site"] == MD else 0 for t in MH3])
g = np.array([t["fam"] for t in MH3])
keep = np.asarray(X.sum(1)).ravel() > 0
Xk, yk, gk = X[keep], y[keep], g[keep]
base = lib.auc(yk, lib.oof_scores(Xk, yk, gk, classes=[0, 1], reps=5)[:, 1])
uni = [v for v in vocab if v.startswith("u:")]
rows = []
Xd = Xk.toarray()
for u in uni:
    j = vocab.index(u)
    a = int(Xd[yk == 1, j].sum()); b = int(Xd[yk == 0, j].sum())
    if a + b < 8:
        continue
    _, p = fisher_exact([[a, (yk == 1).sum() - a], [b, (yk == 0).sum() - b]])
    s = u[2:]
    cols = [i for i, v in enumerate(vocab) if v == u or (v.startswith("b:") and s in v[2:].split("_"))]
    Xa = Xk.tolil(copy=True); Xa[:, cols] = 0; Xa = Xa.tocsr()
    ka = np.asarray(Xa.sum(1)).ravel() > 0
    a2 = lib.auc(yk[ka], lib.oof_scores(Xa[ka], yk[ka], gk[ka], classes=[0, 1], reps=5)[:, 1])
    rows.append(dict(sign=s, md=a, h=b, rate_md=a / (yk == 1).sum(), rate_h=b / (yk == 0).sum(), p=p,
                     auc_drop=base - a2, allograph_group=next((r for r, m in lib.allograph_groups("A1").items() if s in m), None)))
ps = np.array([r["p"] for r in rows]); order = np.argsort(ps); m = len(ps); q = np.empty(m); run = 1
for rank, i in enumerate(order[::-1]):
    run = min(run, ps[i] * m / (m - rank)); q[i] = run
for r, qq in zip(rows, q):
    r["q"] = qq
rows.sort(key=lambda r: -r["auc_drop"])
OUT["drivers"] = dict(base_auc=base, n_tested=len(rows), top_by_auc_drop=rows[:15],
                      bh_q10=[r for r in sorted(rows, key=lambda r: r["p"]) if r["q"] < 0.10])
log("drivers base", round(base, 3), [(r["sign"], round(r["auc_drop"], 3), r["md"], r["h"], round(r["q"], 3)) for r in rows[:10]])

# allograph variant use by site (A1 groups): does the variant choice split MD vs Harappa?
allo = {}
for root, members in lib.allograph_groups("A1").items():
    cnt = {s: Counter() for s in (MD, HA)}
    for t in MH:
        for x in t["signs"]:
            if x in members:
                cnt[t["site"]][x] += 1
    tot = sum(sum(c.values()) for c in cnt.values())
    if tot < 8:
        continue
    top = Counter({k: cnt[MD][k] + cnt[HA][k] for k in members}).most_common(1)[0][0]
    a, b = cnt[MD][top], cnt[HA][top]
    _, p = fisher_exact([[a, sum(cnt[MD].values()) - a], [b, sum(cnt[HA].values()) - b]])
    allo[root] = dict(md=dict(cnt[MD]), h=dict(cnt[HA]), main_variant=top, p_fisher=p)
OUT["allograph_split"] = allo
log("allograph split", {k: (v["md"], v["h"], round(v["p_fisher"], 3)) for k, v in allo.items()})

# ------------------------------------------------------------------ robustness variants (exploratory)
rob = {}
for v in ("rep", "all"):
    Ev = load(v)
    MHv = [t for t in Ev if t["site"] in (MD, HA)]
    D3 = [t for t in MHv if len(t["signs"]) >= 3 and lib.band(t) is not None]
    r1, _ = binary_test(MHv, "all", A0, R=R_SEC)
    r2, _ = binary_test(D3, "medial", A1, strata=[lib.band(t) for t in D3], R=R_SEC)
    rob[v] = dict(P1=r1, P2=r2)
    log("robust", v, round(r1["auc"], 3), r1["p"], round(r2["auc"], 3), r2["p"])
# undated included, medial A1 unstratified
r, _ = binary_test(MH3, "medial", A1, R=R_SEC)
rob["strict_medial_A1_alltexts"] = r
OUT["robustness"] = rob

# M77 replication (Mahadevan list lumps Wells carving variants; same objects as ICIT, not independent)
M = lib.eligible_m77()
if MODE == "dryrun":
    ss = [t["site"] for t in M]; pm = np.random.default_rng(2).permutation(len(M))
    for t, j in zip(M, pm):
        t["site"] = ss[j]
MM = [t for t in M if t["site"] in (MD, HA)]
m77 = {}
for slot, TT in (("all", MM), ("medial", [t for t in MM if len(t["signs"]) >= 3])):
    r, _ = binary_test(TT, slot, {}, R=R_SEC)
    m77[slot] = r
    log("M77", slot, round(r["auc"], 3), r["p"])
OUT["m77"] = m77

# multisite >= 20 seals (secondary, 6 sites)
sites20 = [s for s, c in Counter(t["site"] for t in E).most_common() if c >= 20 and s != "Unknown"]
OUT["P4_sites20"] = multisite_test(E, sites20, A1, R=R_SEC)
log("P4 sites20", OUT["P4_sites20"])

# ------------------------------------------------------------------ P5 beta diversity vs distance (low power)
def hav(a, b):
    (la1, lo1), (la2, lo2) = COORD[a], COORD[b]
    la1, lo1, la2, lo2 = map(radians, (la1, lo1, la2, lo2))
    h = sin((la2 - la1) / 2) ** 2 + cos(la1) * cos(la2) * sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371 * asin(sqrt(h))


COORD = lib.COORDS


def beta(sites, n_rare, R=200, seed=lib.SEED):
    rng = np.random.default_rng(seed)
    bysite = {s: [lib.mapped(t["signs"], A1) for t in E if t["site"] == s] for s in sites}
    def dissim(groups):
        k = len(sites); BC = np.zeros((k, k)); JA = np.zeros((k, k))
        for _ in range(R):
            prof = []
            for s in sites:
                ix = rng.choice(len(groups[s]), n_rare, replace=False)
                prof.append(Counter(x for i in ix for x in groups[s][i]))
            for i in range(k):
                for j in range(i + 1, k):
                    a, b = prof[i], prof[j]
                    keys = set(a) | set(b)
                    num = sum(abs(a[x] - b[x]) for x in keys); den = sum(a.values()) + sum(b.values())
                    BC[i, j] += num / den
                    JA[i, j] += 1 - len(set(a) & set(b)) / len(keys)
        return BC / R, JA / R
    BC, JA = dissim(bysite)
    # pooled-labels null: same sizes drawn from one pan-Indus pool
    pool = [x for s in sites for x in bysite[s]]
    BCn, JAn = dissim({s: pool for s in sites})
    k = len(sites); iu = np.triu_indices(k, 1)
    D = np.array([[hav(a, b) if a != b else 0 for b in sites] for a in sites])
    from itertools import permutations
    def mantel(M):
        x, yv = D[iu], M[iu]
        obs = np.corrcoef(x, yv)[0, 1]
        perms = list(permutations(range(k)))
        null = []
        for pmt in perms:
            Mp = M[np.ix_(pmt, pmt)]
            Mp = np.triu(Mp) + np.triu(Mp, 1).T if False else Mp
            Ms = np.maximum(Mp, Mp.T)
            null.append(np.corrcoef(x, Ms[iu])[0, 1])
        return obs, (np.sum(np.array(null) >= obs - 1e-12)) / len(null), len(perms)
    BCs, JAs = np.maximum(BC, BC.T), np.maximum(JA, JA.T)
    mb = mantel(BCs); mj = mantel(JAs)
    return dict(sites=sites, n_rarefied=n_rare, bray_curtis=BCs[iu].tolist(), jaccard=JAs[iu].tolist(),
                bray_curtis_pool_null=np.maximum(BCn, BCn.T)[iu].tolist(), jaccard_pool_null=np.maximum(JAn, JAn.T)[iu].tolist(),
                dist_km=D[iu].tolist(), mantel_bc=dict(r=mb[0], p=mb[1], n_perm=mb[2]),
                mantel_jaccard=dict(r=mj[0], p=mj[1], n_perm=mj[2]),
                excess_bc_mean=float(np.mean(BCs[iu] - np.maximum(BCn, BCn.T)[iu])))


P5 = beta(sites30, 30)
log("P5", P5["mantel_bc"], P5["mantel_jaccard"], "excess BC", round(P5["excess_bc_mean"], 4))
P5b = beta([s for s in sites20 if s in COORD], 20)
log("P5 sites20", P5b["mantel_bc"], P5b["mantel_jaccard"], "excess BC", round(P5b["excess_bc_mean"], 4))
OUT["P5"] = P5
OUT["P5_sites20"] = P5b
OUT["runtime_s"] = time.time() - t0
lib.jdump(OUT, lib.HERE / f"s1_{MODE}.json")
log("done", round(time.time() - t0))
