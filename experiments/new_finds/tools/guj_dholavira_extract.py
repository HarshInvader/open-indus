"""Extract per-object photos from Bisht 2015 Dholavira report catalogue tables.
Usage: python -I guj_dholavira_extract.py report.pdf outdir firstpage lastpage prefix
Writes outdir/<prefix>_sl<N>_acc<ACC>.jpg (clip rendered at 300 dpi) and outdir/<prefix>_index.json
"""
import json
import os
import re
import sys

import pymupdf

pdf, out, a, b, prefix = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
os.makedirs(out, exist_ok=True)
doc = pymupdf.open(pdf)
index = []
for pno in range(a - 1, b):
    page = doc[pno]
    words = page.get_text("words")  # x0,y0,x1,y1,word,block,line,wno
    W = page.rect.width
    # rows: "N." in the leftmost column
    rows = []
    for w in words:
        if w[0] < W * 0.2 and re.fullmatch(r"\d{1,3}\.", w[4]):
            rows.append((w[1], int(w[4][:-1]), w[2]))
    rows.sort()
    if not rows:
        continue
    infos = [i for i in page.get_image_info(xrefs=True) if (i["bbox"][2] - i["bbox"][0]) > 40]
    for k, (y, sl, xr) in enumerate(rows):
        ynext = rows[k + 1][0] if k + 1 < len(rows) else page.rect.height
        # acc no: first all-digit word right of sl column near the row
        cand = [w for w in words if w[0] > xr and w[0] < W * 0.3 and re.fullmatch(r"\d{2,6}", w[4]) and y - 15 < w[1] < ynext]
        cand.sort(key=lambda w: w[1])
        acc = cand[0][4] if cand else "NA"
        text = " ".join(w[4] for w in sorted(
            [w for w in words if w[0] > W * 0.12 and y - 15 < w[1] < ynext - 2 and w[0] < W * 0.72],
            key=lambda w: (w[5], w[6], w[7])))
        # render the photo cell band of this row; page clip paths hide image overflow
        x0 = W * float(os.environ.get("PX0", "0.63"))
        x1 = W * float(os.environ.get("PX1", "0.93"))
        r = pymupdf.Rect(x0, y - 8, x1, min(ynext - 6, page.rect.height - 40))
        files = []
        if any(pymupdf.Rect(i["bbox"]).intersects(r) for i in infos):
            pix = page.get_pixmap(dpi=300, clip=r)
            fn = f"{prefix}_sl{sl:03d}_acc{acc}.png"
            pix.save(os.path.join(out, fn))
            files.append(fn)
        index.append({"page": pno + 1, "sl": sl, "acc": acc, "text": text, "files": files})
json.dump(index, open(os.path.join(out, f"{prefix}_index.json"), "w"), indent=1)
print(len(index), "rows;", sum(len(r["files"]) for r in index), "images")
