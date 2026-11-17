"""Write pak_abroad/manifest.csv: python -I pa_manifest.py"""
import csv

OUT = "experiments/new_finds/raw/pak_abroad/manifest.csv"
COLS = ["file", "site", "object_id_in_source", "object_type", "field_symbol", "publication_year",
        "citation", "source_url", "n_signs_visible", "legibility", "published_transcription", "notes"]

FRENEZ2016 = ("Frenez D., Degli Esposti M., Méry S., Kenoyer J.M. 2016. Bronze Age Salūt (ST1) and the Indus "
              "Civilization: recent discoveries and new insights on regional interaction. Proceedings of the "
              "Seminar for Arabian Studies 46: 107-124.")
FRENEZ2020 = ("Frenez D. 2020 (2nd ed.; 1st ed. 2018). The Indus Civilization Trade with the Oman Peninsula. In "
              "S. Cleuziou & M. Tosi, In the Shadow of the Ancestors (2nd ed.), Archaeopress/Ministry of Heritage "
              "and Culture Oman, pp. 385-396.")
DIDIER2017 = ("Didier A. et al. 2017. Nouvelles recherches sur les débuts de la Civilisation de l'Indus "
              "(2500-1900 av. n. è.) au Pakistan. Les fouilles de Chanhu-daro (Sindh). Comptes rendus de "
              "l'Académie des Inscriptions et Belles-Lettres 161(2): 947-980.")
LAURSEN2010 = ("Laursen S.T. 2010. The westward transmission of Indus Valley sealing technology: origin and "
               "development of the 'Gulf Type' seal and other administrative technologies in Early Dilmun, "
               "c.2100-2000 BC. Arabian Archaeology and Epigraphy 21: 96-134. doi:10.1111/j.1600-0471.2010.00329.x")
JALAL = ("Vidale M., Desset F., Frenez D. 2021. The Jalalabad Seal, A Reappraisal. Journal of Archaeological "
         "Studies (Tehran) 12(4): 283-297.")
JALAL_URL = "https://jarcs.ut.ac.ir/article_81265_f85f962ddf0a7a91b4da2c938352e375.pdf"
LAURSEN_URL = "https://doi.org/10.1111/j.1600-0471.2010.00329.x (PDF via harappa.com, Wayback copy)"

