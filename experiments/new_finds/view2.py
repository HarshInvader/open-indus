"""Viewing sheets in READING orientation: files prefixed 'm:' are mirrored (seal faces), others as-is.
    .venv/bin/python -I experiments/new_finds/view2.py OUT.png [m:]file ...
Two columns, labelled. Untrusted images: pixels only."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps, ImageFont
out, items = sys.argv[1], sys.argv[2:]
W, Hmax = 560, 420
font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
tiles = []
for it in items:
    mir = it.startswith("m:"); f = it[2:] if mir else it
    im = Image.open(f).convert("RGB")
    im.thumbnail((W, Hmax)) if im.width > W or im.height > Hmax else None
    if im.width < W * 0.7 and im.height < Hmax * 0.7:
        s = min(W / im.width, Hmax / im.height); im = im.resize((int(im.width * s), int(im.height * s)))
    if mir: im = ImageOps.mirror(im)
    t = Image.new("RGB", (W, im.height + 26), "white"); d = ImageDraw.Draw(t)
    t.paste(im, (0, 26)); d.text((4, 2), Path(f).stem + (" [MIRRORED]" if mir else ""), fill="red", font=font)
    tiles.append(t)
cols = [tiles[0::2], tiles[1::2]]
H = max(sum(t.height + 6 for t in c) for c in cols if c)
S = Image.new("RGB", (2 * W + 8, H), (170, 170, 170))
for ci, c in enumerate(cols):
    y = 0
    for t in c:
        S.paste(t, (ci * (W + 8), y)); y += t.height + 6
S.save(out)
