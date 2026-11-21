"""Uniformity paper, step 1 (prereg docs/prereg/uniformity_paper_step1.md).

Every condition goes through the benchmark's own code, exactly as experiments/redteam_uniformity/rt.py does:
uniformity_benchmark/run.py clean() (drop strings found at both sides, then the non-chaining greedy de-dup of
fish_tick_closer_v2/dedup.py), draw_n() (Indus length mix, balanced sides, bin filling) and score() (frozen
site_signal NB pipeline + one permuted-label AUC per draw). Planted stocks use rt.plant(); descriptive stats
use rt.describe(). No new classifier.

  A  Linear B Knossos vs Pylos (DAMOS), plus variants; Proto-Elamite is checked for size only.
  B  Name-free references (Ur III by ORACC part of speech, Latin by editors' capitals, Linear B by name lists),
     and a reverse power test: city-specific "names" planted into Indus at several rates.
  C  Within-city floor: Mohenjo-daro DK area vs HR+VS areas, DK deep vs shallow, Harappa mound F vs AB (M77).

  board/run.sh .venv/bin/python -I experiments/uniformity_paper/step1/s1.py sizes
  board/run.sh .venv/bin/python -I experiments/uniformity_paper/step1/s1.py run      # resumable -> draws.jsonl
  .venv/bin/python -I experiments/uniformity_paper/step1/s1.py report                 # -> results.json, table.md
"""
import csv
import json
import re
import sys
import zlib
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments/uniformity_benchmark"))
sys.path.insert(0, str(ROOT / "experiments/redteam_uniformity"))
import run as ub  # noqa: E402  benchmark clean / draw / score, unchanged
import rt  # noqa: E402  red-team pools, transforms, plant(), describe(), unchanged
import lib  # noqa: E402  frozen site_signal pipeline
from corpus.load import m77_texts  # noqa: E402

DATA = HERE / "data"
N_DRAWS = 30
SEED = 20261123
N_MAX = 227                      # Indus like-for-like size per side
MIX, _ = ub.indus_mix()
MD, HA = "Mohenjo-daro", "Harappa"
GATE_Q = 0.15                    # planted-answer power gate: rt.plant new100 stock at q = 0.15
NAME_RATES = (0.1, 0.2, 0.3, 0.5, 0.75, 1.0)


def _jl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8")]


def _fix(texts):
    out = []
    for t in texts:
        L = [l for l in t["lines"] if l]
        if L:
            out.append(dict(id=t["id"], site=t["site"], lines=L, group=t["group"]))
    return out


# =========================================================================== A  Linear B
LB_KEEP = {
    "whole": lambda w, cl, tag: [w],
    "syll": lambda w, cl, tag: [w] if cl == "w" else [],
    "ideo": lambda w, cl, tag: [w] if cl == "i" else [],
    "nonames": lambda w, cl, tag: [] if tag == "name" else [w],
    "syll_nonames": lambda w, cl, tag: [w] if (cl == "w" and tag != "name") else [],
    "whitelist": lambda w, cl, tag: [w] if (cl in ("i", "n") or tag == "common") else [],
    "signs": lambda w, cl, tag: (w.split("-") if cl == "w" else [w]),
}


def lb_raw(variant):
    R = _jl(DATA / "lb.jsonl")
    f = LB_KEEP[variant]
    return _fix([dict(id=r["id"], site=r["site"], group=r["group"], series=r["series"],
                      lines=[[x for w, cl, tag in r["toks"] for x in f(w, cl, tag)]]) for r in R])


def lb_series_balanced(texts):
    """Keep, for each Bennett series letter, the same number of tablets at both sites (the smaller count;
    tablets chosen by a fixed hash of their id). Pre-processing only: draw and score are unchanged."""
    ser = {r["group"]: r["series"][0] for r in _jl(DATA / "lb.jsonl")}
    tabs = {}
    for t in texts:
        tabs.setdefault((t["site"], ser[t["group"]]), set()).add(t["group"])
    keep = set()
    for L in {k[1] for k in tabs}:
        a, b = tabs.get(("Knossos", L), set()), tabs.get(("Pylos", L), set())
        m = min(len(a), len(b))
        for s in (a, b):
            keep |= set(sorted(s, key=lambda g: zlib.crc32(g.encode()))[:m])
    return [t for t in texts if t["group"] in keep]


