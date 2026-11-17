"""Shared data + statistics for the stratigraphic half-life experiment (Fable plan 2, item 9).

Units: distinct (dataset, period, sequence) triples = a text counted once per period, so mould copies
of one tablet in one period count once, but the same text found in two periods counts in both.
"""
import csv, json, sys
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from corpus.load import icit_texts, m77_lines, runs  # noqa

OUT = ROOT / "experiments" / "half_life"
BRIDGE = json.load(open(ROOT / "sources/shaunmortal_indus/data/bridge_WM.json"))
W2M = {f"W{int(k):03d}": f"M{v['M'][0]}" for k, v in BRIDGE.items()}

# ---------- roles (functional_reading lexicon, top-weight role) ----------
FRAME_ROLES = {"OPENER", "CONNECTIVE", "CLOSER", "TITLE ELEMENT", "POST-CLOSER CLITIC", "BRACKETED-FISH CLOSER"}
CORE_ROLES = {"NOUN", "FISH-CLASS NOUN"}
NUM_ROLES = {"NUMERAL(short)", "NUMERAL(tall)", "UNIT/MEASURE"}


def lexicon_roles():
    out = {}
    for r in csv.DictReader(open(ROOT / "experiments/functional_reading/lexicon.csv")):
        if r["kind"] != "sign" or not r["roles"].strip():
            continue
        best, bw = None, -1
        for part in r["roles"].split(";"):
            part = part.strip()
            name, w = part.rsplit(" ", 1)
            if float(w) > bw:
                best, bw = name, float(w)
        cls = "FRAME" if best in FRAME_ROLES else "CORE" if best in CORE_ROLES else "NUM" if best in NUM_ROLES else "OTHER"
        out[r["item"]] = (best, cls)
    return out


def signs(seq):
    return [s for s in seq if s not in ("|", "#")]


def otype_icit(ty):
    return "seal" if ty.startswith("SEAL") else "tablet" if ty.startswith("TAB") else "tag" if ty.startswith("TAG") \
        else "pot" if ty.startswith("PO") else "other"


def otype_m77(ty):
    return {"seal": "seal", "sealing": "tablet", "miniature tablet": "tablet", "pottery graffito": "pot"}.get(ty, "other")


# ---------- period orderings (fixed before any slot statistic was computed) ----------
def icit_period(t):
    s, per, ph = t["site"], t["period"].strip(), t["phase"].strip()
    if s == "Harappa":            # HARP: 3B ~2450-2200, 3C ~2200-1900 BCE; 3B/C = mixed/transitional deposits
        if per == "3" and ph in ("B", "B?"): return 0
        if per == "3" and ph == "B/C": return 1
        if per == "3" and ph == "C": return 2
        return None
    if s == "Mohenjo-daro":       # period level only (sub-phase numbering direction uncertain)
        return {"Early": 0, "Intermediate": 1, "Late": 2}.get(per)
    if s == "Dholavira":          # stages 4, 5, 6 (4/5, 5/6 and stages 1-3 dropped)
        return {"4": 0, "5": 1, "5?": 1, "6": 2}.get(per)
    if s == "Kalibangan":         # period II early+middle vs late
        if per != "2": return None
        return {"Early": 0, "Middle": 0, "Late": 1}.get(ph)
    if s == "Lothal":             # Rao phases II, III, IV (I and V too thin; II-III dropped)
        return {"II": 0, "III": 1, "IV": 2}.get(ph)
    return None


ICIT_SITES = {"Harappa": "HAR", "Mohenjo-daro": "MD", "Dholavira": "DHO", "Kalibangan": "KAL", "Lothal": "LOT"}


def build_icit(to_M=True):
    """Return dict dataset -> list of units (period, otype, set_of_signs, seq_tuple). Signs in M if to_M (OOV kept as W)."""
    D = defaultdict(list); seen = set()
    for t in icit_texts():
        if t["site"] not in ICIT_SITES: continue
        p = icit_period(t)
        ss = signs(t["seq"])
        if p is None or not ss: continue
        seq = tuple((W2M.get(x, x) if to_M else x) if x not in ("|", "#") else x for x in t["seq"])
        k = (t["site"], p, seq)
        if k in seen: continue
        seen.add(k)
        D[ICIT_SITES[t["site"]]].append(dict(period=p, ot=otype_icit(t["type"]), seq=seq,
                                             signs=frozenset(x for x in seq if x not in ("|", "#"))))
    return dict(D)


