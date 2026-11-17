"""B3b. Power of typological fingerprinting, then (only if power is real) apply to Indus.
Reads out/b3_features.json from b3_sim.py.
Run: .venv/bin/python experiments/language/b3_classify.py
"""
import json
import random
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parents[1]))

D = json.load(open(HERE / "out" / "b3_features.json"))
sims = D["sims"]
FEATS = [k for k in sims[0] if k not in ("cls", "rep")]
DROP_SCRIPT = {"V", "logV", "ttr", "hapax", "heaps_ratio", "len_mean", "len_sd"}  # script/genre-driven
TYPO = [f for f in FEATS if f not in DROP_SCRIPT]
X_all = np.array([[r[f] for f in FEATS] for r in sims])
y = np.array([r["cls"] for r in sims])
classes = sorted(set(y))


def cv_acc(X, y, model, reps=5):
    accs, cms = [], np.zeros((len(set(y)),) * 2)
    labels = sorted(set(y))
    for s in range(reps):
        skf = StratifiedKFold(5, shuffle=True, random_state=s)
        p = cross_val_predict(model, X, y, cv=skf)
        accs.append(float(np.mean(p == y)))
        cms += confusion_matrix(y, p, labels=labels)
    return float(np.mean(accs)), float(np.std(accs)), cms / reps, labels


def rf():
    return RandomForestClassifier(400, min_samples_leaf=2, random_state=0, n_jobs=2)


def lr():
    return make_pipeline(StandardScaler(), LogisticRegression(C=0.5, max_iter=5000))


def main():
    res = {"n_corpora": len(y), "per_class": dict(Counter(y)), "features_all": FEATS, "features_typological": TYPO}
    idx = {f: i for i, f in enumerate(FEATS)}
    Xt = X_all[:, [idx[f] for f in TYPO]]
    power = {}
    for fname, X in [("all_features", X_all), ("typological_only", Xt)]:
        for mname, mk in [("RF", rf), ("LR", lr)]:
            a, s, cm, labels = cv_acc(X, y, mk())
            power[f"{fname}/{mname}"] = dict(acc=round(a, 3), sd=round(s, 3), chance=round(1 / len(classes), 3),
                                             confusion=dict(labels=labels, matrix=np.round(cm, 1).tolist()))
            print(fname, mname, round(a, 3), "+-", round(s, 3))
    # binary questions that matter
    def binary(maskA, maskB, X, name):
        m = np.isin(y, maskA + maskB)
        yy = np.where(np.isin(y[m], maskA), "A", "B")
        a, s, _, _ = cv_acc(X[m], yy, rf())
        base = max(Counter(yy).values()) / len(yy)
        power[name] = dict(A=maskA, B=maskB, acc=round(a, 3), sd=round(s, 3), majority_baseline=round(base, 3))
        print(name, round(a, 3), "baseline", round(base, 3))
    binary(["DRA"], ["IA"], Xt, "binary_DRA_vs_IA")
    binary(["DRA"], ["MUN"], Xt, "binary_DRA_vs_MUN")
    binary(["DRA"], ["ELA"], Xt, "binary_DRA_vs_ELA")
    binary(["DRA", "IA", "ELA", "SUM"], ["MUN", "BUR"], Xt, "binary_suffixing_vs_prefixing")
    binary(["NONLING"], [c for c in classes if c != "NONLING"], Xt, "binary_nonling_vs_language")
    res["power"] = power

    # leave-one-feature-group-out importance (RF on typological)
    m = rf().fit(Xt, y)
    imp = sorted(zip(TYPO, m.feature_importances_), key=lambda x: -x[1])
    res["rf_importance"] = [[f, round(float(v), 3)] for f, v in imp]

    # ---- Indus: out-of-distribution check first
    ind = D["indus"]
    Xi = {k: np.array([[v[f] for f in TYPO]]) for k, v in ind.items()}
    sc = StandardScaler().fit(Xt)
    Z = sc.transform(Xt)
    ood = {}
    for k, xi in Xi.items():
        zi = sc.transform(xi)[0]
        d_ind = np.sort(np.linalg.norm(Z - zi, axis=1))[:5].mean()
        d_sims = [np.sort(np.linalg.norm(np.delete(Z, i, 0) - Z[i], axis=1))[:5].mean() for i in range(len(Z))]
        ood[k] = dict(knn5_dist=round(float(d_ind), 2), sim_knn5_p95=round(float(np.percentile(d_sims, 95)), 2),
                      sim_knn5_max=round(float(np.max(d_sims)), 2),
                      percentile_vs_sims=round(float(np.mean(np.array(d_sims) < d_ind)), 3),
                      extreme_features=[[f, round(float(z), 1)] for f, z in sorted(zip(TYPO, zi), key=lambda x: -abs(x[1]))[:6]])
    res["indus_ood"] = ood
    print("OOD:", json.dumps(ood, indent=0))

    # ---- posterior (reported with the power caveat)
    best_acc = power["typological_only/RF"]["acc"]
    post = {}
    for k, xi in Xi.items():
        probs = []
        for seed in range(20):
            mm = RandomForestClassifier(400, min_samples_leaf=2, random_state=seed, n_jobs=2)
            idxb = np.random.RandomState(seed).choice(len(y), len(y), replace=True)
            mm.fit(Xt[idxb], y[idxb])
            p = dict(zip(mm.classes_, mm.predict_proba(xi)[0]))
            probs.append([p.get(c, 0.0) for c in classes])
        probs = np.array(probs)
        post[k] = {c: [round(float(probs[:, i].mean()), 3), round(float(np.percentile(probs[:, i], 5)), 3),
                       round(float(np.percentile(probs[:, i], 95)), 3)] for i, c in enumerate(classes)}
    res["indus_posterior_RF_bootstrap_mean_p5_p95"] = post
    res["note"] = "Posterior is only meaningful if power >> chance AND Indus is inside the simulated feature space."
    print(json.dumps(post, indent=0))
    # Indus bootstrap over texts (feature uncertainty) for M77_all
    from b3_sim import features, indus_corpora  # noqa
    corp = indus_corpora()["M77_all"]
    mm = rf().fit(Xt, y)
    rng = random.Random(3)
    bs = []
    for _ in range(30):
        samp = [rng.choice(corp) for _ in corp]
        f = features(samp)
        p = mm.predict_proba(np.array([[f[x] for x in TYPO]]))[0]
        bs.append(dict(zip(mm.classes_, p)))
    res["indus_M77_text_bootstrap"] = {c: [round(float(np.mean([b[c] for b in bs])), 3),
                                           round(float(np.percentile([b[c] for b in bs], 5)), 3),
                                           round(float(np.percentile([b[c] for b in bs], 95)), 3)] for c in classes}
    res["indus_M77_text_bootstrap_argmax_counts"] = dict(Counter(max(b, key=b.get) for b in bs))
    print(res["indus_M77_text_bootstrap"], res["indus_M77_text_bootstrap_argmax_counts"])
    # simulated feature ranges vs Indus
    res["feature_ranges"] = {f: dict(indus=round(float(ind["M77_all"][f]), 3),
                                     **{c: [round(float(np.percentile(X_all[y == c, idx[f]], 10)), 3),
                                            round(float(np.percentile(X_all[y == c, idx[f]], 90)), 3)] for c in classes})
                             for f in FEATS}
    json.dump(res, open(HERE / "out" / "b3_classify.json", "w"), indent=1, default=float)


if __name__ == "__main__":
    main()
