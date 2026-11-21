"""Uniformity paper, step 2 (prereg docs/prereg/uniformity_paper_step2.md).

Every condition goes through the benchmark's own clean() + draw_n() + score() (uniformity_benchmark/run.py),
called the way step-1 s1.py and redteam rt1.py call them. Planted-answer gates use rt.plant() (s1 rule);
the Indus local-stock power test is rt1.plant_harappa()'s old20 recipe with the planted side as a parameter.
No new classifier.

  Part 1  seal-type references, between-site vs their own within-site floors at matched size:
          Ur III seal impressions (ORACC), Ur III seals one per seal (CDLI), Latin instrumentum
          owner/maker marks (EDH), Old Babylonian seal impressions (ORACC).
  Part 2  all-site Indus map: every site pair with >= 40 complete texts of the object type, per editor
          (M77, ICIT), between AUC, random-halves floor of the larger site, planted local stock power, q-values.

  board/run.sh .venv/bin/python -I experiments/uniformity_paper/step2/s2.py sizes
  board/run.sh .venv/bin/python -I experiments/uniformity_paper/step2/s2.py run 1     # part 1, resumable
  board/run.sh .venv/bin/python -I experiments/uniformity_paper/step2/s2.py run 2     # part 2, resumable
  .venv/bin/python -I experiments/uniformity_paper/step2/s2.py report                  # results.json, table.md
"""
import itertools
import json
import sys
import zlib
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "experiments/uniformity_paper/step1"))
sys.path.insert(0, str(ROOT / "experiments/redteam_uniformity_step1"))
import s1  # noqa: E402  step-1 pools (imports ub = benchmark run.py, rt, lib)
import rt1  # noqa: E402  red-team step-1 (LAT_SPLITS)

ub, rt, lib = s1.ub, s1.rt, s1.lib
from corpus.load import icit_texts, m77_texts  # noqa: E402

DATA = HERE / "data"
N_DRAWS = 50
SEED = 20261125
N_MAX = 227
MIX = s1.MIX
MARGIN = 0.05
GATE_Q = 0.15
PLANT_Q = (0.10, 0.15, 0.20)
MIN_TEXTS = 40
MD, HA = "Mohenjo-daro", "Harappa"


def _jl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8")]


def half(i):
    return "X" if zlib.crc32(("r" + i).encode()) % 2 else "Y"


# =========================================================================== Part 1 pools
def ur3_variant(T, variant):
    """T: rows with lines of [form, pos] and a side label. whole / namefree / namefree_owner (step-1 rules:
    owner de-dup on full forms first, then names removed), then ub.clean."""
    if variant == "namefree_owner":
        full = [dict(t, lines=[[w for w, _ in l] for l in t["lines"]]) for t in T]
        ids = {t["id"] for t in rt.ur3_owner_dedup(full)}
        T = [t for t in T if t["id"] in ids]
    if variant == "whole":
        T = s1._fix([dict(t, lines=[[w for w, _ in l] for l in t["lines"]]) for t in T])
    else:
        T = s1._fix([dict(t, lines=[[w for w, p in l if not s1.ur3_proper(w, p)] for l in t["lines"]]) for t in T])
    return ub.clean(T)


_C = {}


def cache(k, f):
    if k not in _C:
        _C[k] = f()
    return _C[k]


def ur3_rows():
    def f():
        M = {r["id"]: r for r in _jl(DATA / "ur3meta.jsonl")}
        return [dict(r, reign=M[r["id"]]["reign"], museum=M[r["id"]]["museum"]) for r in _jl(s1.DATA / "ur3pos.jsonl")]
    return cache("ur3", f)


def cdli_rows():
    return cache("cdli", lambda: [r for r in _jl(DATA / "cdliseal.jsonl") if r["period"] == "Ur III"])


def ob_rows():
    return cache("ob", lambda: _jl(DATA / "obpos.jsonl"))


