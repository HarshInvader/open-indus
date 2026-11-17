"""Shared data + estimators for the identifiers experiment (S3 unseen-species, S4 identifier repulsion).

Units
  * sample  = one inscribed OBJECT (M77 text_no; ICIT id before the '.'), all sides joined.
  * species = the object's distinct text (tuple of its side texts, line breaks dropped).
  Objects with any break '#' or flagged incomplete are dropped for species work (a damaged text
  could be a copy of a known one or a new one; we cannot tell).
Classes (fixed before any statistic): seal, sealing (true clay sealings / tags), moulded tablet,
incised tablet, copper tablet. M77 'sealing' at Mohenjo-daro / Harappa is mostly moulded tablets.
"""
import csv, json, math, sys
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from corpus.load import icit_texts, m77_texts, m77_lines, dev_heldout  # noqa

OUT = ROOT / "experiments" / "identifiers"
BRIDGE = json.load(open(ROOT / "sources/shaunmortal_indus/data/bridge_WM.json"))
W2M = {f"W{int(k):03d}": f"M{v['M'][0]}" for k, v in BRIDGE.items()}

M77_SITE = {"Mohenjodaro": "Mohenjo-daro", "Chanhudaro": "Chanhu-daro"}
M77_TRUE_SEALING_SITES = {"Lothal", "Kalibangan", "Other sites"}


def m77_class(ot, site):
    if ot == "seal": return "seal"
    if ot == "sealing": return "sealing" if site in M77_TRUE_SEALING_SITES else "moulded_tablet"
    if ot == "miniature tablet": return "tablet"
    if ot == "copper tablet": return "copper_tablet"
    return "other"


def icit_class(ty):
    if ty.startswith("SEAL"): return "seal"
    if ty.startswith("TAG"): return "sealing"
    if ty == "TAB:B": return "moulded_tablet"
    if ty == "TAB:I": return "incised_tablet"
    if ty == "TAB:C": return "copper_tablet"
    return "other"


def clean(seq):
    return tuple(s for s in seq if s != "|")


# ---------------------------------------------------------------- objects
def m77_objects(subset=None):
    """subset: None | 'dev' | 'heldout' -> objects whose (every) side text is in that split.
    Returns list of dicts: obj, site, cls, locus, sp (species key), sides (list of tuples), complete."""
    T = m77_texts()
    loc = {}
    for l in m77_lines():
        loc.setdefault(l["text_no"], l.get("locus") or "")
    split = None
    if subset:
        dev, ho = dev_heldout()
        keep = {" ".join(t["seq"]) for t in (dev if subset == "dev" else ho)}
    by = defaultdict(list)
    for t in T:
        by[t["text_no"]].append(t)
    out = []
    for no, ts in by.items():
        ts = sorted(ts, key=lambda t: t["side"])
        if subset and not all(" ".join(t["seq"]) in keep for t in ts):
            continue
        sides = [clean(t["seq"]) for t in ts]
        comp = all(t["complete"] for t in ts) and not any("#" in s for s in sides) and all(sides)
        site = M77_SITE.get(ts[0]["site"], ts[0]["site"])
        out.append(dict(obj=no, site=site, cls=m77_class(ts[0]["object_type"], ts[0]["site"]),
                        locus=loc.get(no, ""), sides=sides, sp=tuple(sides), complete=comp))
    return out


def icit_objects(to_M=False):
    by = defaultdict(list)
    for t in icit_texts():
        by[t["id"].split(".")[0]].append(t)
    out = []
    for oid, ts in by.items():
        ts = sorted(ts, key=lambda t: t["id"])
        sides = [tuple((W2M.get(x, x) if to_M else x) for x in clean(t["seq"])) for t in ts]
        comp = all(t["complete"] for t in ts) and not any("#" in s for s in sides) and all(sides)
        t0 = ts[0]
        out.append(dict(obj=oid, site=t0["site"], cls=icit_class(t0["type"]), type=t0["type"],
                        period=t0["period"].strip(), phase=t0["phase"].strip(), cisi=t0["cisi"],
                        sides=sides, sp=tuple(sides), complete=comp))
    return out