def lb_pool(variant, frame=False, balanced=False):
    T = lb_raw(variant)
    if balanced:
        T = lb_series_balanced(T)
    T = ub.clean(T)
    if frame:
        T, _ = ub.strip_frame(T)
        T = ub.clean(T)
    return T


# =========================================================================== B  name-free references
UR3_PAIRS = {"ug": ("Umma", "Girsu"), "pn": ("Puzriš-Dagan", "Nippur")}
NAME_DET = re.compile(r"\{(d|ki|iri|uru|kur|m|f|disz|1)\}")


def ur3_proper(form, pos):
    """Proper noun by ORACC part of speech (PN, RN, DN, SN, GN, FN, WN, TN, MN, AN ... any *N except N),
    unknown / unlemmatised (X, u, ?), or a name determinative in the form."""
    return (pos.endswith("N") and pos != "N") or pos in ("X", "u", "?") or bool(NAME_DET.search(form))


def ur3_pool(pair, owner=True, frame=False):
    a, b = UR3_PAIRS[pair]
    R = [r for r in _jl(DATA / "ur3pos.jsonl") if r["site"] in (a, b)]
    T = [dict(id=r["id"], site=r["site"], group=r["group"], lines=r["lines"]) for r in R]
    if owner:  # rt.ur3_owner_dedup on the full forms (first line), before names are removed
        full = [dict(t, lines=[[w for w, _ in l] for l in t["lines"]]) for t in T]
        ids = {t["id"] for t in rt.ur3_owner_dedup(full)}
        T = [t for t in T if t["id"] in ids]
    T = _fix([dict(t, lines=[[w for w, p in l if not ur3_proper(w, p)] for l in t["lines"]]) for t in T])
    T = ub.clean(T)
    if frame:
        T, _ = ub.strip_frame(T)
        T = ub.clean(T)
    return T


def lat_pool(namefree=True, civil=False, frame=False):
    R = _jl(DATA / "lattr.jsonl")
    T = [dict(id=r["id"], site=r["site"], group=r["group"], lines=[[w for w, _ in l] for l in r["lines"]],
              flags=r["lines"]) for r in R]
    if civil:
        ok = {t["id"] for t in rt.lat_civil(T)}
        T = [t for t in T if t["id"] in ok]
    if namefree:
        T = [dict(t, lines=[[w for w, f in l if f != "proper"] for l in t["flags"]]) for t in T]
    T = ub.clean(_fix(T))
    if frame:
        T, _ = ub.strip_frame(T)
        T = ub.clean(T)
    return T


def plant_names(sample, form, r, rng, common):
    """Reverse power test. Permute site labels (kill real signal), then give a share r of texts a local
    'name' from its site's own stock of 100 names (Zipf weights, as rt.plant):
      sign   - each name is one new site-specific symbol; it replaces one sign of the text.
      spelt  - each name is a pair of existing common Indus signs (both sites spell from one shared sign
               list, but each has its own names); it replaces two adjacent signs in one line, or the whole
               line if the text is one sign long."""
    sites = [t["site"] for t in sample]
    sites = [sites[i] for i in rng.permutation(len(sites))]
    S = sorted(set(sites))
    w = (1 / np.arange(1, 101)) / (1 / np.arange(1, 101)).sum()
    if form == "sign":
        stock = {s: [[f"{s[:2]}_n{i}"] for i in range(100)] for s in S}
    else:
        stock = {}
        for s in S:
            names = set()
            while len(names) < 100:
                names.add(tuple(rng.choice(common, 2, replace=True)))
            stock[s] = [list(n) for n in sorted(names)]
    out = []
    for t, s in zip(sample, sites):
        L = [list(l) for l in t["lines"]]
        if rng.random() < r:
            nm = stock[s][rng.choice(100, p=w)]
            if form == "sign":
                cand = [(i, j) for i, l in enumerate(L) for j in range(len(l))]
                i, j = cand[rng.integers(len(cand))]
                L[i][j] = nm[0]
            else:
                cand = [(i, j) for i, l in enumerate(L) for j in range(len(l) - 1)]
                if cand:
                    i, j = cand[rng.integers(len(cand))]
                    L[i][j:j + 2] = nm
                else:
                    L[0] = list(nm)
        out.append(dict(t, site=s, lines=L))
    return out


