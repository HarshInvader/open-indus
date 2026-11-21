"""Score the 10-guesser ensemble against the sealed key (prereg: docs/prereg/ensemble_rehearsal.md).
Run only after guesses/G01.json .. G10.json exist:
.venv/bin/python -I experiments/ensemble_rehearsal/score.py
"""
import json, random
from collections import Counter
from pathlib import Path
from scipy.stats import beta, binomtest

HERE = Path(__file__).resolve().parent
CLASSES = ["GRAIN_FOOD", "LIQUID_DAIRY", "VESSEL", "TEXTILE", "LIVESTOCK", "OTHER_GOODS", "OFFICE_PERSON", "PLACE_INST"]
AGREE = 0.70          # primary agreement rule
GO_COV, GO_PREC, KILL_PREC = 0.10, 0.60, 0.50
N_PERM = 10000
rng = random.Random(20261121)

key = json.load(open(HERE / "sealed/key.json"))
ids = sorted(key)
G = {}
for f in sorted((HERE / "guesses").glob("G*.json")):
    try:
        g = json.load(open(f))
    except Exception:
        continue
    G[f.stem] = {i: (g.get(i, {}).get("class") if g.get(i, {}).get("class") in CLASSES else None) for i in ids}
    G[f.stem + "_rec"] = {i: bool(g.get(i, {}).get("recognised")) for i in ids}
    G[f.stem + "_raw"] = g
gids = sorted(k for k in G if len(k) == 3)
N = len(gids)
assert N >= 1, "no guess files"

recognised = {i for i in ids if any(G[g + "_rec"][i] for g in gids)}
nonrec = [i for i in ids if i not in recognised]
truth = {i: key[i]["class"] for i in ids}


def modal(votes):
    """votes: dict gid->class or None. Returns (class or None if tie/empty, share of N)."""
    c = Counter(v for v in votes if v is not None)
    if not c:
        return None, 0.0
    top = c.most_common()
    if len(top) > 1 and top[0][1] == top[1][1]:
        return None, top[0][1] / N  # tie: no unique modal class, never enters a subset
    return top[0][0], top[0][1] / N


def subset_stats(guess_table, signs, thr):
    sel, k = 0, 0
    for i in signs:
        m, sh = modal([guess_table[g][i] for g in gids])
        if m is not None and sh >= thr - 1e-9:
            sel += 1
            k += m == truth[i]
    return sel, k


def cp(k, n):
    if n == 0:
        return [None, None]
    lo = beta.ppf(0.025, k, n - k + 1) if k > 0 else 0.0
    hi = beta.ppf(0.975, k + 1, n - k) if k < n else 1.0
    return [round(float(lo), 3), round(float(hi), 3)]


table = {g: G[g] for g in gids}
n_nr = len(nonrec)
res = {"n_guessers": N, "guessers": gids, "n_targets": len(ids), "n_recognised_any": len(recognised),
       "n_not_recognised": n_nr, "recognised_ids": sorted(recognised)}

# primary
sel, k = subset_stats(table, nonrec, AGREE)
cov = sel / n_nr if n_nr else 0.0
prec = k / sel if sel else None
if sel == 0 or cov < GO_COV or (prec is not None and prec < KILL_PREC):
    verdict = "KILL"
elif prec >= GO_PREC:
    verdict = "GO"
else:
    verdict = "INCONCLUSIVE (precision 50-60%)"
res["primary"] = {"agreement_rule": AGREE, "n_high_agreement": sel, "n_correct": k, "coverage": round(cov, 3),
                  "precision": None if prec is None else round(prec, 3), "precision_ci95_cp": cp(k, sel),
                  "binom_p_vs_0.125": binomtest(k, sel, 0.125, alternative="greater").pvalue if sel else None,
                  "verdict": verdict}

# curve and secondary thresholds
curve = []
for thr in (0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0):
    s_, k_ = subset_stats(table, nonrec, thr)
    curve.append({"threshold": thr, "n": s_, "correct": k_, "coverage": round(s_ / n_nr, 3) if n_nr else None,
                  "precision": round(k_ / s_, 3) if s_ else None, "ci95": cp(k_, s_)})
