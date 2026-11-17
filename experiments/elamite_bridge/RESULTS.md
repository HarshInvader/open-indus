# Linear Elamite as a bridge to the Indus script?

elamite_bridge agent, 2026-11-15. Code: `eb_core.py`, `eb_calibrate.py`, `eb_test.py`, `build_objects.py` (run from the repo root with `.venv/bin/python`). Pre-registration: `docs/prereg/elamite_bridge.md` (hashes in `docs/prereg/HASHES.txt`, frozen before any Indus test). Outputs: `calibration.json`, `test_results.json`, `eb_test.log`, `objects.csv`, `results.json`. Downloads: `raw/fuls2024_ijas/` (PDF and extracted text, untrusted).

## Conclusion first

1. **Linear Elamite opens no route to an Indus anchor today.** No object carries Indus signs and a readable Linear Elamite (or cuneiform) text together. No Linear Elamite or Old Elamite text names Meluhha, an Indus person, or an Indus good.
2. **Linear Elamite sound values do not carry over to look-alike Indus signs.** This was pre-registered as H4. Fuls's 2024 look-alike key, using Desset's values, gives 1 Indus sign pair that is also an attested Linear Elamite syllable pair. Keys with the same values shuffled give 3.4 ± 2.5 (p = 0.90). That repeats paragorth's earlier fail (2 vs 4.1, P = 0.83) with independent code. Only 24 Indus pair tokens are covered at all, mostly by two-stroke and bracket signs.
3. **Do the look-alikes behave like syllables? Borderline, and not supported.** This was pre-registered as H1. I first checked that a neighbour-diversity measure separates syllabograms from logograms in Linear B at Indus size (AUC 0.91), so the measure works.
   - The 10 complex Indus look-alikes do sit slightly above frequency-matched random signs: mean residual +0.13, AUC 0.67, raw p = 0.049.
   - That p fails the pre-registered Holm correction (p = 0.099).
   - M77 points the same way but is not significant (7 bridged signs, p = 0.14).
   - Read it as "not excluded", not as evidence of borrowing.
4. **The single most useful fact for the project is functional, not phonetic.** The Linear Elamite Gulf seal LEI 22 (Ligabue Collection) has the Indus-seal layout, a bull under a text band, and its text band reads *za-ši-ri₂* "Zaširi", a personal name. It confirms that the text slot of this seal type held an owner's name. paragorth §6 and §10 already used this; I confirm the reading from the Liège database. It is not a bilingual: it carries no Indus signs.
5. **The only mixed object is Susa "text O"** (Louvre Sb 9382), a red clay tablet. It has about 20 Indus-like and about 3 Linear Elamite-like graphemes, plus the sign pair of the Sibri seal Sb-4. It is eroded, undated and excluded from the Linear Elamite corpus. It has no parallel text, so it cannot fix values. It is still the one object worth imaging well (RTI).

## 1. State of Linear Elamite (published facts vs claims)

- **Decipherment.** Desset, Tabibzadeh, Kervran, Basello & Marchesi 2022, *ZA* 112(1): 11–60, doi:10.1515/za-2022-0003.
  - Their reading has 72 phonographic signs (5 vowels, 12 consonants, 60 CV signs), no logograms, and an inventory of 348 glyphs that groups into 80–110 graphemes.
  - It is anchored on royal names that also appear in cuneiform: Puzur-Šušinak, Insušinak and Šušen from the bigraphic *Table au Lion* (Bork 1905); Šilhaha, Eparti and Napiriša on the silver *kunanki* vessels.
  - Fuls (2024) reports the team's claim that about 96% of the texts are readable, but many words are not understood. The team compares the situation to Etruscan.
- **Corpus.**
  - The HLED database (Liège) has 45 documents and about 2,100–2,300 syllable tokens (local copy: `sources/paragorth_Indus-/data/derived/linear-elamite-corpus-hled.json`).
  - Fuls 2024, using OCLEI, counts 39 artefacts, 141 lines and 1,491 readable signs. Each of the 265 sign variants occurs on average only 5.6 times.
  - Edition: Desset, Tabibzadeh, Basello & Marchesi 2026, *Linear Elamite Inscriptions and Related Cuneiform Texts I: Linear Elamite Texts from Susa* (OrientLab Series Maior 10, Bologna: Ante Quem). Vol. II (Fars, Kerman and other texts) is cited by HLED as 2026. Vol. III will hold the Old Elamite cuneiform royal inscriptions.
