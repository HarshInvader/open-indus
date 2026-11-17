"""Render a PDF page region at high dpi and save.
python -I crop.py pdf page(1-based) x0 y0 x1 y1 out.png [dpi]
coords are fractions (0-1) of page width/height."""
import sys
import pymupdf

pdf, page, x0, y0, x1, y1, out = sys.argv[1:8]
dpi = int(sys.argv[8]) if len(sys.argv) > 8 else 300
doc = pymupdf.open(pdf)
p = doc[int(page) - 1]
r = p.rect
clip = pymupdf.Rect(r.x0 + float(x0) * r.width, r.y0 + float(y0) * r.height,
                    r.x0 + float(x1) * r.width, r.y0 + float(y1) * r.height)
pix = p.get_pixmap(dpi=dpi, clip=clip)
pix.save(out)
print(out, pix.width, pix.height)
