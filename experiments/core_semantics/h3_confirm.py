"""Pre-registered confirmatory tests (docs/prereg/2026-11-14_core_semantics.md).

Usage:
  .venv/bin/python experiments/core_semantics/h3_confirm.py devcv     # dev-only rehearsal: dev split in 2 halves
  .venv/bin/python experiments/core_semantics/h3_confirm.py heldout   # the registered run (train = dev, test = held-out)
Tests: HD1 HD2 (head direction), HD3 (pair order transfer), SC1 (fish substitution coherence), SC3 (fish in
compounds, R), SC4 (fish partners productive, PH), SC5 (fish-fish compounding), SC6 (Mantel object type),
SC7 (fish partner set transfer).
"""
import sys, json
from collections import Counter, defaultdict
import numpy as np
from scipy.stats import binomtest
sys.path.insert(0, __import__("os").path.dirname(__file__))
import cs_data as D
import h1_head as H
import s2_classes as S2

FISH = set(D.FISH)
REPS = 5000


def adjacent_pairs(inc):
    """unordered adjacent pair -> [count in sorted order, count reversed], weighted by distinct texts."""
    by = defaultdict(lambda: [0, 0])
    for c, k in inc.items():
        for a, b in zip(c, c[1:]):
            if a == b:
                continue
            x, y = sorted((a, b))
            by[(x, y)][0 if (a, b) == (x, y) else 1] += k
    return by


def hd3(train_inc, test_inc):
    tr = adjacent_pairs(train_inc); te = adjacent_pairs(test_inc)
    agree = n = 0; npairs = 0
    for p, (f, r) in tr.items():
        tot = f + r
        if tot < 2 or max(f, r) / tot < 2 / 3:
            continue
        maj = 0 if f >= r else 1
        if p in te:
            tf, trv = te[p]
            if tf + trv:
                npairs += 1
                agree += tf if maj == 0 else trv
                n += tf + trv
    p = binomtest(agree, n, 0.5, alternative="greater").pvalue if n else 1.0
    return dict(train_pairs_with_majority=sum(1 for v in tr.values() if sum(v) >= 2 and max(v) / sum(v) >= 2 / 3),
                test_pairs=npairs, test_occurrences=n, agree=agree, share=round(agree / n, 3) if n else None,
                p=float(p))


def fish_sig(test_occ, kmin, rng):
    B = S2.build(test_occ, kmin=kmin)
    signs = B["signs"]
    feats = {s: B["frames"][s] + B["partners"][s] for s in signs}
    S = S2.ppmi_cos(signs, feats)
    sc1 = S2.set_coherence(S, signs, FISH, REPS, rng, B["cnt"])
    total = Counter({s: B["cnt"][s] for s in B["cnt"]})
    df = S2.theophoric_table(signs, B["mtypes"], B["multi"], B["standalone"], total)
    isf = df.el.isin(FISH).values; logn = np.log(df.n.values)
    out = {}
    for k in ("R", "PH"):
        v = df[k].values.astype(float)
        ok = ~np.isnan(v)
        fidx = np.where(isf & ok)[0]; others = np.where(~isf & ok)[0]
        obs = v[fidx].mean(); null = []
        for _ in range(REPS):
            pick = []
            for i in fidx:
                cand = [j for j in others if abs(logn[j] - logn[i]) < 0.4 and j not in pick]
                pick.append(rng.choice(cand if cand else others))
            null.append(v[pick].mean())
        null = np.array(null)
        out[k] = dict(fish=[df.el.values[i] for i in fidx], fish_mean=round(float(obs), 3),
                      null_mean=round(float(null.mean()), 3), p=float((1 + (null >= obs).sum()) / (1 + REPS)))
    types = ["seal", "sealing", "miniature tablet", "copper tablet", "pottery graffito"]
    Pobj = np.array([[B["obj"][s][t] for t in types] for s in signs], float) + 0.5
    Pobj /= Pobj.sum(1, keepdims=True)
    Sobj = 1 - 0.5 * np.abs(Pobj[:, None, :] - Pobj[None, :, :]).sum(-1)
    sc6 = S2.mantel(S, Sobj, 2000, rng)
    return dict(n_signs=len(signs), SC1=sc1, SC3=out["R"], SC4=out["PH"], SC6=sc6)


def sc5(test_inc, rng):
    """share of multi-sign core types (distinct) with >=2 fish tokens vs a shuffle of signs across multi-sign cores."""
    cores = [c for c in test_inc if len(c) > 1]
    obs = np.mean([sum(s in FISH for s in c) >= 2 for c in cores])
    toks = [s for c in cores for s in c]; lens = [len(c) for c in cores]
    null = []
    for _ in range(REPS):
        p = rng.permutation(toks); i = 0; k = 0
        for L in lens:
            k += sum(s in FISH for s in p[i:i + L]) >= 2; i += L
        null.append(k / len(cores))
    null = np.array(null)
    return dict(n_cores=len(cores), obs=round(float(obs), 4), null_mean=round(float(null.mean()), 4),
                p=float((1 + (null >= obs).sum()) / (1 + REPS)))


