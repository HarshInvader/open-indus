"""Independent red-team reimplementation of half_life P3 (relative chronology at Harappa).
Written without reading experiments/half_life code. Run from repo root.

Unit = distinct (dataset, period, coarse object type, sequence). Per-sign shift = mean over the
sign's units of (relative period - mean relative period of units of the same stratum), where the
stratum is the object type (optionally x area / x length bin). Null = relative periods permuted
within stratum.
"""
import csv, json, re, sys
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from corpus.load import m77_lines, icit_texts, runs  # noqa

BR = json.load(open(ROOT / "sources/shaunmortal_indus/data/bridge_WM.json"))
W2M = {"W%03d" % int(k): "M%d" % v["M"][0] for k, v in BR.items() if v.get("M")}

RAW = list(csv.DictReader(open(ROOT / "sources/field-cady_indus_valley_script_corpus/inscriptions.csv")))
ICIT = icit_texts()
assert len(RAW) == len(ICIT) and all(a["id"] == b["id"] for a, b in zip(RAW, ICIT))


def bridge(seq):
    """ICIT seq -> M signs; unbridged W signs kept as W (no shared identity with M77)."""
    return [W2M.get(s, s) if s not in ("|", "#") else s for s in seq]


def icit_type(t):
    t = t.upper()
    if t.startswith("TAB:B"): return "tab_moulded"
    if t.startswith("TAB:I"): return "tab_incised"
    if t.startswith("TAB"): return "tablet"
    if t.startswith("SEAL"): return "seal"
    if t.startswith("POT") or t.startswith("POST"): return "pot"
    if t.startswith("TAG"): return "sealing"
    return "other"


def icit_shape(t):
    """finer object type for seals (SEAL:S square, SEAL:R rectangular...)"""
    return t.upper()


def m77_type(o):
    return {"miniature tablet": "tablet", "seal": "seal", "sealing": "sealing",
            "pottery graffito": "pot", "copper tablet": "copper"}.get(o, "other")


def coarse(t):
    """tablet types merged (to compare across ICIT / M77)."""
    return "tablet" if t.startswith("tab") else t


def signs_of(seq):
    return [s for s in seq if s not in ("|", "#")]


def depth_ft(s):
    m = re.match(r"\s*(-?\d+(?:\.\d+)?)\s*ft", s or "")
    return float(m.group(1)) if m else None


# ---------------------------------------------------------------- datasets
def m77_objects(site):
    by = defaultdict(list)
    for l in m77_lines():
        if l["site"] == site:
            by[(l["text_no"], l["side"])].append(l)
    out = []
    for (tn, sd), ls in by.items():
        ls.sort(key=lambda x: x["line"])
        seq = []
        for i, l in enumerate(ls):
            if i: seq.append("|")
            seq += [s for seg in l["segments"] for s in seg + ["#"]][:-1] if l["segments"] else []
        lev = ls[0]["level"]
        out.append(dict(text_no=tn, side=sd, seq=seq, type=m77_type(ls[0]["object_type"]),
                        level=None if lev in ("0", "", None) else float(lev), locus=ls[0]["locus"]))
    return out


def tertile_within_locus(objs, min_obj=15, min_levels=3, absolute=False):
    """relative time 0 (deepest/oldest) .. 1 (shallowest) by depth tertile within locus."""
    by = defaultdict(list)
    for o in objs:
        if o["level"] is not None:
            by["ALL" if absolute else o["locus"]].append(o)
    units = []
    for loc, os_ in by.items():
        if len(os_) < min_obj or len({o["level"] for o in os_}) < min_levels:
            continue
        lev = np.array([o["level"] for o in os_])
        # rank: deeper (more negative) = older; average ranks for ties
        from scipy.stats import rankdata
        r = (rankdata(lev) - 0.5) / len(lev)  # 0..1, low = deep
        terc = np.minimum((r * 3).astype(int), 2)
        for o, t in zip(os_, terc):
            units.append(dict(o, rel=t / 2.0, area=loc))
    return units


def dataset_vats(**kw):
    return dedupe(tertile_within_locus(m77_objects("Harappa"), **kw))