def harp(o):
    """ICIT Harappa object from the HARP excavations (1986-): a HARP period is recorded. ICIT-only by date."""
    return o["site"] == "Harappa" and o["period"] not in ("-", "")


def icit_group(o):
    """Site+period group for S4 (co-found = same site, same recorded period/phase)."""
    s, per, ph = o["site"], o["period"], o["phase"]
    if s == "Harappa":
        if per == "3" and ph in ("B", "B?", "B/C", "C"): return f"HAR-3{ph.rstrip('?')}"
        if ph.startswith("Stratum"): return "HAR-Vats-" + ph.split()[-1]
        return None
    if s == "Mohenjo-daro":
        return f"MD-{per}" if per in ("Early", "Intermediate", "Late") else None
    if per in ("-", ""): return None
    return f"{s}-{per}-{ph}"


# ---------------------------------------------------------------- abundance estimators
def freq_counts(abund):
    x = np.asarray([a for a in abund if a > 0], int)
    return x, Counter(x.tolist())


def chao1(abund):
    x, f = freq_counts(abund); n = x.sum(); S = len(x); f1, f2 = f.get(1, 0), f.get(2, 0)
    if f2 > 0:
        f0 = (n - 1) / n * f1 * f1 / (2 * f2)
    else:
        f0 = (n - 1) / n * f1 * (f1 - 1) / 2
    return S + f0


def ace(abund, k=10):
    x, f = freq_counts(abund); S = len(x)
    rare = x[x <= k]; Sr = len(rare); Sab = S - Sr; nr = rare.sum()
    if nr == 0: return float(S)
    f1 = f.get(1, 0)
    if f1 == nr: return chao1(abund)  # all rare singletons: ACE undefined, fall back
    C = 1 - f1 / nr
    s = sum(i * (i - 1) * f.get(i, 0) for i in range(1, k + 1))
    g2 = max(Sr / C * s / (nr * (nr - 1)) - 1, 0)
    return Sab + Sr / C + f1 / C * g2


def coverage(abund, m=None):
    """Chao & Jost 2012 sample coverage of the sample (m=None) or of a rarefied/extrapolated size m."""
    x, f = freq_counts(abund); n = int(x.sum()); f1, f2 = f.get(1, 0), f.get(2, 0)
    if f2 > 0: a = (n - 1) * f1 / ((n - 1) * f1 + 2 * f2)
    elif f1 > 0: a = (n - 1) * (f1 - 1) / ((n - 1) * (f1 - 1) + 2)
    else: a = 0.0
    Cn = 1 - f1 / n * a
    if m is None or m == n: return Cn
    if m < n:
        from scipy.special import gammaln
        tot = 0.0
        for xi in x:
            if n - xi >= m:
                tot += xi / n * math.exp(gammaln(n - xi + 1) - gammaln(n - xi - m + 2) - gammaln(n) + gammaln(n - m + 1))
        # = sum xi/n * C(n-xi, m)/C(n-1, m)
        return 1 - tot
    return 1 - f1 / n * a ** (m - n + 1)


def s_at(abund, m):
    """iNEXT interpolated (m<n) / extrapolated (m>n) expected richness."""
    x, f = freq_counts(abund); n = int(x.sum()); S = len(x)
    if m <= n:
        from scipy.special import gammaln
        lc = lambda a, b: gammaln(a + 1) - gammaln(b + 1) - gammaln(a - b + 1)
        base = lc(n, m)
        return float(sum(1 - (math.exp(lc(n - xi, m) - base) if n - xi >= m else 0) for xi in x))
    f1 = f.get(1, 0); f0 = chao1(abund) - S
    if f0 <= 0 or f1 == 0: return float(S)
    return S + f0 * (1 - (1 - f1 / (n * f0 + f1)) ** (m - n))


