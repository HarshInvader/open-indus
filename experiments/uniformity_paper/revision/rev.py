"""Uniformity paper, revision analyses for review 1 (prereg docs/prereg/uniformity_paper_revision.md).

Every scored draw goes through the benchmark's own clean() + draw_n() + score() (uniformity_benchmark/run.py),
with pools from step-2 s2.py, red-team rt2.py and chanhudaro_followup cd.py. De-duplication is clean()
(fish_tick_closer_v2/dedup.py greedy, non-chaining). The only new scorers are the ones review 1 asked for:
logistic regression through the frozen lib.oof_scores(model="lr") and a classifier-free Jensen-Shannon test.

  R1 boot     pool-level bootstrap over texts for every headline gap; 95% CI and TOST at +-0.05
  R2 names    planted names at r = 0 .. 0.50 (step 0.05 from 0.20) on bootstrapped pools; 80% / 95% lines
     diffuse  diffuse planted effects (local variants; frequency shift) in the step-2 power format
  R3 roles    Ur III personal names split by legend role (owner, father, patron); same-collection between
  R4 latin    Latin owner/maker marks by object class (military, stamps, graffiti)
  R5 alt      logistic regression + Jensen-Shannon permutation test on the core contrasts
  R6 m93      M93 occurrences, concordance, and merge test (Chanhu-daro pairs)
  R7 unicorn  Mohenjo-daro vs Harappa within unicorn seals

  .venv/bin/python -I experiments/uniformity_paper/revision/rev.py sizes
  .venv/bin/python -I experiments/uniformity_paper/revision/rev.py roles_audit     # writes data/roles_sample.txt
  board/run.sh .venv/bin/python -I experiments/uniformity_paper/revision/rev.py run boot|names|diffuse|roles|latin|alt|m93|unicorn
  .venv/bin/python -I experiments/uniformity_paper/revision/rev.py report
"""
import glob
import json
import re
import sys
import zlib
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "experiments/chanhudaro_followup"))
import cd  # noqa: E402  (imports rt2 -> s2 -> s1, rt1, ub, rt, lib)

rt2, s2, s1, ub, rt, lib = cd.rt2, cd.s2, cd.s1, cd.ub, cd.rt, cd.lib
from corpus.load import icit_texts, m77_texts  # noqa: E402

DATA = HERE / "data"
SEED = 20261201
MIX = s2.MIX
MARGIN = 0.05
GATE_Q = 0.15
N_MAX = 227
MD, HA, CD = s2.MD, s2.HA, cd.CD
IFAMS = ("m77_seal", "icit_seal", "icit_sealtype")

# R1
B_REPS, B_D = 200, 5
# R2
N_REPS, N_D = 60, 3
RATES = (0.0, 0.10, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50)
FORMS = ("sign", "spelt", "ur3emp")
DIFF_LEVELS = (0.10, 0.20, 0.30, 0.50)
# R3-R7
N_DRAWS = 50
JSD_PERM = 200
PS_BAR = 0.80

S2RES = json.load(open(ROOT / "experiments/uniformity_paper/step2/results.json"))


def s2n(cond):
    return S2RES["conditions"][cond]["n_side"]


def rng_for(*key):
    return np.random.default_rng([SEED] + [zlib.crc32(str(k).encode()) for k in key])


_C = {}


def cache(k, f):
    if k not in _C:
        _C[k] = f()
    return _C[k]


def natural(T, a, b):
    c = Counter(t["site"] for t in T)
    return min(c[a], c[b], N_MAX)


# =========================================================================== scorers
def score_lr(sample, a, seed):
    """ub.score with the frozen lib.oof_scores(model='lr') (L2, C = 0.5, balanced), plus one permuted-label AUC."""
    T = [dict(signs=[w for l in t["lines"] for w in l], runs=t["lines"], fam=t["group"], site=t["site"]) for t in sample]
    X, _ = lib.design(T, {}, "all")
    y = np.array([1 if t["site"] == a else 0 for t in T])
    g = np.array([t["fam"] for t in T])
    keep = np.asarray(X.sum(1)).ravel() > 0
    X, y, g = X[keep], y[keep], g[keep]
    P = lib.oof_scores(X, y, g, model="lr", classes=[0, 1], seed=seed)
    obs = lib.auc(y, P[:, 1])
    rng = np.random.default_rng(seed + 7)
    yp = lib.permute_within(y, np.zeros(len(y), int), rng)
    Pp = lib.oof_scores(X, yp, g, model="lr", classes=[0, 1], seed=seed + 1, reps=1)
    return float(obs), float(lib.auc(yp, Pp[:, 1]))


def feats(t):
    f = Counter()
    for l in t["lines"]:
        for w in l:
            f["u:" + w] += 1
        for x, y in zip(l, l[1:]):
            f["b:" + x + "_" + y] += 1
    return f


