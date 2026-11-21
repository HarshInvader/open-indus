"""Red team of uniformity paper step 2 (prereg docs/prereg/redteam_uniformity_step2.md).

Every scored condition goes through the benchmark's own clean() + draw_n() + score()
(experiments/uniformity_benchmark/run.py), with pools from step-2 s2.py / step-1 s1.py. No new classifier.
corpus/build.py::_close is not used; de-duplication is clean() (fish_tick_closer_v2/dedup.py greedy), and the
strict sealing de-dup calls the same dedup.greedy with MIN_DROP = 2.

  A1  name tagging audit (seeded samples, hand-judged in audit.csv) + strict / loose name stripping, scored
  A2  which part of the names carries place: toponyms + gods (+ theophoric names) vs personal names;
      Latin unit words + numerals vs personal names
  A3  Indus analog: site-specific names planted into MD vs Harappa seals (real labels) at rates up to the
      Ur III name share; largest share still consistent with the observed gap
  A4  floor bias: every step-2 gap re-read against the shuffled-label null and a conservative reference
      (no new draws; step-2 draws.jsonl)
  A5  sealings: strict de-dup, seal-vs-sealing cross-object test, Harappa mound floor; tablets subtype-matched

  board/run.sh .venv/bin/python -I experiments/redteam_uniformity_step2/rt2.py sizes
  .venv/bin/python -I experiments/redteam_uniformity_step2/rt2.py audit      # writes audit_sample.csv
  board/run.sh .venv/bin/python -I experiments/redteam_uniformity_step2/rt2.py run
  .venv/bin/python -I experiments/redteam_uniformity_step2/rt2.py report
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
ROOT = HERE.parents[1]
S2DIR = ROOT / "experiments/uniformity_paper/step2"
sys.path.insert(0, str(S2DIR))
import s2  # noqa: E402  step-2 pools (imports s1, rt1, ub, rt, lib)

s1, rt, ub, lib = s2.s1, s2.rt, s2.ub, s2.lib
dedup = ub.dedup

N_DRAWS = 50
SEED = 20261127
AUDIT_SEED = 20261126
N_MAX = 227
MIX = s2.MIX
MARGIN = 0.05
GATE_Q = 0.15
MD, HA = s2.MD, s2.HA
RATES = (0.05, 0.10, 0.20, 0.30, 0.50, 0.75, 1.0)
FORMS = ("sign", "spelt", "ur3emp")
IFAMS = ("m77_seal", "icit_seal", "icit_sealtype")


def _jl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8")]


_C = {}


def cache(k, f):
    if k not in _C:
        _C[k] = f()
    return _C[k]


# =========================================================================== A1/A2 Ur III token classes
NONPN_PROPER = lambda p: p.endswith("N") and p not in ("N", "PN", "RN")   # SN GN DN TN WN FN AN MN ...
PLACE_DET = re.compile(r"\{(ki|iri|uru|kur)\}")
KIN = {"dumu", "dam", "šeš", "dumu-munus", "arad₂", "geme₂"}


def ever_proper():
    def f():
        E = set()
        for fn in (s1.DATA / "ur3pos.jsonl", S2DIR / "data/obpos.jsonl"):
            for r in _jl(fn):
                for l in r["lines"]:
                    for w, p in l:
                        if s1.ur3_proper(w, p) and not s1.NAME_DET.search(w):
                            E.add(w)
        return E
    return cache("ever", f)


def ur3_line(variant):
    """line [[form, pos], ...] -> kept forms."""
    main = s1.ur3_proper
    preds = {
        "whole": lambda w, p: False,
        "namefree": main,                                                   # step-2 rule
        "loose": lambda w, p: p.endswith("N") and p != "N",                  # POS only; unknowns + det forms kept
        "noTG": lambda w, p: NONPN_PROPER(p) or bool(PLACE_DET.search(w)) or ("{d}" in w and p not in ("PN", "RN")),
        "noTGtheo": lambda w, p: (NONPN_PROPER(p) or bool(PLACE_DET.search(w))
                                  or ("{d}" in w and p not in ("PN", "RN")) or (p == "PN" and "{d}" in w)),
        "noPN": lambda w, p: p == "PN" or p in ("X", "u", "?"),
    }
    if variant == "strict":
        E = ever_proper()

        def f(l):
            out, prev = [], None
            for w, p in l:
                if not (main(w, p) or w in E or "{" in w or prev in KIN):
                    out.append(w)
                prev = w
            return out
        return f
    pr = preds[variant]
    return lambda l: [w for w, p in l if not pr(w, p)]


def ur3_pool(rows, variant, city=None, split=None, splits=None):
    fl = ur3_line(variant)
    T = []
    for r in rows:
        if city is None:
            if r["site"] not in ("Umma", "Girsu"):
                continue
            s = r["site"]
        else:
            if r["site"] != city:
                continue
            s = splits[split][1](r)
            if s is None:
                continue
        T.append(dict(id=r["id"], site=s, group=r["group"], lines=[fl(l) for l in r["lines"]]))
    return ub.clean(s1._fix(T))


# ---------------------------------------------------------------- Latin token classes
LAT_UNITWORDS = {"LEGIO", "LEGIONIS", "COHORS", "COHORTIS", "ALAE", "CLASSIS", "VEXILLATIO", "NUMERI"}


def lat_unit(w, f):
    return f == "num" or bool(rt.MIL.match(w)) or w in LAT_UNITWORDS


LAT_PRED = {
    "whole": lambda w, f: False,
    "namefree": lambda w, f: f == "proper",
    "loose": lambda w, f: f == "proper" and len(w) >= 3,
    "strict": lambda w, f: f == "proper" or lat_unit(w, f) or len(w) <= 2,
    "noUNIT": lambda w, f: lat_unit(w, f),
    "noPN": lambda w, f: f == "proper" and not lat_unit(w, f),
}


def lat_pool(variant, split=None):
    ids = s2.lat_ids()
    pr = LAT_PRED[variant]
    T = []
    for r in s2.lat_rows():
        if r["id"] not in ids:
            continue
        if split is None:
            s = r["site"]
        else:
            prov, f = s2.LAT_SPLITS[split]
            if r["site"] != prov:
                continue
            s = s2.half(r["id"]) if f == "random" else f(r.get("region", ""))
            if s is None:
                continue
        T.append(dict(id=r["id"], site=s, group=r["group"], lines=[[w for w, fl in l if not pr(w, fl)] for l in r["lines"]]))
    return ub.clean(s1._fix(T))


# =========================================================================== A3 Indus planted names
def ur3_pn_stock():
    """Empirical personal-name frequencies (POS PN) per city in the raw Ur III seal legends."""
    def f():
        st = {"Umma": Counter(), "Girsu": Counter()}
        for r in s2.ur3_rows():
            if r["site"] in st:
                for l in r["lines"]:
                    for w, p in l:
                        if p == "PN":
                            st[r["site"]][w] += 1
        return st
    return cache("pnstock", f)


def ur3_name_share():
    """Share of raw Umma + Girsu legends with >= 1 PN token; PN tokens per legend; PN share of tokens."""
    R = [r for r in s2.ur3_rows() if r["site"] in ("Umma", "Girsu")]
    has = [any(p == "PN" for l in r["lines"] for w, p in l) for r in R]
    npn = [sum(p == "PN" for l in r["lines"] for w, p in l) for r in R]
    ntok = [sum(len(l) for l in r["lines"]) for r in R]
    C = s2.between_pool(s2.ur3_rows(), "Umma", "Girsu", "whole")
    ids = {t["id"] for t in C}
    hasC = [h for r, h in zip(R, has) if r["id"] in ids]
    return dict(n=len(R), share_any_pn=float(np.mean(has)), pn_per_legend=float(np.mean(npn)),
                pn_token_share=float(sum(npn) / sum(ntok)), n_clean=len(hasC), share_any_pn_clean=float(np.mean(hasC)))


def plant_names_real(sample, form, r, rng, common, a):
    """s1.plant_names without the label permutation (real labels kept), plus 'ur3emp': each planted name is
    drawn from the real Ur III personal-name frequencies of one city (Umma -> site a, Girsu -> the other) and
    spelt as a fixed pair of common signs (one mapping per draw, shared by both sites, so names the two
    cities share stay shared)."""
    S = sorted({t["site"] for t in sample})
    w = (1 / np.arange(1, 101)) / (1 / np.arange(1, 101)).sum()
    if form == "sign":
        stock = {s: [[f"{s[:2]}_n{i}"] for i in range(100)] for s in S}
    elif form == "spelt":
        stock = {}
        for s in S:
            names = set()
            while len(names) < 100:
                names.add(tuple(rng.choice(common, 2, replace=True)))
            stock[s] = [list(n) for n in sorted(names)]
    else:
        st = ur3_pn_stock()
        forms = sorted(set(st["Umma"]) | set(st["Girsu"]))
        pairs = rng.choice(common, (len(forms), 2), replace=True)
        spell = {f: [str(x) for x in pr] for f, pr in zip(forms, pairs)}
        emp = {}
        for s in S:
            c = st["Umma"] if s == a else st["Girsu"]
            ks = sorted(c)
            pw = np.array([c[k] for k in ks], float)
            emp[s] = (ks, pw / pw.sum())
    out = []
    for t in sample:
        s = t["site"]
        L = [list(l) for l in t["lines"]]
        if rng.random() < r:
            if form == "ur3emp":
                ks, pw = emp[s]
                nm = spell[ks[rng.choice(len(ks), p=pw)]]
            else:
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
        out.append(dict(t, lines=L))
    return out


# =========================================================================== A5 sealings / tablets
def strict_clean(T):
    """clean(), then dedup.greedy again with MIN_DROP = 2 (texts of >= 2 signs within one edit of / contained
    in a kept text are dropped), then one text per sign multiset (multisets found at both sides dropped)."""
    K = ub.clean(T)
    old = dedup.MIN_DROP
    dedup.MIN_DROP = 2
    try:
        K = dedup.greedy(K)
    finally:
        dedup.MIN_DROP = old
    key = lambda t: tuple(sorted(w for l in t["lines"] for w in l))
    sides = {}
    for t in K:
        sides.setdefault(key(t), set()).add(t["site"])
    seen, out = set(), []
    for t in sorted(K, key=lambda t: t["id"]):
        k = key(t)
        if len(sides[k]) > 1 or k in seen:
            continue
        seen.add(k); out.append(t)
    return out


def dup_profile(fam):
    """Raw complete texts, distinct strings, after clean(), after strict_clean(); largest identical-string cluster."""
    R = s2.indus_raw(fam)
    out = {}
    for s in (MD, HA):
        X = [x for x in R if x["site"] == s]
        strs = Counter(" ".join(w for l in x["lines"] for w in l) for x in X)
        out[s] = dict(raw=len(X), distinct=len(strs), largest_cluster=max(strs.values()) if strs else 0,
                      top5=[c for _, c in strs.most_common(5)])
    T = s2.indus_between(fam, MD, HA)
    S = strict_clean([x for x in s2.indus_raw(fam) if x["site"] in (MD, HA)])
    out["clean"] = dict(Counter(t["site"] for t in T))
    out["strict"] = dict(Counter(t["site"] for t in S))
    return out


def cross_pool(ed, sealing_site, seal_site):
    """Sealings of one city (side 'sealing') vs seals of one city (side 'seal'), through clean()."""
    sl = s2.indus_raw(f"{ed}_sealing"); se = s2.indus_raw(f"{ed}_seal")
    T = ([dict(x, site="sealing") for x in sl if x["site"] == sealing_site] +
         [dict(x, site="seal") for x in se if x["site"] == seal_site])
    return ub.clean(T)


def m77_sealing_mound():
    meta = s1.m77_meta()
    def f():
        out = []
        for t in s2.m77_texts():
            if t["object_type"] != "sealing" or t["site"] != "Harappa" or "#" in t["seq"] or not t.get("complete"):
                continue
            loc, _ = meta.get(t["text_no"], (None, None))
            s = "F" if loc in s1.HA_F else ("AB" if loc in s1.HA_AB else None)
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
        return ub.clean(out)
    return cache("mound", f)


def icit_tab(types):
    def f():
        out = []
        for t in s2.icit_texts():
            if (t["type"] or "") not in types or t["site"] not in (MD, HA) or "#" in t["seq"] or not t["complete"]:
                continue
            L = [list(seg) for seg in t["segments"] if seg]
            if L:
                out.append(dict(id=t["id"], site=t["site"], lines=L, group=t["id"]))
        return out
    return cache("tab" + "".join(types), f)


# =========================================================================== conditions
def conditions():
    C = {}

    def add(name, build, a, b, n=None, plant=None, **info):
        C[name] = dict(build=build, a=a, b=b, n=n, plant=plant, info=info)

    def trio(key, wbuild, wa, wb, bbuild, ba, bb, n=None, gate=True, **info):
        nn = n if n is not None else ("match", f"W_{key}", f"B_{key}")
        add(f"W_{key}", wbuild, wa, wb, n=nn, role="within", **info)
        add(f"B_{key}", bbuild, ba, bb, n=nn, role="between", **info)
        if gate:
            add(f"G_{key}", bbuild, ba, bb, n=f"B_{key}", plant=("gate", GATE_Q), role="gate", **info)

    # ---------------- A1 / A2 Ur III (ORACC, CDLI)
    for corp, rows, splits, sps in (("ur3", s2.ur3_rows, s2.UR3_SPLITS, ("U_reign", "U_coll", "G_reign", "G_coll")),
                                    ("cdli", s2.cdli_rows, s2.CDLI_SPLITS, ("U_reign", "G_reign"))):
        for v in ("loose", "strict", "noTG", "noTGtheo", "noPN"):
            for sp in sps:
                city = splits[sp][0]
                trio(f"{corp}_{v}_{sp}",
                     lambda rows=rows, v=v, city=city, sp=sp, splits=splits: ur3_pool(rows(), v, city, sp, splits),
                     *s2.split_sides(sp),
                     lambda rows=rows, v=v: ur3_pool(rows(), v), "Umma", "Girsu",
                     attack="A1" if v in ("loose", "strict") else "A2", corpus=corp, variant=v, split=sp)
    # size control: whole legends at the name-free matched size (ORACC, reign splits)
    for sp in ("U_reign", "G_reign"):
        city = s2.UR3_SPLITS[sp][0]
        add(f"S_nfW_{sp}", lambda city=city, sp=sp: ur3_pool(s2.ur3_rows(), "namefree", city, sp, s2.UR3_SPLITS),
            *s2.split_sides(sp), role="size_only")
        add(f"S_nfB_{sp}", lambda: ur3_pool(s2.ur3_rows(), "namefree"), "Umma", "Girsu", role="size_only")
        trio(f"ur3_wholeAtNF_{sp}", lambda city=city, sp=sp: ur3_pool(s2.ur3_rows(), "whole", city, sp, s2.UR3_SPLITS),
             *s2.split_sides(sp), lambda: ur3_pool(s2.ur3_rows(), "whole"), "Umma", "Girsu",
             n=("match", f"S_nfW_{sp}", f"S_nfB_{sp}"), attack="A1", corpus="ur3", variant="wholeAtNF", split=sp)
    # ---------------- A1 / A2 Latin
    for v in ("loose", "strict", "noUNIT", "noPN"):
        for sp in ("ge_rlp_vs_bwhe", "br_north_vs_south"):
            trio(f"lat_{v}_{sp}", lambda v=v, sp=sp: lat_pool(v, sp), "X", "Y",
                 lambda v=v: lat_pool(v), "Britannia", "Germania",
                 attack="A1" if v in ("loose", "strict") else "A2", corpus="lat", variant=v, split=sp)
    # ---------------- A3 Indus planted names (real labels), n = step-2 IB n
    for fam in IFAMS:
        a, b = s2.pair_order(fam, MD, HA)
        for form in FORMS:
            for r in RATES:
                add(f"P_{fam}_{form}_{r}", lambda fam=fam, a=a, b=b: s2.indus_between(fam, a, b), a, b,
                    n=("step2", f"IB_{fam}|{a}|{b}"), plant=("names", form, r), role="plant", attack="A3",
                    family=fam, form=form, rate=r)
    # ---------------- A5 sealings
    for ed in ("icit", "m77"):
        fam = f"{ed}_sealing"
        a, b = s2.pair_order(fam, MD, HA)
        add(f"W_strict_{ed}", lambda fam=fam, a=a: strict_clean([dict(x, site=s2.half(x["id"])) for x in s2.indus_raw(fam)
                                                                 if x["site"] == a]), "X", "Y",
            n=("match", f"W_strict_{ed}", f"B_strict_{ed}"), role="within", attack="A5", family=fam)
        add(f"B_strict_{ed}", lambda fam=fam, a=a, b=b: strict_clean([x for x in s2.indus_raw(fam) if x["site"] in (a, b)]),
            a, b, n=("match", f"W_strict_{ed}", f"B_strict_{ed}"), role="between", attack="A5", family=fam)
        add(f"PW_strict_{ed}", lambda fam=fam, a=a, b=b: strict_clean([x for x in s2.indus_raw(fam) if x["site"] in (a, b)]),
            a, b, n=f"B_strict_{ed}", plant=("side", b, GATE_Q), role="power", attack="A5", family=fam)
        xs = {"X1": (HA, MD), "X2": (HA, HA), "X3": (MD, HA), "X4": (MD, MD)}
        for k, (sl, se) in xs.items():
            add(f"X_{ed}_{k}", lambda ed=ed, sl=sl, se=se: cross_pool(ed, sl, se), "sealing", "seal",
                n=("min", [f"X_{ed}_{j}" for j in xs]), role="cross", attack="A5", family=ed, cross=k)
            if k in ("X1", "X3"):
                add(f"GX_{ed}_{k}", lambda ed=ed, sl=sl, se=se: cross_pool(ed, sl, se), "sealing", "seal",
                    n=f"X_{ed}_{k}", plant=("gate", GATE_Q), role="gate", attack="A5", family=ed, cross=k)
    add("W_mound_m77", m77_sealing_mound, "F", "AB", n=("match", "W_mound_m77", "B_mound_m77"), role="within",
        attack="A5", family="m77_sealing")
    add("B_mound_m77", lambda: s2.indus_between("m77_sealing", HA, MD), HA, MD,
        n=("match", "W_mound_m77", "B_mound_m77"), role="between", attack="A5", family="m77_sealing")
    add("G_mound_m77", lambda: s2.indus_between("m77_sealing", HA, MD), HA, MD, n="B_mound_m77",
        plant=("side", MD, GATE_Q), role="power", attack="A5", family="m77_sealing")
    # tablets, subtype-matched (larger site a = Harappa; floor = Harappa random halves)
    for key, types in (("moulded", ("TAB:B",)), ("noncopper", ("TAB:B", "TAB:I"))):
        add(f"W_tab_{key}", lambda types=types: ub.clean([dict(x, site=s2.half(x["id"])) for x in icit_tab(types)
                                                         if x["site"] == HA]), "X", "Y",
            n=("match", f"W_tab_{key}", f"B_tab_{key}"), role="within", attack="A5", family="tab_" + key)
        add(f"B_tab_{key}", lambda types=types: ub.clean(icit_tab(types)), HA, MD,
            n=("match", f"W_tab_{key}", f"B_tab_{key}"), role="between", attack="A5", family="tab_" + key)
        add(f"PW_tab_{key}", lambda types=types: ub.clean(icit_tab(types)), HA, MD, n=f"B_tab_{key}",
            plant=("side", MD, GATE_Q), role="power", attack="A5", family="tab_" + key)
    return C


# =========================================================================== machinery
_BUILT = {}


def built(name, C):
    if name not in _BUILT:
        _BUILT[name] = C[name]["build"]()
    return _BUILT[name]


def natural_n(name, C):
    c = C[name]
    cnt = Counter(t["site"] for t in built(name, C))
    return min(cnt[c["a"]], cnt[c["b"]], N_MAX)


def step2_results():
    return cache("s2res", lambda: json.load(open(S2DIR / "results.json")))


def n_side_of(name, C):
    n = C[name]["n"]
    if n is None:
        return natural_n(name, C)
    if isinstance(n, int):
        return n
    if isinstance(n, str):
        return n_side_of(n, C)
    if n[0] == "match":
        return min(natural_n(x, C) for x in n[1:])
    if n[0] == "min":
        return min(natural_n(x, C) for x in n[1])
    if n[0] == "step2":
        return step2_results()["conditions"][n[1]]["n_side"]
    raise ValueError(n)


def sizes():
    C = conditions()
    for name, c in C.items():
        if c["info"].get("role") in ("gate", "power", "plant"):
            continue
        cnt = Counter(t["site"] for t in built(name, C))
        print(f"{name:42s} {c['a']}={cnt[c['a']]} {c['b']}={cnt[c['b']]} n_side={n_side_of(name, C)}", flush=True)
    print("ur3 name share", json.dumps(ur3_name_share()))
    for ed in ("icit", "m77"):
        print(ed, "sealing duplication", json.dumps(dup_profile(f"{ed}_sealing")))


def run():
    C = conditions()
    path = HERE / "draws.jsonl"
    done = Counter()
    if path.exists():
        for l in open(path):
            done[json.loads(l)["cond"]] += 1
    with open(path, "a") as f:
        for name, c in C.items():
            if c["info"].get("role") == "size_only" or done[name] >= N_DRAWS:
                continue
            T = built(name, C)
            a, b = c["a"], c["b"]
            cnt = Counter(t["site"] for t in T)
            n_side = n_side_of(name, C)
            common = None
            if c["plant"]:
                freq = Counter(w for t in T for l in t["lines"] for w in l)
                common = sorted(s for s, k in freq.items() if k >= 5)
            rec = {}
            for k in range(done[name], N_DRAWS):
                rng = np.random.default_rng([SEED, k, zlib.crc32(name.encode())])
                smp = None
                if n_side >= 5:
                    smp, short = ub.draw_n(T, a, b, rng, MIX, False, n_side, 2 * n_side)
                if smp is None:
                    rec = dict(cond=name, draw=k, auc=None, n_side=n_side, avail=[cnt[a], cnt[b]])
                else:
                    p = c["plant"]
                    if p and p[0] == "gate":
                        smp = rt.plant(smp, "new100", p[1], rng, common)
                    elif p and p[0] == "side":
                        smp = s2.plant_side(smp, p[1], p[2], rng, common)
                    elif p and p[0] == "names":
                        smp = plant_names_real(smp, p[1], p[2], rng, common, a)
                    obs, nul, nf, nn = ub.score(smp, a, SEED + k)
                    rec = dict(cond=name, draw=k, auc=obs, null_auc=nul, n_feat=nf, n=nn, n_side=n_side,
                               short=short, avail=[cnt[a], cnt[b]], **rt.describe(smp, a))
                f.write(json.dumps(rec) + "\n"); f.flush()
            print(name, "n", n_side, "done", rec.get("auc"), flush=True)


# =========================================================================== audit sample (A1)
def audit():
    """50 kept + 50 removed token occurrences per corpus under the step-2 name-free rule, seeded. Writes
    audit_sample.csv with an empty 'judgement' column for hand labels (name / not_name / unclear)."""
    rng = np.random.default_rng(AUDIT_SEED)
    rows = []

    def take(corpus, occ):
        for kind in ("kept", "removed"):
            X = [o for o in occ if o[0] == kind]
            for i in sorted(rng.choice(len(X), 50, replace=False)):
                k, w, tag, ctx = X[i]
                rows.append(dict(corpus=corpus, status=kind, token=w, tag=tag, context=ctx, judgement="", reason=""))

    for corpus, R in (("ur3_oracc", s2.ur3_rows()), ("ur3_cdli", s2.cdli_rows())):
        occ = []
        for r in sorted(R, key=lambda r: r["id"]):
            if r["site"] not in ("Umma", "Girsu"):
                continue
            ctx = " / ".join(" ".join(w for w, _ in l) for l in r["lines"])
            for l in r["lines"]:
                for w, p in l:
                    occ.append(("removed" if s1.ur3_proper(w, p) else "kept", w, p, ctx))
        take(corpus, occ)
    occ = []
    ids = s2.lat_ids()
    for r in sorted(s2.lat_rows(), key=lambda r: r["id"]):
        if r["id"] not in ids:
            continue
        ctx = " / ".join(" ".join(w for w, _ in l) for l in r["lines"])
        for l in r["lines"]:
            for w, f in l:
                occ.append(("removed" if f == "proper" else "kept", w, f, ctx))
    take("latin", occ)
    with open(HERE / "audit_sample.csv", "w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0]))
        wr.writeheader(); wr.writerows(rows)
    print(len(rows), "rows written")


# =========================================================================== report
def bh(ps):
    return s2.bh(ps)


def summ(rs):
    ok = [r for r in rs if r["auc"] is not None]
    if not ok:
        return dict(failed=len(rs), n_side=rs[0]["n_side"] if rs else None)
    a = np.array([r["auc"] for r in ok]); nu = np.array([r["null_auc"] for r in ok])
    return dict(n_side=ok[0]["n_side"], n_draws=len(ok), failed=len(rs) - len(ok), avail=ok[0]["avail"],
                median=float(np.median(a)), lo=float(np.quantile(a, 0.025)), hi=float(np.quantile(a, 0.975)),
                null_med=float(np.median(nu)), null_q95=float(np.quantile(nu, 0.95)),
                p_chance=float((1 + np.sum(nu >= np.median(a))) / (1 + len(nu))),
                local_share=float(np.mean([r["local_share"] for r in ok])), _a=a, _n=nu)


def load(path):
    by = {}
    for l in open(path):
        r = json.loads(l); by.setdefault(r["cond"], []).append(r)
    return {k: summ(v) for k, v in by.items()}


def pfloor(S, w, b):
    return float((1 + np.sum(S[w]["_a"] >= S[b]["median"])) / (1 + len(S[w]["_a"])))


def gate_of(S, g, b):
    if g not in S or "_a" not in S[g]:
        return None
    thr = max(0.65, S[b]["null_q95"])
    return float(np.mean(S[g]["_a"] >= thr))


STRUCT = {"ur3": ("U_reign", "U_coll", "G_reign", "G_coll"), "cdli": ("U_reign", "G_reign"),
          "lat": ("ge_rlp_vs_bwhe", "br_north_vs_south")}


def family_verdict(rows):
    gated = [r for r in rows if r.get("gate_pass") and r.get("delta") is not None]
    if not gated:
        return "underpowered", None
    m = min(r["delta"] for r in gated)
    return ("above floor" if m >= MARGIN else "not above floor"), m


def a4(S2):
    """Floor bias: re-read every step-2 gap against the shuffled-label null and a conservative reference."""
    C2 = s2.conditions()
    out1, out2 = [], []
    for name, c in C2.items():
        i = c["info"]
        if c["part"] == "1" and i.get("role") == "between":
            w = f"W_{name[2:].replace('_at_', '_')}"
            if name not in S2 or w not in S2 or "median" not in S2[name] or "median" not in S2[w]:
                continue
            b, wm, nm = S2[name]["median"], S2[w]["median"], S2[name]["null_med"]
            g = gate_of(S2, "G_" + name, name)
            out1.append(dict(corpus=i["corpus"], variant=i["variant"], split=i["split"], n_side=S2[name]["n_side"],
                             b=b, w=wm, null_med=nm, w_null_med=S2[w]["null_med"], d_floor=b - wm, d_null=b - nm,
                             d_cons=b - max(wm, nm), p_floor=pfloor(S2, w, name), p_chance=S2[name]["p_chance"],
                             gate=g, gate_pass=g is not None and g >= 0.8))
        if c["part"] == "2" and i.get("role") == "between":
            tag = name[3:]; w = "IW_" + tag
            if name not in S2 or w not in S2 or "median" not in S2[name]:
                continue
            b, wm, nm = S2[name]["median"], S2[w]["median"], S2[name]["null_med"]
            pw = {}
            for ref, rv in (("floor", wm), ("null", nm), ("cons", max(wm, nm))):
                pn = f"IP{GATE_Q}_{tag}"
                pw[ref] = float(np.mean(S2[pn]["_a"] - rv >= MARGIN)) if pn in S2 and "_a" in S2[pn] else None
            out2.append(dict(family=i["family"], a=i["pair"][0], b=i["pair"][1], n_side=S2[name]["n_side"], between=b,
                             within=wm, null_med=nm, w_null_med=S2[w]["null_med"], d_floor=b - wm, d_null=b - nm,
                             d_cons=b - max(wm, nm), p_floor=pfloor(S2, w, name), p_chance=S2[name]["p_chance"],
                             power=pw))
    for fam in s2.FAMILIES:
        rows = [r for r in out2 if r["family"] == fam]
        for r, qf, qc in zip(rows, bh([r["p_floor"] for r in rows]), bh([r["p_chance"] for r in rows])):
            r["q_floor"], r["q_chance"] = qf, qc
    for r in out2:
        def v(d, q, pw):
            g = pw is not None and pw >= 0.8
            if d >= MARGIN and q <= 0.10 and g:
                return "differs"
            if d < MARGIN and g:
                return "same"
            if d >= MARGIN and q <= 0.10:
                return "differs (gate fails)"
            return "underpowered"
        r["v_floor"] = v(r["d_floor"], r["q_floor"], r["power"]["floor"])
        r["v_null"] = v(r["d_null"], r["q_chance"], r["power"]["null"])
        r["v_cons"] = v(r["d_cons"], max(r["q_floor"], r["q_chance"]), r["power"]["cons"])
        r["flip"] = len({r["v_floor"], r["v_null"], r["v_cons"]}) > 1
    fam1 = {}
    for tier in ("whole", "namefree"):
        for corp in ("ur3", "cdli", "lat", "ob"):
            st = STRUCT.get(corp, ("N_rand", "I_rand"))
            rows = [r for r in out1 if r["corpus"] == corp and r["variant"] == tier and r["split"] in st]
            res = {}
            for ref in ("d_floor", "d_null", "d_cons"):
                rr = [dict(r, delta=r[ref]) for r in rows]
                res[ref] = family_verdict(rr)
            fam1[f"{corp}|{tier}"] = res
    return out1, out2, fam1


def report():
    C = conditions()
    S = load(HERE / "draws.jsonl")
    S2 = load(S2DIR / "draws.jsonl")
    R = dict()
    # ---------------- A1/A2 rows
    P = []
    for name, c in C.items():
        i = c["info"]
        if i.get("role") != "between" or i.get("attack") not in ("A1", "A2"):
            continue
        key = name[2:]; w = "W_" + key; g = "G_" + key
        if name not in S or w not in S or "median" not in S[name] or "median" not in S[w]:
            P.append(dict(corpus=i["corpus"], variant=i["variant"], split=i["split"], failed=True)); continue
        b, wm, nm = S[name]["median"], S[w]["median"], S[name]["null_med"]
        gt = gate_of(S, g, name)
        P.append(dict(corpus=i["corpus"], variant=i["variant"], split=i["split"], n_side=S[name]["n_side"], b=b, w=wm,
                      null_med=nm, delta=b - wm, d_cons=b - max(wm, nm), p_floor=pfloor(S, w, name),
                      p_chance=S[name]["p_chance"], gate=gt, gate_pass=gt is not None and gt >= 0.8))
    fams = {}
    for corp in STRUCT:
        for v in ("loose", "strict", "noTG", "noTGtheo", "noPN", "noUNIT", "wholeAtNF"):
            rows = [r for r in P if r["corpus"] == corp and r["variant"] == v and r["split"] in STRUCT[corp]]
            if rows:
                fams[f"{corp}|{v}"] = dict(zip(("verdict", "min_delta"), family_verdict(rows)),
                                           cons=family_verdict([dict(r, delta=r.get("d_cons")) for r in rows]))
    R["a12_rows"], R["a12_families"] = P, fams
    # ---------------- A3
    s2r = step2_results()
    W = {r["family"]: r for r in s2r["part2"] if {r["a"], r["b"]} == {MD, HA} and r["family"] in IFAMS}
    A3 = {}
    share = ur3_name_share()
    for fam in IFAMS:
        obs = W[fam]["delta"]; wm = W[fam]["within"]
        curve = []
        for form in FORMS:
            excl = None
            for r in RATES:
                nm = f"P_{fam}_{form}_{r}"
                if nm not in S or "_a" not in S[nm]:
                    continue
                gap = S[nm]["_a"] - wm
                frac = float(np.mean(gap > obs))
                curve.append(dict(form=form, rate=r, median=S[nm]["median"], med_gap=float(np.median(gap)), frac_above_obs=frac))
                if excl is None and frac >= 0.95:
                    excl = r
            maxok = max([r for r in RATES if excl is None or r < excl], default=None)
            A3[f"{fam}|{form}"] = dict(obs_delta=obs, within=wm, excluded_from=excl, max_consistent=maxok,
                                       # Ur III share is 0.998 of legends: compared with the nearest grid point, 1.0
                                       ur3_share_excluded=(excl is not None and excl <= min(RATES, key=lambda x: abs(x - share["share_any_pn"]))))
        A3[f"{fam}|curve"] = curve
    R["a3"], R["ur3_name_share"] = A3, share
    # ---------------- A4
    a4_1, a4_2, a4_f = a4(S2)
    R["a4_part1"], R["a4_part2"], R["a4_part1_families"] = a4_1, a4_2, a4_f
    # ---------------- A5
    A5 = {}
    for ed in ("icit", "m77"):
        b, w, pw = f"B_strict_{ed}", f"W_strict_{ed}", f"PW_strict_{ed}"
        if b in S and w in S and "median" in S[b] and "median" in S[w]:
            wm = S[w]["median"]
            A5[f"strict_{ed}"] = dict(n_side=S[b]["n_side"], between=S[b]["median"], within=wm, delta=S[b]["median"] - wm,
                                      null_med=S[b]["null_med"], p_floor=pfloor(S, w, b), p_chance=S[b]["p_chance"],
                                      power=float(np.mean(S[pw]["_a"] - wm >= MARGIN)) if pw in S and "_a" in S[pw] else None)
        X = {k: S.get(f"X_{ed}_{k}", {}) for k in ("X1", "X2", "X3", "X4")}
        if all("median" in x for x in X.values()):
            g1, g3 = gate_of(S, f"GX_{ed}_X1", f"X_{ed}_X1"), gate_of(S, f"GX_{ed}_X3", f"X_{ed}_X3")
            d1 = X["X1"]["median"] - X["X2"]["median"]; d3 = X["X3"]["median"] - X["X4"]["median"]
            if not (g1 is not None and g1 >= 0.8 and g3 is not None and g3 >= 0.8):
                xv = "underpowered"
            elif d1 >= MARGIN and d3 >= MARGIN:
                xv = "place-consistent"
            elif d1 < MARGIN and d3 < MARGIN:
                xv = "object/format"
            else:
                xv = "mixed"
            A5[f"cross_{ed}"] = dict(n_side=X["X1"]["n_side"], **{k: X[k]["median"] for k in X},
                                     d_HAsealing=d1, d_MDsealing=d3, gate_X1=g1, gate_X3=g3, verdict=xv)
    ps = [A5[f"strict_{e}"]["p_floor"] for e in ("icit", "m77") if f"strict_{e}" in A5]
    for e, q in zip([e for e in ("icit", "m77") if f"strict_{e}" in A5], bh(ps)):
        x = A5[f"strict_{e}"]; x["q_floor"] = q
        g = x["power"] is not None and x["power"] >= 0.8
        x["verdict"] = ("differs" if x["delta"] >= MARGIN and q <= 0.10 and g else
                        "same" if x["delta"] < MARGIN and g else
                        "differs (gate fails)" if x["delta"] >= MARGIN and q <= 0.10 else "underpowered")
    if "B_mound_m77" in S and "W_mound_m77" in S and "median" in S["W_mound_m77"]:
        wm = S["W_mound_m77"]["median"]
        pwr = float(np.mean(S["G_mound_m77"]["_a"] - wm >= MARGIN)) if "_a" in S.get("G_mound_m77", {}) else None
        A5["mound_m77"] = dict(n_side=S["B_mound_m77"]["n_side"], between=S["B_mound_m77"]["median"], within=wm,
                               delta=S["B_mound_m77"]["median"] - wm, p_floor=pfloor(S, "W_mound_m77", "B_mound_m77"),
                               power=pwr)
    elif "W_mound_m77" in S:
        A5["mound_m77"] = dict(failed=True, n_side=S["W_mound_m77"].get("n_side"))
    for key in ("moulded", "noncopper"):
        b, w, pw = f"B_tab_{key}", f"W_tab_{key}", f"PW_tab_{key}"
        if b in S and w in S and "median" in S[b] and "median" in S[w]:
            wm = S[w]["median"]
            pwr = float(np.mean(S[pw]["_a"] - wm >= MARGIN)) if pw in S and "_a" in S[pw] else None
            d = S[b]["median"] - wm; pf = pfloor(S, w, b)
            g = pwr is not None and pwr >= 0.8
            A5[f"tab_{key}"] = dict(n_side=S[b]["n_side"], between=S[b]["median"], within=wm, delta=d, p_floor=pf,
                                    p_chance=S[b]["p_chance"], power=pwr,
                                    verdict=("differs" if d >= MARGIN and pf <= 0.10 and g else "same" if d < MARGIN and g
                                             else "differs (gate fails)" if d >= MARGIN and pf <= 0.10 else "underpowered"))
    A5["dup_icit"], A5["dup_m77"] = dup_profile("icit_sealing"), dup_profile("m77_sealing")
    R["a5"] = A5
    R["conditions"] = {k: {kk: vv for kk, vv in v.items() if not kk.startswith("_")} for k, v in S.items()}
    lib.jdump(R, HERE / "results.json")
    print(json.dumps({k: v for k, v in R.items() if k not in ("conditions", "a4_part1", "a4_part2", "a12_rows")},
                     indent=1, ensure_ascii=False, default=str)[:20000])


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "sizes"
    {"sizes": sizes, "run": run, "report": report, "audit": audit}[mode]()
