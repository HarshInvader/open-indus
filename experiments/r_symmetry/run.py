"""r_symmetry: do the R rows survive the 12 sign lists and the other edition? Prereg docs/prereg/r_symmetry.md (sealed).

Run from the repo root (nice, isolated):
    nice -n 20 .venv/bin/python -I experiments/r_symmetry/run.py shape                   # invariance pass -> shape.json
    nice -n 20 .venv/bin/python -I experiments/r_symmetry/run.py power --reproduce-only  # native statistics vs published
    nice -n 20 .venv/bin/python -I experiments/r_symmetry/run.py power                   # kill test -> power.json
    nice -n 20 .venv/bin/python -I experiments/r_symmetry/run.py test                    # needs power.json committed

Sub-tests (a row may hold several):
    Q1, Q2, Q3   m328_measure/l2_quantity                 MC-MUK23-cup-vessel-fee
    T1, T3       tablet_archives/t_tests (copied)          T3: licence-pairing and tablets-tokens; T1: tablets-tokens
    EMB          context/q1_animal + animal_tie_power      MC-MUK23-emblem-organisation
    SJ           signmap/strokedjar_test (copied)          MC-MUK19-stroked-jar-MET
    RND          round_own_order/run.py (copied)           MC-LAU10-other-language

Implementation choices not spelled out in the sealed text (flagged for review before the code is sealed):
  U1. Units are native. Mould-copy identities (Q1/Q2), find-spot units (Q3), copy groups (T1/T3), distinct seal texts
      (EMB), distinct texts (SJ) and the round/home text sets (RND) are built on the native labels; a list only relabels
      the signs inside them. Otherwise a lump would merge different texts into fake "copies". This is what makes
      "T1 uses no obverse signs, so only the tier-lumping lists apply" true.
  U2. "Identical inputs" (INVARIANT) is judged up to a one-to-one renaming of labels (the statistics do not read label
      names), on the per-unit features each statistic reads.
  U3. Rows with several sub-tests: a cell is testable if any of its sub-tests is; the kill condition is met in a cell
      only if it is met in every testable sub-test; the survive bar is met if any testable sub-test meets it.
  U4. A split/image family's survive bar is met only by a strict majority of its testable members (ties: not met).
  U5. The M77 list is not a named family; it is reported per cell and not counted (maps.FAMILY["M77"] = None).
  U6. M77 tablets (T1/T3 other edition): Harappa objects whose side is exactly {tall 2/3/4, M328}; tier 3 = any of the
      five tall-three signs; other sides joined in side order = obverse; obverse complete = every obverse side has
      complete = true and no '#'; stratum = object type (M77 has no period); deposit = locus. This gives 234 objects,
      not the prereg's 242 (242 = all sites and all tall values incl. M86/M96; Harappa alone gives 241).
  U7. Q2 other edition (M77): objects of all sites with one N before M328 (fr.TALL), identity = full object text,
      stratum = object type, copies = objects per identity.
  U8. SJ other-edition count gate: distinct M77 texts holding any of M343-M345 >= 30 (the signmap/count_gate rule).
      SJ power is the sealed Poisson 2x formula on the null mean, computed exactly (sum over sites of
      n_pottery * n_SJ / n), so no observed count is read before test mode.
"""
import sys, json, csv, subprocess, importlib.util, collections, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for p in ("", "experiments/context", "experiments/functional_reading", "experiments/self_label",
          "experiments/m328_measure", "experiments/typology"):
    sys.path.insert(0, str(ROOT / p))
sys.path.insert(0, str(HERE))

import maps as MP                       # noqa: E402
from maps import TIER_M, CUP_M, SJ_M, TALL_M, OTHER, LISTS  # noqa: E402
import l2_quantity as L2                # noqa: E402  (icit_units, identities, m77_units, strat_perm_spearman, perm_chi2, power_spearman, power_lot)
import s2_test as S2                    # noqa: E402  experiments/self_label/s2_test.py (icit_set, m77_set, perm_test)
import q1_animal as Q                   # noqa: E402  (build, featurize)
import common as CM                     # noqa: E402  experiments/context/common.py
import q2_gulf                          # noqa: E402  (FOREIGN_ALL, as in round_own_order/run.py)
import fr                               # noqa: E402  functional_reading/fr.py (TALL)
from corpus.load import icit_texts, m77_texts, m77_lines, distinct  # noqa: E402
import copied_t_tests as TT             # noqa: E402
import copied_round as RO               # noqa: E402
import copied_strokedjar as SJT         # noqa: E402

assert "protocuneiform" not in S2.__file__ and S2.__file__.endswith("self_label/s2_test.py"), S2.__file__


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


ATP = _load("animal_tie_power_run", ROOT / "experiments/animal_tie_power/run.py")   # auc_bin, plant, drawA, nullA, pval

