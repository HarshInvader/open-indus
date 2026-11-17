"""v2 step 2: crop pipeline that reports REAL detail, and re-measures the v1 crops.

Fixes over p2_crop.py:
- px/mm is reported twice: nominal (box size / seal size, as in v1) and TRUE = nominal / enlargement
  factor, where the factor comes from v2_effres.true_factor() measured on the crop itself.
- crops are taken at native pixels of the decoded JP2 (no resampling; v1 also did this, so the v1 loss
  is in the source uploads, not in cropping). Bit depth (mid-tone fraction) is recorded per crop.
- reader packets must not be shrunk by the image viewer: tile() cuts a crop into overlapping tiles of at
  most 1000 px on the long side (no resampling), for use whenever a later gate runs.
- scan choice per volume uses measured TRUE px/mm among greyscale/colour uploads (work/v2_scan_audit*.csv),
  not stated ppi or nominal page size.

Also builds the FEM evidence sheet: for the 8 v1 FEM seals, the same box from
  (a) in.gov.ignca.9954 (the v1 crop; greyscale, 6x enlargement),
  (b) in.ernet.dli.2015.57013 (same master scan, same page geometry, but 1-bit),
  (c) the CISI vol. 1 photo where one exists.
Outputs: crops_v2/v1_remeasure.csv, crops_v2/fem_dli_bitonal_<key>.png, crops_v2/contact_fem_compare.png
Run: .venv/bin/python -I experiments/plate_corpus/v2_crop.py
"""
import csv, os, sys
import numpy as np
from PIL import Image, ImageDraw
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
from v2_effres import measure, true_factor

OUT = os.path.join(D, "crops_v2")
DLI_FEM = "in.ernet.dli.2015.57013"


def tile(im, maxside=1000, overlap=0.15):
    """Split an image into native-resolution tiles no larger than maxside (no resampling)."""
    w, h = im.size
    if max(w, h) <= maxside:
        return [((0, 0), im)]
    step = int(maxside * (1 - overlap))
    out = []
    for y in range(0, max(1, h - int(maxside * overlap)), step):
        for x in range(0, max(1, w - int(maxside * overlap)), step):
            out.append(((x, y), im.crop((x, y, min(w, x + maxside), min(h, y + maxside)))))
    return out


def dli_page(idx):
    for p in (os.path.join(D, "raw", "v2", DLI_FEM, "pages", f"{idx:04d}.jp2"),
              os.path.join(D, "raw", DLI_FEM, "pages", f"{idx:04d}.jp2")):
        if os.path.exists(p):
            return p
    raise FileNotFoundError(idx)


