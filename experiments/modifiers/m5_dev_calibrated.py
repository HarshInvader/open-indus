"""Dev: calibrated robust test per modifier (final, init, seal) + negative control of the calibrated test."""
import json, sys, zlib
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import *  # noqa

NF = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
P = profiles(m77_corpus("dev"))
pairs = [p for p in load_pairs(HERE / "decomp_frozen.csv") if p[3] in ("high", "medium")]
groups = {m: [p for p in pairs if p[2] == m] for m in sorted({p[2] for p in pairs})}
groups["TICKS4_nonfish"] = [p for p in pairs if p[2] == "TICKS4" and p[4] != "fish"]
groups["TICKS4_fish"] = [p for p in pairs if p[2] == "TICKS4" and p[4] == "fish"]
groups["INSERT_nocontainer"] = [p for p in pairs if p[2] == "INSERT" and p[4] not in ("jar", "cup")]
groups["INSERT_container"] = [p for p in pairs if p[2] == "INSERT" and p[4] in ("jar", "cup")]
out = {"families": {}}
main_mods = sorted({p[2] for p in pairs})
for m, pr in groups.items():
    g = by_base(usable(pr, P, 1))
    if len(g) < 3:
        out["families"][m] = {"tested": False, "k": len(g)}
        continue
    out["families"][m] = {"tested": True, "k": len(g),
                          **{f: calibrated_test(g, P, f, n_fake=NF, seed=zlib.crc32((m + f).encode())) for f in ("final", "init", "seal")}}
    r = out["families"][m]
    print(m.ljust(19), f"k={len(g):2d}", "  ".join(f"{f}: z={r[f]['z']:+.1f} T={r[f]['T']:+.1f} {r[f]['up']}up/{r[f]['down']}dn p={r[f]['p_two']:.3f}" for f in ("final", "init", "seal")))
ps, keys = [], []
for m in main_mods:
    if out["families"][m]["tested"]:
        for f in ("final", "init", "seal"):
            ps.append(out["families"][m][f]["p_two"]); keys.append((m, f))
q = bh(ps)
out["bh"] = [{"modifier": m, "feature": f, "p": p, "q": float(x)} for (m, f), p, x in zip(keys, ps, q)]
out["n_tests"] = len(ps)
print("tests", len(ps), "q<0.1:", [(m, f, round(p, 4), round(x, 3)) for (m, f), p, x in zip(keys, ps, q) if x < 0.1])

# negative control for the calibrated test: fake modifier classes (random pairings, k=6, rarity-matched)
rng = np.random.default_rng(5)
pool = freq_pool(P, 1); big = [s for s in pool if P[s]["n"] >= 5]
fp = {"final": 0, "init": 0}; NC = 100
for i in range(NC):
    bases = list(rng.choice(big, 6, replace=False)); g = {}
    for b in bases:
        c = [s for s in pool if 0.05 * P[b]["n"] <= P[s]["n"] <= 0.5 * P[b]["n"] and s not in bases] or pool
        g[b] = [c[rng.integers(len(c))]]
    for f in fp:
        fp[f] += calibrated_test(g, P, f, n_fake=300, seed=i)["p_two"] < 0.05
out["negative_control_calibrated"] = {"n": NC, "k": 6, "fpr_p<0.05": {f: v / NC for f, v in fp.items()}}
print("negative control (calibrated test):", out["negative_control_calibrated"])
json.dump(out, open(HERE / "dev_calibrated.json", "w"), indent=1, default=float)
