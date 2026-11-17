"""Power check + held-out-script gate on genre-matched corpora (prereg docs/prereg/meaning_classes_seal.md).
Run: .venv/bin/python -I experiments/meaning_classes_seal/gate.py
Features, model and scoring are imported unchanged from experiments/meaning_classes/mc_gate.py.
"""
import json, random, sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments/meaning_classes"))
import mc_gate as G  # noqa  (features, fit, macro, TARGET, MINF, indus procedure)

SCRIPTS = ["cun_seal", "egy_nom", "lat_label"]
N_UNITS, NPERM, SEEDS = 2300, 200, [0, 1, 2, 3, 4]


def load(name):
    U = []
    for l in open(HERE / "data" / f"{name}.jsonl"):
        r = json.loads(l)
        if 2 <= len(r["seq"]) <= 17:
            U.append(list(zip(r["seq"], r["cls"])))
    return U


ALL = {s: load(s) for s in SCRIPTS}


def xy(S, rename=None):
    lab = defaultdict(Counter)
    for u in S:
        for t, c in u: lab[t][c] += 1
    is_num = {t for t, c in lab.items() if c.most_common(1)[0][0] == "NUM"}
    types, X = G.features([[t for t, _ in u] for u in S], is_num)
    y = np.array([lab[t].most_common(1)[0][0] or "NONE" for t in types])
    keep = np.isin(y, G.TARGET)
    return X[keep], y[keep]


def sample(s, seed, n=N_UNITS):
    U = ALL[s]; r = random.Random(seed)
    return r.sample(U, min(n, len(U)))


def halves(s, seed):
    U = ALL[s][:]; random.Random(1000 + seed).shuffle(U)
    h = min(len(U) // 2, N_UNITS)
    return U[:h], U[h:2 * h]


def evaluate(train_sets, test_set, perm_seed=None):
    Xtr = np.vstack([a for a, _ in train_sets]); ytr = np.concatenate([b for _, b in train_sets])
    Xte, yte = test_set
    full = G.macro(yte, G.fit(Xtr, ytr).predict(Xte))
    base = G.macro(yte, G.fit(Xtr[:, :1], ytr).predict(Xte[:, :1]))
    null = None
    if perm_seed is not None:
        rng = np.random.default_rng(perm_seed); null = []
        for _ in range(NPERM):
            yp = np.concatenate([rng.permutation(b) for _, b in train_sets])
            null.append(G.macro(yte, G.fit(Xtr, yp).predict(Xte)))
        null.sort()
    return full, base, null


def verdict(full, base, null):
    n95 = null[int(0.95 * NPERM) - 1]
    p = (sum(v >= full for v in null) + 1) / (NPERM + 1)
    return dict(full=full, base=base, null_mean=float(np.mean(null)), null_95=n95, p_perm=p,
                pass_=bool(full >= base + 0.10 and full > n95))


def power():
    """same-system transfer: train on other scripts + half A of S; test on half B of S (types renamed:
    features are computed on B alone, so no type identity is shared)."""
    out = {}
    for s in SCRIPTS:
        F, B, W = [], [], []
        null = None
        for seed in SEEDS:
            a, b = halves(s, seed)
            others = [xy(sample(o, seed)) for o in SCRIPTS if o != s]
            A, Bt = xy(a), xy(b)
            f, bs, nl = evaluate(others + [A], Bt, perm_seed=0 if seed == 0 else None)
            F.append(f); B.append(bs)
            if nl is not None: null = nl
            W.append(evaluate([A], Bt)[0])               # within-script ceiling
        v = verdict(float(np.mean(F)), float(np.mean(B)), null)
        v.update(within_script=float(np.mean(W)), half_units=len(a), runs=F)
        out[s] = v
    return out, sum(v["pass_"] for v in out.values()) >= 2


def gate():
    out = {}
    for s in SCRIPTS:
        F, B = [], []; null = None; cc = None; nt = []
        for seed in SEEDS:
            D = {x: xy(sample(x, seed)) for x in SCRIPTS}
            tr = [D[x] for x in SCRIPTS if x != s]
            f, bs, nl = evaluate(tr, D[s], perm_seed=0 if seed == 0 else None)
            F.append(f); B.append(bs); nt.append(int(len(D[s][1])))
            if nl is not None: null = nl; cc = dict(Counter(D[s][1].tolist()))
        v = verdict(float(np.mean(F)), float(np.mean(B)), null)
        v.update(runs=F, n_types=nt, class_counts=cc, units=min(N_UNITS, len(ALL[s])))
        out[s] = v
    return out, all(v["pass_"] for v in out.values())


if __name__ == "__main__":
    print({s: len(ALL[s]) for s in SCRIPTS})
    P, pok = power()
    print("POWER", json.dumps(P, indent=1, default=float)); print("power gate pass:", pok)
    Gt, gok = gate()
    print("GATE", json.dumps(Gt, indent=1, default=float)); print("held-out gate pass:", gok)
    R = dict(power=P, power_pass=bool(pok), gate=Gt, gate_pass=bool(gok and pok))
    if gok and pok:
        G.SCRIPTS = SCRIPTS
        G.script_data = lambda name, seed: xy(sample(name, seed))
        R["indus"] = G.indus()
        print(json.dumps({k: v for k, v in R["indus"].items() if k != "dev_probs"}, indent=1))
    else:
        print("GATE FAILED: no Indus application")
    json.dump(R, open(HERE / "results.json", "w"), indent=1, default=float)
