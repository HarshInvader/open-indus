"""Step 0 (allowed before the pre-registration): dimension and metadata coverage only.
No outcome (sign class vs size, seal vs sealing profile) is computed here."""
import json, sys
from collections import Counter
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from sas_lib import icit_texts, is_steatite, num, signs, t4_table, t6_table, HERE

T = icit_texts()
sq = [t for t in T if t["type"] == "SEAL:S"]
st = [t for t in sq if is_steatite(t["material"])]
dim = [t for t in st if num(t["width_mm"]) * num(t["height_mm"]) > 20]
txt = [t for t in dim if signs(t["seq"])]
comp = [t for t in txt if t["complete"] and "#" not in t["seq"]]
per = [t for t in txt if (t["period"], t["phase"]) != ("-", "-")]
out = dict(
    square_seal_objects=len(sq), steatite=len(st), material_unknown=sum(1 for t in sq if t["material"] == "-"),
    steatite_with_dims=len(dim), share_with_dims=round(len(dim) / len(st), 3),
    with_text=len(txt), complete_text=len(comp), with_period_or_phase=len(per),
    share_period=round(len(per) / len(txt), 3),
    by_site={s: dict(steatite=sum(1 for t in st if t["site"] == s), dims=sum(1 for t in dim if t["site"] == s),
                     period=sum(1 for t in per if t["site"] == s))
             for s, _ in Counter(t["site"] for t in st).most_common(12)},
)
R = t4_table(require_complete=True)
Rall = t4_table(require_complete=False)
out["t4_distinct_texts_complete"] = len(R)
out["t4_distinct_texts_all"] = len(Rall)
out["t4_strata"] = len({r["stratum"] for r in R})
out["t4_strata_with_2plus"] = sum(1 for s, n in Counter(r["stratum"] for r in R).items() if n >= 2)
out["t4_texts_in_2plus_strata"] = sum(n for s, n in Counter(r["stratum"] for r in R).items() if n >= 2)
out["t4_by_site"] = dict(Counter(r["site"] for r in R).most_common())
out["t4_catalogue_vs_metric"] = dict(Counter("catalogue" if r["catalogue"] else "metric" for r in R))
out["t4_half"] = dict(Counter(r["half"] for r in R))
out["t4_length_dist"] = dict(sorted(Counter(min(r["length"], 8) for r in R).items()))
# T6 sample sizes
for lab, rc in [("complete", True), ("all", False)]:
    R6 = t6_table(require_complete=rc)
    c = Counter((r["site"], r["oc"]) for r in R6)
    sites = sorted({s for s, o in c if o == "sealing"}, key=lambda s: -c[(s, "sealing")])
    out[f"t6_{lab}"] = {s: dict(sealing=c[(s, "sealing")], seal=c[(s, "seal")]) for s in sites}
json.dump(out, open(HERE / "coverage.json", "w"), indent=1)
print(json.dumps(out, indent=1))
