"""Contact sheet: python -I sheet.py out.png cols img1 img2 ...  (labels each tile with filename)"""
import sys
from PIL import Image, ImageDraw

out, cols, files = sys.argv[1], int(sys.argv[2]), sys.argv[3:]
ims = [Image.open(f).convert("RGB") for f in files]
w = max(i.width for i in ims)
h = max(i.height for i in ims)
rows = (len(ims) + cols - 1) // cols
sheet = Image.new("RGB", (cols * w, rows * (h + 14)), "white")
d = ImageDraw.Draw(sheet)
for k, (f, im) in enumerate(zip(files, ims)):
    x, y = (k % cols) * w, (k // cols) * (h + 14)
    sheet.paste(im, (x, y + 14))
    d.text((x + 2, y), f.split("/")[-1], fill="red")
sheet.save(out)
