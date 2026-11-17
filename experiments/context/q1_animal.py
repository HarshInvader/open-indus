"""Q1. Does the whole text predict the seal animal (field symbol)?

Unit: distinct seal texts (one per sequence; texts seen under >1 animal class are dropped and counted).
Model: L2 logistic regression on whole-text features; 5-fold stratified CV; metric = balanced accuracy
and macro one-vs-rest AUC; null = labels permuted within site (200x). Also unicorn vs other (AUC).
Held-out: fit on M77 dev, score on M77 heldout. Replication: ICIT square seals, CV + train MD/Harappa ->
test on other sites. Plus: text length by animal; same-emblem sign sharing (Jaccard) vs within-site null.
"""
import warnings
from common import *
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import balanced_accuracy_score, roc_auc_score
from sklearn.preprocessing import label_binarize

warnings.filterwarnings("ignore")
rng = np.random.default_rng(1)
NPERM = 200


def build(records, animal_fn, sym_key, short, tall, jar):
    by = defaultdict(list)
    for r in records:
        a = animal_fn(r[sym_key])
        if a is None:
            continue
        by[" ".join(r["seq"])].append((a, r["site"], r))
    items, conflict = [], 0
    for k, v in by.items():
        labs = {a for a, _, _ in v}
        if len(labs) > 1:
            conflict += 1
            continue
        items.append((k.split(), v[0][0], v[0][1]))
    return items, conflict


def featurize(items, vocab=None, bigr=None, short=None, tall=None, jar=None):
    seqs = [s for s, _, _ in items]
    if vocab is None:
        c = Counter(x for s in seqs for x in set(signs(s)))
        vocab = [x for x, n in c.items() if n >= 5]
        cb = Counter(b for s in seqs for b in ngrams(s, 2))
        bigr = [x for x, n in cb.items() if n >= 5]
    vi = {x: i for i, x in enumerate(vocab)}
    bi = {x: i for i, x in enumerate(bigr)}
    nb = len(vocab)
    X = np.zeros((len(seqs), 2 * nb + len(bigr) + 8))
    groups = {"length": [], "classes": [], "signs": [], "bigrams": []}
    for r, s in enumerate(seqs):
        ss = signs(s)
        for x in set(ss):
            if x in vi: X[r, vi[x]] = 1
        if ss and ss[0] in vi: X[r, nb + vi[ss[0]]] = 1  # initial sign
        for b in ngrams(s, 2):
            if b in bi: X[r, 2 * nb + bi[b]] = 1
        o = 2 * nb + len(bigr)
        L = len(ss)
        X[r, o] = L / 5; X[r, o + 1] = (L <= 2); X[r, o + 2] = (L >= 6)
        X[r, o + 3] = any(x in short for x in ss); X[r, o + 4] = any(x in tall for x in ss)
        X[r, o + 5] = bool(ss) and ss[-1] == jar; X[r, o + 6] = s.count("|") > 0
        X[r, o + 7] = sum(x in short or x in tall for x in ss) / 2
    cols = {"signs": list(range(0, 2 * nb)), "bigrams": list(range(2 * nb, 2 * nb + len(bigr))),
            "length+classes": list(range(2 * nb + len(bigr), X.shape[1]))}
    return X, vocab, bigr, cols


def cv_score(X, y, k=5, seed=0):
    classes = np.unique(y)
    skf = StratifiedKFold(k, shuffle=True, random_state=seed)
    P = np.zeros((len(y), len(classes)))
    for tr, te in skf.split(X, y):
        m = LogisticRegression(C=0.3, max_iter=2000, class_weight="balanced")
        m.fit(X[tr], y[tr])
        pr = m.predict_proba(X[te])
        idx = [list(classes).index(c) for c in m.classes_]
        P[np.ix_(te, idx)] = pr
    pred = classes[P.argmax(1)]
    bal = balanced_accuracy_score(y, pred)
    Yb = label_binarize(y, classes=classes)
    auc = np.mean([roc_auc_score(Yb[:, j], P[:, j]) for j in range(len(classes)) if 0 < Yb[:, j].sum() < len(y)])
    return bal, auc, P, classes