- **How secure is it?**
  - Secure: the name-based values (about 12 signs before 2018, plus the dynastic names). The language is Elamite.
  - Contested:
    - **Jacob Dahl (Oxford)** says the claim of a *purely* syllabic script is "certainly not correct" (National Geographic). In Dahl 2023, *Akkadica* 144(2): 107–126, he argues that Linear Elamite was invented around Puzur-Šušinak's time partly from recovered Proto-Elamite tablets ("schismogenesis"), not evolved continuously from Proto-Elamite. He points to the "unusual content" of texts O and M and to inconsistent sign forms. In Dahl 2009, *Iran* 47: 23–31, he called it a limited-use system with few practitioners.
    - **Mäder (Bern)** estimates that only about 70% of signs are purely phonographic (Mäder 2021).
    - The key texts are **unprovenanced silver vessels** (London private collection, surfaced in 2004).
    - The **Konar Sandal tablets** are suspected forgeries (Lawler 2007, *Science* 317: 588–589), and Dahl objected to their use.
  - Supporters cited: Krebernik, Stolper, Steinkeller.
  - I found no formal, peer-reviewed refutation of the sign values.
- **Is it contemporary with the Mature Harappan period (2600–1900 BCE)?**
  - Securely dated texts: Susa under Puzur-Šušinak (about 2150–2100 BCE) and the Sukkalmah kunanki vessels (about 1970–1880 BCE). The "possibly pre-Old Akkadian" Susa cones and tablets are not securely dated.
  - **Shahdad LEI 19** (text S, Iran National Museum 8527, *ti-n-ra-X-r*): the lead-cosmetic sample from Grave 30 gave 2923–2667 cal BC. Eskandari, Nokandeh, Vidale & Marchesi 2025, *ZA* 115(2): 123–136, doi:10.1515/za-2025-0012, argue from this for centuries of Early Bronze Age use. The caveats are real: the date falls on an unfavourable part of the calibration curve, Grave 338 gives 2500–2300, and the sample dates the cosmetic, not the inscription.
  - **Konar Sandal tablets LEI 28–31:** "end of 3rd millennium", authenticity disputed.
  - So the overlap with the Mature Harappan period is real but thin: a handful of short texts from Kerman and Susa (names such as *Zulari*, *Pa(a)reri*, *Tinra…r*). **None of them is on an object with Indus signs.**

## 2. Meluhha, Indus goods or Indus names in Elamite sources

- **Linear Elamite:** none. A search of all 45 HLED transliterations for Meluhha-, Magan-, Dilmun- or Marhaši-like strings gave 0 hits. The content is royal titulary, divine names, dedications, and personal names on seals and tablets.
- **Old Elamite cuneiform:** I found no published Elamite-language mention of Meluhha. Meluhha in Susa comes from **Akkadian** texts:
  - Old Akkadian MDP 14 tablets with Meluhha and boat rations. This is from the meluhha catalogue (`experiments/meluhha/catalogue.csv`); I did not re-verify it, because CDLI search returned HTTP 500.
  - The Šu-ilišu "interpreter of Meluhha" seal (Louvre AO 22310). Its Susa provenance is "said to be".
  - Sukkalmah-period Susa documents are mostly in Akkadian.
- **Foreign names that could be Indus:** only the Eastern Linear Elamite names (*Zaširi* on the Gulf seal, the Konar Sandal and Shahdad names, *ra~haši-zana-niri* on the "Central Asian" gold seal). None is tied to an Indus-inscribed object, and none is said to be non-Elamite in the sources.

## 3. Indus-inscribed objects in Iran, Central Asia and the Gulf (`objects.csv`, 34 rows)

`objects.csv` lists each object with its ICIT id, reading-order Wells text, Mahadevan text (only when the bridge maps every sign one-to-one; the bridge covers 176 signs, so most rows are blank), context and date, publication, photo availability, and any other writing. Mesopotamian finds are already in `experiments/meluhha/foreign_objects.csv` and are not repeated here.

