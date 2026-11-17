"""Marshall 1931 (MIC) vol. II pp. 402-405 'Mohenjo-daro: Tabulation of Seals' (archive.org
in.ernet.dli.2015.107493, djvu word boxes, leaves 55-58; two tables side by side per page) -> mic_seals.csv.
Columns: Serial | Size (in.) | Level below surface | Type | Materials and colour | Site and No.
Run: .venv/bin/python -I experiments/old_registers/parse_mic.py
"""
import csv, os, pickle, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from tablib import deskew, cut_rows, num, inches, seq_repair

W = pickle.load(open(os.path.join(HERE, "work/in.ernet.dli.2015.107493.words.pkl"), "rb"))
FIELD = re.compile(r"\b(HR|VS|DK|SD|DM|L|C|E|F|D|B|A|R|BJ|UR|MR|DR)\b[\s.,'‘]*([0-9IlOoSs,]{1,6}[a-z]?)\s*$")

rows_out = []
for leaf in range(55, 59):
    w, words = W[leaf]
    ds, _ = deskew(words)
    hy = [y for x0, x1, y, t in ds if t.lower().startswith(("surface", "sur fa", "s'l"))]
    ymin = (max(hy) + 30) if hy else 450
    mid = w / 2
    for half in (0, 1):
        H = [d for d in ds if (d[0] < mid - 40) == (half == 0)]
        if not H:
            continue
        body = [d for d in H if d[2] > ymin]
        x_no = min(d[0] for d in body)
        is_anchor = lambda t: re.fullmatch(r"[0-9IlOoSs=+'‘’■\-]{1,4}", t) is not None and len(num(t)) >= 1
        for a, ws in cut_rows(H, is_anchor, x_no + 60, ymin=ymin):
            row = " ".join(t for x0, x1, y, t in sorted(ws))
            sr = num(a[3])
            msz = re.match(r"\s*(\S+)\s*(?:[xX×<>/y\\]|[\.,]\s)?\s*(\S+)?", row)
            szs = re.findall(r"([0-9IlOoS][0-9IlOoS'’‘•*\-.,= ]{0,4}[0-9IlOoS])", row.split("'")[0] if "'" in row else row)
            dims = [inches(z.replace(" ", "")) for z in szs[:2]]
            mlev = re.search(r"(\d{1,2}|[IlSsz])\s*['’]\s*([0-9IlOo]{0,2})\s*[\"”'’^]?|Sur\.?", row)
            if mlev and mlev.group(0).lower().startswith("sur"):
                lev = "surface"
            elif mlev:
                ft = num(mlev.group(1)) or "0"
                inch = num(mlev.group(2)) or "0"
                i = int(inch) if int(inch) < 12 else int(inch[0])
                lev = f"{-(int(ft) + i / 12):.2f}"
            else:
                lev = ""
            mf = FIELD.search(row)
            fld = f"{mf.group(1)} {num(mf.group(2))}" if mf else ""
            rows_out.append(dict(source="Marshall1931_MIC", serial=sr, leaf=leaf, half=half, row_raw=row,
                                 l_in=dims[0] if dims else None, w_in=dims[1] if len(dims) > 1 else None,
                                 level_ft=lev, field_no=fld))
# within each half-column the serials run consecutively
out = []
for leaf in range(55, 59):
    for half in (0, 1):
        part = [r for r in rows_out if r["leaf"] == leaf and r["half"] == half]
        seq_repair(part)
        out += part
rows_out = [r for r in out if r["row_raw"].strip()]
with open(os.path.join(HERE, "mic_seals.csv"), "w", newline="") as fh:
    wr = csv.DictWriter(fh, fieldnames=list(rows_out[0]))
    wr.writeheader(); wr.writerows(rows_out)
print(len(rows_out), "rows; distinct", len({r["serial"] for r in rows_out}), "level", sum(1 for r in rows_out if r["level_ft"]),
      "field", sum(1 for r in rows_out if r["field_no"]), "dims", sum(1 for r in rows_out if r["l_in"]))
