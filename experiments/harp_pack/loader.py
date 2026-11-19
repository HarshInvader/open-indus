"""Frozen loader for the HARP (Harappa Archaeological Research Project) inscribed-object /
marked-sherd spreadsheet.  Pre-registration: docs/prereg/harp_pack.md (section "Loader").

    from experiments.harp_pack.loader import load
    df, report = load("raw/harp/harp.xlsx")        # or .csv / .tsv

Returns a pandas DataFrame with the CANONICAL columns below (missing ones are all-NA) and a
report dict (header mapping, unit conversions, value counts of normalised categorical columns,
row drops). The report never contains a test statistic, so printing it does not unblind anything.

Rules (frozen):
  * Header matching: normalise (lower case, drop a trailing unit in brackets, keep [a-z0-9]).
    Tier 1 = exact match to a synonym. Tier 2 = header contains a synonym of >= 4 characters
    (longest synonym wins). Two headers on one canonical column: the better tier wins; a tie
    raises AmbiguousColumns and the mapping must be fixed in a hashed column_map.json
    (amendment) BEFORE any outcome is computed.
  * Units: lengths to mm (cm x10, m x1000), mass to g (kg x1000, mg /1000), from the header
    or per cell ("4.5 cm").
  * Signs: tokens W### / M### are parsed; M is mapped to Wells via bridge_WM.json (first Wells
    number in sorted order; unmapped M kept as 'M###'). Bare numbers are used only if the scheme
    is given (column sign_scheme or argument) as 'wells' or 'mahadevan'; otherwise signs = None
    and every sign test is UNTESTABLE until a concordance amendment is hashed.
  * '#', '?', 'x' tokens are kept as '#' (break).
"""
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
BRIDGE = ROOT / "sources/shaunmortal_indus/data/bridge_WM.json"

CANON = {
    "lot": ["lot", "lotno", "lotnumber", "lotnum", "excavationlot", "harplot", "lotid"],
    "mound": ["mound", "area", "excavationarea"],
    "trench": ["trench", "trenchno", "grid", "square", "gridsquare", "trenchgrid"],
    "period": ["period", "harpperiod", "phase", "periodphase", "stratum", "chronology", "subperiod"],
    "object_type": ["objecttype", "object", "type", "category", "class", "artifacttype",
                    "artefacttype", "objtype", "objectclass", "objectcategory", "item"],
    "material": ["material", "materials"],
    "firing": ["firing", "firingstage", "prepostfiring", "prepost", "firingstatus",
               "markingstage", "prefiringpostfiring", "prefiring", "postfiring"],
    "technique": ["technique", "method", "markingtechnique", "marktype", "inscriptiontype",
                  "manufacture", "markingmethod", "inscriptiontechnique"],
    "vessel_form": ["vesselform", "vesseltype", "form", "vessel", "shape", "potform",
                    "vesselshape", "ceramicform", "potterytype"],
    "length_mm": ["length", "len", "maxlength", "l", "maxlen"],
    "width_mm": ["width", "breadth", "w", "maxwidth"],
    "thickness_mm": ["thickness", "thick", "t", "th"],
    "height_mm": ["height", "h", "maxheight"],
    "rim_diam_mm": ["rimdiameter", "rimdiam", "rimd", "diameterrim", "rimdia"],
    "inner_diam_mm": ["innerdiameter", "internaldiameter", "innerdiam", "insidediameter",
                      "innerdia"],
    "mass_g": ["mass", "weight", "wt", "massg", "weightg"],
    "inscription_id": ["cisi", "cisino", "cisinumber", "inscriptionid", "inscriptionno",
                       "hno", "catalogno", "catno", "icit", "icitno", "cisiid", "hnumber"],
    "field_no": ["fieldno", "fieldnumber", "harpno", "harpnumber", "regno", "registrationno",
                 "registration", "registrationnumber", "objectno", "objectnumber", "objectid",
                 "accession", "accessionno", "excavationno", "excavationnumber", "findno",
                 "itemno", "designation"],
    "signs": ["signs", "sequence", "text", "inscriptiontext", "signsequence", "signno",
              "signnos", "signnumbers", "wells", "mahadevan", "transcription", "reading",
              "marks", "mark", "inscription", "signlistnumbers"],
    "sign_scheme": ["signscheme", "scheme", "signlist", "numbering"],
}
LEN_COLS = {"length_mm", "width_mm", "thickness_mm", "height_mm", "rim_diam_mm", "inner_diam_mm"}
COLUMNS = list(CANON) + ["lot_key", "firing_class", "icit_cisi", "readable_n"]

