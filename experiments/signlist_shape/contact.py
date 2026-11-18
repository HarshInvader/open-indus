"""Contact sheet of the top 30 proposed merges (greedy shape+context, in acceptance order = rank order).
    .venv/bin/python -I experiments/signlist_shape/contact.py"""
import json, sys
from pathlib import Path
from collections import Counter
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from corpus.load import dev_heldout, runs  # noqa

i1 = json.load(open(HERE / "out/i1.json"))
MODE = sys.argv[1] if len(sys.argv) > 1 else "both"
if MODE == "both":
    acc = i1["accepted_both_sims"][:30]
else:
    acc = [(a, b, sc, float("nan")) for a, b, d, sc in i1["accepted_shape"][:30]]
dl = {(a, b): d for a, b, d, _ in i1[f"accepted_{MODE}"]}
dev, _ = dev_heldout()
c = Counter(s for t in dev for r in runs(t["seq"]) for s in r)
W, H = 330, 150
cols = 3
rows = (len(acc) + cols - 1) // cols
sheet = Image.new("RGB", (W * cols, H * rows + 40), "white")
d = ImageDraw.Draw(sheet)
try:
    f = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 13)
    fb = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
except Exception:
    f = fb = ImageFont.load_default()
d.text((10, 10), f"Top 30 {MODE} merges (greedy, dev texts only). shape/ctx = pair percentile; dLL = CV gain", fill="black", font=fb)


def tile(s):
    im = Image.open(ROOT / "data/sign_images" / f"{s}.png").convert("RGBA")
    bg = Image.new("RGBA", im.size, "white"); bg.alpha_composite(im)
    return bg.convert("RGB").resize((100, 100))


for k, (a, b, ss, sc) in enumerate(acc):
    x0 = (k % cols) * W; y0 = 40 + (k // cols) * H
    sheet.paste(tile(a), (x0 + 10, y0 + 5)); sheet.paste(tile(b), (x0 + 120, y0 + 5))
    d.rectangle([x0 + 2, y0 + 2, x0 + W - 4, y0 + H - 4], outline=(200, 200, 200))
    d.text((x0 + 10, y0 + 108), f"#{k+1} {a} ({c[a]})  +  {b} ({c[b]})", fill="black", font=f)
    d.text((x0 + 10, y0 + 126), f"shape {ss:.3f}  ctx {sc:.2f}  dLL {dl[(a, b)]:.1f}", fill=(80, 80, 80), font=f)
name = "contact_top30.png" if MODE == "both" else f"contact_top30_{MODE}.png"
sheet.save(HERE / name)
print("wrote", HERE / name)
