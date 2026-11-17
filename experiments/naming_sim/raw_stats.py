"""Descriptive: the 9 statistics on the REAL lists (no generator), 100 subsamples of n = min(800, #types)
distinct types, mean and 2.5-97.5%. Inventory is each system's own (not matched to Indus).
Usage: .venv/bin/python -I experiments/naming_sim/raw_stats.py  -> raw_stats.json"""
import sys, json
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import stats as S, names as N
out = {}
for nm in N.SYSTEMS:
    t, c = N.load(nm)
    n = min(800, len(t))
    rows = S.bootstrap(t, n, 100 if len(t) > n else 1, np.random.default_rng(3), c)
    s = S.summarise(rows); s["_n"] = n; s["_types"] = len(t)
    s["_len_dist"] = {L: sum(1 for x in t if min(len(x), 4) == L) / len(t) for L in (1, 2, 3, 4)}
    out[nm] = s
    print(f"{nm:16s} n={n:4d} " + " ".join(f"{k}={s[k]['mean'] if s[k] else None}" for k in S.KEYS), flush=True)
json.dump(out, open(HERE / "raw_stats.json", "w"), indent=1)
