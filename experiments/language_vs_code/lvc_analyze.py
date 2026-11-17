"""Power of each discriminator on known systems, then the frozen classifier applied to Indus.

usage: lvc_analyze.py [size] [--heldout]
  size = dev (1680 texts) or heldout (565 texts)
Unit of evidence = the corpus (system), not the subsample: leave-one-corpus-out (LOCO) throughout.
"""
import sys, json, math
from collections import defaultdict
from pathlib import Path
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from lvc_metrics import METRICS  # noqa

size = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "dev"
use_ho = "--heldout" in sys.argv
rows = [json.loads(l) for l in open(HERE / "out/calib.jsonl")]
rows = [r for r in rows if r["size"] == size]
by = defaultdict(list)
for r in rows: by[r["corpus"]].append(r)
lab = {k: v[0]["label"] for k, v in by.items()}
TRAIN = [k for k in by if lab[k] in ("L", "C")]
indus_dev = [json.loads(l) for l in open(HERE / "out/indus_dev.jsonl")]
if size == "dev":
    indus_rows = {"indus_dev (full)": [r for r in indus_dev if r["rep"] == -1]}
else:
    indus_rows = {"indus_dev subsamples@565": [r for r in indus_dev if r["corpus"] == "indus_dev_sub"]}
if use_ho:
    ho = [json.loads(l) for l in open(HERE / "out/indus_heldout.jsonl")]
    indus_rows["indus_heldout (full)"] = ho

def vec(r, ms): return [r[m] if r[m] == r[m] else 0.0 for m in ms]

out = {"size": size, "per_metric": {}, "corpus_medians": {}}
print(f"\n=== size {size}: corpus medians [5%,95%] ===")
hdr = "corpus         lab " + " ".join(f"{m:>16s}" for m in METRICS)
print(hdr)
for k in sorted(by, key=lambda k: (lab[k], k)):
    a = np.array([vec(r, METRICS) for r in by[k]])
    med = np.median(a, 0); lo = np.percentile(a, 5, 0); hi = np.percentile(a, 95, 0)
    out["corpus_medians"][k] = {m: [float(med[i]), float(lo[i]), float(hi[i])] for i, m in enumerate(METRICS)}
    print(f"{k:14s} {lab[k]:3s} " + " ".join(f"{med[i]:6.2f}[{lo[i]:5.1f},{hi[i]:5.1f}]"[:16].rjust(16) for i in range(len(METRICS))))
for name, rr in indus_rows.items():
    a = np.array([vec(r, METRICS) for r in rr]); med = np.median(a, 0)
    lo = np.percentile(a, 5, 0); hi = np.percentile(a, 95, 0)
    out["corpus_medians"][name] = {m: [float(med[i]), float(lo[i]), float(hi[i])] for i, m in enumerate(METRICS)}
    print(f"{name[:14]:14s} I   " + " ".join(f"{med[i]:6.2f}[{lo[i]:5.1f},{hi[i]:5.1f}]"[:16].rjust(16) for i in range(len(METRICS))))


def auc(pos, neg):
    s = sum((p > n) + 0.5 * (p == n) for p in pos for n in neg)
    return s / (len(pos) * len(neg))


print("\n=== single-metric power (corpus level, labelled systems only) ===")
print("metric        AUC(L>C)  LOCO-acc(corpora)  LOCO-acc(subsamples)  Indus side (dev point/full)")
for i, m in enumerate(METRICS):
    med = {k: np.median([r[m] for r in by[k]]) for k in TRAIN}
    Lm = [med[k] for k in TRAIN if lab[k] == "L"]; Cm = [med[k] for k in TRAIN if lab[k] == "C"]
    A = auc(Lm, Cm); sign = 1 if A >= 0.5 else -1
    corr_c, corr_s, tot_s = 0, 0, 0
    for k in TRAIN:
        tr = [j for j in TRAIN if j != k]
        Lt = [med[j] for j in tr if lab[j] == "L"]; Ct = [med[j] for j in tr if lab[j] == "C"]
        sg = 1 if auc(Lt, Ct) >= 0.5 else -1
        # threshold maximising balanced accuracy on training corpus medians
        cands = sorted(set(Lt + Ct)); best, thr = -1, 0
        for a_, b_ in zip(cands, cands[1:] + [cands[-1] + 1]):
            t = (a_ + b_) / 2
            ba = 0.5 * (np.mean([sg * (x - t) > 0 for x in Lt]) + np.mean([sg * (x - t) <= 0 for x in Ct]))
            if ba > best: best, thr = ba, t
        pred = lambda x: "L" if sg * (x - thr) > 0 else "C"
        corr_c += pred(med[k]) == lab[k]
        for r in by[k]:
            corr_s += pred(r[m]) == lab[k]; tot_s += 1
    ivals = {n: float(np.median([r[m] for r in rr])) for n, rr in indus_rows.items()}
    out["per_metric"][m] = dict(auc=A, loco_acc_corpora=corr_c / len(TRAIN), loco_acc_subsamples=corr_s / tot_s,
                                L_medians=sorted(Lm), C_medians=sorted(Cm), indus=ivals)
    side = " ".join(f"{v:.2f}" for v in ivals.values())
    print(f"{m:12s}  {A:5.2f}     {corr_c}/{len(TRAIN)}               {corr_s / tot_s:.2f}              {side}")