# ------------------------------------------------------------------ constants
NWORK = 4                       # at most 4 worker processes
POWER_BAR = 0.8
# Draw counts: the original preregs' own counts, unchanged.
#   Q1/Q2 power_spearman(rho=0.3, sims=300, nperm=400); Q3 power_lot(plant=0.3, sims=200, nperm=400)   (l2_quantity defaults)
#   T1/T3 NPLANT=200 plants x NPERM_PLANT=1000                                                         (t_tests.py line 14)
#   EMB  NNULL_A=1000 nulls, NDRAW=40 plants at delta 0.20 (non-unicorn target)                         (animal_tie_power)
#   RND  NSETS=200 home sets, NSH=200 shuffles, ND=1000                                                 (round_own_order)
#   SJ   Poisson 2x at the 0.99 quantile (analytic)                                                    (strokedjar_test)
EMB_DELTA = 0.20
Q3_OTHER_NPERM = 5000           # the existing Q3_secondary_icit_phase used nperm=5000

ROWS = collections.OrderedDict([
    ("MC-MUK23-cup-vessel-fee", ["Q1", "Q2", "Q3"]),
    ("MC-MUK23-licence-pairing", ["T3"]),
    ("MC-KM-tablets-tokens", ["T1", "T3"]),
    ("MC-MUK23-emblem-organisation", ["EMB"]),
    ("MC-MUK19-stroked-jar-MET", ["SJ"]),
    ("MC-LAU10-other-language", ["RND"]),
])
OUT_OF_SCOPE = collections.OrderedDict([
    ("FUN-kriger-hunt", "out of scope: kh_tests.planted() covers K4 only, so K1 and K3 have no plant and no cell can be gated"),
    ("KEY-pierson", "out of scope: its key is defined per Mahadevan sign, so no other list applies, and its R rests on "
                    "its own failed power gate, not on a list-dependent statistic"),
])
SUBS = ["Q1", "Q2", "Q3", "T1", "T3", "EMB", "SJ", "RND"]
NATIVE = dict(Q1="ICIT", Q2="ICIT", Q3="M77", T1="ICIT", T3="ICIT", EMB="M77", SJ="ICIT", RND="ICIT")
OTHER_NOT_RUN = dict(Q1="not run: M77 has no sizes", RND="not run: only 7 of 32 round texts link to M77")
NT_BY_CONSTRUCTION = {("SJ", v): "merges M343-M345 with the plain jar M342 (NT by construction)"
                      for v in ("lump_jar_man", "lump_all", "img_hi", "img_mid", "img_lo")}

# published native values (reproduce-first). Source files in parentheses.
PUBLISHED = dict(
    Q1=("rho", -0.1680865545396352, "m328_measure/l2_results.json Q1 (RESULTS.md: -0.17, n 275)"),
    Q2=("rho", 0.07573257373149819, "m328_measure/l2_results.json Q2 (RESULTS.md: +0.08, n 300)"),
    Q3=("chi2", 28.207299806428097, "m328_measure/l2_results.json Q3 (RESULTS.md: chi2 28.2, n 215)"),
    T1=("G", 42.76895914121987, "tablet_archives/results.json T1 (RESULTS.md: p 0.83, 153 units, 22 deposits)"),
    T3=("S", 100.99545622748444, "tablet_archives/results.json T3 (prereg: S = 101.0)"),
    EMB=("auc", 0.5156110592385101, "animal_tie_power/full.json real_indus.auc_bin (RESULTS.md: AUC 0.516, p 0.31)"),
    SJ=("ratio", 0.739, "signmap/strokedjar_result.json SJ ratio (prereg: 0.74; 17 vs 23.0)"),
    RND=("excess", -0.09548841085517358, "round_own_order/real.json round_loo.excess (prereg: -0.10)"),
)
TOL = dict(Q1=1e-9, Q2=1e-9, Q3=1e-6, T1=1e-6, T3=1e-6, EMB=1e-9, SJ=5e-4, RND=1e-9)

# kill / survive (each row's own thresholds, prereg table)
ALPHA_Q = 0.0125


def verdict_of(sub, r):
    """-> (kill_met, survive_met) for one testable sub-test result r."""
    if sub in ("Q1", "Q3"):
        return r["p"] > ALPHA_Q, r["p"] <= ALPHA_Q            # Q1 is one-sided 'greater'; Q3 chi2 has no direction
    if sub == "Q2":
        return r["p"] > ALPHA_Q, (r["p"] <= ALPHA_Q and r["rho"] > 0)
    if sub in ("T1", "T3"):
        return r["p"] >= 0.01, r["p"] < 0.01                  # one-sided 'greater' permutation p
    if sub == "EMB":
        return r["p"] >= 0.05, r["p"] < 0.05                  # one-sided AUC permutation p
    if sub == "SJ":
        return r["ratio"] <= 1, (r["ratio"] >= 2 and r["p_enrich"] <= 0.01)
    if sub == "RND":
        return (not r["found"]), r["found"]
    raise KeyError(sub)


# ------------------------------------------------------------------ mapping helpers
def variant(cell):
    return None if cell in (None, OTHER) else MP.Variant(cell)


def fw_of(V):
    """W sign -> label (first M partner, then tok); identity for native."""
    return (lambda w: w) if V is None else (lambda w: MP.w_to_label(V, w))


def ftok_of(V):
    return (lambda m: m) if V is None else (lambda m: MP.m_to_label(V, m))


