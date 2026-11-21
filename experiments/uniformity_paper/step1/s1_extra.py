"""EXPLORATORY (added after scoring; not pre-registered). C8 failed: M77 Harappa has 200 seal texts after
cleaning, below C2's 204 per side. Rerun C2 and C8 at 200 per side so the depth floor has a matched between-city
number. Same code path as s1.run; output draws_extra.jsonl.
  board/run.sh .venv/bin/python -I experiments/uniformity_paper/step1/s1_extra.py
"""
import json
import zlib
from collections import Counter

import numpy as np

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import s1  # noqa: E402

C = {
    "X_C2_m77_MD_DK_deep_vs_shallow_200": ("C", lambda: s1.ub.clean(s1.m77_seals(s1.lab_depth)), "deep", "shallow", 200),
    "X_C8_m77_MD_vs_H_200": ("C", lambda: s1.ub.clean(s1.m77_seals(s1.lab_city)), s1.MD, s1.HA, 200),
}
out = {}
with open(s1.HERE / "draws_extra.jsonl", "w") as f:
    for name, (part, build, a, b, n) in C.items():
        T = build()
        aucs, nuls = [], []
        for k in range(s1.N_DRAWS):
            rng = np.random.default_rng([s1.SEED, k, zlib.crc32(name.encode())])
            smp, short = s1.ub.draw_n(T, a, b, rng, s1.MIX, False, n, 2 * n)
            obs, nul, nf, nn = s1.ub.score(smp, a, s1.SEED + k)
            aucs.append(obs); nuls.append(nul)
            f.write(json.dumps(dict(cond=name, draw=k, auc=obs, null_auc=nul, n_side=n)) + "\n")
        a_ = np.array(aucs); nu = np.array(nuls)
        out[name] = dict(n_side=n, median_auc=float(np.median(a_)), lo=float(np.quantile(a_, 0.025)),
                         hi=float(np.quantile(a_, 0.975)), null_q95=float(np.quantile(nu, 0.95)))
        print(name, out[name], flush=True)
s1.lib.jdump(out, s1.HERE / "results_extra.json")
