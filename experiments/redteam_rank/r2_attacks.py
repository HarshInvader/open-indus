"""Step 2: attacks 1-4 and 6 on all data and on the own family held-out."""
import sys, json, collections as C
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import numpy as np
from data import build, families, split, FEATS, w_width
from stats import strata_test, ols_test, add_quantiles, nbin

NP = 3000
T = build(); add_quantiles(T)
fam = families(T); ho = split(T, fam, seed=7)
ALL = np.ones(len(T), bool)
OUT = {}
SIGNS = ["W590", "W70x"]
EMBS = ["none", "zebu"]


def run(label, mask, kind="base", y="la", feats=SIGNS + EMBS, quiet=False):
    Ts = [t for t, m in zip(T, mask) if m]
    add_quantiles(Ts)
    res = {}
    for f in feats:
        x = np.array([t[f] if f in FEATS else t["emb"] == f for t in Ts]).astype(int)
        r = strata_test(Ts, x, kind, y, NP)
        if r.get("n", 0) == 0:
            res[f] = r; continue
        r["p"] = min(r["p_lo"], r["p_hi"]) * 2
        res[f] = r
    OUT[label] = dict(n_texts=len(Ts), res=res)
    if not quiet:
        s = "  ".join(f"{f}:{r['eff']:+.0%}(n{r['n']},p{r['p']:.3f})" if r.get("n") else f"{f}:-" for f, r in res.items())
        print(f"{label:38s} N={len(Ts):4d} {s}")
    return res


print("== 0. baseline (site x nsign x lines)")
run("base/all", ALL); run("base/heldout_own", ho)

print("\n== 1. glyph-width controls")
print("glyph width px: M249(W590)=%.0f M336(W70x)=%.0f; median of bridged = %.0f" % (
    w_width("W590"), w_width("W704"), np.median([x for x in [w_width("W%03d" % i) for i in range(1, 960)] if x])))
for k in ["glyph", "glyph+n", "linew"]:
    run(f"{k}/all", ALL, k); run(f"{k}/heldout_own", ho, k)
fe = [lambda t: t["site"], lambda t: min(t["lines"], 2)]
for label, cov in [("ols n", [lambda t: t["nsign"]]),
                   ("ols glyph_total+lines", [lambda t: t["glyph_total"]]),
                   ("ols n+glyph+linew", [lambda t: t["nsign"], lambda t: t["glyph_total"], lambda t: t["linew_max"]]),
                   ("ols n+glyph+linew+emb", None)]:
    res = {}
    for f in SIGNS + EMBS:
        x = np.array([t[f] if f in FEATS else t["emb"] == f for t in T]).astype(int)
        if cov is None:
            fe2 = fe + [lambda t: t["emb"]] if f in FEATS else fe
            cv = [lambda t: t["nsign"], lambda t: t["glyph_total"], lambda t: t["linew_max"]]
        else:
            fe2, cv = fe, cov
        r = ols_test(T, x, cv, fe2, nperm=1500)
        r["p"] = 2 * min(r["p_lo"], r["p_hi"]); res[f] = r
    OUT["A1_" + label] = res
    print(f"{label:38s} " + "  ".join(f"{f}:{r['eff']:+.0%}(p{r['p']:.3f})" for f, r in res.items()))

print("\n-- width vs height outcomes (base strata)")
for y in ["lw", "lh"]:
    run(f"outcome {y}/all", ALL, "base", y)

print("\n== 2. shape / completeness / type")
asp = np.array([abs(np.log(t["aspect"])) for t in T])
print("aspect |log|>0.1 share:", (asp > 0.1).mean().round(3))
run("near-square (|log asp|<0.1)", asp < 0.1)
comp = np.array([t["complete"] and "#" not in t["seq"] for t in T])
run("complete texts only", comp)
run("complete, near-square", comp & (asp < 0.1))
run("steatite only", np.array([t["material"] == "Steatite" for t in T]))
for typ in [("SEAL:R",), ("SEAL",), ("TAG", "TAG:L", "TAG:P", "TAG:B")]:
    Tt = build(types=typ); add_quantiles(Tt)
    res = {}
    for f in SIGNS + EMBS:
        x = np.array([t[f] if f in FEATS else t["emb"] == f for t in Tt]).astype(int)
        r = strata_test(Tt, x, "base", "la", NP)
        if r.get("n"):
            r["p"] = 2 * min(r["p_lo"], r["p_hi"])
        res[f] = r
    OUT["A2_type_" + typ[0]] = dict(n=len(Tt), res=res)
    print(f"type {typ[0]:8s} N={len(Tt)} " + "  ".join(f"{f}:{r['eff']:+.0%}(n{r['n']},p{r['p']:.3f})" if r.get("n") else f"{f}:-" for f, r in res.items()))

print("\n== 3. measurement source / site / period")
site = np.array([t["site"] for t in T]); inch = np.array([t["inch"] for t in T])
print("inch-grid share by site:", {s: round(float(inch[site == s].mean()), 2) for s in ["Mohenjo-daro", "Harappa", "Chanhu-daro", "Dholavira", "Lothal", "Kalibangan"]})
run("Mohenjo-daro only", site == "Mohenjo-daro")
run("Harappa only", site == "Harappa")
metric = ~np.isin(site, ["Mohenjo-daro", "Harappa", "Chanhu-daro"])
run("metric sites (not MD/H/Chanhu)", metric)
run("inch-grid measurements only", inch)
run("not inch-grid", ~inch)
run("not inch-grid, MD+Harappa", ~inch & np.isin(site, ["Mohenjo-daro", "Harappa"]))
run("base+phase strata", ALL, "base+phase")
per = np.array([t["period"] for t in T])
for p_ in ["Early", "Intermediate", "Late"]:
    run(f"MD period {p_}", (site == "Mohenjo-daro") & (per == p_))
