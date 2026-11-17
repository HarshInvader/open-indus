import sys; sys.path.insert(0, "experiments/redteam_chrono")
from rc_lib import *
from collections import Counter
H = dataset_harp(); V = dataset_vats()
for name, D in [("HARP", H), ("VATS", V)]:
    print(name, len(D), "units")
    c = Counter((u["rel"], u["type"]) for u in D)
    for r in sorted({u["rel"] for u in D}):
        tot = sum(v for (rr, t), v in c.items() if rr == r)
        print("  rel", r, tot, {t: v for (rr, t), v in sorted(c.items()) if rr == r})
# shared texts
hs = {" ".join(signs_of(u["seq"])) for u in H}; vs = {" ".join(signs_of(u["seq"])) for u in V}
print("shared identical texts", len(hs & vs))
A = Shift(H); B = Shift(V)
r = compare(A, B, nperm=2000)
print("HARP~VATS type-stratified: n=%d rho=%.3f p=%.4f null %.3f+-%.3f" % (r["n"], r["rho"], r["p"], r["null_mean"], r["null_sd"]))
