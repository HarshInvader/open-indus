"""Shared code for the roof-vs-context test (docs/prereg/roof_context.md).

Roofed set: FROZEN rows with modifier ROOF and confidence high/medium in
experiments/modifiers/decomp.csv (Mahadevan) and experiments/modifiers/w_decomp.csv (Wells).
Both files are hash-frozen in docs/prereg/HASHES.txt; they are read, never edited.

Run scripts from the repo root: .venv/bin/python experiments/roof_context/<script>.py
"""
import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from corpus.load import m77_texts, m77_lines, icit_texts, dev_heldout, distinct  # noqa: E402,F401

HERE = Path(__file__).resolve().parent
SEED = 20261115
CONF = ("high", "medium")
FROZEN_SHA = {
    "experiments/modifiers/decomp.csv": "b0c849648852e8d1b40df0b5bf901f1d73ec2d2373c34260522bb9325877291e",
    "experiments/modifiers/w_decomp.csv": "d908461551c2bee8b249b68b8f2e1f6c6970ed8e3b76cb65cfb42072ce71e05f",
}


def check_frozen():
    for p, h in FROZEN_SHA.items():
        got = hashlib.sha256(open(ROOT / p, "rb").read()).hexdigest()
        assert got == h, f"{p} changed since freeze ({got})"


def roof_pairs(which="M"):
    """{base: [derived, ...]} for ROOF rows at high/medium confidence."""
    check_frozen()
    p = ROOT / ("experiments/modifiers/decomp.csv" if which == "M" else "experiments/modifiers/w_decomp.csv")
    g = defaultdict(list)
    for r in csv.DictReader(open(p)):
        if r["modifier"] == "ROOF" and r["confidence"] in CONF:
            g[r["base"]].append(r["sign"])
    return dict(g)


# ---------------- corpora ----------------
def _toks(seq):
    return [s for s in seq if s not in ("|", "#")]


def icit_class(ty):
    ty = (ty or "").upper()
    if ty.startswith("TAG"):
        return "sealing"
    if ty.startswith("SEAL") and not ty.startswith("SEAL:C"):  # SEAL:C = cylinder (mostly foreign)
        return "seal"
    return None


def icit_seal_sealing():
    """Distinct (W sequence, class, site) units, class in {seal, sealing}. Breaks allowed."""
    seen, out = set(), []
    for t in icit_texts():
        c = icit_class(t["type"])
        s = tuple(x for x in _toks(t["seq"]) if x.startswith("W"))
        if c is None or not s:
            continue
        k = (s, c, t["site"])
        if k in seen:
            continue
        seen.add(k)
        out.append({"seq": s, "ctx": c == "sealing", "stratum": t["site"], "site": t["site"]})
    return out


M77_TRUE_SEALING_SITES = {"Lothal", "Kalibangan", "Other sites"}  # MD/Harappa 'sealing' = mostly moulded tablets


def m77_seal_sealing():
    """M77 distinct (seq, class, site), restricted to sites whose 'sealing' class is clay sealings."""
    seen, out = set(), []
    for t in m77_texts():
        if t["object_type"] not in ("seal", "sealing") or t["site"] not in M77_TRUE_SEALING_SITES:
            continue
        s = tuple(_toks(t["seq"]))
        if not s:
            continue
        k = (s, t["object_type"], t["site"])
        if k in seen:
            continue
        seen.add(k)
        out.append({"seq": s, "ctx": t["object_type"] == "sealing", "stratum": t["site"], "site": t["site"]})
    return out


def merged_area(site, a, f_as_nondomestic=False):
    a = (a or "").strip()
    if site == "Mohenjo-daro":
        if a.startswith("SD") or a.startswith("L"):
            return "citadel"
        if a[:2] in ("HR", "VS", "DK", "MN"):
            return "lower"
    if site == "Harappa":
        if a.startswith("AB"):
            return "citadel"
        if a.startswith("F"):
            return "citadel" if f_as_nondomestic else "lower"
        if a[:1] in ("E", "D", "J", "G", "H") and a[:2] != "--":
            return "lower"
    if site == "Dholavira":
        if "astle" in a or a.startswith("Bailey") or "Outside castle" in a or "Outside Bailey" in a:
            # 'Outside castle/Bailey' are ambiguous; counted citadel only if literally Castle/Bailey section
            if a.startswith("-Outside"):
                return None
            return "citadel"
        if a.startswith("Middle Town") or a.startswith("Lower Town") or a.startswith("Annexe"):
            return "lower"
    return None


def load_merged():
    return json.load(open(ROOT / "sources/paragorth_Indus-/data/derived/merged-corpus-reading-order.json"))


