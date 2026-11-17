"""Step 1: detachment from layout alone. Dev split defines; held-out and ICIT-only replicate.
Run: .venv/bin/python -I experiments/detached_signs/d1_detach.py
"""
import json, sys
from collections import Counter
from pathlib import Path
import numpy as np
from scipy.stats import hypergeom
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ds_lib import *  # noqa

OUT = Path(__file__).parent


def bh(p):
    p = np.asarray(p, float); n = len(p); o = np.argsort(p)
    q = np.empty(n); prev = 1.0
    for i in range(n - 1, -1, -1):
        prev = min(prev, p[o[i]] * n / (i + 1)); q[o[i]] = prev
    return q


def table(texts):
    tok = Counter(); det = Counter(); tok_multi = Counter(); single_line = Counter(); one_sign = Counter()
    N = Nm = K = 0
    for t in texts:
        fl = solo_flags(t["seq"])
        for s, solo, nl in fl:
            tok[s] += 1; N += 1
            if nl >= 2:
                tok_multi[s] += 1; Nm += 1
            else:
                single_line[s] += 1
                if len(fl) == 1:
                    one_sign[s] += 1
            if solo:
                det[s] += 1; K += 1
    return dict(tok=tok, det=det, tok_multi=tok_multi, single_line=single_line, one_sign=one_sign,
                N=N, Nm=Nm, K=K)


def test(tb, min_det=2):
    rows = []
    for s in tb["tok"]:
        n, k, nm = tb["tok"][s], tb["det"][s], tb["tok_multi"][s]
        pg = hypergeom.sf(k - 1, tb["N"], tb["K"], n)          # global: whole split
        pc = hypergeom.sf(k - 1, tb["Nm"], tb["K"], nm) if nm else 1.0  # within multi-line texts
        rows.append(dict(sign=s, n=n, det=k, n_multi=nm, single_line=tb["single_line"][s],
                         one_sign_text=tb["one_sign"][s],
                         exp_global=n * tb["K"] / tb["N"], exp_cond=nm * tb["K"] / max(tb["Nm"], 1),
                         p_global=pg, p_cond=pc))
    tested = [r for r in rows if r["det"] >= min_det or r["n"] >= 10]
    qg = bh([r["p_global"] for r in tested]); qc = bh([r["p_cond"] for r in tested])
    for r, a, b in zip(tested, qg, qc):
        r["q_global"] = float(a); r["q_cond"] = float(b)
    return sorted(tested, key=lambda r: r["p_global"])


dev, ho = dev_heldout(version=2)
res = {}
tbd = table(dev); rd = test(tbd)
res["dev_counts"] = dict(N=tbd["N"], N_multi=tbd["Nm"], K_solo=tbd["K"], n_texts=len(dev),
                         n_multiline=sum(t["n_lines"] > 1 for t in dev), n_signs_tested=len(rd))
# frozen rule: detached if q_global<0.05 AND p_cond<0.05 (dev)
CLASS = [r["sign"] for r in rd if r["q_global"] < 0.05 and r["p_cond"] < 0.05]
res["detached_class_dev"] = CLASS
res["dev_top"] = rd[:25]

tbh = table(ho); rh = {r["sign"]: r for r in test(tbh, min_det=0)}
res["heldout_counts"] = dict(N=tbh["N"], N_multi=tbh["Nm"], K_solo=tbh["K"], n_texts=len(ho))
rep = {}
for s in CLASS:
    r = rh.get(s)
    rep[s] = r and {k: r[k] for k in ("n", "det", "n_multi", "exp_global", "p_global", "p_cond")}
res["heldout_replication"] = rep
# pooled held-out class test
def pooled(tb, signs):
    n = sum(tb["tok"][s] for s in signs); k = sum(tb["det"][s] for s in signs)
    nm = sum(tb["tok_multi"][s] for s in signs)
    return dict(n=n, det=k, n_multi=nm, exp_global=n * tb["K"] / tb["N"],
                p_global=float(hypergeom.sf(k - 1, tb["N"], tb["K"], n)),
                p_cond=float(hypergeom.sf(k - 1, tb["Nm"], tb["K"], nm)) if nm else None)
res["heldout_pooled"] = pooled(tbh, CLASS)

io = icit_only()
tbi = table(io); ri = {r["sign"]: r for r in test(tbi, min_det=0)}
res["icit_only_counts"] = dict(N=tbi["N"], N_multi=tbi["Nm"], K_solo=tbi["K"], n_texts=len(io),
                               n_multiline=sum("|" in t["seq"] for t in io))
WCLASS = sorted(set().union(*[M2W.get(s, set()) for s in CLASS])) if CLASS else []
res["class_W_via_bridge"] = {s: sorted(M2W.get(s, [])) for s in CLASS}
res["icit_only_replication"] = {w: ri.get(w) and {k: ri[w][k] for k in ("n", "det", "n_multi", "exp_global", "p_global", "p_cond")} for w in WCLASS}
res["icit_only_pooled"] = pooled(tbi, WCLASS) if WCLASS else None
res["icit_only_top"] = sorted(ri.values(), key=lambda r: r["p_global"])[:15]
# all-M77 (descriptive) table of the class
tba = table(distinct(m77_texts()))
res["all_m77_class"] = {s: dict(n=tba["tok"][s], det=tba["det"][s], n_multi=tba["tok_multi"][s],
                               single_line=tba["single_line"][s], one_sign_text=tba["one_sign"][s]) for s in CLASS}
json.dump(res, open(OUT / "d1_detach.json", "w"), indent=1, default=float)
print(json.dumps({k: v for k, v in res.items() if k not in ("dev_top", "icit_only_top")}, indent=1, default=float))
print("DEV TOP")
for r in rd[:25]:
    print(f"{r['sign']:6} n={r['n']:4} det={r['det']:3} exp={r['exp_global']:.2f} nm={r['n_multi']:3} expc={r['exp_cond']:.2f} single={r['single_line']:3} pg={r['p_global']:.1e} qg={r['q_global']:.3f} pc={r['p_cond']:.1e}")
print("ICIT-only TOP")
for r in res["icit_only_top"]:
    print(f"{r['sign']:6} n={r['n']:4} det={r['det']:3} exp={r['exp_global']:.2f} nm={r['n_multi']:3} pg={r['p_global']:.1e} pc={r['p_cond']:.1e}")
