"""Power of the language_vs_code battery on the genre-matched short-label calibration set, and (with
--indus) the frozen classifier applied to Indus.

usage: .venv/bin/python experiments/short_labels/sl_analyze.py [--indus] [--perm N]
Classifier = the language_vs_code one, unchanged: 8 metrics, StandardScaler, logistic C=0.3,
class- and corpus-balanced weights; a system's P(L) = mean over its replicates.
Validation units = systems: leave-one-system-out (LOSO) and leave-one-family-out (LOFO).
Output: out/analysis.json and out/analysis.log
"""
import sys, json, math, random
from collections import defaultdict
from pathlib import Path
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "experiments/language_vs_code"))
from lvc_metrics import METRICS  # noqa

USE_INDUS = "--indus" in sys.argv
NPERM = int(sys.argv[sys.argv.index("--perm") + 1]) if "--perm" in sys.argv else 200
rows = [json.loads(l) for l in open(HERE / "out/calib.jsonl")]
LOG = open(HERE / ("out/analysis_indus.log" if USE_INDUS else "out/analysis.log"), "w")


def P(*a):
    s = " ".join(str(x) for x in a); print(s); LOG.write(s + "\n")


def vec(r, ms): return [r[m] if r[m] == r[m] else 0.0 for m in ms]


SETS = {
    "genre_real": lambda r: r["set"] == "genre",                 # PRIMARY
    "genre_plus_synth": lambda r: r["set"] in ("genre", "synth"),
    "all": lambda r: r["set"] in ("genre", "synth", "old"),
}
FEATS = {"all8": METRICS, "all8_C100": METRICS, "ldd_only": ["edge_ldd", "skip_cmi"],
         "menzerath_abbrev": ["mal_surp", "mal_seg", "abbrev"], "no_heaps_no_open":
         [m for m in METRICS if m not in ("heaps", "open_edge")]}


def auc(pos, neg):
    return sum((p > n) + 0.5 * (p == n) for p in pos for n in neg) / (len(pos) * len(neg))


class Cal:
    def __init__(self, size, setname):
        rr = [r for r in rows if r["size"] == size and SETS[setname](r) and r["label"] in ("L", "C")]
        self.by = defaultdict(list)
        for r in rr: self.by[r["corpus"]].append(r)
        self.lab = {k: v[0]["label"] for k, v in self.by.items()}
        self.fam = {k: v[0]["family"] for k, v in self.by.items()}
        self.sys = sorted(self.by)

    def fit(self, ks, ms, lab=None, C_=0.3):
        lab = lab or self.lab
        X = np.array([vec(r, ms) for k in ks for r in self.by[k]])
        y = np.array([lab[k] == "L" for k in ks for r in self.by[k]])
        ncls = {c: sum((lab[k] == "L") == c for k in ks) for c in (True, False)}
        if min(ncls.values()) == 0: return None
        w = np.array([1.0 / (len(self.by[k]) * ncls[lab[k] == "L"]) for k in ks for r in self.by[k]])
        sc = StandardScaler().fit(X)
        clf = LogisticRegression(C=C_, max_iter=3000).fit(sc.transform(X), y, sample_weight=w)
        return lambda rr_: clf.predict_proba(sc.transform(np.array([vec(r, ms) for r in rr_])))[:, 1], clf

    def cv(self, ms, group="system", lab=None, C_=0.3):
        lab = lab or self.lab
        res = {}
        for k in self.sys:
            hold = {k} if group == "system" else {j for j in self.sys if self.fam[j] == self.fam[k]}
            out = self.fit([j for j in self.sys if j not in hold], ms, lab, C_)
            res[k] = 0.5 if out is None else float(np.mean(out[0](self.by[k])))
        L = [k for k in self.sys if lab[k] == "L"]; Cc = [k for k in self.sys if lab[k] == "C"]
        ba = 0.5 * (np.mean([res[k] > 0.5 for k in L]) + np.mean([res[k] <= 0.5 for k in Cc]))
        return res, float(ba), sum(res[k] > 0.5 for k in L), len(L), sum(res[k] > 0.5 for k in Cc), len(Cc)

    def perm_p(self, ms, ba_obs, n=NPERM, seed=0):
        """label-permutation null for LOSO balanced accuracy (labels shuffled across systems)"""
        rng = random.Random(seed); labs = [self.lab[k] for k in self.sys]; ge = 0
        for _ in range(n):
            rng.shuffle(labs); lab = dict(zip(self.sys, labs))
            ge += self.cv(ms, "system", lab)[1] >= ba_obs - 1e-9
        return (ge + 1) / (n + 1)


def indus_rows(size):
    if not USE_INDUS: return {}
    out = {}
    dev = [json.loads(l) for l in open(HERE / "out/indus_dev.jsonl")]
    out["indus_dev_sub"] = [r for r in dev if r["size"] == size and r["rep"] >= 0]
    ho = [json.loads(l) for l in open(HERE / "out/indus_heldout.jsonl")]
    if size == "A": out["indus_heldout_full"] = [r for r in ho if r["size"] == "A"]
    else: out["indus_heldout_sub"] = [r for r in ho if r["size"] == "B"]
    return out


