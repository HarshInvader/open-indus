"""Scan the whole CDLI dump for tablets whose ATF notes a STAMP (non-cylinder) seal impression,
or an uninscribed/illegible/pictorial impression, and list those from the 3rd and early 2nd
millennium (Old Akkadian .. Old Babylonian). Gulf/Dilmun stamp impressions on cuneiform tablets
would show up here if CDLI transliterators noted them.
Run: .venv/bin/python -I experiments/sealing_hunt/stamp_scan.py
"""
import csv, os, re, sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW = os.path.join(ROOT, "experiments/short_labels/raw/cdli")
OUT = os.path.join(ROOT, "experiments/sealing_hunt")
csv.field_size_limit(sys.maxsize)

STAMP = re.compile(r"stamp|round seal|square seal|button seal|dilmun seal|gulf seal|indus", re.I)
UNINS = re.compile(r"uninscribed seal|illegible seal|anepigraph|no legend|figurative|pictorial seal", re.I)
cur = None
hits = {}
for line in open(os.path.join(RAW, "cdliatf_unblocked.atf"), encoding="utf-8", errors="replace"):
    if line[:2] in ("&P", "&X"):
        cur = line[1:8]
        continue
    s = line.strip()
    if not s or s.startswith("#tr") or s[0] not in "#$@":
        continue
    if STAMP.search(s):
        hits.setdefault(cur, set()).add("STAMP: " + s[:120])
    elif UNINS.search(s):
        hits.setdefault(cur, set()).add("UNINS: " + s[:120])

want = {int(p[1:]) for p in hits if p and p[0] == "P"}
cat = {}
for r in csv.DictReader(open(os.path.join(RAW, "cdli_cat.csv"), encoding="utf-8", errors="replace")):
    try:
        i = int(r["id_text"])
    except Exception:
        continue
    if i in want:
        cat[i] = r

EARLY = ("Old Akkadian", "Ur III", "Lagash II", "Old Babylonian", "Early Old Babylonian", "Ebla", "ED III")
rows = []
for p, notes in hits.items():
    r = cat.get(int(p[1:]), {})
    rows.append(dict(pnum=p, designation=r.get("designation", ""), period=r.get("period", ""),
                     provenience=r.get("provenience", ""), museum_no=r.get("museum_no", ""),
                     photo_up=r.get("photo_up", ""), kind="STAMP" if any(n.startswith("STAMP") for n in notes) else "UNINS",
                     notes=" || ".join(sorted(notes))))
rows.sort(key=lambda x: (x["kind"], x["period"], x["provenience"]))
with open(os.path.join(OUT, "stamp_scan.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print("texts with stamp/uninscribed notes:", len(rows))
print(Counter((r["kind"], r["period"][:22]) for r in rows).most_common(30))
for r in rows:
    if r["kind"] == "STAMP" and r["period"].startswith(EARLY):
        print(r["pnum"], r["designation"][:30], r["period"][:15], r["provenience"][:25], r["museum_no"], "ph" if r["photo_up"] else "", "|", r["notes"][:150])
