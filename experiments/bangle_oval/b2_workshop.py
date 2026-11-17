"""H4 workshop-mark descriptives + H2 slot descriptives on the DISCOVERY bangles (ICIT BNGL).

Descriptive only: these are the data the lead came from. Object-level (every BNGL row,
incl. duplicate texts) and distinct-text level. Series at Mohenjo-daro:
'surface 1983-85' = excavation numbers starting 83-/84-/85- or MD/MN/HR-E/DK-x 83-...;
'old excavations' = Marshall/Mackay DK/HR/SD/VS numbers.
Run: .venv/bin/python experiments/bangle_oval/b2_workshop.py
"""
import json
import re
from pathlib import Path

import pandas as pd
from scipy.stats import fisher_exact

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "experiments/bangle_oval"
OVAL, LENS2 = "W790", "W840"

d = pd.read_csv(ROOT / "sources/field-cady_indus_valley_script_corpus/inscriptions.csv", dtype=str).fillna("")
meta = d.set_index("id")
icit = {json.loads(l)["id"]: json.loads(l) for l in open(ROOT / "data/icit_texts.jsonl")}

rows = []
for i, r in icit.items():
    if r["type"] != "BNGL":
        continue
    ws = [s for s in r["seq"] if s.startswith("W")]
    if not ws:
        continue
    exc = meta.loc[i, "excavation-idno"]
    if r["site"] == "Mohenjo-daro":
        series = "MD surface 1983-85" if re.search(r"(^|\s)8[345]-", exc) else "MD old excavations"
    else:
        series = r["site"]
    rows.append({"id": i, "obj": r["cisi"] if r["cisi"] != "-" else exc, "site": r["site"], "series": series,
                 "material": r["material"], "period": r["period"] + " " + r["phase"], "seq": " ".join(ws),
                 "n": len(ws), "oval": OVAL in ws, "m403": LENS2 in ws,
                 "pos": [("alone" if len(ws) == 1 else "first" if j == 0 else "last" if j == len(ws) - 1 else "mid")
                         for j, s in enumerate(ws) if s == OVAL]})
df = pd.DataFrame(rows)
# object level: one row per object (first text line of that object)
obj = df.groupby("obj").agg(site=("site", "first"), series=("series", "first"), material=("material", "first"),
                            oval=("oval", "max"), m403=("m403", "max")).reset_index()
dist = df.drop_duplicates(["seq", "site"])


def tab(frame, key):
    return {k: [int(g.oval.sum()), int(g.m403.sum()), int(len(g))] for k, g in frame.groupby(key)}


res = {"note": "[oval, m403, n] per group; discovery data, descriptive only"}
for name, frame in (("objects", obj), ("distinct_texts", dist)):
    res[name] = {"by_site": tab(frame, "site"), "by_series": tab(frame, "series"), "by_material": tab(frame, "material")}
    md = frame[frame.site == "Mohenjo-daro"]
    ha = frame[frame.site == "Harappa"]
    a, b = int(md.oval.sum()), int(ha.oval.sum())
    res[name]["fisher_MD_vs_Harappa_oval"] = {"MD": [a, len(md)], "Harappa": [b, len(ha)],
                                              "p_two_sided": fisher_exact([[a, len(md) - a], [b, len(ha) - b]])[1]}
    s = md[md.series == "MD surface 1983-85"]
    o = md[md.series == "MD old excavations"]
    a, b = int(s.oval.sum()), int(o.oval.sum())
    res[name]["fisher_MD_surface_vs_old"] = {"surface": [a, len(s)], "old": [b, len(o)],
                                             "p_two_sided": fisher_exact([[a, len(s) - a], [b, len(o) - b]])[1]}
    a, b = int((frame.oval | frame.m403)[frame.site == "Mohenjo-daro"].sum()), int((frame.oval | frame.m403)[frame.site == "Harappa"].sum())
    res[name]["oval_family_MD_vs_Harappa"] = {"MD": [a, len(md)], "Harappa": [b, len(ha)]}
ov = df[df.oval]
res["oval_rows"] = ov[["id", "obj", "site", "series", "material", "period", "seq", "pos"]].to_dict("records")
pos = [p for ps in dist[dist.oval].pos for p in ps]
res["slot_distinct"] = {p: pos.count(p) for p in set(pos)}
json.dump(res, open(OUT / "workshop.json", "w"), indent=1, default=str)
print(json.dumps({k: v for k, v in res.items() if k != "oval_rows"}, indent=1, default=str))
print(ov[["obj", "site", "series", "material", "period", "seq", "pos"]].to_string())
