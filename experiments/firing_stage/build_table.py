"""Build vessel_marks.csv: every inscribed vessel in ICIT plus vessels from published
sources that record the firing stage. No sign statistics are computed here.

Run: .venv/bin/python -I experiments/firing_stage/build_table.py
"""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from corpus.load import icit_texts  # noqa: E402

RAW_ICIT = ROOT / "sources/field-cady_indus_valley_script_corpus/inscriptions.csv"

# ---------------------------------------------------------------- source citations
KEN21 = ("Kenoyer, J.M. 2021 [2022]. Painted Indus script on ceramics and steatite. "
         "Ancient Pakistan 32: 1-15, Table 1, Figs 3 and 6 (raw/kenoyer_painted/k.pdf)")
KM10 = ("Kenoyer & Meadow 2010, Inscribed objects from Harappa excavations 1986-2007, CISI 3.1: "
        "stamped script on vessels was impressed before firing, almost exclusively on Period 3C pointed-base goblets")
CISI1 = "Joshi & Parpola 1987, CISI 1, p. xxvi: seal impressions on pots made by the potter on wet clay before firing (M-420 to 424)"
VATS = "Vats 1940, Excavations at Harappa: 286-287 (only pointed-base goblets are stamped at Harappa)"
MACK43 = "Mackay 1943, Chanhu-daro Excavations 1935-36: 70 (pot-marks Nos 3, 5)"
MACK38 = "Mackay 1938, Further Excavations at Mohenjo-daro: 183-184"

# ICIT type code -> (technique, firing stage, basis)
TYPE_RULE = {
    "POT:T:p": ("painted", "pre", "painted script is applied before firing (Kenoyer 2021); ICIT 'p' rows = Kenoyer's painted list (K-120, H-1007, G-8, G-10, Sktd-3..6 all cited by him as painted)"),
    "POT:T:s": ("stamped", "pre", "seal impression on vessel; " + KM10 + "; " + CISI1),
    "POT:T:S": ("stamped", "pre", "seal impression on vessel; " + KM10),
    "POT:M": ("moulded", "pre", "moulded script made in the vessel mould (Kenoyer 2021: 11; Dales & Kenoyer 1986: 570)"),
    "POT:T:g": ("incised", "unknown", "ICIT 'graffito'; CISI defines graffiti as incised before OR after firing (CISI 1: xxx); stage not recorded per object"),
    "POsT:T:g": ("incised", "unknown", "ICIT 'graffito' (typo in type code); stage not recorded"),
    "POT:D": ("unknown", "unknown", "ICIT POT:D, undefined code"),
}

# Kenoyer 2021 Fig. 3: Harappa post-firing inscribed pottery, matched to ICIT by HARP number.
# (HARP no. in Kenoyer, ICIT id, vessel form, note)
POST_K21 = {
    "541.1": ("H93/4043-503", "black-slipped jar", "post-firing graffiti on body (Fig 3.7)"),
    "542.1": ("H93/4159-500", "black-slipped jar", "post-firing graffiti on body (Fig 3.6)"),
    "543.1": ("H93/4304-500", "black-slipped jar", "post-firing graffiti on body (Fig 3.8)"),
}
# Kenoyer Fig 3.2 (H95-2662/6640-501) = ICIT 728.1/728.2: post-firing graffiti on rim and body
# AND pre-firing potter's marks on base and body; ICIT does not say which side is which -> mixed.
MIXED = {"728.1": "H95-2662/6640-501 black-slipped jar: post-firing graffiti + pre-firing potter's marks; side not identified (Kenoyer 2021 Fig 3.2)",
         "728.2": "same vessel as 728.1"}
# ICIT 4132.1 has field no. 4305439 which may be Kenoyer's H93/4305-500 (Fig 3.5) - not certain.
POSSIBLE_POST = {"4132.1": "field no. 4305439 may be Kenoyer 2021 Fig 3.5 (H93/4305-500, post-firing); match uncertain"}

