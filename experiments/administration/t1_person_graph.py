"""Test 1. Person graph: is line 2 (or a second side, or the second half of a one-line text)
itself a complete text of ANOTHER object, above nulls?

Unit: distinct M77 object-side texts. Reference set (what counts as "attested"): every
complete one-line M77 text (no '#'), excluding the source object (text_no).

A. Second lines/sides. Candidates = lines 2+ of multi-line texts and sides 2+ of
   multi-sided SEALS, length >= 2. Statistic = share that equal a complete text of
   another object. Null = random proper L-windows (text length > L) from one-line texts
   of other objects at the same site (or the whole corpus if the site has none), 2000 reps.
   Comparison stat: line 1 of the same objects against the same null.
B. Same-site: among attested candidates, share with a same-site attestation. Null = site
   labels permuted among reference texts within length strata (2000 reps).
C. Compounds: one-line texts T (len >= 4) = A + B, |A|,|B| >= 2, both complete texts of
   other objects. Null = MLE bigram corpora of the same size and length distribution
   (trained on the analysed texts), 200 reps; same-site version with site permutation.

Usage: t1_person_graph.py [dev|heldout|all]
"""
import random
import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from common import *  # noqa

split = sys.argv[1] if len(sys.argv) > 1 else "dev"
rng = random.Random(SEED)
T = m77_texts()
dev, ho = dev_heldout(version=2)
pick = {"dev": dev, "heldout": ho, "all": dev + ho}[split]
pickk = {key(t["seq"]) for t in pick}

# reference set from ALL objects (attestation can be anywhere), but the candidate texts come from the split
comp = defaultdict(set)
onel = []  # (text_no, site, tuple)
for t in T:
    # reference = one-line texts of single-sided objects only (side 0), so that copies of the
    # same multi-sided object (prisms, two-sided tablets) cannot attest each other
    if "#" in t["seq"] or "|" in t["seq"] or t["side"] != 0:
        continue
    s = tuple(t["seq"])
    comp[s].add((t["text_no"], t["site"]))
    onel.append((t["text_no"], t["site"], s))


def attested(s, src):
    return {x for x in comp.get(tuple(s), set()) if x[0] != src}


# ---------- A: second lines / sides
cands = []  # (src text_no, site, line1 tuple, line2 tuple, kind)
for t in distinct(T):
    if key(t["seq"]) not in pickk or "|" not in t["seq"]:
        continue
    L = lines_of([x for x in t["seq"] if x != "#"])
    for l in L[1:]:
        cands.append((t["text_no"], t["site"], tuple(L[0]), tuple(l), "line"))
# multi-sided seals: side 2+ vs side 1
bys = defaultdict(dict)
for t in T:
    if t["object_type"] == "seal" and t["side"] >= 1:
        bys[t["text_no"]][t["side"]] = t
for tn, d in bys.items():
    if 1 in d and len(d) > 1:
        s1 = d[1]
        for sd, t in d.items():
            if sd == 1 or key(t["seq"]) not in pickk or "#" in t["seq"]:
                continue
            cands.append((tn, t["site"], tuple(signs(s1["seq"])), tuple(signs(t["seq"])), "side"))
cands = [c for c in cands if len(c[3]) >= 2]
_seen, _c2 = set(), []
for c in cands:  # one candidate per distinct (first line/side, second line/side) pair
    if (c[2], c[3]) not in _seen:
        _seen.add((c[2], c[3])); _c2.append(c)
cands = _c2

by_site_len = defaultdict(list)
for tn, site, s in onel:
    by_site_len[site].append((tn, s))


def window(site, L, src):
    pool = [x for x in by_site_len.get(site, []) if len(x[1]) > L and x[0] != src]
    if len(pool) < 20:
        pool = [x for x in onel if len(x[2]) > L and x[0] != src]
        pool = [(a, c) for a, b, c in pool]
    tn, s = rng.choice(pool)
    i = rng.randrange(len(s) - L + 1)
    return tn, s[i:i + L]


