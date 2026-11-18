"""Summarise out/runs.jsonl -> table.md, results.json, ledger_rows.csv. Verdict rules: docs/prereg/consensus_corpus.md.

    .venv/bin/python -I experiments/consensus_corpus/summarise.py
"""
import json, csv, statistics as st
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy.stats import binom, binomtest

HERE = Path(__file__).resolve().parent
R = {}
for l in open(HERE / "out/runs.jsonl"):
    if l.strip():
        r = json.loads(l); R[r["cond"]] = r

TESTS = [("T1", "#1 order beats permutations"), ("T2", "#3 ticked fish final"), ("T3", "#5 M109+M59"),
         ("T4", "#6 object-type registers"), ("T5", "#7 L-R reversals"), ("T6", "#10a cores 1-2 word signs"),
         ("T7", "#10b fixed pair order"), ("T8", "#11 fish lexical class"), ("T9", "#9 functional parse")]


def effect(t, x):  # copied verbatim from experiments/assumption_audit/summarise.py (importing it rewrites its files)
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


def power(t, x, b, sims=2000, seed=0):
    """Approximate power of count tests at the BASE effect size with this condition's n and null."""
    rng = np.random.default_rng(seed)
    if x.get("survives") is None or b.get("survives") is None: return None
    if t == "T2":
        n = x["tokens"]; q = b["share"]; nm = x["null_mean"]
        crit = binom.ppf(0.95, n, nm) / n if n else 1
        k = rng.binomial(n, q, sims) / max(n, 1)
        return float(np.mean((k > crit) & (k > x["plain_share"])))
    if t == "T3":
        N = x["n"]; q = b["k"] / max(b["n"], 1)
        ks = rng.binomial(N, q, sims)
        ok = {k: (k >= 3 and binomtest(int(k), N, x["base"], alternative="greater").pvalue < 0.01) for k in set(ks.tolist())} if N else {}
        return float(np.mean([ok.get(k, False) for k in ks])) if N else 0.0
    if t == "T5":
        n = x["n_clean"]; q = b["share"]
        ks = rng.binomial(n, q, sims)
        ok = {k: (k / n >= 0.70 and binomtest(int(k), n, .5, alternative="greater").pvalue < 1e-3) for k in set(ks.tolist())} if n else {}
        return float(np.mean([ok.get(k, False) for k in ks])) if n else 0.0
    if t == "T7":
        n = x["occurrences"]; q = b["share"]
        if not n: return 0.0
        ks = rng.binomial(n, q, sims)
        ok = {k: (k / n >= 0.75 and binomtest(int(k), n, .5, alternative="greater").pvalue < 1e-3) for k in set(ks.tolist())}
        return float(np.mean([ok.get(k, False) for k in ks]))
    return None


fams = defaultdict(list)
for c in R:
    fams[c.rsplit("_s", 1)[0] if "_s" in c and c.rsplit("_s", 1)[1].isdigit() else c].append(c)
ORDER = ["base", "cons_sign_ext", "icit_ext", "struct100", "cons_text_ext", "cons_sign_reg", "icit_reg",
         "match_m77", "match_icit", "struct50", "struct150", "unif100"]
fam_names = [f for f in ORDER if f in fams]
PRIMARY = ["cons_sign_ext", "icit_ext", "struct100"]
B = R.get("base", {})

verd = {}
for f in fam_names:
    cs = sorted(fams[f], key=lambda c: int(c.rsplit("_s", 1)[1]) if "_s" in c and c.rsplit("_s", 1)[1].isdigit() else 0)
    for t, _ in TESTS:
        xs = [R[c][t] for c in cs]
        surv = [x.get("survives") for x in xs]
        n_pass = sum(bool(s) for s in surv)
        n_dir = sum(bool(effect(t, x)[0]) for x in xs)
        pw = None
        if all(s is None for s in surv):
            v = "NT"
        elif len(cs) > 1:
            need = int(np.ceil(0.8 * len(cs)))
            v = "holds" if n_pass >= need else ("weakens" if n_dir >= need else "fails")
            pw = n_pass / len(cs)
        else:
            x = xs[0]
            pw = power(t, x, B.get(t, {}))
            if surv[0]: v = "holds"
            elif pw is not None and pw < 0.8: v = "underpowered"
            else: v = "weakens" if effect(t, x)[0] else "fails"
        verd[(f, t)] = dict(verdict=v, passes=f"{n_pass}/{len(cs)}", power=None if pw is None else round(pw, 2),
                            effects=[effect(t, x)[1] for x in xs])

