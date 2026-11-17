"""Pull every CDLI text mentioning Meluhha (and the known Meluhhan names / Gu'abba
Meluhha village) from the local CDLI bulk dump, and record seal status.

Run: .venv/bin/python -I experiments/sealing_hunt/extract.py
Input (untrusted data, read only): experiments/short_labels/raw/cdli/{cdliatf_unblocked.atf,cdli_cat.csv}
Output: experiments/sealing_hunt/meluhha_texts.csv, meluhha_atf.txt
"""
import csv, re, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW = os.path.join(ROOT, "experiments/short_labels/raw/cdli")
OUT = os.path.join(ROOT, "experiments/sealing_hunt")
csv.field_size_limit(sys.maxsize)

# Meluhha spellings (ATF is lower-case ascii with sz etc.)
PAT = re.compile(r"me-lu[h2]?-ha|me-luh|me-lu-ha|me-luh-ha|na-na-sa3|na-na-za|sa6-ma-ar|"
                 r"lu2-mar-za|ur-\{d\}ig-alim dumu me|sak-ku-szi", re.I)

texts = {}
cur = None
buf = []
with open(os.path.join(RAW, "cdliatf_unblocked.atf"), encoding="utf-8", errors="replace") as f:
    for line in f:
        if line.startswith("&P") or line.startswith("&X") or line.startswith("&Q"):
            if cur and buf:
                texts[cur] = "".join(buf)
            cur = line[1:8]
            buf = [line]
        elif cur:
            buf.append(line)
    if cur and buf:
        texts[cur] = "".join(buf)

hits = {}
for pid, t in texts.items():
    body = "\n".join(l for l in t.splitlines() if not l.startswith("#tr") and not l.startswith("&"))
    if PAT.search(body):
        hits[pid] = t
print("texts in dump", len(texts), "hits", len(hits))

cat = {}
want = set(int(p[1:]) for p in hits if p.startswith("P"))
with open(os.path.join(RAW, "cdli_cat.csv"), encoding="utf-8", errors="replace") as f:
    for r in csv.DictReader(f):
        try:
            i = int(r["id_text"])
        except Exception:
            continue
        if i in want:
            cat[i] = r


def seal_info(t):
    lines = t.splitlines()
    sealed = False
    legend = []
    notes = []
    in_seal = False
    for l in lines:
        s = l.strip()
        low = s.lower()
        if low.startswith("@seal") or low.startswith("@object seal"):
            sealed = True; in_seal = True; legend.append("[" + s + "]"); continue
        if s.startswith("@") and not low.startswith("@column"):
            in_seal = False
        if ("seal" in low and (s.startswith("$") or s.startswith("#"))) and not low.startswith("#tr"):
            sealed = True; notes.append(s)
        if in_seal and re.match(r"^\d+'?\.", s):
            legend.append(s.split(".", 1)[1].strip())
    return sealed, " | ".join(legend), " | ".join(notes)


rows = []
for pid, t in sorted(hits.items()):
    r = cat.get(int(pid[1:]), {}) if pid.startswith("P") else {}
    sealed, legend, notes = seal_info(t)
    ctx = [l.split(".", 1)[-1].strip() for l in t.splitlines()
           if PAT.search(l) and not l.startswith("#")][:3]
    rows.append(dict(
        pnum=pid, designation=r.get("designation", ""), period=r.get("period", ""),
        provenience=r.get("provenience", ""), museum_no=r.get("museum_no", ""),
        collection=r.get("collection", ""), date=r.get("date_of_origin", ""),
        genre=r.get("genre", ""), object_type=r.get("object_type", ""),
        sealed=int(sealed), seal_legend=legend, seal_notes=notes,
        seal_id=r.get("seal_id", ""), seal_information=r.get("seal_information", ""),
        photo_up=r.get("photo_up", ""), lineart_up=r.get("lineart_up", ""),
        meluhha_context=" || ".join(ctx)))

with open(os.path.join(OUT, "meluhha_texts.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)
with open(os.path.join(OUT, "meluhha_atf.txt"), "w") as f:
    for pid, t in sorted(hits.items()):
        f.write(t + "\n")
ns = sum(r["sealed"] for r in rows)
print("sealed", ns)
from collections import Counter
print(Counter(r["period"][:20] for r in rows).most_common())
print(Counter(r["provenience"][:25] for r in rows).most_common(15))
print("sealed with photo", sum(1 for r in rows if r["sealed"] and r["photo_up"]))
