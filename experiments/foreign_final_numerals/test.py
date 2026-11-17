"""Board #15: are foreign-found Indus texts numeral-final more often than length-matched home seals?
Pre-registered: docs/prereg/foreign_final_numerals.md
Run: .venv/bin/python -I experiments/foreign_final_numerals/test.py
"""
import csv, json, sys
from collections import defaultdict
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "experiments/grammar"))
from glib import icit_units, FOREIGN  # noqa

rng = np.random.default_rng(1517)
NDRAW, NPOW = 20000, 2000


def isnum(s):
    return s.startswith("W") and s[1:].isdigit() and 1 <= int(s[1:]) <= 59


def clean(seq):
    return tuple(x for x in seq.split("-") if x and x not in ("#", "|", "?"))


fc = {r["id"]: r for r in csv.DictReader(open(ROOT / "experiments/foreign_corpus/foreign_corpus.csv"))}
rc = {r["id"]: r for r in csv.DictReader(open(ROOT / "experiments/foreign_readings/readings_check.csv"))}
SURV = {"UR-01", "GIRSU-02", "BAHRAIN-01", "BAHRAIN-06", "BAHRAIN-07", "UNPROV-02", "UNPROV-03", "UNPROV-07", "SALUT-01"}


def seq_of(i):
    r = fc[i]
    s = clean(r["seq_wells"])
    if len(s) < 2 and i == "UNPROV-02":           # row has a shifted column; Wells reading sits in seq_m77 slot
        s = clean(r["seq_m77"])
    return s


home = set()
for u in icit_units(exclude_sites=FOREIGN | {"Unknown"}, types={"seal"}):
    s = tuple(x for x in u["signs"] if x not in ("#", "|"))
    if len(s) >= 2:
        home.add(s)
BYLEN = defaultdict(list)
for s in home:
    BYLEN[len(s)].append(isnum(s[-1]))
BYLEN = {L: np.array(v) for L, v in BYLEN.items()}


def pool(L):
    if len(BYLEN.get(L, [])) >= 30:
        return BYLEN[L]
    return np.concatenate([BYLEN.get(k, np.array([], bool)) for k in (L - 1, L, L + 1)])


def null(lengths, n=NDRAW):
    T = np.zeros(n, int)
    for L in lengths:
        P = pool(L)
        T += P[rng.integers(0, len(P), n)]
    return T


def test(texts):
    obs = sum(isnum(t[-1]) for t in texts)
    T = null([len(t) for t in texts])
    return obs, float(T.mean()), float((T >= obs).mean())


def sets(direction_flip):
    prim, sec = [], []
    for i, r in rc.items():
        u = r["use_in_crib_attack"]
        if not (u.startswith("yes") or u.startswith("sensitivity")) or i not in fc:
            continue
        s = seq_of(i)
        if len(s) < 2:
            continue
        if direction_flip and i in ("SUSA-02", "BAHRAIN-01"):
            s = s[::-1]
        (prim if u.startswith("yes") else sec).append((i, s))
    return prim, prim + sec


out = {"home_texts": len(home), "home_final_numeral_rate": float(np.mean([isnum(s[-1]) for s in home]))}
for flip in (False, True):
    prim, sec = sets(flip)
    tag = "reversed" if flip else "as_read"
    for name, S in (("primary", prim), ("secondary", sec)):
        obs, mu, p = test([s for _, s in S])
        loo = max(test([s for j, s in S if j != i])[2] for i, _ in S)
        out[f"{name}_{tag}"] = {"n": len(S), "obs": obs, "null_mean": round(mu, 2), "p": p, "loo_max_p": loo,
                                "numeral_final_ids": [i for i, s in S if isnum(s[-1])]}
        print(name, tag, out[f"{name}_{tag}"])

# descriptive: whole foreign corpus (as #10)
allf = [(i, clean(r["seq_wells"])) for i, r in fc.items() if r["n_legible"].isdigit() and int(r["n_legible"]) >= 2]
allf = [(i, s) for i, s in allf if len(s) >= 2]
obs, mu, p = test([s for _, s in allf])
out["descriptive_all"] = {"n": len(allf), "obs": obs, "null_mean": round(mu, 2), "p": p,
                          "numeral_final_ids": [i for i, s in allf if isnum(s[-1])]}
sv = [s for i, s in allf if i in SURV]; rest = [s for i, s in allf if i not in SURV]
out["survivors_rate"] = [sum(isnum(s[-1]) for s in sv), len(sv)]
out["rest_rate"] = [sum(isnum(s[-1]) for s in rest), len(rest)]
print("descriptive", out["descriptive_all"], "survivors", out["survivors_rate"], "rest", out["rest_rate"])

# power for the primary set lengths
prim, _ = sets(False)
lens = [len(s) for _, s in prim]
crit_T = null(lens, 20000)
crit = int(np.quantile(crit_T, 0.95)) + 1  # smallest T with p < ~0.05
while (crit_T >= crit).mean() > 0.05:
    crit += 1
out["primary_critical_T"] = crit
for r in (0.2, 0.3, 0.5):
    hits = (rng.random((NPOW, len(lens))) < r).sum(1) >= crit
    out[f"power_primary_r{r}"] = float(hits.mean())
for r in (0.2, 0.3):
    _, S = sets(False)
    l2 = [len(s) for _, s in S]; T2 = null(l2, 20000); c2 = 0
    while (T2 >= c2).mean() > 0.05:
        c2 += 1
    out[f"power_secondary_r{r}"] = float(((rng.random((NPOW, len(l2))) < r).sum(1) >= c2).mean())
print({k: v for k, v in out.items() if k.startswith("power") or k.startswith("home") or "critical" in k})
json.dump(out, open(HERE / "results.json", "w"), indent=1)
