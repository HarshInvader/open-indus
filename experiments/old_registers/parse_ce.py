"""Mackay 1943 (Chanhu-daro Excavations 1935-36), 'Catalogue of illustrated objects', Pls. XLIX-LIII
(seal-amulets, seals, sealings; archive.org in.ernet.dli.2015.105167 djvu.txt, lines 23847-24185) -> ce_seals.csv.
Each entry: (plate no.). (field no.). colour/material. dims (ins.). Sq./Trench, loc., lev. (ft) + description.
Run: .venv/bin/python -I experiments/old_registers/parse_ce.py
"""
import csv, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
L = open(os.path.join(HERE, "raw/in.ernet.dli.2015.105167/ocr.txt"), encoding="utf-8").read().split("\n")[23846:24185]
txt = "\n".join(l.strip() for l in L if l.strip())
FIX = str.maketrans({"i": "1", "l": "1", "I": "1", "o": "0", "O": "0", "S": "5"})
PLATES = ["XLIX", "L", "LI", "LII", "LIII"]

entries, plate, last = [], None, 0
# split on entry starts "(n)" at line start or after newline
for m in re.finditer(r"(?m)^(Plate\s+(XLIX|LIII|LII|LI|L)\.|\(?([0-9il]{1,2}|[0-9]\s*[°'.][0-9]?)\s*[).\-T]\s*[.\-]?\s*[(C]\s*([0-9il^?]{2,4}[0-9il^?]?))", txt):
    if m.group(1).startswith("Plate"):
        plate, last = m.group(2), 0
        continue
    entries.append((m.start(), plate, m.group(3), m.group(4)))
rows = []
for i, (pos, plate, no_raw, fno) in enumerate(entries):
    end = entries[i + 1][0] if i + 1 < len(entries) else len(txt)
    body = txt[pos:end]
    body = re.split(r"\nPlate\s+L", body)[0].replace("\n", " ")
    no = re.sub(r"\D", "", no_raw.translate(FIX))
    rows.append(dict(plate=plate, no=no, field_no=fno.translate(FIX).replace("^", "?"), body=body))
# plate LIII header is lost in OCR: numbering restarting at 1 after LII means LIII
seen_lii = False
prev = 0
for r in rows:
    if r["plate"] == "LII":
        if seen_lii and r["no"].isdigit() and int(r["no"]) < prev - 5:
            r["plate"] = "LIII"
        seen_lii = True
    if r["plate"] == "LIII" or (r["plate"] == "LII" and any(x["plate"] == "LIII" for x in rows[:rows.index(r)])):
        r["plate"] = "LIII"
    prev = int(r["no"]) if r["no"].isdigit() else prev
out = []
for r in rows:
    b = r["body"]
    dims = re.search(r"([0-9io.]+\.[0-9io]+|\d)\s*(?:di\.)?\s*[Xx]\s*([0-9io?.\-]+)(?:\s*(?:th\.)?\s*[Xx]\s*([0-9io?.\-]+))?\s*(?:ins|th)", b)
    mat = re.search(r"(steat|St\.|pot|faience|fai\.|copper|silver|paste|ivory|shell|clay)", b, re.I)
    col = re.search(r"\b(Wh|Gr|Br|Bl|Yell|Cr|Lt\.\s*rd|Rd|Gy)\b", b)
    sq = re.search(r"((?:Cut\.,\s*)?(?:Mound\s+I+,\s*)?(?:sq\.|Sq\.|Trench)\s*[^,]+)", b)
    loc = re.search(r"loc\.\s*([0-9il1o ]{1,5}|no)\b", b)
    lev = re.search(r"lev\.\s*([+\-—–]|-f-?|-\|-|-\(-|-j-?|4-|T)?\s*([0-9il1o]{1,2})\s*[.\-]\s*([0-9il1o^])", b)
    sign = ""
    if lev:
        g = lev.group(1) or ""
        sign = "-" if g in ("-", "—", "–") else "+"
    def f(x):
        if not x: return None
        x = x.translate(FIX).replace("-", ".").strip(".")
        try:
            v = float(x); return v if 0.05 <= v <= 6 else None
        except ValueError:
            return None
    out.append(dict(source="Mackay1943_CE", plate=r["plate"], plate_no=r["no"], plate_ref=f"CE pl. {r['plate']}, {r['no']}",
                    field_no=r["field_no"], material=(mat.group(1).lower().replace("st.", "steat") if mat else ""),
                    colour=col.group(1) if col else "",
                    l_in=f(dims.group(1)) if dims else None, w_in=f(dims.group(2)) if dims else None, t_in=f(dims.group(3)) if dims else None,
                    findspot=(sq.group(1).strip() if sq else "") + (f", loc. {loc.group(1).translate(FIX).replace(' ', '')}" if loc else ""),
                    level_ft=(f"{sign}{int(lev.group(2).translate(FIX))}.{lev.group(3).translate(FIX).replace('^', '0')}" if lev else ""),
                    description=b[:400]))
with open(os.path.join(HERE, "ce_seals.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
from collections import Counter
print(len(out), Counter(r["plate"] for r in out), "level", sum(1 for r in out if r["level_ft"]), "dims", sum(1 for r in out if r["l_in"]))