def dataset_md_m77(**kw):
    return dedupe(tertile_within_locus(m77_objects("Mohenjodaro"), **kw))


HARP_PHASE = {"B": 0.0, "B?": 0.0, "B/C": 0.5, "C": 1.0}


def area_of(raw):
    a = raw["area-section"].strip()
    m = re.match(r"(ET|AB|E|F|D|G|H|J)", a)
    return m.group(1) if m else "?"


def icit_units(site, relfn):
    units = []
    for raw, t in zip(RAW, ICIT):
        if t["site"] != site:
            continue
        rel = relfn(raw)
        if rel is None:
            continue
        units.append(dict(seq=bridge(t["seq"]), type=icit_type(t["type"]), fine=icit_shape(t["type"]),
                          rel=rel, area=area_of(raw), trench=raw["area-section"].strip(),
                          cisi=raw["cisi"], depth=depth_ft(raw["depth"]), id=t["id"]))
    return units


def dataset_harp():
    def f(r):
        if r["period"].strip() == "3" and r["phase"].strip() in HARP_PHASE:
            return HARP_PHASE[r["phase"].strip()]
    return dedupe(icit_units("Harappa", f))


ROMAN = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7}


def dataset_vats_strata(within_area=True):
    """ICIT Harappa objects with Vats' own stratum labels (Stratum I = top = latest)."""
    def f(r):
        m = re.match(r"Stratum\s+([IV]+)\s*$", r["phase"].strip())
        return ROMAN[m.group(1)] if m else None
    u = icit_units("Harappa", f)
    # convert: higher numeral = older. rel = 1 - (s - min)/(max - min) within area (or globally)
    by = defaultdict(list)
    for x in u:
        by[x["area"] if within_area else "ALL"].append(x)
    out = []
    for a, xs in by.items():
        ss = sorted({x["rel"] for x in xs})
        if len(ss) < 2 or len(xs) < 10:
            continue
        lo, hi = ss[0], ss[-1]
        for x in xs:
            out.append(dict(x, stratum=x["rel"], rel=1 - (x["rel"] - lo) / (hi - lo)))
    return dedupe(out)


def dataset_icit_md():
    m = {"Early": 0.0, "Intermediate": 0.5, "Late": 1.0}
    return dedupe(icit_units("Mohenjo-daro", lambda r: m.get(r["period"].strip())))


def dataset_kal():
    def f(r):
        if r["period"].strip() == "2":
            return {"Early": 0.0, "Middle": 0.0, "Late": 1.0}.get(r["phase"].strip())
    return dedupe(icit_units("Kalibangan", f))


def dataset_lot():
    def f(r):
        return {"II": 0.0, "II-III": 0.25, "III": 0.5, "IV": 1.0}.get(r["phase"].strip())
    return dedupe(icit_units("Lothal", f))


def dataset_dho():
    return dedupe(icit_units("Dholavira", lambda r: {"4": 0.0, "4/5": 0.25, "5": 0.5, "6": 1.0}.get(r["period"].strip())))


def dedupe(units):
    """distinct (rel, type, seq); keep a copy count."""
    seen = {}
    for u in units:
        if not signs_of(u["seq"]):
            continue
        k = (u["rel"], u["type"], " ".join(u["seq"]))
        if k in seen:
            seen[k]["copies"] += 1
        else:
            seen[k] = dict(u, copies=1)
    return list(seen.values())


# ---------------------------------------------------------------- families
def _unused_lev(a, b):
    if abs(len(a) - len(b)) > 1:
        return 9
    d = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        p, d[0] = d[0], i
        for j, y in enumerate(b, 1):
            p, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, p + (x != y))
    return d[-1]


def _close(a, b):
    """project rule (corpus/build.py splits_v2): <=1 edit with both >= 4 signs, or the
    shorter (>= 3 signs) is a contiguous part of the longer. Reimplemented here."""
    if len(a) > len(b):
        a, b = b, a
    la, lb = len(a), len(b)
    if la >= 3 and lb > la and any(b[i:i + la] == a for i in range(lb - la + 1)):
        return True
    if lb - la > 1 or la < 4:
        return False
    if la == lb:
        return sum(x != y for x, y in zip(a, b)) <= 1
    i = 0
    while i < la and a[i] == b[i]:
        i += 1
    return a[i:] == b[i + 1:]


