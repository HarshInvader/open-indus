"""Exploratory checks on DEV only (used to write the prereg; not confirmatory).
 a) T2 feature effects under extra controls: + emblem class, + multiplicity (text on >1 seal), + phase (subset)
 b) composite: frame-feature count on unicorn vs other-animal seals, within site x length strata
"""
import sys, math, json
from collections import Counter
import numpy as np
sys.path.insert(0, __import__("os").path.dirname(__file__))
from common import seal_table, strata, resid_by_strata, FRAME, HERE
from t2_status import perm_within

rows = [r for r in seal_table("dev") if r["log_area"] is not None]
y = np.array([r["log_area"] for r in rows])
def emc(e): return "unicorn" if e == "unicorn" else ("none" if e in ("none", "unknown") else "rare")
base = strata(rows)
variants = {
    "base": base,
    "+emblem": [s + (emc(r["emblem"]),) for s, r in zip(base, rows)],
    "+multi": [s + (r["n_obj"] > 1,) for s, r in zip(base, rows)],
    "+emblem+multi": [s + (emc(r["emblem"]), r["n_obj"] > 1) for s, r in zip(base, rows)],
}
rng = np.random.default_rng(0)
out = {}
for f in ["TB_W590", "PC_W400", "TB_W70x", "CL_W405", "CL_W390", "MJ_W741"]:
    x = np.array([f in r["feats"] for r in rows])
    out[f] = {}
    for vn, st in variants.items():
        res = np.array(resid_by_strata(list(y), st))
        d = res[x].mean() - res[~x].mean()
        nd = np.array([res[p][x].mean() - res[p][~x].mean() for p in (perm_within(st, rng) for _ in range(2000))])
        out[f][vn] = (round(100 * (math.exp(d) - 1), 1), round(float((1 + (np.abs(nd) >= abs(d)).sum()) / 2001), 4))
    # phase subset
    sub = [i for i, r in enumerate(rows) if r["phase"] not in ("-", "")]
    st = [base[i] + (rows[i]["phase"],) for i in sub]
    res = np.array(resid_by_strata(list(y[sub]), st)); xs = x[sub]
    if xs.sum() >= 5:
        d = res[xs].mean() - res[~xs].mean()
        nd = np.array([res[p][xs].mean() - res[p][~xs].mean() for p in (perm_within(st, rng) for _ in range(2000))])
        out[f]["phase_subset"] = (int(xs.sum()), round(100 * (math.exp(d) - 1), 1), round(float((1 + (np.abs(nd) >= abs(d)).sum()) / 2001), 4))
    print(f, out[f])

# b) composite frame count, unicorn vs other animal
R = [r for r in seal_table("dev") if r["emblem"] not in ("unknown", "none", "other")]
st = strata(R)
cnt = np.array([len(r["feats"]) for r in R], float)
u = np.array([r["emblem"] == "unicorn" for r in R])
res = np.array(resid_by_strata(list(cnt), st))
d = res[~u].mean() - res[u].mean()
nd = []
for _ in range(4000):
    p = perm_within(st, rng); nd.append(res[~u[p]].mean() - res[u[p]].mean())
nd = np.array(nd)
print("frame count, other-animal minus unicorn (residual within strata):", d, "raw means", cnt[~u].mean(), cnt[u].mean(),
      "n", (~u).sum(), u.sum(), "p", (1 + (np.abs(nd) >= abs(d)).sum()) / 4001, "mde", 2.8 * nd.std())
# per animal
for a in ["gaur", "zebu", "elephant", "rhino", "tiger", "buffalo", "shorthorn", "goat"]:
    m = np.array([r["emblem"] == a for r in R])
    print(a, m.sum(), round(res[m].mean(), 3))
# also any-frame presence
anyf = np.array([len(r["feats"]) > 0 for r in R], float)
print("any frame: unicorn", anyf[u].mean(), "other", anyf[~u].mean())
