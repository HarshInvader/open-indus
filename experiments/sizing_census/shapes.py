"""Shape tabulation for the sizing census (prereg docs/prereg/sizing_census.md, sealed).

Run from the repo root:  .venv/bin/python -I experiments/sizing_census/shapes.py
Writes experiments/sizing_census/shapes.json (the prereg's `cases.json` role: kill-case shapes, census-route
shapes, curve counts and the U-row assignment).

Reading rule (frozen): counts only. Rows, class sizes, single-variable prevalences (a sign's row count over all
rows; a sign's rate inside a text-length stratum of ONE class), documents per word, words per document, and the
marginal base rates of each anchor. No feature x label table is built, no association statistic is computed, and
`experiments/anchor_ceiling/truth/labels_*.json` is never opened (truth/words.txt is a word list, not labels).

Where the repo holds no marginal for a route, the stated prereg count is carried and the row is flagged
`bound: "upper"` (calc.py then maximises power over the unknown marginal); nothing is invented silently.
"""
import csv, importlib.util, json, math, sys
from collections import Counter
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
OUT = HERE / "shapes.json"
SEED = 20261125                                   # only for the generator-based margins (texts, not outcomes)


def load(name, rel):
    """import a repo script under a unique module name (several experiments call their file run.py)."""
    p = ROOT / rel
    sys.path.insert(0, str(p.parent))
    spec = importlib.util.spec_from_file_location(name, p)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


# ------------------------------------------------------------------ A1 helpers
def a1_shape(n, n_A, counts, m, alpha, alpha_note, cand_rule, extra=None):
    s = dict(family="A1", n=int(n), n_A=int(n_A), n_B=int(n - n_A), c_g=sorted(int(c) for c in counts),
             n_candidates=len(counts), m=int(m), alpha=alpha, alpha_note=alpha_note, candidate_rule=cand_rule)
    s.update(extra or {})
    return s


def m77_seals():
    """case 4 / route 1: the 1,149 distinct M77 seal texts of animal classes with >= 10 texts (animal_tie_power)."""
    R = load("atp_run", "experiments/animal_tie_power/run.py")
    items, _ = R.indus_items()
    sets = [set(R.signs(s)) for s, _, _ in items]
    cls = Counter(a for _, a, _ in items)                 # class sizes: a label marginal
    doc = Counter(g for s in sets for g in s)             # sign row counts over all rows: a text marginal
    return len(items), cls, doc


def tablet_rows():
    """case 3 / route 2: tablet_pic_text rows (61), class sizes, tie signs in >= 5 rows."""
    T = load("tpt_run", "experiments/tablet_pic_text/run.py")
    R, info = T.rows()
    gate = json.load(open(ROOT / "experiments/tablet_pic_text/gate.json"))
    cnt = Counter(r["cls"] for r in R)
    elig = sorted(c for c, n in cnt.items() if n >= T.MIN_ROWS and c not in gate["failed"])
    doc = Counter(g for r in R for g in set(r["flat"]))
    tie = {g: n for g, n in doc.items() if n >= T.MIN_VOC}
    return len(R), cnt, elig, tie


