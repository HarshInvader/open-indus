"""R1a diagnostic (NOT pre-registered, added after seeing that the 'other' residual depends on trigram lambda):
calibrate the trigram weight on a target the red team already accepted as pure grammar collisions,
objects on repeated 1-3 sign seal texts (observed 145; redteam_identifiers C1b), then read off the 4-5 band.
usage: .venv/bin/python experiments/redteam_local_repeats/r1_calib.py [nsim]
"""
import sys, os, json
from collections import Counter
import numpy as np
NSIM = int(sys.argv[1]) if len(sys.argv) > 1 else 100
sys.argv = sys.argv[:1] + ["10"]
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from rlib import *  # noqa
import c1, lr  # noqa

rng = np.random.default_rng(99)
T = [o["text"] for o in lr.SEALS]; L = [len(t) for t in T]
D_all = c1.distinct_corpus(c1.ALL); V = sorted({s for t in D_all for s in t})
seal45 = {t for t in T if 4 <= len(t) <= 5}; D_lo = [t for t in D_all if t not in seal45]


def st(TT):
    c = Counter(TT); rep = [t for t, k in c.items() if k > 1]
    return dict(rep13=sum(c[t] for t in rep if len(t) <= 3), rep45=sum(c[t] for t in rep if 4 <= len(t) <= 5),
                rep45_other=sum(c[t] for t in rep if 4 <= len(t) <= 5 and not is_formula(t)), rep6=sum(c[t] for t in rep if len(t) >= 6))


obs = st(T); out = {"observed": obs}; print("obs", obs)
g = c1.Bigram(D_all, V); g.prepare(max(L))
mods = {"N2": g}
for l3 in (0.3, 0.4, 0.5, 0.6, 0.7):
    mods["TRI-A_l%d" % int(l3 * 100)] = Trigram(D_all, V, (l3, (1 - l3) * 0.75, (1 - l3) * 0.25))
    mods["TRI-L_l%d" % int(l3 * 100)] = Trigram(D_lo, V, (l3, (1 - l3) * 0.75, (1 - l3) * 0.25))
for k, m in mods.items():
    S = [st(m.sample(L, rng)) for _ in range(NSIM)]
    out[k] = {kk: summ([s[kk] for s in S], obs[kk]) for kk in obs}
    print(k, {kk: "%.1f [%.0f-%.0f] p=%.3f" % (v["mean"], v["lo"], v["hi"], v["p_ge"]) for kk, v in out[k].items()}, flush=True)
json.dump(out, open(os.path.join(HERE, "r1_calib.json"), "w"), indent=1)
