"""T5 site signal: shared data, allograph maps, features, CV and permutation machinery.

Run scripts from repo root: .venv/bin/python experiments/site_signal/<script>.py
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from corpus.load import icit_texts, m77_texts  # noqa: E402
from corpus.build import _close  # noqa: E402  (splits_v2 family rule)

HERE = Path(__file__).resolve().parent
SEED = 20261114

# --------------------------------------------------------------- allograph maps
BRIDGE = json.load(open(ROOT / "sources/shaunmortal_indus/data/bridge_WM.json"))
M5 = json.load(open(ROOT / "sources/shaunmortal_indus/data/model5_wells_allographs.json"))


class UF:
    def __init__(self):
        self.p = {}

    def f(self, a):
        self.p.setdefault(a, a)
        while self.p[a] != a:
            self.p[a] = self.p[self.p[a]]
            a = self.p[a]
        return a

    def u(self, a, b):
        ra, rb = self.f(a), self.f(b)
        if ra != rb:
            self.p[max(ra, rb)] = min(ra, rb)


def W(n):
    return "W%03d" % int(n)


FISH = {220, 231, 233, 235, 240}  # fish family (lexical class members, not carving variants)
NUMERAL_PAIR = {(31, 32)}         # tall-1 ~ tall-2 (stroke count, not carving)
FONT_ARTEFACT = {(405, 407)}


def allograph_map(level):
    """level 'A0' raw Wells; 'A1' carving-variant merges; 'A2' A1 + fish family + tall-1/2."""
    if level == "A0":
        return {}
    uf = UF()
    # (a) Wells splits that Mahadevan lumps: several W with exactly one M each, same M
    byM = defaultdict(list)
    for w, v in BRIDGE.items():
        if len(v["M"]) == 1:
            byM[v["M"][0]].append(int(w))
    for m, ws in byM.items():
        for w in ws[1:]:
            uf.u(W(ws[0]), W(w))
    # (b) image+distribution allograph candidates (shaunmortal M5)
    for a, b, _img, _dist in M5["allograph_candidates"]:
        if (a, b) in FONT_ARTEFACT:
            continue
        if level == "A1" and ((a, b) in NUMERAL_PAIR or (a in FISH and b in FISH)):
            continue
        uf.u(W(a), W(b))
    if level == "A2":
        for a in FISH:
            uf.u(W(220), W(a))
        uf.u(W(31), W(32))
    return {k: uf.f(k) for k in list(uf.p)}


def allograph_groups(level):
    m = allograph_map(level)
    g = defaultdict(set)
    for k, r in m.items():
        g[r].add(k)
    return {r: sorted(s) for r, s in g.items() if len(s) > 1}


# --------------------------------------------------------------- data
COORDS = {  # decimal degrees (approx. site centres)
    "Mohenjo-daro": (27.329, 68.139), "Harappa": (30.631, 72.864), "Dholavira": (23.887, 70.213),
    "Lothal": (22.522, 72.249), "Chanhu-daro": (26.174, 68.322), "Kalibangan": (29.473, 74.130),
    "Banawali": (29.597, 75.391), "Nausharo": (29.360, 67.600),
}


def band(t):
    """Coarse aligned period band (pre-registered): 'late', 'earlier', or None (undated/ambiguous)."""
    s, per, ph = t["site"], t["period"].strip(), t["phase"].strip()
    if s == "Mohenjo-daro":
        if per == "Late":
            return "late"
        if per in ("Early", "Intermediate"):
            return "earlier"
        return None
    if s == "Harappa":
        if per == "3":
            return {"C": "late", "A": "earlier", "B": "earlier"}.get(ph)  # B/C mixed -> None
        if ph.startswith("Stratum"):
            r = ph.replace("Stratum", "").strip()
            return "late" if r in ("I", "II", "III") else ("earlier" if r in ("IV", "V", "VI", "VII") else None)
    return None


def fine_period(t):
    return (t["period"].strip() + "/" + t["phase"].strip())


def icit_seals():
    """ICIT seal inscriptions: type SEAL*, complete flag, no break marks, >= 1 sign."""
    out = []
    for t in icit_texts():
        if not t["type"].startswith("SEAL"):
            continue
        if "#" in t["seq"] or not t["complete"]:
            continue
        signs = [s for s in t["seq"] if s != "|"]
        if not signs:
            continue
        r = dict(t)
        r["signs"] = signs
        r["runs"] = [list(x) for x in t["segments"]]
        out.append(r)
    return out


def families_over(keys_signs, direct=None):
    """Union-find over distinct sign tuples with corpus/build.py _close.
    If `direct` is a dict, it is filled with key -> number of distinct texts it is directly _close to."""
    keys = list(keys_signs)
    parent = list(range(len(keys)))

    def f(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    idx = [i for i, k in enumerate(keys) if len(k) >= 3]  # 1-2 sign texts never link under _close
    idx.sort(key=lambda i: len(keys[i]))
    sets = {i: set(keys[i]) for i in idx}
    for a_pos, i in enumerate(idx):
        a = keys[i]
        for j in idx[a_pos + 1:]:
            b = keys[j]
            if len(b) - len(a) > 1 and not sets[i] <= sets[j]:
                continue
            if len(sets[i] & sets[j]) < len(sets[i]) - 1:
                continue
            if _close(list(a), list(b)):
                if direct is not None:
                    direct[a] = direct.get(a, 0) + 1
                    direct[b] = direct.get(b, 0) + 1
                ri, rj = f(i), f(j)
                if ri != rj:
                    parent[ri] = rj
    return {k: f(i) for i, k in enumerate(keys)}


def eligible_icit(variant="strict"):
    """Seals for the test.
    strict: (PRIMARY) drop any seal whose exact text occurs on more than one ICIT object of any type,
            and any seal that is directly a near-copy (_close) of another distinct ICIT text.
    chain:  drop exact repeats and every seal whose CHAINED v2 family holds another distinct text
            (transitive 3-sign containment chains 338 seals into one family; sensitivity only).
    rep:    drop exact repeats; keep one seal (lowest id) per family.
    all:    drop exact repeats only; families kept and used as CV groups.
    Returns list of records with 'fam' set."""
    allt = icit_texts()
    cnt = Counter(tuple(s for s in t["seq"] if s not in ("|", "#")) for t in allt)
    # family universe: all distinct break-free ICIT texts (any object type) with >= 1 sign
    universe = set()
    for t in allt:
        k = tuple(s for s in t["seq"] if s not in ("|",))
        if "#" in k:
            # broken texts join families through their longest run (contained-copy rule)
            for r in t["segments"]:
                if len(r) >= 3:
                    universe.add(tuple(r))
        elif k:
            universe.add(k)
    direct = {}
    fam = families_over(universe, direct)
    famsize = Counter(fam.values())
    seals = icit_seals()
    out, seen_fam = [], set()
    for t in sorted(seals, key=lambda r: float(r["id"]) if r["id"].replace(".", "", 1).isdigit() else 1e9):
        k = tuple(t["signs"])
        if cnt[k] > 1:
            continue
        f = fam[k]
        if variant == "strict" and direct.get(k, 0) > 0:
            continue
        if variant == "chain" and famsize[f] > 1:
            continue
        if variant == "rep":
            if f in seen_fam:
                continue
            seen_fam.add(f)
        t["fam"] = f
        out.append(t)
    return out


def eligible_m77():
    """M77 seals, complete, no breaks; strict exclusion of exact repeats (any object) and v2 families."""
    allt = m77_texts()
    cnt = Counter(tuple(s for s in t["seq"] if s not in ("|", "#")) for t in allt)
    universe = set(tuple(s for s in t["seq"] if s != "|") for t in allt if "#" not in t["seq"] and t["seq"])
    fam = families_over(universe)
    famsize = Counter(fam.values())
    out = []
    for t in allt:
        if t["object_type"] != "seal" or "#" in t["seq"] or not t.get("complete"):
            continue
        k = tuple(s for s in t["seq"] if s != "|")
        if not k or cnt[k] > 1 or famsize[fam[k]] > 1:
            continue
        r = dict(t)
        r["signs"] = list(k)
        r["runs"] = []
        cur = []
        for s in t["seq"]:
            if s == "|":
                if cur:
                    r["runs"].append(cur)
                cur = []
            else:
                cur.append(s)
        if cur:
            r["runs"].append(cur)
        r["fam"] = fam[k]
        r["site"] = {"Mohenjodaro": "Mohenjo-daro"}.get(t["site"], t["site"])
        out.append(r)
    return out


# --------------------------------------------------------------- features
def mapped(seq, amap):
    return [amap.get(s, s) for s in seq]


def slot_features(t, amap, slot):
    """slot: 'all' (unigrams + bigrams within runs), 'opener' (first sign), 'closer' (last sign),
    'medial' (unigrams of signs 2..n-1 and bigrams wholly inside them, within runs),
    'frame' (opener + closer)."""
    sg = mapped(t["signs"], amap)
    n = len(sg)
    if slot == "opener":
        return {"u:" + sg[0]}
    if slot == "closer":
        return {"u:" + sg[-1]}
    if slot == "frame":
        return {"o:" + sg[0], "c:" + sg[-1]}
    feats = set()
    if slot == "all":
        for s in sg:
            feats.add("u:" + s)
        for r in t["runs"]:
            r = mapped(r, amap)
            for a, b in zip(r, r[1:]):
                feats.add("b:" + a + "_" + b)
        return feats
    if slot == "medial":
        if n < 3:
            return feats
        # positions 1..n-2 in the flattened text; bigrams only if adjacent in one run
        pos_in_run = []
        for ri, r in enumerate(t["runs"]):
            for j in range(len(r)):
                pos_in_run.append((ri, j))
        for i in range(1, n - 1):
            feats.add("u:" + sg[i])
        for i in range(1, n - 2):
            if pos_in_run[i][0] == pos_in_run[i + 1][0]:
                feats.add("b:" + sg[i] + "_" + sg[i + 1])
        return feats
    raise ValueError(slot)


def design(texts, amap, slot, min_df=2):
    from scipy.sparse import csr_matrix
    F = [slot_features(t, amap, slot) for t in texts]
    df = Counter(f for fs in F for f in fs)
    vocab = sorted(f for f, c in df.items() if c >= min_df)
    idx = {f: i for i, f in enumerate(vocab)}
    rows, cols = [], []
    for i, fs in enumerate(F):
        for f in fs:
            if f in idx:
                rows.append(i); cols.append(idx[f])
    X = csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(len(texts), len(vocab)))
    return X, vocab


# --------------------------------------------------------------- CV
def folds(y, groups, k, rng):
    """Stratified group folds: assign each group (all members share a label in practice) to a fold,
    balancing class counts. Returns fold id per sample."""
    g2idx = defaultdict(list)
    for i, g in enumerate(groups):
        g2idx[g].append(i)
    glist = list(g2idx)
    rng.shuffle(glist)
    # order by majority label then size, deal round-robin within label to balance
    fold = np.empty(len(y), dtype=int)
    counters = defaultdict(int)
    for g in sorted(glist, key=lambda g: Counter(y[i] for i in g2idx[g]).most_common(1)[0][0]):
        lab = Counter(y[i] for i in g2idx[g]).most_common(1)[0][0]
        f = counters[lab] % k
        counters[lab] += 1
        for i in g2idx[g]:
            fold[i] = f
    return fold


def oof_scores(X, y, groups, model="nb", k=5, reps=3, seed=SEED, classes=None):
    """Out-of-fold class probabilities averaged over repeated stratified group k-fold."""
    from sklearn.naive_bayes import BernoulliNB
    from sklearn.linear_model import LogisticRegression
    rng = np.random.default_rng(seed)
    classes = classes if classes is not None else np.unique(y)
    P = np.zeros((len(y), len(classes)))
    for _ in range(reps):
        fold = folds(y, groups, k, rng)
        for f in range(k):
            tr, te = fold != f, fold == f
            if te.sum() == 0 or len(np.unique(y[tr])) < len(classes):
                continue
            if model == "nb":
                clf = BernoulliNB(alpha=1.0, fit_prior=False)
            else:
                clf = LogisticRegression(C=0.5, class_weight="balanced", max_iter=2000, solver="liblinear")
            clf.fit(X[tr], y[tr])
            pr = clf.predict_proba(X[te])
            cl = list(clf.classes_)
            for j, c in enumerate(classes):
                P[te, j] += pr[:, cl.index(c)]
    return P / reps


def auc(y01, s):
    from scipy.stats import rankdata
    r = rankdata(s)
    n1 = y01.sum(); n0 = len(y01) - n1
    return (r[y01 == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


def bal_acc(y, P, classes):
    pred = np.array(classes)[P.argmax(1)]
    return float(np.mean([np.mean(pred[y == c] == c) for c in classes]))


def permute_within(y, strata, rng):
    y2 = y.copy()
    for s in np.unique(strata):
        ix = np.where(strata == s)[0]
        y2[ix] = y[rng.permutation(ix)]
    return y2


def jdump(obj, path):
    def conv(o):
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        raise TypeError(type(o))
    json.dump(obj, open(path, "w"), indent=1, default=conv)
