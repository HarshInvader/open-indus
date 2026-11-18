# Source sweep results (2026-11-17)

## Anchor candidates
**None found.** No object turned up with Indus signs plus a readable second script or personal name. Of the sources read, only the Desset chapter and the CISI 3.3 front matter deal with another script (Linear Elamite at Shahdad and Konar Sandal), and those objects carry no Indus signs.

## Conclusion
- **Job A:** the frozen bangle_oval test cannot be run. There is **1 confirmed inscribed bangle text not in ICIT** (Mohenjo-daro DK-M 83-615, three strokes) and 3 unsure ones (a Dholavira graffito that cannot be read from the publication, and two unnamed Kenoyer 2021 figures, probably ICIT duplicates). The test needs **19**. The prereg's minimum for any test is n >= 10, and that is not reached either.
- Diameters were recovered from Franke 1984 for **19 bangles** (18 with outer and inner, 1 with outer only). 18 of these are ICIT discovery-set bangles and 1 is the new 83-615.
- **Job B: 0 truly new inscribed objects confirmed.** Every inscribed Gulf/Iran/Central Asia object in the sources read is already in ICIT or the repo lists. The new Gulf objects (the Kalba 2023 Gulf-type seal, the Dahwa silver ring, the Al-Moyassar prism) carry no signs. The open leads are below.

## Job A: inscribed bangles (bangles_found.csv, 23 rows)
**Target citation:** I could not get Franke-Vogt, U. 1992, "Inscribed bangles: an inquiry into their relevance", in C. Jarrige (ed.), *South Asian Archaeology 1989*, Madison: Prehistory Press. It is not online in open form; the volume is confirmed but I found no scan. The catalogue with the measurements is the 1984 paper:

