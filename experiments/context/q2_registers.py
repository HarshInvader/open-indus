"""Q2a. Object-type registers: which signs / bigrams are specific to seals, sealings, tablets, copper
tablets, pottery, implements, rods?

Unit: distinct texts WITHIN each object type (a text on 30 moulded tablets counts once for tablets).
Null: object-type labels permuted within site x length-bin strata, computed EXACTLY as a sum of per-stratum hypergeometrics. BH over all
(n-gram x type) tests. Replication: each M77 survivor is mapped to Wells signs via the bridge and
re-tested on ICIT with the same null (one-sided, Bonferroni over the replicated set).
Also: register classifier (one-vs-rest AUC per type, 5-fold CV, within-site label-permutation null).
"""
import warnings
from common import *
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score

warnings.filterwarnings("ignore")
rng = np.random.default_rng(2)
NPERM = 5000


def units(recs, typekey, typemap):
    seen, out = set(), []
    for r in recs:
        ty = typemap(r[typekey])
        if ty is None: continue
        ss = signs(r["seq"])
        if not ss: continue
        k = (ty, " ".join(r["seq"]))
        if k in seen: continue
        seen.add(k)
        out.append(dict(type=ty, seq=r["seq"], site=r["site"], L=len(ss), side=r.get("side", 0)))
    return out


def enrichment(U, min_texts=5, min_type=15, feats=None, label=""):
    types = [t for t, n in Counter(u["type"] for u in U).items() if n >= min_type]
    U = [u for u in U if u["type"] in types]
    if feats is None:
        c = Counter()
        for u in U:
            for f in set(signs(u["seq"])) | ngrams(u["seq"], 2): c[f] += 1
        feats = [f for f, n in c.items() if n >= min_texts]
    fi = {f: i for i, f in enumerate(feats)}
    X = np.zeros((len(U), len(feats)), dtype=np.float32)
    for r, u in enumerate(U):
        for f in set(signs(u["seq"])) | ngrams(u["seq"], 2):
            if f in fi: X[r, fi[f]] = 1
    ti = {t: i for i, t in enumerate(types)}
    y = np.array([ti[u["type"]] for u in U])
    st = np.array([f"{u['site']}|{lenbin(u['L'])}" for u in U])
    obs, exp, p_hi, p_lo = strat_hyper_matrix(X, y, st, len(types))
    p = np.minimum(1, 2 * np.minimum(p_hi, p_lo))
    q = bh(p.ravel()).reshape(p.shape)
    rows = []
    for a, t in enumerate(types):
        for b, f in enumerate(feats):
            if q[a, b] < 0.05:
                rows.append(dict(type=t, feat=f, obs=int(obs[a, b]), exp=float(exp[a, b]), total=int(X[:, b].sum()),
                                 ratio=float((obs[a, b] + .5) / (exp[a, b] + .5)), p=float(p[a, b]), q=float(q[a, b])))
    rows.sort(key=lambda r: (r["type"], -r["ratio"]))
    print(f"\n[{label}] {len(U)} distinct type-texts, types {dict(Counter(u['type'] for u in U))}; "
          f"{len(feats)} features x {len(types)} types = {obs.size} tests; BH q<0.05 survivors: {len(rows)}")
    return rows, types, feats, (obs, exp, p_hi, p_lo)


def classifier(U, label):
    types = [t for t, n in Counter(u["type"] for u in U).items() if n >= 15]
    U = [u for u in U if u["type"] in types]
    c = Counter(f for u in U for f in set(signs(u["seq"])) | ngrams(u["seq"], 2))
    feats = [f for f, n in c.items() if n >= 3]; fi = {f: i for i, f in enumerate(feats)}
    X = np.zeros((len(U), len(feats) + 2))
    for r, u in enumerate(U):
        for f in set(signs(u["seq"])) | ngrams(u["seq"], 2):
            if f in fi: X[r, fi[f]] = 1
        X[r, -2] = u["L"] / 5; X[r, -1] = u["seq"].count("|") > 0
    st = np.array([u["site"] for u in U])
    out = {}
    print(f"  register classifier [{label}]: one-vs-rest CV AUC, null = type label permuted within site (100x)")
    for t in types:
        yb = np.array([u["type"] == t for u in U]).astype(int)
        def sc(yy, seed):
            p = np.zeros(len(yy))
            for tr, te in StratifiedKFold(5, shuffle=True, random_state=seed).split(X, yy):
                p[te] = LogisticRegression(C=0.5, max_iter=2000, class_weight="balanced").fit(X[tr], yy[tr]).predict_proba(X[te])[:, 1]
            return roc_auc_score(yy, p)
        a = sc(yb, 0)
        # only permute among sites where this type occurs alongside others
        null = np.array([sc(strat_perm(yb, st, rng), i + 1) for i in range(100)])
        out[t] = dict(n=int(yb.sum()), auc=a, null=float(null.mean()), null95=float(np.quantile(null, .95)), p=float((1 + (null >= a).sum()) / 101))
        print(f"    {t:18s} n={yb.sum():4d} AUC {a:.3f} null {null.mean():.3f} (95% {np.quantile(null,.95):.3f}) p={out[t]['p']:.3f}")
    return out