| region | Indus-inscribed objects (ICIT) | other writing on the same object |
|---|---|---|
| Iran | Susa round seal 3881; Susa cylinder Sb 2425 = 3882 (Louvre: Indus-made, steatite, Suse IVB 2400–2100, photo online); Tepe Yahya sherd 3886 (IVA/IVB); "Luristan" round seal 2153 (unprovenanced) | **none** |
| Iran, mixed | Susa text O (Sb 9382): Indus-like plus Linear Elamite-like graphemes, unreadable | not a parallel text |
| Iran, no Indus text | Konar Sandal marble cylinder (Indus iconography, uninscribed) and bronze gharial stamp; Konar Sandal Linear Elamite tablets; Shahdad Linear Elamite vessel | Linear Elamite only |
| Central Asia | Altyn Depe Alt-90 = 16 (W415-W390, priest's tomb, Namazga V); Gonur elephant seal = 4155 (8 signs, ends in the jar); Shortughai rhino seal = 3874 (an Indus outpost) | **none** |
| Central Asia, claimed | Gonur potsherd "Linear Elamite" (Klochkov 1998; surface find; Desset doubtful); gold seal LEI 33 (unprovenanced, Linear Elamite) | no Indus signs |
| Gulf | Failaka 147, 148; Bahrain 3863, 5227–5230, 5232; Hajar 160; Kalba 5551; Ra's al-Jinz 935, 3864–3866; Salut 4173, 4174 | **none** |
| Gulf, Linear Elamite | LEI 22 Zaširi seal (Indus layout) | Linear Elamite only, no Indus signs |
| Indus borderland | Sibri Sb-4 = 5386 (W095 + a sign Fuls identifies with Linear Elamite sign 2; ICIT records it as illegible); Miri Qalat 5442, 5444 | shape match only |

**Verdict:** across all three regions there is no bilingual or digraphic object. Every Indus-inscribed object abroad carries Indus signs only. Every Linear Elamite object in the contact zone carries Linear Elamite only.

Two discrepancies to note:
- For Salut 4174, ICIT says the emblem is an elephant; Frenez et al. 2016 describe two bison.
- The Susa round seal's Louvre number is unconfirmed (possibly Sb 5614).

## 4. Structural comparison and the pre-registered tests

### Published comparison
Fuls 2024 (*IJAS* 14(1): 3–16, doi:10.22111/IJAS.2024.48980.1305) concludes the two scripts are "not directly related". They share methods of modifying signs (marking, insertion, attachment, hatching, reduplication, enclosing) and right-to-left reading. But Linear Elamite is syllabic and Indus logo-syllabic.
- His Fig. 9 pairs 21 Indus signs with Linear Elamite signs, and he flags 6 of them as "graphic universals".
- He warns that comparing two lists of several hundred signs inflates chance matches, and cites Dahl's warning against arguing from standardised forms.
- He suggests any influence ran from Indus to Linear Elamite, because Indus writing is older.

Other comparisons:
- Hunter 1934 and Gelb 1963 proposed a common source.
- The Zenodo preprint by S. Dunn (2026) claims more than 10 one-to-one matches and a "Sanskrit sister language". It is not peer-reviewed and uses its own values, not Desset's, so it was not tested.

I checked that Fuls's sign numbers are ICIT/Wells numbers: W853 is initial in 10 of 11 ICIT occurrences, exactly as he states.

### Calibration (planted known answer, `calibration.json`)
The metric D is the neighbour diversity of a sign: log of its distinct left and right neighbours, minus the value expected from its frequency. I ran it on Indus-length chunks at the ICIT token count (13,190):

| reference | phonetic vs logographic AUC (5–95%) | power: 12 true phonetic signs vs frequency-matched random sets |
|---|---|---|
| Linear B (DAMOS): syllabograms vs ideograms | 0.91 (0.89–0.94) | 0.73 |
| Egyptian (TLA): 26 uniliterals vs all other signs | 0.67 (0.63–0.71) | 0.73 |

### Tests (Holm across the two confirmatory tests)

| id | hypothesis | result | verdict |
|---|---|---|---|
| H1 | The 10 complex look-alikes (W455, 371, 360, 440, 400, 335, 615, 794, 831, 482) have higher D than frequency-matched signs (ICIT, distinct texts) | mean D +0.128 vs 0; AUC 0.67; p = 0.049, Holm 0.099 | **not supported** (borderline) |
| H2 | All 14 look-alikes with 10+ tokens (descriptive) | +0.116; AUC 0.66; p = 0.035 | descriptive only |
| H3 | M77 replication of H1 (7 bridged signs: M127, M135, M176, M192, M233, M245, M379) | +0.107; AUC 0.61; p = 0.14 | same direction, not significant |
| H4 | Desset values on Fuls's look-alikes reproduce Linear Elamite syllable pairs | 1 attested vs 3.40 ± 2.52; p = 0.90 | **refuted at this power** |

Per-sign D for H1: W440 +0.41, W455 +0.34, W615 +0.32, W831 +0.26, W371 +0.22, W794 +0.17, W360 +0.15, W482 −0.09, W400 −0.23, W335 −0.26.

**Caveats:**
- High neighbour diversity can also come from logograms in an open "noun" slot. A positive H1 would not have shown syllabic use in Indus.
- The look-alikes were chosen by one author, from standardised sign forms.
- Power is about 0.7 for a 12-sign set; with 10 signs it is lower.
- H4 covers only 24 pair tokens. It cannot detect a few borrowed values; it can only show that the key as a whole carries no signal.

Tests counted: 2 confirmatory, 2 descriptive, 2 calibration. The Linear Elamite toponym search is a lookup, not a test.

## 5. What would change this: concrete leads

1. **Image Susa text O (Louvre Sb 9382) with RTI or photogrammetry, both faces.**
   - The only published drawing is Fuls's. A better image would show whether the "Indus" graphemes are Indus signs in Indus order (the W853 initial; the 220+33 pair).
   - Contacts: the Louvre Département des Antiquités orientales; Andreas Fuls (TU Berlin); François Desset (CNRS / Liège), who excluded it from the corpus and can say why.
2. **Ask Desset et al. whether any Linear Elamite object from Konar Sandal, Shahdad or the Gulf carries Indus signs or Indus-style seal impressions.**
   - Vol. II of the corpus (2026, Fars and Kerman) is the place it would appear. It is not online. A library or purchase copy is needed.
   - Ask too about the "unpublished seal with a Linear Elamite inscription said to be from Bahrain" (Glassner, cited in Laursen 2010, n. 4). A Gulf seal in Linear Elamite from an excavated Bahrain context would sit beside the Indus-inscribed Gulf seals of the same workshops.
3. **Konar Sandal sealings.** A "door sealing" impression from Konar Sandal is mentioned alongside Nindowari and Lakhan-jo-daro (ResearchGate snippet, unverified). Ask Massimo Vidale (Padua) or Holly Pittman (Penn, Konar Sandal glyptic) whether any Konar Sandal sealing carries Indus signs. That would be an Indus text at a site that also has Linear Elamite.
4. **Sibri Sb-4 (CISI 3.2, pp. 103 and 329).** Check the photo for whether the non-Indus sign really is Linear Elamite sign 2.
5. **Do not pursue graphic look-alike keys further.** Two independent implementations fail, and Linear Elamite's own values rest on royal names that have no Indus counterpart.

## Sources and key passages

- Desset, F., Tabibzadeh, K., Kervran, M., Basello, G. P. & Marchesi, G. 2022. The Decipherment of Linear Elamite Writing. *Zeitschrift für Assyriologie* 112(1): 11–60. doi:10.1515/za-2022-0003. Open PDF: cris.unibo.it/bitstream/11585/890284/1/Marchesi et al 2022_Linear Elamite.pdf. "72 phonographic signs", "between 80 and 110 graphemes", inventory of 348 glyphs (via Wikipedia's citation of pp. 19–23 and 34–35).
- Fuls, A. 2024. Comparison of Linear Elamite and Indus Writing Systems. *Iranian Journal of Archaeological Studies* 14(1): 3–16. doi:10.22111/IJAS.2024.48980.1305. https://ijas.usb.ac.ir/article_8463.html (PDF in `raw/fuls2024_ijas/`).
  - "They are, as far as we can tell, not directly related to each other."
  - "the comparison is made between lists of several hundred signs, which increases the probability of an accidental coincidence."
  - On text O: "There are 20 graphemes on text O resembling Indus signs. Most interesting is Indus sign 853 used in initial text position in ten out of eleven Indus texts… I am a long way from seeing Text O as an original Indus text".
  - "text O represents an extraordinary mixture of a sign pair from Sibri (Mehrgarh), Linear Elamite and Indus signs dating from the beginning of the 2nd millennium BCE".
  - "no LE inscription was found at any Indus site… LE seems to have been a regionally restricted writing system".
- Dahl, J. L. 2023. Proto-Elamite and Linear Elamite, a Misunderstood Relationship? *Akkadica* 144(2): 107–126. ORA: ora.ox.ac.uk/objects/uuid:51adb1c2-61de-438c-9b29-125addf3d2a1. Quoted via Fuls: "linear Elamite had a point of invention, and that it was based partially on recovered proto-Elamite texts… the result of schismogenesis". Not read directly.
- Dahl, J. L. 2009. *Iran* 47: 23–31 (limited-use system; possible pseudo-glyphs). Via Wikipedia.
- Mäder, M. 2021. Linear Elamite. In *The Encyclopedia of Ancient History: Asia and Africa*. doi:10.1002/9781119399919.eahaa00064. Gives the estimate that about 70% of signs are phonographic.
- Eskandari, N., Nokandeh, J., Vidale, M. & Marchesi, G. 2025. New Radiocarbon Evidence from Shahdad and the Earliest Datable Linear Elamite Text. *ZA* 115(2): 123–136. doi:10.1515/za-2025-0012. The Grave 30 cosmetic gave 2923–2667 cal BC, and Grave 338 gave 2500–2300 (from Wikipedia's summary; the full text was 403 at academia.edu).
- Desset, F. 2014. A New Writing System Discovered in 3rd Millennium BCE Iran: The Konar Sandal 'Geometric' Tablets. *Iranica Antiqua* 49: 83–109. doi:10.2143/IA.49.0.3009239.
- Desset, F., Tabibzadeh, K., Basello, G. P. & Marchesi, G. 2026. *Linear Elamite Inscriptions and Related Cuneiform Texts I: Linear Elamite Texts from Susa*. OrientLab Series Maior 10. Bologna: Ante Quem. ISBN 978-88-7849-226-4.
- Hatamti–Linear Elamite Database (Université de Liège):
  - doc 22: Persian Gulf seal, Ligabue, chlorite, "beginning of the 2nd millennium", *za-ši-ri₂* (signs 70, 57, 46), Winkelmann 1999 p. 25 figs 1–2.
  - doc 19: Shahdad vessel, INM 8527, *ti-n-ra-X-r*, dated "ca. 2700".
  - doc 28: Konar Sandal large tablet.
  - https://hatamti-elam.uliege.be/elamiteli/doc_detail/22 (and /19, /28).
- Laursen, S. T. 2010. The Westward Transmission of Indus Valley Sealing Technology. *Arabian Archaeology and Epigraphy* 21: 96–134. doi:10.1111/j.1600-0471.2010.00329.x. Seal no. 28 is "the only example where a seal with Indus imagery has its Indus characters replaced by a Linear Elamite inscription". Note 4 is the Glassner Bahrain seal. (Via search snippet; paragorth §10 read the full paper.)
- Vidale, M. & Frenez, D. 2015. Indus Components in the Iconography of a White Marble Cylinder Seal from Konar Sandal South (Kerman, Iran). *South Asian Studies* 31(1). doi:10.1080/02666030.2015.1008820. Uninscribed; the same site has Indus-type weights.
- Louvre, SB 2425 (AS 41): cylinder seal, "Lieu de création : Vallée de l'Indus; Lieu de découverte : Suse", Paléo-élamite IB = Suse IV B (−2400/−2100), "Écriture : Indus", steatite, H 2.3 cm, D 1.6 cm. https://collections.louvre.fr/ark:/53355/cl010176471
- Frenez, D., Degli Esposti, M., Méry, S. & Kenoyer, J. M. 2016. Bronze Age Salut (ST1) and the Indus Civilization: recent discoveries and new insights on regional interaction. *Proceedings of the Seminar for Arabian Studies* 46. (Venue and volume are from memory; the search result gave only authors, title and pp. 113–119. Verify.)
- Klochkov, I. S. 1998. Signs on a potsherd from Gonur (on the question of the script used in Margiana). *Ancient Civilizations from Scythia to Siberia* 5(2): 165–175.
- Lawler, A. 2007. Ancient Writing or Modern Fakery? *Science* 317: 588–589.
- Stevenson, T. 2025. Beyond Mesopotamia. *London Review of Books* 47(4). Covers the contested role of the kunanki vessels and Dahl's February 2023 critique.
- Penn Museum, *Expedition*: "The Middle Asian Interaction Sphere". It describes the Gonur Indus elephant seal and the two Altyn Depe seals.

Not obtained:
- The full text of Desset et al. 2022 (an open PDF exists at unibo; I relied on the HLED database and secondary summaries for values).
- Dahl 2023, Eskandari et al. 2025, and Desset et al. 2026 vols I–II, all in full.
- CISI 3.2 and 3.3, which hold the photos of the Sibri, Miri Qalat, Altyn Depe, Gonur and Shortughai objects.
- CDLI was down (HTTP 500).

## Next experiments
- Nothing computational is pending on this route. The leads above are imaging and correspondence.
- If CISI 3.3 is obtained, re-check the Central Asian and Iranian texts in `objects.csv` against the photos.
- Optional: rerun H1 once a second independent look-alike list exists (for example from Desset or Mäder sign lists, drawn blind by a rater who has not seen Indus distributions). A second list reaching p < 0.05 would justify a sound-value test restricted to those signs.
