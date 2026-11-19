"""Synthetic fixture test for the frozen HARP loader and scorer (no real data involved).
Run: board/run.sh .venv/bin/python -I experiments/harp_pack/test_loader.py
Writes fixture/harp_fixture.csv and exits non-zero on any failure."""
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from experiments.harp_pack import loader as L  # noqa: E402
from experiments.harp_pack import score as S  # noqa: E402

FIX = Path(__file__).with_name("fixture")
FIX.mkdir(exist_ok=True)
fails = []


def check(cond, msg):
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond:
        fails.append(msg)


# 1. messy headers, units, values -------------------------------------------------------------
rows = [
    # Field No., Lot No., Period/Phase, Obj. Type, Vessel Form, Firing, Technique, Max Length (cm), Wt (g), Rim Dia (mm), CISI No., Signs (Wells), Notes
    ["H90-1234/171-9", "171", "Period 3B", "Pottery sherd", "Large storage jar", "post-firing", "incised", "4.5", "12", "310", "H-1189", "W740 W176", "x"],
    ["H96-2001/45-2", "", "IIIC", "pot sherd", "Dish", "Pre-firing", "painted", "3 cm", "0.02 kg", "", "h 2578", "W820", ""],
    ["H88-0101/12-1", "12", "3B/C", "Incised tablet", "", "", "", "2.1", "4.5", "", "H1438", "M342, M176", ""],
    ["H95-3333/77-4", "77", "Stratum IV", "Seal", "", "", "", "", "", "", "", "W740 # W033", ""],
    ["H99-4444/80-1", "80", "", "sherd", "goblet", "pre or post?", "stamped", "", "", "", "", "?", ""],
    ["H99-4445/80-2", "80", "Period 2", "sherd", "bowl", "", "seal impression", "", "", "", "", "740 400", ""],
]
cols = ["Field No.", "Lot No.", "Period/Phase", "Obj. Type", "Vessel Form", "Firing", "Technique",
        "Max Length (cm)", "Wt (g)", "Rim Dia (mm)", "CISI No.", "Signs (Wells)", "Notes"]
raw = pd.DataFrame(rows, columns=cols)
raw.to_csv(FIX / "harp_fixture.csv", index=False)
df, rep = L.load(FIX / "harp_fixture.csv")
m = rep["mapping"]
check(m.get("field_no") == "Field No." and m.get("lot") == "Lot No." and m.get("period") == "Period/Phase",
      f"id/lot/period headers mapped: {m}")
check(m.get("object_type") == "Obj. Type" and m.get("vessel_form") == "Vessel Form", "type/form headers mapped")
check(m.get("length_mm") == "Max Length (cm)" and m.get("mass_g") == "Wt (g)" and m.get("rim_diam_mm") == "Rim Dia (mm)",
      "dimension headers mapped")
check(m.get("inscription_id") == "CISI No." and m.get("signs") == "Signs (Wells)", "inscription id / signs mapped")
check("Notes" in rep["unmapped_headers"], "unrelated header left unmapped")
check(np.isclose(df.loc[0, "length_mm"], 45.0) and np.isclose(df.loc[1, "length_mm"], 30.0), "cm -> mm (header and cell)")
check(np.isclose(df.loc[1, "mass_g"], 20.0), "kg cell -> g")
check(list(df["object_type"]) == ["POT", "POT", "TAB:I", "SEAL", "POT", "POT"], f"object types {list(df['object_type'])}")
check(list(df["firing_class"]) == ["post", "pre_hand", "NA", "NA", "NA", "pre_stamp"], f"firing classes {list(df['firing_class'])}")
check(list(df["vessel_form"]) == ["storage_jar", "bowl_dish", "NA", "NA", "goblet_beaker", "bowl_dish"], f"forms {list(df['vessel_form'])}")
check(list(df["period"]) == ["3B", "3C", "3B/C", "Vats-IV", "NA", "2"], f"periods {list(df['period'])}")
check(list(df["icit_cisi"])[:3] == ["H-1189", "H-2578", "H-1438"], "CISI ids normalised")
check(df.loc[1, "lot_key"] == "96-45" and df.loc[0, "lot_key"] == "90-171", f"lot keys {list(df['lot_key'])}")
check(df.loc[2, "signs"] == ["W740", L._m2w()["M176"]] == ["W740", "W400"], f"Mahadevan -> Wells via bridge {df.loc[2, 'signs']}")
check(df.loc[3, "signs"] == ["W740", "#", "W033"] and df.loc[3, "readable_n"] == 2, "breaks kept, not counted")
check(df.loc[5, "signs"] is None, "bare numbers without a stated scheme -> no signs")
d2, _ = L.load_frame(raw, sign_scheme="wells")
check(d2.loc[5, "signs"] == ["W740", "W400"], "bare numbers with scheme=wells")

# 2. ambiguity must stop the loader ---------------------------------------------------------
amb = pd.DataFrame({"Weight": [1], "Mass": [2], "Signs": ["W1"]})
try:
    L.load_frame(amb)
    check(False, "two exact mass headers raise AmbiguousColumns")
except L.AmbiguousColumns:
    check(True, "two exact mass headers raise AmbiguousColumns")
d3, r3 = L.load_frame(amb, override_map={"mass_g": "Mass"})
check(r3["mapping"]["mass_g"] == "Mass" and d3.loc[d3.index[0], "mass_g"] == 2, "override map resolves ambiguity")

# 3. end-to-end scorer on synthetic sherds --------------------------------------------------
rng = np.random.default_rng(1)
signs = ["W740", "W033", "W031", "W002", "W400", "W820", "W176", "W090"]
p = np.array([.17, .1, .1, .1, .1, .05, .2, .18])
p /= p.sum()


def synth(n, jar_pre):
    out = []
    for i in range(n):
        pre = rng.random() < 0.3
        sg = list(rng.choice(signs, size=int(rng.integers(1, 4)), p=p))
        if pre and rng.random() > jar_pre:
            sg = [s if s != "W740" else "W033" for s in sg]
        out.append(dict(object_type="POT", signs=sg, readable_n=len(sg),
                        firing_class="pre_hand" if pre else "post", lot_key=f"L{i % 90}",
                        period=["3A", "3B", "3C"][i % 3], vessel_form=["storage_jar", "bowl_dish"][i % 2],
                        rim_diam_mm=float(rng.normal(250, 50)), icit_cisi=None, mass_g=np.nan))
    return pd.DataFrame(out)


S.MIN_N = {}
strong = S.test_C1(synth(900, jar_pre=0.05))
null = S.test_C1(synth(900, jar_pre=1.0))
check(strong["p"] < 1e-4 and strong["RR"] < 0.5, f"C1 detects a planted depletion (RR {strong['RR']:.2f}, p {strong['p']:.1e})")
check(null["p"] > 0.01, f"C1 quiet under no effect (RR {null['RR']:.2f}, p {null['p']:.2f})")
res = S.run_all(synth(600, 0.5), n_perm=99, seals=[["W740"], ["W033", "W740"], ["W176", "W090", "W740"]],
                tabs=S.load_tablets(), icit_pot=(set(), {}))
check(all("verdict" in res[k] for k in res if k not in ("DROPPED",)), f"run_all returns a verdict per test: "
      + ", ".join(f"{k}={res[k]['verdict']}" for k in res if k != "DROPPED"))
a, e, pu, pl = S.strat_hyper([(10, 5, 5, 5)])
check(np.isclose(pu, 1 / 252), "stratified hypergeometric exact tail (1/252)")
print("FAILED:", len(fails)) if fails else print("ALL OK")
sys.exit(1 if fails else 0)
