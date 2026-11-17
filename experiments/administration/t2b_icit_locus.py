"""Test 2b (pre-registered P9, P10). ICIT / merged-corpus replication of t2 with the excavators'
area-section field, including data absent from M77: HARP Harappa (Mounds ET, E) and Dholavira.

Areas: MD SD, L (citadel) / HR, VS, DK-A..E, DK-G, DK other (lower town).
Harappa AB (citadel), F, E, ET, D/J/G. Dholavira Castle + Bailey (citadel), Middle Town, Lower Town.
Features: the same 13 as t2, read on W sequences bridged to M (first M of the bridge; W817/W861 -> M267).
Unit: distinct (text, area) pairs. Null: area labels permuted within object type x length bin, 2000 reps.
BH over all feature x site tests. Citadel test: citadel share of texts opened by M267 / M293 / M391,
chi-square-like G over the three openers, same permutation null, per site.
"""
import math
import random
import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from common import *  # noqa
import t2_offices_locus as _t2  # noqa  (reuses FEATURES and gstat; t2 runs its dev analysis on import)

FEATURES, gstat = _t2.FEATURES, _t2.gstat
rng = random.Random(SEED + 22)
br = load_bridge()


def area(site, a):
    a = (a or "").strip()
    if site == "Mohenjo-daro":
        if a.startswith("SD"): return "SD"
        if a.startswith("L"): return "L"
        if a.startswith("HR"): return "HR"
        if a.startswith("VS"): return "VS"
        if a.startswith("DKG"): return "DK-G"
        if a[:3] in ("DKA", "DKB", "DKC", "DKD", "DKE", "DKH"): return "DK-A..E"
        if a.startswith("DK"): return "DK other"
    if site == "Harappa":
        if a.startswith("AB"): return "AB"
        if a.startswith("ET"): return "ET"
        if a.startswith("E"): return "E"
        if a.startswith("F"): return "F"
        if a[:1] in ("D", "J", "G"): return "D/J/G"
    if site == "Dholavira":
        if "Castle" in a or "castle" in a or a.startswith("Bailey"): return "Castle+Bailey"
        if a.startswith("Middle Town"): return "Middle Town"
        if a.startswith("Lower Town"): return "Lower Town"
    return None


CIT = {"Mohenjo-daro": {"SD", "L"}, "Harappa": {"AB"}, "Dholavira": {"Castle+Bailey"}}
mc = load_merged()
D, seen = [], set()
for r in mc:
    if r["site"] not in CIT or not r["seq"]:
        continue
    a = area(r["site"], r["area-section"])
    if a is None:
        continue
    s = tuple(br.get(w, "OOV%d" % w) for w in r["seq"] if isinstance(w, int))
    if not s:
        continue
    k = (r["site"], s, a)
    if k in seen:
        continue
    seen.add(k)
    D.append((None, r["site"], r["type"].split(":")[0] + (":" + r["type"].split(":")[1] if r["type"].startswith("TAB") else ""), s, None, a))

NREP = 2000
results, cit_out = [], {}
for site in CIT:
    rows = [r for r in D if r[1] == site]
    strata = defaultdict(list)
    for i, r in enumerate(rows):
        strata[(r[2], min(len(r[3]), 6))].append(i)
    print(f"{site}: {len(rows)} distinct (text, area); areas {dict(Counter(r[5] for r in rows))}")
    perms = []
    for _ in range(NREP):
        lab = [None] * len(rows)
        for idx in strata.values():
            a = [rows[i][5] for i in idx]
            rng.shuffle(a)
            for i, x in zip(idx, a):
                lab[i] = x
        perms.append(lab)
    for fname, f in FEATURES.items():
        feat = [f(r[3]) for r in rows]
        if sum(feat) < 8:
            continue
        g = gstat(rows, feat)
        nullg = [gstat([(None,) * 5 + (x,) for x in lab], feat) for lab in perms]
        p = (1 + sum(x >= g for x in nullg)) / (NREP + 1)
        exp = Counter()
        for lab in perms[:500]:
            for x, ff in zip(lab, feat):
                if ff: exp[x] += 1
        obs = Counter(r[5] for r, ff in zip(rows, feat) if ff)
        top = max(obs, key=lambda a: obs[a] - exp[a] / 500)
        results.append(dict(site=site, feature=fname, n=sum(feat), G=g, p=p, top_area=top,
                            top_obs=obs[top], top_exp=exp[top] / 500))
    # citadel x opener
    ops = ("M267", "M293", "M391")
    idx_op = [i for i, r in enumerate(rows) if r[3][0] in ops]

    def gcit(lab):
        tab = {o: [0, 0] for o in ops}
        for i in idx_op:
            tab[rows[i][3][0]][int(lab[i] in CIT[site])] += 1
        n = sum(sum(v) for v in tab.values()); c = sum(v[1] for v in tab.values())
        if c == 0 or c == n:
            return 0.0, tab
        g = 0.0
        for o, (a0, a1) in tab.items():
            no = a0 + a1
            for obs_, tot in ((a1, c), (a0, n - c)):
                e = no * tot / n
                if obs_ > 0 and e > 0:
                    g += 2 * obs_ * math.log(obs_ / e)
        return g, tab
    lab0 = [r[5] for r in rows]
    g0, tab0 = gcit(lab0)
    pc = (1 + sum(gcit(lab)[0] >= g0 for lab in perms)) / (NREP + 1)
    allc = sum(r[5] in CIT[site] for r in rows)
    print(f"  citadel x opener {site}: (lower, citadel) {tab0}; all texts citadel {allc}/{len(rows)}; G={g0:.2f} p={pc:.4f}")
    cit_out[site] = dict(table=tab0, citadel_all=allc, n=len(rows), G=g0, p=pc)

q = bh([r["p"] for r in results])
for r, qq in zip(results, q):
    r["q"] = qq
results.sort(key=lambda r: r["p"])
print(f"{len(results)} feature x site tests (BH):")
for r in results:
    print(f"  {'*' if r['q']<0.05 else ' '} {r['site'][:9]:9} {r['feature']:18} n={r['n']:4d} G={r['G']:6.1f} p={r['p']:.4f} q={r['q']:.3f} top {r['top_area']} {r['top_obs']} vs {r['top_exp']:.1f}")
save_json("t2b_icit_locus", {"tests": results, "citadel": cit_out})