# ------------- multivariate LOCO -------------
def fit(ks, ms, C_=0.3):
    X = np.array([vec(r, ms) for k in ks for r in by[k]])
    y = np.array([lab[k] == "L" for k in ks for r in by[k]])
    ncls = {c: sum((lab[k] == "L") == c for k in ks) for c in (True, False)}
    w = np.array([1.0 / (len(by[k]) * ncls[lab[k] == "L"]) for k in ks for r in by[k]])  # class-balanced
    sc = StandardScaler().fit(X)
    clf = LogisticRegression(C=C_, max_iter=2000).fit(sc.transform(X), y, sample_weight=w)
    return lambda rr: clf.predict_proba(sc.transform(np.array([vec(r, ms) for r in rr])))[:, 1], clf, sc


def loco(ms, C_=0.3):
    res = {}
    for k in TRAIN:
        f, _, _ = fit([j for j in TRAIN if j != k], ms, C_)
        res[k] = float(np.mean(f(by[k])))
    return res


sets = {"all": METRICS,
        "no_heaps_no_open": [m for m in METRICS if m not in ("heaps", "open_edge")],
        "ldd_only": ["edge_ldd", "skip_cmi"],
        "menzerath_abbrev": ["mal_surp", "mal_seg", "abbrev"]}
out["multivariate"] = {}
print("\n=== multivariate LOCO (logistic, C=0.3, corpus-balanced) ===")
for sname, ms in sets.items():
    lo = loco(ms)
    acc = 0.5 * (np.mean([lo[k] > 0.5 for k in TRAIN if lab[k] == "L"]) + np.mean([lo[k] <= 0.5 for k in TRAIN if lab[k] == "C"]))
    nL = sum(lab[k] == "L" for k in TRAIN); nC = len(TRAIN) - nL
    sens = sum(lo[k] > 0.5 for k in TRAIN if lab[k] == "L"); fpr = sum(lo[k] > 0.5 for k in TRAIN if lab[k] == "C")
    ll = -np.mean([math.log(max(1e-6, lo[k] if lab[k] == "L" else 1 - lo[k])) for k in TRAIN])
    f, clf, sc = fit(TRAIN, ms)
    ind = {n: float(np.median(f(rr))) for n, rr in indus_rows.items()}
    ind_ci = {n: [float(np.percentile(f(rr), 5)), float(np.percentile(f(rr), 95))] for n, rr in indus_rows.items()}
    others = {k: float(np.mean(f(by[k]))) for k in by if lab[k] not in ("L", "C")}
    # calibrated posterior: Laplace-smoothed LOCO sensitivity / false-positive rate, prior 0.5
    se = (sens + 1) / (nL + 2); fp = (fpr + 1) / (nC + 2)
    post = {}
    for n, p in ind.items():
        post[n] = se / (se + fp) if p > 0.5 else (1 - se) / ((1 - se) + (1 - fp))
    out["multivariate"][sname] = dict(metrics=ms, loco=lo, loco_acc=float(acc), loco_logloss=float(ll),
                                      sens=f"{sens}/{nL}", fpr=f"{fpr}/{nC}", indus_p=ind, indus_p_90=ind_ci,
                                      other_p=others, calibrated_posterior_language=post,
                                      coef=dict(zip(ms, map(float, clf.coef_[0]))))
    print(f"[{sname}] LOCO balanced acc {acc:.2f} (L correct {sens}/{nL}, C called L {fpr}/{nC}), logloss {ll:.2f}")
    print("   LOCO P(L): " + ", ".join(f"{k}={lo[k]:.2f}" for k in sorted(lo, key=lambda k: (lab[k], k))))
    print("   others: " + ", ".join(f"{k}={v:.2f}" for k, v in others.items()))
    for n in ind:
        print(f"   {n}: raw P(L)={ind[n]:.2f} [90%: {ind_ci[n][0]:.2f}-{ind_ci[n][1]:.2f}] -> calibrated posterior {post[n]:.2f}")
    print("   coef: " + ", ".join(f"{m}={c:+.2f}" for m, c in zip(ms, clf.coef_[0])))

# nearest labelled systems to Indus in metric space (z-scored over corpus medians)
print("\n=== nearest systems to Indus (Euclidean on standardised corpus medians, all metrics) ===")
names = [k for k in by]
M = np.array([[np.median([r[m] for r in by[k]]) for m in METRICS] for k in names])
mu, sd = M.mean(0), M.std(0) + 1e-9
out["nearest"] = {}
for n, rr in indus_rows.items():
    v = (np.median(np.array([vec(r, METRICS) for r in rr]), 0) - mu) / sd
    d = sorted(((float(np.linalg.norm((M[i] - mu) / sd - v)), names[i]) for i in range(len(names))))
    out["nearest"][n] = d[:6]
    print(n, ", ".join(f"{k}({lab[k]}) {x:.2f}" for x, k in d[:6]))

tag = size + ("_heldout" if use_ho else "")
json.dump(out, open(HERE / f"out/analysis_{tag}.json", "w"), indent=1)
