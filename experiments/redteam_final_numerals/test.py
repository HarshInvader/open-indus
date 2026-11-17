"""Board #21: red team of #15 (final numerals on foreign texts). Prereg: docs/prereg/redteam_final_numerals.md
Run: .venv/bin/python -I experiments/redteam_final_numerals/test.py
"""
import csv, json, sys
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
from scipy.stats import fisher_exact

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "experiments/grammar"))
from glib import FOREIGN  # noqa
from corpus.load import icit_texts  # noqa

rng = np.random.default_rng(2117)
NDRAW = 20000
NONCOUNT = {"W001", "W002", "W031"}


def isnum(s):
    return s.startswith("W") and s[1:].isdigit() and 1 <= int(s[1:]) <= 59


def iscount(s):
    return isnum(s) and s not in NONCOUNT


def clean(seq):
    return tuple(x for x in seq.split("-") if x and x not in ("#", "|", "?"))


fc = {r["id"]: r for r in csv.DictReader(open(ROOT / "experiments/foreign_corpus/foreign_corpus.csv"))}
rc = {r["id"]: r for r in csv.DictReader(open(ROOT / "experiments/foreign_readings/readings_check.csv"))}


def seq_of(i):
    s = clean(fc[i]["seq_wells"])
    if len(s) < 2 and i == "UNPROV-02":
        s = clean(fc[i]["seq_m77"])
    return s


ALL = {i: clean(r["seq_wells"]) for i, r in fc.items() if r["n_legible"].isdigit() and int(r["n_legible"]) >= 2}
ALL = {i: s for i, s in ALL.items() if len(s) >= 2}
SEC = {}
for i, r in rc.items():
    u = r["use_in_crib_attack"]
    if (u.startswith("yes") or u.startswith("sensitivity")) and i in fc and len(seq_of(i)) >= 2:
        SEC[i] = seq_of(i)
ROUND = {i: s for i, s in ALL.items() if fc[i]["shape"].lower().startswith("round")}

# home pools
pools = {"SQ": set(), "CIRC": set(), "RECT": set()}
for t in icit_texts():
    if t["site"] in FOREIGN or t["site"] == "Unknown":
        continue
    s = tuple(x for x in t["seq"] if x not in ("#", "|"))
    if len(s) < 2:
        continue
    ty = t["type"]
    if ty in ("SEAL:S", "SEAL"):
        pools["SQ"].add(s)
    elif ty == "SEAL:C":
        pools["CIRC"].add(s)
    elif ty == "SEAL:R":
        pools["RECT"].add(s)


def bylen(pool, f):
    d = defaultdict(list)
    for s in pool:
        d[len(s)].append(f(s[-1]))
    return {L: np.array(v) for L, v in d.items()}


def null(lengths, BL, n=NDRAW):
    T = np.zeros(n, int)
    for L in lengths:
        P = BL[L] if len(BL.get(L, [])) >= 30 else np.concatenate([BL.get(k, np.array([], bool)) for k in (L - 1, L, L + 1)])
        if len(P) == 0:
            P = np.concatenate(list(BL.values()))
        T += P[rng.integers(0, len(P), n)]
    return T


def lm_test(texts, pool, f):
    BL = bylen(pool, f)
    obs = sum(f(t[-1]) for t in texts)
    T = null([len(t) for t in texts], BL)
    return {"n": len(texts), "obs": int(obs), "null_mean": round(float(T.mean()), 3), "p": float((T >= obs).mean())}


out = {"pool_sizes": {k: len(v) for k, v in pools.items()}}
out["home_rates"] = {k: {"numeral_final": float(np.mean([isnum(s[-1]) for s in v])),
                         "count_final": float(np.mean([iscount(s[-1]) for s in v]))} for k, v in pools.items()}
out["home_circ_final_signs"] = Counter(s[-1] for s in pools["CIRC"]).most_common(8)

# baseline reproduction of #15
out["repro_ALL_SQ"] = lm_test(list(ALL.values()), pools["SQ"], isnum)
out["repro_SEC_SQ"] = lm_test(list(SEC.values()), pools["SQ"], isnum)