# =========================================================================== C  within-city (M77)
DK = {"31", "32", "33", "34"}
HRVS = {"16", "17", "18", "20", "22"}
HA_F = {"40", "41", "42", "43", "44", "45"}
HA_AB = {"46", "47", "48", "49"}


def m77_meta():
    M = {}
    for x in _jl(ROOT / "data/m77_lines.jsonl"):
        M.setdefault(x["text_no"], (x["locus"], x["level"]))
    return M


def m77_seals(label):
    """M77 seal texts (complete, no break mark), each object side one text, as rt.m77_pool; label(site,
    locus, level) -> side name or None."""
    meta = m77_meta()
    out = []
    for t in m77_texts():
        if t["object_type"] != "seal" or "#" in t["seq"] or not t.get("complete"):
            continue
        loc, lev = meta.get(t["text_no"], (None, None))
        s = label(t["site"], loc, lev)
        if s is None:
            continue
        L, cur = [], []
        for x in t["seq"]:
            if x == "|":
                if cur:
                    L.append(cur)
                cur = []
            else:
                cur.append(x)
        if cur:
            L.append(cur)
        if L:
            i = f"m{t['text_no']}.{t['side']}"
            out.append(dict(id=i, site=s, lines=L, group=i))
    return out


def lab_area(site, loc, lev):
    if site != "Mohenjodaro":
        return None
    return "DK" if loc in DK else ("HRVS" if loc in HRVS else None)


def dk_median():
    meta = m77_meta()
    lv = [int(lev) for t in m77_texts() if t["object_type"] == "seal" and t["site"] == "Mohenjodaro"
          for loc, lev in [meta.get(t["text_no"], (None, None))]
          if loc in DK and lev not in (None, "", "0") and re.fullmatch(r"-?\d+", lev)]
    return float(np.median(lv))


def lab_depth(site, loc, lev, _m=[None]):
    if site != "Mohenjodaro" or loc not in DK or lev in (None, "", "0") or not re.fullmatch(r"-?\d+", lev or ""):
        return None
    if _m[0] is None:
        _m[0] = dk_median()
    return "deep" if int(lev) <= _m[0] else "shallow"


def lab_mound(site, loc, lev):
    if site != "Harappa":
        return None
    return "F" if loc in HA_F else ("AB" if loc in HA_AB else None)


def lab_city(site, loc, lev):
    return {"Mohenjodaro": MD, "Harappa": HA}.get(site)


def icit_area_pool():
    """ICIT seals of Mohenjo-daro with an excavation area from the CISI field number (DK vs HR/VS)."""
    pre = {}
    for r in csv.DictReader(open(ROOT / "experiments/old_registers/cisi_basic.csv")):
        m = re.match(r"\s*([A-Z]{1,3})\s*\d", r.get("field_no") or "")
        if r["cisi"].startswith("M-") and m:
            pre[r["cisi"]] = m.group(1)
    out = [t for t in rt.icit_seal_pool() if t["site"] == MD]
    from corpus.load import icit_texts
    cis = {t["id"]: t["cisi"] for t in icit_texts()}
    res = []
    for t in out:
        p = pre.get(cis.get(t["id"]))
        s = "DK" if p == "DK" else ("HRVS" if p in ("HR", "VS") else None)
        if s:
            res.append(dict(t, site=s))
    return res


