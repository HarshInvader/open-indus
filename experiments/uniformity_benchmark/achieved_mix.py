"""Descriptive: the length mix actually achieved in draw 0 of each pair/variant (same rng as run.py). No scoring.
    .venv/bin/python -I experiments/uniformity_benchmark/achieved_mix.py"""
import json, numpy as np
from collections import Counter
import run as R
mix, _ = R.indus_mix()
out = {"indus_mean_len": sum(b * p for b, p in mix.items())}
for pair, (pool, a, b, *_r) in R.PAIRS.items():
    P, _ = R.pools(pair)
    for v in ("whole", "frame_removed"):
        rng = np.random.default_rng([R.SEED, 0, sum(map(ord, pair)), len(v), len("balanced")])
        smp, short = R.draw_n(P[v], a, b, rng, mix, pool == "pc", None, R.N_TOTAL)
        L = [min(sum(len(l) for l in t["lines"]), 9) for t in smp]
        c = Counter(L)
        out[f"{pair}|{v}"] = dict(mean_len=float(np.mean(L)), share_by_bin={k: round(c[k] / len(L), 3) for k in R.BINS}, filled=short)
        print(pair, v, round(np.mean(L), 2), out[f"{pair}|{v}"]["share_by_bin"], short)
print("indus mean", round(out["indus_mean_len"], 2), {k: round(x, 3) for k, x in mix.items()})
json.dump(out, open(R.HERE / "achieved_mix.json", "w"), indent=1)
