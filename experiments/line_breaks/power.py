"""Step 1b: power gate. Synthetic breaks only; the observed break positions are NOT read.
Planted: with probability f a text's break is moved to a true boundary, else drawn from the
uniform null. 'True boundary' = (A) the position with the highest ESR, (B) a random slot-rule
boundary position. Detection = one-sided p < 0.05 for the pre-registered statistic.
Run: .venv/bin/python experiments/line_breaks/power.py
"""
import json, sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lb_lib as L

OUT = Path(__file__).parent
rng = np.random.default_rng(20261114)
model, ntrain = L.fit_model()
texts = L.usable_m77()
for t in texts:
    t.pop("k")  # never touch observed breaks here
tabs_all = L.text_tables(model, texts)


def plant(tabs, f, mode):
    ks = []
    for tb in tabs:
        m = tb["n"] - 1
        if rng.random() < f:
            if mode == "A":
                best = np.flatnonzero(tb["rank"] == tb["rank"].max())
                ks.append(int(rng.choice(best)) + 1); continue
            cand = np.flatnonzero(tb["slot"] == 1)
            if len(cand):
                ks.append(int(rng.choice(cand)) + 1); continue
        ks.append(int(rng.integers(1, m + 1)))
    return ks


def null_quantile(tabs, nsim=2000):
    sims = np.array([L.stat(tabs, L.null_draw(tabs, rng)) for _ in range(nsim)])
    return float(np.quantile(sims, 0.95))


res = dict(n_train_single_line_dev=ntrain, n_usable_m77=len(texts),
           slot_boundary_share_of_positions=float(np.mean(np.concatenate([tb["slot"] for tb in tabs_all]))),
           power={})
for n in [len(texts), 113, 150, 300, 500]:
    for f in [0.2, 0.3]:
        for mode in ["A", "B"]:
            hits = 0; reps = 300
            for _ in range(reps):
                idx = rng.integers(0, len(tabs_all), n) if n != len(texts) else np.arange(n)
                tabs = [tabs_all[i] for i in idx]
                crit = null_quantile(tabs, 400)
                hits += L.stat(tabs, plant(tabs, f, mode)) > crit
            res["power"][f"n{n}_f{f}_{mode}"] = hits / reps
            print(n, f, mode, hits / reps, flush=True)

# false-positive check at f = 0
fp = 0
for _ in range(300):
    crit = null_quantile(tabs_all, 400)
    fp += L.stat(tabs_all, plant(tabs_all, 0.0, "A")) > crit
res["false_positive_rate_f0"] = fp / 300
res["gate"] = dict(n_required=150, power_required=0.8,
                   n_pass=len(texts) >= 150,
                   power_pass=res["power"][f"n{len(texts)}_f0.2_A"] >= 0.8)
res["gate"]["pass"] = res["gate"]["n_pass"] and res["gate"]["power_pass"]
json.dump(res, open(OUT / "power.json", "w"), indent=1)
print(json.dumps(res, indent=1))
