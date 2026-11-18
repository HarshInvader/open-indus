"""slot_function: tests A (which slot carries object type) and B (human-figure signs as counted).

Pre-registration: docs/prereg/slot_function.md. Run:
    .venv/bin/python -I experiments/slot_function/sf.py gate   # planted checks only
    .venv/bin/python -I experiments/slot_function/sf.py full   # gates, then real tests
Writes experiments/slot_function/out/*.json.
"""
import json, sys, zlib
from pathlib import Path
from collections import Counter
import numpy as np
from scipy.optimize import minimize

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from corpus import load  # noqa: E402

OUT = Path(__file__).parent / "out"
OUT.mkdir(exist_ok=True)


def rng(tag):
    return np.random.default_rng(zlib.crc32(tag.encode()))


# ---------------------------------------------------------------- data
SEAL, LABEL = 0, 1
M77_LABEL = {"miniature tablet", "copper tablet", "pottery graffito", "ivory/bone rod", "bronze implement"}


def icit_class(t):
    ty = t["type"]
    if ty.startswith("SEAL"):
        return SEAL
    if ty in ("TAB:B", "TAB:I", "TAB:C", "ROD", "BNGL") or ty.startswith("TAG") or ty.startswith("POT"):
        return LABEL
    return None


def usable(t):
    return t["complete"] and "#" not in t["seq"] and len([s for s in t["seq"] if s != "|"]) >= 3


def flat(t):
    return [s for s in t["seq"] if s != "|"]


def icit_A():
    out = []
    for t in load.distinct(load.icit_texts()):
        c = icit_class(t)
        if c is not None and usable(t):
            out.append((flat(t), c, t["site"]))
    return out


def m77_A():
    dev, ho = load.dev_heldout(version=2)

    def conv(ts):
        r = []
        for t in ts:
            if not usable(t):
                continue
            if t["object_type"] == "seal":
                r.append((flat(t), SEAL))
            elif t["object_type"] in M77_LABEL:
                r.append((flat(t), LABEL))
        return r
    return conv(dev), conv(ho)


# ---------------------------------------------------------------- model
def lenbin(n):
    return min(n, 6) - 3  # 0..3 for 3,4,5,6+


def featurize(train_seqs, test_seqs, kind):
    """One-hot slot features (+4 length bins). Signs seen < 2 times in training -> UNK."""
    def slot(seq):
        if kind == "INIT":
            return [seq[0]]
        if kind == "TERM":
            return [seq[-1]]
        if kind == "MID":
            return seq[1:-1]
        return []
    cnt = Counter(s for q in train_seqs for s in slot(q))
    vocab = {s: i for i, s in enumerate(sorted(k for k, v in cnt.items() if v >= 2))}
    unk = len(vocab)
    d = unk + 1 + 4

    def mat(seqs):
        X = np.zeros((len(seqs), d))
        for r, q in enumerate(seqs):
            for s in slot(q):
                X[r, vocab.get(s, unk)] += 1
            X[r, unk + 1 + lenbin(len(q))] = 1
        return X
    return mat(train_seqs), mat(test_seqs)


def fit_lr(X, y, C=1.0):
    """L2 logistic regression, sklearn convention: C * sum(logloss) + 0.5 |w|^2 (intercept unpenalised)."""
    n, d = X.shape

    def f(w):
        z = X @ w[:d] + w[d]
        ll = np.logaddexp(0, z) - y * z
        p = 1 / (1 + np.exp(-z))
        g = X.T @ (p - y) * C + w[:d]
        return C * ll.sum() + 0.5 * w[:d] @ w[:d], np.append(g, C * (p - y).sum())
    w = minimize(f, np.zeros(d + 1), jac=True, method="L-BFGS-B").x
    return w


def predict(w, X):
    return X @ w[:-1] + w[-1]


