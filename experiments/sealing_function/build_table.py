"""Build sealings.csv (all ICIT sealing objects, Lothal reverse types joined) and sealings_m77.csv
(M77 multi-side sealing objects outside Harappa). Pre-registration: docs/prereg/sealing_function.md.

Run: .venv/bin/python -I experiments/sealing_function/build_table.py
Inputs (data only, never executed):
  data/icit_texts.jsonl, data/m77_texts.jsonl (via corpus/load.py)
  sources/paragorth_Indus-/data/derived/lothal-sealings-frenez-tosi2005.json  (Frenez & Tosi 2005 Table 1)
  sources/paragorth_Indus-/data/derived/dark/loop71_lothal_sealings.csv        (FT notes, Rao reverse notes)
"""
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from corpus.load import icit_texts, m77_texts  # noqa: E402

OUT = Path(__file__).resolve().parent
FTJ = ROOT / "sources/paragorth_Indus-/data/derived/lothal-sealings-frenez-tosi2005.json"
CAT = ROOT / "sources/paragorth_Indus-/data/derived/dark/loop71_lothal_sealings.csv"

DOOR = {"pegs-on-wall"}
FIXED = {"pegs-on-wall", "lockers", "structures"}


def back_class(b):
    if not b or b == "undiagnostic":
        return ""
    if b in DOOR:
        return "DOOR"
    if b in FIXED:
        return "FIXED_OTHER"
    return "CONTAINER"


def main():
    ft = {r[0]: dict(n=r[1], back=r[2], ctx=r[3]) for r in json.load(open(FTJ))["rows"]}
    cat = {r["cisi"]: r for r in csv.DictReader(open(CAT))}
    objs = defaultdict(list)
    for r in icit_texts():
        if not r["type"].startswith("TAG"):
            continue
        key = (r["site"], r["cisi"] if r["cisi"] not in ("", "-") else "id:" + str(r["id"]).split(".")[0])
        objs[key].append(r)
    # Lothal sealings in FT with no ICIT face still get a row (reverse type known, text missing)
    have = {k[1] for k in objs if k[0] == "Lothal"}
    for c in ft:
        if c not in have:
            objs[("Lothal", c)] = []
    rows = []
    for (site, cid), faces in sorted(objs.items()):
        f = ft.get(cid) if site == "Lothal" else None
        texts = [" ".join(x["seq"]) for x in faces]
        legible = [t for t in texts if t.replace("#", "").strip()]
        distinct_txt = sorted(set(legible))
        n_faces = len(faces)
        if f:
            multi = int(f["n"] >= 2)
            multi_src = "FT2005 n_impressions"
        else:
            multi = int(n_faces >= 2 and (len(distinct_txt) >= 2 or len(legible) < n_faces))
            multi_src = "ICIT faces"
        c = cat.get(cid, {}) if site == "Lothal" else {}
        rows.append(dict(
            site=site, object=cid, icit_ids=";".join(str(x["id"]) for x in faces),
            icit_type=";".join(sorted({x["type"] for x in faces})), n_faces_icit=n_faces,
            n_impressions_ft=f["n"] if f else "", multi=multi, multi_source=multi_src,
            back_type=f["back"] if f else "", back_class=back_class(f["back"]) if f else "",
            context_ft=f["ctx"] if f else "",
            ft_note=c.get("ft_note", ""), rao_reverse=c.get("rao_reverse", ""),
            faces=" | ".join(texts), n_distinct_legible=len(distinct_txt),
            reverse_source="Frenez & Tosi 2005 Table 1 (paragorth transcription)" if f else "not available in open sources",
        ))
    keys = list(rows[0].keys())
    with open(OUT / "sealings.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, keys)
        w.writeheader()
        w.writerows(rows)
    # M77 multi-side sealing objects (Harappa excluded: moulded tablets with count sides)
    g = defaultdict(list)
    for t in m77_texts():
        if t["object_type"] == "sealing" and t["site"] != "Harappa":
            g[(t["site"], t["text_no"])].append(t)
    mrows = []
    for (site, no), sides in sorted(g.items()):
        texts = [" ".join(s["seq"]) for s in sorted(sides, key=lambda s: s["side"])]
        legible = [x for x in texts if x.strip()]
        mrows.append(dict(site=site, m77_text_no=no, n_sides=len(sides), n_distinct_legible=len(set(legible)),
                          multi=int(len(sides) >= 2 and (len(set(legible)) >= 2 or len(legible) < len(sides))),
                          sides=" | ".join(texts)))
    with open(OUT / "sealings_m77.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, list(mrows[0].keys()))
        w.writeheader()
        w.writerows(mrows)
    from collections import Counter
    print(f"sealings.csv: {len(rows)} objects; by site {Counter(r['site'] for r in rows).most_common()}")
    print(f"  with reverse type: {sum(1 for r in rows if r['back_type'])}; diagnostic {sum(1 for r in rows if r['back_class'])}; "
          f"diagnostic with >=1 legible face {sum(1 for r in rows if r['back_class'] and r['n_distinct_legible'])}")
    print(f"  multi-impression objects: {sum(r['multi'] for r in rows)}; by site {Counter(r['site'] for r in rows if r['multi']).most_common()}")
    print(f"sealings_m77.csv: {len(mrows)} objects, multi {sum(r['multi'] for r in mrows)}; {Counter(r['site'] for r in mrows if r['multi']).most_common()}")


if __name__ == "__main__":
    main()
