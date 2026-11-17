"""Contact sheets of all Mahadevan sign drawings (data/sign_images) for visual transcription.
    .venv/bin/python experiments/new_finds/make_refsheets.py
Writes experiments/new_finds/refsheets/M_sheet_{k}.png (70 signs each) and mirrored versions."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "data" / "sign_images"; OUT = ROOT / "experiments" / "new_finds" / "refsheets"
OUT.mkdir(exist_ok=True)
ids = sorted(int(p.stem[1:]) for p in SRC.glob("M*.png"))
CELL, COLS, PER = 110, 10, 70
try:
    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
except Exception:
    font = ImageFont.load_default()
for k in range(0, len(ids), PER):
    chunk = ids[k:k + PER]; rows = (len(chunk) + COLS - 1) // COLS
    sheet = Image.new("RGB", (COLS * CELL, rows * CELL), "white"); d = ImageDraw.Draw(sheet)
    for i, n in enumerate(chunk):
        im = Image.open(SRC / f"M{n}.png").convert("L"); im.thumbnail((CELL - 10, CELL - 30))
        x, y = (i % COLS) * CELL, (i // COLS) * CELL
        sheet.paste(im, (x + (CELL - im.width) // 2, y + 24))
        d.text((x + 4, y + 2), f"M{n}", fill="red", font=font)
        d.rectangle([x, y, x + CELL - 1, y + CELL - 1], outline=(200, 200, 200))
    sheet.save(OUT / f"M_sheet_{k // PER + 1}.png")
print(len(ids), "signs")
