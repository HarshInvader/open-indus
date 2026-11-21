"""Uniformity paper, referee checks from review 2 (prereg docs/prereg/uniformity_referee_checks.md).

(a) A within-Harappa floor. M77 seals: Vats-register mound split (mound F against the other mounds, labels from
    experiments/reg_harappa/findspots.csv). Every family: Harappa random halves (ICIT has no locus field).
(b) Joint resampling of the Mohenjo-daro texts shared by the between pool and the Mohenjo-daro random-halves floor,
    with 20 + 20 draws per replicate; plus an independent resample at the same draw count, to separate the effect of
    jointness from the effect of more draws.

Every scored draw goes through the frozen benchmark clean() + draw_n() + score() (uniformity_benchmark/run.py) with
the step-2 length mix, exactly as experiments/uniformity_paper/revision/rev.py calls them. No new scorer.

  .venv/bin/python -I experiments/uniformity_referee_checks/rc.py sizes            # pool sizes only, no scoring
  board/run.sh .venv/bin/python -I experiments/uniformity_referee_checks/rc.py run hpoint|hboot|joint|indep20|rt
  .venv/bin/python -I experiments/uniformity_referee_checks/rc.py report           # results.json
"""
import csv
import json
import sys
import zlib
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments/uniformity_paper/revision"))
import rev  # noqa: E402  (imports cd -> rt2 -> s2 -> s1, ub, lib)

s2, ub = rev.s2, rev.ub
sys.path.insert(0, str(ROOT / "experiments/fish_tick_closer_v2"))
import dedup  # noqa: E402

SEED = 20261122
MIX = s2.MIX
MARGIN = 0.05
GATE_Q = 0.15
N_MAX = 227
MIN_SIDE = 40
MD, HA = s2.MD, s2.HA
IFAMS = rev.IFAMS
B_REPS = 200
H_D = 5          # (a) draws per replicate, as R1
J_D = 20         # (b) draws per replicate
N_POINT = 50     # (a) point estimate and power gate draws
RT_REPS = 100    # red-team bootstrap replicates
OTHER_MOUNDS = {"AB", "D", "E", "G", "H", "J"}


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


def med(x):
    return float(np.median(x))


# =========================================================================== pools
def mound_of():
    """M77 text_no -> 'F' / 'O' (other mounds) / None (no register row, blank mound, or rows on both sides)."""
    def f():
        m = defaultdict(set)
        for r in csv.DictReader(open(ROOT / "experiments/reg_harappa/findspots.csv")):
            if r["m77_text_no"]:
                m[str(int(float(r["m77_text_no"])))].add(r["mound"])
        out = {}
        for k, s in m.items():
            if s == {"F"}:
                out[k] = "F"
            elif s and s <= OTHER_MOUNDS:
                out[k] = "O"
        return out
    return cache("mound", f)


def ha_raw(fam):
    return [x for x in s2.indus_raw(fam) if x["site"] == HA]


def md_raw(fam):
    return [x for x in s2.indus_raw(fam) if x["site"] == MD]


def ha_mound(fam="m77_seal", only=None):
    """Harappa M77 seals labelled by mound. only=('F','AB') restricts 'other' to mound AB (red team)."""
    def f():
        m = mound_of()
        if only:
            reg = defaultdict(set)
            for r in csv.DictReader(open(ROOT / "experiments/reg_harappa/findspots.csv")):
                if r["m77_text_no"]:
                    reg[str(int(float(r["m77_text_no"])))].add(r["mound"])
            lab = {k: ("F" if s == {"F"} else "O" if s == {"AB"} else None) for k, s in reg.items()}
        else:
            lab = m
        T = []
        for x in ha_raw(fam):
            l = lab.get(x["id"][1:].split(".")[0])
            if l:
                T.append(dict(x, site=l))
        return ub.clean(T)
    return cache(f"hm{fam}{only}", f)


def ha_rand(fam):
    return cache("hr" + fam, lambda: ub.clean([dict(x, site=s2.half(x["id"])) for x in ha_raw(fam)]))


def between(fam):
    return cache("b" + fam, lambda: s2.indus_between(fam, MD, HA))


