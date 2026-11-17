"""Red team claim A (fixed number-names) and B (counted items).
Independent reimplementation. Usage: .venv/bin/python experiments/redteam_pnl/a_numbernames.py
"""
import numpy as np
from collections import Counter, defaultdict
from scipy.stats import fisher_exact, binomtest
from rt_common import *  # noqa

rng = np.random.default_rng(7)
DEV, HO = dev_heldout(version=2)
NPERM = 4000


def classify(dev_tok, min_n=8, spike=0.6, q_thr=0.05):
    """Dev head classes. key=(sys, head). lexeme: share>=0.6 and perm q<0.05; count: >=3 values, max<0.6, ns."""
    by = defaultdict(list)
    for t in dev_tok:
        by[(t["sys"], t["head"])].append(t["value"])
    pool = {s: np.array([t["value"] for t in dev_tok if t["sys"] == s]) for s in ("short", "tall")}
    res = {}
    keys = [k for k, v in by.items() if len(v) >= min_n]
    ps = []
    for k in keys:
        v = by[k]; c = Counter(v); val, m = c.most_common(1)[0]
        share = m / len(v)
        P = pool[k[0]]
        null = np.empty(NPERM)
        for b in range(NPERM):
            smp = rng.choice(P, len(v), replace=False)
            null[b] = Counter(smp.tolist()).most_common(1)[0][1] / len(v)
        p = (1 + (null >= share - 1e-12).sum()) / (NPERM + 1)
        res[k] = dict(n=len(v), mode=val, share=share, nvals=len(c), p=p, dist=dict(c))
        ps.append(p)
    # BH
    order = np.argsort(ps); m = len(ps); q = np.empty(m); prev = 1.0
    for rank, i in reversed(list(enumerate(order, 1))):
        prev = min(prev, ps[i] * m / rank); q[i] = prev
    for k, qq in zip(keys, q):
        r = res[k]; r["q"] = float(qq)
        if r["share"] >= spike and qq < q_thr:
            r["cls"] = "lexeme"
        elif r["nvals"] >= 3 and r["share"] < spike and qq >= q_thr:
            r["cls"] = "count"
        elif qq < q_thr:
            r["cls"] = "formula"
        else:
            r["cls"] = "other"
    return res


def heldout_test(cls, ho_tok, which="lexeme", pool_tok=None):
    """Share of held-out tokens of class heads at the dev mode; expectation from pooled numerals of that system;
    permutation p (shuffle held-out values within system)."""
    pool_tok = pool_tok if pool_tok is not None else ho_tok
    pool = {s: Counter(t["value"] for t in pool_tok if t["sys"] == s) for s in ("short", "tall")}
    pp = {s: {v: c / sum(pool[s].values()) for v, c in pool[s].items()} for s in pool}
    idx = [i for i, t in enumerate(ho_tok) if cls.get((t["sys"], t["head"]), {}).get("cls") == which]
    if not idx:
        return dict(n=0)
    kept = sum(ho_tok[i]["value"] == cls[(ho_tok[i]["sys"], ho_tok[i]["head"])]["mode"] for i in idx)
    exp = sum(pp[ho_tok[i]["sys"]].get(cls[(ho_tok[i]["sys"], ho_tok[i]["head"])]["mode"], 0) for i in idx)
    # permutation within system
    vals = np.array([t["value"] for t in ho_tok]); sysv = np.array([t["sys"] for t in ho_tok])
    modes = np.array([cls[(ho_tok[i]["sys"], ho_tok[i]["head"])]["mode"] for i in idx])
    cnt = 0
    for b in range(NPERM):
        v2 = vals.copy()
        for s in ("short", "tall"):
            m = sysv == s; v2[m] = rng.permutation(v2[m])
        if (v2[idx] == modes).sum() >= kept: cnt += 1
    per = Counter()
    tot = Counter()
    for i in idx:
        k = (ho_tok[i]["sys"], ho_tok[i]["head"]); tot[k] += 1
        per[k] += ho_tok[i]["value"] == cls[k]["mode"]
    return dict(n=len(idx), kept=int(kept), share=kept / len(idx), expected_share=exp / len(idx),
                p_perm=(cnt + 1) / (NPERM + 1),
                per_head={f"{k[0]} {k[1]} (dev mode {cls[k]['mode']})": f"{per[k]}/{tot[k]}" for k in tot},
                idx=idx)


