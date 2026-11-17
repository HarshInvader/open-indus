"""Self-recognition: score each real list (and Indus dev) against its OWN fitted generator at its own n.
If a list is rejected by its own generator, cross-system rejections partly reflect generator misfit.
-> selfcheck.json"""
import sys, json
from pathlib import Path
from multiprocessing import Pool
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import gen, stats as S
from identify import PRIMARY
from score import gof
FITS = HERE / "fits"
NAMES = ["indus_dev", "old_english", "old_high_german", "old_norse", "germanic_pooled", "greek", "sanskrit", "egyptian",
         "ur3", "chinese_given", "chinese_full", "plains", "sangam"]
def _job(a):
    nm, r = a
    f = json.loads((FITS / f"{nm}.json").read_text()); th = f["theta"]
    rng = np.random.default_rng(r + 31 * sum(map(ord, nm)))
    ty, c = gen.sample(th, f["n_fit"], rng, V=th["V"])
    st = S.compute(ty, rng, c, 30)
    return nm, [st[k] for k in S.KEYS]
if __name__ == "__main__":
    with Pool(2) as p:
        res = p.map(_job, [(nm, r) for nm in NAMES for r in range(100)], chunksize=4)
    y = np.array([a for a, _ in res]); X = np.array([b for _, b in res], float)
    import identify; identify.SYSTEMS[:] = NAMES   # gof iterates SYSTEMS
    import score; score.SYSTEMS = NAMES
    out = {}
    for nm in NAMES:
        obs = json.loads((FITS / f"{nm}.json").read_text())["target"]
        m = y == nm
        g = score.gof(X[m], y[m], obs, PRIMARY)
        out[nm] = g.get(nm)
        print(f"{nm:16s}", out[nm])
    json.dump(out, open(HERE / "selfcheck.json", "w"), indent=1)
