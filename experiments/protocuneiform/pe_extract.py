"""Render Proto-Elamite sign glyphs from Pandey 2023 (L2/23-196) repertoire table (untrusted PDF, read only).
Each table row: glyph in font Uni1BD00ProtoElamite..., then CDLI name in Consolas. Output pe_signs/<name>.png
Run: .venv/bin/python -I experiments/protocuneiform/pe_extract.py
"""
import json, re
from pathlib import Path
import pymupdf

HERE = Path(__file__).resolve().parent
OUT = HERE / "pe_signs"; OUT.mkdir(exist_ok=True)
d = pymupdf.open(HERE / "raw/pe_pandey/23196-proto-elamite.pdf")
names = {}
for pno in range(d.page_count):
    p = d[pno]
    txt = p.get_text()
    if "CDLI Name" not in txt or "Unicode Character Name" not in txt:
        continue
    spans = []
    for b in p.get_text("rawdict")["blocks"]:
        for l in b.get("lines", []):
            for s in l["spans"]:
                t = "".join(c["c"] for c in s["chars"])
                spans.append((s["font"], t, s["bbox"], s["chars"]))
    glyphs = [(t.strip(), bb, ch) for f, t, bb, ch in spans if "ProtoElamite" in f and t.strip()]
    labels = [(t, bb) for f, t, bb, _ in spans if f.startswith("Consolas") and re.match(r"^(M\d|\d+\(N|\|)", t)]
    for g, gb, ch in glyphs:
        cy = (gb[1] + gb[3]) / 2
        cands = [(abs((lb[1] + lb[3]) / 2 - cy), t) for t, lb in labels if lb[0] > gb[2] and lb[0] - gb[2] < 40]
        if not cands:
            continue
        dist, name = min(cands)
        if dist > 8 or name in names:
            continue
        c = [x for x in ch if x["c"].strip()][0]
        bb = pymupdf.Rect(c["bbox"])
        clip = pymupdf.Rect(bb.x0 - 1, bb.y0 - 1, bb.x1 + 1, bb.y1 + 1)
        pix = p.get_pixmap(matrix=pymupdf.Matrix(8, 8), clip=clip, colorspace=pymupdf.csGRAY)
        fn = re.sub(r"[^A-Za-z0-9~+()|._-]", "_", name) + ".png"
        pix.save(OUT / fn)
        names[name] = {"file": fn, "page": pno + 1, "codepoint": hex(ord(c["c"]))}
json.dump(names, open(HERE / "pe_signs.json", "w"), indent=0)
print(len(names), "PE glyphs rendered")
