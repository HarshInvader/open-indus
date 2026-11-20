"""Parse Jamison 2017 Appendix 7.1 (500 seals) and 9.1 (seal groups) and join them to ICIT by CISI number.

Source: G. M. Jamison 2017, "The Organization of Indus Unicorn Seal Production", PhD thesis, University of
Wisconsin-Madison, https://search.library.wisc.edu/digital/AC3N6TSMX73CAE8O (open PDF; (c) the author,
all rights reserved). The thesis stays local in raw/ (gitignored). Only derived counts are published.

Run from the repo root:  .venv/bin/python -I experiments/carver_text/parse.py
Writes out/seals.json (one row per Appendix 7.1 seal, with group, attributes and ICIT link) and prints the join.
"""
import json, re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
TXT = HERE / "raw" / "jamison2017.txt"
OUT = HERE / "out"; OUT.mkdir(exist_ok=True)
ATTR = ["EYE", "EAR", "HEAD", "HORN", "NECK", "HALTER", "TAIL", "LEG", "HOOF", "PIZZLE", "STAND"]
VAL = r"(?:n/a|\d+[a-z]?)"


def section(text, start, end):
    a = text.index(start, text.index(start) + 1)  # skip the table of contents entry
    b = text.index(end, a) if end else len(text)
    return text[a:b]


TAIL = re.compile(rf"\s+({VAL}(?:\s+{VAL}){{10}})\s*$")


def rows_of(s):
    """Yield (prefix fields split on 2+ spaces, 11 attribute values) for every attribute-table line."""
    for line in s.splitlines():
        m = TAIL.search(line)
        if not m:
            continue
        pre = [x.strip() for x in re.split(r"\s{2,}", line[:m.start()].strip()) if x.strip()]
        if len(pre) == 2:
            yield pre, m.group(1).split()


def parse_71(s):
    rows = {}
    for (sid, site), vals in rows_of(s):
        sid = sid.replace(" ", "")
        if re.fullmatch(r"[A-Za-z]+\d+[A-Za-z]?", sid):
            rows[sid] = dict(id=sid, site=site, attrs=dict(zip(ATTR, vals)))
    return rows


def parse_91(s):
    rows = []
    for (grp, sid), vals in rows_of(s):
        sid = sid.replace(" ", "")
        if grp.lower() == "group" or not re.fullmatch(r"[A-Za-z]+\d+[A-Za-z]?", sid):
            continue
        rows.append(dict(group=grp.replace(" ", ""), id=sid, attrs=dict(zip(ATTR, vals))))
    return rows


def norm(cisi):
    return re.sub(r"[^A-Z0-9]", "", cisi.upper())


def main():
    text = TXT.read_text(errors="replace")
    s71 = section(text, "Appendix 7.1", "Appendix 9.1")
    s91 = section(text, "Appendix 9.1", None)
    a71, g91 = parse_71(s71), parse_91(s91)
    icit = [json.loads(l) for l in (ROOT / "data/icit_texts.jsonl").read_text().splitlines() if l.strip()]
    by = defaultdict(list)
    for r in icit:
        if r["cisi"] not in ("-", ""):
            by[norm(r["cisi"])].append(r)
    group_of = {}
    for r in g91:
        group_of.setdefault(r["id"], r["group"])
    for r in g91:
        a71.setdefault(r["id"], dict(id=r["id"], site="(9.1 only)", attrs=r["attrs"]))
    seals = []
    for sid, r in a71.items():
        hits = by.get(norm(sid), [])
        seals.append(dict(id=sid, site=r["site"], group=group_of.get(sid), attrs=r["attrs"],
                          icit=[dict(id=h["id"], site=h["site"], type=h["type"], symbol=h["symbol"], seq=h["seq"],
                                     complete=h["complete"], period=h["period"], width_mm=h["width_mm"], height_mm=h["height_mm"])
                                for h in hits]))
    (OUT / "seals.json").write_text(json.dumps(seals, indent=1))
    grouped = [s for s in seals if s["group"]]
    linked = [s for s in grouped if s["icit"]]
    gsize = Counter(s["group"] for s in grouped)
    lsize = Counter(s["group"] for s in linked)
    print("Appendix 7.1 seals:", len(a71), "| Appendix 9.1 rows:", len(g91), "groups:", len({r['group'] for r in g91}))
    print("9.1 ids not in 7.1:", sorted({r['id'] for r in g91} - set(a71))[:20])
    print("all seals linked to ICIT:", sum(1 for s in seals if s["icit"]), "of", len(seals))
    print("grouped seals:", len(grouped), "linked:", len(linked))
    print("groups with >=2 linked members:", sum(1 for g, n in lsize.items() if n >= 2),
          "| seals in them:", sum(n for n in lsize.values() if n >= 2))
    sym = Counter(h["symbol"] for s in linked for h in s["icit"][:1])
    print("ICIT symbol on linked grouped seals:", sym.most_common(6))
    site_ok = Counter((s["site"] == "(9.1 only)") or (s["site"].split()[0].lower()[:5] == s["icit"][0]["site"].lower()[:5]) for s in linked)
    print("site agrees (first 5 letters):", dict(site_ok))
    multi = Counter(len(s["icit"]) for s in linked)
    print("ICIT rows per linked seal:", dict(multi))
    print("unlinked grouped ids (first 30):", [s["id"] for s in grouped if not s["icit"]][:30])


if __name__ == "__main__":
    main()
