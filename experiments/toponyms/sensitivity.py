"""Exploratory follow-ups AFTER the confirmatory run (not pre-registered).
1. ICIT T1 without stroke-numeral candidates (W031, W032 and n-grams containing them).
2. ICIT T1 without Chanhu-daro homes.
3. Full-data travel test (all ICIT; candidates discovered on all ICIT) for maximum power.
4. Small-site-only enrichment (MD and Harappa removed from the data).
5. Chanhu-daro end mark M93 = W031 W032 described.
.venv/bin/python experiments/toponyms/sensitivity.py
"""
import json
from common import *
import confirm as C

C.MODE = "final"
out = {}
res = json.load(open(HERE / "confirm_final.json"))
cands = res["ICIT"]["candidates"]
B = icit_split()["B"]
NUM = {"W031", "W032", "W033", "W034"}

def nonum(c):
    return not (set(c["feature"].split()) & NUM)

for tag, sel in [("no_numerals", [c for c in cands if nonum(c)]),
                 ("no_chanhudaro", [c for c in cands if c["home"] != "Chanhu-daro"]),
                 ("no_numerals_no_chanhudaro", [c for c in cands if nonum(c) and c["home"] != "Chanhu-daro"])]:
    r, _ = C.enrich_replication(B, sel)
    out["T1_" + tag] = {k: v for k, v in r.items() if k != "per_cand"}
    print(tag, out["T1_" + tag])

# 3. full data
U = icit_units()
fc, info = C.discover(U)
T = collapse(U, "travel")
cl = [(c["feature"], c["home"]) for c in fc]
for mob in ("primary", "broad"):
    tr = travel_test(T, cl, MOBILE[mob], R=5000)
    out["fulldata_travel_" + mob] = {k: v for k, v in tr.items() if k != "per_cand"}
    print("full-data travel", mob, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in out["fulldata_travel_" + mob].items()})
out["fulldata_travel_power_primary"] = C.travel_power(T, cl, MOBILE["primary"], alpha=0.05)
print("full-data power (alpha 0.05)", out["fulldata_travel_power_primary"])
out["fulldata_candidates"] = fc
# small sites only for candidates whose home is small; off-home sealing tokens listed
tr = travel_test(T, cl, MOBILE["primary"], R=1)
out["fulldata_offhome_sealings"] = [d for d in tr["per_cand"] if d["mob_off"] > 0]
for d in out["fulldata_offhome_sealings"]:
    print("   ", d["feature"], d["home"], "home", d["n_home"], "off", d["n_off"], "off sealings", d["mob_off"], "exp", d["E_off"])

# 4. small sites only
S = [u for u in U if u["site"] not in C.BIG]
fs, info_s = C.discover(S)
E = collapse(S, "enrich")
feats, X = feature_matrix(E, C.MIN)
sites, obs, exp, p = enrichment(E, X, R=2000)
pp = [p[i, j] for j in range(len(feats)) for i, s in enumerate(sites) if obs[i, j] >= 3 and s not in C.EXCL]
q = bh(pp)
out["small_sites_only"] = dict(n_units=len(E), n_tests=len(pp), n_p01=int(sum(x < 0.01 for x in pp)),
                               expected_p01=0.01 * len(pp), n_q10=int((q < 0.1).sum()),
                               top=[c for c in fs[:10]])
print("small sites only:", {k: v for k, v in out["small_sites_only"].items() if k != "top"})
for c in fs[:10]:
    print("   ", c)

# 5. M93
m93 = [dict(text=r["text_no"], site=r["site"], obj=r["object_type"], seq=" ".join(r["seq"])) for r in m77_texts() if "M93" in r["seq"]]
out["M93"] = m93
jdump(out, HERE / "sensitivity.json")
