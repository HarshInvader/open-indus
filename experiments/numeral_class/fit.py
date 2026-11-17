"""Fit Indus short-stroke numeral value distributions against reference quantity classes.

usage: .venv/bin/python experiments/numeral_class/fit.py
Frozen rules: docs/prereg/numeral_class.md. Inputs: data/refs.json (refs.py), corpus loaders.
Writes fit.json and prints the decision table.
"""
import json, sys, math
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np
from scipy.special import gammaln, logsumexp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from corpus.load import m77_texts, icit_texts  # noqa

STROKES = json.load(open(ROOT / "sources/shaunmortal_indus/data/stroke_signs.json"))
M_SHORT = {f"M{k}": v for k, v in STROKES["short"].items() if k not in ("99", "100", "101")}
W_SHORT = {"W001": 1, "W003": 3, "W004": 4, "W005": 5, "W006": 6, "W007": 7, "W013": 3, "W014": 4,
           "W015": 5, "W016": 6, "W017": 7, "W018": 8, "W019": 9, "W055": 12}
S_M77 = [1, 3, 4, 5, 6, 7, 8, 9, 10, 12]
S_ICIT = [1, 3, 4, 5, 6, 7, 8, 9, 12]
FORMULA_HEADS = {"M194": 7, "M197": 7, "M190": 3, "M403": 3, "M15": 3, "M25": 1}
rng = np.random.default_rng(20261115)


# ------------------------------------------------------------------ Indus counts
def sig(seq):
    return [s for s in seq if s not in ("|", "#")]


def m77_units(mode="tokens"):
    """list of (site, otype_stratum, [values]) over distinct (site, object_type, seq)."""
    seen, out = set(), []
    for t in m77_texts():
        k = (t["site"], t["object_type"], " ".join(t["seq"]))
        if k in seen: continue
        seen.add(k)
        ot = t["object_type"]
        strat = "SEAL" if ot == "seal" else ("TABLET" if ot == "miniature tablet" or (ot == "sealing" and t["site"] == "Harappa") else ot)
        s = sig(t["seq"])
        vals = []
        for i, x in enumerate(s):
            if x in M_SHORT:
                nxt = s[i + 1] if i + 1 < len(s) else None
                if mode == "noformula" and FORMULA_HEADS.get(nxt) == M_SHORT[x]: continue
                vals.append((M_SHORT[x], x, nxt))
        if mode == "first" and vals: vals = vals[:1]
        out.append((t["site"], strat, vals))
    if mode == "types":                 # distinct (numeral sign, next sign) types
        ty = {}
        for site, strat, vals in out:
            for v, x, n in vals: ty.setdefault((x, n), (site, strat, v))
        out = [(s, st, [(v, None, None)]) for (s, st, v) in ty.values()]
    return out


def icit_units():
    seen, out = set(), []
    for t in icit_texts():
        ty = t["type"].split(":")[0]
        k = (t["site"], ty, " ".join(t["seq"]))
        if k in seen: continue
        seen.add(k)
        strat = {"SEAL": "SEAL", "TAB": "TABLET"}.get(ty, ty)
        out.append((t["site"], strat, [(W_SHORT[x], x, None) for x in sig(t["seq"]) if x in W_SHORT]))
    return out


def counts(units, support, site=None, strat=None):
    c = Counter()
    for s, st, vals in units:
        if site and s != site: continue
        if strat and st != strat: continue
        for v, *_ in vals:
            if v in support: c[v] += 1
    return np.array([c.get(v, 0) for v in support], float)


# ------------------------------------------------------------------ reference predictives
def ref_alpha(rc, support, ceiling):
    r = {int(k): v for k, v in rc.items()}
    if ceiling:
        r = dict(r); r[12] = sum(n for v, n in r.items() if v >= 12)
    return np.array([r.get(v, 0) for v in support], float) + 0.5


def ll_dm(o, alpha):
    A, N = alpha.sum(), o.sum()
    return float(gammaln(A) - gammaln(A + N) + np.sum(gammaln(alpha + o) - gammaln(alpha)))


def ll_fixed(o, p):
    p = p / p.sum()
    return float(np.sum(o * np.log(p)))