def perm_test(X, y, strata, label=""):
    bal, auc, P, classes = cv_score(X, y)
    nb, na = [], []
    for i in range(NPERM):
        yp = strat_perm(y, strata, rng)
        b, a, _, _ = cv_score(X, yp, seed=i + 1)
        nb.append(b); na.append(a)
    nb, na = np.array(nb), np.array(na)
    res = dict(bal_acc=bal, bal_null_mean=nb.mean(), bal_null_95=np.quantile(nb, .95), p_bal=(1 + (nb >= bal).sum()) / (NPERM + 1),
               auc=auc, auc_null_mean=na.mean(), auc_null_95=np.quantile(na, .95), p_auc=(1 + (na >= auc).sum()) / (NPERM + 1))
    print(f"  {label:35s} balAcc {bal:.3f} (null {nb.mean():.3f}, 95% {res['bal_null_95']:.3f}, p={res['p_bal']:.3f})  "
          f"macroAUC {auc:.3f} (null {na.mean():.3f}, p={res['p_auc']:.3f})")
    return res, P, classes


def binary_unicorn(X, y, strata, label=""):
    yb = (y == "unicorn").astype(int)
    def sc(yy, seed):
        skf = StratifiedKFold(5, shuffle=True, random_state=seed)
        p = np.zeros(len(yy))
        for tr, te in skf.split(X, yy):
            m = LogisticRegression(C=0.3, max_iter=2000, class_weight="balanced").fit(X[tr], yy[tr])
            p[te] = m.predict_proba(X[te])[:, 1]
        return roc_auc_score(yy, p)
    a = sc(yb, 0)
    null = np.array([sc(strat_perm(yb, strata, rng), i + 1) for i in range(NPERM)])
    p = (1 + (null >= a).sum()) / (NPERM + 1)
    print(f"  {label:35s} unicorn-vs-other AUC {a:.3f} (null {null.mean():.3f}, 95% {np.quantile(null,.95):.3f}, p={p:.3f})")
    return dict(auc=a, null_mean=null.mean(), null95=np.quantile(null, .95), p=p)


def length_by_animal(items, label):
    L = np.array([len(signs(s)) for s, _, _ in items]); y = np.array([a for _, a, _ in items])
    st = np.array([site for _, _, site in items])
    out = {}
    print(f"  length by animal ({label}); null = labels permuted within site, two-sided, 2000x")
    for a in sorted(set(y), key=lambda a: -(y == a).sum()):
        n = (y == a).sum()
        obs = L[y == a].mean() - L[y != a].mean()
        null = []
        for _ in range(2000):
            yp = strat_perm(y, st, rng)
            null.append(L[yp == a].mean() - L[yp != a].mean())
        null = np.array(null)
        p = (1 + (np.abs(null) >= abs(obs)).sum()) / 2001
        out[a] = dict(n=int(n), mean_len=float(L[y == a].mean()), diff=float(obs), p=float(p))
    q = bh([v["p"] for v in out.values()])
    for (a, v), qq in zip(out.items(), q):
        v["q"] = float(qq)
        print(f"    {a:15s} n={v['n']:4d} mean len {v['mean_len']:.2f} diff vs rest {v['diff']:+.2f} p={v['p']:.4f} BH q={qq:.3f}")
    return out