def NT(reason):
    return dict(NT=reason)


TALLCUP_CATS = {"tall1": {"M86"}, "tall2": {"M87"}, "tall3": TIER_M[3], "tall4": {"M95"}, "tall5": {"M96"}, "cup": CUP_M}
TIER_CATS = {"tier2": TIER_M[2], "tier3": TIER_M[3], "tier4": TIER_M[4], "cup": CUP_M}
EMB_CATS = {"short": set(CM.M_SHORT), "tall": set(CM.M_TALL), "jar": {CM.JAR_M}}
SJ_CATS = {"stroked jar": SJ_M}


def colkey(X):
    return tuple(sorted(tuple(np.round(c, 9).tolist()) for c in np.asarray(X).T))


# ------------------------------------------------------------------ Q1 / Q2 / Q3 (l2_quantity)
def nb_set(seq, cupL, tallL):
    """l2_quantity.n_before with the cup and tall signs as label sets (the cup can have several allographs)."""
    return [tallL[seq[i - 1]] for i, x in enumerate(seq) if x in cupL and i > 0 and seq[i - 1] in tallL]


def icit_units_mapped(V):
    """l2_quantity.icit_units with N read off the mapped labels; the object list and sides stay native (U1)."""
    if V is None:
        return L2.icit_units()
    fw = fw_of(V)
    cupL = {fw("W700")} | V.labels_of(["M328"])
    tallL = {}
    for w, v in L2.W_TALL.items():
        for lab in (V.labels_of([MP.W2M_ALL[w][0]]) if w in MP.W2M_ALL else {w}):
            tallL[lab] = v
    objs = collections.defaultdict(list)
    for t in icit_texts():
        objs[t["id"].split(".")[0]].append(t)
    out = []
    for oid, recs in objs.items():
        recs.sort(key=lambda r: r["id"])
        vals = set()
        for r in recs:
            vals |= set(nb_set([fw(x) for x in r["seq"]], cupL, tallL))
        if not vals or len(vals) > 1:
            continue
        ws = [L2.f(r["width_mm"]) for r in recs]; hs = [L2.f(r["height_mm"]) for r in recs]
        typ = recs[0]["type"]
        strat = "TAB:B" if typ == "TAB:B" else "TAB:I" if typ == "TAB:I" else "other"
        out.append(dict(oid=oid, N=vals.pop(), sides=tuple(" ".join(r["seq"]) for r in recs), w=max(ws), h=max(hs),
                        strat=strat, site=recs[0]["site"], lot=(recs[0]["period"], recs[0]["phase"])))
    return out


def q12_inputs(sub, cell):
    if cell == OTHER:
        if sub == "Q1":
            return NT(OTHER_NOT_RUN["Q1"])
        ids = L2.identities(m77_q2_objects())
        return dict(N=[u["N"] for u in ids], y=[u["copies"] for u in ids], strata=[u["strat"] for u in ids],
                    alt="two", n=len(ids))
    V = variant(cell)
    if V is not None:
        bad = MP.set_check(V, TALLCUP_CATS)
        if bad:
            return NT(bad)
    ids = L2.identities(icit_units_mapped(V))
    if sub == "Q1":
        U = [u for u in ids if u["length"] > 0]
        d = dict(N=[u["N"] for u in U], y=[u["length"] for u in U], strata=[u["strat"] for u in U], alt="greater")
    else:
        d = dict(N=[u["N"] for u in ids], y=[u["copies"] for u in ids], strata=[u["strat"] for u in ids], alt="two")
    d["n"] = len(d["N"])
    d["key"] = tuple(sorted(zip(d["N"], d["y"], d["strata"])))
    return d


def m77_q2_objects():
    """U7: M77 objects (all sites) with one tall-stroke N before M328; identity = full object text; stratum = type."""
    objs = collections.defaultdict(list)
    for l in m77_lines():
        objs[l["text_no"]].append(l)
    out = []
    for tn, ls in objs.items():
        vals = set()
        for l in ls:
            for seg in l["segments"]:
                vals |= set(L2.n_before(seg, "M328", fr.TALL))
        if len(vals) != 1:
            continue
        full = " | ".join(" ".join(l["signs"]) for l in sorted(ls, key=lambda l: (l["side"], l["line"])))
        out.append(dict(oid=tn, N=vals.pop(), sides=(full,), w=0.0, h=0.0, strat=ls[0]["object_type"], site=ls[0]["site"]))
    return out


def m77_units_mapped(V):
    """l2_quantity.m77_units (heldout_only=False) with N read off mapped labels; unit text stays native (U1)."""
    if V is None:
        return sorted(L2.m77_units())
    tok = ftok_of(V)
    cupL = V.labels_of(["M328"])
    tallL = MP.labels_value(V, fr.TALL)
    objs = collections.defaultdict(list)
    for l in m77_lines():
        if l["site"] == "Harappa":
            objs[l["text_no"]].append(l)
    units = set()
    for tn, ls in objs.items():
        vals = set()
        for l in ls:
            for seg in l["segments"]:
                vals |= set(nb_set([tok(s) for s in seg], cupL, tallL))
        if len(vals) != 1:
            continue
        loc = ls[0]["locus"]
        if loc in ("", "-", None):
            continue
        full = " | ".join(" ".join(l["signs"]) for l in sorted(ls, key=lambda l: (l["side"], l["line"])))
        units.add((loc, full, vals.pop(), ls[0]["object_type"]))
    units = list(units)
    c = collections.Counter(u[0] for u in units)
    return sorted(u for u in units if c[u[0]] >= 5)