def model_ps(name, support, ceiling):
    """returns list of probability vectors over support (parameter grid, equal prior weight)."""
    S = np.array(support, float)
    if name == "B_month":
        return [np.ones(len(S))]
    if name == "H1_benford":
        return [np.log10(1 + 1 / S)]
    grid = []
    if name == "H2_zipf":
        for a in np.linspace(0, 3, 2001):
            p = S ** -a
            if ceiling:
                k = np.arange(12, 5000, dtype=float); p = p.copy(); p[-1] = np.sum(k ** -a) if a > 1.0001 else np.nan
            grid.append(p)
    if name == "H3_geometric":
        for q in np.linspace(0.0005, 0.9995, 2001):
            p = q ** S
            if ceiling: p = p.copy(); p[-1] = q ** 12 / (1 - q)
            grid.append(p)
    return grid


def ll_model(o, name, support, ceiling):
    ps = [p for p in model_ps(name, support, ceiling) if np.all(np.isfinite(p))]
    lls = [ll_fixed(o, p) for p in ps]
    return float(logsumexp(lls) - np.log(len(lls))), ps[int(np.argmax(lls))]


MODEL_CLASS = {"B_month": "B", "H1_benford": "H", "H2_zipf": "H", "H3_geometric": "H"}
CEIL_OK = {"H2_zipf", "H3_geometric"}
EXACT_ONLY_REFS = ("E", "G", "I")    # closed-ended classes: exact only


def components(refs, support):
    """-> list of (class, name, variant, kind, payload)"""
    comp = []
    for k, d in refs.items():
        variants = ["exact"] if d["cls"] in EXACT_ONLY_REFS else ["exact", "ceiling"]
        for var in variants:
            comp.append((d["cls"], k, var, "ref", ref_alpha(d["counts"], support, var == "ceiling")))
    for m, c in MODEL_CLASS.items():
        for var in (["exact", "ceiling"] if m in CEIL_OK else ["exact"]):
            comp.append((c, m, var, "model", None))
    return comp


def score(o, comp, support):
    rows = []
    for cls, name, var, kind, alpha in comp:
        if kind == "ref":
            ll = ll_dm(o, alpha); best = alpha / alpha.sum()
        else:
            ll, best = ll_model(o, name, support, var == "ceiling")
            best = best / best.sum()
        rows.append(dict(cls=cls, name=name, var=var, ll=ll, p=best.tolist()))
    byc = defaultdict(list)
    for r in rows: byc[r["cls"]].append(r["ll"])
    cls_ll = {c: float(logsumexp(v) - np.log(len(v))) for c, v in byc.items()}
    return rows, cls_ll


def summarize(cls_ll):
    order = sorted(cls_ll, key=lambda c: -cls_ll[c])
    top, second = order[0], order[1]
    return dict(order=order, top=top, log10_bf_top_vs_second=(cls_ll[top] - cls_ll[second]) / math.log(10),
                log10_ml={c: cls_ll[c] / math.log(10) for c in order})


def ppc(o, row, comp_alpha, n_sim=10000):
    """G statistic; for refs draw p ~ Dirichlet(alpha) then multinomial; models use best-fit p."""
    N = int(o.sum())
    def G(x, e):
        m = x > 0
        return 2 * np.sum(x[m] * np.log(x[m] / e[m]))
    if comp_alpha is not None:
        e = comp_alpha / comp_alpha.sum() * N
        P = rng.dirichlet(comp_alpha, size=n_sim)
    else:
        p = np.array(row["p"]); e = p * N
        P = np.tile(p, (n_sim, 1))
    sims = np.array([rng.multinomial(N, pp) for pp in P])
    g_obs = G(o, e)
    g_sim = np.array([G(s, e) for s in sims])
    return dict(G_obs=float(g_obs), p=float(np.mean(g_sim >= g_obs)), N=N)


