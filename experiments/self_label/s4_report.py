"""Summary sheet, results.json and ledger rows from results_raw.json (+ redteam_bangle.json).
Run: .venv/bin/python -I experiments/self_label/s4_report.py
"""
import csv
import json
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "experiments/self_label"
raw = json.load(open(OUT / "results_raw.json"))
fr = json.load(open(OUT / "frozen_candidates.json"))
rt = json.load(open(OUT / "redteam_bangle.json"))
import sys; sys.path.insert(0, str(OUT))
from shapes import SILHOUETTES  # noqa: E402

icit = {(x["cls"], x["sign"]): x for x in raw["sets"]["icit"]["rows"]}
ho = {(x["cls"], x["sign"]): x for x in raw["sets"]["m77_heldout_v2"]["rows"]}
dev = {(x["cls"], x["sign"]): x for x in raw["sets"]["m77_dev"]["rows"]}

# ---- results sheet: per class, first silhouette + frozen signs of each route with ICIT obs/exp
cell = 96
routes = ["chamfer", "catalogue", "hu"]
classes = list(SILHOUETTES)
W, H = 150 + cell * (1 + 9) + 30, 40 + len(classes) * (cell + 28)
sheet = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(sheet)
d.text((150, 6), "object silhouette | chamfer top-3 | catalogue top-3 | Hu top-3   (ICIT obs/exp on that object class; * = confirmed)", fill="black")
for i, cls in enumerate(classes):
    y = 30 + i * (cell + 28)
    d.text((5, y + 35), cls, fill="black")
    name = list(SILHOUETTES[cls])[0]
    sheet.paste(Image.open(OUT / "silhouettes" / f"{name}.png").convert("RGB").resize((84, 84)), (150, y))
    for r_i, r in enumerate(routes):
        for k, x in enumerate(fr["classes"][cls][r]):
            s = x["sign"]
            xx = 150 + cell * (1 + r_i * 3 + k) + r_i * 10
            im = Image.open(ROOT / f"data/sign_images/{s}.png").convert("RGBA")
            bg = Image.new("RGBA", im.size, "white")
            bg.alpha_composite(im)
            sheet.paste(bg.convert("RGB").resize((80, 80)), (xx, y))
            row = icit.get((cls, s))
            lab = f"{s} {row['obs']}/{row['exp']:.1f}" if row else f"{s} n/a"
            if (cls, s) in [tuple(p) for p in raw["confirmed_pairs"]]:
                lab += " *"
            d.text((xx, y + 82), lab, fill="black")
sheet.save(OUT / "results_sheet.png")

# ---- results.json
res = {
    "area": "self_label",
    "question": "Do signs depict the object they are written on?",
    "prereg": "docs/prereg/self_label.md",
    "n_frozen_pairs": raw["n_pairs"],
    "untestable_classes": {"weight": "no inscribed weights", "bead": "2 ICIT items",
                           "copper tablet": "one site only: cannot pass second-site rule"},
    "confirmed_pairs": raw["confirmed_pairs"],
    "verdict": raw["verdict"],
    "decision": "NULL for the decisive bar (needs >=2 signs); 1 single lead (bangle x M373/W790)",
    "global_tests": raw["global"],
    "bangle_M373": {"icit": icit[("bangle", "M373")], "redteam_exploratory": rt},
    "copper_M169_hu": {"dev": dev.get(("copper tablet", "M169")), "heldout": ho.get(("copper tablet", "M169")),
                       "icit": icit.get(("copper tablet", "M169")),
                       "note": "enriched in all three sets but fails C2 by design (one site); found by the Hu route, "
                               "flagged unreliable before testing; M169 is a known copper-legend sign"},
    "jar_M342_on_pottery": {"dev": dev.get(("pottery graffito", "M342")), "heldout": ho.get(("pottery graffito", "M342")),
                            "icit": icit.get(("pottery graffito", "M342"))},
}
json.dump(res, open(OUT / "results.json", "w"), indent=1, default=float)

