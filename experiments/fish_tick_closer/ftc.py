"""fish_tick_closer: is the corner tick on a fish sign a closer drawn inside the sign?
Prereg: docs/prereg/fish_tick_closer.md. Library used by run.py.
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "corpus"))
import load as L  # noqa: E402

BASES_M = [("M59", "M60"), ("M65", "M66"), ("M67", "M68"), ("M70", "M71"), ("M72", "M73")]
BASES_W = [("W220", "W226"), ("W235", "W236"), ("W240", "W241"), ("W231", "W232"), ("W233", "W234")]
CLOSER_M = {"M342", "M211", "M15", "M254", "M12", "M14", "M388"}
POSTCLOSER_M = {"M176", "M1", "M242", "M139", "M224", "M93", "M374"}
POST1977 = {"Dholavira", "Nausharo", "Banawali", "Rakhigarhi", "Farmana", "Bhirrana", "Gola Dhoro (Bagasra)",
            "Karanpura", "Khirsara", "Kanmer", "Shikarpur", "Lakhanjo-daro", "Tarkhanewala-dera", "Naru-Waro-dharo"}
BINS = [2, 3, 4, 5, 6, 7]  # 7 = 7+


def m_to_w(ms):
    b = json.load(open(ROOT / "sources/shaunmortal_indus/data/bridge_WM.json"))
    nums = {int(m[1:]) for m in ms}
    return {"W%03d" % int(w) for w, v in b.items() if set(v["M"]) & nums}


class Scheme:
    def __init__(self, wells):
        self.bases = BASES_W if wells else BASES_M
        self.closers = m_to_w(CLOSER_M) if wells else set(CLOSER_M)
        self.post = m_to_w(POSTCLOSER_M) if wells else set(POSTCLOSER_M)
        self.plain = {p for p, _ in self.bases}
        self.tick = {t for _, t in self.bases}
        self.fish = self.plain | self.tick


# ---------- near-copy collapse (rule copied from corpus/build.py::_close) ----------
def _close(a, b):
    if len(a) > len(b):
        a, b = b, a
    la, lb = len(a), len(b)
    if la >= 3 and lb - la >= 1:
        for i in range(lb - la + 1):
            if b[i:i + la] == a:
                return True
    if lb - la > 1 or la < 4:
        return False
    if la == lb:
        return sum(x != y for x, y in zip(a, b)) <= 1
    i = 0
    while i < la and a[i] == b[i]:
        i += 1
    return a[i:] == b[i + 1:]


def collapse(texts):
    texts = L.distinct(texts)
    sg = [[s for s in t["seq"] if s not in ("|", "#")] for t in texts]
    n = len(texts)
    par = list(range(n))

    def find(x):
        while par[x] != x:
            par[x] = par[par[x]]; x = par[x]
        return x
    for i in range(n):
        for j in range(i + 1, n):
            if sg[i] and sg[j] and _close(sg[i], sg[j]):
                par[find(i)] = find(j)
    fam = defaultdict(list)
    for i in range(n):
        fam[find(i)].append(i)
    keep = []
    for ids in fam.values():
        best = min(ids, key=lambda i: (-len(sg[i]), " ".join(texts[i]["seq"])))
        keep.append(texts[best])
    keep.sort(key=lambda t: " ".join(t["seq"]))
    return keep


def prep(texts):
    """Flatten line breaks; keep '#'. Record single-line flag."""
    out = []
    for t in texts:
        seq = [s for s in t["seq"] if s != "|"]
        if not seq:
            continue
        out.append(dict(seq=seq, single="|" not in t["seq"], complete=bool(t["complete"])))
    return out


def load_sets(collapse_near=True):
    dev, ho = L.dev_heldout(version=2)
    new = [t for t in L.icit_texts() if t["site"] in POST1977]
    f = collapse if collapse_near else L.distinct
    return {"DEV": (prep(f(dev)), Scheme(False)), "HELD": (prep(f(ho)), Scheme(False)),
            "NEW": (prep(f(new)), Scheme(True))}


# ---------- P1 ----------
def p1_tokens(texts, sch, tick_override=None, strata=False, drop_start=False):
    """Per base: list of A contexts, plain tokens [(context, is_B, lenbin)]."""
    ticks = tick_override or [t for _, t in sch.bases]
    res = []
    for (p, _), tk in zip(sch.bases, ticks):
        A, P = [], []
        for t in texts:
            s = t["seq"]; n = len(s)
            nb = min(sum(x != "#" for x in s), 7)
            for i, x in enumerate(s):
                if x != tk and x != p:
                    continue
                ctx = "<S>" if i == 0 else s[i - 1]
                if ctx == "#" or (drop_start and ctx == "<S>"):
                    continue
                if x == tk:
                    A.append(ctx)
                else:
                    if i + 1 < n:
                        nx = s[i + 1]
                        if nx == "#":
                            continue
                        P.append((ctx, nx in sch.closers, nb))
                    elif t["complete"]:
                        P.append((ctx, False, nb))
        res.append((A, P))
    return res


def _jsd_rows(Pm, q):
    """JS distance between each row of Pm (R x V, distributions) and vector q (V)."""
    M = 0.5 * (Pm + q)
    with np.errstate(divide="ignore", invalid="ignore"):
        a = np.where(Pm > 0, Pm * np.log2(Pm / M), 0.0).sum(1)
        b = np.where(q > 0, q * np.log2(q / M), 0.0).sum(1)
    return np.sqrt(np.clip(0.5 * a + 0.5 * b, 0, None))


def base_delta(A, P, R, rng, strata=False):
    """Observed Delta and permutation deltas (R). Returns None if untestable."""
    nA, nB = len(A), sum(b for _, b, _ in P)
    nD = len(P) - nB
    if nA < 3 or nB < 3 or nD < 3:
        return None
    voc = {c: i for i, c in enumerate(sorted(set(A) | {c for c, _, _ in P}))}
    V = len(voc)
    a = np.bincount([voc[c] for c in A], minlength=V).astype(float); a /= a.sum()
    ctx = np.array([voc[c] for c, _, _ in P]); lab = np.array([b for _, b, _ in P], bool)
    oh = np.zeros((len(P), V)); oh[np.arange(len(P)), ctx] = 1
    tot = oh.sum(0)

    def deltas(L_):  # L_: (k x nP) bool
        Bc = L_.astype(float) @ oh; Dc = tot - Bc
        Bd = Bc / Bc.sum(1, keepdims=True); Dd = Dc / Dc.sum(1, keepdims=True)
        return _jsd_rows(Dd, a) - _jsd_rows(Bd, a)
    obs = float(deltas(lab[None, :])[0])
    if R == 0:
        return obs, None
    perm = np.empty((R, len(P)), bool)
    if strata:
        bins = np.array([b for _, _, b in P])
        for r in range(R):
            l2 = lab.copy()
            for bb in np.unique(bins):
                idx = np.where(bins == bb)[0]
                l2[idx] = rng.permutation(lab[idx])
            perm[r] = l2
    else:
        for r in range(R):
            perm[r] = rng.permutation(lab)
    out = []
    for k in range(0, R, 2000):
        out.append(deltas(perm[k:k + 2000]))
    return obs, np.concatenate(out)


def p1(texts, sch, R, rng, tick_override=None, strata=False, drop_start=False):
    toks = p1_tokens(texts, sch, tick_override, drop_start=drop_start)
    per, obs_sum, null_sum, ntest = [], 0.0, np.zeros(R), 0
    for (p, t), (A, P) in zip(sch.bases, toks):
        nB = sum(b for _, b, _ in P)
        rec = dict(base=p, tick=(tick_override[sch.bases.index((p, t))] if tick_override else t),
                   nA=len(A), nB=nB, nD=len(P) - nB)
        d = base_delta(A, P, R, rng, strata)
        if d is None:
            rec.update(testable=False)
        else:
            o, nl = d
            rec.update(testable=True, delta=o, p=float((1 + (nl >= o).sum()) / (1 + R)), null_mean=float(nl.mean()))
            obs_sum += o; null_sum += nl; ntest += 1
        per.append(rec)
    pooled = dict(n_testable=ntest, delta_sum=obs_sum,
                  p=(float((1 + (null_sum >= obs_sum).sum()) / (1 + R)) if ntest else None))
    npass = sum(1 for r in per if r.get("testable") and r["delta"] > 0 and r["p"] < 0.01)
    return dict(bases=per, n_pass_001=npass, pooled=pooled)


def p1_obs_sum(texts, sch, drop_start=False):
    s, n = 0.0, 0
    for A, P in p1_tokens(texts, sch, drop_start=drop_start):
        d = base_delta(A, P, 0, None)
        if d is not None:
            s += d[0]; n += 1
    return s, n


# ---------- P2 ----------
def p2_texts(texts):
    return [t for t in texts if t["single"] and t["complete"] and "#" not in t["seq"] and len(t["seq"]) >= 2]


def _bin(n):
    return min(n, 7)


def p2(texts, sch, rng, draws=100000, tickset=None, pool="primary"):
    ts = p2_texts(texts)
    tickset = tickset or sch.tick
    target = [t for t in ts if t["seq"][-1] in tickset]
    k = sum(1 for t in target if not (set(t["seq"][:-1]) & sch.closers))
    if pool == "plainfish":
        ref = [t for t in ts if t["seq"][-1] in sch.plain]
    else:
        ref = [t for t in ts if t["seq"][-1] not in sch.closers and t["seq"][-1] not in sch.fish
               and t["seq"][-1] not in tickset]
        if pool == "nopost":
            ref = [t for t in ref if t["seq"][-1] not in sch.post]
    cf = [t for t in ts if t["seq"][-1] in sch.closers]
    cf_rate = (sum(1 for t in cf if not (set(t["seq"][:-1]) & sch.closers)) / len(cf)) if cf else None
    out = dict(n_target=len(target), k_no_other_closer=k, share=(k / len(target) if target else None),
               n_ref=len(ref), closer_final_no_second=cf_rate, n_closer_final=len(cf))
    if not target or len(ref) < 5:
        out.update(testable=False, p=None)
        return out
    byb = defaultdict(list)
    for t in ref:
        byb[_bin(len(t["seq"]))].append(not (set(t["seq"][:-1]) & sch.closers))

    def rate(b):
        got, order = list(byb.get(b, [])), [b]
        cand = [x for x in range(b - 1, 1, -1)] + [x for x in range(b + 1, 8)]
        for c in cand:
            if len(got) >= 5:
                break
            got += byb.get(c, []); order.append(c)
        return float(np.mean(got))
    rs = np.array([rate(_bin(len(t["seq"]))) for t in target])
    null = (rng.random((draws, len(rs))) < rs).sum(1)
    out.update(testable=True, expected=float(rs.sum()), null_share=float(rs.mean()),
               p=float((1 + (null >= k).sum()) / (1 + draws)))
    return out


# ---------- planting ----------
def plant(texts, sch, frac, rng, false_alarm=False):
    """Return (planted texts, list of X sign names per base)."""
    texts = [dict(t, seq=list(t["seq"])) for t in texts]
    X = []
    edits = []
    for bi, (p, _) in enumerate(sch.bases):
        x = "X%d" % bi; X.append(x)
        pairs, plain = [], []
        for ti, t in enumerate(texts):
            s = t["seq"]
            for i, y in enumerate(s):
                if y != p:
                    continue
                if i > 0 and s[i - 1] == "#":
                    continue
                plain.append((ti, i))
                if i + 1 < len(s) and s[i + 1] in sch.closers:
                    pairs.append((ti, i))
        m = int(np.floor(frac * len(pairs) + 0.5))
        src = plain if false_alarm else pairs
        if m == 0 or not src:
            continue
        pick = rng.choice(len(src), size=min(m, len(src)), replace=False)
        for j in pick:
            ti, i = src[j]
            edits.append((ti, i, x, (not false_alarm)))
    # apply deletions from the right so indices stay valid
    for ti, i, x, merge in sorted(edits, key=lambda e: (e[0], -e[1])):
        s = texts[ti]["seq"]
        s[i] = x
        if merge:
            del s[i + 1]
    return texts, X
