"""Confirmatory held-out tests, exactly as pre-registered in
docs/prereg/2026-11-14_internal_phonetics.md. Writes results.json[heldout]."""
import sys
from collections import Counter

from scipy.stats import poisson

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from common import bh, glyph_sim, load_split, save_results
from run_indus_dev import FAM, excluded, transparency
from tests import t1_local, t2_transitivity, t3_events, t3_ligatures, t4_drops

D, H = load_split()
print("held-out distinct clean texts:", len(H))
out = {}

# H1
items = []
for o in ("prev", "next"):
    r = t1_local(H, excluded, o, nperm=20000, wide=1, minev=4)
    for it in r["items"]:
        it["orient"] = o; items.append(it)
q = bh([i["p"] for i in items])
passed = []
for it, qq in zip(items, q):
    it["q"] = float(qq)
    if qq < 0.05:
        tr, a, b = transparency(H, it["sign"], it["top_hosts"][0][0], it["orient"])
        it["transparency"] = tr; it["host_with_x"] = a; it["host_total"] = b
        if tr is not None and tr >= 0.40:
            passed.append(it)
dev_pass = {("M242", "M342", "prev")}
overlap = [p for p in passed if (p["sign"], p["top_hosts"][0][0], p["orient"]) in dev_pass]
out["H1"] = {"n_tested": len(items), "sig": [i for i in items if i["q"] < 0.05], "passed": passed,
             "n_pass_signs": len({p["sign"] for p in passed}), "overlap_with_dev": overlap,
             "supported": len({p["sign"] for p in passed}) >= 3 and len(overlap) >= 1}
print("H1 tested %d, sig %d, passed %d, overlap %d -> supported=%s" % (
    len(items), len(out["H1"]["sig"]), len(passed), len(overlap), out["H1"]["supported"]))
for i in out["H1"]["sig"]:
    print("   ", i["orient"], i["sign"], i["n"], "q=%.3g" % i["q"], i["top_hosts"], "transp", i.get("transparency"))

# H2
r = t2_transitivity(H, nnull=1000, kmin=1)
h2 = {}
for k in ("M65|M72", "M402|M99"):
    v = r["pairs"].get(k, {"k": 0, "p": 1.0})
    h2[k] = {"k_ho": v["k"], "p": v["p"], "p_emp": v.get("p_emp"), "lam": v.get("lam"),
             "replicates": v["k"] >= 1 and v["p"] < 0.025}
cases = {}
for grp in (["M59", "M65", "M67", "M70", "M72"], ["M267", "M391", "M293"]):
    for i, a in enumerate(grp):
        for b in grp[i + 1:]:
            k = "%s|%s" % tuple(sorted([a, b]))
            v = r["pairs"].get(k, {"k": 0})
            cases[k] = {"k_ho": v["k"], "p": v.get("p"), "glyph_sim": glyph_sim(a, b)}
ho_sig = {k: v for k, v in r["pairs"].items() if v["q"] < 0.05}
out["H2"] = {"pairs": h2, "cases": cases, "n_frames": r["n_frames"], "heldout_exploratory_sig": ho_sig}
print("H2 frames", r["n_frames"], h2)
for k, v in cases.items():
    print("   case", k, v)
print("   held-out exploratory q<0.05:", ho_sig)

# H3
r3 = t3_ligatures(H, minfam=1)
m12 = [i for i in r3["items"] if (i["A"], i["B"], i["C"]) == ("M12", "M342", "M176")]
ev = t3_events(H)
zero = {}
for A, parts in {"M343": [("M342", "M97"), ("M342", "M98"), ("M97", "M342"), ("M98", "M342")],
                 "M344": [("M342", "M99"), ("M99", "M342"), ("M342", "M87"), ("M87", "M342")],
                 "M345": [("M342", "M102"), ("M102", "M342"), ("M342", "M89"), ("M89", "M342")],
                 "M348": [("M347", "M176"), ("M176", "M347"), ("M347", "M342"), ("M342", "M176")],
                 "M190": [("M162", "M186"), ("M186", "M162"), ("M162", "M185")]}.items():
    zero[A] = sum(1 for e in ev if e[0] == A and e[1] in parts)
out["H3"] = {"M12_M342_M176": m12, "replicates": bool(m12) and m12[0]["p"] < 0.05, "compositional_events": zero,
             "n_events": len(ev), "top10": r3["items"][:10],
             "M103_M403_replaced_by": Counter(e[0] for e in ev if e[1] == ("M103", "M403")).most_common()}
print("H3 events", len(ev), "M12<->M342 M176:", m12, "compositional events:", zero)
print("   top:", [(i["A"], i["B"], i["C"], i["k"], round(i["p"], 4)) for i in r3["items"][:10]])

# H4
h4 = {}
for cls, pairs in FAM.items():
    rr = t4_drops(H, pairs)
    o = sum(x["obs"] for x in rr); e = sum(x["exp"] for x in rr)
    h4[cls] = {"obs": o, "exp": e, "n_mod_subs": sum(x["n_mod_subs"] for x in rr),
               "p_more": float(poisson.sf(o - 1, e)) if e > 0 else None,
               "p_never": float(poisson.pmf(0, e)) if o == 0 else None,
               "pairs_with_swaps": [x for x in rr if x["obs"]]}
    print("H4 %-22s obs %d exp %.2f mod-subs %d p_more %s p_never %s" % (
        cls, o, e, h4[cls]["n_mod_subs"], h4[cls]["p_more"], h4[cls]["p_never"]))
out["H4"] = h4
save_results("heldout", out)
