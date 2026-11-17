"""Exploratory follow-ups (run AFTER the frozen r1 primary run; not pre-registered).
E1 carriers of the leading signals (M112 at MD, M162/M293/M389 at Harappa): texts, depths, families.
E2 length trend combined over sites (Stouffer).
E3 M162 at Harappa: with vs without its count-frame context; seals vs other types.
"""
import sys, json
import numpy as np
from scipy.stats import norm
sys.path.insert(0, __import__("os").path.dirname(__file__))
from rlib import datasets, Perm, trend_stat, two_sided_p, HERE

DS = datasets("primary")
out = {}
for ds, sign in (("MD_FEM", "M112"), ("HAR_EH", "M162"), ("HAR_EH", "M293"), ("HAR_EH", "M389"), ("MD_FEM", "M162")):
    us = DS[ds]
    car = [u for u in us if sign in u["signs"]]
    out[f"{ds}_{sign}"] = [dict(rel=round(u["rel"], 2), area=u["area"], type=u["type"], text=" ".join(u["signs"]),
                                members=u["n_members"]) for u in sorted(car, key=lambda u: u["rel"])]
    print(ds, sign, len(car))
    for c in out[f"{ds}_{sign}"]:
        print("   ", c)

# E2 length Stouffer (from frozen r1 results)
r1 = json.load(open(HERE / "r1_primary.json"))
zs = [t["z"] for t in r1["T1c_classes"] if t["cls"] == "LENGTH"]
zc = sum(zs) / np.sqrt(len(zs))
out["E2_length_stouffer"] = dict(z_sites=zs, z=float(zc), p_two_sided=float(2 * norm.sf(abs(zc))))
print("E2", out["E2_length_stouffer"])

# E3 M162 at Harappa: units with M162 followed by/preceded by numeral? report contexts and type split
us = DS["HAR_EH"]
P = Perm(us, seed=7)
NULL = P.perms(10000)
for lab, fn in (("M162_seal", lambda u: "M162" in u["signs"] and u["type"] == "seal"),
                ("M162_nonseal", lambda u: "M162" in u["signs"] and u["type"] != "seal"),
                ("M162_final", lambda u: u["signs"] and u["signs"][-1] == "M162")):
    x = np.array([[1.0 if fn(u) else 0.0] for u in us])
    if x.sum() >= 3:
        o = trend_stat(x, P.cent); nl = trend_stat(x, NULL)
        out[f"E3_{lab}"] = dict(n=int(x.sum()), shift=float(o[0]), p=float(two_sided_p(o, nl)[0]))
        print("E3", lab, out[f"E3_{lab}"])
json.dump(out, open(HERE / "r2_explore.json", "w"), indent=1)
