"""Render PDF pages to PNG and dump page text hits.
Usage: python -I pdfpages.py file.pdf outdir [dpi] [pages e.g. 3-7,10]
       python -I pdfpages.py file.pdf --grep word1,word2   (list pages containing words)
       python -I pdfpages.py file.pdf --images outdir     (extract embedded images >= 200px)"""
import os
import sys

import pymupdf

pdf = sys.argv[1]
doc = pymupdf.open(pdf)
if sys.argv[2] == "--grep":
    words = [w.lower() for w in sys.argv[3].split(",")]
    for i, p in enumerate(doc):
        t = p.get_text().lower()
        hits = [w for w in words if w in t]
        if hits:
            print(i + 1, hits)
    sys.exit()
if sys.argv[2] == "--images":
    out = sys.argv[3]
    os.makedirs(out, exist_ok=True)
    for i, p in enumerate(doc):
        for j, img in enumerate(p.get_images(full=True)):
            pix = pymupdf.Pixmap(doc, img[0])
            if pix.width < 200 or pix.height < 200:
                continue
            if pix.n - pix.alpha >= 4:
                pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
            pix.save(os.path.join(out, f"p{i+1:03d}_{j}.png"))
    sys.exit()
out = sys.argv[2]
dpi = int(sys.argv[3]) if len(sys.argv) > 3 else 150
os.makedirs(out, exist_ok=True)
sel = None
if len(sys.argv) > 4:
    sel = set()
    for part in sys.argv[4].split(","):
        if "-" in part:
            a, b = part.split("-")
            sel.update(range(int(a), int(b) + 1))
        else:
            sel.add(int(part))
for i, p in enumerate(doc):
    if sel and (i + 1) not in sel:
        continue
    p.get_pixmap(dpi=dpi).save(os.path.join(out, f"p{i+1:03d}.png"))
print(len(doc), "pages")
