"""Report figures + results.json (after the confirmatory run). Exploratory only; no new tests.
Run: .venv/bin/python -I experiments/protocuneiform/s3_report.py
"""
import json, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from s1_freeze import ink_of, first_exemplar  # noqa: E402

R = json.load(open(HERE / "test_results.json"))
pc = json.load(open(HERE / "pc_pool.json")); pe = json.load(open(HERE / "pe_pool.json"))
rows = [r for r in R["pairs_table"] if r["pc_class"] != "UNKNOWN" and r["dev"]]
cell = 120
W = Image.new("RGB", (4 * 3 * cell, ((len(rows) + 3) // 4) * (cell + 34)), "white"); dr = ImageDraw.Draw(W)


def thumb(p, crop=False):
    ink = ink_of(p)
    if crop: ink = first_exemplar(ink)
    ys, xs = np.nonzero(ink); ink = ink[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    im = Image.fromarray((~ink * 255).astype(np.uint8)); im.thumbnail((cell - 16, cell - 16)); return im


for n, r in enumerate(rows):
    rr, c = divmod(n, 4); x0, y0 = c * 3 * cell, rr * (cell + 34)
    for k, (p, crop) in enumerate([(ROOT / f"data/sign_images/{r['indus']}.png", False), (HERE / pc[r["pc"]]["image"], True),
                                   (HERE / pe[r["pe"]]["image"], False)]):
        W.paste(thumb(p, crop), (x0 + k * cell + 6, y0 + 4))
    d = r["dev"]
    dr.text((x0 + 4, y0 + cell - 6), f"{r['indus']}  ~ {r['pc']} ({r['pc_class'][:9]})  ~ PE {r['pe']}", fill="black")
    dr.text((x0 + 4, y0 + cell + 8), f"dev n={d['n']} after-num={d['AN']:.2f} end={d['END2']:.2f} init={d['INIT']:.2f}", fill=(90, 90, 90))
    dr.line([(x0 + 3 * cell - 2, y0), (x0 + 3 * cell - 2, y0 + cell + 30)], fill=(190, 190, 190))
W.save(HERE / "classed_pairs.png")

out = {"area": "protocuneiform", "date": "2026-11-15",
       "verdict": R["verdict"], "power_dev": R["power_dev"],
       "n_supported": sum(v["supported"] for v in R["verdict"].values()),
       "confirmatory": R["confirmatory"],
       "exploratory_fullpool": {k: v for k, v in R["exploratory"].items() if k.startswith("fullpool")},
       "shape_control": json.load(open(HERE / "shape_control.json")),
       "corpora": {"pc_texts": 4965, "pc_lines": 28967, "pe_texts": 1443, "pe_lines": 10297, "pc_pool": len(pc), "pe_pool": len(pe),
                   "indus_pool": 196, "lookalike_sets": 66},
       "tests_run": {"confirmatory": 15, "exploratory": 34, "power_sims": 5}}
json.dump(out, open(HERE / "results.json", "w"), indent=1)
print("ok", len(rows))
