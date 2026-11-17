"""Development only (KNOWN refs + Indus dev): slot-level features."""
import numpy as np
from co_lib import *
rng = np.random.default_rng(2)
refs = load_refs()
for g in KNOWN:
    C = ref_corpus((g,), refs)
    LR = [runs_of(c["slot"], c["tok"]) for c in C]
    print(g, "share legends <=2 runs", np.mean([len(r) <= 2 for r in LR]))
    for s in ("SEAL_OF", "OWNER", "TITLE", "KIN", "FATHER", "SERV", "LORD"):
        f = slot_features(LR, s, rng, name_slot="OWNER")
        if f: print("  %-8s" % s, {a: round(b, 2) for a, b in f.items()})
dev = indus_seals("dev")
LR = [runs_of([indus_class(x) for x in s], s) for s in dev]
print("indus dev share <=2 runs", np.mean([len(r) <= 2 for r in LR]), Counter(len(r) for r in LR))
for s in ("OPEN", "CONN", "CORE", "CLOSER", "POST"):
    f = slot_features(LR, s, rng, name_slot="CORE")
    if f: print("  %-8s" % s, {a: round(b, 2) for a, b in f.items()})
# jar-only closer
LRj = [runs_of(["CLOSER" if x == "M342" else ("CORE" if indus_class(x) == "CLOSER" else indus_class(x)) for x in s], s) for s in dev]
print("  jar-only", {a: round(b, 2) for a, b in slot_features(LRj, "CLOSER", rng, name_slot="CORE").items()})
