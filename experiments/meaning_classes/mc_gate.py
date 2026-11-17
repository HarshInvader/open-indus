"""Held-out-script gate for meaning classes (prereg docs/prereg/meaning_classes.md).
usage: .venv/bin/python -I experiments/meaning_classes/mc_gate.py
"""
import sys, json, random
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np
from scipy.stats import rankdata, spearmanr
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "experiments/numeral_grammar"))
from corpus.load import m77_texts, distinct, dev_heldout, runs  # noqa
from common import M_NUM  # noqa

SCRIPTS = ["cun", "egy", "lat"]
TARGET = ["NAME", "CONTENT", "FUNC"]
N_UNITS, MINF, NPERM, SEEDS = 2300, 3, 200, [0, 1, 2, 3, 4]


def load(name):
    U = []
    for l in open(HERE / "data" / f"{name}.jsonl"):
        r = json.loads(l)
        if 2 <= len(r["seq"]) <= 17 and "<BRK>" not in r["seq"]:
            U.append(list(zip(r["seq"], r["cls"])))
    return U


def features(units, is_num):
    """units: list of list of type; is_num: set of numeral types. returns types, X (rank-percentile per feature)."""
    occ = Counter(t for u in units for t in u)
    ini = Counter(); fin = Counter(); pos = defaultdict(float); L = defaultdict(set); R = defaultdict(set)
    pnum = Counter(); fnum = Counter(); nunits = defaultdict(set); single = Counter(); ulen = defaultdict(float); nn = Counter()
    for k, u in enumerate(units):
        n = len(u)
        for i, t in enumerate(u):
            if i == 0: ini[t] += 1
            if i == n - 1: fin[t] += 1
            pos[t] += i / (n - 1) if n > 1 else 0.5
            nunits[t].add(k); ulen[t] += n
            if i > 0:
                L[t].add(u[i - 1]); nn[t] += 1
                pnum[t] += u[i - 1] in is_num; single[t] += occ[u[i - 1]] == 1
            if i < n - 1:
                R[t].add(u[i + 1]); nn[t] += 1
                fnum[t] += u[i + 1] in is_num; single[t] += occ[u[i + 1]] == 1
    types = [t for t, c in occ.items() if c >= MINF]
    rows = []
    for t in types:
        c = occ[t]
        rows.append([np.log(c), ini[t] / c, fin[t] / c, pos[t] / c, len(L[t]) / c, len(R[t]) / c,
                     pnum[t] / c, fnum[t] / c, len(nunits[t]) / c, single[t] / max(nn[t], 1), ulen[t] / c])
    X = np.array(rows, float)
    X = np.column_stack([rankdata(X[:, j]) / len(X) for j in range(X.shape[1])])
    return types, X


def script_data(name, seed):
    U = load(name)
    r = random.Random(seed); S = r.sample(U, N_UNITS)
    lab = defaultdict(Counter)
    for u in S:
        for t, c in u: lab[t][c] += 1
    is_num = {t for t, c in lab.items() if c.most_common(1)[0][0] == "NUM"}
    types, X = features([[t for t, _ in u] for u in S], is_num)
    y = np.array([lab[t].most_common(1)[0][0] or "NONE" for t in types])
    keep = np.isin(y, TARGET)
    return X[keep], y[keep]


def macro(y, p):
    cls = [c for c in TARGET if (y == c).sum() >= 10]
    return f1_score(y, p, labels=cls, average="macro")


def fit(X, y):
    m = LogisticRegression(C=1.0, class_weight="balanced", max_iter=2000)
    return m.fit(X, y)


def gate():
    res = {s: {"full": [], "base": [], "n_types": [], "class_counts": None} for s in SCRIPTS}
    null = {}
    for seed in SEEDS:
        D = {s: script_data(s, seed) for s in SCRIPTS}
        for s in SCRIPTS:
            tr = [x for x in SCRIPTS if x != s]
            Xtr = np.vstack([D[x][0] for x in tr]); ytr = np.concatenate([D[x][1] for x in tr])
            Xte, yte = D[s]
            res[s]["full"].append(macro(yte, fit(Xtr, ytr).predict(Xte)))
            res[s]["base"].append(macro(yte, fit(Xtr[:, :1], ytr).predict(Xte[:, :1])))
            res[s]["n_types"].append(int(len(yte)))
            if seed == 0:
                res[s]["class_counts"] = dict(Counter(yte.tolist()))
                rng = np.random.default_rng(0); vals = []
                for _ in range(NPERM):
                    yp = np.concatenate([rng.permutation(D[x][1]) for x in tr])
                    vals.append(macro(yte, fit(Xtr, yp).predict(Xte)))
                null[s] = sorted(vals)
    out = {}
    ok = True
    for s in SCRIPTS:
        f = float(np.mean(res[s]["full"])); b = float(np.mean(res[s]["base"]))
        n95 = null[s][int(0.95 * NPERM) - 1]
        p = (sum(v >= f for v in null[s]) + 1) / (NPERM + 1)
        pas = (f >= b + 0.10) and (f > n95)
        ok &= pas
        out[s] = dict(full=f, full_runs=res[s]["full"], base=b, base_runs=res[s]["base"], null_mean=float(np.mean(null[s])),
                      null_95=n95, p_perm=p, n_types=res[s]["n_types"], class_counts=res[s]["class_counts"], pass_=pas)
    return out, ok


def indus(seed=0):
    texts = distinct(m77_texts())
    dev, ho = dev_heldout(texts)
    def units(T):
        return [r for t in T for r in runs(t["seq"]) if len(r) >= 2]
    Dtr = {s: script_data(s, seed) for s in SCRIPTS}
    m = fit(np.vstack([Dtr[s][0] for s in SCRIPTS]), np.concatenate([Dtr[s][1] for s in SCRIPTS]))
    out = {}
    for name, T in (("dev", dev), ("heldout", ho)):
        U = units(T)
        types, X = features(U, set(M_NUM))
        keep = [i for i, t in enumerate(types) if t not in M_NUM]
        P = m.predict_proba(X[keep])
        out[name] = {types[i]: dict(zip(m.classes_.tolist(), P[j].round(3).tolist())) for j, i in enumerate(keep)}
    common = sorted(set(out["dev"]) & set(out["heldout"]))
    rho = {c: float(spearmanr([out["dev"][t][c] for t in common], [out["heldout"][t][c] for t in common])[0]) for c in m.classes_}
    agree = {}
    for t in common:
        a = max(out["dev"][t], key=out["dev"][t].get); b = max(out["heldout"][t], key=out["heldout"][t].get)
        if a == b and out["dev"][t][a] >= 0.6 and out["heldout"][t][b] >= 0.6:
            agree[t] = a
    return dict(n_common=len(common), spearman=rho, stable_assignments=agree,
                stable_counts=dict(Counter(agree.values())), dev_probs=out["dev"])


if __name__ == "__main__":
    out, ok = gate()
    print(json.dumps(out, indent=1, default=float))
    R = {"gate": out, "gate_pass": bool(ok)}
    if ok:
        R["indus"] = indus()
        print(json.dumps({k: v for k, v in R["indus"].items() if k != "dev_probs"}, indent=1))
    else:
        print("GATE FAILED: no Indus application")
    json.dump(R, open(HERE / "results.json", "w"), indent=1, default=float)
