"""sealing_generative count gate (plan 12, family 4). Counting only, no model.

Run from the repo root:  python3 -I experiments/sealing_generative/count_gate.py
Writes experiments/sealing_generative/count_gate.json.

Counts:
  1. N_indus: distinct non-empty sign sequences on M77 objects typed seal or sealing; FLOOR = ceil(N/2).
  2. Local CDLI bulk dump: distinct legible seal legends (@seal blocks with at least one numbered
     text line, none of whose lines is wholly broken) per CDLI period, and per language tag.
  3. Local ORACC Ur III seal units used by meaning_classes_seal (distinct legends).
"""
import collections
import csv
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
M77 = os.path.join(ROOT, "data", "m77_texts.jsonl")
ATF = os.path.join(ROOT, "experiments", "short_labels", "raw", "cdli", "cdliatf_unblocked.atf")
CAT = os.path.join(ROOT, "experiments", "short_labels", "raw", "cdli", "cdli_cat.csv")
UR3 = os.path.join(ROOT, "experiments", "meaning_classes_seal", "data", "cun_seal.jsonl")


def indus():
    seen = set()
    by_type = collections.Counter()
    for line in open(M77, encoding="utf-8"):
        d = json.loads(line)
        if d.get("object_type") not in ("seal", "sealing"):
            continue
        seq = tuple(s for s in d.get("seq", []) if s != "|")
        if not seq:
            continue
        by_type[d["object_type"]] += 1
        seen.add(seq)
    n = len(seen)
    return {"objects_with_text": dict(by_type), "distinct_legends": n, "floor": math.ceil(n / 2)}


LINE_RE = re.compile(r"^\d+[a-z']*\.\s+(.*)$")


def norm(s):
    s = re.sub(r"[#?!*\[\]<>]", "", s)
    return re.sub(r"\s+", " ", s).strip()


