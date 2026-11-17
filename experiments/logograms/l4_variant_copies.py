"""L4. Duplicated / variant texts: minimal pairs between a picture and a sign, outside the copper tablets.

For every text T that occurs on an object WITH a picture P, look for a text T' on an object WITHOUT a
picture such that T' = T plus exactly one extra sign S (inserted anywhere), on the same site.
Each such (S, P) is a candidate 'sign in place of picture'. A logogram S for P predicts the same S
recurs with P across DIFFERENT text types. Null: picture labels of the pictured texts permuted within
site x object type (5,000x); statistic = number of (S, P) pairs supported by >=2 distinct text types.
Also lists exact duplicates whose copies carry different pictures (picture-picture variation).
Run on ICIT (symbol field; copper excluded) and M77 (fs80; copper excluded).
"""
from common import *

rng = np.random.default_rng(5)
NOPIC_ICIT = {"None"}
UNKNOWN_ICIT = {"-", "?", "Unknown", "Misc", "MISC"}


def records(src):
    out = []
    if src == "ICIT":
        for t in icit_texts():
            if t["type"] == "TAB:C" or "#" in t["seq"] or t["symbol"] in UNKNOWN_ICIT:
                continue
            pic = None if t["symbol"] in NOPIC_ICIT else t["symbol"].split(":")[0]
            out.append(dict(seq=tuple(s for s in t["seq"] if s != "|"), pic=pic, site=t["site"], ot=t["type"].split(":")[0]))
    else:
        for t in m77_texts():
            if t["object_type"] == "copper tablet" or "#" in t["seq"] or t["fs80"] == 999:
                continue
            out.append(dict(seq=tuple(s for s in t["seq"] if s != "|"), pic=t["fs80"] or None, site=t["site"], ot=t["object_type"]))
    return out


def m77_class(fs):
    if fs is None: return None
    return fs // 10 * 10 if fs < 361 else fs  # merge orientation/cult-object variants of one animal (11-17 -> 10, ...)


def find_pairs(recs, pickey):
    pictured = defaultdict(set)   # (site, seq) -> pictures
    unpictured = defaultdict(set)
    for r in recs:
        (pictured if r["pic"] else unpictured)[(r["site"], r["seq"])].add(pickey(r["pic"]) if r["pic"] else None)
    pairs = []
    unp_by_site = defaultdict(list)
    for (site, seq) in unpictured:
        unp_by_site[site].append(seq)
    for (site, T), pics in pictured.items():
        if len(T) < 2:
            continue
        for T2 in unp_by_site[site]:
            if len(T2) != len(T) + 1:
                continue
            for i in range(len(T2)):
                if T2[:i] + T2[i + 1:] == T:
                    for P in pics:
                        pairs.append(dict(site=site, T=" ".join(T), T2=" ".join(T2), S=T2[i], pos=i, P=P))
                    break
    return pairs


def main():
    R = {}
    for src in ("ICIT", "M77"):
        recs = records(src)
        key = (lambda p: p) if src == "ICIT" else m77_class
        pairs = find_pairs(recs, key)
        sp = defaultdict(set)
        for p in pairs:
            sp[(p["S"], p["P"])].add(p["T"])
        multi = {k: v for k, v in sp.items() if len(v) >= 2}
        # null: permute pictures among pictured records within site x object type
        def stat(recs_perm):
            pp = find_pairs(recs_perm, key)
            d = defaultdict(set)
            for p in pp: d[(p["S"], p["P"])].add(p["T"])
            return sum(len(v) >= 2 for v in d.values())
        obs = len(multi)
        strata = defaultdict(list)
        for i, r in enumerate(recs):
            if r["pic"]: strata[(r["site"], r["ot"])].append(i)
        null = []
        for _ in range(300):
            rp = [dict(r) for r in recs]
            for idx in strata.values():
                perm = rng.permutation(idx)
                for a, b in zip(idx, perm): rp[a]["pic"] = recs[b]["pic"]
            null.append(stat(rp))
        null = np.array(null); p = (1 + (null >= obs).sum()) / (len(null) + 1)
        print(f"\n{src}: {len(pairs)} picture->sign minimal pairs (T with picture P; T+S without picture), "
              f"{len(sp)} distinct (S,P); supported by >=2 text types: {obs} (null mean {null.mean():.1f}, p={p:.3f})")
        top = sorted(sp.items(), key=lambda z: -len(z[1]))[:12]
        for (S, P), Ts in top:
            print(f"   S={S:5s} P={str(P):10s} text types {len(Ts)}: {sorted(Ts)[:4]}")
        # S position profile: is S added at the start/end (detached sign) or inside?
        pos = Counter("end" if p["pos"] == len(p["T2"].split()) - 1 else ("start" if p["pos"] == 0 else "inside") for p in pairs)
        print(f"   position of the extra sign: {dict(pos)}")
        # exact duplicates with different pictures
        dup = defaultdict(set)
        for r in recs:
            if r["pic"] and len(r["seq"]) >= 3: dup[(r["site"], r["seq"])].add(key(r["pic"]))
        dd = {k: v for k, v in dup.items() if len(v) > 1}
        print(f"   texts (>=3 signs) with copies carrying different pictures: {len(dd)} of "
              f"{sum(1 for k in dup)}; e.g. {[(' '.join(k[1]), sorted(map(str, v))) for k, v in list(dd.items())[:5]]}")
        R[src] = dict(n_pairs=len(pairs), n_sp=len(sp), multi_obs=obs, null_mean=float(null.mean()), p=float(p),
                      top=[dict(S=S, P=str(P), n_types=len(Ts), types=sorted(Ts)) for (S, P), Ts in top],
                      positions=dict(pos), diff_picture_dups=len(dd), dups=len(dup))
    save_json("l4_variant_copies", R)


if __name__ == "__main__":
    main()