def emblem_sharing(items, label, min_n=8):
    """Mean Jaccard of sign sets within each animal class vs labels permuted within site."""
    sets = [set(signs(s)) for s, _, _ in items]
    y = np.array([a for _, a, _ in items]); st = np.array([site for _, _, site in items])
    n = len(sets)
    J = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            u = len(sets[i] | sets[j])
            J[i, j] = J[j, i] = len(sets[i] & sets[j]) / u if u else 0
    def within(yy, a):
        idx = np.where(yy == a)[0]
        if len(idx) < 2: return np.nan
        sub = J[np.ix_(idx, idx)]
        return sub[np.triu_indices(len(idx), 1)].mean()
    out = {}
    print(f"  same-emblem sign sharing ({label}): mean pairwise Jaccard within class vs within-site label permutation (1000x)")
    classes = [a for a in set(y) if (y == a).sum() >= min_n]
    nulls = {a: [] for a in classes}
    for _ in range(1000):
        yp = strat_perm(y, st, rng)
        for a in classes: nulls[a].append(within(yp, a))
    for a in sorted(classes, key=lambda a: -(y == a).sum()):
        obs = within(y, a); nu = np.array(nulls[a])
        p = (1 + (nu >= obs).sum()) / 1001
        out[a] = dict(n=int((y == a).sum()), jaccard=float(obs), null=float(nu.mean()), p=float(p))
    q = bh([v["p"] for v in out.values()])
    for (a, v), qq in zip(out.items(), q):
        v["q"] = float(qq)
        print(f"    {a:15s} n={v['n']:4d} J={v['jaccard']:.4f} null {v['null']:.4f} ratio {v['jaccard']/v['null']:.2f} p={v['p']:.4f} q={qq:.3f}")
    return out


