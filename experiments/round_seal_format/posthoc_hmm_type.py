"""POST-HOC (not pre-registered): what is #34's 'short numeral-opening' HMM type, in plain sign terms?
    .venv/bin/python -I experiments/round_seal_format/posthoc_hmm_type.py"""
import sys, json
from pathlib import Path
from collections import Counter
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "experiments/genres_scratch"), str(ROOT / "experiments/grammar"), str(ROOT)]
import data, glib
tri, tei = data.icit()
units = tri + tei
r = json.load(open(ROOT / "experiments/genres_scratch/out/main_icit_HMM.json"))
g = np.array(r["explore_assign_train"] + r["explore_assign_test"])
NUM = glib.NUM["ICIT"]
out = {}
for k in range(4):
    us = [u for u, z in zip(units, g) if z == k]
    first = Counter(u["runs"][0][0][0] for u in us if u["runs"][0][1])
    out[k] = dict(n=len(us), mean_len=round(float(np.mean([len(u["signs"]) for u in us])), 2),
                  numeral_first=round(sum(v for s, v in first.items() if s in NUM) / max(1, sum(first.values())), 3),
                  top_first=first.most_common(6),
                  round_n=sum(u["reg"] == "seal_round" for u in us), sq_share=round(sum(u["reg"] == "seal_sq" for u in us) / sum(u["reg"] == "seal_sq" for u in units), 3))
    print(k, out[k])
rd = [(u["key"], int(z)) for u, z in zip(units, g) if u["reg"] == "seal_round"]
print("round by type", Counter(z for _, z in rd))
json.dump(out, open(Path(__file__).parent / "posthoc_hmm_type.json", "w"), indent=1)
