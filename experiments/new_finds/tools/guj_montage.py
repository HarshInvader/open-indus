"""Contact sheet (Gujarat agent copy). Usage: python -I guj_montage.py out.jpg cols thumbw img1 img2 ..."""
import os
import sys

from PIL import Image, ImageDraw

Image.MAX_IMAGE_PIXELS = None
out, cols, tw = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
thumbs = []
for f in sys.argv[4:]:
    im = Image.open(f).convert("RGB")
    im.thumbnail((tw, int(tw * 1.5)))
    thumbs.append((os.path.basename(f), im))
th = max(t[1].height for t in thumbs) + 16
rows = (len(thumbs) + cols - 1) // cols
sheet = Image.new("RGB", (cols * tw, rows * th), "white")
d = ImageDraw.Draw(sheet)
for i, (n, im) in enumerate(thumbs):
    x, y = (i % cols) * tw, (i // cols) * th
    sheet.paste(im, (x, y + 16))
    d.text((x + 2, y + 2), n, fill="red")
sheet.save(out, quality=85)
print(out, sheet.size)
