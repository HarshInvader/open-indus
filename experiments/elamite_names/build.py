"""Board #24: short Elamite/eastern personal-name crib list from Ur III texts (contemporary with Gulf seals).

Source: ORACC epsd2/admin/ur3 corpusjson (CC0), read in place from experiments/meaning_classes_seal/raw/ur3.zip.
Rule (fixed before looking at the names):
  a PN is 'eastern' if, in the same text line, the noun lu2 is followed (anywhere later in the line) by a
  settlement/geographic name in EAST, or by the word elam. Messenger-text pattern 'PN lu2 Anšan{ki}'.
  A name is kept if it is attested so, and it is NOT also a name in onomasticon/names.csv tagged Sumerian or
  Akkadian (those are Mesopotamian envoys, not Elamites). Syllables from the written form: determinatives,
  sign indices and damage marks removed, logographic capitals lower-cased, joined with '.'.
Writes: names_all.csv (every eastern PN with counts and places), short_Elamite_top150.csv (onomasticon format).
    .venv/bin/python -I experiments/elamite_names/build.py
"""
import csv, json, re, zipfile
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EAST = {"Anšan", "Šušin", "Susa", "Huhnuri", "Zabšali", "Šimaški", "Sabum", "Urua", "Marhaši", "Adamšah", "Hurti",
        "Ba.šim", "Pa.šim.e", "Gi.ša", "Du.du.li₂", "Elam", "Kimaš", "Hu.rim₃", "Šimašgi", "Šigriš", "Duduli", "Gisa"}
SUBS = str.maketrans("₀₁₂₃₄₅₆₇₈₉ₓ", "           ")


def walk(n, line, out):
    if isinstance(n, dict):
        if n.get("node") == "d" and n.get("type") == "line-start":
            line[0] = n.get("label", n.get("ref", ""))
        if isinstance(n.get("f"), dict):
            out.append((line[0], n["f"]))
        if "cdl" in n:
            walk(n["cdl"], line, out)
    elif isinstance(n, list):
        for x in n:
            walk(x, line, out)


def syllab(form):
    s = re.sub(r"\{[^}]*\}", "", form)            # determinatives
    s = re.sub(r"[\[\]#!?<>⸢⸣*]", "", s)
    s = s.translate(SUBS).replace(" ", "")
    s = re.sub(r"[0-9]", "", s)
    parts = [p.lower() for p in re.split(r"[-.+|]", s) if p and p.lower() != "x"]
    return ".".join(parts)


def main():
    known = {}
    for r in csv.DictReader(open(ROOT / "experiments/onomasticon/names.csv")):
        if r["language"] in ("Sumerian", "Akkadian"):
            known[r["name"].lower()] = r["language"]
    z = zipfile.ZipFile(ROOT / "experiments/meaning_classes_seal/raw/ur3.zip")
    cnt, forms, places, texts = Counter(), defaultdict(Counter), defaultdict(Counter), defaultdict(set)
    ntext = 0
    for nm in z.namelist():
        if "/corpusjson/" not in nm or not nm.endswith(".json"):
            continue
        try:
            d = json.loads(z.read(nm))
        except Exception:
            continue
        ntext += 1
        out = []; walk(d.get("cdl", []), [""], out)
        bylines = defaultdict(list)
        for lab, f in out:
            bylines[lab].append(f)
        for lab, fs in bylines.items():
            for i, f in enumerate(fs):
                if f.get("cf") != "lu" and f.get("form", "").split("{")[0] not in ("lu₂", "lu2"):
                    continue
                east = next((g.get("cf") for g in fs[i + 1:] if g.get("pos") in ("SN", "GN") and g.get("cf") in EAST)
                            or (g.get("cf") for g in fs[i + 1:] if (g.get("cf") or "").lower() == "elam"), None)
                if not east:
                    continue
                for g in fs[:i]:
                    if g.get("pos") == "PN" and g.get("cf"):
                        cnt[g["cf"]] += 1; forms[g["cf"]][g.get("form", "")] += 1
                        places[g["cf"]][east] += 1; texts[g["cf"]].add(d.get("textid", nm))
                break
    rows = []
    for n, c in cnt.most_common():
        form = forms[n].most_common(1)[0][0]
        rows.append(dict(name=n, written=form, syllables=syllab(form), attestations=c, n_texts=len(texts[n]),
                         places=";".join(f"{p}:{k}" for p, k in places[n].most_common()),
                         mesopotamian_dup=known.get(n.lower(), "")))
    with open(HERE / "names_all.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    keep = [r for r in rows if not r["mesopotamian_dup"] and r["syllables"]]
    short = keep[:150]
    with open(HERE / "short_Elamite_top150.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["syllables", "n_syll", "written", "name", "language", "attestations", "source",
                                          "source_text_id", "role"])
        w.writeheader()
        for r in short:
            w.writerow(dict(syllables=r["syllables"], n_syll=len(r["syllables"].split(".")), written=r["written"],
                            name=r["name"], language="Elamite/eastern (by origin)", attestations=r["attestations"],
                            source="ORACC epsd2/admin/ur3", source_text_id="", role="lu2 " + r["places"].split(":")[0]))
    stats = dict(texts_read=ntext, eastern_pns=len(rows), dropped_as_mesopotamian=sum(1 for r in rows if r["mesopotamian_dup"]),
                 kept=len(keep), short=len(short), place_counts=dict(Counter(p for r in rows for p in places[r["name"]]).most_common()),
                 mean_syll_short=sum(len(r["syllables"].split(".")) for r in short) / max(1, len(short)))
    json.dump(stats, open(HERE / "stats.json", "w"), indent=1, ensure_ascii=False)
    print(json.dumps(stats, ensure_ascii=False))


if __name__ == "__main__":
    main()
