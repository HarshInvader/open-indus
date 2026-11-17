"""Mackay 1938 (FEM) vol. I, 'Tabulation of Seals' pp. 370-391 (archive.org in.ernet.dli.2015.70071,
djvu word boxes, leaves 392-413) -> fem_seals.csv.
Columns: No | Type | Dimensions (in.) | Material | Block | House | Room | Level (ft) | Field No.
Run: .venv/bin/python -I experiments/old_registers/parse_fem.py
"""
import csv, os, pickle, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from tablib import deskew, cut_rows, num, inches

W = pickle.load(open(os.path.join(HERE, "work/in.ernet.dli.2015.70071.words.pkl"), "rb"))
HEAD = ["Type", "Dimensions", "Material", "Block", "House", "Room", "Level", "Field"]


def header_x(words):
    fy = [y for x0, x1, y, t in words if t.startswith("Dimens")]
    if not fy:
        return {}, 0
    y0 = fy[0]
    hx = {}
    for x0, x1, y, t in words:
        for h in HEAD:
            if h not in hx and t.lower().startswith(h.lower()[:5]) and abs(y - y0) < 90:
                hx[h] = x0
    return hx, y0 + 45


def level(tokens):
    s = " ".join(tokens)
    if re.search(r"surf", s, re.I):
        return "surface"
    sign = "+" if re.search(r"\+|-\|-|-f|-\(-|-j|-I-|-1-|4-", s) else "-"
    d = re.sub(r"[^0-9IlOo]", "", s).translate(str.maketrans("IlOo", "1100"))
    if not d or len(d) > 3:
        return ""
    v = int(d) / 10 if len(d) >= 2 else float(d)
    return f"{sign}{v:.1f}"


rows_out = []
prev_hx = {}
for leaf in range(391, 414):
    w, words = W[leaf]
    ds, slope = deskew(words)
    hx, ymin = header_x(ds)
    xs_no = [x0 for x0, x1, y, t in ds if t.startswith("No") and abs(y - ymin) < 140]
    x_no = min(xs_no) if xs_no else min(x0 for x0, *_ in ds)
    if len(hx) < 6:
        hx = {k: v + (x_no - prev_hx.get("_no", x_no)) for k, v in prev_hx.items() if k != "_no"}
    hx["_no"] = x_no
    prev_hx = dict(hx)
    bounds = sorted((v, k) for k, v in hx.items() if k != "_no")
    def col(x):
        c = "No"
        for v, k in bounds:
            if x >= v - 25:
                c = k
        return c
    is_anchor = lambda t: re.fullmatch(r"[0-9IlOo]{1,3}[A-C]?", t) is not None
    for a, ws in cut_rows(ds, is_anchor, x_no + 80, ymin=ymin):
        cells = {}
        for x0, x1, y, t in sorted(ws):
            cells.setdefault(col(x0), []).append(t)
        no = num(a[3][:-1]) + a[3][-1] if a[3][-1] in "ABC" else num(a[3])
        dims_raw = " ".join(cells.get("Dimensions", []))
        parts = [p.split()[0] if p.split() else "" for p in re.split(r"\s*[xX×<>]\s*", dims_raw)]
        dims = [inches(p) if p not in ("?", "") else None for p in parts][:3]
        if not dims_raw and not cells.get("Level"):
            continue
        rows_out.append(dict(
            source="Mackay1938_FEM", serial=no, leaf=leaf,
            type=" ".join(cells.get("Type", [])), dims_raw=dims_raw,
            l_in=dims[0] if len(dims) > 0 else None, w_in=dims[1] if len(dims) > 1 else None, t_in=dims[2] if len(dims) > 2 else None,
            material=" ".join(cells.get("Material", [])),
            block=" ".join(cells.get("Block", [])), house=" ".join(cells.get("House", [])), room=" ".join(cells.get("Room", [])),
            level_raw=" ".join(cells.get("Level", [])), level_ft=level(cells.get("Level", [])),
            field_raw=" ".join(cells.get("Field", []))))

# drop prose rows, then repair OCR-misread serials from sequence order (tablib.seq_repair)
rows_out = [r for r in rows_out if not re.search(r"[a-wyzA-WYZ]{3,}", r["dims_raw"])]
from tablib import seq_repair
seq_repair(rows_out)

# carry material and field prefix down (ditto marks)
mat, pre = "Steatite", "DK"
for r in rows_out:
    m = re.search(r"(Steatite|Faience|Paste|Silver|Copper|Pottery|Ivory|Shell|Stone|Clay|Terra)", r["material"], re.I)
    if m:
        mat = m.group(1).capitalize()
    r["material_n"] = mat
    p = re.search(r"\b(DK|SD|VS|HR|DM|L)\b\.?\s*(H\.)?", r["field_raw"])
    if p:
        pre = p.group(1)
    d = re.findall(r"\d{2,5}", r["field_raw"].translate(str.maketrans("IlOo", "1100")))
    r["field_no"] = f"{pre} {d[-1]}" if d else ""
    r["findspot"] = " / ".join(x for x in (r["block"], r["house"], r["room"]) if x and x not in ("—", "-"))

with open(os.path.join(HERE, "fem_seals.csv"), "w", newline="") as fh:
    wr = csv.DictWriter(fh, fieldnames=list(rows_out[0]))
    wr.writeheader(); wr.writerows(rows_out)
ser = [r["serial"] for r in rows_out]
print(len(rows_out), "rows; distinct serials", len(set(ser)),
      "with level", sum(1 for r in rows_out if r["level_ft"]), "with field", sum(1 for r in rows_out if r["field_no"]),
      "with dims", sum(1 for r in rows_out if r["l_in"]))
