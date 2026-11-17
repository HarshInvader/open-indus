"""Blind shape step for the self-labelling test.

Silhouettes of each inscribed object class are defined HERE, as line drawings in code,
from the physical shape of the object (Harappan seals, sealings, tablets, jars, goblets,
ivory rods, copper axes/blades, stoneware bangles). They were written before any
sign-by-object distribution was computed in this area.

Every sign drawing (data/sign_images/M*.png) is compared with every silhouette by
  * primary  : symmetric chamfer distance between thinned, size-normalised line drawings
               (keeps orientation and aspect ratio, which a depiction would keep)
  * secondary: L1 distance between log Hu moments of the ink (rotation/scale invariant)
  * tertiary : keyword match in the blind referent catalogue (experiments/iconography)
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = ROOT / "experiments/self_label"
CANVAS = 154
STROKE = 5  # Mahadevan drawings are ~4-6 px lines on a 154 px canvas


def ellipse(cx, cy, rx, ry, n=72, a0=0.0, a1=2 * np.pi):
    t = np.linspace(a0, a1, n)
    return list(zip(cx + rx * np.cos(t), cy + ry * np.sin(t)))


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]


# object class -> list of silhouettes; each silhouette = list of polylines in (x, y), y down.
SILHOUETTES = {
    # square stamp seal: face view, and profile (flat plate + pierced boss on the back)
    "seal": {
        "seal_face": [rect(0, 0, 1, 1)],
        "seal_profile": [rect(0, 0.62, 1, 0.85),
                         ellipse(0.5, 0.62, 0.17, 0.30, a0=np.pi, a1=2 * np.pi),
                         ellipse(0.5, 0.48, 0.05, 0.05)],
    },
    # clay sealing: irregular lump carrying a square impression
    "sealing": {
        "sealing_lump": [[(0.65 + 0.65 * np.cos(t) * (1 + 0.06 * np.sin(5 * t)),
                           0.5 + 0.5 * np.sin(t) * (1 + 0.06 * np.cos(3 * t)))
                          for t in np.linspace(0, 2 * np.pi, 90)],
                         rect(0.35, 0.2, 0.95, 0.8)],
    },
    # miniature tablets (Harappa): flat rectangular bar, and triangular prism (end view)
    "miniature tablet": {
        "tablet_bar": [rect(0, 0, 3, 1)],
        "tablet_prism_end": [[(0, 1), (0.5, 0.13), (1, 1), (0, 1)]],
    },
    # copper tablets (Mohenjo-daro): small rectangle ~2:1
    "copper tablet": {
        "copper_tablet": [rect(0, 0, 2, 1)],
    },
    # pottery graffiti are on jars: globular jar with neck and everted rim (profile outline)
    "pottery graffito": {
        "jar": [[(0.30, 0.0), (0.34, 0.08), (0.34, 0.16), (0.12, 0.30), (0.02, 0.48), (0.04, 0.68),
                 (0.18, 0.88), (0.32, 1.0), (0.68, 1.0), (0.82, 0.88), (0.96, 0.68), (0.98, 0.48),
                 (0.88, 0.30), (0.66, 0.16), (0.66, 0.08), (0.70, 0.0), (0.30, 0.0)]],
    },
    # stamped pottery (ICIT POT:T:s) is mostly on pointed-base goblets
    "stamped pottery": {
        "goblet": [[(0.0, 0.0), (0.04, 0.35), (0.16, 0.70), (0.42, 0.98), (0.5, 1.0), (0.58, 0.98),
                    (0.84, 0.70), (0.96, 0.35), (1.0, 0.0), (0.0, 0.0)]],
    },
    # ivory/bone rods: a long thin stick, drawn as a line (upright or lying)
    "ivory/bone rod": {
        "rod_upright": [[(0, 0), (0, 1)]],
        "rod_lying": [[(0, 0), (1, 0)]],
    },
    # copper/bronze implements: flat axe (celt), knife blade, spearhead with tang
    "bronze implement": {
        "flat_axe": [[(0.32, 0.0), (0.68, 0.0), (0.80, 0.55)] + ellipse(0.5, 0.62, 0.5, 0.38, n=30, a0=-0.15, a1=np.pi + 0.15)[::1] + [(0.20, 0.55), (0.32, 0.0)]],
        "knife_blade": [[(0.0, 0.45), (0.18, 0.45), (0.18, 0.30), (0.55, 0.22), (0.85, 0.30), (1.0, 0.5),
                         (0.80, 0.62), (0.40, 0.70), (0.18, 0.70), (0.18, 0.55), (0.0, 0.55)]],
        "spearhead": [[(0.5, 0.0), (0.78, 0.30), (0.82, 0.55), (0.60, 0.75), (0.56, 1.0), (0.44, 1.0),
                       (0.40, 0.75), (0.18, 0.55), (0.22, 0.30), (0.5, 0.0)]],
    },
    # stoneware/clay bangles: a ring, face-on and seen obliquely
    "bangle": {
        "ring": [ellipse(0.5, 0.5, 0.5, 0.5)],
        "ring_oblique": [ellipse(0.5, 0.25, 0.5, 0.25)],
    },
}

# keyword rules for the referent catalogue route (tertiary), fixed before any distribution
KEYWORDS = {
    "seal": ["square", "seal", "stamp", "box"],
    "sealing": ["square", "seal", "stamp", "box"],
    "miniature tablet": ["rectangle", "rectangular", "tablet", "bar", "triangle"],
    "copper tablet": ["rectangle", "rectangular", "tablet", "bar"],
    "pottery graffito": ["jar", "pot", "vessel", "bowl", "cup"],
    "stamped pottery": ["goblet", "cup", "jar", "vessel", "pot"],
    "ivory/bone rod": ["rod", "stick", "staff", "pole", "post"],
    "bronze implement": ["axe", "blade", "knife", "spear", "dagger", "chisel", "razor", "celt"],
    "bangle": ["ring", "circle", "bangle", "loop", "oval"],
}
KW_CLASS = {"pottery graffito": "vessel", "stamped pottery": "vessel", "bronze implement": "tool_weapon"}


def render(polys):
    pts = np.array([p for poly in polys for p in poly], float)
    lo, hi = pts.min(0), pts.max(0)
    span = max((hi - lo).max(), 1e-9)
    s = (CANVAS - 30) / span
    off = (CANVAS - (hi - lo) * s) / 2
    img = np.zeros((CANVAS, CANVAS), np.uint8)
    for poly in polys:
        q = np.round((np.array(poly) - lo) * s + off).astype(np.int32)
        cv2.polylines(img, [q], False, 255, STROKE, lineType=cv2.LINE_8)
    return img > 0


def load_sign(n):
    a = np.array(Image.open(ROOT / f"data/sign_images/M{n}.png").convert("RGBA")).astype(float)
    alpha = a[..., 3] / 255.0
    lum = a[..., :3].mean(-1)
    ink = (alpha > 0.5) & (lum < 128)
    return ink


def thin(mask):
    """Zhang-Suen thinning (numpy)."""
    img = np.pad(mask.astype(np.uint8), 1)
    changed = True
    while changed:
        changed = False
        for step in (0, 1):
            P = img
            p2, p3, p4 = P[:-2, 1:-1], P[:-2, 2:], P[1:-1, 2:]
            p5, p6, p7 = P[2:, 2:], P[2:, 1:-1], P[2:, :-2]
            p8, p9 = P[1:-1, :-2], P[:-2, :-2]
            nb = [p2, p3, p4, p5, p6, p7, p8, p9]
            B = sum(x.astype(int) for x in nb)
            seq = nb + [p2]
            A = sum(((seq[i] == 0) & (seq[i + 1] == 1)).astype(int) for i in range(8))
            if step == 0:
                c = (p2 * p4 * p6 == 0) & (p4 * p6 * p8 == 0)
            else:
                c = (p2 * p4 * p8 == 0) & (p2 * p6 * p8 == 0)
            m = (P[1:-1, 1:-1] == 1) & (B >= 2) & (B <= 6) & (A == 1) & c
            if m.any():
                img[1:-1, 1:-1][m] = 0
                changed = True
    return img[1:-1, 1:-1].astype(bool)


NORM = 128


def normalise(mask):
    """Crop to ink bbox, scale longest side to 100 px keeping aspect, centre on 128 canvas, thin."""
    ys, xs = np.nonzero(mask)
    crop = mask[ys.min():ys.max() + 1, xs.min():xs.max() + 1].astype(np.uint8) * 255
    h, w = crop.shape
    s = 100.0 / max(h, w)
    nh, nw = max(1, int(round(h * s))), max(1, int(round(w * s)))
    r = cv2.resize(crop, (nw, nh), interpolation=cv2.INTER_AREA) > 60
    out = np.zeros((NORM, NORM), bool)
    y0, x0 = (NORM - nh) // 2, (NORM - nw) // 2
    out[y0:y0 + nh, x0:x0 + nw] = r
    return out, thin(out)


def chamfer(sk_a, sk_b):
    da = cv2.distanceTransform((~sk_a).astype(np.uint8), cv2.DIST_L2, 5)
    db = cv2.distanceTransform((~sk_b).astype(np.uint8), cv2.DIST_L2, 5)
    return 0.5 * (db[sk_a].mean() + da[sk_b].mean())


def loghu(mask):
    # v2 fix: Hu moments of the hole-filled region (v1 used the 1-px outline, which is degenerate)
    from scipy.ndimage import binary_closing, binary_fill_holes
    region = binary_fill_holes(binary_closing(mask, iterations=2))
    h = cv2.HuMoments(cv2.moments(region.astype(np.uint8), binaryImage=True)).ravel()
    return -np.sign(h) * np.log10(np.abs(h) + 1e-30)


def hu_dist(a, b):
    return float(np.abs(a - b)[:4].sum())  # first four invariants: the stable ones
