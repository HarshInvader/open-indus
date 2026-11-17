"""Parse CISI vol. 1 and 2 'Basic data for the objects illustrated' tables (Apple Vision OCR of the
archive.org jp2 page scans, work/vocr/*.tsv) into cisi_basic.csv:
    vol, page, cisi, num4 (second column, 4 digits), field_no (excavation/field number), rest (raw).
Rows are anchored on the CISI number (M-123, H-45, ...) and other OCR boxes are assigned to the
nearest anchor in y within the same half page.  Run: .venv/bin/python -I experiments/old_registers/parse_cisi.py
"""
import csv, glob, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from vrows import load

ANCH = re.compile(r"^([A-Z][a-z]{0,2}|[MHLKCB4])\s*[-.:/#]?\s*([0-9IlOHRN#T]{1,4}[A-Za-z]?)(\s*\((\d)\))?\b(.*)$")
FIX = str.maketrans({"I": "1", "l": "1", "O": "0", "H": "8", "R": "8", "N": "8", "#": "8", "T": "7"})


def norm_field(s):
    s = s.strip().replace("DK:", "DK").replace("DK.", "DK").replace("V5", "VS").replace("V3", "VS")
    m = re.match(r"^(DK|VS|HR|SD|DM|HM|L|UPM/MD|DK-[A-Gi1I])\s*[-.]?\s*([0-9]{1,5}[a-z]?)", s)
    if not m:
        return ""
    pre = m.group(1).replace("DK-1", "DK-i").replace("DK-I", "DK-i")
    return f"{pre} {m.group(2)}"


def parse_page(path, vol):
    items = load(path)
    out = []
    for half in (0, 1):
        H = [it for it in items if (it[0] < 0.5) == (half == 0)]
        if not H:
            continue
        x0 = min(it[0] for it in H)
        anchors = []
        for it in H:
            if it[0] - x0 > 0.03:
                continue
            m = re.match(r"^([MHLKC]|[A-Z][a-z]{1,2})\s*[-.:/]?\s*([0-9IlOHRN#T]{1,4})\b\s*(\(\d\))?\s*(.*)$", it[4])
            if m and (m.group(1) in "MHLKC" or len(m.group(1)) > 1):
                anchors.append((it, m))
        for it in H:
            pass
        A = []
        for it, m in anchors:
            num = m.group(2).translate(FIX)
            if not num.isdigit():
                continue
            A.append(dict(y=it[1], cisi=f"{m.group(1)}-{int(num)}", sub=(m.group(3) or ""), parts=[(it[0], m.group(4))]))
        if not A:
            continue
        ys = sorted(a["y"] for a in A)
        gap = sorted(b - a for a, b in zip(ys, ys[1:]))
        g = gap[len(gap) // 2] if gap else 0.009
        for it in H:
            if any(it is a_it for a_it, _ in anchors):
                continue
            best = min(A, key=lambda a: abs(a["y"] - it[1]))
            if abs(best["y"] - it[1]) < 0.55 * g:
                best["parts"].append((it[0], it[4]))
        for a in A:
            txt = " ".join(t for _, t in sorted(a["parts"]) if t).strip()
            m4 = re.match(r"^([0-9OIl]{4})\b\s*(.*)$", txt)
            num4 = m4.group(1).translate(FIX) if m4 else ""
            rest = m4.group(2) if m4 else txt
            out.append(dict(vol=vol, page=os.path.basename(path)[:-4], cisi=a["cisi"] + a["sub"], num4=num4,
                            field_no=norm_field(rest), rest=rest))
    return out


if __name__ == "__main__":
    rows = []
    for f in sorted(glob.glob(os.path.join(HERE, "work/vocr/*.tsv"))):
        rows += parse_page(f, 1 if os.path.basename(f).startswith("ind") else 2)
    with open(os.path.join(HERE, "cisi_basic.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    n = len(rows)
    print(n, "rows; num4", sum(1 for r in rows if r["num4"]), "field_no", sum(1 for r in rows if r["field_no"]))
