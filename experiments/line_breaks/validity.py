"""Is '|' a real wrap? Descriptive checks of M77 line records (no boundary scores at breaks).
Run: .venv/bin/python experiments/line_breaks/validity.py
"""
import json, sys
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from corpus.load import m77_lines, m77_texts, distinct  # noqa

OUT = Path(__file__).parent
lines_by = defaultdict(list)
for l in m77_lines():
    lines_by[(l["text_no"], l["side"])].append(l)

multi = distinct([t for t in m77_texts() if t["n_lines"] > 1])
single = distinct([t for t in m77_texts() if t["n_lines"] == 1 and "#" not in t["seq"]])
standalone = Counter(t["seq"][0] for t in single if len(t["seq"]) == 1)
alltok = Counter(s for t in single for s in t["seq"])
in_text = Counter(s for t in single if len(t["seq"]) > 1 for s in t["seq"])

kinds = Counter(); one_sign_l2 = Counter(); rows = []
for t in multi:
    ls = [l for l in sorted(lines_by[(t["text_no"], t["side"])], key=lambda x: x["line"]) if l["signs"]]
    if len(ls) < 2:
        kinds["one non-empty line only"] += 1; continue
    d = [l["direction"] for l in ls]
    ds = set(d) - {"single sign"}
    if len(ds) > 1:
        kinds["lines run in different directions"] += 1
    elif any(len(l["signs"]) == 1 for l in ls[1:]):
        kinds["a later line is one sign"] += 1
        for l in ls[1:]:
            if len(l["signs"]) == 1:
                one_sign_l2[l["signs"][0]] += 1
    elif len(ls[0]["signs"]) == 1:
        kinds["line 1 is one sign"] += 1
    else:
        kinds["two multi-sign lines, same direction"] += 1

res = dict(n_distinct_multiline=len(multi), layout_kinds=dict(kinds))
top = []
for s, c in one_sign_l2.most_common(12):
    top.append(dict(sign=s, as_one_sign_line2=c, single_line_texts_with_sign=in_text[s],
                    standalone_single_line=standalone[s]))
res["one_sign_second_lines_top"] = top
res["one_sign_line2_signs_rare_in_running_text"] = int(sum(c for s, c in one_sign_l2.items() if in_text[s] < 5))
res["one_sign_line2_total"] = int(sum(one_sign_l2.values()))
json.dump(res, open(OUT / "validity.json", "w"), indent=1)
print(json.dumps(res, indent=1))
