"""S4 post hoc (NOT pre-registered): power of T1 at the claim's own sample size (10 slots) for weaker planted
pairs. Run after run.py:  .venv/bin/python -I experiments/s4_sixfish_rare_null/posthoc.py  -> posthoc.json
"""
import json, sys
from pathlib import Path
from collections import Counter
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import numpy as np
import run as R
from corpus.load import dev_heldout

dev, ho = dev_heldout(version=2)
Rd, Rh = R.m77_runs(dev), R.m77_runs(ho)
cnt = Counter(x for r in Rd for x in r)
carriers = [c["carrier"] for c in json.load(open(HERE / "results.json"))["planted_control"]["carriers"]]
OUT = {}
for rate in (0.1, 0.2, 0.3, 0.6):
    ps = []
    for c in carriers:
        S = R.slots(Rh, c)[:10]          # keep only the first 10 slots: same n as M109
        keep = set(S)
        R2 = [list(r) for r in Rh]
        # drop the carrier's other tokens so the test sees exactly 10 slots
        for i, j in R.slots(Rh, c)[10:]: R2[i][j] = "X_" + c
        pick = R.g("ph", c, rate).random(len(S)) < rate
        for (i, j), pk in zip(S, pick):
            if pk: R2[i][j + 1] = "M59"
        ps.append(R.matched_null(R2, c, "M59", cnt, 20_000, R.g("phn", c, rate))["p"])
    OUT[str(rate)] = dict(power=float(np.mean(np.array(ps) < 0.05)), median_p=float(np.median(ps)))
json.dump(OUT, open(HERE / "posthoc.json", "w"), indent=1)
print(json.dumps(OUT, indent=1))