def family_level(ho, ho_tok, res, cls):
    """Collapse held-out tokens into families: (a) identical local window prev-num-head-next;
    (b) text families joined by a shared 3-gram; (c) shared 4-gram. Majority 'kept' per family."""
    out = {}
    idx = res["idx"]
    def win(i):
        t = ho_tok[i]; return t["head"], t["numsign"]
    # local window = text-local context
    wins = {}
    for i in idx:
        t = ho_tok[i]
        seq = [s for s in ho[t["text_idx"]]["seq"]]
        wins.setdefault(" ".join(seq), []).append(i)
    for k in (3, 4):
        fam = families(ho, k)
        g = defaultdict(list)
        for i in idx:
            g[fam[ho_tok[i]["text_idx"]]].append(i)
        kept_f = 0; w_kept = 0.0
        sizes = []
        for f, ii in g.items():
            ks = [ho_tok[i]["value"] == cls[(ho_tok[i]["sys"], ho_tok[i]["head"])]["mode"] for i in ii]
            kept_f += np.mean(ks) > 0.5; w_kept += np.mean(ks); sizes.append(len(ii))
        out[f"shared_{k}gram"] = dict(n_families=len(g), majority_kept=int(kept_f), weighted_kept=round(w_kept, 2),
                                      largest_family_tokens=max(sizes), family_sizes=sorted(sizes, reverse=True)[:8])
    return out


def leave_one_head_out(cls, ho_tok, res):
    out = {}
    idx = res["idx"]
    heads = Counter((ho_tok[i]["sys"], ho_tok[i]["head"]) for i in idx)
    for h in heads:
        ii = [i for i in idx if (ho_tok[i]["sys"], ho_tok[i]["head"]) != h]
        kept = sum(ho_tok[i]["value"] == cls[(ho_tok[i]["sys"], ho_tok[i]["head"])]["mode"] for i in ii)
        out[f"{h[0]} {h[1]}"] = f"{kept}/{len(ii)}"
    return out


def generic_collocation_baseline(dev, ho, min_n=8, spike=0.6):
    """Does ANY sign keep its dev-modal predecessor (non-numeral, any sign) on held-out as often?
    For heads with >= min_n dev predecessor tokens whose modal predecessor share >= spike (same rule as lexeme)."""
    s0, t0 = numeral_tables()
    def pred(texts):
        d = defaultdict(list)
        for t in texts:
            for r in runs(t["seq"]):
                for a, b in zip(r, r[1:]):
                    if a in s0 or a in t0 or b in s0 or b in t0: continue
                    d[b].append(a)
        return d
    D, H = pred(dev), pred(ho)
    kept = n = 0; heads = 0
    for b, v in D.items():
        if len(v) < min_n: continue
        a, m = Counter(v).most_common(1)[0]
        if m / len(v) < spike: continue
        heads += 1
        n += len(H.get(b, [])); kept += sum(x == a for x in H.get(b, []))
    return dict(heads=heads, n=n, kept=kept, share=kept / max(1, n))