def merged_area_units(f_as_nondomestic=False):
    """Distinct (W sequence, area, site, type) units with a mapped area (MD, Harappa, Dholavira)."""
    seen, out = set(), []
    for r in load_merged():
        if r["site"] not in ("Mohenjo-daro", "Harappa", "Dholavira") or not r["seq"]:
            continue
        a = merged_area(r["site"], r["area-section"], f_as_nondomestic)
        if a is None:
            continue
        s = tuple("W%03d" % w for w in r["seq"] if isinstance(w, int))
        if not s:
            continue
        ty = r["type"].split(":")[0]
        k = (s, a, r["site"], ty)
        if k in seen:
            continue
        seen.add(k)
        out.append({"seq": s, "ctx": a == "citadel", "stratum": (r["site"], ty), "site": r["site"]})
    return out


def m77_area(site, loc):
    try:
        l = int(loc)
    except (TypeError, ValueError):
        return None
    if site == "Mohenjodaro":
        if 1 <= l <= 15:
            return "citadel"
        if 16 <= l <= 39:
            return "lower"
    if site == "Harappa":
        if 47 <= l <= 51:
            return "citadel"
        if 40 <= l <= 46 or 52 <= l <= 54:
            return "lower"
    return None


def m77_area_units():
    """Distinct (seq, area, site, object_type) M77 object sides with a mapped locus (administration t2 map)."""
    obj = defaultdict(list)
    for l in m77_lines():
        obj[(l["text_no"], l["side"])].append(l)
    seen, out = set(), []
    for ls in obj.values():
        site = ls[0]["site"]
        a = m77_area(site, ls[0]["locus"])
        if a is None:
            continue
        ls.sort(key=lambda x: x["line"])
        s = tuple(x for l in ls for x in l["signs"] if x not in ("|", "#"))
        if not s:
            continue
        k = (s, a, site, ls[0]["object_type"])
        if k in seen:
            continue
        seen.add(k)
        out.append({"seq": s, "ctx": a == "citadel", "stratum": (site, ls[0]["object_type"]), "site": site})
    return out


# ---------------- statistics ----------------
def token_table(units):
    """sign -> stratum -> [tokens, tokens in ctx]."""
    T = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    for u in units:
        for s in u["seq"]:
            c = T[s][u["stratum"]]
            c[0] += 1
            c[1] += int(u["ctx"])
    return T


def cmh_z(pairs, T):
    """Mantel-Haenszel z, derived vs base, ctx share; strata = base x unit stratum. + = derived higher."""
    a_sum = e_sum = v_sum = 0.0
    num = den = 0.0
    for b, ds in pairs.items():
        strata = set(T[b]) | {st for d in ds for st in T[d]}
        for st in strata:
            n1 = sum(T[d][st][0] for d in ds) if any(st in T[d] for d in ds) else 0
            a = sum(T[d][st][1] for d in ds) if n1 else 0
            n0, c = (T[b][st] if st in T[b] else (0, 0))
            N = n1 + n0
            m1 = a + c
            if N < 2 or n1 == 0 or n0 == 0 or m1 == 0 or m1 == N:
                continue
            a_sum += a
            e_sum += n1 * m1 / N
            v_sum += n1 * n0 * m1 * (N - m1) / (N * N * (N - 1))
            num += a * (n0 - c) / N
            den += (n1 - a) * c / N
    if v_sum == 0:
        return {"z": 0.0, "or": float("nan"), "p_up": 1.0}
    z = (a_sum - e_sum) / np.sqrt(v_sum)
    return {"z": float(z), "or": float(num / den) if den else float("inf"), "p_up": float(norm.sf(z)),
            "obs": float(a_sum), "exp": float(e_sum)}


def pair_shares(pairs, T):
    out = {}
    for b, ds in pairs.items():
        nb = sum(v[0] for v in T[b].values()); cb = sum(v[1] for v in T[b].values())
        for d in ds:
            nd = sum(v[0] for v in T[d].values()); cd = sum(v[1] for v in T[d].values())
            out[f"{d}<-{b}"] = {"derived_tok": nd, "derived_ctx": cd, "base_tok": nb, "base_ctx": cb,
                                "derived_share": cd / nd if nd else None, "base_share": cb / nb if nb else None}
    return out


def updown(pairs, T):
    up = dn = 0
    for b, ds in pairs.items():
        nb = sum(v[0] for v in T[b].values()); cb = sum(v[1] for v in T[b].values())
        nd = sum(T[d][st][0] for d in ds for st in T[d]); cd = sum(T[d][st][1] for d in ds for st in T[d])
        if nb == 0 or nd == 0:
            continue
        up += cd / nd > cb / nb
        dn += cd / nd < cb / nb
    return int(up), int(dn)


def usable(pairs, T):
    """Keep pairs where base and at least one derived form have >= 1 token in this corpus."""
    g = {}
    for b, ds in pairs.items():
        dd = [d for d in ds if d in T and sum(v[0] for v in T[d].values()) > 0]
        if dd and b in T and sum(v[0] for v in T[b].values()) > 0:
            g[b] = dd
    return g