EARLY, LATE = {"SH", "AS"}, {"SS", "IS"}
UR3_SPLITS = {   # name -> (city, label(row) -> side | None)
    "U_reign": ("Umma", lambda r: "early" if r["reign"] in EARLY else ("late" if r["reign"] in LATE else None)),
    "U_coll": ("Umma", lambda r: "BM" if r["museum"] == "BM" else ("Yale" if r["museum"] in ("YBC", "NBC") else None)),
    "U_rand": ("Umma", lambda r: half(r["id"])),
    "G_reign": ("Girsu", lambda r: "early" if r["reign"] in EARLY else ("late" if r["reign"] in LATE else None)),
    "G_coll": ("Girsu", lambda r: "BM" if r["museum"] == "BM" else ("L" if r["museum"] == "L" else None)),
    "G_rand": ("Girsu", lambda r: half(r["id"])),
}
CDLI_SPLITS = {
    "U_reign": ("Umma", lambda r: r["reign"]),
    "U_rand": ("Umma", lambda r: half(r["id"])),
    "G_reign": ("Girsu", lambda r: r["reign"]),
    "G_rand": ("Girsu", lambda r: half(r["id"])),
}
OB_SPLITS = {
    "N_rand": ("Nippur", lambda r: half(r["id"])),
    "I_rand": ("Isin", lambda r: half(r["id"])),
}


def split_sides(split):
    lab = {"U_reign": ("early", "late"), "G_reign": ("early", "late"), "U_coll": ("BM", "Yale"), "G_coll": ("BM", "L")}
    return lab.get(split, ("X", "Y"))


def within_pool(rows, splits, split, variant):
    city, f = splits[split]
    T = []
    for r in rows:
        if r["site"] != city:
            continue
        s = f(r)
        if s is not None:
            T.append(dict(id=r["id"], site=s, group=r["group"], lines=r["lines"]))
    return ur3_variant(T, variant)


def between_pool(rows, a, b, variant):
    return ur3_variant([dict(id=r["id"], site=r["site"], group=r["group"], lines=r["lines"]) for r in rows
                        if r["site"] in (a, b)], variant)


# ---- Latin instrumentum owner/maker marks
LAT_TM = {"tile", "instrumentum domesticum", "signaculum", "amphora", "lamp", "vessel"}


def lat_ids(stamped_only=False):
    out = set()
    for m in _jl(DATA / "latmeta.jsonl"):
        if m["tm"] in LAT_TM and m["ti"] == "owner/artist inscription" and (m["stamped"] or not stamped_only):
            out.add(m["id"])
    return out


def lat_rows():
    return cache("lat", lambda: _jl(s1.DATA / "lattr.jsonl"))


def lat_between(namefree):
    ids = lat_ids()
    T = [dict(id=r["id"], site=r["site"], group=r["group"],
              lines=[[w for w, f in l if not (namefree and f == "proper")] for l in r["lines"]])
         for r in lat_rows() if r["id"] in ids]
    return ub.clean(s1._fix(T))


LAT_SPLITS = dict(rt1.LAT_SPLITS)
LAT_SPLITS["br_random"] = ("Britannia", "random")


def lat_within(split, namefree, stamped_only=False):
    ids = lat_ids(stamped_only)
    prov, f = LAT_SPLITS[split]
    T = []
    for r in lat_rows():
        if r["id"] not in ids or r["site"] != prov:
            continue
        s = half(r["id"]) if f == "random" else f(r.get("region", ""))
        if s is None:
            continue
        T.append(dict(id=r["id"], site=s, group=r["group"],
                      lines=[[w for w, fl in l if not (namefree and fl == "proper")] for l in r["lines"]]))
    return ub.clean(s1._fix(T))


# =========================================================================== Part 2 pools (Indus)
M77_NAME = {"Mohenjodaro": MD, "Harappa": HA, "Lothal": "Lothal", "Chanhudaro": "Chanhu-daro", "Kalibangan": "Kalibangan"}


