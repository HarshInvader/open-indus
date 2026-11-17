"""Claim 3 add-on: does the register classifier's AUC survive family-grouped CV (near-duplicate
variants of one legend never split across train/test)? And fish claim on ICIT sites absent from M77."""
from collections import Counter
import numpy as np
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, StratifiedGroupKFold, cross_val_predict
from sklearn.metrics import roc_auc_score
from rt_common import m77, icit, near_dup_clusters, save
import r3_registers as R3  # reuse own type maps / unit builder (redteam code)


def feats(s):
    d = {x: 1 for x in s}
    d.update({a + "_" + b: 1 for a, b in zip(s, s[1:])})
    d["_first_" + s[0]] = 1; d["_last_" + s[-1]] = 1; d["_len"] = len(s) / 5
    return d


def run(U, label):
    seqs = [u["flat"] for u in U]
    cl = near_dup_clusters(sorted(set(seqs)))
    gid = {s: i for i, c in enumerate(cl) for s in c}
    groups = np.array([gid[s] for s in seqs])
    X = DictVectorizer().fit_transform([feats(s) for s in seqs])
    out = {}
    for ty in ("seal", "tablet", "copper", "rod", "pottery", "sealing"):
        y = np.array([u["type"] == ty for u in U]).astype(int)
        if y.sum() < 15: continue
        clf = LogisticRegression(C=1.0, max_iter=2000)
        p1 = cross_val_predict(clf, X, y, cv=StratifiedKFold(5, shuffle=True, random_state=0), method="predict_proba")[:, 1]
        p2 = cross_val_predict(clf, X, y, cv=StratifiedGroupKFold(5, shuffle=True, random_state=0), groups=groups, method="predict_proba")[:, 1]
        out[ty] = dict(n=int(y.sum()), auc_plain=round(roc_auc_score(y, p1), 3), auc_grouped=round(roc_auc_score(y, p2), 3))
        print(label, ty, out[ty])
    return out


import r3_registers  # noqa
res = {"M77": run(R3.units(m77(), R3.M_TYPE, "object_type"), "M77"),
       "ICIT": run(R3.units(icit(), R3.i_type, "type"), "ICIT")}
save("r3b_register_cv", res)
