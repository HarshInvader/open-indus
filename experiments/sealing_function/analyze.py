"""Pre-registered tests H1, S0, S1, S2 (+ M77 replication of S1/S2). docs/prereg/sealing_function.md.

Run: .venv/bin/python -I experiments/sealing_function/analyze.py   (after build_table.py)
Writes results.json and prints the log (saved as analyze.log).
"""
import csv
import json
import random
import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

OUT = Path(__file__).resolve().parent
SEED = 20261114
NPERM = 20000
rng = random.Random(SEED)

W_TITLES = {"T347": [("W760",)], "T8": [("W100",)], "TB336": [("W705", "W033")],
            "TB249": [("W590", "W390"), ("W590", "W405")]}
M_TITLES = {"T347": [("M347",)], "T8": [("M8",)], "TB336": [("M336", "M89")],
            "TB249": [("M249", "M161"), ("M249", "M162")]}
CLOSERS_W = {"jar": "W740", "arrow": "W520"}
ELE = "W817 W002 W048 W740"


def runs(text):
    out, cur = [], []
    for s in text.split():
        if s in ("#", "|"):
            if cur:
                out.append(cur)
            cur = []
        else:
            cur.append(s)
    if cur:
        out.append(cur)
    return out


def has(text, pats):
    for r in runs(text):
        for p in pats:
            k = len(p)
            if any(tuple(r[i:i + k]) == p for i in range(len(r) - k + 1)):
                return True
    return False


def titles_of(text, T):
    return {t for t, pats in T.items() if has(text, pats)}


def last_sign(text):
    r = [s for s in text.split() if s not in ("#", "|")]
    return r[-1] if r else None


def pval(obs, null):
    return (1 + sum(x >= obs for x in null)) / (len(null) + 1)


def holm(ps):
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    adj, run = [0] * len(ps), 0
    for k, i in enumerate(order):
        run = max(run, min(1, (len(ps) - k) * ps[i]))
        adj[i] = run
    return adj


def load():
    rows = list(csv.DictReader(open(OUT / "sealings.csv")))
    for r in rows:
        r["face_list"] = [f.strip() for f in r["faces"].split(" | ")] if r["faces"] else []
        r["legible"] = [f for f in r["face_list"] if f.replace("#", "").strip()]
        r["multi"] = int(r["multi"])
    return rows


def stratum(ctx):
    return {"W": "W", "W1": "W", "W2": "W2"}.get(ctx, "O?")


# ------------------------------------------------------------------ H1 / S0
def door_test(units, lab_of, target, T_names, log, label):
    """units: list of (stratum, label, set_of_titles). target = set of labels counted as 'in'."""
    strata = defaultdict(list)
    for i, (s, l, _) in enumerate(units):
        strata[s].append(i)
    labels = [u[1] for u in units]
    n_in = sum(l in target for l in labels)
    n_out = len(units) - n_in
    res = {}
    obs = {t: sum(1 for (s, l, ts) in units if l in target and t in ts) for t in T_names}
    tot = {t: sum(1 for (s, l, ts) in units if t in ts) for t in T_names}
    null = {t: [] for t in T_names}
    for _ in range(NPERM):
        lab = list(labels)
        for s, idx in strata.items():
            sub = [labels[i] for i in idx]
            rng.shuffle(sub)
            for i, v in zip(idx, sub):
                lab[i] = v
        for t in T_names:
            null[t].append(sum(1 for i, u in enumerate(units) if lab[i] in target and t in u[2]))
    for t in T_names:
        a, b = obs[t], tot[t] - obs[t]
        er = (a / n_in) / (b / n_out) if b and n_in else (float("inf") if a else 0.0)
        res[t] = dict(a=a, n_in=n_in, b=b, n_out=n_out, ER=er, p=pval(a, null[t]),
                      null_mean=sum(null[t]) / NPERM)
    ad = holm([res[t]["p"] for t in T_names])
    for t, q in zip(T_names, ad):
        res[t]["p_holm"] = q
        r = res[t]
        log(f"  {label} {t}: in-class {r['a']}/{r['n_in']}  other {r['b']}/{r['n_out']}  ER={r['ER']:.2f}  "
            f"null mean {r['null_mean']:.2f}  p={r['p']:.4f}  Holm={q:.4f}")
    return res


def power_h1(units, target, t, rate_mult=3.0, reps=500, nperm=2000):
    """Plant: title present on 'in' units with prob = mult x observed out-rate (1/n_out if 0); others as observed.
    Success = a >= 2, ER >= 3 and 4 x p < 0.05 (Holm worst case over 4 titles)."""
    import numpy as np
    n_in = sum(u[1] in target for u in units)
    out = [u for u in units if u[1] not in target]
    r_out = sum(t in u[2] for u in out) / len(out)
    if r_out == 0:
        r_out = 1 / len(out)
    p_in = min(1.0, rate_mult * r_out)
    g = np.random.default_rng(SEED + 7)
    isin = np.array([u[1] in target for u in units])
    strata = defaultdict(list)
    for i, u in enumerate(units):
        strata[u[0]].append(i)
    P = np.zeros((nperm, len(units)), dtype=bool)  # permuted 'in' indicators
    for k in range(nperm):
        for s, idx in strata.items():
            P[k, idx] = g.permutation(isin[idx])
    base = np.array([t in u[2] for u in units])
    hits = 0
    for _ in range(reps):
        pres = np.where(isin, g.random(len(units)) < p_in, base)
        a = int((pres & isin).sum()); b = int(pres.sum()) - a
        if a < 2 or (b and (a / n_in) < 3 * (b / len(out))):
            continue
        null = (P & pres).sum(1)
        p = (1 + (null >= a).sum()) / (nperm + 1)
        hits += 4 * p < 0.05
    return dict(p_in_planted=p_in, r_out=r_out, n_in=n_in, power=hits / reps)


