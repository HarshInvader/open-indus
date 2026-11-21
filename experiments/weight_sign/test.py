"""Weight-sign test (prereg docs/prereg/weight_sign.md).

Is Parpola's sign 193 ("weight"), or the earlier-proposed M197, found more often on
inscribed objects from excavation units that held weights, once we control for how
many finds a unit has?

Run from repo root, through the compute gate:
  board/run.sh .venv/bin/python -I experiments/weight_sign/test.py
Writes experiments/weight_sign/results.json and prints a log (save as run.log).

Inputs (all frozen before this script was first run):
  experiments/assemblage/linked_objects.csv   inscribed objects -> unit, crafts, Wells signs
  experiments/weight_sign/weight_units_md.csv Hemmy (Mackay 1938 App. I) weight houses
"""
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SEED = 20261120
NPERM = 10000          # real-data permutations
GATE_REPS = 400        # planted-sign replicates per gate
GATE_PERM = 2000       # permutations inside each gate replicate
ALPHA = 0.05 / 2       # two candidates
RATIO_BAR = 2.0        # support bar on the Mantel-Haenszel rate ratio (inside vs outside weight units)
KILL_RATIO = 1.2       # refutation bar (only if the gate passed)
PLANT_RR = 3.0         # planted enrichment for the gate
GATE_POWER = 0.80
MIN_TEXTS = 5          # fewer candidate texts than this in a data set -> untestable
BINS = [1, 2, 3, 5, 10, 20, 10**9]   # unit size bins on distinct texts: 1, 2, 3-4, 5-9, 10-19, 20+

CANDIDATES = {
    "P193": {"wells": {504, 505}, "label": "Parpola 193 = M206 (W504) + M208 (W505); M207 has no Wells number"},
    "M197": {"wells": {575}, "label": "M197 (W575), the catalogue's earlier guess and the assemblage near miss"},
}
JAR = 740  # M342
DRY = "--dry" in sys.argv   # description + small gate only; prints no real-sign outcome


# ---------------------------------------------------------------- data
def load_linked():
    rows = list(csv.DictReader(open(ROOT / "experiments/assemblage/linked_objects.csv")))
    out = []
    for r in rows:
        seq = tuple(int(x) for x in r["seq_wells"].split() if x.strip().lstrip("-").isdigit() and int(x) > 0)
        if seq:
            out.append({"site": r["site"], "unit": r["unit"], "stratum": r["stratum"],
                        "weight": "WEIGHT" in r["crafts"].split(";"), "seq": seq})
    return out


def hemmy_units():
    keys = set()
    for r in csv.DictReader(open(HERE / "weight_units_md.csv")):
        b = r["block"]
        num = int("".join(ch for ch in b if ch.isdigit()))
        area = "DKG. (S)" if num <= 12 else "DKG. (N)"
        keys.add(f"{area}|{b}|{r['house']}")
    return keys


def build_sets(linked):
    """Return the two pre-registered data sets as {site: {unit: (is_weight, stratum, set_of_texts)}}."""
    units = defaultdict(lambda: defaultdict(lambda: {"w": False, "stratum": "", "texts": set()}))
    for x in linked:
        u = units[x["site"]][x["unit"]]
        u["w"] |= x["weight"]
        u["stratum"] = x["stratum"]
        u["texts"].add(x["seq"])
    # SEEN: the assemblage's own Harappa and Mohenjo-daro units and WEIGHT labels
    seen = {s: {k: (v["w"], v["stratum"], v["texts"]) for k, v in units[s].items()} for s in ("Harappa", "Mohenjo-daro")}
    # FRESH: Mohenjo-daro DK-G houses labelled by Hemmy's list, minus every unit the
    # assemblage already labelled WEIGHT (their texts are dropped), plus Chanhu-daro.
    hem = hemmy_units()
    md = {}
    dropped = []
    for k, v in units["Mohenjo-daro"].items():
        if not k.startswith("DKG."):
            continue
        if v["w"]:
            dropped.append(k)
            continue
        md[k] = (k in hem, v["stratum"], v["texts"])
    ch = {k: (v["w"], v["stratum"], v["texts"]) for k, v in units["Chanhu-daro"].items()}
    fresh = {"Mohenjo-daro (DK-G, Hemmy)": md, "Chanhu-daro": ch}
    meta = {"hemmy_units": sorted(hem), "hemmy_units_linked": sorted(k for k in md if md[k][0]),
            "dropped_seen_weight_units": sorted(dropped)}
    return {"fresh": fresh, "seen": seen}, meta


