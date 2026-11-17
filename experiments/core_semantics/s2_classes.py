"""Q2 semantic classes of core signs (dev exploration; held-out scoring in h3_heldout.py).

Per core sign (>= KMIN core occurrences in distinct texts):
  frame vector  : left and right neighbour in the full text (strokes collapsed to NUM; edges ^ $ |)
  partner vector: other signs in the same core
  -> PPMI, cosine similarity.
Tests (label permutation among signs, 5000):
  referent class coherence (sign_referents.csv; numerals excluded): mean within - mean between cosine
  fish family coherence
  Mantel: similarity vs object-type profile similarity, vs number-adjacency similarity
Theophoric signature per element: R = distinct multi-element core types containing it, D = distinct partners /
multi-element occurrences, S = standalone share (1-element core, not next to a numeral). T = z(log R) + z(D) - z(S).
Calibrated as AUC(deity vs other) on Ur III ({d}) and Sanskrit (deity list) at Indus dev size.
Usage: .venv/bin/python experiments/core_semantics/s2_classes.py [dev|heldout|all]
"""
import sys, json
from collections import Counter, defaultdict
import numpy as np
import pandas as pd
from scipy.stats import spearmanr, mannwhitneyu
from sklearn.metrics import roc_auc_score
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform
sys.path.insert(0, __import__("os").path.dirname(__file__))
import cs_data as D

KMIN = 5
STROKES = {f"M{i}" for i in range(86, 123)}  # Mahadevan stroke/numeral block (approx.)
REF = pd.read_csv(D.ROOT / "experiments" / "iconography" / "sign_referents.csv").set_index("sign")


def ctx(s):
    return "NUM" if s in STROKES else s


def build(occ, kmin=KMIN):
    cnt = Counter()
    seen = set()
    frames = defaultdict(Counter); partners = defaultdict(Counter)
    standalone = Counter(); multi = Counter(); numadj = Counter(); obj = defaultdict(Counter)
    mtypes = defaultdict(set)
    for o in occ:
        key = (o["text"], o["core"])
        if key in seen:
            continue
        seen.add(key)
        c = o["core"]
        for i, s in enumerate(c):
            cnt[s] += 1
            L = c[i - 1] if i > 0 else o["left"]; R = c[i + 1] if i < len(c) - 1 else o["right"]
            frames[s]["L:" + ctx(L)] += 1; frames[s]["R:" + ctx(R)] += 1
            obj[s][o["object_type"]] += 1
            if len(c) == 1:
                if o["num_adj"]:
                    numadj[s] += 1
                else:
                    standalone[s] += 1
            else:
                multi[s] += 1
                mtypes[s].add(c)
                for j, p in enumerate(c):
                    if j != i:
                        partners[s]["P:" + p] += 1
    signs = sorted([s for s, k in cnt.items() if k >= kmin], key=lambda s: -cnt[s])
    return dict(signs=signs, cnt=cnt, frames=frames, partners=partners, standalone=standalone, multi=multi,
                numadj=numadj, obj=obj, mtypes=mtypes)


def ppmi_cos(signs, feats):
    cols = sorted({f for s in signs for f in feats[s]})
    ci = {f: i for i, f in enumerate(cols)}
    M = np.zeros((len(signs), len(cols)))
    for r, s in enumerate(signs):
        for f, v in feats[s].items():
            M[r, ci[f]] = v
    tot = M.sum(); pr = M.sum(1, keepdims=True) / tot; pc = M.sum(0, keepdims=True) / tot
    with np.errstate(divide="ignore", invalid="ignore"):
        P = np.log((M / tot) / (pr * pc ** 0.75 / (pc ** 0.75).sum()))
    P[~np.isfinite(P)] = 0; P = np.maximum(P, 0)
    nrm = np.linalg.norm(P, axis=1, keepdims=True); nrm[nrm == 0] = 1
    X = P / nrm
    return X @ X.T


