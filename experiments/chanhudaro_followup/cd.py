"""Chanhu-daro follow-up (prereg docs/prereg/chanhudaro_followup.md).

Is Chanhu-daro's difference from Mohenjo-daro / Harappa place, period, a few repeated seals / one findspot,
a few signs, or iconography / format? Every condition runs through the benchmark's own clean() + draw_n() +
score() with step-2 pools (s2.py); near-copy de-dup is clean() (fish_tick_closer_v2/dedup.py) and the
red-team strict_clean() (dedup.greedy with MIN_DROP = 2 + sign multiset). No new classifier.

  board/run.sh .venv/bin/python -I experiments/chanhudaro_followup/cd.py sizes
  board/run.sh .venv/bin/python -I experiments/chanhudaro_followup/cd.py run main     # T0-T2, T4, T5
  board/run.sh .venv/bin/python -I experiments/chanhudaro_followup/cd.py run loso     # T3 stage 1
  board/run.sh .venv/bin/python -I experiments/chanhudaro_followup/cd.py run drivers  # T3 stage 2 (rule-based)
  .venv/bin/python -I experiments/chanhudaro_followup/cd.py report
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
sys.path.insert(0, str(ROOT / "experiments/redteam_uniformity_step2"))
import rt2  # noqa: E402  (imports s2, s1, ub, rt, lib; strict_clean)

s2, s1, ub, rt, lib = rt2.s2, rt2.s1, rt2.ub, rt2.rt, rt2.lib
MD, HA, CD = "Mohenjo-daro", "Harappa", "Chanhu-daro"
SEED = 20261128
N_MAIN = 200      # T0 baseline: per-draw permuted AUCs give p resolution 1/201
N_TEST = 50
N_LOSO = 30
MIX = s2.MIX
MARGIN = 0.05
GATE_Q = 0.15
JHUKAR_FT = 13.7  # Mackay 1943: Jhukar floors on Mound II at +13.7 to +15.8 ft and objects up to +22.7 ft
LOSO_MIN = 5      # signs with >= 5 tokens on the Chanhu-daro side
DRIVER = 0.03     # median AUC drop that marks a driver sign
PAIRS = [("m77_seal", HA), ("m77_seal", MD), ("icit_sealtype", HA), ("icit_sealtype", MD)]


def _cache(k, f, _C={}):
    if k not in _C:
        _C[k] = f()
    return _C[k]


# =========================================================================== Chanhu-daro metadata (M77 texts)
def cd_meta():
    """text_no -> dict(depth, mound1, square) from the Mackay 1943 register (experiments/old_registers), else
    the M77 level (whole feet)."""
    def f():
        out = {}
        for r in csv.DictReader(open(ROOT / "experiments/old_registers/registers.csv", encoding="utf-8")):
            if "1943" not in r["source"] or not r["m77_text_no"]:
                continue
            d = r["depth_ft"].strip()
            fs = re.sub(r"\s+", " ", r["findspot"])
            sq = re.search(r"[Ss]q\. ?([0-9lo]+/[A-Z])", fs)
            out[int(float(r["m77_text_no"]))] = dict(
                depth=float(d) if re.fullmatch(r"[+-]?\d+(\.\d+)?", d) else None,
                mound1=bool(re.search(r"Mound I\b(?!I)", fs)), square=sq.group(1).replace("l", "1").replace("o", "0") if sq else None,
                src="register")
        meta = s1.m77_meta()
        for t in s2.m77_texts():
            if t["site"] != "Chanhudaro" or t["text_no"] in out:
                continue
            loc, lev = meta.get(t["text_no"], (None, None))
            out[t["text_no"]] = dict(depth=float(lev) if lev and re.fullmatch(r"-?\d+", lev) else None, mound1=False,
                                     square=None, src="m77")
        return out
    return _cache("meta", f)


def tno(i):
    return int(i[1:].split(".")[0])


def is_jhukar(i):
    m = cd_meta().get(tno(i), {})
    return (m.get("src") == "register" and m.get("depth") is not None and m["depth"] >= JHUKAR_FT
            and not m.get("mound1"))


def top_square():
    c = Counter(m["square"] for m in cd_meta().values() if m.get("square"))
    return c.most_common(1)[0][0]


# =========================================================================== pools
def raw_pair(fam, big):
    return [x for x in s2.indus_raw(fam) if x["site"] in (big, CD)]


def base(fam, big):
    return ub.clean(raw_pair(fam, big))


def within_big(fam, big):
    return s2.indus_within(fam, big)


def harappan_only(fam, big):
    return ub.clean([x for x in raw_pair(fam, big) if x["site"] != CD or not is_jhukar(x["id"])])


def strict(fam, big):
    return rt2.strict_clean(raw_pair(fam, big))


def drop_square(fam, big):
    sq = top_square()
    return ub.clean([x for x in raw_pair(fam, big) if x["site"] != CD or cd_meta().get(tno(x["id"]), {}).get("square") != sq])


def has_depth(i):
    m = cd_meta().get(tno(i), {})
    return m.get("src") == "register" and m.get("depth") is not None and not m.get("mound1")


def cd_depth_within():
    """Chanhu-daro deep vs shallow: M77 seals with a Mackay 1943 register depth (feet vs datum), Mound II only,
    split at the median depth. M77 level numbers are not used (unknown datum)."""
    R = [x for x in s2.indus_raw("m77_seal") if x["site"] == CD]
    ds = [cd_meta()[tno(x["id"])]["depth"] for x in R if has_depth(x["id"])]
    med = float(np.median(ds))
    T = []
    for x in R:
        if not has_depth(x["id"]):
            continue
        T.append(dict(x, site="deep" if cd_meta()[tno(x["id"])]["depth"] <= med else "shallow"))
    return ub.clean(T)


def icit_symbol_map():
    return _cache("sym", lambda: {t["id"]: (t["symbol"] or "") for t in s2.icit_texts()})


def unicorn_only(big):
    sym = icit_symbol_map()
    return ub.clean([x for x in raw_pair("icit_sealtype", big) if sym.get(x["id"], "").startswith("Bull1")])


def unicorn_within(big):
    sym = icit_symbol_map()
    return ub.clean([dict(x, site=s2.half(x["id"])) for x in s2.indus_raw("icit_sealtype")
                     if x["site"] == big and sym.get(x["id"], "").startswith("Bull1")])


def md_symbol_floor():
    """Format floor: Mohenjo-daro unicorn seals vs Mohenjo-daro seals with no field symbol."""
    sym = icit_symbol_map()
    T = []
    for x in s2.indus_raw("icit_sealtype"):
        if x["site"] != MD:
            continue
        s = sym.get(x["id"], "")
        lab = "unicorn" if s.startswith("Bull1") else ("nosymbol" if s == "None" else None)
        if lab:
            T.append(dict(x, site=lab))
    return ub.clean(T)


def drop_signs(T, signs):
    S = set(signs)
    out = []
    for t in T:
        L = [[w for w in l if w not in S] for l in t["lines"]]
        L = [l for l in L if l]
        if L:
            out.append(dict(id=t["id"], site=t["site"], lines=L, group=t["group"]))
    return ub.clean(out)


def loso_signs(fam, big):
    T = base(fam, big)
    c = Counter(w for t in T if t["site"] == CD for l in t["lines"] for w in l)
    return sorted(s for s, k in c.items() if k >= LOSO_MIN)


# =========================================================================== conditions
def tag(fam, big):
    return f"{fam}|{big}"


def conditions(stage):
    C = {}

    def add(name, build, a, b, n=None, plant=None, draws=N_TEST, **info):
        C[name] = dict(build=build, a=a, b=b, n=n, plant=plant, draws=draws, info=info)

    if stage == "main":
        for fam, big in PAIRS:
            tg = tag(fam, big)
            nn = ("match", f"W0_{tg}", f"B0_{tg}")
            add(f"W0_{tg}", lambda fam=fam, big=big: within_big(fam, big), "X", "Y", n=nn, draws=N_MAIN, test="T0", role="within")
            add(f"B0_{tg}", lambda fam=fam, big=big: base(fam, big), big, CD, n=nn, draws=N_MAIN, test="T0", role="between")
            add(f"P0_{tg}", lambda fam=fam, big=big: base(fam, big), big, CD, n=f"B0_{tg}", plant=("side", CD, GATE_Q),
                test="T0", role="power")
            for key, fn in (("T2", strict), ("T5", drop_square)) + ((("T1", harappan_only),) if fam == "m77_seal" else ()):
                add(f"B{key}_{tg}", lambda fam=fam, big=big, fn=fn: fn(fam, big), big, CD,
                    n=("match", f"W0_{tg}", f"B{key}_{tg}"), test=key, role="between")
        # T1b Chanhu-daro deep vs shallow floor, with Harappa / Mohenjo-daro vs Chanhu-daro at the same n
        add("W1_cdDepth", cd_depth_within, "deep", "shallow", n=("match", "W1_cdDepth", "B0_m77_seal|Harappa"),
            test="T1b", role="within")
        for big in (HA, MD):
            add(f"B1_cdDepth|{big}", lambda big=big: base("m77_seal", big), big, CD, n="W1_cdDepth", test="T1b", role="between")
            add(f"G1_cdDepth|{big}", lambda big=big: base("m77_seal", big), big, CD, n="W1_cdDepth",
                plant=("side", CD, GATE_Q), test="T1b", role="power")
        # T4 iconography / format
        for big in (HA, MD):
            nn = ("match", f"W4_{big}", f"B4_{big}")
            add(f"W4_{big}", lambda big=big: unicorn_within(big), "X", "Y", n=nn, test="T4", role="within")
            add(f"B4_{big}", lambda big=big: unicorn_only(big), big, CD, n=nn, test="T4", role="between")
            add(f"P4_{big}", lambda big=big: unicorn_only(big), big, CD, n=f"B4_{big}", plant=("side", CD, GATE_Q),
                test="T4", role="power")
        add("F4_mdSymbol", md_symbol_floor, "unicorn", "nosymbol", n=("match", "B0_icit_sealtype|Harappa", "B0_icit_sealtype|Harappa"),
            test="T4b", role="floor")
    elif stage == "loso":
        for fam, big in PAIRS[:2]:
            tg = tag(fam, big)
            for s in loso_signs(fam, big):
                add(f"L_{tg}|{s}", lambda fam=fam, big=big, s=s: drop_signs(base(fam, big), [s]), big, CD,
                    n=f"B0_{tg}", draws=N_LOSO, test="T3", role="loso", sign=s, base=f"B0_{tg}")
            add(f"LB_{tg}", lambda fam=fam, big=big: base(fam, big), big, CD, n=f"B0_{tg}", draws=N_LOSO, test="T3",
                role="loso_base")
    elif stage == "loso2":
        # Deviation 1: L_ conditions with no valid draw (dropping the sign merged 1-3 Chanhu-daro texts under
        # clean(), so the side fell below the fixed n) are rescored at their own natural n, against an
        # unmanipulated baseline drawn at that same n.
        S = load()
        for fam, big in PAIRS[:2]:
            tg = tag(fam, big)
            for s in loso_signs(fam, big):
                if "median" in S.get(f"L_{tg}|{s}", {}):
                    continue
                T = drop_signs(base(fam, big), [s])
                cnt = Counter(t["site"] for t in T)
                nd = min(cnt[big], cnt[CD], s2.N_MAX)
                add(f"L2_{tg}|{s}", lambda T=T: T, big, CD, n=nd, draws=N_LOSO, test="T3", role="loso", sign=s,
                    base=f"LB2_{tg}|{nd}")
                add(f"LB2_{tg}|{nd}", lambda fam=fam, big=big: base(fam, big), big, CD, n=nd, draws=N_LOSO,
                    test="T3", role="loso_base")
    elif stage in ("drivers", "drivers2"):
        D = drivers()
        if stage == "drivers2":
            old = drivers(only_l=True)   # the set the original drivers stage used (BD_)
            D = {k: v for k, v in D.items() if v and v != old.get(k)}
        for fam, big in PAIRS:
            tg = tag(fam, big)
            ds = D.get(tag("m77_seal", big), [])
            if not ds:
                continue
            if fam == "m77_seal":
                add(f"{'BD2' if stage == 'drivers2' else 'BD'}_{tg}", lambda fam=fam, big=big, ds=ds: drop_signs(base(fam, big), ds), big, CD,
                    n=("match", f"W0_{tg}", f"{'BD2' if stage == 'drivers2' else 'BD'}_{tg}"), test="T3b", role="between", signs=ds)
    return C


# =========================================================================== machinery
_BUILT = {}
ALL = {}


def all_conditions():
    if not ALL:
        for st in ("main", "loso", "loso2"):
            ALL.update(conditions(st))
    return ALL


def built(name, C):
    if name not in _BUILT:
        _BUILT[name] = C[name]["build"]()
    return _BUILT[name]


def natural_n(name, C):
    c = C[name]
    cnt = Counter(t["site"] for t in built(name, C))
    return min(cnt[c["a"]], cnt[c["b"]], s2.N_MAX)


def n_side_of(name, C):
    n = C[name]["n"]
    if n is None:
        return natural_n(name, C)
    if isinstance(n, int):
        return n
    if isinstance(n, str):
        return n_side_of(n, C)
    return min(natural_n(x, C) for x in n[1:])


def merged(stage):
    C = dict(all_conditions())
    C.update(conditions(stage))
    return C


def sizes():
    C = merged("main")
    for name, c in C.items():
        if c["info"].get("role") in ("power", "loso"):
            continue
        cnt = Counter(t["site"] for t in built(name, C))
        print(f"{name:40s} {c['a']}={cnt[c['a']]} {c['b']}={cnt[c['b']]} n_side={n_side_of(name, C)}", flush=True)
    M = cd_meta()
    ids = [x["id"] for x in s2.indus_raw("m77_seal") if x["site"] == CD]
    print("CD m77 seals", len(ids), "register", sum(M.get(tno(i), {}).get("src") == "register" for i in ids),
          "with register depth", sum(has_depth(i) for i in ids),
          "jhukar-level", sum(is_jhukar(i) for i in ids), "top square", top_square(),
          "in it", sum(M.get(tno(i), {}).get("square") == top_square() for i in ids))
    for fam, big in PAIRS[:2]:
        print("loso signs", fam, big, len(loso_signs(fam, big)))


def run(stage):
    C = merged(stage)
    path = HERE / "draws.jsonl"
    done = Counter()
    if path.exists():
        for l in open(path):
            done[json.loads(l)["cond"]] += 1
    mine = set(conditions(stage)) if stage not in ("loso2",) else {k for k in C if k.startswith(("L2_", "LB2_"))}
    with open(path, "a") as f:
        for name, c in C.items():
            if name not in mine or done[name] >= c["draws"]:
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
            for k in range(done[name], c["draws"]):
                rng = np.random.default_rng([SEED, k, zlib.crc32(name.encode())])
                smp = None
                if n_side >= 5:
                    smp, short = ub.draw_n(T, a, b, rng, MIX, False, n_side, 2 * n_side)
                if smp is None:
                    rec = dict(cond=name, draw=k, auc=None, n_side=n_side, avail=[cnt[a], cnt[b]])
                else:
                    if c["plant"]:
                        smp = s2.plant_side(smp, c["plant"][1], c["plant"][2], rng, common)
                    obs, nul, nf, nn = ub.score(smp, a, SEED + k)
                    rec = dict(cond=name, draw=k, auc=obs, null_auc=nul, n_side=n_side, avail=[cnt[a], cnt[b]], local_share=0.0)
                f.write(json.dumps(rec) + "\n"); f.flush()
            print(name, "n", n_side, "done", rec.get("auc"), flush=True)


# =========================================================================== report
def load():
    by = {}
    p = HERE / "draws.jsonl"
    if p.exists():
        for l in open(p):
            r = json.loads(l); by.setdefault(r["cond"], []).append(r)
    return {k: rt2.summ(v) for k, v in by.items()}


def drivers(only_l=False):
    """T3 stage-1 rule: a sign is a driver if removing it lowers the median between AUC by >= DRIVER against the
    30-draw unmanipulated baseline (LB_)."""
    S = load()
    out = {}
    for fam, big in PAIRS[:2]:
        tg = tag(fam, big)
        b = S.get(f"LB_{tg}", {}).get("median")
        if b is None:
            continue
        ds = [(d, s) for s, d, _ in loso_drops(S, tg, only_l) if d >= DRIVER]
        out[tg] = [s for _, s in sorted(ds, reverse=True)]
    return out


def loso_drops(S, tg, only_l=False):
    """(sign, drop, n) for every scored leave-one-sign-out condition; L_ against LB_, else (deviation 1) L2_
    against LB2_ at the same n."""
    out = []
    b = S.get(f"LB_{tg}", {}).get("median")
    for k, v in S.items():
        if k.startswith(f"L_{tg}|") and "median" in v and b is not None:
            out.append((k.split("|")[-1], b - v["median"], v["n_side"]))
        elif k.startswith(f"L2_{tg}|") and "median" in v and not only_l:
            b2 = S.get(f"LB2_{tg}|{v['n_side']}", {}).get("median")
            if b2 is not None:
                out.append((k.split("|")[-1], b2 - v["median"], v["n_side"]))
    return out


def sign_profile(signs):
    """Classifier-free: share of texts containing the sign, and share where it is the first / last sign, per site
    (M77 seals, raw complete texts)."""
    R = s2.indus_raw("m77_seal")
    out = {}
    for s in signs:
        row = {}
        for site in (CD, HA, MD):
            X = [x for x in R if x["site"] == site]
            flat = [[w for l in x["lines"] for w in l] for x in X]
            row[site] = dict(n=len(X), has=float(np.mean([s in f for f in flat])),
                             first=float(np.mean([bool(f) and f[0] == s for f in flat])),
                             last=float(np.mean([bool(f) and f[-1] == s for f in flat])))
        out[s] = row
    return out


def report():
    S = load()
    C = merged("main")
    R = {}
    T0 = []
    for fam, big in PAIRS:
        tg = tag(fam, big)
        b, w, p = S.get(f"B0_{tg}"), S.get(f"W0_{tg}"), S.get(f"P0_{tg}")
        if not (b and w and "median" in b and "median" in w):
            continue
        ref = max(w["median"], b["null_med"])
        T0.append(dict(pair=tg, n_side=b["n_side"], between=b["median"], within=w["median"], null_med=b["null_med"],
                       d_floor=b["median"] - w["median"], d_null=b["median"] - b["null_med"], d_cons=b["median"] - ref,
                       p_floor=rt2.pfloor(S, f"W0_{tg}", f"B0_{tg}"), p_chance=b["p_chance"],
                       power=float(np.mean(p["_a"] - ref >= MARGIN)) if p and "_a" in p else None))
    for r, q in zip(T0, rt2.bh([r["p_chance"] for r in T0])):
        r["q_chance"] = q
        r["distinct"] = r["d_cons"] >= MARGIN and q <= 0.05 and (r["power"] or 0) >= 0.8
    nd = sum(r["distinct"] for r in T0)
    R["T0"] = T0
    R["T0_verdict"] = "distinct" if nd >= 3 else ("not distinct" if nd <= 1 else "equivocal")
    base_ref = {r["pair"]: r for r in T0}
    tests = {}
    for key in ("T1", "T2", "T5", "T3b"):
        rows = []
        for fam, big in PAIRS:
            tg = tag(fam, big)
            nm = f"B{'D' if key == 'T3b' else key}_{tg}"
            if key == "T3b" and f"BD2_{tg}" in S:
                nm = f"BD2_{tg}"
            if nm not in S or "median" not in S[nm] or tg not in base_ref:
                continue
            b0 = base_ref[tg]
            ref = max(b0["within"], S[nm]["null_med"])
            d = S[nm]["median"] - ref
            rows.append(dict(pair=tg, n_side=S[nm]["n_side"], between=S[nm]["median"], d_cons=d, base_d_cons=b0["d_cons"],
                             p_chance=S[nm]["p_chance"],
                             accounts=(d < MARGIN) or (b0["d_cons"] - d >= b0["d_cons"] / 2)))
        tests[key] = rows
    # T1b depth floor
    if "W1_cdDepth" in S and "median" in S["W1_cdDepth"]:
        wd = S["W1_cdDepth"]["median"]; rows = []
        for big in (HA, MD):
            b, g = S.get(f"B1_cdDepth|{big}"), S.get(f"G1_cdDepth|{big}")
            if b and "median" in b:
                pw = float(np.mean(g["_a"] - wd >= MARGIN)) if g and "_a" in g else None
                rows.append(dict(big=big, n_side=b["n_side"], between=b["median"], cd_depth_within=wd,
                                 d=b["median"] - wd, power=pw,
                                 verdict=("underpowered" if (pw or 0) < 0.8 else
                                          "depth floor matches" if b["median"] - wd < MARGIN else "above depth floor")))
        tests["T1b"] = rows
    # T4
    rows = []
    for big in (HA, MD):
        b, w, p = S.get(f"B4_{big}"), S.get(f"W4_{big}"), S.get(f"P4_{big}")
        if b and w and "median" in b and "median" in w:
            ref = max(w["median"], b["null_med"])
            pair0 = base_ref.get(tag("icit_sealtype", big), {})
            rows.append(dict(big=big, n_side=b["n_side"], between=b["median"], within=w["median"], null_med=b["null_med"],
                             d_cons=b["median"] - ref, base_d_cons=pair0.get("d_cons"), p_chance=b["p_chance"],
                             power=float(np.mean(p["_a"] - ref >= MARGIN)) if p and "_a" in p else None,
                             accounts=pair0.get("d_cons") is not None and ((b["median"] - ref < MARGIN) or
                                                                           (pair0["d_cons"] - (b["median"] - ref) >= pair0["d_cons"] / 2))))
    tests["T4"] = rows
    if "F4_mdSymbol" in S and "median" in S["F4_mdSymbol"]:
        tests["T4b"] = dict(n_side=S["F4_mdSymbol"]["n_side"], md_unicorn_vs_nosymbol=S["F4_mdSymbol"]["median"],
                            null_med=S["F4_mdSymbol"]["null_med"])
    R["tests"] = tests
    # T3
    loso = {}
    for fam, big in PAIRS[:2]:
        tg = tag(fam, big)
        b = S.get(f"LB_{tg}", {}).get("median")
        rows = sorted(loso_drops(S, tg), key=lambda r: -r[1])
        loso[tg] = dict(base=b, rows=[dict(sign=s, drop=d, n_side=n) for s, d, n in rows], n_signs=len(rows))
    R["T3_loso"] = loso
    D = drivers()
    R["T3_drivers"] = D
    sig = sorted({s for v in D.values() for s in v} | {"M93"})
    R["sign_profile"] = sign_profile(sig)
    # explanation verdicts (prereg rules)
    expl = {}
    for key, nm in (("T1", "period (Jhukar levels)"), ("T2", "repeated seals / near copies"),
                    ("T5", "one findspot (largest square)"), ("T3b", "a few signs")):
        rows = tests.get(key, [])
        m77 = [r for r in rows if r["pair"].startswith("m77_seal")]
        expl[nm] = ("not run" if not m77 else "accounts" if all(r["accounts"] for r in m77) else
                    "partly" if any(r["accounts"] for r in m77) else "does not account")
    t4 = tests.get("T4", [])
    expl["iconography / format (unicorn-only)"] = ("not run" if not t4 else
                                                   "underpowered" if any((r["power"] or 0) < 0.8 for r in t4) else
                                                   "accounts" if all(r["accounts"] for r in t4) else
                                                   "partly" if any(r["accounts"] for r in t4) else "does not account")
    t1b = tests.get("T1b", [])
    expl["within-Chanhu-daro depth floor"] = ("not run" if not t1b else
                                              "underpowered" if any(r["verdict"] == "underpowered" for r in t1b) else
                                              "accounts" if all(r["verdict"] == "depth floor matches" for r in t1b) else
                                              "does not account")
    R["explanations"] = expl
    if R["T0_verdict"] == "not distinct":
        final = "NO ROBUST DIFFERENCE: Chanhu-daro is not distinct from the big cities beyond chance"
    else:
        acc = [k for k, v in expl.items() if v == "accounts"]
        under = [k for k, v in expl.items() if v == "underpowered"]
        if acc:
            final = "EXPLAINED BY: " + "; ".join(acc)
        elif under:
            final = "PLACE NOT EXCLUDED; untested alternatives underpowered: " + "; ".join(under)
        else:
            final = "PLACE: distinct, and no tested alternative accounts for it"
        if R["T0_verdict"] == "equivocal":
            final = "EQUIVOCAL BASELINE; " + final
    R["final"] = final
    R["conditions"] = {k: {kk: vv for kk, vv in v.items() if not kk.startswith("_")} for k, v in S.items()}
    lib.jdump(R, HERE / "results.json")
    print(json.dumps({k: v for k, v in R.items() if k != "conditions"}, indent=1, default=str))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "sizes"
    if mode == "run":
        run(sys.argv[2])
    else:
        {"sizes": sizes, "report": report}[mode]()
