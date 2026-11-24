"""lb_shape_ladder addendum 1 (docs/prereg/lb_shape_ladder_add1.md): refute-only rungs at 95% and 90% token coverage,
Indus chunks (as R0/R1). Reuses run.py unchanged; no N2 (certify never passes on undivided text).
Run: nice -n 20 .venv/bin/python -I experiments/lb_shape_ladder/coverage.py
"""
import json, random, sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path
import numpy as np
import importlib.util
HERE = Path(__file__).resolve().parent
# run.py does `import run as base` (lb_certify); load it under its own name so that import resolves to lb_certify.
sys.path.insert(0, str(HERE.parents[1] / "experiments/lb_certify"))
_spec = importlib.util.spec_from_file_location("ladder", HERE / "run.py")
L = importlib.util.module_from_spec(_spec); sys.modules["ladder"] = L; _spec.loader.exec_module(L)


def init():
    L.init()

COV = {"R95": 0.95, "R90": 0.90}


def one(args):
    k, rung = args
    cov = COV[rung]
    dev, ho, _ = L.build(k, "chunk")
    rng = random.Random(L.SEED + 1000 * k + 7 * (10 + list(COV).index(rung)))
    freq = Counter(s for t in dev + ho for w in t for s in w)
    order = sorted(freq); rng.shuffle(order)
    tot = sum(freq.values()); kept, c = [], 0
    for s in order:
        if c / tot >= cov: break
        kept.append(s); c += freq[s]
    true = {s: L.base.true_value(s) for s in kept}
    cl = L.classes(kept, true)
    H = L.IC(ho, L.LEX); t_ho = H.full(true)
    n1 = np.array([H.full(L.permute_in_class_bins(true, cl, freq, rng)) for _ in range(L.NPERM)])
    Hs = L.IC(L.unigram(ho, rng), L.LEX); t_sh = Hs.full(true)
    n1s = np.array([Hs.full(L.permute_in_class_bins(true, cl, freq, rng)) for _ in range(L.NPERM)])
    return dict(k=k, rung=rung, cov_actual=c / tot, true_ic=t_ho, n1_p99=float(np.quantile(n1, .99)),
                refute=bool(t_ho > np.quantile(n1, .99)), shuffled_refute=bool(t_sh > np.quantile(n1s, .99)),
                cons_per_seg=H.shape(true)["cons_per_seg"])


if __name__ == "__main__":
    jobs = [(k, r) for r in COV for k in range(1, L.NSUB + 1)]
    with Pool(4, initializer=init) as P:
        res = P.map(one, jobs, chunksize=1)
    summ = {r: dict(refute_n=sum(x["refute"] for x in res if x["rung"] == r),
                    shuffled_refute_n=sum(x["shuffled_refute"] for x in res if x["rung"] == r),
                    passes=sum(x["refute"] for x in res if x["rung"] == r) >= 16 and sum(x["shuffled_refute"] for x in res if x["rung"] == r) <= 1,
                    true_ic_mean=float(np.mean([x["true_ic"] for x in res if x["rung"] == r])),
                    n1_p99_mean=float(np.mean([x["n1_p99"] for x in res if x["rung"] == r]))) for r in COV}
    print(json.dumps(summ, indent=1))
    json.dump(dict(summary=summ, runs=res), open(HERE / "coverage.json", "w"), indent=1)
