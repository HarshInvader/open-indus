"""Board task #1: one row per Indus-inscribed object found outside the Indus region.

Run: .venv/bin/python -I experiments/foreign_corpus/build.py
Writes foreign_corpus.csv. Sign sequences come from ICIT (Wells numbers) or M77 (Mahadevan numbers) as held in
data/; the other list is filled through sources/shaunmortal_indus/data/bridge_WM.json (first candidate, '?' = no
bridge). Cross-identifications (ICIT <-> M77 <-> Laursen 2010 Fig. 11 as transcribed in
sources/paragorth_Indus-/data/gulf_seals.csv) were made by hand from Mahadevan 1977 Appendix V (OCR in
experiments/old_registers/raw/mahadevan_item) and the meluhha catalogue.
"""
import csv, json, sys
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from corpus.load import icit_texts, m77_texts  # noqa

BR = json.load(open(ROOT / "sources/shaunmortal_indus/data/bridge_WM.json"))
W2M = {f"W{int(k):03d}": [f"M{m}" for m in v["M"]] for k, v in BR.items()}
M2W = defaultdict(list)
for w, ms in W2M.items():
    for m in ms:
        M2W[m].append(w)
ICIT = {t["id"]: t for t in icit_texts()}
M77 = {}
for t in m77_texts():
    M77.setdefault(t["text_no"], t)
PG = {r["seal_no"]: r for r in csv.DictReader(open(ROOT / "sources/paragorth_Indus-/data/gulf_seals.csv"))}

conv = lambda seq, table: "-".join(s if s in "|#" else (table.get(s) or ["?"])[0] for s in seq)