def auc(score, y):
    from scipy.stats import rankdata
    r = rankdata(score)
    n1 = y.sum(); n0 = len(y) - n1
    return (r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


def cv_scores(seqs, y, kind, seed=0):
    """5-fold CV stratified by class; returns pooled out-of-fold scores."""
    g = np.random.default_rng(seed)
    folds = np.zeros(len(y), int)
    for c in (0, 1):
        idx = np.where(y == c)[0]
        g.shuffle(idx)
        folds[idx] = np.arange(len(idx)) % 5
    sc = np.zeros(len(y))
    for k in range(5):
        tr, te = folds != k, folds == k
        Xtr, Xte = featurize([seqs[i] for i in np.where(tr)[0]], [seqs[i] for i in np.where(te)[0]], kind)
        sc[te] = predict(fit_lr(Xtr, y[tr]), Xte)
    return sc


def boot_diff(s_term, s_init, y, n=2000, tag="boot"):
    g = rng(tag)
    i1, i0 = np.where(y == 1)[0], np.where(y == 0)[0]
    diffs = np.empty(n)
    for b in range(n):  # stratified resample keeps both classes present
        idx = np.concatenate([g.choice(i1, len(i1)), g.choice(i0, len(i0))])
        yy = y[idx]
        diffs[b] = auc(s_term[idx], yy) - auc(s_init[idx], yy)
    return diffs


def a1_rule(seqs, y, tag, nboot=2000):
    st, si = cv_scores(seqs, y, "TERM"), cv_scores(seqs, y, "INIT")
    d = auc(st, y) - auc(si, y)
    bd = boot_diff(st, si, y, nboot, tag)
    lo, hi = np.percentile(bd, [2.5, 97.5])
    return dict(auc_term=auc(st, y), auc_init=auc(si, y), diff=d, ci=[lo, hi],
                p_one_sided=float((bd <= 0).mean()), fires=bool(d >= 0.03 and lo > 0))


def shuffle_within(seqs, g):
    out = []
    for q in seqs:
        q = list(q); g.shuffle(q); out.append(q)
    return out


# ---------------------------------------------------------------- test A
def gate_A(nplant=100, nboot=2000):
    """Planted check (A1 rule exactly as in the real test)."""
    data = icit_A()
    seqs = [d[0] for d in data]; y = np.array([d[1] for d in data])
    res = {"term": 0, "init": 0, "none": 0}
    for i in range(nplant):
        g = rng(f"gateA{i}")
        sh = shuffle_within(seqs, g)
        lab = np.where(y == 1)[0]
        pick = g.choice(lab, int(round(0.15 * len(lab))), replace=False)
        for where in ("term", "init"):
            q = [list(s) for s in sh]
            for j in pick:
                if where == "term":
                    q[j][-1] = "PLANT"
                else:
                    q[j][0] = "PLANT"
            res[where] += a1_rule(q, y, f"gA{where}{i}", nboot)["fires"]
        res["none"] += a1_rule(sh, y, f"gAn{i}", nboot)["fires"]
        print("gateA", i, res, flush=True)
    res["pass"] = res["term"] >= 80 and res["init"] <= 5 and res["none"] <= 10
    json.dump(res, open(OUT / "gate_A.json", "w"), indent=1)
    return res


def test_A(nnull_icit=200, nnull_m77=500):
    data = icit_A()
    seqs = [d[0] for d in data]; y = np.array([d[1] for d in data])
    out = {"icit_n": {"seal": int((y == 0).sum()), "label": int((y == 1).sum())}}
    a1 = a1_rule(seqs, y, "A1icit")
    out["A1_icit"] = a1
    for k in ("MID", "LEN"):
        out[f"auc_{k}_icit"] = auc(cv_scores(seqs, y, k), y)
    null = []
    for i in range(nnull_icit):
        sh = shuffle_within(seqs, rng(f"A2icit{i}"))
        null.append(auc(cv_scores(sh, y, "TERM"), y))
    null = np.array(null)
    out["A2_icit"] = dict(auc_term=a1["auc_term"], null_p95=float(np.percentile(null, 95)),
                         null_mean=float(null.mean()), p=float((1 + (null >= a1["auc_term"]).sum()) / (1 + len(null))))
    out["A2_icit"]["holds"] = bool(a1["auc_term"] > out["A2_icit"]["null_p95"])
    # M77: fit on dev, score held-out
    dev, ho = m77_A()
    ys_d = np.array([d[1] for d in dev]); ys_h = np.array([d[1] for d in ho])
    sd = [d[0] for d in dev]; sh_ = [d[0] for d in ho]
    m = {"n_dev": [int((ys_d == 0).sum()), int((ys_d == 1).sum())], "n_held": [int((ys_h == 0).sum()), int((ys_h == 1).sum())]}
    sc = {}
    for k in ("TERM", "INIT", "MID", "LEN"):
        Xtr, Xte = featurize(sd, sh_, k)
        sc[k] = predict(fit_lr(Xtr, ys_d), Xte)
        m[f"auc_{k}"] = auc(sc[k], ys_h)
    m["diff"] = m["auc_TERM"] - m["auc_INIT"]
    bd = boot_diff(sc["TERM"], sc["INIT"], ys_h, 2000, "A1m77")
    m["ci"] = list(np.percentile(bd, [2.5, 97.5]))
    null = []
    for i in range(nnull_m77):
        g = rng(f"A2m77{i}")
        a, b = shuffle_within(sd, g), shuffle_within(sh_, g)
        Xtr, Xte = featurize(a, b, "TERM")
        null.append(auc(predict(fit_lr(Xtr, ys_d), Xte), ys_h))
    null = np.array(null)
    m["A2_null_p95"] = float(np.percentile(null, 95)); m["A2_null_mean"] = float(null.mean())
    m["A2_p"] = float((1 + (null >= m["auc_TERM"]).sum()) / (1 + len(null)))
    out["m77"] = m
    icit_ok = a1["fires"] and out["A2_icit"]["holds"]
    if a1["diff"] <= 0:
        v = "REFUTED"
    elif icit_ok and np.sign(m["diff"]) == np.sign(a1["diff"]):
        v = "SUPPORTED"
    elif icit_ok:
        v = "WEAKENED"
    else:
        v = "WEAKENED (direction right, ICIT thresholds missed)"
    out["verdict"] = v
    json.dump(out, open(OUT / "test_A.json", "w"), indent=1, default=float)
    return out


# ---------------------------------------------------------------- test B
H = {f"M{i}" for i in range(1, 47)}
HT = {f"M{i}" for i in range(18, 47)}
NUM = {f"M{i}" for i in range(86, 123)} - {"M99", "M100"}


def m77_runs(texts):
    return [r for t in texts for r in load.runs(t["seq"]) if len(r) >= 2]


def sign_counts(runs_):
    """Per sign: (non-initial tokens, non-initial tokens preceded by NUM)."""
    den, num = Counter(), Counter()
    for r in runs_:
        for a, b in zip(r, r[1:]):
            den[b] += 1
            if a in NUM:
                num[b] += 1
    return den, num


def control_sets(dev_runs, target, nsets, tag):
    tok = Counter(s for r in dev_runs for s in r)
    fin = Counter(r[-1] for r in dev_runs)
    seen = sorted(tok)
    freqs = np.array([tok[s] for s in seen])
    fshare = np.array([fin[s] / tok[s] for s in seen])
    dec_cut = np.percentile(freqs, np.arange(10, 100, 10))
    ter_cut = np.percentile(fshare, [100 / 3, 200 / 3])
    dec = dict(zip(seen, np.searchsorted(dec_cut, freqs, side="right")))
    ter = dict(zip(seen, np.searchsorted(ter_cut, fshare, side="right")))
    pool = [s for s in seen if s not in H and s not in NUM]
    tgt = [s for s in sorted(target) if s in tok]
    g = rng(tag)
    sets = []
    for _ in range(nsets):
        used, cs = set(), []
        for s in tgt:
            cand = [c for c in pool if dec[c] == dec[s] and ter[c] == ter[s] and c not in used]
            if not cand:
                cand = [c for c in pool if dec[c] == dec[s] and c not in used] or [c for c in pool if c not in used]
            c = cand[g.integers(len(cand))]
            used.add(c); cs.append(c)
        sets.append(cs)
    return tgt, sets


def rate(signs, den, num):
    d = sum(den[s] for s in signs)
    return sum(num[s] for s in signs) / d if d else np.nan


def b1_rule(tgt, sets, runs_):
    den, num = sign_counts(runs_)
    rh = rate(tgt, den, num)
    rc = np.array([rate(s, den, num) for s in sets])
    ratio = rh / rc.mean() if rc.mean() > 0 else np.inf
    p95 = float(np.percentile(rc, 95))
    return dict(r=rh, ctrl_mean=float(rc.mean()), ctrl_p95=p95, ratio=float(ratio),
                p=float((1 + (rc >= rh).sum()) / (1 + len(rc))), fires=bool(ratio >= 2 and rh >= p95))


def gate_B(nplant=100):
    dev, ho = load.dev_heldout(version=2)
    dr, hr = m77_runs(dev), m77_runs(ho)
    tgt, sets = control_sets(dr, H, 1000, "B1sets")
    numl = sorted(NUM)
    hits = 0
    for i in range(nplant):
        g = rng(f"gateB{i}")
        sh = shuffle_within(hr, g)
        k = int(g.integers(len(sets)))
        pseudo = set(sets[k])
        occ = [(a, j) for a, r in enumerate(sh) for j in range(1, len(r)) if r[j] in pseudo]
        pick = g.choice(len(occ), int(round(0.3 * len(occ))), replace=False) if occ else []
        for p in pick:
            a, j = occ[p]
            sh[a][j - 1] = numl[g.integers(len(numl))]
        others = [s for t, s in enumerate(sets) if t != k]
        hits += b1_rule(sets[k], others, sh)["fires"]
    res = {"hits": hits, "n": nplant, "pass": hits >= 80}
    json.dump(res, open(OUT / "gate_B.json", "w"), indent=1)
    return res


def mh_or(tables):
    nume = sum(a * d / (a + b + c + d) for a, b, c, d in tables if a + b + c + d)
    deno = sum(b * c / (a + b + c + d) for a, b, c, d in tables if a + b + c + d)
    return nume / deno if deno else np.inf


def test_B(nperm=2000):
    out = {}
    dev, ho = load.dev_heldout(version=2)
    dr, hr = m77_runs(dev), m77_runs(ho)
    for name, target in (("H", H), ("HT", HT)):
        tgt, sets = control_sets(dr, target, 1000, f"B1sets{'' if name == 'H' else name}")
        out[f"B1_{name}_held"] = b1_rule(tgt, sets, hr)
        out[f"B1_{name}_dev_exploratory"] = b1_rule(tgt, sets, dr)
        out[f"B1_{name}_targets_in_dev"] = len(tgt)
    # B2 on ICIT
    bridge = json.load(open(ROOT / "sources/shaunmortal_indus/data/bridge_WM.json"))
    HW = {f"W{int(k):03d}" for k, v in bridge.items() if any(1 <= m <= 46 for m in v["M"])}
    rows = []
    for t in load.distinct(load.icit_texts()):
        if not usable(t):
            continue
        ty = t["type"]
        cls = 1 if ty in ("TAB:B", "TAB:I") else 0 if ty.startswith("SEAL") else None
        if cls is None:
            continue
        q = flat(t)
        h = sum(s in HW for s in q)
        rows.append((t["site"], cls, h, len(q) - h))
    sites = sorted({r[0] for r in rows})

    def tables(cls_of):
        T = []
        for s in sites:
            a = b = c = d = 0
            for (site, _, h, nh), cl in zip(rows, cls_of):
                if site != s:
                    continue
                if cl == 1:
                    a += h; b += nh
                else:
                    c += h; d += nh
            T.append((a, b, c, d))
        return T
    cls = np.array([r[1] for r in rows])
    obs = mh_or(tables(cls))
    g = rng("B2perm")
    site_idx = {s: np.array([i for i, r in enumerate(rows) if r[0] == s]) for s in sites}
    perm = []
    for _ in range(nperm):
        c2 = cls.copy()
        for s, idx in site_idx.items():
            c2[idx] = g.permutation(cls[idx])
        perm.append(mh_or(tables(c2)))
    perm = np.array(perm)
    tot = np.array(tables(cls)).sum(0)
    out["B2_icit"] = dict(HW_size=len(HW), n_texts=len(rows), n_tablet=int(cls.sum()), mh_or=obs,
                          p=float((1 + (perm >= obs).sum()) / (1 + nperm)),
                          share_H_tablet=tot[0] / (tot[0] + tot[1]), share_H_seal=tot[2] / (tot[2] + tot[3]))
    out["B2_icit"]["holds"] = bool(obs >= 1.5 and out["B2_icit"]["p"] < 0.05)
    # M77 descriptive
    allm = load.distinct(load.m77_texts())
    def share(ot):
        toks = [s for t in allm if t["object_type"] == ot for s in flat(t) if s != "#"]
        return sum(s in H for s in toks) / len(toks)
    out["B2_m77_descriptive"] = {"miniature tablet": share("miniature tablet"), "seal": share("seal")}
    json.dump(out, open(OUT / "test_B.json", "w"), indent=1, default=float)
    return out


if __name__ == "__main__":
    mode = sys.argv[1]
    gb = gate_B(); print("gate_B", gb, flush=True)
    ga = gate_A(); print("gate_A", ga, flush=True)
    if mode == "full":
        print(json.dumps(test_B(), indent=1, default=float), flush=True)
        print(json.dumps(test_A(), indent=1, default=float), flush=True)
