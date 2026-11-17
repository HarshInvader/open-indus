import sys, json; sys.path.insert(0, "experiments/redteam_chrono")
from rc_lib import *
from collections import Counter
NP = 2000
H = dataset_harp(); V = dataset_vats()
out = {}
def run(key, A, B, **kw):
    r = compare(A, B, nperm=NP, **kw)
    out[key] = {k: r[k] for k in ("n", "rho", "p")}
    print("%-60s n=%3d rho=%+.3f p=%.4f" % (key, r["n"], r["rho"], r["p"]), flush=True)
    return r
def famdedupe(D):
    f = families(D); seen = {}
    for u, ff in zip(D, f):
        k = (ff, u["rel"], u["type"])
        if k not in seen: seen[k] = dict(u, fam=ff)
    return list(seen.values())
HF, VF = famdedupe(H), famdedupe(V)
print("distinct family x period x type: HARP %d, VATS %d" % (len(HF), len(VF)))
out["fam_units"] = [len(HF), len(VF)]
r = run("F1 distinct family per period (block unit)", Shift(HF), Shift(VF))
run("F1 + nmin 3", Shift(HF), Shift(VF), nmin=3)
# exact-sequence dedupe across types/periods: does a distinct text in many periods matter?
# share of each sign's units that come from its single largest family
def topfam_share(D):
    f = families(D); bys = defaultdict(Counter)
    for u, ff in zip(D, f):
        for s in set(signs_of(u["seq"])): bys[s][ff] += 1
    return {s: (sum(c.values()), max(c.values()), len(c)) for s, c in bys.items()}
tH, tV = topfam_share(H), topfam_share(V)
base = compare(Shift(H), Shift(V), nperm=1)
print("\nsign  nH famsH topH | nV famsV topV | shiftH shiftV")
rows = []
for s, a, b in zip(base["signs"], base["sa"], base["sb"]):
    rows.append((s, tH[s], tV[s], a, b))
for s, h, v, a, b in sorted(rows, key=lambda x: -abs(x[3] * x[4])):
    print("%-5s %3d %3d %3d | %3d %3d %3d | %+.3f %+.3f" % (s, *h, *v, a, b))
json.dump(out, open("experiments/redteam_chrono/r3.json", "w"), indent=1)
