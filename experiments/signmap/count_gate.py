"""Count gate for the stroked-jar signs agreed by both blind mappers (prereg docs/prereg/signmap_figfish_strokedjar.md).
Counts distinct ICIT texts (all sites, all object types) containing any agreed sign, bridged to Mahadevan numbers.
No object-type breakdown is read here (that is the outcome of the separate prereg, run only if n >= 30).
Run: .venv/bin/python -I experiments/signmap/count_gate.py
"""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "experiments/grammar"))
import glib  # noqa: E402

m1 = {x["item"]: x for x in json.load(open(HERE / "mapper_1.json"))}
m2 = {x["item"]: x for x in json.load(open(HERE / "mapper_2.json"))}
items = [f"img{i}" for i in range(1, 9)] + ["fig"]
agree = {i: m1[i]["candidates"][0] for i in items if m1[i]["candidates"] and m2[i]["candidates"] and m1[i]["candidates"][0] == m2[i]["candidates"][0]}
usable = {i: s for i, s in agree.items() if m1[i]["confidence"] in ("high", "medium") and m2[i]["confidence"] in ("high", "medium")}
claimed = [usable[i] for i in ("img1", "img2", "img3") if i in usable]
res = dict(agreement_rate=f"{len(agree)}/{len(items)}", agreed=agree, usable=usable, fig_usable="fig" in usable,
           stroked_jar_signs=sorted(set(claimed)))
if len(set(claimed)) >= 2:
    texts = set()
    for u in glib.icit_units():
        b = glib.bridge_unit(u)
        if any(s in set(claimed) for s in b["signs"]):
            texts.add(tuple(b["signs"]))
    res["icit_distinct_texts"] = len(texts); res["gate_30"] = len(texts) >= 30
print(json.dumps(res, indent=1)); json.dump(res, open(HERE / "result.json", "w"), indent=1)
