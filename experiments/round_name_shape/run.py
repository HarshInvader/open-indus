"""Round seal texts vs phonetic-name shape (prereg docs/prereg/round_name_shape.md).
Run: .venv/bin/python -I experiments/round_name_shape/run.py [power|real]"""
import sys, json, re
from pathlib import Path
from collections import defaultdict
import numpy as np
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "experiments/typology"))
from corpus.load import icit_texts, distinct  # noqa
from corpora import ur3_names  # noqa
import q2_gulf as Q  # noqa  (residue, is_person, is_num, FOREIGN_ALL)

SEED = 20261123
rng = np.random.default_rng(SEED)

def legible(seq):
    return [s for s in seq if re.fullmatch(r"W\d+", s)]

R = json.load(open(ROOT / "experiments/round_seal_format/results.json"))["round_texts"]
round_res = [r for r in (Q.residue(legible(u["seq"].split())) for u in R) if r]
home = [r for r in (Q.residue(legible(t["seq"])) for t in distinct(icit_texts())
        if t["type"] == "SEAL:S" and t["site"] not in Q.FOREIGN_ALL and t["site"] != "Unknown") if r]
bylen = defaultdict(list)
for r in home: bylen[min(len(r), 5)].append(r)
inv = sorted({s for r in home for s in r})

def G(res):
    toks = [s for r in res for s in r]
    return len(set(toks)) / len(toks), float(np.mean([len(set(r)) < len(r) for r in res]))

def null(keys, nd):
    g1, g2 = np.empty(nd), np.empty(nd)
    for i in range(nd):
        g1[i], g2[i] = G([bylen[k][rng.integers(len(bylen[k]))] for k in keys])
    return g1, g2

def decide(res, nd):
    keys = [min(len(r), 5) for r in res]
    o1, o2 = G(res); g1, g2 = null(keys, nd)
    p1 = (1 + (g1 <= o1).sum()) / (nd + 1); p2 = (1 + (g2 >= o2).sum()) / (nd + 1)
    ps = sorted([(p1, "G1"), (p2, "G2")]); holm = {}
    run = 0
    for i, (p, k) in enumerate(ps):
        run = max(run, min(1, p * (2 - i))); holm[k] = run
    sup = holm["G1"] < 0.05 or (holm["G2"] < 0.05 and o2 >= 0.15)
    return dict(G1=o1, G2=o2, p1=p1, p2=p2, holm=holm, supported=bool(sup),
                null_G1=float(g1.mean()), null_G2=float(g2.mean()))

def syllabic_ur(n):
    logos = {"ur", "lu2", "lugal", "nin", "e2", "dingir", "szesz", "ab", "ad", "sa6", "kal", "mes", "nig2", "inim", "gu", "za"}
    return "{" not in "".join(n) and all(re.fullmatch(r"[^aeiu\d]{0,2}[aeiu][^aeiu\d]?\d?", s) for s in n) and n[0] not in logos

names = [n for n in ur3_names() if 2 <= len(n) <= 5 and syllabic_ur(n)]
nbylen = defaultdict(list)
for n in names: nbylen[len(n)].append(n)
syl = sorted({s for n in names for s in n})

def plant():
    m = dict(zip(syl, rng.choice(inv, size=len(syl), replace=len(syl) > len(inv))))
    out = []
    for r in round_res:
        L = len(r)
        if 2 <= L <= 5 and nbylen[L]:
            n = nbylen[L][rng.integers(len(nbylen[L]))]; out.append([m[s] for s in n])
        else:
            out.append(r)
    return out

mode = sys.argv[1] if len(sys.argv) > 1 else "power"
info = dict(n_round_residues=len(round_res), n_home=len(home), n_names=len(names), n_syllables=len(syl),
            round_len=dict(sorted({L: sum(len(r) == L for r in round_res) for L in {len(r) for r in round_res}}.items())))
print(info)
if mode == "power":
    res = [decide(plant(), 1000) for _ in range(200)]
    pw = float(np.mean([r["supported"] for r in res]))
    out = dict(info, power=pw, plant_G1_mean=float(np.mean([r["G1"] for r in res])),
               plant_G2_mean=float(np.mean([r["G2"] for r in res])), gate="PASS" if pw >= 0.8 else "STOP: untestable at n")
    print(out); json.dump(out, open(HERE / "power.json", "w"), indent=1)
elif mode == "real":
    assert json.load(open(HERE / "power.json"))["power"] >= 0.8, "power gate not passed"
    assert not (HERE / "real.json").exists(), "real set already scored"
    out = dict(info, **decide(round_res, 10000)); print(out); json.dump(out, open(HERE / "real.json", "w"), indent=1)
