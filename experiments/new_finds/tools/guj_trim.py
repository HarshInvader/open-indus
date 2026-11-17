"""Trim near-white borders of images in place. Usage: python -I guj_trim.py img1 img2 ..."""
import sys

from PIL import Image, ImageChops

for f in sys.argv[1:]:
    im = Image.open(f).convert("RGB")
    bg = Image.new("RGB", im.size, (255, 255, 255))
    diff = ImageChops.difference(im, bg).convert("L").point(lambda v: 255 if v > 30 else 0)
    box = diff.getbbox()
    if box:
        im = im.crop(box)
    im.save(f)