def cdli():
    csv.field_size_limit(sys.maxsize)
    period, lang = {}, {}
    with open(CAT, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            try:
                pid = "P%06d" % int(r["id_text"])
            except (ValueError, KeyError):
                continue
            period[pid] = (r.get("period") or "").strip() or "?"
            lang[pid] = (r.get("language") or "").strip() or "?"
    legends = collections.defaultdict(set)  # period -> distinct legends
    blocks = collections.Counter()
    lang_by_period = collections.defaultdict(collections.Counter)
    cur, in_seal, buf, bad = None, False, [], False

    def flush():
        if in_seal and cur:
            per = period.get(cur, "?")
            blocks[per] += 1
            text = [norm(x) for x in buf]
            text = [t for t in text if t and not re.fullmatch(r"[x .\-]*", t)]
            if text and not bad:
                legends[per].add(" | ".join(text))
                lang_by_period[per][lang.get(cur, "?")] += 1

    for raw in open(ATF, encoding="utf-8", errors="replace"):
        line = raw.rstrip("\n")
        if line.startswith("&P"):
            flush()
            cur, in_seal, buf, bad = line[1:8], False, [], False
            continue
        if line.startswith("@"):
            flush()
            in_seal = line.startswith("@seal")
            buf, bad = [], False
            continue
        if in_seal:
            m = LINE_RE.match(line.strip())
            if m:
                body = m.group(1)
                if re.fullmatch(r"[\s\[\]x.\-]*", body) or "..." in body and len(norm(body)) < 4:
                    bad = True
                buf.append(body)
    flush()
    out = {}
    for per in sorted(blocks, key=lambda p: -len(legends[p])):
        out[per] = {
            "seal_blocks": blocks[per],
            "distinct_legible_legends": len(legends[per]),
            "top_languages": lang_by_period[per].most_common(3),
        }
    return out


SEAL_OBJ = ("seal (not impression)", "seal", "sealing", "bulla")


def cdli_seal_objects():
    """CDLI catalogue objects whose object_type is a seal, sealing or bulla: distinct legible legends
    (all numbered text lines of the object, damaged-only lines dropped) per period. These are seal
    objects and composite seals, not impressions on tablets (those are counted by cdli())."""
    csv.field_size_limit(sys.maxsize)
    meta = {}
    with open(CAT, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if (r.get("object_type") or "").strip().lower() not in SEAL_OBJ:
                continue
            try:
                pid = "P%06d" % int(r["id_text"])
            except (ValueError, KeyError):
                continue
            meta[pid] = (r.get("period") or "").strip() or "?"
    legends = collections.defaultdict(set)
    objects = collections.Counter()
    cur, buf = None, []

    def flush():
        if cur in meta:
            objects[meta[cur]] += 1
            text = [norm(x) for x in buf]
            text = [t for t in text if t and not re.fullmatch(r"[x .\-]*", t)]
            if text:
                legends[meta[cur]].add(" | ".join(text))

    for raw in open(ATF, encoding="utf-8", errors="replace"):
        line = raw.rstrip("\n")
        if line.startswith("&P"):
            flush()
            cur, buf = line[1:8], []
            continue
        m = LINE_RE.match(line.strip())
        if m and cur in meta:
            buf.append(m.group(1))
    flush()
    return {per: {"objects_with_atf": objects[per], "distinct_legible_legends": len(legends[per])}
            for per in sorted(objects, key=lambda p: -len(legends[p]))}


def ur3():
    seen = set()
    for line in open(UR3, encoding="utf-8"):
        seen.add(tuple(json.loads(line)["seq"]))
    return {"distinct_legends": len(seen)}


ROW_RE = re.compile(r'<a class="tr" role="row" href="/inscription/(\d+)">(.*?)</a>', re.S)
CELL_RE = re.compile(r'<div class="td[^"]*" role="gridcell">(.*?)</div>', re.S)


def pnm(pages_dir):
    """PNM listing pages for object type 'Scarab, seal, scaraboid, intaglio and similar objects',
    fetched (start=0..3500, step 50) into pages_dir, outside the repo. Columns: type, inventory,
    material, size, text type, date, origin, provenance?, owner."""
    import html as _html
    rows = {}
    for fn in sorted(os.listdir(pages_dir)):
        t = open(os.path.join(pages_dir, fn), encoding="utf-8").read()
        for m in ROW_RE.finditer(t):
            cells = [re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", "", c))).strip()
                     for c in CELL_RE.findall(m.group(2))]
            rows[m.group(1)] = cells
    text_type = collections.Counter(c[4] if len(c) > 4 else "?" for c in rows.values())
    owners = set()
    royal = set()
    for c in rows.values():
        owner = c[-1] if c else ""
        if owner:
            owners.add(owner)
        if len(c) > 5 and c[4].lower().startswith("royal"):
            royal.add(c[5])
    return {
        "objects": len(rows),
        "text_type": text_type.most_common(),
        "distinct_named_owners": len(owners),
        "distinct_royal_legends": len(royal),
        "distinct_legend_lower_bound": len(owners) + len(royal),
    }


def main():
    res = {"indus": indus(), "oracc_ur3_seal_units": ur3(), "cdli_by_period": cdli(),
           "cdli_seal_objects_by_period": cdli_seal_objects()}
    for per, v in list(res["cdli_seal_objects_by_period"].items())[:15]:
        print("OBJ", v["distinct_legible_legends"], v["objects_with_atf"], per)
    if len(sys.argv) > 1:
        res["pnm_egyptian_seals"] = pnm(sys.argv[1])
        print(json.dumps(res["pnm_egyptian_seals"], ensure_ascii=False))
    with open(os.path.join(HERE, "count_gate.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1, ensure_ascii=False)
    print(json.dumps(res["indus"]), json.dumps(res["oracc_ur3_seal_units"]))
    for per, v in list(res["cdli_by_period"].items())[:25]:
        print(f'{v["distinct_legible_legends"]:7d} {v["seal_blocks"]:7d}  {per}  {v["top_languages"]}')


if __name__ == "__main__":
    main()