def icit_phase_lots():
    """l2_quantity.main 'secondary: ICIT lot = period/phase (Harappa)' block, verbatim logic."""
    objs = L2.icit_units()
    lotu = set()
    for o in objs:
        if o["site"] == "Harappa" and o["lot"] != ("-", "-"):
            lotu.add(("/".join(o["lot"]), o["sides"], o["N"], o["strat"]))
    lotu = list(lotu); c = collections.Counter(u[0] for u in lotu)
    return sorted(u for u in lotu if c[u[0]] >= 5)


def q3_inputs(cell):
    if cell == OTHER:
        units = icit_phase_lots()
        return dict(units=units, n=len(units), nperm=Q3_OTHER_NPERM)
    V = variant(cell)
    if V is not None:
        bad = MP.set_check(V, TALLCUP_CATS)
        if bad:
            return NT(bad)
    units = m77_units_mapped(V)
    return dict(units=units, n=len(units), nperm=L2.NPERM, key=tuple(sorted((u[0], u[2], u[3]) for u in units)))


# ------------------------------------------------------------------ T1 / T3 (tablet_archives, copied)
def icit_tablet_rows():
    rows = [r for r in csv.DictReader(open(ROOT / "experiments/tablet_archives/tablets.csv")) if r["tier"] in ("2", "3", "4")]
    for r in rows:
        r["tier"] = int(r["tier"])
    return rows


def m77_tablet_rows():
    """U6."""
    tier_of = {m: t for t, ms in TIER_M.items() for m in ms}
    locus = {}
    for l in m77_lines():
        locus.setdefault(l["text_no"], l["locus"])
    by = collections.defaultdict(list)
    for t in m77_texts():
        if t["site"] == "Harappa":
            by[t["text_no"]].append(t)
    rows = []
    for tn, sides in by.items():
        sides.sort(key=lambda t: t["side"])
        tiers, obv, comp = set(), [], True
        for t in sides:
            s = t["seq"]
            if len(s) == 2 and "M328" in s and any(x in tier_of for x in s):
                tiers.add(tier_of[[x for x in s if x in tier_of][0]])
            else:
                obv.append(" ".join(s)); comp = comp and bool(t["complete"])
        if len(tiers) != 1 or not obv:
            continue
        tier = tiers.pop(); obv_text = " / ".join(obv)
        complete = comp and "#" not in obv_text
        typ = sides[0]["object_type"]
        loc = locus.get(tn, "")
        rows.append(dict(oid=tn, type=typ, tier=tier, obverse=obv_text, obv_complete="1" if complete else "0",
                         period_key="", deposit="" if loc in ("", "-", None) else str(loc),
                         copy_group=f"{typ}|{obv_text}|{tier}" if complete else f"single|{tn}"))
    return rows


def t_arrays(rows, sign_fn):
    """t_tests.py lines 26-35, 37-47, 114-116, 126-129, 134, 168 with obverse signs passed through sign_fn."""
    groups = collections.OrderedDict()
    for r in rows:
        groups.setdefault(r["copy_group"], []).append(r)
    G = []
    for k, mem in groups.items():
        f = mem[0]
        G.append(dict(key=k, type=f["type"], tier=f["tier"], mult=len(mem), complete=f["obv_complete"] == "1",
                      stratum=f"{f['type']}|{f['period_key']}",
                      signs=sorted(set(sign_fn(x) for x in f["obverse"].replace("/", " ").split() if x != "#"))))
    GC = [g for g in G if g["complete"]]
    seen, U1 = set(), []
    for r in rows:
        if not r["deposit"]:
            continue
        k = (r["copy_group"], r["deposit"])
        if k in seen:
            continue
        seen.add(k)
        U1.append(dict(dep=r["deposit"], tier=r["tier"], stratum=f"{r['type']}|{r['period_key']}"))
    dep_count = collections.Counter(u["dep"] for u in U1)
    U1k = [u for u in U1 if dep_count[u["dep"]] >= 3]
    dep1 = TT.codes([u["dep"] for u in U1k]); tier1 = np.array([u["tier"] for u in U1k]); str1 = [u["stratum"] for u in U1k]
    sign_n = collections.Counter(s for g in GC for s in g["signs"])
    feat = [s for s, n in sign_n.items() if n >= 5]
    X3 = np.array([[s in g["signs"] for s in feat] for g in GC], float)
    tier3 = np.array([g["tier"] for g in GC]); str3 = [g["stratum"] for g in GC]
    marg = np.bincount(tier3 - 2, minlength=3) / len(tier3)
    top15 = [feat.index(s) for s, _ in sorted(((s, sign_n[s]) for s in feat), key=lambda x: -x[1])[:15]]
    return dict(dep1=dep1, tier1=tier1, str1=str1, X3=X3, tier3=tier3, str3=str3, marg=marg, top15=top15,
                n_T1_units=len(U1k), n_T1_deposits=int(dep1.max() + 1) if len(dep1) else 0,
                n_groups_complete=len(GC), n_features=len(feat))