def jsd_counts(A, B):
    keys = sorted(set(A) | set(B))
    p = np.array([A.get(k, 0) for k in keys], float); q = np.array([B.get(k, 0) for k in keys], float)
    p /= p.sum(); q /= q.sum(); m = (p + q) / 2

    def kl(x):
        nz = x > 0
        return float(np.sum(x[nz] * np.log2(x[nz] / m[nz])))
    return 0.5 * kl(p) + 0.5 * kl(q)


def jsd_test(sample, a, rng, nperm=JSD_PERM):
    """Classifier-free: JSD between the two sides' pooled sign + within-line pair counts; permutation p by
    shuffling side labels over texts (same sizes)."""
    F = [feats(t) for t in sample]
    y = np.array([t["site"] == a for t in sample])

    def stat(lab):
        A, B = Counter(), Counter()
        for f, l in zip(F, lab):
            (A if l else B).update(f)
        return jsd_counts(A, B)
    obs = stat(y)
    perm = np.array([stat(rng.permutation(y)) for _ in range(nperm)])
    return float(obs), float((1 + np.sum(perm >= obs)) / (1 + nperm)), float(np.median(perm))


# =========================================================================== R1 bootstrap
def boot_pool(T, rng):
    """Resample texts with replacement within each side label, keeping each side's size. Copies keep the
    original group, so grouped CV puts them in one fold."""
    by = defaultdict(list)
    for t in T:
        by[t["site"]].append(t)
    out = []
    for s in sorted(by):
        L = by[s]
        for i in rng.integers(len(L), size=len(L)):
            out.append(L[i])
    return out


def ur3_cond(corp, split):
    rows = s2.ur3_rows if corp == "ur3" else s2.cdli_rows
    splits = s2.UR3_SPLITS if corp == "ur3" else s2.CDLI_SPLITS
    sa, sb = s2.split_sides(split)
    return (lambda: s2.between_pool(rows(), "Umma", "Girsu", "whole"), "Umma", "Girsu",
            lambda: s2.within_pool(rows(), splits, split, "whole"), sa, sb)


def unicorn_raw(fam):
    sym = cd.icit_symbol_map()
    return [x for x in s2.indus_raw(fam) if sym.get(x["id"], "").startswith("Bull1")]


def unicorn_between(fam):
    return cache("uB" + fam, lambda: ub.clean([x for x in unicorn_raw(fam) if x["site"] in (MD, HA)]))


def unicorn_within(fam):
    return cache("uW" + fam, lambda: ub.clean([dict(x, site=s2.half(x["id"])) for x in unicorn_raw(fam) if x["site"] == MD]))


def boot_comparisons():
    """name -> dict(B, a, b, W, wa, wb, n, kind). kind: 'indus' (floor + null), 'ref' (floor), 'cd' (cons)."""
    C = {}
    for fam in IFAMS:
        a, b = s2.pair_order(fam, MD, HA)
        C[f"MDHA_{fam}"] = dict(B=lambda fam=fam, a=a, b=b: s2.indus_between(fam, a, b), a=a, b=b,
                                W=lambda fam=fam, a=a: s2.indus_within(fam, a), wa="X", wb="Y",
                                n=lambda fam=fam, a=a, b=b: s2n(f"IB_{fam}|{a}|{b}"), kind="indus")
    for fam in ("icit_seal", "icit_sealtype"):
        C[f"UNI_{fam}"] = dict(B=lambda fam=fam: unicorn_between(fam), a=MD, b=HA, W=lambda fam=fam: unicorn_within(fam),
                               wa="X", wb="Y", n=None, kind="indus")
    for corp, sps in (("ur3", ("U_reign", "U_coll", "G_reign", "G_coll")), ("cdli", ("U_reign", "G_reign"))):
        for sp in sps:
            Bf, a, b, Wf, sa, sb = ur3_cond(corp, sp)
            C[f"REF_{corp}_{sp}"] = dict(B=Bf, a=a, b=b, W=Wf, wa=sa, wb=sb,
                                         n=lambda corp=corp, sp=sp: s2n(f"B_{corp}_whole_at_{sp}"), kind="ref")
    for sp in ("ge_rlp_vs_bwhe", "br_north_vs_south"):
        C[f"REF_lat_{sp}"] = dict(B=lambda: s2.lat_between(False), a="Britannia", b="Germania",
                                  W=lambda sp=sp: s2.lat_within(sp, False), wa="X", wb="Y",
                                  n=lambda sp=sp: s2n(f"B_lat_whole_at_{sp}"), kind="ref")
    for fam, big in cd.PAIRS:
        C[f"CD_{fam}_{big}"] = dict(B=lambda fam=fam, big=big: cd.base(fam, big), a=big, b=CD,
                                    W=lambda fam=fam, big=big: cd.within_big(fam, big), wa="X", wb="Y", n=None, kind="cd")
    return C