# ------------------------------------------------------------------ harp_pack generator inputs (power.py, re-derived)
def harp_inputs():
    """The real-input block of harp_pack/power.py, re-derived here: power.py itself is NOT imported, because importing
    it truncates power.log and runs its generator at module level."""
    from corpus.load import icit_texts, distinct
    import experiments.harp_pack.score as S
    from experiments.harp_pack.loader import numeral_value
    H = [r for r in icit_texts() if r["site"] == "Harappa"]
    graf = distinct([r for r in H if r["type"] in ("POT:T:g", "POsT:T:g")])
    tok, lens, nbroken = {}, [], 0
    for r in graf:
        sg = [s for s in r["seq"] if s not in ("|", "#")]
        if not sg: continue
        lens.append(len(sg)); nbroken += "#" in r["seq"]
        for s in sg: tok[s] = tok.get(s, 0) + 1
    signs = np.array(sorted(tok)); P = np.array([tok[s] for s in signs], float); P /= P.sum()
    LENS = np.array(lens); BROKEN = nbroken / len(lens)
    seals = S.harappa_seals()
    st = {}
    for sg in seals:
        c = st.setdefault(S.len_stratum(sg), [0, 0]); c[0] += 1; c[1] += S._has(sg, S.JAR)
    short = float(np.mean(LENS <= 5))
    strata = []
    for k in sorted(st):
        ln, br = k.split("|")
        share = (short if ln == "1-5" else 1 - short) * (BROKEN if br == "broken" else 1 - BROKEN)
        strata.append(dict(stratum=k, ref_n=st[k][0], ref_rate=st[k][1] / st[k][0], target_share=share))
    rng = np.random.default_rng(SEED)

    def text():
        return list(rng.choice(signs, size=int(rng.choice(LENS)), p=P))
    # value margin of numeral_value over generated sherd texts (power.py's C9 rows), ties kept
    V = Counter(int(numeral_value(text())) for _ in range(200000))
    margin = {str(v): c / 200000 for v, c in sorted(V.items())}

    def dup_share(n_rows, lots_pp, reps=200):
        """power.py collapse of rim rows to (lot, text) units: share of rows that are duplicates."""
        PER = ["1", "2", "3A", "3B", "3C", "4", "5"]; PS = np.array([0.05, 0.10, 0.15, 0.25, 0.30, 0.10, 0.05])
        tot_r = tot_u = 0
        for _ in range(reps):
            per = rng.choice(PER, size=n_rows, p=PS); keys = set()
            for i in range(n_rows):
                sg = text()
                if rng.random() < BROKEN: sg.insert(int(rng.integers(0, len(sg) + 1)), "#")
                keys.add((f"{per[i]}-{int(rng.integers(lots_pp))}", " ".join(sg)))
            tot_r += n_rows; tot_u += len(keys)
        return 1 - tot_u / tot_r
    return dict(n_graffiti=len(LENS), broken=BROKEN, short_share=short, seal_strata=strata, n_seals=len(seals),
                v_margin=margin, dup_share=dup_share)


# ------------------------------------------------------------------ anchor_ceiling (case 1, curve)
def anchor_shapes():
    """draw-0 shape for family B, plus the 5-draw pool rule (text counts only; no truth label opened)."""
    K = load("ac_core", "experiments/anchor_ceiling/core.py")
    words = sorted(open(ROOT / "experiments/anchor_ceiling/truth/words.txt").read().split())
    D = [K.draw_docs(k) for k in range(K.NDRAW)]
    sc = [set(K.eligible(dev, held)[1]) for dev, held in D]
    ok = Counter(w for s in sc for w in s)
    pool = [w for w in words if ok[w] >= 4]; rest = [w for w in words if ok[w] < 4]
    dev, held = D[0]
    cd, ch = K.doc_counts(dev), K.doc_counts(held)
    base = {}
    for v, key in (("S", "site"), ("K", "cls"), ("P", "pic")):
        c = Counter(d[key] for d in dev + held); n = sum(c.values())
        base[v] = {str(x): k / n for x, k in sorted(c.items())}
    fields = [["place", 25, 16], ["admin", 14, 10], ["land", 8, 5], ["occupation", 8, 3], ["person", 5, 3]]
    B = dict(family="B", n_dev=len(dev), n_held=len(held),
             wpd_dev=[len(d["words"]) for d in dev], wpd_held=[len(d["words"]) for d in held],
             base=base, fields=fields,
             words_pool=[[cd[w], ch[w]] for w in pool], words_rest=[[cd[w], ch[w]] for w in rest],
             s=1.0, ndraw=5, need=4, min_dev=5, min_held=2, min_field_words=3, kcl=6,
             held_in_centroids=True, dev_gate=True, plant_rule="v2", nperm=1000,
             note="fields and pool counts as stated in the prereg (from anchor_ceiling v2); counts per word from draw 0")
    held_counts = sorted(ch[w] for w in pool if cd[w] >= 5 and ch[w] >= 2)
    diag = dict(union_words=len(words), pool_words=len(pool), rest_words=len(rest),
                prereg_union=92, prereg_pool=44, draw_sizes=[[len(a), len(b)] for a, b in D],
                pool_held_docs_draw0=dict(Counter(held_counts)),
                dev_docs_per_union_word_draw0=dict(Counter(cd[w] for w in words)))
    # curve: draw 0, dev and held together
    docs = dev + held
    cnt = K.doc_counts(docs)
    E = {str(d): sum(1 for w, n in cnt.items() if n >= d + 5) for d in (2, 3, 5, 8, 12, 20)}
    curve = dict(n_docs=len(docs), E_d=E, reachable={d: e >= 30 for d, e in E.items()},
                 docs_per_word=dict(sorted(Counter(cnt.values()).items())),
                 wpd=dict(sorted(Counter(len(d["words"]) for d in docs).items())))
    return B, diag, curve


