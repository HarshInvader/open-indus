"""Code Mohenjo-daro DK-G weight findspots from Hemmy's Appendix I ("Tabulation of
Weights") in Mackay 1938, Further Excavations at Mohenjo-daro, pp. 607-612.

This script reads report OCR ONLY. It never opens an inscribed text. Its output
(weights_md.csv, weight_units_md.csv) is hash-frozen before any text is joined.

Two independent OCRs of the same book are parsed and merged by field number:
  v1  experiments/magnitude/raw/mackay1938_v1/ocr.txt   (one table cell per line)
  v1b experiments/magnitude/raw/mackay1938_v1b/ocr.txt  (one table row per line)
A locus counts at house level only if its house is a clean Roman numeral in at least
one OCR and the two OCRs do not disagree. Otherwise the weight is kept at block
level only (house unknown) and is not used to label a house.

Run: .venv/bin/python -I experiments/weight_sign/build_weights.py
"""
import csv
import re
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
V1 = ROOT / "experiments/magnitude/raw/mackay1938_v1/ocr.txt"
V1B = ROOT / "experiments/magnitude/raw/mackay1938_v1b/ocr.txt"
ROMAN = re.compile(r"^(X{0,3})(IX|IV|V?I{0,3})$")


def clean_roman(s):
    s = s.strip().upper().replace("L", "I") if s.strip().upper() not in ("L",) else s
    return s if s and ROMAN.match(s) and s != "" else None


def parse_v1b():
    lines = open(V1B, errors="replace").read().splitlines()
    start = next(i for i, l in enumerate(lines) if "APPENDIX I.—TABULATION OF WEIGHTS" in l)
    out = {}
    for l in lines[start:start + 420]:
        m = re.match(r"^\s*(?:DK|px|[»,;nwyap5eo2‘’'\"]{1,3}|[a-z]{1,2})?\s*(\d{2,5})\b", l)
        if not m or "|" not in l:
            continue
        fno = m.group(1)
        # locus: block house room just before the depth column  e.g. "7 VOI 23] -163"
        loc = re.search(r"\|\s*(\d{1,2}A?)\s+([IVXLivxl]{1,5})\s+(\d{1,3})\s*[\]|}]\s*[-~=]?\s*[\d·.:-]+", l)
        street = re.search(r"(First|Central|West|East|Second|Third)\s+St", l)
        rec = {"fno": fno, "raw": l.strip()[:200]}
        if loc:
            rec.update(block=loc.group(1), house=loc.group(2), room=loc.group(3))
        elif street:
            rec.update(street=street.group(0))
        else:
            b = re.search(r"\|\s*(\d{1,2}A?)\s+\S{1,4}\s+(\d{1,3})\s*[\]|}]\s*[-~=]?\s*[\d·.:-]+", l)
            if b:
                rec.update(block=b.group(1), house=None, room=b.group(2))
        out.setdefault(fno, rec)
    return out


def parse_v1():
    lines = open(V1, errors="replace").read().splitlines()
    start = next(i for i, l in enumerate(lines) if "Tabulation of Weights" in l and i > 110000)
    end = start + 7200
    seg = [l.strip() for l in lines[start:end]]
    seg = [l for l in seg if l]
    out = {}
    last_fno = None
    for i, l in enumerate(seg):
        m = re.match(r"^(?:DK\s*)?(\d{2,5})\s*\.?\s*,?$", l)
        if m and i + 2 < len(seg) and re.match(r"^[X—~\-_.,/\\ ]{1,6}$", seg[i + 1]):
            last_fno = m.group(1)
            continue
        h = re.match(r"^([IVXL]{1,5})\s+(\d{1,3})$", l)
        if h and last_fno and last_fno not in out:
            prev = seg[i - 1] if i else ""
            b = re.search(r"(\d{1,2}A?)\s*\)?$", prev)
            out[last_fno] = {"fno": last_fno, "block": b.group(1) if b else None,
                             "house": h.group(1), "room": h.group(2), "raw": f"{prev} | {l}"}
    return out


def main():
    a, b = parse_v1b(), parse_v1()
    rows = []
    for fno in sorted(set(a) | set(b), key=int):
        ra, rb = a.get(fno, {}), b.get(fno, {})
        block = ra.get("block") or rb.get("block")
        if ra.get("block") and rb.get("block") and ra["block"] != rb["block"]:
            block_flag = "block_conflict"
        else:
            block_flag = ""
        ha = clean_roman(ra["house"]) if ra.get("house") else None
        hb = clean_roman(rb["house"]) if rb.get("house") else None
        if ha and hb and ha != hb:
            house, hflag = None, "house_conflict"
        else:
            house = ha or hb
            hflag = "" if house else ("house_unreadable" if block else "")
        street = ra.get("street", "")
        if block_flag:
            block, house = None, None
        level = "house" if (block and house) else ("block" if block else ("street" if street else "none"))
        rows.append({"field_no": fno, "block": block or "", "house": house or "", "room": ra.get("room") or rb.get("room") or "",
                     "street": street, "level": level, "flags": ";".join(x for x in (block_flag, hflag) if x),
                     "src_v1b": ra.get("raw", "")[:160], "src_v1": rb.get("raw", "")[:80]})
    with open(HERE / "weights_md.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    units = Counter((r["block"], r["house"]) for r in rows if r["level"] == "house")
    blocks = Counter(r["block"] for r in rows if r["block"])
    with open(HERE / "weight_units_md.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["block", "house", "n_weights", "source"])
        for (bl, ho), n in sorted(units.items()):
            w.writerow([bl, ho, n, "Hemmy in Mackay 1938, App. I pp. 607-612"])
    print("weights parsed:", len(rows), Counter(r["level"] for r in rows))
    print("house-level weight units:", len(units), "blocks with any weight:", len(blocks))
    print("flags:", Counter(r["flags"] for r in rows))


if __name__ == "__main__":
    main()
