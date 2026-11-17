"""Step 2: do detached-class signs go with non-textual covariates beyond their frequency?
Pre-registered: docs/prereg/detached_signs.md (hashed with this file before it was run).
Run: .venv/bin/python -I experiments/detached_signs/d2_covariates.py
"""
import csv, json, math, sys
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ds_lib import *  # noqa
from corpus.load import icit_texts, m77_texts, distinct, dev_heldout  # noqa

OUT = Path(__file__).parent
SEED = 20261114
NCTRL = 2000
CLASS_M = ["M242", "M374", "M93", "M326", "M393"]          # frozen from d1 (dev only)
CLASS_W = ["W621", "W790", "W384"]                          # bridge images (M93, M393 have none)
CORE_M = ["M242", "M374", "M393"]                           # secondary: layout-replicated core
CORE_W = ["W621", "W790"]

# ---------------- objects used by earlier leads (confirmatory exclusion) ----------------
SCENE_CODED = {r["cisi"] for r in csv.DictReader(open(ROOT / "experiments/scene_text/scene_codes_objects.csv"))}
SCENE_TEXT_HITS = {"M-295", "M-296", "M-306", "M-310", "M-1186"}


def lenbin(n):
    return n if n <= 5 else (6 if n <= 7 else 8)


def nsig(seq):
    return sum(1 for s in seq if s not in ("|", "#"))


# ---------------- unit builders ----------------
def m77_units(texts, exclude_overlap):
    out = []
    for t in texts:
        signs = set(s for s in t["seq"] if s not in ("|", "#"))
        if not signs:
            continue
        fs = t.get("fs_category")
        scene = fs in ("Scenes", "Anthropomorphic forms")
        animal = fs == "Animals"
        if exclude_overlap and "M242" in signs and fs == "Scenes" and t["object_type"] in ("seal", "sealing"):
            continue  # logograms hit: M242 x scene field (fs80 600-810)
        out.append(dict(signs=signs, site=t["site"], nlen=nsig(t["seq"]), multi=t["n_lines"] > 1,
                        otype=t["object_type"], icon=("scene" if scene else "animal" if animal else None)
                        if t["object_type"] in ("seal", "sealing") else None,
                        material=None, logarea=None))
    return out


ANIMAL = {"Bull1", "Bull", "Bull2", "Bull3", "Bult", "Gaur", "Elep", "Gavi", "Zebu", "Rhin", "Goat", "Tigr",
          "Buff", "Comp", "CompBull", "Hare", "Mult", "Htgr", "Ass", "Turt", "Bird", "Fish", "Gavi+Bult"}


def icit_otype(ty):
    p = ty.split(":")
    if p[0] == "TAB" and len(p) > 1:
        return "TAB:" + p[1]
    if p[0] in ("SEAL", "TAG", "POT", "BNGL", "ROD", "IMPL"):
        return p[0]
    return "OTHER"


def icit_material(m):
    m = m.strip().lower()
    if m in ("", "-"):
        return None
    if m in ("clay", "terracotta", "ceramic"):
        return "clay"
    if m in ("steatite", "faience", "copper", "stoneware"):
        return m
    if m in ("ivory", "bone"):
        return "ivory/bone"
    return "other"


def fnum(x):
    try:
        return float(x)
    except Exception:
        return 0.0


def icit_units(texts, exclude_overlap):
    out = []
    for t in texts:
        signs = set(s for s in t["seq"] if s not in ("|", "#"))
        if not signs:
            continue
        if exclude_overlap and (t["type"] == "BNGL" or t["cisi"] in SCENE_CODED or t["cisi"] in SCENE_TEXT_HITS):
            continue
        sym = t["symbol"].split(":")[0]
        ot = icit_otype(t["type"])
        icon = None
        if ot in ("SEAL", "TAG"):
            icon = "scene" if sym in ("Scene", "Anth") else "animal" if sym in ANIMAL else None
        w, h = fnum(t["width_mm"]), fnum(t["height_mm"])
        la = math.log(w * h) if (t["type"] == "SEAL:S" and w > 5 and h > 5) else None
        out.append(dict(signs=signs, site=t["site"], nlen=nsig(t["seq"]), multi="|" in t["seq"], otype=ot,
                        icon=icon, material=icit_material(t["material"]), logarea=la))
    return out


# ---------------- statistics ----------------
def stratum(u):
    return (u["site"], lenbin(u["nlen"]), u["multi"])


def carriers(units, cls):
    cls = set(cls)
    return np.array([bool(u["signs"] & cls) for u in units])


