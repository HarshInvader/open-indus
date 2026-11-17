"""Q6. Do stroke numerals follow the Indus weight system (binary 1,2,4,8,16,32,64 then 160,200,320,640)?

Within the attested stroke range (short 1-12, tall 1-5) the weight-series values are 1,2,4,8.
Statistic per value v: local excess E(v) = log(c_v+.5) - mean(log(c_{v-1}+.5), log(c_{v+1}+.5)) (a spike
above its neighbours; 0 for any smooth log-linear distribution). CI by bootstrap over distinct texts
(5000x). Short 2 (M99/100) is excluded as a connective (STATE F7), so short binary tests are v=4 and 8.
Also: in texts with two numerals, is their ratio a power of two more often than for numerals paired at
random (within object type)? Unit: distinct texts per object type (M77), replication on ICIT.
"""
from common import *

rng = np.random.default_rng(6)


def values(seq, short, tall):
    return [("S", short[x]) for x in signs(seq) if x in short] + [("T", tall[x]) for x in signs(seq) if x in tall]


def excess(counts, v):
    c = lambda k: np.log(counts.get(k, 0) + .5)
    return c(v) - (c(v - 1) + c(v + 1)) / 2


def analyse(texts, short, tall, label):
    R = {}
    vals = [values(t, short, tall) for t in texts]
    for cls, vs, rng_ in (("short", [3, 4, 5, 6, 7, 8], range(1, 13)), ("tall", [2, 3, 4], range(1, 6))):
        C = Counter(v for vv in vals for c, v in vv if c == cls[0].upper())
        obs = {v: excess(C, v) for v in vs}
        boots = {v: [] for v in vs}
        n = len(vals)
        for _ in range(5000):
            idx = rng.integers(n, size=n)
            Cb = Counter(v for i in idx for c, v in vals[i] if c == cls[0].upper())
            for v in vs: boots[v].append(excess(Cb, v))
        R[cls] = dict(counts={int(k): int(C.get(k, 0)) for k in rng_},
                      excess={int(v): dict(obs=float(obs[v]), ci=[float(np.quantile(boots[v], .025)), float(np.quantile(boots[v], .975))],
                                           binary=v in (1, 2, 4, 8, 16)) for v in vs})
        print(f"  [{label}] {cls} counts: {R[cls]['counts']}")
        for v in vs:
            e = R[cls]["excess"][v]
            print(f"     v={v:2d} {'(weight-series)' if e['binary'] else '               '} local excess {e['obs']:+.2f} [95% CI {e['ci'][0]:+.2f}, {e['ci'][1]:+.2f}]")
    # ratio test
    pairs = [(sorted([a[1], b[1]])) for vv in vals if len(vv) == 2 for a, b in [vv]]
    def p2(a, b):
        r = b / a
        return r == int(r) and r > 1 and (int(r) & (int(r) - 1)) == 0
    obs = np.mean([p2(a, b) for a, b in pairs]) if pairs else np.nan
    flat = [v for vv in vals for _, v in vv]
    null = [np.mean([p2(*sorted(rng.choice(flat, 2))) for _ in pairs]) for _ in range(2000)] if pairs else [np.nan]
    p = (1 + sum(x >= obs for x in null)) / 2001
    R["pairs"] = dict(n=len(pairs), pow2_ratio_share=float(obs), null=float(np.mean(null)), p=float(p))
    print(f"     texts with exactly 2 numerals: {len(pairs)}; ratio a power of 2 in {obs:.2f} vs random pairing {np.mean(null):.2f} (p={p:.3f})")
    return R


def main():
    R = {}
    T = m77_texts()
    by = defaultdict(set)
    for t in T: by[t["object_type"]].add(" ".join(t["seq"]))
    allt = []
    for ty, S in by.items(): allt += [s.split() for s in S]
    R["m77_all"] = analyse(allt, M_SHORT, M_TALL, "M77 all objects (distinct per type)")
    for ty in ("seal", "sealing", "miniature tablet", "pottery graffito", "copper tablet"):
        R[f"m77_{ty}"] = analyse([s.split() for s in by[ty]], M_SHORT, M_TALL, f"M77 {ty}")
    I = icit_texts()
    byi = defaultdict(set)
    for t in I: byi[t["type"].split(":")[0]].add(" ".join(t["seq"]))
    alli = [s.split() for S in byi.values() for s in S]
    R["icit_all"] = analyse(alli, W_SHORT, W_TALL, "ICIT all objects")
    R["icit_POT"] = analyse([s.split() for s in byi["POT"]], W_SHORT, W_TALL, "ICIT pottery")
    save_json("q6_metrology", R)


if __name__ == "__main__":
    main()