obsA = [bool(attested(c[3], c[0])) for c in cands]
obsA1 = [bool(attested(c[2], c[0])) for c in cands if len(c[2]) >= 2]
NREP = 2000
null = []
for _ in range(NREP):
    k = 0
    for c in cands:
        tn, w = window(c[1], len(c[3]), c[0])
        k += bool(attested(w, tn))
    null.append(k / len(cands))
mA = sum(obsA) / len(cands)
pA = (1 + sum(x >= mA for x in null)) / (NREP + 1)
mean_null = sum(null) / NREP

print(f"[{split}] A. second lines/sides len>=2: n={len(cands)} (lines {sum(c[4]=='line' for c in cands)}, sides {sum(c[4]=='side' for c in cands)})")
print(f"   attested as a complete text elsewhere: {sum(obsA)}/{len(cands)} = {mA:.3f}; window null {mean_null:.3f}; p={pA:.4f}")
print(f"   line 1 of same objects (len>=2): {sum(obsA1)}/{len(obsA1)} = {sum(obsA1)/max(1,len(obsA1)):.3f}")
for c, o in zip(cands, obsA):
    if o:
        at = attested(c[3], c[0])
        print(f"     {c[0]} {c[1][:5]} {c[4]}: [{' '.join(c[2])}] | [{' '.join(c[3])}]  -> {sorted(at)[:5]}")

# ---------- B: same-site
att = [(c, attested(c[3], c[0])) for c in cands]
att = [(c, a) for c, a in att if a]
obsB = sum(any(x[1] == c[1] for x in a) for c, a in att)
# null: permute site labels among reference objects (one-line), within length strata
objs = list({(tn, site, s) for tn, site, s in onel})
strata = defaultdict(list)
for i, (tn, site, s) in enumerate(objs):
    strata[min(len(s), 6)].append(i)
nullB = []
for _ in range(NREP):
    newsite = {}
    for st, idx in strata.items():
        sites = [objs[i][1] for i in idx]
        rng.shuffle(sites)
        for i, s in zip(idx, sites):
            newsite[objs[i][0]] = s
    nullB.append(sum(any(newsite.get(x[0], x[1]) == c[1] for x in a) for c, a in att))
pB = (1 + sum(x >= obsB for x in nullB)) / (NREP + 1) if att else 1.0
print(f"B. same-site among attested: {obsB}/{len(att)}; null mean {sum(nullB)/NREP:.2f}; p={pB:.4f}")

# ---------- C: compounds A+B
texts = [t for t in distinct(T) if key(t["seq"]) in pickk and "#" not in t["seq"] and "|" not in t["seq"]]


def compounds(textlist, compset, sites=None):
    """textlist: [(id, site, tuple)]; compset: dict tuple -> set((id, site)). Returns list of hits."""
    hits = []
    for tid, site, s in textlist:
        if len(s) < 4:
            continue
        for k in range(2, len(s) - 1):
            a, b = s[:k], s[k:]
            if not core(a) or not core(b):  # skip bare opener formulae / bare closers
                continue
            A = {x for x in compset.get(a, ()) if x[0] != tid}
            B = {x for x in compset.get(b, ()) if x[0] != tid}
            if A and B:
                ss = any(x[1] == site for x in A) and any(x[1] == site for x in B)
                hits.append((tid, site, a, b, ss))
                break
    return hits


real = [(t["text_no"], t["site"], tuple(t["seq"])) for t in texts]
hC = compounds(real, comp)
nC = sum(len(s) >= 4 for _, _, s in real)
obsC = len(hC)
obsCss = sum(h[4] for h in hC)
print(f"C. compounds (len>=4): {obsC}/{nC} = {obsC/max(1,nC):.3f}; both halves at same site: {obsCss}")
for h in hC[:40]:
    print(f"     {h[0]} {h[1][:5]}  [{' '.join(h[2])}] + [{' '.join(h[3])}] same-site={h[4]}")