def t_inputs(sub, cell):
    if cell == OTHER:
        d = t_arrays(m77_tablet_rows(), lambda x: x)
    else:
        V = variant(cell)
        if V is not None:
            bad = MP.set_check(V, TIER_CATS)
            if bad:
                return NT(bad)
        d = t_arrays(icit_tablet_rows(), fw_of(V))
    if sub == "T1":
        d["key"] = (tuple(d["dep1"].tolist()), tuple(d["tier1"].tolist()), tuple(d["str1"]))
        d["n"] = d["n_T1_units"]
    else:
        d["key"] = (tuple(d["tier3"].tolist()), tuple(d["str3"]), colkey(d["X3"]))
        d["n"] = d["n_groups_complete"]
    return d


def tt_setup(d):
    TT.setup(rng=np.random.default_rng(20261114), tier1=d["tier1"], dep1=d["dep1"], marg=d["marg"],
             tier3=d["tier3"], X3=d["X3"], top15=d["top15"])


# ------------------------------------------------------------------ EMB (q1_animal + animal_tie_power)
def emb_inputs(cell):
    if cell == OTHER:
        I = [t for t in icit_texts() if t["type"] in ("SEAL:S", "SEAL")]
        items, _ = Q.build(I, CM.icit_animal, "symbol", CM.W_SHORT, CM.W_TALL, CM.JAR_W)
        c = collections.Counter(a for _, a, _ in items); keep = {a for a, n in c.items() if n >= 10}
        items = [it for it in items if it[1] in keep]
        short, tall, jar = CM.W_SHORT, CM.W_TALL, CM.JAR_W
    else:
        items, _ = ATP.indus_items()          # q1_animal.build on native M77 seal texts (U1: native units)
        V = variant(cell)
        short, tall, jar = CM.M_SHORT, CM.M_TALL, CM.JAR_M
        if V is not None:
            bad = MP.set_check(V, EMB_CATS)
            if bad:
                return NT(bad)
            items = [([V.tok(s) for s in seq], a, site) for seq, a, site in items]
            short = V.labels_of(list(CM.M_SHORT)); tall = V.labels_of(list(CM.M_TALL))
            jl = V.labels_of([CM.JAR_M]); jar = next(iter(jl)) if len(jl) == 1 else MP.AnyOf(jl)
    X, _, _, _ = Q.featurize(items, short=short, tall=tall, jar=jar)
    y = np.array([a for _, a, _ in items]); site = np.array([s for _, _, s in items])
    d = dict(items=items, X=X, y=y, site=site, sets=[set(CM.signs(s)) for s, _, _ in items], n=len(items))
    d["key"] = (tuple(y.tolist()), tuple(site.tolist()), colkey(X))
    return d


def emb_set_A(d):
    ATP.A.clear()
    ATP.A.update(items=d["items"], X=d["X"], y=d["y"], site=d["site"], sets=d["sets"])


def emb_null(d):
    emb_set_A(d)
    return np.array([ATP.nullA((i, "bin"))[1] for i in range(ATP.NNULL_A)])


# ------------------------------------------------------------------ SJ (stroked jar, copied)
def sj_icit_texts(V):
    """s2_test.icit_set with each M partner passed through V.tok (all-partners rule kept, prereg)."""
    if V is None:
        return S2.icit_set()
    seen, out = set(), []
    for t in icit_texts():
        ws = [s for s in t["seq"] if s.startswith("W")]
        if not ws:
            continue
        cls = S2.icit_cls(t["type"])
        key = (" ".join(t["seq"]), cls, t["site"])
        if key in seen:
            continue
        seen.add(key)
        ms = set()
        for w in ws:
            ms.update(MP.w_to_labels_all(V, w))
        out.append({"site": t["site"], "cls": cls, "signs": ms})
    return out


def sj_gate_m77():
    texts = {" ".join(t["seq"]) for t in m77_texts() if set(t["seq"]) & SJ_M}
    return len(texts)


def sj_inputs(cell):
    if cell == OTHER:
        n = sj_gate_m77()
        if n < 30:
            return NT(f"not run: count gate failed ({n} < 30 M77 texts with M343-M345)")
        texts = S2.m77_set(); SJL = set(SJ_M)
        gate = n
    else:
        if ("SJ", cell) in NT_BY_CONSTRUCTION:
            return NT(NT_BY_CONSTRUCTION[("SJ", cell)])
        V = variant(cell)
        if V is not None:
            bad = MP.set_check(V, SJ_CATS)
            if bad:
                return NT(bad)
        texts = sj_icit_texts(V)
        SJL = set(SJ_M) if V is None else V.labels_of(sorted(SJ_M))
        gate = None
    has = [bool(t["signs"] & SJL) for t in texts]
    d = dict(texts=texts, SJL=SJL, n=sum(t["cls"] == "pottery graffito" for t in texts), gate=gate)
    d["key"] = tuple((h, t["cls"], t["site"]) for h, t in zip(has, texts))
    return d


