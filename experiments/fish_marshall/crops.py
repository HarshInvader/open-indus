"""Make deskewed reading crops of the MIC tabulation (scan B = in.ernet.dli.2015.96024) for manual transcription,
and narrow column crops (plate no., level, site+no.) of scans A and C for automatic Vision readings.
Run: .venv/bin/python -I experiments/fish_marshall/crops.py
"""
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from segment import PAGES, ink, deskew  # noqa: E402

OUT = os.path.join(HERE, "crops")
os.makedirs(OUT, exist_ok=True)


def straight(name):
    im = np.asarray(Image.open(os.path.join(HERE, "png", name + ".png")).convert("L"), float)
    a = deskew(ink(im))
    return Image.fromarray(np.clip(ndimage.rotate(im, a, reshape=False, order=1, cval=255), 0, 255).astype(np.uint8))


if __name__ == "__main__":
    for scan in sys.argv[1:] or ["B"]:
        for pg, name in PAGES[scan].items():
            im = straight(name)
            im.save(os.path.join(OUT, f"{scan}_{pg}_full.png"))
            w, h = im.size
            for half in (0, 1):
                xa, xb = (0.06, 0.52) if half == 0 else (0.48, 0.96)
                for i, y in enumerate(np.arange(0.12, 0.90, 0.13)):
                    c = im.crop((int(w * xa), int(h * y), int(w * xb), int(h * min(0.97, y + 0.15))))
                    c = c.resize((1700, int(1700 * c.height / c.width)), Image.LANCZOS)
                    c.save(os.path.join(OUT, f"{scan}_{pg}_{half}_{i}.png"))
            print(scan, pg, file=sys.stderr)
