"""Per-text 'non-Indus order' flag for foreign_corpus.csv, as pre-registered in docs/prereg/foreign_corpus.md.

Run: .venv/bin/python -I experiments/foreign_corpus/score.py
Re-implements validate.py part (d) training (Wells grammar on icit_devlike(m77 heldout), 5-fold CV native scores)
without importing validate.py (which runs the whole validation on import).
"""
import csv, json, sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import binomtest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
G = ROOT / "experiments/grammar"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(G))
from glib import (ClassBigram, KNBigram, m77_units, icit_devlike, family_folds, unit_from)  # noqa
from step1_classes_seeds import SEED_W  # noqa

CW = json.load(open(G / "classes_wells.json"))
KW, AW = CW["K"], CW["alpha"]
gram = lambda units: ClassBigram(KW, alpha=AW).fit(units, init=SEED_W, restarts=5)

wl = icit_devlike(m77_units("heldout"))
native = [u for u in wl if u["register"] == "seal"]
fo = family_folds(wl, 5, 0)
cvg, cvk = {}, {}
for f in range(5):
    tr = [u for u, q in zip(wl, fo) if q != f]
    g, k = gram(tr), KNBigram().fit(tr)
    for u, q in zip(wl, fo):
        if q == f and u["register"] == "seal":
            a, n = g.unit_logp(u); cvg[u["key"]] = -a / n
            a, n = k.unit_logp(u); cvk[u["key"]] = -a / n
GW, KB = gram(wl), KNBigram().fit(wl)


def pool(cv):
    by = defaultdict(list)
    for u in native:
        if u["key"] in cv:
            by[(min(len(u["signs"]), 6), u["full"])].append(cv[u["key"]])
    return {k: np.array(v) for k, v in by.items()}


PG, PK = pool(cvg), pool(cvk)
rows = list(csv.DictReader(open(HERE / "foreign_corpus.csv")))
out = []
for r in rows:
    seq = [s for s in r["seq_wells"].split("-") if s]
    seq = ["#" if s == "?" else s for s in seq]
    if int(r["n_legible"]) < 2 or r["note"].startswith("PICTORIAL"):
        out.append(dict(id=r["id"], scored=False)); continue
    complete = "#" not in seq
    u = unit_from(seq, complete)
    if max(len(x[0]) for x in u["runs"]) < 2:
        out.append(dict(id=r["id"], scored=False)); continue
    res = dict(id=r["id"], scored=True, region=r["region"], shape=r["shape"], conf=r["reading_confidence"], n=len(u["signs"]))
    for name, m, P in (("grammar", GW, PG), ("bigram", KB, PK)):
        a, n = m.unit_logp(u); b = -a / n
        key = (min(len(u["signs"]), 6), u["full"])
        ref = P.get(key, P.get((key[0], not key[1])))
        p = (1 + (ref >= b).sum()) / (len(ref) + 1)
        res[f"{name}_bits"] = round(float(b), 3); res[f"{name}_p"] = round(float(p), 4)
    p = res["grammar_p"]
    res["flag"] = "NON-INDUS ORDER" if p < 0.05 else ("BORDERLINE" if p < 0.20 else "INDUS-LIKE")
    out.append(res)

sc = [o for o in out if o["scored"]]
nflag = sum(o["flag"] == "NON-INDUS ORDER" for o in sc)
nflag_b = sum(o["bigram_p"] < 0.05 for o in sc)
summ = dict(n_objects=len(rows), n_scored=len(sc), n_non_indus=nflag, expected_false=0.05 * len(sc),
            binom_p=binomtest(nflag, len(sc), 0.05, alternative="greater").pvalue,
            n_non_indus_bigram=nflag_b, n_native_ref=sum(len(v) for v in PG.values()))
grp = defaultdict(lambda: [0, 0])
for o in sc:
    g = "round/cylinder" if any(w in o["shape"] for w in ("round", "cylinder", "button")) else (
        "square" if "square" in o["shape"] else "other")
    grp[g][0] += o["flag"] == "NON-INDUS ORDER"; grp[g][1] += 1
summ["by_shape"] = {k: f"{a}/{b}" for k, (a, b) in grp.items()}
print(json.dumps(summ, indent=1))
for o in sc:
    print(f"{o['id']:13s} n={o['n']} {o['shape'][:22]:22s} g={o['grammar_bits']:.2f} p={o['grammar_p']:.3f}  kn p={o['bigram_p']:.3f}  {o['flag']}")
with open(HERE / "order_flags.csv", "w", newline="") as f:
    keys = ["id", "scored", "region", "shape", "conf", "n", "grammar_bits", "grammar_p", "bigram_bits", "bigram_p", "flag"]
    w = csv.DictWriter(f, fieldnames=keys); w.writeheader()
    for o in out:
        w.writerow({k: o.get(k, "") for k in keys})
json.dump(dict(summary=summ, per_text=out), open(HERE / "results.json", "w"), indent=1, default=str)
