"""Calibrate the 'consistent modifier' decision rule on fake modifiers (dev).
Rule (dev strength): |CMH z| >= 2.58, leave-one-base-out worst z same sign and |z| >= 1.96,
and >= 2/3 of bases with a difference shift the same way.
Fake modifiers: k bases; derived = random sign. 'rarity' = derived has 0.05-0.5x base tokens
(real pairs: median derived/base token ratio is about 0.1-0.3)."""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import *  # noqa


def rule(r, zc=2.58, zl=1.96):
    s = np.sign(r["z"])
    tot = r["up"] + r["down"]
    maj = (r["up"] if s > 0 else r["down"]) >= (2 / 3) * tot if tot else False
    return abs(r["z"]) >= zc and r["loo_worst_z"] * s >= zl and maj


def main():
    P = profiles(m77_corpus("dev"))
    pool = freq_pool(P, 1)
    big = [s for s in pool if P[s]["n"] >= 5]
    rng = np.random.default_rng(11)
    out = {}
    for rar in (False, True):
        for k in (4, 7, 11):
            hits = {f: 0 for f in ("final", "init")}
            hits_conf = {f: 0 for f in ("final", "init")}
            N = 1000
            for _ in range(N):
                bases = list(rng.choice(big, k, replace=False)); g = {}
                for b in bases:
                    nb = P[b]["n"]
                    c = [s for s in pool if (0.05 * nb <= P[s]["n"] <= 0.5 * nb if rar else True) and s not in bases]
                    c = c or [s for s in pool if s not in bases]
                    g[b] = [c[rng.integers(len(c))]]
                for f in hits:
                    r = robust(g, P, f)
                    hits[f] += rule(r)
                    hits_conf[f] += rule(r, 1.645, 0.0)
            out[f"rarity={rar},k={k}"] = {"dev_rule_fpr": {f: v / N for f, v in hits.items()},
                                          "confirm_rule_fpr(two directions)": {f: v / N for f, v in hits_conf.items()}}
            print(f"rarity={rar} k={k}", out[f"rarity={rar},k={k}"])
    # real pairs token ratio
    pairs = [p for p in load_pairs(HERE / "decomp_frozen.csv") if p[3] in ("high", "medium")]
    rat = [P[d]["n"] / P[b]["n"] for d, b, *_ in pairs if P[d]["n"] and P[b]["n"]]
    out["real_ratio_quartiles"] = list(np.percentile(rat, [25, 50, 75]))
    print("real derived/base token ratio quartiles", out["real_ratio_quartiles"])
    json.dump(out, open(HERE / "rule_fpr.json", "w"), indent=1)


if __name__ == "__main__":
    main()
