"""Step 1: full inventory of numeral signs (M77 + ICIT) and every adjacent numeral sequence,
plus a contact sheet. Run after the held-out test (uses all distinct texts)."""
import csv, json, sys
from collections import Counter, defaultdict
sys.path.insert(0, "experiments/numeral_grammar")
from common import *
from PIL import Image, ImageDraw, ImageFont

OUT = ROOT / "experiments/numeral_grammar"
M = distinct(m77_texts()); I = distinct(icit_texts())
cM = Counter(s for t in M for s in t["seq"]); cI = Counter(s for t in I for s in t["seq"])

rows = []
for s, (c, v, lay) in M_NUM.items():
    rows.append(dict(corpus="M77", sign=s, cls=c, value=v, layout=lay, distinct_text_tokens=cM[s]))
for s, (c, v, lay) in W_NUM.items():
    rows.append(dict(corpus="ICIT", sign=s, cls=c, value=v, layout=lay, distinct_text_tokens=cI[s]))
with open(OUT / "inventory.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

seqs = defaultdict(Counter); examples = defaultdict(list)
for name, texts, table in (("M77", M, M_NUM), ("ICIT", I, W_NUM)):
    for t in texts:
        for g in groups_from_runs(t["seq"], table):
            if len(g["group"]) > 1:
                k = key(g["group"]); seqs[k][name] += 1
                if len(examples[k]) < 3:
                    examples[k].append(f"{name} {t['site']}: " + " ".join(s for s, _, _ in g["group"]))
with open(OUT / "pairs.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["sequence", "M77_distinct", "ICIT_distinct", "examples"])
    for k in sorted(seqs, key=lambda k: -(seqs[k]["M77"] + seqs[k]["ICIT"])):
        w.writerow([k, seqs[k]["M77"], seqs[k]["ICIT"], " ; ".join(examples[k])])

# summary numbers
summ = {}
for name, texts, table in (("M77", M, M_NUM), ("ICIT", I, W_NUM)):
    L = Counter(); orderS1 = Counter(); with12 = Counter()
    for t in texts:
        for g in groups_from_runs(t["seq"], table):
            L[len(g["group"])] += 1
            if len(g["group"]) > 1 and any(v == 12 for _, c, v in g["group"]):
                with12[key(g["group"])] += 1
    summ[name] = dict(group_lengths=dict(L), groups_with_12=dict(with12))
json.dump(summ, open(OUT / "inventory_summary.json", "w"), indent=1)
print(json.dumps(summ, indent=1))

# contact sheet: M77 drawings grouped by class, then the Wells numeral strip
order = [("Short strokes", [s for s in M_NUM if M_NUM[s][0] in "SC"]),
         ("Tall strokes", [s for s in M_NUM if M_NUM[s][0] == "T"]),
         ("Chevrons and arcs", [s for s in M_NUM if M_NUM[s][0] in "VA"])]
W, H, cols = 120, 150, 12
try:
    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 13)
    big = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
except Exception:
    font = big = ImageFont.load_default()
nrows = sum((len(v) + cols - 1) // cols for _, v in order)
wells = Image.open(ROOT / "sources/paragorth_Indus-/data/derived/dark/loop57_images/wells_glyphs_sheet0.png").convert("RGB")
wstrip = wells.crop((0, 0, 1024, 222))
sheet = Image.new("RGB", (cols * W, nrows * H + 40 * len(order) + 260 + 60), "white")
d = ImageDraw.Draw(sheet); y = 10
for title, signs in order:
    d.text((10, y), title + " (Mahadevan 1977; value, layout, distinct-text tokens)", fill="black", font=big); y += 30
    for i, s in enumerate(signs):
        x = (i % cols) * W; yy = y + (i // cols) * H
        im = Image.open(ROOT / f"data/sign_images/{s}.png").convert("RGB"); im.thumbnail((90, 90))
        sheet.paste(im, (x + 15, yy + 5))
        c, v, lay = M_NUM[s]
        d.text((x + 8, yy + 98), f"{s}  ={v}" + ("c" if c == "C" else ""), fill="black", font=font)
        d.text((x + 8, yy + 114), f"{lay[:10]}  n={cM[s]}", fill=(90, 90, 90), font=font)
    y += ((len(signs) + cols - 1) // cols) * H + 10
d.text((10, y), "ICIT / Wells numeral glyphs (Wells numbers under each; W056 = one 3-row block of 7-8 strokes, read M121 M121 by Mahadevan)", fill="black", font=big)
sheet.paste(wstrip, (10, y + 30))
sheet.save(OUT / "contact_sheet.png")
print("saved", OUT / "contact_sheet.png", sheet.size)
