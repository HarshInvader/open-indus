"""Combine raters A and B (and tie-break C for split rows) into final.json, with kappa. Prereg docs/prereg/scorecard_v1.md.
Run: .venv/bin/python -I experiments/scorecard_v1/finalize.py
"""
import csv, json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATS = "AFSRUPN"


def main():
    rows = list(csv.DictReader(open(HERE / "rows.csv")))
    A = {x["id"]: x for x in json.load(open(HERE / "rater_A.json"))}
    B = {x["id"]: x for x in json.load(open(HERE / "rater_B.json"))}
    C = {x["id"]: x for x in json.load(open(HERE / "rater_C.json"))}
    n = len(rows); ids = [r["id"] for r in rows]
    po = sum(A[i]["tier"] == B[i]["tier"] for i in ids) / n
    ca, cb = Counter(A[i]["tier"] for i in ids), Counter(B[i]["tier"] for i in ids)
    pe = sum(ca[c] * cb[c] for c in CATS) / n / n; kappa = (po - pe) / (1 - pe)
    out = []
    for r in rows:
        i = r["id"]; split = A[i]["tier"] != B[i]["tier"]
        tier = C[i]["tier"] if split else A[i]["tier"]
        reason = C[i]["reason"] if split else A[i]["reason"]
        out.append(dict(r, tier=tier, reason=reason, split=split, rater_tiers=[A[i]["tier"], B[i]["tier"]] + ([C[i]["tier"]] if split else [])))
    res = dict(kappa=round(kappa, 3), agreement=round(po, 3), n=n, kappa_bar=0.8, passed=kappa >= 0.8,
               counts=dict(Counter(x["tier"] for x in out)), rows=out)
    json.dump(res, open(HERE / "final.json", "w"), indent=1)
    print({k: v for k, v in res.items() if k != "rows"})
    for g in ("calibration", "phonetic key", "function claim", "meaning claim", "our finding"):
        print(g, dict(Counter(x["tier"] for x in out if x["group"] == g)))


if __name__ == "__main__":
    main()