def label_perm_test(units, pairs, n=5000, seed=SEED):
    """Null: ctx labels permuted among units within stratum. One-sided p for CMH z (derived higher)."""
    rng = np.random.default_rng(seed)
    T = token_table(units)
    g = usable(pairs, T)
    obs = cmh_z(g, T)
    by = defaultdict(list)
    for i, u in enumerate(units):
        by[u["stratum"]].append(i)
    labs = np.array([u["ctx"] for u in units])
    rel = set(g) | {d for ds in g.values() for d in ds}
    # only units containing relevant signs matter for the statistic, but permute all within strata
    zs = []
    for _ in range(n):
        lab = labs.copy()
        for idx in by.values():
            lab[idx] = rng.permutation(labs[idx])
        Tp = defaultdict(lambda: defaultdict(lambda: [0, 0]))
        for i, u in enumerate(units):
            for s in u["seq"]:
                if s in rel:
                    c = Tp[s][u["stratum"]]
                    c[0] += 1
                    c[1] += int(lab[i])
        zs.append(cmh_z(g, Tp)["z"])
    zs = np.array(zs)
    up, dn = updown(g, T)
    return {**obs, "k": len(g), "up": up, "down": dn,
            "p_perm_up": float((1 + np.sum(zs >= obs["z"] - 1e-12)) / (n + 1)),
            "pairs": pair_shares(g, T)}


def fake_modifier_test(units, pairs, n=2000, seed=SEED):
    """Null: same structure, each base and derived sign replaced by a random sign of 0.5-2x its tokens
    (widened until >= 8 candidates). One-sided p for CMH z (derived higher)."""
    rng = np.random.default_rng(seed)
    T = token_table(units)
    g = usable(pairs, T)
    obs = cmh_z(g, T)
    tot = {s: sum(v[0] for v in T[s].values()) for s in T}
    pool = np.array(sorted(tot)); pn = np.array([tot[s] for s in pool])

    def cands(k):
        lo, hi = 0.5, 2.0
        while True:
            idx = np.where((pn >= k * lo) & (pn <= k * hi))[0]
            if len(idx) >= 8 or lo < 0.01:
                return idx
            lo /= 1.5; hi *= 1.5
    struct = [(cands(tot[b]), [cands(tot[d]) for d in ds]) for b, ds in g.items()]
    zs = []
    for _ in range(n):
        used, fk = set(), {}
        for cb, cds in struct:
            b = pool[rng.choice(cb)]
            while b in used:
                b = pool[rng.choice(cb)]
            used.add(b); ds = []
            for cd in cds:
                d = pool[rng.choice(cd)]; tries = 0
                while d in used and tries < 50:
                    d = pool[rng.choice(cd)]; tries += 1
                used.add(d); ds.append(d)
            fk[b] = ds
        zs.append(cmh_z(fk, T)["z"])
    zs = np.array(zs)
    up, dn = updown(g, T)
    return {**obs, "k": len(g), "up": up, "down": dn,
            "p_fake_up": float((1 + np.sum(zs >= obs["z"] - 1e-12)) / (n + 1)),
            "pairs": pair_shares(g, T)}


def power(units, pairs, odds_ratio, n_sim=1000, seed=SEED, alpha=0.05, null="perm", n_null=500):
    """Power of the one-sided CMH z (normal approx, alpha) when derived tokens carry ctx with
    odds = OR x the stratum's overall ctx odds. Uses only marginals (token counts per stratum
    and the stratum's ctx rate over all units), not the observed derived x ctx table."""
    rng = np.random.default_rng(seed)
    T = token_table(units)
    g = usable(pairs, T)
    rate = defaultdict(lambda: [0, 0])
    for u in units:
        r = rate[u["stratum"]]; r[0] += 1; r[1] += int(u["ctx"])
    hits = 0
    for _ in range(n_sim):
        Q = defaultdict(lambda: defaultdict(lambda: [0, 0]))
        for b, ds in g.items():
            for s, orr in [(b, 1.0)] + [(d, odds_ratio) for d in ds]:
                for st, (nt, _) in T[s].items():
                    p0 = min(max(rate[st][1] / rate[st][0], 1e-6), 1 - 1e-6)
                    o = p0 / (1 - p0) * orr
                    p = o / (1 + o)
                    Q[s][st] = [nt, int(rng.binomial(nt, p))]
        hits += cmh_z(g, Q)["z"] > norm.isf(alpha)
    return hits / n_sim


def save_json(name, obj, path=None):
    p = path or HERE / "results.json"
    d = json.load(open(p)) if p.exists() else {}
    d[name] = obj
    json.dump(d, open(p, "w"), indent=1, default=float)