def md_floor(fam):
    return cache("w" + fam, lambda: s2.indus_within(fam, MD))


def unicorn_raw_md(fam):
    return [x for x in rev.unicorn_raw(fam) if x["site"] == MD]


def drop_cross_near(T, a, b):
    """Red team: drop BOTH members of every cross-side near-copy pair (dedup.near: >= 4 signs, contained in or
    within one edit of a text on the other side). clean() already keeps one member; this removes both."""
    S = {id(t): dedup.signs(t) for t in T}
    A = [t for t in T if t["site"] == a]
    B = [t for t in T if t["site"] == b]
    bad = set()
    for x in A:
        for y in B:
            sx, sy = S[id(x)], S[id(y)]
            short, long_ = (sx, sy) if len(sx) <= len(sy) else (sy, sx)
            if len(short) >= dedup.MIN_DROP and dedup.near(short, long_):
                bad.add(id(x)); bad.add(id(y))
    return [t for t in T if id(t) not in bad]


# (a) rows: name -> (between pool fn, Harappa floor fn, floor side labels)
def h_rows(variant="base"):
    R = {}
    if variant in ("base", "seed"):
        R["m77_seal|mound"] = (lambda: between("m77_seal"), lambda: ha_mound(), ("F", "O"), "m77_seal")
        for fam in (IFAMS if variant == "base" else ()):
            R[f"{fam}|rand"] = (lambda fam=fam: between(fam), lambda fam=fam: ha_rand(fam), ("X", "Y"), fam)
    elif variant == "FvAB":
        R["m77_seal|FvAB"] = (lambda: between("m77_seal"), lambda: ha_mound(only=("F", "AB")), ("F", "O"), "m77_seal")
    elif variant == "neardrop":
        R["m77_seal|mound|neardrop"] = (lambda: cache("bnd", lambda: drop_cross_near(between("m77_seal"), MD, HA)),
                                        lambda: cache("hnd", lambda: drop_cross_near(ha_mound(), "F", "O")),
                                        ("F", "O"), "m77_seal")
    return R


def h_n(Bf, Wf, sides):
    return min(natural(Bf(), MD, HA), natural(Wf(), *sides))


# (b) pools: name -> (between, MD floor, n per side as in R1)
def j_pools():
    P = {}
    for fam in IFAMS:
        P[f"MDHA_{fam}"] = (lambda fam=fam: between(fam), lambda fam=fam: md_floor(fam),
                            lambda fam=fam: rev.s2n(f"IB_{fam}|{MD}|{HA}"))
    for fam in ("icit_seal", "icit_sealtype"):
        P[f"UNI_{fam}"] = (lambda fam=fam: rev.unicorn_between(fam), lambda fam=fam: rev.unicorn_within(fam),
                           lambda fam=fam: min(natural(rev.unicorn_between(fam), MD, HA),
                                               natural(rev.unicorn_within(fam), "X", "Y")))
    return P


# =========================================================================== resampling
def boot_side(T, rng):
    return rev.boot_pool(T, rng)


def joint_resample(B, W, shared_site, rng):
    """Resample the texts of `shared_site` ONCE (by id, with replacement, over the union of its ids in B and W),
    and use that one draw for the shared side of the between pool and for the floor. The other between side is
    resampled on its own. Copies keep their id and group, so grouped CV keeps them in one fold."""
    Bs = {t["id"]: t for t in B if t["site"] == shared_site}
    Ws = {t["id"]: t for t in W}
    U = sorted(set(Bs) | set(Ws))
    pick = [U[i] for i in rng.integers(len(U), size=len(U))]
    other = [t for t in B if t["site"] != shared_site]
    Bb = [Bs[i] for i in pick if i in Bs] + [other[i] for i in rng.integers(len(other), size=len(other))]
    Wb = [Ws[i] for i in pick if i in Ws]
    return Bb, Wb


def draws(T, a, b, n, rng, k, seed0):
    out, nul = [], []
    for d in range(k):
        smp, _ = ub.draw_n(T, a, b, rng, MIX, False, n, 2 * n)
        if smp is not None:
            o, nu, _, _ = ub.score(smp, a, seed0 + d)
            out.append(o); nul.append(nu)
    return out, nul