def main():
    R = {}
    # ---------------- M77 ----------------
    seals = [t for t in m77_texts() if t["object_type"] == "seal"]
    items, conf = build(seals, m77_animal, "fs80", M_SHORT, M_TALL, JAR_M)
    c = Counter(a for _, a, _ in items)
    keep = {a for a, n in c.items() if n >= 10}
    items = [it for it in items if it[1] in keep]
    print(f"M77 seals: {len(items)} distinct texts with animal (dropped {conf} texts seen under >1 animal); classes {Counter(a for _,a,_ in items)}")
    X, vocab, bigr, cols = featurize(items, short=M_SHORT, tall=M_TALL, jar=JAR_M)
    y = np.array([a for _, a, _ in items]); st = np.array([s for _, _, s in items])
    R["m77_classes"] = dict(Counter(y))
    R["m77_all"], P, classes = perm_test(X, y, st, "M77 all features")
    for g, ci in cols.items():
        R[f"m77_{g}"], _, _ = perm_test(X[:, ci], y, st, f"M77 {g} only")
    R["m77_unicorn_bin"] = binary_unicorn(X, y, st, "M77 all features")
    # confusion summary per class
    pred = classes[P.argmax(1)]
    R["m77_per_class_recall"] = {a: float((pred[y == a] == a).mean()) for a in classes}
    print("  per-class CV recall:", {a: round(v, 2) for a, v in R["m77_per_class_recall"].items()})
    # held-out: fit dev, test heldout
    dev, ho = dev_heldout()
    dk = {" ".join(t["seq"]) for t in dev}
    tr = [it for it in items if " ".join(it[0]) in dk]; te = [it for it in items if " ".join(it[0]) not in dk]
    Xtr, v2, b2, _ = featurize(tr, short=M_SHORT, tall=M_TALL, jar=JAR_M)
    Xte, _, _, _ = featurize(te, v2, b2, short=M_SHORT, tall=M_TALL, jar=JAR_M)
    ytr = np.array([a for _, a, _ in tr]); yte = np.array([a for _, a, _ in te])
    m = LogisticRegression(C=0.3, max_iter=2000, class_weight="balanced").fit(Xtr, ytr)
    pr = m.predict_proba(Xte)
    ba = balanced_accuracy_score(yte, m.classes_[pr.argmax(1)])
    ui = list(m.classes_).index("unicorn")
    auc_u = roc_auc_score((yte == "unicorn").astype(int), pr[:, ui])
    nb = [balanced_accuracy_score(rng.permutation(yte), m.classes_[pr.argmax(1)]) for _ in range(2000)]
    nu = [roc_auc_score(rng.permutation((yte == "unicorn").astype(int)), pr[:, ui]) for _ in range(2000)]
    R["m77_heldout"] = dict(n_train=len(tr), n_test=len(te), bal_acc=ba, null_mean=float(np.mean(nb)), p=(1 + sum(x >= ba for x in nb)) / 2001,
                            unicorn_auc=auc_u, unicorn_auc_p=(1 + sum(x >= auc_u for x in nu)) / 2001)
    print(f"  HELD-OUT (fit dev n={len(tr)}, test n={len(te)}): balAcc {ba:.3f} (null {np.mean(nb):.3f}, p={R['m77_heldout']['p']:.3f}); unicorn AUC {auc_u:.3f} p={R['m77_heldout']['unicorn_auc_p']:.3f}")
    # top coefficients for non-unicorn classes (descriptive)
    mfull = LogisticRegression(C=0.3, max_iter=2000, class_weight="balanced").fit(X, y)
    names = [f"has:{v}" for v in vocab] + [f"init:{v}" for v in vocab] + [f"bi:{b}" for b in bigr] + \
            ["len/5", "len<=2", "len>=6", "short", "tall", "jarfinal", "multiline", "nnum"]
    R["m77_top_features"] = {}
    for k, a in enumerate(mfull.classes_):
        top = np.argsort(-mfull.coef_[k])[:6]
        R["m77_top_features"][a] = [(names[i], round(float(mfull.coef_[k][i]), 2)) for i in top]
    R["m77_length"] = length_by_animal(items, "M77 seals")
    R["m77_sharing"] = emblem_sharing(items, "M77 seals")

    # ---------------- ICIT ----------------
    I = [t for t in icit_texts() if t["type"] in ("SEAL:S", "SEAL")]
    items_i, conf_i = build(I, icit_animal, "symbol", W_SHORT, W_TALL, JAR_W)
    c = Counter(a for _, a, _ in items_i)
    keep = {a for a, n in c.items() if n >= 10}
    items_i = [it for it in items_i if it[1] in keep]
    print(f"\nICIT square seals: {len(items_i)} distinct texts (dropped {conf_i} conflicting); classes {Counter(a for _,a,_ in items_i)}")
    Xi, vi_, bi_, cols_i = featurize(items_i, short=W_SHORT, tall=W_TALL, jar=JAR_W)
    yi = np.array([a for _, a, _ in items_i]); sti = np.array([s for _, _, s in items_i])
    R["icit_classes"] = dict(Counter(yi))
    R["icit_all"], _, _ = perm_test(Xi, yi, sti, "ICIT all features")
    R["icit_length+classes"], _, _ = perm_test(Xi[:, cols_i["length+classes"]], yi, sti, "ICIT length+classes only")
    R["icit_unicorn_bin"] = binary_unicorn(Xi, yi, sti, "ICIT all features")
    # cross-site: train MD + Harappa, test elsewhere (unicorn vs other)
    home = np.isin(sti, ["Mohenjo-daro", "Harappa"])
    tr = [it for it, h in zip(items_i, home) if h]; te = [it for it, h in zip(items_i, home) if not h]
    Xtr, v2, b2, _ = featurize(tr, short=W_SHORT, tall=W_TALL, jar=JAR_W)
    Xte, _, _, _ = featurize(te, v2, b2, short=W_SHORT, tall=W_TALL, jar=JAR_W)
    ytr = np.array([a == "unicorn" for _, a, _ in tr]).astype(int); yte = np.array([a == "unicorn" for _, a, _ in te]).astype(int)
    m = LogisticRegression(C=0.3, max_iter=2000, class_weight="balanced").fit(Xtr, ytr)
    pte = m.predict_proba(Xte)[:, 1]
    a = roc_auc_score(yte, pte)
    nu = [roc_auc_score(rng.permutation(yte), pte) for _ in range(2000)]
    R["icit_crosssite_unicorn"] = dict(n_train=len(tr), n_test=len(te), test_sites=dict(Counter(s for _, _, s in te)),
                                       auc=a, null_mean=float(np.mean(nu)), p=(1 + sum(x >= a for x in nu)) / 2001)
    print(f"  CROSS-SITE (train MD+Harappa n={len(tr)} -> other sites n={len(te)}): unicorn AUC {a:.3f} (null {np.mean(nu):.3f}, p={R['icit_crosssite_unicorn']['p']:.4f})")
    R["icit_length"] = length_by_animal(items_i, "ICIT square seals")
    R["icit_sharing"] = emblem_sharing(items_i, "ICIT square seals")
    save_json("q1_animal", R)


if __name__ == "__main__":
    main()
