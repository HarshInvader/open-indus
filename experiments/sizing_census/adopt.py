"""Applies the frozen R1/R2 rules of docs/prereg/sizing_census.md to kill.json -> adoption.json.
Written after the kill run (calc.py has no adoption step). It encodes only the prereg's sealed values and rules:
- "counted cells" are the cells counted in the SEALED run (the prereg's table), not calc.py's own feasibility flag;
- R1: sealed <= 0.5 or >= 0.9 -> prediction on the same side of 0.8; R2: sealed in [0.05, 0.95] -> |error| <= 0.20.
"""
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
K = json.load(open(HERE / "kill.json"))

SEALED = {  # prereg table, counted cells only (tablet delta 0.238 is grey and excluded)
    "case3": [0.03, 0.03], "case4a": [0.20, 0.73, 1.00, 1.00], "case4b": [0.18, 0.60, 0.95, 1.00, 1.00],
    "case4c": [0.10, 0.30, 0.68, 1.00, 1.00], "case5a": [1.00, 1.00, 0.99, 0.99, 0.84],
    "case5b": [1.00, 0.99, 0.89, 0.82, 0.39]}
FAM = {"A1": ["case1x", "case3", "case4a", "case4b", "case4c"], "A2": ["case5a"], "A3": ["case5b"], "B": ["case1"]}
FAM["A1"].remove("case1x")


def check(case):
    pred = [c["power"] for c in K[case]["cells"]][:len(SEALED[case])]
    cells = []
    for s, p in zip(SEALED[case], pred):
        r1 = None if 0.5 < s < 0.9 else ((s >= 0.8) == (p >= 0.8))
        r2 = None if not (0.05 <= s <= 0.95) else abs(p - s) <= 0.20
        cells.append(dict(sealed=s, predicted=round(p, 3), error=round(p - s, 3), R1=r1, R2=r2,
                          below_sealed_by_more_than_0_10=p < s - 0.10))
    ok = all(c["R1"] is not False and c["R2"] is not False for c in cells)
    return dict(cells=cells, reproduced=ok)


out = {c: check(c) for c in SEALED}
c1 = K["case1"]
r1 = (c1["dev_gate_met"] is True) and (c1["held_gate_met"] is False)
r2 = abs(c1["held_median_ari"] - 0.56) <= 0.20 and abs(c1["held_field_recovery"]["person"] - 0.65) <= 0.20
out["case1"] = dict(dev_gate_predicted=c1["dev_gate_met"], held_gate_predicted=c1["held_gate_met"],
                    held_ari=round(c1["held_median_ari"], 3), person=c1["held_field_recovery"]["person"],
                    R1=r1, R2=r2, reproduced=bool(r1 and r2))
out["adopted"] = {f: all(out[c]["reproduced"] for c in cs) for f, cs in FAM.items()}
json.dump(out, open(HERE / "adoption.json", "w"), indent=1)
for k, v in out.items():
    print(k, v if k == "adopted" else v["reproduced"])
