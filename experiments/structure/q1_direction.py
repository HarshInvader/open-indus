"""Q1. Reading direction: positional asymmetry, L-to-R exception texts, multi-line texts, ICIT direction field.

All sequences in data/ are in READING order as assigned by the transcribers (Mahadevan from physical cues such
as cramping, spacing and line arrangement). We test whether that order is consistent with the sign grammar in a
way that does not depend on the jar sign alone, and whether the L-to-R texts behave like the R-to-L texts once
read in their labelled direction (i.e. the label is real) or like mirrored texts (label is wrong).
"""
import random
from collections import Counter, defaultdict

from scipy.stats import binomtest, spearmanr

from common import (Bigram, distinct, icit_texts, m77_lines, m77_split, m77_texts, save_json, signs, entropy)

random.seed(20261114)
res = {}


def line_groups(lines, dirkey, rl, lr, symkey="signs"):
    g = defaultdict(list)
    seen = set()
    for l in lines:
        d = l[dirkey]
        s = [x for x in l[symkey] if x not in ("|", "#")]
        if "#" in l[symkey] or len(s) < 2:
            continue
        key = (d, " ".join(s))
        if key in seen:
            continue
        seen.add(key)
        if d in rl:
            g["RL"].append(s)
        elif d in lr:
            g["LR"].append(s)
    return g


def end_stats(seqs, jar):
    n = len(seqs)
    last = sum(s[-1] == jar for s in seqs)
    first = sum(s[0] == jar for s in seqs)
    return {"n": n, "jar_last": last, "jar_first": first, "jar_last_share": last / n, "jar_first_share": first / n}


def final_rates(seqs, minn=5):
    tot, fin, ini = Counter(), Counter(), Counter()
    for s in seqs:
        for x in set(s):
            tot[x] += 1
        fin[s[-1]] += 1
        ini[s[0]] += 1
    return {x: (fin[x] / tot[x], ini[x] / tot[x]) for x in tot if tot[x] >= minn}


def direction_classifier(train, test):
    """Bigram trained on reading-order training lines; predict 'as given' if logP(seq) > logP(reversed)."""
    bg = Bigram(train)
    correct = ties = 0
    for s in test:
        a, b = bg.logprob(s), bg.logprob(s[::-1])
        if abs(a - b) < 1e-9:
            ties += 1
        elif a > b:
            correct += 1
    n = len(test) - ties
    return correct, n


def jarfree(seqs, jar):
    return [s for s in seqs if jar not in s]


def analyse(name, lines, dirkey, rl, lr, jar, symkey, dev_keys=None):
    g = line_groups(lines, dirkey, rl, lr, symkey)
    out = {"RL": end_stats(g["RL"], jar), "LR": end_stats(g["LR"], jar)}
    # binomial: among LR lines with the jar at an end, is it at the reading end?
    k = out["LR"]["jar_last"]; m = k + out["LR"]["jar_first"]
    out["LR_jar_end_binom_p"] = binomtest(k, m, 0.5, alternative="greater").pvalue if m else None
    # positional profile correlation, labelled vs mirrored
    rr = final_rates(g["RL"]); lrr = final_rates(g["LR"], minn=3)
    common = [x for x in lrr if x in rr]
    fin_rl = [rr[x][0] for x in common]; ini_rl = [rr[x][1] for x in common]
    fin_lr = [lrr[x][0] for x in common]
    out["profile_signs"] = len(common)
    out["rho_final_LR_vs_final_RL"] = spearmanr(fin_lr, fin_rl).statistic
    out["rho_final_LR_vs_initial_RL(mirror)"] = spearmanr(fin_lr, ini_rl).statistic
    # direction classifier: train on RL lines (dev half), test on held-out RL half and on LR lines, jar-free too
    rl_lines = g["RL"][:]
    random.shuffle(rl_lines)
    half = len(rl_lines) * 3 // 4
    tr, te = rl_lines[:half], rl_lines[half:]
    c, n = direction_classifier(tr, te)
    out["classifier_RL_heldout_acc"] = (c, n, c / n)
    c, n = direction_classifier(tr, g["LR"])
    out["classifier_LR_acc"] = (c, n, c / n, binomtest(c, n, 0.5, alternative="greater").pvalue)
    # jar-free: remove every line containing the jar from train and test
    trj = jarfree(tr, jar)
    c, n = direction_classifier(trj, jarfree(te, jar))
    out["classifier_RL_heldout_acc_jarfree"] = (c, n, c / n)
    c, n = direction_classifier(trj, jarfree(g["LR"], jar))
    out["classifier_LR_acc_jarfree"] = (c, n, c / n, binomtest(c, n, 0.5, alternative="greater").pvalue)
    # asymmetry of ends in RL
    fi = Counter(s[0] for s in g["RL"]); la = Counter(s[-1] for s in g["RL"])
    out["RL_first_types"] = len(fi); out["RL_last_types"] = len(la)
    out["RL_H_first_bits"] = entropy(fi); out["RL_H_last_bits"] = entropy(la)
    out["RL_top_last"] = la.most_common(5); out["RL_top_first"] = fi.most_common(5)
    res[name] = out
    return g


