"""P3: build blind reader packets outside the repo (/tmp/pc_readers/).
- P-set: the 20 plate crops; C-set: the CISI crops. Each set gets its own random IDs (seed 7117) and order.
- Readers see only images named by ID and the sign chart; no plate number, site, M77/ICIT text.
- CISI crops are upscaled (Lanczos) so the long side is 800 px, for display only (adds no detail).
- Sign chart: all 417 Mahadevan drawings in labelled sheets of 70 (chart_01..06.png).
The key (ID -> seal) is written to work/reader_key.csv, which readers never see.
Run: .venv/bin/python -I experiments/plate_corpus/p3_reader_packets.py"""
import csv, os, random, re, shutil
from PIL import Image, ImageDraw
D = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(os.path.dirname(D))
OUT = "/tmp/pc_readers"


def chart():
    files = sorted(os.listdir(os.path.join(REPO, "data/sign_images")), key=lambda f: int(re.sub(r"\D", "", f)))
    per, cols, cell = 70, 10, 130
    for k in range(0, len(files), per):
        chunk = files[k:k + per]
        rows = (len(chunk) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * cell, rows * (cell + 18)), "white"); dr = ImageDraw.Draw(sheet)
        for i, f in enumerate(chunk):
            im = Image.open(os.path.join(REPO, "data/sign_images", f)).convert("RGBA")
            bg = Image.new("RGBA", im.size, "white"); bg.alpha_composite(im); im = bg.convert("RGB")
            im.thumbnail((cell - 14, cell - 14))
            x, y = (i % cols) * cell, (i // cols) * (cell + 18)
            sheet.paste(im, (x + 7, y + 18)); dr.text((x + 6, y + 3), f[:-4], fill=(200, 0, 0))
        sheet.save(os.path.join(OUT, f"chart_{k // per + 1:02d}.png"))


def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(os.path.join(OUT, "P")); os.makedirs(os.path.join(OUT, "C"))
    rows = list(csv.DictReader(open(os.path.join(D, "crops.csv"))))
    rng = random.Random(7117)
    key = []
    for setname, prefix in (("P", "plate"), ("C", "cisi")):
        items = [r for r in rows if os.path.exists(os.path.join(D, "crops", f"{prefix}_{r['key']}.png"))]
        ids = rng.sample(range(100, 1000), len(items))
        for r, i in zip(items, ids):
            rid = f"{setname}{i}"
            im = Image.open(os.path.join(D, "crops", f"{prefix}_{r['key']}.png")).convert("L")
            if setname == "C":
                s = 800 / max(im.size); im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
            im.save(os.path.join(OUT, setname, f"{rid}.png"))
            key.append(dict(reader_id=rid, set=setname, key=r["key"]))
    with open(os.path.join(D, "work", "reader_key.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["reader_id", "set", "key"]); w.writeheader(); w.writerows(key)
    chart()
    print("P", sum(k["set"] == "P" for k in key), "C", sum(k["set"] == "C" for k in key))


if __name__ == "__main__":
    main()