# numeral values, identical to experiments/magnitude/run.py (W_NUM)
W_NUM = {"W001": 1, "W003": 3, "W004": 4, "W005": 5, "W006": 6, "W007": 7, "W013": 3, "W014": 4,
         "W015": 5, "W016": 6, "W017": 7, "W018": 8, "W019": 9, "W055": 12}
W_NUM.update({f"W{30 + k:03d}": k for k in range(1, 8)})


class AmbiguousColumns(Exception):
    pass


def _norm(h):
    h = str(h).lower()
    unit = None
    m = re.search(r"[\(\[]\s*([a-z]+)\s*[\)\]]\s*$", h)
    if m:
        unit = m.group(1)
        h = h[: m.start()]
    else:
        m = re.search(r"[\s_](mm|cm|m|g|kg|mg)\s*$", h)
        if m:
            unit = m.group(1)
            h = h[: m.start()]
    return re.sub(r"[^a-z0-9]", "", h), unit


def map_columns(headers, override=None):
    """-> (mapping canonical -> header, info). override: dict canonical -> header (amendment)."""
    syn = {c: set(v) for c, v in CANON.items()}
    cands = {}
    info = {"tier": {}, "unmapped": [], "units": {}}
    for h in headers:
        n, unit = _norm(h)
        hit = [(c, 1, len(n)) for c, s in syn.items() if n in s]
        if not hit:
            fz = [(c, 2, len(x)) for c, s in syn.items() for x in s if len(x) >= 4 and x in n]
            if fz:
                best = max(l for _, _, l in fz)
                hit = sorted({(c, 2, l) for c, _, l in fz if l == best})
        if len(hit) != 1:
            if len(hit) > 1:
                info.setdefault("multi", {})[str(h)] = [c for c, _, _ in hit]
            info["unmapped"].append(str(h))
            continue
        c, tier, _ = hit[0]
        cands.setdefault(c, []).append((tier, h, unit))
    mapping, conflicts = {}, {}
    for c, lst in cands.items():
        lst.sort(key=lambda x: x[0])
        if len(lst) > 1 and lst[0][0] == lst[1][0]:
            conflicts[c] = [str(x[1]) for x in lst]
            continue
        mapping[c] = lst[0][1]
        info["tier"][c] = lst[0][0]
        info["units"][c] = lst[0][2]
        for x in lst[1:]:
            info["unmapped"].append(str(x[1]))
    if override:
        for c, h in override.items():
            if h not in headers:
                raise KeyError(f"override header {h!r} not in sheet")
            mapping[c] = h
            info["tier"][c] = 0
            info["units"][c] = _norm(h)[1]
            conflicts.pop(c, None)
    if conflicts:
        raise AmbiguousColumns(conflicts)
    return mapping, info


_FACT_LEN = {"mm": 1.0, "cm": 10.0, "m": 1000.0, "in": 25.4}
_FACT_MASS = {"g": 1.0, "gm": 1.0, "gms": 1.0, "gram": 1.0, "grams": 1.0, "kg": 1000.0,
              "mg": 0.001}


def _num(v, default_unit, table):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return np.nan
    if isinstance(v, (int, float, np.integer, np.floating)):
        return float(v) * table.get(default_unit, 1.0)
    s = str(v).strip().lower().replace(",", "")
    m = re.match(r"^[~c\.\s]*(-?\d+(?:\.\d+)?)\s*([a-z]*)", s)
    if not m:
        return np.nan
    unit = m.group(2) or default_unit
    return float(m.group(1)) * table.get(unit, table.get(default_unit, 1.0))


