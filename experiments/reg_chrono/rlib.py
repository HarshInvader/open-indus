"""reg_chrono shared library: register depths -> within-area ordinal depth units.

Run from repo root: .venv/bin/python experiments/reg_chrono/<script>.py
"""
import sys, json, csv
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from corpus.load import m77_lines  # noqa: E402
from corpus.build import _close  # noqa: E402  (project family rule)

HERE = Path(__file__).resolve().parent
REG = ROOT / "experiments/old_registers/registers.csv"
MIN_AREA = 15  # units per area stratum after family collapse

TICKED = {"M60", "M66", "M68", "M71", "M73"}
MARKERS = {
    "ticked_fish": lambda s: any(x in TICKED for x in s),
    "M99_connective": lambda s: "M99" in s,
    "M342_jar": lambda s: "M342" in s,
    "M162_count_frame": lambda s: "M162" in s,
}


def m77_objects():
    """text_no -> dict(seq, type, level, locus, site) built from M77 lines (side 0 preferred)."""
    by = defaultdict(list)
    for l in m77_lines():
        by[(l["text_no"], l["side"])].append(l)
    out = {}
    for (tn, sd), ls in sorted(by.items()):
        ls.sort(key=lambda x: x["line"])
        seq = []
        for i, l in enumerate(ls):
            if i:
                seq.append("|")
            if l["segments"]:
                seq += [s for seg in l["segments"] for s in seg + ["#"]][:-1]
        o = out.setdefault(tn, dict(text_no=tn, seqs=[], type=ls[0]["object_type"], site=ls[0]["site"],
                                     locus=ls[0]["locus"], level=ls[0]["level"]))
        o["seqs"].append(seq)
    for o in out.values():
        o["signs"] = [s for sq in o["seqs"] for s in sq if s not in ("|", "#")]
        o["seq"] = [s for s in o["seqs"][0]]  # side 0 / first side for positional tests
    return out


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def clean_depth(row, m77lev):
    """Return (depth, how). Larger = shallower (above datum / nearer surface). Ordinal use only."""
    src = row["source"]
    d = _f(row["depth_ft"])
    lev = _f(m77lev)
    if lev == 0:
        lev = None
    if src == "Mackay1938_FEM":
        on = _f(row["object_no"])
        if d is not None and on is not None and on <= 686:
            d = -abs(d)  # Mackay sorts serials 1-686 by depth below datum; OCR drops minus signs
    elif src == "Vats1940_EH":
        if d is not None:
            d = -abs(d)  # depth below local surface
    if d is not None and lev is not None and abs(d - lev) > 1.5:
        return lev, "m77_override"
    if d is None:
        return (lev, "m77_integer") if lev is not None else (None, "none")
    return d, "register"


def load_objects(sources=("Mackay1938_FEM",), mic_strict=False):
    """Register rows linked to M77, one per M77 text_no, with cleaned depth and area."""
    objs = m77_objects()
    rows = list(csv.DictReader(open(REG)))
    seen, out = set(), []
    for r in rows:
        if r["source"] not in sources or not r["m77_text_no"]:
            continue
        if r["source"] == "Marshall1931_MIC" and mic_strict:
            if r["check_depth_vs_m77"] != "agree" or (_f(r["seq_sim_m77_icit"]) or 0) < 0.5:
                continue
        tn = int(float(r["m77_text_no"]))
        if tn in seen or tn not in objs:
            continue
        seen.add(tn)
        o = objs[tn]
        d, how = clean_depth(r, o["level"])
        if d is None or not o["signs"]:
            continue
        blk = (r.get("block") or "").strip()
        out.append(dict(text_no=tn, source=r["source"], area=o["locus"], block=blk, depth=d, how=how,
                        type=o["type"], signs=o["signs"], seq=o["seq"], object_no=r["object_no"]))
    return out


def m77_integer_objects(site):
    """Sensitivity: all M77 objects of a site with integer level (no register)."""
    out = []
    for o in m77_objects().values():
        lev = _f(o["level"])
        if o["site"] != site or lev in (None, 0) or not o["signs"]:
            continue
        out.append(dict(text_no=o["text_no"], source="M77", area=o["locus"], block="", depth=lev, how="m77_integer",
                        type=o["type"], signs=o["signs"], seq=o["seq"], object_no=""))
    return out


def coarse_type(t):
    return {"seal": "seal", "sealing": "sealing", "miniature tablet": "tablet"}.get(t, "other")


def make_units(objs, area_key="area", min_area=MIN_AREA):
    """Collapse to one unit per text family per area; rel = within-area depth rank in (0,1),
    0 = deepest (oldest), 1 = shallowest. Representative text = member with most signs."""
    by_area = defaultdict(list)
    for o in objs:
        by_area[o[area_key]].append(o)
    units = []
    for a, os_ in sorted(by_area.items()):
        # families within area
        keys = sorted({" ".join(o["signs"]) for o in os_})
        parent = {k: k for k in keys}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        sg = {k: k.split() for k in keys}
        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                if keys[i] == keys[j] or _close(sg[keys[i]], sg[keys[j]]):
                    parent[find(keys[i])] = find(keys[j])
        r = rankdata([o["depth"] for o in os_])
        rel = (r - 0.5) / len(os_)
        fam = defaultdict(list)
        for o, x in zip(os_, rel):
            fam[find(" ".join(o["signs"]))].append((o, x))
        us = []
        for f, mem in sorted(fam.items()):
            rep = max(mem, key=lambda m: (len(m[0]["signs"]), -m[0]["text_no"]))[0]
            types = sorted({coarse_type(m[0]["type"]) for m in mem})
            us.append(dict(area=a, rel=float(np.mean([m[1] for m in mem])), signs=rep["signs"], seq=rep["seq"],
                           type=coarse_type(rep["type"]) if len(types) == 1 else types[0],
                           n_members=len(mem), text_nos=[m[0]["text_no"] for m in mem]))
        if len(us) >= min_area:
            units += us
    for u in units:
        u["stratum"] = f'{u["area"]}|{u["type"]}'
    return units


