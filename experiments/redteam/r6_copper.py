"""Claim 6 (context): copper tablets with identical text share the picture (0.62 vs 0.06, 272 pairs).
Attack: the unit. 272 pairs come from a handful of legends; a legend on k tablets gives k(k-1)/2
pairs. Recount at the legend (tablet-type) level, with fine (fs80) and coarse (first word of
the fs description) picture labels, and with a legend-level permutation null.
Picture per tablet from the IM77 line file (paragorth data, read as data only)."""
import csv
from collections import Counter, defaultdict
import numpy as np
from rt_common import ROOT, m77, save

rng = np.random.default_rng(5)
rows = list(csv.DictReader(open(ROOT / "sources/paragorth_Indus-/data/im77/im77_corpus_lines.csv")))
img = defaultdict(set)
for r in rows:
    if r["object_code"] == "5" and r["fs80"] not in ("0", "", "999"):
        img[int(r["text_no"])].add(int(r["fs80"]))
desc = {}
for t in [json for json in []]: pass
from rt_common import m77_lines
for l in m77_lines():
    if l.get("fs80"): desc[l["fs80"]] = l.get("fs_description", "")
by = defaultdict(list)
for t in m77():
    if t["object_type"] == "copper tablet": by[t["text_no"]].append(t)
tabs = []
for no, sides in by.items():
    ts = [s for s in sides if len([x for x in s["seq"] if x not in "|#"]) >= 2 and "#" not in s["seq"]]
    if len(img[no]) == 1 and len(ts) == 1:
        fs = next(iter(img[no]))
        coarse = (desc.get(fs, "") or f"fs{fs}").split(",")[0].split("(")[0].strip().lower()[:25]
        tabs.append(dict(no=no, text=" ".join(ts[0]["seq"]), fs=fs, coarse=coarse))
leg = defaultdict(list)
for t in tabs: leg[t["text"]].append(t)
multi = {k: v for k, v in leg.items() if len(v) >= 2}
res = dict(n_tablets=len(tabs), n_legends=len(leg), legends_on_2plus=len(multi),
           pairs=sum(len(v) * (len(v) - 1) // 2 for v in multi.values()),
           legend_sizes=sorted([len(v) for v in multi.values()], reverse=True))
# pairs share contributed by the largest legends
sz = sorted(multi.items(), key=lambda kv: -len(kv[1]))
res["top3_legends_pair_share"] = round(sum(len(v) * (len(v) - 1) / 2 for _, v in sz[:3]) / res["pairs"], 3)


def legend_stat(lab_of):
    """mean over legends of share of tablets carrying the legend's modal picture"""
    vals = []
    for k, v in multi.items():
        c = Counter(lab_of[t["no"]] for t in v)
        vals.append(c.most_common(1)[0][1] / len(v))
    return float(np.mean(vals))


for key in ("fs", "coarse"):
    lab = {t["no"]: t[key] for t in tabs}
    obs = legend_stat(lab)
    nos = [t["no"] for t in tabs]; labs = [t[key] for t in tabs]
    null = []
    for _ in range(5000):
        p = rng.permutation(labs); null.append(legend_stat(dict(zip(nos, p))))
    null = np.array(null)
    # legends where ALL copies share one picture
    allsame = sum(len({lab[t["no"]] for t in v}) == 1 for v in multi.values())
    res[f"legend_level_{key}"] = dict(modal_share=round(obs, 3), null=round(float(null.mean()), 3),
                                      p=float((1 + (null >= obs).sum()) / 5001), legends_all_same=f"{allsame}/{len(multi)}")
res["legends"] = [dict(text=k, n=len(v), pictures=dict(Counter(t["coarse"] for t in v)), fs=dict(Counter(t["fs"] for t in v)))
                  for k, v in sz]
for k, v in res.items(): print(k, v)
save("r6_copper", res)
