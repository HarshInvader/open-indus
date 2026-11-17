"""Post-hoc (exploratory, not pre-registered): (a) power of the calibrated robust statistic T itself,
by planting a final-share shift of +0.2 / +0.5 on every derived form at the observed token counts and
comparing with the one-sided 95th percentile of that family's fake-modifier null; (b) partner-class
shift consistency (sign-flip over bases, mean pairwise cosine of left+right role-class difference
vectors) in held-out and ICIT."""
import json, sys, zlib
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import *  # noqa
import m6_confirm as m6


def null_T(g, P, f, n_fake, seed):
    """Return the fake-modifier null distribution of T (same construction as calibrated_test)."""
    rng = np.random.default_rng(seed)
    pool = np.array(freq_pool(P, 1)); pn = np.array([P[s]["n"] for s in pool])
    def cands(n):
        lo, hi = 0.5, 2.0
        while True:
            idx = np.where((pn >= n * lo) & (pn <= n * hi))[0]
            if len(idx) >= 8 or lo < 0.01:
                return idx
            lo /= 1.5; hi *= 1.5
    struct = [(cands(P[b]["n"]), [cands(P[d]["n"]) for d in ds]) for b, ds in g.items()]
    Ts = []
    for _ in range(n_fake):
        used, gg = set(), {}
        for cb, cds in struct:
            b = pool[rng.choice(cb)]
            while b in used:
                b = pool[rng.choice(cb)]
            used.add(b); ds = []
            for cd in cds:
                d = pool[rng.choice(cd)]; t = 0
                while d in used and t < 50:
                    d = pool[rng.choice(cd)]; t += 1
                used.add(d); ds.append(d)
            gg[b] = ds
        Ts.append(robust_T(robust(gg, P, f)))
    return np.array(Ts)


def T_power(g, P, shift, crit, n_sim=400, seed=0):
    rng = np.random.default_rng(seed); hits = 0
    for _ in range(n_sim):
        Q = {}
        for b, ds in g.items():
            pb = feat(P[b], "final")
            Q[b] = {"n": P[b]["n"], "final": rng.binomial(P[b]["n"], pb)}
            for d in ds:
                Q[d] = {"n": P[d]["n"], "final": rng.binomial(P[d]["n"], min(1.0, pb + shift))}
        hits += robust_T(robust(g, Q, "final")) >= crit
    return hits / n_sim


def main():
    sets = {"heldout_v2": (m77_corpus("heldout"), load_pairs(HERE / "decomp_frozen.csv")),
            "icit_all": (icit_corpus(False), load_pairs(HERE / "w_decomp.csv")),
            "dev": (m77_corpus("dev"), load_pairs(HERE / "decomp_frozen.csv"))}
    out = {}
    for s, (C, pairs) in sets.items():
        P = profiles(C); out[s] = {}
        for m, pr in m6.groups_for(pairs).items():
            g = by_base(usable(pr, P, 1))
            if len(g) < 3:
                continue
            Ts = null_T(g, P, "final", 1000, zlib.crc32((s + m).encode()))
            crit = float(np.percentile(Ts, 95))
            rec = {"k": len(g), "crit_T_one_sided_95": crit,
                   "T_power_+0.2": T_power(g, P, 0.2, crit), "T_power_+0.5": T_power(g, P, 0.5, crit)}
            g2 = by_base(usable(pr, P, 2))
            if len(g2) >= 3:
                r = signflip_test(g2, P)
                rec.update(partner_k=r["k"], partner_cos=r["obs"]["partner_cos"], partner_p=r["p"]["partner_cos"],
                           partner_jsd=r["obs"]["jsd"])
            out[s][m] = rec
            print(s, m.ljust(18), {k: (round(v, 3) if isinstance(v, float) else v) for k, v in rec.items()})
    json.dump(out, open(HERE / "power_partners.json", "w"), indent=1)


if __name__ == "__main__":
    main()
