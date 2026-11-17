"""Summarise out/runs.jsonl by the rules in docs/prereg/crib_le_known_answer.md."""
import json, sys
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from le_run import RULES, SAMPLING, NS, ANCHORS, setup  # noqa

rows = [json.loads(l) for l in open(HERE / "out" / "runs.jsonl")]
g = defaultdict(lambda: defaultdict(list))
for r in rows:
    g[(r["rule"], r["samp"], r["n"], r["a"], r["sub"])][r["kind"]].append(r)
C = setup()
print("name-bearing words under the true key:", {k: len(v) for k, v in C["named"].items()}, "of", len(C["wid"]))
out = []
for rule in RULES:
    for samp in SAMPLING:
        for n in NS:
            for a in ANCHORS:
                subs = [g[(rule, samp, n, a, s)] for s in range(6) if g.get((rule, samp, n, a, s))]
                subs = [s for s in subs if s["real"] and s["wrong"] and s["shuffle"]]
                if not subs:
                    continue
                P, prec, rec, Et, Er, q95s, Ew, trueq = [], [], [], [], [], [], [], []
                good = Counter()
                for s in subs:
                    re_, wr = s["real"][0], s["wrong"][0]
                    q = float(np.quantile([x["E"] for x in s["shuffle"]], 0.95))
                    P.append(re_["E"] > q and re_["E"] > wr["E"])
                    prec.append(re_["n_correct"] / re_["n_used"] if re_["n_used"] else 0.0)
                    rec.append(re_["n_correct"] / re_["n_signs"] if re_["n_signs"] else 0.0)
                    Et.append(re_["E_true"]); Er.append(re_["E"]); q95s.append(q); Ew.append(wr["E"])
                    trueq.append(re_["E_true"] > q); good.update(re_["correct_signs"])
                d = dict(rule=rule, samp=samp, n=n, a=a, subsets=len(subs), pass_share=float(np.mean(P)),
                         E_real_med=float(np.median(Er)), E_wrong_med=float(np.median(Ew)),
                         null_q95_med=float(np.median(q95s)), E_true_med=float(np.median(Et)),
                         true_beats_q95=float(np.mean(trueq)), prec_med=float(np.median(prec)),
                         rec_med=float(np.median(rec)), correct_signs=dict(good.most_common()))
                d["recovers"] = bool(d["pass_share"] >= 0.8 and d["prec_med"] >= 0.5)
                out.append(d)
json.dump(out, open(HERE / "out" / "summary.json", "w"), indent=1, ensure_ascii=False)
print("| rule | sampling | n | a | E real med | E wrong med | shuffle q95 med | E true med | true>q95 | pass share | prec med | rec med | recovers |")
print("|" + "---|" * 13)
for d in out:
    print(f"| {d['rule']} | {d['samp']} | {d['n']} | {d['a']} | {d['E_real_med']:.1f} | {d['E_wrong_med']:.1f} | "
          f"{d['null_q95_med']:.1f} | {d['E_true_med']:.1f} | {d['true_beats_q95']:.2f} | {d['pass_share']:.2f} | "
          f"{d['prec_med']:.2f} | {d['rec_med']:.2f} | {'YES' if d['recovers'] else '-'} |")
prim = [d for d in out if d["rule"] == "CV" and d["samp"] == "random" and d["n"] == 45]
print("\nprimary (CV, random, n=45) recovers:", [d["recovers"] for d in prim])
print("any cell recovers:", [(d["rule"], d["samp"], d["n"], d["a"]) for d in out if d["recovers"]])
