"""Crop the photo of each flagged sherd from Vol. II App. III plates.

Finds the catalogue label's position with pdftotext -bbox, renders the page and crops the
photo area above the label. Output: work/crops/<catalogue>.png
Run: .venv/bin/python -I experiments/tn_brahmi_graffiti/crop_sherds.py
"""
import csv, os, re, subprocess, html
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(HERE, "raw", "inscribed_potsherds_2026.pdf")
OUT = os.path.join(HERE, "work", "crops"); os.makedirs(OUT, exist_ok=True)
DPI = 200


def norm(s):
    k = re.sub(r"[^a-z0-9]", "", s.lower()).replace("ttnsda", "tnsda"); return re.sub(r"(tupu|tnsda)0+", r"\1", k)


def find(label, pages):
    key = norm(label)
    for p in pages:
        xml = subprocess.run(["pdftotext", "-f", str(p), "-l", str(p), "-bbox", PDF, "-"],
                             capture_output=True, text=True).stdout
        page_w = float(re.search(r'<page width="([\d.]+)" height="([\d.]+)"', xml).group(1))
        page_h = float(re.search(r'<page width="([\d.]+)" height="([\d.]+)"', xml).group(2))
        for m in re.finditer(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)</word>', xml):
            if norm(html.unescape(m.group(5))) == key:
                return p, [float(m.group(i)) for i in range(1, 5)], page_w, page_h
    return None


rows = list(csv.DictReader(open(os.path.join(HERE, "both_sherds.csv"))))
for r in rows:
    lab = r["catalogue_no"]
    hit = find(lab, range(602, 712))
    if not hit:
        print("NOT FOUND", lab); continue
    p, (x0, y0, x1, y1), W, H = hit
    png = os.path.join(OUT, f"page{p}")
    if not os.path.exists(png + ".png"):
        subprocess.run(["pdftoppm", "-f", str(p), "-l", str(p), "-r", str(DPI), "-png", "-singlefile", PDF, png])
    im = Image.open(png + ".png")
    s = DPI / 72
    cx = (x0 + x1) / 2
    box = (max(0, cx - 115), max(0, y0 - 190), min(W, cx + 115), y1 + 4)
    im.crop(tuple(int(v * s) for v in box)).save(os.path.join(OUT, f"{lab}.png"))
    print("ok", lab, "page", p)
