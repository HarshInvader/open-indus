"""EXPLORATORY (not pre-registered): power of the A5 MD non-FEM replication for a BLOCK-SIZED cluster.

M77 loci are excavation areas, much larger than Mackay's blocks. Plant the FEM house-12 pattern
(4 extra ticked-fish seals among 19 random seals of one locus) and re-run the A5 test.
Run: .venv/bin/python experiments/redteam_fish_block/a5_power_blocksize.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from corpus.load import m77_lines  # noqa: E402

TF = {"M60", "M66", "M68", "M71", "M73"}
rng = np.random.default_rng(7)
L = pd.DataFrame(m77_lines())
L["lev"] = pd.to_numeric(L.level, errors="coerce")
s = L[(L.object_type == "seal") & (L.site == "Mohenjodaro")].groupby("text_no").agg(
    signs=("signs", lambda x: set(y for l in x for y in l)), lev=("lev", "first"), locus=("locus", "first")).reset_index()
s = s[~s.text_no.between(2000, 2999) & s.locus.notna()]
s["tf"] = s.signs.apply(lambda x: bool(x & TF)).astype(float)
cnt = s.locus.astype(str).value_counts()
big = set(cnt[cnt >= 8].index)
u = np.array([x if x in big else "other" for x in s.locus.astype(str)])
lab = pd.factorize(u)[0]
nu = lab.max() + 1
st = pd.factorize(np.floor(s.lev.abs() / 5).fillna(-1))[0]
f0 = s.tf.to_numpy()


def g(f, l):
    n1 = np.bincount(l, weights=f, minlength=nu); n = np.bincount(l, minlength=nu).astype(float)
    p = f.mean(); e1, e0 = n * p, n * (1 - p); n0 = n - n1
    with np.errstate(divide="ignore", invalid="ignore"):
        return 2 * (np.where(n1 > 0, n1 * np.log(n1 / e1), 0).sum() + np.where(n0 > 0, n0 * np.log(n0 / e0), 0).sum())


groups = [np.where(st == k)[0] for k in np.unique(st)]
P = []
for _ in range(1000):
    x = lab.copy()
    for gi in groups:
        x[gi] = lab[gi][rng.permutation(len(gi))]
    P.append(x)
n = np.bincount(lab, minlength=nu)
elig = np.where(n >= 19)[0]
hits = 0
for _ in range(300):
    uu = rng.choice(elig)
    idx = np.where((lab == uu) & (f0 == 0))[0]
    f = f0.copy()
    f[rng.choice(idx, 4, replace=False)] = 1  # 4 extra ticked fish in one locus (house-12/V-like cluster)
    o = g(f, lab)
    nl = np.array([g(f, p) for p in P])
    hits += (1 + (nl >= o - 1e-9).sum()) / 1001 <= 0.05
res = {"power_plus4_in_one_locus": hits / 300, "n": int(len(s)), "n_tf": int(f0.sum())}
print(res)
r = json.load(open(Path(__file__).parent / "results.json"))
r["A5_exploratory_blocksize_power"] = res
json.dump(r, open(Path(__file__).parent / "results.json", "w"), indent=1)
