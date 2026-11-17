"""Build craft_units.csv: craft indicators per findspot unit, coded from excavation
reports ONLY (no inscribed texts are read here).

Run (report OCR is untrusted data; read-only reuse of experiments/magnitude/raw):
  .venv/bin/python -I experiments/assemblage/build_coding.py \
      experiments/magnitude/raw/vats1940_v1/ocr.txt \
      experiments/magnitude/raw/mackay1938_v1/ocr.txt \
      experiments/magnitude/raw/marshall1931_v2/<file>_djvu.txt \
      sources/paragorth_Indus-/data/derived/lothal-sealings-frenez-tosi2005.json

Outputs experiments/assemblage/craft_units.csv with columns
  site, unit, craft, evidence, source
"""
import csv
import json
import re
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent

CRAFT_RE = {
    "BEAD": r"unfinished[^.;]{0,40}\bbeads?\b|\bbeads?\b[^.;]{0,30}unfinished|bead[- ]?(blank|core|making|maker)|\b(stone|chert|flint) drills?\b|\bdrills? of (chert|stone|flint)",
    "SHELL": r"\bconch|columell|unfinished[^.;]{0,30}shell|shell[^.;]{0,15}\b(core|cores|waste|cut|cutting|pieces|fragments|working|inlay pieces)\b|\bshells\b",
    "COPPER": r"crucible|\bslag\b|copper ore|\bfurnace|\bingot",
    "SEALCUT": r"unfinished[^.;]{0,40}\bseal|\bseal[^.;]{0,40}unfinished|seal in the making",
    "WEIGHT": r"(?<!loom-)(?<!loom )\bweights?\b(?!\s*[\d'*.:-]+\s*g)(?! with the)",
    "KILN": r"\bkilns?\b",
}
CRAFT_RE = {k: re.compile(v, re.I) for k, v in CRAFT_RE.items()}


def classify(text):
    t = re.sub(r"\s+", " ", text)
    return [k for k, r in CRAFT_RE.items() if r.search(t)]


rows = []


def add(site, unit, craft, evidence, source):
    rows.append({"site": site, "unit": unit, "craft": craft,
                 "evidence": re.sub(r"\s+", " ", evidence)[:200], "source": source})


# ---------------- Harappa: Vats 1940 item lists with grid squares ----------------
def vats(path):
    txt = Path(path).read_text(errors="replace")
    # line offsets for citations
    starts = [0]
    for m in re.finditer("\n", txt):
        starts.append(m.end())
    import bisect
    sq = re.compile(r"[Ss]quares?\s+([A-Z1l])\s*\.{0,2}\s*(\d{1,2})\s*/\s*[^\s;,.]{1,3}")
    prev_end = 0
    for m in sq.finditer(txt):
        letter = m.group(1).replace("1", "I").replace("l", "I")
        unit = f"{letter}{int(m.group(2))}"
        start = max(prev_end, m.start() - 350)
        window = txt[start:m.start()]
        # cut at the end of the previous item ("b.s." depth tail) if present
        cut = max(window.rfind("b.s"), window.rfind("b. s"), window.rfind("b.a"))
        if cut > 0:
            window = window[cut + 3:]
        prev_end = m.end()
        line = bisect.bisect_right(starts, m.start())
        for c in classify(window):
            add("Harappa", unit, c, window[-160:], f"Vats 1940 OCR line {line}")
        if re.search(r"Great Granary Area", txt[m.start() - 60:m.start()]):
            add("Harappa", unit, "STORAGE", "Mound F, Great Granary Area", f"Vats 1940 OCR line {line}")


# ---------------- Mohenjo-daro: Mackay 1938 object lists by block/house ----------------
ROMAN = {"I": 1, "V": 5, "X": 10, "L": 50}


def clean_roman(s):
    s = s.upper().replace("T", "I").replace("F", "V").replace(" ", "").replace("1", "I").replace("L", "I")
    return s if re.fullmatch(r"[IVX]+", s) else None


def mackay_lists(path):
    lines = Path(path).read_text(errors="replace").splitlines()
    for lo, hi, half in ((11859, 19334, "DKG. (S)"), (20344, 21400, "DKG. (N)")):
        block, house = None, None
        for i in range(lo - 1, min(hi, len(lines))):
            ln = lines[i].strip()
            mb = re.match(r"^Block\s+(\d+|l|lA|\d+A)\s*[A]?\.?\s*$", ln)
            if mb:
                b = mb.group(1).replace("l", "1")
                if ln.rstrip(".").endswith("A") and not b.endswith("A"):
                    b += "A"
                block, house = b, None
                continue
            mh = re.match(r"^Hou\w*\.?\s*([IVXTFl1 ]+)[.,]?\s*$", ln)
            if mh:
                house = clean_roman(mh.group(1))
                continue
            if block is None or not ln or ln.startswith("(") or re.match(r"^[-\d. ]+$", ln):
                continue
            unit = f"{half}|{block}|{house or '-'}"
            for c in classify(ln):
                if c == "SHELL" and not re.search(r"unfinished|worked|waste|core", ln, re.I):
                    continue  # finished shell objects are not working debris
                add("Mohenjo-daro", unit, c, ln, f"Mackay 1938 vol.1 OCR line {i+1} (object list)")


def vats_hand():
    src = "Vats 1940 OCR line"
    for c in ("SHELL", "SEALCUT", "BEAD"):
        add("Harappa", "J12", c, "group No. 10460, square J 12/23: four unfinished steatite seals, conch shells, shell cores ~4 lb, inlay pieces, unfinished bead; 'a shop or workshop'", f"{src} 8134-8170")
    for u in ("I13", "I14", "J13", "H14"):
        add("Harappa", u, "COPPER", "furnaces Fa-Fp in Trench IV, Mound F (slag, crucible use per Vats)", f"{src} 83071-83280")


