"""Baselines from the DISCOVERY data (ICIT) for the bangle-oval prereg.

Counts, on distinct ICIT texts: share carrying W790 (oval, = M373/M374) and W840 (= M403)
by object class and site. Also the workshop-mark descriptives on the 41 ICIT bangle texts
(site, area, period, excavation series). Nothing here touches the new sample.
Run: .venv/bin/python experiments/bangle_oval/b0_baselines.py
"""
import json
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "experiments/bangle_oval"
OVAL, LENS2 = "W790", "W840"

d = pd.read_csv(ROOT / "sources/field-cady_indus_valley_script_corpus/inscriptions.csv", dtype=str).fillna("")
icit = [json.loads(l) for l in open(ROOT / "data/icit_texts.jsonl")]
meta = d.set_index("id")


def distinct(rows):
    seen, out = set(), []
    for r in rows:
        ws = [s for s in r["seq"] if s.startswith("W")]
        if not ws:
            continue
        k = (" ".join(r["seq"]), r["type"] == "BNGL", r["site"])
        if k in seen:
            continue
        seen.add(k)
        out.append(r)
    return out


D = distinct(icit)
res = {"n_distinct_icit": len(D)}

# non-bangle baseline by site (all lengths, and 1-3 sign texts)
by = defaultdict(lambda: [0, 0, 0, 0, 0, 0])  # oval, n, oval_short, n_short, lens2, lens2_short
for r in D:
    if r["type"] == "BNGL":
        continue
    ws = [s for s in r["seq"] if s.startswith("W")]
    for key in (r["site"], "ALL"):
        b = by[key]
        b[0] += OVAL in ws
        b[1] += 1
        b[4] += LENS2 in ws
        if len(ws) <= 3:
            b[2] += OVAL in ws
            b[3] += 1
            b[5] += LENS2 in ws
res["nonbangle_baseline"] = {
    k: {"oval": v[0], "n": v[1], "share": round(v[0] / v[1], 4), "oval_short": v[2], "n_short": v[3],
        "share_short": round(v[2] / max(v[3], 1), 4), "m403": v[4], "m403_short": v[5]}
    for k, v in by.items() if k in ("ALL", "Mohenjo-daro", "Harappa", "Kalibangan", "Lothal", "Dholavira",
                                    "Chanhu-daro", "Bala-kot", "Nausharo", "Rakhigarhi", "Banawali")}

# discovery bangles: workshop descriptives
B = [r for r in D if r["type"] == "BNGL"]
rows = []
for r in B:
    m = meta.loc[r["id"]]
    ws = [s for s in r["seq"] if s.startswith("W")]
    rows.append({"id": r["id"], "cisi": r["cisi"], "site": r["site"], "material": r["material"],
                 "area": m["area-section"], "exc": m["excavation-idno"], "period": r["period"], "phase": r["phase"],
                 "n_signs": len(ws), "oval": OVAL in ws, "m403": LENS2 in ws,
                 "oval_alone": ws == [OVAL], "oval_pos": [i for i, s in enumerate(ws) if s == OVAL]})
res["discovery_bangles"] = rows
res["discovery_summary"] = {
    "n": len(B), "oval": sum(x["oval"] for x in rows), "m403": sum(x["m403"] for x in rows),
    "oval_or_m403": sum(x["oval"] or x["m403"] for x in rows),
    "by_site": {s: [sum(x["oval"] for x in rows if x["site"] == s), sum(1 for x in rows if x["site"] == s)]
                for s in sorted({x["site"] for x in rows})},
    "by_material": {s: [sum(x["oval"] for x in rows if x["material"] == s), sum(1 for x in rows if x["material"] == s)]
                    for s in sorted({x["material"] for x in rows})},
}
json.dump(res, open(OUT / "baselines.json", "w"), indent=1, default=str)
print(json.dumps(res["nonbangle_baseline"], indent=1))
print(json.dumps(res["discovery_summary"], indent=1))
