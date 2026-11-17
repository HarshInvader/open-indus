"""Controls (no Indus data is touched here).

C1  gold-to-gold transfer: Ur III seal slots aligned to Old Babylonian seal slots (and to the small
    Old Akkadian + Old Assyrian pool), both cut to Indus seal size. Does each slot find its
    same-meaning partner?
C2  planted blind control: Ur III cut to Indus size, words relabelled to random ids, slots INDUCED
    blindly from distribution (no gold labels), then aligned to gold OB slots. Does each induced
    class get the meaning of the gold slot that most of its tokens really belong to?
Also freezes the standardisation (mean/sd from cuneiform slots only) and the calibrated acceptance
threshold for a match, written to controls.json for the pre-registered Indus run.

usage: .venv/bin/python -I experiments/genre_alignment/ga_controls.py
"""
import json, math, random, sys
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from sklearn.cluster import KMeans

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ga_slots as GS
import ga_core as GC

N_INDUS = {"all": 1629, "dev": None, "heldout": None}
REPS = 40


def relabel(texts, rng):
    vocab = sorted({t for x in texts for t in x["toks"]}); ids = list(range(len(vocab))); rng.shuffle(ids)
    m = dict(zip(vocab, ids))
    return [{"toks": [f"w{m[t]}" for t in x["toks"]], "slots": x["slots"], "gold": x["slots"]} for x in texts]


def induce(texts, k=6, fmin=5, seed=0):
    """blind positional-class induction: frequent types clustered on position/context features,
    rare types form one open class 'R'. Returns texts with induced slot labels (gold kept)."""
    df = Counter(t for x in texts for t in set(x["toks"]))
    freq = [t for t, n in df.items() if n >= fmin]
    fs = set(freq)
    ini = Counter(); fin = Counter(); pos = defaultdict(list); tot = Counter()
    L = defaultdict(Counter); Rn = defaultdict(Counter)
    for x in texts:
        s = x["toks"]; n = len(s)
        for i, t in enumerate(s):
            tot[t] += 1
            if i == 0: ini[t] += 1
            if i == n - 1: fin[t] += 1
            pos[t].append(i / (n - 1) if n > 1 else 0.5)
            L[t][s[i - 1] if i > 0 and s[i - 1] in fs else ("<s>" if i == 0 else "<rare>")] += 1
            Rn[t][s[i + 1] if i < n - 1 and s[i + 1] in fs else ("</s>" if i == n - 1 else "<rare>")] += 1
    def H(c):
        p = np.array(list(c.values()), float); p /= p.sum(); return float(-(p * np.log2(p)).sum())
    X = np.array([[ini[t] / tot[t], fin[t] / tot[t], np.mean(pos[t]), math.log(tot[t]),
                   H(L[t]), H(Rn[t]), L[t]["<rare>"] / tot[t], Rn[t]["<rare>"] / tot[t]] for t in freq])
    X = (X - X.mean(0)) / (X.std(0) + 1e-9)
    lab = KMeans(n_clusters=min(k, len(freq)), n_init=10, random_state=seed).fit_predict(X)
    cl = {t: f"c{l}" for t, l in zip(freq, lab)}
    return [dict(x, slots=[cl.get(t, "R") for t in x["toks"]]) for x in texts]


def majority_gold(texts):
    c = defaultdict(Counter)
    for x in texts:
        for s, g in zip(x["slots"], x["gold"]): c[s][g] += 1
    return {s: cc.most_common(1)[0][0] for s, cc in c.items()}, {s: cc.most_common(1)[0][1] / sum(cc.values()) for s, cc in c.items()}


def random_match_expect(A_lab, B_keys, truth, reps=4000, seed=0):
    rng = random.Random(seed); hits = []
    for _ in range(reps):
        perm = rng.sample(B_keys, len(A_lab)) if len(B_keys) >= len(A_lab) else None
        hits.append(sum(truth[a] == b for a, b in zip(A_lab, perm)) / len(A_lab))
    return float(np.mean(hits)), np.array(hits)