def site_arrays(units):
    """Flatten a site's units into per-text arrays."""
    keys = sorted(units)
    n = np.array([len(units[k][2]) for k in keys])
    bins = np.digitize(n, BINS) - 1
    text_unit, texts = [], []
    for j, k in enumerate(keys):
        for t in sorted(units[k][2]):
            text_unit.append(j); texts.append(t)
    w_unit = np.array([units[k][0] for k in keys], dtype=bool)
    strata = [units[k][1] for k in keys]
    return {"keys": keys, "n": n, "bin": bins, "w_unit": w_unit, "strata": strata,
            "text_unit": np.array(text_unit), "texts": texts,
            "text_bin": bins[np.array(text_unit)] if text_unit else np.array([], int),
            "text_w": w_unit[np.array(text_unit)] if text_unit else np.array([], bool)}


def indicator(A, signs):
    return np.array([any(g in signs for g in t) for t in A["texts"]], dtype=np.int64)


# ---------------------------------------------------------------- nulls
def n1_null(A, x, nperm, rng):
    """N1 (primary): shuffle texts among units of the same size bin within the site.
    Each unit keeps its number of texts. Returns null draws of T = texts with the sign in weight units."""
    out = np.zeros(nperm, dtype=np.int64)
    for b in np.unique(A["text_bin"]):
        idx = np.where(A["text_bin"] == b)[0]
        nw = int(A["text_w"][idx].sum())
        if nw == 0 or nw == len(idx):
            out += int(x[idx][A["text_w"][idx]].sum()) if nw else 0
            continue
        xb = x[idx]
        if xb.sum() == 0:
            continue
        # number of sign-texts landing in the nw weight slots = hypergeometric draw
        out += rng.hypergeometric(int(xb.sum()), len(idx) - int(xb.sum()), nw, size=nperm)
    return out


def n2_null(A, x, nperm, rng):
    """N2 (red team): permute WEIGHT labels among units of the same size bin (texts stay in
    their units, so clustering of a sign inside a unit is kept)."""
    c = np.bincount(A["text_unit"], weights=x, minlength=len(A["keys"])).astype(np.int64)
    out = np.zeros(nperm, dtype=np.int64)
    for b in np.unique(A["bin"]):
        idx = np.where(A["bin"] == b)[0]
        nw = int(A["w_unit"][idx].sum())
        if nw == 0:
            continue
        if nw == len(idx):
            out += int(c[idx].sum()); continue
        r = rng.random((nperm, len(idx))).argsort(axis=1)[:, :nw]
        out += c[idx][r].sum(axis=1)
    return out


def n0_null(A, x, nperm, rng):
    """N0 (old assemblage null, for comparison only): permute WEIGHT labels among units within
    the site's mound strata, ignoring unit size."""
    c = np.bincount(A["text_unit"], weights=x, minlength=len(A["keys"])).astype(np.int64)
    st = np.array(A["strata"])
    out = np.zeros(nperm, dtype=np.int64)
    for s in np.unique(st):
        idx = np.where(st == s)[0]
        nw = int(A["w_unit"][idx].sum())
        if nw == 0:
            continue
        r = rng.random((nperm, len(idx))).argsort(axis=1)[:, :nw]
        out += c[idx][r].sum(axis=1)
    return out


def mh_terms(A, x):
    """Mantel-Haenszel rate-ratio terms over size-bin strata: share of texts with the sign
    inside weight units vs outside them."""
    num = den = 0.0
    for b in np.unique(A["text_bin"]):
        idx = A["text_bin"] == b
        w = A["text_w"][idx]; xb = x[idx]
        n1, n0 = int(w.sum()), int((~w).sum())
        N = n1 + n0
        if n1 == 0 or n0 == 0:
            continue
        a, c = int(xb[w].sum()), int(xb[~w].sum())
        num += a * n0 / N; den += c * n1 / N
    return num, den


