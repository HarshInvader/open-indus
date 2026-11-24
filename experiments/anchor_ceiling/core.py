"""anchor_ceiling core (prereg docs/prereg/anchor_ceiling.md). Shared by words.py, kill.py and run.py.

Code-level rules fixed before any word x anchor count:
- word: a token that, after stripping the half brackets, is two or more syllabic signs joined by '-' and has a
  lowercase letter (e.g. 'po-me', '*56-ra'). Latin metadata words and one-sign adjuncts are not words.
- ideogram: a token with no lowercase syllable whose base (text before ':', ';', '+', '.') is SA, a capital name of
  >= 3 letters (OVIS, GRA, HORD, ...) or a numbered sign ('*146', '*209VAS'). Single capitals are measures
  (S T V Z M N P Q L X ...) and two-letter capitals are syllabic adjuncts (DA, TA, ZE ...): never ideograms.
- picture (A3): the first ideogram, collapsed to OVIS GRA VIR MUL OLE TELA LANA SA, else 'other', or 'none'.
- hand (A4): the last '( )' group of the heading; '(-)' -> 'unknown'.
"""
import math, random, re, sys
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.optimize import linear_sum_assignment
from sklearn.metrics import adjusted_rand_score

HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments/meaning_calibration")); sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments/language_vs_code"))
import load as LB          # noqa: E402
import fcore as F          # noqa: E402
import lvc_corpora as C    # noqa: E402

NDRAW = 5
MIN_DEV, MIN_HELD = 5, 2
PICS = ["OVIS", "GRA", "VIR", "MUL", "OLE", "TELA", "LANA", "SA"]
RUNGS = {"A1": ["site"], "A2": ["site", "cls"], "A3": ["site", "cls", "pic"], "A4": ["site", "cls", "pic", "hand"]}
ADDED = {"A1": "site", "A2": "cls", "A3": "pic", "A4": "hand"}
WORD = re.compile(r"[a-z0-9*]+(-[a-z0-9*]+)+")


def word_of(t):
    t = t.replace("⌞", "").replace("⌟", "")
    return t if WORD.fullmatch(t) and re.search(r"[a-z]", t) else None


def ideo_base(t):
    if t == "#" or re.search(r"[a-z]", t.split(":")[0].split(";")[0]) or re.fullmatch(r"\d+", t):
        return None
    b = re.split(r"[:;+.]", t)[0]
    if b == "SA" or re.fullmatch(r"[A-Z]{3,}", b) or re.fullmatch(r"\*\d+[A-Z]*", b):
        return b
    return None


def picture(seq):
    for t in seq:
        b = ideo_base(t)
        if b:
            return b if b in PICS else "other"
    return "none"


def hand(heading):
    m = re.findall(r"\(([^()]*)\)\s*$", heading)
    return m[0] if m and m[0] not in ("-", "") else "unknown"


def annotate(docs):
    for d in docs:
        d["words"] = sorted({w for w in map(word_of, d["seq"]) if w})
        d["pic"] = picture(d["seq"]); d["hand"] = hand(d["heading"])
    return docs


_DOCS = None


def all_docs():
    global _DOCS
    if _DOCS is None:
        _DOCS = annotate(LB.documents())
    return _DOCS


def draw_docs(k, docs=None):
    """Same stream as fcore.draw(k) (checked in words.py), returning document dicts."""
    docs = docs or all_docs()
    rng = random.Random(F.SEED0 + k)
    dl = [len(t) for t in C.indus("dev")]; hl = [len(t) for t in C.indus("held")]
    by = defaultdict(list)
    for i, d in enumerate(docs): by[LB.length(d["seq"])].append(i)
    for v in by.values(): rng.shuffle(v)
    def take(L):
        for dd in [0, 1, -1, 2, -2, 3, -3, 4, -4, 5, -5, 6, -6, 8, -8, 10, 12, 15, 20, 30, 50]:
            if by.get(L + dd): return docs[by[L + dd].pop()]
        return None
    dev = [take(dl[rng.randrange(len(dl))]) for _ in range(1680)]
    held = [take(hl[rng.randrange(len(hl))]) for _ in range(565)]
    return [d for d in dev if d], [d for d in held if d]


def doc_counts(docs):
    c = Counter()
    for d in docs: c.update(d["words"])
    return c


def eligible(dev, held):
    cd, ch = doc_counts(dev), doc_counts(held)
    el = sorted(w for w, n in cd.items() if n >= MIN_DEV)
    return el, sorted(w for w in el if ch[w] >= MIN_HELD), cd