def stat_binary(units, c, key, level):
    """one-sided z for 'carriers have covariate==level more than their stratum mates'. Units with covariate None dropped."""
    idx = [i for i, u in enumerate(units) if u[key] is not None]
    by = defaultdict(list)
    for i in idx:
        by[stratum(units[i])].append(i)
    O = E = V = 0.0
    for s, ii in by.items():
        x = np.array([units[i][key] == level for i in ii], float); cc = c[ii]
        N, k, m = len(ii), cc.sum(), x.sum()
        if N < 2 or k == 0:
            continue
        O += (cc * x).sum(); E += k * m / N
        V += k * (m / N) * (1 - m / N) * (N - k) / (N - 1)
    z = (O - E) / math.sqrt(V) if V > 0 else 0.0
    return z, O, E


def stat_omni(units, c, key):
    idx = [i for i, u in enumerate(units) if u[key] is not None]
    by = defaultdict(list)
    for i in idx:
        by[stratum(units[i])].append(i)
    O = Counter(); E = Counter()
    for s, ii in by.items():
        cc = c[ii]; k = cc.sum(); N = len(ii)
        if k == 0:
            continue
        cnt = Counter(units[i][key] for i in ii)
        for lev, m in cnt.items():
            E[lev] += k * m / N
        for i in ii:
            if c[i]:
                O[units[i][key]] += 1
    G = sum((O[l] - E[l]) ** 2 / E[l] for l in E if E[l] > 0)
    return G, dict(O), {l: round(v, 2) for l, v in E.items()}


def stat_size(units, c):
    idx = [i for i, u in enumerate(units) if u["logarea"] is not None]
    by = defaultdict(list)
    for i in idx:
        by[stratum(units[i])].append(i)
    res = []
    for s, ii in by.items():
        if len(ii) < 2:
            continue
        a = np.array([units[i]["logarea"] for i in ii]); m = a.mean()
        for j, i in enumerate(ii):
            if c[i]:
                res.append(a[j] - m)
    return (float(np.mean(res)) if res else 0.0), len(res)


def control_sets(units, cls, rng, n=NCTRL):
    cnt = Counter(s for u in units for s in u["signs"])
    cls = [s for s in cls if cnt[s] > 0]
    pool = [s for s in cnt if s not in set(CLASS_M) | set(CLASS_W)]
    cand = {}
    for s in cls:
        ns = cnt[s]
        c = [x for x in pool if max(1, 0.7 * ns - 1) <= cnt[x] <= 1.3 * ns + 1]
        if len(c) < 5:
            c = sorted(pool, key=lambda x: abs(cnt[x] - ns))[:10]
        cand[s] = c
    sets = []
    for _ in range(n):
        used = set(); st = []
        for s in cls:
            opts = [x for x in cand[s] if x not in used]
            x = opts[rng.integers(len(opts))]; used.add(x); st.append(x)
        sets.append(st)
    return sets, {s: cnt[s] for s in cls}


def run_test(units, cls, kind, rng, **kw):
    c = carriers(units, cls)
    f = {"binary": lambda cc: stat_binary(units, cc, kw["key"], kw["level"])[0],
         "omni": lambda cc: stat_omni(units, cc, kw["key"])[0],
         "size": lambda cc: stat_size(units, cc)[0]}[kind]
    if kind == "binary":
        z, O, E = stat_binary(units, c, kw["key"], kw["level"]); detail = dict(O=O, E=round(E, 2), z=round(z, 2))
        obs = z
    elif kind == "omni":
        G, O, E = stat_omni(units, c, kw["key"]); detail = dict(G=round(G, 2), O=O, E=E); obs = G
    else:
        m, n = stat_size(units, c); detail = dict(mean_resid_logarea=round(m, 3), n_carriers_with_size=n); obs = m
    sets, cnts = control_sets(units, cls, rng)
    null = np.array([f(carriers(units, s)) for s in sets])
    p = (1 + np.sum(null >= obs - 1e-12)) / (1 + len(null))
    detail.update(n_units=len(units), n_carriers=int(c.sum()), class_token_counts=cnts, p_ctrl=float(p),
                  null_mean=float(null.mean()), null_p95=float(np.quantile(null, 0.95)))
    return detail, null