# Kenoyer 2021 Table 1 painted vessels. Wells numbers as he gives them (sign1 first = first read).
# key: Kenoyer fig no -> dict(site, form, location, ICIT id if the same object is in ICIT, wells list, note)
K21 = [
    # fig, site, form, location, icit_match, wells, note
    ("6.1", "Balakot", "bangle", "interior", None, ["W550", "W750"], "terracotta bangle (Blk-6), not a vessel: EXCLUDED from vessel analyses"),
    ("6.2", "Karanpura", "bowl", "interior base", None, ["W540"], "KRP 806, Prabhakar & Majid 2014 fig 35"),
    ("6.3", "Surkotada", "dish", "interior", "3879.1", None, "Kenoyer: Sktd-3/4 are dishes with W741; ICIT gives W741 under Sktd-5/6 -> CISI numbers swapped between sources; form follows Kenoyer's sign-form pairing"),
    ("6.4", "Surkotada", "dish", "interior", "3880.1", None, "see 6.3"),
    ("6.5", "Harappa", "dish", "interior", "1159.1", None, "H-1007"),
    ("6.6", "Shikarpur", "dish", "interior", "5541.1", None, "Bhan pers. comm."),
    ("6.7", "Balakot", "dish", "interior", "5542.1", None, "unpublished"),
    ("6.8", "Kalibangan", "small jar", "exterior (inverted)", "1964.1", None, "K-120"),
    ("6.9", "Harappa", "globular jar", "exterior", None, ["W645"], "sign uncertain ('?')"),
    ("6.10", "Dholavira", "globular jar", "exterior", "5543.1", None, "Bisht 2015 fig 8.10"),
    ("6.11", "Dholavira", "globular jar", "exterior", None, ["#", "W700"], "Bisht 2015 fig 8.10; sign 2 uncertain"),
    ("6.12", "Ras al-Hadd HD1", "small jar", "exterior", None, ["W515", "W861"], "Oman, Umm an-Nar context; W861 uncertain"),
    ("6.13", "Karanpura", "globular jar", "exterior", "5544.1", None, "KRP 815; Kenoyer: painted sign matches no known Indus sign; also has post-firing graffito"),
    ("6.14", "Mohenjo-daro", "globular jar", "exterior", "5545.1", None, "M-2077; questionable as script"),
    ("6.15", "Gumla", "globular jar", "exterior", "159.1", None, "G-8; pottery looks Kot Dijian (possibly Early Harappan)"),
    ("6.16", "Gumla", "globular jar", "exterior", "5546.1", None, "G-10; possibly Early Harappan"),
    ("6.17", "Surkotada", "globular jar", "exterior", "3877.1", None, "Sktd; red paint"),
    ("6.18", "Surkotada", "globular jar", "exterior", "3878.1", None, "Sktd"),
    ("6.19", "Mohenjo-daro", "globular jar", "exterior", "5547.1", None, "Dales & Kenoyer 1986 fig 90.6; Kenoyer W867?, ICIT W861"),
    ("6.20", "Harappa", "globular jar", "exterior", None, ["W550", "W220"], "W220 uncertain"),
    ("6.21", "Daimabad", "globular jar", "exterior", None, ["W066"], "Dmd-9; date unknown; sign uncertain"),
    ("6.22", "Bagasra", "globular jar", "exterior", None, ["W742"], "Ajithprasad pers. comm."),
    ("6.23", "Bagasra", "globular jar", "exterior", None, [], "sign unidentified"),
    ("6.24", "Shikarpur", "globular jar", "exterior", "5549.1", None, "Ajithprasad pers. comm."),
    ("6.25", "Shikarpur", "globular jar", "exterior", None, ["W820"], "second W820 jar; only one is in ICIT"),
    ("6.26", "Shikarpur", "globular jar", "exterior", "5550.1", None, ""),
]
# ICIT painted rows that Kenoyer does not list (kept, form unknown):
#   1202.1 Kanmer (Period IIa), 5271.1 Chanhu-daro C-91, 5548.1 Harappa ]000-530[ (possibly = Kenoyer 6.9 or 6.20).
POSSIBLE_DUP = {"5548.1": "may be the same sherd as Kenoyer 6.9 or 6.20 (Harappa); dropped in sensitivity run"}

