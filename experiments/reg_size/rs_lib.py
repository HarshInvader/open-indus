"""reg_size: independent replication of space_and_sealing T4 on register measurements.

Frozen with docs/prereg/reg_size.md. Imports T4's frozen definitions (sas_lib) read-only.

New objects come from experiments/old_registers/registers.csv (Mackay 1938 FEM = Mohenjo-daro,
Vats 1940 EH = Harappa; Marshall 1931 MIC and Mackay 1943 CE sensitivity only). Their texts come
from M77 (Mahadevan numbers) through Mahadevan's own serial rule (m77_text_no). T4's Wells classes
are translated to Mahadevan numbers through the bridge (an M sign belongs to class c if any Wells
sign it is bridged to, after sas_lib.NORM, is in c). Unbridged M signs are core.
"""
import json, math, sys, csv
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments/space_and_sealing"))
from corpus.load import m77_texts, icit_texts  # noqa: E402
import sas_lib  # noqa: E402  (frozen T4 definitions; read-only)
from sas_lib import CLASSES, PRIMARY_T4, norm, num, is_steatite, signs  # noqa: E402

HERE = Path(__file__).resolve().parent
REG = ROOT / "experiments/old_registers/registers.csv"
BRIDGE = json.load(open(ROOT / "sources/shaunmortal_indus/data/bridge_WM.json"))
IN2MM = 25.4

PRIMARY_SOURCES = {"Mackay1938_FEM": "Mohenjo-daro", "Vats1940_EH": "Harappa"}
SENS_SOURCES = {"Marshall1931_MIC": "Mohenjo-daro", "Mackay1943_CE": "Chanhu-daro"}

# ---------------- class map in Mahadevan numbers ----------------
M2W = defaultdict(set)
for w, v in BRIDGE.items():
    for m in v["M"]:
        M2W[f"M{m}"].add(norm("W%03d" % int(w)))
M_CLASS = {}
M_CLASS_AMBIG = {}
for m, ws in M2W.items():
    cs = {c for c, members in CLASSES.items() if ws & members}
    if len(cs) == 1:
        M_CLASS[m] = cs.pop()
        if any(not any(w in mem for mem in CLASSES.values()) for w in ws):
            M_CLASS_AMBIG[m] = sorted(ws)        # also bridged to a non-class Wells sign
    elif len(cs) > 1:
        raise SystemExit(f"class conflict for {m}: {cs}")
FRAME_M = {m for m, c in M_CLASS.items() if c != "numeral"}


def classes_of_m(sg):
    out = {c: 0 for c in CLASSES}
    for s in sg:
        c = M_CLASS.get(s)
        if c:
            out[c] += 1
    out["core"] = sum(1 for s in sg if s not in M_CLASS)
    return out


# ---------------- canonical tokens shared by Wells and Mahadevan texts ----------------
# connected components of the W-M bridge graph; unbridged tokens -> wildcard "?"
_par = {}


def _f(x):
    _par.setdefault(x, x)
    while _par[x] != x:
        _par[x] = _par[_par[x]]; x = _par[x]
    return x


for w, v in BRIDGE.items():
    for m in v["M"]:
        a, b = _f(norm("W%03d" % int(w))), _f(f"M{m}")
        _par[a] = b
for w in list(sas_lib.NORM):
    _par.setdefault(w, w)
    a, b = _f(w), _f(sas_lib.NORM[w])
    _par[a] = b


def canon(tok):
    if tok.startswith("W"):
        tok = norm(tok)
    return _f(tok) if tok in _par else "?"


def canon_seq(sg):
    return tuple(canon(s) for s in sg)


def canon_eq(a, b):
    return len(a) == len(b) and all(x == y or (x == "?" and y == "?") for x, y in zip(a, b))


def within_one_edit(a, b):
    """Levenshtein distance <= 1 with wildcard matching between unbridged tokens."""
    eq = lambda x, y: x == y  # noqa: E731  ('?' == '?' counts as equal)
    la, lb = len(a), len(b)
    if abs(la - lb) > 1:
        return False
    if la == lb:
        return sum(not eq(x, y) for x, y in zip(a, b)) <= 1
    if la > lb:
        a, b, la, lb = b, a, lb, la
    i = 0
    while i < la and eq(a[i], b[i]):
        i += 1
    return all(eq(a[j], b[j + 1]) for j in range(i, la))


# ---------------- T4 analysed set (object ids and texts) ----------------
def t4_objects():
    """Re-create T4's object filter (sas_lib.t4_table) and return
    (rows as in T4 after keep_multi, set of ICIT object ids behind those rows)."""
    rows0 = sas_lib.t4_table(require_complete=True)
    c = Counter(r["stratum"] for r in rows0)
    rows = [r for r in rows0 if c[r["stratum"]] >= 2]
    keys = {r["key"] for r in rows}
    ids = set()
    for t in icit_texts():
        if t["type"] != "SEAL:S" or not is_steatite(t["material"]) or not signs(t["seq"]):
            continue
        if num(t["width_mm"]) * num(t["height_mm"]) <= 20:
            continue
        if " ".join(t["seq"]) in keys:
            ids.add(t["id"])
    return rows, ids


# ---------------- register rows ----------------
def fnum(x):
    try:
        v = float(x)
        return v if v > 0 else None
    except Exception:
        return None


