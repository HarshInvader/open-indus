"""Contact sheets for eye inspection: sheets.py NAME [PER_SHEET] [CELL]
Reads raw/records_NAME.jsonl and raw/img/<nat>.jpg; writes raw/sheets_NAME/sheet_XX.jpg with a numbered label per cell
and raw/sheets_NAME/index.json mapping the cell number to (ypm, nat)."""
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"


def main(name, per=6, cell=700):
    recs = [json.loads(l) for l in (RAW / f"records_{name}.jsonl").read_text().splitlines()]
    items = [(r.get("ypm"), n) for r in recs for n in r["nat"] if (RAW / "img" / f"{n}.jpg").exists()]
    out = RAW / f"sheets_{name}"; out.mkdir(exist_ok=True)
    cols = 3
    rows = (per + cols - 1) // cols
    index = {}
    for s in range(0, len(items), per):
        sheet = Image.new("RGB", (cols * cell, rows * cell), "white")
        d = ImageDraw.Draw(sheet)
        for k, (ypm, nat) in enumerate(items[s:s + per]):
            im = Image.open(RAW / "img" / f"{nat}.jpg").convert("RGB")
            im.thumbnail((cell - 10, cell - 30))
            x, y = (k % cols) * cell, (k // cols) * cell
            sheet.paste(im, (x + 5, y + 28))
            num = s + k
            d.rectangle([x, y, x + 260, y + 24], fill="yellow")
            d.text((x + 4, y + 4), f"#{num} {ypm}", fill="black")
            index[num] = [ypm, nat]
        sheet.save(out / f"sheet_{s // per:03d}.jpg", quality=85)
    (out / "index.json").write_text(json.dumps(index, indent=0))
    print(len(items), "items,", (len(items) + per - 1) // per, "sheets")


if __name__ == "__main__":
    main(sys.argv[1], *(int(x) for x in sys.argv[2:]))
