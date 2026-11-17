"""Dev-only model selection: 5-fold family-grouped CV within dev (M77 v2 dev).
Chooses K (number of fine classes) and alpha for the class grammar; compares with KN bigram,
position-only and unigram baselines. Never touches held-out."""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from glib import *  # noqa

dev = m77_units("dev")
folds = family_folds(dev, k=5, seed=0)
print("dev units", len(dev), "full", sum(u["full"] for u in dev), "families", len(set(families(dev))))

Ks = [int(x) for x in sys.argv[1:]] or [6, 8, 12, 16, 20, 25, 30, 40]
alphas = [float(x) for x in __import__("os").environ.get("ALPHAS", "0.3,1,3").split(",")]
res = {}


def cv(make):
    lp = n = 0
    for f in range(5):
        tr = [u for u, g in zip(dev, folds) if g != f]
        te = [u for u, g in zip(dev, folds) if g == f]
        m = make().fit(tr)
        b, k, _ = bits(m, te)
        lp += b * k; n += k
    return lp / n


t0 = time.time()
for name, mk in [("unigram", lambda: Unigram()), ("position", lambda: PositionModel()),
                 ("kn_bigram", lambda: KNBigram())]:
    res[name] = cv(mk); print(f"{name:12s} {res[name]:.3f} bits/event", flush=True)
import os
disc = float(os.environ["DISC"]) if os.environ.get("DISC") else None
for K in Ks:
    for a in alphas:
        r = cv(lambda: ClassBigram(K, alpha=a, disc=disc))
        res[f"class_K{K}_a{a}"] = r
        print(f"class K={K:3d} alpha={a}: {r:.3f}  ({time.time()-t0:.0f}s)", flush=True)
json.dump(res, open(HERE / f"dev_cv_{'_'.join(map(str, Ks))}.json", "w"), indent=1)