def norm_object_type(v):
    s = str(v).lower() if v is not None and str(v) != "nan" else ""
    if not s:
        return "NA"
    if "sealing" in s or "impression" in s:
        return "SEALING"
    if "tablet" in s:
        if "incis" in s:
            return "TAB:I"
        if any(k in s for k in ("bas", "relief", "mould", "mold", "faience", "terracotta")):
            return "TAB:B"
        return "TAB"
    if "seal" in s:
        return "SEAL"
    if any(k in s for k in ("sherd", "pot", "vessel", "jar", "bowl", "ceramic", "dish", "goblet")):
        return "POT"
    if "bangle" in s:
        return "BNGL"
    if "rod" in s:
        return "ROD"
    if any(k in s for k in ("tool", "implement", "axe", "blade", "chisel", "copper", "bronze", "spear")):
        return "IMPL"
    if "tag" in s:
        return "TAG"
    return "OTHER"


def norm_firing(firing, technique):
    """-> 'pre_hand' (painted or incised before firing), 'pre_stamp' (stamped/moulded), 'post', 'NA'."""
    f = str(firing).lower() if firing is not None and str(firing) != "nan" else ""
    t = str(technique).lower() if technique is not None and str(technique) != "nan" else ""
    both = f + " " + t
    if "pre" in f and "post" in f:
        return "NA"  # 'pre or post', 'pre/post?' = unknown
    stamp = any(k in both for k in ("stamp", "impress", "seal", "mould", "mold"))
    paint = "paint" in both
    if "post" in f or "after" in f:
        stage = "post"
    elif "pre" in f or "before" in f or "wet" in f:
        stage = "pre"
    elif stamp or paint:
        stage = "pre"
    elif "post" in t:
        stage = "post"
    elif "pre" in t:
        stage = "pre"
    else:
        return "NA"
    if stage == "post":
        return "post"
    return "pre_stamp" if stamp else "pre_hand"


def norm_form(v):
    s = str(v).lower() if v is not None and str(v) != "nan" else ""
    if not s:
        return "NA"
    if "storage" in s or "large jar" in s:
        return "storage_jar"
    if "jar" in s or "pot" == s.strip():
        return "jar_other"
    if any(k in s for k in ("goblet", "beaker", "cup", "pointed")):
        return "goblet_beaker"
    if any(k in s for k in ("bowl", "dish", "plate", "basin", "pan")):
        return "bowl_dish"
    return "other"


_ROMAN = {"i": "1", "ii": "2", "iii": "3", "iv": "4", "v": "5"}


def norm_period(v):
    s = str(v).strip().lower() if v is not None and str(v) != "nan" else ""
    if not s or s in ("-", "?", "na", "n/a", "unknown"):
        return "NA"
    m = re.search(r"stratum\s*([ivx]+)", s)
    if m:
        return "Vats-" + m.group(1).upper()
    m = re.search(r"(?:period\s*)?\b([1-5]|iv|v|i{1,3})\s*([abc](?:\s*[/-]\s*[abc])?)?\b", s)
    if not m:
        return "NA"
    num = _ROMAN.get(m.group(1), m.group(1))
    sub = (m.group(2) or "").upper().replace(" ", "").replace("-", "/")
    return num + sub


def norm_id(v):
    s = str(v).strip() if v is not None and str(v) != "nan" else ""
    m = re.match(r"^H\s*[-_ ]?\s*(\d+)\s*([A-Za-z]?)$", s, re.I)
    return f"H-{int(m.group(1))}{m.group(2).upper()}" if m else None


_HARP = re.compile(r"H\s*(\d{2,4})\s*[-/]\s*(\d+)\s*/\s*(\d+)\s*-\s*(\d+)", re.I)


def lot_from_field(v):
    m = _HARP.search(str(v)) if v is not None else None
    return f"{m.group(1)}-{int(m.group(3))}" if m else None


def _m2w():
    b = json.load(open(BRIDGE))
    out = {}
    for w, rec in b.items():
        for m in rec["M"]:
            out.setdefault(f"M{m}", []).append(f"W{int(w):03d}")
    return {m: sorted(ws)[0] for m, ws in out.items()}


