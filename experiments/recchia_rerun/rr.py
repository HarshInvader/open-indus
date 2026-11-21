"""Recchia & Louwerse 2016 rerun (prereg docs/prereg/recchia_rerun.md).

Their test, as far as the abstract and the brief allow: LSA document vectors for Indus texts, summed into one
vector per site (Mohenjo-daro, Harappa, Chanhu-daro, Lothal, Kalibangan), site-by-site cosines -> 2-D MDS ->
compared with the real site coordinates. Seals and sealings separately.

What we add: exact 120-assignment permutation test, site-label permutation null (sizes kept), bootstrap over
texts, leave-one-site-out, near-copy removal (experiments/fish_tick_closer_v2/dedup.py::greedy), size-matched
subsampling, a planted geographic-gradient gate, and the Mohenjo-daro vs Harappa seal check in the same space.

  board/run.sh .venv/bin/python -I experiments/recchia_rerun/rr.py sizes
  board/run.sh .venv/bin/python -I experiments/recchia_rerun/rr.py run
"""
import itertools
import json
import math
import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments/uniformity_paper/step2"))
sys.path.insert(0, str(ROOT / "experiments/fish_tick_closer_v2"))
import s2  # noqa: E402  (M77 / ICIT loaders)
import dedup  # noqa: E402  (non-chaining near-copy removal; never corpus/build.py::_close)

SEED = 20261130
K_MAIN = 100
K_SENS = (20, 50, "full")
N_PERM = 5000
N_BOOT = 1000
N_MATCH = 1000
N_PERM_LOSO = 2000
N_GATE_REP = 100
N_GATE_PERM = 1000
GATE_Q = (0.05, 0.10, 0.15, 0.20)
GATE_AT = 0.15
GATE_PASS = 0.80
GATE_STOCK = 10       # new signs per site
GATE_LAMBDA = 300.0   # km; stock of site t used by site s with weight exp(-d_st / lambda)
ALPHA = 0.05
N_MDHA = 1000

MD, HA, CD, LO, KB = "Mohenjo-daro", "Harappa", "Chanhu-daro", "Lothal", "Kalibangan"
SITES = [MD, HA, CD, LO, KB]
COORD = {  # lat, lon (deg), frozen in the prereg
    MD: (27.3243, 68.1357), HA: (30.6280, 72.8640), CD: (26.1740, 68.3240),
    LO: (22.5215, 72.2491), KB: (29.4730, 74.1300)}
M77_SITE = {"Mohenjodaro": MD, "Harappa": HA, "Chanhudaro": CD, "Lothal": LO, "Kalibangan": KB}
R_EARTH = 6371.0


# =========================================================================== geography
def gc_km(a, b):
    (la1, lo1), (la2, lo2) = [(math.radians(x), math.radians(y)) for x, y in (a, b)]
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * R_EARTH * math.asin(math.sqrt(h))


def xy_km(sites):
    lat0 = math.radians(np.mean([COORD[s][0] for s in sites]))
    return np.array([[R_EARTH * math.radians(COORD[s][1]) * math.cos(lat0), R_EARTH * math.radians(COORD[s][0])]
                     for s in sites])


def gc_matrix(sites):
    return np.array([[gc_km(COORD[a], COORD[b]) for b in sites] for a in sites])


# =========================================================================== texts
def signs_of(seq):
    return [x for x in seq if x not in ("|", "#")]


def m77_all():
    """Every M77 object side; seq kept with '|' / '#' for dedup; terms exclude them."""
    out = []
    for t in s2.m77_texts():
        sg = signs_of(t["seq"])
        if sg:
            out.append(dict(id=f"m{t['text_no']}.{t['side']}", site=M77_SITE.get(t["site"], t["site"]),
                            obj=t["object_type"], seq=list(t["seq"]), signs=sg, complete=bool(t.get("complete"))))
    return out


def icit_all():
    out = []
    for t in s2.icit_texts():
        sg = signs_of(t["seq"])
        if not sg:
            continue
        ty = t["type"] or ""
        obj = "sealing" if ty == "SEAL:R" else ("seal" if ty.startswith("SEAL") else ty)
        out.append(dict(id=t["id"], site=t["site"], obj=obj, seq=list(t["seq"]), signs=sg, complete=bool(t["complete"])))
    return out


def analysis_set(corpus, obj, complete_only=False, dedup_on=False):
    T = [t for t in corpus if t["obj"] == obj and t["site"] in SITES and (t["complete"] or not complete_only)]
    if dedup_on:
        out = []
        for s in SITES:
            out += dedup.greedy([t for t in T if t["site"] == s])
        T = out
    return T