# ------------------------------------------------------------------ permutation machinery
class Perm:
    """Permute rel within stratum. Precomputes index groups."""

    def __init__(self, units, seed=0):
        self.units = units
        self.rel = np.array([u["rel"] for u in units])
        st = defaultdict(list)
        for i, u in enumerate(units):
            st[u["stratum"]].append(i)
        self.groups = [np.array(v) for v in st.values() if len(v) > 1]
        # centred rel: rel minus stratum mean (so statistics are within-stratum)
        self.cent = self.rel.copy()
        for v in st.values():
            v = np.array(v)
            self.cent[v] = self.rel[v] - self.rel[v].mean()
        self.rng = np.random.default_rng(seed)

    def perm_rel(self):
        r = self.rel.copy()
        for g in self.groups:
            r[g] = self.rel[self.rng.permutation(g)]
        return r

    def perms(self, n):
        """matrix n x N of permuted CENTRED rel (centring is invariant under within-stratum perms)."""
        out = np.empty((n, len(self.rel)))
        for k in range(n):
            out[k] = self._cent_of(self.perm_rel())
        return out

    def _cent_of(self, r):
        c = r.copy()
        for g in self.groups:
            c[g] = r[g] - r[g].mean()
        return c


def trend_stat(X, cent):
    """X: N x m presence (0/1) or share matrix; cent: centred rel (N,) or (P,N).
    Statistic per column: sum_i X_i * cent_i / sum_i X_i  = mean centred rel of carriers
    (> 0: more common in shallow = later)."""
    n = X.sum(0)
    n[n == 0] = 1
    return (cent @ X) / n


def two_sided_p(obs, null):
    """obs (m,), null (P,m); two-sided p around null mean."""
    mu = null.mean(0)
    return (1 + (np.abs(null - mu) >= np.abs(obs - mu) - 1e-12).sum(0)) / (1 + null.shape[0])


def bh(p):
    p = np.asarray(p, float)
    m = len(p)
    o = np.argsort(p)
    q = np.empty(m)
    prev = 1.0
    for rank, i in reversed(list(enumerate(o, 1))):
        prev = min(prev, p[i] * m / rank)
        q[i] = prev
    return q


def holm(p):
    p = np.asarray(p, float)
    m = len(p)
    o = np.argsort(p)
    q = np.empty(m)
    run = 0
    for k, i in enumerate(o):
        run = max(run, min(1, (m - k) * p[i]))
        q[i] = run
    return q


def role_map():
    import pandas as pd
    d = pd.read_csv(ROOT / "experiments/functional_reading/lexicon.csv")
    d = d[d.kind == "sign"]
    m = {}
    for it, ro in zip(d["item"], d["roles"].astype(str)):
        r = ro.split()[0]
        r = {"BRACKETED-FISH": "FISH-CLASS", "UNIT/MEASURE": "NOUN"}.get(r, r)
        m[it] = r
    return m


ROLES = ["OPENER", "CONNECTIVE", "NUMERAL(short)", "NUMERAL(tall)", "FISH-CLASS", "TITLE", "NOUN", "CLOSER",
         "POST-CLOSER"]


def datasets(kind="primary"):
    if kind == "primary":
        return {"MD_FEM": make_units(load_objects(("Mackay1938_FEM",))),
                "HAR_EH": make_units(load_objects(("Vats1940_EH",)))}
    if kind == "block":  # MD sensitivity: Mackay block as area
        return {"MD_FEM_block": make_units(load_objects(("Mackay1938_FEM",)), area_key="block", min_area=8)}
    if kind == "mic":
        return {"MD_FEM+MIC": make_units(load_objects(("Mackay1938_FEM", "Marshall1931_MIC"), mic_strict=False))}
    if kind == "m77int":
        return {"MD_M77int": make_units(m77_integer_objects("Mohenjodaro")),
                "HAR_M77int": make_units(m77_integer_objects("Harappa"))}
    raise ValueError(kind)


if __name__ == "__main__":
    for kind in ("primary", "block", "mic", "m77int"):
        for k, us in datasets(kind).items():
            from collections import Counter
            print(kind, k, "units", len(us), "areas", dict(Counter(u["area"] for u in us)),
                  "types", dict(Counter(u["type"] for u in us)))
    objs = load_objects(("Mackay1938_FEM",))
    from collections import Counter
    print("FEM depth source", Counter(o["how"] for o in objs))
    objs = load_objects(("Vats1940_EH",))
    print("EH depth source", Counter(o["how"] for o in objs))
    # validation: Mackay serial order vs cleaned depth
    from scipy.stats import spearmanr
    o = [x for x in load_objects(("Mackay1938_FEM",)) if _f(x["object_no"]) and _f(x["object_no"]) <= 686]
    print("FEM serial vs cleaned depth rho", spearmanr([_f(x["object_no"]) for x in o], [x["depth"] for x in o])[0])
