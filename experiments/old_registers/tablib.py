"""Shared helpers: deskew djvu word boxes and cut table rows anchored on a serial-number column."""
import re

DIG = str.maketrans({"I": "1", "l": "1", "i": "1", "O": "0", "o": "0", "S": "5", "s": "5", "Z": "2", "z": "2",
                     "B": "8", "G": "6", "g": "9", "q": "9", "t": "1", "?": "7"})


def deskew(words):
    best, bs = 0.0, -1
    for k in range(-40, 41):
        s = k * 0.0015
        h = {}
        for x0, x1, yt, yb, t in words:
            b = int(((yt + yb) / 2 - s * x0) // 5)
            h[b] = h.get(b, 0) + 1
        sc = sum(v * v for v in h.values())
        if sc > bs:
            best, bs = s, sc
    return [(x0, x1, (yt + yb) / 2 - best * x0, t) for x0, x1, yt, yb, t in words], best


def cut_rows(words, is_anchor, xmax_anchor, ymin=0, bias=0.0):
    """words: deskewed (x0,x1,y,t). Anchors: words with x0 < xmax_anchor and is_anchor(t).
    Returns list of (anchor_word, [words]) with each word assigned to nearest anchor (y + bias)."""
    A = sorted([w for w in words if w[0] < xmax_anchor and w[2] > ymin and is_anchor(w[3])], key=lambda w: w[2])
    # drop anchors too close to the previous one (split tokens like '1 1')
    B = []
    for a in A:
        if B and abs(a[2] - B[-1][2]) < 12:
            continue
        B.append(a)
    if not B:
        return []
    gaps = sorted(b[2] - a[2] for a, b in zip(B, B[1:])) or [60]
    g = gaps[len(gaps) // 2]
    rows = [(a, []) for a in B]
    for w in words:
        if w in B or w[2] <= ymin:
            continue
        y = w[2] + bias
        i = min(range(len(B)), key=lambda j: abs(B[j][2] - y))
        if abs(B[i][2] - y) < 0.6 * g:
            rows[i][1].append(w)
    return rows


def num(s):
    s = s.translate(DIG)
    s = re.sub(r"[^0-9]", "", s)
    return s


def inches(tok):
    """'1-05' / '1*05' / "1'05" / '105' -> float inches (decimal point lost by OCR). None if unparseable."""
    t = tok.replace("•", ".").replace("*", ".").replace("'", ".").replace("’", ".").replace("-", ".").replace("‘", ".").replace("·", ".").replace(",", ".")
    t = t.translate(DIG)
    t = re.sub(r"[^0-9.]", "", t).strip(".")
    if not t:
        return None
    if "." not in t:
        if len(t) == 1:
            return float(t)
        t = t[0] + "." + t[1:]
    try:
        v = float(t.split(".")[0] + "." + "".join(t.split(".")[1:]))
    except ValueError:
        return None
    return v if 0.05 <= v <= 8 else None


def seq_repair(rows, key="serial", maxstep=3):
    """In-place: rows in printed order; replace OCR-misread serials by a one-digit edit that continues
    the sequence (prev+1..prev+maxstep). Original kept in <key>_repaired."""
    prev = None
    for r in rows:
        r[key + "_repaired"] = ""
        s = r[key]
        if not s.isdigit():
            m = re.match(r"^(\d+)([A-Ca-c])$", s)
            if m:
                prev = int(m.group(1))
            continue
        v = int(s)
        if prev is None or prev + 1 <= v <= prev + maxstep:
            prev = v
            continue
        cands = set()
        for k in range(len(s)):
            for d in "0123456789":
                cands.add(int(s[:k] + d + s[k + 1:]))
        for k in range(len(s) + 1):
            for d in "0123456789":
                cands.add(int(s[:k] + d + s[k:]))
        if len(s) > 1:
            for k in range(len(s)):
                cands.add(int(s[:k] + s[k + 1:]))
        ok = sorted(c for c in cands if prev + 1 <= c <= prev + maxstep)
        if ok:
            r[key + "_repaired"] = s
            r[key] = str(ok[0])
            prev = ok[0]
        else:
            prev = v