# ---- ledger rows
L = ROOT / "docs/test_ledger.csv"
cols = next(csv.reader(open(L)))
existing = {r["id"] for r in csv.DictReader(open(L))}
n_icit = len(raw["sets"]["icit"]["rows"])
rows = []
b = icit[("bangle", "M373")]
rep = [r for r in b["site_rep"] if r["p"] < 0.05][0]
rows.append(dict(id="sl_bangle_M373_icit", claim="Oval sign M373 (=W790, bridge-lumped with M261/M374) enriched on bangles (self-label)",
                 statistic=f"{b['obs']}/{b['n_cls']} bangle texts vs {b['exp']} exp, register pct {b['register_pct']:.2f}",
                 p_value=f"{b['p']:.2g}", n=f"{b['n_cls']} bangle texts", split="ICIT", mode="confirmatory",
                 note=f"BH q={b['q']:.3f} over {n_icit} frozen ICIT pairs; found by catalogue route only"))
rows.append(dict(id="sl_bangle_M373_site2", claim="same, second site (Harappa)",
                 statistic=f"{rep['obs']}/{rep['n_cls']} vs {rep['exp']} exp", p_value=f"{rep['p']:.2g}",
                 n=f"{rep['n_cls']} Harappa bangle texts", split="ICIT", mode="confirmatory",
                 note="2 texts, one broken; no bangles in M77 so no held-out v2 test"))
rows.append(dict(id="sl_bangle_M373_len", claim="same, length- and site-matched control",
                 statistic=f"{rt['length_site_matched']['obs']} vs {rt['length_site_matched']['exp']:.2f} exp",
                 p_value=f"{rt['length_site_matched']['p']:.2g}", n="41 bangle texts", split="ICIT", mode="exploratory",
                 note="redteam, not preregistered"))
rows.append(dict(id="sl_decisive", claim=">=2 signs depict the object they are written on (decisive bar)",
                 statistic=f"{raw['verdict']['n_confirmed_signs']} sign confirmed of {raw['n_pairs']} frozen pairs",
                 p_value="", n=f"{raw['n_pairs']} pairs", split="ICIT+v2", mode="confirmatory", note="fail"))
for g in raw["global"]:
    rows.append(dict(id=f"sl_global_{g['route']}_{g['set']}",
                     claim=f"Shape-nearest signs ({g['route']} route) enriched on their object beyond register",
                     statistic=f"mean register pct {g['mean_pct']} vs null {g['null_mean']}", p_value=f"{g['p']:.3g}",
                     n=f"{g['n']} frozen signs", split={"m77_dev": "dev", "m77_heldout_v2": "v2", "icit": "ICIT"}[g["set"]],
                     mode="confirmatory", note="Bonferroni alpha 0.0056 over 9" + ("; reversed (depleted)" if g["mean_pct"] < 0.4 else "")))
c = icit[("copper tablet", "M169")]
rows.append(dict(id="sl_copper_M169", claim="M169 (Hu-route pick for copper tablet) enriched on copper tablets",
                 statistic=f"ICIT {c['obs']} vs {c['exp']}; dev q 0.006; v2 p 0.006", p_value=f"{c['p']:.2g}",
                 n="98 ICIT copper texts", split="ICIT", mode="confirmatory",
                 note="fails second-site rule by design (MD only); Hu route visibly poor match; copper-legend register word"))
for r in rows:
    r.update(area="self_label", file="experiments/self_label/RESULTS.md", p_source="permutation",
             distinct_text_unit="yes", family="self_label", family_size=str(raw["n_pairs"]),
             replicated_independently="no", readme_claim="")
with open(L, "a", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    for r in rows:
        if r["id"] not in existing:
            w.writerow({k: r.get(k, "") for k in cols})
print("ledger rows", len(rows), "sheet + results.json written")