# =========================================================================== LSA
class Space:
    """Log-entropy weighted term-document matrix of `train` texts, truncated SVD with k dimensions.
    Document vector of any text = weighted term vector . V_k (the U_k S_k row for training texts)."""

    def __init__(self, train, k):
        vocab = sorted({s for t in train for s in t["signs"]})
        self.ix = {s: i for i, s in enumerate(vocab)}
        X = self._tf(train)
        N = X.shape[0]
        gf = X.sum(0)
        P = np.divide(X, gf, out=np.zeros_like(X), where=gf > 0)
        with np.errstate(divide="ignore", invalid="ignore"):
            ent = np.where(P > 0, P * np.log(P), 0.0).sum(0)
        self.g = 1.0 + ent / math.log(N)
        W = np.log1p(X) * self.g
        _, S, Vt = np.linalg.svd(W, full_matrices=False)
        r = int((S > 1e-10 * S[0]).sum())
        kk = r if k == "full" else min(k, r)
        self.V = Vt[:kk].T
        self.k = kk

    def _tf(self, texts):
        X = np.zeros((len(texts), len(self.ix)))
        for i, t in enumerate(texts):
            for s in t["signs"]:
                j = self.ix.get(s)
                if j is not None:
                    X[i, j] += 1
        return X

    def docs(self, texts, unit=False):
        D = (np.log1p(self._tf(texts)) * self.g) @ self.V
        if unit:
            n = np.linalg.norm(D, axis=1, keepdims=True)
            D = np.divide(D, n, out=np.zeros_like(D), where=n > 0)
        return D


# =========================================================================== fit statistics
def cos_dist(V):
    n = np.linalg.norm(V, axis=1, keepdims=True)
    U = V / np.where(n > 0, n, 1)
    return np.clip(1.0 - U @ U.T, 0.0, 2.0)


def cmds2(Dm):
    m = Dm.shape[0]
    J = np.eye(m) - 1.0 / m
    B = -0.5 * J @ (Dm ** 2) @ J
    w, v = np.linalg.eigh(B)
    o = np.argsort(w)[::-1][:2]
    return v[:, o] * np.sqrt(np.clip(w[o], 0, None))


def _norm(X):
    X = X - X.mean(0)
    f = np.linalg.norm(X)
    return X / f if f > 0 else X


def proc_r(X, Y):
    """Procrustes / bidimensional-regression correlation with rotation, reflection and scaling (0..1)."""
    return float(np.linalg.svd(_norm(X).T @ _norm(Y), compute_uv=False).sum())


def pair_r(a, b):
    iu = np.triu_indices(a.shape[0], 1)
    x, y = a[iu], b[iu]
    if x.std() == 0 or y.std() == 0:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def stats_from_sitevecs(V, sites):
    Dm = cos_dist(V)
    X = cmds2(Dm)
    Y = xy_km(sites)
    G = gc_matrix(sites)
    mds_d = np.sqrt(((X[:, None, :] - X[None, :, :]) ** 2).sum(-1))
    return dict(R_proc=proc_r(X, Y), r_mds=pair_r(mds_d, G), r_cos=pair_r(Dm, G)), X, Dm


def exact_perm(V, sites):
    """All m! assignments of coordinates to sites; p = share with R_proc >= observed (observed included)."""
    X = cmds2(cos_dist(V))
    Y = xy_km(sites)
    obs = proc_r(X, Y)
    vals = [proc_r(X, Y[list(p)]) for p in itertools.permutations(range(len(sites)))]
    vals = np.array(vals)
    return float((vals >= obs - 1e-12).mean()), int((vals > obs + 1e-12).sum()) + 1, len(vals)


def site_sums(D, lab, sites):
    return np.vstack([D[lab == s].sum(0) for s in sites])


def label_perm(D, lab, sites, n, rng):
    """Shuffle site labels within the analysed set (sizes kept); null of R_proc."""
    sizes = [int((lab == s).sum()) for s in sites]
    cuts = np.cumsum(sizes)[:-1]
    Y = xy_km(sites)
    out = np.empty(n)
    for i in range(n):
        Dp = D[rng.permutation(len(D))]
        V = np.vstack([b.sum(0) for b in np.split(Dp, cuts)])
        out[i] = proc_r(cmds2(cos_dist(V)), Y)
    return out


def pval(null, obs):
    return float((1 + (null >= obs - 1e-12).sum()) / (1 + len(null)))


# =========================================================================== analyses
def full_block(D, lab, sites, rng, n_perm):
    V = site_sums(D, lab, sites)
    st, X, Dm = stats_from_sitevecs(V, sites)
    pe, rank, nass = exact_perm(V, sites)
    null = label_perm(D, lab, sites, n_perm, rng)
    return dict(sites=sites, n=[int((lab == s).sum()) for s in sites], **st, p_exact=pe, rank=rank, n_assign=nass,
                p_label=pval(null, st["R_proc"]), null_median=float(np.median(null)), null_q95=float(np.quantile(null, 0.95)),
                cosdist={f"{a}|{b}": float(Dm[i, j]) for i, a in enumerate(sites) for j, b in enumerate(sites) if i < j},
                mds=X.tolist())


