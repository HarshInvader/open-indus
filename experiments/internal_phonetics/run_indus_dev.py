"""All four tests on Indus DEV (distinct M77 texts, dev_heldout(version=2)).
Held-out is NOT touched here. Writes results.json[indus_dev] and a log."""
import sys
from collections import Counter, defaultdict

import numpy as np
from scipy.stats import poisson

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from common import Bigram, bh, glyph_sim, load_split, one_two_pairs, save_results
from tests import t1_complements, t1_local, t2_transitivity, t3_ligatures, t4_drops, t3_events

FISH = {"M%d" % i for i in range(59, 76)}


def excluded(x, pos):
    return x in ("M176", "M1") or (x in FISH and pos == 0)


FAM = {  # sign-internal modifier pairs (base, modified); from novel_methods/exp3 (their visual reading)
    "enclosure_fish_ticks": [("M59", "M60"), ("M65", "M66"), ("M67", "M68"), ("M70", "M71"), ("M72", "M73")],
    "enclosure_other": [("M1", "M2"), ("M8", "M9"), ("M25", "M26"), ("M110", "M111"), ("M141", "M143"),
                        ("M141", "M144"), ("M155", "M156"), ("M162", "M164"), ("M178", "M179"),
                        ("M206", "M207"), ("M219", "M220"), ("M249", "M250"), ("M280", "M281"),
                        ("M287", "M289"), ("M307", "M308"), ("M387", "M388"), ("M389", "M390"),
                        ("M391", "M392"), ("M403", "M404")],
    "roof": [("M59", "M65"), ("M60", "M66"), ("M89", "M92"), ("M137", "M138"), ("M162", "M163")],
    "inner_strokes": [("M342", "M343"), ("M342", "M344"), ("M342", "M345"), ("M328", "M329"), ("M328", "M330")],
    "fish_marks": [("M59", "M67"), ("M59", "M70"), ("M59", "M72"), ("M59", "M74")],
    "ears": [("M328", "M342")],
}


def transparency(texts, x, h, orient):
    """Next-sign distribution after 'h x' vs after h when x absent (orient prev);
    mirror for next. Overlap = sum min(p1, p0). 1 = x is transparent (optional)."""
    a, b = Counter(), Counter(); nh = nhx = 0
    for t in texts:
        tt = ("^",) + t + ("$",)
        if orient == "next":
            tt = tt[::-1]
        for i in range(1, len(tt) - 1):
            if tt[i] != h:
                continue
            nh += 1
            if tt[i + 1] == x:
                nhx += 1
                if i + 2 < len(tt):
                    a[tt[i + 2]] += 1
            else:
                b[tt[i + 1]] += 1
    if not a or not b:
        return None, nhx, nh
    A, B = sum(a.values()), sum(b.values())
    return float(sum(min(a[k] / A, b[k] / B) for k in set(a) | set(b))), nhx, nh


