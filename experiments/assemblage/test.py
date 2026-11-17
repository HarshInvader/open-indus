"""R7 assemblage test (prereg docs/prereg/assemblage.md). Joins inscribed texts to the
frozen craft coding (craft_units.csv) and runs the pre-registered permutation test.

Run from repo root:  .venv/bin/python -I experiments/assemblage/test.py
Writes assemblages.csv, linked_objects.csv, results.json, run.log (stdout).
"""
import csv
import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SEED = 20261114
NPERM = 10000
CRAFTS = ["BEAD", "SHELL", "COPPER", "SEALCUT", "WEIGHT", "KILN", "STORAGE"]

merged = json.load(open(ROOT / "sources/paragorth_Indus-/data/derived/merged-corpus-reading-order.json"))
coding = list(csv.DictReader(open(HERE / "craft_units.csv")))
bridge = json.load(open(ROOT / "sources/shaunmortal_indus/data/bridge_WM.json"))
W2M = {int(w): "M%d" % v["M"][0] for w, v in bridge.items()}

# ---------------- craft labels per unit ----------------
craft_of = defaultdict(set)
lothal_units = set()
for r in coding:
    key = (r["site"], r["unit"])
    if r["site"] == "Lothal":
        lothal_units.add(r["unit"])
    if r["craft"] in CRAFTS:
        craft_of[key].add(r["craft"])
# Marshall VS units are recorded without block ("VS|<block>|<house>" from regex) -> keep as is


def md_unit(r):
    area = r["area-section"].strip()
    bh = r["block-house"].strip()
    m = re.match(r"^(\d+A?)([IVXL]+)?-?$", bh)
    if not m:
        return None
    if area in ("DKG. (S)", "DKG. (N)"):
        a = area
    elif area.startswith("VS"):
        a = "VS"
    elif area in ("HRA", "HRB"):
        a = area
    elif area.startswith("DK") and len(area) == 3 and area[2] in "ABCDE":
        a = area
    else:
        return None
    return f"{a}|{m.group(1)}|{m.group(2) or '-'}", a


def unit_of(r):
    s = r["site"]
    if s == "Harappa":
        m = re.match(r"^-?([A-Z])(\d+)/", r["room-grid"].strip())
        if not m:
            return None
        area = r["area-section"]
        mm = re.match(r"^(AB|ET|EC|E|F|D|G|H|J|I)", area)
        return f"{m.group(1)}{int(m.group(2))}", (mm.group(1) if mm else "?")
    if s == "Mohenjo-daro":
        return md_unit(r)
    if s == "Chanhu-daro":
        m = re.search(r"sq\.?\s*(\d+)\s*/\s*([A-Z])", r["room-grid"])
        return (f"{m.group(1)}/{m.group(2)}", "all") if m else None
    if s == "Lothal":
        c = r["cisi"].strip()
        return (c, "all") if c in lothal_units else None
    return None


def is_seal(t):
    return t.startswith("SEAL")


# ---------------- link ----------------
linked = []
for r in merged:
    u = unit_of(r)
    if u is None:
        continue
    seq = tuple(x for x in r["seq"] if x > 0)
    if not seq:
        continue
    linked.append({"site": r["site"], "unit": u[0], "stratum": u[1], "type": r["type"],
                   "cisi": r["cisi"], "seq": seq})