# ------------------------------------------------------------------ route-5 in-hand pool (m342_offsite primary)
def m342_pool():
    M = load("m342_mod", "experiments/m342_offsite/m342.py")
    pool = M.pool_m(M.cons_recs())
    st = {}
    for seq, pot, s in pool:
        c = st.setdefault(str(s), [0, 0, 0])
        if pot: c[2] += 1                                  # pottery count only (its jar count is the outcome)
        else:
            c[0] += 1; c[1] += any(x == M.JAR for x in seq)
    strata = [dict(stratum=k, ref_n=a, ref_rate=b / a, target_n=p) for k, (a, b, p) in sorted(st.items()) if a > 0]
    dropped = sum(p for k, (a, b, p) in st.items() if a == 0)
    return dict(strata=strata, n_pot=sum(x["target_n"] for x in strata), n_seal=sum(x["ref_n"] for x in strata),
                pot_in_strata_without_seals=dropped)


def main():
    out = dict(prereg="docs/prereg/sizing_census.md", reading_rule="counts only; no feature x label table",
               kill={}, census=[], curve={}, u_rows={})

    # ---------------- case 1 (B)
    B, diag, curve = anchor_shapes()
    out["kill"]["case1"] = dict(B, cells=["dev_gate", "held_ari", "held_person"], diagnostics=diag)
    out["curve"] = curve

    # ---------------- case 3 (A1, tablet bovine)
    n, cnt, elig, tie = tablet_rows()
    out["kill"]["case3"] = a1_shape(n, cnt["bovine"], tie.values(), m=len(tie), alpha=0.025,
                                    alpha_note="test at alpha/m = 0.025/13 (prereg: m = 13, alpha = 0.025)",
                                    cand_rule="signs in >= 5 of the rows (tablet_pic_text S['tie'])",
                                    extra=dict(class_sizes=dict(cnt), eligible=elig, deltas=[0.05, 0.10, 0.20],
                                               grey=[0.20], effect="delta (nominal)"))

    # ---------------- case 4 (A1, M77 seals)
    nS, cls, doc = m77_seals()
    c5 = [c for c in doc.values() if c >= 5]; c15 = [c for c in doc.values() if c >= 15]
    nonuni = nS - cls["unicorn"]
    out["kill"]["case4a"] = a1_shape(nS, nonuni, c5, m=len(c5), alpha=0.05,
                                     alpha_note="test at 0.05/m, m = candidate list size (classifier statistic)",
                                     cand_rule="M77 signs in >= 5 of the 1,149 texts (animal_tie_power cands)",
                                     extra=dict(deltas=[0.05, 0.10, 0.20, 0.40], class_A="non_unicorn"))
    for key, a in (("case4b", "shorthorn_bull"), ("case4c", "elephant")):
        out["kill"][key] = a1_shape(nS, cls[a], c15, m=30, alpha=0.05, alpha_note="test at 0.05/30 (sealed F14 test count)",
                                    cand_rule="M77 signs in >= 15 of the 1,149 texts (F14 min_doc; strata not modelled, G2)",
                                    extra=dict(deltas=[0.05, 0.10, 0.20, 0.40, 0.80], class_A=a))

    # ---------------- case 5 (harp_pack)
    H = harp_inputs()
    scen = {"central": dict(n_sherd=975, rim=0.30, lots_pp=60, n_forms=5),
            "pessimistic": dict(n_sherd=600, rim=0.20, lots_pp=40, n_forms=6)}   # form share 0.7 adds an 'NA' form
    c6 = dict(family="A2b", strata=[dict(stratum=s["stratum"], ref_n=s["ref_n"], ref_rate=s["ref_rate"],
                                         target_share=s["target_share"]) for s in H["seal_strata"]],
              ref_fixed=True, tail="upper", ratio="oe", bar=1.25, R=1.5, alpha=0.05 / 13,
              alpha_note="harp_pack 0.05/13 = 0.00385, m = 1 (pre-named)", m=1,
              cells=[dict(n=725, label="central"), dict(n=546, label="central x0.75"), dict(n=393, label="pessimistic"),
                     dict(n=366, label="central x0.5"), dict(n=184, label="central x0.25")],
              note="target stratum shares = power.py generator (length from Harappa graffiti, broken share); "
                   "reference = ICIT Harappa seals per len_stratum, rate = jar-sign presence within stratum")
    out["kill"]["case5a"] = c6
    cells9 = []
    for n_, sc_, k_ in ((290, "central", 1.0), (220, "central", 0.75), (146, "central", 0.5),
                        (120, "pessimistic", 1.0), (72, "central", 0.25)):
        p = scen[sc_]; rows = int(round(p["n_sherd"] * k_ * p["rim"]))
        cells9.append(dict(n=n_, label=f"{sc_} x{k_}", n_strata=p["n_forms"] * 7,
                           dup_share=H["dup_share"](rows, p["lots_pp"]), generator_rim_rows=rows))
    c9 = dict(family="A3", v_margin=H["v_margin"], rho=0.5, min_pos=8, min_n=3, alpha=0.05 / 13, m=1,
              alpha_note="harp_pack 0.00385, two-sided", cells=cells9,
              note="value margin = numeral_value over 200,000 power.py-generator texts; strata = forms x 7 periods, "
                   "equal-sized (G4); duplicate share from the generator's (lot, text) collapse of rim rows")
    out["kill"]["case5b"] = c9

    # ---------------- census (list frozen in the prereg; shapes recounted where the repo holds them)
    C = out["census"]
    st1 = [dict(label=f"in hand, class {a} ({cls[a]})",
                shape=a1_shape(nS, cls[a], c15, 30, 0.05, "0.05/30 (F14 family)", "signs in >= 15 texts"))
           for a, _ in cls.most_common() if a != "unicorn"]
    st1.insert(0, dict(label=f"in hand, non-unicorn ({nonuni})",
                       shape=a1_shape(nS, nonuni, c5, len(c5), 0.05, "0.05/m, classifier", "signs in >= 5 texts")))
    C.append(dict(route=1, name="seal text x animal", source="atlas 5.7", family="A1", effect=dict(delta=0.23),
                  effect_source="Linear B strength (animal_tie_power)", stated="1,149 rows; minorities 78/45/34/15/12/10/10",
                  recount=dict(n=nS, classes=dict(cls)), states=st1, what_adds_rows="more pictured seals with legible texts"))
    tb = out["kill"]["case3"]
    st2 = []
    for lab, k in (("in hand (61)", 1.0), ("ICIT code list (136)", 136 / 61), ("about 2x of 136 (CISI 3, HARP)", 272 / 61)):
        st2.append(dict(label=lab, shape=a1_shape(round(n * k), round(cnt["bovine"] * k), [round(c * k) for c in tie.values()],
                                                  len(tie), 0.025, "0.025/m as case 3", "signs in >= 5 rows",
                                                  extra=dict(scaled_from="case3", scale=k))))
    C.append(dict(route=2, name="tablet picture x text", source="5.7; Fuls code list; CISI 3", family="A1",
                  effect=dict(delta=0.23), effect_source="Linear B strength", stated="61 rows -> 136 -> about 2x",
                  recount=dict(n=n, classes=dict(cnt)), states=st2,
                  what_adds_rows="ICIT picture-code list; CISI vol. 3; HARP tablets"))
    C.append(dict(route=3, name="copper emblem out of sample", source="ranked study 6", family="A1",
                  effect=dict(delta=0.23), effect_source="Linear B strength", stated="under 30 rows, 7 signs",
                  states=[dict(label="in hand (stated)", shape=dict(family="A1", n=29, n_A=None, c_g=None, n_candidates=7,
                                                                   m=7, alpha=0.05, bound="upper",
                                                                   note="no class or sign marginal in the repo: n = 29 "
                                                                        "('under 30'), m = 7; calc maximises over n_A and c_g"))],
                  what_adds_rows="out-of-sample copper tablets"))
    C.append(dict(route=4, name="per-sign profiles: sign x object, sign x site", source="3.6", family="B",
                  effect="curve d*", effect_source="U-row curve leg", stated="2-5 held-out documents per sign",
                  states=[dict(label="in hand (case-1 shape, 2-5 held-out docs)", shape="kill.case1")],
                  what_adds_rows="documents per sign >= d*"))
    m3 = m342_pool()
    C.append(dict(route=5, name="jar sign on pottery", source="7.8; harp C6", family="A2b", effect=dict(R=1.5),
                  effect_source="m342_offsite.md, harp_pack.md", stated="65 texts -> >= 184 new units",
                  recount=dict(n_pot=m3["n_pot"], n_seal=m3["n_seal"]),
                  states=[dict(label=f"in hand (consensus H/L/K, {m3['n_pot']} pottery)",
                               shape=dict(family="A2b", strata=m3["strata"], ref_fixed=True, tail="upper", ratio="oe",
                                          bar=1.25, R=1.5, alpha=0.05, m=1, alpha_note="m342_offsite one test, 0.05",
                                          n=m3["n_pot"])),
                          dict(label="HARP (>= 184 new units)", shape=dict(c6, n=184, cells=None))],
                  what_adds_rows="HARP sherd database (new units off ICIT)"))
    pre_obj = 0
    for r in csv.DictReader(open(ROOT / "experiments/firing_stage/vessel_marks.csv")):
        pre_obj += r["firing_conf"] == "object"
    PS = [0.05, 0.10, 0.15, 0.25, 0.30, 0.10, 0.05]
    def fs(rate_t, rate_r, tail, bar, lab):
        return [dict(label=f"{lab} in hand ({pre_obj} object-staged vs 384 graffiti, one stratum)",
                     shape=dict(family="A2b", strata=[dict(stratum="all", ref_n=384, ref_rate=rate_r, target_share=1.0)],
                                ref_fixed=True, tail=tail, ratio="rr", bar=bar, R=rate_t / rate_r, alpha=0.025, m=1,
                                alpha_note="firing_stage 0.025", n=pre_obj)),
                dict(label=f"{lab} HARP (146 pre-firing units)",
                     shape=dict(family="A2b", strata=[dict(stratum=str(i), ref_rate=rate_r, target_share=s, ref_share=s)
                                                      for i, s in enumerate(PS)],
                                ref_fixed=False, ref_n_total=4 * 146, tail=tail, ratio="rr", bar=bar, R=rate_t / rate_r,
                                alpha=0.05 / 13, m=1, alpha_note="harp_pack 0.00385", n=146,
                                note="post units = 4 x pre (power.py pre share 0.20); 7 period strata at PSHARE"))]
    C.append(dict(route=6, name="firing stage", source="10b.3; harp C1, C2", family="A2b",
                  effect=dict(C1="0.04 vs 0.16", C2="0.15 vs 0.05"), effect_source="harp_pack.md",
                  stated="36 staged vessels -> >= 146 pre-firing units", recount=dict(object_staged=pre_obj),
                  states=fs(0.04, 0.16, "lower", 0.5, "C1") + fs(0.15, 0.05, "upper", 2.0, "C2"),
                  what_adds_rows="HARP sherd database with firing stage"))
    small = {str(v): 1 / 8 for v in range(8)}
    C.append(dict(route=7, name="numerals vs size", source="6.8; harp C9-C12", family="A3", effect=dict(rho=0.5),
                  effect_source="magnitude.md, harp_pack.md", stated="rods 13, implements 3, bangles 0 -> 146 rims",
                  states=[dict(label="rods in hand (13)", shape=dict(family="A3", v_margin=small, rho=0.5, min_pos=0, min_n=8,
                                                                    alpha=0.0125, m=1, n=13, n_strata=1, dup_share=0.0,
                                                                    alpha_note="magnitude 0.05/4",
                                                                    note="margin = power.py sim_small_class (V uniform 0-7)")),
                          dict(label="implements in hand (3)", shape=dict(family="A3", v_margin=small, rho=0.5, min_pos=0,
                                                                         min_n=8, alpha=0.0125, m=1, n=3, n_strata=1,
                                                                         dup_share=0.0, alpha_note="magnitude 0.05/4")),
                          dict(label="bangles in hand (0)", shape=dict(family="A3", v_margin=small, rho=0.5, min_pos=0,
                                                                      min_n=8, alpha=0.0125, m=1, n=0, n_strata=1,
                                                                      dup_share=0.0, alpha_note="magnitude 0.05/4")),
                          dict(label="HARP rims (146)", shape=dict(c9, n=146, n_strata=35, dup_share=cells9[2]["dup_share"],
                                                                  cells=None))],
                  what_adds_rows="HARP rim diameters; linked implement masses"))
    C.append(dict(route=8, name="bangle oval", source="10b.2; BO-H1", family="A2a", effect=dict(p1=0.15),
                  effect_source="bangle_oval.md", stated="0 new texts -> HARP list",
                  states=[dict(label="in hand (0 new texts)", shape=dict(family="A2a", n=0, p0=0.0106, bar=0.08, min_n=10,
                                                                       alpha=0.05, m=1, p1=0.15))],
                  what_adds_rows="HARP inscribed-bangle list; Fuls 2023 catalogue"))
    C.append(dict(route=9, name="titles on door sealings", source="5.8", family="A1", effect=dict(delta=0.23),
                  effect_source="Linear B strength", stated="3 door sealings of 55",
                  states=[dict(label="in hand", shape=a1_shape(55, 3, [6], 1, 0.05, "one pre-named feature (any title)",
                                                               "any title sign; 6 of 55 diagnostic sealings (atlas 5.8 marginal)"))],
                  what_adds_rows="newly excavated door sealings with recorded backs"))
    J = json.load(open(ROOT / "experiments/scene_text/join_results.json"))["H1_primary_cons_excl_discovery"]
    nH = J["n_types_by_site"]["Harappa"]; cH = round(J["base_rate_by_site"]["Harappa"] * nH)
    C.append(dict(route=10, name="M328 on offering scenes", source="10b.1", family="A1", effect=dict(OR=3.0),
                  effect_source="scene_text.md (pass bar)", stated="1 offering type -> 3-6 with photos",
                  recount=dict(population_types=J["population_types"], offering_types=J["offering_types"],
                               harappa_types=nH, harappa_W700_types=cH),
                  states=[dict(label=f"{lab} ({k} offering types)",
                               shape=a1_shape(nH, k, [cH], 1, 0.05, "one pre-named sign, 0.05",
                                              "W700 rate on Harappa TAB:B types (0.59)"))
                          for lab, k in (("in hand", J["offering_types"]), ("photos, low", 3), ("photos, high", 6))],
                  what_adds_rows="600 dpi / RTI of the offering tablets; CISI vol. 3"))
    C.append(dict(route=11, name="ticked fish by area", source="10b.15; TF1; harp C13", family="A2a",
                  effect=dict(rate_multiple=3), effect_source="harp_pack.md", stated="6 ticked fish of 417 Harappa seal texts",
                  states=[dict(label="in hand (one area of 20 seals)",
                               shape=dict(family="A2a", n=20, p0=6 / 417, p1=3 * 6 / 417, bar=None, min_n=0,
                                          alpha=0.05 / 13, m=1, alpha_note="harp_pack 0.00385",
                                          note="area size = the stated minimum of 20 seals"))],
                  what_adds_rows="block or house findspots for more ticked-fish seals"))
    C.append(dict(route=12, name="city sign stock", source="10b.5", family="A1", effect=dict(delta=0.23),
                  effect_source="Linear B strength", stated="as in atlas -> 3x dated seals",
                  states=[dict(label="in hand (P2 open slot, 270 seals, 60 Harappa)",
                               shape=dict(family="A1", n=270, n_A=60, c_g=None, m=1, alpha=0.05, bound="upper",
                                          note="site_signal RESULTS counts; sign marginals not tabulated: best c_g, m = 1")),
                          dict(label="3x dated Harappa seals (390, 180 Harappa)",
                               shape=dict(family="A1", n=390, n_A=180, c_g=None, m=1, alpha=0.05, bound="upper"))],
                  what_adds_rows="about 3x more dated Harappa seals"))
    for r, nm, src, st in ((13, "line breaks", "10b.10", "74 two-line texts; sealed gate n >= 150"),
                           (14, "tablets quote seals; M99 relator", "5.10; 4.11", "as in atlas"),
                           (15, "Gulf round texts", "1.10; F1/F2", "12-28 texts; 0 new of 8 needed"),
                           (16, "new-find predictions P1-P15, L1-L7, PK", "registry A",
                            "12 new objects, 2 scorable; each minimum n as sealed"),
                           (17, "lots and archives", "5.1, 5.3, 10b.4, 10b.14; harp C7", "-> 184 tablet units in lots >= 3"),
                           (18, "copper calendar; carver hands, craft", "5.6; 10b.17", "as in atlas"),
                           (19, "Meluhha tablet photos", "9.2", "0 photos -> 2 tablets"),
                           (20, "edition sweep for stamped tablets", "ranked item 2", "1 firm positive; 10 needed")):
        C.append(dict(route=r, name=nm, source=src, family="none", effect="raw n", stated=st, states=[],
                      note="raw n as stated in the prereg; not recounted"))
    C.append(dict(route=21, name="phonetic keys by fit", source="1.1", family="C", effect="not sized",
                  stated="10,005 tokens; key coverage", states=[], verdict="untestable by fit at stated power"))

    # ---------------- U rows (assignment frozen in the prereg)
    rows = {r["id"]: r for r in json.load(open(ROOT / "experiments/scorecard_v1/final.json"))["rows"]}
    own = ["MUK25-fish-gem", "MUK22-gold-ratti", "MUK23-kanmer-occupation", "MUK23-wild-ass", "MUK19-crop-on-jars",
           "PAR-sign193-weight", "PAR-man-steelyard", "LAU10-twins-prefix", "MAH09-jar-bearer", "MAH09-arrow-bearer",
           "PAR75-chanhu-toponym"]
    route = {"WEL15-jar-40L": 5, "KEN06-jar-strokes": 7, "MUK23-triple-cup-goblet": 7, "HV-bangle-workshop": 8,
             "FT05-access-control": 9, "LAU10-other-language": 15, "CAL-noise-keys": 21, "KEY-yajnadevam": 21}
    none = ["FUN-sigil", "MUK23-no-names-no-toponyms", "MAH-bearer-kaviti", "PAR-vel-substitution",
            "PAR-murukan-partners", "KEN20-premature-marks", "FSW04-emblems", "OWN-7"]
    U = {}
    for i in own + list(route) + none:
        r = rows.get(i)
        U[i] = dict(in_final=r is not None, tier=r and r["tier"], evidence=r and r["evidence"],
                    rule="own A1 at delta 0.23" if i in own else (f"census route {route[i]}" if i in route else "no count rule"),
                    shape=None if i in own else "-")
    out["u_rows"] = dict(rows=U, n_assigned=len(U), n_U_in_final=sum(1 for r in rows.values() if r["tier"] == "U"),
                         note="own-A1 shapes are read by hand from each row's cited RESULTS (prereg); fill `shape` "
                              "with an A1 shape before the curve leg, else that row reports raw n only")
    json.dump(out, open(OUT, "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
    k = out["kill"]
    print(json.dumps(dict(case1=diag | dict(n_dev=B["n_dev"], n_held=B["n_held"]),
                          case3=dict(n=k["case3"]["n"], n_A=k["case3"]["n_A"], m=k["case3"]["m"]),
                          case4=dict(n=nS, n_A=[k["case4a"]["n_A"], k["case4b"]["n_A"], k["case4c"]["n_A"]],
                                     m_4a=k["case4a"]["m"], cands15=len(c15)),
                          case5b_dup=[c["dup_share"] for c in cells9], curve_E_d=curve["E_d"],
                          route5_in_hand=dict(n_pot=m3["n_pot"], n_seal=m3["n_seal"]), route6_object_staged=pre_obj,
                          route10=dict(nH=nH, cH=cH)), indent=1, default=str))


if __name__ == "__main__":
    main()