# A: genre
r_hit = sum(isnum(s[-1]) for s in ROUND.values()); r_n = len(ROUND)
c_hit = sum(isnum(s[-1]) for s in pools["CIRC"]); c_n = len(pools["CIRC"])
odds, pA1 = fisher_exact([[r_hit, r_n - r_hit], [c_hit, c_n - c_hit]], alternative="greater")
pw = 0
for _ in range(2000):
    a = rng.binomial(r_n, 0.29); b = rng.binomial(c_n, 0.046)
    pw += fisher_exact([[a, r_n - a], [b, c_n - b]], alternative="greater")[1] < 0.05
out["A1_round_vs_circ"] = {"round": [r_hit, r_n], "circ": [c_hit, c_n], "fisher_p": float(pA1), "power": pw / 2000}
out["A2_round_vs_rect_lenmatched"] = lm_test(list(ROUND.values()), pools["RECT"], isnum)
out["A2b_round_vs_sq_lenmatched"] = lm_test(list(ROUND.values()), pools["SQ"], isnum)
out["A_nonround_foreign_vs_sq"] = lm_test([s for i, s in ALL.items() if i not in ROUND], pools["SQ"], isnum)
out["round_ids_numeral_final"] = [i for i, s in ROUND.items() if isnum(s[-1])]

# B: M77 readings
bridge = json.load(open(ROOT / "sources/shaunmortal_indus/data/bridge_WM.json"))
M2W = {}
for w, v in bridge.items():
    for m in v["M"]:
        M2W.setdefault(f"M{m}", f"W{int(w):03d}")


def m77_final_isnum(i):
    s = [x for x in fc[i]["seq_m77"].split("-") if x and x not in ("#", "|", "?")]
    if not s:
        return None
    w = M2W.get(s[-1])
    return bool(w and isnum(w)), s[-1]


def b_texts(D):
    texts, agree = [], []
    for i, s in D.items():
        r = m77_final_isnum(i) if fc[i]["seq_m77"] else None
        if r is None:
            texts.append(s); continue
        flag, last = r
        agree.append((i, isnum(s[-1]), flag, last))
        texts.append(s[:-1] + (("W004",) if flag else ("W999",)))  # same length, outcome from M77 reading
    return texts, agree


tB, agB = b_texts(ALL)
out["B_ALL_m77"] = lm_test(tB, pools["SQ"], isnum)
out["B_SEC_m77"] = lm_test(b_texts(SEC)[0], pools["SQ"], isnum)
out["B_disagreements"] = [a for a in agB if a[1] != a[2]]
out["B_n_compared"] = len(agB)

# C: count-only
out["C_ALL_count"] = lm_test(list(ALL.values()), pools["SQ"], iscount)
out["C_SEC_count"] = lm_test(list(SEC.values()), pools["SQ"], iscount)
out["C_foreign_final_numeral_signs"] = Counter(s[-1] for s in ALL.values() if isnum(s[-1])).most_common()
homesq_tok = Counter(); homesq_fin = Counter()
for s in pools["SQ"]:
    for x in s:
        homesq_tok[x] += 1
    homesq_fin[s[-1]] += 1
out["C_home_final_share_of_sign"] = {w: [homesq_fin[w], homesq_tok[w], round(homesq_fin[w] / max(1, homesq_tok[w]), 3)]
                                     for w, _ in out["C_foreign_final_numeral_signs"]}

# planted control
texts = list(ALL.values()); BL = bylen(pools["SQ"], isnum); lens = [len(t) for t in texts]
T0 = null(lens, BL)
hits = 0
for _ in range(1000):
    k = sum((isnum(t[-1]) if rng.random() >= 0.3 else True) for t in texts)
    hits += (T0 >= k).mean() < 0.05
out["planted_power_r0.3"] = hits / 1000

for k, v in out.items():
    print(k, v)
json.dump(out, open(HERE / "results.json", "w"), indent=1)