# bigram null: train MLE bigram on all one-line distinct texts; generate a synthetic corpus of the
# same size and length distribution as ALL one-line reference objects; count compounds among
# synthetic texts mapped to the split size.
allone = [s for _, _, s in onel]
big = defaultdict(Counter)
for s in set(allone):
    prev = "<s>"
    for x in s:
        big[prev][x] += 1
        prev = x
cum = {}
for p, c in big.items():
    items = list(c.items())
    tot = sum(v for _, v in items)
    cum[p] = ([k for k, _ in items], [v / tot for _, v in items])


def gen(L):
    out, prev = [], "<s>"
    while len(out) < L:
        ks, ps = cum.get(prev, cum["<s>"])
        x = rng.choices(ks, ps)[0]
        out.append(x)
        prev = x
    return tuple(out)


NR = 200
nullC = []
nullCss = []
lens_all = [(tn, site, len(s)) for tn, site, s in onel]
cand_ids = {tid for tid, _, _ in real}
for _ in range(NR):
    syn = [(tn, site, gen(L)) for tn, site, L in lens_all]
    cs = defaultdict(set)
    for tn, site, s in syn:
        cs[s].add((tn, site))
    # candidate texts: synthetic texts at the object slots belonging to the split (one per distinct real text)
    sub = [x for x in syn if x[0] in cand_ids]
    seen, sub2 = set(), []
    for x in sub:
        if x[0] not in seen:
            seen.add(x[0]); sub2.append(x)
    h = compounds(sub2, cs)
    nullC.append(len(h) / max(1, sum(len(s) >= 4 for _, _, s in sub2)))
    nullCss.append(sum(x[4] for x in h) / max(1, len(h)))
pC = (1 + sum(x >= obsC / nC for x in nullC)) / (NR + 1)
print(f"   bigram null rate {sum(nullC)/NR:.3f} (95th {sorted(nullC)[int(.95*NR)]:.3f}); p={pC:.4f}")
# same-site among compounds: site permutation within length strata
nullCs = []
for _ in range(NREP // 4):
    newsite = {}
    for st, idx in strata.items():
        sites = [objs[i][1] for i in idx]
        rng.shuffle(sites)
        for i, s in zip(idx, sites):
            newsite[objs[i][0]] = s
    k = 0
    for tid, site, a, b, _ in hC:
        A = {x for x in comp[a] if x[0] != tid}
        B = {x for x in comp[b] if x[0] != tid}
        k += any(newsite.get(x[0], x[1]) == site for x in A) and any(newsite.get(x[0], x[1]) == site for x in B)
    nullCs.append(k)
pCs = (1 + sum(x >= obsCss for x in nullCs)) / (len(nullCs) + 1)
print(f"   same-site compounds {obsCss}/{obsC}; site-permutation null {sum(nullCs)/len(nullCs):.2f}; p={pCs:.4f}")

# introducing sign: first sign of line 2 and last of line 1 among candidates
print("   first sign of second line/side:", Counter(c[3][0] for c in cands).most_common(8))
print("   first sign of compound second half:", Counter(h[3][0] for h in hC).most_common(8))
print("   last sign of compound first half:", Counter(h[2][-1] for h in hC).most_common(8))

save_json(f"t1_person_graph_{split}", {
    "A_n": len(cands), "A_attested": sum(obsA), "A_rate": mA, "A_null": mean_null, "A_p": pA,
    "A_line1_rate": sum(obsA1) / max(1, len(obsA1)),
    "B_same_site": obsB, "B_n": len(att), "B_null": sum(nullB) / NREP, "B_p": pB,
    "C_n": nC, "C_compounds": obsC, "C_rate": obsC / max(1, nC), "C_null": sum(nullC) / NR, "C_p": pC,
    "C_same_site": obsCss, "C_same_site_null": sum(nullCs) / len(nullCs), "C_same_site_p": pCs,
})