def sc7(train_inc, test_inc, top=5):
    def partners(inc):
        c = Counter()
        for core in inc:
            if len(core) > 1 and any(s in FISH for s in core):
                for s in core:
                    if s not in FISH:
                        c[s] += 1
        return c
    trp = partners(train_inc)
    P = [s for s, _ in trp.most_common(top)]
    tep = partners(test_inc)
    hit = sum(tep[s] for s in P); n = sum(tep.values())
    base_c = Counter(s for core in test_inc if len(core) > 1 for s in core if s not in FISH)
    base = sum(base_c[s] for s in P) / sum(base_c.values())
    p = binomtest(hit, n, base, alternative="greater").pvalue if n else 1.0
    return dict(partner_set=P, test_fish_partner_tokens=n, hits=hit, share=round(hit / n, 3) if n else None,
                baseline_share=round(base, 3), p=float(p))


def run(train_inc, test_inc, test_occ, kmin, rng, n_label):
    two = [c for c in test_inc if len(c) == 2]
    single = {o["core"][0] for o in test_occ if len(o["core"]) == 1 and not o["num_adj"]}
    hd = H.indus_test(two, single, 2000, rng)
    n = len([t for t in two if t[0] != t[1]])
    s2, s1 = D.sanskrit_names(); u2, u1 = D.ur3_names()
    calib = {"sanskrit": H.subsample(list(s2), s1, n, 1000, rng), "ur3": H.subsample(list(u2), u1, n, 1000, rng)}
    res = {"label": n_label, "n_two_types": n,
           "HD1_HFI_prod": hd["bootstrap"]["HFI_prod"] | {"observed": hd["observed"]["HFI_prod"], "order_null_p": hd["p_two_sided"]["HFI_prod"]},
           "HD2_hub_pos2": hd["bootstrap"]["hub_pos2"] | {"observed": hd["observed"]["hub_pos2"], "order_null_p": hd["p_two_sided"]["hub_pos2"]},
           "head_other": {k: hd["observed"][k] for k in ("logV", "HFI_sa")},
           "calibration_at_n": calib,
           "HD3_pair_order": hd3(train_inc, test_inc)}
    res.update(fish_sig(test_occ, kmin, rng))
    res["SC5_fish_fish"] = sc5(test_inc, rng)
    res["SC7_fish_partner_set"] = sc7(train_inc, test_inc)
    return res


def verdicts(r):
    a = 0.05 / 9
    v = {}
    h1 = r["HD1_HFI_prod"]; v["HD1"] = h1["lo"] <= 0.5 <= h1["hi"] and h1["lo"] > 0.30
    h2 = r["HD2_hub_pos2"]; v["HD2"] = h2["lo"] <= 0.5 <= h2["hi"] and h2["lo"] > 0.35
    h3 = r["HD3_pair_order"]; v["HD3"] = bool(h3["share"] is not None and h3["share"] >= 0.75 and h3["p"] < a)
    v["SC1"] = r["SC1"]["p"] < a
    v["SC3"] = r["SC3"]["p"] < a
    v["SC4"] = r["SC4"]["p"] < a
    v["SC5"] = r["SC5_fish_fish"]["p"] < a
    v["SC6"] = r["SC6"]["rho"] > 0 and r["SC6"]["p"] < a
    v["SC7"] = r["SC7_fish_partner_set"]["p"] < a
    return {k: bool(x) for k, x in v.items()}


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "devcv"
    rng = np.random.default_rng(2026)
    if mode == "heldout":
        tr_inc, _ = D.indus_types("dev"); te_inc, te_occ = D.indus_types("heldout")
        res = run(tr_inc, te_inc, te_occ, 3, rng, "train=dev test=heldout")
    else:
        inc, occ = D.indus_types("dev")
        texts = sorted({o["text"] for o in occ})
        perm = np.random.default_rng(0).permutation(len(texts))
        A = {texts[i] for i in perm[: len(texts) // 2]}
        def sub(keep):
            oc = [o for o in occ if (o["text"] in A) == keep]
            ic = Counter(); seen = set()
            for o in oc:
                if (o["text"], o["core"]) not in seen:
                    seen.add((o["text"], o["core"])); ic[o["core"]] += 1
            return dict(ic), oc
        tr_inc, _ = sub(True); te_inc, te_occ = sub(False)
        res = run(tr_inc, te_inc, te_occ, 3, rng, "dev half A -> dev half B (rehearsal)")
    res["verdicts"] = verdicts(res)
    print(json.dumps(res, indent=1, default=str))
    json.dump(res, open(D.HERE / f"h3_confirm_{mode}.json", "w"), indent=1, default=str)
