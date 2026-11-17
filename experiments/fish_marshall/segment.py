"""Segment MIC vol. II tabulation pages (pp. 402-405) into row strips for Vision OCR.

For each scan (A = archive.org ..._801_d, B = in.ernet.dli.2015.96024, C = OLMh...), each page and each half-table:
deskew, find the plate-number column and its 70 row bands, write one PNG strip per row (whole half-row) to strips/.
Run: .venv/bin/python -I experiments/fish_marshall/segment.py
"""
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
PAGES = {  # scan -> {page_no: png}
    "A": {402: "A_p_0055", 403: "A_p_0056", 404: "A_p_0057", 405: "A_p_0058"},
    "B": {402: "B_p_0058", 403: "B_p_0059", 404: "B_p_0060", 405: "B_p_0061"},
    "C": {402: "C_p_0059", 403: "C_p_0060", 404: "C_p_0061", 405: "C_p_0062"},
}
OUT = os.path.join(HERE, "strips")
os.makedirs(OUT, exist_ok=True)


def load(name):
    im = np.asarray(Image.open(os.path.join(HERE, "png", name + ".png")).convert("L"), float)
    return im


def ink(im):
    t = np.percentile(im, 50) * 0.6  # dark ink
    return (im < t).astype(np.uint8)


def deskew(b):
    best = (0, -1)
    small = b[::4, ::4]
    for a in np.arange(-2.0, 2.01, 0.1):
        r = ndimage.rotate(small, a, reshape=False, order=0)
        v = np.var(r.sum(1))
        if v > best[1]:
            best = (a, v)
    return best[0]


def bands(profile, minh):
    on = profile > 0
    out, i = [], 0
    while i < len(on):
        if on[i]:
            j = i
            while j < len(on) and on[j]:
                j += 1
            if j - i >= minh:
                out.append((i, j))
            i = j
        else:
            i += 1
    return out


if __name__ == "__main__":
    meta = []
    for scan, pages in PAGES.items():
        for pg, name in pages.items():
            im = load(name)
            b = ink(im)
            ang = deskew(b)
            imr = ndimage.rotate(im, ang, reshape=False, order=1, cval=255)
            br = ink(imr)
            H, W = br.shape
            # vertical rules / text columns: column profile over the middle 60% of the page height
            y0, y1 = int(H * 0.25), int(H * 0.8)
            colp = br[y0:y1].sum(0).astype(float)
            # page split: the central double rule = the strongest column near the middle
            mid_lo, mid_hi = int(W * 0.4), int(W * 0.6)
            midx = mid_lo + int(np.argmax(colp[mid_lo:mid_hi]))
            for half in (0, 1):
                xa, xb = (0, midx) if half == 0 else (midx, W)
                sub = br[:, xa:xb]
                # text body x-extent: columns with ink in body rows (exclude long vertical rules)
                cp = sub[y0:y1].sum(0).astype(float)
                rule = cp > 0.6 * (y1 - y0)
                cp[rule] = 0
                sm = ndimage.uniform_filter1d(cp, max(3, W // 300))
                xs = np.where(sm > sm.max() * 0.03)[0]
                if not len(xs):
                    continue
                # plate-number column = first text cluster
                gaps = np.where(np.diff(xs) > W // 120)[0]
                first_end = xs[gaps[0]] if len(gaps) else xs[-1]
                px0, px1 = xs[0], first_end + 1
                colink = sub[:, px0:px1].sum(1).astype(float)
                colink = ndimage.uniform_filter1d(colink, 3)
                # find the body: rows of numbers start below the header; use bands of the plate column
                bb = bands(colink > max(1, colink.max() * 0.05), minh=max(4, H // 700))
                # keep bands in the lower 85% with plausible heights
                hs = np.array([e - s for s, e in bb])
                if not len(hs):
                    continue
                med = np.median(hs)
                bb = [(s, e) for s, e in bb if 0.5 * med <= e - s <= 2.5 * med and s > H * 0.12]
                # merge into rows by pitch: estimate pitch from median spacing
                cs = np.array([(s + e) / 2 for s, e in bb])
                pitch = np.median(np.diff(cs)) if len(cs) > 2 else med * 1.5
                for k, (s, e) in enumerate(bb):
                    c = (s + e) / 2
                    top = int(max(0, c - pitch * 0.62)); bot = int(min(H, c + pitch * 0.62))
                    strip = imr[top:bot, xa:xb]
                    fn = f"{scan}_{pg}_{half}_{k:02d}.png"
                    img = Image.fromarray(np.clip(strip, 0, 255).astype(np.uint8))
                    img = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)
                    img.save(os.path.join(OUT, fn))
                    meta.append(dict(scan=scan, page=pg, half=half, k=k, y=float(c), pitch=float(pitch), file=fn,
                                     angle=float(ang)))
            print(scan, pg, "angle", round(ang, 2), "rows", sum(1 for m in meta if m["scan"] == scan and m["page"] == pg),
                  file=sys.stderr)
    json.dump(meta, open(os.path.join(HERE, "strips_meta.json"), "w"), indent=0)
