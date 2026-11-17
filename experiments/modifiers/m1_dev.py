"""Dev exploration: every modifier with >= 3 usable bases (exact sign-flip test over bases),
positive control (ticks), negative controls (random and rarity-matched fake modifiers)."""
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import fisher_exact

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import *  # noqa


def pair_table(u, P):
    rows = []
    for d, b, m, c, fam in u:
        pd, pb = P[d], P[b]
        fe = fisher_exact([[pd["final"], pd["n"] - pd["final"]], [pb["final"], pb["n"] - pb["final"]]])[1]
        rows.append({"derived": d, "base": b, "n_d": pd["n"], "n_b": pb["n"],
                     **{f"{f}_d": round(feat(pd, f), 3) for f in FEATS},
                     **{f"{f}_b": round(feat(pb, f), 3) for f in FEATS}, "final_fisher_p": fe})
    return rows


def run_family(pairs, P, label, conf=("high", "medium")):
    pr = [p for p in pairs if p[3] in conf]
    u = usable(pr, P)
    g = by_base(u)
    rec = {"modifier": label, "pairs_listed": len(pr), "pairs_usable": len(u), "bases": len(g),
           "pairs": pair_table(u, P)}
    if len(g) < MIN_BASES:
        rec["tested"] = False
        return rec
    r = signflip_test(g, P)
    rec.update(tested=True, k=r["k"], p=r["p"], min_attainable_p=r["min_attainable_p"],
               obs={k: v for k, v in r["obs"].items()})
    return rec


def fake_control(P, k, n_fake, rarity, seed):
    rng = np.random.default_rng(seed)
    pool = freq_pool(P, MIN_TOK)
    big = [s for s in pool if P[s]["n"] >= 10]
    fp = {f: 0 for f in FEATS + ["partner_cos"]}
    allsame = 0
    for i in range(n_fake):
        if rarity:
            bases = list(rng.choice(big, k, replace=False)); g = {}
            for b in bases:
                nb = P[b]["n"]
                c = [s for s in pool if 0.1 * nb <= P[s]["n"] <= 0.6 * nb and s not in bases and s not in g.values()]
                if not c:
                    c = [s for s in pool if P[s]["n"] < nb and s not in bases]
                g[b] = [c[rng.integers(len(c))]]
        else:
            ch = rng.choice(len(pool), 2 * k, replace=False)
            g = {pool[ch[2 * j + 1]]: [pool[ch[2 * j]]] for j in range(k)}
        r = signflip_test(g, P)
        for f in fp:
            fp[f] += r["p"][f] < 0.05
        o = r["obs"]
        allsame += o["final_pos"] in (0, k) and o["final_neg"] in (0, k)
    return {"k": k, "n": n_fake, "rarity_matched": rarity,
            "fpr_p<0.05": {f: v / n_fake for f, v in fp.items()}, "share_all_same_final_direction": allsame / n_fake}


def main():
    C = m77_corpus("dev")
    P = profiles(C)
    pairs = load_pairs(HERE / "decomp_frozen.csv")
    mods = sorted({p[2] for p in pairs})
    out = {"n_texts_dev": len(C), "min_tok": MIN_TOK, "families": []}
    for m in mods:
        out["families"].append(run_family([p for p in pairs if p[2] == m], P, m))
    extra = {
        "TICKS_ANY": lambda p: p[2] in ("TICKS4", "PAIRTICKS4"),
        "TICKS4_fish": lambda p: p[2] == "TICKS4" and p[4] == "fish",
        "TICKS4_nonfish": lambda p: p[2] == "TICKS4" and p[4] != "fish",
        "TICKS_ANY_nonfish": lambda p: p[2] in ("TICKS4", "PAIRTICKS4") and p[4] != "fish",
        "ENCLOSE_ANY_nonfish": lambda p: p[2] in ("TICKS4", "PAIRTICKS4", "BRACKET", "PAIRBARS", "RAYS4") and p[4] != "fish",
    }
    for lab, fn in extra.items():
        out["families"].append(run_family([p for p in pairs if fn(p)], P, lab))
    out["families"].append(run_family([p for p in pairs if p[2] == "TICKS4"], P, "TICKS4_allconf", conf=("high", "medium", "low")))

    tested = [f for f in out["families"] if f.get("tested") and f["modifier"] in mods]
    ps, keys = [], []
    for f in tested:
        for k in FEATS + ["partner_cos"]:
            ps.append(f["p"][k]); keys.append((f["modifier"], k))
    q = bh(ps)
    out["bh_dev"] = [{"modifier": m, "feature": k, "p": p, "q": float(qq)} for (m, k), p, qq in zip(keys, ps, q)]
    out["n_tests_dev"] = len(ps)
    out["negative_control"] = [fake_control(P, 7, 500, False, 1), fake_control(P, 7, 500, True, 2),
                               fake_control(P, 5, 500, True, 3)]
    json.dump(out, open(HERE / "dev_results.json", "w"), indent=1, default=float)

    print(f"dev texts {out['n_texts_dev']}")
    for f in out["families"]:
        if not f.get("tested"):
            print(f"{f['modifier']:20s} bases={f['bases']} usable={f['pairs_usable']}/{f['pairs_listed']}  NOT TESTED")
            continue
        o = f["obs"]
        s = "  ".join(f"{k}={o[k]:+.3f}({o[k+'_pos']}+/{o[k+'_neg']}-) p={f['p'][k]:.3f}" for k in FEATS)
        print(f"{f['modifier']:20s} k={f['k']} minp={f['min_attainable_p']:.3f} {s}  pcos={o['partner_cos']:+.2f} p={f['p']['partner_cos']:.3f}")
    print("tests:", out["n_tests_dev"], "BH q<0.2:", [(x["modifier"], x["feature"], round(x["q"], 3)) for x in out["bh_dev"] if x["q"] < 0.2])
    for nc in out["negative_control"]:
        print("negative control:", nc)
    for f in out["families"]:
        if f["modifier"] in ("TICKS4", "ROOF", "INSERT", "CANOPY", "COMB", "TICKS4_nonfish"):
            print(f["modifier"])
            for r in f["pairs"]:
                print("   ", r["derived"], "<-", r["base"], r["n_d"], r["n_b"], "final", r["final_d"], r["final_b"], "init", r["init_d"], r["init_b"], "p=%.3g" % r["final_fisher_p"])


if __name__ == "__main__":
    main()
