"""Genre detection floor at Indus size (board #43). Prereg: docs/prereg/genre_floor.md

Reuses the HMM mixture and formula (LCA) models of experiments/genres_scratch (read-only import).
Fix for near-copy chaining: families are built by LEADER clustering (no transitive chaining):
texts are visited longest-first; a text joins the first existing leader it is close to under the
same _close rule as splits_v2, else it becomes a leader. Every unit gets a 'fam' key, which
glib.families / family_split / family_folds / fam_boot_diff all honour.
"""
import math
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GS = ROOT / "experiments/genres_scratch"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(GS))
import gs  # noqa: E402
import data  # noqa: E402
from corpus.build import _close  # noqa: E402


# ------------------------------------------------------------------ families without chaining
def leader_families(units):
    order = sorted(range(len(units)), key=lambda i: (-len(units[i]["signs"]), " ".join(units[i]["signs"])))
    leaders_by_len = defaultdict(list)  # len -> [(unit index, fam id)]
    fam = [None] * len(units)
    nf = 0
    for i in order:
        s = list(units[i]["signs"])
        L = len(s)
        hit = None
        for Ll in sorted(leaders_by_len):
            if Ll < L or (Ll > L + 1 and L < 3):
                continue
            for j, f in leaders_by_len[Ll]:
                if _close(s, list(units[j]["signs"])):
                    hit = f; break
            if hit is not None:
                break
        if hit is None:
            hit = nf; nf += 1
            leaders_by_len[L].append((i, hit))
        fam[i] = hit
    for u, f in zip(units, fam):
        u["fam"] = f
    return fam


def chain_stats(units):
    """largest family under the old chaining rule vs leader rule"""
    old = Counter(gs.glib.families([{k: v for k, v in u.items() if k != "fam"} for u in units]))
    new = Counter(u["fam"] for u in units)
    return dict(n=len(units), old_max=max(old.values()), old_n=len(old), new_max=max(new.values()), new_n=len(new))


# ------------------------------------------------------------------ base corpora
def indus_pool():
    dev, ho = data.m77()
    us = dev + ho
    leader_families(us)
    return us


def cun_pool(seed):
    """Ur III seals (class A source) and other cuneiform genres (OB seal, tag, brick: class B source)"""
    import json
    rng = random.Random(seed)
    def load(f):
        out, seen = [], set()
        for l in open(ROOT / f"experiments/short_labels/data/{f}.jsonl"):
            s = [x for x in json.loads(l)["seq"] if x not in ("|", "#", "")]
            k = " ".join(s)
            if 1 <= len(s) <= 17 and k not in seen:
                seen.add(k); out.append(s)
        rng.shuffle(out)
        return out
    return load("cun_seal_ur3"), load("cun_seal_ob") + load("cun_tag") + load("cun_brick")


# ------------------------------------------------------------------ plants
def _subs(ranked, rng):
    m = {}
    for b in range(0, len(ranked), 5):
        blk = ranked[b:b + 5]
        if len(blk) < 2:
            m[blk[0]] = blk[0]; continue
        off = rng.randint(1, len(blk) - 1)
        for i, s in enumerate(blk):
            m[s] = blk[(i + off) % len(blk)]
    return m


def _labels_by_family(us, rng, share=0.30):
    fam = [u["fam"] for u in us]
    ids = sorted(set(fam)); rng.shuffle(ids)
    cnt = Counter(fam); quota = share * len(us); lab = {}
    for f in ids:
        if cnt[f] <= quota:
            lab[f] = 1; quota -= cnt[f]
        else:
            lab[f] = 0
    return [lab[f] for f in fam]


