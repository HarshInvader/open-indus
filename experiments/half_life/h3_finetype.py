"""Exploratory: is P3 (HAR ~ HAR_VATS chronology agreement) carried by object SUB-type change over time?
Re-run with fine object types (ICIT full type code; M77 raw object_type) as the permutation/residual strata."""
import h1_main as H
from hl_lib import *
H.rng = np.random.default_rng(11)
D = build_icit(); V = build_m77_depth("Harappa")
# fine types
fine = {}
seen = set()
for t in icit_texts():
    if t["site"] != "Harappa": continue
    p = icit_period(t)
    if p is None: continue
    seq = tuple(W2M.get(x, x) if x not in ("|", "#") else x for x in t["seq"])
    fine.setdefault((p, seq), t["type"].split(":")[0] + ":" + (t["type"].split(":")[1] if ":" in t["type"] else ""))
for u in D["HAR"]: u["ot_coarse"] = u["ot"]; u["ot"] = fine.get((u["period"], u["seq"]), u["ot"])
print("HAR fine types x period", sorted(Counter((u["ot"], u["period"]) for u in D["HAR"]).items()))
L = m77_lines(); raw = {}
for r in L:
    if r["site"] == "Harappa": raw[tuple(r["signs"])] = r["object_type"]
for u in V:
    first = tuple(H.runs(list(u["seq"]))[0]) if H.runs(list(u["seq"])) else ()
    u["ot"] = {"miniature tablet": "mtab", "sealing": "mould", "seal": "seal"}.get(raw.get(first, u["ot"]), u["ot"])
print("VATS fine types x period", sorted(Counter((u["ot"], u["period"]) for u in V).items()))
res = H.p3({"HAR": D["HAR"], "HAR_VATS": V}, [("HAR", "HAR_VATS")], nperm=2000)
print("P3 HAR~HAR_VATS with fine-type strata:", res)
json.dump(res, open(OUT / "results_finetype.json", "w"), indent=1, default=float)
