"""Rebuild table rows from archive.org djvu.xml word boxes (untrusted data; run with python -I).

pages(path) -> list of pages; each page = list of rows; each row = list of (x0, text) sorted by x.
Rows are formed by clustering words on vertical centre (tolerance ~ half median word height).
"""
import re
import xml.etree.ElementTree as ET


def _words(page_el):
    out = []
    for w in page_el.iter("WORD"):
        t = (w.text or "").strip()
        c = w.get("coords")
        if not t or not c:
            continue
        x0, y1, x1, y0 = (int(v) for v in c.split(",")[:4])  # djvu: left,bottom,right,top
        out.append((x0, x1, min(y0, y1), max(y0, y1), t))
    return out


def rows_of(words, tol=None):
    if not words:
        return []
    hs = sorted(w[3] - w[2] for w in words)
    med = hs[len(hs) // 2] or 20
    tol = tol or med * 0.55
    ws = sorted(words, key=lambda w: (w[2] + w[3]) / 2)
    rows, cur, cy = [], [], None
    for w in ws:
        y = (w[2] + w[3]) / 2
        if cy is None or abs(y - cy) <= tol:
            cur.append(w)
            cy = sum((v[2] + v[3]) / 2 for v in cur) / len(cur)
        else:
            rows.append(cur)
            cur, cy = [w], y
    if cur:
        rows.append(cur)
    return [sorted(((w[0], w[4]) for w in r)) for r in rows]


def pages(path):
    out = []
    for _, el in ET.iterparse(path, events=("end",)):
        if el.tag == "OBJECT":
            out.append(rows_of(_words(el)))
            el.clear()
    return out


def page_text(rows):
    return "\n".join(" ".join(t for _, t in r) for r in rows)


if __name__ == "__main__":
    import sys
    P = pages(sys.argv[1])
    lo, hi = int(sys.argv[2]), int(sys.argv[3])
    for i in range(lo, hi + 1):
        print(f"===== leaf {i}")
        print(page_text(P[i]))


def page_words(path):
    """list (per leaf) of word tuples (x0, x1, ytop, ybot, text) plus page width."""
    out = []
    for _, el in ET.iterparse(path, events=("end",)):
        if el.tag == "OBJECT":
            out.append((int(el.get("width") or 0), _words(el)))
            el.clear()
    return out
