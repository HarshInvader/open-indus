"""EXPLORATORY (not pre-registered): the frozen null permutes context labels across units,
so a context recorded in big, find-rich units makes every sign look enriched (Harappa
WEIGHT). Here the statistic is the sign's SHARE of records inside context units minus its
share outside, with the same within-stratum label permutation. Run after test.py.
  .venv/bin/python -I experiments/assemblage/explore_size.py
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.argv = sys.argv[:1]
HERE = Path(__file__).resolve().parent
import importlib.util
spec = importlib.util.spec_from_file_location("t", HERE / "test.py")
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)

rng = np.random.default_rng(t.SEED)
out = {}
for objset in ("all", "nonseal"):
    M = t.site_matrices(objset)
    by = {}
    for x in t.linked:
        if objset == "nonseal" and t.is_seal(x["type"]):
            continue
        by.setdefault(x["site"], {}).setdefault(x["unit"], set()).add(x["seq"])
    rows = []
    for s, m in M.items():
        recs = np.array([len(by[s][u]) for u in m["units"]])
        P = t.perms(m["strata"], 5000, rng)
        freq = m["N"].sum(axis=1)
        ok = np.where(freq >= 5)[0]
        for c in t.CRAFTS:
            cv = np.array([1 if c in t.craft_of.get((s, u), set()) else 0 for u in m["units"]])
            if cv.sum() < 2 or cv.sum() == len(cv):
                continue
            Pc = cv[P]
            Rin = Pc @ recs; Rout = recs.sum() - Rin
            Sin = Pc @ m["N"][ok].T
            Sout = freq[ok][None, :] - Sin
            with np.errstate(divide="ignore", invalid="ignore"):
                dnull = Sin / Rin[:, None] - Sout / np.maximum(Rout, 1)[:, None]
            rin, rout = (cv @ recs), recs.sum() - cv @ recs
            sin = m["N"][ok] @ cv
            d = sin / rin - (freq[ok] - sin) / max(rout, 1)
            p = (1 + (np.nan_to_num(dnull, nan=-9) >= d).sum(axis=0)) / 5001
            for k, i in enumerate(ok):
                rows.append({"site": s, "context": c, "sign_W": m["signs"][i], "sign_M": t.W2M.get(m["signs"][i], ""),
                             "in": f"{int(sin[k])}/{int(rin)}", "out": f"{int(freq[i]-sin[k])}/{int(rout)}", "p": float(p[k])})
    # cross-site: same sign+context p<=0.05 at two sites
    from collections import defaultdict
    d = defaultdict(dict)
    for r in rows:
        d[(r["sign_W"], r["context"])][r["site"]] = r
    both = [v for v in d.values() if sum(1 for r in v.values() if r["p"] <= 0.05) >= 2]
    ntest = sum(1 for v in d.values() if len(v) >= 2)
    print(f"[{objset}] size-conditioned: (sign,context) with >=2 sites: {ntest}; p<=0.05 at >=2 sites: {len(both)} (chance ~{ntest*0.0025:.2f} per pair)")
    for v in both:
        print("   ", list(v.values()))
    out[objset] = {"n_testable": ntest, "both_p05": both}
json.dump(out, open(HERE / "explore_size.json", "w"), indent=1, default=float)
