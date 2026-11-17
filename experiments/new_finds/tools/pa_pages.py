"""Contact sheets of PDF pages that contain images.
python -I pa_pages.py pdf outprefix [dpi=40] [per_sheet=12] [cols=4] [first-last]
Writes outprefix_N.png; tiles labelled with page numbers (1-based)."""
import sys
import pymupdf
from PIL import Image, ImageDraw

pdf, pre = sys.argv[1], sys.argv[2]
dpi = int(sys.argv[3]) if len(sys.argv) > 3 else 40
per = int(sys.argv[4]) if len(sys.argv) > 4 else 12
cols = int(sys.argv[5]) if len(sys.argv) > 5 else 4
doc = pymupdf.open(pdf)
rng = range(len(doc))
if len(sys.argv) > 6:
    a, b = sys.argv[6].split("-")
    rng = range(int(a) - 1, min(int(b), len(doc)))
pages = [i for i in rng if doc[i].get_images() or len(sys.argv) > 6]
tiles = []
for i in pages:
    pix = doc[i].get_pixmap(dpi=dpi)
    tiles.append((i + 1, Image.frombytes("RGB", (pix.width, pix.height), pix.samples)))
for s in range(0, len(tiles), per):
    chunk = tiles[s:s + per]
    w = max(t.width for _, t in chunk)
    h = max(t.height for _, t in chunk)
    rows = (len(chunk) + cols - 1) // cols
    sh = Image.new("RGB", (cols * w, rows * (h + 16)), "white")
    d = ImageDraw.Draw(sh)
    for k, (pn, t) in enumerate(chunk):
        x, y = (k % cols) * w, (k // cols) * (h + 16)
        sh.paste(t, (x, y + 16))
        d.text((x + 4, y + 2), f"p{pn}", fill="red")
    sh.save(f"{pre}_{s // per}.png")
print(len(doc), "pages;", "image pages:", [p for p, _ in tiles])