# =========================================================================== jobs
def job_hpoint(f, done, variant="base", seed_shift=0):
    """(a) point estimates at matched n: between, Harappa floor, MD floor at the same n, power gate (20-sign stock
    on the Harappa side at q = 0.15), 50 draws each. Not bootstrapped."""
    for name, (Bf, Wf, sides, fam) in h_rows(variant).items():
        if name in done:
            continue
        B, W = Bf(), Wf()
        n = h_n(Bf, Wf, sides)
        rec = dict(job="hpoint", cond=name, variant=variant, seed_shift=seed_shift, n=n,
                   n_floor_sides=[Counter(t["site"] for t in W)[s] for s in sides])
        if n < 5:
            rec.update(b=[], w=[], wmd=[], power=[]); f.write(json.dumps(rec) + "\n"); continue
        g = rng_for("hpoint", name, seed_shift)
        s0 = SEED + 31 * seed_shift
        rec["b"], rec["bnull"] = draws(B, MD, HA, n, g, N_POINT, s0)
        rec["w"], _ = draws(W, sides[0], sides[1], n, g, N_POINT, s0 + 500)
        rec["wmd"], _ = draws(md_floor(fam), "X", "Y", n, g, N_POINT, s0 + 900)
        freq = Counter(w for t in B for l in t["lines"] for w in l)
        common = sorted(s for s, k in freq.items() if k >= 5)
        pw = []
        for d in range(N_POINT):
            smp, _ = ub.draw_n(B, MD, HA, g, MIX, False, n, 2 * n)
            if smp is None:
                continue
            smp = s2.plant_side(smp, HA, GATE_Q, g, common)
            pw.append(ub.score(smp, MD, s0 + 1300 + d)[0])
        rec["power"] = pw
        f.write(json.dumps(rec) + "\n"); f.flush()
        print("hpoint", name, "n", n, flush=True)


def job_hboot(f, done, variant="base", seed_shift=0, reps=B_REPS):
    """(a) bootstrap of Δ_H = median(b) − median(w_H), 5 + 5 draws per replicate. 'indep' resamples the between
    and floor pools separately (as R1); 'joint' resamples Harappa once, shared by the between pool and the floor."""
    for name, (Bf, Wf, sides, fam) in h_rows(variant).items():
        B, W = Bf(), Wf()
        n = h_n(Bf, Wf, sides)
        if n < 5:
            continue
        for mode in ("indep", "joint"):
            key = f"{name}|{mode}"
            for rep in range(reps):
                if (key, rep) in done:
                    continue
                g = rng_for("hboot", key, rep, seed_shift)
                if mode == "indep":
                    Bb, Wb = boot_side(B, g), boot_side(W, g)
                else:
                    Bb, Wb = joint_resample(B, W, HA, g)
                s0 = SEED + 31 * seed_shift + 1000 * rep
                b, bn = draws(Bb, MD, HA, n, g, H_D, s0)
                w, _ = draws(Wb, sides[0], sides[1], n, g, H_D, s0 + 500)
                f.write(json.dumps(dict(job="hboot", cond=key, rep=rep, variant=variant, seed_shift=seed_shift,
                                        n=n, b=b, bnull=bn, w=w)) + "\n")
            f.flush()
            print("hboot", key, "n", n, flush=True)


def job_jboot(f, done, mode, seed_shift=0, reps=B_REPS, only=None):
    """(b) Δ = median(b) − median(w_MD), 20 + 20 draws per replicate. mode 'joint' resamples MD once per replicate
    (shared by the between pool and both floor halves); 'indep' resamples the two pools separately."""
    for name, (Bf, Wf, nf) in j_pools().items():
        if only and name not in only:
            continue
        B, W, n = Bf(), Wf(), nf()
        key = f"{name}|{mode}"
        for rep in range(reps):
            if (key, rep) in done:
                continue
            g = rng_for("jboot", key, rep, seed_shift)
            if mode == "joint":
                Bb, Wb = joint_resample(B, W, MD, g)
            else:
                Bb, Wb = boot_side(B, g), boot_side(W, g)
            s0 = SEED + 31 * seed_shift + 1000 * rep
            b, bn = draws(Bb, MD, HA, n, g, J_D, s0)
            w, _ = draws(Wb, "X", "Y", n, g, J_D, s0 + 500)
            f.write(json.dumps(dict(job="jboot", cond=key, rep=rep, seed_shift=seed_shift, n=n, b=b, bnull=bn, w=w)) + "\n")
            if rep % 20 == 19:
                f.flush()
        f.flush()
        print("jboot", key, "n", n, flush=True)


