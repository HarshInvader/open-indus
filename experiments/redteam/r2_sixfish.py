"""Claim 2 (language): two-tier six M109 + fish M59 is a fixed pair; 7+fish refuted.
Independent recount in M77 and native ICIT (W016 = two-tier 3/3 six, W006 = one-row
six, W007 one-row 7, W017 two-tier 4/3 seven, W220 plain fish; identified by font render).
Checks: distinct texts, near-duplicate families, site and object type, register confound
for the 7+fish depletion (sevens live on copper tablets where fish are rare)."""
from collections import Counter, defaultdict
from scipy.stats import binomtest, fisher_exact
from rt_common import icit, m77, distinct_recs, near_dup_clusters, save

FISH_M = {"M59"}; FISH_W = {"W220"}
SIX_M = {"M109": "two-tier", "M108": "one-row"}; SEVEN_M = {"M110", "M111", "M112"}
SIX_W = {"W016": "two-tier", "W006": "one-row"}; SEVEN_W = {"W007", "W017", "W026"}
NUM_M = {f"M{i}" for i in (97, 98, 102, 104, 105, 106, 107, 108, 109, 110, 111, 112, 114, 115, 116, 117, 121)}
NUM_W = {f"W{i:03d}" for i in list(range(1, 21)) + [25, 26, 27, 28]} - {"W002", "W012"}


def runs(seq):
    out, cur = [], []
    for s in seq:
        if s in ("|", "#"):
            if cur: out.append(cur)
            cur = []
        else:
            cur.append(s)
    if cur: out.append(cur)
    return out


def collect(recs, num, fish, typekey):
    """Return list of (numeral, followed_by_fish, text tuple, site, type) over distinct texts."""
    rows = []
    for r in distinct_recs(recs):
        for ru in runs(r["seq"]):
            for i, s in enumerate(ru[:-1]):
                if s in num:
                    rows.append((s, ru[i + 1] in fish, tuple(r["seq"]), r["site"], r[typekey]))
    return rows


def summary(rows, signs, label):
    sel = [x for x in rows if x[0] in signs]
    k = sum(x[1] for x in sel); n = len(sel)
    base = sum(x[1] for x in rows if x[0] not in signs); nb = sum(1 for x in rows if x[0] not in signs)
    fam = near_dup_clusters(sorted({x[2] for x in sel if x[1]}))
    p_enr = binomtest(k, n, base / nb, alternative="greater").pvalue if n else None
    p_dep = binomtest(k, n, base / nb, alternative="less").pvalue if n else None
    return dict(label=label, n=n, with_fish=k, rate=round(k / n, 3) if n else None,
                base_rate=round(base / nb, 3), p_enriched=p_enr, p_depleted=p_dep,
                fish_texts=len({x[2] for x in sel if x[1]}), fish_families_ed1=len(fam),
                sites_with_fish=Counter(x[3] for x in sel if x[1]),
                types=Counter(x[4] for x in sel), types_with_fish=Counter(x[4] for x in sel if x[1]))


out = {}
for corpus, recs, num, fish, six, seven, tk, sealpred in [
        ("M77", m77(), NUM_M, FISH_M, SIX_M, SEVEN_M, "object_type", lambda t: t == "seal"),
        ("ICIT", icit(), NUM_W, FISH_W, SIX_W, SEVEN_W, "type", lambda t: t.startswith("SEAL"))]:
    rows = collect(recs, num, fish, tk)
    o = {}
    for s, nm in six.items():
        o[f"six_{nm}_{s}"] = summary(rows, {s}, f"{corpus} {s}")
    o["seven_all"] = summary(rows, seven, f"{corpus} seven")
    seal_rows = [x for x in rows if sealpred(x[4])]
    o["seals_only_seven"] = summary(seal_rows, seven, f"{corpus} seals seven")
    o["seals_only_six2"] = summary(seal_rows, {k for k, v in six.items() if v == "two-tier"}, f"{corpus} seals six2")
    # per-numeral fish rate on seals, to see if 6 is the outlier or just one of several
    per = defaultdict(lambda: [0, 0])
    for x in seal_rows:
        per[x[0]][0] += 1; per[x[0]][1] += x[1]
    o["seal_fish_rate_by_numeral"] = {k: f"{v[1]}/{v[0]}" for k, v in sorted(per.items()) if v[0] >= 5}
    out[corpus] = o
    for k, v in o.items():
        print(corpus, k, v)
save("r2_sixfish", out)