def run_variant(name, dev, ho, short, tall, direction="before", cluster=False, verbose=True):
    dtok = numeral_tokens(dev, short, tall, direction, cluster)
    htok = numeral_tokens(ho, short, tall, direction, cluster)
    cls = classify(dtok)
    lex = {f"{k[0]} {k[1]}": (v["mode"], f"{v['share']:.2f}", v["n"]) for k, v in cls.items() if v["cls"] == "lexeme"}
    cnt = {f"{k[0]} {k[1]}": (v["mode"], f"{v['share']:.2f}", v["n"]) for k, v in cls.items() if v["cls"] == "count"}
    A = heldout_test(cls, htok, "lexeme")
    A_devpool = heldout_test(cls, htok, "lexeme", pool_tok=dtok)
    B = heldout_test(cls, htok, "count")
    out = dict(variant=name, n_dev_tokens=len(dtok), n_ho_tokens=len(htok), lexeme_heads=lex, count_heads=cnt,
               A={k: v for k, v in A.items() if k != "idx"},
               A_expected_from_dev_pool=A_devpool.get("expected_share"),
               B={k: v for k, v in B.items() if k != "idx"})
    if A.get("n") and B.get("n"):
        tab = [[A["kept"], A["n"] - A["kept"]], [B["kept"], B["n"] - B["kept"]]]
        out["A_vs_B_fisher_p"] = float(fisher_exact(tab, alternative="greater")[1])
    if verbose:
        print(f"\n=== {name} ===  dev tokens {len(dtok)}, held-out tokens {len(htok)}")
        print(" lexeme:", lex); print(" count:", cnt)
        print(" A:", {k: v for k, v in out["A"].items()}, " exp(dev pool)", out["A_expected_from_dev_pool"])
        print(" B:", out["B"], " fisher", out.get("A_vs_B_fisher_p"))
    return out, cls, dtok, htok, A, B


def minimal_pairs(texts, short, tall, heads):
    """Distinct texts identical except for the numeral sign directly before a given head:
    direct evidence that a value is substitutable (counting), per head."""
    res = {}
    for h in heads:
        frames = defaultdict(set)
        for t in texts:
            seq = t["seq"]
            for i in range(len(seq) - 1):
                if seq[i + 1] == h[1] and (seq[i] in (short if h[0] == "short" else tall)):
                    frame = tuple(seq[:i]) + ("_",) + tuple(seq[i + 1:])
                    frames[frame].add((short if h[0] == "short" else tall)[seq[i]])
        multi = [f for f, v in frames.items() if len(v) >= 2]
        res[f"{h[0]} {h[1]}"] = dict(frames=len(frames), frames_with_2plus_values=len(multi),
                                     examples=[" ".join(f) + " : " + str(sorted(frames[f])) for f in multi[:3]])
    return res


def icit_replication(cls):
    """Apply DEV classes (M numbering) to ICIT via the bridge. Numerals identified on the Wells side
    (independent stroke classification), heads bridged W->M. Sets: all ICIT distinct texts (= same objects,
    independent transcription) and ICIT texts from sites outside the five big M77 sites."""
    ws, wt = icit_numeral_tables()
    w2m = W2M()
    big = {"Harappa", "Mohenjo-daro", "Lothal", "Kalibangan", "Chanhu-daro"}
    out = {}
    allt = distinct(icit_texts())
    for name, texts in (("icit_all", allt), ("icit_new_sites", [t for t in allt if t["site"] not in big])):
        tok = numeral_tokens(texts, ws, wt, "before")
        for t in tok:
            t["head"] = w2m.get(t["head"], "OOV:" + t["head"])
        # lexeme heads whose dev mode is writable in ICIT (short 2 cannot be: W2 excluded)
        res = heldout_test(cls, tok, "lexeme")
        resB = heldout_test(cls, tok, "count")
        o = dict(n_texts=len(texts), n_tokens=len(tok), A={k: v for k, v in res.items() if k != "idx"},
                 B={k: v for k, v in resB.items() if k != "idx"})
        if res.get("n"):
            fam = family_level(texts, tok, res, cls)
            o["A_families"] = fam
        out[name] = o
        print(f"\n--- {name}: texts {len(texts)}, numeral tokens {len(tok)}")
        print(" A:", o["A"]); print(" B:", o["B"]); print(" fam:", o.get("A_families"))
    # stroke system agreement on the same objects: M59 after tall vs short in ICIT
    tok = numeral_tokens(allt, ws, wt, "before")
    agree = Counter()
    for t in tok:
        h = w2m.get(t["head"])
        if h in ("M59", "M211", "M328", "M162", "M169", "M194", "M197", "M403", "M190"):
            agree[(h, t["sys"], t["value"])] += 1
    out["icit_head_value_counts"] = {f"{k[0]} {k[1]} {k[2]}": v for k, v in sorted(agree.items()) if v >= 2}
    return out