def sj_null_mean(d):
    """Exact mean of the pooled SJ count on pottery under within-site label permutation (no observed count read)."""
    by = collections.defaultdict(lambda: [0, 0, 0])
    for t in d["texts"]:
        b = by[t["site"]]; b[0] += 1; b[1] += t["cls"] == "pottery graffito"; b[2] += bool(t["signs"] & d["SJL"])
    return float(sum(npot * nsj / n for n, npot, nsj in by.values()))


# ------------------------------------------------------------------ RND (round_own_order, copied)
def rnd_inputs(cell):
    if cell == OTHER:
        return NT(OTHER_NOT_RUN["RND"])
    V = variant(cell)
    fw = fw_of(V)
    # round_own_order/run.py lines 15-18 (data construction); the list maps each legal W sign afterwards
    RT = json.load(open(ROOT / "experiments/round_seal_format/results.json"))["round_texts"]
    rnd = [[fw(s) for s in t] for t in (RO.leg(u["seq"].split()) for u in RT) if len(t) >= 2]
    home = [[fw(s) for s in t] for t in (RO.leg(x["seq"]) for x in distinct(icit_texts())
            if x["type"] == "SEAL:S" and x["site"] not in q2_gulf.FOREIGN_ALL and x["site"] != "Unknown") if len(t) >= 2]
    # lines 19-22
    Vv = sorted({s for t in rnd + home for s in t}) + ["<s>", "</s>"]
    hbylen = collections.defaultdict(list)
    for t in home:
        hbylen[min(len(t), 6)].append(t)
    keys = [min(len(t), 6) for t in rnd]
    d = dict(rnd=rnd, home=home, NV=len(Vv), hbylen=hbylen, keys=keys, n=len(rnd))
    d["key"] = MP.canon((rnd, home))
    return d


def ro_setup(d):
    RO.setup(rng=np.random.default_rng(20261124), NV=d["NV"], hbylen=d["hbylen"], keys=d["keys"])


# ------------------------------------------------------------------ dispatch
def inputs(sub, cell):
    if sub in ("Q1", "Q2"):
        return q12_inputs(sub, cell)
    if sub == "Q3":
        return q3_inputs(cell)
    if sub in ("T1", "T3"):
        return t_inputs(sub, cell)
    if sub == "EMB":
        return emb_inputs(cell)
    if sub == "SJ":
        return sj_inputs(cell)
    if sub == "RND":
        return rnd_inputs(cell)
    raise KeyError(sub)


def statistic(sub, d):
    """The row's own statistic on one cell's inputs. Called on native cells (reproduce) and, in test mode only, on
    variant / other-edition cells."""
    if sub in ("Q1", "Q2"):
        rho, p = L2.strat_perm_spearman(d["N"], d["y"], d["strata"], alt=d["alt"], rng=np.random.default_rng(20261115))
        return dict(rho=rho, p=p, n=d["n"])
    if sub == "Q3":
        units = d["units"]
        chi, p, shape = L2.perm_chi2([u[2] for u in units], [u[0] for u in units], [u[3] for u in units],
                                     nperm=d["nperm"], rng=np.random.default_rng(20261115))
        return dict(chi2=chi, p=p, shape=list(shape), n=d["n"])
    if sub == "T1":
        tt_setup(d)
        o, p, _ = TT.perm_p(lambda T: TT.t1_stat(d["dep1"], T), d["tier1"], d["str1"], TT.NPERM)
        return dict(G=o, p=p, units=d["n_T1_units"], deposits=d["n_T1_deposits"])
    if sub == "T3":
        tt_setup(d)
        o, p, _ = TT.perm_p(lambda T: TT.t3_stat(d["X3"], T), d["tier3"], d["str3"], TT.NPERM)
        return dict(S=o, p=p, groups=d["n_groups_complete"], features=d["n_features"])
    if sub == "EMB":
        auc = ATP.auc_bin(d["X"], (d["y"] == "unicorn").astype(int))
        return dict(auc=auc, n=d["n"])                       # p needs the null; added by statistic_p
    if sub == "SJ":
        S2.rng = np.random.default_rng(20261115)             # s2_test.py line 19, fresh as in the original run
        texts = [dict(t, signs=set(t["signs"])) for t in d["texts"]]
        r = SJT.strokedjar(S2, texts, d["SJL"])
        sj = r["signs"]["SJ"]
        return dict(obs=sj["obs"], exp=sj["exp"], ratio=sj["ratio"], p_enrich=sj["p_enrich"], n=r["n_pottery_texts"])
    if sub == "RND":
        ro_setup(d)
        return dict(RO.loo(d["rnd"]), n=d["n"])
    raise KeyError(sub)


def statistic_full(sub, d):
    r = statistic(sub, d)
    if sub == "EMB":
        r["p"] = float(ATP.pval(r["auc"], emb_null(d)))
    return r


