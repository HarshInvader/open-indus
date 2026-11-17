"""Step 1: own reimplementation of the base claims (A: title signs vs size; B: emblem vs size)."""
import sys, json
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import numpy as np
from data import build, families, split, FEATS, DEV_SIGN
from stats import strata_test, group_S, add_quantiles

T = build()
add_quantiles(T)
fam = families(T)
ho = split(T, fam, seed=7)
print("distinct square-seal texts with both dims:", len(T), "families:", len(set(fam)), "held-out:", ho.sum())

out = {"n_texts": len(T), "n_families": len(set(fam)), "n_heldout_own": int(ho.sum())}
for name, m in [("dev_own", ~ho), ("heldout_own", ho), ("all", np.ones(len(T), bool))]:
    S, p, per = group_S(T, m)
    print(f"\n[{name}] S={S:.2f} p={p:.4f}")
    for f, r in per.items():
        print(f"  {f}: n={r['n']} eff={r['eff']:+.1%} z={r['z']:+.2f}")
    out[name] = dict(S=S, p=p, per=per)

# their split (data artifact only) for comparison
sp = json.load(open("experiments/rank_ladder/icit_family_split.json"))
hk = set(sp.get("heldout", sp if isinstance(sp, list) else []))
if not hk:
    print("split keys:", list(sp)[:5])
else:
    m = np.array([t["key"] in hk for t in T])
    S, p, per = group_S(T, m)
    print(f"\n[heldout_theirs n={m.sum()}] S={S:.2f} p={p:.4f}")
    for f, r in per.items():
        print(f"  {f}: n={r['n']} eff={r['eff']:+.1%} z={r['z']:+.2f}")
    out["heldout_theirs"] = dict(n=int(m.sum()), S=S, p=p, per=per)

# emblem (claim B) on all data and own held-out
for name, m in [("heldout_own", ho), ("all", np.ones(len(T), bool))]:
    Ts = [t for t, k in zip(T, m) if k]
    for e in ["none", "zebu", "gaur", "elephant", "unknown"]:
        x = np.array([t["emb"] == e for t in Ts])
        r = strata_test(Ts, x, "base")
        print(f"[{name}] emblem {e}: n={r['n']} eff={r['eff']:+.1%} p_lo={r['p_lo']:.4f} p_hi={r['p_hi']:.4f}")
        out.setdefault("emblem_" + name, {})[e] = r
json.dump(out, open("experiments/redteam_rank/r1.json", "w"), indent=1)
