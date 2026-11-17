"""T3: do FRAME signs (titles, closers) co-vary with the animal emblem?

Unit: distinct texts on square seals (SEAL:S) with a known emblem (no area needed).
Emblem classes: unicorn, gaur, zebu, elephant, rhino, tiger, buffalo, goat, shorthorn,
none, other (classes with < 5 texts merged into other).
Null: emblem labels permuted within site x length strata (keeps site emblem mix and
the length-emblem link: zebu/elephant seals are bigger and longer).
Tests
  glob  sum over frame features of the chi-square (feature x emblem class)
  uni   unicorn vs any other animal, per feature (two-sided)
  cell  per (feature, emblem) cell with expected >= 3: obs vs permutation expectation
  clf   held-out only: logistic model (frame features + length) fit on dev predicts
        unicorn vs other on held-out; AUC vs label-permutation null
Usage: t3_emblem.py dev|heldout
"""
import json, math, sys
from collections import Counter, defaultdict
import numpy as np
sys.path.insert(0, __import__("os").path.dirname(__file__))
from common import seal_table, strata, FRAME, HERE
from t2_status import perm_within

N_PERM = 4000
MINC = 8


def load(split):
    rows = [r for r in seal_table(split) if r["emblem"] not in ("unknown",)]
    return rows


def classes(rows, keep=None):
    c = Counter(r["emblem"] for r in rows)
    if keep is None:
        keep = {e for e, n in c.items() if n >= 5}
    return [r["emblem"] if r["emblem"] in keep else "other" for r in rows], keep


def chi(X, lab, cats):
    tot = 0.0
    n = len(lab)
    for j in range(X.shape[1]):
        x = X[:, j]; p = x.mean()
        for c in cats:
            m = lab == c; nc = m.sum()
            if nc == 0:
                continue
            o = x[m].sum(); e = nc * p
            if e > 0:
                tot += (o - e) ** 2 / e + ((nc - o) - (nc - e)) ** 2 / max(nc - e, 1e-9)
    return tot


def analyse(split, keep=None):
    rows = load(split)
    lab, keep = classes(rows, keep)
    lab = np.array(lab); cats = sorted(set(lab))
    st = strata(rows)
    F = [f for f in FRAME if sum(f in r["feats"] for r in rows) >= MINC]
    X = np.array([[f in r["feats"] for f in F] for r in rows], float)
    rng = np.random.default_rng(3)
    perms = [perm_within(st, rng) for _ in range(N_PERM)]
    out = dict(split=split, n_texts=len(rows), emblems=dict(Counter(lab)), features=F)
    obs = chi(X, lab, cats)
    nl = np.array([chi(X, lab[p], cats) for p in perms[:2000]])
    out["global"] = dict(stat=float(obs), null_mean=float(nl.mean()), p=float((1 + (nl >= obs).sum()) / 2001))
    # unicorn vs other animal (exclude none/other)
    an = np.isin(lab, [c for c in cats if c not in ("none", "other")])
    uni = {}
    for j, f in enumerate(F):
        x = X[:, j]
        u = (lab == "unicorn")
        o = x[an & ~u].sum()
        nl_ = np.array([x[an][(lab[p][an] != "unicorn")].sum() if True else 0 for p in perms[:2000]])
        e = nl_.mean()
        uni[f] = dict(obs_nonunicorn=int(o), exp=float(e), n_nonunicorn=int((an & ~u).sum()),
                      p=float((1 + (np.abs(nl_ - e) >= abs(o - e)).sum()) / 2001))
    out["unicorn_vs_other"] = uni
    # cells
    cells = {}
    for j, f in enumerate(F):
        x = X[:, j]
        for c in cats:
            if c == "unicorn":
                continue
            m = lab == c
            o = x[m].sum()
            nl_ = np.array([x[lab[p] == c].sum() for p in perms])
            e = nl_.mean()
            if e < 3 and o < 3:
                continue
            cells[f"{f}|{c}"] = dict(obs=int(o), exp=float(e), n_class=int(m.sum()),
                                     p=float((1 + (np.abs(nl_ - e) >= abs(o - e)).sum()) / (1 + N_PERM)))
    out["cells"] = cells
    out["n_cells"] = len(cells)
    return out, keep


def classifier():
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import roc_auc_score
    d = [r for r in load("dev") if r["emblem"] not in ("none", "other")]
    h = [r for r in load("heldout") if r["emblem"] not in ("none", "other")]
    F = list(FRAME)
    def XY(rows):
        X = np.array([[f in r["feats"] for f in F] + [min(r["length"], 10) / 10] for r in rows], float)
        y = np.array([r["emblem"] != "unicorn" for r in rows], int)
        return X, y
    Xd, yd = XY(d); Xh, yh = XY(h)
    m = LogisticRegression(C=0.5, class_weight="balanced", max_iter=2000).fit(Xd, yd)
    auc = roc_auc_score(yh, m.predict_proba(Xh)[:, 1])
    # length-only baseline
    m0 = LogisticRegression(class_weight="balanced").fit(Xd[:, -1:], yd)
    auc0 = roc_auc_score(yh, m0.predict_proba(Xh[:, -1:])[:, 1])
    rng = np.random.default_rng(9)
    nl = []
    for _ in range(1000):
        yp = rng.permutation(yd)
        mp = LogisticRegression(C=0.5, class_weight="balanced", max_iter=2000).fit(Xd, yp)
        nl.append(roc_auc_score(yh, mp.predict_proba(Xh)[:, 1]))
    nl = np.array(nl)
    return dict(n_dev=len(d), n_heldout=len(h), heldout_nonunicorn=int(yh.sum()), auc=float(auc),
                auc_length_only=float(auc0), null_mean=float(nl.mean()), null_p95=float(np.quantile(nl, 0.95)),
                p=float((1 + (nl >= auc).sum()) / 1001))


if __name__ == "__main__":
    split = sys.argv[1]
    if split == "dev":
        o, keep = analyse("dev")
        o["keep"] = sorted(keep)
    else:
        keep = set(json.load(open(HERE / "t3_dev.json"))["keep"])
        o, _ = analyse("heldout", keep)
        o["classifier"] = classifier()
    json.dump(o, open(HERE / f"t3_{split}.json", "w"), indent=1)
    print(split, o["n_texts"], o["emblems"])
    print("global", o["global"])
    if "classifier" in o:
        print("classifier", o["classifier"])
    print("unicorn vs other (top):")
    for f, v in sorted(o["unicorn_vs_other"].items(), key=lambda kv: kv[1]["p"])[:8]:
        print(" ", f, v)
    print("cells (top of", o["n_cells"], "):")
    for f, v in sorted(o["cells"].items(), key=lambda kv: kv[1]["p"])[:12]:
        print(" ", f, v)
