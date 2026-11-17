"""Build objects.csv: Indus-inscribed (and related mixed / Linear Elamite-on-Indus-type) objects from
Iran, Central Asia and the Gulf. Texts come from ICIT (reading order); M numbers via the shaunmortal
bridge only when every sign maps to exactly one Mahadevan sign.
Run: .venv/bin/python experiments/elamite_bridge/build_objects.py
"""
import csv, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from corpus.load import icit_texts
ROOT = Path(__file__).resolve().parents[2]
br = json.load(open(ROOT / "sources/shaunmortal_indus/data/bridge_WM.json"))
icit = {t["id"]: t for t in icit_texts()}


def to_m(seq):
    out = []
    for s in seq:
        if s in ("#", "|"): out.append(s); continue
        e = br.get(str(int(s[1:])))
        if not e or len(e["M"]) != 1: return ""
        out.append("M%d" % e["M"][0])
    return "-".join(out)


# (object, icit_id, site, region, type, emblem, context_date, publication, photo, other_writing, notes)
ROWS = [
 # ---------------- Iran ----------------
 ("Susa round seal (Louvre; Sb no. to confirm, possibly Sb 5614)", "3881.1", "Susa", "Iran (Khuzestan)", "round stamp seal", "gaur/short-horned bull",
  "Acropole, 'late 3rd mill.' (ICIT); no stratum", "Amiet 1972 Glyptique susienne (MDP 43) no. 1643; Laursen 2010", "Louvre collections site (check); Wikimedia 'Sb 5614'", "none",
  "Gulf-type round seal; text breaks Indus grammar (context Q4)"),
 ("Susa cylinder seal Sb 2425 (AS 41)", "3882.1", "Susa", "Iran (Khuzestan)", "cylinder seal, steatite, H 2.3 cm D 1.6 cm", "two bulls/buffalo at manger",
  "found 1898-1906 Acropole; Louvre dates Suse IVB 2400-2100 BCE", "Louvre record https://collections.louvre.fr/ark:/53355/cl010176471; Amiet 1972", "yes, Louvre site + Wikimedia Commons", "none",
  "Louvre: made in the Indus valley, found at Susa; 8 signs"),
 ("Susa 'text O' red clay tablet (Louvre Sb 9382, 11 x 7 cm)", "", "Susa", "Iran (Khuzestan)", "incised clay tablet", "none",
  "undated; Fuls proposes early 2nd mill. BCE", "Fuls 2024 IJAS 14(1) Fig. 10; excluded from LE corpus (OCLEI); Dahl 2023 calls its content unusual", "drawing in Fuls 2024; Louvre record not found online",
  "about 3 Linear Elamite-like + about 20 Indus-like graphemes + Sibri-type sign pair",
  "eroded; first sign like W853 (initial in 10/11 Indus texts) and also initial here; pair 220+33. MIXED object, not a bilingual: no parallel text"),
 ("Tepe Yahya stamped sherd TY-106", "3886.1", "Tepe Yahya", "Iran (Kerman)", "potsherd stamped with seal", "none",
  "Period IVA/IVB (late 3rd mill.)", "Pittman 2001; CISI 3.3 (2023)", "CISI 3.3 (library)", "none (Proto-Elamite tablets at the site are c. 3000 BCE, earlier)", ""),
 ("Luristan round seal", "2153.1", "'Luristan'", "Iran (Zagros)", "round stamp seal", "gaur",
  "unprovenanced (market attribution)", "ICIT; CISI 3.3?", "unknown", "none", "identity trail 840-413 (paragorth)"),
 ("Konar Sandal South white marble cylinder seal", "", "Konar Sandal South (Jiroft)", "Iran (Kerman)", "cylinder seal", "Indus animal series in local style",
  "Trench IX metallurgical area, 2nd half 3rd mill.", "Vidale & Frenez 2015, South Asian Studies 31(1), doi:10.1080/02666030.2015.1008820", "yes, in paper (harappa.com PDF)", "none",
  "UNINSCRIBED; same site has Linear Elamite tablets LEI 28-31 and Indus-type weights (1 cubical, 12 spherical)"),
 ("Konar Sandal bronze stamp seal (caprid + gharial)", "", "Konar Sandal (surface)", "Iran (Kerman)", "stamp seal", "caprid, gharial",
  "surface find", "Vidale & Frenez 2015", "in paper", "none", "UNINSCRIBED; Indus-inspired gharial"),
 ("Konar Sandal tablets LEI 28-31 (B', C', D', E')", "", "Konar Sandal South (Jiroft)", "Iran (Kerman)", "fired clay tablets/bricks", "none",
  "end of 3rd mill. (E' upper layers)", "Desset 2014 Iranica Antiqua 49: 83-109; HLED docs 28-31; Desset et al. 2026 vol. 2", "HLED site", "Linear Elamite (Eastern): zu-la-ri2, pa-a-ri-ri2 ... (names)",
  "NO Indus signs. Authenticity questioned (Lawler 2007 Science 317: 588; Dahl 2022 interview)"),
 ("Shahdad ceramic vessel LEI 19 (text S), Iran National Museum 8527", "", "Shahdad, Cemetery A, Grave 30", "Iran (Kerman)", "ceramic vessel", "none",
  "grave sample 14C 2923-2667 cal BC (unfavourable curve; Grave 338: 2500-2300)", "Eskandari, Nokandeh, Vidale & Marchesi 2025, ZA 115(2): 123-136, doi:10.1515/za-2025-0012; Hinz 1971", "HLED doc 19 photo",
  "Linear Elamite ti-n-ra-X-r (name?)", "NO Indus signs; 348 potters' marks at Shahdad (Hakemi) never shown to be script"),
 # ---------------- Central Asia ----------------
 ("Altyn Depe square seal Alt-90", "16.1", "Altyn Depe", "Turkmenistan", "square stamp seal, soft stone, 14 mm", "none",
  "Excavation 7, 'priest's' tomb; Namazga V (c. 2300-2000 BCE)", "Masson 1981 pl. XXII; Masson 1988 Altyn-Depe; CISI 3.3", "CISI 3.3; Penn Expedition", "none",
  "2 signs; second Altyn Depe seal (swastika) uninscribed"),
 ("Gonur Depe square elephant seal", "4155.1", "Gonur Depe", "Turkmenistan (Margiana)", "square stamp seal, steatite", "elephant",
  "Sarianidi excavations (1980s-90s); BMAC c. 2300-1700 BCE; exact locus not in our sources", "Sarianidi; Kohl 2007 fig. 5.12a; CISI 3.3", "Kohl 2007; CISI 3.3", "none",
  "8 signs, ends with jar W740; Indus-made by style (Penn Expedition)"),
 ("Gonur potsherd with signs", "", "Gonur Depe (surface)", "Turkmenistan (Margiana)", "potsherd", "none",
  "surface find, undated", "Klochkov 1998, Ancient Civilizations from Scythia to Siberia 5(2): 165-175", "in paper", "claimed Linear Elamite (Klochkov); Desset 2018 doubtful",
  "not an Indus text; not a bilingual"),
 ("Shortughai rhinoceros seal Sh-69", "3874.1", "Shortughai", "Afghanistan", "square stamp seal, steatite, 36 mm", "rhinoceros",
  "Indus outpost on the Oxus (Francfort 1989), Mature Harappan", "Francfort 1989; CISI 3.3", "CISI 3.3", "none", "Indus colony site, so not foreign usage"),
 ("'Central Asian gold seal' LEI 33", "", "unknown", "Central Asia (attrib.)", "gold seal", "?",
  "unprovenanced; 'beginning of 2nd mill.'", "HLED doc 33; Desset et al. 2026 vol. 2", "HLED", "Linear Elamite ra~ha?-ši-za-na-ni?-ri2", "NO Indus signs"),
 # ---------------- Gulf ----------------
 ("Linear Elamite Gulf-type seal LEI 22 (text V), Ligabue Collection", "", "unknown, 'Persian Gulf'", "Gulf", "round stamp seal, chlorite, D 2.5 cm", "bull over 3-pronged object (Indus layout)",
  "unprovenanced; early 2nd mill. by type", "Winkelmann 1999 p. 25 figs 1-2; Laursen 2010 no. 28; HLED doc 22 (za-ši-ri2 = signs 70, 57, 46)", "HLED photo + drawing",
  "Linear Elamite za-ši-ri2 'Zaširi'", "Indus-seal format with the text slot in Linear Elamite: shows the slot held a personal name. NO Indus signs, so not a bilingual"),
 ("Failaka seal", "147.1", "Failaka", "Kuwait", "Gulf-type round seal", "gaur", "Kjaerum 1983, c. 2000 BCE", "Kjaerum 1983", "Kjaerum 1983", "none", ""),
 ("Failaka seal", "148.1", "Failaka", "Kuwait", "Gulf-type round seal", "-", "Kjaerum 1983, c. 2000 BCE", "Kjaerum 1983", "Kjaerum 1983", "none", ""),
 ("Qala'at al-Bahrain seal", "3863.1", "Qala'at al-Bahrain", "Bahrain", "Gulf-type round seal, steatite", "gaur", "Period IIa (c. 2050-1900 BCE)", "Laursen 2010", "Laursen 2010", "none", ""),
 ("Karzakan seal", "5227.1", "Karzakan", "Bahrain", "Gulf-type round seal", "gaur", "grave mound, c. 2050-1900 BCE", "Laursen 2010", "Laursen 2010", "none", "starts with person sign W091"),
 ("Karzakan seal", "5228.1", "Karzakan", "Bahrain", "Gulf-type round seal", "gaur", "grave mound", "Laursen 2010", "Laursen 2010", "none", "starts with person sign W091"),
 ("Karzakan seal", "5230.1", "Karzakan", "Bahrain", "Gulf-type round seal", "gaur", "grave mound", "Laursen 2010", "Laursen 2010", "none", ""),
 ("Saar seal", "5229.1", "Saar", "Bahrain", "Gulf-type round seal", "none", "settlement, c. 2000-1900 BCE", "Laursen 2010", "Laursen 2010", "none", ""),
 ("Janabiyah seal", "5232.1", "Janabiyah", "Bahrain", "Gulf-type round seal", "gaur", "grave", "Laursen 2010", "Laursen 2010", "none", ""),
 ("Hajar object", "160.1", "Hajar", "Bahrain", "ICIT type TAB:I (incised tablet?), 38 mm", "gaur", "-", "ICIT", "?", "none", "object type needs checking"),
 ("Kalba seal", "5551.1", "Kalba", "UAE", "round seal", "none", "-", "ICIT", "?", "none", "single person sign W091"),
 ("Ra's al-Jinz copper seal", "935.1", "Ra's al-Jinz (RJ-2)", "Oman", "square stamp seal, copper", "bull", "Period II-III, later 3rd mill.", "Cleuziou & Tosi; ICIT", "?", "none", "text illegible"),
 ("Ra's al-Jinz sherd", "3864.1", "Ra's al-Jinz (RJ-2)", "Oman", "potsherd graffito", "none", "-", "Cleuziou & Tosi", "?", "none", ""),
 ("Ra's al-Jinz sherd", "3865.1", "Ra's al-Jinz (RJ-2)", "Oman", "potsherd graffito", "none", "Period II", "Cleuziou & Tosi", "?", "none", ""),
 ("Ra's al-Jinz sherd", "3866.1", "Ra's al-Jinz (RJ-2)", "Oman", "potsherd graffito", "none", "Period II", "Cleuziou & Tosi", "?", "none", ""),
 ("Salut ST1 soft-stone seal", "4173.1", "Salut ST1", "Oman", "square stamp seal, local soft stone", "gaur/Indian bison", "Umm an-Nar period, late 3rd mill.", "Frenez, Degli Esposti, Mery & Kenoyer 2016; Frenez 2018 chapter", "yes (Frenez/Kenoyer photos, harappa.com PDF)", "none", "made locally with Indus technique"),
 ("Salut ST1 jar impression", "4174.1", "Salut ST1", "Oman", "local jar stamped before firing", "two bison in combat (Frenez); ICIT says elephant", "late 3rd mill.", "Frenez et al. 2016 fig. 10", "yes (ResearchGate fig.)", "none", "emblem disagreement ICIT vs publication"),
 # ---------------- Indus borderland, relevant to Linear Elamite contact ----------------
 ("Miri Qalat seal MQ-11", "5442.1", "Miri Qalat", "Pakistan (Makran)", "square seal, steatite, 28 mm", "bull", "Period IV", "Besenval; CISI 3.3", "CISI 3.3", "none", "Makran route to Iran"),
 ("Miri Qalat seal MQ-12", "5444.1", "Miri Qalat", "Pakistan (Makran)", "square seal, steatite, 21 mm", "bull", "Period IV", "Besenval; CISI 3.3", "CISI 3.3", "none", ""),
 ("Sibri seal Sb-4", "5386.1", "Sibri (near Mehrgarh)", "Pakistan (Kachi plain)", "square seal 14 x 11 x 8 mm", "none", "Mehrgarh VIII, c. 2100-1900 BCE", "Santoni 1981; Jarrige et al. 1995 fig. 8.33A; CISI 3.2 pp. 103, 329; Fuls 2024 Fig. 10", "CISI 3.2", "one sign = Linear Elamite sign 2 (Fuls)", "ICIT encodes it as W095 + # (the LE-like sign not in the Indus list); same pair on Susa text O. Shape match only"),
]

FIELDS = ["object", "icit_id", "site", "region", "type", "emblem", "text_W_reading_order", "text_M_bridge",
          "n_signs", "context_date", "publication", "photo_availability", "other_writing", "notes"]
with open(ROOT / "experiments/elamite_bridge/objects.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(FIELDS)
    for (obj, iid, site, reg, typ, emb, ctx, pub, photo, other, notes) in ROWS:
        t = icit.get(iid.rstrip("?")) if iid else None
        tw = "-".join(t["seq"]) if t and iid.endswith("?") is False else ""
        if iid.endswith("?"): tw = ""
        tm = to_m(t["seq"]) if tw else ""
        n = sum(1 for s in t["seq"] if s not in ("#", "|")) if tw else ""
        w.writerow([obj, iid, site, reg, typ, emb, tw, tm, n, ctx, pub, photo, other, notes])
print("rows", len(ROWS))