def m77_obj(obj):
    def f():
        out = []
        for t in m77_texts():
            if t["object_type"] != obj or "#" in t["seq"] or not t.get("complete"):
                continue
            site = M77_NAME.get(t["site"])
            if site is None:
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
                out.append(dict(id=i, site=site, lines=L, group=i))
        return out
    return cache("m77" + obj, f)


ICIT_TYPES = {"seal": lambda ty: ty in ("SEAL:S", "SEAL"), "sealtype": lambda ty: ty.startswith("SEAL"),
              "sealing": lambda ty: ty == "SEAL:R", "tablet": lambda ty: ty.startswith("TAB")}


def icit_obj(obj):
    def f():
        out = []
        for t in icit_texts():
            if not ICIT_TYPES[obj](t["type"] or "") or "#" in t["seq"] or not t["complete"]:
                continue
            L = [list(seg) for seg in t["segments"] if seg]
            if L:
                out.append(dict(id=t["id"], site=t["site"], lines=L, group=t["id"]))
        return out
    return cache("icit" + obj, f)


def indus_raw(fam):
    ed, obj = fam.split("_", 1)
    return m77_obj(obj) if ed == "m77" else icit_obj(obj)


FAMILIES = {   # frozen in the prereg from counts of complete texts before cleaning (>= 40 per site)
    "m77_seal": [MD, HA, "Lothal", "Chanhu-daro", "Kalibangan"],
    "icit_seal": [MD, HA, "Dholavira", "Chanhu-daro"],
    "icit_sealtype": [MD, HA, "Dholavira", "Lothal", "Chanhu-daro", "Kalibangan"],
    "icit_sealing": [MD, HA],
    "m77_sealing": [MD, HA],
    "icit_tablet": [MD, HA],
}


def pair_order(fam, s, t):
    c = Counter(x["site"] for x in indus_raw(fam))
    return (s, t) if c[s] >= c[t] else (t, s)


def indus_between(fam, a, b):
    return ub.clean([x for x in indus_raw(fam) if x["site"] in (a, b)])


def indus_within(fam, a):
    return ub.clean([dict(x, site=half(x["id"])) for x in indus_raw(fam) if x["site"] == a])


def plant_side(sample, side, q, rng, common):
    """rt1.plant_harappa 'old20' recipe with the planted side as a parameter: real labels kept; tokens of
    `side` texts replaced with prob q by a 20-sign stock drawn from the pool's common signs."""
    stock = list(rng.choice(common, 20, replace=False))
    out = []
    for t in sample:
        if t["site"] == side:
            t = dict(t, lines=[[stock[rng.integers(20)] if rng.random() < q else x for x in l] for l in t["lines"]])
        out.append(t)
    return out


