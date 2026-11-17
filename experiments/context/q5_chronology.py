"""Q5. Chronology: does sign use change with period/phase?

Extends STATE F9/F17 (which found no single-sign drift at MD Intermediate vs Late and Harappa 3B vs 3C):
 (a) whole-text classifier early vs late within each site (CV AUC; null = period labels permuted within
     object-type strata, 200x);
 (b) per-feature ordinal trends (text length, numerals, tall/short strokes, jar-final, M343-type, etc.)
     Spearman vs phase rank; null = phase labels permuted within object type; BH; cross-site replication;
 (c) innovation / obsolescence: for every sign with >= 8 dated distinct-text occurrences, the mean
     RELATIVE time (phase rank rescaled 0..1 within site) of texts containing it vs all dated texts,
     null = time labels permuted within site x object type (5000x), BH;
 (d) Harappa Period 1-2 (Ravi / Kot Diji, pre-urban) inscriptions: inventory vs Period 3.
Unit: distinct (site, sequence).
"""
import warnings
from common import *
from scipy.stats import spearmanr
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score

warnings.filterwarnings("ignore")
rng = np.random.default_rng(5)


def phase_rank(t):
    s, per, ph = t["site"], t["period"].strip(), t["phase"].strip()
    if s == "Harappa":
        if per in ("1",): return 0
        if per == "2": return 1
        if per == "2/3": return 1.5
        if per == "3" and ph in ("A", "B", "B?", "A-C"): return 2 if ph != "A-C" else None
        if per == "3" and ph == "B/C": return 3
        if per == "3" and ph == "C": return 4
        if per in ("3/4", "4/5"): return 5
        return None
    if s == "Mohenjo-daro":   # period level only; sub-phase numbering direction is not certain
        return {"Early": 0, "Intermediate": 1, "Late": 2}.get(per)
    if s == "Dholavira":
        return {"1": 0, "2": 0, "3": 0, "4": 1, "4/5": 1.5, "5": 2, "5?": 2, "5/6": 2.5, "6": 3}.get(per)
    if s == "Kalibangan":
        return {"Early": 0, "Middle": 1, "Late": 2}.get(ph) if per == "2" else None
    return None


def otype(ty):
    return "seal" if ty.startswith("SEAL") else "tablet" if ty.startswith("TAB") else "tag" if ty.startswith("TAG") else "pot" if ty.startswith("PO") else "other"


def feats(seq):
    ss = signs(seq)
    return {"length": len(ss), "has_short": any(x in W_SHORT for x in ss), "has_tall": any(x in W_TALL for x in ss),
            "jar_final": bool(ss) and ss[-1] == "W740", "has_W741(M343)": "W741" in ss, "has_W400(M176)": "W400" in ss,
            "has_W700(M328)": "W700" in ss, "has_W002": "W002" in ss, "has_W090(person)": "W090" in ss,
            "has_W390(M161)": "W390" in ss, "has_W520(arrow)": "W520" in ss, "has_W220(fish)": "W220" in ss,
            "has_W861(opener)": "W861" in ss, "multiline": "|" in seq}