# ---------- profiles and clustering ----------
def feature_space(dev, rung, A):
    """A: dict anchor -> list of values per doc id (A[var][doc_id]). Returns list of (var, value)."""
    return [(v, x) for v in RUNGS[rung] for x in sorted({A[v][d["id"]] for d in dev})]


def profiles(docs, words, rung, A, space, base_docs):
    """log-ratio of the word's per-value document share to the base rate (base = base_docs), add-0.5."""
    idx = {f: i for i, f in enumerate(space)}
    base = np.zeros(len(space)); nv = Counter(v for v, _ in space)
    for d in base_docs:
        for v in RUNGS[rung]:
            j = idx.get((v, A[v][d["id"]]))
            if j is not None: base[j] += 1
    nb = len(base_docs)
    base = np.array([(base[i] + 0.5) / (nb + 0.5 * nv[v]) for i, (v, _) in enumerate(space)])
    wi = {w: i for i, w in enumerate(words)}
    cnt = np.zeros((len(words), len(space))); n = np.zeros(len(words))
    for d in docs:
        rows = [wi[w] for w in d["words"] if w in wi]
        if not rows: continue
        cols = [idx[(v, A[v][d["id"]])] for v in RUNGS[rung] if (v, A[v][d["id"]]) in idx]
        for r in rows:
            n[r] += 1
            for c in cols: cnt[r, c] += 1
    den = np.array([[n[r] + 0.5 * nv[v] for (v, _) in space] for r in range(len(words))])
    return np.log(((cnt + 0.5) / den) / base[None, :])


def _unit(X):
    nrm = np.linalg.norm(X, axis=1, keepdims=True); nrm[nrm == 0] = 1
    return X / nrm


def cluster(P, k):
    if len(P) <= k: return np.arange(len(P))
    Z = linkage(_unit(P), method="average", metric="cosine")
    return fcluster(Z, t=k, criterion="maxclust") - 1


def assign(Q, P, lab):
    """nearest centroid (cosine); ties -> lowest cluster id (ids are stable in alphabetical word order)."""
    ks = sorted(set(lab))
    cent = _unit(np.array([P[lab == c].mean(0) for c in ks]))
    sim = _unit(Q) @ cent.T
    return np.array([ks[int(np.argmax(s))] for s in sim])


# ---------- scoring ----------
def field_f1(truth, pred, fields):
    """Hungarian-matched F1 per field (fields alphabetical; clusters sorted -> ties alphabetical)."""
    cl = sorted(set(pred))
    M = np.zeros((len(fields), len(cl)))
    t = np.asarray(truth); p = np.asarray(pred)
    for i, f in enumerate(fields):
        tf = t == f; nt = tf.sum()
        for j, c in enumerate(cl):
            pc = p == c; tp = (tf & pc).sum()
            M[i, j] = 0 if tp == 0 else 2 * tp / (nt + pc.sum())
    if not cl: return {f: 0.0 for f in fields}
    r, c = linear_sum_assignment(-M)
    out = {f: 0.0 for f in fields}
    for i, j in zip(r, c): out[fields[i]] = float(M[i, j])
    return out


def freq_bins(ws, cd):
    def b(n): return 0 if n < 10 else 1 if n < 20 else 2 if n < 50 else 3
    return np.array([b(cd[w]) for w in ws])


def perm_null(truth, pred, fields, bins, nperm, rng):
    """field-label permutations within frequency bins -> per-field F1 and ARI null arrays."""
    truth = np.asarray(truth); f1 = {f: np.zeros(nperm) for f in fields}; ari = np.zeros(nperm)
    groups = [np.where(bins == b)[0] for b in sorted(set(bins))]
    for k in range(nperm):
        t = truth.copy()
        for g in groups: t[g] = truth[rng.permutation(g)]
        s = field_f1(t, pred, fields)
        for f in fields: f1[f][k] = s[f]
        ari[k] = adjusted_rand_score(t, pred)
    return f1, ari