def parse_signs(v, scheme=None, m2w=None):
    if v is None or str(v).strip() in ("", "nan"):
        return None
    s = str(v)
    toks = re.findall(r"([WwMm])\s*0*(\d{1,3})|(#|\?|\bx\b)|(\d{1,3})", s)
    out = []
    for pre, num, brk, bare in toks:
        if brk:
            out.append("#")
        elif pre:
            code = f"{pre.upper()}{int(num)}"
            out.append(f"W{int(num):03d}" if pre.upper() == "W" else (m2w or {}).get(code, code))
        elif bare:
            if scheme == "wells":
                out.append(f"W{int(bare):03d}")
            elif scheme == "mahadevan":
                out.append((m2w or {}).get(f"M{int(bare)}", f"M{int(bare)}"))
            else:
                return None
    return out or None


def numeral_value(signs):
    return sum(W_NUM.get(s, 0) for s in (signs or []))


def load(path, override_map=None, sign_scheme=None, sheet=0):
    path = Path(path)
    if path.suffix.lower() in (".xlsx", ".xlsm", ".xls"):
        raw = pd.read_excel(path, sheet_name=sheet, dtype=object)
    elif path.suffix.lower() in (".tsv", ".tab"):
        raw = pd.read_csv(path, sep="\t", dtype=object)
    else:
        raw = pd.read_csv(path, dtype=object)
    if override_map is None and (path.parent / "column_map.json").exists():
        override_map = json.load(open(path.parent / "column_map.json"))
    return load_frame(raw, override_map=override_map, sign_scheme=sign_scheme)


def load_frame(raw, override_map=None, sign_scheme=None):
    raw = raw.dropna(how="all")
    mapping, info = map_columns(list(raw.columns), override_map)
    df = pd.DataFrame(index=raw.index)
    for c in CANON:
        df[c] = raw[mapping[c]] if c in mapping else None
    for c in LEN_COLS:
        u = info["units"].get(c) or "mm"
        df[c] = [_num(v, u, _FACT_LEN) for v in df[c]]
    u = info["units"].get("mass_g") or "g"
    df["mass_g"] = [_num(v, u, _FACT_MASS) for v in df["mass_g"]]
    df["object_type"] = [norm_object_type(v) for v in df["object_type"]]
    df["firing_class"] = [norm_firing(f, t) for f, t in zip(df["firing"], df["technique"])]
    df["vessel_form"] = [norm_form(v) for v in df["vessel_form"]]
    df["period"] = [norm_period(v) for v in df["period"]]
    ids = [norm_id(v) for v in df["inscription_id"]]
    if all(i is None for i in ids):  # a CISI-style number may sit in the field_no column
        ids = [norm_id(v) for v in df["field_no"]]
    df["icit_cisi"] = ids
    lots = []
    for lot, fno in zip(df["lot"], df["field_no"]):
        if lot is not None and str(lot).strip() not in ("", "nan", "-"):
            l = str(lot).strip().upper()
            yr = _HARP.search(str(fno)) if fno is not None else None
            lots.append(f"{yr.group(1)}-{l}" if yr and "-" not in l else l)
        else:
            lots.append(lot_from_field(fno))
    df["lot_key"] = lots
    m2w = _m2w()
    sch = []
    for v in df["sign_scheme"]:
        s = str(v).lower() if v is not None else ""
        sch.append("wells" if "well" in s else "mahadevan" if "maha" in s else sign_scheme)
    df["signs"] = [parse_signs(v, s, m2w) for v, s in zip(df["signs"], sch)]
    df["readable_n"] = [sum(1 for x in (s or []) if x != "#") for s in df["signs"]]
    report = {
        "n_rows": int(len(df)),
        "mapping": {c: str(h) for c, h in mapping.items()},
        "mapping_tier": info["tier"],
        "units": info["units"],
        "unmapped_headers": info["unmapped"],
        "multi_candidate_headers": info.get("multi", {}),
        "counts": {c: df[c].value_counts(dropna=False).astype(int).to_dict()
                   for c in ("object_type", "firing_class", "vessel_form", "period")},
        "n_with_signs": int(df["signs"].notna().sum()),
        "n_with_lot": int(pd.Series(df["lot_key"]).notna().sum()),
        "n_with_cisi": int(sum(i is not None for i in ids)),
        "n_mass": int(pd.Series(df["mass_g"]).notna().sum()),
        "n_rim": int(pd.Series(df["rim_diam_mm"]).notna().sum()),
    }
    return df[COLUMNS], report


if __name__ == "__main__":
    import sys
    d, r = load(sys.argv[1])
    print(json.dumps(r, indent=1, default=str))