def main():
    D, H = load_split()
    print("dev distinct clean texts:", len(D))
    out = {}
    # ---------------- T1
    t1 = {}
    for name, fn in [("local_wide", lambda o: t1_local(D, excluded, o, nperm=20000, wide=1, minev=4)),
                     ("edit1", lambda o: t1_complements(D, excluded, o, nperm=20000, minev=4))]:
        items = []; nev = {}
        for o in ("prev", "next"):
            r = fn(o); nev[o] = r["n_events"]
            for it in r["items"]:
                it["orient"] = o; items.append(it)
        q = bh([i["p"] for i in items])
        for it, qq in zip(items, q):
            it["q"] = float(qq)
            if qq < 0.05:
                tr, nhx, nh = transparency(D, it["sign"], it["top_hosts"][0][0], it["orient"])
                it["transparency"] = tr; it["host_with_x"] = nhx; it["host_total"] = nh
        sig = sorted([i for i in items if i["q"] < 0.05], key=lambda i: i["p"])
        t1[name] = {"n_events": nev, "n_tested": len(items), "n_sig_tests": len(sig),
                    "n_sig_signs": len({i["sign"] for i in sig}), "sig": sig}
        print("T1", name, "events", nev, "tested", len(items), "sig signs", len({i["sign"] for i in sig}))
        for i in sig:
            print("   ", i["orient"], i["sign"], "n=%d p=%.4g q=%.3g" % (i["n"], i["p"], i["q"]), i["top_hosts"],
                  "transp=%s host %s/%s" % (i.get("transparency"), i.get("host_with_x"), i.get("host_total")))
    # transparency baseline: random (x,h) adjacent pairs with >=5 joint occurrences
    big = Counter((t[i], t[i + 1]) for t in D for i in range(len(t) - 1))
    base = [transparency(D, x, h, "prev")[0] for (h, x), c in big.items() if c >= 5]
    base = [b for b in base if b is not None]
    t1["transparency_baseline"] = {"median": float(np.median(base)), "q90": float(np.quantile(base, 0.9)), "n": len(base)}
    print("   transparency baseline (adjacent pairs n>=5): median %.2f q90 %.2f" % (np.median(base), np.quantile(base, 0.9)))
    out["t1"] = t1

    # ---------------- T2
    r = t2_transitivity(D, nnull=1000)
    sig = {k: v for k, v in r["pairs"].items() if v["q"] < 0.05}
    tok = Counter(s for t in D for s in t)
    freq = [s for s, c in tok.items() if c >= 5]
    sims = [glyph_sim(a, b) for i, a in enumerate(freq) for b in freq[i + 1:]]
    thr = float(np.quantile(sims, 0.95))
    for k, v in sig.items():
        a, b = k.split("|"); v["glyph_sim"] = glyph_sim(a, b); v["similar"] = v["glyph_sim"] >= thr
    # components
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            x = parent[x]
        return x
    for k in sig:
        a, b = k.split("|"); parent[find(a)] = find(b)
    comps = defaultdict(set)
    for k in sig:
        for s in k.split("|"):
            comps[find(s)].add(s)
    comps = sorted([sorted(c, key=lambda s: int(s[1:])) for c in comps.values()], key=len, reverse=True)
    cases = {}
    for grp in (["M59", "M65", "M67", "M70", "M72"], ["M267", "M391", "M293"]):
        for i, a in enumerate(grp):
            for b in grp[i + 1:]:
                k = "%s|%s" % tuple(sorted([a, b]))
                cases[k] = {"k": r["all_k"].get(k, 0), **r["pairs"].get(k, {}), "glyph_sim": glyph_sim(a, b)}
    out["t2"] = {"n_frames": r["n_frames"], "n_pairs": r["n_pairs"], "n_multi_obs": r["n_multi_obs"],
                 "n_multi_null": [r["n_multi_null_mean"], r["n_multi_null_sd"]], "p_global": r["p_global"],
                 "n_tested": len(r["pairs"]), "sig": sig, "components": comps, "glyph_thr95": thr, "cases": cases}
    print("T2 frames %d pairs %d multi-frame pairs %d vs null %.1f+-%.1f p=%.4f tested %d sig %d (glyph thr %.2f)" % (
        r["n_frames"], r["n_pairs"], r["n_multi_obs"], r["n_multi_null_mean"], r["n_multi_null_sd"], r["p_global"],
        len(r["pairs"]), len(sig), thr))
    for k, v in sorted(sig.items(), key=lambda kv: kv[1]["p"]):
        print("   ", k, v)
    print("   components:", comps)
    for k, v in cases.items():
        print("   case", k, v)

    # ---------------- T3
    r3 = t3_ligatures(D)
    for it in r3["items"]:
        it["sim_AB"] = glyph_sim(it["A"], it["B"]); it["sim_AC"] = glyph_sim(it["A"], it["C"])
    sig3 = [i for i in r3["items"] if i["q"] < 0.05]
    # bigram-null calibration: number of q<0.05 triples in Indus-fitted bigram corpora
    rng = np.random.default_rng(1); Bg = Bigram(D)
    null_sig = [sum(1 for i in t3_ligatures(Bg.sample(len(D), rng))["items"] if i["q"] < 0.05) for _ in range(10)]
    ev = t3_events(D)
    cand = {}
    for A in ["M343", "M344", "M345", "M348", "M190", "M404"]:
        cand[A] = Counter("%s %s" % e[1] for e in ev if e[0] == A).most_common(8)
    comp_check = {}
    for A, parts in {"M343": [("M342", "M97"), ("M342", "M98"), ("M97", "M342"), ("M98", "M342")],
                     "M344": [("M342", "M99"), ("M99", "M342"), ("M342", "M87"), ("M87", "M342")],
                     "M345": [("M342", "M102"), ("M102", "M342"), ("M342", "M89"), ("M89", "M342")],
                     "M348": [("M347", "M176"), ("M176", "M347"), ("M347", "M342"), ("M342", "M176")],
                     "M190": [("M162", "M186"), ("M186", "M162"), ("M162", "M185")]}.items():
        comp_check[A] = {"%s %s" % bc: sum(1 for e in ev if e[0] == A and e[1] == bc) for bc in parts}
        comp_check[A]["bigram_in_corpus"] = {"%s %s" % bc: sum(1 for t in D for i in range(len(t) - 1) if t[i:i + 2] == bc)
                                             for bc in parts}
    m103 = Counter(e[0] for e in ev if e[1] == ("M103", "M403")).most_common(10)
    out["t3"] = {"n_events": r3["n_events"], "n_tested": r3["n_triples_tested"], "sig": sig3,
                 "top20": r3["items"][:20], "bigram_null_nsig": null_sig, "candidate_events": cand,
                 "composition_check": comp_check, "M103_M403_replaced_by": m103}
    print("T3 events %d triples tested (>=2 indep families) %d sig %d; bigram-null nsig %s" % (
        r3["n_events"], r3["n_triples_tested"], len(sig3), null_sig))
    for i in r3["items"][:20]:
        print("   ", i)
    print("   candidates:", cand)
    print("   composition:", comp_check)
    print("   M103 M403 <-> single sign:", m103)

    # ---------------- T4
    t4 = {}
    for cls, pairs in FAM.items():
        rr = t4_drops(D, pairs)
        o = sum(x["obs"] for x in rr); e = sum(x["exp"] for x in rr); nm = sum(x["n_mod_subs"] for x in rr)
        t4[cls] = {"pairs": rr, "obs": o, "exp": e, "n_mod_subs": nm,
                   "p_more": float(poisson.sf(o - 1, e)) if e > 0 else None,
                   "p_never": float(poisson.pmf(0, e)) if o == 0 else None}
        print("T4 %-22s obs %d exp %.2f mod-subs %d p_more %s p_never %s" % (cls, o, e, nm, t4[cls]["p_more"], t4[cls]["p_never"]))
        for x in rr:
            if x["obs"] or x["n_mod_subs"]:
                print("     ", x)
    out["t4"] = t4
    save_results("indus_dev", out)


if __name__ == "__main__":
    main()
