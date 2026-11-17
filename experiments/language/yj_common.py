"""Shared helpers for testing Yajnadevam's Sanskrit key (xlits.csv) and readings.

Reading order: the ICIT csv `text` field is stored as drawn; Yajnadevam reads it reversed,
which equals the reading order used in corpus/load.py (checked on +410-017+ -> 'hara',
+031-705-167+ -> 'vanAH', +740-615-495-240-002-861+ -> 'ravamARa').
"""
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "sources" / "field-cady_indus_valley_script_corpus"
EXT = Path(__file__).resolve().parent / "ext"

SLP_VOW = set("aAiIuUfFxXeEoO")
SLP_CONS = set("kKgGNcCjJYwWqQRtTdDnpPbBmyrlvSzshMH")


def load_key():
    """sign (3-digit str) -> value string, resolving empty values through `canonical`."""
    rows = list(csv.DictReader(open(SRC / "xlits.csv"), ))
    raw = {r["sign"]: r["xlit"] for r in rows}
    canon = {r["sign"]: r["canonical"] for r in rows}
    key = {}
    for s in raw:
        v = raw[s]
        if v == "" and canon.get(s):
            parts = canon[s].split("-")
            v = "".join(raw.get(p, "") for p in parts if p != s)
        key[s] = v.strip()
    return key


def load_inscriptions():
    return list(csv.DictReader(open(SRC / "inscriptions.csv")))


def text_signs(text):
    """csv text '+740-002-861+' -> reading-order list of 3-digit sign codes (None for unreadable)."""
    t = text.strip().strip("+")
    if not t:
        return []
    out = []
    for tok in re.split(r"[-+]", t)[::-1]:
        tok = tok.strip()
        if re.fullmatch(r"\d{3}", tok):
            out.append(tok)
        else:
            out.append(None)  # break, ligature notation 'a/b', illegible
    return out


# ---------------- consonant classes ----------------
# Coarse classes that the key's lower-case letters can stand for. Derived empirically by
# a1_free_choices.py (see RESULTS.md); used for the generous matcher.
KEY_CHAR_TO_SLP = {  # key letters are mostly plain consonants; map onto SLP1 base letters
    "k": "k", "g": "g", "c": "c", "j": "j", "t": "t", "d": "d", "n": "n", "p": "p", "b": "b",
    "m": "m", "y": "y", "r": "r", "l": "l", "v": "v", "s": "s", "h": "h",
}
BASE = {}
for grp in ["kKgG", "cC", "jJ", "wWtT", "qQdD", "pP", "bB", "nNRYM", "m", "y", "r", "l", "v",
            "Szs", "hH"]:
    for ch in grp:
        BASE[ch] = grp[0]


def skeleton_slp(word):
    """SLP1 word -> tuple of base consonant classes (vowels dropped)."""
    return tuple(BASE[c] for c in word if c in BASE)


_IAST = [("kh", "K"), ("gh", "G"), ("ch", "C"), ("jh", "J"), ("ṭh", "W"), ("ḍh", "Q"), ("th", "T"),
         ("dh", "D"), ("ph", "P"), ("bh", "B"), ("ai", "E"), ("au", "O"), ("ā", "A"), ("ī", "I"),
         ("ū", "U"), ("ṛ", "f"), ("ṝ", "F"), ("ḷ", "x"), ("ṅ", "N"), ("ñ", "Y"), ("ṭ", "w"), ("ḍ", "q"),
         ("ṇ", "R"), ("ś", "S"), ("ṣ", "z"), ("ṃ", "M"), ("ṁ", "M"), ("ḥ", "H")]


def iast_to_slp(w):
    import unicodedata
    w = unicodedata.normalize("NFC", w.lower())
    for a, b in _IAST:
        w = w.replace(a, b)
    return "".join(ch for ch in w if ch.isascii() and ch.isalpha())
