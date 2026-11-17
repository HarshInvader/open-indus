"""Corrected format control for headline #4 (context Q4 / redteam R4).
Home circular/cylinder seals = ICIT SEAL:C + SEAL:CY at Indus sites (not SEAL:R).
Scores every home text by 10-fold CV with the Q4 Kneser-Ney bigram (same code, imported read-only),
foreign texts by the model trained on all native texts, and compares:
  (1) home circular vs home square-or-rectangular seals (length-matched draws, as Q4)
  (2) foreign round vs home circular: difference of means, permutation p over group labels
  (3) bigram gain over unigram for each group
    PYTHONHASHSEED=0 .venv/bin/python -I experiments/round_label_audit/fmt_control.py
"""
import sys, json
from pathlib import Path
from collections import Counter
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "experiments/context"), str(ROOT)]
import q4_gulf as Q  # noqa  (main() not run)
from corpus.load import icit_texts  # noqa

Q.rng = np.random.default_rng(4)
ROUND = ("SEAL:C", "SEAL:CY")
seen, native, foreign = set(), [], []
for t in icit_texts():
    s = Q.clean(t["seq"])
    if not s: continue
    site = t["site"]
    grp = "f" if site in Q.FOREIGN_WEST | Q.FOREIGN_CA else "u" if site == "Unknown" else "n"
    if grp == "u": continue
    fmt = "round" if t["type"] in ROUND else "seal" if t["type"].startswith("SEAL") else "other"
    k = (grp, " ".join(s))
    if k in seen: continue
    seen.add(k)
    (native if grp == "n" else foreign).append(dict(seq=s, site=site, fmt=fmt, type=t["type"], id=t["id"]))
fk = {" ".join(r["seq"]) for r in foreign}
native = [r for r in native if " ".join(r["seq"]) not in fk]
nt = [r["seq"] for r in native]
nb = Q.cv_bits(nt); nl = np.array([len(x) for x in nt])
M = Q.KN(nt)
fr = [r for r in foreign if r["fmt"] == "round"]
fb = np.array([M.bits(r["seq"]) for r in fr])
rd = np.array([r["fmt"] == "round" for r in native]); sq = np.array([r["fmt"] == "seal" for r in native])
R = {}
R["home_circular_vs_home_seals"] = Q.compare(nb[rd], nl[rd], nb[sq], nl[sq], "HOME circular/cyl vs home square+rect seals")
R["foreign_round_vs_home_seals"] = Q.compare(fb, [len(r["seq"]) for r in fr], nb[sq], nl[sq], "FOREIGN round vs home square+rect")

# (2) foreign round vs home circular, permutation of labels
hb = nb[rd]
obs = fb.mean() - hb.mean()
allb = np.concatenate([fb, hb]); nf = len(fb)
rng = np.random.default_rng(22)
perm = np.array([(lambda p: allb[p[:nf]].mean() - allb[p[nf:]].mean())(rng.permutation(len(allb))) for _ in range(20000)])
p2 = (1 + (np.abs(perm) >= abs(obs)).sum()) / (len(perm) + 1)
R["foreign_round_minus_home_circular"] = dict(n_foreign=nf, n_home=len(hb), foreign=float(fb.mean()), home=float(hb.mean()),
                                              diff=float(obs), p_two_sided=float(p2))
print(f"  FOREIGN round {fb.mean():.3f} (n={nf}) vs HOME circular {hb.mean():.3f} (n={len(hb)}): diff {obs:+.3f}, perm p={p2:.4f}")

# (3) bigram gain over unigram (Q4 decomposition formula)
cu = Counter(x for t in nt for x in t); tot = sum(cu.values()) + len(nt)
ubits = lambda t: -np.mean([np.log2((cu.get(x, 0) + 0.5) / (tot + 0.5 * len(cu))) for x in t] + [np.log2(len(nt) / tot)])
for name, texts, bits in (("foreign_round", [r["seq"] for r in fr], fb),
                          ("home_circular", [r["seq"] for r, z in zip(native, rd) if z], hb),
                          ("home_square_rect", [r["seq"] for r, z in zip(native, sq) if z], nb[sq])):
    g = np.array([ubits(t) for t in texts]) - np.asarray(bits)
    R[f"gain_{name}"] = dict(n=len(texts), bigram_gain=float(g.mean()))
    print(f"  bigram gain {name:18s} n={len(texts):4d} {g.mean():+.3f}")
R["home_circular_texts"] = [dict(id=r["id"], site=r["site"], type=r["type"], seq=" ".join(r["seq"]), bits=round(float(b), 2))
                            for r, b in zip([r for r, z in zip(native, rd) if z], hb)]
for x in R["home_circular_texts"]: print("   ", x)
# power: with n_home texts, chance a draw of real home-seal texts sits as high as foreign mean
json.dump(R, open(Path(__file__).resolve().parent / "fmt_control.json", "w"), indent=1)
