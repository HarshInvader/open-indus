"""R10 (review 2): bootstrap contrast Δfloor(Ur III) − Δfloor(Indus) from the saved replicates in draws_boot.jsonl.
Rules in docs/prereg/uniformity_paper_contrast.md. No classifier runs; arithmetic only. Writes contrast.json."""
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
MARGIN = 0.05
QS = (2.5, 5, 50, 95, 97.5)
INDUS = ("MDHA_m77_seal", "MDHA_icit_seal", "MDHA_icit_sealtype")
UNI = ("UNI_icit_seal", "UNI_icit_sealtype")
UR3 = ("REF_ur3_U_reign", "REF_ur3_U_coll", "REF_ur3_G_reign", "REF_ur3_G_coll", "REF_cdli_U_reign", "REF_cdli_G_reign")
PRIMARY_UR3 = "REF_ur3_U_reign"


def load():
    d = {}
    for l in open(HERE / "draws_boot.jsonl"):
        r = json.loads(l)
        if r["b"] and r["w"]:
            d.setdefault(r["cond"], {})[r["rep"]] = float(np.median(r["b"]) - np.median(r["w"]))
    return d


def summarise(D):
    D = np.asarray(D, float)
    p = {str(q): float(np.percentile(D, q)) for q in QS}
    return dict(n=int(D.size), pct=p, above=bool(p["2.5"] > 0), above_margin=bool(p["5"] >= MARGIN))


def contrast(d, u, i):
    reps = sorted(set(d[u]) & set(d[i]))
    paired = [d[u][r] - d[i][r] for r in reps]
    U, I = np.array([d[u][r] for r in d[u]]), np.array([d[i][r] for r in d[i]])
    allc = (U[:, None] - I[None, :]).ravel()
    return dict(ur3=u, indus=i, paired=summarise(paired), all_combinations=summarise(allc))


def main():
    d = load()
    out = dict(primary=[contrast(d, PRIMARY_UR3, i) for i in INDUS],
               secondary=[contrast(d, u, i) for u in UR3 for i in INDUS] + [contrast(d, PRIMARY_UR3, i) for i in UNI])
    json.dump(out, open(HERE / "contrast.json", "w"), indent=1)
    for k in ("primary", "secondary"):
        print(f"== {k}")
        for c in out[k]:
            p, a = c["paired"]["pct"], c["all_combinations"]["pct"]
            print(f"{c['ur3']:18s} - {c['indus']:20s} med {p['50']:+.3f}  95% [{p['2.5']:+.3f}, {p['97.5']:+.3f}]  "
                  f"q5 {p['5']:+.3f}  above={c['paired']['above']} margin={c['paired']['above_margin']}  "
                  f"| all-comb [{a['2.5']:+.3f}, {a['97.5']:+.3f}]")


if __name__ == "__main__":
    main()
