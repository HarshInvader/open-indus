"""Post hoc (NOT pre-registered): is the S1 per-title hit for T347 (W760 = M347/M358) real?
Checks: (a) one face per distinct text per object (removes one die stamped several times);
(b) M77 with M347 alone; (c) list the objects.
Run: .venv/bin/python -I experiments/sealing_function/explore_t347.py
"""
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyze as A  # noqa: E402

OUT = Path(__file__).resolve().parent
A.NPERM = 20000


def main():
    lines = []

    def log(s=""):
        print(s)
        lines.append(s)

    rows = A.load()
    is347 = lambda f: "T347" in A.titles_of(f, A.W_TITLES)
    log("Objects with W760 faces:")
    for r in rows:
        if any(is347(f) for f in r["legible"]):
            log(f"  {r['site']} {r['object']} multi={r['multi']} faces: {r['faces']}")
    raw = [(r["site"], r["multi"], r["legible"]) for r in rows if r["legible"]]
    ded = [(r["site"], r["multi"], sorted(set(r["legible"]))) for r in rows if r["legible"]]
    R = {"icit_raw": A.s1(raw, is347, log, "ICIT T347 raw faces"),
         "icit_dedup": A.s1(ded, is347, log, "ICIT T347 one face per distinct text per object")}
    mrows = list(csv.DictReader(open(OUT / "sealings_m77.csv")))
    mobjs = [(r["site"], int(r["multi"]), sorted(set(f.strip() for f in r["sides"].split(" | ") if f.strip()))) for r in mrows]
    m347 = lambda f: "M347" in f.split()
    log("M77 objects with M347:")
    for r in mrows:
        if any(m347(f) for f in r["sides"].split(" | ")):
            log(f"  {r['site']} {r['m77_text_no']} multi={r['multi']} sides: {r['sides']}")
    R["m77_dedup"] = A.s1(mobjs, m347, log, "M77 M347 one side per distinct text per object")
    json.dump(R, open(OUT / "explore_t347.json", "w"), indent=1)
    open(OUT / "explore_t347.log", "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
