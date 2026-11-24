"""meaning_calibration v2 claims stage (prereg meaning_calibration.md + v2 + addendum 1). Scores A's 30 true claims,
B's 30 uninformed claims and the chance baseline with fcore2.verdict2 unchanged; majority over the 5 v2 draws.
Run: nice -n 20 .venv/bin/python -I experiments/meaning_calibration/run.py
"""
import json, random, sys
from collections import Counter
from pathlib import Path
from scipy.stats import beta

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fcore as F    # noqa: E402
import fcore2 as G   # noqa: E402
F.SEED0 = G.SEED0

K2 = json.load(open(HERE / "kill2.json"))
POWER = {b: v["power"] for b, v in K2["power_by_bin"].items()}
A = json.load(open(HERE / "claims/A_claims.json"))
B = json.load(open(HERE / "claims/B_claims.json"))
opaque = json.load(open(HERE / "claims_input/opaque.json")); back = {v: k for k, v in opaque.items()}
dmap = json.load(open(HERE / "claims/decoy_map.json"))
SCORE = {"S": 2, "U": 1, "U-resolution": 1, "R": 0}
N_CHANCE = 50


def majority(vs):
    c = Counter("U" if v == "U-resolution" else v for v in vs)
    top = c.most_common()
    if len(top) > 1 and top[0][1] == top[1][1]: return "U"
    return top[0][0]


def main():
    docs = F.LB.documents()
    sides = []
    for k in range(F.NDRAW):
        d, h = F.draw(k, docs); sides.append((F.Side(d), F.Side(h)))
    inv = sorted(opaque)

    def score(head, main, sq):
        vs = [G.verdict2(D, H, head, main, tuple(sq), POWER)[0] for D, H in sides]
        return majority(vs), vs

    rows = []
    for a in A:
        v, vs = score(a["head"], a["main"], a["secondaries"])
        rows.append(dict(who="A", head=a["head"], cls=F.tclass(a["head"]), P=[a["main"], *a["secondaries"]], meaning=a["meaning"], verdict=v, draws=vs))
    rng = random.Random(G.SEED0 + 4242)
    chance = []
    for b, dm in zip(B, dmap):
        head = back[b["id"]]; assert head == dm["decoy"]
        P = [back[b["main"]], *[back[x] for x in b["secondaries"]]]
        v, vs = score(head, P[0], P[1:])
        rows.append(dict(who="B", head=head, cls=F.tclass(head), P=P, meaning=b["meaning"], verdict=v, draws=vs))
        for _ in range(N_CHANCE):
            Q = rng.sample([t for t in inv if t != head], len(P))
            chance.append(score(head, Q[0], Q[1:])[0])
    Ar = [r for r in rows if r["who"] == "A"]; Br = [r for r in rows if r["who"] == "B"]
    nA = len(Ar); kR = sum(r["verdict"] == "R" for r in Ar)
    ub = float(beta.ppf(0.9, kR + 1, nA - kR)) if kR < nA else 1.0
    wins = sum((SCORE[x["verdict"]] > SCORE[y["verdict"]]) + 0.5 * (SCORE[x["verdict"]] == SCORE[y["verdict"]]) for x in Ar for y in Br)
    auc = wins / (len(Ar) * len(Br))
    uA = sum(r["verdict"] == "U" for r in Ar) / nA
    ideo = [r for r in Ar if r["cls"] == "ideogram/measure"]
    res = dict(
        A=dict(Counter(r["verdict"] for r in Ar)), B=dict(Counter(r["verdict"] for r in Br)),
        chance=dict(Counter(chance)), chance_survival=round(sum(c == "S" for c in chance) / len(chance), 4),
        false_refutation=dict(k=kR, n=nA, rate=round(kR / nA, 3), upper90=round(ub, 3), bar=0.15, met=ub <= 0.15),
        auc=dict(value=round(auc, 3), bar=0.75, met=auc >= 0.75),
        A_U_share=round(uA, 3), underpowered=uA > 0.6,
        B_false_survival=round(sum(r["verdict"] == "S" for r in Br) / len(Br), 3),
        A_ideogram_stratum=dict(n=len(ideo), verdicts=dict(Counter(r["verdict"] for r in ideo))),
        A_nonideogram_stratum=dict(Counter(r["verdict"] for r in Ar if r["cls"] != "ideogram/measure")),
        power_by_bin_used=POWER, rows=rows)
    json.dump(res, open(HERE / "result.json", "w"), indent=1, ensure_ascii=False)
    print(json.dumps({k: v for k, v in res.items() if k != "rows"}, indent=1, ensure_ascii=False))
    for r in rows: print(r["who"], r["head"], r["P"], r["verdict"], r["draws"])


if __name__ == "__main__":
    main()