def m77_type(t):
    return {"seal": "seal", "sealing": "sealing", "miniature tablet": "tablet", "copper tablet": "copper",
            "pottery graffito": "pottery", "ivory/bone rod": "rod", "bronze implement": "implement"}.get(t)


def icit_type(t):
    if t.startswith("SEAL"): return "seal"
    if t.startswith("TAG"): return "sealing"
    if t in ("TAB:B", "TAB:I"): return "tablet"
    if t == "TAB:C": return "copper"
    if t.startswith("POT") or t.startswith("POsT"): return "pottery"
    if t == "ROD": return "rod"
    if t == "IMPL": return "implement"
    if t == "BNGL": return "bangle"
    return None


def m2w_feat(f):
    """Map an M-feature (sign or bigram) to all Wells equivalents via the bridge."""
    inv = defaultdict(list)
    for w, ms in W2M.items():
        for m in ms: inv[m].append(w)
    parts = f.split()
    opts = [inv.get(p, []) for p in parts]
    if any(not o for o in opts): return []
    res = [[]]
    for o in opts: res = [r + [x] for r in res for x in o]
    return [" ".join(r) for r in res]


def main():
    R = {}
    U = units(m77_texts(), "object_type", m77_type)
    rows, types, feats, _ = enrichment(U, label="M77")
    R["m77_survivors"] = rows
    for r in rows:
        if r["ratio"] > 1:
            print(f"  {r['type']:9s} {r['feat']:14s} obs {r['obs']:3d} exp {r['exp']:6.1f} (in {r['total']:3d} texts) ratio {r['ratio']:5.2f} q={r['q']:.2g}")
    # sensitivity: single-sided objects / side<=1 only (removes the side-2 docket formula of F15)
    U1 = [u for u in U if u["side"] in (0, 1)]
    rows1, _, _, _ = enrichment(U1, label="M77 side 0/1 only")
    R["m77_side01_survivors"] = rows1
    for r in rows1:
        if r["ratio"] > 1 and r["type"] not in ("seal",):
            print(f"  {r['type']:9s} {r['feat']:14s} obs {r['obs']:3d} exp {r['exp']:6.1f} ratio {r['ratio']:5.2f} q={r['q']:.2g}")
    R["m77_classifier"] = classifier(U, "M77")

    # ICIT replication of M77 positive survivors
    UI = units(icit_texts(), "type", icit_type)
    pos = [r for r in rows if r["ratio"] > 1]
    rep_feats, back = [], {}
    for r in pos:
        for wf in m2w_feat(r["feat"]):
            rep_feats.append(wf); back.setdefault(wf, []).append(r)
    rep_feats = sorted(set(rep_feats))
    rowsI, typesI, featsI, (obs, exp, p_hi, p_lo) = enrichment(UI, min_texts=1, feats=rep_feats, label="ICIT replication of M77 survivors")
    rep = []
    ntest = sum(1 for wf in rep_feats for r in back[wf] if r["type"] in typesI)
    for b, wf in enumerate(featsI):
        for r in back[wf]:
            if r["type"] not in typesI: continue
            a = typesI.index(r["type"])
            ok = p_hi[a, b] * ntest < 0.05
            rep.append(dict(m_feat=r["feat"], w_feat=wf, type=r["type"], icit_obs=int(obs[a, b]), icit_exp=float(exp[a, b]),
                            p_one=float(p_hi[a, b]), replicated=bool(ok)))
    print(f"  replication tests: {ntest} (Bonferroni one-sided)")
    for x in sorted(rep, key=lambda x: x["p_one"]):
        print(f"    {x['type']:9s} {x['m_feat']:12s} -> {x['w_feat']:12s} ICIT obs {x['icit_obs']:3d} exp {x['icit_exp']:6.1f} p1={x['p_one']:.4f} {'REPLICATED' if x['replicated'] else ''}")
    R["icit_replication"] = rep
    # ICIT standalone
    rowsI2, _, _, _ = enrichment(UI, label="ICIT standalone")
    R["icit_survivors"] = rowsI2
    for r in rowsI2:
        if r["ratio"] > 1:
            print(f"  {r['type']:9s} {r['feat']:14s} obs {r['obs']:3d} exp {r['exp']:6.1f} ratio {r['ratio']:5.2f} q={r['q']:.2g}")
    R["icit_classifier"] = classifier(UI, "ICIT")
    save_json("q2_registers", R)


if __name__ == "__main__":
    main()