# (id, icit_ids, m77_no, laursen_no, findspot, region, shape, animal, date, sources, note)
OBJ = [
 ("UR-01", ["3897.1"], 9832, "16", "Ur", "Mesopotamia", "round Gulf", "gaur", "undated (bought at Ur 1928-9)", "Gadd 1932 no.2; BM 122187", ""),
 ("UR-02", ["3898.1"], 9846, "21", "Ur", "Mesopotamia", "round Gulf", "gaur/short-horned bull", "Ur III? (ICIT 'Dynasty III'; Woolley fill, insecure)", "Gadd 1932 no.16; BM 123208; U.17649", "ICIT ends W328-W004-W002, M77/Laursen end W717-W005 (354): last signs disputed; ICIT/paragorth label 'Dilmun'; Gadd 1932 says FOUR characters, all well known"),
 ("UR-03", ["5231.1"], None, "18", "Ur", "Mesopotamia", "round Gulf (fragment)", "-", "undated", "Laursen 2010 no.18 cites Gadd 1932 no.4", "CONFLICT: Gadd says no.4 keeps only a 'fish' sign and part of another; ICIT/Laursen read man+W405. Mahadevan gives Gadd 4 as M77 9834 = M75 (a fish). Identity with UR-06 unresolved"),
 ("UR-04", ["5225.1"], 9833, "19", "Ur", "Mesopotamia", "round Gulf (fragment)", "illegible", "undated (Diqdiqqah)", "Gadd 1932 no.5 (Laursen no.19)", "fragment; only man sign sure; M77 9833 is Gadd no.3 or no.5 (OCR ambiguous)"),
 ("UR-05", ["3899.1"], None, None, "Ur", "Mesopotamia", "round", "gaur", "undated", "ICIT; Gadd 1932 no.3 (U.17342)?", "Gadd number unconfirmed; NOT M77 9842 (that is Gadd 12, see UR-10)"),
 ("UR-10", [], 9842, None, "Ur", "Mesopotamia", "round Gulf", "water-carrier device (pictorial)", "Kassite(?) level", "Gadd 1932 no.12 = U.16747; Mahadevan App. V 'No.12'", "PICTORIAL: Mahadevan read the water-carrier device as signs M175-M12-M182; Gadd calls it a 'hieroglyphic' picture, not an ordinary inscription; exclude from order and crib tests"),
 ("UR-06", [], 9834, None, "Ur", "Mesopotamia", "seal", "none", "undated", "Gadd 1932 no.4 = BM 122188; Mahadevan App. V 'No.4'", "single legible sign M75 (roofed fish), consistent with Gadd's 'fish sign and fragment of another'"),
 ("UR-07", [], 9845, "20", "Ur", "Mesopotamia", "round Gulf", "short-horned bull", "grave probably Sargonic", "Gadd 1932 no.15 = U.8685 (Penn); Mahadevan App. V 'No.15'; Laursen 2010 no.20", "= Laursen no.20 ('missing' in paragorth); Gadd: inscription crowded and not distinct, first sign (left in impression) unique flower/skin form"),
 ("UR-09", [], None, "17", "Ur", "Mesopotamia", "round Gulf", "?", "undated", "Laursen 2010 Fig.11 no.17", "4-5 signs, first damaged; not in any corpus we hold"),
 ("KISH-01", ["1970.1"], 9821, None, "Kish", "Mesopotamia", "square", "unicorn", "Akkadian? (under Hammurabi-age temple)", "Mackay JRAS 1925", "core W240-W643 also at Harappa and Mohenjo-daro"),
 ("KISH-02", ["1971.1"], 9822, None, "Kish", "Mesopotamia", "square", "unicorn", "Akkadian? (ICIT)", "Langdon JRAS 1931", ""),
 ("UMMA-01", ["3884.1"], 9811, None, "Umma (Djokha)", "Mesopotamia", "clay sealing (tag)", "unicorn", "undated (bought)", "Scheil RA 1925", ""),
 ("UMMA-02", [], None, None, "Umma", "Mesopotamia", "square", "unicorn", "undated (surface 2017)", "SAHI 2018 fig.6.61", "partial: ...-803-740 only"),
 ("GIRSU-01", ["5222.1"], 9852, "22", "Girsu (Telloh)", "Mesopotamia", "round Gulf", "gaur/short-horned bull", "undated", "Delaporte CCO I pl.II.8; Laursen 2010 no.22", "drawing shows 5 signs vs 4"),
 ("GIRSU-02", ["3885.1"], 9851, None, "Girsu (Telloh)", "Mesopotamia", "square", "tiger", "3rd mill.", "RA 1925 p.99", ""),
 ("NIPPUR-01", ["3860.1"], None, None, "Nippur", "Mesopotamia", "square (faience)", "zebu", "Kassite context (heirloom)", "Zettler OIP 111; IM 78230", ""),
 ("ASMAR-01", [], None, None, "Tell Asmar (Eshnunna)", "Mesopotamia", "square stamp", "?", "Akkadian houses", "Frankfort OIC 16 1933; As.31-221", "inscribed, sequence not transcribed"),
 ("BABYLON-01", [], None, None, "Babylon", "Mesopotamia", "round", "bull over manger", "c.2500-2000 BCE", "BM image 01613325406 (stamp-seal, Babylon)", "sequence not transcribed; check whether = a Gadd item"),
 ("SUSA-01", ["3881.1"], None, "14", "Susa", "Iran", "round Gulf", "gaur", "late 3rd mill. (Acropole)", "Amiet 1972 no.1643", ""),
 ("SUSA-02", ["3882.1"], 9801, None, "Susa", "Iran", "cylinder", "three bulls in file", "late 3rd mill.", "Delaporte CCO I pl.XXV.15; Louvre Sb 2425", "M77 reads L-R starting M173(W416); ICIT ends with W416: reading direction disputed; interior signs differ"),
 ("LURISTAN-01", ["2153.1"], None, "15", "Luristan", "Iran", "round Gulf", "gaur", "undated (unprovenanced within Luristan)", "Amiet 1973 pl.23a-b", ""),
 ("YAHYA-01", ["3886.1"], None, None, "Tepe Yahya", "Iran", "seal impression on sherd", "-", "IVA/IVB", "Pittman 2001 fig.10.63", ""),
 ("JALALABAD-01", [], None, None, "Jalalabad (Fars)", "Iran", "cylinder (Oxus type)", "worship scene", "late 3rd mill.?", "Ascalone 2008; Vidale & Frenez 2021 JARCS (raw/jalalabad_2021.pdf)", "3-5 signs, readings alternative: fringed-V(740/741?) twins(32) man(90) 3 strokes+man; new to us"),
 ("SISTAN-01", [], None, None, "Sistan? (unprovenanced)", "Iran", "cylinder", "lost", "?", "Knox 1994 (in Parpola & Koskikallio eds)", "man signs + strokes; new to us"),
 ("FAILAKA-01", ["148.1"], None, "12", "Failaka", "Gulf", "round Gulf", "-", "c.2000 BCE", "Kjaerum 1983 no.319", "drawing order reversed vs corpus"),
 ("FAILAKA-02", ["147.1"], None, "13", "Failaka", "Gulf", "round Dilmun type", "gaur", "c.2000 BCE", "Kjaerum 1983 no.279", "drawing has extra signs and a scene"),
 ("BAHRAIN-01", ["3863.1"], None, "7", "Qala'at al-Bahrain", "Gulf", "round Gulf", "gaur", "City IIa", "Kjaerum 1994 fig.1725; Al-Sindi 1999 no.279", "drawing order reversed vs corpus; photo confirms W055"),
 ("BAHRAIN-02", [], None, "6", "Qala'at al-Bahrain", "Gulf", "round Gulf (fragment)", "?", "City II", "Kjaerum 1994 fig.1726", "only twins legible"),
 ("BAHRAIN-03", ["5227.1"], None, "8", "Karzakan", "Gulf", "round Gulf", "gaur/rhino", "c.2050-1900 BCE", "Srivastava 1991; Al-Sindi 1999 no.180; BBM 18839", ""),
 ("BAHRAIN-04", ["5228.1"], None, "11", "Karzakan", "Gulf", "round Gulf", "gaur", "c.2050-1900 BCE", "Laursen 2010 fig.1b; BBM 14569", ""),
 ("BAHRAIN-05", ["5230.1"], None, "56", "Karzakan", "Gulf", "round Gulf", "gaur", "c.2050-1900 BCE", "Al-Sindi 1999 no.160; BBM 20362", "middle element is a motif, not script"),
 ("BAHRAIN-06", ["5229.1"], None, "9", "Saar", "Gulf", "round Gulf", "none", "c.2050-1900 BCE", "Al-Sindi 1999 no.182", "photo confirms W055"),
 ("BAHRAIN-07", ["5232.1"], None, "10", "Janabiyah", "Gulf", "round Gulf", "gaur", "c.2050-1900 BCE", "Laursen 2010 fig.1a", "last block maybe 9 not 12"),
 ("KALBA-01", ["5551.1"], None, None, "Kalba", "Gulf", "round", "none", "?", "ICIT", "single sign"),
 ("SALUT-01", ["4173.1"], None, None, "Salut ST1", "Oman", "square (local softstone)", "gaur", "late 3rd mill.", "Frenez et al. 2016", ""),
 ("SALUT-02", ["4174.1"], None, None, "Salut ST1", "Oman", "stamped jar (tablet impression)", "two bison/elephant", "late 3rd mill.", "Frenez et al. 2016", "only one legible sign"),
 ("RJ-01", ["935.1"], None, None, "Ra's al-Jinz RJ-2", "Oman", "square copper seal", "unicorn", "Period III", "Cleuziou et al. 1994", "illegible under corrosion"),
 ("RJ-02", ["3864.1"], None, None, "Ra's al-Jinz RJ-2", "Oman", "pottery graffito", "-", "Period II/III", "Cleuziou et al. 1994", ""),
 ("RJ-03", ["3865.1"], None, None, "Ra's al-Jinz RJ-2", "Oman", "pottery graffito", "-", "Period II", "Cleuziou et al. 1994", ""),
 ("RJ-04", ["3866.1"], None, None, "Ra's al-Jinz RJ-2", "Oman", "pottery graffito", "-", "Period II", "Cleuziou et al. 1994", ""),
 ("HAJAR-01", ["160.1"], None, None, "Hajar", "Oman", "tablet", "gaur", "?", "ICIT", ""),
 ("UAQ-01", [], None, None, "Umm al-Quwain (site not named)", "Gulf", "round softstone", "humped bull", "c.2300 BCE (reported)", "news report c. April 2026 (ittihaas.com aggregator)", "unverified press report; no sign sequence published"),
 ("GONUR-01", ["4155.1"], None, None, "Gonur Depe", "Central Asia", "square", "elephant", "late 3rd mill.", "Sarianidi; Bakry 2016 fig.10", ""),
 ("ALTYN-01", ["16.1"], None, None, "Altyn Depe", "Central Asia", "square", "none", "Namazga V", "Masson; Bakry 2016 fig.8", ""),
 ("SHORT-01", ["3874.1"], None, None, "Shortughai", "Central Asia", "square", "rhino", "Mature Harappan", "Francfort", "Shortughai is an Indus colony: foreign findspot, home milieu"),
 ("UNPROV-01", ["3889.1"], 9901, "23", "unknown (Near East)", "unknown-WA", "round Gulf", "gaur/short-horned bull", "?", "Gadd 1932 no.17", ""),
 ("UNPROV-02", ["3887.1"], 9902, "24", "unknown (Babylonia, via Baghdad dealer)", "unknown-WA", "round Gulf", "bull mating cow", "?", "Gadd 1932 no.18 = BM 123059; Mahadevan App. V 'No.18'", "ONE object: ICIT 3887 (W190-W091-W603) and M77 9902 (M65-M1-M1-M245-M245). Gadd's text (5 signs: damaged fish, two men side by side, two others like Marshall 297 and 28) and plate III fit M77; sequence taken from M77"),
 ("UNPROV-03", ["5223.1"], None, "26", "unknown (Mesopotamia?)", "unknown-WA", "round Gulf", "gaur", "?", "Buchanan 1981 no.1088; Newell 23", "drawing has one more initial sign"),
 ("UNPROV-04", ["5226.1"], None, "27", "unknown (Mesopotamia?)", "unknown-WA", "round Gulf", "bird", "?", "Buchanan 1981 no.1089; Newell 876", ""),
 ("UNPROV-05", ["5224.1"], None, None, "unknown", "unknown-WA", "round Gulf", "gaur", "?", "ICIT", "provenance West Asian assumed from ICIT block"),
 ("UNPROV-06", ["3888.1"], None, None, "unknown", "unknown-WA", "cylinder", "?", "c.2000 BCE (ICIT)", "ICIT", ""),
 ("UNPROV-08", [], 9903, "25", "unknown (prob. West Asia)", "unknown-WA", "seal", "short-horned bull", "?", "Langdon JRAS 1932 p.48 (Rosen coll.)", "M77 7 signs vs Laursen 'about 6'"),
 ("UNPROV-09", [], 9904, None, "unknown (prob. West Asia)", "unknown-WA", "seal", "short-horned bull", "?", "Mahadevan 1977 App. V", "M77 only"),
 ("UNPROV-10", [], 9905, None, "unknown (prob. West Asia)", "unknown-WA", "seal", "two-register scene", "?", "Iraq 1936 p.88 fig.1", "M77 only"),
]

