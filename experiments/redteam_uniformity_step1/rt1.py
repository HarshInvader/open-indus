"""Red team of uniformity_paper step 1 (prereg docs/prereg/redteam_uniformity_step1.md).

Every condition goes through the benchmark's own clean() + draw_n() + score() (uniformity_benchmark/run.py),
called the way uniformity_paper/step1/s1.py calls them; pools come from s1.py / rt.py builders. No new
classifier. One change of input only, used in attack 2: after a draw, the CV group of each Linear B line can be
set to its scribal hand (hand-held-out CV), so that no hand is in both a training and a test fold.

  1  like-for-like floors: within-site splits of Knossos, Pylos (scribal-hand groups, random tablet halves),
     Latin within one province (regions), Indus within Mohenjo-daro; between-site at the same size.
  2  scribe / series: Knossos vs Pylos with hand-held-out CV, series-balanced, name-free.
  3  formula words: names + frame (commonest 38.3% of tokens) removed, and top-k types removed, for Linear B,
     Ur III, Latin and Indus.
  4  Indus findspot validity: M77 locus -> area checked against old_registers field numbers; confirmed-only
     rerun; cross-split near-copy counts and a cross-split near-copy drop.
  5  sign lists: Indus within and between under ICIT raw / A1 / A2 (CISI area split) and M77 / lump_all.
  6  power: a Harappa-only planted stock at q = 0.10 / 0.15 / 0.20 of tokens; how often between - within >= 0.05.

  board/run.sh .venv/bin/python -I experiments/redteam_uniformity_step1/rt1.py sizes
  board/run.sh .venv/bin/python -I experiments/redteam_uniformity_step1/rt1.py run       # resumable -> draws.jsonl
  .venv/bin/python -I experiments/redteam_uniformity_step1/rt1.py report                  # -> results.json, table.md
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
sys.path.insert(0, str(ROOT / "experiments/uniformity_paper/step1"))
import s1  # noqa: E402  step-1 pools (also imports ub = benchmark run.py, rt, lib)

ub, rt, lib = s1.ub, s1.rt, s1.lib
sys.path.insert(0, str(ROOT / "experiments/fish_tick_closer_v2"))
import dedup  # noqa: E402  non-chaining de-dup (near())

N_DRAWS = 30
SEED = 20261124
N_MAX = 227
MIX = s1.MIX
MD, HA = s1.MD, s1.HA
K, P = "Knossos", "Pylos"
MARGIN = 0.05                     # frozen step-1 rule: between - within >= 0.05 = city signal above floor
N_HAND_PARTS = 3                  # number of random hand-group partitions per palace
PLANT_Q = (0.10, 0.15, 0.20)
TOPK = (10, 20)


# =========================================================================== Linear B helpers
def _lbmeta():
    M = {}
    for r in s1._jl(s1.DATA / "lb.jsonl"):
        m = re.search(r"\(([^)]*)\)\s*$", r["heading"])
        h = m.group(1) if m else "-"
        h = re.split(r"[-?]", h)[0] if h not in ("-", "") else "-"   # 124-S, 124-R, 124? -> 124
        M[r["group"]] = dict(site=r["site"], hand=h or "-", series=r["series"][0])
    return M


LBM = None


def lbm():
    global LBM
    if LBM is None:
        LBM = _lbmeta()
    return LBM


def hand_of(group):
    h = lbm()[group]["hand"]
    return f"H{lbm()[group]['site'][0]}{h}" if h != "-" else f"T{group}"   # unknown hand: own group


def lb_hand_split(variant, site, part, balanced=False):
    """Within one palace: hands (known only) assigned to two sides by a seeded shuffle, greedy toward the
    side with fewer tablets. Optional series balance across the two sides (s1 rule, by Bennett letter)."""
    M = lbm()
    T = [t for t in s1.lb_raw(variant) if M[t["group"]]["site"] == site and M[t["group"]]["hand"] != "-"]
    tabs = Counter()
    for g in {t["group"] for t in T}:
        tabs[M[g]["hand"]] += 1
    hands = sorted(tabs, key=lambda h: zlib.crc32(f"{site}{h}{part}".encode()))
    side, cnt = {}, {"X": 0, "Y": 0}
    for h in hands:
        s = "X" if cnt["X"] <= cnt["Y"] else "Y"
        side[h] = s; cnt[s] += tabs[h]
    T = [dict(t, site=side[M[t["group"]]["hand"]]) for t in T]
    if balanced:
        T = _series_bal(T, "X", "Y")
    return ub.clean(T)


def lb_random_split(variant, site):
    M = lbm()
    T = [t for t in s1.lb_raw(variant) if M[t["group"]]["site"] == site]
    T = [dict(t, site="X" if zlib.crc32(("r" + t["group"]).encode()) % 2 else "Y") for t in T]
    return ub.clean(T)


def _series_bal(texts, a, b):
    M = lbm()
    tabs = {}
    for t in texts:
        tabs.setdefault((t["site"], M[t["group"]]["series"]), set()).add(t["group"])
    keep = set()
    for L in {k[1] for k in tabs}:
        A, B = tabs.get((a, L), set()), tabs.get((b, L), set())
        m = min(len(A), len(B))
        for s in (A, B):
            keep |= set(sorted(s, key=lambda g: zlib.crc32(g.encode()))[:m])
    return [t for t in texts if t["group"] in keep]


# =========================================================================== Latin within one province
LAT_SPLITS = {
    # Germania Superior core: Rheinland-Pfalz vs Baden-Württemberg + Hessen
    "ge_rlp_vs_bwhe": ("Germania", lambda r: "X" if r.startswith("Rheinland-Pfalz") else
                       ("Y" if r.startswith(("Baden-Württemberg", "Hessen")) else None)),
    # Britannia: Wall zone and north vs the rest
    "br_north_vs_south": ("Britannia", lambda r: "X" if r in {"Northumberland", "Cumbria", "Tyne and Wear", "Durham",
                          "East Lothian", "North Yorkshire", "Scottish Borders", "Dumfries and Galloway", "Lancashire",
                          "Stirling", "Falkirk", "West Lothian", "West Dunbartonshire", "East Dunbartonshire",
                          "North Lanarkshire", "Glasgow", "Fife", "Perth and Kinross", "Angus", "West Yorkshire",
                          "South Yorkshire", "East Riding of Yorkshire"} else ("Y" if r else None)),
    "ge_random": ("Germania", "random"),
}


def lat_within(split, namefree=True, frame=False):
    prov, f = LAT_SPLITS[split]
    R = [r for r in s1._jl(s1.DATA / "lattr.jsonl") if r["site"] == prov]
    T = []
    for r in R:
        s = ("X" if zlib.crc32(("r" + r["id"]).encode()) % 2 else "Y") if f == "random" else f(r.get("region", ""))
        if s is None:
            continue
        L = [[w for w, fl in l if not (namefree and fl == "proper")] for l in r["lines"]]
        T.append(dict(id=r["id"], site=s, group=r["group"], lines=L))
    T = ub.clean(s1._fix(T))
    if frame:
        T, _ = ub.strip_frame(T); T = ub.clean(T)
    return T


# =========================================================================== formula-word removal
def strip_topk(texts, k):
    wc = Counter(w for t in texts for l in t["lines"] for w in l)
    top = {w for w, _ in wc.most_common(k)}
    out = []
    for t in texts:
        L = [[w for w in l if w not in top] for l in t["lines"]]
        L = [l for l in L if l]
        if L:
            out.append(dict(t, lines=L))
    return ub.clean(out)


def framed(T):
    T, _ = ub.strip_frame(T)
    return ub.clean(T)


def lb_whitelist_frame():
    return framed(s1.lb_pool("whitelist"))


def lb_nonames_frame():
    return framed(s1.lb_pool("nonames"))


# =========================================================================== Indus pools
def m77_city(partition=None):
    T = s1.m77_seals(s1.lab_city)
    if partition:
        T = [dict(t, lines=[[partition.get(x, x) for x in l] for l in t["lines"]]) for t in T]
    return ub.clean(T)


def m77_area(partition=None, keep_ids=None):
    T = s1.m77_seals(s1.lab_area)
    if keep_ids is not None:
        T = [t for t in T if t["id"] in keep_ids]
    if partition:
        T = [dict(t, lines=[[partition.get(x, x) for x in l] for l in t["lines"]]) for t in T]
    return ub.clean(T)


def md_random_split():
    T = [t for t in s1.m77_seals(s1.lab_city) if t["site"] == MD]
    return ub.clean([dict(t, site="X" if zlib.crc32(("r" + t["id"]).encode()) % 2 else "Y") for t in T])


def icit_city(amap=None):
    return ub.clean([t for t in rt.icit_seal_pool(amap) if t["site"] in (MD, HA)])


def icit_area(amap=None):
    base = {t["id"]: t["site"] for t in s1.icit_area_pool()}
    return ub.clean([dict(t, site=base[t["id"]]) for t in rt.icit_seal_pool(amap) if t["id"] in base])


# ---------------------------------------------------------------- attack 4: findspot check
AREA_OF_PREFIX = {"DK": "DK", "HR": "HRVS", "VS": "HRVS"}


def findspot_status():
    """For each M77 Mohenjo-daro seal text in the C1 split: confirmed / contradicted / uncertain, from the
    field-number prefix (or, failing that, the findspot field) of linked old-register rows."""
    reg = {}
    for r in csv.DictReader(open(ROOT / "experiments/old_registers/registers.csv")):
        if not r["m77_text_no"] or r["site"] != "Mohenjo-daro":
            continue
        m = re.match(r"\s*([A-Z]{1,3})\s*\d", r["field_no"] or "")
        p = m.group(1) if m else None
        if p is None:
            m = re.match(r"\s*([A-Z]{2})\b", r["findspot"] or "")
            p = m.group(1) if m else None
        for no in re.split(r"[;, ]+", r["m77_text_no"]):
            if no.strip().isdigit():
                reg.setdefault(int(no), []).append(p)
    meta = s1.m77_meta()
    st, by_locus = {}, {}
    for t in s1.m77_seals(s1.lab_area):
        no = int(t["id"][1:].split(".")[0])
        ps = [p for p in reg.get(no, []) if p]
        areas = {AREA_OF_PREFIX.get(p, "other:" + p) for p in ps}
        if not ps:
            s = "uncertain"
        elif areas == {t["site"]}:
            s = "confirmed"
        elif t["site"] in areas:
            s = "mixed"
        else:
            s = "contradicted"
        st[t["id"]] = s
        loc = meta.get(no, (None, None))[0]
        by_locus.setdefault(loc, Counter()).update(ps or ["none"])
    return st, by_locus


def confirmed_ids():
    st, _ = findspot_status()
    return {i for i, s in st.items() if s == "confirmed"}


def drop_cross_near(T, a, b, min_len=3):
    """Drop every text (>= min_len signs) that is within one edit of, or a contiguous part of, a text on the
    other side (dedup.near both ways, threshold lowered from 4 to min_len). Applied to both sides."""
    sg = {t["id"]: [x for l in t["lines"] for x in l] for t in T}
    A = [t for t in T if t["site"] == a]; B = [t for t in T if t["site"] == b]
    bad = set()
    old = dedup.MIN_DROP
    dedup.MIN_DROP = min_len
    try:
        for x in A:
            for y in B:
                u, v = sg[x["id"]], sg[y["id"]]
                if len(u) < min_len or len(v) < min_len:
                    continue
                s_, l_ = (u, v) if len(u) <= len(v) else (v, u)
                if dedup.near(s_, l_):
                    bad.add(x["id"]); bad.add(y["id"])
    finally:
        dedup.MIN_DROP = old
    return [t for t in T if t["id"] not in bad], len(bad)


def cross_near_count(T, a, b, min_len=2):
    _, n = drop_cross_near(T, a, b, min_len)
    return n


# =========================================================================== conditions
# name -> dict(att, build, a, b, n (int | name-of-condition | None), opg, plant, cv)
def conditions():
    C = {}

    def add(name, att, build, a, b, n=None, opg=False, plant=None, cv=None):
        C[name] = dict(att=att, build=build, a=a, b=b, n=n, opg=opg, plant=plant, cv=cv)

    # ---------------- 1 floors (within) and matched between
    for site in (K, P):
        for p in range(N_HAND_PARTS):
            add(f"W1_lb_{site[:2]}_hands_p{p}", "1", lambda site=site, p=p: lb_hand_split("whole", site, p), "X", "Y", opg=True)
            add(f"W1_lb_{site[:2]}_hands_p{p}_serbal", "1", lambda site=site, p=p: lb_hand_split("whole", site, p, True), "X", "Y", opg=True)
            add(f"W1_lb_{site[:2]}_hands_p{p}_namefree", "1", lambda site=site, p=p: lb_hand_split("whitelist", site, p), "X", "Y", opg=True)
        add(f"W1_lb_{site[:2]}_random", "1", lambda site=site: lb_random_split("whole", site), "X", "Y", opg=True)
    for split in LAT_SPLITS:
        add(f"W1_lat_{split}_namefree", "1", lambda split=split: lat_within(split), "X", "Y")
        add(f"W1_lat_{split}_whole", "1", lambda split=split: lat_within(split, namefree=False), "X", "Y")
    add("W1_md_area_C1", "1", lambda: m77_area(), "DK", "HRVS")
    add("W1_md_random", "1", md_random_split, "X", "Y")
    # between at each within size (n borrowed)
    for site in (K, P):
        for p in range(N_HAND_PARTS):
            add(f"B1_lb_whole_at_{site[:2]}_p{p}", "1", lambda: s1.lb_pool("whole"), K, P, n=f"W1_lb_{site[:2]}_hands_p{p}", opg=True)
            add(f"B1_lb_serbal_at_{site[:2]}_p{p}", "1", lambda: s1.lb_pool("whole", balanced=True), K, P, n=f"W1_lb_{site[:2]}_hands_p{p}_serbal", opg=True)
            add(f"B1_lb_namefree_at_{site[:2]}_p{p}", "1", lambda: s1.lb_pool("whitelist"), K, P, n=f"W1_lb_{site[:2]}_hands_p{p}_namefree", opg=True)
    for split in LAT_SPLITS:
        add(f"B1_lat_namefree_at_{split}", "1", lambda: s1.lat_pool(), "Britannia", "Germania", n=f"W1_lat_{split}_namefree")
        add(f"B1_lat_whole_at_{split}", "1", lambda: s1.lat_pool(namefree=False), "Britannia", "Germania", n=f"W1_lat_{split}_whole")
    add("B1_md_h_at_C1", "1", lambda: m77_city(), MD, HA, n="W1_md_area_C1")

    # ---------------- 2 scribe / series (hand-held-out CV)
    add("H_lb_whole_handcv", "2", lambda: s1.lb_pool("whole"), K, P, opg=True, cv="hand")
    add("H_lb_serbal_handcv", "2", lambda: s1.lb_pool("whole", balanced=True), K, P, opg=True, cv="hand")
    add("H_lb_namefree_handcv", "2", lambda: s1.lb_pool("whitelist"), K, P, opg=True, cv="hand")
    add("H_lb_namefree_serbal_handcv", "2", lambda: s1.lb_pool("whitelist", balanced=True), K, P, opg=True, cv="hand")
    add("H_lb_serbal_tabcv", "2", lambda: s1.lb_pool("whole", balanced=True), K, P, opg=True)   # A8 rerun, this seed

    # ---------------- 3 formula words
    add("F_lb_namefree_frame", "3", lb_whitelist_frame, K, P, opg=True)
    add("F_lb_nonames_frame", "3", lb_nonames_frame, K, P, opg=True)
    add("F_ur3_ug_namefree_frame", "3", lambda: s1.ur3_pool("ug", owner=False, frame=True), "Umma", "Girsu")
    add("F_ur3_pn_namefree_frame", "3", lambda: s1.ur3_pool("pn", owner=False, frame=True), "Puzriš-Dagan", "Nippur")
    add("F_ur3_ug_namefree_owner_frame", "3", lambda: s1.ur3_pool("ug", owner=True, frame=True), "Umma", "Girsu")
    add("F_lat_namefree_frame", "3", lambda: s1.lat_pool(frame=True), "Britannia", "Germania")
    add("F_icit_frame", "3", lambda: framed(icit_city()), MD, HA)
    add("F_m77_city_frame", "3", lambda: framed(m77_city()), MD, HA)
    add("F_m77_area_frame", "3", lambda: framed(m77_area()), "DK", "HRVS")
    add("F_m77_city_frame_at_area", "3", lambda: framed(m77_city()), MD, HA, n="F_m77_area_frame")
    for k in TOPK:
        add(f"F_lb_namefree_top{k}", "3", lambda k=k: strip_topk(s1.lb_pool("whitelist"), k), K, P, opg=True)
        add(f"F_ur3_ug_namefree_top{k}", "3", lambda k=k: strip_topk(s1.ur3_pool("ug", owner=False), k), "Umma", "Girsu")
        add(f"F_lat_namefree_top{k}", "3", lambda k=k: strip_topk(s1.lat_pool(), k), "Britannia", "Germania")
        add(f"F_icit_top{k}", "3", lambda k=k: strip_topk(icit_city(), k), MD, HA)

    # ---------------- 4 findspot validity
    add("L_md_area_confirmed", "4", lambda: m77_area(keep_ids=confirmed_ids()), "DK", "HRVS")
    add("L_md_h_at_confirmed", "4", lambda: m77_city(), MD, HA, n="L_md_area_confirmed")
    add("L_md_area_xnear", "4", lambda: drop_cross_near(m77_area(), "DK", "HRVS")[0], "DK", "HRVS")
    add("L_md_h_xnear", "4", lambda: drop_cross_near(m77_city(), MD, HA)[0], MD, HA, n="L_md_area_xnear")

    # ---------------- 5 sign lists
    A1, A2 = lib.allograph_map("A1"), lib.allograph_map("A2")
    lump = rt.lump_all_partition()
    for nm, am in (("raw", None), ("A1", A1), ("A2", A2)):
        add(f"S_icit_{nm}_area", "5", lambda am=am: icit_area(am), "DK", "HRVS")
        add(f"S_icit_{nm}_city", "5", lambda am=am: icit_city(am), MD, HA, n=f"S_icit_{nm}_area")
    for nm, pt in (("m77", None), ("lumpall", lump)):
        add(f"S_{nm}_area", "5", lambda pt=pt: m77_area(pt), "DK", "HRVS")
        add(f"S_{nm}_city", "5", lambda pt=pt: m77_city(pt), MD, HA, n=f"S_{nm}_area")

    # ---------------- 6 power: Harappa-only stock in the M77 between pool at C1 size
    for q in PLANT_Q:
        add(f"P_old20_q{q}", "6", lambda: m77_city(), MD, HA, n="W1_md_area_C1", plant=("old20", q))
        add(f"P_new100_q{q}", "6", lambda: m77_city(), MD, HA, n="W1_md_area_C1", plant=("new100", q))

    # ---------------- planted-answer gates (s1 rule: same pool and size, labels permuted, rt.plant new100 q=0.15)
    for g in GATED:
        c = C[g]
        add("G_" + g, c["att"], c["build"], c["a"], c["b"], n=g, opg=c["opg"], plant=("gate", 0.15), cv=c["cv"])
    return C


GATED = ("W1_lb_Kn_hands_p0", "W1_lb_Py_hands_p0", "W1_lat_ge_rlp_vs_bwhe_namefree", "H_lb_serbal_handcv",
         "F_lb_namefree_frame", "F_ur3_ug_namefree_frame", "F_lat_namefree_frame", "L_md_area_confirmed")


# =========================================================================== machinery
_BUILT = {}


def built(name, C):
    if name not in _BUILT:
        _BUILT[name] = C[name]["build"]()
    return _BUILT[name]


def n_side_of(name, C):
    c = C[name]
    if isinstance(c["n"], int):
        return c["n"]
    if isinstance(c["n"], str):
        return n_side_of(c["n"], C)
    T = built(name, C)
    if c["opg"]:
        cnt = Counter(s for s, g in {(t["site"], t["group"]) for t in T})
    else:
        cnt = Counter(t["site"] for t in T)
    return min(cnt[c["a"]], cnt[c["b"]], N_MAX)


def plant_harappa(sample, kind, q, rng, common):
    """Real labels kept. Harappa texts only: each token replaced with prob q by a Harappa stock token.
    old20: 20 existing common signs (benchmark calib recipe, uniform). new100: 100 new symbols, Zipf (rt.plant)."""
    if kind == "old20":
        stock = list(rng.choice(common, 20, replace=False)); w = np.full(20, 1 / 20)
    else:
        stock = [f"Ha_{i}" for i in range(100)]
        w = (1 / np.arange(1, 101)) / (1 / np.arange(1, 101)).sum()
    out = []
    for t in sample:
        if t["site"] == HA:
            L = [[stock[rng.choice(len(stock), p=w)] if rng.random() < q else x for x in l] for l in t["lines"]]
            t = dict(t, lines=L)
        out.append(t)
    return out


def sizes():
    C = conditions()
    for name, c in C.items():
        try:
            T = built(name, C)
            cnt = Counter(t["site"] for t in T)
            print(f"{c['att']} {name:42s} {c['a']}={cnt[c['a']]} {c['b']}={cnt[c['b']]} n_side={n_side_of(name, C)}", flush=True)
        except Exception as e:
            print(f"{c['att']} {name:42s} ERROR {e!r}", flush=True)
    st, by_locus = findspot_status()
    print("findspot status", Counter(st.values()))
    print("findspot status by side", Counter((i and s, st[i]) for s in ("DK", "HRVS") for i in [t["id"] for t in s1.m77_seals(s1.lab_area) if t["site"] == s]))
    for loc in sorted(by_locus, key=str):
        print("  locus", loc, by_locus[loc].most_common(6))
    M = lbm()
    for site in (K, P):
        print(site, "hands", Counter(v["hand"] for v in M.values() if v["site"] == site).most_common(12))


def run(only=None):
    C = conditions()
    path = HERE / "draws.jsonl"
    done = Counter()
    if path.exists():
        for l in open(path):
            done[json.loads(l)["cond"]] += 1
    with open(path, "a") as f:
        for name, c in C.items():
            if only and not any(name.startswith(o) for o in only):
                continue
            if done[name] >= N_DRAWS:
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
                smp, short = ub.draw_n(T, a, b, rng, MIX, c["opg"], n_side, 2 * n_side)
                if smp is None:
                    rec = dict(cond=name, att=c["att"], draw=k, auc=None, n_side=n_side, avail=[cnt[a], cnt[b]])
                else:
                    if c["plant"] and c["plant"][0] == "gate":
                        smp = rt.plant(smp, "new100", c["plant"][1], rng, common)
                    elif c["plant"]:
                        smp = plant_harappa(smp, c["plant"][0], c["plant"][1], rng, common)
                    if c["cv"] == "hand":
                        smp = [dict(t, group=hand_of(t["group"])) for t in smp]
                    obs, nul, nf, nn = ub.score(smp, a, SEED + k)
                    rec = dict(cond=name, att=c["att"], draw=k, auc=obs, null_auc=nul, n_feat=nf, n=nn, n_side=n_side,
                               short=short, avail=[cnt[a], cnt[b]], **rt.describe(smp, a))
                    if c["cv"] == "hand":
                        rec["n_cv_groups"] = len({t["group"] for t in smp})
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
            out[name] = dict(att=rs[0]["att"], failed=len(rs), n_side=rs[0]["n_side"], avail=rs[0].get("avail"))
            continue
        a = np.array([r["auc"] for r in ok]); nu = np.array([r["null_auc"] for r in ok])
        d = dict(att=ok[0]["att"], n_side=ok[0]["n_side"], n_draws=len(ok), failed=len(rs) - len(ok),
                 median_auc=float(np.median(a)), lo=float(np.quantile(a, 0.025)), hi=float(np.quantile(a, 0.975)),
                 null_q95=float(np.quantile(nu, 0.95)), avail=ok[0]["avail"], _aucs=a.tolist())
        for k in ("types", "local_share", "mean_len"):
            d[k] = float(np.mean([r[k] for r in ok]))
        out[name] = d
    med = lambda n: out.get(n, {}).get("median_auc")
    # ---- attack 1 gap table
    gaps = {}
    def gap(label, between, withins):
        ws = [med(w) for w in withins if med(w) is not None]
        bs = [med(x) for x in (between if isinstance(between, list) else [between]) if med(x) is not None]
        if ws and bs:
            gaps[label] = dict(between=float(np.median(bs)), within=float(np.median(ws)),
                               delta=float(np.median(bs) - np.median(ws)),
                               within_each=[round(x, 3) for x in ws], between_each=[round(x, 3) for x in bs])
    for site in (K, P):
        s2 = site[:2]
        gap(f"LB whole, {site} hand groups", [f"B1_lb_whole_at_{s2}_p{p}" for p in range(N_HAND_PARTS)], [f"W1_lb_{s2}_hands_p{p}" for p in range(N_HAND_PARTS)])
        gap(f"LB series-balanced, {site} hand groups", [f"B1_lb_serbal_at_{s2}_p{p}" for p in range(N_HAND_PARTS)], [f"W1_lb_{s2}_hands_p{p}_serbal" for p in range(N_HAND_PARTS)])
        gap(f"LB name-free, {site} hand groups", [f"B1_lb_namefree_at_{s2}_p{p}" for p in range(N_HAND_PARTS)], [f"W1_lb_{s2}_hands_p{p}_namefree" for p in range(N_HAND_PARTS)])
        gap(f"LB whole, {site} random halves", [f"B1_lb_whole_at_{s2}_p{p}" for p in range(N_HAND_PARTS)], [f"W1_lb_{s2}_random"])
    for split in LAT_SPLITS:
        gap(f"Latin name-free, {split}", f"B1_lat_namefree_at_{split}", [f"W1_lat_{split}_namefree"])
        gap(f"Latin whole, {split}", f"B1_lat_whole_at_{split}", [f"W1_lat_{split}_whole"])
    gap("Indus M77, MD DK vs HR+VS", "B1_md_h_at_C1", ["W1_md_area_C1"])
    gap("Indus M77, MD random halves", "B1_md_h_at_C1", ["W1_md_random"])
    gap("Indus M77, findspot-confirmed only", "L_md_h_at_confirmed", ["L_md_area_confirmed"])
    gap("Indus M77, cross-split near copies dropped", "L_md_h_xnear", ["L_md_area_xnear"])
    gap("Indus M77, frame removed", "F_m77_city_frame_at_area", ["F_m77_area_frame"])
    for nm in ("raw", "A1", "A2"):
        gap(f"Indus ICIT {nm}, CISI area split", f"S_icit_{nm}_city", [f"S_icit_{nm}_area"])
    for nm in ("m77", "lumpall"):
        gap(f"Indus {nm}, M77 area split", f"S_{nm}_city", [f"S_{nm}_area"])
    # ---- attack 6 power: share of planted draws with between - within >= MARGIN
    w_aucs = out.get("W1_md_area_C1", {}).get("_aucs")
    w_med = med("W1_md_area_C1")
    power = {}
    for name in C:
        if name.startswith("P_") and name in out and "_aucs" in out[name] and w_aucs:
            pa = np.array(out[name]["_aucs"])
            power[name] = dict(median=out[name]["median_auc"],
                               vs_within_median=float(np.mean(pa - w_med >= MARGIN)),
                               vs_within_paired=float(np.mean(pa - np.array(w_aucs[:len(pa)]) >= MARGIN)),
                               median_delta_meets=bool(out[name]["median_auc"] - w_med >= MARGIN))
    gates = {}
    for g in GATED:
        if "G_" + g in out and "_aucs" in out["G_" + g] and g in out:
            thr = max(0.65, out[g].get("null_q95", 0.0))
            rate = float(np.mean(np.array(out["G_" + g]["_aucs"]) >= thr))
            out[g]["gate_detect_rate"] = rate; out[g]["gate_pass"] = rate >= 0.8
            gates[g] = dict(rate=rate, thr=thr)
    for d in out.values():
        d.pop("_aucs", None)
    out["_gates"] = gates
    out["_gaps"] = gaps
    out["_power"] = power
    st, by_locus = findspot_status()
    out["_findspot"] = dict(status=dict(Counter(st.values())),
                            by_side={s: dict(Counter(st[t["id"]] for t in s1.m77_seals(s1.lab_area) if t["site"] == s)) for s in ("DK", "HRVS")},
                            by_locus={str(k): dict(v.most_common(8)) for k, v in by_locus.items()})
    for nm, (bld, a, b) in {"area_C1": (m77_area, "DK", "HRVS"), "city": (m77_city, MD, HA)}.items():
        T = bld()
        out["_findspot"][f"cross_near_ge2_{nm}"] = cross_near_count(T, a, b, 2)
        out["_findspot"][f"cross_near_ge3_{nm}"] = cross_near_count(T, a, b, 3)
        out["_findspot"][f"texts_{nm}"] = dict(Counter(t["site"] for t in T))
    lib.jdump(out, HERE / "results.json")
    lines = ["| attack | condition | n per side | median AUC | 2.5-97.5% | null q95 | types | local share |",
             "|---|---|---|---|---|---|---|---|"]
    for name in C:
        d = out.get(name)
        if not d:
            continue
        if "median_auc" not in d:
            lines.append(f"| {d['att']} | {name} | {d['n_side']} | failed (avail {d.get('avail')}) | | | | |")
            continue
        lines.append(f"| {d['att']} | {name} | {d['n_side']} | {d['median_auc']:.3f} | {d['lo']:.3f}-{d['hi']:.3f} | "
                     f"{d['null_q95']:.3f} | {d['types']:.0f} | {d['local_share']:.3f} |")
    lines += ["", "| corpus / split | between | within | between - within |", "|---|---|---|---|"]
    for k, g in gaps.items():
        lines.append(f"| {k} | {g['between']:.3f} | {g['within']:.3f} | {g['delta']:+.3f} |")
    lines += ["", "| power condition | median | share of draws between - within >= 0.05 (vs within median) | (paired draws) |", "|---|---|---|---|"]
    for k, p in power.items():
        lines.append(f"| {k} | {p['median']:.3f} | {p['vs_within_median']:.0%} | {p['vs_within_paired']:.0%} |")
    (HERE / "table.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(json.dumps(out["_findspot"], indent=1, ensure_ascii=False))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "sizes"
    if mode == "run":
        run(sys.argv[2:] or None)
    else:
        {"sizes": sizes, "report": report}[mode]()
