"""Design step (DEV ONLY). Start from the strict template (opener first, connective only after an
opener, closers/clitics only at the end, numerals before a head) and greedily add single transitions
that most increase  coverage(real) - coverage(within-text shuffled)  in 5-fold CV inside dev.
Stops when no edge improves the margin by >= 0.005. Held-out is not touched."""
import random, json
import numpy as np
from fr import *

rng = random.Random(1)
dev, ho = dev_heldout()
dev = [t for t in dev if t["site"] != "West Asian finds"]
idx = list(range(len(dev))); rng.shuffle(idx)
folds = [idx[i::5] for i in range(5)]


def shuffled(t, rng):
    seq = list(t["seq"])
    pos = [i for i, s in enumerate(seq) if s not in ("|", "#")]
    vals = [seq[i] for i in pos]; rng.shuffle(vals)
    for i, v in zip(pos, vals): seq[i] = v
    return dict(t, seq=seq)


FOLD = []
for f in range(5):
    fs = set(folds[f])
    test = [dev[i] for i in folds[f] if not has_break(dev[i]) and sum(1 for s in dev[i]["seq"] if s not in "|#") >= 2]
    train = [dev[i] for i in idx if i not in fs]
    r2 = random.Random(f)
    FOLD.append((build_lexicon(train), train, test, [[shuffled(t, r2) for _ in range(3)] for t in test]))


def evaluate(extra):
    real = []; sh = []
    for lex, train, test, shs in FOLD:
        G = Grammar(lex, "final", extra=extra).fit(train, iters=5)
        for t, ss in zip(test, shs):
            real.append(G.accepts(t)); sh.append(np.mean([G.accepts(x) for x in ss]))
    return float(np.mean(real)), float(np.mean(sh))


base = allowed_matrix("strict")
cands = [(a, b) for a in ROLES for b in ROLES + ["$"] if b not in base[a]]
cur = []
r, s = evaluate(cur); log = [dict(edges=[], real=r, shuf=s, margin=r - s)]
print("strict", r, s, r - s)
while True:
    best = None
    for e in cands:
        if e in cur: continue
        r2, s2 = evaluate(cur + [e])
        if best is None or (r2 - s2) > best[1]:
            best = (e, r2 - s2, r2, s2)
    if best[1] < log[-1]["margin"] + 0.005:
        break
    cur.append(best[0]); log.append(dict(edges=list(cur), real=best[2], shuf=best[3], margin=best[1]))
    print("add", best[0], "real %.3f shuf %.3f margin %.3f" % (best[2], best[3], best[1]))
json.dump(dict(steps=log, frozen=cur), open(OUT / "g1_design_dev.json", "w"), indent=1)
print("FROZEN", cur)
