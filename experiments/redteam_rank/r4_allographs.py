"""Step 4: does graphic variant (allograph) choice track seal size? And power on metric sites.
Allograph pairs from sources/shaunmortal_indus/STATE.md (line ~249, distributional + image similarity)."""
import sys, json
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import numpy as np
from data import build
from stats import strata_test

T = build()
OUT = {}
PAIRS = [("W705", "W706"), ("W220", "W231"), ("W220", "W233"), ("W220", "W240"), ("W741", "W742"), ("W741", "W745"),
         ("W803", "W806"), ("W151", "W156"), ("W384", "W388"), ("W904", "W923"), ("W031", "W032"), ("W405", "W407")]


def eff(sign_set, mask=None, nperm=3000):
    m = np.ones(len(T), bool) if mask is None else mask
    Ts = [t for t, k in zip(T, m) if k]
    x = np.array([any(s in sign_set for s in t["signs"]) for t in Ts]).astype(int)
    return strata_test(Ts, x, "base", "la", nperm)


print("allograph pair: effect of each member (base control, all data)")
rows = []
for a, b in PAIRS:
    ra, rb = eff({a}), eff({b})
    # direct contrast among texts carrying exactly one of the two
    only_a = np.array([(a in t["signs"]) and (b not in t["signs"]) for t in T])
    only_b = np.array([(b in t["signs"]) and (a not in t["signs"]) for t in T])
    m = only_a | only_b
    Ts = [t for t, k in zip(T, m) if k]
    rc = strata_test(Ts, only_b[m].astype(int), "base", "la", 3000) if m.sum() > 5 else {}
    rows.append(dict(a=a, b=b, a_res=ra, b_res=rb, b_vs_a=rc))
    fmt = lambda r: f"{r['eff']:+.0%}(n{r['n']},z{r['z']:+.1f})" if r.get("n") else "-"
    print(f"  {a} {fmt(ra):>18s} | {b} {fmt(rb):>18s} | {b} vs {a} within-pair: {fmt(rc)}")
OUT["allographs"] = rows

print("\nW590 with / without W390 (M249-M161 block)")
for lab, f in [("W590+W390 adjacent", lambda t: any(x == "W590" and y == "W390" for x, y in zip(t["signs"], t["signs"][1:]))),
               ("W590 not before W390", lambda t: "W590" in t["signs"] and not any(x == "W590" and y == "W390" for x, y in zip(t["signs"], t["signs"][1:]))),
               ("W390 without W590", lambda t: "W390" in t["signs"] and "W590" not in t["signs"])]:
    x = np.array([f(t) for t in T]).astype(int)
    r = strata_test(T, x, "base", "la", 3000)
    OUT[lab] = r
    print(f"  {lab}: n={r['n']} {r['eff']:+.0%} z={r['z']:+.2f}")

print("\nmetric sites only: estimate, 95% CI by within-strata permutation SD, and MDE")
site = np.array([t["site"] for t in T])
metric = ~np.isin(site, ["Mohenjo-daro", "Harappa", "Chanhu-daro"])
for lab, ss in [("W590", {"W590"}), ("W706", {"W706"}), ("W70x", {"W704", "W705", "W706"})]:
    r = eff(ss, metric, 4000)
    if not r.get("n"):
        print(" ", lab, "no carriers"); continue
    lo = np.log1p(r["eff"]); se = abs(lo / r["z"]) if r["z"] else np.nan
    ci = (np.expm1(lo - 1.96 * se), np.expm1(lo + 1.96 * se))
    mde = np.expm1(2.8 * se)
    OUT["metric_" + lab] = dict(r, ci=ci, mde=mde)
    print(f"  {lab}: n={r['n']} {r['eff']:+.0%} 95%CI {ci[0]:+.0%}..{ci[1]:+.0%}  MDE(80%) ~{mde:.0%}")
for e in ["none", "zebu"]:
    Ts = [t for t, k in zip(T, metric) if k]
    x = np.array([t["emb"] == e for t in Ts]).astype(int)
    r = strata_test(Ts, x, "base", "la", 4000)
    if r.get("n"):
        lo = np.log1p(r["eff"]); se = abs(lo / r["z"])
        OUT["metric_" + e] = dict(r, ci=(np.expm1(lo - 1.96 * se), np.expm1(lo + 1.96 * se)))
        print(f"  {e}: n={r['n']} {r['eff']:+.0%} 95%CI {np.expm1(lo - 1.96 * se):+.0%}..{np.expm1(lo + 1.96 * se):+.0%}")
json.dump(OUT, open("experiments/redteam_rank/r4.json", "w"), indent=1, default=float)
