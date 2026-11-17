"""Short crib lists from names.csv (list size drives the noise fit, see H3's note on the board).

Writes:
  short_gulf_core.csv  people explicitly tied to Meluhha/Magan/Dilmun (catalogue + literature) + Gulf deities
  short_<lang>_top150.csv  the 150 most attested distinct syllable strings per language (Sumerian, Akkadian, Amorite)
usage: .venv/bin/python -I experiments/onomasticon/short_lists.py
"""
import csv
import re
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
R = list(csv.DictReader(open(HERE / "names.csv")))


def attest(r):
    m = re.search(r"\(x(\d+)\)", r["role"])
    if m:
        return int(m.group(1))
    ids = r["source_text_id"].split(";")
    extra = sum(int(x[1:]) for x in ids if x.startswith("+"))
    return len([x for x in ids if x and not x.startswith("+")]) + extra


cols = ["syllables", "n_syll", "written", "name", "language", "attestations", "source", "source_text_id", "role"]
core = [r for r in R if r["lang_basis"] in ("catalogue (literature)", "literature") and r["syllables"]]
with open(HERE / "short_gulf_core.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols + ["kind"], extrasaction="ignore")
    w.writeheader()
    for r in core:
        w.writerow({**r, "attestations": attest(r), "kind": "person"})
    for d in csv.DictReader(open(HERE / "deities_formulas.csv")):
        if d["kind"] in ("deity", "place") and d["syllables"]:
            w.writerow({"syllables": d["syllables"], "n_syll": len(d["syllables"].split(".")), "written": d["written"],
                        "name": d["name"], "language": d["language"], "attestations": "", "source": d["source"],
                        "source_text_id": d["text_id"], "role": d["role"] + " [" + d["verified"] + "]", "kind": d["kind"]})
print("core", len(core))
for lang in ("Sumerian", "Akkadian", "Amorite"):
    agg = defaultdict(lambda: [0, None])
    for r in R:
        if r["language"] == lang and r["syllables"]:
            a = agg[r["syllables"]]; a[0] += attest(r); a[1] = a[1] or r
    top = sorted(agg.items(), key=lambda kv: -kv[1][0])[:150]
    with open(HERE / f"short_{lang}_top150.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for s, (n, r) in top:
            w.writerow({**r, "attestations": n})
    print(lang, len(agg), "->", len(top), "min attestations in list", top[-1][1][0])
