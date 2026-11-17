"""Development only: KNOWN refs (Ur III, OB) + Indus dev. Run before the prereg; no fresh data touched."""
import numpy as np, json
from co_lib import *
rng = np.random.default_rng(1)
refs = load_refs()
T = titles(); print("titles", len(T), sorted(T)[:80])
for g in KNOWN:
    C = ref_corpus((g,), refs)
    print(g, len(C), Counter(c for x in C for c in x["cls"]))
    F = ref_class_features(C, rng=rng)
    for k, v in F.items(): print("  %-8s" % k, {a: round(b, 2) for a, b in v.items()})
dev = indus_seals("dev"); print("indus dev seals", len(dev), "mean len", np.mean([len(s) for s in dev]))
for name, S in (("jar", {"M342"}), ("closers", CLOSER_M), ("M99", {"M99"}), ("conn", CONN_M), ("open", OPEN_M)):
    f = token_features(dev, lambda l, i, S=S: l[i] in S, rng=rng)
    print("  %-8s" % name, {a: round(b, 2) for a, b in f.items()})
