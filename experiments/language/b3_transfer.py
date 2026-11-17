"""B3c. Robustness of the typological classifier to MIS-SPECIFICATION of the simulator.
Spec A (b3_features.json) and spec B (b3_features_alt.json) differ only in choices we cannot know
for a 3rd-millennium seal genre (title before/after name, which case endings, how often prefixes,
whether patronymics use vowel change, agreement marking, slot counts). Train on A, test on B (and
reverse). If accuracy collapses, the within-simulator power of b3_classify.py is a property of our
simulator, not of the languages, and an Indus posterior would mean little.
Run: .venv/bin/python experiments/language/b3_transfer.py
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
A = json.load(open(HERE / "out" / "b3_features.json"))
import sys
B = json.load(open(HERE / "out" / ("b3_features_open.json" if "--opener" in sys.argv else "b3_features_alt.json")))
DROP = {"V", "logV", "ttr", "hapax", "heaps_ratio", "len_mean", "len_sd", "cls", "rep"}
F = [k for k in A["sims"][0] if k not in DROP]


def XY(D):
    return np.array([[r[f] for f in F] for r in D["sims"]]), np.array([r["cls"] for r in D["sims"]])


def models():
    return {"RF": lambda: RandomForestClassifier(400, min_samples_leaf=2, random_state=0, n_jobs=2),
            "LR": lambda: make_pipeline(StandardScaler(), LogisticRegression(C=0.5, max_iter=5000))}


def main():
    XA, yA = XY(A); XB, yB = XY(B)
    labels = sorted(set(yA))
    res = {"features": F, "n_A": len(yA), "n_B": len(yB)}
    for mn, mk in models().items():
        m = mk().fit(XA, yA); pAB = m.predict(XB)
        m2 = mk().fit(XB, yB); pBA = m2.predict(XA)
        res[f"{mn}_train_A_test_B"] = round(float(np.mean(pAB == yB)), 3)
        res[f"{mn}_train_B_test_A"] = round(float(np.mean(pBA == yA)), 3)
        res[f"{mn}_A_to_B_confusion"] = dict(labels=labels, matrix=confusion_matrix(yB, pAB, labels=labels).tolist())
        # pooled CV
        X = np.vstack([XA, XB]); y = np.concatenate([yA, yB])
        p = cross_val_predict(mk(), X, y, cv=StratifiedKFold(5, shuffle=True, random_state=0))
        res[f"{mn}_pooled_cv"] = round(float(np.mean(p == y)), 3)
        print(mn, "A->B", res[f"{mn}_train_A_test_B"], "B->A", res[f"{mn}_train_B_test_A"], "pooled CV", res[f"{mn}_pooled_cv"])
    # binary: Dravidian vs Indo-Aryan across specs
    for a, b in [("DRA", "IA"), ("DRA", "MUN"), ("DRA", "ELA")]:
        mA = np.isin(yA, [a, b]); mB = np.isin(yB, [a, b])
        m = models()["RF"]().fit(XA[mA], yA[mA])
        res[f"binary_{a}_vs_{b}_A_to_B"] = round(float(np.mean(m.predict(XB[mB]) == yB[mB])), 3)
        m = models()["RF"]().fit(XB[mB], yB[mB])
        res[f"binary_{a}_vs_{b}_B_to_A"] = round(float(np.mean(m.predict(XA[mA]) == yA[mA])), 3)
    mA = np.where(yA == "NONLING", "N", "L"); mB = np.where(yB == "NONLING", "N", "L")
    m = models()["RF"]().fit(XA, mA)
    res["binary_nonling_A_to_B"] = round(float(np.mean(m.predict(XB) == mB)), 3)
    res["binary_nonling_A_to_B_recall_nonling"] = round(float(np.mean(m.predict(XB)[mB == "N"] == "N")), 3)
    # Indus under each spec and pooled
    xi = np.array([[A["indus"]["M77_all"][f] for f in F]])
    xi2 = np.array([[A["indus"]["ICIT_all"][f] for f in F]])
    post = {}
    for name, (X, y) in {"A": (XA, yA), "B": (XB, yB), "A+B": (np.vstack([XA, XB]), np.concatenate([yA, yB]))}.items():
        for mn, mk in models().items():
            m = mk().fit(X, y)
            post[f"{name}/{mn}/M77"] = {c: round(float(p), 3) for c, p in zip(m.classes_, m.predict_proba(xi)[0])}
            post[f"{name}/{mn}/ICIT"] = {c: round(float(p), 3) for c, p in zip(m.classes_, m.predict_proba(xi2)[0])}
    res["indus_posteriors"] = post
    res["indus_argmax"] = {k: max(v, key=v.get) for k, v in post.items()}
    print(json.dumps(res["indus_argmax"], indent=0))
    print({k: v for k, v in res.items() if k.startswith("binary")})
    json.dump(res, open(HERE / "out" / ("b3_transfer_open.json" if "--opener" in sys.argv else "b3_transfer.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
