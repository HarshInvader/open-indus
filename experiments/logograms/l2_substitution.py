"""L2. Picture <-> sign substitution on copper tablets, with nulls.

Reads the per-tablet table written by l1 (copper_tablets.csv). Unit of evidence: the exact legend
(after Wells->Mahadevan normalisation) and the legend family; M77 and ICIT are analysed separately and
together (they overlap: many objects are in both).

Tests
 T1 slot exclusivity: a one-sign face and a picture never share a tablet.
 T2 substitution: legends that occur both with a picture P and with a one-sign face S (the S=P candidates).
 T3 consistency: within a legend, is the one-sign face always the same sign (family)? Null: sign-face
    labels permuted among sign-face tablets (10,000x).
 T4 do sign faces prefer legends that are otherwise pictured? Fisher / permutation over families.
 T5 one sign, one picture?  For each sign family: the set of pictures of its partner legends.
 T6 iconic class test: 'frontal horned head' signs (M346 + horned-U family M362-M364) pair only with
    legends whose picture is a horned being; chance = share of pictured legend families whose picture
    is horned. M355 (horned U with wheel) is reported separately because it is a horned-U variant in
    Mahadevan's drawing but pairs with the hare (counterexample).
"""
from common import *
from scipy.stats import fisher_exact

rng = np.random.default_rng(7)
HORNED_PICS = {"unicorn", "short-horned bull", "buffalo", "horned tiger", "rhinoceros",
               "goat-antelope (horns arching back)", "goat-antelope (twirled horns)", "ox-antelope (short horns)",
               "ox-antelope (long curly horns)", "horned archer personage", "composite animal", "bull (ICIT)",
               "ox-antelope/gaur (ICIT Gaur)", "goat-antelope (twirled horns)"}
HORNLESS = {"hare", "elephant", "tiger", "endless knot", "double-axe"}
SIGNFAM = lambda s: "horned-U (M362/M363/M364)" if s in HORNED_U else s


def load():
    return list(csv.DictReader(open(OUT / "copper_tablets.csv")))