def resolve_n(c):
    if c["n"] is not None:
        return c["n"]()
    B, W = c["B"](), c["W"]()
    return min(natural(B, c["a"], c["b"]), natural(W, c["wa"], c["wb"]))


def run_boot(f, done):
    C = boot_comparisons()
    for name, c in C.items():
        B, W = c["B"](), c["W"]()
        n = resolve_n(c)
        for rep in range(B_REPS):
            if (name, rep) in done:
                continue
            rng = rng_for("boot", name, rep)
            Bb, Wb = boot_pool(B, rng), boot_pool(W, rng)
            bs, bn, ws = [], [], []
            for d in range(B_D):
                smp, _ = ub.draw_n(Bb, c["a"], c["b"], rng, MIX, False, n, 2 * n)
                if smp is not None:
                    o, nu, _, _ = ub.score(smp, c["a"], SEED + 1000 * rep + d)
                    bs.append(o); bn.append(nu)
                smp, _ = ub.draw_n(Wb, c["wa"], c["wb"], rng, MIX, False, n, 2 * n)
                if smp is not None:
                    o, _, _, _ = ub.score(smp, c["wa"], SEED + 1000 * rep + d + 500)
                    ws.append(o)
            f.write(json.dumps(dict(job="boot", cond=name, rep=rep, n=n, b=bs, bnull=bn, w=ws)) + "\n"); f.flush()
        print("boot", name, "n", n, flush=True)


# =========================================================================== R2 planted names
def run_names(f, done):
    for fam in IFAMS:
        a, b = s2.pair_order(fam, MD, HA)
        B = s2.indus_between(fam, a, b)
        W = s2.indus_within(fam, a)
        n = s2n(f"IB_{fam}|{a}|{b}")
        freq = Counter(w for t in B for l in t["lines"] for w in l)
        common = sorted(s for s, k in freq.items() if k >= 5)
        for rep in range(N_REPS):
            if (fam, rep) in done:
                continue
            rng = rng_for("names", fam, rep)
            Bb, Wb = boot_pool(B, rng), boot_pool(W, rng)
            ws = []
            for d in range(N_D):
                smp, _ = ub.draw_n(Wb, "X", "Y", rng, MIX, False, n, 2 * n)
                if smp is not None:
                    ws.append(ub.score(smp, "X", SEED + 7000 + d)[0])
            res = {}
            for form in FORMS:
                for r in RATES:
                    if r == 0.0 and form != "sign":
                        continue
                    key = "0.0" if r == 0.0 else f"{form}|{r}"
                    out = []
                    for d in range(N_D):
                        g = rng_for("namesdraw", fam, rep, key, d)
                        smp, _ = ub.draw_n(Bb, a, b, g, MIX, False, n, 2 * n)
                        if smp is None:
                            continue
                        if r > 0:
                            smp = rt2.plant_names_real(smp, form, r, g, common, a)
                        out.append(ub.score(smp, a, SEED + 9000 + d)[0])
                    res[key] = out
            f.write(json.dumps(dict(job="names", cond=fam, rep=rep, n=n, w=ws, b=res)) + "\n"); f.flush()
            if rep % 10 == 0:
                print("names", fam, rep, flush=True)