def families(units):
    """family id per unit (connected components of identical-or-_close sign strings)."""
    keys = [tuple(signs_of(u["seq"])) for u in units]
    uniq = sorted(set(keys))
    parent = {k: k for k in uniq}

    def find(k):
        while parent[k] != k:
            parent[k] = parent[parent[k]]; k = parent[k]
        return k
    for i in range(len(uniq)):
        for j in range(i + 1, len(uniq)):
            if _close(list(uniq[i]), list(uniq[j])):
                parent[find(uniq[i])] = find(uniq[j])
    return [find(k) for k in keys]


# ---------------------------------------------------------------- shifts
class Shift:
    """Precomputes the sign x unit incidence so permutation nulls are fast."""

    def __init__(self, units, strat=lambda u: u["type"], weight=None):
        self.units = units
        self.rel = np.array([u["rel"] for u in units], float)
        sk = [strat(u) for u in units]
        self.groups = defaultdict(list)
        for i, k in enumerate(sk):
            self.groups[k].append(i)
        self.groups = {k: np.array(v) for k, v in self.groups.items()}
        self.w = np.ones(len(units)) if weight is None else np.asarray(weight, float)
        signs = sorted({s for u in units for s in signs_of(u["seq"])})
        self.signs = signs
        idx = {s: i for i, s in enumerate(signs)}
        rows, cols = [], []
        for j, u in enumerate(units):
            for s in set(signs_of(u["seq"])):
                rows.append(idx[s]); cols.append(j)
        from scipy.sparse import csr_matrix
        self.X = csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(len(signs), len(units)))
        self.n = np.asarray(self.X.sum(1)).ravel()
        self.Xw = self.X.multiply(self.w[None, :]).tocsr()
        self.wsum = np.asarray(self.Xw.sum(1)).ravel()

    def resid(self, rel):
        e = rel.copy()
        for k, g in self.groups.items():
            if len(g):
                e[g] = rel[g] - np.average(rel[g], weights=self.w[g])
        return e

    def shifts(self, rel=None):
        e = self.resid(self.rel if rel is None else rel)
        return np.asarray(self.Xw @ e).ravel() / np.maximum(self.wsum, 1e-12)

    def perm_rel(self, rng):
        r = self.rel.copy()
        for g in self.groups.values():
            r[g] = r[rng.permutation(g)]
        return r

    def table(self):
        return dict(zip(self.signs, zip(self.shifts(), self.n)))


def compare(A, B, nmin=5, nperm=2000, seed=0, signs=None):
    """Spearman rho of shifts over shared signs (n >= nmin in both); null = within-stratum
    period permutation in both datasets. Returns dict."""
    from scipy.stats import spearmanr
    ia = {s: i for i, s in enumerate(A.signs)}
    ib = {s: i for i, s in enumerate(B.signs)}
    shared = [s for s in A.signs if s in ib and A.n[ia[s]] >= nmin and B.n[ib[s]] >= nmin]
    if signs is not None:
        shared = [s for s in shared if s in signs]
    if len(shared) < 6:
        return dict(n=len(shared), rho=float("nan"), p=float("nan"))
    a_i = np.array([ia[s] for s in shared]); b_i = np.array([ib[s] for s in shared])
    sa, sb = A.shifts()[a_i], B.shifts()[b_i]
    rho = spearmanr(sa, sb)[0]
    rng = np.random.default_rng(seed)
    null = np.empty(nperm)
    for k in range(nperm):
        null[k] = spearmanr(A.shifts(A.perm_rel(rng))[a_i], B.shifts(B.perm_rel(rng))[b_i])[0]
    p = (1 + np.sum(null >= rho)) / (nperm + 1)
    return dict(n=len(shared), rho=float(rho), p=float(p), null_mean=float(null.mean()),
                null_sd=float(null.std()), signs=shared, sa=sa.tolist(), sb=sb.tolist())