PREFER_M77 = {"UNPROV-02"}
NEW = {"JALALABAD-01", "SISTAN-01", "UAQ-01", "BABYLON-01"}  # in none of ICIT, M77, paragorth gulf_seals, meluhha/foreign_objects.csv
rows = []
for (oid, icit, m77, lno, site, reg, shape, animal, date, src, note) in OBJ:
    seqW = seqM = ""
    origin = ""
    if icit and not (m77 and oid in PREFER_M77):
        t = ICIT[icit[0]]
        seqW = "-".join(t["seq"]); seqM = conv(t["seq"], W2M); origin = "ICIT"
    elif m77:
        t = M77[m77]
        seqM = "-".join(t["seq"]); seqW = conv(t["seq"], M2W); origin = "M77"
    elif lno and PG[lno]["sequence_glyph_coding"]:
        s = [f"W{int(x):03d}" for x in PG[lno]["sequence_glyph_coding"].split("-")]
        seqW = "-".join(s); seqM = conv(s, W2M); origin = "Laursen/paragorth"
    m77seq = "-".join(M77[m77]["seq"]) if m77 else ""
    pg = PG.get(lno) if lno else None
    conf = pg["confidence"] if pg and pg["confidence"] != "missing" or (pg and not origin) else "corpus only" if origin else ("none: no transcription" if not origin else "corpus only")
    verified = ("checked vs Laursen 2010 drawing/photo (paragorth)" if pg and pg["confidence"] in ("confirmed", "probable", "uncertain")
                else "no")
    legible = [x for x in seqW.split("-") if x and x not in "|#"]
    rows.append(dict(id=oid, findspot=site, region=reg, shape=shape, animal=animal, date=date,
                     seq_wells=seqW, seq_m77=seqM, m77_text=m77 or "", m77_seq_as_published=m77seq,
                     icit_id=";".join(icit), laursen2010_no=lno or "", seq_origin=origin, n_legible=len(legible),
                     reading_confidence=conf, verified_against_image=verified,
                     new_to_us="yes" if oid in NEW else "no",
                     sources=src, note=note))

with open(HERE / "foreign_corpus.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(len(rows), "objects;", sum(r["new_to_us"] == "yes" for r in rows), "new to us;",
      sum(r["n_legible"] >= 2 for r in rows), "with >=2 legible signs")