def main():
    T = load()
    R = {}
    # T1
    for src in ("M77", "ICIT"):
        k = Counter(t["kind"] for t in T if t["source"] == src)
        R[f"T1_{src}"] = dict(k)
    print("T1 kinds (no tablet has both a picture and a one-sign face):", R["T1_M77"], R["T1_ICIT"])

    # T2: exact legends with both picture and sign face
    ex = defaultdict(lambda: dict(pics=Counter(), signs=Counter(), src=Counter(), fam=None))
    for t in T:
        L = t["legend"]
        if not L or "#" in L.split():
            continue
        e = ex[L]; e["fam"] = t["family"]
        if t["picture"] and not t["picture"].startswith("other") and t["picture"] != "unknown":
            e["pics"][t["picture"]] += 1
        elif t["picture"]:
            e["pics"]["(ICIT 'Othr' picture)"] += 1
        if t["sign_face"]:
            e["signs"][SIGNFAM(t["sign_face"])] += 1
        e["src"][t["source"]] += 1
    print("\nT2 exact legends carrying a one-sign face (and their pictures on other tablets):")
    subs = []
    for L, e in sorted(ex.items(), key=lambda z: z[1]["fam"]):
        if e["signs"]:
            print(f"  {e['fam']} {L:42s} signs={dict(e['signs'])}  pictures={dict(e['pics'])}")
            subs.append(dict(legend=L, family=e["fam"], signs=dict(e["signs"]), pictures=dict(e["pics"])))
    R["T2_sign_face_legends"] = subs

    # T3 consistency within exact legend (and within family), per source
    for src in ("M77", "ICIT", "both"):
        sf = [(t["legend"], SIGNFAM(t["sign_face"])) for t in T if t["sign_face"] and (src == "both" or t["source"] == src)]
        legs = np.array([a for a, b in sf]); labs = np.array([b for a, b in sf])
        groups = [np.where(legs == L)[0] for L in set(legs)]
        groups = [g for g in groups if len(g) >= 2]
        def homog(lb):
            return sum(len(set(lb[g])) == 1 for g in groups)
        obs = homog(labs)
        null = np.array([homog(rng.permutation(labs)) for _ in range(10000)])
        p = (1 + (null >= obs).sum()) / 10001
        R[f"T3_{src}"] = dict(n_tablets=len(sf), legends_with_2plus=len(groups), homogeneous=obs,
                             null_mean=float(null.mean()), p=float(p))
        print(f"T3 {src}: {obs}/{len(groups)} legends with >=2 sign-face tablets always carry the same sign family "
              f"(null mean {null.mean():.2f}, p={p:.4f}; {len(sf)} tablets)")

    # T4: are sign-face families otherwise pictured more than other families? (families with >=2 tablets)
    fam = defaultdict(lambda: dict(pic=False, sign=False, n=0))
    for t in T:
        f = fam[t["family"]]; f["n"] += 1
        if t["picture"]: f["pic"] = True
        if t["sign_face"]: f["sign"] = True
    F = [f for k, f in fam.items() if f["n"] >= 2 and k != "F--"]
    a = sum(f["sign"] and f["pic"] for f in F); b = sum(f["sign"] and not f["pic"] for f in F)
    c = sum(not f["sign"] and f["pic"] for f in F); d = sum(not f["sign"] and not f["pic"] for f in F)
    orr, p = fisher_exact([[a, b], [c, d]], alternative="greater")
    R["T4"] = dict(signface_pictured=a, signface_unpictured=b, other_pictured=c, other_unpictured=d, odds=orr, p=p)
    print(f"T4 families (>=2 tablets): with sign face {a} pictured / {b} not; without {c} / {d}; Fisher p={p:.3f}")

    # T5 sign family -> pictures of its partner legends
    s2p = defaultdict(lambda: defaultdict(Counter))
    for s in subs:
        for sg in s["signs"]:
            for pc, n in s["pictures"].items():
                s2p[sg][s["family"]][pc] += n
    print("\nT5 sign family -> pictures of partner legends (by legend family):")
    R["T5"] = {}
    for sg, d in s2p.items():
        print(f"  {sg:28s} " + "; ".join(f"{f}: {dict(c)}" for f, c in d.items()))
        R["T5"][sg] = {f: dict(c) for f, c in d.items()}

    # T6 iconic class test on legend families (M77 fs80 pictures only, to avoid ICIT's coarse labels)
    fam_pic = defaultdict(Counter)
    for t in T:
        if t["source"] == "M77" and t["picture"]:
            fam_pic[t["family"]][t["picture"]] += 1
    maj = {f: c.most_common(1)[0][0] for f, c in fam_pic.items()}
    pictured = [f for f in maj if maj[f] in HORNED_PICS | HORNLESS]
    rate = np.mean([maj[f] in HORNED_PICS for f in pictured])
    head_fams = sorted({t["family"] for t in T if t["sign_face"] in HORNED_U | {"M346"} and t["family"] in maj})
    k = sum(maj[f] in HORNED_PICS for f in head_fams)
    from scipy.stats import binom
    p6 = binom.sf(k - 1, len(head_fams), rate)
    R["T6"] = dict(pictured_families=len(pictured), share_horned=float(rate), head_sign_families=head_fams,
                   horned=k, p=float(p6), counterexample="M355 (horned U + wheel) pairs with the hare legend (ICIT M-593, M-1547)")
    print(f"\nT6 'horned frontal head' sign faces sit on {len(head_fams)} pictured families {head_fams}; "
          f"{k} have a horned picture; base rate {rate:.2f} over {len(pictured)} pictured families; binomial p={p6:.3f}")
    print("   counterexample: M355/W753 (horned U with wheel) is the sign face of the HARE legend.")
    # T7 copper minimal pairs: exact legends at edit distance 1, with their (M77 fs80) pictures
    lp = defaultdict(Counter)
    for t in T:
        L = t["legend"]
        if t["source"] == "M77" and t["picture"] and L and "#" not in L.split():
            lp[L][t["picture"]] += 1
    Ls = sorted(lp)
    print("\nT7 copper minimal pairs (exact legends at edit distance 1, M77 pictures):")
    mp = []
    for i, a in enumerate(Ls):
        for b in Ls[i + 1:]:
            A, B = a.split(), b.split()
            if lev(A, B) == 1:
                same = lp[a].most_common(1)[0][0] == lp[b].most_common(1)[0][0]
                mp.append(dict(a=a, b=b, pics_a=dict(lp[a]), pics_b=dict(lp[b]), same_picture=same))
                print(f"  {'SAME' if same else 'DIFF'}  {a:40s} {dict(lp[a])}\n        {b:40s} {dict(lp[b])}")
    R["T7_minimal_pairs"] = mp
    # within-legend picture variation (one legend, several pictures)
    multi = {L: dict(c) for L, c in lp.items() if len(c) > 1}
    print("  legends with more than one picture class:", multi)
    R["T7_multi_picture_legends"] = multi
    save_json("l2_substitution", R)


if __name__ == "__main__":
    main()