overall = {}
for t, name in TESTS:
    vs = [verd[(f, t)]["verdict"] for f in PRIMARY if (f, t) in verd]
    if any(v == "fails" for v in vs): o = "fails"
    elif all(v in ("holds", "underpowered") for v in vs) and any(v == "holds" for v in vs): o = "holds"
    else: o = "weakens"
    overall[t] = dict(finding=name, overall=o, primary={f: verd[(f, t)]["verdict"] for f in PRIMARY if (f, t) in verd},
                      underpowered=[f for f in PRIMARY if verd.get((f, t), {}).get("verdict") == "underpowered"])

lines = ["| finding | " + " | ".join(fam_names) + " | **overall** |", "|---|" + "---|" * (len(fam_names) + 1)]
for t, name in TESTS:
    row = []
    for f in fam_names:
        v = verd[(f, t)]
        s = v["verdict"] + (f" {v['passes']}" if len(fams[f]) > 1 else "")
        if v["power"] is not None and len(fams[f]) == 1: s += f" (pw {v['power']:.2f})"
        row.append(s)
    lines.append(f"| {t} {name} | " + " | ".join(row) + f" | **{overall[t]['overall']}** |")
lines += ["", "## Effect sizes (one entry per seed)", ""]
for t, name in TESTS:
    lines.append(f"**{t} {name}**")
    for f in fam_names:
        lines.append(f"- {f}: " + " ; ".join(verd[(f, t)]["effects"]))
    lines.append("")
lines += ["## Sample sizes", ""] + [f"- {c}: " + str({k: R[c][k] for k in R[c] if k.startswith("n_")}) for c in sorted(R)]
(HERE / "table.md").write_text("\n".join(lines) + "\n")
json.dump(dict(overall=overall, cells={f"{f}|{t}": v for (f, t), v in verd.items()}), open(HERE / "results.json", "w"), indent=1)

cols = "id,claim,area,file,statistic,p_value,p_source,ci,n,distinct_text_unit,split,mode,family,family_size,replicated_independently,readme_claim,q_global,q_area,q_hier,q_all,note".split(",")
rc = {"T1": 1, "T2": 3, "T3": 5, "T4": 6, "T5": 7, "T6": 10, "T7": 10, "T8": 11, "T9": 9}
with open(HERE / "ledger_rows.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=cols); w.writeheader()
    for f in fam_names:
        if f == "base": continue
        for t, name in TESTS:
            v = verd[(f, t)]
            ps = [R[c][t].get("p") for c in sorted(fams[f]) if isinstance(R[c][t].get("p"), (int, float))]
            c0 = sorted(fams[f])[0]
            w.writerow(dict(id=f"cc_{f}_{t}", claim=f"{name} under {f} (consensus corpus / real error rate)", area="consensus_corpus",
                            file="experiments/consensus_corpus/RESULTS.md", statistic=v["effects"][0],
                            p_value=f"{st.median(ps):.3g}" if ps else "", p_source="computed (median over seeds)" if len(ps) > 1 else ("computed" if ps else ""),
                            n=R[c0]["n_ho"], distinct_text_unit="yes", split="v2 (fixed from original M77 text)", mode="robustness",
                            family=f"consensus_corpus:{f}", family_size=9, replicated_independently="no", readme_claim=rc[t],
                            note=f"{v['verdict']} ({v['passes']} pass frozen bar" + (f"; power {v['power']}" if v["power"] is not None else "") + ")"))
print("\n".join(lines[:len(TESTS) + 2]))
print(json.dumps({t: o["overall"] for t, o in overall.items()}))
