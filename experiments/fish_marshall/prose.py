"""Findspots from MIC prose (pre-registered route (b)): sentences in MIC vols. I-II that cite a field number
together with Section/Block/House/Room. A field number takes the locative phrase of its own sentence
(nearest preceding Block/House within the sentence, else the nearest following one). Conflicting
findspots for one field number -> dropped.
Output: prose_findspots.csv (key, area, section, block, house, room, n_mentions, conflict, source, snippet)
Run: .venv/bin/python -I experiments/fish_marshall/prose.py
"""
import re
from collections import defaultdict
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TEXTS = [
    HERE / "raw/mohenjodaroandtheinduscivilizationvol1jmarshalled1931_84_N/djvu.txt",
    HERE / "raw/in.ernet.dli.2015.69817/djvu.txt",
    ROOT / "experiments/old_registers/raw/in.ernet.dli.2015.107493/ocr.txt",
    ROOT / "experiments/old_registers/raw/in.ernet.dli.2015.96024/ocr.txt",
]
FN = re.compile(r"\b(HR|VS|DK|SD|L|C|E|D|B)\.?\s?(\d{1,4}[ab]?)\b")
BLOCK = re.compile(r"Block\s*(\d{1,2}|[ivxIl]{1,3}\b)", re.I)
SECT = re.compile(r"Se[cf]t[il1]on\s*([A-E])\b|Se[cCfF]+[tT]?[il1]?on\s*([A-E])\b")
HOUSE = re.compile(r"House\s*([IVXL]{1,7})\b")
ROOM = re.compile(r"(?:Room|Chamber|Court)\s*(\d{1,3})")
AREA = re.compile(r"\b(HR|VS|DK|SD|L)\s*Area", re.I)


def fix_num(s):
    return s.replace("i", "1").replace("I", "1").replace("l", "1")


def sentences(t):
    t = re.sub(r"-\n(?=\w)", "", t)
    t = re.sub(r"\s+", " ", t)
    return re.split(r"(?<=[.;])\s+(?=[A-Z(])", t)


rows = defaultdict(list)
for path in TEXTS:
    if not path.exists():
        continue
    txt = path.read_text(encoding="utf-8", errors="replace")
    for s in sentences(txt):
        if not FN.search(s) or not (BLOCK.search(s) or HOUSE.search(s)):
            continue
        for m in FN.finditer(s):
            # skip things like 'Room 5' captured as codes; require parentheses or 'No.' context nearby
            pre = s[max(0, m.start() - 12):m.start()]
            if not ("(" in pre or "No" in pre or s[m.start() - 1:m.start()] == "("):
                continue
            key = f"{m.group(1)} {m.group(2)}"
            after = s[m.end():]
            before = s[:m.start()]

            def find(rx, txt, last):
                ms = list(rx.finditer(txt))
                return (ms[-1] if last else ms[0]) if ms else None
            loc = {}
            for name, rx in (("block", BLOCK), ("house", HOUSE), ("room", ROOM), ("section", SECT), ("area", AREA)):
                mm = find(rx, after[:220], False) or find(rx, before[-220:], True)
                if mm:
                    val = next(g for g in mm.groups() if g)
                    loc[name] = fix_num(val) if name == "block" else val.upper() if name in ("area", "section") else val
            if "block" in loc or "house" in loc:
                rows[key].append(dict(loc, source=path.parent.name, snippet=s[max(0, m.start() - 100):m.end() + 160]))

out = []
for key, lst in rows.items():
    sig = {(r.get("area"), r.get("section"), r.get("block"), r.get("house")) for r in lst}
    blocks = {(r.get("area"), r.get("section"), r.get("block")) for r in lst if r.get("block")}
    r0 = lst[0]
    out.append(dict(key=key, area=r0.get("area"), section=r0.get("section"), block=r0.get("block"),
                    house=r0.get("house"), room=r0.get("room"), n_mentions=len(lst),
                    conflict=len({b[2] for b in blocks}) > 1, source=r0["source"], snippet=r0["snippet"]))
df = pd.DataFrame(out).sort_values("key")
df.to_csv(HERE / "prose_findspots.csv", index=False)
print(len(df), "field numbers with a prose findspot;", int(df.block.notna().sum()), "with block;",
      int(df.conflict.sum()), "conflicting")