def rr(num, den):
    if den > 0:
        return round(num / den, 3)
    return float("inf") if num > 0 else None


def combined(D, signs, null_fn, nperm, rng, xs=None):
    """Effect size = Mantel-Haenszel rate ratio (RR) over site x size-bin strata.
    p = permutation p of T (texts with the sign in weight units) under null_fn, summed over sites."""
    obs, nulls, per_site, NUM, DEN = 0, np.zeros(nperm, dtype=np.int64), {}, 0.0, 0.0
    for s, A in D.items():
        x = indicator(A, signs) if xs is None else xs[s]
        o = int(x[A["text_w"]].sum())
        nu = null_fn(A, x, nperm, rng)
        obs += o; nulls += nu
        num, den = mh_terms(A, x); NUM += num; DEN += den
        e = float(nu.mean())
        per_site[s] = {"obs": o, "exp": round(e, 3), "obs_over_exp": round(o / e, 3) if e > 0 else None,
                       "rr_mh": rr(num, den), "p": float((1 + (nu >= o).sum()) / (1 + nperm)),
                       "n_sign_texts": int(x.sum())}
    e = float(nulls.mean())
    return {"obs": obs, "exp": round(e, 3), "obs_over_exp": round(obs / e, 3) if e > 0 else None,
            "ratio": rr(NUM, DEN), "p": float((1 + (nulls >= obs).sum()) / (1 + nperm)), "sites": per_site}


# ---------------------------------------------------------------- gate
def gate(D, counts, rng, reps=GATE_REPS, nperm=GATE_PERM, rr=PLANT_RR):
    """Plant a sign rr times as likely in weight-unit texts, with the given number of texts per
    site (the real candidate's count), and ask how often the decision rule detects it under N1."""
    hits = 0
    for _ in range(reps):
        xs = {}
        for s, A in D.items():
            k = counts.get(s, 0)
            nw, nt = int(A["text_w"].sum()), len(A["texts"])
            if k == 0 or nt == 0:
                xs[s] = np.zeros(nt, dtype=np.int64); continue
            po = k / (nt - nw + rr * nw)
            pi = min(1.0, rr * po)
            p = np.where(A["text_w"], pi, po)
            xs[s] = (rng.random(nt) < p).astype(np.int64)
        r = combined(D, None, n1_null, nperm, rng, xs=xs)
        hits += (r["p"] <= ALPHA and r["ratio"] is not None and r["ratio"] >= RATIO_BAR)
    return hits / reps


# ---------------------------------------------------------------- verdicts
def verdict(n_texts, power, nc_ok, r1, r2, seen):
    if n_texts < MIN_TEXTS:
        return "untestable (too few texts)"
    if power < GATE_POWER:
        return "underpowered"
    if not nc_ok:
        return "inconclusive (negative control failed: null does not remove find density)"
    if r1["p"] <= ALPHA and r1["ratio"] is not None and r1["ratio"] >= RATIO_BAR:
        v = "signal" if r2["p"] <= ALPHA else "fragile signal (fails red-team null N2)"
        return ("exploratory " + v) if seen else ("supported: " + v)
    if r1["ratio"] is not None and r1["ratio"] <= KILL_RATIO:
        return "refuted in this data" + (" (already-seen data, exploratory)" if seen else "")
    return "inconclusive"


