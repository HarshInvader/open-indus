"""Confirmatory run for docs/prereg/roof_context.md. Do not edit after hashing.

A  sealing vs seal (ICIT primary; M77 Lothal/Kalibangan/other-site sealings replicate)
A2 Lothal door/storeroom backs (untestable if < 3 roofed sealings with a diagnostic back)
B  citadel vs lower town (merged ICIT area-section primary; M77 locus replicate); sensitivity: Harappa F as non-domestic
C  position: C1 text-initial shift (modifiers statistic, data already seen -> descriptive);
   C2 order of roofed form vs its own base inside one text (new); C3 leave-roof-fish-out
"""
import json
import sys
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import *  # noqa
from scipy.stats import binomtest, fisher_exact

import importlib.util
_spec = importlib.util.spec_from_file_location("modcommon", ROOT / "experiments/modifiers/common.py")
MC = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(MC)

PM, PW = roof_pairs("M"), roof_pairs("W")
ALPHA = 0.025  # Bonferroni over the two primary context tests (A, B)
R = {"pairs_M": PM, "pairs_W": PW}


def drop_fish(P, which):
    fish_base = "M59" if which == "M" else "W220"
    fish_ticked = "M60" if which == "M" else "W226"
    return {b: d for b, d in P.items() if b not in (fish_base, fish_ticked)}


def both(U, P, tag):
    a = label_perm_test(U, P, n=5000, seed=zlib.crc32(tag.encode()))
    f = fake_modifier_test(U, P, n=2000, seed=zlib.crc32((tag + "f").encode()))
    a["p_fake_up"] = f["p_fake_up"]
    a["p_max"] = max(a["p_perm_up"], a["p_fake_up"])
    return a


# ---- A ----
UA_i, UA_m = icit_seal_sealing(), m77_seal_sealing()
R["A_icit"] = both(UA_i, PW, "A_icit")
R["A_m77"] = both(UA_m, PM, "A_m77")
R["A_icit_noFish"] = both(UA_i, drop_fish(PW, "W"), "A_icit_nf")
R["A_pass"] = bool(R["A_icit"]["p_max"] < ALPHA and R["A_m77"]["z"] > 0)

# ---- A2 ----
ft = json.load(open(ROOT / "sources/paragorth_Indus-/data/derived/lothal-sealings-frenez-tosi2005.json"))["rows"]
back = {r[0]: r[2] for r in ft if r[2] != "undiagnostic"}
DOOR = {"structures", "pegs-on-wall", "lockers"}
roofW = {d for ds in PW.values() for d in ds}
lot = {}
for t in icit_texts():
    if t["site"] == "Lothal" and t["cisi"] in back:
        lot.setdefault(t["cisi"], False)
        lot[t["cisi"]] |= bool(roofW & set(t["seq"]))
nroof = sum(lot.values())
if nroof >= 3:
    tab = [[sum(1 for c, r in lot.items() if r and back[c] in DOOR), sum(1 for c, r in lot.items() if r and back[c] not in DOOR)],
           [sum(1 for c, r in lot.items() if not r and back[c] in DOOR), sum(1 for c, r in lot.items() if not r and back[c] not in DOOR)]]
    R["A2_lothal"] = {"table": tab, "p_up": float(fisher_exact(tab, alternative="greater")[1]), "verdict": "tested"}
else:
    R["A2_lothal"] = {"n_roofed_sealings": int(nroof), "verdict": "untestable (<3 roofed sealings with diagnostic back)"}

# ---- B ----
UB_i, UB_m, UB_iF = merged_area_units(), m77_area_units(), merged_area_units(f_as_nondomestic=True)
R["B_merged"] = both(UB_i, PW, "B_merged")
R["B_m77"] = both(UB_m, PM, "B_m77")
R["B_merged_Fnondomestic"] = both(UB_iF, PW, "B_mF")
R["B_merged_noFish"] = both(UB_i, drop_fish(PW, "W"), "B_merged_nf")
R["B_pass"] = bool(R["B_merged"]["p_max"] < ALPHA and R["B_m77"]["z"] > 0)
R["context_supported"] = R["A_pass"] or R["B_pass"]

# ---- C ----
def c1(corpus, P, tag):
    Pr = MC.profiles(corpus)
    g = {b: [d for d in ds if Pr[d]["n"] >= 1] for b, ds in P.items() if Pr[b]["n"] >= 1}
    g = {b: ds for b, ds in g.items() if ds}
    r = MC.calibrated_test(g, Pr, "init", n_fake=2000, seed=zlib.crc32(tag.encode()))
    r["init_shares"] = {f"{d}<-{b}": [Pr[d]["init"], Pr[d]["n"], Pr[b]["init"], Pr[b]["n"]] for b, ds in g.items() for d in ds}
    return r


M_all = MC.m77_corpus("all")
I_all = MC.icit_corpus()
R["C1_m77_all"] = c1(M_all, PM, "C1m")
R["C1_icit_all"] = c1(I_all, PW, "C1i")
R["C1_m77_all_noFish"] = c1(M_all, drop_fish(PM, "M"), "C1mnf")
R["C1_icit_all_noFish"] = c1(I_all, drop_fish(PW, "W"), "C1inf")
R["position_supported"] = bool(R["C1_m77_all"]["p_up"] < 0.05 and R["C1_icit_all"]["p_up"] < 0.05)


def c2(corpus, P):
    first = second = 0
    ex = []
    for seq, *_ in corpus:
        for b, ds in P.items():
            for d in ds:
                if d in seq and b in seq:
                    i, j = seq.index(d), seq.index(b)
                    first += i < j; second += i > j
                    if len(ex) < 12:
                        ex.append(" ".join(seq))
    n = first + second
    return {"roofed_first": first, "base_first": second, "n": n,
            "p_two": float(binomtest(first, n, 0.5).pvalue) if n else None,
            "verdict": "untestable (n<5)" if n < 5 else "tested", "examples": ex}


R["C2_m77_all"] = c2(M_all, PM)
R["C2_icit_all"] = c2(I_all, PW)

if R["context_supported"] and R["position_supported"]:
    v = "house of X supported (context + position)"
elif R["position_supported"]:
    v = "opener variant (position only; context not supported)"
elif R["context_supported"]:
    v = "context only (no position effect on all data)"
else:
    v = "neither"
R["verdict"] = v
for k in ("A_icit", "A_m77", "A_icit_noFish", "B_merged", "B_m77", "B_merged_Fnondomestic", "B_merged_noFish"):
    x = R[k]
    print(f"{k}: k={x['k']} z={x['z']:+.2f} OR={x['or']:.2f} obs/exp={x.get('obs',0):.1f}/{x.get('exp',0):.1f} up/down={x['up']}/{x['down']} p_perm={x['p_perm_up']:.4f} p_fake={x['p_fake_up']:.4f}")
for k in ("C1_m77_all", "C1_icit_all", "C1_m77_all_noFish", "C1_icit_all_noFish"):
    x = R[k]
    print(f"{k}: k={x['k']} T={x['T']:+.2f} z={x['z']:+.2f} up/down={x['up']}/{x['down']} p_up={x['p_up']:.4f}")
print("A2:", R["A2_lothal"])
print("C2:", {k: R[k] for k in ("C2_m77_all", "C2_icit_all")})
print("A_pass", R["A_pass"], "B_pass", R["B_pass"], "position", R["position_supported"])
print("VERDICT:", v)
json.dump(R, open(HERE / "r1_results.json", "w"), indent=1, default=float)