def power_of(sub, d):
    """Planted power at the original prereg's effect size, on this cell's mapped inputs. Reads no real statistic."""
    if sub in ("Q1", "Q2"):
        L2.rng = np.random.default_rng(20261115)            # jitter stream used inside power_spearman
        return float(L2.power_spearman(d["N"], d["strata"], alt=d["alt"]))
    if sub == "Q3":
        u = d["units"]
        return float(L2.power_lot(u))
    if sub == "T1":
        tt_setup(d)
        return float(TT.power(TT.plant_t1, lambda T: TT.t1_stat(d["dep1"], T), d["str1"], "greater"))
    if sub == "T3":
        tt_setup(d)
        return float(TT.power(TT.plant_t3, lambda T: TT.t3_stat(d["X3"], T), d["str3"], "greater"))
    if sub == "EMB":
        null = emb_null(d)                                   # label-permutation null, no real AUC computed
        draws = [ATP.drawA(("non_unicorn", EMB_DELTA, i)) for i in range(ATP.NDRAW)]
        ok = [x for x in draws if x["feasible"]]
        return float(np.mean([ATP.pval(x["auc_bin"], null) < 0.05 for x in ok])) if ok else 0.0
    if sub == "SJ":
        return SJT.power_2x_from_mu(sj_null_mean(d))
    if sub == "RND":
        ro_setup(d)
        return float(np.mean([RO.loo(RO.homeset())["found"] for _ in range(RO.NSETS)]))
    raise KeyError(sub)


# ------------------------------------------------------------------ modes
def shape():
    out = dict(cells={}, native={})
    for sub in SUBS:
        nat = inputs(sub, None)
        out["native"][sub] = dict(n=nat["n"])
        out["cells"][sub] = {}
        for cell in MP.CELLS:
            d = inputs(sub, cell)
            if "NT" in d:
                st = "NOT_RUN" if d["NT"].startswith("not run") else "NT"
                out["cells"][sub][cell] = dict(status=st, reason=d["NT"])
            elif cell != OTHER and d["key"] == nat["key"]:
                out["cells"][sub][cell] = dict(status="INVARIANT", n=d["n"])
            else:
                out["cells"][sub][cell] = dict(status="candidate", n=d["n"])
                if sub == "SJ" and cell == OTHER:
                    out["cells"][sub][cell]["gate_texts"] = d["gate"]
            print(sub, cell, out["cells"][sub][cell], flush=True)
    out["summary"] = {}
    for row, subs in ROWS.items():
        out["summary"][row] = {s: dict(collections.Counter(out["cells"][s][c]["status"] for c in MP.CELLS)) for s in subs}
    json.dump(out, open(HERE / "shape.json", "w"), indent=1)
    print(json.dumps(out["summary"], indent=1))
    return out


def reproduce():
    rep = {}
    for sub in SUBS:
        t0 = time.time()
        r = statistic(sub, inputs(sub, None))
        name, pub, src = PUBLISHED[sub]
        got = r[name]
        rep[sub] = dict(statistic=name, published=pub, reproduced=got, match=bool(abs(got - pub) <= TOL[sub]),
                        source=src, detail={k: v for k, v in r.items() if k != name}, seconds=round(time.time() - t0, 1))
        print(sub, rep[sub], flush=True)
    # the native Q3 unit set must equal l2_quantity.m77_units() exactly
    rep["Q3"]["units_equal_l2"] = sorted(L2.m77_units()) == m77_units_mapped(None)
    return rep


def _power_task(args):
    sub, cell = args
    t0 = time.time()
    d = inputs(sub, cell)
    pw = power_of(sub, d)
    return sub, cell, dict(power=pw, n=d["n"], seconds=round(time.time() - t0, 1))


def unchecked_rows(rep):
    return [row for row, subs in ROWS.items() if any(not rep[s]["match"] for s in subs)]


def power_mode(reproduce_only=False):
    rep = reproduce()
    bad = unchecked_rows(rep)
    print("rows UNCHECKED by reproduce mismatch:", bad)
    if reproduce_only:
        return
    sh = json.load(open(HERE / "shape.json"))
    live = {s for row, subs in ROWS.items() if row not in bad for s in subs}
    tasks = [(s, c) for s in SUBS if s in live for c in MP.CELLS if sh["cells"][s][c]["status"] == "candidate"]
    tasks.sort(key=lambda t: t[0] != "EMB")                 # longest first
    print(f"{len(tasks)} candidate cells -> planted power, {NWORK} workers", flush=True)
    from multiprocessing import Pool
    t0 = time.time()
    with Pool(NWORK) as P:
        res = P.map(_power_task, tasks, chunksize=1)
    cells = {s: {} for s in SUBS}
    for s in SUBS:
        for c in MP.CELLS:
            cells[s][c] = dict(sh["cells"][s][c])
    for s, c, r in res:
        cells[s][c].update(r)
        cells[s][c]["status"] = "testable" if r["power"] >= POWER_BAR else "NT"
        if r["power"] < POWER_BAR:
            cells[s][c]["reason"] = f"power {r['power']:.3f} < {POWER_BAR} (the list masks the effect)"
        print(s, c, cells[s][c], flush=True)
    out = dict(reproduce=rep, rows_unchecked=bad, power_bar=POWER_BAR, cells=cells, seconds=round(time.time() - t0, 1),
               draws=dict(Q12="power_spearman rho 0.3, 300 sims x 400 perms", Q3="power_lot 30%, 200 x 400",
                          T="200 plants x 1000 perms", EMB=f"{ATP.NNULL_A} nulls, {ATP.NDRAW} plants at +{EMB_DELTA}",
                          RND=f"{RO.NSETS} home sets", SJ="Poisson 2x analytic"))
    json.dump(out, open(HERE / "power.json", "w"), indent=1, default=float)
    print("wrote power.json; commit it before running test mode")


