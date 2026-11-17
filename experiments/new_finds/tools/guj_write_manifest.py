"""Merge Dholavira catalogue rows with hand rows for other Gujarat files into manifest.csv.
Usage: python -I guj_write_manifest.py dholavira.jsonl out_manifest.csv"""
import csv
import json
import sys

COLS = ["file", "site", "object_id_in_source", "object_type", "field_symbol", "publication_year", "citation",
        "source_url", "n_signs_visible", "legibility", "published_transcription", "notes"]

BISHT = ("Bisht, R.S. 2015. Excavations at Dholavira (1989-90 to 2004-2005). New Delhi: Archaeological Survey "
         "of India (report dated Jan/Apr 2015)")
BURL = "https://archive.org/details/dholavirareportpreliminaryjan2015_860_K"
IAR0910 = ("Indian Archaeology 2009-10 - A Review (ASI), Khirsara excavation, J. Nath, Excavation Branch V "
           "Vadodara; see also Nath, Kumaran & Kulkarni 2012, Puratattva 42:122-132")
IARURL = "https://asi.nic.in/admin/publications/ePublicationReportsDetails/download/19"
PLOS = ("Pokharia, A.K. et al. 2017. Altered cropping pattern and cultural continuation with declined "
        "prosperity following abrupt and extreme arid event at ~4,200 yrs BP: Evidence from an Indus archaeological "
        "site Khirsara, Gujarat, western India. PLOS ONE 12(10): e0185684")
PLOSURL = "https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0185684"
SHIK = ("Bhan, K.K., V.H. Sonawane, P. Ajithprasad & S. Pratapchandran 2009. Excavations at Shikarpur, "
        "Gujarat 2008-2009 (MSU Baroda report), Fig. 4")
SHIKURL = "https://web.archive.org/web/20120921233909/http://www.harappa.com/goladhoro/Shikarpur-2008-2009.pdf"
RAO = ("Rao, R.P.N. 2018. The Indus Script and Economics: A Role for Indus Seals and Tablets in Rationing and "
       "Administration of Labor. In Walking with the Unicorn (Kenoyer felicitation vol.), Archaeopress; Fig. 7E "
       "(courtesy T. Osada). Original publication: Kharakwal, Rawat & Osada 2013, Excavations at Kanmer, BAR S2454")
RAOURL = "https://arxiv.org/abs/1812.00049"


def r(file, site, oid, otype, field, year, cit, url, n, leg, notes, tr=""):
    return dict(zip(COLS, [file, site, oid, otype, field, year, cit, url, n, leg, tr, notes]))


