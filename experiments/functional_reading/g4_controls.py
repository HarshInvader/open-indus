"""Controls.
1. Planted answer: sample a synthetic corpus (same size, same role grammar, true role of every token known)
   from the fitted model, re-run the whole pipeline (hand lexicon for the same signs, positional induction
   for the rest, EM) on 75% and score role recovery and coverage on the other 25%.
2. Lexicon-permutation null on real data: shuffle the role sets among the hand-assigned signs (keeps how
   many signs have each role set), refit on dev, measure held-out coverage. If our evidence-based
   assignments carry information, the real lexicon should beat permuted ones.
"""
import json, random, copy
from collections import Counter
import numpy as np
import fr
from fr import *

rng = np.random.default_rng(11); prng = random.Random(11)
dev, ho, dev_g, lex, comps, G = load_model()
R = {}

# ---------------------------------------------------------------- 1. planted answer
K = len(ROLES)
signs = sorted({s for (s, r) in G.ecount})
E = np.zeros((K, len(signs)))
for (s, r), c in G.ecount.items():
    E[RI[r], signs.index(s)] += c
E /= E.sum(1, keepdims=True) + 1e-12


def sample_text():
    while True:
        k = rng.choice(K, p=G.start); seq, roles = [], []
        for _ in range(20):
            if E[k].sum() == 0: break
            seq.append(signs[rng.choice(len(signs), p=E[k])]); roles.append(ROLES[k])
            p = np.append(G.trans[k], G.end[k]); p /= p.sum()
            nk = rng.choice(K + 1, p=p)
            if nk == K: return seq, roles
            k = nk


syn = []; keys = set()
while len(syn) < len(dev_g) + len(ho):
    s, r = sample_text()
    if " ".join(s) in keys: continue
    keys.add(" ".join(s)); syn.append(dict(seq=s, roles=r, site="syn"))
cut = int(0.75 * len(syn)); sdev, sho = syn[:cut], syn[cut:]
slex = build_lexicon(sdev)
SG = Grammar(slex, "final").fit(sdev)
acc = Counter(); tot = Counter(); cov = []
for t in sho:
    p = SG.viterbi(t["seq"])
    cov.append(p is not None)
    if p is None: continue
    for s, pr, tr in zip(t["seq"], p, t["roles"]):
        grp = "hand" if s in HAND else "induced" if slex.get(s, {}).get("source") == "dev-positional" and slex[s]["grade"] == "C" else "default-N"
        tot[grp] += 1; acc[grp] += (pr == tr)
        tot["all"] += 1; acc["all"] += (pr == tr)
shuf_cov = []
for t in sho:
    s = list(t["seq"]); prng.shuffle(s); shuf_cov.append(SG.viterbi(s) is not None)
# role-set recovery for induced signs: does the induced role set contain the sign's majority true role?
true_major = {}
cnt = Counter((s, r) for t in sdev for s, r in zip(t["seq"], t["roles"]))
for s in {s for (s, r) in cnt}:
    true_major[s] = max((r for (x, r) in cnt if x == s), key=lambda r: cnt[(s, r)])
ind = [s for s, e in slex.items() if e["source"] == "dev-positional" and e["grade"] == "C"]
rec = np.mean([true_major[s] in slex[s]["roles"] for s in ind]) if ind else float("nan")
R["planted"] = dict(n_dev=len(sdev), n_test=len(sho), coverage=float(np.mean(cov)), shuffled_coverage=float(np.mean(shuf_cov)),
                    token_role_accuracy={k: acc[k] / tot[k] for k in tot}, token_counts=dict(tot),
                    induced_signs=len(ind), induced_roleset_contains_true_major=float(rec))
print("planted:", json.dumps(R["planted"], indent=1))

# ---------------------------------------------------------------- 2. lexicon-permutation null (real data)
def held_cov(Gx):
    ts = [t for t in ho if t["site"] != "West Asian finds" and not has_break(t) and sum(1 for s in t["seq"] if s not in "|#") >= 2]
    return float(np.mean([Gx.accepts(t) for t in ts]))


real_cov = held_cov(G)
hand_signs = [s for s in HAND if any(s == x for t in dev_g for x in t["seq"])]
orig = {s: HAND[s] for s in hand_signs}
null = []
for b in range(200):
    perm = list(orig.values()); prng.shuffle(perm)
    saved = dict(fr.HAND)
    for s, v in zip(orig, perm):
        fr.HAND[s] = (v[0],) + orig[s][1:]
    lx = fr.build_lexicon(dev_g)
    Gx = fr.Grammar(lx, "final").fit(dev_g, iters=8)
    null.append(held_cov(Gx))
    fr.HAND.clear(); fr.HAND.update(saved)
R["lexicon_permutation_null"] = dict(real_heldout_coverage=real_cov, null_mean=float(np.mean(null)), null_sd=float(np.std(null)),
                                     null_max=float(np.max(null)), p=float((np.sum(np.array(null) >= real_cov) + 1) / (len(null) + 1)))
print("lexicon permutation null:", R["lexicon_permutation_null"])
json.dump(R, open(OUT / "g4_controls.json", "w"), indent=1)