rows = [
    ["ganweriwala_twistedtablet_gulzar.png", "Ganweriwala (Cholistan, Pakistan)", "Mound 1a surface find, Fig. 5",
     "tablet", "none (twisted/triangular clay tablet)", "2023",
     "Gulzar S. 2023. Harappan Cities: Landscape and Surface Survey at Ganweriwala (EASAA paper), Fig. 5. First "
     "announced in Gulzar S. & Parpola A. 2016, New Indus Civilization inscription found, Current World Archaeology 77: 7.",
     "https://easaa.org/wp-content/uploads/2023/01/Sidra-Gulzar-3.pdf", "7", "fair", "",
     "Object itself (molded tablet, signs in relief/incised). New surface find c.2015; authors say 7 signs. Not in CISI."],
    ["ganweriwala_yogitablet_masih.jpg", "Ganweriwala (Cholistan, Pakistan)", "Fig. 4 (Masih tablet)",
     "tablet", "seated yogi-like figure with kneeling figure (other face)", "2018",
     "Masih F. 2018. Ganweriwala - A new Perspective. In D. Frenez, G. Jamison, R. Law, M. Vidale, R. Meadow (eds), "
     "Walking with the Unicorn (Archaeopress), pp. 381ff. Image reproduced in harappa.com blog 'Glimpses of Ganweriwala'.",
     "https://www.harappa.com/blog/glimpses-ganweriwala", "3", "fair", "",
     "Photo and drawing of both faces; script on reverse. Surface collection, new; not in CISI."],
    ["salut_seal_st1_frenez2016fig9.png", "Salut ST1 (Oman)", "ST1 SU53 stamp seal, Fig. 9",
     "seal: square", "Indian bison (gaur) with lowered head before manger-like object", "2016",
     FRENEZ2016 + " Fig. 9.", "https://zenodo.org/records/5514184", "5", "good", "",
     "Seal face photo (mirror-reversed) plus authors' drawing. Chlorite, local manufacture in Indus style. New find "
     "(excavated 2010s)."],
    ["salut_seal_st1_harappacom.jpg", "Salut ST1 (Oman)", "ST1 stamp seal (harappa.com)",
     "seal: square", "Indian bison (gaur) before manger-like object", "2016",
     FRENEZ2016 + " Photo reproduced on harappa.com blog 'New Indus finds from Salut, Oman'.",
     "https://www.harappa.com/blog/new-indus-finds-salut-oman", "5", "good", "",
     "SAME OBJECT as salut_seal_st1_frenez2016fig9.png; photo of all sides incl. seal face (mirror-reversed)."],
    ["salut_stampedsherd_st1.png", "Salut ST1 (Oman)", "stamped jar sherd, Fig. 10",
     "other", "two bisons in combat (impression of elongated tablet/seal)", "2016",
     FRENEZ2016 + " Fig. 10. Also Frenez 2020 (OCNUS 27) Fig. 19, compared with M-1367.",
     "https://zenodo.org/records/5514184", "3?", "poor", "",
     "Impression (reads correctly, not reversed) stamped before firing on local Umm an-Nar jar. New find."],
    ["rasaljinz_RJ2_sherd_graffito_b2r18.png", "Ras al-Jinz RJ-2 (Oman)", "Building II Room 18, Period II; Fig. 35.2b",
     "pottery graffito", "none", "2018",
     FRENEZ2020 + " Fig. 35.2b.", "https://zenodo.org/records/5513716", "3", "fair", "",
     "Signs incised on black-slipped Indus jar. RJ-2 excavations published earlier (Cleuziou & Tosi 2000); check ICIT "
     "before treating as new."],
    ["bisyah_seal_omannm.png", "Bisyah (Oman), Oman National Museum", "Fig. 35.14c",
     "seal: square", "humped zebu", "2018",
     FRENEZ2020 + " Fig. 35.14c.", "https://zenodo.org/records/5513716", "3?", "fair", "",
     "Seal face (mirror-reversed). Authors call the marks 'enigmatic objects/signs'; may not be Indus script."],
    ["hajjar_prismseal_bahrain.png", "Hajjar (Bahrain)", "three-sided prismatic seal, Fig. 35.15 right",
     "seal: square", "goats and Indian bison on other faces", "2018",
     FRENEZ2020 + " Fig. 35.15.", "https://zenodo.org/records/5513716", "3", "good", "",
     "Seal face(s) (mirror-reversed). Previously published (Bahrain excavations, probably 1990s); probably known."],
    ["jalalabad_cylinder_NMI2698.png", "Jalalabad (Fars, Iran), National Museum of Iran", "NMI 2698, Fig. 1",
     "seal: cylinder", "none visible besides signs", "2021",
     JALAL + " Fig. 1.", JALAL_URL, "4", "fair",
     "Right to left: 1 effaced, possibly 'fringed V' Parpola 311/Wells 740; 2 Parpola 148/Wells 32; 3 variant of "
     "Parpola 13/Wells 90 'man' (or ligature like P33/W142 or P41/W111); last possibly P42/W112 or variant of "
     "P31/W145, or P13 + P130",
     "Cylinder plus modern impression. Previously known object (Chakrabarti & Moghadam 1977; Ascalone 2003); "
     "reappraisal reading new."],
    ["jalalabad_cylinder_NMI2698_signs_drawing.png", "Jalalabad (Fars, Iran), National Museum of Iran", "NMI 2698, Fig. 3",
     "seal: cylinder", "", "2021", JALAL + " Fig. 3.", JALAL_URL, "4", "fair", "(see previous row)",
     "SAME OBJECT as jalalabad_cylinder_NMI2698.png; authors' drawing of signs with alternatives."],
    ["gonur_elephantseal.png", "Gonur Depe North (Turkmenistan)", "'temple of the water' seal (Nov 2004)",
     "seal: square", "standing Asian elephant", "2009",
     "Parpola A. 2009 (dated 2006). A New Indus Seal Excavated at Gonur (Turkmenistan) in November 2004. In T. Osada "
     "(ed.), Linguistics, Archaeology and the Human Past in South Asia, pp. 71-76; Sarianidi 2005: 258, fig. 114; "
     "described in Frenez 2018, ARA 15: 13-33. Photo from Dubova 2019 (Margiana Archaeological Expedition) via harappa.com.",
     "https://www.harappa.com/content/gonur-depe-city-kings-and-gods-and-capital-margush-country-modern-turkmenistan",
     "8", "good", "", "Seal face photo (mirror-reversed). Found 2004, after CISI/ICIT coverage likely incomplete; verify."],
    ["umma_sealing_ashmolean.jpg", "Umma/Jokha (Iraq), Ashmolean", "Ashmolean sealing (donated 1931)",
     "sealing", "bull and manger", "2019?",
     "harappa.com blog 'An Indus seal impression from Umma, Mesopotamia' (Ashmolean Museum object).",
     "https://www.harappa.com/blog/indus-seal-impression-umma-mesopotamia", "6", "good", "",
     "Impression (reads correctly). PREVIOUSLY KNOWN object (in Louvre before WWI); likely in older corpora; keep "
     "only as a check."],
    ["chanhudaro_seal_sq_trench2_2016-18.png", "Chanhu-daro (Sindh, Pakistan)", "Trench 2 seal, Fig. 10b",
     "seal: square", "animal (unclear, small image)", "2017",
     DIDIER2017 + " Fig. 10b. HAL halshs-02978545.", "https://shs.hal.science/halshs-02978545/document",
     "4?", "poor", "", "Seal face (mirror-reversed). New find, French mission (MAFBI) 2016-18. Image small."],
    ["chanhudaro_sealfrag_trench2_2016-18.png", "Chanhu-daro (Sindh, Pakistan)", "Trench 2 seal fragment, Fig. 10",
     "seal: square", "broken; partly lost", "2017",
     DIDIER2017 + " Fig. 10. HAL halshs-02978545.", "https://shs.hal.science/halshs-02978545/document",
     "2?", "poor", "", "Seal face fragment (mirror-reversed). New find, MAFBI 2016-18."],
    ["janabiyah_gulfseal_laursen10.png", "Janabiyah mound cemetery (Bahrain)", "Laursen Table 1 no. 10, Fig. 1a",
     "seal: round Gulf", "none (script only)", "2010",
     LAURSEN2010 + " Fig. 1a.", LAURSEN_URL, "6", "good",
     "Parpola, tentative, right to left on impression: (1) either very uncertain 53, or an unidentified sign (possibly "
     "badly drawn 'fish', 60) followed by 147, (2) 364, (3) 145, (4) either very uncertain 126 ... or very uncertain "
     "125 ± very uncertain 128, (5) uncertain 16, (6) 145",
     "Seal plus impression plus drawing. Bahrain National Museum excavation 1999/2005; first published here."],
    ["karzakkan_gulfseal_laursen11.png", "Karzakkan (Bahrain)", "Laursen Table 1 no. 11, Fig. 1b",
     "seal: round Gulf", "none (script only)", "2010",
     LAURSEN2010 + " Fig. 1b.", LAURSEN_URL, "4", "good", "",
     "Seal plus impression. BNM excavation 1999/2005; first published here."],
    ["karzakkan_gulfseal_laursen56.png", "Karzakkan (Bahrain)", "Laursen Table 1 no. 56, Fig. 1c",
     "seal: round Gulf", "", "2010",
     LAURSEN2010 + " Fig. 1c.", LAURSEN_URL, "2", "fair", "",
     "Excavated 1983-84; previously published Al-Sindi 1999 no. 160 (previously known)."],
]

with open(OUT, "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(COLS)
    for r in rows:
        assert len(r) == len(COLS), r[0]
        w.writerow(r)
print(len(rows), "rows ->", OUT)