def bootstrap(D, lab, sites, rng):
    idx = {s: np.where(lab == s)[0] for s in sites}
    R, pe = [], []
    for _ in range(N_BOOT):
        V = np.vstack([D[rng.choice(idx[s], len(idx[s]), replace=True)].sum(0) for s in sites])
        R.append(stats_from_sitevecs(V, sites)[0]["R_proc"])
        pe.append(exact_perm(V, sites)[0])
    R, pe = np.array(R), np.array(pe)
    return dict(R_median=float(np.median(R)), R_ci=[float(np.quantile(R, 0.025)), float(np.quantile(R, 0.975))],
                share_p_exact_le_05=float((pe <= ALPHA).mean()))


def loso(D, lab, sites, rng):
    out = {}
    for s in sites:
        keep = [x for x in sites if x != s]
        m = np.isin(lab, keep)
        b = full_block(D[m], lab[m], keep, rng, N_PERM_LOSO)
        out[s] = {k: b[k] for k in ("R_proc", "r_mds", "r_cos", "p_exact", "rank", "n_assign", "p_label", "null_q95")}
    return out


MATCH_MIN = 20  # sites with fewer texts are left out of the size-matched analysis


def size_matched(D, lab, sites, rng):
    sites = [s for s in sites if (lab == s).sum() >= MATCH_MIN]
    idx = {s: np.where(lab == s)[0] for s in sites}
    n = min(len(v) for v in idx.values())
    Y = xy_km(sites)
    real, null, pe = [], [], []
    for _ in range(N_MATCH):
        sub = {s: rng.choice(idx[s], n, replace=False) for s in sites}
        V = np.vstack([D[sub[s]].sum(0) for s in sites])
        real.append(proc_r(cmds2(cos_dist(V)), Y))
        pe.append(exact_perm(V, sites)[0])
        allx = np.concatenate([sub[s] for s in sites])
        allx = allx[rng.permutation(len(allx))]
        Vn = np.vstack([D[allx[i * n:(i + 1) * n]].sum(0) for i in range(len(sites))])
        null.append(proc_r(cmds2(cos_dist(Vn)), Y))
    real, null = np.array(real), np.array(null)
    med = float(np.median(real))
    return dict(sites=sites, n_per_site=n, R_median=med, null_median=float(np.median(null)), null_q95=float(np.quantile(null, 0.95)),
                p_matched=float((1 + (null >= med).sum()) / (1 + len(null))), share_p_exact_le_05=float((np.array(pe) <= ALPHA).mean()))


def mdha_check(D, lab, rng):
    """Cosine distance Mohenjo-daro vs Harappa (size-matched) against two disjoint random sets of the larger site."""
    a, b = (MD, HA) if (lab == MD).sum() >= (lab == HA).sum() else (HA, MD)
    ia, ib = np.where(lab == a)[0], np.where(lab == b)[0]
    n = len(ib)
    if 2 * n > len(ia):
        n = len(ia) // 2
    betw, within = [], []
    for _ in range(N_MDHA):
        sa = rng.choice(ia, n, replace=False)
        sb = rng.choice(ib, n, replace=False)
        betw.append(cos_dist(np.vstack([D[sa].sum(0), D[sb].sum(0)]))[0, 1])
        h = rng.permutation(ia)[:2 * n]
        within.append(cos_dist(np.vstack([D[h[:n]].sum(0), D[h[n:]].sum(0)]))[0, 1])
    betw, within = np.array(betw), np.array(within)
    return dict(larger=a, n=int(n), between_median=float(np.median(betw)), within_median=float(np.median(within)),
                within_q95=float(np.quantile(within, 0.95)), share_between_gt_within_q95=float((betw > np.quantile(within, 0.95)).mean()),
                conflict=bool(np.median(betw) > np.quantile(within, 0.95)))


# =========================================================================== planted gate
def plant(T, q, rng):
    """Labels already shuffled. Each token of a site-s text is replaced with prob q by a sign from the stock of
    site t, t drawn with weight exp(-d_st / lambda)."""
    G = gc_matrix(SITES)
    W = np.exp(-G / GATE_LAMBDA)
    W = W / W.sum(1, keepdims=True)
    out = []
    for t in T:
        si = SITES.index(t["site"])
        sg = []
        for s in t["signs"]:
            if rng.random() < q:
                tt = rng.choice(len(SITES), p=W[si])
                sg.append(f"P{tt}_{rng.integers(GATE_STOCK)}")
            else:
                sg.append(s)
        out.append(dict(t, signs=sg))
    return out