# =========================================================================== conditions
def conditions():
    """name -> (part, builder, a, b, n_side or None (= min(avail, 227)), one_per_group, plant)
    plant: None | ("gate", q) | ("name", form, r)."""
    C = {}
    K, P = "Knossos", "Pylos"
    # ---- A: Linear B
    C["A1_lb_whole"] = ("A", lambda: lb_pool("whole"), K, P, None, True, None)
    C["A2_lb_frame"] = ("A", lambda: lb_pool("whole", frame=True), K, P, None, True, None)
    C["A3_lb_syll"] = ("A", lambda: lb_pool("syll"), K, P, None, True, None)
    C["A4_lb_ideo"] = ("A", lambda: lb_pool("ideo"), K, P, None, True, None)
    C["A5_lb_nonames"] = ("A", lambda: lb_pool("nonames"), K, P, None, True, None)
    C["A6_lb_syll_nonames"] = ("A", lambda: lb_pool("syll_nonames"), K, P, None, True, None)
    C["A7_lb_whitelist"] = ("A", lambda: lb_pool("whitelist"), K, P, None, True, None)
    C["A8_lb_series_bal"] = ("A", lambda: lb_pool("whole", balanced=True), K, P, None, True, None)
    C["A9_lb_signs"] = ("A", lambda: lb_pool("signs"), K, P, None, True, None)
    C["A10_lb_whitelist_series_bal"] = ("A", lambda: lb_pool("whitelist", balanced=True), K, P, None, True, None)
    # ---- B: name-free references
    for pr, (a, b) in UR3_PAIRS.items():
        C[f"B1_ur3_{pr}_namefree"] = ("B", lambda pr=pr: ur3_pool(pr, owner=False), a, b, None, False, None)
        C[f"B2_ur3_{pr}_namefree_owner"] = ("B", lambda pr=pr: ur3_pool(pr, owner=True), a, b, None, False, None)
        C[f"B3_ur3_{pr}_namefree_owner_frame"] = ("B", lambda pr=pr: ur3_pool(pr, owner=True, frame=True), a, b, None, False, None)
    Br, Ge = "Britannia", "Germania"
    C["B4_lat_tr_whole"] = ("B", lambda: lat_pool(namefree=False), Br, Ge, None, False, None)
    C["B5_lat_namefree"] = ("B", lambda: lat_pool(), Br, Ge, None, False, None)
    C["B6_lat_namefree_civil"] = ("B", lambda: lat_pool(civil=True), Br, Ge, None, False, None)
    C["B7_lat_namefree_frame"] = ("B", lambda: lat_pool(frame=True), Br, Ge, None, False, None)
    icit = lambda: ub.clean([t for t in rt.icit_seal_pool() if t["site"] in (MD, HA)])
    for form in ("sign", "spelt"):
        for r in NAME_RATES:
            C[f"BW_name_{form}_r{r}"] = ("B", icit, MD, HA, N_MAX, False, ("name", form, r))
    # ---- C: within-city floor (M77) and between-city controls at matched size
    C["C1_m77_MD_DK_vs_HRVS"] = ("C", lambda: ub.clean(m77_seals(lab_area)), "DK", "HRVS", None, False, None)
    C["C2_m77_MD_DK_deep_vs_shallow"] = ("C", lambda: ub.clean(m77_seals(lab_depth)), "deep", "shallow", None, False, None)
    C["C3_m77_H_F_vs_AB"] = ("C", lambda: ub.clean(m77_seals(lab_mound)), "F", "AB", None, False, None)
    C["C4_m77_MD_vs_H_at_C1"] = ("C", lambda: ub.clean(m77_seals(lab_city)), MD, HA, "C1_m77_MD_DK_vs_HRVS", False, None)
    C["C5_m77_MD_vs_H_at_C3"] = ("C", lambda: ub.clean(m77_seals(lab_city)), MD, HA, "C3_m77_H_F_vs_AB", False, None)
    C["C6_icit_MD_DK_vs_HRVS"] = ("C", lambda: ub.clean(icit_area_pool()), "DK", "HRVS", None, False, None)
    C["C7_icit_MD_vs_H_227"] = ("C", icit, MD, HA, N_MAX, False, None)
    C["C8_m77_MD_vs_H_at_C2"] = ("C", lambda: ub.clean(m77_seals(lab_city)), MD, HA, "C2_m77_MD_DK_deep_vs_shallow", False, None)
    # ---- planted-answer power gates (same pool and size as the condition, labels permuted, q = 0.15)
    for g in ("A1_lb_whole", "A7_lb_whitelist", "A8_lb_series_bal", "B2_ur3_ug_namefree_owner",
              "B2_ur3_pn_namefree_owner", "B5_lat_namefree", "C1_m77_MD_DK_vs_HRVS",
              "C2_m77_MD_DK_deep_vs_shallow", "C3_m77_H_F_vs_AB", "C7_icit_MD_vs_H_227"):
        part, build, a, b, n, opg, _ = C[g]
        C["G_" + g] = (part, build, a, b, g, opg, ("gate", GATE_Q))
    return C