HAND = [
    r("dholavira_signboard.png", "Dholavira", "North Gate signboard, figs 8.3-8.4", "signboard (gypsum inlay)",
      "none", "2015", BISHT + ", figs 8.3/8.4, p.228 (printed)", BURL, 10, "good",
      "photo + drawing in one image; inlaid letters, reads directly (not mirrored); found 1990-91 and widely "
      "published since the 1990s, probably already in ICIT"),
    r("dholavira_stoneblock_photo.png", "Dholavira", "inscribed stone block, fig 8.8", "inscribed stone",
      "none", "2015", BISHT + ", fig 8.8", BURL, 3, "poor",
      "stone block from the Bailey, 16.5x8 cm, 4 letters of which 3 clear; direct inscription; same object as "
      "dholavira_stoneblock_drawing.png"),
    r("dholavira_stoneblock_drawing.png", "Dholavira", "inscribed stone block, fig 8.9", "inscribed stone",
      "none", "2015", BISHT + ", fig 8.9", BURL, 4, "fair",
      "drawing of the stone block; same object as dholavira_stoneblock_photo.png"),
    r("dholavira_tablet8099_flat.png", "Dholavira", "Acc. No. 8099", "tablet (plano-convex terracotta)",
      "seated human lifting two humans", "2015", BISHT + ", section 8.2 (tablets)", BURL, 5, "good",
      "moulded tablet, Stage IV, Lower Town; flat face only (5 signs + scene); curved face (crocodiles, "
      "bull-man combat) has no signs and is not saved; moulded, so signs read as impression"),
    r("dholavira_graffito_fig810_b.jpg", "Dholavira", "fig 8.10 (b)", "inscribed pottery (graffito)", "none",
      "2015", BISHT + ", fig 8.10, p.232 (printed)", BURL, 4, "fair", "post-firing graffito on sherd; direct"),
    r("dholavira_graffito_fig810_c.jpg", "Dholavira", "fig 8.10 (c)", "inscribed pottery (graffito)", "none",
      "2015", BISHT + ", fig 8.10, p.232 (printed)", BURL, 2, "fair", "graffito on sherd; direct"),
    r("dholavira_graffito_fig810_jar.jpg", "Dholavira", "fig 8.10 (jar)", "inscribed pottery", "none",
      "2015", BISHT + ", fig 8.10, p.232 (printed)", BURL, 1, "fair",
      "jar neck with a single incised/painted sign; may be a potter's mark rather than script"),
    r("khirsara_barseal.jpg", "Khirsara", "Fig 2H (bar seal)", "seal (bar/rectangular, no animal)", "none",
      "2017", PLOS + ", Fig 2H (via Wikimedia Commons 'Indus script recovered from Khirsara')", PLOSURL, 10,
      "good", "seal face (mirror-reversed); IAR 2009-10 says 'ten Harappan characters'; same object as "
      "khirsara_barseal_iar.png"),
    r("khirsara_barseal_iar.png", "Khirsara", "IAR 2009-10 Pl.5A (centre)", "seal (bar)", "none", "2009-10 (IAR)",
      IAR0910 + ", Pl.5A p.32", IARURL, 10, "fair",
      "seal face (mirror-reversed); same object as khirsara_barseal.jpg"),
    r("khirsara_seal_bison.jpg", "Khirsara", "Fig 2G", "seal (square)", "bison / humpless bull", "2017",
      PLOS + ", Fig 2G", PLOSURL, 5, "fair",
      "seal face (mirror-reversed); same object as the seal photo in IAR 2010-11 p.38 (not saved)"),
    r("khirsara_sealfrag_a.png", "Khirsara", "IAR 2009-10 Pl.5A (left)", "seal fragment", "none",
      "2009-10 (IAR)", IAR0910 + ", Pl.5A p.32", IARURL, 2, "poor",
      "seal face; probably the 'small broken piece of rectangular soapstone seal depicting two Harappan characters'"),
    r("khirsara_sealfrag_b.png", "Khirsara", "IAR 2009-10 Pl.5A (right)", "seal fragment", "unclear",
      "2009-10 (IAR)", IAR0910 + ", Pl.5A p.32", IARURL, 1, "poor", "seal face; broken"),
    r("khirsara_graffito_a.png", "Khirsara", "IAR 2009-10 Pl.4C (a)", "inscribed pottery (graffito)", "none",
      "2009-10 (IAR)", IAR0910 + ", Pl.4C", IARURL, 2, "fair", "graffito on sherd; direct"),
    r("khirsara_graffito_b.png", "Khirsara", "IAR 2009-10 Pl.4C (b)", "inscribed pottery (graffito)", "none",
      "2009-10 (IAR)", IAR0910 + ", Pl.4C", IARURL, 1, "poor", "graffito on sherd; direct"),
    r("khirsara_graffito_c.png", "Khirsara", "IAR 2009-10 Pl.4C (c)", "inscribed pottery (graffito)", "none",
      "2009-10 (IAR)", IAR0910 + ", Pl.4C", IARURL, 1, "poor", "graffito on sherd; direct"),
    r("shikarpur_2009_tablet_a.jpg", "Shikarpur", "Fig.4 (tablet, trench Fk13)", "tablet (terracotta, square)",
      "none", "2009", SHIK, SHIKURL, 5, "poor",
      "inscribed tablet, 4-5 signs in two lines; source image was stored vertically flipped and was corrected"),
    r("shikarpur_2009_sealing_c.jpg", "Shikarpur", "Fig.4 (sealing)", "sealing", "unclear", "2009", SHIK, SHIKURL,
      4, "fair", "impression (reads normally); three consecutive stampings of inscribed seal(s)"),
    r("shikarpur_iar2012-13_seal_rhino.png", "Shikarpur", "IAR 2012-13 Pl.32", "seal (steatite, 3x3 cm)",
      "rhinoceros", "2012-13 (IAR)",
      "Indian Archaeology 2012-13 - A Review (ASI), Shikarpur 6th season, dir. P. Ajithprasad (MSU Baroda), "
      "Pl.32 pp.36-37", "https://asi.nic.in/admin/publications/ePublicationReportsDetails/download/16", 5, "good",
      "seal face (mirror-reversed); report says 'five Harappan signs'", "count only (five signs)"),
]
for i in (1, 2, 3):
    HAND.append(r(f"kanmer_token{i}.png", "Kanmer", f"Fig 7E token {i}", "token (pierced terracotta, sealed)",
                  "unicorn", "2018", RAO, RAOURL, 4, "fair",
                  "obverse = unicorn seal impression with 2 signs (reads normally), reverse = incised signs; all "
                  "three obverses are impressions of the same seal; same objects published in Kharakwal et al. 2013"))

rows = [json.loads(l) for l in open(sys.argv[1])] + HAND
with open(sys.argv[2], "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=COLS)
    w.writeheader()
    w.writerows(rows)
print(len(rows), "rows")
