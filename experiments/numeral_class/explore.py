"""Exploratory diagnostics (NOT pre-registered; run after fit.py).
1. Flat benchmark: Dirichlet(0.5) prior over the support ("any distribution") vs each class.
2. Local spike at 7 (vs 6 and 8) and the 12-to-(9,10) ratio in every reference and in Indus.
3. Shape without the peaks: class ranking on Indus with values 7 and 12 removed.
4. PPC of the best component for the formula-free Indus counts.
usage: .venv/bin/python experiments/numeral_class/explore.py
"""
import json, math, sys
from pathlib import Path
import numpy as np
from scipy.special import gammaln
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fit as F

refs = json.load(open(HERE / "data/refs.json"))
U = F.m77_units()
o = F.counts(U, F.S_M77)
out = {}

flat = F.ll_dm(o, np.full(len(o), 0.5)) / math.log(10)
_, cls_ll = F.score(o, F.components(refs, F.S_M77), F.S_M77)
out["flat_benchmark"] = dict(flat_log10=flat, classes={c: v / math.log(10) for c, v in cls_ll.items()})
print("flat Dirichlet(0.5) log10 ML", round(flat, 1), "| best class", max(cls_ll, key=cls_ll.get), round(max(cls_ll.values()) / math.log(10), 1))


def spikes(c):
    g = lambda v: math.log(c.get(v, 0) + 0.5)
    return dict(E7=g(7) - (g(6) + g(8)) / 2, r12=(c.get(12, 0) + .5) / ((c.get(10, 0) + c.get(9, 0)) / 2 + .5),
                share7=c.get(7, 0) / max(1, sum(c.get(v, 0) for v in F.S_M77)))
ind = {v: int(n) for v, n in zip(F.S_M77, o)}
nf = {v: int(n) for v, n in zip(F.S_M77, F.counts(F.m77_units("noformula"), F.S_M77))}
out["spikes"] = {"INDUS_M77": spikes(ind), "INDUS_noformula": spikes(nf)}
for k, d in refs.items():
    out["spikes"][k] = spikes({int(a): b for a, b in d["counts"].items()})
print(f"{'source':28s}  E7(log spike)  12/(9,10)")
for k, s in out["spikes"].items():
    print(f"{k:28s}  {s['E7']:+.2f}        {s['r12']:.2f}")

S2 = [1, 3, 4, 5, 6, 8, 9, 10]
o2 = F.counts(U, S2)
rows, cl = F.score(o2, F.components(refs, S2), S2)
sm = F.summarize(cl)
out["no_peaks"] = dict(order=sm["order"], log10_bf=sm["log10_bf_top_vs_second"],
                       best=[(r["name"], r["var"], r["ll"] / math.log(10)) for r in sorted(rows, key=lambda r: -r["ll"])[:4]])
best = max(rows, key=lambda r: r["ll"])
alpha = next((c[4] for c in F.components(refs, S2) if c[1] == best["name"] and c[2] == best["var"]), None)
out["no_peaks"]["ppc"] = F.ppc(o2, best, alpha)
print("without 7 and 12:", sm["order"][:4], "BF", round(sm["log10_bf_top_vs_second"], 2), out["no_peaks"]["best"][:3], out["no_peaks"]["ppc"])

onf = F.counts(F.m77_units("noformula"), F.S_M77)
rows, cl = F.score(onf, F.components(refs, F.S_M77), F.S_M77)
best = max(rows, key=lambda r: r["ll"])
alpha = next((c[4] for c in F.components(refs, F.S_M77) if c[1] == best["name"] and c[2] == best["var"]), None)
out["noformula_ppc"] = dict(component=f"{best['name']}|{best['var']}", **F.ppc(onf, best, alpha),
                            exp=[round(x * onf.sum(), 1) for x in best["p"]], obs=onf.tolist())
print("formula-free PPC:", out["noformula_ppc"])
json.dump(out, open(HERE / "explore.json", "w"), indent=1, default=float)