def main():
    results = {}
    s0, t0 = numeral_tables("base")
    base, cls, dtok, htok, A, B = run_variant("base (numeral before head)", DEV, HO, s0, t0)
    results["base"] = base
    results["base"]["A_families"] = family_level(HO, htok, A, cls)
    results["base"]["A_leave_one_head_out"] = leave_one_head_out(cls, htok, A)
    results["base"]["B_families"] = family_level(HO, htok, B, cls) if B.get("n") else None
    results["base"]["B_leave_one_head_out"] = leave_one_head_out(cls, htok, B) if B.get("n") else None
    print(" A families:", results["base"]["A_families"])
    print(" A leave-one-head-out:", results["base"]["A_leave_one_head_out"])
    print(" B families:", results["base"]["B_families"])
    print(" B leave-one-head-out:", results["base"]["B_leave_one_head_out"])

    # held-out B per-token detail
    Bdet = [(htok[i]["head"], htok[i]["sys"], htok[i]["value"], " ".join(HO[htok[i]["text_idx"]]["seq"])) for i in B["idx"]]
    Adet = [(htok[i]["head"], htok[i]["sys"], htok[i]["value"], " ".join(HO[htok[i]["text_idx"]]["seq"])) for i in A["idx"]]
    results["base"]["B_tokens"] = Bdet; results["base"]["A_tokens"] = Adet

    # count-head exact tests: binomial on B alone vs its expectation; B n per head
    if B.get("n"):
        results["base"]["B_binom_vs_expected"] = float(binomtest(B["kept"], B["n"], B["expected_share"]).pvalue)

    # generic collocation baseline (are numeral+head pairs special, or do all lexicalised pairs repeat?)
    results["generic_collocation_baseline"] = generic_collocation_baseline(DEV, HO)
    print("\n generic collocation baseline:", results["generic_collocation_baseline"])

    # segmentation variants
    for v in ("with_2s", "strict_tall", "pure"):
        s, t = numeral_tables(v)
        results[v] = run_variant(v, DEV, HO, s, t)[0]
    results["cluster_sum"] = run_variant("cluster sum", DEV, HO, s0, t0, cluster=True)[0]
    results["after"] = run_variant("numeral AFTER sign", DEV, HO, s0, t0, direction="after")[0]
    # mould/copies: held-out restricted to seals only (no tablets/copper)
    seals = [t for t in HO if t["object_type"] == "seal"]
    dseals = [t for t in DEV if t["object_type"] == "seal"]
    results["seals_only_heldout"] = run_variant("held-out seals only (dev classes from all dev)", DEV, seals, s0, t0)[0]
    # minimal pairs (all distinct M77 texts)
    allm = distinct(m77_texts())
    heads = [k for k, v in cls.items() if v["cls"] in ("lexeme", "count")]
    results["minimal_pairs_all_m77"] = minimal_pairs(allm, s0, t0, heads)
    print("\n minimal pairs:"); [print("  ", k, v["frames"], v["frames_with_2plus_values"]) for k, v in results["minimal_pairs_all_m77"].items()]
    # ICIT
    results["icit"] = icit_replication(cls)
    dump(results, "a_results.json")


if __name__ == "__main__":
    main()
