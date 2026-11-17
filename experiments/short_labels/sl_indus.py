"""Run the battery on Indus (run only after docs/prereg/short_labels.md is frozen).

usage: .venv/bin/python experiments/short_labels/sl_indus.py dev|heldout [R]
  dev     -> out/indus_dev.jsonl: R dev subsamples at size A (held-out length list) and at size B
  heldout -> out/indus_heldout.jsonl: full held-out (size A) + R held-out subsamples at size B
"""
import sys, json, random
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parents[1] / "experiments/language_vs_code"))
from sl_corpora import indus  # noqa
from sl_calibrate import lens  # noqa
from lvc_metrics import battery, matched_sample  # noqa

split = sys.argv[1]
R = int(sys.argv[2]) if len(sys.argv) > 2 else 40
LENS = lens()
X = indus(split)
rows = []
if split == "heldout":
    r0 = battery(X, seed=0); r0.update(corpus="indus_heldout_full", size="A", rep=-1, n=len(X)); rows.append(r0)
for size in (("A", "B") if split == "dev" else ("B",)):
    for r in range(R):
        S = matched_sample(X, LENS[size], random.Random(1000 + r))
        res = battery(S, seed=r); res.update(corpus=f"indus_{split}_sub", size=size, rep=r, n=len(S)); rows.append(res)
with open(HERE / f"out/indus_{split}.jsonl", "w") as f:
    for r in rows: f.write(json.dumps(r, default=float) + "\n")
print(len(rows), "rows")
