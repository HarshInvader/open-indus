"""Exploratory pass on the DISCOVERY data only (ICIT half A; M77 dev).
Usage: .venv/bin/python experiments/toponyms/explore.py [icit|m77]
"""
import sys
from common import *

which = sys.argv[1] if len(sys.argv) > 1 else "icit"
U = icit_split()["A"] if which == "icit" else m77_units("dev")
ensure_families(U)
E = collapse(U, "enrich")
T = collapse(U, "travel")
MIN = {1: 5, 2: 4, 3: 4}
feats, X = feature_matrix(E, MIN)
print(which, "units", len(U), "site-families", len(E), "features", len(feats))
sites, obs, exp, p = enrichment(E, X, R=2000)
rows = []
for j, f in enumerate(feats):
    for i, s in enumerate(sites):
        if obs[i, j] >= 3 and exp[i, j] > 0:
            rows.append((p[i, j], f, s, int(obs[i, j]), exp[i, j], int(X[:, j].sum())))
rows.sort()
allp = [r[0] for r in rows]
q = bh(allp)
print("tests", len(rows), "p<0.01:", sum(x < 0.01 for x in allp), "q<0.1:", sum(q < 0.1))
for (pp, f, s, o, e, n), qq in list(zip(rows, q))[:40]:
    print(f"{f:22s} {s:14s} obs {o:3d} exp {e:6.2f} ratio {o/e:5.2f} tot {n:3d} p {pp:.4f} q {qq:.3f}")

cands = [(f, s) for (pp, f, s, o, e, n) in rows if pp < 0.01 and o / e >= 2 and s not in ("Other sites", "West Asian finds")]
print("\ncandidates (p<0.01, ratio>=2):", len(cands))
for mobile in ("primary", "broad"):
    r = travel_test(T, cands, MOBILE[mobile], R=5000)
    print(mobile, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items() if k != "per_cand"})
    if mobile == "primary":
        for c in r["per_cand"]:
            print("   ", c)

featsT, XT = feature_matrix(T, MIN)
hits = reverse_count(T, XT, featsT)
print("\nreverse hits (seal at one site only, sealing elsewhere):", len(hits))
for h in hits:
    print("   ", h)

if which == "icit":
    print("\nsignboard signs (half A, site-family units):")
    for sg in sorted(set(SIGNBOARD)):
        ix = [k for k, u in enumerate(E) if sg in unit_features(u, (1,))]
        c = Counter((E[k]["site"], E[k]["medium"]) for k in ix)
        print(sg, len(ix), c.most_common(8))
