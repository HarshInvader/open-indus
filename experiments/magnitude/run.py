"""R4 magnitude: do numerals on an object track a physical magnitude of that object?

usage: .venv/bin/python experiments/magnitude/run.py
Frozen rules: docs/prereg/magnitude.md. Inputs: extract.csv (hand extraction from reports, with
provenance), ICIT record dimensions for rods. Writes magnitude.csv and results.json.
"""
import csv, json, sys
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr, rankdata

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from corpus.load import icit_texts, m77_texts  # noqa

rng = np.random.default_rng(20261115)
STROKES = json.load(open(ROOT / "sources/shaunmortal_indus/data/stroke_signs.json"))
M_NUM = {f"M{k}": v for k, v in STROKES["short"].items() if k not in ("99", "100", "101")}
M_NUM.update({f"M{k}": v for k, v in STROKES["tall"].items()})
M_ARC = {f"M{k}": v for k, v in STROKES["arc"].items()}  # Mackay's inverted-U 'tens' (exploratory)
W_NUM = {"W001": 1, "W003": 3, "W004": 4, "W005": 5, "W006": 6, "W007": 7, "W013": 3, "W014": 4,
         "W015": 5, "W016": 6, "W017": 7, "W018": 8, "W019": 9, "W055": 12}
W_NUM.update({f"W{30 + k:03d}": k for k in range(1, 8)})  # tall W031-W037 = 1-7

ICIT = {}
for r in icit_texts():
    ICIT.setdefault(r["id"].split(".")[0], []).append(r)
M77 = {}
for t in m77_texts():
    M77.setdefault(str(t["text_no"]), []).append(t)


def v_icit(rid):
    recs = ICIT.get(str(rid), [])
    signs = [s for r in recs for s in r["seq"]]
    return sum(W_NUM.get(s, 0) for s in signs), sum(s in W_NUM for s in signs), " / ".join(" ".join(r["seq"]) for r in recs)


def v_m77(tn):
    recs = M77.get(str(tn), [])
    signs = [s for r in recs for s in r["seq"]]
    v = sum(M_NUM.get(s, 0) for s in signs)
    mack = v + 10 * sum(M_ARC.get(s, 0) for s in signs)
    return v, mack, " / ".join(" ".join(r["seq"]) for r in recs)


def f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------- build table
rows = []
seen_icit = set()
for e in csv.DictReader(open(HERE / "extract.csv")):
    rid = e["icit_ids"]
    seen_icit.add(rid)
    V, ntok, txt = v_icit(rid) if rid else (None, None, "")
    Vm, Vmack, mtxt = v_m77(e["m77_text"]) if e["m77_text"] else ("", "", "")
    rows.append(dict(e, V_icit=V, n_num_tokens=ntok, icit_text=txt, V_m77=Vm, V_mackay_tens=Vmack, m77_seq=mtxt))

# rods: ICIT records of class ROD with a length, ivory/bone, not already hand-entered
for rid, recs in ICIT.items():
    r = recs[0]
    if r["type"] != "ROD" or rid in seen_icit:
        continue
    L = max(f(r["width_mm"]) or 0, f(r["height_mm"]) or 0)
    if L < 20 or r["material"] not in ("Ivory", "Bone"):
        continue
    V, ntok, txt = v_icit(rid)
    complete = all(x["complete"] for x in recs)
    rows.append({"obj_id": f"ICIT-{rid}", "class": "rod", "type": f"rod ({r['material'].lower()})", "site": r["site"],
                 "cisi": r["cisi"], "icit_ids": rid, "m77_text": "", "exc_no": "",
                 "source": "ICIT width/height (Wells, from reports)", "locator": f"ICIT record {rid}", "mass_g": "",
                 "length_mm": L, "width_mm": min(f(r['width_mm']) or 0, f(r['height_mm']) or 0) or "",
                 "length_complete": "unknown", "link_grade": "B",
                 "link_basis": "ICIT record carries both text and dimensions",
                 "note": "" if complete else "inscription broken", "V_icit": V, "n_num_tokens": ntok,
                 "icit_text": txt, "V_m77": "", "V_mackay_tens": "", "m77_seq": ""})

