"""Contact sheets of Mahadevan sign drawings for blind visual decomposition (no corpus data read)."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
R = Path(__file__).resolve().parents[2]
out = R / "experiments/modifiers/sheets"; out.mkdir(exist_ok=True)
T, COLS, ROWS = 130, 10, 5
try:
    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
except Exception:
    font = ImageFont.load_default()
ids = list(range(1, 418))
for p in range(0, len(ids), COLS * ROWS):
    chunk = ids[p:p + COLS * ROWS]
    sheet = Image.new("RGB", (COLS * T, ROWS * (T + 22)), "white")
    d = ImageDraw.Draw(sheet)
    for k, n in enumerate(chunk):
        im = Image.open(R / f"data/sign_images/M{n}.png").convert("RGBA")
        bg = Image.new("RGBA", im.size, "white"); bg.alpha_composite(im)
        im = bg.convert("RGB").resize((T - 10, T - 10))
        x, y = (k % COLS) * T, (k // COLS) * (T + 22)
        sheet.paste(im, (x + 5, y + 22))
        d.text((x + 5, y + 2), f"M{n}", fill="red", font=font)
        d.rectangle([x, y, x + T - 1, y + T + 21], outline="#ccc")
    sheet.save(out / f"sheet_{p // (COLS * ROWS):02d}.png")
print("ok")
