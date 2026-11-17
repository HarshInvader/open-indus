"""Dev: stratified token-level (CMH) shift per modifier + power for +0.2 / +0.5 final shifts."""
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
    if len(g) < 1:
        continue
    r = {f: cmh(g, P, f) for f in ("final", "init")}
    r["bases"] = len(g); r["tokens_derived"] = sum(P[d]["n"] for ds in g.values() for d in ds)
    r["power_final_+0.2"] = power_sim(g, P, 0.2, n_sim=500); r["power_final_+0.5"] = power_sim(g, P, 0.5, n_sim=500)
    out[m] = r
    print(f"{m:16s} bases={len(g):2d} ntok_d={r['tokens_derived']:4d} final OR={r['final']['or']:.2f} z={r['final']['z']:+.2f} p={r['final']['p']:.2g} | init z={r['init']['z']:+.2f} p={r['init']['p']:.2g} | power +0.2={r['power_final_+0.2']:.2f} +0.5={r['power_final_+0.5']:.2f}")
json.dump(out, open(HERE / "dev_cmh.json", "w"), indent=1)
