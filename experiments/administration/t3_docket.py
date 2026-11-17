"""Test 3. Docket arithmetic on two-sided tablets/sealings.

(a) Fixed or variable: for the same side-1 identity, is the side-2 tall-stroke value N constant?
    Unit: distinct (side-1 text, side-2 text) pairs whose side 2 has exactly one tall-stroke sign.
    Statistic: within-identity sum of squared deviations of N (smaller = more fixed) and the number
    of identities with a single N. Null: N shuffled across pairs within object type (5000 reps).
    M77 (split by side-1 text) and ICIT (TAB/TAG with sides .1/.2, W031-W035).
(b) Bundling bound: in distinct M77 texts that hold short-stroke numerals, is the short value lower
    (capped) when a tall-stroke numeral co-occurs? Null: tall-presence label permuted within
    object type x length bin (5000 reps). Also the maximum short value with/without tall.
(c) Stratigraphy: does side-2 N (or any tall value with M328) rise with phase at Harappa?
    ICIT/merged corpus 'time' (HARP Period 3A..4) and Vats 'Stratum I-VII' (I = top = latest);
    M77 Harappa 'level' within locus (deeper = older). Spearman, null = values permuted within
    object type (and within locus for M77), 5000 reps. Distinct (text, phase) units.

Usage: t3_docket.py [dev|heldout|all]   (split applies to the M77 parts)
"""
import random
import re
import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from common import *  # noqa
from scipy.stats import spearmanr

split = sys.argv[1] if len(sys.argv) > 1 else "dev"
rng = random.Random(SEED + 3)
dev, ho = dev_heldout(version=2)
pickk = {key(t["seq"]) for t in {"dev": dev, "heldout": ho, "all": dev + ho}[split]}
NREP = 5000
out = {}

ICIT_TALL = {"W031": 1, "W032": 2, "W033": 3, "W034": 4, "W035": 5}


def fixedness(pairs):
    """pairs: list of (identity, otype, N). Returns (SS_within, n_identities>=2, n_single_N, perm p for SS, perm p for single)."""
    byid = defaultdict(list)
    for i, (idn, ot, n) in enumerate(pairs):
        byid[idn].append(i)
    multi = [v for v in byid.values() if len(v) >= 2]

    def stats(N):
        ss, single = 0.0, 0
        for v in multi:
            xs = [N[i] for i in v]
            m = sum(xs) / len(xs)
            ss += sum((x - m) ** 2 for x in xs)
            single += len(set(xs)) == 1
        return ss, single
    N0 = [p[2] for p in pairs]
    ss0, s0 = stats(N0)
    byot = defaultdict(list)
    for i, p in enumerate(pairs):
        byot[p[1]].append(i)
    le_ss = ge_s = 0
    nss, ns = [], []
    for _ in range(NREP):
        N = list(N0)
        for idx in byot.values():
            v = [N0[i] for i in idx]
            rng.shuffle(v)
            for i, x in zip(idx, v):
                N[i] = x
        ss, s = stats(N)
        nss.append(ss); ns.append(s)
        le_ss += ss <= ss0
        ge_s += s >= s0
    return dict(n_pairs=len(pairs), n_identities_multi=len(multi), ss_within=ss0, ss_null=sum(nss) / NREP,
                p_fixed_ss=(1 + le_ss) / (NREP + 1), single_N=s0, single_null=sum(ns) / NREP,
                p_fixed_single=(1 + ge_s) / (NREP + 1))


# ---------- (a) M77
T = m77_texts()
byobj = defaultdict(dict)
for t in T:
    byobj[t["text_no"]][t["side"]] = t
pairs, seen = [], set()
examples = defaultdict(Counter)
for tn, d in byobj.items():
    if 1 not in d or 2 not in d:
        continue
    s1, s2 = d[1], d[2]
    if "#" in s1["seq"] or key(s1["seq"]) not in pickk:
        continue
    tall = [TALL[x] for x in signs(s2["seq"]) if x in TALL]
    if len(tall) != 1:
        continue
    k = (key(s1["seq"]), key(s2["seq"]))
    if k in seen:
        continue
    seen.add(k)
    pairs.append((key(s1["seq"]), s1["object_type"], tall[0]))
    examples[key(s1["seq"])][key(s2["seq"])] += 1
