"""Planted-answer controls: run all four tests on synthetic logo-syllabic corpora at
Indus dev size (1,675 distinct texts) with the mechanism planted (ON) and absent (OFF).
Reports recall of planted items and false positives. Writes results.json[controls]."""
import sys, time
from collections import defaultdict

import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from common import bh, save_results
from synth import Synth, synth_excluded
from run_indus_dev import transparency
from tests import t1_complements, t1_local, t2_transitivity, t3_ligatures, t4_drops

SEEDS = range(10)
ALL = ("comp", "homo", "lig", "det")
SLOTSIG = lambda s: s[0] in "OKCPF"


def run_t1(T, S):
    out = {}
    comp = {x: h for h, x in S.truth["comp"]}
    for name, fn in [("local_wide", lambda T, o: t1_local(T, synth_excluded, o, nperm=2000, wide=1, minev=4)),
                     ("edit1", lambda T, o: t1_complements(T, synth_excluded, o, nperm=2000, minev=4))]:
        items = []
        for o in ("prev", "next"):
            r = fn(T, o)
            for it in r["items"]:
                it["orient"] = o; items.append(it)
        q = bh([i["p"] for i in items])
        sig = {}
        for it, qq in zip(items, q):
            if qq < 0.05:
                sig.setdefault(it["sign"], (it["orient"], it["top_hosts"][0][0]))
        tp = [x for x, (o, h) in sig.items() if o == "prev" and comp.get(x) == h]
        trans = {x: transparency(T, x, h, o)[0] or 0.0 for x, (o, h) in sig.items()}
        passed = [x for x in sig if trans[x] >= 0.40]
        out[name] = {"n_tested": len(items), "n_sig": len(sig), "tp": len(tp), "n_planted": len(comp),
                     "fp_nonslot": sum(1 for x, (o, h) in sig.items() if x not in tp and not SLOTSIG(x)),
                     "sig": {x: list(v) + [trans[x]] for x, v in sig.items()},
                     "n_pass": len(passed), "tp_pass": sum(1 for x in passed if x in tp), "rule_met": len(passed) >= 3}
    return out


def run_t2(T, S, nnull):
    r = t2_transitivity(T, nnull=nnull)
    planted = {"%s|%s" % tuple(sorted(p)) for p in S.truth["homo"]}
    sig = [k for k, v in r["pairs"].items() if v["q"] < 0.05]
    tp = [k for k in sig if k in planted]
    slot = [k for k in sig if k not in planted and all(SLOTSIG(s) for s in k.split("|"))]
    other = [k for k in sig if k not in planted and k not in slot]
    return {"n_frames": r["n_frames"], "n_multi_obs": r["n_multi_obs"], "n_multi_null": r["n_multi_null_mean"],
            "p_global": r["p_global"], "n_tested": len(r["pairs"]), "n_sig": len(sig), "tp": len(tp),
            "n_planted": len(planted), "fp_slot_paradigm": len(slot), "fp_other": len(other),
            "planted_k": {k: r["all_k"].get(k, 0) for k in planted}, "fp_other_pairs": other[:10]}


def run_t3(T, S):
    r = t3_ligatures(T)
    planted = {(g, bc[0], bc[1]) for g, bc in S.truth["lig"]}
    sig = [(i["A"], i["B"], i["C"]) for i in r["items"] if i["q"] < 0.05]
    tp = [s for s in sig if s in planted]
    return {"n_events": r["n_events"], "n_tested": r["n_triples_tested"], "n_sig": len(sig), "tp": len(tp),
            "n_planted": len(planted), "fp": [s for s in sig if s not in planted]}


def run_t4(T, S):
    pairs = [(b, m) for m, b in S.truth["det_silent"]] + [(b, m) for m, b in S.truth["det_lex"]]
    r = t4_drops(T, pairs)
    sil = r[:4]; lex = r[4:]
    pooled = lambda rr: (sum(x["obs"] for x in rr), sum(x["exp"] for x in rr))
    from scipy.stats import poisson
    so, se = pooled(sil); lo, le = pooled(lex)
    return {"silent": sil, "lex": lex, "silent_pooled": [so, se, float(poisson.sf(so - 1, se)) if se else None],
            "lex_pooled": [lo, le, float(poisson.sf(lo - 1, le)) if le else None],
            "silent_pair_hits": sum(1 for x in sil if x["p_more"] < 0.05),
            "lex_pair_hits": sum(1 for x in lex if x["p_more"] < 0.05)}


