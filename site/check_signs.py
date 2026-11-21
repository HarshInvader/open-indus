#!/usr/bin/env python3
"""Spot-check the sign catalogue against the corpus files. Run after site/build.py, from the repo root:
    .venv/bin/python -I site/check_signs.py [M342 M403 ...]

Recounts each sign straight from data/*.jsonl with the shared loaders in corpus/load.py (a separate code path
from site/build_signs.py) and compares the numbers with site/data/signs.json and with the text of the
built page site/signs/M{n}.html. Exits non-zero on any mismatch."""
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from corpus.load import m77_texts, icit_texts, distinct, runs  # noqa: E402

snap = {s["id"]: s for s in json.loads((ROOT / "site/data/signs.json").read_text())["signs"]}
ids = sys.argv[1:] or ["M342", "M403", "M59", "M60", "M87", "M103", "M109", "M267", "M99"] + \
      random.Random(7).sample(sorted(snap), 8)
m77, icit = m77_texts(), icit_texts()
dm, di = distinct(m77), distinct(icit)
bad = 0


def same(sid, what, got, want):
    global bad
    ok = got == want
    bad += not ok
    print(f"  {'ok ' if ok else 'BAD'} {what}: catalogue {got!r}, recount {want!r}")


for sid in ids:
    s = snap[sid]
    print(sid)
    texts = sum(1 for t in dm if sid in t["seq"])
    tokens = sum(t["seq"].count(sid) for t in m77)
    objects = sum(1 for t in m77 if sid in t["seq"])
    same(sid, "distinct texts", s["texts"], texts)
    same(sid, "uses (all objects)", s["tokens"], tokens)
    same(sid, "objects", s["objects"], objects)
    seals = sum(1 for t in dm if sid in t["seq"] and t["object_type"] == "seal")
    same(sid, "texts on seals", s["by_type"].get("seal", 0), seals)
    harappa = sum(1 for t in dm if sid in t["seq"] and t["site"] == "Harappa")
    same(sid, "texts at Harappa", dict(s["by_site"]).get("Harappa", 0), harappa)
    final = sum(1 for t in dm if "#" not in t["seq"] and len([x for x in t["seq"] if x != "|"]) > 1
                and [x for x in t["seq"] if x != "|"][-1] == sid)
    same(sid, "uses as last sign", s["pos"].get("final", 0), final)
    after = Counter(b for t in dm for r in runs(t["seq"]) for a, b in zip(r, r[1:]) if a == sid)
    if after:
        top = max(after.values())
        same(sid, "count of commonest next sign", s["after"][0][1] if s["after"] else 0, top)
    for w in s["wells"]:
        wt = sum(1 for t in di if w in t["seq"])
        same(sid, f"ICIT distinct texts for {w}", next(x["texts"] for x in s["icit"] if x["w"] == w), wt)
    page = (ROOT / f"site/signs/{sid}.html").read_text()
    m = re.search(r"Appears in ([\d,]+) texts? \(([\d,]+) uses?\)", page)
    same(sid, "page headline (texts, uses)", (int(m.group(1).replace(",", "")), int(m.group(2).replace(",", ""))) if m else None,
         (texts, tokens))

print("all checks passed" if not bad else f"{bad} mismatches")
sys.exit(1 if bad else 0)
