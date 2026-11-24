"""MUK19-stroked-jar-MET: are the stroked-jar signs (M343/M344/M345, agreed by two blind mappers) enriched >= 2x on
pottery? Prereg addendum 1 of docs/prereg/signmap_figfish_strokedjar.md. Machinery from experiments/self_label/s2_test.py.
Run: .venv/bin/python -I experiments/signmap/strokedjar_test.py
"""
import json, sys
from pathlib import Path
import numpy as np
from scipy.stats import poisson
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments/self_label"))
import s2_test as T  # noqa: E402

SJ = {"M343", "M344", "M345"}
texts = T.icit_set()
for t in texts:
    if t["signs"] & SJ: t["signs"] = t["signs"] | {"SJ"}
signs = ["SJ", "M343", "M344", "M345"]
r = T.perm_test(texts, signs, ["pottery graffito"])["pottery graffito"]
out = {}
for j, s in enumerate(signs):
    mu = float(r["mu"][j]); obs = int(r["obs"][j])
    out[s] = dict(obs=obs, exp=round(mu, 2), ratio=round(obs / mu, 3) if mu else None, p_enrich=float(r["p"][j]), present=int(r["present"][j]))
mu = out["SJ"]["exp"]; q99 = poisson.ppf(0.99, mu)
power_2x = float(1 - poisson.cdf(q99 - 1, 2 * mu))
sj = out["SJ"]
verdict = ("survives: enriched >= 2x on pottery" if sj["ratio"] >= 2 and sj["p_enrich"] <= 0.01 else
           "refuted: ratio <= 1 on pottery (kill condition), test powered for 2x" if sj["ratio"] <= 1 and power_2x >= 0.8 else
           "inconclusive")
res = dict(primary="ICIT pottery graffito, pooled SJ = text has any of M343/M344/M345, within-site label permutation, 10,000 draws",
           n_pottery_texts=r["n_cls"], signs=out, power_2x=round(power_2x, 3), verdict=verdict,
           note="M343 alone was already seen in self_label (6 vs 15.67); M344/M345 on pottery graffiti were not.")
print(json.dumps(res, indent=1)); json.dump(res, open(HERE / "strokedjar_result.json", "w"), indent=1)