def run(job):
    path = HERE / f"draws_{job}.jsonl"
    done = set()
    if path.exists():
        for l in open(path):
            r = json.loads(l)
            done.add((r["cond"], r["rep"]) if "rep" in r else r["cond"])
    with open(path, "a") as f:
        if job == "hpoint":
            job_hpoint(f, done)
        elif job == "hboot":
            job_hboot(f, done)
        elif job == "joint":
            job_jboot(f, done, "joint")
        elif job == "indep20":
            job_jboot(f, done, "indep")
        elif job == "rt":
            # red team (exploratory, specified in the prereg): seed, split choice, near-copy removal
            job_hpoint(f, {c for c in done if isinstance(c, str)}, "seed", seed_shift=1)
            job_hpoint(f, {c for c in done if isinstance(c, str)}, "FvAB")
            job_hpoint(f, {c for c in done if isinstance(c, str)}, "neardrop")
        elif job == "rtboot":
            sub = {c for c in done if isinstance(c, tuple)}
            job_hboot(f, sub, "FvAB", reps=RT_REPS)
            job_hboot(f, sub, "neardrop", reps=RT_REPS)
            job_hboot(f, {c for c in done if isinstance(c, tuple)}, "seed", seed_shift=1, reps=RT_REPS)
            job_jboot(f, sub, "joint", seed_shift=1, reps=RT_REPS, only={"MDHA_m77_seal", "MDHA_icit_sealtype"})
        else:
            raise ValueError(job)


# =========================================================================== report
def pct(d):
    d = np.asarray(d, float)
    return dict(median=float(np.median(d)), lo=float(np.percentile(d, 2.5)), hi=float(np.percentile(d, 97.5)),
                q05=float(np.percentile(d, 5)), q95=float(np.percentile(d, 95)))


def summarise_boot(rs):
    df, dc = [], []
    for r in rs:
        if not r["b"] or not r["w"]:
            continue
        b, w, nu = med(r["b"]), med(r["w"]), med(r["bnull"])
        df.append(b - w); dc.append(b - max(w, nu))
    if not df:
        return dict(failed=True)
    p = pct(df)
    return dict(n_side=rs[0]["n"], reps=len(df), d_floor=p, d_cons=pct(dc),
                includes_zero=bool(p["lo"] <= 0), tost=bool(p["q05"] > -MARGIN and p["q95"] < MARGIN),
                m_star=float(max(abs(p["q05"]), abs(p["q95"]))), upper95=p["q95"], above_margin=bool(p["q05"] >= MARGIN))


def load(job):
    p = HERE / f"draws_{job}.jsonl"
    return [json.loads(l) for l in open(p)] if p.exists() else []