def gate(corpus, obj, rng):
    T0 = analysis_set(corpus, obj)
    rest = [t for t in corpus if not (t["obj"] == obj and t["site"] in SITES)]
    res = {}
    for q in GATE_Q:
        hit = 0
        for _ in range(N_GATE_REP):
            labs = [t["site"] for t in T0]
            perm = rng.permutation(len(labs))
            Ts = [dict(t, site=labs[perm[i]]) for i, t in enumerate(T0)]
            Tp = plant(Ts, q, rng)
            sp = Space(rest + Tp, K_MAIN)
            D = sp.docs(Tp)
            lab = np.array([t["site"] for t in Tp])
            V = site_sums(D, lab, SITES)
            obs = proc_r(cmds2(cos_dist(V)), xy_km(SITES))
            pe = exact_perm(V, SITES)[0]
            pl = pval(label_perm(D, lab, SITES, N_GATE_PERM, rng), obs)
            hit += (pe <= ALPHA and pl <= ALPHA)
        res[str(q)] = hit / N_GATE_REP
        print(f"  gate {obj} q={q}: {res[str(q)]:.2f}", flush=True)
    res["pass"] = res[str(GATE_AT)] >= GATE_PASS
    return res


# =========================================================================== driver
def sizes():
    for name, corp in (("M77", m77_all()), ("ICIT", icit_all())):
        for obj in ("seal", "sealing"):
            for co in (False, True):
                T = analysis_set(corp, obj, complete_only=co)
                Td = analysis_set(corp, obj, complete_only=co, dedup_on=True)
                print(name, obj, "complete" if co else "all", len(T), dict(Counter(t["site"] for t in T)), "dedup", len(Td), dict(Counter(t["site"] for t in Td)))


def present(sites, lab):
    return [s for s in sites if (lab == s).sum() >= 2]


def block(name, corpus, obj, rng, k=K_MAIN, unit=False, complete_only=False, dedup_on=False, local=False, extra=True):
    T = analysis_set(corpus, obj, complete_only, dedup_on)
    sp = Space(T if local else corpus, k)
    D = sp.docs(T, unit=unit)
    lab = np.array([t["site"] for t in T])
    sites = present(SITES, lab)
    r = dict(name=name, k=sp.k, full=full_block(D, lab, sites, rng, N_PERM))
    if extra:
        r["boot"] = bootstrap(D, lab, sites, rng)
        r["loso"] = loso(D, lab, sites, rng)
        r["matched"] = size_matched(D, lab, sites, rng)
        r["mdha"] = mdha_check(D, lab, rng)
    f = r["full"]
    print(f"{name}: k={sp.k} n={f['n']} R={f['R_proc']:.3f} r_mds={f['r_mds']:.3f} r_cos={f['r_cos']:.3f} "
          f"p_exact={f['p_exact']:.4f} p_label={f['p_label']:.4f}", flush=True)
    return r


def run():
    rng = np.random.default_rng(SEED)
    m77, icit = m77_all(), icit_all()
    out = {"primary": {}, "variants": {}, "gate": {}}
    print("== gate", flush=True)
    for obj in ("seal", "sealing"):
        out["gate"][obj] = gate(m77, obj, rng)
    print("== primary", flush=True)
    for obj in ("seal", "sealing"):
        out["primary"][obj] = block(f"M77 {obj} all k{K_MAIN}", m77, obj, rng)
        out["variants"][f"{obj}_dedup"] = block(f"M77 {obj} dedup", m77, obj, rng, dedup_on=True)
    print("== sensitivity", flush=True)
    for obj in ("seal", "sealing"):
        for k in K_SENS:
            out["variants"][f"{obj}_k{k}"] = block(f"M77 {obj} k{k}", m77, obj, rng, k=k, extra=False)
        out["variants"][f"{obj}_unit"] = block(f"M77 {obj} unit-norm docs", m77, obj, rng, unit=True, extra=False)
        out["variants"][f"{obj}_complete"] = block(f"M77 {obj} complete only", m77, obj, rng, complete_only=True, extra=False)
        out["variants"][f"{obj}_local"] = block(f"M77 {obj} local space", m77, obj, rng, local=True, extra=False)
        out["variants"][f"{obj}_icit"] = block(f"ICIT {obj}", icit, obj, rng, extra=False)
        out["variants"][f"{obj}_icit_dedup"] = block(f"ICIT {obj} dedup", icit, obj, rng, dedup_on=True, extra=False)
    json.dump(out, open(HERE / "results.json", "w"), indent=1)
    print("done", flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "sizes":
        sizes()
    elif sys.argv[1] == "run":
        run()