def plant_indus(kind, s, rep):
    """kind in VOC, FORM, LEN, MIX; s in [0,1]. Minority class (30%, by family) gets the edit."""
    base = indus_pool()
    rng = random.Random(f"{kind}-{s}-{rep}")
    allsig = Counter(x for u in base for x in u["signs"])
    ranked = [w for w, _ in allsig.most_common()]
    sub = _subs(ranked, rng)
    mid = ranked[20:80]
    openers = rng.sample(mid, 3); closers = rng.sample([w for w in mid if w not in openers], 3)
    y = _labels_by_family(base, rng)
    voc = kind in ("VOC", "MIX"); form = kind in ("FORM", "MIX"); ln = kind in ("LEN", "MIX")
    out = []
    for u, c in zip(base, y):
        runs = [(list(r), b, e) for r, b, e in u["runs"]]
        if c == 1:
            if voc:
                runs = [([sub[x] if rng.random() < s else x for x in r], b, e) for r, b, e in runs]
            if form:
                if runs[0][1] and rng.random() < s:
                    runs[0][0][0] = rng.choice(openers)
                if runs[-1][2] and rng.random() < s and len(runs[-1][0]) >= 2:
                    runs[-1][0][-1] = rng.choice(closers)
            if ln:
                for _ in range(2):
                    r = max(range(len(runs)), key=lambda i: len(runs[i][0]))
                    if len(runs[r][0]) >= 2 and rng.random() < s:
                        del runs[r][0][rng.randrange(len(runs[r][0]))]
        runs = [(tuple(r), b, e) for r, b, e in runs]
        out.append(dict(runs=runs, full=u["full"], signs=tuple(x for r, _, _ in runs for x in r), y=str(c),
                        fam=u["fam"]))
    return gs.family_split(out, 0.25, seed=rep)


def plant_cun(s, rep, total=2270, share=0.30):
    """dilution: class A = Ur III seals; class B = with prob s an OB-seal/tag/brick text, else Ur III seal"""
    A, B = cun_pool(rep)
    rng = random.Random(f"CUN-{s}-{rep}")
    nB = int(round(share * total)); nA = total - nB
    a_it, b_it = iter(A), iter(B)
    units = []
    for _ in range(nA):
        units.append(gs.glib.unit_from(next(a_it), True, y="0"))
    for _ in range(nB):
        src = b_it if rng.random() < s else a_it
        units.append(gs.glib.unit_from(next(src), True, y="1"))
    leader_families(units)
    return gs.family_split(units, 0.25, seed=rep)


def make(kind, s, rep):
    return plant_cun(s, rep) if kind == "CUN" else plant_indus(kind, s, rep)


# ------------------------------------------------------------------ supervised scale (same as genres_scratch/final.py)
def lr_gain(tr, te, yd, yh):
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.linear_model import LogisticRegressionCV
    cv = CountVectorizer(analyzer=lambda u: gs.LDA.doc(u) + [f"^{u['runs'][0][0][0]}", f"{u['runs'][-1][0][-1]}$",
                                                           f"len{min(len(u['signs']), 7)}"], min_df=2)
    Xd = cv.fit_transform(tr); Xh = cv.transform(te)
    m = LogisticRegressionCV(Cs=[0.01, 0.03, 0.1, 0.3, 1, 3], cv=3, max_iter=2000, n_jobs=1).fit(Xd, yd)
    P = m.predict_proba(Xh); cls = list(m.classes_)
    base = Counter(yd); L = len(set(yd) | set(yh))
    g = [math.log2(max(P[i, cls.index(y)], 1e-6)) - math.log2((base[y] + .5) / (len(yd) + .5 * L))
         for i, y in enumerate(yh)]
    return float(np.mean(g))


# ------------------------------------------------------------------ detection (prereg rule)
KS = [1, 2, 3, 4]


def detect(name, tr, te, rep):
    sys.path.insert(0, str(GS))
    import run_main
    res = gs.cv_curve(name, tr, KS, folds=3, seed=rep, restarts=1 if name == "HMM" else 2)
    K, means, best = gs.pick_K(res)
    out = dict(K=int(K))
    if K < 2:
        out.update(S1=False, p=1.0, det=False)
        return out
    m = gs.MODELS[name]().fit(tr, K, seed=rep, restarts=1 if name == "HMM" else 2)
    m1 = gs.MODELS[name]().fit(tr, 1, seed=rep, restarts=1)
    d = m.loglik(te) - m1.loglik(te)
    ci = run_main.fam_boot_diff(te, d, n=300)
    gd, gh = m.assign(tr), m.assign(te)
    r = gs.assoc_test(gd, [u["y"] for u in tr], gh, [u["y"] for u in te], K, nperm=500, seed=rep)
    out.update(ci=ci, S1=bool(ci[0] > 0), p=r["p"], G=r["G"], ari=gs.ari(gh, [u["y"] for u in te]))
    out["det"] = bool(out["S1"] and r["p"] < 0.05)
    return out
