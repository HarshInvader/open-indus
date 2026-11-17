"""Pre-run power and sample sizes (marginals only: no roofed-sign x context table is computed).
Run before freezing docs/prereg/roof_context.md. Output: power.json."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import *  # noqa

PM, PW = roof_pairs("M"), roof_pairs("W")
sets = {
    "A_icit_sealing": (icit_seal_sealing(), PW),
    "A_m77_sealing_trueSites": (m77_seal_sealing(), PM),
    "B_merged_citadel": (merged_area_units(), PW),
    "B_m77_locus_citadel": (m77_area_units(), PM),
}
out = {}
for name, (U, P) in sets.items():
    T = token_table(U)
    g = usable(P, T)
    ntok = {d: sum(v[0] for v in T[d].values()) for ds in g.values() for d in ds}
    btok = {b: sum(v[0] for v in T[b].values()) for b in g}
    ctx_rate = sum(u["ctx"] for u in U) / len(U)
    rec = {"units": len(U), "ctx_rate_all_units": ctx_rate, "k_bases": len(g), "derived_tokens": ntok, "base_tokens": btok}
    for orr in (2.0, 3.0):
        rec[f"power_OR{orr:g}"] = power(U, P, orr, n_sim=1000)
    out[name] = rec
    print(name, json.dumps({k: v for k, v in rec.items()}, default=float))

# Lothal backs: how many sealings with a diagnostic back carry a roofed sign (no back type looked at)
ft = json.load(open(ROOT / "sources/paragorth_Indus-/data/derived/lothal-sealings-frenez-tosi2005.json"))["rows"]
back = {r[0]: r[2] for r in ft if r[2] != "undiagnostic"}
roofW = {d for ds in PW.values() for d in ds}
n_roof = len({t["cisi"] for t in icit_texts() if t["site"] == "Lothal" and t["cisi"] in back and roofW & set(t["seq"])})
out["A2_lothal_backs"] = {"sealings_with_diag_back": len(back), "with_roofed_sign": n_roof}
print("Lothal sealings with diagnostic back:", len(back), "with a roofed sign:", n_roof)
json.dump(out, open(HERE / "power.json", "w"), indent=1, default=float)