# =========================================================================== modes
_BUILT = {}


def built(name, C):
    if name not in _BUILT:
        _BUILT[name] = C[name][1]()
    return _BUILT[name]


def n_side_of(name, C):
    part, build, a, b, n, opg, pl = C[name]
    if isinstance(n, int):
        return n
    if isinstance(n, str):            # size borrowed from another condition
        return n_side_of(n, C)
    T = built(name, C)
    if opg:   # one text per group (tablet): the cap is the number of tablets
        c = Counter(s for s, g in {(t["site"], t["group"]) for t in T})
    else:
        c = Counter(t["site"] for t in T)
    return min(c[a], c[b], N_MAX)


def sizes():
    C = conditions()
    for name, (part, build, a, b, n, opg, pl) in C.items():
        if name.startswith("BW_") and not name.endswith("r0.1"):
            continue
        T = built(name, C)
        c = Counter(t["site"] for t in T)
        ng = {s: len({t["group"] for t in T if t["site"] == s}) for s in (a, b)}
        lm = {s: round(float(np.mean([sum(len(l) for l in t["lines"]) for t in T if t["site"] == s] or [0])), 2) for s in (a, b)}
        print(f"{part} {name:40s} {a}={c[a]} {b}={c[b]} groups={ng} mean_len={lm} n_side={n_side_of(name, C)}", flush=True)
    print("DK depth median (ft):", dk_median())
    print("Proto-Elamite: see RESULTS.md (22 transliterated non-Susa tablets with a secure findspot; not run)")


def run(only=None):
    C = conditions()
    path = HERE / "draws.jsonl"
    done = Counter()
    if path.exists():
        for l in open(path):
            done[json.loads(l)["cond"]] += 1
    common = None
    with open(path, "a") as f:
        for name, (part, build, a, b, n, opg, pl) in C.items():
            if only and not any(name.startswith(o) for o in only):
                continue
            if done[name] >= N_DRAWS:
                continue
            T = built(name, C)
            c = Counter(t["site"] for t in T)
            n_side = n_side_of(name, C)
            if pl:
                freq = Counter(w for t in T for l in t["lines"] for w in l)
                common = sorted(s for s, k in freq.items() if k >= 5)
            rec = {}
            for k in range(done[name], N_DRAWS):
                rng = np.random.default_rng([SEED, k, zlib.crc32(name.encode())])
                smp, short = ub.draw_n(T, a, b, rng, MIX, opg, n_side, 2 * n_side)
                if smp is None:
                    rec = dict(cond=name, part=part, draw=k, auc=None, n_side=n_side, avail=[c[a], c[b]])
                else:
                    if pl and pl[0] == "gate":
                        smp = rt.plant(smp, "new100", pl[1], rng, common)
                    elif pl and pl[0] == "name":
                        smp = plant_names(smp, pl[1], pl[2], rng, common)
                    obs, nul, nf, nn = ub.score(smp, a, SEED + k)
                    rec = dict(cond=name, part=part, draw=k, auc=obs, null_auc=nul, n_feat=nf, n=nn, n_side=n_side,
                               short=short, avail=[c[a], c[b]], **rt.describe(smp, a))
                f.write(json.dumps(rec) + "\n"); f.flush()
            print(name, "done", rec.get("auc"), flush=True)


