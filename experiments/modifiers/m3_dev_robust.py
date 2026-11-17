"""Dev: CMH with leave-one-base-out robustness, per modifier and feature (min 1 token each)."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import *  # noqa
P = profiles(m77_corpus("dev"))
pairs = [p for p in load_pairs(HERE / "decomp_frozen.csv") if p[3] in ("high", "medium")]
groups = {m: [p for p in pairs if p[2] == m] for m in sorted({p[2] for p in pairs})}
groups["TICKS4_nonfish"] = [p for p in pairs if p[2] == "TICKS4" and p[4] != "fish"]
groups["TICKS4_fish"] = [p for p in pairs if p[2] == "TICKS4" and p[4] == "fish"]
out = {}
for m, pr in groups.items():
    g = by_base(usable(pr, P, 1))
    if len(g) < 3:
        continue
    out[m] = {f: robust(g, P, f) for f in ("final", "init", "seal")}
    print(m.ljust(15), "  ".join(f"{f}: z={r['z']:+.1f} loo={r['loo_worst_z']:+.1f} {r['up']}up/{r['down']}dn" for f, r in out[m].items()))
json.dump(out, open(HERE / "dev_robust.json", "w"), indent=1)