# =========================================================================== conditions
def conditions():
    C = {}

    def add(name, part, build, a, b, n=None, plant=None, **info):
        C[name] = dict(part=part, build=build, a=a, b=b, n=n, plant=plant, info=info)

    def pairup(part, wname, wbuild, wa, wb, bname, bbuild, ba, bb, gate=True, **info):
        add(wname, part, wbuild, wa, wb, n=("match", wname, bname), role="within", **info)
        add(bname, part, bbuild, ba, bb, n=("match", wname, bname), role="between", **info)
        if gate:
            add("G_" + bname, part, bbuild, ba, bb, n=bname, plant=("gate", GATE_Q), role="gate", **info)

    # ---------------- Part 1
    for v in ("namefree", "whole", "namefree_owner"):
        for sp in UR3_SPLITS:
            sa, sb = split_sides(sp)
            pairup("1", f"W_ur3_{v}_{sp}", lambda v=v, sp=sp: within_pool(ur3_rows(), UR3_SPLITS, sp, v), sa, sb,
                   f"B_ur3_{v}_at_{sp}", lambda v=v: between_pool(ur3_rows(), "Umma", "Girsu", v), "Umma", "Girsu",
                   corpus="ur3", variant=v, split=sp)
        for sp in CDLI_SPLITS:
            sa, sb = split_sides(sp)
            pairup("1", f"W_cdli_{v}_{sp}", lambda v=v, sp=sp: within_pool(cdli_rows(), CDLI_SPLITS, sp, v), sa, sb,
                   f"B_cdli_{v}_at_{sp}", lambda v=v: between_pool(cdli_rows(), "Umma", "Girsu", v), "Umma", "Girsu",
                   corpus="cdli", variant=v, split=sp)
    for v in ("namefree", "whole"):
        for sp in OB_SPLITS:
            pairup("1", f"W_ob_{v}_{sp}", lambda v=v, sp=sp: within_pool(ob_rows(), OB_SPLITS, sp, v), "X", "Y",
                   f"B_ob_{v}_at_{sp}", lambda v=v: between_pool(ob_rows(), "Nippur", "Isin", v), "Nippur", "Isin",
                   corpus="ob", variant=v, split=sp)
        nf = v == "namefree"
        for sp in ("ge_rlp_vs_bwhe", "br_north_vs_south", "ge_random", "br_random"):
            pairup("1", f"W_lat_{v}_{sp}", lambda sp=sp, nf=nf: lat_within(sp, nf), "X", "Y",
                   f"B_lat_{v}_at_{sp}", lambda nf=nf: lat_between(nf), "Britannia", "Germania",
                   corpus="lat", variant=v, split=sp)
        for sp in ("ge_rlp_vs_bwhe", "ge_random"):
            add(f"W_latstamp_{v}_{sp}", "1", lambda sp=sp, nf=nf: lat_within(sp, nf, stamped_only=True), "X", "Y",
                role="within_only", corpus="latstamp", variant=v, split=sp)

    # ---------------- Part 2
    for fam, sites in FAMILIES.items():
        for s, t in itertools.combinations(sites, 2):
            a, b = pair_order(fam, s, t)
            tag = f"{fam}|{a}|{b}"
            pairup("2", f"IW_{tag}", lambda fam=fam, a=a: indus_within(fam, a), "X", "Y",
                   f"IB_{tag}", lambda fam=fam, a=a, b=b: indus_between(fam, a, b), a, b, gate=False,
                   family=fam, pair=[a, b])
            for q in PLANT_Q:
                add(f"IP{q}_{tag}", "2", lambda fam=fam, a=a, b=b: indus_between(fam, a, b), a, b, n=f"IB_{tag}",
                    plant=("side", b, q), role="power", family=fam, pair=[a, b], q=q)
    return C


# =========================================================================== machinery
_BUILT = {}


def built(name, C):
    if name not in _BUILT:
        _BUILT[name] = C[name]["build"]()
    return _BUILT[name]


def natural_n(name, C):
    c = C[name]
    T = built(name, C)
    cnt = Counter(t["site"] for t in T)
    return min(cnt[c["a"]], cnt[c["b"]], N_MAX)


def n_side_of(name, C):
    n = C[name]["n"]
    if isinstance(n, int):
        return n
    if isinstance(n, str):
        return n_side_of(n, C)
    if isinstance(n, tuple):
        return min(natural_n(x, C) for x in n[1:])
    return natural_n(name, C)


def sizes():
    C = conditions()
    for name, c in C.items():
        if c["info"].get("role") in ("gate", "power"):
            continue
        T = built(name, C)
        cnt = Counter(t["site"] for t in T)
        print(f"{c['part']} {name:58s} {c['a']}={cnt[c['a']]} {c['b']}={cnt[c['b']]} n_side={n_side_of(name, C)}", flush=True)
    for fam in FAMILIES:
        print(fam, "complete texts before cleaning", Counter(x["site"] for x in indus_raw(fam)).most_common(10))
    print("latin instrumentum owner/maker", Counter(r["site"] for r in lat_rows() if r["id"] in lat_ids()),
          "stamped", Counter(r["site"] for r in lat_rows() if r["id"] in lat_ids(True)))


