"""POST HOC (not pre-registered; run after run.py results were seen). Uses cached out/scores.pkl.
(a) leave-two-out over the 8 home round texts, KN and GR, N1 null; (b) median instead of mean, N1 null;
(c) share of texts whose real order beats >=half of their shuffles (q>=0.5), round vs N1-matched seals.
    board/run.sh env PYTHONHASHSEED=0 .venv/bin/python -I experiments/redteam_round_order/posthoc.py
"""
import sys, json, pickle, itertools
from pathlib import Path
from collections import defaultdict
import numpy as np
ROOT = Path(__file__).resolve().parents[2]; OUT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "experiments/context"), str(ROOT / "experiments/grammar"), str(ROOT)]
import q4_gulf as Q  # noqa
import glib  # noqa  (needed to unpickle model classes)
from corpus.load import icit_texts  # noqa
class GRw: pass  # stubs so the cached run.py models unpickle
class POSw: pass
S =pickle.load(open(OUT / "out/scores.pkl", "rb"))
rng = np.random.default_rng(2525)
seen, native, foreign = set(), [], []
for t in icit_texts():
    s = Q.clean(t["seq"])
    if not s: continue
    site = t["site"]; grp = "f" if site in Q.FOREIGN_WEST | Q.FOREIGN_CA else "u" if site == "Unknown" else "n"
    if grp == "u": continue
    fmt = "round" if t["type"] in ("SEAL:C", "SEAL:CY") else "seal" if t["type"].startswith("SEAL") else "other"
    k = (grp, " ".join(s))
    if k in seen: continue
    seen.add(k); (native if grp == "n" else foreign).append(dict(seq=s, fmt=fmt, id=t["id"]))
fk = {" ".join(r["seq"]) for r in foreign}
native = [r for r in native if " ".join(r["seq"]) not in fk]
N = len(native); assert N == len(S["P_nat"])
L = np.array([len(r["seq"]) for r in native]); r_ = S["r_nat"]
fmt = np.array([r["fmt"] for r in native]); ids = np.array([r["id"] for r in native])
hp = np.array([len(p) > 0 for p in S["P_nat"]])
seal = (fmt == "seal") & hp
circ = np.where((fmt == "round") & hp & ~np.isin(ids, ["1387.1", "1388.1", "1388.2"]))[0]
pools = defaultdict(list)
for i in np.where(seal)[0]: pools[(min(L[i], 9), min(r_[i], 3))].append(i)
pools = {k: np.array(v) for k, v in pools.items()}
def key(i):
    for LL in range(min(L[i], 9), 0, -1):
        for rr in range(min(r_[i], 3), -1, -1):
            if len(pools.get((LL, rr), [])) >= 5: return (LL, rr)
R = {}
for s in ("KN", "GR"):
    D = S[s]
    d = np.array([D["real"][i] - D["pb"][i].mean() if len(D["pb"][i]) else np.nan for i in range(N)])
    q = np.array([(D["pb"][i] <= D["real"][i]).mean() if len(D["pb"][i]) else np.nan for i in range(N)])
    def test(sel, vals, agg=np.mean, nd=5000):
        draws = np.stack([vals[pools[key(i)][rng.integers(len(pools[key(i)]), size=nd)]] for i in sel])
        dr = agg(draws, axis=0); obs = agg(vals[sel])
        return dict(obs=float(obs), null=float(dr.mean()), diff=float(obs - dr.mean()), p=float((1 + (dr >= obs).sum()) / (nd + 1)))
    l2o = [dict(dropped=[ids[circ[a]], ids[circ[b]]], **test(np.delete(circ, [a, b]), d, nd=3000))
           for a, b in itertools.combinations(range(len(circ)), 2)]
    worst = max(l2o, key=lambda x: x["p"])
    R[s] = dict(leave_two_out_max_p=worst["p"], worst_pair=worst["dropped"], worst_diff=worst["diff"],
                n_pairs_p_lt_05=sum(x["p"] < 0.05 for x in l2o), n_pairs=len(l2o),
                median_N1=test(circ, d, agg=np.median), share_q_ge_half_N1=test(circ, (q >= 0.5).astype(float)))
    print(s, json.dumps(R[s], indent=1))
json.dump(R, open(OUT / "posthoc.json", "w"), indent=1, default=str)