STRONG = dict(mult_p=0.6, comp_n=12, comp_rmax=40, homo_p=0.5, lig_p=0.6, det_p=0.5)


def main(nnull=500, strength="realistic"):
    res = defaultdict(list)
    kw = STRONG if strength == "strong" else {}
    for seed in SEEDS:
        for cond, mech in [("ON", ALL), ("OFF", ())]:
            t = time.time()
            S = Synth(seed, mech, **kw); T = S.corpus()
            row = {"seed": seed, "t1": run_t1(T, S), "t2": run_t2(T, S, nnull), "t3": run_t3(T, S), "t4": run_t4(T, S)}
            res[cond].append(row)
            print(cond, seed, "%.0fs" % (time.time() - t),
                  "T1 local sig/tp/fp %d/%d/%d edit1 %d/%d" % (row["t1"]["local_wide"]["n_sig"], row["t1"]["local_wide"]["tp"],
                                                               row["t1"]["local_wide"]["fp_nonslot"], row["t1"]["edit1"]["n_sig"],
                                                               row["t1"]["edit1"]["tp"]),
                  "T2 sig/tp/slot/other %d/%d/%d/%d" % (row["t2"]["n_sig"], row["t2"]["tp"], row["t2"]["fp_slot_paradigm"],
                                                        row["t2"]["fp_other"]),
                  "T3 sig/tp %d/%d" % (row["t3"]["n_sig"], row["t3"]["tp"]),
                  "T4 silent %s lex %s" % (row["t4"]["silent_pooled"], row["t4"]["lex_pooled"]), flush=True)
    # summaries
    summ = {}
    for cond in ("ON", "OFF"):
        R = res[cond]
        summ[cond] = {
            "t1_local_nsig": [r["t1"]["local_wide"]["n_sig"] for r in R],
            "t1_local_tp": [r["t1"]["local_wide"]["tp"] for r in R],
            "t1_local_fp_nonslot": [r["t1"]["local_wide"]["fp_nonslot"] for r in R],
            "t1_rule_met": [r["t1"]["local_wide"]["rule_met"] for r in R],
            "t1_npass": [r["t1"]["local_wide"]["n_pass"] for r in R],
            "t1_tp_pass": [r["t1"]["local_wide"]["tp_pass"] for r in R],
            "t1_edit1_nsig": [r["t1"]["edit1"]["n_sig"] for r in R],
            "t1_edit1_tp": [r["t1"]["edit1"]["tp"] for r in R],
            "t2_tp": [r["t2"]["tp"] for r in R], "t2_fp_slot": [r["t2"]["fp_slot_paradigm"] for r in R],
            "t2_fp_other": [r["t2"]["fp_other"] for r in R], "t2_p_global": [r["t2"]["p_global"] for r in R],
            "t2_multi_obs": [r["t2"]["n_multi_obs"] for r in R], "t2_multi_null": [r["t2"]["n_multi_null"] for r in R],
            "t3_tp": [r["t3"]["tp"] for r in R], "t3_nsig": [r["t3"]["n_sig"] for r in R],
            "t4_silent_p": [r["t4"]["silent_pooled"][2] for r in R], "t4_lex_p": [r["t4"]["lex_pooled"][2] for r in R],
            "t4_silent_pair_hits": [r["t4"]["silent_pair_hits"] for r in R],
            "t4_lex_pair_hits": [r["t4"]["lex_pair_hits"] for r in R],
        }
    save_results("controls_" + strength, {"strength_kwargs": kw, "summary": summ, "runs": res,
                              "design": "Synth(seed, mech) at 1,675 distinct texts; mechanisms comp/homo/lig/det; see synth.py"})
    for cond in summ:
        print(cond)
        for k, v in summ[cond].items():
            print("  ", k, v)


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 500, sys.argv[2] if len(sys.argv) > 2 else "realistic")