def boot_ci(abund, fn, B=200, seed=0):
    """Chao et al. 2014 bootstrap: augment with estimated undetected species, multinomial resample."""
    rng = np.random.default_rng(seed)
    x, f = freq_counts(abund); n = int(x.sum()); S = len(x)
    f1, f2 = f.get(1, 0), f.get(2, 0)
    f0 = int(math.ceil(chao1(abund) - S))
    Cn = coverage(abund)
    lam = (1 - Cn) / np.sum(x / n * (1 - x / n) ** n) if np.sum(x / n * (1 - x / n) ** n) > 0 else 0
    p = x / n * (1 - lam * (1 - x / n) ** n)
    if f0 > 0:
        p = np.concatenate([p, np.full(f0, (1 - Cn) / f0)])
    p = np.clip(p, 0, None); p = p / p.sum()
    vals = []
    for _ in range(B):
        y = rng.multinomial(n, p)
        vals.append(fn(y[y > 0]))
    return np.percentile(vals, [2.5, 97.5]).tolist()


def summarize(abund, boot=True, seed=0):
    x, f = freq_counts(abund); n = int(x.sum()); S = len(x)
    d = dict(n=n, S=S, f1=f.get(1, 0), f2=f.get(2, 0), chao1=chao1(x), ace=ace(x), cov=coverage(x),
             S_2n=s_at(x, 2 * n), complete=S / chao1(x) if chao1(x) else float("nan"),
             new_rate=1 - coverage(x))
    if boot and n >= 5:
        d["chao1_ci"] = boot_ci(x, chao1, seed=seed)
        d["cov_ci"] = boot_ci(x, coverage, seed=seed)
    return d


def abundances(objs):
    return list(Counter(o["sp"] for o in objs).values())


# ---------------------------------------------------------------- distances (S4)
def edit(a, b):
    la, lb = len(a), len(b)
    prev = list(range(lb + 1))
    for i in range(1, la + 1):
        cur = [i] + [0] * lb
        ai = a[i - 1]
        for j in range(1, lb + 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ai != b[j - 1]))
        prev = cur
    return prev[lb]


def ned(a, b):
    return edit(a, b) / max(len(a), len(b), 1)


def shared(a, b):
    return sum((Counter(a) & Counter(b)).values())


def flat(sp):
    return tuple(s for side in sp for s in side) if sp and isinstance(sp[0], tuple) else tuple(sp)


def bh(p):
    p = np.asarray(p, float); n = len(p); o = np.argsort(p); q = np.empty(n)
    q[o] = np.minimum.accumulate((p[o] * n / np.arange(1, n + 1))[::-1])[::-1]
    return np.minimum(q, 1)


# ---------------------------------------------------------------- core / frame (functional_reading lexicon)
FRAME_ROLES = {"OPENER", "CONNECTIVE", "CLOSER", "TITLE ELEMENT", "POST-CLOSER CLITIC", "BRACKETED-FISH CLOSER"}


def _roles():
    out = {}
    for r in csv.DictReader(open(ROOT / "experiments/functional_reading/lexicon.csv")):
        if r["kind"] != "sign" or not r["roles"].strip():
            continue
        best = max((p.strip().rsplit(" ", 1) for p in r["roles"].split(";")), key=lambda x: float(x[1]))[0]
        out[r["item"]] = best
    return out


ROLES = _roles()


def is_frame(s):
    return ROLES.get(W2M.get(s, s)) in FRAME_ROLES


def decompose(text):
    """text (flat tuple) -> (skeleton, cores): skeleton = frame signs with each maximal non-frame run
    replaced by a slot 'X'; cores = list of the non-frame runs (tuples), in order."""
    skel, cores, cur = [], [], []
    for s in text:
        if is_frame(s):
            if cur: skel.append("X"); cores.append(tuple(cur)); cur = []
            skel.append(s)
        else:
            cur.append(s)
    if cur: skel.append("X"); cores.append(tuple(cur))
    return tuple(skel), cores


def core_key(text):
    return tuple(s for s in text if not is_frame(s))


def frame_key(text):
    return decompose(text)[0]