def coherence(S, labels, reps, rng, exclude=None):
    """mean within-label cosine - mean between, label permutation p (one-sided, greater)."""
    idx = [i for i, l in enumerate(labels) if l is not None and l != exclude]
    lab = np.array([labels[i] for i in idx]); Ss = S[np.ix_(idx, idx)]
    iu = np.triu_indices(len(idx), 1)

    def stat(l):
        same = (l[:, None] == l[None, :])[iu]
        v = Ss[iu]
        return v[same].mean() - v[~same].mean()
    obs = stat(lab)
    null = np.array([stat(rng.permutation(lab)) for _ in range(reps)])
    return dict(n_signs=len(idx), obs=round(float(obs), 4), null_mean=round(float(null.mean()), 4),
                p=round(float((1 + (null >= obs).sum()) / (1 + reps)), 4))


def set_coherence(S, signs, members, reps, rng, cnt):
    """mean pairwise cosine within a member set vs frequency-matched random sets."""
    idx = [i for i, s in enumerate(signs) if s in members]
    if len(idx) < 2:
        return None
    iu = np.triu_indices(len(idx), 1)
    obs = S[np.ix_(idx, idx)][iu].mean()
    others = [i for i in range(len(signs)) if signs[i] not in members]
    logf = np.log([cnt[s] for s in signs])
    null = []
    for _ in range(reps):
        pick = []
        for i in idx:
            cand = [j for j in others if abs(logf[j] - logf[i]) < 0.5 and j not in pick] or others
            pick.append(rng.choice(cand))
        null.append(S[np.ix_(pick, pick)][iu].mean())
    null = np.array(null)
    return dict(members=[signs[i] for i in idx], obs=round(float(obs), 4), null_mean=round(float(null.mean()), 4),
                p=round(float((1 + (null >= obs).sum()) / (1 + reps)), 4))


def mantel(S, P, reps, rng):
    iu = np.triu_indices(len(S), 1)
    obs = spearmanr(S[iu], P[iu])[0]
    null = []
    for _ in range(reps):
        p = rng.permutation(len(S))
        null.append(spearmanr(S[iu], P[np.ix_(p, p)][iu])[0])
    null = np.array(null)
    return dict(rho=round(float(obs), 4), p=round(float((1 + (null >= obs).sum()) / (1 + reps)), 4))


def theophoric_table(elements, mtypes, multi, standalone, total):
    prod = Counter()
    for t in {t for e in mtypes for t in mtypes[e]}:
        for x in set(t):
            prod[x] += 1
    rows = []
    for e in elements:
        ph = [np.log(prod[p]) for t in mtypes[e] for p in t if p != e]
        R = len(mtypes[e]); partners = {p for t in mtypes[e] for p in t if p != e}
        Dv = len(partners) / multi[e] if multi[e] else 0
        S = standalone[e] / total[e] if total[e] else 0
        rows.append(dict(el=e, R=R, D=Dv, S=S, n=total[e], PH=float(np.mean(ph)) if ph else np.nan))
    df = pd.DataFrame(rows)
    z = lambda x: (x - x.mean()) / (x.std() or 1)
    df["T"] = z(np.log1p(df.R)) + z(df.D) - z(df.S)
    return df


def ref_theophoric(two, single, is_deity, n_multi, n_single, reps, rng, kmin=KMIN):
    """AUC of T (and components) for deity vs other elements, refs subsampled to Indus size."""
    two = list(two); single = list(single)
    out = defaultdict(list)
    for _ in range(reps):
        tw = [two[i] for i in rng.choice(len(two), min(n_multi, len(two)), replace=False)]
        sg = [single[i] for i in rng.choice(len(single), min(n_single, len(single)), replace=False)]
        mtypes = defaultdict(set); multi = Counter(); st = Counter(); tot = Counter()
        for t in tw:
            for e in t:
                mtypes[e].add(t); multi[e] += 1; tot[e] += 1
        for e in sg:
            st[e] += 1; tot[e] += 1
        els = [e for e in tot if tot[e] >= kmin]
        df = theophoric_table(els, mtypes, multi, st, tot)
        y = np.array([is_deity(e) for e in df.el])
        if y.sum() < 2 or y.sum() == len(y):
            continue
        for k in ("T", "R", "D"):
            out[k].append(roc_auc_score(y, df[k]))
        ok = ~df.PH.isna().values
        if 2 <= y[ok].sum() < ok.sum():
            out["PH"].append(roc_auc_score(y[ok], df.PH.values[ok]))
        out["S"].append(roc_auc_score(y, -df["S"]))
        out["n_deity"].append(int(y.sum())); out["n_el"].append(len(y))
    return {k: dict(mean=round(float(np.mean(v)), 3), lo=round(float(np.percentile(v, 2.5)), 3),
                    hi=round(float(np.percentile(v, 97.5)), 3)) for k, v in out.items()}