# Other literature vessels with an explicit firing statement but no sign transcription usable here
LIT_OTHER = [
    dict(vid="LIT-Mackay43-3", site="Chanhu-daro", source="Mackay 1943", technique="impressed", firing="pre",
         basis="'impressed upon it when the clay was damp'", form="jar-stand", text_wells="", note="3 devices, two familiar from MD seals; not transcribed - LOOKUP", citation=MACK43),
    dict(vid="LIT-Mackay43-5", site="Chanhu-daro", source="Mackay 1943", technique="incised", firing="post",
         basis="'scratched after it had been fired'", form="large jar (side)", text_wells="", note="V-shaped device + 12 upright strokes + oval; may be ICIT Chanhu-daro graffito - LOOKUP (Pl. XXXIX)", citation=MACK43),
    dict(vid="LIT-Mackay38-DK6986", site="Mohenjo-daro", source="Mackay 1938", technique="incised", firing="post",
         basis="'scratched on the opposite side of a sherd' of a slipped flat dish (scratching on a finished sherd)", form="flat dish", text_wells="", note="five strokes + Smith & Gadd sign xi/lxxxviii; plus a boat drawing; stage inferred, not stated", citation=MACK38),
    dict(vid="LIT-Vats-post", site="Harappa", source="Vats 1940", technique="incised", firing="post",
         basis="'engraved by cutting through the red or black slip of the finished wares'", form="various", text_wells="",
         note="Vats pottery Nos. 1, 3, 10, 12, 26, 28, 48, 62, 84, 86 'etc.' are post-firing; Vats-number -> CISI/ICIT concordance needed - LOOKUP", citation=VATS),
]


def main():
    raw = {r["id"]: r for r in csv.DictReader(open(RAW_ICIT, encoding="utf-8"))}
    icit = {r["id"]: r for r in icit_texts()}
    rows = []
    k21_by_icit = {k[4]: k for k in K21 if k[4]}
    for iid, r in icit.items():
        if not r["type"].upper().startswith("PO"):
            continue
        rr = raw[iid]
        tech, stage, basis = TYPE_RULE[r["type"]]
        form, conf, note, src = "", "class", "", "ICIT"
        if r["type"] in ("POT:T:s", "POT:T:S") and r["site"] == "Harappa":
            form = "pointed-base goblet (by source statement for Harappa stamped vessels)"
        if iid in POST_K21:
            hn, form, n = POST_K21[iid]
            stage, conf, basis, note = "post", "object", "Kenoyer 2021 Fig 3: " + n, hn
            src = "ICIT+Kenoyer2021"
        if iid in MIXED:
            stage, conf, basis, form = "mixed", "object", MIXED[iid], "black-slipped jar"
        if iid in POSSIBLE_POST:
            note = POSSIBLE_POST[iid]
        if iid in k21_by_icit:
            k = k21_by_icit[iid]
            form, conf, src = k[2], "object", "ICIT+Kenoyer2021"
            note = f"Kenoyer 2021 fig {k[0]}; location {k[3]}; {k[6]}"
        if iid in POSSIBLE_DUP:
            note = (note + "; " if note else "") + POSSIBLE_DUP[iid]
        seq = [s for s in r["seq"]]
        rows.append(dict(
            vid="ICIT-" + iid, icit_id=iid, cisi=r["cisi"], site=r["site"], region=r["region"],
            period=(rr.get("time", "-") + " / " + rr.get("period", "-")), field_no=rr.get("excavation-idno", ""),
            icit_type=r["type"], technique=tech, firing=stage, firing_conf=conf, firing_basis=basis,
            vessel_form=form, vessel_size="", vessel=("no" if False else "yes"),
            text_wells=" ".join(seq), complete=r["complete"], source=src, note=note,
            citation="ICIT (Wells & Fuls) via field-cady export" + ("; " + KEN21 if "Kenoyer" in src else ""),
        ))
    for k in K21:
        fig, site, form, loc, match, wells, note = k
        if match:
            continue
        rows.append(dict(
            vid="K21-" + fig, icit_id="", cisi="", site=site, region="", period="Harappan (per Kenoyer)", field_no="",
            icit_type="", technique="painted", firing="pre", firing_conf="object", firing_basis="painted before firing (Kenoyer 2021)",
            vessel_form=form, vessel_size="", vessel=("no" if form == "bangle" else "yes"),
            text_wells=" ".join(wells), complete="", source="Kenoyer2021", note=f"location {loc}; {note}", citation=KEN21,
        ))
    for d in LIT_OTHER:
        rows.append(dict(
            vid=d["vid"], icit_id="", cisi="", site=d["site"], region="", period="", field_no="", icit_type="",
            technique=d["technique"], firing=d["firing"], firing_conf="object", firing_basis=d["basis"],
            vessel_form=d["form"], vessel_size="", vessel="yes", text_wells=d["text_wells"], complete="",
            source=d["source"], note=d["note"], citation=d["citation"],
        ))
    cols = list(rows[0].keys())
    with open(HERE / "vessel_marks.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    from collections import Counter
    print(len(rows), "rows")
    print(Counter((r["technique"], r["firing"], r["firing_conf"]) for r in rows))
    print("form recorded:", sum(1 for r in rows if r["vessel_form"]))


if __name__ == "__main__":
    main()
