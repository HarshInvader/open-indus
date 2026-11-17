"""Test 2. Offices by locus: do title blocks and opener formulae cluster by excavation locus
(M77 locus codes, mapped to named areas) beyond permutation within site x object type x length?

Unit: distinct (text, locus) pairs from M77 object sides in the chosen split, MD and Harappa only.
M77 locus codes were mapped to ICIT/merged-corpus area-sections by matching identical texts
(locus_map below; see t2 log). MD: 1-7 SD (citadel), 8-15 L / citadel south, 16-18 HR, 20-22 VS,
23-29 DK-A..E, 31 DK-G South, 32 DK-G North, 33-39 DK other. Harappa: 40-46 Mound F, 47-51 AB,
52-54 J/D, 55+ other.

Statistic per feature x site: G statistic of feature presence x area, null = area labels permuted
within (object type x length bin) strata, 2000 reps. BH over all feature x site tests.
Also: (i) exact repeated texts: do copies of the same text (>=2 objects, seals only) share a locus
more than permutation predicts? (ii) Citadel test for M267 vs M293 openers.

Usage: t2_offices_locus.py [dev|heldout|all]
"""
import math
import random
import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from common import *  # noqa

split = sys.argv[1] if len(sys.argv) > 1 else "dev"
rng = random.Random(SEED + 2)
dev, ho = dev_heldout(version=2)
pickk = {key(t["seq"]) for t in {"dev": dev, "heldout": ho, "all": dev + ho}[split]}


def area(site, loc):
    l = int(loc)
    if site == "Mohenjodaro":
        if 1 <= l <= 7: return "SD"
        if 8 <= l <= 15: return "L"
        if 16 <= l <= 18: return "HR"
        if 20 <= l <= 22: return "VS"
        if 23 <= l <= 29: return "DK-A..E"
        if l == 31: return "DK-G S"
        if l == 32: return "DK-G N"
        if 33 <= l <= 39: return "DK other"
    if site == "Harappa":
        if 40 <= l <= 46: return "F"
        if 47 <= l <= 51: return "AB"
        if 52 <= l <= 54: return "J/D"
    return None


CITADEL = {"SD", "L"}

FEATURES = {
    "TB M336-M89": lambda s: _has(s, ["M336", "M89"]),
    "TB M51-M130-M149": lambda s: _has(s, ["M51", "M130"]) or _has(s, ["M130", "M149"]),
    "TB M249-M161": lambda s: _has(s, ["M249", "M161"]),
    "TB M387-M59": lambda s: _has(s, ["M387", "M59"]),
    "TB M171-M59": lambda s: _has(s, ["M171", "M59"]),
    "open M267": lambda s: s[0] == "M267",
    "open M293": lambda s: s[0] == "M293",
    "open M391": lambda s: s[0] == "M391",
    "open M150": lambda s: s[0] == "M150",
    "open M216": lambda s: s[0] == "M216",
    "M176 clitic": lambda s: "M176" in s,
    "end M342": lambda s: s[-1] == "M342",
    "end M211": lambda s: s[-1] == "M211",
}


def _has(s, ng):
    n = len(ng)
    return any(list(s[i:i + n]) == ng for i in range(len(s) - n + 1))


# object-side records with locus
L = m77_lines()
obj = defaultdict(list)
for l in L:
    obj[(l["text_no"], l["side"])].append(l)
recs = []  # (text_no, site, otype, seq tuple, locus, area)
for (tn, sd), ls in obj.items():
    site = ls[0]["site"]
    if site not in ("Mohenjodaro", "Harappa"):
        continue
    ls.sort(key=lambda x: x["line"])
    seq = []
    for i, l in enumerate(ls):
        if i: seq.append("|")
        seq += l["signs"]
    if key(seq) not in pickk:
        continue
    a = area(site, ls[0]["locus"])
    s = tuple(signs(seq))
    if not s:
        continue
    recs.append((tn, site, ls[0]["object_type"], s, ls[0]["locus"], a))

# distinct (text, locus)
seen, D = set(), []
for r in recs:
    k = (r[3], r[4])
    if r[5] is None or k in seen:
        continue
    seen.add(k); D.append(r)


def gstat(rows, feat):
    tab = defaultdict(lambda: [0, 0])
    for r, f in zip(rows, feat):
        tab[r[5]][int(f)] += 1
    n = len(rows); F = sum(feat)
    if F == 0 or F == n:
        return 0.0
    g = 0.0
    for a, (n0, n1) in tab.items():
        na = n0 + n1
        for obs, tot in ((n1, F), (n0, n - F)):
            e = na * tot / n
            if obs > 0:
                g += 2 * obs * math.log(obs / e)
    return g


