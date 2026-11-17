"""Q4b. Do the foreign (Gulf/West Asian) round-seal texts share an INTERNAL order structure of their own?
Statistic: number of ordered sign bigrams that occur in >= 2 distinct foreign round texts.
Null: signs shuffled within each text (keeps each text's sign multiset), 20,000x.
Comparison: the same statistic for random sets of home round seals of the same lengths (scale reference).
"""
from common import *
from q4_gulf import FOREIGN_WEST, FOREIGN_CA, clean

rng = np.random.default_rng(44)


def shared(texts):
    c = Counter()
    for t in texts:
        c.update({(a, b) for a, b in zip(t, t[1:])})
    return sum(1 for v in c.values() if v >= 2), [k for k, v in c.items() if v >= 2]


def test(texts, label, n=20000):
    obs, which = shared(texts)
    null = np.array([shared([list(rng.permutation(t)) for t in texts])[0] for _ in range(n)])
    p = (1 + (null >= obs).sum()) / (n + 1)
    print(f"  {label:38s} n={len(texts):3d} shared ordered bigrams {obs} vs within-text-shuffle null {null.mean():.2f} (p={p:.4f}) {which[:8]}")
    return dict(n=len(texts), obs=obs, null=float(null.mean()), p=float(p), bigrams=[" ".join(b) for b in which])


def main():
    I = icit_texts()
    seen = set(); fr, hr = [], []
    for t in I:
        s = clean(t["seq"])
        if len(s) < 2 or t["type"] not in ("SEAL:R", "SEAL:C", "SEAL:CY"): continue
        k = (t["site"] in FOREIGN_WEST | FOREIGN_CA, " ".join(s))
        if k in seen: continue
        seen.add(k)
        if t["site"] in FOREIGN_WEST | FOREIGN_CA: fr.append(s)
        elif t["site"] != "Unknown": hr.append(s)
    R = {"foreign_round": test(fr, "foreign round seals")}
    # reference: random home-round subsets of same size and lengths
    vals = []
    for _ in range(200):
        pick = [hr[i] for i in rng.choice(len(hr), len(fr), replace=False)]
        o, _ = shared(pick)
        nu = np.mean([shared([list(rng.permutation(t)) for t in pick])[0] for _ in range(200)])
        vals.append(o - nu)
    R["home_round_excess_mean"] = float(np.mean(vals)); R["home_round_excess_q"] = [float(np.quantile(vals, .05)), float(np.quantile(vals, .95))]
    print(f"  home round seals, same n: excess shared bigrams over shuffle null mean {np.mean(vals):.2f} (90% {np.quantile(vals,.05):.2f}..{np.quantile(vals,.95):.2f})")
    save_json("q4b_gulf_internal", R)


if __name__ == "__main__":
    main()
