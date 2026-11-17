"""P2: crop each sampled seal from its plate page and from CISI (baseline); measure px per mm.

Plate pages: original JP2s fetched by pcfetch.page() into raw/<item>/pages/ (untrusted image data, only decoded).
Seed points: SEEDS below, located by the analyst by eye on downscaled plate views (fractions of page width/height),
next to the printed number. The seal box is then found automatically: in a window around the seed, Otsu
threshold (seal darker than paper / plate ground), close, fill, take the component under the seed.
BOX_OVERRIDE (fractions) replaces automatic boxes that fail crop QA (logged in crops.csv: box_method).
CISI: boxes from experiments/carver_hands/work/boxes.csv (impression 'a' preferred, else seal 'A' / unlabelled),
pages experiments/carver_hands/work/pages/.
px/mm = sqrt(box_w * box_h) / sqrt(l_mm * w_mm), as pre-registered.
Outputs: crops/plate_<key>.png, crops/cisi_<key>.png, crops.csv, work/qa_sheet.png
Run: .venv/bin/python -I experiments/plate_corpus/p2_crop.py
"""
import csv, os, sys, math
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
D = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(os.path.dirname(D))
sys.path.insert(0, D)
import pcfetch

ITEM = {"Mackay1938_FEM": "in.gov.ignca.9954", "Vats1940_EH": "dli.ministry.25730",
        "Mackay1943_CE": "dli.ministry.25495", "Marshall1931_MIC": "in.gov.ignca.48270"}
# (source, object_no) -> (page index in item, x_frac, y_frac)
SEEDS = {
    ("Mackay1938_FEM", "83"): (181, .672, .597), ("Mackay1938_FEM", "273"): (189, .330, .088),
    ("Mackay1938_FEM", "288"): (189, .380, .345), ("Mackay1938_FEM", "289"): (189, .540, .361),
    ("Mackay1938_FEM", "308"): (189, .130, .583), ("Mackay1938_FEM", "407"): (201, .140, .518),
    ("Mackay1938_FEM", "420"): (201, .465, .739), ("Mackay1938_FEM", "461"): (203, .265, .602),
    ("Vats1940_EH", "3"): (96, .740, .194), ("Vats1940_EH", "16"): (97, .206, .152),
    ("Vats1940_EH", "106"): (100, .116, .171), ("Vats1940_EH", "138"): (100, .256, .603),
    ("Vats1940_EH", "224"): (101, .772, .862), ("Vats1940_EH", "286"): (103, .138, .710),
    ("Mackay1943_CE", "CE pl. LI, 16"): (402, .865, .354), ("Mackay1943_CE", "CE pl. LII, 9"): (403, .340, .250),
    ("Mackay1943_CE", "CE pl. LII, 20"): (403, .710, .358), ("Mackay1943_CE", "CE pl. LII, 27"): (403, .810, .481),
    ("Marshall1931_MIC", "91"): (187, .310, .623), ("Marshall1931_MIC", "441"): (201, .080, .483),
}
BOX_OVERRIDE = {  # (source, object_no) -> (x0, y0, x1, y1) as page fractions; set after crop QA (auto box wrong)
    ("Vats1940_EH", "3"): (.621, .096, .858, .268),        # Otsu split the low-contrast halftone seal
    ("Vats1940_EH", "138"): (.224, .623, .296, .671),      # seed was on the gap between photos
    ("Mackay1943_CE", "CE pl. LI, 16"): (.783, .330, .947, .389),  # auto box caught one dark stroke only
    ("Vats1940_EH", "16"): (.1216, .1001, .2943, .2129),   # edge trim cut the lighter left side; untrimmed auto box
    ("Mackay1943_CE", "CE pl. LII, 27"): (.7522, .4347, .8704, .5275),  # edge trim cut the horn; untrimmed auto box
}
CISI_SIDE_PREF = ["a", "", "A"]


def key(src, no):
    return (src.split("_")[1] + "_" + no.replace("CE pl. ", "").replace(", ", "-")).replace(" ", "")


