"""Q3. Positional classes. For every sign attested on >=10 distinct texts: distribution over initial / medial / final /
standalone positions (clean texts only: no break mark, flagged complete). Null: within-text shuffle (keeps each text's
sign multiset and length). Clustering: k-means on the 4-d profile, K chosen by bootstrap stability (adjusted Rand).
Held-out: classes learned on dev, profiles re-measured on held-out texts.
"""
import json
import random
from collections import Counter, defaultdict

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score

from common import (ROOT, bh, distinct, icit_texts, is_clean, load_bridge, m77_split, m77_texts, save_json, signs)

rng = np.random.default_rng(20261114)
random.seed(20261114)
POS = ["initial", "medial", "final", "standalone"]
STROKES = set("M%s" % k for k in json.load(open(ROOT / "sources/shaunmortal_indus/data/stroke_signs.json"))["short"]) | \
    set("M%s" % k for k in json.load(open(ROOT / "sources/shaunmortal_indus/data/stroke_signs.json")).get("tall", {}))


def profiles(texts):
    cnt = defaultdict(lambda: np.zeros(4)); ntext = Counter(); tokens = Counter()
    for s in texts:
        tokens.update(s)
        for x in set(s):
            ntext[x] += 1
        if len(s) == 1:
            cnt[s[0]][3] += 1; continue
        for i, x in enumerate(s):
            cnt[x][0 if i == 0 else (2 if i == len(s) - 1 else 1)] += 1
    return cnt, ntext, tokens


def null_expect(texts, reps=300):
    """Within-text shuffle null: expected positional counts and permutation distribution."""
    sims = defaultdict(list)
    for _ in range(reps):
        sh = []
        for s in texts:
            s = s[:]; random.shuffle(s); sh.append(s)
        c, _, _ = profiles(sh)
        for k, v in c.items():
            sims[k].append(v.copy())
    return {k: np.array(v) for k, v in sims.items()}


def positional_tests(texts, signs_keep):
    obs, _, _ = profiles(texts)
    sims = null_expect(texts)
    out = {}
    for x in signs_keep:
        o = obs[x]; S = sims[x]; m = S.mean(0)
        # statistic: G-like distance of profile from null mean over initial/medial/final (standalone fixed by length)
        def stat(v):
            return np.sum((v[:3] - m[:3]) ** 2 / (m[:3] + 0.5))
        so = stat(o); sn = np.array([stat(v) for v in S])
        p = (np.sum(sn >= so) + 1) / (len(sn) + 1)
        out[x] = {"obs": o.tolist(), "null_mean": m.tolist(), "p": float(p),
                  "init_ratio": float((o[0] + 0.5) / (m[0] + 0.5)), "final_ratio": float((o[2] + 0.5) / (m[2] + 0.5))}
    q = bh([out[x]["p"] for x in signs_keep])
    for x, qq in zip(signs_keep, q):
        out[x]["q"] = qq
    return out


def feat(cnt, keep):
    X = np.array([cnt[x] / cnt[x].sum() for x in keep])
    return X


def choose_k(texts, keep, ks=range(2, 9), B=30):
    """bootstrap stability: resample texts, recompute profiles, cluster, compare to full-data clustering."""
    cnt, _, _ = profiles(texts)
    X = feat(cnt, keep)
    res = {}
    for k in ks:
        base = KMeans(k, n_init=20, random_state=0).fit(X)
        aris = []
        for b in range(B):
            idx = rng.integers(0, len(texts), len(texts))
            cb, _, _ = profiles([texts[i] for i in idx])
            Xb = np.array([cb[x] / cb[x].sum() if cb[x].sum() else np.ones(4) / 4 for x in keep])
            lb = KMeans(k, n_init=10, random_state=b).fit_predict(Xb)
            aris.append(adjusted_rand_score(base.labels_, lb))
        res[k] = {"ARI_mean": float(np.mean(aris)), "ARI_sd": float(np.std(aris)), "silhouette": float(silhouette_score(X, base.labels_))}
    return res


def name_cluster(c):
    i, m, f, s = c
    if s > 0.35:
        return "standalone-prone"
    if i > 0.45:
        return "opener"
    if f > 0.45:
        return "closer"
    if m > 0.7:
        return "medial-core"
    if i > f and i > 0.2:
        return "initial-leaning"
    if f > i and f > 0.2:
        return "final-leaning"
    return "mixed"


def run(texts, label, minn=10, K=None):
    cnt, ntext, tokens = profiles(texts)
    keep = sorted([x for x in ntext if ntext[x] >= minn], key=lambda x: -ntext[x])
    tests = positional_tests(texts, keep)
    stab = choose_k(texts, keep)
    if K is None:
        # largest K whose bootstrap ARI >= 0.6 (fall back to best ARI)
        good = [k for k in stab if stab[k]["ARI_mean"] >= 0.6]
        K = max(good) if good else max(stab, key=lambda k: stab[k]["ARI_mean"])
    X = feat(cnt, keep)
    km = KMeans(K, n_init=50, random_state=0).fit(X)
    names = {}
    for c in range(K):
        nm = name_cluster(km.cluster_centers_[c]); base = nm; j = 2
        while nm in names.values():
            nm = f"{base}-{j}"; j += 1
        names[c] = nm
    classes = {x: names[l] for x, l in zip(keep, km.labels_)}
    summary = {}
    for c in range(K):
        mem = [x for x in keep if classes[x] == names[c]]
        summary[names[c]] = {"n_signs": len(mem), "centroid": dict(zip(POS, map(float, km.cluster_centers_[c]))),
                             "tokens": int(sum(tokens[x] for x in mem)),
                             "members_top": sorted(mem, key=lambda x: -tokens[x])[:15],
                             "stroke_signs_in_class": sorted(set(mem) & STROKES, key=lambda x: -tokens[x])}
    n_sig = sum(1 for x in keep if tests[x]["q"] < 0.05)
    return {"label": label, "texts": len(texts), "signs_n_ge_min": len(keep), "K": K, "stability": stab,
            "classes_summary": summary, "n_positional_q05": n_sig,
            "per_sign": {x: {"ntext": ntext[x], "tokens": tokens[x], "profile": dict(zip(POS, map(float, cnt[x] / cnt[x].sum()))),
                             "counts": cnt[x].tolist(), "class": classes[x], "p_positional": tests[x]["p"], "q": tests[x]["q"],
                             "init_ratio_vs_shuffle": tests[x]["init_ratio"], "final_ratio_vs_shuffle": tests[x]["final_ratio"]}
                         for x in keep},
            "_centers": km.cluster_centers_.tolist(), "_names": [names[c] for c in range(K)]}


