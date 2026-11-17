"""Flag Mesopotamian-shaped names in names_all.csv (theophoric/logographic Sumero-Akkadian elements),
write short_Elamite_core.csv (unflagged, not in names.csv as Sum/Akk) and summary stats comparable to #2.
Rule: flag if any syllable is in MESO, or the name was already in onomasticon/names.csv as Sumerian/Akkadian.
    .venv/bin/python -I experiments/elamite_names/finalize.py"""
import csv, json, random
from pathlib import Path
HERE = Path(__file__).resolve().parent
MESO = {"dingir", "puzur", "ur", "suen", "utu", "iškur", "nanše", "lugal", "nin", "enlil", "šara", "ilum", "il", "silim",
        "lu", "igi", "e", "ha", "dumu", "ama"}
R = list(csv.DictReader(open(HERE / "names_all.csv")))
for r in R:
    syl = r["syllables"].split(".")
    r["meso_shape"] = "yes" if (r["mesopotamian_dup"] or any(s in MESO for s in syl)) else ""
core = [r for r in R if not r["meso_shape"] and r["syllables"]]
with open(HERE / "names_all.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(R[0])); w.writeheader(); w.writerows(R)
with open(HERE / "short_Elamite_core.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["syllables", "n_syll", "written", "name", "language", "attestations", "source", "source_text_id", "role"])
    w.writeheader()
    for r in core:
        w.writerow(dict(syllables=r["syllables"], n_syll=len(r["syllables"].split(".")), written=r["written"], name=r["name"],
                        language="Elamite/eastern (by origin)", attestations=r["attestations"], source="ORACC epsd2/admin/ur3",
                        source_text_id="", role="lu2 " + r["places"].split(":")[0]))
def rep(names):  # share of names with a repeated syllable
    return sum(len(set(s)) < len(s) for s in names) / len(names)
S = [r["syllables"].split(".") for r in core]
rng = random.Random(0); pool = [x for s in S for x in s]; null = []
for _ in range(2000):
    rng.shuffle(pool); i = 0; sh = []
    for s in S: sh.append(pool[i:i + len(s)]); i += len(s)
    null.append(rep(sh))
null.sort()
out = dict(n_core=len(core), n_flagged=len(R) - len(core), mean_syll=sum(map(len, S)) / len(S),
           repeat_share=rep(S), repeat_null_mean=sum(null) / len(null), repeat_null_95=[null[50], null[1949]],
           places=sorted({r["places"].split(":")[0] for r in core}))
json.dump(out, open(HERE / "stats_core.json", "w"), indent=1, ensure_ascii=False)
print(out)
