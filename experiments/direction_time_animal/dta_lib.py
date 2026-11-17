"""Shared data for direction_time_animal (Fable plan 6, E2/E3/E4). Pre-registered: docs/prereg/direction_time_animal.md."""
import csv, json, re, sys
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from corpus.load import icit_texts, m77_lines  # noqa

OUT = ROOT / "experiments" / "direction_time_animal"
BRIDGE = json.load(open(ROOT / "sources/shaunmortal_indus/data/bridge_WM.json"))
W2M = {f"W{int(k):03d}": f"M{v['M'][0]}" for k, v in BRIDGE.items()}


def to_m(s):
    return W2M.get(s, s)


def signs(seq):
    return [s for s in seq if s not in ("|", "#")]


# ---------- roles ----------
ROLE_MERGE = {"OPENER": "OPENER", "CONNECTIVE": "CONNECTIVE", "NUMERAL(short)": "NUMERAL", "NUMERAL(tall)": "NUMERAL",
              "UNIT/MEASURE": "NUMERAL", "NOUN": "NOUN", "FISH-CLASS NOUN": "NOUN", "TITLE ELEMENT": "TITLE ELEMENT",
              "CLOSER": "CLOSER", "BRACKETED-FISH CLOSER": "CLOSER", "POST-CLOSER CLITIC": "CLITIC"}
ROLES = ["OPENER", "CONNECTIVE", "NUMERAL", "NOUN", "TITLE ELEMENT", "CLOSER", "CLITIC", "UNK"]


def lexicon_roles():
    out = {}
    for r in csv.DictReader(open(ROOT / "experiments/functional_reading/lexicon.csv")):
        if r["kind"] != "sign" or not r["roles"].strip():
            continue
        best, bw = None, -1
        for part in r["roles"].split(";"):
            name, w = part.strip().rsplit(" ", 1)
            if float(w) > bw:
                best, bw = name, float(w)
        out[r["item"]] = ROLE_MERGE.get(best, "UNK")
    return out


# ---------- periods (binary, fixed in the prereg) ----------
ROMAN = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7}


def binary_period(t):
    """Return (dataset, 0=early/1=late) or None."""
    s, per, ph = t["site"], t["period"].strip(), t["phase"].strip()
    if s == "Mohenjo-daro":
        return ("MD", {"Early": 0, "Intermediate": 0, "Late": 1}[per]) if per in ("Early", "Intermediate", "Late") else None
    if s == "Harappa":
        m = re.match(r"Stratum\s+([IV]+)\s*$", ph)
        if m and m.group(1) in ROMAN:
            return ("HAR_VATS", 0 if ROMAN[m.group(1)] >= 4 else 1)
        if per == "3" and ph in ("B", "B?", "B/C"):
            return ("HAR_HARP", 0)
        if per == "3" and ph == "C":
            return ("HAR_HARP", 1)
        return None
    if s == "Dholavira":
        if per == "4": return ("DHO", 0)
        if per in ("5", "5?", "6"): return ("DHO", 1)
        return None
    if s == "Lothal":
        if ph in ("II", "III"): return ("LOT", 0)
        if ph == "IV": return ("LOT", 1)
        return None
    if s == "Kalibangan":
        if per != "2": return None
        return {"Early": ("KAL", 0), "Middle": ("KAL", 0), "Late": ("KAL", 1)}.get(ph)
    return None


SEAL_TYPES = ("SEAL:S", "SEAL:R", "SEAL")


def area(t):
    try:
        return float(t["width_mm"]) * float(t["height_mm"])
    except (ValueError, TypeError):
        return 0.0


def site_group(s):
    return {"Mohenjo-daro": "MD", "Harappa": "HAR", "Dholavira": "DHO", "Lothal": "LOT"}.get(s, "OTHER")