def run(part):
    C = conditions()
    path = HERE / "draws.jsonl"
    done = Counter()
    if path.exists():
        for l in open(path):
            done[json.loads(l)["cond"]] += 1
    with open(path, "a") as f:
        for name, c in C.items():
            if c["part"] != part or done[name] >= N_DRAWS:
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
                if n_side < 5:
                    rec = dict(cond=name, part=part, draw=k, auc=None, n_side=n_side, avail=[cnt[a], cnt[b]])
                    f.write(json.dumps(rec) + "\n"); continue
                smp, short = ub.draw_n(T, a, b, rng, MIX, False, n_side, 2 * n_side)
                if smp is None:
                    rec = dict(cond=name, part=part, draw=k, auc=None, n_side=n_side, avail=[cnt[a], cnt[b]])
                else:
                    if c["plant"] and c["plant"][0] == "gate":
                        smp = rt.plant(smp, "new100", c["plant"][1], rng, common)
                    elif c["plant"]:
                        smp = plant_side(smp, c["plant"][1], c["plant"][2], rng, common)
                    obs, nul, nf, nn = ub.score(smp, a, SEED + k)
                    rec = dict(cond=name, part=part, draw=k, auc=obs, null_auc=nul, n_feat=nf, n=nn, n_side=n_side,
                               short=short, avail=[cnt[a], cnt[b]], **rt.describe(smp, a))
                f.write(json.dumps(rec) + "\n"); f.flush()
            print(name, "n", n_side, "done", rec.get("auc"), flush=True)


# =========================================================================== report
def bh(ps):
    ps = np.asarray(ps, float); n = len(ps)
    if n == 0:
        return []
    o = np.argsort(ps); q = np.empty(n)
    prev = 1.0
    for rank, i in reversed(list(enumerate(o, 1))):
        prev = min(prev, ps[i] * n / rank); q[i] = prev
    return q.tolist()