def main():
    refs = json.load(open(HERE / "data/refs.json"))
    out = {}
    U = m77_units()
    compM = components(refs, S_M77)
    strata = {"M77_pooled": counts(U, S_M77)}
    site_n = Counter()
    for s, st, vals in U:
        site_n[s] += sum(1 for v, *_ in vals if v in S_M77)
    sites = [s for s, n in site_n.items() if n >= 15 and s not in ("Other sites", "West Asian finds")]
    for s in sites: strata[f"site:{s}"] = counts(U, S_M77, site=s)
    for st in ("SEAL", "TABLET"): strata[f"type:{st}"] = counts(U, S_M77, strat=st)
    for mode in ("first", "types", "noformula"):
        strata[f"sens:{mode}"] = counts(m77_units(mode), S_M77)
    I = icit_units()
    compI = components(refs, S_ICIT)
    istr = {"ICIT_pooled": counts(I, S_ICIT), "ICIT_type:SEAL": counts(I, S_ICIT, strat="SEAL"),
            "ICIT_type:TABLET": counts(I, S_ICIT, strat="TABLET")}
    isite = Counter()
    for s, st, vals in I: isite[s] += len(vals)
    for s, n in isite.items():
        if n >= 40: istr[f"ICIT_site:{s}"] = counts(I, S_ICIT, site=s)

    for name, o in list(strata.items()) + list(istr.items()):
        sup = S_ICIT if name.startswith("ICIT") else S_M77
        comp = compI if name.startswith("ICIT") else compM
        rows, cls_ll = score(o, comp, sup)
        sm = summarize(cls_ll)
        best_rows = sorted(rows, key=lambda r: -r["ll"])[:3]
        out[name] = dict(n=int(o.sum()), counts=dict(zip(map(str, sup), map(int, o))), **sm,
                         best_components=[dict(name=r["name"], var=r["var"], log10_ml=r["ll"] / math.log(10)) for r in best_rows],
                         components={f"{r['name']}|{r['var']}": r["ll"] / math.log(10) for r in rows})
        print(f"\n== {name}  n={int(o.sum())}  counts={dict(zip(sup, map(int, o)))}")
        print("   class log10 ML: " + "  ".join(f"{c}:{sm['log10_ml'][c]:.1f}" for c in sm["order"]))
        print(f"   top {sm['top']} vs {sm['order'][1]}: log10 BF = {sm['log10_bf_top_vs_second']:.2f}; best comps: " +
              ", ".join(f"{r['name']}|{r['var']} {r['ll']/math.log(10):.1f}" for r in best_rows))

    # ---------------- decision rule
    pooled = out["M77_pooled"]; W = pooled["top"]
    c1 = pooled["log10_bf_top_vs_second"] > 1
    def stratum_ok(key):
        s = out[key]; n = s["n"]
        if n >= 40:
            return s["top"] == W and s["log10_bf_top_vs_second"] > 1
        if n >= 15:
            return max(v for c, v in s["log10_ml"].items() if c != W) - s["log10_ml"][W] <= 1
        return True
    site_keys = [k for k in out if k.startswith("site:")]
    type_keys = ["type:SEAL", "type:TABLET"]
    c2 = {k: stratum_ok(k) for k in site_keys}
    c3 = {k: stratum_ok(k) for k in type_keys}
    c4 = out["ICIT_pooled"]["top"] == W and out["ICIT_pooled"]["log10_bf_top_vs_second"] > 1
    win = c1 and all(c2.values()) and all(c3.values()) and c4
    # PPC for pooled top class's best component, and for best component overall per class
    o = strata["M77_pooled"]
    rows, _ = score(o, compM, S_M77)
    ppcs = {}
    for cls in sorted(set(r["cls"] for r in rows)):
        r = max((r for r in rows if r["cls"] == cls), key=lambda r: r["ll"])
        alpha = next((c[4] for c in compM if c[1] == r["name"] and c[2] == r["var"]), None)
        pp = ppc(o, r, alpha)
        p = np.array(r["p"]); N = o.sum()
        pp.update(component=f"{r['name']}|{r['var']}",
                  exp_share7=float(p[S_M77.index(7)]), exp_share12=float(p[S_M77.index(12)]),
                  obs_share7=float(o[S_M77.index(7)] / N), obs_share12=float(o[S_M77.index(12)] / N),
                  exp_counts=[round(float(x * N), 1) for x in p])
        ppcs[cls] = pp
        print(f"PPC class {cls} ({pp['component']}): G={pp['G_obs']:.1f} p={pp['p']:.4f}; share7 obs {pp['obs_share7']:.3f} exp {pp['exp_share7']:.3f}; share12 obs {pp['obs_share12']:.3f} exp {pp['exp_share12']:.3f}")
    adequate = ppcs[W]["p"] >= 0.05
    verdict = ("WIN+ADEQUATE" if win and adequate else "WIN+INADEQUATE" if win else "NO WIN")
    dec = dict(top_pooled=W, c1_pooled_bf_gt10=c1, log10_bf_pooled=pooled["log10_bf_top_vs_second"],
               c2_sites=c2, c3_types=c3, c4_icit=c4, icit_top=out["ICIT_pooled"]["top"],
               win=win, ppc_winner=ppcs[W], adequate=adequate, verdict=verdict)
    print("\nDECISION:", json.dumps(dec, indent=1, default=str))
    json.dump(dict(strata=out, ppc=ppcs, decision=dec), open(HERE / "fit.json", "w"), indent=1, default=float)


if __name__ == "__main__":
    main()
