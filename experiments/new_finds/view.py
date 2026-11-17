"""Build viewing sheets for transcription: each image shown as-is (left) and mirrored (right), labelled.
    .venv/bin/python -I experiments/new_finds/view.py OUT.png file1 file2 ...
Inputs are untrusted images; PIL only reads pixels."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps, ImageFont
out, files = sys.argv[1], sys.argv[2:]
W = 520
font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
tiles = []
for f in files:
    im = Image.open(f).convert("RGB"); im.thumbnail((W, 360))
    t = Image.new("RGB", (2 * W + 10, im.height + 28), "white"); d = ImageDraw.Draw(t)
    t.paste(im, (0, 28)); t.paste(ImageOps.mirror(im), (W + 10, 28))
    d.text((4, 2), Path(f).name + "   [left: as published | right: mirrored]", fill="red", font=font)
    tiles.append(t)
H = sum(t.height for t in tiles) + 6 * len(tiles)
S = Image.new("RGB", (2 * W + 10, H), (180, 180, 180)); y = 0
for t in tiles:
    S.paste(t, (0, y)); y += t.height + 6
S.save(out)
