"""Shared numeral inventory and group extraction for numeral_grammar.

Values read by eye from Mahadevan's drawings (data/sign_images) and the Wells glyph sheet
(sources/paragorth_Indus-/data/derived/dark/loop57_images/wells_glyphs_sheet0.png), 2026-11-15.
Corrections to shaunmortal stroke_signs.json: M122 is 12 in brackets (4/4/4), not 5;
M113 is 7 in brackets (4/3); M101 is 2 as 1-over-1; M115 is 9 in one row;
M119/M120 are chevron groups of 8 (2/3/3) and 9 (3/3/3); M315 has 7 arcs.
"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from corpus.load import m77_texts, icit_texts, distinct, dev_heldout, runs  # noqa

# sign -> (class, value, layout)
M_NUM = {
    # short strokes
    "M97": ("S", 1, "1"), "M98": ("S", 1, "1 low"),
    "M99": ("C", 2, "2 (connective)"), "M100": ("S", 2, "2"), "M101": ("S", 2, "1/1"),
    "M102": ("S", 3, "3"), "M103": ("S", 3, "2/1"),
    "M104": ("S", 4, "4"), "M105": ("S", 4, "2/2"),
    "M106": ("S", 5, "5"), "M107": ("S", 5, "3/2"),
    "M108": ("S", 6, "6"), "M109": ("S", 6, "3/3"),
    "M110": ("S", 7, "7"), "M111": ("S", 7, "(7)"), "M112": ("S", 7, "4/3"), "M113": ("S", 7, "(4/3)"),
    "M114": ("S", 8, "4/4"),
    "M115": ("S", 9, "9"), "M116": ("S", 9, "5/4"), "M117": ("S", 9, "roof 5/4"),
    "M118": ("S", 10, "5/5"),
    "M121": ("S", 12, "4/4/4"), "M122": ("S", 12, "(4/4/4)"),
    # tall strokes
    "M86": ("T", 1, "1"), "M87": ("T", 2, "2"), "M88": ("T", 3, "3 dotted"), "M89": ("T", 3, "3"),
    "M92": ("T", 3, "roof 3"), "M93": ("T", 3, "3 slant"), "M94": ("T", 3, "3 slant"),
    "M95": ("T", 4, "4"), "M96": ("T", 5, "5"),
    # chevrons and arcs
    "M119": ("V", 8, "chevron 2/3/3"), "M120": ("V", 9, "chevron 3/3/3"),
    "M312": ("A", 1, "arc"), "M313": ("A", 2, "2 arcs"), "M314": ("A", 3, "3 arcs"), "M315": ("A", 7, "7 arcs"),
}

W_NUM = {
    "W001": ("S", 1, "1"), "W002": ("C", 2, "2 (connective)"), "W003": ("S", 3, "3"), "W004": ("S", 4, "4"),
    "W005": ("S", 5, "5"), "W006": ("S", 6, "6"), "W007": ("S", 7, "7"),
    "W012": ("S", 2, "1/1"), "W013": ("S", 3, "2/1"), "W014": ("S", 4, "2/2"), "W015": ("S", 5, "3/2"),
    "W016": ("S", 6, "3/3"), "W017": ("S", 7, "4/3"), "W018": ("S", 8, "4/4"), "W019": ("S", 9, "5/4"),
    "W020": ("S", 10, "5/5"),
    "W025": ("D", 5, "dots 2/2/1"), "W026": ("D", 5, "dots 2/1/2"), "W027": ("D", 7, "dots 2/3/2"),
    "W028": ("D", 8, "dots 3/3/2"),
    "W029": ("V", 9, "chevron 3/3/3"), "W059": ("V", 8, "chevron (slanted)"),
    "W031": ("T", 1, "1"), "W032": ("T", 2, "2"), "W033": ("T", 3, "3"), "W034": ("T", 4, "4"),
    "W035": ("T", 5, "5"), "W036": ("T", 6, "6"), "W037": ("T", 7, "7"), "W039": ("T", 8, "8 thin"),
    "W042": ("T", 3, "3 dotted"), "W043": ("T", 4, "4 dotted"), "W044": ("T", 3, "roof 3"),
    "W047": ("T", 3, "(3)"),
    "W048": ("S", 7, "(4/3)"), "W049": ("S", 7, "(7)"), "W050": ("S", 9, "(9?)"), "W051": ("S", 9, "roof 5/4"),
    "W055": ("S", 12, "4/4/4"), "W056": ("S", 21, "7/7/7 (4+3 per row)"), "W057": ("S", 12, "(4/4/4)"),
}

M77_SITES = {"Mohenjodaro", "Harappa", "Lothal", "Kalibangan", "Chanhudaro"}


def groups_from_runs(seq, table, keep_conn=False):
    """Yield (group, prev_sign, next_sign, pos) for maximal runs of adjacent numeral signs.
    group = list of (sign, class, value). Connective (class C) breaks a group unless keep_conn."""
    out = []
    for r in runs(seq):
        i = 0
        while i < len(r):
            def isnum(s):
                return s in table and (keep_conn or table[s][0] != "C")
            if isnum(r[i]):
                j = i
                while j < len(r) and isnum(r[j]):
                    j += 1
                g = [(s,) + table[s][:2] for s in r[i:j]]
                out.append(dict(group=g, prev=r[i - 1] if i > 0 else None,
                                next=r[j] if j < len(r) else None, start=i, end=j, runlen=len(r)))
                i = j
            else:
                i += 1
    return out


def key(g):
    return " + ".join(f"{c}{v}" for _, c, v in g)
