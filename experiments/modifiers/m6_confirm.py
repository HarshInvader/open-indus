"""Confirmation run (pre-registered in docs/prereg/modifiers.md). Do not edit after hashing.
Sets: M77 held-out v2 (decomp_frozen.csv); ICIT native Wells (w_decomp.csv), all sites;
ICIT sites absent from M77. Primary statistic: calibrated robust CMH T (common.calibrated_test)."""
import json
import zlib
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import *  # noqa

NF = 2000
CONF = ("high", "medium")
FEAT_SETS = ("final", "init", "seal")


def groups_for(pairs):
    pr = [p for p in pairs if p[3] in CONF]
    g = {m: [p for p in pr if p[2] == m] for m in sorted({p[2] for p in pr})}
    g["TICKS4_nonfish"] = [p for p in pr if p[2] == "TICKS4" and p[4] != "fish"]
    g["TICKS4_fish"] = [p for p in pr if p[2] == "TICKS4" and p[4] == "fish"]
    g["INSERT_container"] = [p for p in pr if p[2] == "INSERT" and p[4] in ("jar", "cup")]
    return g


PRIMARY = {  # pre-registered directional predictions
    "TICKS4": ("final", "up"),            # C1 positive control
    "TICKS4_nonfish": ("final", "up"),    # C2
    "CANOPY": ("final", "up"),            # C3
    "INSERT_container": ("final", "down"),  # C4
}


def run_set(name, corpus, pairs):
    P = profiles(corpus)
    res = {"n_texts": len(corpus), "families": {}}
    for m, pr in groups_for(pairs).items():
        u = usable(pr, P, 1)
        g = by_base(u)
        rec = {"k": len(g), "pairs": [f"{d}<-{b} ({P[d]['n']}/{P[b]['n']}, final {feat(P[d],'final'):.2f}/{feat(P[b],'final'):.2f})" for d, b, *_ in u]}
        if len(g) >= MIN_BASES:
            rec["tested"] = True
            for f in FEAT_SETS:
                rec[f] = calibrated_test(g, P, f, n_fake=NF, seed=zlib.crc32((name + m + f).encode()))
            for shift in (0.2, 0.5):
                rec[f"power_final_+{shift}"] = power_sim(g, P, shift, n_sim=1000)
        elif len(g) >= 1:
            rec["tested"] = False
            rec["cmh_final"] = cmh(g, P, "final")
            rec["power_final_+0.5"] = power_sim(g, P, 0.5, n_sim=1000)
        else:
            rec["tested"] = False
        res["families"][m] = rec
    # verdicts on primary predictions
    res["primary"] = {}
    for m, (f, d) in PRIMARY.items():
        rec = res["families"].get(m, {})
        if not rec.get("tested"):
            res["primary"][m] = {"verdict": "untestable (k<3)", "k": rec.get("k", 0)}
            continue
        r = rec[f]
        p = r["p_up"] if d == "up" else r["p_down"]
        res["primary"][m] = {"feature": f, "direction": d, "T": r["T"], "z": r["z"], "p_one_sided": p,
                             "up": r["up"], "down": r["down"], "k": rec["k"],
                             "verdict": "confirmed" if p < 0.05 else "not confirmed"}
    # paradigm family: every other main modifier, two-sided, BH
    keys, ps = [], []
    for m, rec in res["families"].items():
        if m in PRIMARY or m.endswith("_fish") or not rec.get("tested"):
            continue
        for f in FEAT_SETS:
            keys.append((m, f)); ps.append(rec[f]["p_two"])
    q = bh(ps) if ps else []
    res["paradigm_family"] = [{"modifier": m, "feature": f, "p_two": p, "q": float(x)} for (m, f), p, x in zip(keys, ps, q)]
    return res


def main():
    out = {}
    mp = load_pairs(HERE / "decomp_frozen.csv")
    wp = load_pairs(HERE / "w_decomp.csv")
    out["heldout_v2"] = run_set("heldout", m77_corpus("heldout"), mp)
    out["icit_all"] = run_set("icit", icit_corpus(False), wp)
    out["icit_newsites"] = run_set("icitnew", icit_corpus(True), wp)
    json.dump(out, open(HERE / "confirm_results.json", "w"), indent=1, default=float)
    for s, r in out.items():
        print(f"== {s}: {r['n_texts']} texts")
        for m, v in r["primary"].items():
            print("  PRIMARY", m, v)
        for m, rec in r["families"].items():
            if rec.get("tested"):
                print(f"  {m:18s} k={rec['k']:2d} " + "  ".join(
                    f"{f}: z={rec[f]['z']:+.1f} T={rec[f]['T']:+.1f} {rec[f]['up']}up/{rec[f]['down']}dn p2={rec[f]['p_two']:.3f}" for f in FEAT_SETS)
                    + f"  power(+0.2/+0.5)={rec['power_final_+0.2']:.2f}/{rec['power_final_+0.5']:.2f}")
            else:
                print(f"  {m:18s} k={rec['k']:2d} not tested" + (f" cmh_final z={rec['cmh_final']['z']:+.1f} power+0.5={rec['power_final_+0.5']:.2f}" if 'cmh_final' in rec else ""))
        print("  paradigm q<0.1:", [x for x in r["paradigm_family"] if x["q"] < 0.1])


if __name__ == "__main__":
    main()
