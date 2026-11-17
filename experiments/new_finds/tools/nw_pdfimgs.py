"""Extract embedded images (>= min px) from a PDF, or render pages.
Usage:
  python -I pdfimgs.py extract file.pdf outdir [minpx] [firstpage lastpage]
  python -I pdfimgs.py render file.pdf outdir dpi page[,page...]
  python -I pdfimgs.py text file.pdf  (prints page numbers + lines mentioning seal/inscri)
"""
import sys, os, re
import pymupdf

mode, pdf = sys.argv[1], sys.argv[2]
doc = pymupdf.open(pdf)
if mode == "extract":
    out = sys.argv[3]; os.makedirs(out, exist_ok=True)
    minpx = int(sys.argv[4]) if len(sys.argv) > 4 else 200
    a = int(sys.argv[5]) if len(sys.argv) > 5 else 1
    b = int(sys.argv[6]) if len(sys.argv) > 6 else len(doc)
    for pno in range(a - 1, b):
        for i, img in enumerate(doc[pno].get_images(full=True)):
            xref = img[0]
            try:
                pix = pymupdf.Pixmap(doc, xref)
                if pix.width < minpx or pix.height < minpx:
                    continue
                if pix.alpha:
                    pix = pymupdf.Pixmap(pix, 0)
                if pix.colorspace is None or pix.colorspace.n not in (1, 3):
                    pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
                pix.save(os.path.join(out, f"p{pno+1:03d}_{i}.png"))
            except Exception as e:
                print("skip", pno + 1, xref, e)
elif mode == "render":
    out = sys.argv[3]; os.makedirs(out, exist_ok=True)
    dpi = int(sys.argv[4])
    for p in sys.argv[5].split(","):
        pg = doc[int(p) - 1]
        pg.get_pixmap(dpi=dpi).save(os.path.join(out, f"page{int(p):03d}.png"))
elif mode == "text":
    pat = re.compile(sys.argv[3] if len(sys.argv) > 3 else r"seal|inscri|sign", re.I)
    for i, pg in enumerate(doc):
        for line in pg.get_text().splitlines():
            if pat.search(line):
                print(i + 1, line.strip()[:160])
