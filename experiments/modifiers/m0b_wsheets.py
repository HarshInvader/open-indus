"""Contact sheets of Wells glyphs (font U+E000+n) for mapping frozen M pairs to Wells codes. Uses only the set of codes present, no counts."""
import json
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
R = Path(__file__).resolve().parents[2]
out = R / "experiments/modifiers/sheets"
F = ImageFont.truetype(str(R / "sources/paragorth_Indus-/tools/indus_font.ttf"), 64)
L = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
codes = set()
for l in open(R / "data/icit_texts.jsonl"):
    codes |= {x for x in json.loads(l)["seq"] if x.startswith("W")}
codes = sorted(int(c[1:]) for c in codes)
T, C, RW = 110, 12, 8
for p in range(0, len(codes), C * RW):
    ch = codes[p:p + C * RW]
    sh = Image.new("RGB", (C * T, RW * (T + 18)), "white"); d = ImageDraw.Draw(sh)
    for k, n in enumerate(ch):
        x, y = (k % C) * T, (k // C) * (T + 18)
        d.text((x + 4, y + 1), f"W{n}", fill="red", font=L)
        d.text((x + 20, y + 22), chr(0xE000 + n), fill="black", font=F)
        d.rectangle([x, y, x + T - 1, y + T + 17], outline="#ccc")
    sh.save(out / f"wsheet_{p // (C * RW):02d}.png")
print(len(codes))