def report():
    out = dict(prereg="docs/prereg/uniformity_referee_checks.md")
    hp = {}
    for r in load("hpoint") + load("rt"):
        key = r["cond"] + (f"|seed{r['seed_shift']}" if r.get("seed_shift") else "")
        if not r.get("b"):
            hp[key] = dict(n=r["n"], untestable=True); continue
        b, w, wmd = med(r["b"]), med(r["w"]), med(r["wmd"])
        power = float(np.mean(np.array(r["power"]) - w >= MARGIN))
        d = b - w
        verdict = ("underpowered" if power < 0.80 else "beyond the Harappa floor" if d >= MARGIN else
                   "not beyond the Harappa floor")
        hp[key] = dict(n=r["n"], floor_sides=r["n_floor_sides"], between=b, null=med(r["bnull"]), floor_ha=w,
                       floor_md_same_n=wmd, delta_ha=d, delta_md_same_n=b - wmd, power_q15=power, point_verdict=verdict)
    out["a_point"] = hp
    hb = defaultdict(list)
    for r in load("hboot") + [x for x in load("rtboot") if x["job"] == "hboot"]:
        hb[r["cond"] + (f"|seed{r['seed_shift']}" if r.get("seed_shift") else "")].append(r)
    out["a_boot"] = {k: summarise_boot(v) for k, v in hb.items()}
    a_prim = out["a_boot"].get("m77_seal|mound|indep", {})
    if a_prim and not a_prim.get("failed"):
        pv = hp.get("m77_seal|mound", {})
        if pv.get("power_q15", 0) < 0.80:
            v = "UNDERPOWERED"
        elif a_prim["d_floor"]["lo"] > 0:
            v = "BEYOND (interval excludes zero)"
        else:
            v = "WITHIN (interval includes zero)"
        out["a_primary_verdict"] = v
        out["a_secondary_all_include_zero"] = all(out["a_boot"][k]["includes_zero"] for k in out["a_boot"]
                                                  if k.endswith("|rand|indep") and not out["a_boot"][k].get("failed"))
    jb = defaultdict(list)
    for r in load("joint") + load("indep20") + [x for x in load("rtboot") if x["job"] == "jboot"]:
        jb[r["cond"] + (f"|seed{r['seed_shift']}" if r.get("seed_shift") else "")].append(r)
    out["b_boot"] = {k: summarise_boot(v) for k, v in jb.items()}
    head = [out["b_boot"].get(f"MDHA_{fam}|joint") for fam in IFAMS]
    if all(h and not h.get("failed") for h in head):
        out["b_every_interval_includes_zero"] = all(h["includes_zero"] for h in head)
        mx = max(h["m_star"] for h in head)
        out["b_max_m_star"] = mx
        out["b_upper_limit_verdict"] = ("~0.11 holds" if 0.095 <= mx <= 0.115 else
                                        "tighter than 0.11" if mx < 0.095 else "wider than 0.11")
        out["b_tost_any"] = any(h["tost"] for h in head)
    # secondary: Ur III (ORACC Umma reigns, R1 replicates) minus Indus joint replicates
    ur = [r for r in map(json.loads, open(ROOT / "experiments/uniformity_paper/revision/draws_boot.jsonl"))
          if r["cond"] == "REF_ur3_U_reign" and r["b"] and r["w"]]
    ur_d = {r["rep"]: med(r["b"]) - med(r["w"]) for r in ur}
    con = {}
    for fam in IFAMS:
        rs = {r["rep"]: med(r["b"]) - med(r["w"]) for r in jb.get(f"MDHA_{fam}|joint", []) if r["b"] and r["w"]}
        D = [ur_d[k] - rs[k] for k in sorted(set(ur_d) & set(rs))]
        if D:
            p = pct(D)
            con[fam] = dict(reps=len(D), **p, above_zero=bool(p["lo"] > 0), above_margin=bool(p["q05"] >= MARGIN))
    out["b_contrast_ur3_minus_indus_joint"] = con
    json.dump(out, open(HERE / "results.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if not k.startswith(("a_point", "a_boot", "b_boot"))}, indent=1))


# =========================================================================== sizes (no scoring)
def sizes():
    for name, (Bf, Wf, sides, fam) in {**h_rows(), **h_rows("FvAB"), **h_rows("neardrop")}.items():
        W = Wf()
        print(f"(a) {name:28s} floor sides {dict(Counter(t['site'] for t in W))} n {h_n(Bf, Wf, sides)}", flush=True)
    for name, (Bf, Wf, nf) in j_pools().items():
        B, W = Bf(), Wf()
        mdB = {t["id"] for t in B if t["site"] == MD}; mdW = {t["id"] for t in W}
        print(f"(b) {name:22s} B {dict(Counter(t['site'] for t in B))} W {dict(Counter(t['site'] for t in W))} "
              f"n {nf()} MD ids shared {len(mdB & mdW)} / B-only {len(mdB - mdW)} / W-only {len(mdW - mdB)}", flush=True)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "sizes"
    if mode == "run":
        run(sys.argv[2])
    elif mode == "report":
        report()
    else:
        sizes()
