"""B3d. Leave-one-specification-out power + Indus posterior across all simulator specifications.
Specs: A base (b3_features.json), B alternative grammar/genre choices (--alt), C genre opener
word for every language (--opener), D scribes omit grammatical affixes (--underspell).
Power that survives training on three specs and testing on the fourth is the honest power.
Run: .venv/bin/python experiments/language/b3_robust.py
"""
import json
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
SPECS = {"A": "b3_features.json", "B": "b3_features_alt.json", "C": "b3_features_open.json", "D": "b3_features_under.json",
         "E": "b3_features_sym.json"}
DATA = {k: json.load(open(HERE / "out" / v)) for k, v in SPECS.items()}
DROP = {"V", "logV", "ttr", "hapax", "heaps_ratio", "len_mean", "len_sd", "cls", "rep"}
F = [k for k in DATA["A"]["sims"][0] if k not in DROP]
IND = DATA["A"]["indus"]


def XY(spec):
    s = DATA[spec]["sims"]
    return np.array([[r[f] for f in F] for r in s]), np.array([r["cls"] for r in s])


MODELS = {"RF": lambda: RandomForestClassifier(500, min_samples_leaf=2, random_state=0, n_jobs=2),
          "LR": lambda: make_pipeline(StandardScaler(), LogisticRegression(C=0.5, max_iter=5000))}


def main():
    res = {"features": F, "specs": SPECS}
    XYs = {k: XY(k) for k in SPECS}
    labels = sorted(set(XYs["A"][1]))
    xi = {k: np.array([[IND[k][f] for f in F]]) for k in IND}
    loso = {}
    for mn, mk in MODELS.items():
        accs, cm = {}, np.zeros((len(labels), len(labels)))
        for held in SPECS:
            Xtr = np.vstack([XYs[k][0] for k in SPECS if k != held]); ytr = np.concatenate([XYs[k][1] for k in SPECS if k != held])
            m = mk().fit(Xtr, ytr)
            p = m.predict(XYs[held][0])
            accs[held] = round(float(np.mean(p == XYs[held][1])), 3)
            cm += confusion_matrix(XYs[held][1], p, labels=labels)
            for k in xi:
                pr = dict(zip(m.classes_, m.predict_proba(xi[k])[0]))
                loso.setdefault(f"{mn}/{k}", []).append({c: round(float(pr[c]), 3) for c in labels})
        res[f"{mn}_leave_one_spec_out_acc"] = accs
        res[f"{mn}_loso_mean_acc"] = round(float(np.mean(list(accs.values()))), 3)
        res[f"{mn}_loso_confusion"] = dict(labels=labels, matrix=cm.astype(int).tolist())
        X = np.vstack([XYs[k][0] for k in SPECS]); y = np.concatenate([XYs[k][1] for k in SPECS])
        p = cross_val_predict(mk(), X, y, cv=StratifiedKFold(5, shuffle=True, random_state=0))
        res[f"{mn}_pooled_cv_acc"] = round(float(np.mean(p == y)), 3)
        print(mn, "LOSO", accs, "pooled CV", res[f"{mn}_pooled_cv_acc"])
        # pooled-model posterior
        m = mk().fit(X, y)
        for k in xi:
            res.setdefault("indus_posterior_pooled", {})[f"{mn}/{k}"] = {c: round(float(v), 3) for c, v in zip(m.classes_, m.predict_proba(xi[k])[0])}
    res["indus_posterior_loso_models"] = loso
    res["indus_argmax_loso"] = {k: [max(d, key=d.get) for d in v] for k, v in loso.items()}
    # binary DRA vs IA, LOSO
    for a, b in [("DRA", "IA"), ("DRA", "MUN"), ("DRA", "ELA"), ("IA", "MUN")]:
        acc = []
        for held in SPECS:
            Xtr = np.vstack([XYs[k][0][np.isin(XYs[k][1], [a, b])] for k in SPECS if k != held])
            ytr = np.concatenate([XYs[k][1][np.isin(XYs[k][1], [a, b])] for k in SPECS if k != held])
            mh = np.isin(XYs[held][1], [a, b])
            m = MODELS["RF"]().fit(Xtr, ytr)
            acc.append(float(np.mean(m.predict(XYs[held][0][mh]) == XYs[held][1][mh])))
        res[f"binary_{a}_vs_{b}_loso"] = [round(x, 3) for x in acc]
    # which features separate IA from DRA, and where Indus sits (z vs pooled class means)
    X = np.vstack([XYs[k][0] for k in SPECS]); y = np.concatenate([XYs[k][1] for k in SPECS])
    mu = X.mean(0); sd = X.std(0) + 1e-9
    res["indus_z_vs_class_means"] = {f: dict(indus=round(float((IND["M77_all"][f] - mu[i]) / sd[i]), 2),
                                             **{c: round(float((X[y == c, i].mean() - mu[i]) / sd[i]), 2) for c in labels})
                                     for i, f in enumerate(F)}
        # spec E alone (equalised endings): does the Indus label survive?
    for mn, mk in MODELS.items():
        m = mk().fit(*XYs["E"])
        for k in xi:
            res.setdefault("indus_posterior_E_only", {})[f"{mn}/{k}"] = {c: round(float(v), 3) for c, v in zip(m.classes_, m.predict_proba(xi[k])[0])}
    json.dump(res, open(HERE / "out" / "b3_robust.json", "w"), indent=1)
    print("E only:", json.dumps(res["indus_posterior_E_only"]))
    print(json.dumps(res["indus_posterior_pooled"], indent=0))
    print(res["indus_argmax_loso"])
    print({k: v for k, v in res.items() if k.startswith("binary")})


if __name__ == "__main__":
    main()