# ---------- M77 lines (distinct line sequences per direction) ----------
L = m77_lines()
g = analyse("M77_lines", L, "direction", {"right-to-left"}, {"left-to-right"}, "M342", "signs")

# L-R by object type and site
bytype = defaultdict(Counter)
seen = set()
for l in L:
    if l["direction"] != "left-to-right":
        continue
    s = signs(l["signs"])
    if len(s) < 2 or " ".join(s) in seen:
        continue
    seen.add(" ".join(s))
    bytype[l["object_type"]]["n"] += 1
    bytype[l["object_type"]]["jar_last"] += s[-1] == "M342"
    bytype[l["object_type"]]["jar_first"] += s[0] == "M342"
    bytype[l["site"]]["site_n"] += 1
res["M77_LR_by_type_site"] = {k: dict(v) for k, v in bytype.items()}

# ---------- multi-line texts: line order consistency ----------
T = distinct(m77_texts())
ml = [t for t in T if t["n_lines"] >= 2 and "#" not in t["seq"]]
endline = Counter()
for t in ml:
    parts = []
    cur = []
    for x in t["seq"]:
        if x == "|":
            parts.append(cur); cur = []
        else:
            cur.append(x)
    parts.append(cur)
    parts = [p for p in parts if p]
    if len(parts) < 2:
        continue
    endline["texts"] += 1
    endline["jar_end_last_line"] += parts[-1][-1] == "M342"
    endline["jar_end_first_line"] += parts[0][-1] == "M342"
    endline["jar_start_first_line"] += parts[0][0] == "M342"
    endline["jar_start_last_line"] += parts[-1][0] == "M342"
    endline["opener_start_first"] += parts[0][0] in ("M267", "M391", "M293", "M216")
    endline["opener_start_last"] += parts[-1][0] in ("M267", "M391", "M293", "M216")
res["M77_multiline"] = dict(endline)
k, m = endline["jar_end_last_line"], endline["jar_end_last_line"] + endline["jar_end_first_line"]
res["M77_multiline"]["binom_p_jar_last_line"] = binomtest(k, m, 0.5, alternative="greater").pvalue

# ---------- ICIT ----------
I = icit_texts()
for t in I:
    t["_signs"] = t["seq"]
analyse("ICIT", I, "direction", {"R/L", "R/l"}, {"L/R"}, "W740", "_signs")
dh = [t for t in I if t["site"] == "Dholavira"]
analyse("ICIT_Dholavira", dh, "direction", {"R/L", "R/l"}, {"L/R"}, "W740", "_signs")

save_json("q1_direction", res)
import json
print(json.dumps(res, indent=1, default=str))

# ---------- multi-line texts: line order by bigram classifier (trained on single-line texts) ----------
single = [signs(t["seq"]) for t in T if t["n_lines"] == 1 and "#" not in t["seq"] and len(signs(t["seq"])) >= 2]
bg = Bigram(single)
cnt = Counter()
lens = Counter()
for t in ml:
    parts, cur = [], []
    for x in t["seq"]:
        if x == "|":
            parts.append(cur); cur = []
        else:
            cur.append(x)
    parts.append(cur)
    parts = [p for p in parts if p]
    if len(parts) < 2:
        continue
    lens[(len(parts[0]), len(parts[-1]))] += 1
    a = bg.logprob(sum(parts, [])); b = bg.logprob(sum(parts[::-1], []))
    cnt["given_better" if a > b else ("tie" if a == b else "swapped_better")] += 1
    cnt["last_line_shorter"] += len(parts[-1]) < len(parts[0])
    cnt["last_line_single_sign"] += len(parts[-1]) == 1
res["M77_multiline_classifier"] = dict(cnt)
k = cnt["given_better"]; n = k + cnt["swapped_better"]
res["M77_multiline_classifier"]["binom_p"] = binomtest(k, n, 0.5, alternative="greater").pvalue

# ---------- Dholavira as an independent site: classifier trained on non-Dholavira ICIT R/L ----------
gI = line_groups([t for t in I if t["site"] != "Dholavira"], "direction", {"R/L", "R/l"}, {"L/R"}, "_signs")
gD = line_groups(dh, "direction", {"R/L", "R/l"}, {"L/R"}, "_signs")
c, n = direction_classifier(gI["RL"], gD["RL"])
res["ICIT_Dholavira_RL_classifier_trained_elsewhere"] = (c, n, c / n, binomtest(c, n, 0.5, alternative="greater").pvalue)
c, n = direction_classifier(jarfree(gI["RL"], "W740"), jarfree(gD["RL"], "W740"))
res["ICIT_Dholavira_RL_classifier_trained_elsewhere_jarfree"] = (c, n, c / n, binomtest(c, n, 0.5, alternative="greater").pvalue)
save_json("q1_direction", res)
print(res["M77_multiline_classifier"], res["ICIT_Dholavira_RL_classifier_trained_elsewhere"], res["ICIT_Dholavira_RL_classifier_trained_elsewhere_jarfree"])
