"""Shared definitions for space_and_sealing (Fable plan 5, tests T4 and T6).

Frozen with the pre-registration docs/prereg/space_and_sealing.md.
Native Wells (W) numbering on ICIT (dimensions, material, period exist only there).
Unit everywhere: DISTINCT texts (one row per distinct sign sequence within the stated
object set), so repeated strings count once.
"""
import json, math, sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from corpus.load import icit_texts  # noqa: E402

HERE = Path(__file__).resolve().parent
FAMILY_SPLIT = ROOT / "experiments/rank_ladder/icit_family_split.json"  # seed 2026, sha afba6af6...

# ---------------- allograph (carving variant) normalisation ----------------
# Variants are counted as one sign. Sources: Wells signs bridged to the same Mahadevan
# sign, and the allograph candidates of shaunmortal STATE M5 (line ~249).
# Fish signs are NOT merged in the primary analysis (lexically distinct, README #11);
# FISH_MERGE is a sensitivity analysis only.
NORM = {
    "W704": "W705", "W706": "W705",             # M336 (W706 = the size-tracking variant)
    "W742": "W741", "W745": "W741",             # M343/344/345 handled jar
    "W806": "W803",                             # M387 leaf-trident
    "W154": "W151", "W156": "W151", "W161": "W151",  # M12/M14/M15
    "W388": "W384",                             # M326/327
    "W923": "W904",                             # M294/296
    "W861": "W817",                             # both M267
    "W405": "W390", "W406": "W390", "W407": "W390",  # all M169 in the bridge
    "W526": "W527",                             # M254
}
FISH_MERGE = {"W231": "W220", "W233": "W220", "W235": "W220", "W240": "W220"}


def norm(s, fish=False):
    s = NORM.get(s, s)
    if fish:
        s = FISH_MERGE.get(s, s)
    return s


# ---------------- sign classes (frozen; given in NORMALISED signs) ----------------
CLASSES = {
    "opener": {"W817", "W820", "W920"},                 # M267 (W817/W861), M391, M293
    "connective": {"W002", "W060"},                     # M99, M123
    "numeral": ({"W001"} | {"W%03d" % i for i in range(3, 36)} | {"W055", "W056"}),  # stroke signs, W002 excluded
    "title": {"W760", "W100", "W176", "W705", "W255", "W590"},  # rank_ladder title/title-block heads
    "jar": {"W740"},                                    # M342 closer
    "other_closer": {"W520", "W390", "W151", "W527", "W368", "W804"},  # M211, M169 fam, M12/15 fam, M254, ...
    "ticked_fish": {"W226", "W236", "W241", "W232"},   # M60, M66, M68, M71
    "post_closer": {"W400", "W090"},                    # M176, M1
}
PRIMARY_T4 = list(CLASSES)
FRAME = set().union(*(CLASSES[c] for c in ["opener", "connective", "title", "jar", "other_closer",
                                            "ticked_fish", "post_closer"]))
NUMERAL = CLASSES["numeral"]

# T6 closer classes (primary family) and frame classes (secondary family)
T6_CLOSERS = {
    "jar_M342": {"W740"},
    "M211": {"W520"},
    "M169_family": {"W390"},
    "M12_M15_family": {"W151"},
    "M254": {"W527"},
    "ticked_fish": CLASSES["ticked_fish"],
}
T6_FRAME = {k: CLASSES[k] for k in ["opener", "connective", "title", "post_closer", "numeral"]}


def signs(seq):
    return [s for s in seq if s not in ("|", "#")]


def nsigns(seq, fish=False):
    return [norm(s, fish) for s in signs(seq)]


def classes_of(sg):
    """sg: normalised sign list -> dict class -> count"""
    out = {c: sum(1 for s in sg if s in ws) for c, ws in CLASSES.items()}
    out["core"] = sum(1 for s in sg if s not in FRAME and s not in NUMERAL)
    return out


def num(x):
    try:
        return float(x)
    except Exception:
        return 0.0


def period_key(t):
    p, ph = (t.get("period") or "-").strip(), (t.get("phase") or "-").strip()
    return f"{p}|{ph}"


def heldout_keys():
    return set(json.load(open(FAMILY_SPLIT))["heldout"])


CATALOGUE_SITES = {"Mohenjo-daro", "Harappa", "Chanhu-daro"}  # 1930s measurement set (STATE F36)


def is_steatite(m):
    return (m or "").strip().lower() in ("steatite", "soft stone")


# ---------------- T4 table: square steatite seals ----------------
def t4_table(require_complete=True):
    """One row per distinct text among square (SEAL:S) steatite seals with both face
    dimensions > 0 (area > 20 mm^2). Physical values of all objects carrying the text are
    pooled: mean log area; modal site; modal site|period stratum."""
    groups = defaultdict(list)
    for t in icit_texts():
        if t["type"] != "SEAL:S" or not is_steatite(t["material"]):
            continue
        if not signs(t["seq"]):
            continue
        a = num(t["width_mm"]) * num(t["height_mm"])
        if a <= 20:
            continue
        groups[" ".join(t["seq"])].append((t, a))
    held = heldout_keys()
    rows = []
    for k, objs in groups.items():
        ts = [o[0] for o in objs]
        complete = all(t["complete"] for t in ts) and "#" not in ts[0]["seq"]
        if require_complete and not complete:
            continue
        site = Counter(t["site"] for t in ts).most_common(1)[0][0]
        per = Counter(period_key(t) for t in ts if t["site"] == site).most_common(1)[0][0]
        sg = nsigns(ts[0]["seq"])
        rows.append(dict(
            key=k, seq=ts[0]["seq"], signs=sg, length=len(sg),
            n_lines=1 + ts[0]["seq"].count("|"), site=site, stratum=f"{site}#{per}",
            period=per, log_area=sum(math.log(a) for _, a in objs) / len(objs), n_obj=len(objs),
            half="B" if k in held else "A", catalogue=site in CATALOGUE_SITES,
            cls=classes_of(sg)))
    return rows


# ---------------- T6 table: seals vs sealings ----------------
SEAL_TYPES_PREFIX = "SEAL"
SEALING_TYPES_PREFIX = "TAG"


def t6_table(require_complete=True):
    """One row per distinct (site, object class, text). Object class: seal (type SEAL*) or
    sealing (type TAG*). Each face of a sealing is its own text."""
    groups = defaultdict(list)
    for t in icit_texts():
        ty = t["type"]
        if ty.startswith(SEAL_TYPES_PREFIX):
            oc = "seal"
        elif ty.startswith(SEALING_TYPES_PREFIX):
            oc = "sealing"
        else:
            continue
        if not signs(t["seq"]):
            continue
        complete = t["complete"] and "#" not in t["seq"]
        if require_complete and not complete:
            continue
        groups[(t["site"], oc, " ".join(t["seq"]))].append(t)
    rows = []
    for (site, oc, k), ts in groups.items():
        sg = nsigns(ts[0]["seq"])
        rows.append(dict(site=site, oc=oc, key=k, signs=sg, length=len(sg), n_obj=len(ts),
                         objects=sorted({t["id"].split(".")[0] for t in ts})))
    return rows


def has_any(sg, ws):
    return any(s in ws for s in sg)
