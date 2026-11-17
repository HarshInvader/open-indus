"""One-to-many substitution (Maya method): shared code.

An *event* is a pair of distinct texts in which one sign X in text A stands where a
2- or 3-sign string Y in text B stands, with matching flanks on both sides:
    A = ... L X R ...      B = ... L Y R ...
Flanks are taken from texts padded with edge markers (^ ^ ... $ $):
  * tier "W" (whole-text frame): A and B are identical outside X/Y, with >=2 real
    context signs in total (for k=2 this is internal_phonetics' T3 event set);
  * tier "L" (local frame): left flank of 2 tokens and right flank of 1, or 1 and 2,
    edges allowed as tokens, >=2 real signs among the 3 flank tokens. W is a subset of L.
X must not occur inside Y (that would be a plain insertion, already covered by the
phonetic-complement test in internal_phonetics).

Support of an equation X=Y = number of INDEPENDENT frames: events of the same
equation are merged (union-find) when they share a text or the same 2+2 local
context. Distinct texts only, always.
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import poisson

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from corpus.load import dev_heldout, distinct, icit_texts, m77_texts  # noqa: E402

OUT = Path(__file__).resolve().parent
M77_SITES_ICIT = {"Mohenjo-daro", "Harappa", "Chanhu-daro", "Lothal", "Kalibangan"}


def clean(seq):
    if "#" in seq:
        return None
    t = tuple(x for x in seq if x != "|")
    return t or None


def load_m77():
    dev, ho = dev_heldout(version=2)
    D = sorted({c for t in dev if (c := clean(t["seq"]))})
    H = sorted({c for t in ho if (c := clean(t["seq"]))} - set(D))
    return D, H


def load_icit(new_sites_only=False):
    out = set()
    for t in distinct(icit_texts()):
        if new_sites_only and t["site"] in M77_SITES_ICIT:
            continue
        c = clean(t["seq"])
        if c:
            out.add(c)
    return sorted(out)


def save_results(key, obj):
    p = OUT / "results.json"
    d = json.load(open(p)) if p.exists() else {}
    d[key] = obj
    json.dump(d, open(p, "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))


def bh(pvals):
    p = np.asarray(pvals, float); n = len(p)
    if n == 0:
        return p
    o = np.argsort(p); q = np.empty(n); run = 1.0
    for r, i in enumerate(o[::-1]):
        k = n - r
        run = min(run, p[i] * n / k); q[i] = run
    return q


def poscls(i, n):
    return "I" if i == 0 else ("F" if i == n - 1 else "M")


EDGE = ("^", "$")


# ------------------------------------------------------------------ mining
def mine(texts, ks=(2, 3), tier="L"):
    """Return list of events: dict(X, Y, k, pos, ctx, a, b) where ctx is the 2+2
    local context (padded), a/b are text indices (A has X, B has Y)."""
    texts = list(texts)
    pad = [("^", "^") + t + ("$", "$") for t in texts]
    ev = {}
    if tier == "W":
        key = defaultdict(list)
        for ti, t in enumerate(texts):
            for k in ks:
                for i in range(len(t) - k + 1):
                    key[(t[:i], t[i + k:])].append((ti, i, k))
        for ai, u in enumerate(texts):
            for j in range(len(u)):
                L, R = u[:j], u[j + 1:]
                if len(L) + len(R) < 2:
                    continue
                for bi, i, k in key.get((L, R), []):
                    X, Y = u[j], texts[bi][i:i + k]
                    if X in Y:
                        continue
                    pu = pad[ai]
                    ctx = (pu[j:j + 2], pu[j + 3:j + 5])
                    e = (X, Y, ai, bi)
                    ev[e] = dict(X=X, Y=Y, k=k, pos=poscls(j, len(u)), ctx=ctx, a=ai, b=bi)
        return list(ev.values())
    # local tier
    keyY = defaultdict(list)
    for ti, p in enumerate(pad):
        for k in ks:
            for i in range(2, len(p) - 2 - k + 1):
                if p[i] in EDGE or p[i + k - 1] in EDGE:
                    continue
                for l, r in ((2, 1), (1, 2)):
                    L, R = p[i - l:i], p[i + k:i + k + r]
                    if sum(x not in EDGE for x in L + R) < 2:
                        continue
                    keyY[(l, L, R)].append((ti, i, k))
    for ai, p in enumerate(pad):
        n = len(p) - 4
        for j in range(2, len(p) - 2):
            for l, r in ((2, 1), (1, 2)):
                L, R = p[j - l:j], p[j + 1:j + 1 + r]
                if sum(x not in EDGE for x in L + R) < 2:
                    continue
                for bi, i, k in keyY.get((l, L, R), []):
                    if bi == ai:
                        continue
                    X, Y = p[j], pad[bi][i:i + k]
                    if X in Y:
                        continue
                    e = (X, Y, ai, bi)
                    if e not in ev:
                        ev[e] = dict(X=X, Y=Y, k=k, pos=poscls(j - 2, n), ctx=(p[j - 2:j], p[j + 1:j + 3]),
                                     a=ai, b=bi)
    return list(ev.values())


class UF:
    def __init__(self):
        self.p = {}

    def f(self, x):
        self.p.setdefault(x, x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]; x = self.p[x]
        return x

    def u(self, a, b):
        self.p[self.f(a)] = self.f(b)


def to_units(events):
    """Collapse events into frame units: one unit per (equation, independent frame).
    Events of one equation are merged when they share a text or a 2+2 context."""
    g = defaultdict(list)
    for e in events:
        g[(e["X"], e["Y"])].append(e)
    units = []
    for (X, Y), evs in g.items():
        uf = UF()
        for i, e in enumerate(evs):
            uf.f(i); uf.u(i, ("t", e["a"])); uf.u(i, ("t", e["b"])); uf.u(i, ("c", e["ctx"]))
        comp = defaultdict(list)
        for i in range(len(evs)):
            comp[uf.f(i)].append(evs[i])
        for es in comp.values():
            units.append(dict(X=X, Y=Y, k=len(Y), pos=Counter(e["pos"] for e in es).most_common(1)[0][0],
                              texts=frozenset(t for e in es for t in (e["a"], e["b"])),
                              ctxs=frozenset(e["ctx"] for e in es)))
    return units


def eq_support(units):
    """Support (independent frames) of every equation among units."""
    g = defaultdict(list)
    for u in units:
        g[(u["X"], u["Y"])].append(u)
    eqs = {}
    for key, us in g.items():
        if len(us) == 1:
            eqs[key] = 1; continue
        uf = UF()
        for i, u in enumerate(us):
            uf.f(i)
            for t in u["texts"]:
                uf.u(i, ("t", t))
            for c in u["ctxs"]:
                uf.u(i, ("c", c))
        eqs[key] = len({uf.f(i) for i in range(len(us))})
    return eqs


def system_score(eqs, kmin=2):
    """Shared-syllable score among recurrent equations (support>=kmin):
    S = number of signs that occur on the spelling side of >=2 recurrent equations
    with different X; P = number of unordered pairs of recurrent equations (different X)
    sharing a spelling sign in the same position."""
    rec = [(x, y) for (x, y), k in eqs.items() if k >= kmin]
    usex = defaultdict(set)
    bypos = defaultdict(set)
    for x, y in rec:
        for i, s in enumerate(y):
            usex[s].add(x)
            bypos[(i, len(y), s)].add(x)
    S = sum(1 for s, xs in usex.items() if len(xs) >= 2)
    P = sum(len(xs) * (len(xs) - 1) // 2 for xs in bypos.values())
    return S, P


def stats(units, kmin=2):
    eqs = eq_support(units)
    G = sum(1 for k in eqs.values() if k >= kmin)
    S, P = system_score(eqs, kmin)
    return dict(n_units=len(units), n_eq=len(eqs), G=G, S=S, P=P,
                kmax=max(eqs.values()) if eqs else 0), eqs


def stratum(u, strat):
    if strat == "pos":
        return (u["pos"], u["k"])
    c = min(u["ctxs"])
    if strat == "left":
        return (u["k"], c[0][-1])
    if strat == "flank":
        return (u["k"], c[0][-1], c[1][0])
    raise ValueError(strat)


def perm_null(units, nperm=500, seed=0, kmin=2, eq_track=None, strat="pos"):
    """Frame-matched null: permute the replacing strings Y among frame units within
    strata (slot I/M/F, k). Keeps every frame, the X marginal and the Y marginal; only
    the pairing of X with Y is randomised."""
    rng = np.random.default_rng(seed)
    strata = defaultdict(list)
    for i, u in enumerate(units):
        strata[stratum(u, strat)].append(i)
    Ys = [u["Y"] for u in units]
    out = {"G": [], "S": [], "P": [], "kmax": []}
    lam = Counter(); ge = Counter()
    track = eq_track or {}
    for _ in range(nperm):
        newY = list(Ys)
        for idx in strata.values():
            perm = rng.permutation(len(idx))
            for a, b in zip(idx, perm):
                newY[a] = Ys[idx[b]]
        un = [dict(u, Y=newY[i]) for i, u in enumerate(units)]
        st, eqs = stats(un, kmin)
        for kk in out:
            out[kk].append(st[kk])
        for key, kobs in track.items():
            kn = eqs.get(key, 0)
            lam[key] += kn
            if kn >= kobs:
                ge[key] += 1
    res = {kk: np.array(v) for kk, v in out.items()}
    eqp = {}
    for key, kobs in track.items():
        l = lam[key] / nperm
        eqp[key] = dict(lam=l, p_emp=(ge[key] + 1) / (nperm + 1),
                        p=max(float(poisson.sf(kobs - 1, max(l, 1e-3))), 1e-12))
    return res, eqp


def analyse(texts, nperm=500, seed=0, kmin=2, tier="L", ks=(2, 3), track_top=True, strat="pos"):
    ev = mine(texts, ks=ks, tier=tier)
    units = to_units(ev)
    st, eqs = stats(units, kmin)
    st["n_events"] = len(ev)
    track = {k: v for k, v in eqs.items() if v >= kmin} if track_top else None
    null, eqp = perm_null(units, nperm, seed, kmin, track, strat)
    out = dict(st)
    for kk in ("G", "S", "P", "kmax"):
        out[kk + "_null_mean"] = float(null[kk].mean())
        out[kk + "_null_sd"] = float(null[kk].std())
        out["p_" + kk] = float((1 + (null[kk] >= st[kk]).sum()) / (1 + nperm))
    items = []
    if track_top:
        keys = list(eqp)
        q = bh([eqp[k]["p"] for k in keys])
        for key, qq in zip(keys, q):
            items.append(dict(X=key[0], Y=" ".join(key[1]), k=eqs[key], lam=eqp[key]["lam"],
                              p=eqp[key]["p"], p_emp=eqp[key]["p_emp"], q=float(qq)))
        items.sort(key=lambda r: (r["p"], -r["k"]))
    out["n_sig_q05"] = sum(1 for r in items if r["q"] < 0.05)
    return out, items, ev, units, eqs


# ================================================================ frame co-fill design
def frames_2x2(texts, ks=(2, 3), minreal=2):
    """Frames = exact 2+2 local contexts (edges ^/$ allowed as tokens, >=minreal real
    signs among the 4). For each frame: the set of single-sign fillers F1 and of
    2-3-sign fillers F2, each filler with the set of texts it comes from."""
    F1 = defaultdict(lambda: defaultdict(set)); F2 = defaultdict(lambda: defaultdict(set))
    for ti, t in enumerate(texts):
        p = ("^", "^") + tuple(t) + ("$", "$")
        for k in (1,) + tuple(ks):
            for i in range(2, len(p) - 2 - k + 1):
                fill = p[i:i + k]
                if any(x in EDGE for x in fill):
                    continue
                c = (p[i - 2:i], p[i + k:i + k + 2])
                if sum(x not in EDGE for x in c[0] + c[1]) < minreal:
                    continue
                (F1 if k == 1 else F2)[c][fill[0] if k == 1 else fill].add(ti)
    out = []
    for c in F1:
        if c in F2:
            out.append((c, dict(F1[c]), dict(F2[c])))
    return out


def fslot(c):
    l, r = c
    return ("I" if l[-1] == "^" else "M") + ("F" if r[0] == "$" else "M")


def cofill_counts(frs):
    """k(X,Y) = number of distinct frames in which X and Y both fill, with the X-text
    and Y-text different and X not inside Y. Also returns example frames."""
    cnt = Counter(); ex = defaultdict(list)
    for c, f1, f2 in frs:
        for X, tx in f1.items():
            for Y, ty in f2.items():
                if X in Y:
                    continue
                if tx | ty and not (len(tx) == 1 and tx == ty):
                    cnt[(X, Y)] += 1
                    if len(ex[(X, Y)]) < 4:
                        ex[(X, Y)].append((c, sorted(tx)[:2], sorted(ty)[:2]))
    return cnt, ex


def cofill_analyse(texts, nperm=300, seed=0, kmin=2, ks=(2, 3)):
    """Null: permute the F2 filler sets among frames of the same slot class (I/M x M/F),
    keeping every frame's F1 set and every Y's number of frames (degree)."""
    rng = np.random.default_rng(seed)
    frs = frames_2x2(texts, ks)
    obs, ex = cofill_counts(frs)
    G = sum(1 for v in obs.values() if v >= kmin)
    S, P = system_score(obs, kmin)
    strata = defaultdict(list)
    for i, (c, _, _) in enumerate(frs):
        strata[fslot(c)].append(i)
    tested = [k for k, v in obs.items() if v >= kmin]
    lam = Counter(); ge = Counter(); nG = []; nS = []; nP = []
    for _ in range(nperm):
        f2s = [f2 for _, _, f2 in frs]
        for idx in strata.values():
            perm = rng.permutation(len(idx))
            vals = [f2s[idx[j]] for j in perm]
            for a, v in zip(idx, vals):
                f2s[a] = v
        frn = [(c, f1, f2s[i]) for i, (c, f1, _) in enumerate(frs)]
        cn, _ = cofill_counts(frn)
        nG.append(sum(1 for v in cn.values() if v >= kmin))
        s_, p_ = system_score(cn, kmin); nS.append(s_); nP.append(p_)
        for key in tested:
            v = cn.get(key, 0); lam[key] += v
            if v >= obs[key]:
                ge[key] += 1
    items = []
    for key in tested:
        l = lam[key] / nperm
        items.append(dict(X=key[0], Y=" ".join(key[1]), k=obs[key], lam=l,
                          p=max(float(poisson.sf(obs[key] - 1, max(l, 1e-3))), 1e-12),
                          p_emp=(ge[key] + 1) / (nperm + 1), ex=ex[key]))
    q = bh([r["p"] for r in items])
    for r, qq in zip(items, q):
        r["q"] = float(qq)
    items.sort(key=lambda r: (r["p"], -r["k"]))
    nG, nS, nP = map(np.array, (nG, nS, nP))
    out = dict(n_frames=len(frs), n_pairs=len(obs), G=G, S=S, P=P,
               G_null_mean=float(nG.mean()), G_null_sd=float(nG.std()), p_G=float((1 + (nG >= G).sum()) / (1 + nperm)),
               S_null_mean=float(nS.mean()), S_null_sd=float(nS.std()), p_S=float((1 + (nS >= S).sum()) / (1 + nperm)),
               P_null_mean=float(nP.mean()), p_P=float((1 + (nP >= P).sum()) / (1 + nperm)),
               n_sig_q05=sum(1 for r in items if r["q"] < 0.05))
    return out, items, obs


# ================================================================ system-consistent equations
def paradigm_partners(texts):
    """1<->1 substitution partners: signs that fill the same exact 2+2 frame (>=2 real
    context signs) as single-sign fillers in different texts."""
    frs = frames_2x2(texts, ks=())
    # frames_2x2 only keeps frames with F2; rebuild F1-only frames here
    F1 = defaultdict(set)
    for ti, t in enumerate(texts):
        p = ("^", "^") + tuple(t) + ("$", "$")
        for i in range(2, len(p) - 2):
            c = (p[i - 2:i], p[i + 1:i + 3])
            if sum(x not in EDGE for x in c[0] + c[1]) >= 2:
                F1[c].add(p[i])
    part = defaultdict(set)
    for c, xs in F1.items():
        if len(xs) > 1:
            for x in xs:
                part[x] |= xs - {x}
    return part


def sce_filter(items, part, alpha=0.05):
    """System-consistent equations: q < alpha, and no sign of the spelling Y is X itself
    or a 1<->1 paradigm partner of X (a syllabic spelling is written with signs from a
    different set than the word signs it replaces; paradigm alternations such as
    fish <-> fish+fish fail this)."""
    out = []
    for r in items:
        if r["q"] >= alpha:
            continue
        Y = r["Y"].split()
        if any(y == r["X"] or y in part.get(r["X"], ()) for y in Y):
            continue
        out.append(r)
    return out


def sce_system(sces):
    """Spelling signs shared by >=2 SCEs with different X (the 'shared syllables')."""
    use = defaultdict(set)
    for r in sces:
        for s in set(r["Y"].split()):
            use[s].add(r["X"])
    shared = {s: xs for s, xs in use.items() if len(xs) >= 2}
    n_in_sys = sum(1 for r in sces if any(s in shared for s in r["Y"].split()))
    return len(shared), n_in_sys, shared
