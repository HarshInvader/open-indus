"""F4-A1 (prereg forward_predictions.md amendment A1). Run after fp.py --mode <m>; reads results_<m>.json.
    .venv/bin/python -I experiments/forward_predictions/fp_a1.py --mode forward
"""
import json, argparse
from pathlib import Path
OUT = Path(__file__).resolve().parent
ap = argparse.ArgumentParser(); ap.add_argument("--mode", choices=["dryrun", "forward"], required=True)
m = ap.parse_args().mode
R = json.load(open(OUT / f"results_{m}.json"))
f = R["F4"]; n = f["n"]
a = dict(n=n, min_n=10, evaluable=n >= 10)
if n:
    s5 = f["test_cup_N"].get("5", 0) / n; g = f["gain_bits_per_unit"]
    a.update(share_5=round(s5, 4), gain_bits_per_unit=g)
    a["verdict"] = ("pass" if s5 <= 0.02 and g > 0 else "fail" if s5 > 0.05 or g < 0 else "neither") if n >= 10 else "not evaluable"
else:
    a["verdict"] = "not evaluable"
R["F4_A1"] = a
json.dump(R, open(OUT / f"results_{m}.json", "w"), indent=1, default=float)
print(json.dumps(a))
