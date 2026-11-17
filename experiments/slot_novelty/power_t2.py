"""DEV ONLY: T2 label stability at held-out sizes + positive/negative controls through the pooled rule."""
import numpy as np
from collections import Counter
from sn_lib import *
rng = np.random.default_rng(2)
cfg = dict(share_single=0.50, ratio_single=1.5, ratio_even=1.5)
dev = indus_seals("dev", min_len=3); com = common_set(indus_seals("dev"))
out = {}
r = t2_pooled_ci(dev, com, rng, B=300)
print("dev pooled", {s: round(r['P'][s], 3) for s in SLOTS}, "share", {s: round(r['share'][s], 2) for s in SLOTS},
      "top", r['top'], "t/2", round(r['ratio_top_second'], 2), r['ci_ratio_top_second'], "max/min", round(r['ratio_max_min'], 2),
      r['ci_ratio_max_min'], "minOM/closer", round(r['ratio_minOM_over_closer'], 2), r['ci_ratio_minOM_over_closer'], pooled_label(r, cfg))
out["dev_pooled"] = {k: v for k, v in r.items() if k != "per_stratum"}
w = t2_windows(dev, com, rng); print("dev windows", w); out["dev_windows"] = w
md = indus_seals("dev", "Mohenjodaro", 3)
# label frequencies when subsampling dev to held-out-like pooled sizes
for name, T, n in (("dev->n276", dev, 276), ("devMD->n221", md, 221), ("dev->n129", dev, 129)):
    labs = Counter(); closer_low = 0
    for _ in range(100):
        idx = rng.choice(len(T), n, replace=False)
        rr = t2_pooled_ci([T[i] for i in idx], com, rng, B=60)
        labs[pooled_label(rr, cfg)] += 1
        closer_low += (rr["low"] == "closer" and rr["ratio_minOM_over_closer"] >= 1.5 and rr["ci_ratio_minOM_over_closer"][0] > 1.0)
    print(name, dict(labs), "P2 closer-closed pass rate", closer_low / 100)
    out[f"stability_{name}"] = dict(labels=dict(labs), p2_pass=closer_low / 100)
# controls through pooled rule
sh = shuffle_within(dev, rng)
labs = Counter()
for _ in range(50):
    idx = rng.choice(len(sh), 276, replace=False)
    labs[pooled_label(t2_pooled_ci([sh[i] for i in idx], com, rng, B=60), cfg)] += 1
print("NEG shuffled n=276", dict(labs)); out["neg_shuffled_n276"] = dict(labs)
U = ur3_legends(); words = [tuple(u["words"]) for u in U if len(u["words"]) >= 3]
ind_c = Counter(s for t in indus_seals("dev") for s in t); syms, wt = zip(*ind_c.items()); wt = np.array(wt, float); wt /= wt.sum()
for name, conv in (("ur3_words", None), ("ur3_merged", "m")):
    labs = Counter(); tops = Counter()
    for _ in range(50):
        idx = rng.choice(len(words), 276, replace=False); W = [words[i] for i in idx]
        if conv:
            mp = {}
            W = [tuple(mp.setdefault(x, syms[rng.choice(len(syms), p=wt)]) for x in t) for t in W]
        rr = t2_pooled_ci(W, common_set(W), rng, B=60); labs[pooled_label(rr, cfg)] += 1; tops[(rr['top'], rr['low'])] += 1
    print(name, "n=276", dict(labs), dict(tops)); out[f"pos_{name}_n276"] = dict(labels=dict(labs), top_low={str(k): v for k, v in tops.items()})
dump(out, HERE / "dev_power_t2.json")
