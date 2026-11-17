"""Step 1 (blind): rank every sign drawing against each object silhouette and freeze top-k.
No object-class distribution of any sign is read here. The only corpus statistic used is
overall sign frequency (to define a testable pool), which carries no object information.

Run: .venv/bin/python -I experiments/self_label/s1_freeze.py
"""
import csv
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from corpus.load import m77_texts, distinct  # noqa: E402
from shapes import (KEYWORDS, KW_CLASS, OUT, ROOT, SILHOUETTES, chamfer, hu_dist,  # noqa: E402
                    load_sign, loghu, normalise, render)

K = 3
MIN_FREQ = 5  # distinct M77 texts containing the sign, all object types pooled

# pool: frequency only
freq = Counter()
for t in distinct(m77_texts()):
    for s in set(t["seq"]):
        if s.startswith("M"):
            freq[s] += 1
pool = sorted([s for s, c in freq.items() if c >= MIN_FREQ], key=lambda s: int(s[1:]))
print("pool size", len(pool))

signs = {}
for s in pool:
    filled, sk = normalise(load_sign(int(s[1:])))
    signs[s] = (filled, sk, loghu(filled))

(OUT / "silhouettes").mkdir(exist_ok=True)
sil = {}
for cls, d in SILHOUETTES.items():
    for name, polys in d.items():
        m = render(polys)
        Image.fromarray((~m).astype(np.uint8) * 255).save(OUT / "silhouettes" / f"{name}.png")
        filled, sk = normalise(m)
        sil[name] = (cls, filled, sk, loghu(filled))

dist = {"chamfer": {}, "hu": {}}
for name, (cls, f, sk, h) in sil.items():
    dist["chamfer"][name] = {s: float(chamfer(sk, v[1])) for s, v in signs.items()}
    dist["hu"][name] = {s: hu_dist(h, v[2]) for s, v in signs.items()}

frozen = {"k": K, "min_freq": MIN_FREQ, "pool": pool, "classes": {}}
for cls, d in SILHOUETTES.items():
    entry = {}
    for method in ("chamfer", "hu"):
        best = {s: min(dist[method][n][s] for n in d) for s in pool}
        via = {s: min(d, key=lambda n: dist[method][n][s]) for s in pool}
        ranked = sorted(pool, key=lambda s: (best[s], int(s[1:])))
        entry[method] = [{"sign": s, "dist": round(best[s], 4), "silhouette": via[s]} for s in ranked[:K]]
        entry[method + "_full_rank"] = ranked
    frozen["classes"][cls] = entry

# tertiary: referent catalogue keyword match (top-120 signs only)
cat = list(csv.DictReader(open(ROOT / "experiments/iconography/sign_referents.csv")))
for cls, kws in KEYWORDS.items():
    scored = []
    for r in cat:
        if r["sign"] not in pool:
            continue
        hits = sum(any(k in r[f"desc{i}"].lower() for k in kws) for i in (1, 2, 3))
        bonus = 0.5 if KW_CLASS.get(cls) and r["referent_class"] == KW_CLASS[cls] else 0
        if hits + bonus > 0:
            scored.append((-(hits + bonus), int(r["rank"]), r["sign"], hits + bonus))
    scored.sort()
    frozen["classes"][cls]["catalogue"] = [{"sign": s, "score": sc} for _, _, s, sc in scored[:K]]

json.dump(frozen, open(OUT / "frozen_candidates.json", "w"), indent=1)
json.dump(dist, open(OUT / "shape_distances.json", "w"))

# contact sheet: each silhouette, then its top-3 signs by chamfer and by Hu
cell = 110
rows = [(n, v[0]) for n, v in sil.items()]
W, H = cell * 7 + 160, cell * len(rows) + 30
sheet = Image.new("RGB", (W, H), "white")
dr = ImageDraw.Draw(sheet)
dr.text((170, 5), "silhouette | top-3 by chamfer (primary) | top-3 by Hu moments", fill="black")
for i, (name, cls) in enumerate(rows):
    y = 30 + i * cell
    dr.text((5, y + 40), f"{cls}\n{name}", fill="black")
    im = Image.open(OUT / "silhouettes" / f"{name}.png").convert("RGB").resize((100, 100))
    sheet.paste(im, (160, y))
    for j, method in enumerate(("chamfer", "hu")):
        ranked = sorted(pool, key=lambda s: (dist[method][name][s], int(s[1:])))[:K]
        for k, s in enumerate(ranked):
            x = 160 + cell * (1 + j * 3 + k) + (10 if j else 0)
            sim = Image.open(ROOT / f"data/sign_images/{s}.png").convert("RGBA")
            bg = Image.new("RGBA", sim.size, "white")
            bg.alpha_composite(sim)
            sheet.paste(bg.convert("RGB").resize((90, 90)), (x, y))
            dr.text((x, y + 92), f"{s} {dist[method][name][s]:.2f}", fill="black")
sheet.save(OUT / "contact_sheet.png")
for cls in frozen["classes"]:
    e = frozen["classes"][cls]
    print(cls, "| chamfer", [x["sign"] for x in e["chamfer"]], "| hu", [x["sign"] for x in e["hu"]],
          "| catalogue", [x["sign"] for x in e["catalogue"]])
