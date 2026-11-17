"""Crop by fractional coords. Usage: python -I nw_fcrop.py in out fx0 fy0 fx1 fy1 [in2 out2 ...] (groups of 6)"""
import sys
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
a = sys.argv[1:]
for i in range(0, len(a), 6):
    src, dst = a[i], a[i + 1]
    fx0, fy0, fx1, fy1 = map(float, a[i + 2:i + 6])
    im = Image.open(src).convert("RGB")
    w, h = im.size
    c = im.crop((int(fx0 * w), int(fy0 * h), int(fx1 * w), int(fy1 * h)))
    c.save(dst, quality=95)
    print(dst, c.size)
