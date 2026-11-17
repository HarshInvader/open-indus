"""Shared code for the toponym (Jemdet Nasr city-seal) test.

Unit = distinct (site, medium, sign sequence). The same text at two sites, or on a
seal and a sealing at one site, counts twice; exact repeats (moulded tablets) once.
Run from repo root: .venv/bin/python experiments/toponyms/<script>.py
"""
import sys, json, random
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from corpus.load import icit_texts, m77_texts, runs, dev_heldout, distinct  # noqa

HERE = Path(__file__).resolve().parent
SEED = 20261114

# ---------------------------------------------------------------- media
def icit_medium(t):
    if t.startswith("SEAL"):
        return "seal"
    if t.startswith("TAG"):
        return "sealing"
    if t in ("TAB:B", "TAB:I"):
        return "tablet"
    if t == "TAB:C":
        return "copper"
    if t.startswith("POT") or t.startswith("POs"):
        return "pottery"
    return "other"


M77_MED = {"seal": "seal", "sealing": "sealing", "miniature tablet": "tablet",
           "copper tablet": "copper", "pottery graffito": "pottery"}


def m77_medium(t):
    return M77_MED.get(t, "other")


# mobile definitions (pre-registered): primary = clay sealings/tags only;
# broad = sealings + tablets + pottery (the media listed in the plan)
MOBILE = {"primary": {"sealing"}, "broad": {"sealing", "tablet", "pottery"}}

# Dholavira signboard (ICIT 144.1, gypsum, 3 m)
SIGNBOARD = ["W820", "W611", "W388", "W820", "W850", "W645", "W031", "W821", "W798"]


# ---------------------------------------------------------------- units
def icit_units():
    out, seen = [], set()
    for r in icit_texts():
        if r["site"] in ("Unknown", "-", ""):
            continue
        signs = [s for s in r["seq"] if s not in ("|", "#")]
        if not signs:
            continue
        med = icit_medium(r["type"])
        key = (r["site"], med, " ".join(r["seq"]))
        if key in seen:
            continue
        seen.add(key)
        out.append(dict(site=r["site"], region=r["region"], medium=med, type=r["type"],
                        seq=r["seq"], runs=runs(r["seq"]), id=r["id"]))
    return out


def m77_units(which):
    """which in {'dev','heldout'}: distinct (site, medium, seq) units drawn from the
    v2 family split (dev_heldout works on distinct seqs; we re-expand to all
    object records whose seq falls in the chosen half)."""
    dev, ho = dev_heldout(version=2)
    keep = {" ".join(t["seq"]) for t in (dev if which == "dev" else ho)}
    out, seen = [], set()
    for r in m77_texts():
        s = " ".join(r["seq"])
        if s not in keep:
            continue
        med = m77_medium(r["object_type"])
        key = (r["site"], med, s)
        if key in seen:
            continue
        seen.add(key)
        out.append(dict(site=r["site"], region=r["site"], medium=med, type=r["object_type"],
                        seq=r["seq"], runs=runs(r["seq"]), id=r["text_no"]))
    return out


# ---------------------------------------------------------------- families (ICIT split)
class UF:
    def __init__(self, n):
        self.p = list(range(n))

    def f(self, a):
        while self.p[a] != a:
            self.p[a] = self.p[self.p[a]]
            a = self.p[a]
        return a

    def u(self, a, b):
        a, b = self.f(a), self.f(b)
        if a != b:
            self.p[a] = b


def families(units, cont_min=3, edit_min=4):
    """Near-copy families, same rule as corpus/build.py splits_v2: identical sign string
    (any site/medium); <=1 edit with both texts >= edit_min signs; or a complete text of
    >= cont_min signs contained in another. '#' breaks are kept as tokens that match
    nothing, and texts with breaks never act as the contained/edited partner key."""
    flat = [tuple(s for s in u["seq"] if s != "|") for u in units]
    uf = UF(len(units))
    full, wild, dele = defaultdict(list), defaultdict(list), defaultdict(list)
    for i, f in enumerate(flat):
        full[f].append(i)
        if len(f) < edit_min or "#" in f:
            continue
        for k in range(len(f)):
            wild[f[:k] + ("_",) + f[k + 1:]].append(i)   # substitution
            dele[f[:k] + f[k + 1:]].append(i)            # deletion variant
    for d in (full, wild):
        for idx in d.values():
            for j in idx[1:]:
                uf.u(idx[0], j)
    for key, idx in dele.items():                        # indel: shorter == longer minus one
        if key in full and len(key) >= edit_min:
            for j in idx:
                uf.u(full[key][0], j)
    sub = defaultdict(list)
    for i, f in enumerate(flat):
        if len(f) >= cont_min and "#" not in f:
            sub[f].append(i)
    for i, f in enumerate(flat):
        L = len(f)
        for a in range(L):
            for b in range(a + cont_min, L + 1):
                if b - a == L:
                    continue
                for j in sub.get(f[a:b], ()):
                    uf.u(i, j)
    return [uf.f(i) for i in range(len(units))]


