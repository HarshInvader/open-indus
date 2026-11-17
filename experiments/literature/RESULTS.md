# Literature map: Indus script research, with emphasis on 2015-2026

Literature agent, 2026-11-14. Files in this folder: `RESULTS.md` (this file), `proposals.json` (763 machine-readable sign-value claims), `build_proposals.py` (rebuilds it from source data), `results.json`.

## Conclusion first

1. **Nobody has deciphered the Indus script, and no claim has passed an outside test.** Every phonetic key tested against its own shuffled null in 2025-26 failed. That includes Yajnadevam's Sanskrit key, Pierson's Proto-Dravidian key, the keys of Fairservis and S.R. Rao, and paragorth's Tamil key. A fitted key also "reads" planted English, Sanskrit and random strings about equally well.
2. **Statistics alone cannot settle whether the script writes language.** The Rao 2009 entropy result was answered by Sproat (2010, 2014). Raghavendra (arXiv 2608.02999, Aug 2026) then built an artificial emblem system with no sounds ("SIGIL") that matches Indus on every statistic he could score exactly. Treat entropy, Zipf and n-gram arguments as closed.
3. **The field's best facts are structural, and the prior projects in `sources/` have already confirmed most of them with controls.** The script reads right to left. Texts are short (mean about 4.6 signs). It has roughly 400-700 signs depending on how allographs are split, and the jar sign (M342) usually ends a text. Seal texts follow a template: opener, unique middle, title/closer. Stroke signs form two classes (tall and short), and numerals come before the thing counted. Indus-sign seals found abroad break the home grammar.
4. **What is genuinely new since 2015:**
   - The Linear Elamite decipherment (Desset et al. 2022). It shows what kind of anchor a decipherment needs: royal names known from cuneiform, on objects dated well enough to predict which names appear. The Indus script has no such anchor.
   - Ancient DNA from Rakhigarhi (2019): no steppe ancestry in the Indus population, and Indus-related ancestry is the main source for later South Indian ancestry. This fits a non-Indo-European Indus language, most plausibly Dravidian-related, but does not prove it.
   - Mukhopadhyay's administrative/logographic reading (2019, 2023) and her *pīlu* 'elephant/tooth' loanword argument (2021).
   - The 2026 wave of solo + AI projects. The honest ones produced negative or structural results.
5. **The highest-value work left is cheap and falsifiable.** Make each published sign-value proposal predict something in the corpus it was not fitted to: numerals, copper-tablet captions, find context, sealing backs, weights. Then score the predictions on held-out texts. The ranked list is in section 4.

---

## 0. What the prior projects in `sources/` already did (summary, not redone)

| Project | What it established | Key negative results |
|---|---|---|
| **shaunmortal/indus** (Ayush Kumar + Claude). Files: `STATE.md`, `attempts.md`, `research/*.md`. Zenodo 10.5281/zenodo.23399794 | <ul><li>Numerals sit on seals as often as on accounting objects (F1).</li><li>Tall and short strokes are separate classes with complementary counted items, e.g. M328 counted only by tall strokes (F2, F5, F8; replicated on ICIT).</li><li>Stroke layout matters: M103 (2-over-1) is bound to M403 (F7).</li><li>Side 1 of a tablet carries the identity, side 2 a tall-stroke formula (F15).</li><li>The cup formula on tablets avoids the values 1 and 5 (F38).</li><li>96% of seal texts are unique (F26). Title blocks; no sign is tied to an animal motif (F14). Round seals use their own lexicon (F19). No site dialect (F24).</li><li>Allograph merges validated by perplexity (M3-M5). Mahadevan-Wells bridge of 176 signs.</li><li>Sealed 30% hold-out with a public hash.</li></ul> | <ul><li>Wells's "tall stroke = 10" fails 3 tests.</li><li>Kober-style paradigms are at chance once duplicates are removed (F23 retracted).</li><li>Tamil Nadu graffiti look-alikes do not behave like the Indus signs they resemble (F31, p = 0.51).</li><li>No bilingual object anywhere in print (F3, F4, F6, F11).</li></ul> |
| **paragorth/Indus-** (Parag Garg). Files: `README`, `STATUS`, `ANCHORS`, `MYTHS`, `PREREG_RESULTS`, `STRATEGIES` (235+ strategies) | <ul><li>Frame grammar: opener, middle, closer (about 140 titles), suffix.</li><li>A late bar-seal genre.</li><li>Number + item terms shared by seals and tablets.</li><li>Fixed captions on moulded scene tablets.</li><li>214 Meluhha attestations pulled from CDLI. Only Samar and Nanaza (Nisaba 15 0371, about 2032 BCE) have non-Sumerian, non-Akkadian names.</li><li>Identity trails across sites and borders, e.g. Kalibangan/Bahrain 91-56.</li><li>Three frozen preregistrations: P, Q, R.</li></ul> | <ul><li>**Planted-language control:** statistical key-fitting cannot recover a known planted language at Indus size. At 150+ signs, wrong keys beat the true key even with the exact vocabulary. Only an 80-sign syllabary works (S107, S113-S137).</li><li>`tamil-full-80` "passed", then passed equally on planted Sanskrit and English (`STOP.md`).</li><li>Fuls 2024 Linear Elamite look-alike key fails a blind test (2 hits vs 4.1 ± 2.7, P = 0.83).</li><li>Yajnadevam key rejected (Q14).</li></ul> |
| **joyboseroy/indus_decipher** (toolkit). Files: `README`, `CLAIM_EVIDENCE_MATRIX` | <ul><li>Structure at trigram order replicates on M77 and ICIT.</li><li>Substitution communities generalise from Mohenjo-daro to Harappa.</li></ul> | <ul><li>Trigram structure appears in a non-linguistic administrative generator, so it does not imply language.</li><li>Seal-text uniqueness is at or below a null, which counts against a "registration code" reading.</li><li>Sumerian and Sanskrit lose their signal when cut to Indus corpus size.</li></ul> |
| **field-cady/indus_valley_script_corpus** | ICIT export (lipi), `xlits.csv` = Yajnadevam's per-sign key | (data only) |

