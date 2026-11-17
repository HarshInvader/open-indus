"""Development only (KNOWN refs Ur III/OB + Indus dev). Calibrates the procedure before the prereg."""
import numpy as np
from co_core import *
rng = np.random.default_rng(3)
refs = load_refs()
REF = {g: ref_corpus((g,), refs) for g in KNOWN}
nho = len(indus_seals("heldout")); nic = len(icit_newsite_seals())
print("sizes: heldout seals", nho, "icit new-site seals", nic)
F = {g: ref_class_feats(REF[g], rng) for g in KNOWN}
for g in KNOWN:
    for k, v in F[g].items(): print(g, "%-8s" % k, {a: round(v[a], 2) for a in DEC + REPORT})
sd = scale_from(list(F.values())); print("sd", sd.round(3))
dev = indus_seals("dev")
for mode in ("set", "jar"):
    f = feats(indus_runs(dev, mode), "CLOSER", rng)
    print("dev closer", mode, {a: round(f[a], 2) for a in DEC + REPORT})
    for g in KNOWN:
        nn, d = nearest(f, F[g], sd); print("   ->", g, nn, {k: round(x, 2) for k, x in d.items()})
# C1 gold control at Indus held-out size: A's SEAL_OF/SERV/TITLE/KIN slots classified against B's classes
def c1(A, B, n, reps=40):
    res = Counter()
    for r in range(reps):
        a = subsample(REF[A], n, rng); b = subsample(REF[B], max(n, 1000), rng)
        Fa = ref_class_feats(a, rng); Fb = ref_class_feats(b, rng)
        for t, f in Fa.items():
            nn, d = nearest(f, Fb, sd)
            res[(t, nn)] += 1
    return res
for A, B in (("ob", "ur3"), ("ur3", "ob")):
    print("C1", A, "->", B, sorted(c1(A, B, nho).items()))
# C2 blind: relabelled A, top-12 word types each its own label; classify each against B's gold classes
def c2(A, B, n, reps=20, K=12):
    res = defaultdict(Counter)
    for r in range(reps):
        a = subsample(REF[A], n, rng); b = subsample(REF[B], max(n, 1000), rng)
        Fb = ref_class_feats(b, rng)
        cnt = Counter(w for c in a for w in c["tok"])
        top = {w for w, _ in cnt.most_common(K)}
        LR = blind_word_slots(a, None, top)
        gold = {}
        for c in a:
            for w, k in zip(c["tok"], c["cls"]): gold.setdefault(w, Counter())[k] += 1
        for w in top:
            f = feats(LR, "W:" + w, rng)
            if f is None: continue
            nn, d = nearest(f, Fb, sd)
            res[(w, gold[w].most_common(1)[0][0])][nn] += 1
    return res
for A, B in (("ob", "ur3"), ("ur3", "ob")):
    print("C2", A, "->", B)
    for k, v in sorted(c2(A, B, nho).items(), key=lambda x: x[0][1]): print("   ", k, dict(v))
