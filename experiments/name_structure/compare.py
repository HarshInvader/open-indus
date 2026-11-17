"""Board task #10: are foreign-found Indus texts structured like names / seal legends?
Pre-registered: docs/prereg/foreign_name_structure.md.  Run: .venv/bin/python -I experiments/name_structure/compare.py
"""
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "experiments/grammar"))
from glib import icit_units, FOREIGN  # noqa

rng = np.random.default_rng(20261117)
NREF, NPOW = 2000, 500


def cunei_signs(written):
    w = re.sub(r"\{[^}]*\}", "-", written)
    w = re.sub(r"[\[\]⸢⸣<>#!?*˹˺]", "", w).replace("_", "-")
    out = [p.lower() for p in re.split(r"[-.\s]+", w) if p]
    if not out or any(p in ("x", "...") for p in out):
        return None
    return tuple(out)


# ---------------- corpora
foreign = []
for r in csv.DictReader(open(ROOT / "experiments/foreign_corpus/foreign_corpus.csv")):
    if int(r["n_legible"]) < 2:
        continue
    s = tuple(x for x in r["seq_wells"].split("-") if x and x not in ("#", "|", "?"))
    if len(s) >= 2:
        foreign.append((r["id"], s))
F = [s for _, s in foreign]
n_f = len(F)

C = {}
legs = set()
for l in open(ROOT / "experiments/identifiers/data/ur3_occ.jsonl"):
    d = json.loads(l)
    s = cunei_signs(" ".join(w for line in d["legend"] for w in line))
    if s:
        legs.add(s)
C["C1 Ur III seal legends"] = sorted(legs)
by_lang = defaultdict(set)
for r in csv.DictReader(open(ROOT / "experiments/onomasticon/names.csv")):
    s = cunei_signs(r["written"])
    if s and len(s) >= 2:
        by_lang[r["language"]].add(s)
C["C2 Akkadian names"] = sorted(by_lang["Akkadian"])
C["C3 Amorite names"] = sorted(by_lang["Amorite"])
C["C4 Sumerian names"] = sorted(by_lang["Sumerian"])
home = set()
for u in icit_units(exclude_sites=FOREIGN | {"Unknown"}, types={"seal"}):
    s = tuple(x for x in u["signs"] if x not in ("#", "|"))
    if len(s) >= 2:
        home.add(s)
C["C5 Indus home seals"] = sorted(home)
BYLEN = {c: defaultdict(list) for c in C}
for c, texts in C.items():
    for t in texts:
        BYLEN[c][len(t)].append(t)


def draw(c, lengths):
    out = []
    for L in lengths:
        for d in (0, -1, 1, -2, 2, -3, 3, -4, 4):
            pool = BYLEN[c].get(L + d)
            if pool:
                out.append(pool[rng.integers(len(pool))]); break
    return out


def stats(texts):
    occ = Counter(s for t in texts for s in set(t))
    tok = [s for t in texts for s in t]
    s1 = np.mean([occ[s] == 1 for s in tok])
    s2 = np.mean([len(set(t)) < len(t) for t in texts])
    fin = Counter(t[-1] for t in texts); ini = Counter(t[0] for t in texts)
    s3 = np.mean([fin[t[-1]] > 1 for t in texts]); s4 = np.mean([ini[t[0]] > 1 for t in texts])
    return np.array([s1, s2, s3, s4, s3 - s4])


NAMES = ["S1 hapax-text share", "S2 texts with repeat", "S3 shared final", "S4 shared initial", "S5 final-initial"]
Lf = [len(t) for t in F]


def ref(c, lengths, k):
    return np.array([stats(draw(c, lengths)) for _ in range(k)])


def assign(obs, refs):
    D = {c: float(np.sqrt((((obs[:4] - R[:, :4].mean(0)) / R[:, :4].std(0)) ** 2).sum())) for c, R in refs.items()}
    return min(D, key=D.get), D


res = {"n_foreign": n_f, "comparator_sizes": {c: len(v) for c, v in C.items()},
       "foreign_length_dist": dict(sorted(Counter(Lf).items()))}
REF = {c: ref(c, Lf, NREF) for c in C}

# power (planted) at n = n_foreign and n = 30 (lengths resampled from the foreign length distribution)
power = {}
for n in (n_f, 30):
    lens = list(rng.choice(Lf, n)) if n != n_f else Lf
    refs = REF if n == n_f else {c: ref(c, lens, 1000) for c in C}
    conf = {}
    for c in C:
        hits = Counter(assign(stats(draw(c, lens)), refs)[0] for _ in range(NPOW))
        conf[c] = {k: v / NPOW for k, v in hits.items()}
    power[f"n={n}"] = {c: conf[c].get(c, 0.0) for c in C}
    power[f"n={n}_confusion"] = conf
res["power"] = power

obs = stats(F)
res["foreign_stats"] = dict(zip(NAMES, map(float, obs)))
cmp = {}
for c, R in REF.items():
    ps = [float(min(1, 2 * min((R[:, k] >= obs[k]).mean(), (R[:, k] <= obs[k]).mean()))) for k in range(5)]
    cmp[c] = {"mean": dict(zip(NAMES, map(lambda v: round(float(v), 3), R.mean(0)))),
              "p_two_sided": dict(zip(NAMES, ps)),
              "rejected(any S1-S4 p<0.0125)": any(p < 0.0125 for p in ps[:4])}
best, D = assign(obs, REF)
res["comparisons"] = cmp
res["D"] = D
ok_reject = not cmp[best]["rejected(any S1-S4 p<0.0125)"]
ok_power = power[f"n={n_f}"][best] >= 0.8
res["nearest"] = best
res["assignment"] = best if ok_reject and ok_power else (
    f"undecided (nearest {best}; " + ("rejected" if not ok_reject else "") + (" low power" if not ok_power else "") + ")")

# ---------------- descriptive: person/number positions and final-slot signs
def wn(s):
    m = re.fullmatch(r"W(\d+)", s)
    return int(m.group(1)) if m else None


def cls(s):
    n = wn(s)
    if n is None: return "other"
    if 1 <= n <= 59: return "number"
    if 90 <= n <= 175: return "person"
    return "other"


def posprof(texts):
    d = defaultdict(Counter)
    for t in texts:
        for i, s in enumerate(t):
            pos = "initial" if i == 0 else ("final" if i == len(t) - 1 else "interior")
            d[cls(s)][pos] += 1
    return {k: dict(v) for k, v in d.items()}


res["position_profile_foreign"] = posprof(F)
res["position_profile_home"] = posprof(C["C5 Indus home seals"])
fin = Counter(t[-1] for t in F)
hfin = Counter(t[-1] for t in C["C5 Indus home seals"]); hall = Counter(s for t in C["C5 Indus home seals"] for s in t)
res["foreign_final_signs_recurring"] = {s: {"n_final_foreign": k, "home_final_share": round(hfin[s] / max(1, hall[s]), 3),
                                           "class": cls(s)} for s, k in fin.most_common() if k > 1}
ini = Counter(t[0] for t in F)
res["foreign_initial_signs_recurring"] = {s: {"n_initial_foreign": k, "class": cls(s)} for s, k in ini.most_common() if k > 1}
json.dump(res, open(HERE / "results.json", "w"), indent=1, default=float)
print(json.dumps(res, indent=1, default=float))