def locate(crop, page, guess, search=400, s=4):
    """Find crop (from the greyscale upload) inside page (bitonal upload of the same plate) by normalised
    cross-correlation at 1/s scale within +-search px of the guess, then refine at full scale +-s px."""
    from scipy.signal import fftconvolve
    def ncc(a, t):
        a = a - a.mean(); t = t - t.mean()
        num = fftconvolve(a, t[::-1, ::-1], mode="valid")
        ones = np.ones_like(t)
        s1 = fftconvolve(a, ones, mode="valid"); s2 = fftconvolve(a * a, ones, mode="valid")
        var = np.maximum(s2 - s1 ** 2 / t.size, 1e-9)
        return num / np.sqrt(var * (t ** 2).sum())
    gx, gy = guess
    X0, Y0 = max(0, gx - search), max(0, gy - search)
    X1, Y1 = min(page.width, gx + crop.width + search), min(page.height, gy + crop.height + search)
    reg = page.crop((X0, Y0, X1, Y1))
    a = np.asarray(reg.resize((reg.width // s, reg.height // s), Image.BOX), float)
    t = np.asarray(crop.resize((crop.width // s, crop.height // s), Image.BOX), float)
    c = np.abs(ncc(a, t))  # polarity may differ after thresholding
    yy, xx = np.unravel_index(np.argmax(c), c.shape)
    bx, by = X0 + xx * s, Y0 + yy * s
    A = np.asarray(page.crop((bx - s, by - s, bx + crop.width + s, by + crop.height + s)), float)
    cf = np.abs(ncc(A, np.asarray(crop, float)))
    yy, xx = np.unravel_index(np.argmax(cf), cf.shape)
    return bx - s + xx, by - s + yy, float(cf.max())


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = list(csv.DictReader(open(os.path.join(D, "crops.csv"))))
    res = []
    for r in rows:
        k = r["key"]
        im = Image.open(os.path.join(D, "crops", f"plate_{k}.png")).convert("L")
        m = measure(im); f = true_factor(m)
        row = dict(key=k, source=r["source"], item=r["item"], nominal_px_per_mm=float(r["plate_px_per_mm"]),
                   grid_ratio=m["grid_ratio"], grid_period=m["grid_period"], roundtrip_factor=m["eff_factor"],
                   true_factor=f, true_px_per_mm=round(float(r["plate_px_per_mm"]) / f, 2),
                   midtone_frac=m["midtone_frac"], loss=m["loss"])
        if r["cisi"] and os.path.exists(os.path.join(D, "crops", f"cisi_{k}.png")):
            ci = Image.open(os.path.join(D, "crops", f"cisi_{k}.png")).convert("L")
            mc = measure(ci); fc = true_factor(mc)
            row.update(cisi_nominal_px_per_mm=float(r["cisi_px_per_mm"]), cisi_factor=fc,
                       cisi_true_px_per_mm=round(float(r["cisi_px_per_mm"]) / fc, 2))
        if r["source"] == "Mackay1938_FEM":
            x0, y0, x1, y1 = map(int, r["box"].split())
            mg = int(0.04 * max(x1 - x0, y1 - y0))
            pg = Image.open(dli_page(int(r["page"]))).convert("L")
            dx, dy, score = locate(im, pg, (max(0, x0 - mg), max(0, y0 - mg)))
            b = pg.crop((dx, dy, dx + im.width, dy + im.height))
            row["dli_match_corr"] = round(score, 3)
            b.save(os.path.join(OUT, f"fem_dli_bitonal_{k}.png"))
            mb = measure(b)
            row.update(dli_bitonal_midtone=mb["midtone_frac"], dli_bitonal_roundtrip_factor=mb["eff_factor"],
                       dli_bitonal_grid_ratio=mb["grid_ratio"])
        res.append(row)
        print(k, "nominal", row["nominal_px_per_mm"], "factor", f, "TRUE", row["true_px_per_mm"],
              "| cisi true", row.get("cisi_true_px_per_mm", "-"), "| dli mid", row.get("dli_bitonal_midtone", "-"))
    keys = []
    for r in res:
        keys += [k for k in r if k not in keys]
    with open(os.path.join(OUT, "v1_remeasure.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); w.writerows(res)
    # FEM evidence sheet: each row = one seal, columns = IGNCA crop | DLI bitonal | CISI (if any); width 420 each
    fem = [r for r in res if r["source"] == "Mackay1938_FEM"]
    W = 420; cells = []
    for r in fem:
        ims = [Image.open(os.path.join(D, "crops", f"plate_{r['key']}.png")).convert("L"),
               Image.open(os.path.join(OUT, f"fem_dli_bitonal_{r['key']}.png")).convert("L")]
        cp = os.path.join(D, "crops", f"cisi_{r['key']}.png")
        ims.append(Image.open(cp).convert("L") if os.path.exists(cp) else None)
        cells.append((r, [None if i is None else i.resize((W, max(1, round(i.height * W / i.width))), Image.LANCZOS) for i in ims]))
    H = sum(max(i.height for i in c if i is not None) + 22 for _, c in cells) + 24
    sheet = Image.new("L", (3 * (W + 10), H), 255); dr = ImageDraw.Draw(sheet)
    for j, t in enumerate(["IGNCA 9954 greyscale (v1 crop)", "DLI 57013 same scan, 1-bit", "CISI vol. 1"]):
        dr.text((j * (W + 10) + 4, 6), t, fill=0)
    y = 24
    for r, c in cells:
        hh = max(i.height for i in c if i is not None)
        dr.text((4, y + 2), f"FEM {r['key'][4:]}: nominal {r['nominal_px_per_mm']} px/mm, true {r['true_px_per_mm']}", fill=0)
        for j, i in enumerate(c):
            if i is not None:
                sheet.paste(i, (j * (W + 10), y + 18))
        y += hh + 22
    sheet.save(os.path.join(OUT, "contact_fem_compare.png"))


if __name__ == "__main__":
    main()
