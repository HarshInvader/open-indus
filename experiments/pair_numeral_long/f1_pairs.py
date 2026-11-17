"""F1. Bipartite (two inventories: emblem x individual, modifier x head) or compound (one inventory)?

Usage: .venv/bin/python experiments/pair_numeral_long/f1_pairs.py dev|heldout
  dev     : all graph metrics on dev, reference corpora + simulations at matched size, dev split-half
            rehearsal of the order-rule transfer test.  No held-out data touched.
  heldout : the registered tests (docs/prereg/pair_numeral_long.md): graph metrics on held-out pairs and
            the order-rule transfer dev -> held-out on pair types never seen in dev.
"""
import sys, json
import numpy as np
from collections import Counter
from scipy.stats import binomtest
from common import *

mode = sys.argv[1] if len(sys.argv) > 1 else "dev"
rng = np.random.default_rng(11)
R = {}


def show(name, s):
    print(f"{name:26s} E={s['n_edges']:4d} V={s['n_nodes']:4d} POL {s['pol']:.3f} (null {s['pol_null']:.3f}, ex {s['pol_excess']:+.3f}, p={s['pol_p']:.3f})"
          f"  H {s['H']:.3f} (null {s['H_null']:.3f})  both {s['both']:.2f}"
          f"  DICUT {s['dicut']:.3f} (null {s['dicut_null']:.3f}, ex {s['dicut_excess']:+.3f}, p={s['dicut_p']:.3f})"
          f"  MAXCUT {s['maxcut']:.3f} (null {s['maxcut_null']:.3f}, ex {s['maxcut_excess']:+.3f}, p={s['maxcut_p']:.3f})")


def sign_table(pairs, kmin=3):
    o, i = degrees([e for e in pairs if e[0] != e[1]])
    rows = []
    for s in set(o) | set(i):
        d = o[s] + i[s]
        if d >= kmin:
            rows.append((s, o[s], i[s], round(o[s] / d, 2)))
    return sorted(rows, key=lambda r: -(r[1] + r[2]))


