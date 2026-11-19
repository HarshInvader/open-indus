"""POST HOC (not pre-registered): leakage tiers for the board #18 bench.

The deposit removed exact repeats under the authors' readings, so the 20 "exact copies" exist only
under our readings. This splits test texts into: exact copy (ours), near copy only, clean.
Reuses bench.py by running it (it rewrites results.json identically; its rng is seeded).
Run: .venv/bin/python -I experiments/bench_restoration/posthoc_tiers.py
"""
import json, runpy
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
g = runpy.run_path(str(HERE / "bench.py"))
ex, leak, M = g["ex"], g["leak"], g["M"]
exact = np.array([leak[r["text_id"]][0] for r in ex])
fam = np.array([leak[r["text_id"]][1] for r in ex])
tiers = {"exact_copy_ours": exact, "near_copy_only": fam & ~exact, "clean": ~fam}
out = {}
for name, m in tiers.items():
    out[name] = {"positions": int(m.sum()), "texts": len({r["text_id"] for r, k in zip(ex, m) if k})}
    out[name].update({mod: round(100 * v[m, 0].mean(), 1) for mod, v in M.items()})
print(json.dumps(out, indent=1))
(HERE / "posthoc_tiers.json").write_text(json.dumps(out, indent=1))
