"""Vats 1940 (EH) vol. I, 'Harappa: Tabulation of Seals (Pls. LXXXV-CI)' pp. 337-356
(archive.org in.ernet.dli.2015.537391, djvu word boxes, leaves 363-384) -> eh_seals.csv.
Columns: Plate No. | Size (in.) | Level below surface | Type | Steatite | Faience | Pottery (colour) |
Mound or Area | Find No.   Run: .venv/bin/python -I experiments/old_registers/parse_eh.py
"""
import csv, os, pickle, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from tablib import deskew, cut_rows, num, inches, seq_repair

W = pickle.load(open(os.path.join(HERE, "work/in.ernet.dli.2015.537391.words.pkl"), "rb"))
HEAD = {"Size": "Size", "Level": "Level", "Type": "Type", "Steatite": "Steatite", "Faience": "Faience",
        "Pottery": "Pottery", "Mound": "Mound", "Find": "Find"}


def header(words):
    ys = [y for x0, x1, y, t in words if t.lower().startswith("steatite")]
    if not ys:
        return {}, 0
    y0 = ys[0]
    hx = {}
    for x0, x1, y, t in words:
        for h in HEAD:
            if h not in hx and t.lower().startswith(h.lower()[:4]) and abs(y - y0) < 110:
                hx[h] = x0
    return hx, y0 + 25


def depth(tokens):
    s = " ".join(tokens)
    if re.search(r"surf", s, re.I):
        return "surface", s
    m = re.findall(r"(\d{1,2})\s*['’`]\s*([0-9IlO]{1,2})?", s.replace("O'", "0'").replace("o'", "0'"))
    if not m:
        return "", s
    vals = []
    for ft, inch in m:
        inch = inch.translate(str.maketrans("IlO", "110")) if inch else "0"
        i = int(inch) if inch.isdigit() else 0
        if i > 11:
            i = int(str(i)[0])
        vals.append(int(ft) + i / 12)
    return f"{-sum(vals) / len(vals):.2f}", s  # mean if a range 'x to y'


rows_out, prev = [], {}
for leaf in range(363, 385):
    w, words = W[leaf]
    ds, _ = deskew(words)
    hx, ymin = header(ds)
    xs = [x0 for x0, x1, y, t in ds if t.startswith("Plate") and abs(y - ymin) < 200]
    x_no = min(xs) if xs else min(x0 for x0, *_ in ds)
    if len(hx) < 6:
        hx = {k: v + (x_no - prev.get("_no", x_no)) for k, v in prev.items() if k != "_no"}
    hx["_no"] = x_no
    prev = dict(hx)
    bounds = sorted((v, k) for k, v in hx.items() if k != "_no")
    # material columns are narrow; colour word sits under one of them
    def col(x):
        c = "No"
        for v, k in bounds:
            if x >= v - 30:
                c = k
        return c
    is_anchor = lambda t: re.fullmatch(r"[0-9IlOoSs]{1,3}[a-c]?", t) is not None
    for a, ws in cut_rows(ds, is_anchor, x_no + 110, ymin=ymin):
        cells = {}
        for x0, x1, y, t in sorted(ws):
            cells.setdefault(col(x0), []).append((x0, t))
        toks = [t for x0, x1, y, t in sorted(ws)]
        row = " ".join(toks)
        # content-based fields (column x positions drift too much between pages)
        msz = re.search(r"(\?|[0-9][0-9.\-*'’‘•,]*)\s*[xX×]\s*(\?|[0-9][0-9.\-*'’‘•,]*)", row)
        dims = [inches(msz.group(1)) if msz and msz.group(1) != "?" else None, inches(msz.group(2)) if msz and msz.group(2) != "?" else None]
        rest = row[msz.end():] if msz else row
        mlev = re.search(r"(From\s+(surface|spoil)|Surface|\d{1,2}\s*['’`]\s*[0-9IlOo]{0,2}\s*[\"*'’]?(\s*to\s*\d{1,2}\s*['’`]\s*[0-9IlOo]{0,2}\s*[\"*'’]?)?)", rest)
        dft, draw = depth([mlev.group(0)]) if mlev else ("", "")
        if mlev and "spoil" in mlev.group(0).lower():
            dft = "spoil"
        rest2 = rest[mlev.end():] if mlev else rest
        mty = re.match(r"\s*([a-z]{1,2}(\(\?\))?)\b", rest2)
        typ = mty.group(1) if mty else ""
        mcol = re.search(r"(White|Blue|Bluish|Grey|Gray|Black|Green|Yellow|Red|Light red|Brown|Bine|Wliite|Whit)", rest2)
        colour = mcol.group(1).replace("Bine", "Blue").replace("Wliite", "White") if mcol else ""
        tail = rest2[mcol.end():] if mcol else rest2
        mm = re.search(r"\b(AB|F|D|G|H|E|J|K|L|r)\b\s*[^A-Za-z0-9]*\s*([A-Za-z]{0,4}[\s\-]?[0-9IlOo]{1,6}[a-z]?(?:[\-.][0-9]+)?)\s*$", tail)
        mound = (mm.group(1).replace("r", "F")) if mm else ""
        find = mm.group(2).replace(" ", "") if mm else re.sub(r"[^A-Za-z0-9\-]", "", tail.split()[-1]) if tail.split() else ""
        sr = a[3]
        rows_out.append(dict(source="Vats1940_EH", serial=num(sr) + (sr[-1] if sr[-1] in "abc" else ""), leaf=leaf,
                             row_raw=row, size_raw=msz.group(0) if msz else "", l_in=dims[0], w_in=dims[1],
                             level_raw=draw, depth_ft=dft, type=typ, colour=colour, mound=mound, find_raw=find))
rows_out = [r for r in rows_out if r["size_raw"] or r["level_raw"] or r["find_raw"]]
rows_out = [r for r in rows_out if not re.search(r"[a-z]{5,}", r["row_raw"].replace("White", "").replace("surface", "").replace("Yellow", "").replace("Bluish", "").replace("spoil", "").replace("Green", "").replace("Black", "").replace("diam", ""))]
seq_repair(rows_out)
for r in rows_out:
    r["mound_n"] = r["mound"]
    r["find_no"] = r["find_raw"]
with open(os.path.join(HERE, "eh_seals.csv"), "w", newline="") as fh:
    wr = csv.DictWriter(fh, fieldnames=list(rows_out[0]))
    wr.writeheader(); wr.writerows(rows_out)
print(len(rows_out), "rows; distinct", len({r["serial"] for r in rows_out}), "depth", sum(1 for r in rows_out if r["depth_ft"]),
      "dims", sum(1 for r in rows_out if r["l_in"]), "find", sum(1 for r in rows_out if r["find_no"]))
