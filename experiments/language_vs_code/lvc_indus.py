"""Run the battery on Indus.

usage: lvc_indus.py dev        -> out/indus_dev.jsonl   (full dev + R subsamples at held-out size)
       lvc_indus.py heldout    -> out/indus_heldout.jsonl (full held-out; run only after prereg)
"""
import sys, json, random
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from lvc_corpora import indus  # noqa
from lvc_metrics import battery, matched_sample  # noqa

split = sys.argv[1]
R = int(sys.argv[2]) if len(sys.argv) > 2 else 25
OUT = HERE / "out"; OUT.mkdir(exist_ok=True)
rows = []
X = indus(split)
r0 = battery(X, seed=0); r0.update(corpus="indus_" + split, size="dev" if split == "dev" else "heldout", rep=-1, n=len(X))
rows.append(r0); print(json.dumps(r0))
if split == "dev":
    # subsamples of dev at held-out size and length mix (lengths only from held-out)
    ho_lens = [len(t) for t in indus("heldout")]
    for r in range(R):
        rng = random.Random(1000 + r)
        S = matched_sample(X, ho_lens, rng)
        res = battery(S, seed=r); res.update(corpus="indus_dev_sub", size="heldout", rep=r, n=len(S))
        rows.append(res)
with open(OUT / f"indus_{split}.jsonl", "w") as f:
    for r in rows: f.write(json.dumps(r) + "\n")