cols = list(rows[0].keys())
with open(HERE / "magnitude.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=cols)
    w.writeheader()
    w.writerows(rows)


# ---------------------------------------------------------------- tests
def within_rank(x, strata):
    x = np.asarray(x, float); out = np.empty_like(x)
    for s in set(strata):
        idx = [i for i, t in enumerate(strata) if t == s]
        out[idx] = (rankdata(x[idx]) - 0.5) / len(idx) if len(idx) > 1 else 0.5
    return out


def fe_spearman(V, M, types, sites, nperm=10000):
    """Spearman on within-type ranks (type fixed effect); V permuted within type x site."""
    V = np.asarray(V, float); M = np.asarray(M, float)
    rM = within_rank(M, types)

    def stat(v):
        rv = within_rank(v, types)
        return spearmanr(rv, rM)[0] if np.std(rv) > 0 else 0.0
    obs = stat(V)
    cells = {}
    for i, (t, s) in enumerate(zip(types, sites)):
        cells.setdefault((t, s), []).append(i)
    null = []
    for _ in range(nperm):
        v = V.copy()
        for idx in cells.values():
            v[idx] = rng.permutation(V[idx])
        null.append(stat(v))
    null = np.nan_to_num(np.array(null))
    p = (np.sum(np.abs(null) >= abs(obs) - 1e-12) + 1) / (nperm + 1)
    return float(obs), float(p)


def power(V, types, sites, rho=0.5, alpha=0.0125, nsim=300, nperm=500):
    """P(p<=alpha) when the magnitude is planted with correlation ~rho to rank(V)."""
    V = np.asarray(V, float); hits = 0
    z = rankdata(V); z = (z - z.mean()) / (z.std() + 1e-9)
    for _ in range(nsim):
        M = rho * z + np.sqrt(1 - rho ** 2) * rng.standard_normal(len(V))
        _, p = fe_spearman(V, M, types, sites, nperm=nperm)
        hits += p <= alpha
    return hits / nsim


res = {"prereg": "docs/prereg/magnitude.md", "n_rows": len(rows), "tests": {}}

impl = [r for r in rows if r["class"] == "implement"]
mass = [r for r in impl if f(r["mass_g"]) and r["link_grade"] in "AB"]
res["tests"]["T1_mass"] = {"n": len(mass), "verdict": "UNTESTABLE (n<8)",
                           "pairs": [(r["obj_id"], f(r["mass_g"]), r["V_icit"], r["V_mackay_tens"]) for r in mass]}
lenr = [r for r in impl if f(r["length_mm"]) and r["link_grade"] in "AB"]
res["tests"]["T1_length_secondary"] = {
    "n": len(lenr), "n_complete": sum(r["length_complete"] in ("yes", "restored") for r in lenr),
    "verdict": "UNTESTABLE (n<8 complete; types mostly singletons)",
    "pairs": [(r["obj_id"], r["type"], f(r["length_mm"]), r["V_icit"], r["V_mackay_tens"], r["length_complete"]) for r in lenr]}
if len(lenr) >= 4:
    rho, p = spearmanr([r["V_icit"] for r in lenr], [f(r["length_mm"]) for r in lenr])
    res["tests"]["T1_length_secondary"]["exploratory_pooled_spearman_not_a_test"] = {"rho": round(float(rho), 3), "p_two_sided": round(float(p), 3)}

res["tests"]["T2_pottery_capacity"] = {"n": 0, "verdict": "UNTESTABLE: no per-vessel capacity for any inscribed vessel in Marshall 1931, Mackay 1938, Vats 1940 or Mackay 1943; inscribed pottery is mostly sherds"}
res["tests"]["T3_bangle_diameter"] = {"n": 0, "verdict": "UNTESTABLE: Mackay 1938 p.536 gives only the class range (inside 2.08-2.50 in = 53-64 mm) for stoneware bangles; no per-object diameter for any inscribed bangle; Marshall 1931 p.531 none; harappa.com (Kenoyer) blocked"}
res["tests"]["T3o_oval_bangle"] = {"n": 0, "verdict": "UNTESTABLE (same reason)"}

rods = [r for r in rows if r["class"] == "rod" and f(r["length_mm"])]
V = [r["V_icit"] for r in rods]; M = [f(r["length_mm"]) for r in rods]
types = ["rod"] * len(rods)  # prereg T4: stratum = class (amendment A1)
sites = [r["site"] for r in rods]
t4 = {"n": len(rods), "n_V_positive": sum(v > 0 for v in V),
      "n_text_complete": sum("broken" not in r["note"] for r in rods),
      "sites": {s: sites.count(s) for s in set(sites)},
      "pairs": [(r["obj_id"], r["cisi"], r["site"], r["type"], f(r["length_mm"]), r["V_icit"], r["icit_text"]) for r in rods]}
if len(rods) >= 8:
    rho, p = fe_spearman(V, M, types, sites)
    t4.update(rho_fe=round(rho, 3), p=round(p, 4), power_rho05=power(V, types, sites))
    md = [i for i, s in enumerate(sites) if s == "Mohenjo-daro"]
    rho_md, p_md = fe_spearman([V[i] for i in md], [M[i] for i in md], [types[i] for i in md], [sites[i] for i in md])
    t4.update(rho_md_only=round(rho_md, 3), p_md_only=round(p_md, 4))
    t4["verdict"] = ("PASS stage 1 (needs 2nd site)" if p <= 0.0125 else
                     ("REFUTED" if len(rods) >= 15 and t4["power_rho05"] >= 0.8 else "INCONCLUSIVE (underpowered)"))
else:
    t4["verdict"] = "UNTESTABLE (n<8)"
res["tests"]["T4_rod_length"] = t4

by_text = {}
for r in rods:
    by_text.setdefault(r["icit_text"], []).append(f(r["length_mm"]))
res["exploratory_same_text_rods"] = {k: v for k, v in by_text.items() if len(v) > 1}

json.dump(res, open(HERE / "results.json", "w"), indent=1, default=str)
print(json.dumps(res, indent=1, default=str))
