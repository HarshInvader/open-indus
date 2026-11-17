"""Automatic Vision readings of the 'Site and Serial No.' column on scans A and C (and B as a control),
used to confirm the manual transcription (reliability criterion 2).

Each deskewed page is cut into overlapping horizontal strips (both half-tables at once); Apple Vision
(experiments/old_registers/tools/vocr) reads each strip; area-code + number tokens are rebuilt from the
items, split by half-table, ordered by y, and aligned to the manual sequence of that half-table.
Output: vision_reads.csv (serial, scan, vision_key, match)
Run: .venv/bin/python -I experiments/fish_marshall/vision_read.py
"""
import difflib
import os
import re
import subprocess
import sys
import tempfile

import numpy as np
import pandas as pd
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from crops import straight  # noqa: E402
from segment import PAGES  # noqa: E402

VOCR = os.path.join(HERE, "..", "old_registers", "tools", "vocr")
CODES = r"(HR|VS|DK|SD|DM|BJ|MUS|C|E|L|D|B|A|F)"
TR = str.maketrans({"I": "1", "l": "1", "i": "1", "O": "0", "o": "0", "ı": "1", "І": "1", "О": "0", "о": "0"})


def norm_num(s):
    s = s.translate(TR)
    s = re.sub(r"[^0-9ab]", "", s)
    return s


def items(img):
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        img.save(f.name)
        out = subprocess.run([VOCR, f.name], capture_output=True, text=True).stdout
    os.unlink(f.name)
    res = []
    for ln in out.splitlines():
        if "\t" not in ln:
            continue
        b, t = ln.split("\t", 1)
        x, y, w, h = map(float, b.split())
        res.append((x, 1 - y - h, w, h, t.strip()))  # top-left origin, normalised
    return res


# site-column x-ranges and row y-range in 900-px-high preview units of crops/<scan>_<page>_full.png
COLS = {
    "A": {402: ((266, 316), (541, 602), (150, 676)), 403: ((268, 314), (541, 592), (150, 676)),
          404: ((260, 312), (538, 594), (150, 676)), 405: ((268, 317), (546, 594), (150, 676))},
    "C": {402: ((358, 414), (613, 672), (163, 722)), 403: ((288, 347), (608, 670), (150, 722)),
          404: ((363, 414), (613, 674), (160, 722)), 405: ((288, 347), (610, 670), (160, 722))},
    "B": {402: ((326, 412), (712, 830), None), 403: ((350, 454), (710, 810), None),
          404: ((340, 450), (710, 810), None), 405: ((350, 454), (724, 820), None)},
}
B_ROWS = {402: (156, 780), 403: (176, 992), 404: (170, 994), 405: (174, 994)}  # 1/6-scale units


def column_tokens(im, scan, pg, half):
    W, H = im.size
    xl, xr, yr = COLS[scan][pg]
    if scan == "B":
        f = 6.0
        yr = B_ROWS[pg]
    else:
        f = H / 900
    x0, x1 = (xl if half == 0 else xr)
    out = []
    step = 70
    for ya in range(int(yr[0]), int(yr[1]), step):
        yb = min(int(yr[1]), ya + step + 14)
        c = im.crop((int(x0 * f), int(ya * f), int(x1 * f), int(yb * f)))
        sc = 700 / max(c.size)
        if sc < 1:
            c = c.resize((int(c.width * sc), int(c.height * sc)))
        its = items(c)
        for x, y, w, h, t in its:
            out.append((x, ya * f + (y + h / 2) * (yb - ya) * f, t))
    # merge items on the same line (code and number read separately)
    out.sort(key=lambda r: r[1])
    rowh = (yr[1] - yr[0]) * f / 72
    lines = []
    for x, y, t in out:
        for L in lines:
            if abs(L["y"] - y) < rowh * 0.45:
                L["parts"].append((x, t)); break
        else:
            lines.append(dict(y=y, parts=[(x, t)]))
    toks = []
    for L in lines:
        txt = " ".join(t for x, t in sorted(L["parts"]))
        txt = re.sub(r"^\W*([ceCE(])\s+(?=[0-9IlOoiı])", lambda m: {"(": "C"}.get(m.group(1), m.group(1).upper()) + " ", txt)
        m = re.search(CODES + r"\s*[.,]?\s*([0-9IlOoiı]{1,4}[ab]?)", txt)
        if m:
            toks.append((L["y"], f"{m.group(1)} {norm_num(m.group(2))}"))
    # dedupe overlap: same token within half a row
    ded = []
    for y, t in sorted(toks):
        if not any(abs(y - y2) < rowh * 0.5 and t == t2 for y2, t2 in ded):
            ded.append((y, t))
    return [t for y, t in ded]


def main():
    man = []
    for ln in open(os.path.join(HERE, "manual_B.txt")):
        if ln.startswith("#") or not ln.strip():
            continue
        s, lev, a, f = [x.strip() for x in ln.split("|")]
        man.append((s, f"{a} {f.rstrip('?')}" if a != "?" else "?"))
    # serial order per page/half: 70 rows per half (b rows included in their half)
    halves = []
    i = 0
    for pg in (402, 403, 404, 405):
        for h in (0, 1):
            n = 70
            part = man[i:i + n + sum(1 for s, _ in man[i:i + n + 3] if s.endswith("b"))]
            # recompute exactly: take rows until 70 integer serials consumed
            part, cnt, j = [], 0, i
            while j < len(man) and cnt < 70:
                part.append(man[j]); cnt += 0 if man[j][0].endswith("b") else 1; j += 1
            while j < len(man) and man[j][0].endswith("b"):
                part.append(man[j]); j += 1
            halves.append((pg, h, part)); i = j
    recs = []
    for scan in sys.argv[1:] or ["A", "C", "B"]:
        for pg, name in PAGES[scan].items():
            im = Image.open(os.path.join(HERE, "crops", f"{scan}_{pg}_full.png"))
            ntok = 0
            for (p, h, part) in halves:
                if p != pg:
                    continue
                vt = column_tokens(im, scan, pg, h); ntok += len(vt)
                mk = [k for _, k in part]
                sm = difflib.SequenceMatcher(a=mk, b=vt, autojunk=False)
                matched = set()
                for blk in sm.get_matching_blocks():
                    for q in range(blk.size):
                        matched.add(blk.a + q)
                # also accept an exact token anywhere within +-3 positions (alignment slips)
                for q, k in enumerate(mk):
                    if q not in matched:
                        lo = max(0, int(q * len(vt) / max(1, len(mk))) - 4)
                        if k in vt[lo:lo + 9]:
                            matched.add(q)
                for q, (s, k) in enumerate(part):
                    recs.append(dict(serial=s, scan=scan, manual_key=k, match=q in matched))
            print(scan, pg, "tokens", ntok, file=sys.stderr)
    df = pd.DataFrame(recs)
    df.to_csv(os.path.join(HERE, "vision_reads.csv"), index=False)
    print(df.groupby("scan").match.mean())


if __name__ == "__main__":
    main()