# ------------------------------------------------------------------ S1 / S2
def s1(objs, is_target, log, label):
    """objs: list of (site, multi, [faces]). Slots = faces; shuffle faces among slots within site."""
    slots = defaultdict(list)  # site -> list of multi flags per slot
    faces = defaultdict(list)
    for site, multi, fs in objs:
        for f in fs:
            slots[site].append(multi)
            faces[site].append(f)
    obs = sum(m for s in slots for m, f in zip(slots[s], faces[s]) if is_target(f))
    ntar = sum(1 for s in faces for f in faces[s] if is_target(f))
    null = []
    for _ in range(NPERM):
        k = 0
        for s in slots:
            fs = list(faces[s])
            rng.shuffle(fs)
            k += sum(m for m, f in zip(slots[s], fs) if is_target(f))
        null.append(k)
    nm = sum(null) / NPERM
    p = pval(obs, null)
    log(f"  {label}: target faces {ntar}, on multi sealings {obs} (share {obs / ntar if ntar else 0:.2f}) vs null {nm:.2f}; p={p:.4f}")
    return dict(n_target_faces=ntar, on_multi=obs, share=obs / ntar if ntar else None, null_mean=nm, p=p)


def s2(objs, is_target, log, label):
    """objs: multi sealings with >= 2 legible distinct faces: (site, [faces]). Statistic = mixed pairs."""
    groups = defaultdict(list)
    for site, fs in objs:
        groups[site].append(len(fs))
    faces = defaultdict(list)
    for site, fs in objs:
        faces[site].extend(fs)

    def stat(site_faces):
        mixed, tf_alone_partner, tf = 0, 0, 0
        for site, sizes in groups.items():
            fs = site_faces[site]
            i = 0
            for n in sizes:
                grp = fs[i:i + n]
                i += n
                flags = [is_target(f) for f in grp]
                for a, b in combinations(flags, 2):
                    mixed += a != b
                for j, fl in enumerate(flags):
                    if fl:
                        tf += 1
                        tf_alone_partner += not any(flags[:j] + flags[j + 1:])
        return mixed, tf, tf_alone_partner

    obs, tf, tfa = stat(faces)
    null, nulla = [], []
    for _ in range(NPERM):
        sh = {}
        for s in faces:
            fs = list(faces[s])
            rng.shuffle(fs)
            sh[s] = fs
        m, t2, a2 = stat(sh)
        null.append(m)
        nulla.append(a2 / t2 if t2 else 0)
    nm = sum(null) / NPERM
    p = pval(obs, null)
    npairs = sum(n * (n - 1) // 2 for sizes in groups.values() for n in sizes)
    log(f"  {label}: {sum(len(v) for v in groups.values())} sealings, {npairs} pairs; title faces {tf}; mixed pairs {obs} vs null {nm:.2f}; p={p:.4f}; "
        f"title faces with only non-title partners {tfa}/{tf} vs null share {sum(nulla) / NPERM:.2f}")
    return dict(n_sealings=sum(len(v) for v in groups.values()), n_pairs=npairs, title_faces=tf, mixed=obs,
                null_mean=nm, p=p, title_with_nontitle_only=tfa, null_share_nontitle_only=sum(nulla) / NPERM)


def main():
    lines = []

    def log(s=""):
        print(s)
        lines.append(s)

    rows = load()
    R = {}
    T_names = list(W_TITLES)
    # ---------- descriptive: titles on sealings
    log("== Titles on ICIT sealing faces (all sites)")
    for t in T_names:
        objs = [r for r in rows if any(t in titles_of(f, W_TITLES) for f in r["legible"])]
        log(f"  {t}: {len(objs)} objects: " + "; ".join(f"{r['site']} {r['object']} [{r['back_type'] or '-'}]" for r in objs))
    # ---------- H1
    lot = [r for r in rows if r["site"] == "Lothal" and r["back_class"] and r["legible"]]
    units = [(stratum(r["context_ft"]), r["back_class"], set().union(*[titles_of(f, W_TITLES) for f in r["legible"]])) for r in lot]
    log(f"\n== H1: DOOR (pegs-on-wall) vs other diagnostic backs, Lothal sealings with a legible face: n={len(units)}, "
        f"DOOR {sum(u[1] == 'DOOR' for u in units)}; strata {dict(Counter(u[0] for u in units))}")
    log("  back class x any title: " + str(dict(Counter((u[1], bool(u[2])) for u in units))))
    R["H1"] = door_test(units, None, {"DOOR"}, T_names, log, "H1")
    R["H1_power"] = {}
    for t in T_names:
        pw = power_h1(units, {"DOOR"}, t)
        R["H1_power"][t] = pw
        log(f"  power {t} at ER=3: planted DOOR rate {pw['p_in_planted']:.2f} (out-rate {pw['r_out']:.3f}, n_door {pw['n_in']}) -> power {pw['power']:.3f}")
    sup = [t for t in T_names if R["H1"][t]["a"] >= 2 and R["H1"][t]["ER"] >= 3 and R["H1"][t]["p_holm"] < 0.05]
    maxpow = max(R["H1_power"][t]["power"] for t in T_names)
    R["H1_verdict"] = "supported" if sup else ("untestable at this n" if maxpow < 0.5 else "refuted at stated power")
    log(f"  H1 verdict: {R['H1_verdict']} (supported titles {sup}; max power {maxpow:.3f})")
    # robustness: distinct (text, back class) pairs, and without the elephant text
    for drop_ele in (False, True):
        pairs = {(f, r["back_class"], stratum(r["context_ft"])) for r in lot for f in r["legible"]
                 if not (drop_ele and f.replace("#", "").split() == ELE.split())}
        u2 = [(s, b, titles_of(f, W_TITLES)) for f, b, s in pairs]
        log(f"  robustness: distinct (face text, back) pairs{' without elephant' if drop_ele else ''}: n={len(u2)}, DOOR {sum(u[1]=='DOOR' for u in u2)}")
        R[f"H1_distinct{'_noele' if drop_ele else ''}"] = door_test(u2, None, {"DOOR"}, T_names, log, "  H1d")
    # ---------- S0
    units0 = [(s, ("FIXED" if b in ("DOOR", "FIXED_OTHER") else "CONTAINER"), ({"ANY"} if ts else set())) for s, b, ts in units]
    log(f"\n== S0: FIXED (pegs + lockers + structures) vs CONTAINER, any title; FIXED {sum(u[1]=='FIXED' for u in units0)} / {len(units0)}")
    R["S0"] = door_test(units0, None, {"FIXED"}, ["ANY"], log, "S0")
    # ---------- S1
    log("\n== S1: title-bearing faces on multi-impression sealings (faces shuffled among slots within site)")
    objs = [(r["site"], r["multi"], r["legible"]) for r in rows if r["legible"]]
    anyt = lambda f: bool(titles_of(f, W_TITLES))
    R["S1"] = s1(objs, anyt, log, "S1 any title (ICIT, all sites)")
    R["S1_lothal"] = s1([o for o in objs if o[0] == "Lothal"], anyt, log, "  descriptive Lothal only")
    R["S1_per_title"] = {t: s1(objs, (lambda f, t=t: t in titles_of(f, W_TITLES)), log, f"  descriptive {t}") for t in T_names}
    R["S1_closers"] = {c: s1(objs, (lambda f, w=w: last_sign(f) == w), log, f"  descriptive closer {c}") for c, w in CLOSERS_W.items()}
    # ---------- S2
    log("\n== S2: mixed title + non-title pairs on sealings with >= 2 legible distinct faces")
    multi2 = [(r["site"], sorted(set(f for f in r["legible"]))) for r in rows if r["multi"] and len(set(r["legible"])) >= 2]
    R["S2"] = s2(multi2, anyt, log, "S2 any title (ICIT)")
    # ---------- M77 replication
    log("\n== M77 replication (multi-side sealing objects outside Harappa; M-space titles)")
    mrows = list(csv.DictReader(open(OUT / "sealings_m77.csv")))
    mobjs = []
    for r in mrows:
        fs = [f.strip() for f in r["sides"].split(" | ") if f.strip()]
        mobjs.append((r["site"], int(r["multi"]), fs))
    anym = lambda f: bool(titles_of(f, M_TITLES))
    for t in M_TITLES:
        log(f"  {t}: on {sum(1 for o in mobjs for f in o[2] if t in titles_of(f, M_TITLES))} M77 sealing sides")
    R["S1_m77"] = s1(mobjs, anym, log, "S1 any title (M77)")
    m2 = [(s, sorted(set(fs))) for s, m, fs in mobjs if m and len(set(fs)) >= 2]
    R["S2_m77"] = s2(m2, anym, log, "S2 any title (M77)")
    a = 0.05 / 3
    R["secondary_alpha"] = a
    R["verdicts"] = {
        "H1": R["H1_verdict"],
        "S0": "supported" if R["S0"]["ANY"]["p"] < a else "not supported",
        "S1": "supported" if R["S1"]["p"] < a else "not supported",
        "S1_always": bool(R["S1"]["share"] and R["S1"]["share"] >= 0.8 and R["S1"]["n_target_faces"] >= 3 and R["S1"]["p"] < a),
        "S2": "supported" if R["S2"]["p"] < a else "not supported",
    }
    log(f"\nVerdicts: {R['verdicts']}")
    json.dump(R, open(OUT / "results.json", "w"), indent=1, default=str)
    open(OUT / "analyze.log", "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
