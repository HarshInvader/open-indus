"""Educated-guess rehearsal on proto-cuneiform (known answers hidden).

Builds three blind packets (A picture only, B context only, C picture + context) and a sealed key.
Truth classes come from experiments/protocuneiform/pc_classes.py (written 2026-11-15 from PC scholarship,
before this study). Run: .venv/bin/python -I experiments/guess_rehearsal/build.py
"""
import json, random, re, shutil, sys, hashlib
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PCD = ROOT / "experiments/protocuneiform"
sys.path.insert(0, str(PCD))
from pc_classes import pc_class, base  # noqa

rng = random.Random(20261120)
NUM = re.compile(r"^(\d+)\((N\d+[^)]*)\)$")
L = json.load(open(PCD / "pc_lines.json"))
IMG = PCD / "raw/pc_cdli/archsigns"

def simple(t):
    return t != "," and not NUM.match(t) and not t.startswith("|") and "x" not in t and "&" not in t

freq = Counter(t for l in L for t in l["tokens"] if simple(t))
# candidates: simple signs with a known class, an image, and >= 30 line occurrences
cand = defaultdict(list)
for s, n in freq.most_common():
    c = pc_class(s)
    if c != "UNKNOWN" and n >= 30 and (IMG / f"{s}.jpg").exists():
        if all(base(x) != base(s) for x in cand[c]):  # one variant per base sign
            cand[c].append(s)
targets = []
for c, ss in sorted(cand.items()):
    targets += ss[:6]  # up to 6 most frequent per class
rng.shuffle(targets)

# anonymous ids for every non-numeral token in the corpus (targets get T01.., others X###)
others = sorted({t for l in L for t in l["tokens"] if t != "," and not NUM.match(t)} - set(targets))
rng.shuffle(others)
aid = {s: f"T{i+1:02d}" for i, s in enumerate(targets)}
aid.update({s: f"X{i+1:04d}" for i, s in enumerate(others)})

def render(tokens):
    out = []
    for t in tokens:
        if t == ",":
            continue
        m = NUM.match(t)
        out.append(f"#{m.group(1)}" if m else aid[t])
    return " ".join(out) if out else None

# group lines by tablet to give whole-tablet context
by_tab = defaultdict(list)
for l in L:
    by_tab[l["pid"]].append(l)
contexts = {}
for s in targets:
    tabs = sorted({l["pid"] for l in L if s in l["tokens"]})
    rng.shuffle(tabs)
    ex = []
    for p in tabs[:12]:
        lines = [render(l["tokens"]) for l in by_tab[p]]
        ex.append(" / ".join(x for x in lines if x))
    contexts[aid[s]] = {"n_lines": freq[s], "n_tablets": len(tabs), "examples": ex}

CLASSES = ["GRAIN_FOOD", "LIQUID_DAIRY", "VESSEL", "TEXTILE", "LIVESTOCK", "OTHER_GOODS", "OFFICE_PERSON", "PLACE_INST"]
GENERAL = ("Writing system of an early Bronze Age urban society. Texts are short, on small clay objects, "
           "and many contain numbers. Each sign below has an anonymous id. In context lines, '#n' is a number "
           "(n units of some numeral sign; the unit type is hidden), ' / ' separates lines of one object, "
           "and other signs have anonymous ids (T## = also a target, X#### = not a target).")
CLASS_DOC = {
    "GRAIN_FOOD": "grain, cereal products, bread, rations",
    "LIQUID_DAIRY": "beer, milk, oil, dairy and other liquids",
    "VESSEL": "vessels and containers, incl. measuring vessels",
    "TEXTILE": "cloth, wool, flax, fibre",
    "LIVESTOCK": "animals: sheep, goats, cattle, fish, birds and so on",
    "OTHER_GOODS": "metals, aromatics, wood, reed, plants, salt, fruit, other goods",
    "OFFICE_PERSON": "officials, titles, professions, persons, worker categories, kin terms",
    "PLACE_INST": "places, cities, institutions, buildings, deities, fields, waterways",
}

out = HERE / "packets"
if out.exists():
    shutil.rmtree(out)
for cond in "ABC":
    d = out / cond
    d.mkdir(parents=True)
    task = {"condition": cond, "general": GENERAL, "classes": CLASS_DOC, "targets": sorted(aid[s] for s in targets)}
    if cond in "AC":
        (d / "images").mkdir()
        for s in targets:
            shutil.copy(IMG / f"{s}.jpg", d / "images" / f"{aid[s]}.jpg")
    if cond in "BC":
        task["contexts"] = contexts
    json.dump(task, open(d / "task.json", "w"), indent=1)

sealed = HERE / "sealed"
sealed.mkdir(exist_ok=True)
key = {aid[s]: {"sign": s, "class": pc_class(s)} for s in targets}
json.dump(key, open(sealed / "key.json", "w"), indent=1)
print("targets", len(targets), Counter(pc_class(s) for s in targets))
print("key sha256", hashlib.sha256(open(sealed / "key.json", "rb").read()).hexdigest())
