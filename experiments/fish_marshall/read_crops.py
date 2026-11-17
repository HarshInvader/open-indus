"""Composite reading crops (plate..level | site+no.) of deskewed scan-B pages for manual transcription.
Coordinates are in 1/6-scale preview pixels of crops/B_<page>_full.png (set by eye from the previews).
Run: .venv/bin/python -I experiments/fish_marshall/read_crops.py
"""
import os
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
CFG = {  # page: (rows y0, y1), [(half: (x0,x1) plate..level, (x0,x1) site)]
    402: ((158, 778), [((8, 212), (328, 410)), ((408, 578), (712, 828))]),
    403: ((178, 990), [((78, 252), (352, 452)), ((438, 612), (712, 808))]),
    404: ((172, 992), [((82, 252), (342, 448)), ((422, 612), (712, 808))]),
    405: ((176, 992), [((82, 252), (352, 452)), ((442, 618), (726, 818))]),
}
os.makedirs(os.path.join(HERE, "read"), exist_ok=True)
for pg, ((y0, y1), halves) in CFG.items():
    im = Image.open(os.path.join(HERE, "crops", f"B_{pg}_full.png"))
    for h, (a, b) in enumerate(halves):
        n = 4
        step = (y1 - y0) / n
        for i in range(n):
            ya = int((y0 + i * step - 6) * 6); yb = int((y0 + (i + 1) * step + 6) * 6)
            ca = im.crop((a[0] * 6, ya, a[1] * 6, yb)); cb = im.crop((b[0] * 6, ya, b[1] * 6, yb))
            comp = Image.new("L", (ca.width + cb.width + 20, ca.height), 255)
            comp.paste(ca, (0, 0)); comp.paste(cb, (ca.width + 20, 0))
            s = 1500 / max(comp.size)
            comp.resize((int(comp.width * s), int(comp.height * s)), Image.LANCZOS).save(
                os.path.join(HERE, "read", f"B_{pg}_{h}_{i}.png"))
