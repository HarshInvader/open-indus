"""Test 4 (pre-registered P13, P14). Lothal sealings: does any sign predict what was sealed?

Backs: Frenez & Tosi 2005 Table 1 (paragorth transcription,
sources/paragorth_Indus-/data/derived/lothal-sealings-frenez-tosi2005.json): fastening type per sealing.
Texts: ICIT records with the same CISI number (one record per seal impression on the sealing).
'undiagnostic' backs are dropped. No held-out exists (one site, ~60 sealings): the test is
pre-registered and corrected instead.

P13: per sign (W numbers; in >= 3 distinct texts), G statistic of sign presence x back type over
     distinct (text, back type) pairs. Null: back types permuted among sealings (10000 reps), distinct
     pairs recomputed each time. BH over signs. W390 (= M161-169 tree family) and W700 (cup) reported
     whatever their rank.
P14: same seal text -> same back type: number of pairs of sealings with an identical (complete) text
     that share the back type, with and without the elephant-seal text W817-W002-W048-W740.
"""
import math
import random
import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from common import *  # noqa

rng = random.Random(SEED + 4)
ft = json.load(open(ROOT / "sources/paragorth_Indus-/data/derived/lothal-sealings-frenez-tosi2005.json"))["rows"]
back = {r[0]: r[2] for r in ft if r[2] not in ("undiagnostic",)}
I = icit_texts()
texts = defaultdict(list)
for r in I:
    if r["site"] == "Lothal" and r["cisi"] in back:
        s = tuple(x for x in r["seq"] if x != "#")
        if s:
            texts[r["cisi"]].append((s, "#" not in r["seq"]))
seal_ids = sorted(texts)
types0 = [back[c] for c in seal_ids]
print(f"Lothal sealings with a diagnostic back and a transcribed text: {len(seal_ids)}; impressions {sum(len(v) for v in texts.values())}")
print("  back types:", dict(Counter(types0)))


def pairs_for(types):
    return {(s, t) for c, t in zip(seal_ids, types) for s, _ in texts[c]}


def gstat(P, sign):
    tab = defaultdict(lambda: [0, 0])
    for s, t in P:
        tab[t][int(sign in s)] += 1
    n = len(P); F = sum(v[1] for v in tab.values())
    if F == 0 or F == n:
        return 0.0
    g = 0.0
    for t, (a0, a1) in tab.items():
        nt = a0 + a1
        for o, tot in ((a1, F), (a0, n - F)):
            e = nt * tot / n
            if o > 0:
                g += 2 * o * math.log(o / e)
    return g


P0 = pairs_for(types0)
dtexts = {s for s, _ in P0}
signs_n = Counter(x for s in dtexts for x in set(s))
test_signs = sorted([x for x, n in signs_n.items() if n >= 3])
for must in ("W390", "W700"):
    if must in signs_n and must not in test_signs:
        test_signs.append(must)
NREP = 10000
g0 = {w: gstat(P0, w) for w in test_signs}
ge = Counter()
for _ in range(NREP):
    t = list(types0)
    rng.shuffle(t)
    P = pairs_for(t)
    for w in test_signs:
        ge[w] += gstat(P, w) >= g0[w]
pv = {w: (1 + ge[w]) / (NREP + 1) for w in test_signs}
qv = dict(zip(test_signs, bh([pv[w] for w in test_signs])))
res = []
print(f"P13: {len(test_signs)} signs tested over {len(P0)} distinct (text, back) pairs, {len(dtexts)} distinct texts")
for w in sorted(test_signs, key=lambda w: pv[w]):
    bytype = Counter(t for s, t in P0 if w in s)
    print(f"  {'*' if qv[w]<0.05 else ' '} {w}: texts {signs_n[w]}  G={g0[w]:.2f} p={pv[w]:.4f} q={qv[w]:.3f}  backs {dict(bytype)}")
    res.append(dict(sign=w, n_texts=signs_n[w], G=g0[w], p=pv[w], q=qv[w], backs=dict(bytype)))

# P14
ELE = ("W817", "W002", "W048", "W740")


def same_type_pairs(types, drop_ele):
    k = 0
    items = [(c, t) for c, t in zip(seal_ids, types)]
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            ci, ti = items[i]; cj, tj = items[j]
            si = {s for s, comp in texts[ci] if comp}; sj = {s for s, comp in texts[cj] if comp}
            common = si & sj
            if drop_ele:
                common -= {ELE}
            if common and ti == tj:
                k += 1
    return k


def n_same_text_pairs(drop_ele):
    k = 0
    for i in range(len(seal_ids)):
        for j in range(i + 1, len(seal_ids)):
            si = {s for s, comp in texts[seal_ids[i]] if comp}; sj = {s for s, comp in texts[seal_ids[j]] if comp}
            c = si & sj
            if drop_ele:
                c -= {ELE}
            k += bool(c)
    return k


p14 = {}
for drop in (False, True):
    o = same_type_pairs(types0, drop)
    null = []
    for _ in range(2000):
        t = list(types0); rng.shuffle(t)
        null.append(same_type_pairs(t, drop))
    p = (1 + sum(x >= o for x in null)) / 2001
    lab = "without elephant seal" if drop else "all texts"
    print(f"P14 ({lab}): same-text sealing pairs {n_same_text_pairs(drop)}; sharing back type {o} vs null {sum(null)/2000:.2f}; p={p:.4f}")
    p14[lab] = dict(pairs=n_same_text_pairs(drop), same_type=o, null=sum(null) / 2000, p=p)
save_json("t4_lothal_backs", {"n_sealings": len(seal_ids), "signs": res, "same_text": p14})