results = []
NREP = 2000
for site in ("Mohenjodaro", "Harappa"):
    rows = [r for r in D if r[1] == site]
    strata = defaultdict(list)
    for i, r in enumerate(rows):
        strata[(r[2], min(len(r[3]), 6))].append(i)
    areas_n = Counter(r[5] for r in rows)
    print(f"[{split}] {site}: {len(rows)} distinct (text, locus) pairs; areas {dict(areas_n)}")
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
        nullg = []
        for lab in perms:
            rr = [(None,) * 5 + (x,) for x in lab]
            nullg.append(gstat(rr, feat))
        p = (1 + sum(x >= g for x in nullg)) / (NREP + 1)
        # top area: observed / expected (expected under the stratified null)
        exp = Counter()
        for lab in perms[:500]:
            for x, ff in zip(lab, feat):
                if ff: exp[x] += 1
        obs = Counter(r[5] for r, ff in zip(rows, feat) if ff)
        top = max(obs, key=lambda a: obs[a] - exp[a] / 500)
        results.append(dict(site=site, feature=fname, n=sum(feat), G=g, p=p, top_area=top,
                            top_obs=obs[top], top_exp=exp[top] / 500,
                            max_area_share=max(obs.values()) / sum(feat)))
q = bh([r["p"] for r in results])
for r, qq in zip(results, q):
    r["q"] = qq
results.sort(key=lambda r: r["p"])
print(f"{len(results)} feature x site tests (BH):")
for r in results:
    print(f"  {'*' if r['q']<0.05 else ' '} {r['site'][:5]} {r['feature']:18} n={r['n']:4d} G={r['G']:6.1f} p={r['p']:.4f} q={r['q']:.3f}  top {r['top_area']} {r['top_obs']} vs {r['top_exp']:.1f}; max-area share {r['max_area_share']:.2f}")

# (i) exact repeated seal texts: same-locus sharing
print("\n(i) repeated seal texts (objects, not distinct): pairs of copies at the same locus code")
rep_out = {}
for site in ("Mohenjodaro", "Harappa"):
    rows0 = [r for r in recs if r[1] == site and r[2] == "seal" and r[5] and len(r[3]) >= 2]
    # one record per object (text_no): multi-sided seals contribute their longest side only
    best = {}
    for r in rows0:
        if r[0] not in best or len(r[3]) > len(best[r[0]][3]):
            best[r[0]] = r
    rows = list(best.values())
    byt = defaultdict(list)
    for i, r in enumerate(rows):
        byt[r[3]].append(i)
    groups = [v for v in byt.values() if len(v) >= 2]

    def same_pairs(lab):
        k = 0
        for v in groups:
            c = Counter(lab[i] for i in v)
            k += sum(x * (x - 1) // 2 for x in c.values())
        return k
    lab0 = [r[4] for r in rows]
    obs = same_pairs(lab0)
    # strata: length bin x publication series (MIC 1xxx / FEM 2xxx / other), i.e. excavation campaign
    strata = defaultdict(list)
    for i, r in enumerate(rows):
        strata[(min(len(r[3]), 6), r[0] // 1000)].append(i)
    null = []
    for _ in range(NREP):
        lab = list(lab0)
        for idx in strata.values():
            a = [lab0[i] for i in idx]
            rng.shuffle(a)
            for i, x in zip(idx, a):
                lab[i] = x
        null.append(same_pairs(lab))
    p = (1 + sum(x >= obs for x in null)) / (NREP + 1)
    npairs = sum(len(v) * (len(v) - 1) // 2 for v in groups)
    print(f"  {site}: {len(groups)} repeated texts, {npairs} copy pairs; same locus {obs} vs null {sum(null)/NREP:.2f}; p={p:.4f}")
    rep_out[site] = dict(groups=len(groups), pairs=npairs, same=obs, null=sum(null) / NREP, p=p)

# (ii) citadel test (MD): M267- vs M293-initial texts, share in SD+L
print("\n(ii) Mohenjo-daro citadel (SD+L) vs lower town, opener of the text")
rows = [r for r in D if r[1] == "Mohenjodaro"]
cit = {}
for op in ("M267", "M293", "M391", "M150"):
    sub = [r for r in rows if r[3][0] == op]
    cit[op] = (sum(r[5] in CITADEL for r in sub), len(sub))
base = (sum(r[5] in CITADEL for r in rows), len(rows))
print("  opener: citadel/total", cit, "all texts", base)
# permutation within strata: difference in citadel share M267 - M293
strata = defaultdict(list)
for i, r in enumerate(rows):
    strata[(r[2], min(len(r[3]), 6))].append(i)


def diff(lab):
    a = [lab[i] in CITADEL for i, r in enumerate(rows) if r[3][0] == "M267"]
    b = [lab[i] in CITADEL for i, r in enumerate(rows) if r[3][0] == "M293"]
    return (sum(a) / max(1, len(a))) - (sum(b) / max(1, len(b)))


lab0 = [r[5] for r in rows]
d0 = diff(lab0)
null = []
for _ in range(NREP):
    lab = list(lab0)
    for idx in strata.values():
        a = [lab0[i] for i in idx]
        rng.shuffle(a)
        for i, x in zip(idx, a):
            lab[i] = x
    null.append(diff(lab))
pc = (1 + sum(abs(x) >= abs(d0) for x in null)) / (NREP + 1)
print(f"  citadel share M267 - M293 = {d0:+.3f}; two-sided permutation p={pc:.4f}")

save_json(f"t2_offices_locus_{split}", {"tests": results, "repeated_texts": rep_out,
                                         "citadel": {"counts": cit, "all": base, "diff_267_293": d0, "p": pc}})