> Franke, U. 1984. "A selection of inscribed objects recovered from Mohenjo-Daro." In M. Jansen & G. Urban (eds), *Interim Reports Vol. 1: Reports on Field Work carried out at Mohenjo-Daro, Pakistan 1982-83*, Aachen/Rome: RWTH Aachen & IsMEO, pp. 117-138. Bangle catalogue 5.2.1-5.2.20 on pp. 123-125 (PDF pp. 126-128); drawings in Figs. IV-VI, pp. 134-136; plates 8-12. File: raw/halim_vidale/74331.pdf (https://ignca.gov.in/Asi_data/74331.pdf).

Every measurement was read off the page images, not the OCR. The OCR misreads 618 as "28,4"; the scan has Ø 8,4 cm.

- **20 inscribed fragments** (19 stoneware, 1 shell). 19 match ICIT BNGL rows (M-1628..M-1647) by excavation number. **DK-M 83-615 is not in ICIT** under any type. Its entry reads Ø 8,0 / 5,5 cm, "inscription consisting of three strokes", drawn in Fig. IV,4. Whether a lone stroke-numeral counts as a "readable sign" under the prereg is a scoring decision I have not made.
- **Diameter-order reversal:** footnote 26, attached to the first entry, says "Inner/outer diameter". Every entry, though, puts the larger value first (612: "Ø 9,0 cm / 5,1 cm"), and footnote 18 gives outer 8.0-9.2 cm and inner 4.9-5.9 cm. **So the entries are outer/inner and the note is backwards.** The CSV records them that way.
- Inner diameters (mm): 49-60, most of them 50-56. 619 has no inner value; the shell bangle 83-150 has no diameter at all.
- **Places where ICIT and Franke disagree** (flagged, not interpreted):
  - HR-E 83-621 (M-1628): Franke has 1 very faint sign; ICIT 3822.1 has 3 signs, the same sequence as ICIT 3832.1 (W-S 83-628).
  - W-S 83-628: Franke has 2 signs on one side and 3 strokes on the other; ICIT has 3 signs and 1 sign.
  - MN-S 83-626: Franke has 3 signs; ICIT has 2.
  - HR-E 83-622: the entry says 3 signs survive, but Franke's own fn. 12 lists it under 2 signs.
  - All of these need a check against the CISI 2 photographs.
- Franke fn. 11 cites 7 bangle fragments from Harappa (Vats 1940: 448-449, pl. CXXXVIII 1, 4, 7, 8) and 6 from Sutkagen-dor (Stein 1931: 64, pl. VI 32-33). These are **stoneware bangles in general, not inscribed ones.** The local Vats OCR (experiments/old_registers/raw/in.ernet.dli.2015.537391) describes nos. 1, 4, 7, 8, 1573, 3114 and 11538 with no inscription. Not candidates.
- Dholavira (Bisht 2015, pp. 231-232, fig. 8.10): one stoneware bangle fragment is described as carrying graffiti; the signs cannot be read in the photo. The report's list of 91 stoneware bangles has diameters but no inscription column, so this bangle's diameter cannot be identified. Not in ICIT BNGL.
- Vidale 1990 (Ceramics and Civilization 5; raw/chemical_bangles/77275.pdf = raw/harappa/stoneware_bangles.pdf) only illustrates the Franke-era Mohenjo-daro bangles. Nothing new.
- **Where the missing 18+ texts might be** (none of it accessible in open form now): Franke-Vogt 1992; the Aachen/IsMEO 1984-87 surface collections ("5 more found in 1984", fn. 11; ICIT already has eight 84-/85- rows); HARP bangle records (Kenoyer & Meadow 2010 in CISI 3.1, already in ICIT); CISI 3.4 (Dholavira, Gulf; not yet published).

## Job B: objects (objects_found.csv, 19 rows)
**Desset 2022 in CISI 3.3** (raw/cisi33/, from orbi.uliege.be): the 40-page file is the **front matter of CISI 3.3** (*Indo-Iranian Borderlands*, Parpola & Koskikallio eds., Helsinki 2022). It contains the contents, the preface and Desset's essay "Bronze Age Writing in South-Eastern Iran (ca. 3300-1880 BCE)", pp. xix-xxvi. The catalogue photographs are not in it.
- **What Desset covers:**
  - Proto-Elamite tablets from Tepe Yahya (TY-8..34) and Shahr-i Sokhta (SiS-1).
  - Linear Elamite inscriptions from Shahdad (S = Shd-1, on a vessel) and Konar Sandal (B′, C′, D′, E′ = KSS-382, 383, 381, 380), plus the "geometric" sign system on those tablets.
  - Unprovenanced Linear Elamite seals V (Persian Gulf related) and G′ (Central Asian gold seal).
  - Eastern variants on metal vessels (W, A′, M′, N′, O′).
- **What Desset does not cover:** Indus-sign objects. He mentions the Indus script only in the concluding paragraph, where it disappears around 1850 BCE. **No object in the chapter carries both Indus signs and Linear Elamite or any other script.**
- **The preface** (Parpola) names the Indus-type finds: Altyn-depe Alt-49 and Alt-90, the Gonur elephant seal (deferred to CISI 3.4), the TY-106 Indus seal impression, and Shortughai. It also says the Gulf and the Pakistani borderlands (Makran, Gomal) are moved to CISI 3.4.
- **Checked and already covered:** Salut seal and stamped jar; Ras al-Jinz copper seal and jar graffiti; Hajjar seal; Bisyah seal; TY-106; Gonur; Alt-90 (all in ICIT, foreign_corpus, elamite_bridge or new_finds).
- **Checked and not inscribed:**
  - Kalba 2023 Gulf-type seal KAL23/709/3/1 (Schwall et al. 2024, IASA Bulletin 32: 19-21, and Antiquity 2024). Bull and lion, no signs. It is a different object from the ICIT Kalba seal 5551.1.
  - Dahwa silver seal-ring (Oman MHT 2022). Bison only.
  - Al-Moyassar prism seal. Animals only.
  - Lakhan-jo-daro 2017 season (Sindh "The Change" report 2022, pp. 275-276). A motif seal; no signs visible.
- **Open leads (unsure, not counted as new):**
  - Alt-49 (ICIT has only 1 Altyn-depe row).
  - The Umm an-Nar black-slipped jar graffiti listed in Méry 2000 tab. 59 and later papers.
  - The Umm al-Quwain seal, 2026 (press report only).
  - The Rakhigarhi 2023 seal (secondary mention only).
- Rakhigarhi PDF (raw/rakhigarhi/1495696569.pdf): a general site article. It mentions 3 CISI seals; nothing new.

## Blocked or failed URLs (evidence/requests.jsonl)
| URL | status |
|---|---|
| https://repository.si.edu/items/a9c30a34-8dd1-470d-998a-1c44f50208e1/full (Blackman & Vidale 1992) | 403 |
| https://repository.si.edu/bitstreams/64271be1-5d78-4196-8a87-f1ea1669c777/download | 403 |
| https://www.harappa.com/sites/default/files/pdf/580-Article%20Text-993-1-10-20220407.pdf | 404 |
| https://crr.gos.pk/wp-content/uploads/2024/11/BIBLIOGRAPHY-ON-INDUS-VALLEY-CIVILIZATION.pdf | DNS failure |
| https://www.tnarch.gov.in/sites/default/files/IVC_PROCEEDINGS_RMRL.pdf | timeout |
| Franke-Vogt 1992 (SAA 1989) | no open copy found |

harappa.com PDFs did load this time: The_Indus_Civilization_Trade_with_the_Om.pdf and stoneware_bangles.pdf both returned 200.