def report():
    C = conditions()
    R = [json.loads(l) for l in open(HERE / "draws.jsonl")]
    by = {}
    for r in R:
        by.setdefault(r["cond"], []).append(r)
    out = {}
    for name in C:
        rs = by.get(name, [])
        ok = [r for r in rs if r["auc"] is not None]
        if not rs:
            continue
        if not ok:
            out[name] = dict(part=rs[0]["part"], failed=len(rs), n_side=rs[0]["n_side"], avail=rs[0].get("avail"))
            continue
        a = np.array([r["auc"] for r in ok]); nu = np.array([r["null_auc"] for r in ok])
        d = dict(part=ok[0]["part"], n_side=ok[0]["n_side"], n_draws=len(ok), failed=len(rs) - len(ok),
                 median_auc=float(np.median(a)), lo=float(np.quantile(a, 0.025)), hi=float(np.quantile(a, 0.975)),
                 null_mean=float(nu.mean()), null_q95=float(np.quantile(nu, 0.95)),
                 p_own_null=float((1 + np.sum(nu >= np.median(a))) / (1 + len(nu))),
                 share_ge_065=float(np.mean(a >= 0.65)), avail=ok[0]["avail"])
        for k in ("types", "ttr", "local_share", "mean_len", "n_feat"):
            d[k] = float(np.mean([r[k] for r in ok]))
        d["_aucs"] = a.tolist()
        out[name] = d
    # detection: AUC >= max(0.65, null q95 of the matching unplanted condition)
    for name, (part, build, a, b, n, opg, pl) in C.items():
        if not pl or name not in out or "_aucs" not in out[name]:
            continue
        base = name[2:] if pl[0] == "gate" else "C7_icit_MD_vs_H_227"
        thr = max(0.65, out.get(base, {}).get("null_q95", 0.0))
        out[name]["detect_thr"] = thr
        out[name]["detect_rate"] = float(np.mean(np.array(out[name]["_aucs"]) >= thr))
        if pl[0] == "gate" and base in out:
            out[base]["gate_detect_rate"] = out[name]["detect_rate"]
            out[base]["gate_pass"] = out[name]["detect_rate"] >= 0.8
    # reverse power summary
    obs = out.get("C7_icit_MD_vs_H_227", {}).get("median_auc")
    rev = {}
    for form in ("sign", "spelt"):
        rows = [(r, out.get(f"BW_name_{form}_r{r}")) for r in NAME_RATES]
        rows = [(r, d) for r, d in rows if d and "detect_rate" in d]
        p80 = next((r for r, d in rows if d["detect_rate"] >= 0.8), None)
        compat = [r for r, d in rows if obs is not None and d["lo"] <= obs <= d["hi"]]
        rev[form] = dict(rate_80pct_power=p80, max_rate_compatible_with_obs=max(compat) if compat else 0.0,
                         observed=obs, curve={str(r): dict(median=d["median_auc"], detect=d["detect_rate"],
                                                           local_share=d["local_share"]) for r, d in rows})
    for d in out.values():
        d.pop("_aucs", None)
    out["_reverse_power"] = rev
    lib.jdump(out, HERE / "results.json")
    lines = ["| part | condition | n per side | median AUC | 2.5-97.5% | null q95 | p (own null) | share >= 0.65 | gate (q 0.15) | types | local share | mean len |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for name in C:
        d = out.get(name)
        if not d:
            continue
        if "median_auc" not in d:
            lines.append(f"| {d['part']} | {name} | {d['n_side']} | failed (avail {d.get('avail')}) | | | | | | | | |")
            continue
        g = d.get("gate_detect_rate"); dr = d.get("detect_rate")
        gs = f"{g:.0%}" if g is not None else (f"detect {dr:.0%}" if dr is not None else "")
        lines.append(f"| {d['part']} | {name} | {d['n_side']} | {d['median_auc']:.3f} | {d['lo']:.3f}-{d['hi']:.3f} | "
                     f"{d['null_q95']:.3f} | {d['p_own_null']:.3f} | {d['share_ge_065']:.0%} | {gs} | {d['types']:.0f} | "
                     f"{d['local_share']:.3f} | {d['mean_len']:.1f} |")
    (HERE / "table.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(json.dumps(rev, indent=1))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "sizes"
    if mode == "run":
        run(sys.argv[2:] or None)
    else:
        {"sizes": sizes, "report": report}[mode]()
