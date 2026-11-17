"""Attack 5: Wells-grammar scores of the home circular/cylinder units, per unit, with corrected labels
(SEAL:R -> seal, as #22 NEW). Same CV construction as experiments/round_label_audit/d_gulf.py (read-only imports).
    PYTHONHASHSEED=0 .venv/bin/python -I experiments/redteam_round_format/grammar_check.py
"""
import json, sys
from pathlib import Path
from collections import defaultdict
import numpy as np
ROOT = Path(__file__).resolve().parents[2]; G = ROOT / "experiments/grammar"
sys.path[:0] = [str(G), str(ROOT)]
import glib  # noqa
_old = glib.icit_register
glib.icit_register = lambda tp: "seal" if tp == "SEAL:R" else _old(tp)
from glib import ClassBigram, KNBigram, m77_units, icit_devlike, family_folds  # noqa
from step1_classes_seeds import SEED_W  # noqa
from corpus.load import icit_texts  # noqa
CW = json.load(open(G / "classes_wells.json")); KW, ALPHAW = CW["K"], CW["alpha"]
RNG = np.random.default_rng(2026)
wl = icit_devlike(m77_units("heldout"))
native_seals = [u for u in wl if u["register"] == "seal"]
fo = family_folds(wl, 5, 0)
cvb, cvk = {}, {}
for f in range(5):
    tr = [u for u, q in zip(wl, fo) if q != f]
    gw = ClassBigram(KW, alpha=ALPHAW).fit(tr, init=SEED_W, restarts=5); kw = KNBigram().fit(tr)
    for u, q in zip(wl, fo):
        if q == f and u["register"] in ("seal", "round_seal"):
            a, n = gw.unit_logp(u); cvb[u["key"]] = (-a / n, n)
            a, n = kw.unit_logp(u); cvk[u["key"]] = (-a / n, n)
home_round = [u for u in wl if u["register"] == "round_seal" and u["key"] in cvb]
# ICIT ids for home SEAL:C/CY, to label units
NOT_SEALS = {"1387.1", "1388.1", "1388.2"}
idmap = defaultdict(list)
for t in icit_texts():
    if t["type"] in ("SEAL:C", "SEAL:CY"): idmap[t["site"]].append(t)
rows = []
for u in home_round:
    rows.append(dict(key=u["key"], site=u.get("site"), n=len(u["signs"]), grammar=round(cvb[u["key"]][0], 2), kn=round(cvk[u["key"]][0], 2)))
for r in rows: print(r)


def matched(units, scores, label, ndraw=10000):
    key = lambda u: (min(len(u["signs"]), 6), u["full"])
    byk = defaultdict(list)
    for u in native_seals:
        if u["key"] in scores: byk[key(u)].append(scores[u["key"]][0])
    byk = {k: np.array(v) for k, v in byk.items()}
    tb, keys = [], []
    for u in units:
        k = key(u)
        if k not in byk: k = (k[0], not k[1])
        tb.append(scores[u["key"]][0]); keys.append(k)
    obs = float(np.mean(tb)); draws = np.array([np.mean([RNG.choice(byk[k]) for k in keys]) for _ in range(ndraw)])
    p = (1 + (draws >= obs).sum()) / (ndraw + 1)
    out = dict(n=len(tb), bits=obs, matched=float(draws.mean()), diff=obs - float(draws.mean()), p=float(p))
    print(label, out); return out


R = {"units": rows}
R["all_grammar"] = matched(home_round, cvb, "all home round, grammar")
R["all_kn"] = matched(home_round, cvk, "all home round, glib KN")
json.dump(R, open(Path(__file__).resolve().parent / "grammar_check.json", "w"), indent=1)
# corrected set: drop the Harappa incised tablet (H-369) and units with <2 legible signs or broken repeats
DROP = {"W741 W390 W741 W031 W705 W033 W368", "W740", "W003 # # W003", "W140 #"}
corr = [u for u in home_round if u["key"] not in DROP]
R["corrected_grammar"] = matched(corr, cvb, "corrected home circular, grammar")
R["corrected_kn"] = matched(corr, cvk, "corrected home circular, glib KN")
json.dump(R, open(Path(__file__).resolve().parent / "grammar_check.json", "w"), indent=1)
