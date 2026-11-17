"""Make a labelled contact sheet from images. Usage: python -I montage.py out.png thumb_w img1 img2 ..."""
import sys
from PIL import Image, ImageDraw

out, tw = sys.argv[1], int(sys.argv[2])
paths = sys.argv[3:]
thumbs = []
for p in paths:
    im = Image.open(p).convert("RGB")
    r = tw / im.width
    im = im.resize((tw, max(1, int(im.height * r))))
    thumbs.append((p.split("/")[-1], im))
cols = min(8, len(thumbs))
rows = (len(thumbs) + cols - 1) // cols
th = max(t[1].height for t in thumbs) + 16
sheet = Image.new("RGB", (cols * tw, rows * th), "white")
d = ImageDraw.Draw(sheet)
for i, (name, im) in enumerate(thumbs):
    x, y = (i % cols) * tw, (i // cols) * th
    sheet.paste(im, (x, y + 16))
    d.text((x + 2, y + 2), name, fill="red")
sheet.save(out)
