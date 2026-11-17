"""Assemble results.json from the run outputs; Wells-bridge cross-check of the frozen decomposition."""
import csv, json
from pathlib import Path
H = Path(__file__).resolve().parent
R = H.parents[1]
dev = json.load(open(H / "dev_calibrated.json"))
dsf = json.load(open(H / "dev_results.json"))
conf = json.load(open(H / "confirm_results.json"))
new = json.load(open(H / "confirm_newsites_fixed.json"))
pw = json.load(open(H / "power_partners.json"))

b = json.load(open(R / "sources/shaunmortal_indus/data/bridge_WM.json"))
m2w = {}
for w, v in b.items():
    for m in v["M"]:
        m2w.setdefault(f"M{m}", set()).add(w)
rows = list(csv.DictReader(open(H / "decomp_frozen.csv")))
both = [r for r in rows if r["sign"] in m2w and r["base"] in m2w]
merged = [f"{r['sign']}/{r['base']}" for r in both if m2w[r["sign"]] & m2w[r["base"]]]

def prim(s):
    return {m: {k: v for k, v in x.items()} for m, x in s["primary"].items()}

out = {
    "area": "modifiers", "date": "2026-11-15",
    "decomposition": {"pairs": len(rows), "modifier_classes": len({r["modifier"] for r in rows}),
                      "sha256_frozen": "b0c849648852e8d1b40df0b5bf901f1d73ec2d2373c34260522bb9325877291e",
                      "wells_crosscheck": {"pairs_with_both_signs_bridged": len(both), "merged_by_wells": merged}},
    "dev": {"n_texts": dsf["n_texts_dev"], "n_tests_bh": dev["n_tests"],
            "bh_q<0.1": [x for x in dev["bh"] if x["q"] < 0.1],
            "TICKS4_final": {k: dev["families"]["TICKS4"]["final"][k] for k in ("z", "T", "up", "down", "p_two")},
            "TICKS4_nonfish_final": {k: dev["families"]["TICKS4_nonfish"]["final"][k] for k in ("z", "T", "up", "down", "p_two")},
            "negative_control_calibrated": dev["negative_control_calibrated"],
            "negative_control_signflip": dsf["negative_control"],
            "signflip_TICKS4": {"final_p": next(f for f in dsf["families"] if f["modifier"] == "TICKS4")["p"]}},
    "confirm": {"heldout_v2": {"n_texts": conf["heldout_v2"]["n_texts"], "primary": prim(conf["heldout_v2"]),
                               "paradigm_min_p": min(conf["heldout_v2"]["paradigm_family"], key=lambda x: x["p_two"]),
                               "paradigm_n_tests": len(conf["heldout_v2"]["paradigm_family"])},
                "icit_all": {"n_texts": conf["icit_all"]["n_texts"], "primary": prim(conf["icit_all"]),
                             "paradigm_min_p": min(conf["icit_all"]["paradigm_family"], key=lambda x: x["p_two"]),
                             "paradigm_n_tests": len(conf["icit_all"]["paradigm_family"])},
                "icit_newsites_fixed": {"n_texts": None, "primary": prim(new)},
                "icit_newsites_as_hashed_buggy": {"n_texts": conf["icit_newsites"]["n_texts"], "primary": prim(conf["icit_newsites"]),
                                                  "note": "site filter bug: kept Mohenjo-daro/Chanhu-daro; effectively ICIT minus Harappa, Kalibangan, Lothal"}},
    "power_T_final": {s: {m: {"k": v["k"], "+0.2": v["T_power_+0.2"], "+0.5": v["T_power_+0.5"]} for m, v in d.items()} for s, d in pw.items()},
    "partner_shift": {s: {m: {"k": v.get("partner_k"), "cos": v.get("partner_cos"), "p": v.get("partner_p")} for m, v in d.items() if "partner_p" in v} for s, d in pw.items()},
    "verdict": "Ticks are the only graphic modifier with a confirmed slot effect (closing slot). No paradigm: 0 of the other modifier classes passes correction in dev, held-out or ICIT. Inserted strokes in a jar/cup lower final share (held-out confirmed; known jar effect). Ticks on non-fish bases: dev and ICIT yes, held-out no (inconclusive). ROOF -> more initial is an unconfirmed lead (held-out p=0.006, ICIT p=0.04, not pre-registered as primary).",
}
json.dump(out, open(H / "results.json", "w"), indent=1, default=float)
print(json.dumps(out["decomposition"], indent=1)); print(out["confirm"]["heldout_v2"]["paradigm_min_p"], out["confirm"]["icit_all"]["paradigm_min_p"])
