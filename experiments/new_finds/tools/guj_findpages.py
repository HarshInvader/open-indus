"""List PDF pages that contain any keyword, with image count and caption-ish lines.
Usage: python -I guj_findpages.py file.pdf kw1,kw2,...  [mustkw1,mustkw2]"""
import re
import sys

import pymupdf

doc = pymupdf.open(sys.argv[1])
kws = [k.lower() for k in sys.argv[2].split(",")]
must = [k.lower() for k in sys.argv[3].split(",")] if len(sys.argv) > 3 else []
for i, p in enumerate(doc):
    t = p.get_text()
    low = t.lower()
    hits = [k for k in kws if k in low]
    if not hits or (must and not any(m in low for m in must)):
        continue
    nimg = len([x for x in p.get_image_info() if (x["bbox"][2] - x["bbox"][0]) > 60])
    caps = [l.strip() for l in t.splitlines() if re.match(r"\s*(fig|pl\.|plate)", l.strip(), re.I)]
    print(i + 1, hits, "imgs:", nimg, "|", " / ".join(caps)[:250])