def power(units, cls, kind, null, rng, reps=300, **kw):
    """Planted effect: carriers re-drawn within strata, same count, with odds ratio 3 (binary/omni) or +0.5 SD (size)."""
    c0 = carriers(units, cls); k = c0.sum()
    crit = np.quantile(null, 0.95)
    if k == 0:
        return 0.0
    hits = 0
    if kind == "binary":
        w = np.array([3.0 if units[i][kw["key"]] == kw["level"] else 1.0 for i in range(len(units))])
    elif kind == "omni":
        levs = Counter(u[kw["key"]] for u in units if u[kw["key"]] is not None)
        minor = [l for l, _ in levs.most_common()[1:]] or list(levs)
    else:
        la = np.array([u["logarea"] if u["logarea"] is not None else np.nan for u in units])
        sd = np.nanstd(la)
    for r in range(reps):
        if kind == "omni":
            tgt = minor[rng.integers(len(minor))]
            w = np.array([3.0 if units[i][kw["key"]] == tgt else 1.0 for i in range(len(units))])
        if kind == "size":
            # shift: choose carriers with prob proportional to exp(beta*z), beta set so mean shift ~0.5 SD
            z = np.nan_to_num((la - np.nanmean(la)) / sd, nan=0.0)
            w = np.exp(0.5 * z)
        p = w / w.sum()
        cc = np.zeros(len(units), bool); cc[rng.choice(len(units), size=k, replace=False, p=p)] = True
        if kind == "binary":
            s = stat_binary(units, cc, kw["key"], kw["level"])[0]
        elif kind == "omni":
            s = stat_omni(units, cc, kw["key"])[0]
        else:
            s = stat_size(units, cc)[0]
        hits += s >= crit
    return hits / reps


def holm(ps):
    ps = np.asarray(ps, float); o = np.argsort(ps); n = len(ps); out = np.empty(n); run = 0
    for r, i in enumerate(o):
        run = max(run, min(1, (n - r) * ps[i])); out[i] = run
    return out


if __name__ == "__main__":
    rng = np.random.default_rng(SEED)
    dev, ho = dev_heldout(version=2)
    io = icit_only()
    sets = {
        "m77_heldout_conf": m77_units(ho, True),
        "icit_only_conf": icit_units(io, True),
    }
    TESTS = [  # (id, set, kind, kwargs) -- confirmatory family of 6
        ("H1_m77", "m77_heldout_conf", "binary", dict(key="icon", level="scene")),
        ("H1_icit", "icit_only_conf", "binary", dict(key="icon", level="scene")),
        ("H2_m77", "m77_heldout_conf", "omni", dict(key="otype")),
        ("H2_icit", "icit_only_conf", "omni", dict(key="otype")),
        ("H3_icit", "icit_only_conf", "omni", dict(key="material")),
        ("H4_icit", "icit_only_conf", "size", {}),
    ]
    res = {"class_M": CLASS_M, "class_W": CLASS_W, "confirmatory": {}, "secondary_core": {}, "exploratory": {}}
    ps = []
    for tid, sname, kind, kw in TESTS:
        units = sets[sname]
        cls = CLASS_M if sname.startswith("m77") else CLASS_W
        d, null = run_test(units, cls, kind, rng, **kw)
        d["power"] = power(units, cls, kind, null, rng, **kw)
        res["confirmatory"][tid] = d; ps.append(d["p_ctrl"])
        print(tid, json.dumps(d, default=float))
    for tid, q in zip([t[0] for t in TESTS], holm(ps)):
        res["confirmatory"][tid]["holm"] = float(q)
    # secondary: core class (same tests, reported, not in the Holm family)
    for tid, sname, kind, kw in TESTS:
        units = sets[sname]
        cls = CORE_M if sname.startswith("m77") else CORE_W
        d, _ = run_test(units, cls, kind, rng, **kw)
        res["secondary_core"][tid] = d
        print("core", tid, json.dumps(d, default=float))
    # exploratory: overlap objects kept; dev; all ICIT incl. bangles
    ex = {
        "m77_dev_all": (m77_units(dev, False), CLASS_M),
        "m77_heldout_withoverlap": (m77_units(ho, False), CLASS_M),
        "m77_all": (m77_units(distinct(m77_texts()), False), CLASS_M),
        "icit_all_distinct_withoverlap": (icit_units(distinct(icit_texts()), False), CLASS_W),
        "icit_only_withoverlap": (icit_units(io, False), CLASS_W),
    }
    for name, (units, cls) in ex.items():
        res["exploratory"][name] = {}
        for tid, kind, kw in [("icon_scene", "binary", dict(key="icon", level="scene")),
                              ("otype", "omni", dict(key="otype"))] + (
                [("material", "omni", dict(key="material")), ("size", "size", {})] if name.startswith("icit") else []):
            d, _ = run_test(units, cls, kind, rng, **kw)
            res["exploratory"][name][tid] = d
            print("expl", name, tid, json.dumps(d, default=float))
    json.dump(res, open(OUT / "d2_covariates.json", "w"), indent=1, default=float)
