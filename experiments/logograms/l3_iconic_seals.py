"""L3. Iconic agreement on seals/sealings/tablets (copper excluded, it is L1/L2's data).

Question: is a pictorial sign over-represented in texts on objects whose picture shows the same thing?
Pairs are PRE-REGISTERED below (fixed before running). Unit: distinct (text, picture-class) within a
site x object-type stratum; only objects WITH a picture are used, so the comparison is 'picture P vs
other pictures'. Null: picture labels permuted within site x object-type strata (exact: sum of
per-stratum hypergeometrics, Monte-Carlo 20,000x). One-sided (over-representation). BH over all tests.
M77 uses fs80 codes; ICIT uses its `symbol` field with Wells signs mapped through the bridge.
Then an exploratory scan: every sign in >=5 distinct pictured texts x every non-animal picture group.
"""
from common import *

rng = np.random.default_rng(11)
rng_l = lambda a, b: set(range(a, b + 1))

HORNED_PERSONAGE_FS = {470, 480, 511, 512, 520, 530, 670, 680, 770, 780, 810}
PAIRS = [  # name, sign set (Mahadevan), M77 fs80 set, ICIT symbols
    ("fish signs ~ gharial/fish pictures", {f"M{i}" for i in (59, 60, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75)},
     rng_l(361, 371), {"Fish", "Gavi"}),
    ("pipal leaf M326/M327 ~ tree/leaf/pipal pictures", {"M326", "M327"}, rng_l(441, 460) | {502, 770, 780}, {"Pipal", "Phyt"}),
    ("human figure signs M1-M44 ~ anthropomorphic/scenes", {f"M{i}" for i in range(1, 45)}, rng_l(470, 810), {"Anth", "Scene"}),
    ("horned-U M355/M362-M364 ~ horned personage", {"M355", "M362", "M363", "M364"}, HORNED_PERSONAGE_FS, {"Anth"}),
    ("horned man M8 ~ horned personage", {"M8"}, HORNED_PERSONAGE_FS, {"Anth"}),
    ("bow-man M27-M29 ~ archer/weapon scenes", {"M27", "M28", "M29"}, {520, 550, 630, 640, 650}, {"Anth", "Scene"}),
    ("bird signs M76-M83 ~ bird pictures", {f"M{i}" for i in range(76, 84)}, {431}, {"Bird"}),
    ("quadruped signs M50/M183-M185 ~ any animal", {"M50", "M183", "M184", "M185"}, rng_l(11, 352), None),
    ("svastika M148 ~ svastika pictures", {"M148"}, {443, 821, 822}, {"Swas"}),
    ("branch signs M166-M168 ~ kino tree / tree scenes", {"M166", "M167", "M168"}, rng_l(441, 444) | rng_l(730, 760), {"Phyt"}),
]
GROUPS_M77 = {"fish/gharial": rng_l(361, 371), "trees/leaves": rng_l(441, 460), "anthropomorphic": rng_l(470, 599),
              "scenes": rng_l(600, 810), "cult object": {851, 852}, "geometric/motifs": rng_l(821, 988) - {851, 852}}
ANIMAL_ICIT_EXCL = {"None", "-", "?", "Unknown", "Misc", "MISC"}


def m2w():
    rev = defaultdict(set)
    for k, v in BRIDGE.items():
        for m in v["M"]:
            rev[f"M{m}"].add(f"W{int(k):03d}")
    return rev


def items_m77():
    out = set()
    for t in m77_texts():
        if t["object_type"] == "copper tablet" or t["fs80"] in (0, 999, None):
            continue
        out.add((" ".join(t["seq"]), t["fs80"], t["site"], t["object_type"]))
    return [dict(seq=a.split(), pic=b, stratum=f"{c}|{d}") for a, b, c, d in out]


def items_icit():
    out = set()
    for t in icit_texts():
        if t["type"] == "TAB:C" or t["symbol"] in ANIMAL_ICIT_EXCL:
            continue
        out.add((" ".join(t["seq"]), t["symbol"], t["site"], t["type"].split(":")[0]))
    return [dict(seq=a.split(), pic=b, stratum=f"{c}|{d}") for a, b, c, d in out]


