"""Final analyses (descriptive / exploratory, after the gates):
1. Supervised separability scale: calibrated logistic regression held-out bits/text for known genres,
   planted labels and real Indus labels (puts every corpus on one scale).
2. Round-seal check on ICIT forced-K=4 genres (exploratory: no model passed S1).
3. Marker signs of M77 HMM forced-K=4 genres (exploratory).
Usage: board/run.sh .venv/bin/python -I experiments/genres_scratch/final.py
"""
import json
import math
import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import gs  # noqa: E402
import data  # noqa: E402
import run_plant  # noqa: E402

OUT = HERE / "out"
res = {}


def lr_gain(tr, te, yd, yh):
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.linear_model import LogisticRegressionCV
    cv = CountVectorizer(analyzer=lambda u: gs.LDA.doc(u) + [f"^{u['runs'][0][0][0]}", f"{u['runs'][-1][0][-1]}$",
                                                           f"len{min(len(u['signs']), 7)}"], min_df=2)
    Xd = cv.fit_transform(tr); Xh = cv.transform(te)
    m = LogisticRegressionCV(Cs=[0.01, 0.03, 0.1, 0.3, 1, 3], cv=3, max_iter=2000, n_jobs=1).fit(Xd, yd)
    P = m.predict_proba(Xh); cls = list(m.classes_)
    base = Counter(yd); L = len(set(yd) | set(yh))
    g = [math.log2(max(P[i, cls.index(y)], 1e-6)) - math.log2((base[y] + .5) / (len(yd) + .5 * L))
         for i, y in enumerate(yh)]
    return float(np.mean(g))


# 1. supervised scale
scale = {}
for c in ("cun", "lat"):
    tr, te, _ = data.known(c)
    scale[f"{c}_genre"] = lr_gain(tr, te, [u["genre"] for u in tr], [u["genre"] for u in te])
dev, ho = data.m77()
for lab in ("obj", "site"):
    scale[f"m77_{lab}"] = lr_gain(dev, ho, [u[lab] for u in dev], [u[lab] for u in ho])
tri, tei = data.icit()
sd = [u for u in tri if u["shape"]]; sh = [u for u in tei if u["shape"]]
scale["icit_shape"] = lr_gain(sd, sh, [u["shape"] for u in sd], [u["shape"] for u in sh])
scale["icit_reg"] = lr_gain(tri, tei, [u["reg"] for u in tri], [u["reg"] for u in tei])
for f in (0.15, 0.3, 0.5):
    vals = []
    for rep in range(2):
        tr, te = run_plant.plant(f, rep)
        vals.append(lr_gain(tr, te, [u["fake"] for u in tr], [u["fake"] for u in te]))
    scale[f"plant_f{f}"] = float(np.mean(vals))
res["supervised_bits_per_text"] = scale
print(scale, flush=True)

# 2. round seals in ICIT forced-K4 genres
rnd = {}
units = tri + tei
for name in ("HMM", "LCA", "BG"):
    r = json.load(open(OUT / f"main_icit_{name}.json"))
    g = np.array(r["explore_assign_train"] + r["explore_assign_test"])
    reg = np.array([u["reg"] for u in units])
    iR = np.where(reg == "seal_round")[0]; iS = np.where(reg == "seal_sq")[0]
    pS = (np.bincount(g[iS], minlength=4) + .5) / (len(iS) + 2)

    def stat(idx):
        c = np.bincount(g[idx], minlength=4)
        q = (c + .5) / (c.sum() + 2)
        return float((c * np.log(q / pS)).sum())
    obs = stat(iR)
    rng = np.random.default_rng(7)
    null = np.array([stat(rng.choice(iS, len(iR), replace=False)) for _ in range(5000)])
    foreign = [i for i in iR if units[i]["foreign"]]
    rnd[name] = dict(n_round=int(len(iR)), n_foreign_round=len(foreign), obs=obs,
                     p=float((1 + (null >= obs).sum()) / 5001),
                     round_genres=np.bincount(g[iR], minlength=4).tolist(),
                     square_share=np.round(pS, 3).tolist())
res["round_seals_K4"] = rnd
print(rnd, flush=True)

# 3. markers of M77 HMM forced-K4 genres
r = json.load(open(OUT / "main_m77_HMM.json"))
g = np.array(r["explore_assign_train"])
desc = {}
tot = Counter(x for u in dev for x in u["signs"])
N = sum(tot.values())
for k in range(4):
    us = [u for u, z in zip(dev, g) if z == k]
    c = Counter(x for u in us for x in u["signs"]); n = sum(c.values())
    lo = {s: math.log((c[s] + .5) / (n + .5 * len(tot))) - math.log((tot[s] - c[s] + .5) / (N - n + .5 * len(tot)))
          for s in tot if c[s] >= 5}
    desc[k] = dict(n=len(us), mean_len=float(np.mean([len(u["signs"]) for u in us])),
                   markers=[s for s, _ in sorted(lo.items(), key=lambda x: -x[1])[:6]],
                   first=Counter(u["runs"][0][0][0] for u in us if u["runs"][0][1]).most_common(3),
                   last=Counter(u["runs"][-1][0][-1] for u in us if u["runs"][-1][2]).most_common(3),
                   obj=Counter(u["obj"] for u in us).most_common(4))
res["m77_HMM_K4_genres"] = desc
print(json.dumps(desc, indent=1), flush=True)
json.dump(res, open(OUT / "final.json", "w"), indent=1)
