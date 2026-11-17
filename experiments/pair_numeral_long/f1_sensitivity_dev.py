"""F1 sensitivity (dev only): does the core definition hide a two-inventory split?
(a) loose cores (typology 'loose': N, F, numerals, units, titles kept), (b) all adjacent non-numeral pairs in whole
texts (includes openers/closers, i.e. text grammar), (c) references and simulations at held-out size (power)."""
import json
import numpy as np
from collections import Counter
from common import *
import corpora as TY, fr

rng = np.random.default_rng(5)
R = {}
dev, ho = dev_heldout()
devkeys = {tuple(t["seq"]) for t in dev}

# (a) loose cores
bt = TY.indus_cores_by_text(loose=True)
pa = Counter()
for k, cores in bt.items():
    if k not in devkeys: continue
    for c in set(cores):
        for a, b in set(zip(c, c[1:])):
            pa[(a, b)] += 1
R["loose_cores"] = graph_stats(list(pa), rng, nnull=200)
# (b) whole-text adjacent pairs, numerals removed
num = set(fr.SHORT) | set(fr.TALL)
pb = Counter()
for t in dev:
    s = set()
    for r in runs(t["seq"]):
        r = [x for x in r if x not in num]
        s |= set(zip(r, r[1:]))
    for e in s: pb[e] += 1
R["whole_text"] = graph_stats(list(pb), rng, nnull=200)
# (b2) whole-text minus lexicon openers/connectives/closers/clitics (roles O,C,J,P,B,I)
lex = {s: v for s, v in fr.HAND.items()}
strip = {s for s, v in lex.items() if set(v[0]) <= set("OCJPBIUST")}
pc = Counter()
for t in dev:
    s = set()
    for r in runs(t["seq"]):
        r = [x for x in r if x not in num and x not in strip]
        s |= set(zip(r, r[1:]))
    for e in s: pc[e] += 1
R["whole_text_minus_hand_function_signs"] = graph_stats(list(pc), rng, nnull=200)
for k in ("loose_cores", "whole_text", "whole_text_minus_hand_function_signs"):
    s = R[k]
    print(f"{k:40s} E={s['n_edges']} POL {s['pol']:.3f} ex {s['pol_excess']:+.3f} p={s['pol_p']:.3f} both {s['both']:.2f} "
          f"DICUT ex {s['dicut_excess']:+.3f} MAXCUT ex {s['maxcut_excess']:+.3f} p={s['maxcut_p']:.3f}")

# (c) references at held-out size (365 types)
N = 365
R["refs_at_heldout_n"] = {}
for nm in ("chinese_clan", "chinese_given", "sanskrit", "ur3"):
    P = ref_pairs(nm); vals = []
    for rep in range(20):
        idx = rng.choice(len(P), N, replace=False); sub = [P[k] for k in idx]
        p = polarization(sub); pn = np.mean([polarization(orient_null(sub, rng)) for _ in range(50)])
        vals.append((p - pn) / (1 - pn))
    R["refs_at_heldout_n"][nm] = [float(np.min(vals)), float(np.mean(vals)), float(np.max(vals))]
    print(f"ref {nm:14s} at n={N}: POL excess min/mean/max {np.min(vals):+.3f} {np.mean(vals):+.3f} {np.max(vals):+.3f}")
for kind, q in (("compound", 0), ("mix", 0.25), ("mix", 0.5)):
    vals = []
    for rep in range(20):
        sub = sim_pairs(kind, N, rng, q)
        p = polarization(sub); pn = np.mean([polarization(orient_null(sub, rng)) for _ in range(50)])
        vals.append((p - pn) / (1 - pn))
    nm = kind if kind != "mix" else f"mix_q{q}"
    R["refs_at_heldout_n"]["sim_" + nm] = [float(np.min(vals)), float(np.mean(vals)), float(np.max(vals))]
    print(f"sim {nm:14s} at n={N}: POL excess min/mean/max {np.min(vals):+.3f} {np.mean(vals):+.3f} {np.max(vals):+.3f}")
json.dump(R, open(HERE / "f1_sensitivity_dev.json", "w"), indent=1, default=float)
