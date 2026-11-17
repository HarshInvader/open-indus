"""v2: measure REAL detail in an image region, not nominal pixel size.

Measures on a greyscale image:
1. tone: fraction of pixels in 40..215 (a bitonal scan stored as greyscale has very few mid-tones).
2. block grid: mean |gradient| at each offset modulo k (k = 2..40) along rows and columns; ratio of the
   peak offset to the median offset. A clean scan gives ~1.1-1.5. An image enlarged by nearest-neighbour
   (or block-compressed) at period P gives a large ratio at P and its multiples. grid_period = smallest k
   whose ratio is >= 70% of the best ratio.
3. round-trip loss at factor f: shrink by f, enlarge back, RMS difference / RMS of the detail finer than
   16 px. Two variants, and the SMALLER loss is kept: (a) area shrink + bicubic enlarge (detects smooth
   enlargement), (b) grid-aligned block mean + nearest enlarge, best of all phases (detects pixel
   replication, which fools (a) because block edges look like detail).
   eff_factor = largest tested f whose loss is < THRESH (0.17). Calibration: sharp CISI crop -> 1.5 (the
   floor of the test); its 3x / 6x enlargements (nearest or bicubic) -> 3 / 6.
   true px/mm = nominal px/mm / eff_factor.
Calibrated by controls in v2_audit.py (sharp CISI crop enlarged 4x/6x/8x by nearest and bicubic).
Usage: python -I v2_effres.py IMAGE [x0 y0 x1 y1]
"""
import sys
import numpy as np
from PIL import Image

FACTORS = [1.5, 2, 3, 4, 5, 6, 8, 10, 12]
THRESH = 0.17


def load(path, box=None):
    im = Image.open(path).convert("L")
    if box:
        im = im.crop(box)
    return im


def _rt_smooth(a, f):
    h, w = a.shape
    im = Image.fromarray(a.astype(np.uint8))
    small = im.resize((max(2, round(w / f)), max(2, round(h / f))), Image.BOX)
    back = np.asarray(small.resize((w, h), Image.BICUBIC), float)
    return float(np.sqrt(np.mean((a - back) ** 2)))


def _rt_block(a, f):
    if f != int(f):
        return 1e9
    f = int(f)
    best = 1e9
    for py in range(f):
        for px in range(f):
            b = a[py:, px:]
            h, w = b.shape[0] // f * f, b.shape[1] // f * f
            if h < 2 * f or w < 2 * f:
                continue
            b = b[:h, :w]
            m = b.reshape(h // f, f, w // f, f).mean((1, 3))
            back = np.repeat(np.repeat(m, f, 0), f, 1)
            best = min(best, float(np.sqrt(np.mean((b - back) ** 2))))
    return best


def detail_rms(a):
    return _rt_smooth(a, 16)


def block_grid(a, kmax=40):
    gx = np.abs(np.diff(a, axis=1)).mean(0)
    gy = np.abs(np.diff(a, axis=0)).mean(1)
    out = {}
    for k in range(2, kmax + 1):
        best = 0
        for g in (gx, gy):
            n = len(g) // k * k
            if n < 3 * k:
                continue
            prof = g[:n].reshape(-1, k).mean(0)
            best = max(best, prof.max() / (np.median(prof) + 1e-9))
        out[k] = float(best)
    top = max(out.values())
    period = min(k for k, v in out.items() if v >= 0.7 * top) if top >= 2.0 else None
    return round(top, 2), period


def measure(im):
    a = np.asarray(im, float)
    ref = detail_rms(a) + 1e-9
    losses = {f: min(_rt_smooth(a, f), _rt_block(a, f)) / ref for f in FACTORS}
    # largest tested factor whose round trip keeps all but THRESH of the detail; 1.0 if none.
    # Floor of the test: a fully sharp control scores 1.5 (see v2_audit.py controls).
    eff = max([1.0] + [f for f in FACTORS if losses[f] < THRESH])
    gr, gp = block_grid(a)
    tone = float(((a > 40) & (a < 215)).mean())
    return dict(eff_factor=round(eff, 2), loss={str(f): round(v, 3) for f, v in losses.items()},
                grid_ratio=gr, grid_period=gp, midtone_frac=round(tone, 3), size=list(im.size))


def true_factor(m):
    """Final enlargement factor. A block grid (ratio >= 2.5) with period P means pixel replication by P or
    by a divisor of P (a period-12 peak can come from 6x blocks). Each divisor d >= 2 of P that is a tested
    factor and shows a round-trip dip (loss at d below loss at the next smaller tested factor) is a
    candidate; the largest is taken. Otherwise the round-trip factor is used. For clean images the
    round-trip factor has a floor of 1.5-2 (a sharp control scores 2), so nominal/factor is then a lower
    bound on true px/mm; for block-replicated images the period gives the factor exactly."""
    P, L = m["grid_period"], m["loss"]
    if P and m["grid_ratio"] >= 2.5:
        dips = []
        for d in range(2, P + 1):
            if P % d == 0 and str(d) in L:
                smaller = [f for f in FACTORS if f < d]
                if smaller and L[str(d)] < L[str(smaller[-1])]:
                    dips.append(float(d))
        if dips:
            return max(max(dips), m["eff_factor"])
    return m["eff_factor"]


if __name__ == "__main__":
    box = tuple(map(int, sys.argv[2:6])) if len(sys.argv) > 5 else None
    print(measure(load(sys.argv[1], box)))