def report():
    C = conditions()
    by = {}
    for l in open(HERE / "draws.jsonl"):
        r = json.loads(l); by.setdefault(r["cond"], []).append(r)
    S = {}
    for name in C:
        rs = by.get(name, [])
        ok = [r for r in rs if r["auc"] is not None]
        if not rs:
            continue
        if not ok:
            S[name] = dict(n_side=rs[0]["n_side"], failed=len(rs), avail=rs[0].get("avail"))
            continue
        a = np.array([r["auc"] for r in ok]); nu = np.array([r["null_auc"] for r in ok])
        S[name] = dict(n_side=ok[0]["n_side"], n_draws=len(ok), failed=len(rs) - len(ok), avail=ok[0]["avail"],
                       median=float(np.median(a)), lo=float(np.quantile(a, 0.025)), hi=float(np.quantile(a, 0.975)),
                       null_q95=float(np.quantile(nu, 0.95)),
                       p_chance=float((1 + np.sum(nu >= np.median(a))) / (1 + len(nu))),
                       local_share=float(np.mean([r["local_share"] for r in ok])), _a=a)
    med = lambda n: S.get(n, {}).get("median")
    # ---- part 1: gaps
    P1 = []
    for name, c in C.items():
        i = c["info"]
        if c["part"] != "1" or i.get("role") != "between":
            continue
        w = f"W_{name[2:].replace('_at_', '_')}"
        g = "G_" + name
        row = dict(corpus=i["corpus"], variant=i["variant"], split=i["split"], between=name, within=w)
        if name in S and w in S and "median" in S[name] and "median" in S[w]:
            thr = max(0.65, S[name]["null_q95"])
            gate = float(np.mean(S[g]["_a"] >= thr)) if g in S and "_a" in S[g] else None
            row.update(n_side=S[name]["n_side"], b=S[name]["median"], w=S[w]["median"],
                       delta=S[name]["median"] - S[w]["median"],
                       p_floor=float((1 + np.sum(S[w]["_a"] >= S[name]["median"])) / (1 + len(S[w]["_a"]))),
                       gate=gate, gate_pass=(gate is not None and gate >= 0.8))
        else:
            row.update(n_side=S.get(name, S.get(w, {})).get("n_side"), b=med(name), w=med(w), delta=None, gate=None,
                       gate_pass=False, failed=True)
        P1.append(row)
    STRUCT = {"ur3": ("U_reign", "U_coll", "G_reign", "G_coll"), "cdli": ("U_reign", "G_reign"),
              "lat": ("ge_rlp_vs_bwhe", "br_north_vs_south"), "ob": ("N_rand", "I_rand")}
    fam_verdict, p1v, fams = {}, {}, {}
    for tier in ("whole", "namefree"):
        fv = {}
        for corp, splits in STRUCT.items():
            rows = [r for r in P1 if r["corpus"] == corp and r["variant"] == tier and r["split"] in splits]
            gated = [r for r in rows if r.get("gate_pass") and r.get("delta") is not None]
            if not gated:
                v = "underpowered"
            else:
                v = "above floor" if min(r["delta"] for r in gated) >= MARGIN else "not above floor"
            fv[corp] = dict(verdict=v, min_delta=min([r["delta"] for r in gated], default=None),
                            gated=[r["split"] for r in gated], all=[r["split"] for r in rows])
        fam_verdict[tier] = fv
        fm = {"Ur III": fv["ur3"]["verdict"], "Latin": fv["lat"]["verdict"], "Old Babylonian": fv["ob"]["verdict"]}
        fams[tier] = fm
        na = sum(v == "above floor" for v in fm.values()); nn = sum(v == "not above floor" for v in fm.values())
        if na >= 2 and nn == 0:
            p1v[tier] = "SUPPORTED"
        elif na >= 1 and nn >= 1:
            p1v[tier] = "MIXED"
        elif na == 1:
            p1v[tier] = "WEAK"
        elif nn >= 1:
            p1v[tier] = "REFUTED"
        else:
            p1v[tier] = "UNDERPOWERED"
    kill_ur3 = [(r["variant"], r["split"]) for r in P1 if r["corpus"] == "ur3" and r["variant"] in ("whole", "namefree")
                and r["split"] in STRUCT["ur3"] and r.get("gate_pass") and r.get("delta") is not None and r["delta"] <= 0]
    # ---- part 2
    P2 = []
    for name, c in C.items():
        i = c["info"]
        if c["part"] != "2" or i.get("role") != "between":
            continue
        tag = name[3:]; w = "IW_" + tag
        a, b = i["pair"]
        row = dict(family=i["family"], a=a, b=b)
        if name in S and w in S and "median" in S[name] and "median" in S[w]:
            wm = S[w]["median"]
            pw = {}
            for q in PLANT_Q:
                pn = f"IP{q}_{tag}"
                pw[q] = float(np.mean(S[pn]["_a"] - wm >= MARGIN)) if pn in S and "_a" in S[pn] else None
            row.update(n_side=S[name]["n_side"], between=S[name]["median"], within=wm, delta=S[name]["median"] - wm,
                       p_floor=float((1 + np.sum(S[w]["_a"] >= S[name]["median"])) / (1 + len(S[w]["_a"]))),
                       p_chance=S[name]["p_chance"], power=pw,
                       gate_pass=(pw.get(GATE_Q) is not None and pw[GATE_Q] >= 0.8))
        else:
            row.update(n_side=S.get(name, {}).get("n_side"), failed=True, gate_pass=False)
        P2.append(row)
    for fam in FAMILIES:
        rows = [r for r in P2 if r["family"] == fam and "p_floor" in r]
        for r, qf, qc in zip(rows, bh([r["p_floor"] for r in rows]), bh([r["p_chance"] for r in rows])):
            r["q_floor"], r["q_chance"] = qf, qc
    for r in P2:
        if "delta" not in r:
            r["verdict"] = "failed"
        elif r["delta"] >= MARGIN and r["q_floor"] <= 0.10 and r["gate_pass"]:
            r["verdict"] = "differs"
        elif r["delta"] < MARGIN and r["gate_pass"]:
            r["verdict"] = "same"
        elif r["delta"] >= MARGIN and r["q_floor"] <= 0.10:
            r["verdict"] = "differs (gate fails)"
        else:
            r["verdict"] = "underpowered"
    PER = {"Lothal", "Chanhu-daro"}
    per_rows = [r for r in P2 if r["family"] in ("m77_seal", "icit_sealtype", "icit_seal") and PER & {r["a"], r["b"]}]
    mdh = {r["family"]: r["verdict"] for r in P2 if {r["a"], r["b"]} == {MD, HA}}
    yes = [r for r in per_rows if r["verdict"] == "differs" and mdh.get(r["family"]) == "same"]
    any_diff = [r for r in per_rows if r["verdict"].startswith("differs")]
    gated_same = [r for r in per_rows if r["verdict"] == "same"]
    if yes:
        hv = "YES: a peripheral-town pair differs while Mohenjo-daro vs Harappa does not"
    elif not any_diff and len(gated_same) >= 2:
        hv = "NO: no pair with Lothal or Chanhu-daro rises above the within-site floor; >= 2 such pairs gated"
    else:
        hv = "UNDERPOWERED"
    out = dict(conditions={k: {kk: vv for kk, vv in v.items() if kk != "_a"} for k, v in S.items()},
               part1=P1, part1_families=fam_verdict, part1_verdict=p1v, part1_kill_ur3=kill_ur3,
               part2=P2, part2_question=hv)
    lib.jdump(out, HERE / "results.json")
    f3 = lambda x: "" if x is None else f"{x:.3f}"
    L = ["## Part 1: seal-type references, between vs within (median AUC, matched size)", "",
         "| corpus | variant | within split | n/side | between | within | Δ | p (floor) | gate |", "|---|---|---|---|---|---|---|---|---|"]
    for r in P1:
        L.append(f"| {r['corpus']} | {r['variant']} | {r['split']} | {r.get('n_side')} | {f3(r.get('b'))} | {f3(r.get('w'))} | "
                 f"{'' if r.get('delta') is None else f'{r['delta']:+.3f}'} | {f3(r.get('p_floor'))} | "
                 f"{'' if r.get('gate') is None else f'{r['gate']:.0%}'} |")
    L += ["", "| within only (no between) | n/side | median | 95% |", "|---|---|---|---|"]
    for name, c in C.items():
        if c["info"].get("role") == "within_only" and name in S and "median" in S[name]:
            L.append(f"| {name} | {S[name]['n_side']} | {S[name]['median']:.3f} | {S[name]['lo']:.3f}-{S[name]['hi']:.3f} |")
    L += ["", "## Part 2: Indus site pairs", "",
          "| family | site a (larger) | site b | n/side | between | within (a halves) | Δ | p floor | q floor | q chance | power 10/15/20% | verdict |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in P2:
        if "delta" not in r:
            L.append(f"| {r['family']} | {r['a']} | {r['b']} | {r.get('n_side')} | failed | | | | | | | |"); continue
        pw = "/".join("" if r["power"][q] is None else f"{r['power'][q]:.0%}" for q in PLANT_Q)
        L.append(f"| {r['family']} | {r['a']} | {r['b']} | {r['n_side']} | {r['between']:.3f} | {r['within']:.3f} | "
                 f"{r['delta']:+.3f} | {r['p_floor']:.3f} | {r['q_floor']:.3f} | {r['q_chance']:.3f} | {pw} | {r['verdict']} |")
    L += ["", f"Part 1 verdict: {p1v} ({fams}); Ur III kill splits: {kill_ur3}", f"Part 2 question: {hv}"]
    (HERE / "table.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "sizes"
    if mode == "run":
        run(sys.argv[2])
    else:
        {"sizes": sizes, "report": report}[mode]()