The constraint they converge on is that readings can only come sign by sign from outside anchors. paragorth S129 estimates that about 20-40 anchored common signs plus a domain vocabulary would be needed.

---

## 1. State of the field (one page)

### Established (broad consensus, replicated)
- **Direction:** right to left in the great majority of texts. Shown by spacing and cramping, and replicated statistically. Fuls 2024 says 87% read right to left. ([Fuls 2024, IJAS 14(1):3-16](https://ijas.usb.ac.ir/article_8463.html); Mahadevan 1977; paragorth S161.)
- **Corpus shape:**
  - Text length: mean about 4.6 signs, longest single-surface text 17 signs (M-314) ([Farmer, Sproat & Witzel 2004](https://safarmer.com/fsw2.pdf)).
  - Size: about 5,500 inscribed objects in ICIT (Fuls); 4,692 objects and 19,932 signs in Fuls 2024.
- **Sign inventory:** 417 (Mahadevan 1977), about 400 (Parpola), 676-713 (Wells/Fuls; [Fuls 2023 Catalog](https://www.researchgate.net/publication/373522673)). The spread reflects how allographs are split. Parpola argues that about 400 is too many for a syllabary and too few for pure logography, which points to a logo-syllabic system ([Parpola 2010](https://tuhat.helsinki.fi/ws/portalfiles/portal/127256525/Parpola_A_2010._A_Dravidian_solution_to_the_Indus_script_problem.pdf)). Fuls 2024 estimates about 19-22% of signs are syllabic.
- **Rare signs:** about 27% of signs occur once (M77).
- **Frequency:** the 4 commonest signs make up 21% of tokens, and the top 20 more than 50% (FSW 2004).
- **Positional classes:**
  - The jar M342 is the commonest sign and ends about 70% of the texts it appears in. Other terminal signs: M176, M211, M1.
  - Openers: M267 + M99, and M391.
  - Fixed formulas recur across sites. Sources: Mahadevan 1977; Wells 2015 App. II (Fuls); paragorth `GRAMMAR.md`; shaunmortal M1b (only 3 stable classes).
- **Numerals:** stroke groups are numerals or number-like, and the number comes before its head (Parpola; Wells; Mukhopadhyay 2019). The two-class tall/short structure is shown in shaunmortal F2/F5/F8 and paragorth S197-S217.
- **No bilingual exists in print.** The only Indus-type seal with cuneiform, BM 120573 from Ur, has no Indus signs ([Gadd 1932](https://archive.org/download/in.gov.ignca.33779/33779.pdf); shaunmortal F6; paragorth ANCHORS §7).
- **Indus-sign seals abroad break the home grammar:** no home opener, and many sign pairs unseen at home (paragorth ANCHORS §1: p < 0.0001 on IM77). Gulf-type round seals have an excess of the prefixed "twins" sign ([Laursen 2010, AAE 21](https://www.harappa.com/sites/default/files/pdf/The_westward_transmission_of_Indus_Valle.pdf)).

### Contested
- **Is it language?**
  - Not writing: Farmer, Sproat & Witzel 2004; [Sproat 2014, *Language* 90:457](https://muse.jhu.edu/article/547119/summary) (two measures that do separate writing from non-writing put Indus and Pictish on the non-linguistic side).
  - Linguistic: [Rao et al. 2009 *Science*](https://homes.cs.washington.edu/~rao/ScienceIndus.pdf); [Rao et al. 2010 reply, CL 36(4)](https://doi.org/10.1162/coli_c_00030); Parpola; Mahadevan; Wells; Fuls.
  - In between: [Nair 2026, arXiv 2604.17828](https://arxiv.org/abs/2604.17828) places Indus between heraldic and administrative baselines. Mukhopadhyay 2019 calls the inscriptions "formalized data carriers", mostly logographic or semasiographic. paragorth (Sept 2026) calls it most likely a word-sign labelling system.
- **Language family:**
  - Dravidian: Parpola, Mahadevan, Fairservis, the Knorozov team, Wells, Mukhopadhyay 2021.
  - Para-Munda / "Language X": [Witzel 1999, EJVS 5](https://doi.org/10.11588/ejvs.1999.1.828).
  - Indo-Aryan: S.R. Rao, Yajnadevam.
  - Unknown or extinct: many.
- **What the texts say:**
  - Names with titles and deity/astral elements (Parpola).
  - Addresses and titles (Mahadevan's akam/puram).
  - Credentials and licences, taxes and commodity control, with no proper names ([Mukhopadhyay 2023](https://www.nature.com/articles/s41599-023-02320-7); paragorth's working model).
  - Branding in an oligopolistic administration (Frenez 2026, SSRN 6103846).
- **Numeral values:** in Parpola's reading short strokes are units and semicircles are tens. Wells reads tall = 10 and short = 1 (refuted on data by shaunmortal F5). Mukhopadhyay reads them as commodity-specific metrological denominations.
- **Tamil Nadu graffiti continuity:** about 60-90% of marks have shape parallels ([Rajan & Sivanantham 2025](https://www.deccanherald.com/india/tamil-nadu/graffiti-marks-from-tamil-nadu-are-similar-to-indus-valley-civilisation-signs-study-3342349); [tngraffiti.in](https://tngraffiti.in/)). There is a gap of 1,000+ years, the marks are mostly single signs, and look-alikes do not behave alike (shaunmortal F31).

### Refuted or failed
- **Entropy, Zipf or n-gram statistics as proof of language.** Sproat 2010/2014; Raghavendra 2026 (SIGIL; [arXiv 2608.02999](https://arxiv.org/abs/2608.02999)); joyboseroy synthetic continuum.
- **Dictionary-hit maximisation as decipherment.** Wrong keys beat the true key (paragorth S113-S137). SIGIL "decodes" into English, Sanskrit and Tamil.
- **Yajnadevam's Sanskrit key:**
  - Shuffled-key percentile 0.29 (z -0.35) in [Savirinc/indus-script](https://github.com/Savirinc/indus-script). The same bench detects the true Linear B key at Indus density (z 11.5).
  - a + ā make up **94.98%** of vowels in his readings, against 60-68% in every real Sanskrit or Indo-Aryan corpus ([Equationist/indusscript-decipherment-stats](https://github.com/Equationist/indusscript-decipherment-stats)).
  - No gain from real sign order: 57.9% real vs 59.2% shuffled ([thewisecrab/indus-valley-script](https://github.com/thewisecrab/indus-valley-script)).
  - Rejected by paragorth Q14.
- **Pierson 2026 Proto-Dravidian readings:** cut from 605 to 185, 161 and then 94 by the author's own audits. No external test ([Zenodo 20414696](https://zenodo.org/records/20414696)).
- **Wells "tall = 10":** shaunmortal F5 (no fixed order in compound numerals; peaks at 3, 7 and 12; complementary counted items).
- **Fixed sign-animal (emblem) links:** none survive in Mahadevan's coding (paragorth Q10; shaunmortal F14).
- **Shape transfer from Linear Elamite:** Fuls 2024 look-alikes fail blind (P = 0.83). Fuls himself says the scripts are "not directly related".

---

## 2. Decipherment proposals and their falsifiable predictions on our corpus

Sign numbers are Mahadevan (M77), checked against `data/sign_images/` where marked "drawing-checked".

**About the counts in this section:** where a count appears it is *descriptive*, computed on all 2,270 distinct M77 texts as a literature cross-check. These are not tests. Hypothesis tests must be run on `dev` and scored on `heldout`/ICIT.

**Descriptive anchor 1, numeral directly before the plain fish M59 (distinct M77):**

| Preceding numeral | Texts |
|---|---|
| 2 tall strokes (M87) | 65 |
| 3 short | 16 |
| 2 short (M99/M100) | 16 |
| 6 short | 12 |
| 4 short | 5 |
| 1 tall | 5 |
| 1 short | 1 |
| 7 short | 1 |
| 5 | 0 |

This matches paragorth Q4 (3:18, 6:14, 4:5, 7:1, never 5).

**Descriptive anchor 2, other counts:**
- M267 opens 221 distinct texts, and M267-M99 occurs 225 times.
- M293 opens 71 texts.
- M403-M87 occurs 27 times: 18 seals, 4 sealings, 3 miniature tablets.

| Author, year | Language | Key sign values claimed | Evidence type | Falsifiable predictions on our corpus |
|---|---|---|---|---|
| **Knorozov, Kondratov, Albedil, Volchok** (Proto-Indica, 1965-1981) | Dravidian | Positional segmentation; suffixing grammar; few specific values (UNVERIFIED in detail) | Positional statistics, typology ([harappa.com/script/maha15](https://www.harappa.com/script/maha15.html)) | (a) Suffixing: grammatical signs cluster at word ends. This holds (terminal class), but SIGIL shows emblem systems do the same. (b) No other value is concrete enough to test. |
| **Parpola** 1994, 2010, 2015 | Proto-Dravidian (logo-syllabic, rebus) | <ul><li>Fish M59 = *mīn* 'fish' → 'star/god'</li><li>3 + fish (M102 + M59) = *mū-mīn* (Mṛgaśiras)</li><li>6 + fish (M108/109 + M59) = *aṟu-mīn* (Pleiades)</li><li>7 + fish (M110/112 + M59) = *eḻu-mīn* (Ursa Major; seal H-9)</li><li>Roofed fish M65 = *mai-mīn* 'black star' (Saturn)</li><li>'Fig' (Parpola no. 123) + fish = *vaṭa-mīn* 'north star'</li><li>Intersecting circles M403 = *muruku* 'bangle' → Murukan</li><li>Spindle = *katir* 'shine'</li><li>Squirrel = *piḷḷai* 'young'</li><li>Man M1 = *āḷ*</li><li>Strokes = Proto-Dravidian numerals</li></ul> | Rebus and iconography; Old Tamil and Vedic astral names ([Parpola 2010](https://tuhat.helsinki.fi/ws/portalfiles/portal/127256525/Parpola_A_2010._A_Dravidian_solution_to_the_Indus_script_problem.pdf)) | **P1.** Number + fish should take only numbers that name asterisms (3, 6, 7, plus Old Tamil names for any others). Observed: 2 tall + fish is the commonest (65), 4 + fish occurs 5 times with no known asterism name, and 7 + fish occurs once. Prediction for held-out/ICIT: the share of 3/6/7 among short-stroke + fish stays ≥ 0.8, and 5 + fish stays at 0. If 4 or 5 + fish grows, or 2 tall + fish proves to be a count, P1 weakens. **P2.** If fish compounds are deity/star names, they should be enriched on objects with divine iconography (seated "proto-Śiva", tree deity, M-453-type amulets) against a frequency-matched null. **P3.** M403 should be enriched on stoneware bangles (ICIT material 'Stoneware', 23 texts) and on amulets with throne-and-snake scenes, against a material-stratified shuffle. **P4.** The numerals must stay numerals: M102/M108/M110 must keep the numeral distribution (before counted items), not behave like syllables. **P5.** The rebus must be consistent: a sign read *mīn* should not appear where 'fish' is impossible under the same rule, unless a determinative distinguishes the readings. Hard to test without a lexicon. |
| **Mahadevan** 1970-2014 (last papers about 2014-2018) | Dravidian / Old Tamil | <ul><li>Jar M342 = masculine singular suffix *-an* (later a priestly title, contrasted with the military arrow M211)</li><li>M267 + M99 = *akam* 'citadel/inner city' + case marker</li><li>Crescent M293 = *puṟam* 'outer city'</li><li>M373 = *akam* (alternative)</li><li>Quartered circle = *pāḻi* 'city' (number UNVERIFIED)</li><li>Burden-carrier M12 = *poṟai* → *poṟaiyan* (Chera title) (paper UNVERIFIED)</li><li>2014: a four-sign sequence = 'merchant of the city' ~ Pūṣan</li></ul> | Dravidian etymology and Cankam usage; positional frequency ([Akam and Puram excerpts](https://keezhadiandindusvalleycivilization.com/akam-and-puram-of-the-indus-script/); [Jyothibabu review](https://www.academia.edu/101124192); [IRC Bulletin 4](https://rmrl.in/bulletin/bulletin-No-4-Nov-2014.pdf)) | **P6.** If M267 and M293 are "inner" and "outer" addresses, they should be (a) mutually exclusive in a text and (b) share the same following titles and names. Mahadevan claims (b); test the overlap of their follower distributions against frequency-matched sign pairs. (c) At sites with excavated citadel/lower-town loci (Mohenjo-daro, Harappa, Kalibangan, Dholavira), M267 seals should be enriched in citadel loci and M293 seals in lower-town loci. *This locus test has never been run.* **P7.** If M342 is a masculine suffix, it should follow name-like middles, rarely follow numerals, and alternate with a feminine counterpart in the same slot. paragorth Q7: jar-final in count texts is 0.13-0.15 vs 0.31 elsewhere, which fits partly. Look for a sign in complementary distribution with M342 in the same slot. **P8.** If M211 (military) and M342 (priestly) are rival titles, they should rarely co-occur at the end of the same text. |
| **Fairservis** 1992 | Dravidian | Titles and honorifics of chiefs via DEDR rebus; specific values UNVERIFIED | Rebus, archaeology ([Brill](https://www.degruyterbrill.com/document/isbn/9789004676756/html)) | Key rejected by the Savirinc shuffle bench (NULL). No independent prediction recorded. |
| **S.R. Rao** 1982 | Indo-Aryan (alphabet-like) | About 20-sign "alphabet" | Shape comparison with Semitic scripts | Already falsified: an alphabet is excluded by inventory size and positional data (paragorth S169); NULL on Savirinc. |
| **Wells** 2011, 2015 | Proto-Dravidian, with readings in ch. 6 (Dholavira signboard toponym) | <ul><li>Tall stroke = 10, short stroke = 1</li><li>V/cup (M328) = volume measure; about 9.24 L per tall stroke on the 3 Purana Qila pots</li><li>W900 (M287) = positional-notation numeral</li></ul> | Metrology (n = 3 vessels); positional analysis | **P9.** Place value predicts a fixed order in compound numerals and no tall-tall or short-short compounds. **Failed** (shaunmortal F5: SS32, TT12, TS17, ST9). **P10.** Volume predicts that, on pots, the tall count scales with vessel capacity. Only partly supported (F33, pots only). Test on any new measured vessel. **P11.** The signboard sequence (Wells 820-611...) should recur as a place label. It recurs at Lothal and Harappa (paragorth S80); test whether those uses are place-like (e.g. on sealings). |
| **Rao, Yadav, Vahia, Mahadevan et al.** 2009-2010 | Not specified | None (structure) | Conditional entropy; Markov n-grams ([Yadav 2010 PLoS ONE](https://doi.org/10.1371/journal.pone.0009506)) | Not a decipherment. Testable claim: a bigram model restores missing signs better than chance on held-out texts. Holds, but carries no language-specific information. |
| **Mukhopadhyay** 2018-2023 | Logographic; spoken language Proto-Dravidian (2021) | <ul><li>Stroke signs = metrological denominations whose value depends on the commodity</li><li>Rimless pot (M328) + 2-4 tall strokes on tablet backs = metrological fee</li><li>Crop/sheaf signs after numerals = commodities</li><li>Jar = phrase-final functional sign</li><li>No proper names</li><li>Kanmer tablets = gate passes</li></ul> | Functional classes, archaeological context, proto-cuneiform analogy; tooth-word *pīlu* ([2019](https://www.nature.com/articles/s41599-019-0274-1), [2021](https://www.nature.com/articles/s41599-021-00868-w), [2023](https://www.nature.com/articles/s41599-023-02320-7)) | **P12.** Commodity-specific denominations predict that each counted sign has its own set of allowed values. shaunmortal F2/F5 found complementary tall/short sets, which supports this. Extend: every counted sign's value set should differ from the others' more than in a shuffle. **P13.** "No proper names" predicts that seal middles are not idiosyncratic. But 96% of seal texts are unique (F26), and joyboseroy finds uniqueness at or below a matched null. Run a decisive test: do middles behave like names (open set, Zipf tail, hapaxes concentrated in the middle slot) or like a closed vocabulary? **P14.** Licences predict that tablet values repeat per issuer. paragorth S93/S94 finds a given text keeps its count. |
| **Bonta** 2010-2023 | Semiological | About 60 partial values (Academia) | Distributional, self-published ([academia](https://www.academia.edu/105134798)) | No predictions in falsifiable form; not tested by anyone. |
| **Daggumati & Revesz** 2018-2023 | Indus related to Phoenician, Sumerian, Cretan (by sign shape) | Visual similarity, CNN-based | CNN image similarity ([2023, *Information* 14:227](https://doi.org/10.3390/info14040227)) | Shape similarity does not carry values (Fuls 2024; paragorth §11). Prediction: transferred values should give attested syllable pairs above a shuffle. **Failed** for the comparable Linear Elamite key (P = 0.83). |
| **Yajnadevam** (Bharath Rao) 2022-2026 | Post-Vedic Sanskrit, "proto-abugida" | A 714-sign key (`proposals.json`). Examples: fish W220/M59 = *m*; jar W740/M342 = *an*; arrow W520/M211 = *n*; M176 = *i*; tree W390 = *r*; openers W817/W861 (M267) and W820 (M391) = *r*; **numerals get sound values:** 1 short = *a*, 2 short (M99) = *v*, 3 short = *j*, 6 = *s*, 7 = *s*, 2 tall (M87) = *s*, 3 tall (M89) = *j*. 28 signs are blank. | Cryptanalytic search for maximum Monier-Williams dictionary coverage ([paper](https://www.academia.edu/78867798); [lipi](https://github.com/yajnadevam/lipi); replies on [Substack](https://yajnadevam.substack.com/p/refuting-the-falsifications-of-my)) | **Already failed:** shuffle null, vowel distribution, order sensitivity, Q14 (see §1). **New cheap test (P15):** the key gives numerals syllable values, so it predicts that the stroke signs have *no* numeral-specific behaviour. Observed: tall and short strokes have disjoint counted items (F2), 5 never precedes fish, and the cup formula avoids 1 and 5. A syllabic reading must explain why "s" (6, 7, 2 tall) behaves as three different distributional classes. **P16:** three openers all = *r* predicts these signs are interchangeable in the opener slot. Test their follower distributions against matched pairs. |
| **Pierson** 2026 | Proto-Dravidian | 605 → 185 → 161 → 94 readings by simulated annealing over DEDR | Key-fitting ([Zenodo](https://zenodo.org/records/20414696), [glossa-lab](https://github.com/BitConcepts/glossa-lab)) | Must pass a shuffled-key null and a planted-key recovery test at Indus size. paragorth predicts it cannot. Score the 94 readings on held-out texts. |
| **Fuls** 2024 (comparison, not a decipherment) | n/a | 17-20 Indus/Linear Elamite look-alikes with Desset values (W850 = a, W502 = li, W012 = na, W900 = pa ...) | Graphic similarity | Failed blind (paragorth §11). Kept in `proposals.json` as a negative control key. |
| **Shaw** 2026, "Crossing the Indus Threshold" | "Phonetic shadows" | Values assigned in sign-number order (ka, ta ...) | None | Built-in null: values are not derived from data (paragorth S242). Not included in `proposals.json` except by reference. |
| **Dunn** 2026 (Zenodo) | Indo-Iranian sister language, via Linear Elamite | About 6 Mahadevan matches (M87, M101, M202, M236, M303, M214/228) | Shape comparison; rejects Desset | Not independent of Indus-internal guesses (paragorth §6). |

---

## 3. Machine-readable proposals

The file is `experiments/literature/proposals.json`, rebuilt with `.venv/bin/python experiments/literature/build_proposals.py`.

| Source | Entries | Notes |
|---|---|---|
| Parpola | 12 | |
| Mahadevan | 9 | |
| Wells | 4 | |
| Mukhopadhyay | 4 | |
| Fuls 2024 Linear Elamite look-alikes | 20 | |
| Yajnadevam | 714 | Wells numbers from `xlits.csv`; 176 bridged to Mahadevan numbers via `bridge_WM.json` |

Each entry has these fields: `sign`, `sign_M`, `sign_W`, `proposed_value`, `value_type`, `source`, `mapping_confidence`, `note`.

Caveats:
- Parpola's 'fig', 'spindle' and 'squirrel' and Mahadevan's 'city' and 'merchant' signs have **no verified Mahadevan number**. Their `sign_M` is empty.
- Yajnadevam's per-inscription `sanskrit` column in the ICIT csv was **not** used as evidence, per the brief. Only the per-sign key was extracted.

---

## 4. Gaps, ranked by expected value

Expected value here means the chance of a decisive result × how much it would move the field, divided by cost. All of these are runnable with data already on disk unless marked.

1. **Numeral-behaviour test for every phonetic key.**
   - Cost: low. Decisiveness: high.
   - Keys that give stroke signs syllable values (Yajnadevam: 3 = *j*, 6 = 7 = 2-tall = *s*) imply that the strokes behave like ordinary syllables. Keys that keep them as numerals (Parpola) imply they don't.
   - Measure each key's same-value sign groups for distributional coherence against a frequency-matched null.
   - Nobody has scored published keys on this. The existing nulls only shuffle values.
2. **Copper-tablet and moulded-caption consistency test.**
   - Cost: low (needs CISI motif per copper tablet; M77 has the 61 texts but the motif sits on the other side). Decisiveness: high.
   - Mohenjo-daro copper tablets pair one fixed text with one animal or scene. Any proposal with sound values must spell the same animal the same way and give a word plausibly about that image.
   - This is the corpus's only internal image-to-text pairing. paragorth listed the captions (MYTHS §2) but did not test any key on them.
3. **Parpola's own predictions, preregistered and scored on held-out data with nulls (P1-P3).**
   - Covers number + fish value sets, fish compounds on deity-iconography objects, and M403 on stoneware bangles and amulets.
   - These predictions have never been tested with stratified nulls or a hold-out. ICIT has 23 stoneware texts.
4. **Mahadevan's akam/puram locus test (P6c).**
   - Do M267-opened seals come from citadel loci and M293-opened seals from lower-town loci? Uses M77 `locus` and level metadata, plus ICIT area/section for Mohenjo-daro, Harappa and Kalibangan.
   - A clear spatial split would be the first archaeological anchor for an opener. No split would refute his reading.
5. **Sealing backs × text (Lothal).**
   - Frenez & Tosi 2005 record the back of each sealing: woven straw, wooden box, leather sack, pottery, door peg. Transcribed in `sources/paragorth_Indus-/data/derived/lothal-sealings-frenez-tosi2005.json`.
   - Test whether texts, or counted-item signs, depend on package type. This is the nearest thing to "contents known". Small n, but nobody has run it.
6. **Weights joined to numerals.**
   - Data: [Ialongo et al. 2021 PNAS dataset](https://pmc.ncbi.nlm.nih.gov/articles/PMC8271817/) (408 Indus weights) and Ascalone 2022 (about 900 Dholavira weights).
   - Test: do tablet and pot stroke-value distributions match the binary-then-decimal weight ratios (1:2:4:8:16:32:64, 160, 200, 320...)? paragorth found no binary pattern on seals (S207); tablets and pots have not been tested against real weight frequencies.
   - Needs the xlsx via a browser (blocked for curl).
7. **Proto-Elamite pipeline, ported.**
   - Use the methods of [Born et al. 2019](https://aclanthology.org/W19-2516/), [2021](https://aclanthology.org/2021.findings-acl.362.pdf) and [2023](https://aclanthology.org/2023.cawl-1.9/): LDA genres, "header" signs, complex-sign compositionality, and numeral disambiguation by number system.
   - Also apply [Corazza et al. 2022 Sign2Vec](https://doi.org/10.1371/journal.pone.0269544) to settle the 417-vs-713 sign list on images + context, with a Cypriot-style planted control.
   - These are the only computational methods that worked on an undeciphered administrative script without a language. Indus has not had the full set applied.
8. **Craft-site enrichment.**
   - Are specific counted or title signs enriched at single-craft or trade sites against a site-size-matched null? Examples: Chanhu-daro (beads), Lothal (beads and warehouse), Shortughai (lapis), Gola Dhoro/Bagasra (shell).
   - If so, they become candidate commodity logograms that could be matched to Meluhha goods in cuneiform (carnelian *gug gi-rin*, *ab-ba* and *mes* wood, ivory, the *dar* bird; paragorth ANCHORS §5).
   - Nobody has crossed site economy with sign enrichment.
9. **Logo-syllabic planted benchmark at Indus size, plus a unicity-distance calculation.**
   - paragorth planted pure syllabaries. Extend this to a mixed system: logograms, rebus syllables, determinatives, numerals, and texts of about 4.5 signs from a name/title grammar. Use it to measure which recovery methods (anchors-needed curves, Kober grids, rebus-consistency) can work at all.
   - Savirinc argues the corpus is below unicity distance. Compute it formally for logo-syllabic keys.
   - Every future claim needs this calibration (brief rule 4).
10. **Foreign-text onomastics.**
    - Compare the about 40 grammar-breaking foreign texts, and Laursen's twins-prefixed Gulf texts, against the structure of Dilmunite and Meluhhan names in cuneiform (length, reduplication, shared elements).
    - Mine the Gu'abba "Meluhha village" prosopography ([Vermaak 2008](https://www.researchgate.net/publication/266088198)) and Laursen & Steinkeller 2017 App. 1 for non-Sumerian, non-Akkadian names beyond Samar and Nanaza.
    - Low odds, but it is the only route to a phonetic anchor visible in the literature.
11. **Typological fingerprint (lower value).**
    - Numeral-before-noun order and a suffix-heavy terminal class are compatible with Dravidian, Indo-Aryan and Munda alike, and partly with accounting conventions. Sumerian puts numerals after the noun in speech, but proto-cuneiform does not.
    - Cheap to document, but it does not discriminate between the candidate families. Do it only as a caveat table.
12. **Watch list (data, not methods).** Each could supply new held-out text:
    - CISI 3.4.
    - Rakhigarhi seals: the 5-sign cylinder seal with a crocodile, unpublished.
    - Failaka F6 2025 seals.
    - The Umma 2017 seal, a surface find.
    - Konar Sandal sealings (Pittman 2013).
    - The Kanmer passport tablets' incised sides.

**Methods from other fields not yet applied to Indus:**
- Chao1/ACE capture-recapture estimators (from ecology) of the true sign inventory and of the size of the seal-owner name lexicon.
- Born-style topic models for genre discovery.
- Sign2Vec image + context clustering.
- Archaeological network analysis of the identity trails.
- Formal unicity-distance estimates.
- Phylogenetic sign-form evolution on dated Harappa phases (3A-5).

---

## 5. Verification status
- **Verified by fetching the primary or a near-primary text:**
  - Parpola 2010 (full PDF read: fish/star, 3/6/7 + fish, fig + fish = *vaṭa-mīn*, intersecting circles = *muruku*, spindle = *katir*, squirrel = *piḷḷai*).
  - Raghavendra 2026 and Nair 2026 abstracts.
  - The Equationist, Savirinc and thewisecrab READMEs.
  - The Fuls 2024 abstract.
  - Mukhopadhyay 2019/2021/2023 on nature.com.
  - Desset et al. 2022 details via secondary sources.
- **UNVERIFIED:**
  - Parpola's roofed fish = Saturn and man = *āḷ* (well known, page not checked).
  - Mahadevan's *poṟai* reading and the sign numbers in his 2014 "merchant" sequence. M293 and M373 come from a secondary review.
  - Fairservis's and the Knorozov team's specific values.
  - [jplew/icv-test](https://github.com/jplew/icv-test) is an **empty repository** (created 2026-10-18), so there is no result to report.
  - The SSRN pages (403).
  - Kassian 2021 Dravidian phylogenetics (not found). The dated alternative is [Kolipakam et al. 2018](https://doi.org/10.1098/rsos.171504): root about 4,000-4,500 BP.
  - A "Desset 2020 preprint" (only talks found).
- **Linear Elamite facts:** [Desset et al. 2022, ZA 112:11-60](https://doi.org/10.1515/za-2022-0003). Desset 2018 silver *gunagi* beakers: [doi 10.1080/05786967.2018.1471861](https://doi.org/10.1080/05786967.2018.1471861). Critiques: Dahl 2023 (archaising, not purely syllabic); Mäder (about 70% phonetic, forgery concerns); [Kelley, Born, Monroe & Sarkar 2022](https://anoopsarkar.github.io/papers/pdf/IA57001.pdf) (the proposed Proto-Elamite values are "premature").
- **Ancient DNA:**
  - [Shinde et al. 2019 *Cell*](https://www.cell.com/cell/fulltext/S0092-8674(19)30967-5): one genome (I6113) out of 61 skeletons screened; Iranian-related + AASI ancestry; no steppe or Anatolian ancestry.
  - [Narasimhan et al. 2019 *Science*](https://www.science.org/doi/10.1126/science.aat7487): Indus Periphery Cline; steppe ancestry arrives after about 2000 BCE.
  - No new genomes from the Indus core, 2020-2026.
- **Computational decipherment record:**
  - Methods that need a known related language: [Snyder et al. 2010](https://aclanthology.org/P10-1107/) (Ugaritic, 29/30 letters); [Luo et al. 2019](https://arxiv.org/abs/1906.06718) (Linear B 67.3% of cognates); [Luo et al. 2021 TACL](https://aclanthology.org/2021.tacl-1.5.pdf) (finds no strong evidence for Basque as a relative of Iberian).
  - Linear A ML relies on Linear B sound values.
  - Rongorongo: [Ferrara et al. 2024](https://doi.org/10.1038/s41598-024-53063-7) dates the wood of one tablet to before European contact; parallel-passage work continues.
  - None of these methods applies to Indus without anchors. Language-free methods (clustering, positional analysis, topic models) do apply.

### 2026 AI-assisted projects, one-line verdicts

| Project | Verdict |
|---|---|
| [paragorth/Indus-](https://github.com/paragorth/Indus-) | Honest negative. Best planted-language controls in the field. |
| [shaunmortal/indus](https://github.com/shaunmortal/indus) | Structural; sealed hold-out; numerals work is solid. |
| [joyboseroy/indus_decipher](https://github.com/joyboseroy/indus_decipher) | Structural toolkit; walked back its own claims publicly. |
| [Savirinc/indus-script](https://github.com/Savirinc/indus-script) | Best key test bench (Linear B positive control; Finnish and Basque negative controls). All tested keys NULL. |
| [Equationist/indusscript-decipherment-stats](https://github.com/Equationist/indusscript-decipherment-stats) | Single decisive statistic against Yajnadevam (vowel distribution, 95% a/ā). |
| [thewisecrab/indus-valley-script](https://github.com/thewisecrab/indus-valley-script) | Order-shuffle and planted controls. Yajnadevam's readings are insensitive to sign order. |
| [jplew/icv-test](https://github.com/jplew/icv-test) | Empty repository. |
| [commonwealthswarm/indus-tests](https://github.com/commonwealthswarm/indus-tests) | Null scorer only. |
| [k-sandhu/indus-valley-script](https://github.com/k-sandhu/indus-valley-script) | Knowledge base with held-out tests; no readings. |
| [javdhu/indus-script-decipherment](https://github.com/javdhu/indus-script-decipherment) | Preregistered; no language recovered. |
| [apoorvsingh090/indus-script](https://github.com/apoorvsingh090/indus-script) | Claim ladder; process only. |
| [isramos/indus-script-sign-merging](https://github.com/isramos/indus-script-sign-merging) | Shows how much results depend on the sign list; 3 claims retracted. |
| [Khushirm/indus](https://github.com/Khushirm/indus) | LLM proposes, separate verifier tests; structural only. |
| [PowerpBoxCaptain/indus-sign-statistics](https://github.com/PowerpBoxCaptain/indus-sign-statistics) | Statistics only. |
| [SoylentAquamarine/indus-script-collective](https://github.com/SoylentAquamarine/indus-script-collective) | No result. |
| [BitConcepts/glossa-lab](https://github.com/BitConcepts/glossa-lab) (Pierson) | Self-corrected downward; no external test. |
| [Kriger & Hunt, Zenodo 19103880](https://doi.org/10.5281/zenodo.19103880) | "Registration code" on 179 seals; preprint; contradicted by joyboseroy's uniqueness null. |
| [Dunn, Zenodo 21650564](https://zenodo.org/records/21650564) | Fringe; rejects Desset. |
| [Shaw, Zenodo 18240941](https://doi.org/10.5281/zenodo.18240941) | Values assigned in sign-number order. |
| [Bhaskar, SSRN 5460614](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5460614) | Map reading; no null; 6/7 sign-animal pairs fail (paragorth S223). |
| Lengyel 2025 (Lulu) | Proposal only; no trained model. |
| Chhindwara model, "acoustic hypothesis", "Linguist-X 94%" ([themagpost](https://themagpost.com/post/the-silicon-rosetta-ai-cracks-the-indus-valley-script)) | Fringe or likely fabricated. |
| [Tiwari 2026, NLP4DH](https://aclanthology.org/2026.nlp4dh-1.28/) | Peer-reviewed workshop paper; structure only. |

**Tamil Nadu prize:** US$1M announced 5 Jan 2025 ([CNN](https://www.cnn.com/2025/02/28/asia/indus-valley-script-india-prize-intl-hnk-dst/index.html)). No process, panel or award has been reported.