if __name__ == "__main__":
    T = distinct(m77_texts())
    clean = [signs(t["seq"]) for t in T if is_clean(t)]
    full = run(clean, "M77 distinct clean")
    dev, ho = m77_split()
    devc = [signs(t["seq"]) for t in dev if is_clean(t)]
    hoc = [signs(t["seq"]) for t in ho if is_clean(t)]
    rdev = run(devc, "M77 dev clean", K=full["K"])
    # held-out: profile of dev-classified signs measured on held-out; nearest-centroid agreement
    hcnt, hn, _ = profiles(hoc)
    C = np.array(rdev["_centers"]); agree = tot = 0; cls_ho = defaultdict(lambda: np.zeros(4))
    for x, v in rdev["per_sign"].items():
        cls_ho[v["class"]] += hcnt[x]
        if hn[x] >= 5:
            p = hcnt[x] / hcnt[x].sum()
            pred = rdev["_names"][int(np.argmin(((C - p) ** 2).sum(1)))]
            agree += pred == v["class"]; tot += 1
    # null for agreement: shuffle class labels among signs
    labs = [v["class"] for v in rdev["per_sign"].values()]
    heldout = {"signs_with_ge5_heldout_texts": tot, "nearest_centroid_agreement": agree / tot,
               "chance_agreement_label_shuffle": float(sum((labs.count(l) / len(labs)) ** 2 for l in set(labs))),
               "heldout_class_profiles": {k: dict(zip(POS, map(float, v / v.sum()))) for k, v in cls_ho.items()}}
    # dev vs full class agreement
    common = [x for x in rdev["per_sign"] if x in full["per_sign"]]
    # ICIT replication (Wells codes, native)
    I = distinct(icit_texts())
    ic = [signs(t["seq"]) for t in I if is_clean(t)]
    ricit = run(ic, "ICIT distinct clean")
    dh = [signs(t["seq"]) for t in I if is_clean(t) and t["site"] == "Dholavira"]
    # Dholavira: apply ICIT classes, measure Dholavira profile per class
    dcnt, dn, _ = profiles(dh)
    dcls = defaultdict(lambda: np.zeros(4))
    for x, v in ricit["per_sign"].items():
        dcls[v["class"]] += dcnt[x]
    # cross-corpus: bridge W->M, compare class of the same sign
    br = load_bridge(); cross = Counter()
    for w, v in ricit["per_sign"].items():
        m = br.get(w)
        if m and m in full["per_sign"]:
            cross[(full["per_sign"][m]["class"], v["class"])] += 1
    # rho of final share M vs W for bridged signs
    from scipy.stats import spearmanr
    pairs = [(full["per_sign"][br[w]]["profile"], v["profile"]) for w, v in ricit["per_sign"].items() if br.get(w) in full["per_sign"]]
    rho = {p: float(spearmanr([a[p] for a, _ in pairs], [b[p] for _, b in pairs]).statistic) for p in POS}
    out = {"M77_full": full, "M77_dev": rdev, "heldout_check": heldout, "ICIT": ricit,
           "Dholavira_profile_by_ICIT_class": {k: (dict(zip(POS, map(float, v / v.sum()))) if v.sum() else None) | {"n": float(v.sum())} for k, v in dcls.items()},
           "M77_vs_ICIT_class_crosstab": {f"{a} | {b}": c for (a, b), c in cross.items()},
           "M77_vs_ICIT_profile_rho_bridged": rho, "n_bridged_signs": len(pairs),
           "dev_vs_full_class_agreement": float(np.mean([rdev["per_sign"][x]["class"] == full["per_sign"][x]["class"] for x in common]))}
    save_json("q3_positional", out)
    json.dump(out, open(ROOT / "experiments/structure/positional.json", "w"), indent=1, default=float)
    for r in (full, rdev, ricit):
        print(r["label"], r["texts"], "signs", r["signs_n_ge_min"], "K", r["K"], "positional q<.05:", r["n_positional_q05"])
        print({k: (round(v["ARI_mean"], 2), round(v["silhouette"], 2)) for k, v in r["stability"].items()})
        for k, v in r["classes_summary"].items():
            print("  ", k, v["n_signs"], v["tokens"], {a: round(b, 2) for a, b in v["centroid"].items()}, v["members_top"][:10], "strokes:", v["stroke_signs_in_class"])
    print(heldout)
    print(out["Dholavira_profile_by_ICIT_class"])
    print(out["M77_vs_ICIT_class_crosstab"], rho, out["dev_vs_full_class_agreement"])
