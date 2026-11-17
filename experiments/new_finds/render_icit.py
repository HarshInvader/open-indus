"""Render ICIT texts of given sites with the ICIT font (W n -> U+E000+n) for visual novelty checks.
Signs are drawn right-to-left (first sign at the right), as on an impression.
    .venv/bin/python -I experiments/new_finds/render_icit.py SITE [SITE...]
Writes experiments/new_finds/icit_render/<site>_<k>.png (40 texts per sheet)."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from corpus.load import icit_texts
OUT = ROOT / "experiments" / "new_finds" / "icit_render"; OUT.mkdir(exist_ok=True)
FONT = ImageFont.truetype(str(ROOT / "experiments/new_finds/raw/font/indus-font.ttf"), 34)
LAB = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 15)
PER, RH, WID = 40, 50, 1100
for site in sys.argv[1:]:
    ts = [t for t in icit_texts() if t["site"] == site]
    for k in range(0, len(ts), PER):
        ch = ts[k:k + PER]
        S = Image.new("RGB", (WID, RH * len(ch)), "white"); d = ImageDraw.Draw(S)
        for i, t in enumerate(ch):
            y = i * RH
            lab = f"{t['id']} {t['cisi']} {t['type']} {t['symbol']} {t['width_mm']}x{t['height_mm']}"
            d.text((4, y + 4), lab, fill="red", font=LAB)
            d.text((4, y + 24), " ".join(x[1:] for x in t["seq"]), fill="blue", font=LAB)
            x = WID - 10
            for s in t["seq"]:
                if s in ("|",):
                    x -= 20; d.line([(x + 8, y + 5), (x + 8, y + RH - 5)], fill="green"); continue
                if s == "#":
                    x -= 24; d.text((x, y + 10), "#", fill="gray", font=LAB); continue
                ch_ = chr(0xE000 + int(s[1:]))
                w = d.textlength(ch_, font=FONT)
                x -= int(w) + 6
                d.text((x, y + 4), ch_, fill="black", font=FONT)
            d.line([(0, y + RH - 1), (WID, y + RH - 1)], fill=(220, 220, 220))
        S.save(OUT / f"{site.replace(' ', '_').replace('/', '')}_{k // PER + 1}.png")
    print(site, len(ts))