def power_committed():
    rel = "experiments/r_symmetry/power.json"
    if not (HERE / "power.json").exists():
        return False, "power.json does not exist"
    h = subprocess.run(["git", "log", "-1", "--format=%H", "--", rel], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    if not h:
        return False, "power.json is not committed (git log -1 -- experiments/r_symmetry/power.json is empty)"
    dirty = subprocess.run(["git", "status", "--porcelain", "--", rel], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    if dirty:
        return False, f"power.json has uncommitted changes: {dirty}"
    return True, h


def _test_task(args):
    sub, cell = args
    return sub, cell, statistic_full(sub, inputs(sub, cell))


def family_verdict(members):
    """members: list of (kill, survive) for testable cells of one family -> (kill_met, survive_met)."""
    n = len(members)
    k = sum(m[0] for m in members); s = sum(m[1] for m in members)
    if n == 1:
        return members[0]
    return k * 2 > n, s * 2 > n                              # majority decides; 1-1 tie: kill not met (U4 for survive)


def row_verdict(row, cells, unchecked):
    if row in unchecked:
        return dict(verdict="UNCHECKED", reason="native statistic did not reproduce")
    subs = ROWS[row]
    per_cell = {}
    for c in MP.CELLS:
        rs = [(s, cells[s][c]) for s in subs if cells[s][c].get("status") == "testable" and "result" in cells[s][c]]
        if not rs:
            continue
        ks = [verdict_of(s, x["result"]) for s, x in rs]
        per_cell[c] = (all(k for k, _ in ks), any(sv for _, sv in ks))          # U3
    fams = collections.defaultdict(list)
    for c, v in per_cell.items():
        f = MP.FAMILY[c]
        if f is not None:
            fams[f].append(v)
    testable = {f: family_verdict(v) for f, v in fams.items() if (len(v) >= 2 if f in MP.MULTI_FAMILIES else len(v) == 1)}
    out = dict(cells={c: dict(kill=v[0], survive=v[1]) for c, v in per_cell.items()},
               families={f: dict(kill=v[0], survive=v[1]) for f, v in testable.items()})
    n = len(testable)
    notmet = sum(not v[0] for v in testable.values())
    if n < 2:
        out.update(verdict="UNCHECKED", reason=f"{n} testable non-invariant families (< 2)")
    elif any(v[1] for v in testable.values()) or notmet >= 3 or notmet * 2 > n:
        out.update(verdict="ARTEFACT", reason=f"survive bar met in {sum(v[1] for v in testable.values())}; kill not met in {notmet}/{n}")
    elif notmet == 0:
        out.update(verdict="HOLDS", reason=f"kill met in all {n} testable families")
    else:
        out.update(verdict="WEAKENS", reason=f"kill not met in {notmet}/{n} families; survive bar met nowhere")
    return out


def test_mode():
    ok, why = power_committed()
    if not ok:
        sys.exit(f"REFUSED: {why}")
    pw = json.load(open(HERE / "power.json"))
    cells = pw["cells"]; bad = pw["rows_unchecked"]
    live = {s for row, subs in ROWS.items() if row not in bad for s in subs}
    tasks = [(s, c) for s in SUBS if s in live for c in MP.CELLS if cells[s][c].get("status") == "testable"]
    first = [t for t in tasks if t[1] == OTHER]                # the other-edition cells run first
    rest = [t for t in tasks if t[1] != OTHER]
    from multiprocessing import Pool
    with Pool(NWORK) as P:
        res = P.map(_test_task, first, chunksize=1)
        for s, c, r in res:
            print("OTHER EDITION", s, r, flush=True)
        res += P.map(_test_task, rest, chunksize=1)
    for s, c, r in res:
        cells[s][c]["result"] = r
        cells[s][c]["kill"], cells[s][c]["survive"] = verdict_of(s, r)
    verdicts = {row: row_verdict(row, cells, bad) for row in ROWS}
    verdicts.update({row: dict(verdict="OUT OF SCOPE", reason=why) for row, why in OUT_OF_SCOPE.items()})
    out = dict(power_commit=why, order="other-edition cells first", cells=cells, verdicts=verdicts)
    json.dump(out, open(HERE / "test.json", "w"), indent=1, default=float)
    print(json.dumps(verdicts, indent=1))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "shape"
    if mode == "shape":
        shape()
    elif mode == "power":
        power_mode(reproduce_only="--reproduce-only" in sys.argv)
    elif mode == "test":
        test_mode()
    else:
        sys.exit(__doc__)