def main():
    rng = np.random.default_rng(SEED)
    linked = load_linked()
    sets, meta = build_sets(linked)
    out = {"prereg": "docs/prereg/weight_sign.md", "alpha": ALPHA, "meta": meta, "sets": {}}
    for name in ("fresh", "seen"):
        D = {s: site_arrays(u) for s, u in sets[name].items()}
        D = {s: A for s, A in D.items() if len(A["texts"])}
        desc = {s: {"units": len(A["keys"]), "weight_units": int(A["w_unit"].sum()),
                    "texts": len(A["texts"]), "texts_in_weight_units": int(A["text_w"].sum()),
                    "weight_units_by_size_bin": {int(b): int(A["w_unit"][A["bin"] == b].sum()) for b in np.unique(A["bin"])},
                    "units_by_size_bin": {int(b): int((A["bin"] == b).sum()) for b in np.unique(A["bin"])}}
                for s, A in D.items()}
        res = {"description": desc, "candidates": {}}
        print(f"\n===== data set: {name} =====")
        for s, d in desc.items():
            print(f"  {s}: {d}")
        # gates: at M197's frequency (required) and at each candidate's own frequency
        cnt = {c: {s: int(indicator(A, CANDIDATES[c]["wells"]).sum()) for s, A in D.items()} for c in CANDIDATES}
        reps = 40 if DRY else GATE_REPS
        gates = {f"at_{c}_frequency": {"counts": cnt[c], "power": gate(D, cnt[c], rng, reps=reps)} for c in CANDIDATES}
        # pipeline check (not decisional): same plant at 10% of each site's texts, to show the
        # method finds a planted sign when the data are large enough
        big = {s: max(1, len(A["texts"]) // 10) for s, A in D.items()}
        gates["pipeline_check_10pct_of_texts"] = {"counts": big, "power": gate(D, big, rng, reps=reps)}
        res["gates"] = gates
        print("  gates:", gates)
        if DRY:
            print("  dry run: hemmy units linked:", meta["hemmy_units_linked"], "dropped:", meta["dropped_seen_weight_units"])
            continue
        # negative control: jar + 10 most frequent other signs
        freq = defaultdict(int)
        for A in D.values():
            for t in A["texts"]:
                for g in set(t):
                    freq[g] += 1
        excl = set().union(*(c["wells"] for c in CANDIDATES.values())) | {JAR}
        common = [g for g, _ in sorted(freq.items(), key=lambda kv: -kv[1]) if g not in excl][:10]
        nc = {}
        for g in [JAR] + common:
            r1 = combined(D, {g}, n1_null, NPERM, rng)
            r0 = combined(D, {g}, n0_null, NPERM, rng)
            nc[f"W{g:03d}"] = {"N1": {k: r1[k] for k in ("obs", "exp", "ratio", "p")},
                              "N0_old": {k: r0[k] for k in ("obs", "exp", "ratio", "p")}}
        jar_fail = nc[f"W{JAR:03d}"]["N1"]["p"] <= ALPHA
        n_common_fail = sum(nc[f"W{g:03d}"]["N1"]["p"] <= ALPHA for g in common)
        nc_ok = (not jar_fail) and n_common_fail <= 1
        res["negative_control"] = {"signs": nc, "jar_passes_rule": jar_fail, "common_signs_p_le_alpha": n_common_fail,
                                   "control_ok": nc_ok}
        print("  negative control ok:", nc_ok, "| jar p<=alpha:", jar_fail, "| common with p<=alpha:", n_common_fail)
        for g, v in nc.items():
            print(f"    {g}: N1 {v['N1']}  N0 {v['N0_old']}")
        for c, cd in CANDIDATES.items():
            n_texts = sum(cnt[c].values())
            r1 = combined(D, cd["wells"], n1_null, NPERM, rng)
            r2 = combined(D, cd["wells"], n2_null, NPERM, rng)
            r0 = combined(D, cd["wells"], n0_null, NPERM, rng)
            power = gates[f"at_{c}_frequency"]["power"]
            v = verdict(n_texts, power, nc_ok, r1, r2, seen=(name == "seen"))
            res["candidates"][c] = {"label": cd["label"], "n_texts": n_texts, "N1": r1, "N2_redteam": r2,
                                    "N0_old": r0, "gate_power_own_freq": power,
                                    "gate_power_M197_freq": gates["at_M197_frequency"]["power"], "verdict": v}
            print(f"  {c}: n={n_texts} verdict={v}")
            print(f"    N1 {r1}\n    N2 {r2}\n    N0 {r0}")
        out["sets"][name] = res
    if not DRY:
        json.dump(out, open(HERE / "results.json", "w"), indent=1, default=float)


if __name__ == "__main__":
    main()
