"""Exploratory sensitivities and part-3 descriptives (after the registered held-out test)."""
import json, math, sys
from collections import Counter
sys.path.insert(0, "experiments/numeral_grammar")
import models
from common import *

dev, ho = dev_heldout(version=2)
OLD = {"Mohenjo-daro", "Harappa", "Lothal", "Kalibangan", "Chanhu-daro"}
icit_new = [t for t in distinct(icit_texts()) if t["site"] not in OLD]


def G(texts, table, keep_conn=False, merge1=False):
    out = []
    for t in texts:
        for g in groups_from_runs(t["seq"], table, keep_conn=keep_conn):
            gg = tuple(("S" if c == "C" else c, v) for _, c, v in g["group"])
            if merge1:
                gg = tuple(("S", 1) if x == ("T", 1) else x for x in gg)
            out.append(gg)
    return out

R = {}
for label, kw in [("base", {}), ("connective_as_S2", dict(keep_conn=True)), ("T1_merged_into_S1", dict(merge1=True))]:
    for eps in (0.01, 0.05, 0.2):
        models.EPS = eps
        fit = models.Fit(G(dev, M_NUM, **kw))
        res = {}
        for name, gs in (("M77_heldout", G(ho, M_NUM, **kw)), ("ICIT_new", G(icit_new, W_NUM, **kw))):
            ll = {m: models.loglik(fit, m, gs) for m in models.MODELS}
            res[name] = {m: round(ll[m] - ll["M1"], 2) for m in models.MODELS if m != "M1"}
        R[f"{label}_eps{eps}"] = res
        print(label, eps, res)
models.EPS = 0.01

# best case for a 12-unit: score ONLY groups that contain S12 or are allowed by M2 (drop all other pairs)
fit = models.Fit(G(dev, M_NUM))
gs = [g for g in G(ho, M_NUM) + G(icit_new, W_NUM) if len(g) > 1 and ("S", 12) in g]
R["only_12_groups"] = {m: round(models.loglik(fit, m, gs) - models.loglik(fit, "M1", gs), 2) for m in ("M2a", "M2b", "M5")}
print("only groups containing 12:", R["only_12_groups"], len(gs))

# Part 3 descriptives on ALL M77 distinct texts: what follows single vs multi-sign groups
M = distinct(m77_texts())
nxt_single = Counter(); nxt_multi = Counter(); frame = Counter()
for t in M:
    for g in groups_from_runs(t["seq"], M_NUM):
        (nxt_multi if len(g["group"]) > 1 else nxt_single)[g["next"]] += 1
        r = [x for x in runs(t["seq"]) if True]
    for rr in runs(t["seq"]):
        for i in range(len(rr) - 2):
            a, b, c = rr[i:i + 3]
            if a in M_NUM and M_NUM[a][0] != "C" and b not in M_NUM and c not in M_NUM:
                frame[(M_NUM[a][0], b, c)] += 1
R["next_after_multi"] = nxt_multi.most_common(12)
R["next_after_single"] = nxt_single.most_common(12)
tot_m = sum(nxt_multi.values()); tot_s = sum(nxt_single.values())
R["end_of_run_after_multi"] = round(nxt_multi[None] / tot_m, 3)
R["end_of_run_after_single"] = round(nxt_single[None] / tot_s, 3)
R["top_numeral_X_Y_frames"] = [(f"{a} {b} {c}", n) for (a, b, c), n in frame.most_common(15)]
print(json.dumps({k: R[k] for k in ("next_after_multi", "next_after_single", "end_of_run_after_multi",
                                     "end_of_run_after_single", "top_numeral_X_Y_frames")}, indent=0, default=str))
json.dump(R, open("experiments/numeral_grammar/sens.json", "w"), indent=1, default=str)