def icit_split():
    """Return dict half -> list of units ('A' discovery, 'B' confirmation)."""
    U = icit_units()
    fam = families(U, cont_min=4, edit_min=4)
    roots = sorted(set(fam))
    rng = random.Random(SEED)
    rng.shuffle(roots)
    half = {r: ("A" if k % 2 == 0 else "B") for k, r in enumerate(roots)}
    out = {"A": [], "B": []}
    for u, f in zip(U, fam):
        u["family"] = f
        out[half[f]].append(u)
    return out


# ---------------------------------------------------------------- features
def unit_features(u, orders=(1, 2, 3)):
    fs = set()
    for r in u["runs"]:
        for n in orders:
            for i in range(len(r) - n + 1):
                fs.add(" ".join(r[i:i + n]))
    return fs


def feature_matrix(units, min_units):
    F = [unit_features(u) for u in units]
    cnt = Counter(f for fs in F for f in fs)
    feats = sorted(f for f, c in cnt.items()
                   if c >= (min_units[len(f.split())] if isinstance(min_units, dict) else min_units))
    idx = {f: i for i, f in enumerate(feats)}
    X = np.zeros((len(units), len(feats)), dtype=np.int32)
    for r, fs in enumerate(F):
        for f in fs:
            if f in idx:
                X[r, idx[f]] = 1
    return feats, X


def labels(units, key):
    vals = sorted(set(u[key] for u in units))
    ix = {v: i for i, v in enumerate(vals)}
    return vals, np.array([ix[u[key]] for u in units])


def onehot(lab, k):
    M = np.zeros((len(lab), k), dtype=np.int32)
    M[np.arange(len(lab)), lab] = 1
    return M


def permute_within(lab, strata, rng):
    """Permute array lab within each stratum."""
    out = lab.copy()
    for s in np.unique(strata):
        ix = np.where(strata == s)[0]
        out[ix] = lab[rng.permutation(ix)]
    return out


# ---------------------------------------------------------------- enrichment
def enrichment(units, X, R=2000, seed=SEED):
    """Site enrichment of every feature. Null: site labels permuted within medium
    strata (preserves site x medium totals). Returns sites, obs, exp, p (one-sided)."""
    sites, slab = labels(units, "site")
    _, mlab = labels(units, "medium")
    S = onehot(slab, len(sites))
    obs = S.T @ X                                   # sites x feats
    # analytic expectation within medium strata
    exp = np.zeros(obs.shape, dtype=float)
    for m in np.unique(mlab):
        ix = mlab == m
        exp += np.outer(S[ix].sum(0), X[ix].sum(0)) / ix.sum()
    rng = np.random.default_rng(seed)
    ge = np.zeros(obs.shape, dtype=np.int32)
    Xf = X.astype(np.float32)
    for _ in range(R):
        sp = permute_within(slab, mlab, rng)
        Sp = onehot(sp, len(sites)).astype(np.float32)
        ge += (Sp.T @ Xf >= obs - 1e-9)
    p = (1 + ge) / (R + 1)
    return sites, obs, exp, p


def bh(p):
    p = np.asarray(p, float)
    n = len(p)
    o = np.argsort(p)
    q = np.empty(n)
    run = 1.0
    for k in range(n - 1, -1, -1):
        run = min(run, p[o[k]] * n / (k + 1))
        q[o[k]] = run
    return q


# ---------------------------------------------------------------- travel
def site_mobile_rate(units, mobile):
    tot, mob = Counter(), Counter()
    for u in units:
        tot[u["site"]] += 1
        mob[u["site"]] += u["medium"] in mobile
    return {s: mob[s] / tot[s] for s in tot}


def travel_components(units, cands, mob_vec, prate):
    """cands: list of (feature, home). mob_vec: 0/1 array per unit.
    Returns per-candidate dict with n_home, n_off, O_home, E_home, O_off, E_off."""
    out = []
    feats_of = [unit_features(u) for u in units]
    for f, h in cands:
        hi = [i for i, fs in enumerate(feats_of) if f in fs and units[i]["site"] == h]
        oi = [i for i, fs in enumerate(feats_of) if f in fs and units[i]["site"] != h]
        out.append(dict(feature=f, home=h, hi=hi, oi=oi,
                        E_home=sum(prate[units[i]["site"]] for i in hi),
                        E_off=sum(prate[units[i]["site"]] for i in oi)))
    return out


