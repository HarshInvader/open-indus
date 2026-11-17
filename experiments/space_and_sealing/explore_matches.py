"""Exploratory (post hoc, not pre-registered): list the sealing texts that match a seal text,
at the same site or elsewhere. Run after t6_sealing.py."""
import sys
from collections import defaultdict
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from sas_lib import icit_texts, nsigns, signs

seals = defaultdict(set)
for t in icit_texts():
    if t["type"].startswith("SEAL") and t["complete"] and "#" not in t["seq"] and signs(t["seq"]):
        seals[tuple(nsigns(t["seq"]))].add((t["site"], t["cisi"]))
seen = set()
for t in icit_texts():
    if not t["type"].startswith("TAG") or not t["complete"] or "#" in t["seq"] or not signs(t["seq"]):
        continue
    k = (t["site"], tuple(nsigns(t["seq"])))
    if k in seen:
        continue
    seen.add(k)
    m = seals.get(k[1])
    if m:
        same = sorted(c for s, c in m if s == t["site"])
        other = sorted(f"{s}:{c}" for s, c in m if s != t["site"])
        print(f"{t['site']:14s} {t['cisi']:10s} len {len(k[1])}  {' '.join(k[1]):40s} same-site seals {same[:4]} other {other[:4]}")
