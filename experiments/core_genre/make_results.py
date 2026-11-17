"""Collect key numbers into results.json. Usage: .venv/bin/python -I experiments/core_genre/make_results.py"""
import json
from pathlib import Path
H = Path(__file__).resolve().parent
A = json.load(open(H / "partA.json")); D = json.load(open(H / "partA_dist.json")); Cc = json.load(open(H / "partA_calib.json"))
S = json.load(open(H / "partB_score.json"))
m = lambda s: {k: (v["mean"] if v else None) for k, v in s.items()}
out = {
  "partA": {
    "verdict": "WEAKENED",
    "indus_core_dev": m(A["indus_core_dev"]), "indus_core_heldout": m(A["indus_core_heldout"]),
    "A1_merge": {nm: m(A["A1_inventory"][nm]["merge"]) for nm in ("sanskrit", "chinese_given", "sangam", "old_english", "greek", "ur3")},
    "A1_merge_slot": {nm: m(A["A1_inventory"][nm]["merge_slot"]) for nm in ("sanskrit", "chinese_given", "sangam")},
    "A2_grammar_free": {k: m(v["stats"]) for k, v in A["A2_core_definition"].items()},
    "A3_syllables": {nm: m(v["syll"]) for nm, v in A["A3_syllables"].items()},
    "A4_numerals": A["A4_numerals"],
    "distance_labels": D["summary"], "recalibrated_nn": {v: {"median": Cc[v]["median"], "max": Cc[v]["max"]} for v in Cc},
  },
  "partB": {k: {kk: v[kk] for kk in ("label", "nn_d", "ref_nn_median", "ref_nn_max", "nearest", "tied_with_nearest",
                                       "category", "best_by_group", "loso_nearest", "nearest_pooled")} for k, v in S.items()},
  "partB_decisions": {"R1": "not outlier (raw peripheral; merge, sym typical; both splits)",
                      "R2": "undecided", "R3": "no single genre (lead: Linear B entry lines, sym)", "R4": "codes never nearer than names (0/6)"},
}
json.dump(out, open(H / "results.json", "w"), indent=1, ensure_ascii=False)
print("ok")