def main():
    R = {}
    I = icit_texts()
    seen, D = set(), []
    for t in I:
        r = phase_rank(t)
        if r is None or not signs(t["seq"]): continue
        k = (t["site"], " ".join(t["seq"]))
        if k in seen: continue
        seen.add(k)
        D.append(dict(site=t["site"], rank=r, ot=otype(t["type"]), seq=t["seq"]))
    print("dated distinct texts:", Counter(d["site"] for d in D))
    for s in ("Harappa", "Mohenjo-daro", "Dholavira", "Kalibangan"):
        print(f"  {s}: ranks {sorted(Counter(d['rank'] for d in D if d['site']==s).items())}")

    # (b) per-feature trends
    R["trends"] = {}
    tests = []
    for s in ("Harappa", "Mohenjo-daro", "Dholavira", "Kalibangan"):
        sub = [d for d in D if d["site"] == s]
        rk = np.array([d["rank"] for d in sub]); ot = np.array([d["ot"] for d in sub])
        F = [feats(d["seq"]) for d in sub]
        for f in F[0]:
            v = np.array([x[f] for x in F], float)
            if v.std() == 0: continue
            obs = spearmanr(rk, v).correlation
            null = np.array([spearmanr(strat_perm(rk, ot, rng), v).correlation for _ in range(1000)])
            p = (1 + (np.abs(null) >= abs(obs)).sum()) / 1001
            tests.append((s, f, obs, p, int(v.sum()) if f != "length" else len(v)))
    q = bh([t[3] for t in tests])
    print("\n(b) feature x phase Spearman (null: phase permuted within object type, 1000x), BH over", len(tests), "tests")
    for (s, f, rho, p, n), qq in zip(tests, q):
        R["trends"][f"{s}|{f}"] = dict(rho=float(rho), p=float(p), q=float(qq), n=n)
        if p < 0.05: print(f"  {s:13s} {f:18s} rho {rho:+.3f} p={p:.4f} q={qq:.3f} (n={n})")

    # (a) whole-text early vs late classifier per site
    print("\n(a) whole-text classifier, early vs late half (by phase rank), CV AUC; null within object type (200x)")
    R["classifier"] = {}
    for s in ("Harappa", "Mohenjo-daro", "Dholavira", "Kalibangan"):
        sub = [d for d in D if d["site"] == s]
        rk = np.array([d["rank"] for d in sub]); med = np.median(rk)
        y = (rk > med).astype(int) if (rk > med).mean() > 0.2 else (rk >= med).astype(int)
        c = Counter(x for d in sub for x in set(signs(d["seq"])) | ngrams(d["seq"], 2))
        voc = [x for x, n in c.items() if n >= 3]; vi = {x: i for i, x in enumerate(voc)}
        X = np.zeros((len(sub), len(voc) + 3))
        for i, d in enumerate(sub):
            for x in set(signs(d["seq"])) | ngrams(d["seq"], 2):
                if x in vi: X[i, vi[x]] = 1
            X[i, -3] = len(signs(d["seq"])) / 5
            X[i, -2:] = [d["ot"] == "seal", d["ot"] == "tablet"]
        ot = np.array([d["ot"] for d in sub])
        def sc(yy, seed):
            p = np.zeros(len(yy))
            for tr, te in StratifiedKFold(5, shuffle=True, random_state=seed).split(X, yy):
                p[te] = LogisticRegression(C=0.3, max_iter=2000, class_weight="balanced").fit(X[tr], yy[tr]).predict_proba(X[te])[:, 1]
            return roc_auc_score(yy, p)
        a = sc(y, 0)
        null = np.array([sc(strat_perm(y, ot, rng), i + 1) for i in range(200)])
        p = (1 + (null >= a).sum()) / 201
        R["classifier"][s] = dict(n=len(sub), n_late=int(y.sum()), auc=a, null=float(null.mean()), null95=float(np.quantile(null, .95)), p=float(p))
        print(f"  {s:13s} n={len(sub):4d} (late {y.sum()}) AUC {a:.3f} null {null.mean():.3f} (95% {np.quantile(null,.95):.3f}) p={p:.4f}")

    # (c) innovation / obsolescence on relative time
    rel = {}
    for s in set(d["site"] for d in D):
        rs = [d["rank"] for d in D if d["site"] == s]
        lo, hi = min(rs), max(rs)
        for d in D:
            if d["site"] == s: d["rel"] = (d["rank"] - lo) / (hi - lo) if hi > lo else 0.5
    Dd = [d for d in D if d["site"] in ("Harappa", "Mohenjo-daro", "Dholavira", "Kalibangan")]
    tvec = np.array([d["rel"] for d in Dd]); st = np.array([f"{d['site']}|{d['ot']}" for d in Dd])
    c = Counter(x for d in Dd for x in set(signs(d["seq"])))
    cand = [x for x, n in c.items() if n >= 8]
    M = np.array([[x in set(signs(d["seq"])) for x in cand] for d in Dd], float)
    obs = (M * tvec[:, None]).sum(0) / M.sum(0)
    ge = np.zeros(len(cand)); le = np.zeros(len(cand)); NP = 5000
    for _ in range(NP):
        tp = strat_perm(tvec, st, rng)
        m = (M * tp[:, None]).sum(0) / M.sum(0)
        ge += m >= obs; le += m <= obs
    p = np.minimum(1, 2 * np.minimum((ge + 1) / (NP + 1), (le + 1) / (NP + 1)))
    q = bh(p)
    print(f"\n(c) sign relative-time test: {len(cand)} signs (>=8 dated distinct texts), mean rel. time of all {tvec.mean():.3f}")
    R["sign_time"] = []
    for i in np.argsort(p)[:15]:
        # per-site direction for replication
        dirs = {}
        for s in ("Harappa", "Mohenjo-daro", "Dholavira", "Kalibangan"):
            idx = np.array([d["site"] == s for d in Dd])
            if M[idx, i].sum() >= 3:
                dirs[s] = round(float((M[idx, i] * tvec[idx]).sum() / M[idx, i].sum() - tvec[idx].mean()), 3)
        R["sign_time"].append(dict(sign=cand[i], n=int(M[:, i].sum()), mean_rel=float(obs[i]), p=float(p[i]), q=float(q[i]), per_site_shift=dirs))
        print(f"  {cand[i]:6s} n={int(M[:,i].sum()):3d} mean rel time {obs[i]:.3f} p={p[i]:.4f} q={q[i]:.3f} per-site shift {dirs}")
    R["n_sign_time_tests"] = len(cand)

    # (d) Harappa pre-urban inscriptions
    early = [d for d in D if d["site"] == "Harappa" and d["rank"] <= 1.5]
    p3 = [d for d in D if d["site"] == "Harappa" and d["rank"] >= 2]
    inv3 = Counter(x for d in p3 for x in signs(d["seq"]))
    allinv = Counter(x for t in I for x in signs(t["seq"]) if t["site"] == "Harappa")
    toks = [x for d in early for x in signs(d["seq"])]
    print(f"\n(d) Harappa Period 1-2(/3) distinct texts: {len(early)}, tokens {len(toks)}; share of tokens attested in dated Period 3: "
          f"{np.mean([inv3[x] > 0 for x in toks]):.2f}; in any Harappa text: {np.mean([allinv[x] > 1 for x in toks]):.2f}")
    print("   types:", Counter(d["ot"] for d in early), "lengths:", Counter(len(signs(d["seq"])) for d in early))
    for d in early: print("   ", d["ot"], " ".join(d["seq"]))
    R["harappa_early"] = dict(n=len(early), tokens=len(toks), share_in_p3=float(np.mean([inv3[x] > 0 for x in toks])),
                              texts=[" ".join(d["seq"]) for d in early])
    save_json("q5_chronology", R)


if __name__ == "__main__":
    main()