fa = fixedness(pairs)
print(f"[{split}] (a) M77 distinct side1/side2 pairs with one tall value on side 2: {fa}")
for idn, c in sorted(examples.items(), key=lambda x: -len(x[1]))[:8]:
    if len(c) >= 2:
        print(f"     side1 [{idn}] -> side2 {dict(c)}")
out["a_m77"] = fa
# object-level (not distinct) for comparison
pairs_obj = []
for tn, d in byobj.items():
    if 1 in d and 2 in d and "#" not in d[1]["seq"] and key(d[1]["seq"]) in pickk:
        tall = [TALL[x] for x in signs(d[2]["seq"]) if x in TALL]
        if len(tall) == 1:
            pairs_obj.append((key(d[1]["seq"]), d[1]["object_type"], tall[0]))
fo = fixedness(pairs_obj)
print(f"   object-level (mould copies NOT collapsed, for reference only): single-N {fo['single_N']}/{fo['n_identities_multi']} vs {fo['single_null']:.1f}, p={fo['p_fixed_single']:.4f}")
out["a_m77_objects_reference"] = fo

# ---------- (a) ICIT (split-independent: all sites; reported as replication)
I = icit_texts()
ib = defaultdict(dict)
for r in I:
    a, b = r["id"].split(".")
    ib[a][int(b)] = r
ip, seen = [], set()
for a, d in ib.items():
    if 1 not in d or 2 not in d:
        continue
    r1, r2 = d[1], d[2]
    if not (r1["type"].startswith("TAB") or r1["type"].startswith("TAG")):
        continue
    # side order in ICIT is not guaranteed: identity = the side WITHOUT the tall stroke
    t1 = [ICIT_TALL[x] for x in r1["seq"] if x in ICIT_TALL]
    t2 = [ICIT_TALL[x] for x in r2["seq"] if x in ICIT_TALL]
    if len(t2) == 1 and not t1:
        idr, nr = r1, t2[0]
    elif len(t1) == 1 and not t2:
        idr, nr = r2, t1[0]
    else:
        continue
    if "#" in idr["seq"]:
        continue
    k = (key(idr["seq"]), key(d[1]["seq"] + ["/"] + d[2]["seq"]))
    if k in seen:
        continue
    seen.add(k)
    ip.append((key(idr["seq"]), idr["type"].split(":")[0] + idr["type"][3:5], nr))
fi = fixedness(ip)
print(f"   ICIT distinct pairs: {fi}")
out["a_icit"] = fi

# ---------- (b) bundling bound (M77 distinct texts in split)
D = [t for t in distinct(T) if key(t["seq"]) in pickk]
rows = []
for t in D:
    s = signs(t["seq"])
    sh = [SHORT[x] for x in s if x in SHORT]
    if not sh:
        continue
    has_t = any(x in TALL for x in s)
    rows.append((t["object_type"], min(len(s), 7), max(sh), has_t))
with_t = [r[2] for r in rows if r[3]]
without = [r[2] for r in rows if not r[3]]
obs = sum(with_t) / max(1, len(with_t)) - sum(without) / max(1, len(without))
strata = defaultdict(list)
for i, r in enumerate(rows):
    strata[(r[0], r[1])].append(i)
lab0 = [r[3] for r in rows]
cnt = 0
nulls = []
for _ in range(NREP):
    lab = list(lab0)
    for idx in strata.values():
        v = [lab0[i] for i in idx]
        rng.shuffle(v)
        for i, x in zip(idx, v):
            lab[i] = x
    a = [rows[i][2] for i in range(len(rows)) if lab[i]]
    b = [rows[i][2] for i in range(len(rows)) if not lab[i]]
    d = sum(a) / max(1, len(a)) - sum(b) / max(1, len(b))
    nulls.append(d)
    cnt += d <= obs
pb = (1 + cnt) / (NREP + 1)
print(f"(b) texts with short numerals: {len(rows)}; with tall {len(with_t)} (max short {max(with_t) if with_t else None}, dist {sorted(Counter(with_t).items())});"
      f" without tall {len(without)} (max {max(without)}, dist {sorted(Counter(without).items())})")
print(f"    mean short value with - without tall = {obs:+.2f}; null mean {sum(nulls)/NREP:+.2f}; one-sided p (capped) = {pb:.4f}")
out["b_bundling"] = dict(n=len(rows), n_with_tall=len(with_t), max_with=max(with_t) if with_t else None,
                         max_without=max(without), diff=obs, p_capped=pb,
                         dist_with=dict(Counter(with_t)), dist_without=dict(Counter(without)))


