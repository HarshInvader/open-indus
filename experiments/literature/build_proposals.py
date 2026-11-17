"""Build experiments/literature/proposals.json: machine-readable sign-value proposals.

Run: .venv/bin/python experiments/literature/build_proposals.py
Reads DATA files only (no code from sources/ is executed).
Each entry: {sign, sign_M (list, Mahadevan, if known), sign_W (Wells/ICIT, if known),
             proposed_value, value_type (sound|meaning|function|number), source, confidence_of_mapping, note}
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "sources"
OUT = Path(__file__).resolve().parent / "proposals.json"

bridge = json.load(open(SRC / "shaunmortal_indus/data/bridge_WM.json"))  # W -> {"M": [...]}


def w2m(w):
    k = str(int(w))
    return ["M%d" % m for m in bridge.get(k, {}).get("M", [])]


def e(sign, value, vtype, source, M=None, W=None, mapping="from source", note=""):
    return {"sign": sign, "sign_M": M or [], "sign_W": W, "proposed_value": value,
            "value_type": vtype, "source": source, "mapping_confidence": mapping, "note": note}


P = {}

# ---------------- Parpola (Dravidian rebus) ----------------
par = "Parpola 2010, 'A Dravidian solution to the Indus script problem' (Coimbatore), https://tuhat.helsinki.fi/ws/portalfiles/portal/127256525/Parpola_A_2010._A_Dravidian_solution_to_the_Indus_script_problem.pdf ; Parpola 1994 Deciphering the Indus Script (CUP)"
P["parpola"] = [
    e("plain fish", "mīn 'fish' = rebus 'star' -> 'god/deity' in names", "sound+meaning", par, ["M59"], "W220", "verified by drawing"),
    e("3 short strokes + fish", "mū-mīn 'three stars' = Mṛgaśiras (Orion's head)", "sound+meaning", "Parpola 1994 ch.10-11 (UNVERIFIED page)", ["M102", "M59"], None, "verified by drawing", "numeral order: attribute precedes head, as in Proto-Dravidian"),
    e("6 short strokes + fish", "aṟu-mīn 'six stars' = Pleiades (Kṛttikā)", "sound+meaning", par, ["M108", "M109", "M59"], None, "verified by drawing"),
    e("7 short strokes + fish", "eḻu-mīn 'seven stars' = Ursa Major (Seven Sages); whole text of seal H-9", "sound+meaning", par, ["M110", "M112", "M59"], None, "verified by drawing"),
    e("fish with roof/caret", "mēy-mīn 'roof-fish' = rebus mai-mīn 'black star' = Saturn", "sound+meaning", "Parpola 1994: 'roofed fish' (page UNVERIFIED)", ["M65"], "W235", "verified by drawing"),
    e("'fig tree' (Parpola sign 123, three-branched) + fish", "vaṭa-mīn: vaṭam 'banyan/rope' ~ vaṭa 'north' -> 'north star' (Alcor / pole star Thuban)", "sound+meaning", par, [], None, "Mahadevan number UNVERIFIED", "Parpola no. 123; ligature with 'crab' = Parpola 124"),
    e("two intersecting circles", "muruku 'ring, earring, bangle' = rebus muruku 'young man' -> god Murukan", "sound+meaning", par, ["M403"], "W840", "verified by drawing", "esp. M403+M87; frequent on stoneware bangles"),
    e("'spindle' (first sign of M-112/M-241)", "katir 'spindle' = rebus katir 'to shine' (Murukan epithet)", "sound+meaning", par, [], None, "Mahadevan number UNVERIFIED", "new in 2010, not in 1994 book"),
    e("'squirrel on tree' complex sign", "aṇil piḷḷai -> piḷḷai 'young, child' (attribute of Muruku)", "sound+meaning", par, [], None, "Mahadevan number UNVERIFIED"),
    e("man (stick figure)", "āḷ 'man, servant' ~ āḷ 'to rule'", "sound+meaning", "Parpola 1994 (UNVERIFIED page; widely cited)", ["M1"], "W090", "verified by drawing"),
    e("short-stroke numerals 1-7", "oru, iru, mū, nāl, cay/aintu, aṟu, eḻu (Proto-Dravidian numerals)", "sound+number", par, ["M97", "M98", "M99", "M100", "M102", "M103", "M104", "M105", "M106", "M107", "M108", "M109", "M110", "M112"], None, "verified by drawing", "inverted semicircles = tens (Parpola)"),
    e("plain fish on tablet H-902B", "literal 'fish' (offering of four pots of fish)", "meaning", par, ["M59"], "W220", "verified by drawing", "Parpola admits literal use on tablets, rebus on seals"),
]

# ---------------- Mahadevan (Dravidian, Old Tamil) ----------------
mah = "Mahadevan 2010/2011 'Akam and Puram: address signs of the Indus script', IJDL 40:81-94 (excerpts via https://keezhadiandindusvalleycivilization.com/akam-and-puram-of-the-indus-script/ ; review: Jyothibabu, https://www.academia.edu/101124192)"
P["mahadevan"] = [
    e("jar (terminal)", "-an, Dravidian masculine singular suffix (1970); later 'priest/offering' title contrasted with military arrow", "sound/function", "Mahadevan 1970 'Dravidian parallels in proto-Indian script' JTS 2; Jyothibabu review", ["M342"], "W740", "verified by drawing"),
    e("diamond-with-cap ('quarter of city')", "akam 'inside, citadel, inner city' -> address/opening sign", "sound+meaning", mah, ["M267"], "W817/W861", "number from review; drawing consistent"),
    e("two short strokes superscript after M267", "oblique / genitive / locative case marker (-attu?)", "function", mah, ["M99", "M100"], "W002", "verified by drawing"),
    e("crescent (initial)", "puṟam 'outer (city)', address of outer-city residents", "sound+meaning", mah, ["M293"], None, "number from review (crescent)"),
    e("sign 373", "akam (alternative sign)", "sound+meaning", "Jyothibabu review of Mahadevan", ["M373"], None, "number from review, not checked against drawing"),
    e("'city of four quarters' (quartered circle/oval)", "pāḻi 'city, town'", "sound+meaning", mah, [], None, "Mahadevan number UNVERIFIED (candidate M391)"),
    e("arrow", "military title (contrasted with priestly jar)", "meaning", "Jyothibabu review of Mahadevan", ["M211"], "W520", "verified by drawing"),
    e("person carrying two burdens", "poṟai 'burden' -> poṟaiyan (Chera royal title) 'bearer/ruler'", "sound+meaning", "Mahadevan (1970s-1990s; UNVERIFIED exact paper)", ["M12"], "W151", "verified by drawing"),
    e("'wolf back + hook + crossroads + jar' sequence", "'merchant of the city' ~ Vedic Pūṣan", "meaning", "Mahadevan 2014, Dravidian Proof of the Indus Script via the Rig Veda, IRC Bulletin 4, https://rmrl.in/bulletin/bulletin-No-4-Nov-2014.pdf", [], None, "sign numbers UNVERIFIED"),
]

# ---------------- Wells (numerals, metrology) ----------------
P["wells"] = [
    e("long (tall) stroke", "10 (units of volume on pots; ~9.24 L per stroke on Purana Qila vessels)", "number", "Wells 2015 The Archaeology and Epigraphy of Indus Writing, ch.4-5 (Archaeopress)", ["M86", "M87", "M89"], "W031/W032/W033", "verified by drawing", "STATE.md F5 finds 3 data tests against tall=10"),
    e("short stroke", "1", "number", "Wells 2015 ch.5", ["M97", "M98", "M102", "M104", "M106", "M108", "M110"], None, "verified by drawing"),
    e("V/cup sign after tall strokes", "volumetric measure unit", "meaning", "Wells 2015 ch.4", ["M328"], None, "drawing is U-shaped cup; mapping probable"),
    e("sign 900 (right parenthesis)", "positional-notation numeral", "number", "Wells 2015 fig.5.7", ["M287"], "W900", "bridge"),
]

# ---------------- Mukhopadhyay (logographic/administrative) ----------------
muk = "Mukhopadhyay 2019 Palgrave Commun 5:73 https://www.nature.com/articles/s41599-019-0274-1 ; 2023 HSSC 10:972 https://www.nature.com/articles/s41599-023-02320-7"
P["mukhopadhyay"] = [
    e("stroke signs (22 forms)", "NUM: metrological denominations, value depends on commodity", "function", muk, [], None, "class-level"),
    e("rimless pot/cup with 2-4 tall strokes on tablet reverse", "metrological notation (licence fee / quantity)", "meaning", muk, ["M328", "M87", "M89"], None, "drawing consistent"),
    e("jar (terminal)", "phrase-final functional sign of a 'formalized data carrier' (not a name suffix)", "function", muk, ["M342"], "W740", "verified by drawing"),
    e("plant/sheaf signs after strokes", "CROP / commodity", "meaning", muk, ["M161", "M162", "M169"], "W390", "class-level, bridge"),
]

# ---------------- Fuls 2024 Linear Elamite look-alikes ----------------
fk = json.load(open(SRC / "paragorth_Indus-/data/derived/fuls2024-le-indus-key.json"))
P["fuls2024_linear_elamite_lookalikes"] = [
    e("W" + w, v, "sound", "Fuls 2024 IJAS 14(1):3-16 Fig.9 (values: Desset et al. 2022); Fuls says the scripts are NOT directly related",
      w2m(w), "W" + w, "bridge_WM" if w2m(w) else "no Mahadevan bridge", "graphic look-alike only; paragorth ANCHORS §11 blind test P=0.83")
    for w, v in fk["key"].items()]

# ---------------- Yajnadevam (Sanskrit, cryptanalytic) ----------------
rows = list(csv.DictReader(open(SRC / "field-cady_indus_valley_script_corpus/xlits.csv")))
yaj = []
for r in rows:
    s = r["sign"].strip()
    if s in ("000", "999") or not s.isdigit():
        continue
    yaj.append(e("W" + s, r["xlit"], "sound",
                 "Yajnadevam 2024 'A cryptanalytic decipherment of the Indus script' https://www.academia.edu/78867798 ; per-sign key from yajnadevam/lipi xlits.csv via sources/field-cady_indus_valley_script_corpus/xlits.csv",
                 w2m(s), "W" + s, "bridge_WM" if w2m(s) else "no Mahadevan bridge",
                 ("canonical=W%s" % r["canonical"]) if r["canonical"] and r["canonical"] != s else ""))
P["yajnadevam"] = yaj

meta = {
    "_readme": "Sign-value proposals from the literature. sign_M via sources/shaunmortal_indus/data/bridge_WM.json where only Wells numbers are given. 'verified by drawing' = matched against data/sign_images by the literature agent. Values are claims to TEST, not evidence.",
    "counts": {k: len(v) for k, v in P.items()},
}
json.dump({"meta": meta, "proposals": P}, open(OUT, "w"), ensure_ascii=False, indent=1)
print(meta["counts"], "->", OUT)