if mode == "dev":
    dev = indus_pair_types("dev")
    all_types = list(dev)
    rec = [k for k, v in dev.items() if v >= 2]
    print(f"dev pair types {len(all_types)} (tokens {sum(dev.values())}); recurring (>=2 texts) {len(rec)}")
    R["indus_dev_all"] = graph_stats(all_types, rng); show("Indus dev, all pair types", R["indus_dev_all"])
    R["indus_dev_recurring"] = graph_stats(rec, rng, kmin=2); show("Indus dev, recurring (k>=2)", R["indus_dev_recurring"])
    st = sign_table(all_types)
    first = [r for r in st if r[3] >= 0.8]; second = [r for r in st if r[3] <= 0.2]; both = [r for r in st if 0.2 < r[3] < 0.8]
    print(f"signs deg>=3: {len(st)}; first-only(>=.8) {len(first)}, second-only(<=.2) {len(second)}, both {len(both)}")
    print(" top signs (sign,out,in,outshare):", st[:25])
    R["indus_dev_sign_classes"] = dict(n=len(st), first=[r[0] for r in first], second=[r[0] for r in second],
                                       both=[r[0] for r in both], table=st)
    # share of edge types whose both ends are 'both' signs (productive compounding families)
    # references at matched number of pair types (all types)
    N = len(all_types)
    R["refs"] = {}
    for nm in ("chinese_clan", "chinese_given", "sanskrit", "ur3"):
        P = ref_pairs(nm)
        res = []
        for rep in range(5):
            idx = rng.choice(len(P), N, replace=False)
            res.append(graph_stats([P[k] for k in idx], rng, nnull=100))
        agg = {k: [float(np.mean([r[k] for r in res])), float(np.min([r[k] for r in res])), float(np.max([r[k] for r in res]))]
               for k in res[0] if isinstance(res[0][k], (int, float))}
        R["refs"][nm] = agg
        print(f"{nm:26s} pol_ex {agg['pol_excess'][0]:+.3f} [{agg['pol_excess'][1]:+.3f},{agg['pol_excess'][2]:+.3f}]"
              f" both {agg['both'][0]:.2f} dicut_ex {agg['dicut_excess'][0]:+.3f} [{agg['dicut_excess'][1]:+.3f},{agg['dicut_excess'][2]:+.3f}]"
              f" maxcut_ex {agg['maxcut_excess'][0]:+.3f} [{agg['maxcut_excess'][1]:+.3f},{agg['maxcut_excess'][2]:+.3f}]  raw pol {agg['pol'][0]:.3f} dicut {agg['dicut'][0]:.3f} maxcut {agg['maxcut'][0]:.3f}")
    R["sims"] = {}
    for kind, q in (("emblem_x_name", 1), ("blazon", 1), ("compound", 0), ("mix", 0.25), ("mix", 0.5), ("mix", 0.75)):
        res = [graph_stats(sim_pairs(kind, N, rng, q), rng, nnull=100) for _ in range(5)]
        agg = {k: [float(np.mean([r[k] for r in res])), float(np.min([r[k] for r in res])), float(np.max([r[k] for r in res]))]
               for k in res[0] if isinstance(res[0][k], (int, float))}
        nm = kind if kind != "mix" else f"mix_q{q}"
        R["sims"][nm] = agg
        print(f"sim {nm:22s} pol_ex {agg['pol_excess'][0]:+.3f} [{agg['pol_excess'][1]:+.3f},{agg['pol_excess'][2]:+.3f}]"
              f" both {agg['both'][0]:.2f} dicut_ex {agg['dicut_excess'][0]:+.3f} maxcut_ex {agg['maxcut_excess'][0]:+.3f}  raw pol {agg['pol'][0]:.3f}")
    # order-rule transfer rehearsal: split dev texts in halves (by pair-type counter split is not possible
    # without texts, so re-derive pairs per text)
    import cs_data
    occ = cs_data.indus_occurrences("dev")
    texts = sorted({o["text"] for o in occ})
    accs = []
    for rep in range(50):
        r2 = np.random.default_rng(rep)
        A = set(r2.choice(len(texts), len(texts) * 3 // 4, replace=False))
        ta = {texts[k] for k in A}
        ca, cb = Counter(), Counter(); seen = set()
        for o in occ:
            c = o["core"]
            for a, b in zip(c, c[1:]):
                if (o["text"], a, b) in seen: continue
                seen.add((o["text"], a, b))
                (ca if o["text"] in ta else cb)[(a, b)] += 1
        k, n, _ = order_rule_accuracy(ca, cb)
        accs.append((k, n))
    acc = np.array([k / n for k, n in accs]); ns = np.array([n for k, n in accs])
    print(f"dev 75/25 rehearsal: order-rule accuracy on unseen pair types {acc.mean():.3f} (sd {acc.std():.3f}), n per split {ns.mean():.1f}")
    R["dev_rehearsal_order_rule"] = dict(acc_mean=float(acc.mean()), acc_sd=float(acc.std()), n_mean=float(ns.mean()))
    # same rehearsal on references (75/25 of types) for calibration
    R["ref_order_rule"] = {}
    for nm in ("chinese_clan", "chinese_given", "sanskrit", "ur3"):
        P = ref_pairs(nm); out = []
        for rep in range(20):
            idx = rng.choice(len(P), N, replace=False); sub = [P[k] for k in idx]
            cut = len(sub) * 3 // 4
            k, n, _ = order_rule_accuracy(Counter(sub[:cut]), Counter(sub[cut:]))
            if n: out.append(k / n)
        R["ref_order_rule"][nm] = float(np.mean(out))
        print(f"  ref {nm:16s} order-rule accuracy {np.mean(out):.3f}")
    for kind in ("emblem_x_name", "compound", "blazon"):
        out = []
        for rep in range(20):
            sub = sim_pairs(kind, N, rng); rng.shuffle(sub); cut = len(sub) * 3 // 4
            k, n, _ = order_rule_accuracy(Counter(sub[:cut]), Counter(sub[cut:]))
            if n: out.append(k / n)
        R["ref_order_rule"]["sim_" + kind] = float(np.mean(out))
        print(f"  sim {kind:16s} order-rule accuracy {np.mean(out):.3f}")
    json.dump(R, open(HERE / "f1_dev.json", "w"), indent=1, default=float)

else:  # heldout: registered tests (docs/prereg/pair_numeral_long.md)
    import cs_data
    dev = indus_pair_types("dev"); ho = indus_pair_types("heldout")
    R["n_dev_types"] = len(dev); R["n_ho_types"] = len(ho)

    def pol_excess(E, nn=50):
        p = polarization(E); pn = np.mean([polarization(orient_null(E, rng)) for _ in range(nn)])
        return (p - pn) / (1 - pn), p, pn
    # T1 (primary): POL excess on held-out 2-sign-core pair types, bootstrap CI over types
    occ = cs_data.indus_occurrences("heldout")
    two = sorted({(o["core"][0], o["core"][1]) for o in occ if len(o["core"]) == 2 and o["core"][0] != o["core"][1]})
    ex, p, pn = pol_excess(two, 1000)
    bs = []
    for _ in range(1000):
        sub = list({two[k] for k in rng.integers(0, len(two), len(two))})
        bs.append(pol_excess(sub, 30)[0])
    ci = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
    nulls = np.array([polarization(orient_null(two, rng)) for _ in range(2000)])
    R["T1_two_sign_cores"] = dict(n_types=len(two), pol=p, pol_null=pn, excess=ex, ci=ci,
                                  p_vs_orient_null=float((np.sum(nulls >= p) + 1) / 2001),
                                  both=both_share(two))
    print(f"T1 held-out 2-sign cores: n={len(two)} POL {p:.3f} null {pn:.3f} excess {ex:+.3f} 95% CI [{ci[0]:+.3f},{ci[1]:+.3f}]"
          f" p={R['T1_two_sign_cores']['p_vs_orient_null']:.3g} both-position share {both_share(two):.2f}")
    # T2: undirected two-inventory (max-cut excess) on all held-out pair types
    R["T2_all_types"] = graph_stats(list(ho), rng, nnull=500); show("T2 held-out, all types", R["T2_all_types"])
    # T3: order-rule transfer
    k, n, det = order_rule_accuracy(dev, ho)
    bt = binomtest(k, n, 0.5, alternative="greater")
    ci = binomtest(k, n).proportion_ci(0.95, method="wilson")
    R["T3_order_rule"] = dict(correct=k, n=n, acc=k / n if n else None, p_vs_half=bt.pvalue, ci=[ci.low, ci.high], details=det)
    print(f"T3 order rule dev->held-out unseen pair types: {k}/{n} = {k / n:.3f}, 95% CI [{ci.low:.3f},{ci.high:.3f}], p(>0.5)={bt.pvalue:.2g}")
    # descriptive: pooled dev+held-out
    pooled = list(set(dev) | set(ho))
    R["pooled_all"] = graph_stats(pooled, rng, nnull=300); show("pooled dev+held-out", R["pooled_all"])
    json.dump(R, open(HERE / "f1_heldout.json", "w"), indent=1, default=float)
