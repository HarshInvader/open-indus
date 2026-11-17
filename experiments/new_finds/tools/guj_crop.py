"""Crop a region from an image. Usage: python -I crop.py in out x0 y0 x1 y1 [rot]
Coordinates in original pixels. Optional rot in degrees (counter-clockwise)."""
import sys
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
src, dst = sys.argv[1], sys.argv[2]
x0, y0, x1, y1 = map(int, sys.argv[3:7])
im = Image.open(src).convert("RGB").crop((x0, y0, x1, y1))
if len(sys.argv) > 7:
    im = im.rotate(float(sys.argv[7]), expand=True)
im.save(dst, quality=95)
print(dst, im.size)