def mackay_prose():
    # hand-coded from reading the block descriptions (line numbers in mackay1938_v1/ocr.txt)
    src = "Mackay 1938 vol.1 OCR line"
    add("Mohenjo-daro", "DKG. (S)|1|I", "KILN", "Two curious kilns on the eastern side of room 33 of the S. wing (Palace); Mackay: glazing/crucible", f"{src} 6404-6446")
    add("Mohenjo-daro", "DKG. (S)|1|I", "COPPER", "room 51: quantity of copper ore in small pieces ... a metal-smith worked here", f"{src} 6704-6710")
    add("Mohenjo-daro", "DKG. (S)|2|III", "KILN", "two pottery kilns in the northern part of the block (House III)", f"{src} 7268-7281")
    add("Mohenjo-daro", "DKG. (S)|9|II", "KILN", "court 21, 26, in which were two kilns, belonged to House II", f"{src} 9940-9989")


# ---------------- Mohenjo-daro: Marshall 1931 vol. II findspots ----------------
def marshall(path):
    txt = Path(path).read_text(errors="replace")
    import bisect
    starts = [0] + [m.end() for m in re.finditer("\n", txt)]
    pat = re.compile(r"House\s+([IVXL]{1,7})\s*,\s*Block\s+(\d+)\s*,?\s*(?:S\w{2,6}ion\s+([A-E]))?\s*,?\s*(?:of\s+(?:the\s+)?)?(HR|DK|VS)\s+Are", re.S)
    pat_vs = re.compile(r"House\s+([IVXL]{1,7})\s*,?\s*(?:of\s+(?:the\s+)?)?VS\s+Are")
    for p, kind in ((pat, "full"), (pat_vs, "vs")):
        for m in p.finditer(txt):
            window = txt[max(0, m.start() - 300):m.start()]
            # restrict to the current sentence-ish chunk
            window = re.split(r"No\.\s*\d+\s*\(", window)[-1]
            cs = classify(window)
            if not cs:
                continue
            if kind == "full":
                area = m.group(4) + (m.group(3) or "")
                unit = f"{area}|{m.group(2)}|{m.group(1)}"
            else:
                unit = f"VS*|*|{m.group(1)}"
            line = bisect.bisect_right(starts, m.start())
            for c in cs:
                if c == "SHELL" and not re.search(r"unfinished|waste|core|columell|conch", window, re.I):
                    continue
                add("Mohenjo-daro", unit, c, window[-160:], f"Marshall 1931 vol.II OCR line {line}")


# ---------------- Chanhu-daro: Mackay 1943 pp. 52-53 (squares) ----------------
def chanhu():
    src = "Mackay 1943 OCR (mackay1943/ocr.txt) lines"
    for s in ["8/C", "9/C", "9/D", "9/F"]:
        add("Chanhu-daro", s, "BEAD", "Large numbers of unfinished beads, together with the stone drills used for boring them", f"{src} 3818-3820")
    for s in ["8/C", "8/E", "9/D", "9/E", "9/F"]:
        add("Chanhu-daro", s, "WEIGHT", "Specimens of unfinished weights", f"{src} 3826-3829")
    for s in ["7/C", "7/E", "8/D", "8/F"]:
        add("Chanhu-daro", s, "SEALCUT", "Eight unfinished seals of the Harappa Period", f"{src} 3831-3832")
    for s in ["9/E", "7/D", "8/C", "8/D", "8/E", "9/C"]:
        add("Chanhu-daro", s, "SHELL", "unfinished bangles / unfinished shell dishes", f"{src} 3867-3871")
    add("Chanhu-daro", "9/D", "SHELL", "univalve shells in room 215 and other parts of Square 9/D", f"{src} 3873-3874")
    add("Chanhu-daro", "9/D", "COPPER", "Bead Factory with Furnace (215, 286, 287)", f"{src} 3188-3242")
    add("Chanhu-daro", "9/D", "KILN", "Bead Factory with Furnace (215, 286, 287)", f"{src} 3188-3242")
    add("Chanhu-daro", "9/E", "BEAD", "white paste plaques used in glazing near locus 137, bead-making quarter", f"{src} 3876-3878")


# ---------------- Lothal: Frenez & Tosi 2005 warehouse contexts ----------------
def lothal(path):
    d = json.load(open(path))
    for cisi, nimp, back, ctx in d["rows"]:
        if ctx in ("W", "W1", "W2"):
            add("Lothal", cisi, "STORAGE", f"sealing context {ctx} (warehouse), back {back}", "Frenez & Tosi 2005 Table 1 (paragorth transcription)")
        elif ctx == "O":
            add("Lothal", cisi, "NONE", f"sealing context O (outside warehouse), back {back}", "Frenez & Tosi 2005 Table 1 (paragorth transcription)")


if __name__ == "__main__":
    vats_p, mackay_p, marshall_p, lothal_p = sys.argv[1:5]
    vats(vats_p)
    vats_hand()
    mackay_lists(mackay_p)
    mackay_prose()
    marshall(marshall_p)
    chanhu()
    lothal(lothal_p)
    seen, out = set(), []
    for r in rows:
        k = (r["site"], r["unit"], r["craft"], r["source"])
        if k not in seen:
            seen.add(k); out.append(r)
    with open(OUT / "craft_units.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["site", "unit", "craft", "evidence", "source"])
        w.writeheader(); w.writerows(out)
    from collections import Counter
    print(len(out), "indicator rows")
    print(Counter((r["site"], r["craft"]) for r in out))