def main():
    titles, lords = GS.build_lexicons()
    cor = {g: GS.cun_corpus(g, titles, lords) for g in ("ur3", "ob", "oakk", "oa")}
    cor["oth"] = cor["oakk"] + cor["oa"]
    N = N_INDUS["all"]
    res = {"n_texts": {g: len(v) for g, v in cor.items()}, "N_cut": N}

    # frozen standardisation from full-size-cut cuneiform reference slots (seed 0)
    rng = random.Random(0)
    ref = [GC.fingerprints(GC.subsample(cor[g], N, rng), seed=1) for g in ("ur3", "ob")]
    M = np.vstack([v for fp in ref for v in fp.values()])
    mu, sd = M.mean(0), M.std(0); sd[sd == 0] = 1
    Z = lambda fp: {k: (v - mu) / sd for k, v in fp.items()}
    res["standardisation"] = {"mu": mu.tolist(), "sd": sd.tolist(), "features": GC.FEATURES}
    res["ref_fingerprints"] = {g: {k: dict(zip(GC.FEATURES, np.round(v, 3).tolist())) for k, v in fp.items()}
                               for g, fp in zip(("ur3", "ob"), ref)}

    # ---------------- C1 gold-to-gold
    c1 = defaultdict(list); good_d, bad_d = [], []; pairtab = defaultdict(Counter)
    for rep in range(REPS):
        r = random.Random(100 + rep)
        for src, tgt in (("ur3", "ob"), ("ob", "ur3"), ("ur3", "oth")):
            A = Z(GC.fingerprints(GC.subsample(cor[src], N, r), seed=rep))
            B = Z(GC.fingerprints(GC.subsample(cor[tgt], N, r), seed=rep, min_runs=10 if tgt == "oth" else GC.MIN_RUNS))
            if len(A) > len(B):      # Hungarian matches the smaller side completely; score src slots present in tgt
                pairs_r, _, _ = GC.align(B, A); pairs = [(y, x, d) for x, y, d in pairs_r]
                a, b, D = GC.dist_matrix(A, B)
            else:
                pairs, m, (a, b, D) = GC.align(A, B)
            common = [x for x, y, d in pairs if x in B]
            hit = sum(1 for x, y, d in pairs if x == y) / len(common)
            c1[f"{src}->{tgt}"].append(hit)
            for x, y, d in pairs:
                if x in B: pairtab[f"{src}->{tgt}:{x}"][y] += 1
            if (src, tgt) == ("ur3", "ob"):
                for i, x in enumerate(a):
                    for j, y in enumerate(b):
                        (good_d if x == y else bad_d).append(D[i, j])
    # expected hit rate under random matching (Ur III 7 slots onto OB slots)
    A0 = Z(GC.fingerprints(GC.subsample(cor["ur3"], N, random.Random(5)), seed=5))
    B0 = Z(GC.fingerprints(GC.subsample(cor["ob"], N, random.Random(5)), seed=5))
    exp, _ = random_match_expect(sorted(A0), sorted(B0), {k: k for k in A0})
    p_ob = GC.column_perm_null(A0, B0, n=1000, seed=1)
    _, m_obs, _ = GC.align(A0, B0)
    res["C1"] = {
        "hit_mean": {k: float(np.mean(v)) for k, v in c1.items()}, "random_expect": exp,
        "ur3_slots": sorted(A0), "ob_slots": sorted(B0),
        "colperm_p_meanDist": float((p_ob <= m_obs).mean()), "meanDist_obs": m_obs,
        "meanDist_null_mean": float(p_ob.mean()),
        "pair_freq": {k: dict(v) for k, v in pairtab.items()},
        "dist_correct_median": float(np.median(good_d)), "dist_wrong_median": float(np.median(bad_d)),
        "dist_wrong_q05": float(np.quantile(bad_d, 0.05)), "dist_correct_q90": float(np.quantile(good_d, 0.9)),
    }
    # acceptance threshold: largest tau with precision >= 0.8 among pairs d < tau (C1 all pairs)
    allp = sorted([(d, 1) for d in good_d] + [(d, 0) for d in bad_d])
    tau = 0.0; tp = 0
    for i, (d, ok) in enumerate(allp, 1):
        tp += ok
        if tp / i >= 0.8: tau = d
    res["C1"]["tau_precision80"] = float(tau)
    rel = defaultdict(list)
    for key, cnt in pairtab.items():
        x = key.split(":")[1]; rel[x].append(cnt.get(x, 0) / sum(cnt.values()))
    res["C1"]["slot_reliability"] = {x: float(np.mean(v)) for x, v in rel.items()}
    print("C1", {k: v for k, v in res["C1"].items() if k != "pair_freq"})

    # ---------------- C2 planted blind induction
    c2 = defaultdict(list); c2w = defaultdict(list); c2exp = defaultdict(list); purity = defaultdict(list)
    for k in (4, 6, 8):
        for rep in range(REPS // 2):
            r = random.Random(1000 + rep)
            U = relabel(GC.subsample(cor["ur3"], N, r), r)
            Ui = induce(U, k=k, seed=rep)
            maj, pur = majority_gold(Ui)
            A = Z(GC.fingerprints(Ui, seed=rep))
            B = Z(GC.fingerprints(GC.subsample(cor["ob"], N, r), seed=rep))
            pairs, m, _ = GC.align(A, B)
            ok = [(x, y) for x, y, d in pairs]
            hit = sum(maj[x] == y for x, y in ok) / len(ok)
            tokc = Counter(s for x in Ui for s in x["slots"])
            w = sum(tokc[x] for x, y in ok if maj[x] == y) / sum(tokc[x] for x, y in ok)
            e, _ = random_match_expect(sorted(A), sorted(B), maj, reps=500, seed=rep)
            c2[k].append(hit); c2w[k].append(w); c2exp[k].append(e)
            purity[k].append(float(np.mean([pur[x] for x in A])))
    res["C2"] = {f"k{k}": {"hit_mean": float(np.mean(c2[k])), "token_weighted_hit": float(np.mean(c2w[k])),
                           "random_expect": float(np.mean(c2exp[k])), "class_purity": float(np.mean(purity[k])),
                           "p_hit_gt_random(sign)": float(np.mean(np.array(c2[k]) <= np.array(c2exp[k])))}
                 for k in (4, 6, 8)}
    print("C2", res["C2"])
    json.dump(res, open(HERE / "controls.json", "w"), indent=1)


if __name__ == "__main__":
    main()
