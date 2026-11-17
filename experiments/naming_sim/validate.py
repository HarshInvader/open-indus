"""Leave-one-tradition-out validation (run before Indus scoring): would the pipeline recognise a real list?

For a target real list T: every OTHER system's fitted structure is simulated with T's own frequency profile
(V, zipf from fits/T.json) at T's fitting size, exactly as Indus is scored with the Indus profile. T's real
statistics (fits/T.json target) are then scored with score.gof / score.abc. Success = a related system
(same family, T itself and pooled lists containing T excluded) ranks first by ABC posterior and fits (p >= 0.05).
Targets and their relatives:
  old_english -> {old_norse, old_high_german}; old_high_german -> {old_english, old_norse};
  old_norse -> {old_english, old_high_german}; chinese_full -> {chinese_given}; chinese_given -> {chinese_full}
  sanskrit -> {} (no relative; reports which system it lands on); sangam -> {sanskrit} (South Asian)
Usage: .venv/bin/python -I experiments/naming_sim/validate.py -> validate.json
"""
import sys, json
from pathlib import Path
from multiprocessing import Pool
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import gen, stats as S
from identify import SYSTEMS, PRIMARY
from score import gof, abc

FITS = HERE / "fits"
TARGETS = {"old_english": ["old_norse", "old_high_german"], "old_high_german": ["old_english", "old_norse"],
           "old_norse": ["old_english", "old_high_german"], "chinese_full": ["chinese_given"],
           "chinese_given": ["chinese_full"], "sanskrit": [], "sangam": ["sanskrit"], "greek": [], "ur3": []}
R = 100


def _job(a):
    src, prof, n, r = a
    th = dict(json.loads((FITS / f"{src}.json").read_text())["theta"])
    p = json.loads((FITS / f"{prof}.json").read_text())["theta"]
    th["V"], th["zipf"] = p["V"], p["zipf"]
    rng = np.random.default_rng(r * 7919 + sum(map(ord, src + prof)))
    ty, c = gen.sample(th, n, rng, V=th["V"])
    st = S.compute(ty, rng, c, 30)
    return src, [st[k] for k in S.KEYS]


if __name__ == "__main__":
    out = {}
    for T, rel in TARGETS.items():
        fT = json.loads((FITS / f"{T}.json").read_text())
        n = fT["n_fit"]
        srcs = [s for s in SYSTEMS if s != T and not (s == "germanic_pooled" and T in ("old_english", "old_norse", "old_high_german"))]
        with Pool(2) as p:
            res = p.map(_job, [(s, T, n, r) for s in srcs for r in range(R)], chunksize=4)
        y = np.array([a for a, _ in res]); X = np.array([b for _, b in res], float)
        obs = fT["target"]
        g = gof(X, y, obs, PRIMARY)
        a = abc(X, y, obs, PRIMARY)
        top = next(iter(a["posterior"]), None)
        best_gof = max(g, key=lambda s: g[s]["p"])
        out[T] = dict(relatives=rel, abc=a["posterior"], top=top, top_is_relative=top in rel, best_gof=best_gof,
                      gof={s: (v["D2"], round(v["p"], 3)) for s, v in g.items()},
                      relative_fits=[s for s in rel if s in g and g[s]["p"] >= 0.05],
                      n_fit_005=int(sum(v["p"] >= 0.05 for v in g.values())))
        print(f"{T:16s} n={n} ABC top {top} (relative: {top in rel}) post {dict(list(a['posterior'].items())[:3])}; "
              f"best GOF {best_gof} p={g[best_gof]['p']:.3f}; systems fitting p>=.05: {out[T]['n_fit_005']}; "
              f"relatives fitting {out[T]['relative_fits']}", flush=True)
    json.dump(out, open(HERE / "validate.json", "w"), indent=1)