def build_m77_depth(site, nbins=3):
    """M77 objects with depth (level != 0): depth rank within locus -> tertiles (0 = deepest/oldest).
    Unit: distinct (bin, object text). Harappa = Vats excavations (independent of HARP)."""
    L = m77_lines()
    obj = defaultdict(lambda: dict(seq=[], level=None, locus=None, ot=None))
    for r in L:
        if r["site"] != site or r["side"] not in (0, 1): continue
        k = (r["text_no"], r["side"])
        o = obj[k]
        if o["seq"]: o["seq"].append("|")
        o["seq"] += r["signs"]; o["level"] = r["level"]; o["locus"] = r["locus"]; o["ot"] = otype_m77(r["object_type"])
    rows = [o for o in obj.values() if o["level"] not in (None, "0", "-", "") and signs(o["seq"])]
    by_loc = defaultdict(list)
    for o in rows: by_loc[o["locus"]].append(o)
    out, seen = [], set()
    for loc, os_ in by_loc.items():
        if len(os_) < 15: continue
        d = np.array([-float(o["level"]) for o in os_])   # larger = deeper
        if np.unique(d).size < 3: continue
        # rank deepest first; tertiles of within-locus depth rank
        r = (np.argsort(np.argsort(-d, kind="stable"), kind="stable") + 0.5) / len(d)
        for o, rr in zip(os_, r):
            b = min(int(rr * nbins), nbins - 1)
            seq = tuple(o["seq"]); key = (b, seq)
            if key in seen: continue
            seen.add(key)
            out.append(dict(period=b, ot=o["ot"], seq=seq, signs=frozenset(signs(seq)), locus=loc))
    return out


# ---------- statistics ----------
def strat_perm_idx(strata, rng):
    """Permutation index that permutes within strata."""
    idx = np.arange(len(strata))
    out = idx.copy()
    for s in np.unique(strata):
        w = np.where(strata == s)[0]
        out[w] = w[rng.permutation(len(w))]
    return out


def g_stat(counts, expected):
    m = counts > 0
    return 2 * float((counts[m] * np.log(counts[m] / expected[m])).sum())


def drift_scores(units, items_of, nperm, rng, min_n=1):
    """For each item (sign/ngram), the G statistic of its period distribution vs the expectation from period
    sizes within object-type strata, its permutation null (period labels permuted within object type),
    returns dict item -> (G_obs, null array, n)."""
    P = np.array([u["period"] for u in units]); OT = np.array([u["ot"] for u in units])
    T = P.max() + 1
    items = Counter(x for u in units for x in items_of(u))
    items = [x for x, n in items.items() if n >= min_n]
    ix = {x: i for i, x in enumerate(items)}
    X = np.zeros((len(units), len(items)), dtype=np.float32)
    for r, u in enumerate(units):
        for x in items_of(u):
            if x in ix: X[r, ix[x]] = 1
    ots = np.unique(OT)
    OTm = np.array([[o == k for k in ots] for o in OT], float)          # units x types
    # expected counts of item in period t: sum_k n_item,k * N_t,k / N_k  (fixed under permutation within type)
    n_ik = X.T @ OTm                                                    # items x types
    N_k = OTm.sum(0)

    def counts_for(Pv):
        Pm = np.eye(T)[Pv]                                              # units x T
        return X.T @ Pm                                                 # items x T
    N_tk = (np.eye(T)[P]).T @ OTm                                       # T x types (same under perm)
    E = n_ik @ (N_tk / N_k).T                                           # items x T
    E = np.maximum(E, 1e-9)

    def G(C):
        with np.errstate(divide="ignore", invalid="ignore"):
            t = np.where(C > 0, C * np.log(C / E), 0.0)
        return 2 * t.sum(1)
    Gobs = G(counts_for(P))
    null = np.zeros((nperm, len(items)))
    for b in range(nperm):
        null[b] = G(counts_for(P[strat_perm_idx(OT, rng)]))
    nn = X.sum(0)
    return items, Gobs, null, nn, counts_for(P), E


def bh(p):
    p = np.asarray(p, float); n = len(p)
    if n == 0: return p
    o = np.argsort(p); q = p[o] * n / np.arange(1, n + 1)
    q = np.minimum.accumulate(q[::-1])[::-1]
    out = np.empty(n); out[o] = np.minimum(q, 1); return out