def plant_variants(sample, side, v, rng):
    """Diffuse effect 1: half of the sign types at `side` (chosen at random per draw) get a local variant; each
    token of a chosen type is replaced by its variant with probability v. Many rare local forms, no stock."""
    types = sorted({w for t in sample if t["site"] == side for l in t["lines"] for w in l})
    ch = set(rng.choice(types, len(types) // 2, replace=False)) if types else set()
    out = []
    for t in sample:
        if t["site"] == side:
            t = dict(t, lines=[[(w + "_v") if (w in ch and rng.random() < v) else w for w in l] for l in t["lines"]])
        out.append(t)
    return out, altered(out, side, lambda w: w.endswith("_v"))


def altered(sample, side, f):
    toks = [w for t in sample if t["site"] == side for l in t["lines"] for w in l]
    return sum(map(f, toks)) / max(1, len(toks))


def plant_shift(sample, side, s, rng, common, p0):
    """Diffuse effect 2: at `side`, each token is replaced with probability s by a draw from the pool's common-sign
    frequencies reweighted by exp(z), z ~ N(0, 1) per sign (a frequency shift among shared signs; no new signs)."""
    z = rng.normal(size=len(common))
    p = p0 * np.exp(z); p /= p.sum()
    out, nrep, ntok = [], 0, 0
    for t in sample:
        if t["site"] == side:
            L = []
            for l in t["lines"]:
                row = []
                for w in l:
                    ntok += 1
                    if rng.random() < s:
                        row.append(common[rng.choice(len(common), p=p)]); nrep += 1
                    else:
                        row.append(w)
                L.append(row)
            t = dict(t, lines=L)
        out.append(t)
    return out, nrep / max(1, ntok)


def run_diffuse(f, done):
    for fam in IFAMS:
        a, b = s2.pair_order(fam, MD, HA)
        B = s2.indus_between(fam, a, b)
        n = s2n(f"IB_{fam}|{a}|{b}")
        freq = Counter(w for t in B for l in t["lines"] for w in l)
        common = sorted(s for s, k in freq.items() if k >= 5)
        p0 = np.array([freq[c] for c in common], float); p0 /= p0.sum()
        for kind in ("variants", "shift"):
            for v in DIFF_LEVELS:
                name = f"{fam}|{kind}|{v}"
                for k in range(N_DRAWS):
                    if (name, k) in done:
                        continue
                    g = rng_for("diffuse", name, k)
                    smp, _ = ub.draw_n(B, a, b, g, MIX, False, n, 2 * n)
                    if smp is None:
                        continue
                    smp, share = plant_variants(smp, b, v, g) if kind == "variants" else plant_shift(smp, b, v, g, common, p0)
                    o, nu, _, _ = ub.score(smp, a, SEED + k)
                    f.write(json.dumps(dict(job="diffuse", cond=name, draw=k, n=n, auc=o, null=nu, share=share)) + "\n")
                f.flush()
                print("diffuse", name, flush=True)


# =========================================================================== R3 Ur III name roles
NAMELIKE = lambda p: p in ("PN", "RN") or p in ("X", "u", "?")
DED = {"arad₂-zu", "arad₂-zu-ne", "in-na-ba", "in-na-ba-a", "arad₂-da-ni", "geme₂-zu", "arad₂-ni"}


def is_ded(lines):
    return any(w in DED or w.startswith("arad₂-zu") or w.startswith("in-na-ba") for l in lines for w, _ in l)


def roles(lines):
    """Per token role for name-like tokens (PN, RN, unknown X/u/?); None for other tokens.
    Roles: father (right after 'dumu'); patron (every RN; right after 'arad₂' / 'geme₂'; and, in a dedicated
    legend with arad₂-zu... / in-na-ba..., the first-line names when a later owner name follows); owner (the first
    remaining name); other (any further name). A name directly followed by 'ensi₂' gets the suffix '+gov'
    (a governor of Umma or Girsu, in any slot)."""
    flat = [(i, w, p) for i, l in enumerate(lines) for (w, p) in l]
    R = [None] * len(flat)
    ded = is_ded(lines)
    for k, (i, w, p) in enumerate(flat):
        if not NAMELIKE(p):
            continue
        prev = flat[k - 1][1] if k else None
        if prev == "dumu":
            R[k] = "father"
        elif p == "RN" or prev in ("arad₂", "geme₂"):
            R[k] = "patron"
    if ded:
        later = [k for k, (i, w, p) in enumerate(flat) if NAMELIKE(p) and R[k] is None and i > 0]
        if later:
            for k, (i, w, p) in enumerate(flat):
                if NAMELIKE(p) and R[k] is None and i == 0:
                    R[k] = "patron"
    owner_done = False
    for k, (i, w, p) in enumerate(flat):
        if NAMELIKE(p) and R[k] is None:
            R[k] = "other" if owner_done else "owner"
            owner_done = True
    for k in range(len(flat)):
        if R[k] and k + 1 < len(flat) and flat[k + 1][1] == "ensi₂":
            R[k] += "+gov"
    out, k = [], 0
    for l in lines:
        out.append(R[k:k + len(l)]); k += len(l)
    return out


def drop_role(ro, variant):
    if ro is None:
        return False
    base, gov = ro.split("+")[0], ro.endswith("+gov")
    return {"noOwner": base == "owner",
            "noFather": base == "father",
            "noPatron": base == "patron",
            "noOwnFath": base in ("owner", "father"),
            "noPrivate": base in ("owner", "father", "other") and not gov,
            "noOffice": base == "patron" or gov,
            "noAllNames": True}[variant]


def role_rows(rows, variant):
    out = []
    for r in rows:
        if variant == "whole":
            L = [[w for w, _ in l] for l in r["lines"]]
        elif variant == "noPN":
            L = [[w for w, p in l if not (p == "PN" or p in ("X", "u", "?"))] for l in r["lines"]]
        else:
            RL = roles(r["lines"])
            L = [[w for (w, p), ro in zip(l, rl) if not drop_role(ro, variant)] for l, rl in zip(r["lines"], RL)]
        out.append(dict(r, flines=L))
    return out


def role_pool(rows, variant, city=None, split=None, splits=None, museum=None):
    T = []
    for r in role_rows(rows, variant):
        if museum is not None and r.get("museum") != museum:
            continue
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
        T.append(dict(id=r["id"], site=s, group=r["group"], lines=r["flines"]))
    return ub.clean(s1._fix(T))


def roles_audit():
    rng = np.random.default_rng(SEED)
    R = [r for r in s2.ur3_rows() if r["site"] in ("Umma", "Girsu")]
    cnt = Counter(); ded = Counter()
    for r in R:
        RL = roles(r["lines"])
        isded = is_ded(r["lines"])
        for l, rl in zip(r["lines"], RL):
            for (w, p), ro in zip(l, rl):
                if ro:
                    cnt[(r["site"], ro)] += 1
                    if isded:
                        ded[(r["site"], ro)] += 1
    DATA.mkdir(exist_ok=True)
    with open(DATA / "roles_sample.txt", "w", encoding="utf-8") as f:
        dd = [r for r in R if is_ded(r["lines"])]
        nd = [r for r in R if r not in dd]
        for lab, X in (("dedicated", dd), ("plain", nd)):
            for i in sorted(rng.choice(len(X), 25, replace=False)):
                r = X[i]
                RL = roles(r["lines"])
                f.write(f"[{lab}] {r['id']} {r['site']}: " + " / ".join(
                    " ".join(f"{w}<{ro}>" if ro else w for (w, _), ro in zip(l, rl)) for l, rl in zip(r["lines"], RL)) + "\n")
    print("role token counts", sorted(cnt.items()))
    print("in dedicated legends", sorted(ded.items()))
    print("dedicated legends", sum(is_ded(r["lines"]) for r in R), "of", len(R))


ROLE_VARIANTS = ("noPN", "noOwner", "noFather", "noPatron", "noOwnFath", "noPrivate", "noOffice", "noAllNames")
BM_VARIANTS = ("whole", "noPN", "noPrivate")


def role_conditions():
    C = {}

    def trio(key, wb, wa, wbb, bb, a, b, n=None, **info):
        nn = n or ("match", f"W_{key}", f"B_{key}")
        C[f"W_{key}"] = dict(build=wb, a=wa, b=wbb, n=nn, plant=None, info=dict(role="within", **info))
        C[f"B_{key}"] = dict(build=bb, a=a, b=b, n=nn, plant=None, info=dict(role="between", **info))
        C[f"G_{key}"] = dict(build=bb, a=a, b=b, n=f"B_{key}", plant=("gate", GATE_Q), info=dict(role="gate", **info))

    for corp, rows, splits, sps in (("ur3", s2.ur3_rows, s2.UR3_SPLITS, ("U_reign", "U_coll", "G_reign", "G_coll")),
                                    ("cdli", s2.cdli_rows, s2.CDLI_SPLITS, ("U_reign", "G_reign"))):
        for v in ROLE_VARIANTS:
            for sp in sps:
                city = splits[sp][0]
                trio(f"{corp}_{v}_{sp}",
                     lambda rows=rows, v=v, city=city, sp=sp, splits=splits: role_pool(rows(), v, city, sp, splits),
                     *s2.split_sides(sp), lambda rows=rows, v=v: role_pool(rows(), v), "Umma", "Girsu",
                     corpus=corp, variant=v, split=sp)
    for v in BM_VARIANTS:
        for sp in ("U_reign", "U_coll", "G_reign", "G_coll"):
            city = s2.UR3_SPLITS[sp][0]
            trio(f"bm_{v}_{sp}",
                 lambda v=v, city=city, sp=sp: role_pool(s2.ur3_rows(), v, city, sp, s2.UR3_SPLITS),
                 *s2.split_sides(sp), lambda v=v: role_pool(s2.ur3_rows(), v, museum="BM"), "Umma", "Girsu",
                 corpus="bm", variant=v, split=sp)
    return C


# =========================================================================== R4 Latin by object class
UNIT = {"LEG", "LEGIO", "LEGIONIS", "COH", "CHO", "COHORS", "COHORTIS", "AL", "ALA", "ALAE", "CL", "CLASSIS", "CLBR",
        "VEX", "VEXIL", "VEXILLATIO", "NUMERI", "NVMERI", "MIL"}
GRAF = re.compile(r"graffit|geritzt|gepunzt|punktiert|incis|scratch", re.I)
EDH = ROOT / "experiments/short_labels/raw/edh"


def lat_comment():
    def f():
        ids = s2.lat_ids()
        out = {}
        for fn in sorted(glob.glob(str(EDH / "p*.json"))):
            try:
                d = json.load(open(fn, encoding="utf-8"))
            except Exception:
                continue
            for it in d.get("items", []):
                if it["id"] in ids:
                    out[it["id"]] = it.get("commentary") or ""
        return out
    return cache("latcom", f)


def lat_class():
    """id -> class: MIL (any unit word), STAMP (not MIL, stamped per step-2 flag), GRAF (not MIL, not stamped,
    graffito cue in the EDH commentary), UNFL (not MIL, not stamped, no cue)."""
    def f():
        meta = {m["id"]: m for m in s2._jl(s2.DATA / "latmeta.jsonl")}
        com = lat_comment()
        out = {}
        for r in s2.lat_rows():
            if r["id"] not in meta:
                continue
            toks = {w for l in r["lines"] for w, _ in l}
            if toks & UNIT:
                c = "MIL"
            elif meta[r["id"]]["stamped"]:
                c = "STAMP"
            elif GRAF.search(com.get(r["id"], "")):
                c = "GRAF"
            else:
                c = "UNFL"
            out[r["id"]] = c
        return out
    return cache("latclass", f)


LAT_CLASSES = {"MIL": {"MIL"}, "STAMP": {"STAMP"}, "GRAF": {"GRAF"}, "REST": {"GRAF", "UNFL"}}


def lat_class_pool(cls, split=None):
    ids = s2.lat_ids()
    lc = lat_class()
    T = []
    for r in s2.lat_rows():
        if r["id"] not in ids or lc.get(r["id"]) not in LAT_CLASSES[cls]:
            continue
        if split is None:
            s = r["site"]
        else:
            prov, fn = s2.LAT_SPLITS[split]
            if r["site"] != prov:
                continue
            s = s2.half(r["id"]) if fn == "random" else fn(r.get("region", ""))
            if s is None:
                continue
        T.append(dict(id=r["id"], site=s, group=r["group"], lines=[[w for w, _ in l] for l in r["lines"]]))
    return ub.clean(s1._fix(T))


def latin_conditions():
    C = {}
    for cls in LAT_CLASSES:
        for sp in ("ge_rlp_vs_bwhe", "br_north_vs_south"):
            key = f"lat_{cls}_{sp}"
            nn = ("match", f"W_{key}", f"B_{key}")
            C[f"W_{key}"] = dict(build=lambda cls=cls, sp=sp: lat_class_pool(cls, sp), a="X", b="Y", n=nn, plant=None,
                                 info=dict(role="within", corpus="lat", variant=cls, split=sp))
            C[f"B_{key}"] = dict(build=lambda cls=cls: lat_class_pool(cls), a="Britannia", b="Germania", n=nn, plant=None,
                                 info=dict(role="between", corpus="lat", variant=cls, split=sp))
            C[f"G_{key}"] = dict(build=lambda cls=cls: lat_class_pool(cls), a="Britannia", b="Germania", n=f"B_{key}",
                                 plant=("gate", GATE_Q), info=dict(role="gate", corpus="lat", variant=cls, split=sp))
    return C


# =========================================================================== R5 second classifier + JSD
def alt_conditions():
    C = {}
    for fam in IFAMS:
        a, b = s2.pair_order(fam, MD, HA)
        n = s2n(f"IB_{fam}|{a}|{b}")
        C[f"AB_{fam}"] = dict(build=lambda fam=fam, a=a, b=b: s2.indus_between(fam, a, b), a=a, b=b, n=n, plant=None,
                              info=dict(role="between", corpus="indus", variant=fam, split="MD_rand"))
        C[f"AW_{fam}"] = dict(build=lambda fam=fam, a=a: s2.indus_within(fam, a), a="X", b="Y", n=n, plant=None,
                              info=dict(role="within", corpus="indus", variant=fam, split="MD_rand"))
        C[f"AP_{fam}"] = dict(build=lambda fam=fam, a=a, b=b: s2.indus_between(fam, a, b), a=a, b=b, n=n,
                              plant=("side", b, GATE_Q), info=dict(role="power", corpus="indus", variant=fam, split="MD_rand"))
    for corp, sps in (("ur3", ("U_reign", "U_coll", "G_reign", "G_coll")), ("cdli", ("U_reign", "G_reign")),
                      ("lat", ("ge_rlp_vs_bwhe", "br_north_vs_south"))):
        for sp in sps:
            if corp == "lat":
                Bf, a, b = (lambda: s2.lat_between(False)), "Britannia", "Germania"
                Wf, sa, sb = (lambda sp=sp: s2.lat_within(sp, False)), "X", "Y"
                n = s2n(f"B_lat_whole_at_{sp}")
            else:
                Bf, a, b, Wf, sa, sb = ur3_cond(corp, sp)
                n = s2n(f"B_{corp}_whole_at_{sp}")
            key = f"{corp}_{sp}"
            C[f"AB_{key}"] = dict(build=Bf, a=a, b=b, n=n, plant=None, info=dict(role="between", corpus=corp, variant="whole", split=sp))
            C[f"AW_{key}"] = dict(build=Wf, a=sa, b=sb, n=n, plant=None, info=dict(role="within", corpus=corp, variant="whole", split=sp))
            C[f"AG_{key}"] = dict(build=Bf, a=a, b=b, n=n, plant=("gate", GATE_Q), info=dict(role="gate", corpus=corp, variant="whole", split=sp))
    return C


# =========================================================================== R6 M93
M93_VARIANTS = {"base": None, "toM94": ["M94"], "toM89": ["M89"], "toM86M87": ["M86", "M87"], "drop": []}


def m93_pool(big, variant):
    rep = M93_VARIANTS[variant]
    T = []
    for x in cd.raw_pair("m77_seal", big):
        L = x["lines"]
        if rep is not None:
            L = [[y for w in l for y in ((rep if w == "M93" else [w]))] for l in L]
            L = [l for l in L if l]
        if L:
            T.append(dict(x, lines=L))
    return ub.clean(T)


def m93_conditions():
    C = {}
    for big in (HA, MD):
        base_n = natural(cd.base("m77_seal", big), big, CD)
        wn = natural(cd.within_big("m77_seal", big), "X", "Y")
        C[f"MW_{big}"] = dict(build=lambda big=big: cd.within_big("m77_seal", big), a="X", b="Y",
                              n=("m93", big), plant=None, info=dict(role="within", big=big))
        for v in M93_VARIANTS:
            C[f"MB_{big}_{v}"] = dict(build=lambda big=big, v=v: m93_pool(big, v), a=big, b=CD, n=("m93", big),
                                      plant=None, info=dict(role="between", big=big, variant=v))
    return C


def m93_n(big):
    def f():
        ns = [natural(m93_pool(big, v), big, CD) for v in M93_VARIANTS]
        return min(ns + [natural(cd.within_big("m77_seal", big), "X", "Y")])
    return cache("m93n" + big, f)


def m93_listing():
    """Every M93 in M77 (all object types) with site and object id, the ICIT reading of the same object
    (consensus_corpus seq_links), and the M77 numeral-inventory twins."""
    links = json.load(open(ROOT / "experiments/consensus_corpus/out/seq_links.json"))
    icit = {t["id"]: t for t in icit_texts()}
    rows = []
    for t in m77_texts():
        if "M93" in t["seq"]:
            L = links.get(f"[{t['text_no']}, {t['side']}]", {})
            it = icit.get(L.get("icit"))
            rows.append(dict(m77=f"{t['text_no']}.{t['side']}", site=t["site"], object_type=t["object_type"],
                             m77_seq=" ".join(t["seq"]), icit_id=L.get("icit"),
                             icit_cisi=(it or {}).get("cisi"), icit_seq=" ".join(it["seq"]) if it else None,
                             icit_type=(it or {}).get("type")))
    twins = {}
    for s in ("M94", "M89", "M86", "M87"):
        c = Counter((t["site"], t["object_type"]) for t in m77_texts() if s in t["seq"])
        twins[s] = {f"{a}|{b}": k for (a, b), k in c.most_common()}
    # ICIT: texts whose last line is exactly W031 W032 (the ICIT reading of a final-line M93), by site and type
    fin = Counter(); allc = Counter()
    for t in icit_texts():
        if not (t["type"] or "").startswith("SEAL"):
            continue
        allc[t["site"]] += 1
        segs = [s for s in t["segments"] if s]
        if segs and list(segs[-1]) == ["W031", "W032"]:
            fin[t["site"]] += 1
        elif "|" in t["seq"] and t["seq"][-2:] == ["W031", "W032"] and t["seq"][-3] == "|":
            fin[t["site"]] += 1
    inv = [l.strip() for l in open(ROOT / "experiments/numeral_grammar/inventory.csv") if l.startswith("M77,M9")]
    return dict(rows=rows, twins=twins, icit_final_W031_W032={s: [fin[s], allc[s]] for s in allc if fin[s] or s in (MD, HA, CD)},
                numeral_inventory=inv)


# =========================================================================== R7 unicorn
def unicorn_conditions():
    C = {}
    for fam in ("icit_seal", "icit_sealtype"):
        nn = ("match", f"UW_{fam}", f"UB_{fam}")
        C[f"UW_{fam}"] = dict(build=lambda fam=fam: unicorn_within(fam), a="X", b="Y", n=nn, plant=None,
                              info=dict(role="within", family=fam))
        C[f"UB_{fam}"] = dict(build=lambda fam=fam: unicorn_between(fam), a=MD, b=HA, n=nn, plant=None,
                              info=dict(role="between", family=fam))
        for q in (0.10, 0.15, 0.20):
            C[f"UP{q}_{fam}"] = dict(build=lambda fam=fam: unicorn_between(fam), a=MD, b=HA, n=f"UB_{fam}",
                                     plant=("side", HA, q), info=dict(role="power", family=fam, q=q))
    return C


# =========================================================================== generic draw loop
_BUILT = {}


def built(name, C):
    if name not in _BUILT:
        _BUILT[name] = C[name]["build"]()
    return _BUILT[name]


def n_of(name, C):
    n = C[name]["n"]
    if isinstance(n, int):
        return n
    if isinstance(n, str):
        return n_of(n, C)
    if n[0] == "match":
        return min(natural(built(x, C), C[x]["a"], C[x]["b"]) for x in n[1:])
    if n[0] == "m93":
        return m93_n(n[1])
    raise ValueError(n)


def run_generic(job, C, f, done, scorer="nb"):
    for name, c in C.items():
        T = built(name, C)
        a, b = c["a"], c["b"]
        n = n_of(name, C)
        common = None
        if c["plant"]:
            freq = Counter(w for t in T for l in t["lines"] for w in l)
            common = sorted(s for s, k in freq.items() if k >= 5)
        for k in range(N_DRAWS):
            if (name, k) in done:
                continue
            g = rng_for(job, name, k)
            smp = None
            if n >= 5:
                smp, _ = ub.draw_n(T, a, b, g, MIX, False, n, 2 * n)
            if smp is None:
                f.write(json.dumps(dict(job=job, cond=name, draw=k, n=n, auc=None)) + "\n"); continue
            p = c["plant"]
            if p and p[0] == "gate":
                smp = rt.plant(smp, "new100", p[1], g, common)
            elif p and p[0] == "side":
                smp = s2.plant_side(smp, p[1], p[2], g, common)
            rec = dict(job=job, cond=name, draw=k, n=n)
            if scorer == "alt":
                o, nu = score_lr(smp, a, SEED + k)
                js, jp, jn = jsd_test(smp, a, g)
                rec.update(auc=o, null=nu, jsd=js, jsd_p=jp, jsd_null=jn)
            else:
                o, nu, _, _ = ub.score(smp, a, SEED + k)
                rec.update(auc=o, null=nu)
            f.write(json.dumps(rec) + "\n")
        f.flush()
        print(job, name, "n", n, flush=True)


def run(job):
    path = HERE / f"draws_{job}.jsonl"
    done = set()
    if path.exists():
        for l in open(path):
            r = json.loads(l)
            done.add((r["cond"], r.get("rep", r.get("draw"))))
    with open(path, "a") as f:
        if job == "boot":
            run_boot(f, done)
        elif job == "names":
            run_names(f, done)
        elif job == "diffuse":
            run_diffuse(f, done)
        elif job == "roles":
            run_generic(job, role_conditions(), f, done)
        elif job == "latin":
            run_generic(job, latin_conditions(), f, done)
        elif job == "alt":
            run_generic(job, alt_conditions(), f, done, scorer="alt")
        elif job == "m93":
            run_generic(job, m93_conditions(), f, done)
        elif job == "unicorn":
            run_generic(job, unicorn_conditions(), f, done)
        else:
            raise ValueError(job)


# =========================================================================== sizes
def sizes():
    for name, c in boot_comparisons().items():
        B, W = c["B"](), c["W"]()
        print(f"boot {name:34s} B {dict(Counter(t['site'] for t in B))} W {dict(Counter(t['site'] for t in W))} n {resolve_n(c)}", flush=True)
    for job, C in (("roles", role_conditions()), ("latin", latin_conditions()), ("m93", m93_conditions()),
                   ("unicorn", unicorn_conditions())):
        for name, c in C.items():
            if c["info"].get("role") in ("gate", "power"):
                continue
            T = built(name, C)
            cnt = Counter(t["site"] for t in T)
            print(f"{job} {name:40s} {c['a']}={cnt[c['a']]} {c['b']}={cnt[c['b']]} n={n_of(name, C)}", flush=True)
    print("latin classes by province", Counter((r["site"], lat_class().get(r["id"])) for r in s2.lat_rows() if r["id"] in s2.lat_ids()))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "sizes"
    if mode == "run":
        run(sys.argv[2])
    elif mode == "report":
        import report  # noqa: E402
        report.main()
    else:
        {"sizes": sizes, "roles_audit": roles_audit, "m93_list": lambda: print(json.dumps(m93_listing(), indent=1, ensure_ascii=False))}[mode]()