with open(HERE / "linked_objects.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["site", "unit", "stratum", "type", "cisi", "crafts", "seq_wells"])
    for x in linked:
        w.writerow([x["site"], x["unit"], x["stratum"], x["type"], x["cisi"],
                    ";".join(sorted(craft_of.get((x["site"], x["unit"]), []))),
                    " ".join(str(s) for s in x["seq"])])

# assemblages.csv: one row per unit (coded or linked)
units = defaultdict(lambda: {"stratum": "", "n_seal": 0, "n_nonseal": 0, "types": Counter()})
for x in linked:
    u = units[(x["site"], x["unit"])]
    u["stratum"] = x["stratum"]
    u["n_seal" if is_seal(x["type"]) else "n_nonseal"] += 1
    u["types"][x["type"]] += 1
for key in craft_of:
    units[key]
evid = defaultdict(list)
for r in coding:
    evid[(r["site"], r["unit"])].append(f'{r["craft"]}: {r["source"]}')
with open(HERE / "assemblages.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["site", "unit", "stratum", "crafts", "n_inscribed_seal", "n_inscribed_nonseal", "object_types", "craft_sources"])
    for (s, un), u in sorted(units.items()):
        w.writerow([s, un, u["stratum"], ";".join(sorted(craft_of.get((s, un), []))), u["n_seal"], u["n_nonseal"],
                    ";".join(f"{k}:{v}" for k, v in u["types"].most_common()),
                    " | ".join(sorted(set(evid.get((s, un), []))))[:600]])


# ---------------- test ----------------
def site_matrices(objset):
    """Per site: unit list, strata, sign x unit distinct-text counts."""
    out = {}
    by_site = defaultdict(lambda: defaultdict(set))
    strat = {}
    for x in linked:
        if objset == "nonseal" and is_seal(x["type"]):
            continue
        by_site[x["site"]][x["unit"]].add(x["seq"])
        strat[(x["site"], x["unit"])] = x["stratum"]
    for s, ud in by_site.items():
        ulist = sorted(ud)
        signs = sorted({g for u in ulist for t in ud[u] for g in set(t)})
        sidx = {g: i for i, g in enumerate(signs)}
        N = np.zeros((len(signs), len(ulist)), dtype=np.int32)
        for j, u in enumerate(ulist):
            for t in ud[u]:
                for g in set(t):
                    N[sidx[g], j] += 1
        out[s] = {"units": ulist, "strata": [strat[(s, u)] for u in ulist], "signs": signs, "N": N}
    return out


def perms(strata, n, rng):
    strata = np.array(strata)
    idx = np.tile(np.arange(len(strata)), (n, 1))
    for st in np.unique(strata):
        pos = np.where(strata == st)[0]
        for k in range(n):
            idx[k, pos] = pos[rng.permutation(len(pos))]
    return idx


def run(objset, rng, log):
    M = site_matrices(objset)
    res = {"objset": objset, "sites": {}, "contexts": {}}
    site_ctx = {}
    for s, m in M.items():
        c_all = {c: np.array([1 if c in craft_of.get((s, u), set()) else 0 for u in m["units"]]) for c in CRAFTS}
        m["P"] = perms(m["strata"], NPERM, rng)
        res["sites"][s] = {"linked_units": len(m["units"]), "distinct_text_records": int(m["recs"].sum()),
                           "eligible_signs": int((m["N"].sum(axis=1) >= 5).sum())}
        site_ctx[s] = c_all
    eligible = {}  # (sign, ctx) -> {site: (obs, exp, p)}
    tested_detail = {}
    for s, m in M.items():
        N = m["N"]
        freq = N.sum(axis=1)
        for c in CRAFTS:
            cv = site_ctx[s][c]
            n_in = int(cv.sum())
            res["contexts"].setdefault(c, {})[s] = {"ctx_units": n_in, "other_units": int(len(cv) - n_in)}
            if n_in < 2 or n_in == len(cv):
                continue
            ok = np.where(freq >= 5)[0]
            if len(ok) == 0:
                continue
            obs = N[ok] @ cv
            Pc = cv[m["P"]]  # NPERM x units
            null = (Pc @ N[ok].T)  # NPERM x signs
            exp = null.mean(axis=0)
            p = (1 + (null >= obs).sum(axis=0)) / (1 + NPERM)
            for k, i in enumerate(ok):
                g = m["signs"][i]
                eligible.setdefault((g, c), {})[s] = (int(obs[k]), float(exp[k]), float(p[k]), null[:, k])
    testable = {k: v for k, v in eligible.items() if len(v) >= 2}
    pairs = []
    for (g, c), v in testable.items():
        sites = sorted(v)
        for a in range(len(sites)):
            for b in range(a + 1, len(sites)):
                pairs.append((g, c, sites[a], sites[b]))
    K = len(pairs)
    res["K"] = K
    alpha = math.sqrt(0.05 / K) if K else None
    res["alpha_pair"] = alpha
    rows, replicated, G = [], [], 0
    Gnull = np.zeros(NPERM, dtype=np.int64)
    for g, c, a, b in pairs:
        oa, ea, pa, na = testable[(g, c)][a]
        ob, eb, pb, nb = testable[(g, c)][b]
        ra, rb = (oa / ea if ea > 0 else float("inf")), (ob / eb if eb > 0 else float("inf"))
        row = {"sign_W": g, "sign_M": W2M.get(g, ""), "context": c, "siteA": a, "obsA": oa, "expA": round(ea, 2), "pA": pa,
               "siteB": b, "obsB": ob, "expB": round(eb, 2), "pB": pb}
        rows.append(row)
        both = pa <= 0.05 and pb <= 0.05 and ra >= 2 and rb >= 2
        G += both
        if pa <= alpha and pb <= alpha and ra >= 2 and rb >= 2:
            replicated.append(row)
        # null G: per-permutation p-values via rank of each null draw
        # p of a null draw k = (1 + #null >= draw_k)/(1+N); compute via sorting
        for (nul, e, key) in ((na, ea, "a"), (nb, eb, "b")):
            pass
        sa = np.sort(na); sb = np.sort(nb)
        pna = (1 + (NPERM - np.searchsorted(sa, na, side="left"))) / (1 + NPERM)
        pnb = (1 + (NPERM - np.searchsorted(sb, nb, side="left"))) / (1 + NPERM)
        Gnull += ((pna <= 0.05) & (pnb <= 0.05) & (na >= 2 * ea) & (nb >= 2 * eb)).astype(np.int64)
    res["G"] = int(G)
    res["G_null_mean"] = float(Gnull.mean())
    res["G_p"] = float((1 + (Gnull >= G).sum()) / (1 + NPERM)) if K else None
    res["replicated"] = replicated
    res["pairs"] = sorted(rows, key=lambda r: max(r["pA"], r["pB"]))
    res["testable_contexts"] = sorted({c for (_, c) in testable})
    # power
    res["power"] = power(M, site_ctx, testable, alpha, rng) if K else {}
    return res


def power(M, site_ctx, testable, alpha, rng, reps=200, nperm=2000):
    out = {}
    ctx_sites = defaultdict(set)
    for (g, c), v in testable.items():
        ctx_sites[c] |= set(v)
    for c, sites in ctx_sites.items():
        sites = sorted(sites, key=lambda s: -int(site_ctx[s][c].sum()))[:2]
        if "Harappa" in sites and "Mohenjo-daro" in ctx_sites[c] and "Mohenjo-daro" not in sites:
            sites = ["Harappa", "Mohenjo-daro"]
        out[c] = {"sites": sites}
        for OR in (3, 5):
            hits = 0
            for _ in range(reps):
                ok_all = True
                for s in sites:
                    m = M[s]
                    N = m["N"]
                    freq = N.sum(axis=1)
                    target = float(np.median(freq[freq >= 5]))
                    recs = m["recs"]
                    cv = site_ctx[s][c]
                    tot = recs.sum()
                    # solve p_out so that expected count = target
                    lo, hi = 1e-6, 0.999
                    for _i in range(50):
                        po = (lo + hi) / 2
                        pi = OR * po / (1 - po + OR * po)
                        e = (recs * np.where(cv == 1, pi, po)).sum()
                        lo, hi = (po, hi) if e < target else (lo, po)
                    pi = OR * po / (1 - po + OR * po)
                    x = rng.binomial(recs, np.where(cv == 1, pi, po))
                    P = m["P"][:nperm]
                    obs = x @ cv
                    null = cv[P] @ x
                    p = (1 + (null >= obs).sum()) / (1 + nperm)
                    e = null.mean()
                    if not (p <= alpha and e > 0 and obs / e >= 2):
                        ok_all = False
                        break
                hits += ok_all
            out[c][f"OR{OR}"] = hits / reps
    return out


def unit_sizes(m):
    # number of distinct-text records per unit = max over... recompute from linked
    return m["recs"]


def main():
    rng = np.random.default_rng(SEED)
    log = []
    allres = {}
    for objset in ("nonseal", "all"):
        M = None
        res = None
        # attach record counts
        global site_matrices
        res = run_with_recs(objset, rng)
        allres[objset] = res
    return allres


def run_with_recs(objset, rng):
    orig = site_matrices

    def sm(o):
        M = orig(o)
        by = defaultdict(lambda: defaultdict(set))
        for x in linked:
            if o == "nonseal" and is_seal(x["type"]):
                continue
            by[x["site"]][x["unit"]].add(x["seq"])
        for s, m in M.items():
            m["recs"] = np.array([len(by[s][u]) for u in m["units"]])
        return M
    globals()["site_matrices"] = sm
    try:
        return run(objset, rng, None)
    finally:
        globals()["site_matrices"] = orig


if __name__ == "__main__":
    allres = main()
    summary = {}
    for objset, res in allres.items():
        print(f"\n===== object set: {objset} =====")
        for c, d in res["contexts"].items():
            print(f"  {c}: " + ", ".join(f"{s} {v['ctx_units']}/{v['ctx_units'] + v['other_units']}" for s, v in d.items()))
        print(f"  K testable (sign, context, site-pair) = {res['K']}; alpha_pair = {res['alpha_pair']}")
        print(f"  testable contexts: {res['testable_contexts']}")
        print(f"  replicated pairs: {len(res['replicated'])}")
        for r in res["replicated"]:
            print("   ", r)
        print(f"  G = {res['G']} (null mean {res['G_null_mean']:.2f}, p = {res['G_p']})")
        for r in res["pairs"][:15]:
            print("   top:", r)
        print("  power:", res["power"])
        summary[objset] = {k: v for k, v in res.items() if k != "pairs"}
        summary[objset]["top_pairs"] = res["pairs"][:25]
    json.dump(summary, open(HERE / "results.json", "w"), indent=1, default=float)