def ref_coherence(two, is_deity, n_multi, reps, rng, kmin=KMIN):
    """Does partner+position substitution similarity make deity elements coherent (Ur III / Sanskrit)?"""
    two = list(two); vals = []
    for _ in range(reps):
        tw = [two[i] for i in rng.choice(len(two), min(n_multi, len(two)), replace=False)]
        feats = defaultdict(Counter); cnt = Counter()
        for a, b in tw:
            feats[a]["R:" + b] += 1; feats[b]["L:" + a] += 1; cnt[a] += 1; cnt[b] += 1
        els = [e for e in cnt if cnt[e] >= kmin]
        if sum(is_deity(e) for e in els) < 3:
            continue
        S = ppmi_cos(els, feats)
        r = coherence(S, [("deity" if is_deity(e) else "other") for e in els], 200, rng)
        # within-deity mean vs within-other mean is what matters: use the set statistic
        vals.append(r["p"])
    vals = np.array(vals)
    return dict(reps=len(vals), share_p_lt_05=round(float((vals < 0.05).mean()), 3), median_p=round(float(np.median(vals)), 4))


if __name__ == "__main__":
    split = sys.argv[1] if len(sys.argv) > 1 else "dev"
    rng = np.random.default_rng(7)
    inc, occ = D.indus_types(split)
    B = build(occ)
    signs = B["signs"]
    print(f"{split}: {len(signs)} core signs with >= {KMIN} core occurrences")
    res = {"split": split, "n_signs": len(signs)}
    feats = {s: B["frames"][s] + B["partners"][s] for s in signs}
    S = ppmi_cos(signs, feats)
    Sf = ppmi_cos(signs, B["frames"])
    refcls = [REF.referent_class.get(s) if s in REF.index else None for s in signs]
    print("referent classes among core signs:", Counter(r for r in refcls if r))
    res["referent_coherence_frames+partners"] = coherence(S, refcls, 5000, rng, exclude="numeral")
    res["referent_coherence_frames"] = coherence(Sf, refcls, 5000, rng, exclude="numeral")
    fishset = set(D.FISH)
    res["fish_coherence"] = set_coherence(S, signs, fishset, 2000, rng, B["cnt"])
    res["fish_coherence_frames_only"] = set_coherence(Sf, signs, fishset, 2000, rng, B["cnt"])
    # object-type profile and number adjacency
    types = ["seal", "sealing", "miniature tablet", "copper tablet", "pottery graffito"]
    Pobj = np.array([[B["obj"][s][t] for t in types] for s in signs], float) + 0.5
    Pobj /= Pobj.sum(1, keepdims=True)
    Sobj = 1 - 0.5 * np.abs(Pobj[:, None, :] - Pobj[None, :, :]).sum(-1)
    nadj = np.array([B["numadj"][s] / B["cnt"][s] for s in signs])
    Snum = -np.abs(nadj[:, None] - nadj[None, :])
    res["mantel_objtype"] = mantel(S, Sobj, 2000, rng)
    res["mantel_numadj"] = mantel(S, Snum, 2000, rng)
    # number-name class
    nn = sorted(((round(nadj[i], 2), B["cnt"][s], s) for i, s in enumerate(signs)), reverse=True)
    res["number_adjacent_top"] = [(s, a, n) for a, n, s in nn[:15]]
    isfish = np.array([s in fishset for s in signs])
    res["numadj_fish_vs_rest"] = dict(fish=round(float(nadj[isfish].mean()), 3), rest=round(float(nadj[~isfish].mean()), 3),
                                      p=round(float(mannwhitneyu(nadj[isfish], nadj[~isfish], alternative="greater").pvalue), 5))
    # clusters
    Dm = np.clip(1 - S, 0, None); np.fill_diagonal(Dm, 0)
    Z = linkage(squareform(Dm, checks=False), "average")
    cl = fcluster(Z, 10, "maxclust")
    res["clusters"] = {}
    for k in sorted(set(cl)):
        mem = [signs[i] for i in range(len(signs)) if cl[i] == k]
        res["clusters"][int(k)] = [(m, REF.referent_class.get(m, "-") if m in REF.index else "-", B["cnt"][m]) for m in mem]
    # nearest neighbours of key signs
    res["neighbours"] = {}
    for s in ["M59", "M67", "M65", "M72", "M70", "M171", "M178", "M389", "M244", "M343", "M336", "M245", "M53"]:
        if s in signs:
            i = signs.index(s); o = np.argsort(-S[i])[1:7]
            res["neighbours"][s] = [(signs[j], round(float(S[i, j]), 2)) for j in o]
    # theophoric signature
    total = Counter({s: B["cnt"][s] for s in B["cnt"]})
    df = theophoric_table(signs, B["mtypes"], B["multi"], B["standalone"], total)
    df["fish"] = df.el.isin(fishset); df["ref"] = [REF.referent_class.get(e, "-") if e in REF.index else "-" for e in df.el]
    df = df.sort_values("T", ascending=False)
    res["theophoric_top15"] = df.head(15)[["el", "n", "R", "D", "S", "T", "PH", "fish", "ref"]].round(3).values.tolist()
    res["partner_hub_top15"] = df.sort_values("PH", ascending=False).head(15)[["el", "n", "R", "PH", "S", "fish", "ref"]].round(3).values.tolist()
    df.round(4).to_csv(D.HERE / f"core_sign_table_{split}.csv", index=False)
    # fish enrichment, frequency-matched null on T, D, S
    fe = {}
    logn = np.log(df.n.values); isf = df.fish.values
    for k, sign in (("T", 1), ("D", 1), ("S", -1), ("R", 1), ("PH", 1)):
        v = np.nan_to_num(df[k].values, nan=np.nanmean(df[k].values)) * sign
        obs = v[isf].mean()
        null = []
        others = np.where(~isf)[0]
        for _ in range(5000):
            pick = []
            for i in np.where(isf)[0]:
                cand = [j for j in others if abs(logn[j] - logn[i]) < 0.4 and j not in pick]
                pick.append(rng.choice(cand if cand else others))
            null.append(v[pick].mean())
        null = np.array(null)
        fe[k] = dict(fish_mean=round(float(obs * sign), 3), null_mean=round(float(np.mean(null) * sign), 3),
                     p_one_sided=round(float((1 + (null >= obs).sum()) / 5001), 4))
    res["fish_theophoric_freq_matched"] = fe
    res["fish_rank_T"] = [int(r) + 1 for r in np.where(df.fish.values)[0]]
    # calibration of signature and coherence on reference corpora (Indus dev size)
    n_single = sum(1 for c in inc if len(c) == 1); n_multi = sum(1 for c in inc if len(c) > 1)
    s2, s1 = D.sanskrit_names(); u2, u1 = D.ur3_names()
    res["calib_theophoric"] = {
        "ur3": ref_theophoric(u2, u1, D.is_deity_ur, n_multi, n_single, 300, rng),
        "sanskrit": ref_theophoric(s2, s1, lambda e: e in D.SKT_DEITY, n_multi, n_single, 300, rng)}
    res["calib_coherence"] = {
        "ur3": ref_coherence(u2, D.is_deity_ur, n_multi, 100, rng),
        "sanskrit": ref_coherence(s2, lambda e: e in D.SKT_DEITY, n_multi, 100, rng)}
    for k, v in res.items():
        print(k, ":", json.dumps(v, default=str) if not isinstance(v, dict) or len(json.dumps(v, default=str)) < 300 else "")
        if isinstance(v, dict) and len(json.dumps(v, default=str)) >= 300:
            for kk, vv in v.items():
                print("    ", kk, vv)
    json.dump(res, open(D.HERE / f"s2_classes_{split}.json", "w"), indent=1, default=str)
