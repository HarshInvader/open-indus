"""Descriptive: how often do real names contain a numeral element, and is numeral+X a recurring formula?
Share of name types with a numeral element; share of those where the numeral is name-initial; top numeral+X
formulas (pair recurring in >= 2 types). Indus comparison: share of distinct dev texts with a stroke numeral
directly before a name-core sign (frame-level, not inside cores). -> numerals.json"""
import sys, json, re
from pathlib import Path
from collections import Counter
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import names as N
NUM = {
 "sanskrit": {"eka", "dvi", "tri", "catur", "paYca", "zaz", "zaq", "sapta", "azwa", "nava", "daSa", "Sata", "sahasra", "dvAdaSa", "paYcaSiKa"},
 "chinese_given": set("一二三四五六七八九十百千万"),
 "chinese_full": set("一二三四五六七八九十百千万"),
 "plains": {"one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "hundred", "twin"},
 "old_english": {"an", "twa", "thri", "feower", "fif", "siex", "seofon"},
 "greek": {"τρι", "τετρα", "πεντε", "δεκα", "ἑκατον", "εκατον", "χιλιο", "πολυ"},
 "mixtec": {f"num{i}" for i in range(1, 14)},
 "sangam": {"oru", "iru", "mu", "nal", "aim", "ezhu", "pattu", "nooru", "muthu_x"},
}
out = {}
for nm, num in NUM.items():
    t, _ = N.load(nm)
    has = [x for x in t if any(e in num for e in x)]
    ini = [x for x in has if x[0] in num]
    form = Counter((x[i], x[i + 1]) for x in t for i in range(len(x) - 1) if x[i] in num)
    rec = [(a + "+" + b, c) for (a, b), c in form.most_common(5) if c >= 2]
    out[nm] = dict(types=len(t), share_with_numeral=round(len(has) / len(t), 4), share_numeral_initial=round(len(ini) / max(1, len(has)), 3),
                   recurring_formulas=rec, examples=[" ".join(x) for x in has[:6]])
    print(nm, out[nm])
json.dump(out, open(HERE / "numerals.json", "w"), indent=1, ensure_ascii=False)