def travel_stats(comp, mob_vec):
    """S1 = pooled off-home mobile excess (O-E); S2 = pooled MH-weighted interaction
    (off-home excess rate minus home excess rate); also home seal share info."""
    S1 = S2 = 0.0
    Ooff = Eoff = Ohome = Ehome = 0.0
    for c in comp:
        no, nh = len(c["oi"]), len(c["hi"])
        oo = float(mob_vec[c["oi"]].sum()) if no else 0.0
        oh = float(mob_vec[c["hi"]].sum()) if nh else 0.0
        S1 += oo - c["E_off"]
        Ooff += oo; Eoff += c["E_off"]; Ohome += oh; Ehome += c["E_home"]
        if no and nh:
            w = no * nh / (no + nh)
            S2 += w * ((oo - c["E_off"]) / no - (oh - c["E_home"]) / nh)
    return dict(S1=S1, S2=S2, O_off=Ooff, E_off=Eoff, O_home=Ohome, E_home=Ehome)


def travel_test(units, cands, mobile, R=10000, seed=SEED):
    """Null A: medium labels permuted among units within site."""
    prate = site_mobile_rate(units, mobile)
    mob = np.array([u["medium"] in mobile for u in units], dtype=np.int8)
    _, slab = labels(units, "site")
    comp = travel_components(units, cands, mob, prate)
    obs = travel_stats(comp, mob)
    rng = np.random.default_rng(seed)
    null1, null2 = np.zeros(R), np.zeros(R)
    for k in range(R):
        mp = permute_within(mob, slab, rng)
        st = travel_stats(comp, mp)
        null1[k], null2[k] = st["S1"], st["S2"]
    obs["p_S1"] = float((1 + (null1 >= obs["S1"] - 1e-9).sum()) / (R + 1))
    obs["p_S2"] = float((1 + (null2 >= obs["S2"] - 1e-9).sum()) / (R + 1))
    obs["null_S1_mean"], obs["null_S1_95"] = float(null1.mean()), float(np.quantile(null1, 0.95))
    obs["null_S2_mean"], obs["null_S2_95"] = float(null2.mean()), float(np.quantile(null2, 0.95))
    obs["n_cands"] = len(cands)
    obs["n_off_tokens"] = int(sum(len(c["oi"]) for c in comp))
    obs["n_home_tokens"] = int(sum(len(c["hi"]) for c in comp))
    obs["per_cand"] = [dict(feature=c["feature"], home=c["home"], n_home=len(c["hi"]),
                            n_off=len(c["oi"]),
                            mob_home=int(mob[c["hi"]].sum()) if c["hi"] else 0,
                            E_home=round(c["E_home"], 2),
                            mob_off=int(mob[c["oi"]].sum()) if c["oi"] else 0,
                            E_off=round(c["E_off"], 2),
                            off_sites=dict(Counter(units[i]["site"] + ":" + units[i]["medium"] for i in c["oi"])))
                       for c in comp]
    return obs


def reverse_count(units, X, feats, min_seal=2):
    """# features whose seal units all lie at ONE site (>=min_seal) while >=1 sealing
    unit lies at another site and none at the seal site."""
    sites = np.array([u["site"] for u in units])
    med = np.array([u["medium"] for u in units])
    hits = []
    for j, f in enumerate(feats):
        ix = np.where(X[:, j] == 1)[0]
        ss = sites[ix][med[ix] == "seal"]
        gs = sites[ix][med[ix] == "sealing"]
        if len(ss) >= min_seal and len(set(ss)) == 1 and len(gs) >= 1 and ss[0] not in set(gs):
            hits.append((f, ss[0], sorted(set(gs))))
    return hits


def jdump(obj, path):
    def conv(o):
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        if isinstance(o, set):
            return sorted(o)
        raise TypeError(type(o))
    json.dump(obj, open(path, "w"), indent=1, default=conv)


# ---------------------------------------------------------------- collapsing near-copies
MED_PRI = ["seal", "sealing", "tablet", "pottery", "copper", "other"]


def ensure_families(units):
    if "family" not in units[0]:
        fam = families(units, cont_min=4, edit_min=4)
        for u, f in zip(units, fam):
            u["family"] = f
    return units


def collapse(units, level):
    """level 'enrich': one record per (site, family) [one seal and its impressions, or a
    run of moulded/near-copy tablets, count once per site]; medium = highest-priority
    medium present. level 'travel': one record per (site, medium, family).
    Each record carries the union of its members' sign runs."""
    ensure_families(units)
    groups = defaultdict(list)
    for u in units:
        k = (u["site"], u["family"]) if level == "enrich" else (u["site"], u["medium"], u["family"])
        groups[k].append(u)
    out = []
    for k, us in groups.items():
        meds = {u["medium"] for u in us}
        med = next(m for m in MED_PRI if m in meds)
        rr = []
        for u in us:
            rr.extend(u["runs"])
        out.append(dict(site=us[0]["site"], region=us[0]["region"], medium=med,
                        runs=rr, family=k[-1], n_members=len(us),
                        media=sorted(meds), seqs=[" ".join(u["seq"]) for u in us]))
    return out