def score_draw(truth_map, fields_all, held_words, pred_held, cd, nperm, rng):
    """truth_map: word -> scored field (or absent). Returns per-field pass flags and ARI stats for one draw."""
    ws = [w for w in held_words if w in truth_map]
    idx = [held_words.index(w) for w in ws]
    truth = [truth_map[w] for w in ws]; pred = pred_held[idx]
    nheld = Counter(truth)
    fields = [f for f in fields_all if nheld[f] >= 3]
    keep = [i for i, t in enumerate(truth) if t in fields]
    truth = [truth[i] for i in keep]; pred = pred[keep]; ws = [ws[i] for i in keep]
    if len(fields) < 2:
        return dict(fields=fields, n=len(ws), f1={}, passed={}, ari=float("nan"), ari_p=float("nan"))
    obs = field_f1(truth, pred, fields); ari = adjusted_rand_score(truth, pred)
    nf1, nari = perm_null(truth, pred, fields, freq_bins(ws, cd), nperm, rng)
    passed = {f: bool(obs[f] >= 0.5 and obs[f] > np.percentile(nf1[f], 95)) for f in fields}
    return dict(fields=fields, n=len(ws), f1=obs, passed=passed, ari=float(ari),
                ari_p=float((1 + (nari >= ari).sum()) / (1 + nperm)))


def anchors_of(docs):
    return {v: {d["id"]: d[v] for d in docs} for v in ["site", "cls", "pic", "hand"]}


def run_rung(dev, held, rung, A, truth_map, fields_all, nperm, rng, supervised=False):
    """Blind clustering on all eligible words (k = scored fields + 1), held-out words -> nearest dev centroid."""
    el, sc, cd = eligible(dev, held)
    space = feature_space(dev, rung, A)
    P = profiles(dev, el, rung, A, space, dev)
    ch = Counter(truth_map[w] for w in sc if w in truth_map)
    k = sum(1 for f in fields_all if ch[f] >= 3) + 1
    lab = cluster(P, k)
    Q = profiles(held, sc, rung, A, space, dev)
    pred = assign(Q, P, lab)
    out = score_draw(truth_map, fields_all, sc, pred, cd, nperm, rng)
    out["k"] = k
    if supervised:
        out["supervised"] = supervised_control(el, P, truth_map, fields_all, cd, nperm, rng)
        out["pair_auc"] = pair_auc(el, P, truth_map)
    return out


def supervised_control(el, P, truth_map, fields_all, cd, nperm, rng):
    """leave-one-word-out nearest field centroid on dev; same null and recovered rule (fields with >= 3 words)."""
    ws = [w for w in el if w in truth_map]
    if not ws: return {}
    X = _unit(P[[el.index(w) for w in ws]]); t = np.array([truth_map[w] for w in ws])
    fields = [f for f in fields_all if (t == f).sum() >= 3]
    keep = np.isin(t, fields); X, t = X[keep], t[keep]; ws = [w for w, k in zip(ws, keep) if k]
    def predict(tt):
        pr = []
        for i in range(len(tt)):
            m = np.ones(len(tt), bool); m[i] = False
            best, bs = None, -9
            for f in fields:
                sel = m & (tt == f)
                if not sel.any(): continue
                c = X[sel].mean(0); c = c / (np.linalg.norm(c) or 1)
                s = float(X[i] @ c)
                if s > bs + 1e-12: best, bs = f, s
            pr.append(best)
        return np.array(pr)
    pred = predict(t)
    obs = {f: float(((pred == f) & (t == f)).sum() * 2 / max(1, (pred == f).sum() + (t == f).sum())) for f in fields}
    bins = freq_bins(ws, cd); groups = [np.where(bins == b)[0] for b in sorted(set(bins))]
    null = {f: [] for f in fields}
    for _ in range(nperm):
        tt = t.copy()
        for g in groups: tt[g] = t[rng.permutation(g)]
        pp = predict(tt)
        for f in fields:
            null[f].append(((pp == f) & (tt == f)).sum() * 2 / max(1, (pp == f).sum() + (tt == f).sum()))
    return dict(fields=fields, f1=obs, passed={f: bool(obs[f] >= 0.5 and obs[f] > np.percentile(null[f], 95)) for f in fields})


def pair_auc(el, P, truth_map):
    ws = [w for w in el if w in truth_map]
    X = _unit(P[[el.index(w) for w in ws]]); t = [truth_map[w] for w in ws]
    S = X @ X.T; same, diff = [], []
    for i in range(len(ws)):
        for j in range(i + 1, len(ws)):
            (same if t[i] == t[j] else diff).append(S[i, j])
    if not same or not diff: return float("nan")
    s = np.array(same); d = np.array(diff)
    return float(((s[:, None] > d[None, :]).sum() + 0.5 * (s[:, None] == d[None, :]).sum()) / (len(s) * len(d)))
