"""Claim 3 (context): object-type registers; M99 seal-specific; jar+M176 tablet/rod-specific.
Attacks:
 (a) duplicate inflation: context deduplicates on (type, exact seq incl. '|' '#'), so broken
     or line-split copies of one legend count as separate texts. Recount at the level of
     near-duplicate families (edit distance <=1 on break-free flattened text, plus containment
     of a broken fragment in a complete text).
 (b) M99 confound: M99 is the fixed second member of the openers M267-M99 / M391-M99. Is
     'M99 is seal-specific' anything more than 'the opener formula is seal-specific'?
 (c) M342-M176 on rods/tablets: how many independent legends and sites carry it?
Expected counts: site x length-bin stratified rates (same null family as context; own code)."""
from collections import Counter, defaultdict
import numpy as np
from scipy.stats import poisson
from rt_common import icit, m77, near_dup_clusters, save

M_TYPE = {"seal": "seal", "sealing": "sealing", "miniature tablet": "tablet", "copper tablet": "copper",
          "pottery graffito": "pottery", "ivory/bone rod": "rod", "bronze implement": "implement"}


def i_type(t):
    if t.startswith("SEAL"): return "seal"
    if t.startswith("TAG"): return "sealing"
    if t in ("TAB:B", "TAB:I"): return "tablet"
    if t == "TAB:C": return "copper"
    if t.startswith("PO"): return "pottery"
    return {"ROD": "rod", "IMPL": "implement", "BNGL": "bangle"}.get(t)


def units(recs, tmap, tk):
    seen, out = set(), []
    for r in recs:
        ty = tmap(r[tk]) if callable(tmap) else tmap.get(r[tk])
        if not ty: continue
        ss = [s for s in r["seq"] if s not in ("|", "#")]
        if not ss: continue
        k = (ty, " ".join(r["seq"]))
        if k in seen: continue
        seen.add(k)
        out.append(dict(type=ty, raw=tuple(r["seq"]), flat=tuple(ss), site=r["site"],
                        broken="#" in r["seq"]))
    return out


def families(U):
    """Group units of the same type+site into families: edit<=1 on flattened seq, and
    broken fragments contained (as contiguous run) in another unit's flat seq."""
    out = []
    key = defaultdict(list)
    for u in U:
        key[(u["type"], u["site"])].append(u)
    for (ty, site), us in key.items():
        seqs = sorted({u["flat"] for u in us})
        cl = near_dup_clusters(seqs)
        idx = {s: i for i, c in enumerate(cl) for s in c}
        # containment merge for broken fragments (length>=2)
        par = list(range(len(cl)))
        def f(x):
            while par[x] != x: x = par[x]
            return x
        frag = [u["flat"] for u in us if u["broken"] and len(u["flat"]) >= 2]
        for fr in set(frag):
            for s in seqs:
                if s != fr and len(s) > len(fr) and any(s[i:i + len(fr)] == fr for i in range(len(s) - len(fr) + 1)):
                    par[f(idx[fr])] = f(idx[s]); break
        groups = defaultdict(list)
        for s in seqs:
            groups[f(idx[s])].append(s)
        for g in groups.values():
            rep = max(g, key=len)
            out.append(dict(type=ty, site=site, flat=rep, members=g))
    return out


def has(u, feat):
    f = feat.split()
    seqs = u.get("members", [u["flat"]])
    if len(f) == 1:
        return any(f[0] in m for m in seqs)
    return any(tuple(f) == m[i:i + 2] for m in seqs for i in range(len(m) - 1))


def lenbin(n):
    return 1 if n <= 2 else 2 if n <= 4 else 3 if n <= 6 else 4


def enrich(U, feat, ty):
    st = defaultdict(lambda: [0, 0, 0])  # n, n_type, n_feat
    for u in U:
        k = (u["site"], lenbin(len(u["flat"])))
        st[k][0] += 1; st[k][1] += u["type"] == ty; st[k][2] += has(u, feat)
    obs = sum(1 for u in U if u["type"] == ty and has(u, feat))
    exp = sum(v[1] * v[2] / v[0] for v in st.values() if v[0])
    p_hi = poisson.sf(obs - 1, exp) if exp > 0 else None
    p_lo = poisson.cdf(obs, exp) if exp > 0 else None
    return dict(obs=obs, exp=round(exp, 2), ratio=round(obs / exp, 2) if exp else None,
                p_hi=float(p_hi), p_lo=float(p_lo), n_type=sum(u["type"] == ty for u in U))


TESTS_M = [("M99", "seal"), ("M99", "copper"), ("M99", "tablet"), ("M342 M176", "rod"), ("M176", "rod"),
           ("M342 M176", "seal"), ("M407", "copper"), ("M169", "copper")]
TESTS_W = [("W002", "seal"), ("W002", "copper"), ("W002", "tablet"), ("W740 W400", "rod"),
           ("W740 W400", "tablet"), ("W740 W400", "seal"), ("W400", "tablet"), ("W407", "copper"), ("W845", "copper")]


def main():
    res = {}
    for name, recs, tmap, tk, tests, opener, conn in [
            ("M77", m77(), M_TYPE, "object_type", TESTS_M, {"M267", "M391", "M293", "M284"}, "M99"),
            ("ICIT", icit(), i_type, "type", TESTS_W, {"W817", "W861", "W820", "W920"}, "W002")]:
        U = units(recs, tmap, tk)
        F = families(U)
        r = {"n_units": len(U), "n_families": len(F),
             "units_by_type": Counter(u["type"] for u in U), "families_by_type": Counter(f["type"] for f in F)}
        for feat, ty in tests:
            r[f"{feat} @ {ty}"] = dict(units=enrich(U, feat, ty), families=enrich(F, feat, ty),
                                       sites_with=Counter(f["site"] for f in F if f["type"] == ty and has(f, feat)))
        # (b) connective conditional on opener, per type
        cond = {}
        for ty in ("seal", "sealing", "tablet", "copper", "pottery", "rod"):
            us = [f for f in F if f["type"] == ty]
            wo = [f for f in us if any(o in f["flat"] for o in opener)]
            wno = [f for f in us if not any(o in f["flat"] for o in opener)]
            cond[ty] = dict(n=len(us), opener_rate=round(len(wo) / max(1, len(us)), 3),
                            conn_given_opener=f"{sum(conn in f['flat'] for f in wo)}/{len(wo)}",
                            conn_given_no_opener=f"{sum(conn in f['flat'] for f in wno)}/{len(wno)}")
        r["connective_conditional_on_opener"] = cond
        # how much of conn occurrences are right after an opener
        tok = Counter()
        for f in F:
            s = f["flat"]
            for i, x in enumerate(s):
                if x == conn:
                    tok["after_opener" if i > 0 and s[i - 1] in opener else "other"] += 1
        r["connective_tokens_after_opener"] = tok
        res[name] = r
        import json; print(name, json.dumps(r, indent=1, default=str))
    save("r3_registers", res)


if __name__ == "__main__":
    main()