res["curve"] = curve

# modal-vote accuracy on all non-recognised signs (plurality, ties count wrong)
mk = sum(modal([table[g][i] for g in gids])[0] == truth[i] for i in nonrec)
res["plurality_acc_not_recognised"] = [mk, n_nr, round(mk / n_nr, 3) if n_nr else None]

# permutation null: shuffle each guesser's classes across the non-recognised signs, independently
obs_k = {thr: subset_stats(table, nonrec, thr)[1] for thr in (0.5, 0.6, 0.7)}
ge = {thr: 0 for thr in obs_k}
null_sel = {thr: [] for thr in obs_k}
null_prec = {thr: [] for thr in obs_k}
for _ in range(N_PERM):
    pt = {}
    for g in gids:
        vals = [table[g][i] for i in nonrec]
        rng.shuffle(vals)
        pt[g] = dict(zip(nonrec, vals))
    for thr in obs_k:
        s_, k_ = subset_stats(pt, nonrec, thr)
        ge[thr] += k_ >= obs_k[thr]
        null_sel[thr].append(s_)
        if s_:
            null_prec[thr].append(k_ / s_)
res["perm_null"] = {
    str(thr): {"obs_correct": obs_k[thr], "p_correct_ge_obs": (ge[thr] + 1) / (N_PERM + 1),
               "null_mean_n_selected": round(sum(null_sel[thr]) / N_PERM, 2),
               "null_mean_precision_when_nonempty": round(sum(null_prec[thr]) / len(null_prec[thr]), 3) if null_prec[thr] else None,
               "null_frac_nonempty": round(len(null_prec[thr]) / N_PERM, 3)}
    for thr in obs_k}

# single-guesser baseline on the same non-recognised signs
single = {}
for g in gids:
    kk = sum(table[g][i] == truth[i] for i in nonrec)
    own_nr = [i for i in ids if not G[g + "_rec"][i]]
    ko = sum(table[g][i] == truth[i] for i in own_nr)
    single[g] = {"acc_on_ensemble_nonrec": [kk, n_nr, round(kk / n_nr, 3) if n_nr else None],
                 "acc_on_own_nonrec": [ko, len(own_nr), round(ko / len(own_nr), 3) if own_nr else None],
                 "n_flagged": sum(G[g + "_rec"][i] for i in ids)}
accs = [v["acc_on_ensemble_nonrec"][2] for v in single.values() if v["acc_on_ensemble_nonrec"][2] is not None]
res["single_guesser"] = single
res["single_guesser_mean_acc"] = round(sum(accs) / len(accs), 3) if accs else None
res["single_guesser_range"] = [min(accs), max(accs)] if accs else None
res["majority_class_baseline_nonrec"] = round(Counter(truth[i] for i in nonrec).most_common(1)[0][1] / n_nr, 3) if n_nr else None

# recognised signs, descriptive: were the memory calls right?
rec_rows = []
for i in sorted(recognised):
    for g in gids:
        if G[g + "_rec"][i]:
            rec_rows.append({"id": i, "guesser": g, "recognised_as": G[g + "_raw"].get(i, {}).get("recognised_as"),
                             "class": table[g][i], "truth_sign": key[i]["sign"], "truth": truth[i],
                             "class_right": table[g][i] == truth[i]})
res["recognition_calls"] = rec_rows

res["per_sign"] = []
for i in ids:
    votes = [table[g][i] for g in gids]
    m, sh = modal(votes)
    res["per_sign"].append({"id": i, "sign": key[i]["sign"], "truth": truth[i], "recognised": i in recognised,
                            "modal": m, "share": round(sh, 2), "modal_right": m == truth[i],
                            "votes": dict(Counter(v or "NONE" for v in votes))})

json.dump(res, open(HERE / "results.json", "w"), indent=1)
print(json.dumps({k: v for k, v in res.items() if k not in ("per_sign", "recognition_calls", "single_guesser")}, indent=1))