def test(items, has_sign, is_pic, nperm=20000):
    x = np.array([has_sign(i) for i in items]); y = np.array([is_pic(i) for i in items])
    st = np.array([i["stratum"] for i in items])
    obs = int((x & y).sum())
    # expected and Monte Carlo under within-stratum permutation of picture labels
    exp = 0.0; sims = np.zeros(nperm)
    for s in np.unique(st):
        idx = st == s
        N, K, n = idx.sum(), y[idx].sum(), x[idx].sum()
        if K == 0 or n == 0:
            continue
        exp += n * K / N
        sims += rng.hypergeometric(K, N - K, n, size=nperm)
    p = (1 + (sims >= obs).sum()) / (nperm + 1)
    return dict(obs=obs, exp=round(exp, 2), n_sign=int(x.sum()), n_pic=int(y.sum()), n=len(items), p=float(p))


def main():
    R = dict(prereg=[], scan=[])
    rev = m2w()
    I77, IIC = items_m77(), items_icit()
    print(f"distinct pictured texts (copper excluded): M77 {len(I77)}, ICIT {len(IIC)}")
    rows = []
    for name, S, FS, SYM in PAIRS:
        r1 = test(I77, lambda i: bool(S & set(i["seq"])), lambda i: i["pic"] in FS)
        rows.append(("M77", name, r1))
        WS = set().union(*[rev.get(s, set()) for s in S])
        if SYM is None:
            sym_is = lambda i: not i["pic"] in {"Fish", "Pipal", "Phyt", "Anth", "Scene", "Bird", "Swas", "Cros", "Xcrs",
                                                "Maze", "Tri4", "Xhch", "X", "Crs", "T", "Box", "Strokes", "Beye", "S590",
                                                "T-A-T", "T-M-T"}
        else:
            sym_is = lambda i, SYM=SYM: i["pic"] in SYM
        if WS:
            r2 = test(IIC, lambda i: bool(WS & set(i["seq"])), sym_is)
            r2["wells_signs"] = sorted(WS)
            rows.append(("ICIT", name, r2))
    q = bh([r["p"] for _, _, r in rows])
    print(f"\nPre-registered iconic pairs ({len(rows)} tests, BH):")
    for (src, name, r), qq in zip(rows, q):
        r["q"] = float(qq)
        print(f"  {src:4s} {name:52s} obs {r['obs']:3d} exp {r['exp']:6.2f} (texts with sign {r['n_sign']}, with picture {r['n_pic']}) p={r['p']:.4f} q={qq:.3f}")
        R["prereg"].append(dict(source=src, pair=name, **r))

    # exploratory scan (M77): every sign in >=5 pictured texts x non-animal picture group
    cnt = Counter(s for i in I77 for s in set(signs(i["seq"])))
    cand = [s for s, n in cnt.items() if n >= 5]
    scan = []
    for g, FS in GROUPS_M77.items():
        if sum(i["pic"] in FS for i in I77) < 5:
            continue
        for s in cand:
            r = test(I77, lambda i, s=s: s in i["seq"], lambda i, FS=FS: i["pic"] in FS, nperm=4000)
            if r["obs"] >= 2:
                scan.append(dict(sign=s, group=g, **r))
    ntests = len(cand) * sum(1 for g, FS in GROUPS_M77.items() if sum(i["pic"] in FS for i in I77) >= 5)
    ps = [r["p"] for r in scan] + [1.0] * (ntests - len(scan))  # untested (obs<2) cells count as p=1
    qs = bh(ps)[:len(scan)]
    for r, qq in zip(scan, qs):
        r["q"] = float(qq)
    scan.sort(key=lambda r: r["p"])
    print(f"\nExploratory scan M77: {ntests} sign x group tests; top 12:")
    for r in scan[:12]:
        print(f"  {r['sign']:5s} {r['group']:16s} obs {r['obs']:3d} exp {r['exp']:5.2f} p={r['p']:.4f} q={r['q']:.3f}")
    R["scan"] = scan[:30]; R["scan_ntests"] = ntests
    save_json("l3_iconic_seals", R)


if __name__ == "__main__":
    main()
