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
    # Addendum 1: re-rated rows (stale catalogue evidence) replace v1.0 tiers; split rows would go to rater_F.
    dp, ep = HERE / "rater_D.json", HERE / "rater_E.json"
    if dp.exists() and ep.exists():
        D = {x["id"]: x for x in json.load(open(dp))}; Ev = {x["id"]: x for x in json.load(open(ep))}
        F = {x["id"]: x for x in json.load(open(HERE / "rater_F.json"))} if (HERE / "rater_F.json").exists() else {}
        for r in out:
            i = r["id"]
            if i in D:
                sp = D[i]["tier"] != Ev[i]["tier"]
                r["v1_0"] = dict(tier=r["tier"], reason=r["reason"])
                r["tier"] = F[i]["tier"] if sp else D[i]["tier"]; r["reason"] = F[i]["reason"] if sp else D[i]["reason"]
                r["split"] = sp; r["rater_tiers"] = [D[i]["tier"], Ev[i]["tier"]] + ([F[i]["tier"]] if sp else []); r["addendum"] = 1
    # Addenda 2 (FUN-sigil, G/H, tie K2), 3 (stroked jar + vata-min, I/J, tie K), 4 (murukan after calibration, L/M, tie N): same rule.
    for add_no, (a, b, c) in {2: ("rater_G.json", "rater_H.json", "rater_K2.json"), 3: ("rater_I.json", "rater_J.json", "rater_K.json"),
                                  4: ("rater_L.json", "rater_M.json", "rater_N.json")}.items():
        if not ((HERE / a).exists() and (HERE / b).exists()):
            continue
        X = {x["id"]: x for x in json.load(open(HERE / a))}; Y = {x["id"]: x for x in json.load(open(HERE / b))}
        Z = {x["id"]: x for x in json.load(open(HERE / c))} if (HERE / c).exists() else {}
        for r in out:
            i = r["id"]
            if i in X:
                sp = X[i]["tier"] != Y[i]["tier"]
                r.setdefault("v1_0", dict(tier=r["tier"], reason=r["reason"]))
                r["tier"] = Z[i]["tier"] if sp else X[i]["tier"]; r["reason"] = Z[i]["reason"] if sp else X[i]["reason"]
                r["split"] = sp; r["rater_tiers"] = [X[i]["tier"], Y[i]["tier"]] + ([Z[i]["tier"]] if sp else []); r["addendum"] = add_no
    res = dict(kappa=round(kappa, 3), agreement=round(po, 3), n=n, kappa_bar=0.8, passed=kappa >= 0.8,
               counts=dict(Counter(x["tier"] for x in out)), rows=out)
    json.dump(res, open(HERE / "final.json", "w"), indent=1)
    print({k: v for k, v in res.items() if k != "rows"})
    for g in ("calibration", "phonetic key", "function claim", "meaning claim", "our finding"):
        print(g, dict(Counter(x["tier"] for x in out if x["group"] == g)))


if __name__ == "__main__":
    main()
