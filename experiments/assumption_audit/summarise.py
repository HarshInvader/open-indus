"""Summarise out/runs.jsonl -> table.md, results.json, ledger_rows.csv (verdict rules: docs/prereg/assumption_audit.md)."""
import json, csv, statistics as st
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).resolve().parent
R = {}
for l in open(HERE / "out/runs.jsonl"):
    if l.strip():
        r = json.loads(l); R[r["cond"]] = r

TESTS = [("T1", "#1 order beats permutations"), ("T2", "#3 ticked fish final"), ("T3", "#5 M109+M59"),
         ("T4", "#6 object-type registers"), ("T5", "#7 L-R reversals"), ("T6", "#10a cores 1-2 word signs"),
         ("T7", "#10b fixed pair order"), ("T8", "#11 fish lexical class"), ("T9", "#9 functional parse")]


def effect(t, x):
    if x.get("survives") is None: return None, "NT"
    if t == "T1": return x["share"] > x["chance"], f"{x['share']:.3f} vs {x['chance']:.3f} (x{x['ratio']})"
    if t == "T2": return (x["share"] > x["plain_share"] and x["share"] > x["null_mean"]), f"{x['share']:.2f} final vs plain {x['plain_share']:.2f}, null {x['null_mean']:.2f}; p={x['p']:.3g}"
    if t == "T3": return (x["k"] / max(x["n"], 1) > x["base"]), f"{x['k']}/{x['n']} vs base {x['base']:.3f}; p={x['p']:.2g}"
    if t == "T4": return x["mean_auc"] > 0.60, f"mean AUC {x['mean_auc']:.3f}, {x['above']}/{x['n_classes']} above null"
    if t == "T5": return x["share"] > 0.5, f"{x['as_labelled']}/{x['n_clean']} = {x['share']:.2f}; p={x['p']:.2g}"
    if t == "T6": return (x["len1_share"] > 0.14 and x["standalone_tok"] > 0.11), f"len1 {x['len1_share']:.2f}, standalone {x['standalone_tok']:.2f}"
    if t == "T7": return (x["share"] or 0) > 0.5, f"{x['agree']}/{x['occurrences']} = {x['share']}; p={x['p']:.2g}"
    if t == "T8": return x["n_pass"] >= 1, f"{x['n_pass']}/3 sub-tests p<0.05"
    if t == "T9": return x["coverage"] > x["shuffle"], f"{x['coverage']:.2f} vs shuffle {x['shuffle']:.2f} (z {x['z']})"


fams = defaultdict(list)
for c in R:
    fams[c.rsplit("_s", 1)[0] if "_s" in c else c].append(c)
ORDER = ["base", "lineshuf", "rev10", "rev25", "rev50", "noiseR2", "noiseR5", "noiseR10", "noiseV2", "noiseV5", "noiseV10", "dedup", "nodoubt"]
fam_names = [f for f in ORDER if f in fams]

verd = {}
for f in fam_names:
    cs = sorted(fams[f])
    for t, _ in TESTS:
        xs = [R[c][t] for c in cs]
        surv = [x.get("survives") for x in xs]
        if all(s is None for s in surv):
            v = "NT"
        else:
            need = 2 if len(cs) == 3 else 1
            n_pass = sum(bool(s) for s in surv)
            n_dir = sum(bool(effect(t, x)[0]) for x in xs)
            v = "holds" if n_pass >= need else ("weakens" if n_dir >= need else "fails")
        verd[(f, t)] = dict(verdict=v, passes=f"{sum(bool(s) for s in surv)}/{len(cs)}",
                            effects=[effect(t, x)[1] for x in xs])

lines = ["| finding | " + " | ".join(fam_names) + " |", "|---|" + "---|" * len(fam_names)]
for t, name in TESTS:
    row = [f"{verd[(f, t)]['verdict']} {verd[(f, t)]['passes']}" if len(fams[f]) > 1 else verd[(f, t)]["verdict"] for f in fam_names]
    lines.append(f"| {t} {name} | " + " | ".join(row) + " |")
lines += ["", "## Effect sizes (one entry per seed)", ""]
for t, name in TESTS:
    lines.append(f"**{t} {name}**")
    for f in fam_names:
        lines.append(f"- {f}: " + " ; ".join(verd[(f, t)]["effects"]))
    lines.append("")
sizes = {c: {k: R[c][k] for k in R[c] if k.startswith("n_")} for c in sorted(R)}
lines += ["## Sample sizes", ""] + [f"- {c}: {v}" for c, v in sizes.items()]
(HERE / "table.md").write_text("\n".join(lines) + "\n")

json.dump({f"{f}|{t}": v for (f, t), v in verd.items()}, open(HERE / "results.json", "w"), indent=1)

cols = "id,claim,area,file,statistic,p_value,p_source,ci,n,distinct_text_unit,split,mode,family,family_size,replicated_independently,readme_claim,q_global,q_area,q_hier,q_all,note".split(",")
rc = {"T1": 1, "T2": 3, "T3": 5, "T4": 6, "T5": 7, "T6": 10, "T7": 10, "T8": 11, "T9": 9}
with open(HERE / "ledger_rows.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=cols); w.writeheader()
    for f in fam_names:
        if f == "base": continue
        for t, name in TESTS:
            v = verd[(f, t)]
            ps = [R[c][t].get("p") for c in sorted(fams[f]) if isinstance(R[c][t].get("p"), (int, float))]
            w.writerow(dict(id=f"aa_{f}_{t}", claim=f"{name} under {f} (assumption audit)", area="assumption_audit",
                            file="experiments/assumption_audit/RESULTS.md", statistic=v["effects"][0],
                            p_value=f"{st.median(ps):.3g}" if ps else "", p_source="computed (median over seeds)" if len(ps) > 1 else ("computed" if ps else ""),
                            n=R[sorted(fams[f])[0]].get("n_ho_dedup", R[sorted(fams[f])[0]]["n_ho"]),
                            distinct_text_unit="yes", split="v2 (perturbed)", mode="robustness", family=f"assumption_audit:{f}",
                            family_size=9, replicated_independently="no", readme_claim=rc[t],
                            note=f"{v['verdict']} ({v['passes']} seeds pass frozen bar)"))
print("\n".join(lines[:len(TESTS) + 2]))