# ---------- (c) stratigraphy
def time_rank(t):
    m = re.match(r"Period (\d)([ABC]?)(/C)?(?:-(\d))?", t or "")
    if not m:
        return None
    per, sub, bc, n = m.groups()
    r = float(per)
    if sub:
        r += {"A": 0.0, "B": 0.3, "C": 0.6}[sub]
    if bc:
        r += 0.15
    if n:
        r += 0.05 * int(n)
    return r


mc = load_merged()
TW = {31: 1, 32: 2, 33: 3, 34: 4, 35: 5}
for label, rankf in (("HARP time", lambda r: time_rank(r["time"]) if r["time"] != "-" else None),
                     ("Vats stratum (I=latest)", lambda r: (-["I", "II", "III", "IV", "V", "VI", "VII"].index(r["phase"].strip().replace("Stratum ", "")))
                      if r["phase"].strip().startswith("Stratum ") else None)):
    rows, seen = [], set()
    for r in mc:
        if r["site"] != "Harappa" or not r["type"].startswith("TAB"):
            continue
        rk = rankf(r)
        if rk is None:
            continue
        tv = [TW[w] for w in r["seq"] if w in TW]
        if len(tv) != 1:
            continue
        k = (tuple(r["seq"]), rk)
        if k in seen:
            continue
        seen.add(k)
        rows.append((r["type"], rk, tv[0], 700 in r["seq"]))
    for sub, rr in (("all tall", rows), ("tall + cup W700", [x for x in rows if x[3]])):
        if len(rr) < 10:
            continue
        rho = spearmanr([x[1] for x in rr], [x[2] for x in rr]).correlation
        byot = defaultdict(list)
        for i, x in enumerate(rr):
            byot[x[0]].append(i)
        ge = 0
        V0 = [x[2] for x in rr]
        for _ in range(2000):
            V = list(V0)
            for idx in byot.values():
                v = [V0[i] for i in idx]
                rng.shuffle(v)
                for i, x in zip(idx, v):
                    V[i] = x
            r2 = spearmanr([x[1] for x in rr], V).correlation
            ge += abs(r2) >= abs(rho)
        p = (1 + ge) / 2001
        means = defaultdict(list)
        for x in rr:
            means[round(x[1], 2)].append(x[2])
        print(f"(c) Harappa tablets, {label}, {sub}: n={len(rr)} distinct (text, phase); Spearman rho={rho:+.3f}; p={p:.4f}; "
              f"mean N by phase {[(k, round(sum(v)/len(v),2), len(v)) for k, v in sorted(means.items())]}")
        out[f"c_{label}_{sub}"] = dict(n=len(rr), rho=rho, p=p)

# M77 Harappa level within locus (deeper = more negative level = older), side-2 tall value
L = m77_lines()
rows, seen = [], set()
for l in L:
    if l["site"] != "Harappa" or l["level"] in ("0", "") or l["side"] < 1:
        continue
    tv = [TALL[x] for x in l["signs"] if x in TALL]
    if len(tv) != 1:
        continue
    k = (key(l["signs"]), l["locus"], l["level"])
    if k in seen:
        continue
    seen.add(k)
    rows.append((l["locus"], int(l["level"]), tv[0]))
if rows:
    rho = spearmanr([x[1] for x in rows], [x[2] for x in rows]).correlation
    byl = defaultdict(list)
    for i, x in enumerate(rows):
        byl[x[0]].append(i)
    ge = 0
    V0 = [x[2] for x in rows]
    for _ in range(2000):
        V = list(V0)
        for idx in byl.values():
            v = [V0[i] for i in idx]
            rng.shuffle(v)
            for i, x in zip(idx, v):
                V[i] = x
        ge += abs(spearmanr([x[1] for x in rows], V).correlation) >= abs(rho)
    p = (1 + ge) / 2001
    print(f"(c) M77 Harappa lines with one tall value, level (higher = younger) vs N: n={len(rows)}; rho={rho:+.3f}; within-locus perm p={p:.4f}")
    out["c_m77_level"] = dict(n=len(rows), rho=rho, p=p)

save_json(f"t3_docket_{split}", out)