def fdepth(x):
    """signed depth in feet; 0.0 is the parser's placeholder for a missing value -> None"""
    try:
        v = float(str(x).replace("+", ""))
        return None if v == 0 else v
    except Exception:
        return None


def reg_type(src, desc):
    import re
    m = re.search(r"type\s*([A-Za-z]?)", desc or "")
    return (m.group(1) if m else "").strip()


def is_square_row(r):
    """Square stamp seal by the register: max/min side <= 1.25, sides 0.35-3.2 in, and the
    register type is the square-seal type (FEM B, EH a) or blank; FEM material steatite
    (or blank). EH gives no material (colour only)."""
    l, w = fnum(r["l_in"]), fnum(r["w_in"])
    if not l or not w:
        return False, "no dims"
    if max(l, w) / min(l, w) > 1.25:
        return False, "not square"
    if not (0.35 <= l <= 3.2 and 0.35 <= w <= 3.2):
        return False, "implausible size"
    ty = reg_type(r["source"], r["description"])
    if r["source"] == "Mackay1938_FEM":
        if ty.upper() not in ("B", ""):
            return False, f"type {ty}"
        if r["material"] and r["material"].strip().lower() not in ("steatite",):
            return False, "material"
    elif r["source"] == "Vats1940_EH":
        if ty not in ("a", ""):
            return False, f"type {ty}"
    return True, "ok"


def load_registers():
    return list(csv.DictReader(open(REG)))


def m77_seal_index():
    """text_no -> side-0 seal record (stamp seals with one inscribed face)."""
    out = {}
    for t in m77_texts():
        if t["object_type"] == "seal" and t["side"] == 0:
            out[t["text_no"]] = t
    return out


def icit_by_id():
    return {t["id"]: t for t in icit_texts()}


def parse_icit_dims(s):
    """'26.7x28.4' -> (26.7, 28.4); several or zero -> None"""
    if not s or ";" in s:
        return None
    try:
        a, b = (float(x) for x in s.split("x"))
    except Exception:
        return None
    return (a, b) if a > 0 and b > 0 else None


def build_new_set(sources, exclude="exact", t4=None, require_animal=False):
    """Return (rows, audit). One row per distinct M77 text among square register seals of
    `sources`, after removing texts in T4's analysed set. Row fields mirror sas_lib.t4_table:
    key, signs, length, site, stratum, log_area (mean log mm^2 over objects), cls, ..."""
    t4rows, t4ids = t4 if t4 else t4_objects()
    t4canon = [canon_seq(r["signs"]) for r in t4rows]
    t4set = set(t4canon)
    m77 = m77_seal_index()
    audit = Counter()
    groups = defaultdict(list)
    for r in load_registers():
        if r["source"] not in sources:
            continue
        audit["rows"] += 1
        ok, why = is_square_row(r)
        if not ok:
            audit["drop: " + why] += 1
            continue
        if not r["m77_text_no"]:
            audit["drop: no M77 link"] += 1
            continue
        t = m77.get(int(r["m77_text_no"]))
        if t is None:
            audit["drop: M77 text not a one-face seal"] += 1
            continue
        if not t["complete"] or "#" in t["seq"]:
            audit["drop: incomplete text"] += 1
            continue
        if require_animal and t.get("fs_category") != "Animals":
            audit["drop: no animal (sensitivity)"] += 1
            continue
        ids = [i for i in (r["icit_ids"] or "").split(";") if i]
        if any(i in t4ids for i in ids):
            audit["drop: object in T4 (ICIT id)"] += 1
            continue
        sg = signs(t["seq"])
        cs = canon_seq(sg)
        if cs in t4set:
            audit["drop: text in T4 analysed set"] += 1
            continue
        if exclude == "edit1" and any(within_one_edit(cs, x) for x in t4canon):
            audit["drop: within 1 edit of a T4 text (sensitivity)"] += 1
            continue
        l, w = fnum(r["l_in"]) * IN2MM, fnum(r["w_in"]) * IN2MM
        groups[" ".join(sg)].append(dict(row=r, t=t, area=l * w,
                                         depth=fdepth(r["depth_ft"]),
                                         site=PRIMARY_SOURCES.get(r["source"]) or SENS_SOURCES[r["source"]],
                                         source=r["source"]))
        audit["kept objects"] += 1
    rows = []
    for k, objs in groups.items():
        site = Counter(o["site"] for o in objs).most_common(1)[0][0]
        sg = signs(objs[0]["t"]["seq"])
        rows.append(dict(key=k, signs=sg, length=len(sg), site=site, stratum=f"{site}#register",
                         source=Counter(o["source"] for o in objs).most_common(1)[0][0],
                         log_area=sum(math.log(o["area"]) for o in objs) / len(objs), n_obj=len(objs),
                         n_lines=objs[0]["t"]["n_lines"], text_no=objs[0]["t"]["text_no"],
                         animal=objs[0]["t"].get("fs_category") == "Animals",
                         depth=next((o["depth"] for o in objs if o["depth"] is not None), None),
                         icit_ids=sorted({i for o in objs for i in (o["row"]["icit_ids"] or "").split(";") if i}),
                         cls=classes_of_m(sg)))
    audit["distinct texts"] = len(rows)
    return rows, dict(audit)
