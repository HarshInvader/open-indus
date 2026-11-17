"""Pre-outcome coverage for reg_size: replication-set size, register vs ICIT measurement agreement,
M77-vs-ICIT class agreement, and power of the frozen criteria (from T4 data only).
No class-vs-area outcome on the new objects is computed here.
Run: .venv/bin/python experiments/reg_size/coverage.py  -> coverage.json"""
import json, math, sys
from collections import Counter
import numpy as np
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import rs_lib as L
from rs_lib import PRIMARY_T4, CLASSES, HERE, IN2MM

OUT = {}
t4 = L.t4_objects()
T4R, T4IDS = t4
OUT["t4_texts"] = len(T4R); OUT["t4_objects"] = len(T4IDS)

for name, src in [("primary_FEM_EH", set(L.PRIMARY_SOURCES)), ("MIC", {"Marshall1931_MIC"}),
                  ("CE", {"Mackay1943_CE"})]:
    rows, audit = L.build_new_set(src, t4=t4)
    OUT[f"set_{name}"] = dict(audit=audit, by_site=dict(Counter(r["site"] for r in rows)),
                              n_obj=sum(r["n_obj"] for r in rows),
                              length_mean=float(np.mean([r["length"] for r in rows])) if rows else None,
                              area_mm2_median=float(np.median([math.exp(r["log_area"]) for r in rows])) if rows else None)
rows_e1, a_e1 = L.build_new_set(set(L.PRIMARY_SOURCES), t4=t4, exclude="edit1")
OUT["set_primary_edit1"] = dict(n=len(rows_e1))
rows_an, _ = L.build_new_set(set(L.PRIMARY_SOURCES), t4=t4, require_animal=True)
OUT["set_primary_animal_only"] = dict(n=len(rows_an))

# ---------- measurement agreement: register vs ICIT dims for the same object ----------
icit = L.icit_by_id()
agree = {}
for src in ["Mackay1938_FEM", "Vats1940_EH", "Marshall1931_MIC"]:
    d_side, d_logA, pairs = [], [], []
    for r in L.load_registers():
        if r["source"] != src:
            continue
        ok, _ = L.is_square_row(r)
        dims = L.parse_icit_dims(r["icit_dims_mm"])
        if not ok or not dims:
            continue
        ids = [i for i in r["icit_ids"].split(";") if i]
        if len(ids) != 1:
            continue
        reg = sorted([L.fnum(r["l_in"]) * IN2MM, L.fnum(r["w_in"]) * IN2MM])
        ic = sorted(dims)
        d_side += [reg[0] - ic[0], reg[1] - ic[1]]
        d_logA.append(math.log(reg[0] * reg[1]) - math.log(ic[0] * ic[1]))
        pairs.append((math.log(reg[0] * reg[1]), math.log(ic[0] * ic[1]), ids[0] in T4IDS))
    if not pairs:
        continue
    ds, dl = np.array(d_side), np.array(d_logA)
    P = np.array(pairs)
    agree[src] = dict(
        n_objects=len(pairs), n_in_T4=int(P[:, 2].sum()),
        side_diff_mm_median=float(np.median(ds)), side_absdiff_mm_median=float(np.median(np.abs(ds))),
        side_within_0_3mm=float(np.mean(np.abs(ds) <= 0.3)), side_within_1_5mm=float(np.mean(np.abs(ds) <= 1.5)),
        logarea_diff_sd=float(dl.std()), logarea_diff_mad=float(np.median(np.abs(dl))),
        logarea_r=float(np.corrcoef(P[:, 0], P[:, 1])[0, 1]),
        logarea_sd_between_objects=float(P[:, 1].std()),
        reliability=float(1 - dl.var() / 2 / P[:, 1].var()))  # share of area variance that is not error (each source carries half)
OUT["measurement_agreement"] = agree

# ---------- text agreement: class counts from M77 (bridge map) vs ICIT (frozen Wells) ----------
m77 = L.m77_seal_index()
same, tot, per = 0, 0, Counter()
for r in L.load_registers():
    ids = [i for i in (r["icit_ids"] or "").split(";") if i]
    if len(ids) != 1 or not r["m77_text_no"] or r["source"] not in L.PRIMARY_SOURCES:
        continue
    t = m77.get(int(r["m77_text_no"])); it = icit.get(ids[0])
    if t is None or it is None or not t["complete"] or "#" in t["seq"] or "#" in it["seq"]:
        continue
    cm = L.classes_of_m(L.signs(t["seq"]))
    cw = L.sas_lib.classes_of(L.sas_lib.nsigns(it["seq"]))
    tot += 1
    same += all(cm[c] == cw[c] for c in PRIMARY_T4)
    for c in PRIMARY_T4:
        per[c] += cm[c] == cw[c]
OUT["class_agreement_m77_vs_icit"] = dict(n=tot, all_classes_equal=same / max(tot, 1),
                                          per_class={c: per[c] / max(tot, 1) for c in PRIMARY_T4})

# ---------- power of the frozen criteria, from T4 data only ----------
# Draw n_new texts from T4 (without replacement, keep strata with >=2), compute the 8 share slopes
# and compare to the slopes of the REMAINING T4 texts (not the full set: avoids shared data).
sys.path.insert(0, str(L.ROOT / "experiments/space_and_sealing"))
from scipy.stats import spearmanr


def slopes(rows):
    from collections import defaultdict
    g = defaultdict(list)
    for i, r in enumerate(rows):
        g[r["stratum"]].append(i)
    x = np.array([r["log_area"] for r in rows], float)
    for idx in g.values():
        x[idx] -= x[idx].mean()
    Y = np.array([[r["cls"][k] / r["length"] for k in PRIMARY_T4] for r in rows])
    Y = Y - Y.mean(0)
    return x @ Y / (x ** 2).sum() * math.log(2)


def keep_multi(rows):
    c = Counter(r["stratum"] for r in rows)
    return [r for r in rows if c[r["stratum"]] >= 2]


n_new = OUT["set_primary_FEM_EH"]["audit"]["distinct texts"]
rng = np.random.default_rng(1)
ci = [PRIMARY_T4.index(k) for k in ("connective", "other_closer", "post_closer")]
want = np.array([1, -1, -1])
res = []
for _ in range(1000):
    idx = rng.permutation(len(T4R))
    A = keep_multi([T4R[i] for i in idx[:n_new]]); B = [T4R[i] for i in idx[n_new:]]
    sa, sb = slopes(A), slopes(B)
    signs_ok = bool(np.all(np.sign(sa[ci]) == want))
    rho = float(spearmanr(sa, sb).correlation)
    res.append((signs_ok, rho >= 0.5, signs_ok and rho >= 0.5))
res = np.array(res)
OUT["power_if_T4_effect_true"] = dict(n_new=n_new, method="subsample n_new T4 texts vs remaining T4 texts, 1000 draws",
                                      p_signs_all_three=float(res[:, 0].mean()), p_rho_ge_0_5=float(res[:, 1].mean()),
                                      p_both=float(res[:, 2].mean()))
json.dump(OUT, open(HERE / "coverage.json", "w"), indent=1)
print(json.dumps(OUT, indent=1))