def auto_box(g, sx, sy, win):
    H, W = g.shape
    x0, x1 = max(0, sx - win), min(W, sx + win)
    y0, y1 = max(0, sy - win), min(H, sy + win)
    a = g[y0:y1, x0:x1].astype(float)
    a = ndimage.gaussian_filter(a, 2)
    hist, edges = np.histogram(a, bins=256, range=(0, 256))
    p = hist / hist.sum(); om = np.cumsum(p); mu = np.cumsum(p * np.arange(256)); mt = mu[-1]
    sb = (mt * om - mu) ** 2 / (om * (1 - om) + 1e-12)
    t = int(np.nanargmax(sb))
    m = a < t
    m = ndimage.binary_opening(m, iterations=2)
    m = ndimage.binary_closing(m, iterations=6)
    m = ndimage.binary_fill_holes(m)
    m = ndimage.binary_opening(m, iterations=max(4, win // 60))  # drops thin handwritten plate numbers
    lab, n = ndimage.label(m)
    cy, cx = sy - y0, sx - x0
    l = lab[cy, cx]
    if l == 0:  # nearest component to the seed
        dist = ndimage.distance_transform_edt(lab == 0, return_indices=True)[1]
        l = lab[dist[0][cy, cx], dist[1][cy, cx]]
    comp = lab == l
    ys, xs = np.where(comp)
    a0, b0, a1, b1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    # trim edge rows/columns with little coverage (a plate number merged by the closing)
    sub = comp[b0:b1, a0:a1]
    rows, cols = sub.mean(1), sub.mean(0)
    r = np.where(rows >= 0.35 * rows.max())[0]; c = np.where(cols >= 0.35 * cols.max())[0]
    return (x0 + a0 + c.min(), y0 + b0 + r.min(), x0 + a0 + c.max() + 1, y0 + b0 + r.max() + 1), t


def main():
    os.makedirs(os.path.join(D, "crops"), exist_ok=True)
    S = list(csv.DictReader(open(os.path.join(D, "sample.csv"))))
    B = {}
    for b in csv.DictReader(open(os.path.join(REPO, "experiments/carver_hands/work/boxes.csv"))):
        B.setdefault(b["cisi"], []).append(b)
    out, qa = [], []
    for s in S:
        src, no = s["source"], s["object_no"]
        k = key(src, no)
        page, fx, fy = SEEDS[(src, no)]
        f = pcfetch.page(ITEM[src], page)
        im = Image.open(f).convert("L"); g = np.asarray(im)
        H, W = g.shape
        if (src, no) in BOX_OVERRIDE:
            a, b_, c, d = BOX_OVERRIDE[(src, no)]
            box = (int(a * W), int(b_ * H), int(c * W), int(d * H)); method = "manual"
        else:
            box, _ = auto_box(g, int(fx * W), int(fy * H), int(0.09 * W)); method = "auto"
        bw, bh = box[2] - box[0], box[3] - box[1]
        lmm, wmm = float(s["l_in"]) * 25.4, float(s["w_in"]) * 25.4
        ppmm = math.sqrt(bw * bh) / math.sqrt(lmm * wmm)
        mg = int(0.04 * max(bw, bh))
        crop = im.crop((max(0, box[0] - mg), max(0, box[1] - mg), min(W, box[2] + mg), min(H, box[3] + mg)))
        crop.save(os.path.join(D, "crops", f"plate_{k}.png"))
        row = dict(key=k, source=src, object_no=no, item=ITEM[src], page=page, box=" ".join(map(str, box)),
                   box_method=method, box_w=bw, box_h=bh, l_mm=round(lmm, 1), w_mm=round(wmm, 1),
                   aspect_box=round(max(bw, bh) / min(bw, bh), 2), aspect_dims=round(max(lmm, wmm) / min(lmm, wmm), 2),
                   plate_px_per_mm=round(ppmm, 2), plate_face="impression (plate legend: impressions of seals)"
                   if src == "Mackay1938_FEM" else "", cisi=s["cisi"], cisi_file="", cisi_side="", cisi_px_per_mm="")
        cb = sorted(B.get(s["cisi"], []), key=lambda b: CISI_SIDE_PREF.index(b["side"]) if b["side"] in CISI_SIDE_PREF else 9)
        if s["cisi"] and cb:
            b = cb[0]
            ci = Image.open(os.path.join(REPO, "experiments/carver_hands/work/pages", b["file"])).convert("L")
            x0, y0, x1, y1 = (int(b[c]) for c in ("x0", "y0", "x1", "y1"))
            cw, ch = x1 - x0, y1 - y0
            m2 = int(0.04 * max(cw, ch))
            ci.crop((max(0, x0 - m2), max(0, y0 - m2), x1 + m2, y1 + m2)).save(os.path.join(D, "crops", f"cisi_{k}.png"))
            row.update(cisi_file=b["file"], cisi_side=b["side"] or "?",
                       cisi_px_per_mm=round(math.sqrt(cw * ch) / math.sqrt(lmm * wmm), 2))
        out.append(row); qa.append((k, crop))
        print(k, method, box, f"{ppmm:.1f} px/mm", "CISI", row["cisi_px_per_mm"])
    with open(os.path.join(D, "crops.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    # QA sheet (analyst only checks that the right whole object is boxed)
    th = [(k, c.copy()) for k, c in qa]
    for _, c in th:
        c.thumbnail((240, 240))
    sheet = Image.new("L", (5 * 250, 4 * 270), 255); dr = ImageDraw.Draw(sheet)
    for i, (k, c) in enumerate(th):
        x, y = (i % 5) * 250, (i // 5) * 270
        sheet.paste(c, (x + 5, y + 20)); dr.text((x + 5, y + 4), k, fill=0)
    sheet.save(os.path.join(D, "work", "qa_sheet.png"))


if __name__ == "__main__":
    main()
