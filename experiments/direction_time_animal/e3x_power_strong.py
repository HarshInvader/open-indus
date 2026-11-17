"""EXPLORATORY (after the frozen run): power of E3 for a strong plant (q=0.5, f=1.0: half of opener types fully
confined to a home period, swaps permitting). The frozen grid (f<=0.5) barely moved opener drift (see RESULTS)."""
import json, numpy as np
import e3_time as E

units, _ = E.load()
out = {}
for q, f in [(0.5, 1.0)]:
    hits, S = 0, []
    for _ in range(30):
        Dp = E.Data(E.plant(units, q, f))
        dr, _ = E.drift(Dp, Dp.per, nperm=30)
        B = E.bootstrap(Dp, Dp.per, 200, 30)
        hits += np.mean(B[:, 0] <= 0) < 0.05
        S.append(E.stats(dr)["S_oc"])
    out[f"q{q}_f{f}"] = dict(power=hits / 30, mean_S_oc=float(np.mean(S)), n_plants=30)
    print(out, flush=True)
json.dump(out, open(E.OUT / "e3x_power_strong.json", "w"), indent=1)
