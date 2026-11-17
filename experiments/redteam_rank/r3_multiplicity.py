"""Step 3: attack 5 (multiple testing / selection) with analytic within-strata permutation z.
(a) screen every sign with >=15 carrier texts: how special are W590 / W70x?
(b) 300 random family re-splits: rerun the dev selection rule on the 25 prereg frame features
    (two-sided p<0.01 on dev), test the picked group on held-out.
"""
import sys, json, collections as C
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import numpy as np
from scipy.stats import norm
from data import build, families, split, FEATS
from stats import strata_key

T = build()
fam = families(T)
keys = [strata_key(t, "base") for t in T]
y = np.array([t["la"] for t in T])

FRAME = {"W817": {"W817"}, "W861": {"W861"}, "W820": {"W820"}, "W920": {"W920"}, "W002": {"W002"},
         "W060": {"W060"}, "W760": {"W760"}, "W100": {"W100"}, "W176": {"W176"}, "W70x": FEATS["W70x"],
         "W033": {"W033"}, "W255": {"W255"}, "W590": {"W590"}, "W741": {"W741"}, "W740": {"W740"},
         "W520": {"W520"}, "W390": {"W390"}, "W405": {"W405"}, "W407": {"W407"}, "W527": {"W527"},
         "W368": {"W368"}, "W151": {"W151"}, "W154/156": {"W154", "W156"}, "W400": {"W400"}, "W090": {"W090"}}


def zscore(mask, x):
    idx = np.where(mask)[0]
    g = C.defaultdict(list)
    for i in idx:
        g[keys[i]].append(i)
    num = var = 0.0; n = 0
    for k, ii in g.items():
        ii = np.array(ii); m = x[ii].sum(); N = len(ii)
        if N < 2 or m == 0 or m == N:
            continue
        r = y[ii] - y[ii].mean()
        num += (r * x[ii]).sum(); var += m * (N - m) / (N * (N - 1)) * (r ** 2).sum(); n += m
    return (num / np.sqrt(var) if var > 0 else 0.0), n


# (a) screen all signs
cnt = C.Counter(s for t in T for s in set(t["signs"]))
cands = [s for s, c in cnt.items() if c >= 15]
allm = np.ones(len(T), bool)
screen = []
for s in cands:
    x = np.array([s in t["signs"] for t in T], float)
    z, n = zscore(allm, x)
    screen.append((s, n, z))
x = np.array([t["W70x"] for t in T], float); z, n = zscore(allm, x); screen.append(("W70x", n, z))
screen.sort(key=lambda r: -abs(r[2]))
zs = np.array([r[2] for r in screen])
print(f"(a) {len(screen)} signs with >=15 texts. |z|>2.58: {np.sum(abs(zs) > 2.58)} (expected {0.01 * len(zs):.1f}); |z|>3.29: {np.sum(abs(zs) > 3.29)}")
print("    sd of z across signs: %.2f (1.0 under null)" % zs.std())
rank = {r[0]: i + 1 for i, r in enumerate(screen)}
print("    top 12:", [(s, n, round(z, 2)) for s, n, z in screen[:12]])
print("    rank W590:", rank.get("W590"), " W70x:", rank.get("W70x"))
# Bonferroni over the full screen
bonf = {s: min(1, 2 * norm.sf(abs(z)) * len(screen)) for s, n, z in screen}
print("    Bonferroni p over full screen: W590 %.4f, W70x %.4f" % (bonf["W590"], bonf["W70x"]))

# (b) re-splits
NS = 300
sel_count = C.Counter(); rep_count = C.Counter(); Sp = []; npicked = []
for seed in range(NS):
    ho = split(T, fam, seed=1000 + seed)
    picks = {}
    for f, ss in FRAME.items():
        x = np.array([any(s in ss for s in t["signs"]) for t in T], float)
        z, n = zscore(~ho, x)
        if 2 * norm.sf(abs(z)) < 0.01:
            picks[f] = np.sign(z)
    npicked.append(len(picks))
    if not picks:
        Sp.append(1.0); continue
    zsum = 0.0
    for f, sg in picks.items():
        x = np.array([any(s in FRAME[f] for s in t["signs"]) for t in T], float)
        z, n = zscore(ho, x)
        zsum += sg * z
        sel_count[f] += 1
        if sg * z > 1.645:
            rep_count[f] += 1
    S = zsum / np.sqrt(len(picks)); Sp.append(norm.sf(S))
Sp = np.array(Sp)
print(f"\n(b) {NS} random family splits: mean #picked {np.mean(npicked):.1f}; group replicates (p<0.05) in {np.mean(Sp < 0.05):.0%}; p<0.001 in {np.mean(Sp < 0.001):.0%}")
print("    selection / one-sided held-out replication rate per sign:")
for f, c in sel_count.most_common(12):
    print(f"      {f}: picked {c}/{NS}, replicated {rep_count[f]}/{c}")
json.dump(dict(screen=[dict(sign=s, n=n, z=z) for s, n, z in screen], n_screen=len(screen),
               n_abs_z_gt_2_58=int(np.sum(abs(zs) > 2.58)), sd_z=float(zs.std()),
               rank_W590=rank.get("W590"), rank_W70x=rank.get("W70x"), bonf_W590=bonf["W590"], bonf_W70x=bonf["W70x"],
               resplit=dict(n=NS, frac_group_p05=float(np.mean(Sp < 0.05)), frac_group_p001=float(np.mean(Sp < 0.001)),
                            mean_picked=float(np.mean(npicked)),
                            per_sign={f: dict(picked=c, replicated=rep_count[f]) for f, c in sel_count.items()})),
          open("experiments/redteam_rank/r3.json", "w"), indent=1)