result = {"sizes": {}}
for size in ("A", "B"):
    result["sizes"][size] = {}
    for sname in SETS:
        c = Cal(size, sname)
        if not c.sys: continue
        nL = sum(c.lab[k] == "L" for k in c.sys); nC = len(c.sys) - nL
        P(f"\n===== size {size} ({'565' if size == 'A' else '150'} texts), set {sname}: {nL} languages, {nC} codes =====")
        R = {"systems": {k: c.lab[k] for k in c.sys}, "per_metric": {}, "classifiers": {}}
        # medians table
        for k in sorted(c.sys, key=lambda k: (c.lab[k], k)):
            med = np.median(np.array([vec(r, METRICS) for r in c.by[k]]), 0)
            P(f"  {k:16s} {c.lab[k]} " + " ".join(f"{m}={v:6.2f}" for m, v in zip(METRICS, med)))
        for m in METRICS:
            med = {k: float(np.median([r[m] for r in c.by[k]])) for k in c.sys}
            A = auc([med[k] for k in c.sys if c.lab[k] == "L"], [med[k] for k in c.sys if c.lab[k] == "C"])
            R["per_metric"][m] = {"auc_L_above_C": A, "medians": med}
        P("  single-metric AUC: " + ", ".join(f"{m}={R['per_metric'][m]['auc_L_above_C']:.2f}" for m in METRICS))
        IR = indus_rows(size)
        for fname, ms in FEATS.items():
            Cr = 100.0 if fname.endswith("C100") else 0.3
            loso, ba, sL, nL_, fC, nC_ = c.cv(ms, "system", C_=Cr)
            lofo, ba_f, sLf, _, fCf, _ = c.cv(ms, "family", C_=Cr)
            pp = c.perm_p(ms, ba) if (fname == "all8") else None
            fit = c.fit(c.sys, ms, C_=Cr)
            ent = dict(loso_ba=ba, loso_L_called_L=f"{sL}/{nL_}", loso_C_called_L=f"{fC}/{nC_}",
                       lofo_ba=ba_f, lofo_L_called_L=f"{sLf}/{nL_}", lofo_C_called_L=f"{fCf}/{nC_}",
                       perm_p_loso_ba=pp, loso_p=loso, lofo_p=lofo,
                       coef=dict(zip(ms, map(float, fit[1].coef_[0]))))
            se = (sL + 1) / (nL_ + 2); fp = (fC + 1) / (nC_ + 2)
            ind = {}
            for n, rr in IR.items():
                if not rr: continue
                ps = fit[0](rr); p = float(np.median(ps))
                post = se / (se + fp) if p > 0.5 else (1 - se) / ((1 - se) + (1 - fp))
                ind[n] = dict(raw_p=p, p05=float(np.percentile(ps, 5)), p95=float(np.percentile(ps, 95)),
                              calibrated_posterior=float(post), n_rows=len(rr))
            ent["indus"] = ind
            R["classifiers"][fname] = ent
            P(f"  [{fname}] LOSO BA {ba:.2f} (L->L {sL}/{nL_}, C->L {fC}/{nC_})"
              + (f" perm p={pp:.3f}" if pp is not None else "")
              + f" | LOFO BA {ba_f:.2f} (L->L {sLf}/{nL_}, C->L {fCf}/{nC_})")
            if fname in ("all8", "all8_C100"):
                P("     LOSO P(L): " + ", ".join(f"{k}={loso[k]:.2f}" for k in sorted(c.sys, key=lambda k: (c.lab[k], k))))
                P("     coef: " + ", ".join(f"{m}={v:+.2f}" for m, v in ent["coef"].items()))
            for n, d in ind.items():
                lp = sorted(loso.values()); d["percentile_among_LOSO_systems"] = float(np.mean([x < d["raw_p"] for x in lp]))
                P(f"     {n}: raw P(L)={d['raw_p']:.2f} [5-95%: {d['p05']:.2f}-{d['p95']:.2f}] posterior {d['calibrated_posterior']:.2f}")
        # nearest systems to Indus (standardised corpus medians)
        if IR:
            names = c.sys
            M = np.array([[np.median([r[m] for r in c.by[k]]) for m in METRICS] for k in names])
            mu, sd = M.mean(0), M.std(0) + 1e-9
            R["nearest"] = {}
            for n, rr in IR.items():
                if not rr: continue
                v = (np.median(np.array([vec(r, METRICS) for r in rr]), 0) - mu) / sd
                d = sorted((float(np.linalg.norm((M[i] - mu) / sd - v)), names[i]) for i in range(len(names)))
                R["nearest"][n] = d[:6]
                P(f"  nearest to {n}: " + ", ".join(f"{k}({c.lab[k]}) {x:.2f}" for x, k in d[:6]))
                R.setdefault("indus_medians", {})[n] = dict(zip(METRICS, map(float, np.median(np.array([vec(r, METRICS) for r in rr]), 0))))
        result["sizes"][size][sname] = R

json.dump(result, open(HERE / ("out/analysis_indus.json" if USE_INDUS else "out/analysis.json"), "w"), indent=1, default=float)
