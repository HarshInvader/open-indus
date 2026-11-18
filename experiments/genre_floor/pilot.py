"""Pilot (before prereg, no unsupervised model looks at any plant label): chaining fix stats,
supervised-gain mapping of plant strength, and run time of one detection.
Usage: board/run.sh .venv/bin/python -I experiments/genre_floor/pilot.py"""
import json, sys, time, warnings
warnings.filterwarnings("ignore")
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import floor  # noqa: E402

out = {}
us = floor.indus_pool()
out["chain_indus"] = floor.chain_stats(us)
tr, te = floor.make("CUN", 1.0, 0)
out["chain_cun"] = floor.chain_stats(tr + te)
print(out, flush=True)
gain = {}
for kind, grid in (("VOC", [0.5, 1.0]), ("FORM", [0.25, 0.5, 1.0]), ("LEN", [0.5, 1.0]), ("MIX", [0.25, 0.5, 1.0]),
                   ("CUN", [0.1, 0.2, 0.4, 1.0])):
    for s in grid:
        tr, te = floor.make(kind, s, 0)
        gain[f"{kind}_{s}"] = round(floor.lr_gain(tr, te, [u["y"] for u in tr], [u["y"] for u in te]), 3)
        print(kind, s, len(tr), len(te), gain[f"{kind}_{s}"], flush=True)
out["gain"] = gain
for name in ("HMM", "LCA"):
    t = time.time()
    tr, te = floor.make("MIX", 1.0, 0)
    r = floor.detect(name, tr, te, 0)
    out[f"time_{name}"] = time.time() - t
    print(name, round(time.time() - t), flush=True)
json.dump(out, open(HERE / "pilot.json", "w"), indent=1)
