"""Re-test the red team's defensible claims on the family split (splits_v2, zero near-copy leakage).
Run: .venv/bin/python experiments/revalidation/revalidate.py
Each claim is fixed in advance from experiments/redteam/RESULTS.md; this script only re-measures."""
import sys, json, math, random, itertools
from collections import Counter, defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from corpus.load import dev_heldout, runs

rng = random.Random(7)
dev, ho = dev_heldout(version=2)
out = {"split": "v2", "n_dev": len(dev), "n_heldout": len(ho)}
R = lambda ts: [r for t in ts for r in runs(t["seq"])]

# ---------- 1. order beats permutations (bigram trained on dev) ----------
import time; print("section: 1. order beats permutations (bigram trained on dev)", time.strftime("%X"), flush=True)
uni, big = Counter(), Counter()
for r in R(dev):
    seq = ["<s>"] + r + ["</s>"]
    uni.update(seq[:-1]); big.update(zip(seq, seq[1:]))
V = len(uni) + 1
def lp(r):
    seq = ["<s>"] + r + ["</s>"]
    return sum(math.log((big[(a, b)] + 0.1) / (uni[a] + 0.1 * V)) for a, b in zip(seq, seq[1:]))
best = chance = n = 0
for t in ho:
    if not t["complete"]: continue
    for r in runs(t["seq"]):
        if not (3 <= len(r) <= 7): continue
        perms = set(itertools.permutations(r))
        if len(perms) < 6: continue
        s0 = lp(r)
        best += all(lp(list(p)) < s0 for p in perms if list(p) != r)
        chance += 1 / len(perms); n += 1
out["order"] = dict(n_runs=n, true_order_strictly_best=best / n, chance=chance / n)

# ---------- 2. ticked fish take the final slot ----------
import time; print("section: 2. ticked fish take the final slot", time.strftime("%X"), flush=True)
TICK = ["M60", "M66", "M68", "M71", "M73"]; PLAIN = ["M59", "M65", "M67", "M70", "M72"]
def final_share(ts, signs):
    tot = fin = 0
    for t in ts:
        for r in runs(t["seq"]):
            for i, s in enumerate(r):
                if s in signs and len(r) > 1:
                    tot += 1; fin += (i == len(r) - 1)
    return fin, tot
f, tt = final_share(ho, TICK); fp, tp = final_share(ho, PLAIN)
# null: frequency-matched non-closer signs drawn from dev frequency band
freq = Counter(s for r in R(dev) for s in r)
band = [s for s in freq if 10 <= freq[s] <= 80 and s not in TICK + PLAIN]
null = []
for _ in range(2000):
    pick = rng.sample(band, 5); a, b = final_share(ho, pick)
    if b: null.append(a / b)
out["ticked_fish"] = dict(final=f, tokens=tt, share=f / max(tt, 1), plain_share=fp / max(tp, 1),
                          null_mean=float(np.mean(null)), p=float(np.mean([x >= f / max(tt, 1) for x in null])))

# ---------- 3. two-tier six M109 followed by fish M59 ----------
import time; print("section: 3. two-tier six M109 followed by fish M59", time.strftime("%X"), flush=True)
def foll(ts, a):
    c = Counter()
    for r in R(ts):
        for x, y in zip(r, r[1:]):
            if x == a: c[y] += 1
    return c
c = foll(ho, "M109"); base = sum(1 for r in R(dev) for s in r if s == "M59") / sum(len(r) for r in R(dev))
k, N = c["M59"], sum(c.values())
from scipy.stats import binomtest
out["six_fish"] = dict(M109_tokens_with_follower=N, followed_by_M59=k, base_rate=base,
                       p=binomtest(k, N, base, alternative="greater").pvalue if N else None)

# ---------- 4. object-type registers: text predicts object type ----------
import time; print("section: 4. object-type registers: text predicts object type", time.strftime("%X"), flush=True)
types = ["seal", "sealing", "miniature tablet", "copper tablet", "pottery graffito"]
def XY(ts):
    X = [Counter(s for s in t["seq"] if s not in "|#") for t in ts if t["object_type"] in types]
    y = [t["object_type"] for t in ts if t["object_type"] in types]
    return X, y
Xd, yd = XY(dev); Xh, yh = XY(ho)
vocab = sorted({s for x in Xd for s in x}); idx = {s: i for i, s in enumerate(vocab)}
def M(X):
    A = np.zeros((len(X), len(vocab)))
    for i, x in enumerate(X):
        for s, v in x.items():
            if s in idx: A[i, idx[s]] = 1
    return A
clf = LogisticRegression(max_iter=3000, C=0.5, class_weight="balanced").fit(M(Xd), yd)
P = clf.predict_proba(M(Xh)); aucs = {}
for j, cl in enumerate(clf.classes_):
    yy = np.array([y == cl for y in yh])
    if 3 <= yy.sum() < len(yy):
        obs = roc_auc_score(yy, P[:, j])
        nul = [roc_auc_score(rng.sample(list(yy), len(yy)), P[:, j]) for _ in range(500)]
        aucs[cl] = dict(n=int(yy.sum()), auc=round(obs, 3), null95=round(float(np.quantile(nul, .95)), 3))
out["registers"] = aucs

json.dump(out, open(Path(__file__).parent / "results.json", "w"), indent=1)
print(json.dumps(out, indent=1))