run("MD period unknown", (site == "Mohenjo-daro") & (per == "-"))
run("Harappa phase known", (site == "Harappa") & (per != "-"))
run("Harappa phase unknown", (site == "Harappa") & (per == "-"))

print("\n== 4. duplicates / independence")
mult = np.array([t["n_obj"] for t in T])
for f in SIGNS:
    x = np.array([t[f] for t in T]).astype(bool)
    print(f"{f}: texts {x.sum()}, share multi-object {np.mean(mult[x] > 1):.2f} (all {np.mean(mult > 1):.2f}), mean nsign {np.mean([t['nsign'] for t in np.array(T)[x]]):.2f}")
run("base+mult strata", ALL, "base+mult")
run("base+emb strata", ALL, "base+emb", feats=SIGNS)
run("base+emb+mult strata", ALL, "base+emb+mult", feats=SIGNS)
run("single-object texts only", mult == 1)
# W590 block: with/without W161
t590 = [t for t in T if t["W590"]]
print("W590 next-sign counts:", C.Counter(t["signs"][t["signs"].index("W590") + 1] if t["signs"].index("W590") + 1 < len(t["signs"]) else "END" for t in t590).most_common(6))
print("W70x next-sign:", C.Counter(next((t["signs"][i + 1] if i + 1 < len(t["signs"]) else "END") for i, s in enumerate(t["signs"]) if s in FEATS["W70x"]) for t in T if t["W70x"]).most_common(6))
for t in T:
    t["W590_161"] = int(any(a == "W590" and b == "W161" for a, b in zip(t["signs"], t["signs"][1:])))
    t["W590_no161"] = int(t["W590"] and not t["W590_161"])
FEATS["W590_161"] = None; FEATS["W590_no161"] = None
run("W590 split by block", ALL, feats=["W590_161", "W590_no161"])
# jackknife over families: drop each family carrying the sign, record min |z|
for f in SIGNS + EMBS:
    x = np.array([t[f] if f in ("W590", "W70x") else t["emb"] == f for t in T]).astype(int)
    fams = sorted(set(g for g, xi in zip(fam, x) if xi))
    zs = []
    for g in fams:
        keep = np.array([gg != g for gg in fam])
        Ts = [t for t, k in zip(T, keep) if k]
        r = strata_test(Ts, x[keep], "base", "la", 400)
        zs.append(r["z"])
    OUT["A4_jackknife_" + f] = dict(n_fam=len(fams), z_min_abs=float(min(np.abs(zs))), z_max_abs=float(max(np.abs(zs))))
    print(f"jackknife over {len(fams)} families carrying {f}: |z| range {min(np.abs(zs)):.2f}-{max(np.abs(zs)):.2f}")

print("\n== 6. emblems: where and what")
for e in ["zebu", "none", "unicorn"]:
    X = [t for t in T if t["emb"] == e]
    print(e, len(X), "sites", C.Counter(t["site"] for t in X).most_common(4), "period", C.Counter(t["period"] for t in X).most_common(4),
          "incomplete %.2f" % np.mean([not t["complete"] for t in X]), "inch %.2f" % np.mean([t["inch"] for t in X]),
          "nsign %.2f" % np.mean([t["nsign"] for t in X]), "material", C.Counter(t["material"] for t in X).most_common(3))
emb = np.array([t["emb"] for t in T])
run("emblems, MD only", site == "Mohenjo-daro", feats=EMBS)
run("emblems, Harappa only", site == "Harappa", feats=EMBS)
run("emblems, metric sites", metric, feats=EMBS)
run("emblems, complete texts", comp, feats=EMBS)
run("emblems, base+phase", ALL, "base+phase", feats=EMBS)
run("emblems, glyph strata", ALL, "glyph", feats=EMBS)
run("emblems, outcome log width", ALL, "base", "lw", feats=EMBS)
run("emblems, outcome log height", ALL, "base", "lh", feats=EMBS)
for p_ in ["Early", "Intermediate", "Late"]:
    run(f"emblems MD {p_}", (site == "Mohenjo-daro") & (per == p_), feats=EMBS)
# rank-based zebu: share of zebu residuals above median within stratum
zb = [t for t in T if t["emb"] == "zebu"]
la = np.array([t["la"] for t in zb]); print("zebu area mm2 quantiles:", np.round(np.exp(np.quantile(la, [0, .25, .5, .75, 1]))))
uni = np.array([t["la"] for t in T if t["emb"] == "unicorn"]); print("unicorn quantiles:", np.round(np.exp(np.quantile(uni, [0, .25, .5, .75, 1]))))
# drop top-5 largest zebu
order = np.argsort(-la)
big = set(zb[i]["key"] for i in order[:5])
run("zebu minus 5 largest", np.array([t["key"] not in big for t in T]), feats=["zebu"])
json.dump(OUT, open("experiments/redteam_rank/r2.json", "w"), indent=1, default=float)
