"""Step 1: identifiability. Can the statistics tell the fitted naming generators apart at Indus size?

For each real system S: structural parameters fitted to S (fits/S.json) + the Indus element frequency profile
(V, zipf from fits/indus_dev.json). R corpora of n distinct types are simulated per system (n = 800 = Indus dev
types; n = 423 = Indus held-out types) and the 9 statistics computed. No Indus name statistic is used here.
Classifiers on the simulated reference table:
  * LDA (5-fold CV) on the PRIMARY 6 statistics, and on 7 incl. cls_self for systems with a class
  * ABC k-NN (k = 50, standardised statistics, leave-one-out): MAP system
Outputs sims_n{n}.npz (reference table, reused by score.py) and identify.json.
Usage: .venv/bin/python -I experiments/naming_sim/identify.py [R]
"""
import sys, json
from pathlib import Path
from multiprocessing import Pool
import numpy as np
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.model_selection import cross_val_predict, StratifiedKFold
from sklearn.metrics import confusion_matrix

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import gen, stats as S

FITS = HERE / "fits"
PRIMARY = ["len1", "standalone", "both_orders", "hfi", "pol_ex", "both_pos"]
SYSTEMS = ["old_english", "old_norse", "old_high_german", "germanic_pooled", "greek", "sanskrit", "egyptian",
           "ur3", "chinese_given", "chinese_full", "plains", "sangam", "mixtec"]


def theta_at_indus(sys_name):
    th = json.loads((FITS / f"{sys_name}.json").read_text())["theta"]
    ind = json.loads((FITS / "indus_dev.json").read_text())["theta"]
    th = dict(th); th["V"] = ind["V"]; th["zipf"] = ind["zipf"]
    return th


def _job(args):
    name, n, r = args
    th = theta_at_indus(name)
    rng = np.random.default_rng(10_000 * r + n + sum(map(ord, name)))
    ty, c = gen.sample(th, n, rng, V=th["V"])
    st = S.compute(ty, rng, c, 30)
    return name, [st[k] for k in S.KEYS]


def simulate(n, R, systems=SYSTEMS):
    jobs = [(s, n, r) for s in systems for r in range(R)]
    with Pool(2) as p:
        res = p.map(_job, jobs, chunksize=4)
    y = np.array([a for a, _ in res]); X = np.array([b for _, b in res], float)
    np.savez(HERE / f"sims_n{n}.npz", X=X, y=y, keys=np.array(S.KEYS))
    return X, y


def knn_abc(X, y, k=50):
    mu, sd = X.mean(0), X.std(0)
    Z = (X - mu) / sd
    pred = []
    for i in range(len(Z)):
        d = ((Z - Z[i]) ** 2).sum(1); d[i] = np.inf
        nn = y[np.argsort(d)[:k]]
        v, c = np.unique(nn, return_counts=True)
        pred.append(v[np.argmax(c)])
    return np.array(pred)


def evaluate(X, y, keys):
    ix = [S.KEYS.index(k) for k in keys]
    Xp = X[:, ix]
    ok = ~np.isnan(Xp).any(1)
    Xp, yp = Xp[ok], y[ok]
    labs = sorted(set(yp))
    lda = cross_val_predict(LinearDiscriminantAnalysis(), Xp, yp, cv=StratifiedKFold(5, shuffle=True, random_state=0))
    abc = knn_abc(Xp, yp)
    cm = confusion_matrix(yp, lda, labels=labs)
    per = {l: float(cm[i, i] / cm[i].sum()) for i, l in enumerate(labs)}
    # pairwise LDA accuracy for key comparisons
    pairs = {}
    for a, b in [("germanic_pooled", "sanskrit"), ("old_english", "sanskrit"), ("germanic_pooled", "chinese_given"),
                 ("sanskrit", "chinese_given"), ("germanic_pooled", "greek"), ("sanskrit", "sangam"),
                 ("germanic_pooled", "old_english"), ("chinese_given", "chinese_full"), ("ur3", "sanskrit")]:
        if a in labs and b in labs:
            m = np.isin(yp, [a, b])
            pr = cross_val_predict(LinearDiscriminantAnalysis(), Xp[m], yp[m], cv=StratifiedKFold(5, shuffle=True, random_state=0))
            pairs[f"{a}|{b}"] = float(np.mean(pr == yp[m]))
    return dict(keys=keys, labels=labs, n=int(len(yp)), lda_acc=float(np.mean(lda == yp)), abc_acc=float(np.mean(abc == yp)),
                per_system_lda=per, confusion=cm.tolist(), pairwise_lda=pairs)


if __name__ == "__main__":
    R = int(sys.argv[1]) if len(sys.argv) > 1 else 150
    out = {}
    for n in (800, 423):
        X, y = simulate(n, R)
        means = {s: {k: round(float(np.nanmean(X[y == s, j])), 3) for j, k in enumerate(S.KEYS)} for s in SYSTEMS}
        sds = {s: {k: round(float(np.nanstd(X[y == s, j])), 4) for j, k in enumerate(S.KEYS)} for s in SYSTEMS}
        e1 = evaluate(X, y, PRIMARY)
        cls_sys = [s for s in SYSTEMS if not np.isnan(X[y == s, S.KEYS.index("cls_self")]).all()]
        m = np.isin(y, cls_sys)
        e2 = evaluate(X[m], y[m], PRIMARY + ["cls_self"])
        out[f"n{n}"] = dict(sim_means=means, sim_sds=sds, primary=e1, with_class=e2)
        print(f"n={n}: LDA acc (6 stats) {e1['lda_acc']:.3f}, ABC kNN {e1['abc_acc']:.3f}; with cls_self ({len(cls_sys)} systems) "
              f"LDA {e2['lda_acc']:.3f}", flush=True)
        print("  per system:", {k: round(v, 2) for k, v in e1["per_system_lda"].items()})
        print("  pairwise:", {k: round(v, 3) for k, v in e1["pairwise_lda"].items()}, flush=True)
    json.dump(out, open(HERE / "identify.json", "w"), indent=1)
