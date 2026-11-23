# Negative atlas: Indus routes closed or found undecidable

This file records every route the project tested and closed, or found it could not decide. The aim is to save others from repeating them. It stands alone: each entry gives the question, the method, the data, the key number, the power, the verdict and what would reopen it.

Numbers come from each folder's `RESULTS.md` and from `docs/test_ledger.csv`. The ledger held 275 rows (about 14,100 tests) at first writing and 654 rows at cycle 8. **As of cycle 10 (2026-11-15) it holds 842 rows across 64 areas** (511 confirmatory, 192 exploratory, 108 robustness, 13 red-team, the rest calibration, secondary or descriptive), with Benjamini-Hochberg correction. The test total behind the rows was not re-derived.

**Counts in this file.** 81 entries: 63 from cycles 0-6 (sections 1-10, including 5.9, which lists open items), 17 from cycles 7-10 (section 10b) and 1.11 (2026-11-20). Section 11 lists 37 red-team reversals and weakenings: 26 from cycles 0-6, 10 from cycles 7-10 and one correction (2026-11-20).

## How to read an entry

- **Corpora.**
  - **M77** is Mahadevan 1977: 3,573 lines, 13,372 tokens, 417 signs.
  - **ICIT** is the Wells/Fuls transcription: 5,679 inscriptions. About 90% of it comes from M77's sites, so it is mostly a second transcription of the same objects. It is not independent data.
  - **Held-out** means `dev_heldout(version=2)`, a family split with no near copies across the split. Version 1 leaked: 45% of its held-out texts had a near copy in dev.
- **Verdicts.**
  - **Refuted at stated power**: the test was run and failed, and the power line says what size of effect it would have caught.
  - **Untestable**: the current data cannot decide.
  - **Weakened**: an earlier positive result shrank or became construct-dependent, but was not reversed.
- **Power** states the effect size the test would probably have detected. **Not excluded** states what remains possible.
- **Prereg** paths are in `docs/prereg/`. Their hashes are in `docs/prereg/HASHES.txt`, indexed in `docs/PREDICTION_REGISTRY.md`. "None" means exploratory work, or work done before preregistration began.
- **Claim ladder**: L0 structure, L1 function, L2 semantic field, L3 denotation, L4 phonetic value. Nothing in this project reached L3 or L4.

---

## 1. Phonetic routes

### 1.1 Published phonetic keys (Yajnadevam, Pierson, Fairservis, Rao)
- **Question.** Do published sign-to-sound keys read the corpus better than chance?
- **Method.** Score each key on a bench that detects Linear B at z 11.5. Then compare it with keys fitted to noise under the same freedom.
- **Data.** M77. The keys as published.
- **Result.**
  - Yajnadevam (Sanskrit): z = 1.0, p = 0.15, with 1.32 choices per sign. Keys fitted to noise score 4.4 on his metric; his key scores 3.0. The "true" key scores 3.16, below the noise-fitted keys.
  - Pierson: 605 readings fall to 94 under the same rules.
  - Fairservis and Rao: null.
- **Power.** The bench separates a real decipherment by a wide margin (Linear B z 11.5). It cannot test a key that is never stated sign by sign.
- **Not excluded.** A future key with fixed values and fewer free choices per sign.
- **Verdict.** Refuted at stated power, for these keys.
- **Update 2026-11-23 (lb_certify, sealed).** Downgraded to **unsupported** (no evidence for these keys), not "refuted". At Indus text shape (opaque signs, Indus lengths, no word division, 74% coverage), the dictionary-fit score cannot tell real Linear B's true key from shuffled keys (CPW 2.258 vs 99th percentile 2.301). Keys hill-climbed on noise beat the true key (2.37-2.53). Fit can neither prove nor refute a key at this shape. `experiments/lb_certify/RESULTS.md`.
- **Update 2026-11-23 (lb_shape_ladder, sealed).** Standard set. IC counts only words of 4+ consonants and is tested against shuffles that keep text shape. On that test the true Linear B key beats shuffled keys at Indus length, undivided, with all signs keyed (20/20), but not at 74% coverage (13/20). It never beats keys fitted to noise on undivided text (0/20). So fit can refute a full-coverage key and can never certify one. The benched keys stay **unsupported** until a sealed IC rerun. `experiments/lb_shape_ladder/RESULTS.md`.
- **Update 2026-11-23 (yj_ic_refute, sealed, red-teamed).** Yajnadevam's key, the only full-coverage key held, tested under IC. Sealed verdict: **untestable with this lexicon**. His key does not beat its own shuffles (p 0.22-0.27). But on the real, formulaic corpus the planted Sanskrit key beats shuffles in only 5/20 (generous) or 2/20 (strict), so a non-pass is weak evidence. The red team also found a strict-lexicon bug (consonants dropped from 65% of headwords), shared with `a1_key_null.py --strict`. Every held key is now **untestable by fit at stated power**. `experiments/yj_ic_refute/RESULTS.md`.
- **Folder.** `experiments/language`, `experiments/literature`.
- **Prereg.** None.
- **Reopen with.** A key with one value per sign, fixed before it is scored, that beats noise-fitted keys with the same freedom.

### 1.2 Ventris grid (phonetic_grid)
- **Question.** Do signs fall into consonant/vowel series, as Linear B signs do in a Ventris grid?
- **Method.** Infer inflection-like alternations at word ends. Cluster signs. Check replication across sites.
- **Data.** M77, Harappa vs Mohenjo-daro halves.
- **Result.** z −0.04. Harappa-vs-MD cluster agreement ARI 0.06. Strong edges replicate 1/36.
- **Power.** Synthetic syllabary control ARI 0.86. Linear B ARI 0.13.
- **Not excluded.** A syllabary in which inflected endings appear in fewer than about half the texts.
- **Verdict.** Refuted at stated power, for a densely inflected syllabary.
- **Folder.** `experiments/phonetic_grid`.
- **Prereg.** None.
- **Reopen with.** Longer texts with repeated words in different forms (only a handful exist now).

### 1.3 Phonetic complements
- **Question.** Do some signs act as sound markers attached to logograms?
- **Method.** Planted-mechanism calibration, then a test on held-out texts.
- **Data.** M77 dev and held-out.
- **Result.** 0/14 held-out.
- **Power.** 40% at realistic strength (4/10 planted corpora), 90% if strong.
- **Not excluded.** Complements of realistic strength. Power was below a coin flip.
- **Verdict.** Untestable at realistic strength. Refuted only for strong complements.
- **Folder.** `experiments/internal_phonetics`.
- **Prereg.** `2026-11-14_internal_phonetics.md` (not in HASHES.txt; scripts frozen per RESULTS).
- **Reopen with.** A corpus several times larger, or long texts.

### 1.4 Homophones
- **Question.** Do sign pairs substitute for each other like homophones?
- **Method.** Detect planted homophone pairs at q < 0.05.
- **Data.** M77.
- **Result.** No pair passed. The candidate M99|M402 did not replicate.
- **Power.** 8/80 planted pairs found at realistic strength. 23/80 if strong.
- **Not excluded.** Almost any realistic homophony.
- **Verdict.** Untestable.
- **Folder.** `experiments/internal_phonetics`.
- **Prereg.** `2026-11-14_internal_phonetics.md`.
- **Reopen with.** Many more copies of the same name written different ways (multi-impression names).

### 1.5 Ligature decomposition
- **Question.** Are complex signs (M343-345, M348, M190, M12) ligatures of their visible parts, read like sequences?
- **Method.** Count contexts where the ligature and its parts swap. Count triples against a bigram null.
- **Data.** M77.
- **Result.** M343-345, M348 and M190: 0 events. 1 triple observed vs 6.7 expected under the bigram null. M12 falls below the null.
- **Power.** Planted triples: 3/50 at realistic strength, 16/50 if strong. Spurious triples: 2.9-5.0 per corpus.
- **Not excluded.** Ligatures for other signs. Ligatures that never alternate with their spelled-out form.
- **Verdict.** Refuted for these signs (zero events where the parts are frequent).
- **Folder.** `experiments/internal_phonetics`.
- **Prereg.** `2026-11-14_internal_phonetics.md`.
- **Reopen with.** A text that writes one of these signs out as its parts in a duplicate.

### 1.6 Determinatives (silent classifiers)
- **Question.** Do silent semantic classifiers occur?
- **Method.** Planted silent-sign test, pooled.
- **Data.** M77.
- **Result.** Nothing passed.
- **Power.** 20% at realistic strength (2/10), 70% if strong.
- **Not excluded.** Determinatives of realistic strength.
- **Verdict.** Untestable.
- **Folder.** `experiments/internal_phonetics`.
- **Prereg.** `2026-11-14_internal_phonetics.md`.
- **Reopen with.** Longer texts; an external anchor for one classifier.

### 1.7 Substitution X ↔ YZ (rebus alternation)
- **Question.** Does a single sign alternate with a two-sign spelling in the same frame, as a logogram alternates with its phonetic spelling?
- **Method.** Count substitution-class equations (SCEs). Compare them with a null. Then replicate on held-out texts and at new sites.
- **Data.** M77 dev, held-out, new sites. Ur III name control.
- **Result.** 11 SCEs vs 12.5 ± 7.3 under the null (threshold 26.1). 0/11 replicate on held-out; 0/11 at new sites. The Ur III control gives about 450 equations, none phonetic.
- **Power.** Alternating logograms making up ≥20% of word tokens are unlikely (P ≤ 0.08).
- **Not excluded.** Alternation in ≤10% of tokens (P = 0.33).
- **Verdict.** Refuted at stated power, for alternation above 20%.
- **Folder.** `experiments/substitution`.
- **Prereg.** `substitution.md`.
- **Reopen with.** Multi-impression names: one owner's name written several ways.

### 1.8 Statistical decipherment against a candidate language
- **Question.** Does a sign-to-sound fit against Tamil, Sanskrit or Sumerian beat random?
- **Method.** Calibrate the recovery rate on known scripts with related languages. Then fit Indus to each candidate.
- **Data.** M77; lexicons of candidate languages.
- **Result.**
  - Calibration: a related language gives 10-26% recovery with the search used here. **Corrected 2026-11-20:** this plateau measured weak search. With 1,000 restarts plus swap moves, Latin with an Italian model reached 0.62 at 10k and 0.66 at 30k (entry 1.11). At 2.5k, Finnish/Estonian is limited by the objective (171-195 of 200 restarts beat the truth-climbed key), and Latin/Italian by search (0-1 of 200). See `docs/prereg/search_scaling_correction.md`. **Indus-size check (2026-11-20, sealed, `docs/prereg/indus_size_search_check.md`):** at 2,500 tokens, Latin with an Italian model and no anchors gave one solved run (53%), one search-limited (45%) and one objective-limited (46%). At Indus size the result is mixed. Search depth matters, and so does closeness.
  - Indus: Tamil z 0.45-0.76; Sanskrit −0.01 to 0.25; Sumerian 0.33-0.54. The p < 0.01 bound is about 3.4.
- **Power.** Planted true languages give only z 0.3-2.8. The method cannot pick the right language even when it is known.
- **Not excluded.** Any of the candidates.
- **Verdict.** Untestable, because Indus's closeness to any candidate is unknown and planted-language power is z 0.3-2.8. Anchors raised recovery from 0.17 to 0.47-0.68 under the weak search. The earlier wording "anchors, not more text, are the bottleneck" and "not identifiable at any corpus size" is withdrawn (2026-11-20). Whether more text and more search help depends on how close the model language is.
- **Red team (2026-11-18, `experiments/redteam_decipherability`).** Low flat related-language recovery and the shuffle trap survive. "Wrong keys outscore the true key" is weakened: 72% of runs (bar 80%), 0/6 for Latin with an Italian model at 30k. A climb from the true key always ends higher and still 66-83% right, so the blind search fails to reach a mostly-right region the objective favours. Anchors work by putting the search there.
- **Folder.** `experiments/decipherability`.
- **Prereg.** None.
- **Reopen with.** About 10 fixed anchors (names or words with known readings).

### 1.9 Cognate decipherment
- **Question.** Can a cognate-matching decipherer recover values from a related language?
- **Method.** Run it on Linear B and planted corpora with realistic lexicons.
- **Data.** Linear B; Homer; Sanskrit/Pali; Tamil/Malayalam.
- **Result.**
  - Linear B with a hand-made cognate list: 80-91%.
  - Realistic lexicons: 1-39%. Linear B + Homer 1-14%; Sanskrit/Pali 5-24%; Tamil/Malayalam 6-39%.
  - Pali ranks planted Sanskrit last. Malayalam reads Sanskrit at 36% through loanwords.
- **Power.** The method needs a lexicon covering ≥50% of the types, plus word division. Indus has neither, so it was not run on Indus.
- **Not excluded.** Everything.
- **Verdict.** Untestable (the gate failed before any Indus run).
- **Folder.** `experiments/cognate_decipher`.
- **Prereg.** None.
- **Reopen with.** Word division, plus a lexicon of the right family and period.

### 1.10 Foreign names spelled phonetically on Gulf seals
- **Question.** Do Indus-style texts found in the Gulf spell foreign names with a small phonetic subset of signs?
- **Method.** Four one-sided tests on Gulf residues vs home texts: smaller sign set (G1), more repetition (G2), more reduplication (G3), the same few signs recurring (G4).
- **Data.** Gulf seals, n restated to 12; home texts.
- **Result.** G1 p = 0.81; G4 p = 0.94. The one reduplication is a doubled jar (W740). Person and number signs make up 51% of Gulf residues vs 25% at home.
- **Power.** Low at n = 12.
- **Not excluded.** Foreign names written with logograms.
- **Verdict.** Refuted at stated power, for the small-phonetic-subset form.
- **Update 2026-11-23 (round_name_shape).** Downgraded to **untestable**. On the shape-defined set (35 round texts, 28 residues), planted Ur III syllabic names are detected with power 0.22 (bar 0.8). Short names drawn from a large syllabary rarely repeat signs, so this signature cannot show at these lengths. Prereg `round_name_shape`; `experiments/round_name_shape/RESULTS.md`.
- **Folder.** `experiments/typology`.
- **Prereg.** `2026-11-14_typology.md` (not in HASHES.txt).
- **Reopen with.** More Gulf or Mesopotamian seals with Indus texts.

### 1.11 A solvability law in language mismatch (mismatch_study)
- **Question.** Does a related-language model cap recovery at a level set by the mismatch (ΔH), whatever the attack, so that a law in ΔH × size × script type could predict decipherability?
- **Method.** Pre-registered kill test. Latin with an Italian model, and Finnish with an Estonian model, enciphered as a syllabary at 2.5k, 10k and 30k tokens. Four attacks: bigram Gibbs, trigram, EM, and 1,000 restarts with swap polish. The rule: KILL if any attack's cell mean is above 0.5 at ≤ 30k.
- **Data.** Wikipedia and literary text for the four languages. No Indus data.
- **Result.**
  - The planted checks passed: true model ≥ 0.998, dialled mismatch Spearman 1.0, shuffle control passed.
  - The weak attacks reached 0.04-0.37.
  - 1,000 restarts reached 0.62 (10k) and 0.66 (30k) on Latin, so the verdict is **KILL**. Attacks spread by up to 0.52 on the same cell.
  - Finnish 1,000-restart cells and the 10,000-restart arm were not run, since the verdict could not change.
- **Power.** One replicate per 1,000-restart cell.
- **Not excluded.** A pair-dependent ceiling (Finnish/Estonian looks limited by the objective at 2.5k).
- **Verdict.** Refuted: the ceiling was weak search. Prior art had already shown that restart count dominates decipherment accuracy with a matched model (Berg-Kirkpatrick & Klein 2013, https://aclanthology.org/D13-1087.pdf). The study should have run its strongest attack first.
- **Folder.** `experiments/mismatch_study`.
- **Prereg.** `mismatch_study.md`, amendments 1-3, `mismatch_study_fix1.md`.
- **Reopen with.** Nothing in this form.

---

## 2. Language identification

### 2.1 Typology classifier for language family
- **Question.** Can sequence statistics name the language family?
- **Method.** Train a classifier on simulated families. Test leave-one-script-out on real scripts.
- **Data.** Simulated corpora; real scripts.
- **Result.** 95% accuracy inside the simulator. Leave-one-script-out 0.621. Real Latin is called "Munda". The Indus label flips with the random seed. Spec A gave IA 30/30, and the same machinery gave NONLING 30/30.
- **Power.** None on real data.
- **Not excluded.** Any family.
- **Verdict.** Untestable (the method fails its own control).
- **Folder.** `experiments/typology`, `experiments/language`.
- **Prereg.** `2026-11-14_typology.md`.
- **Reopen with.** Nothing statistical. Needs a bilingual or anchors.

### 2.2 Family from naming statistics
- **Question.** Is the Indus naming system closest to Germanic dithematic, Sanskrit compound, or Chinese given names?
- **Method.** Distance from Indus to real name lists (naming_sim P4).
- **Data.** M77 dev and held-out; real name lists.
- **Result.** Declared undecidable in advance. Calibration put family neighbours nearest in 0/7 cases.
- **Power.** None at family level.
- **Not excluded.** Any of the three.
- **Verdict.** Untestable.
- **Folder.** `experiments/naming_sim`.
- **Prereg.** `naming_sim.md`.
- **Reopen with.** A naming statistic that recovers family on known lists.

### 2.3 Head direction (word order)
- **Question.** Is there a consistent head direction in two-sign cores (head-first like Ur III, or head-last like Sanskrit compounds)?
- **Method.** Head-final index on held-out two-sign cores, with bootstrap CI.
- **Data.** M77 held-out.
- **Result.** HFI 0.47 [0.36, 0.54]. Ur III gives 0.22.
- **Power.** Head-initial like Ur III is excluded. A strongly head-final, Sanskrit-like order is only just excluded at the pooled n.
- **Not excluded.** Weak or mixed head direction.
- **Verdict.** Refuted for a consistent head direction (either way).
- **Folder.** `experiments/core_semantics`.
- **Prereg.** `2026-11-14_core_semantics.md` (not in HASHES.txt).
- **Reopen with.** A larger held-out set; word division.

### 2.4 External grounds for a language
- **Question.** Which candidate languages survive non-script evidence?
- **Method.** Literature review.
- **Result.**
  - Vedic Sanskrit: Harappan ancient DNA has no steppe ancestry.
  - Sumerian: the Šu-ilišu seal names a Meluhha interpreter, so the languages differed.
  - Munda: arrives too late.
  - Dravidian: remains open.
- **Verdict.** Weakened for Vedic, Sumerian and Munda. Not a script test.
- **Folder.** `experiments/literature`.
- **Prereg.** None.
- **Reopen with.** New aDNA or dated loanword evidence.

### 2.5 "Seven + fish" as a Dravidian star name (elu-min)
- **Question.** Is the pair seven-strokes + fish a fixed phrase, as the Dravidian reading predicts?
- **Method.** Count 7+fish against frequency expectation; red-team; held-out test.
- **Data.** M77 dev; held-out.
- **Result.**
  - The language team found 1/60, depleted not enriched (p = 0.0025). Held-out 0/13.
  - Red team: p = 0.017; seals only, 1/50, p = 0.07.
- **Power.** Enough to see enrichment at the claimed strength.
- **Not excluded.** Readings that do not need 7+fish as a fixed phrase.
- **Verdict.** Refuted (the pair is rare, not fixed).
- **Folder.** `experiments/language`, `experiments/redteam`.
- **Prereg.** None.
- **Reopen with.** Nothing obvious.

### 2.6 "Three + fish"
- **Question.** Is 3+fish a fixed phrase?
- **Method.** Enrichment on dev, then held-out.
- **Result.** Dev 16/93, p = 0.005. Held-out 2/22.
- **Verdict.** Refuted (failed held-out).
- **Folder.** `experiments/language`.
- **Prereg.** None.
- **Reopen with.** A larger independent corpus.

---

## 3. Language vs code

### 3.1 Language-vs-code classifier
- **Question.** Is the Indus corpus a writing of language or a non-linguistic code?
- **Method.** Train a classifier on known languages and codes. Test leave-one-code-out (LOCO). Apply it to Indus dev and held-out.
- **Data.** Reference languages and codes; M77.
- **Result.**
  - LOCO balanced accuracy 0.61 at held-out size, 0.68 at dev size. 3/6 codes were called language. No single metric beats AUC 0.77.
  - Indus P(language) 0.49 on dev, 0.51 on held-out. Posterior range 0.27-0.58.
  - T1 gate failed. T3 failed: 5/8 values fell inside the dev range.
- **Power.** The battery fails its own gate, so it cannot discriminate.
- **Not excluded.** Either answer.
- **Verdict.** Untestable. On the project STOP list.
- **Folder.** `experiments/language_vs_code`.
- **Prereg.** `2026-11-14_language_vs_code.md` (not in HASHES.txt).
- **Reopen with.** Long texts. Genre-matched code corpora.

### 3.2 Language vs code on genre-matched short labels
- **Question.** Does the classifier work when the references are short labels like Indus seals?
- **Method.** Power gate on real short-label units of length 1-17.
- **Data.** Genre-matched short-label references.
- **Result.** Balanced accuracy 0.69 (permutation p = 0.20; 0.59 at 150 texts). The gate needed 0.80 and failed. Indus scored 0.503.
- **Power.** Below the gate.
- **Not excluded.** Either answer. The missing comparator is a real emblem system; Pictish data are not public.
- **Verdict.** Untestable.
- **Folder.** `experiments/short_labels`.
- **Prereg.** `short_labels.md` (amended before any Indus run; amended script rehashed).
- **Reopen with.** A public corpus of a real emblem or heraldic system.

### 3.3 Entropy and earlier statistics (Rao, Sproat, SIGIL)
- **Question.** Do conditional entropy and related statistics settle language vs code?
- **Method.** Literature replication with controls.
- **Result.** Entropy closed: codes and languages overlap. The fixed-slot code model is a strawman. Segmentation fails the Ur III control. Stemmatics fails its control.
- **Verdict.** Refuted as discriminators.
- **Folder.** `experiments/literature`, `experiments/novel_methods`.
- **Prereg.** None.
- **Reopen with.** None expected.

### 3.4 Functional-reading discriminator (F5)
- **Question.** Can the functional parse itself tell language from code?
- **Result.** Undecidable.
- **Verdict.** Untestable.
- **Folder.** `experiments/functional_reading`.
- **Prereg.** None.
- **Reopen with.** Long texts.

---

## 4. Naming and genre

### 4.1 Two-inventory names (emblem × individual; modifier × head)
- **Question.** Are two-sign cores built from two separate inventories (for example clan emblem + personal sign)?
- **Method.** Polarization excess (F1) on held-out two-sign core types.
- **Data.** M77 held-out.
- **Result.** Polarization +0.075. Two-inventory systems give 0.60-0.85.
- **Power.** High for a full two-inventory system. A 25% two-slot mixture gives about 0.13, close to what was seen.
- **Not excluded.** Chinese-style given names. A minority two-slot component.
- **Verdict.** Refuted at stated power.
- **Folder.** `experiments/pair_numeral_long`.
- **Prereg.** `pair_numeral_long.md`.
- **Reopen with.** None needed for the full form.

### 4.2 Indus as an outlier among naming systems
- **Question.** Is Indus outside the range of real naming systems?
- **Method.** Nearest-neighbour distance to real name lists (naming_sim). Re-run under homography merge and grammar-free cores (core_genre).
- **Data.** M77 dev and held-out; real name lists.
- **Result.**
  - naming_sim: outlier, d 1.57 (dev) and 2.59 vs a maximum of 1.21 among real lists.
  - Merging to 286 signs: Sanskrit 0.16/0.71, Chinese 0.12/0.73. Grammar-free cores: standalone 0.91 → 0.62. Both treatments together: typical (0.92/0.58).
- **Not excluded.** That Indus is a naming system.
- **Verdict.** Weakened (the outlier depends on how cores are built).
- **Folder.** `experiments/naming_sim`, `experiments/core_genre`.
- **Prereg.** `naming_sim.md`, `core_genre.md`.
- **Reopen with.** An independent definition of the core.

### 4.3 Which genre do the texts resemble?
- **Question.** Is Indus nearer to some non-name genre (lists, labels, codes) than to name lists?
- **Method.** Bootstrap rank of genres (core_genre Part B).
- **Result.** No genre singled out. Codes were never nearer than names (0/6).
- **Verdict.** Untestable for a named genre.
- **Folder.** `experiments/core_genre`.
- **Prereg.** `core_genre.md`.
- **Reopen with.** More reference genres of the same length profile.

### 4.4 Closer sign = "servant of"
- **Question.** Does the text-final closer play the role of "servant of X" in Mesopotamian seal legends?
- **Method.** Slot-alignment fingerprint against Ur III and Old Babylonian (genre_alignment).
- **Result.** Ur III SERV 0.22; OB LORD 0.99.
- **Power.** Method calibration: C1 recovers 53-85% vs random 11%; C2 28-35%.
- **Verdict.** Refuted.
- **Folder.** `experiments/genre_alignment`.
- **Prereg.** `genre_alignment.md`.
- **Reopen with.** A bilingual seal.

### 4.5 Connective = "son of" (dumu)
- **Question.** Is the connective slot a kinship relator?
- **Method.** genre_alignment P4, then a grammar-free test in closer_ownership.
- **Result.** Grammar-free: 0/48. Pseudo-slots also get KIN 97% against Ur III, so the earlier match was built into the grammar.
- **Verdict.** Refuted (the positive was a method artefact).
- **Folder.** `experiments/genre_alignment`, `experiments/closer_ownership`.
- **Prereg.** `genre_alignment.md`, `closer_ownership.md`.
- **Reopen with.** None expected.

### 4.6 Closer = ownership ("seal of")
- **Question.** Does the closer mark ownership?
- **Method.** Five predictions on short legends and fresh reference pools (closer_ownership P1-P5).
- **Result.** The P5 gate failed: 0.25 vs a needed 0.75. Fresh references do not separate "servant of" from "seal of".
- **Verdict.** Untestable.
- **Folder.** `experiments/closer_ownership`.
- **Prereg.** `closer_ownership.md`.
- **Reopen with.** Reference legends where the two relators behave differently.

### 4.7 Fish signs = deity names (theophoric)
- **Question.** Do fish signs behave like deity names in theophoric personal names?
- **Method.** SC4 productivity test against frequency-matched signs. Calibration on real theophoric corpora.
- **Result.** SC4 p = 0.014 against a Holm alpha of 0.0056. In real corpora, the theophoric AUC is only 0.32-0.54.
- **Power.** The statistic does not detect theophoric elements even in known corpora.
- **Not excluded.** Fish as deity names.
- **Verdict.** Untestable.
- **Folder.** `experiments/core_semantics`.
- **Prereg.** `2026-11-14_core_semantics.md`.
- **Reopen with.** A statistic that finds deity elements in known name lists.

### 4.8 Occupational "tool" cluster
- **Question.** Do tool-like signs form a cluster (occupation titles)?
- **Result.** Did not replicate (p = 0.66).
- **Verdict.** Refuted.
- **Folder.** `experiments/core_semantics`.
- **Prereg.** None.
- **Reopen with.** None expected.

### 4.9 Recurrent fixed compounds (typology H3)
- **Question.** Do signs recur with fixed partners more than in any reference?
- **Result.** Failed by 0.003 against the frozen bar.
- **Verdict.** Refuted (narrowly).
- **Folder.** `experiments/typology`.
- **Prereg.** `2026-11-14_typology.md`.
- **Reopen with.** None needed.

---

### 4.10 Text genres found from the signs alone
- **Question.** Do Indus texts fall into text types (genres) that an unsupervised model can find from the signs alone?
- **Method.** HMM mixture and formula latent-class model (#34). Detection floor measured with planted genres on 2,269 real M77 texts (#43), with near-copy families rebuilt without chaining.
- **Result.** On Indus, K* = 1 for every valid model (#34). The floor for power 0.8 at Indus size is 0.57 bits/text: the formula model on a genre that differs in vocabulary, formula and length together. The HMM is never reliable on genres made inside Indus texts up to about 0.5 bits. Null false alarms: 0/10. Real Indus object type carries 0.15 bits.
- **Not excluded.** Genres weaker than about 0.5 bits/text, including object-type registers (0.15). Pure length types are excluded only above about 0.17 bits.
- **Excluded.** A strong split like Mesopotamian seal legends vs tags (1.15 bits; the HMM finds it, and finds even a diluted version at 0.02 bits of label signal).
- **Verdict.** Closed at stated power (methods blind below about 0.5 bits/text at 2,300 texts).
- **Folder.** `experiments/genres_scratch`, `experiments/genre_floor`.
- **Prereg.** `genres_from_scratch.md`, `genre_floor.md`.
- **Reopen with.** A corpus several times larger, or a labelled known-answer genre corpus of Indus-like weakness, or a model shown to beat 0.15 bits on these plants.


### 4.11 Connective M99 as a relator between two attested units
- **Question.** In "X M99 Y", are X and Y each attested as independent units (X ends another text, Y starts one) more often than for matched mid-text signs?
- **Method.** Language-neutral relational test (#42), known-answer gate on Ur III and Old Babylonian seal legends thinned to Indus size before any Indus number.
- **Result.** Gate failed: "son of" recovered in 3/100 (Ur III) and 0/100 (OB) thinned samples against a bar of 80/100; title words falsely flagged 0-0.6%. At Indus size only 2-5% of "son of" texts split into two attested parts (18.5% on the full 5,180 Ur III legends, where the test ranks "son of" first of 52 words).
- **Verdict.** Untestable at this corpus size. Not run on Indus.
- **Folder.** `experiments/m99_relator`.
- **Prereg.** `m99_relator.md`.
- **Reopen with.** About four times more texts (e.g. CISI vol 3), or a new prereg on a synthetic 400-sign corpus with a planted joining sign.

---

## 5. Administrative and relational readings

### 5.1 Administrative structure (14 predictions)
- **Question.** Do second lines, compounds, title blocks, copies and sealing backs show household, office or archive structure?
- **Method.** 14 held-out tests. Permutation nulls within site, length and campaign.
- **Data.** M77 held-out; ICIT; Lothal sealing backs (Frenez & Tosi).
- **Result.** 0/14 positive.
  - P1: 2/28 vs 0.12 expected rate (p = 0.88).
  - P9 citadel contrast: p ≥ 0.40.
  - P11: side-2 value N is not fixed (2/7 vs 2.2).
  - P12 bundling: +0.54 (p = 0.85).
  - Phase rho +0.07.
  - Lothal backs: W740 q = 0.10. Without the elephant seal, 5 vs 6.0.
- **Power.** The citadel test catches only large effects.
- **Not excluded.** Moderate area effects.
- **Verdict.** Refuted at stated power.
- **Folder.** `experiments/administration`.
- **Prereg.** `2026-11-14_administration.md`. Frozen in `experiments/administration/prereg_freeze.sha256`, not HASHES.txt.
- **Reopen with.** Find-spot lots for HARP objects (CISI 3.1 data list).

### 5.2 Rank ladder and status
- **Question.** Is frame-sign order a ladder of rank that tracks seal size, emblem or material?
- **Method.** Frozen dev order tested on held-out (C1-C12), then red team.
- **Data.** M77 held-out v2; ICIT held-out.
- **Result.**
  - Transitivity 83% vs an 85% bar.
  - Ladder vs size: rho −0.077 (minimum detectable 0.12).
  - Emblem × title p = 0.75. Material untestable.
  - Red team: M336 fails (W706 carries the effect at +64%; W705 −2%, so it is a carving variant). M249 weakened: −8% at metric sites, n = 14, MDE 32%. Zebu weakened: 33/39 from Mohenjo-daro; split luck took +42% down to +11%. 10/76 signs track size vs 0.8 expected.
- **Power.** MDE rho 0.12 for the ladder.
- **Not excluded.** Weak size signals for single signs.
- **Verdict.** Refuted for the ladder; individual size signs weakened.
- **Folder.** `experiments/rank_ladder`, `experiments/redteam_rank`.
- **Prereg.** `rank_ladder.md`.
- **Reopen with.** Measured seal sizes from more sites.

### 5.3 Tablet deposits as allocation archives
- **Question.** Do moulded tablets sort into tiers by deposit, copy count or sign content?
- **Method.** Five tests (T1-T4b), Holm.
- **Data.** Harappa tablets; HARP deposits.
- **Result.** 0/5.
  - T1 p = 0.83 (power 0.98).
  - T2 rho +0.057 (power 0.42).
  - T3 p = 0.75 (power 0.96).
  - T4b rho −0.37.
- **Power.** High for T1 and T3. Low for T2.
- **Not excluded.** A multiplicity gradient (T2).
- **Verdict.** Refuted at stated power (T1, T3). T2 untestable.
- **Folder.** `experiments/tablet_archives`.
- **Prereg.** `tablet_archives.md`.
- **Reopen with.** The CISI 3.1 lot list (HARP excavation units).

### 5.4 Toponyms (place names that travel on sealings)
- **Question.** Do some sequences mark a home site and travel on sealings to other sites?
- **Method.** Home enrichment and off-home mobility against permutation nulls (T1-T4).
- **Data.** ICIT and M77.
- **Result.**
  - Travel: ICIT 66 vs 71.9 expected (p = 0.82). M77 11 vs 14.6.
  - Reverse test: 7 vs 13.0.
- **Power.** ICIT 0.83 at OR 3. M77 0.73. Full data 0.93 at OR 2.
- **Not excluded.** Places whose sealings never left, or whose sites were never dug.
- **Verdict.** Refuted at stated power. On the STOP list.
- **Folder.** `experiments/toponyms`.
- **Prereg.** `toponyms.md`. Forward version: `2026-11-15_toponym_predictions.md`.
- **Reopen with.** New excavated sealings off-home (see the registry, PK1-PN).

### 5.5 Roofed signs in mobile or citadel contexts
- **Question.** Do "roofed" sign variants mark sealings or citadel use?
- **Method.** Odds ratios against unroofed bases, stratified.
- **Result.** Sealings OR 0.25 (wrong direction). Citadel OR 1.41, p = 0.19.
- **Power.** 0.96-0.99 for OR 3. 0.61-0.73 for OR 2.
- **Not excluded.** A twofold citadel effect.
- **Verdict.** Refuted at stated power for OR 3. Lothal backs untestable.
- **Folder.** `experiments/roof_context`.
- **Prereg.** `roof_context.md`.
- **Reopen with.** More citadel finds with loci (registry L1).

### 5.6 Copper tablets as calendar, tallies or amulets
- **Question.** Are Mohenjo-daro copper tablets a closed calendrical series, commodity tallies, or amulets?
- **Method.** Closure, evenness, ring structure, numeral minimal pairs, picture-popularity (H1-H3).
- **Data.** M77 and ICIT copper tablets, typed by legend.
- **Result.**
  - H1 calendar: Chao1 65 (45-140). Gini 0.55 vs ≤0.27 expected. Numerals p = 0.77.
  - H2 tallies: 0/3 minimal pairs.
  - H3 amulets: pictures do not follow seal popularity (rho −0.23).
- **Power.** Ring power 0.38. About 4 copies per batch surviving could mimic the observed skew.
- **Not excluded.** A calendar with batch survival.
- **Verdict.** Inconclusive, leaning against calendar. Tallies and amulets refuted at low power.
- **Folder.** `experiments/copper_series`.
- **Prereg.** `copper_series.md`.
- **Reopen with.** More copper tablets with find-spots.

### 5.7 Context tests C1-C5
- **Question.** Do texts name the animal on the seal, match emblems, or travel?
- **Result.**
  - Animal not named in the text: AUC 0.516 (not sized).
  - Emblem Jaccard: 16/16 null.
  - Copper sign level: 0.030 vs 0.064.
  - Sealings travel: 13/66 vs 10.0 (p = 0.17).
  - Square seals abroad: +0.44 [−0.54, +1.54].
- **Verdict.** Refuted (C2); others untestable at this n.
- **Folder.** `experiments/context`.
- **Prereg.** None.
- **Reopen with.** More foreign finds.

### 5.8 Title signs mark what a sealing closed (door-peg authority)
- **Question.** Do title signs (M347, M8, M336-M89, M249-M161) sit on door sealings, as storeroom authority would predict? Do they act as countersignatures?
- **Method.** H1: title rate on door (peg-on-wall) sealings vs others, Holm. S0: fixed closures vs containers. S1-S2: co-sealing.
- **Data.** 238 ICIT sealing objects. Back types are known only for Lothal (93; Frenez & Tosi 2005). 55 are diagnostic with a legible impression; 3 of those are door sealings.
- **Result.**
  - H1: 0 of 3 door sealings carry a title, vs 6 of 52 for other diagnostic sealings. Holm p = 1.0.
  - S0: titles on 1/19 fixed vs 5/36 container sealings, ratio 0.38 (p = 0.94).
  - S1: ICIT 12/22 vs 7.5 expected (p = 0.024), which misses the 0.0167 bar. M77 does not replicate (p = 0.31).
  - S2: p = 0.40 (ICIT), 0.38 (M77).
  - Post hoc W760 lead: 4/5 in ICIT, 5/12 in M77 (p = 0.50). Noise.
- **Power.** 0.004-0.012 for a threefold enrichment. 80% power would need about 40-80 inscribed door sealings, more than all known Indus sealings.
- **Not excluded.** Any title-role link. Closed by sample size, not by evidence.
- **Verdict.** Untestable (H1). Countersignature refuted at low power.
- **Folder.** `experiments/sealing_function`.
- **Prereg.** `sealing_function.md` (Amendment A1 hashed as sealing_function_A1).
- **Reopen with.** Newly excavated door sealings with recorded backs, at a scale no single site has produced.

### 5.9 Open, not closed
- M99 relational reading. The next step is listed in `experiments/closer_ownership/RESULTS.md`.
- The experiments listed here as pending at cycle 6 now have results: `carver_hands` and `assemblage` (10b.17), `scene_text` (10b.1).

---

## 6. Numerals and metrology

### 6.1 Weight series
- **Question.** Do numerals follow the Harappan weight series?
- **Method.** Ratio test (context C9).
- **Result.** Ratios 0.19/0.25 vs 0.22/0.23 expected. Short-8 E = −0.84.
- **Verdict.** Refuted.
- **Folder.** `experiments/context`.
- **Prereg.** None.
- **Reopen with.** Inscribed weights.

### 6.2 Tall stroke = 10 (place value, Wells)
- **Question.** Do tall strokes count tens?
- **Result.** Failed.
- **Verdict.** Refuted.
- **Folder.** `experiments/literature`.
- **Prereg.** None.
- **Reopen with.** None expected.

### 6.3 What the numbers count (numeral class)
- **Question.** Which real class of numbers (commodity counts, months, days, ages, names, ritual) matches the Indus value profile?
- **Method.** Likelihood against nine reference classes; posterior predictive check (PPC).
- **Result.** No class wins. PPC fails 9/9. The value 12 is 17.5 times as common as 9-10; references give 0-1.1. The spike at 7 comes from formulas.
- **Verdict.** Refuted for every reference class.
- **Folder.** `experiments/numeral_class`.
- **Prereg.** `numeral_class.md`.
- **Reopen with.** A reference class with a 12 spike.

### 6.4 Numeral base
- **Question.** Is the system additive base 12, base 8/16, or base 10?
- **Method.** Held-out log likelihood against a plain tally (M1).
- **Result.** Base 12: log10 LR −49. Base 8/16: −63.8. Base 10: −62.6. Seven of eight partners of 12 are tall strokes. 15 short + short pairs occur where base 12 forbids them. The 1+12 lead came from 3 families. W056 may be one block of about 24 strokes.
- **Power.** 1.00.
- **Verdict.** Refuted at stated power.
- **Folder.** `experiments/numeral_grammar`.
- **Prereg.** `numeral_grammar.md`.
- **Reopen with.** None needed.

### 6.5 Numerals on M328 tablets as measures
- **Question.** Does the number before M328 count tablet size, batch or lot?
- **Method.** Spearman tests Q1-Q3; model comparison Q4; shape match.
- **Result.**
  - Size: rho −0.17 (p = 0.99). Batch: +0.08. Locus: p = 0.42.
  - Fixed-value model beats count model by ΔAIC 203.
  - Shape positive control 0/2.
  - Phase drift: p = 0.005.
- **Power.** ≥0.98 for rho 0.3.
- **Verdict.** Refuted at stated power. Shape untestable.
- **Folder.** `experiments/m328_measure`.
- **Prereg.** `m328_measure.md`.
- **Reopen with.** High-resolution photos (scene_text is testing the vessel reading).

### 6.6 Counted items after numerals
- **Question.** Do numerals spike on items they count?
- **Result.** 13/25, p = 0.079. The original positive came from a code bug in `ll_spike`.
- **Verdict.** Refuted (red team).
- **Folder.** `experiments/redteam_pnl`.
- **Prereg.** `pair_numeral_long.md`.
- **Reopen with.** None.

### 6.7 Long texts as lists of short labels
- **Question.** Are long texts just concatenated short labels?
- **Result.** The original null was rigged. Corrected bigram null: 0.64 vs 0.67 observed. Joined lines: 0.38.
- **Verdict.** Refuted as a finding; the question is untestable.
- **Folder.** `experiments/redteam_pnl`, `experiments/pair_numeral_long`.
- **Prereg.** `pair_numeral_long.md`.
- **Reopen with.** More long texts.

### 6.8 Numbers vs object size (magnitude)
- **Question.** Do numerals scale with the mass, capacity or length of the inscribed object?
- **Method.** Spearman within class (T1-T4).
- **Data.** Implements n = 3 (masses chemically reduced); pottery 0; bangles 0; rods n = 13.
- **Result.** Rods rho −0.50. Same-text rods: 77.5 vs 78.0 mm.
- **Power.** 0.15 for rods. About 40 objects in one class are needed.
- **Verdict.** Untestable.
- **Folder.** `experiments/magnitude`.
- **Prereg.** `magnitude.md` (Amendment A1 appended; `run.py` rehashed as magnitude_A1).
- **Reopen with.** About 40 inscribed objects in one measured class.

### 6.9 Numeral + sign as frozen number-names
- **Question.** Is numeral + lexeme a frozen name (like "Seven Sisters")?
- **Result.** 29/40. Without M59: 14/24. M59 gives 15/16 of the hits.
- **Verdict.** Weakened (survives, driven by one sign).
- **Folder.** `experiments/pair_numeral_long`, `experiments/redteam_pnl`.
- **Prereg.** `pair_numeral_long.md`.
- **Reopen with.** New texts (registry L4).

---

## 7. Iconography and depiction

### 7.1 Signs depict the seal animal
- **Question.** Do texts name the field animal? Does referent class predict role?
- **Method.** Blind match of text to animal. Cramér's V of referent class vs role.
- **Result.** Blind match 5/24 vs 3.27 (p = 0.22), kappa 0. Class vs role V 0.27 (p = 0.20).
- **Power.** Detection limit V ≈ 0.3.
- **Not excluded.** Weak links below V 0.3.
- **Verdict.** Refuted at stated power.
- **Folder.** `experiments/iconography`.
- **Prereg.** None.
- **Reopen with.** None expected.

### 7.2 Picture signs as logograms
- **Question.** Do pictorial signs (pipal and others) behave as their pictures suggest?
- **Result.** 17 tests null (all p ≥ 0.26). Pipal 0/40. Picture minimal pairs 9 vs 10.4.
- **Verdict.** Refuted.
- **Folder.** `experiments/logograms`.
- **Prereg.** None.
- **Reopen with.** None expected.

### 7.3 Objects that label themselves
- **Question.** Does a sign that looks like an object occur on that object (jar sign on jars, bangle sign on bangles)?
- **Method.** 78 frozen sign-object pairs; four confirmation rules.
- **Result.** 1/78 pairs pass. Chamfer percentiles 0.41/0.44/0.51. Jar sign on pottery: 70 vs 124 expected. Bangle lead M373: 6/41.
- **Verdict.** Refuted ("single lead, not a reading").
- **Folder.** `experiments/self_label`.
- **Prereg.** `self_label.md`.
- **Reopen with.** More inscribed bangles (registry L2).

### 7.4 Graphic modifiers as a paradigm (diacritics)
- **Question.** Do added strokes, ticks or canopies shift a sign's role in the same way across bases?
- **Method.** Mantel-Haenszel z vs fake modifier classes.
- **Result.** Paradigm null: 0/33 held-out, 0/42 ICIT. Brackets null. Hat untestable. Ticked fish was strengthened, not reversed.
- **Power.** ≥0.8 for a +0.5 shift in 11/13 classes. For a +0.2 shift, 0.2-0.76.
- **Not excluded.** Small shifts.
- **Verdict.** Refuted at stated power.
- **Folder.** `experiments/modifiers`.
- **Prereg.** `modifiers.md`.
- **Reopen with.** None needed.

### 7.5 Referent coherence
- **Question.** Do signs with similar referents share contexts?
- **Result.** p = 0.80 and 0.49.
- **Verdict.** Refuted.
- **Folder.** `experiments/core_semantics`.
- **Prereg.** `2026-11-14_core_semantics.md`.
- **Reopen with.** None.

### 7.6 Absolute reading direction from text alone
- **Verdict.** Untestable from text. Direction is known from spacing and cramping on objects, not from sequence statistics.
- **Folder.** `experiments/structure`.
- **Prereg.** None.

### 7.7 Allographs by perplexity
- **Question.** Can perplexity find variant forms of one sign?
- **Result.** Merging 9 candidates gives z −3.6 (p = 0.005) against random merges. But context-matched merges of signs that do not look alike do as well (p = 0.67). Fish variants are not free allographs.
- **Verdict.** Refuted as a method.
- **Folder.** `experiments/structure`.
- **Prereg.** None.


### 7.8 Jar sign M342 as a vessel or storage marker
- **Question.** Is the jar sign M342 enriched on pottery, away from Mohenjo-daro?
- **Method.** One pre-registered contrast (pottery vs seals) at Harappa, Lothal and Kalibangan, length- and break-matched permutation null, planted-enrichment gate (#45). Also forward prediction F3 with Kalibangan held out (#44).
- **Result.** Gate failed: 65 consensus-corpus pottery texts give 47% power for 1.5x (about 250 needed). Descriptively 1.43x (p = 0.057); ICIT for the same sites (265 pottery texts, power 0.92) shows 0.80x, the wrong direction. Once text length is allowed for, M342 is not rarer on pottery either (F3 retired).
- **Not excluded.** A modest enrichment below about 2x on the consensus corpus.
- **Verdict.** Untestable on the consensus corpus; the evidence leans against M342 marking vessels.
- **Folder.** `experiments/m342_offsite`, `experiments/forward_predictions`, `experiments/self_label`.
- **Prereg.** `m342_offsite.md`, `forward_predictions.md`.
- **Reopen with.** New marked-sherd data (HARP sherd database) under a fresh pre-registration.

---

## 8. Cross-script look-alikes

### 8.1 Linear Elamite look-alikes
- **Question.** Do Indus signs that look like Linear Elamite signs behave like syllables, and do their sound values carry over?
- **Method.** H1 syllable-likeness; H4 adjacency of Desset values. Holm.
- **Result.** H4: 1 vs 3.4 ± 2.5 (p = 0.90). H1 Holm p 0.099. Only 24 pair tokens are covered. An earlier test (paragorth) gave 2 vs 4.1 (P = 0.83).
- **Power.** About 0.7 for H1.
- **Not excluded.** A small borrowed layer.
- **Verdict.** Refuted at stated power.
- **Folder.** `experiments/elamite_bridge`.
- **Prereg.** `elamite_bridge.md`.
- **Reopen with.** More deciphered Linear Elamite values.

### 8.2 Proto-cuneiform and Proto-Elamite look-alikes
- **Question.** Do look-alikes share function (counted, office, header)?
- **Method.** Five hypotheses; dev, held-out and ICIT must all pass.
- **Result.** 0/5. H1 0.114 vs 0.154. H2 dev p = 0.041, Holm 0.21; held-out 0.38. Chamfer distances 2.47/3.35/3.71.
- **Power.** 0.92-0.94 for strong carry-over. 0.40 if 60% of look-alikes carried function.
- **Verdict.** Refuted at stated power for strong carry-over.
- **Folder.** `experiments/protocuneiform`.
- **Prereg.** `protocuneiform.md`.
- **Reopen with.** None expected.

### 8.3 Tamil Nadu graffiti
- **Question.** Do Indus-like graffiti signs behave like their Indus look-alikes?
- **Result.** p = 0.51.
- **Verdict.** Refuted.
- **Folder.** `experiments/literature`.
- **Prereg.** None.

### 8.4 Potters' marks as ancestors of frame signs
- **Question.** Are frame signs descended from early potters' marks more than core signs are?
- **Method.** (a) precursor share; (b) vessel restriction; (c) Mature continuity.
- **Result.** M342 and M347 have early ancestors (post-firing marks). Openers M267/M391: none. Frame vs core OR 1.26. Vessel restriction p = 0.23. (c) untestable.
- **Power.** (a) 0.33. (b) 0.22.
- **Verdict.** Untestable (low power).
- **Folder.** `experiments/potters_marks`.
- **Prereg.** `potters_marks.md` (Amendment A1; `tests.py` rehashed).
- **Reopen with.** A dated corpus of Early Harappan marks.

---

## 9. External anchors

### 9.1 Meluhhan names in cuneiform
- **Question.** Are there Meluhhan personal names in cuneiform that could anchor Indus readings?
- **Result.** No anchor in print. Only na-na-sa and sa-ma-ar are secure. Name shape undecidable (n = 2-5).
- **Verdict.** Untestable.
- **Folder.** `experiments/meluhha`.
- **Prereg.** None.
- **Reopen with.** New Meluhha texts.

### 9.2 Indus-related seals on Mesopotamian tablets
- **Question.** Do sealed cuneiform tablets carry Gulf or Indus seal impressions with legible owners?
- **Result.** 12 sealed tablets. 0/10 legible seals are foreign. 0/7 images. 0/173 Ur-Lamma texts. Control: CDLI records the YBC 5447 Gulf stamp only as "(not given)", so the catalogue hides such seals.
- **Verdict.** Untestable via catalogues.
- **Folder.** `experiments/sealing_hunt`.
- **Prereg.** None.
- **Reopen with.** Photographs of P516366 and P453801.
- **Update 2026-11-21: image detector (stamp_detector).** We trained a stamp-impression detector on Yale's CC0 six-side photos (CLIP tile embeddings, multiple-instance logistic regression; 102 stamped, 398 Ur III/OB and 400 late tablets in training) to sweep about 17,000 Ur III and Old Babylonian tablets. The sealed gate failed: recall 0.44 on 73 held-out stamped tablets and controls against a bar of 0.80, and 0 of 5 known controls, including YBC 5447. Recall came only from Achaemenid (11/17) and Hellenistic (21/30) objects; Neo-Babylonian scored 0/11 and early tablets 0/2. So the detector learned late sealing types, not stamp impressions. False flags 1/300 (an Old Babylonian cylinder seal object). No sweep was run. Verdict: untestable with general-purpose image features and about 100 mostly late positives. Reopen with several hundred labelled early-period stamp impressions, or a shape-based detector checked on the 5 controls first. Prereg `stamp_detector.md`.
- **Update 2026-11-22: zero-shot kill test (stamp_zeroshot).** CLIP text prompts for stamp impressions, with no training, against 398 Ur III/OB tablets. Failed: YBC 5447 scored below 88% of the unstamped tablets, and 0 of 5 controls passed the 99th percentile (CDLI controls ranked above 19-97% of negatives). General-purpose image features do not see these stamps; a sweep by such features is closed. Prereg `stamp_zeroshot.md`.
- **Update 2026-11-22: blind eye review (stamp_eye_review).** A vision-model reviewer, blind, among 30 photos marked YBC 5447 "no" and read its impression as a rolled band; 0/29 false yes. On Yale's photo the Gulf impression has no round outline. So shape-based search (trained, zero-shot or by eye) misses the one control. **Verdict for the image route: closed.** Foreign seals must be found by iconography experts; the museum image requests are the only open path. Prereg `stamp_eye_review.md`.

### 9.3 Bilingual search
- **Question.** Is there an Indus-Elamite or Indus-cuneiform bilingual?
- **Result.** None among 34 objects reviewed, or anywhere in print. Leads: LEI 22 (Zaširi seal); text O (Sb 9382). The registration-code reading is weakened. Update 2026-11-18: text O is most likely a Linear Elamite sign list; its supposed Indus-like signs carry the end-of-stroke dots of Linear Elamite, which Indus never uses, and no Linear Elamite object with Indus signs is known (Desset 2026, pp. 44-47; `experiments/desset_textO/NOTES.md`). Lead closed. Update 2026-11-18: no Konar Sandal sealing or seal with Indus signs is known to the excavation's sealing specialist (personal communication, asked by the project); such an object may still be found there.
- **Verdict.** Untestable.
- **Folder.** `experiments/elamite_bridge`, `experiments/literature`.
- **Prereg.** None.
- **Reopen with.** A bilingual find.

---

## 10. Chronology

### 10.1 Sign turnover over time
- **Question.** Do core signs (names) turn over faster than frame signs (formulas)?
- **Method.** Drift contrast P1-P2; relative chronology P3; period-bound signs P4.
- **Result.**
  - Context Q5: 0/102 after BH.
  - half_life P1: S = −0.034 (p = 0.75). P4: 0/302.
  - redteam_chrono: rho 0.474 falls to 0.27 without shared families (p = 0.061). Signs with ≥15 units: −0.04. Cross-site pooled p = 0.48. Best marker q = 0.25.
- **Power.** 1.0 for strong turnover. Weak turnover (≤0.18) not excluded.
- **Verdict.** Refuted for strong turnover; relative chronology weakened.
- **Folder.** `experiments/half_life`, `experiments/redteam_chrono`, `experiments/context`.
- **Prereg.** `half_life.md`.
- **Reopen with.** Dated stratified finds at one site. The Gulf late-period confound is untestable.

### 10.2 Dholavira regional style
- **Question.** Does Dholavira have a regional writing style?
- **Result.** 0.84, vs Kalibangan 0.83 and Chanhu-daro 0.78. An earlier contrast (0.71 vs 1.19) did not hold.
- **Verdict.** Refuted.
- **Folder.** `experiments/redteam`.
- **Prereg.** None.

---

## 10b. Cycles 7-10 (2026-11-14 to 11-15)

Every route below was pre-registered and hashed before its outcome was computed (`docs/prereg/<folder>.md`). Each entry adds two fields the earlier ones lack: **Null** (what the observed value was compared against) and **Planted control** (how often the method found a planted effect of stated size). Where a red team ran, its verdict is the one given; it overrides the original.

Data note. Cycle 9 added public-domain 1930s excavation registers from archive.org: Mackay 1938, Vats 1940, Mackay 1943 and Marshall 1931 (`experiments/old_registers/registers.csv`). They give 1,524 linked M77 texts, decimal depth for 904 objects, dimensions for 912, house/room findspots for 640 Mohenjo-daro seals and field numbers for about 1,570. Links were checked by sign-sequence similarity (364/490 at ≥ 0.5 vs 21/1,984 random). An open-access harvest (`experiments/open_journals`) found no stalled test it could unblock: 0 new bangles, 0 readable new texts, 1 object-level firing stage on a non-script mark.

### 10b.1 Cup sign M328 on offering scenes (scene_text)
- **Route.** Is M328 glossed by the vessel held in offering scenes on tablets (an L3 candidate)?
- **Test.** H1: M328 (W700) enriched on offering-scene moulded tablet types, Mantel-Haenszel OR ≥ 3 and p < 0.05. Blind coding of 1,120 CISI face crops by two model raters from different families. Exploratory: every sign × scene element, BH.
- **Null.** Within-stratum permutation (exact sum of hypergeometrics), strata = site.
- **Planted control.** Power 0 at OR 3 and OR 5; lenient codes 0.09. No rater coded a vessel on any crop; the kneeling figures on M-478/479/480 B and H-177 B were missed.
- **Result.** 1 offering type found (H-180, no cup): 0/1 vs 0.59 expected. 0/4,080 consensus and 0/5,780 lenient element × sign tests at q < 0.05. Lead: W621 (= M242) on 5 Mohenjo-daro scene-seal types vs 0.40 (q = 0.20), 0/8 out of sample.
- **Power.** Even with legible photos, 3-6 offering types would need OR ≥ 10.
- **Verdict.** Untestable at about 100 ppi. W621 frozen as watch item W1 in the registry.
- **Folder.** `experiments/scene_text`.
- **Reopen with.** ≥ 600 dpi or RTI of M-478/479/480 B, H-177 B, H-180 B; CISI vol. 3 scene tablets.

### 10b.2 Oval M373/M374 as a bangle sign (bangle_oval)
- **Route.** Confirm the self_label lead (oval on 6/41 bangle texts) on bangles not used to find it.
- **Test.** H1: oval on ≥ 8% of new bangle texts, binomial p < 0.05 vs 0.0106; min n 10. H4: workshop alternative (site, series).
- **Null.** Non-bangle W790 rate at the same sites (pooled 0.0106).
- **Planted control.** Power analysis: 19 new texts give 80% power at a true 15% rate; 53 at 8%.
- **Result.** n = 0 eligible new bangles; every traceable inscribed bangle is already in ICIT. Descriptive H4: all 5 Mohenjo-daro oval objects come from the 1983-85 surface collection (5/27 vs 0/13 excavated, p = 0.15); one Harappa oval is on a clay bangle.
- **Power.** H4 site test 4-14%.
- **Verdict.** Untestable. Workshop or batch mark not excluded. Frozen as BO-H1 to H4.
- **Folder.** `experiments/bangle_oval`.
- **Reopen with.** HARP inscribed-bangle list or the Fuls 2023 catalogue (≥ 19 texts).

### 10b.3 Pre- vs post-firing vessel marks (firing_stage)
- **Route.** Do signs made by the potter (pre-firing) differ from signs added by a user (post-firing)?
- **Test.** P1: dev pre-firing sign set (≥ 5× enriched) replicates on held-out sites, R ≥ 2 and within-site p < 0.025. P2: painted vs graffiti. Secondary: vessel form.
- **Null.** Labels permuted within site.
- **Planted control.** A sign planted at the dev rate passes 5.9% of the time.
- **Result.** Only 36 of 650 inscribed vessels have an object-level firing stage. P1 held-out 1/16 vs 5/111, p = 1.0. P2 inconclusive (10 painted texts). Form p = 0.08, confounded with stamping. Post hoc, not blind: M391 on 4/25 painted vs 7/384 graffiti (p = 0.003 uncorrected, 3 of 4 from Kutch); jar M342 on 1/25 painted vs 70/384 graffiti.
- **Power.** 0.06.
- **Verdict.** Underpowered; refutes nothing. M342 is not a potter's sign (descriptive). Post hoc lead frozen as FS1.
- **Folder.** `experiments/firing_stage`.
- **Reopen with.** Kenoyer & Meadow HARP sherd database (1,218 marked sherds with stage and form).

### 10b.4 Seal texts as personal identifiers (identifiers, redteam_identifiers)
- **Route.** Do seal texts behave like Ur III personal seal legends: unique, with rare duplicates kept local, and contemporaries kept distinct?
- **Test.** S3: unseen-species estimates per site; P3 repeat locality R < 0.5. S4: nearest-neighbour edit distance among co-found seals (repulsion). Red team: generative nulls and length matching.
- **Null.** S3: random site assignment; red team: bigram corpus simulations keeping site and length. S4: group labels permuted within site.
- **Planted control.** S4 strong planted repulsion caught at 0.83 (ICIT) to 1.0 (M77 dev) over whole bins, but only 0.03-0.07 among small sets of true contemporaries (red team). Ur III identifiers, used as a real positive control, cluster (z −9 to −15) rather than repel.
- **Result.** Seal texts are open-ended: new-text rate 93-97% per site, estimator calibrated out of sample (7/8 cells). Original: repeats cross-site at random (R 0.89 vs Ur III 0.18). Red team: short repeats are chance collisions (145 objects vs 151 expected [129-174]); at equal length Indus 0.51 vs Ur III 0.53. Only 4-5 sign repeats exceed the bigram null (34 vs 8). "Cores more novel than names" fails as stated; it survives only against single Ur III names of the same length (0.75-0.99 vs 0.39-0.59).
- **Power.** See planted control.
- **Verdict.** Identifier-vs-label route undecidable with these statistics once length is matched. Cross-site formula layer reversed (red team). Repulsion test uninformative.
- **Folder.** `experiments/identifiers`, `experiments/redteam_identifiers`.
- **Reopen with.** Lot-level contemporaneous groups (HARP); a comparator matched for text length and unit.

### 10b.5 City-specific sign stock (site_signal)
- **Route.** Do unique seal texts carry a site signature, as local personal-name stocks would?
- **Test.** P1 whole-text Mohenjo-daro vs Harappa classifier; P2 medial slot (primary); P3-P5 transfer, 4-site, distance decay.
- **Null.** Site labels permuted with the full cross-validation re-run, 1,000 times.
- **Planted control.** A 20-sign local stock swapped into 20% of Harappa tokens is caught 92% of the time (exploratory, after the frozen run); at 10%, 22%. P2 planted power 0.12.
- **Result.** P1 AUC 0.49 (p = 0.61), n = 621 seals with no near-copy. P2 0.51 (p = 0.44). 4-site balanced accuracy 0.24 vs 0.25. Time inside Mohenjo-daro is a bigger signal (early vs late AUC 0.61, p = 0.02). The closer hint (W405, W154/W806) vanishes after allograph merging.
- **Power.** 0.92 for a 20% stock (whole text); 0.12 for the open slot.
- **Verdict.** Inconclusive by the frozen rule. A large city-specific stock is excluded for the whole text.
- **Folder.** `experiments/site_signal`.
- **Reopen with.** About 3× more dated Harappa seals.

### 10b.6 Name-plus-title formula (slot_novelty)
- **Route.** Does novelty sit in one open slot (a name) with fixed frame slots around it, and do openers predict closers (a template)?
- **Test.** T2: Baayen productivity per slot; H2a top-slot share ≥ 0.50. T3: opener-closer mutual information beyond the adjacent-sign chain.
- **Null.** T2: signs shuffled within text. T3: swap null and a fitted bigram-chain null.
- **Planted control.** Ur III legends recover the closed slot 50/50. T3 planted template caught 0.94 at strength 0.5, 0.31 at 0.25. T3 real-template control (Ur III presentation seals) shows no excess, so the test misses templates with register-specific middles.
- **Result.** Held-out productivity opener 0.49, medial 0.44, closer 0.32; top share 0.39. Closer ratio 1.39 on primary (bar 1.5), 1.56 and 1.70 on replication sets. T3 Mohenjo-daro excess +0.007 bits (p = 0.35); Harappa no power.
- **Power.** T3 0.94 for strong templates.
- **Verdict.** Single-open-slot name + title formula not supported. Opener-closer templates refuted at strength ≥ 0.5.
- **Folder.** `experiments/slot_novelty`.
- **Reopen with.** Register-split nulls (emblem or size).

### 10b.7 Omission order on small seals (space_and_sealing T4, reg_size, redteam_size)
- **Route.** Do small seals drop optional slots in a fixed order (connective first, closers kept)?
- **Test.** Share of each sign class vs face area, stratified; P3 replication of the order. reg_size re-ran it on 138 register seals T4 had not seen.
- **Null.** Original: area permuted. Red team: keep every closer and delete the rest at random (N2), real lengths and areas kept.
- **Planted control.** Red team: under N2 alone, the replication rho has median 0.52 (95% interval −0.19 to 0.90).
- **Result.** T4: connective +0.013/doubling, non-jar closers −0.021 (Holm 0.004); P3 failed (rho 0.31 / 0.60). reg_size: closers replicate, connective does not (+0.002); rho 0.79 → "replicated". Red team: non-jar closer slope equals N2 exactly (−0.0212 vs −0.0212, p = 0.998); residual order rho 0.52 (p = 0.098); 41 of 138 "new" texts were T4 seals counted twice.
- **Power.** reg_size 0.45 before outcome. Class MDE 0.011-0.038 per doubling.
- **Verdict.** Reversed by red team. What stands: texts carry about one closer regardless of length; the jar sits between closers and the rest. Separately (T4 P4, not attacked): short texts are ordered subsets of longer ones (51% vs 35.5%, p = 0.001), but containment does not depend on area (p = 0.11).
- **Folder.** `experiments/space_and_sealing`, `experiments/reg_size`, `experiments/redteam_size`.
- **Reopen with.** Independent face measurements (CISI scale bars at ≥ 30 px/mm) and a keep-obligatory null.

### 10b.8 A closer class marks seals used for sealing (space_and_sealing T6)
- **Route.** Are some closers enriched on sealings (seals that were actually used)?
- **Test.** 127 end-preserved sealing texts vs 1,426 seal texts, Mantel-Haenszel over site × length band; support requires leave-Lothal-out replication.
- **Null.** No difference (MH OR 1).
- **Planted control.** Planted OR 2 detected at 0.92 (jar), 0.85 (M211), 0.84 (M169), 0.69 (ticked fish) on all sites; 0.51-0.75 without Lothal.
- **Result.** 0/6 classes, all Holm p = 1 (OR 0.29-1.53). Connective OR 1.82 (Holm 0.067). Die survival f = 0.003 (CI −0.04 to 0.06): excavated seals are almost never the dies of surviving sealings.
- **Power.** See planted control. OR below about 1.7 remains possible.
- **Verdict.** Not supported at stated power.
- **Folder.** `experiments/space_and_sealing`.
- **Reopen with.** Per-impression seal identities at Lothal (Frenez & Tosi); new sealings.

### 10b.9 Repeated 4+ sign seal texts as re-cut or office seals (local_repeats, redteam_local_repeats)
- **Route.** Are the repeated longer seal texts one holder's re-cut seals, office seals, or workshop templates?
- **Test.** T1-T5: size difference, emblem identity, period, findspot, one-sign-longer variants. Red team: trigram and slot nulls, commonness-matched controls.
- **Null.** Text labels shuffled among same-site 4+ sign seals; red team: generative trigram/slot corpora.
- **Planted control.** Red team: two models that both fit the 1-3 sign collision band predict 8 vs 32 repeated 4-5 sign objects, so the "excess" depends on the null.
- **Result.** 15 texts on 36 seals; not local (43% same-site pairs vs 45% random). One frame (opener + M99 + 3/4/6 strokes + M162/M169) is 14 objects vs ≤ 1.14 expected under every null, but it is the known M162 count frame (Wells W390 lumps five Mahadevan signs). The other 20 objects do not exceed a fair null (18.6 expected, p = 0.42). "Texts grow" survives smaller: 6 vs 1.8 expected (p = 0.005 trigram, 0.07 bigram); "never shrink" weak. Without the formula, repeats lean local (0.67 vs 0.45, p = 0.087).
- **Power.** n = 15 families; office test untestable (1 dated pair).
- **Verdict.** "Re-cut seals like Ur III" withdrawn; "other repeats exceed chance" reversed; locality undetermined. No new formula.
- **Folder.** `experiments/local_repeats`, `experiments/redteam_local_repeats`.
- **Reopen with.** Dated formula seals (CISI 3, HARP lots); die-matching photos.

### 10b.10 Line breaks as constituent boundaries (line_breaks)
- **Route.** Do line wraps fall at slot boundaries, giving segmentation evidence independent of sign statistics?
- **Test.** Mean percentile rank of a boundary score at the break; gate n ≥ 150 and power ≥ 0.80.
- **Null.** Break placed uniformly within the text (length-stratified); capacity null defined but not run.
- **Planted control.** 20% of breaks moved to a true boundary: power 0.77 (model boundary) and 0.51 (slot-rule boundary) at n = 74. False-positive rate 0.067.
- **Result.** 74 usable two-line texts (about 113 with ICIT). Gate failed; no statistic computed. 39/117 multi-line texts end in a one-sign line; line 1 sits at the 43rd percentile of capacity, so many `|` breaks are editorial, not wraps.
- **Power.** See planted control.
- **Verdict.** Untestable.
- **Folder.** `experiments/line_breaks`.
- **Reopen with.** About 150 (model) or 300 (slot rule) true wraps, recoded from photographs.

### 10b.11 Detached signs as a class apart (detached_signs)
- **Route.** Are signs set on their own line (M242, M374, M393) an emblem-like class tied to scene, object, material or size?
- **Test.** L1-L2: detachment beyond chance, replicated. H1-H4: covariates, with all objects behind earlier leads removed.
- **Null.** 2,000 sets of frequency-matched non-class signs, stratified by site × length × multi-line.
- **Planted control.** Power 0.01-0.32 for the covariates (the 0.74 for H1 ICIT is not meaningful: null 95th percentile is 0).
- **Result.** Detachment real (M242 alone 8/22 vs 0.11, p = 7e-14; held-out p = 8e-9; ICIT-only p = 4e-4). All on the last line; inline M242 is text-final 11/14 (p = 6e-8, exploratory). Covariates 0/6, Holm 1.
- **Power.** ≤ 0.32.
- **Verdict.** Class apart not supported; covariate tie inconclusive. Simpler account: a closing sign given its own line.
- **Folder.** `experiments/detached_signs`.
- **Reopen with.** Face position from hi-res photos; new scene seals and bangles.

### 10b.12 Reversed texts as a class; time by slot; animal-less seals (direction_time_animal)
- **Route.** E2: do left-to-right texts form a functional class? E3: is the opener the slot that changes over time? E4: do seals without an animal compensate with extra signs of one role?
- **Test.** E2 gate ≥ 100 texts with independently fixed direction. E3 frequency-matched drift, opener minus closer. E4 role mix beyond length at matched area (O2) and a held-out-site classifier (O3).
- **Null.** E3 period labels permuted; E4 stratified permutation (site × period × area × length).
- **Planted control.** E3 frozen plants: power 0.00 (design flaw); exploratory strong plant 1.0. E4 planted 10% class: closer type 0.85 (O2) / 0.98 (O3); opener type 0.50 / 0.72.
- **Result.** E2: 31 qualifying texts, gate failed. E3: S_oc −0.098 (p = 0.46); global time signal on seals p = 0.21. E4: +0.81 signs at matched area (fits free space); O2 p = 0.10, O3 AUC 0.57 (Holm 0.17).
- **Power.** See planted control.
- **Verdict.** E2 untestable. E3 inconclusive (strong opener turnover excluded, exploratory). E4 refuted for a closer-type compensating class; opener type not excluded.
- **Folder.** `experiments/direction_time_animal`.
- **Reopen with.** Photo-based direction coding for ≥ 100 L-R texts; finer stratigraphy; square text-only seals.

### 10b.13 Positional grammar as a predictor (grammar)
- **Route.** Does a compact class grammar predict held-out text better than a sign bigram, and is it validated by positive and negative controls?
- **Test.** Bits per sign on 441 held-out texts; restoration; transfer across sites; Gulf negative control; Ur III positive control.
- **Null.** Position-only, unigram and shuffled-trained baselines; Kneser-Ney bigram as the bar.
- **Planted control.** Ur III legends: slot NMI 0.567 vs ≤ 0.469 for shuffles; "son of" isolated (1.00), "servant of" split (0.59).
- **Result.** Bigram 5.49 < grammar 5.79 < shuffled 6.25 < unigram 6.29 < position-only 6.38. Restoration top-5: grammar 0.35, bigram 0.48. Gulf round seals +1.80 bits (p = 0.0001). Stable classes: opener 10 signs, connective M99/M123, medial 85, closer 7.
- **Power.** CIs from 2,000 family bootstraps; differences of 0.3 bits are clear.
- **Verdict.** Not validated (positive control fails on one relator) and not a better predictor than a bigram. Not falsified: positional structure is real and transfers.
- **Folder.** `experiments/grammar`; `docs/GRAMMAR.md`.
- **Reopen with.** A hand-annotated positive control; more held-out text.

### 10b.14 Household or office signature in seal texts (reg_findspot, reg_harappa)
- **Route.** Do seals found in the same house, room or square share a sign (a household or office mark)? Are copies of one text kept together?
- **Test.** F1: same-unit vs other pairs sharing opener, closer, core or whole text, within block/mound × 5-ft depth band. F2: repeated texts co-located or contemporary. F3: classes clustered by unit.
- **Null.** Unit labels permuted within block (or mound) × depth band.
- **Planted control.** A shared sign on half the seals of a unit: caught 0.985-1.0 (Mohenjo-daro house), 0.90-1.0 (room, Harappa square and sub-square) for opener, closer and core. Whole-text test blind (0.03 at room level; 0-0.18 at Harappa).
- **Result.** Mohenjo-daro (Mackay 1938, 345 seals in 74 houses): F1 0/8 (same opener 4.0% vs 3.0%). F2: copies in the same block 3 vs 2.1; depth gap 5.7 vs 5.9 ft. Harappa (Vats 1940, 287 families in 46 squares): F1 0/8 (opener 1.7% vs 1.4%); F3 0/16 (numerals and jar null with power 1.0 at 3×).
- **Power.** See planted control. A quarter-strength signature is excluded only for openers.
- **Verdict.** Refuted at stated power in two cities with different excavators and recording systems.
- **Folder.** `experiments/reg_findspot`, `experiments/reg_harappa`.
- **Reopen with.** HARP lot-level findspots; room lists of co-found objects.

### 10b.15 Ticked fish clustered by block (reg_findspot F3, redteam_fish_block, fish_marshall)
- **Route.** Is the ticked-fish closer (README #3) concentrated in particular buildings, a first text × findspot link?
- **Test.** Block-level G statistic, family-collapsed; red team attacks on depth, batch, multiplicity, coding, replication; replication on Marshall 1931 seals.
- **Null.** Block labels permuted within area × depth band.
- **Planted control.** Red team: block-sized cluster (+4 seals) in other Mohenjo-daro areas caught 0.44 (0.83 for a 6× locus rate). fish_marshall: 0/200 for both plants.
- **Result.** Mackay DK-G p = 0.0007 (q = 0.007 over 21 confirmatory tests); house 12/V has 4 of 21. Survives depth (p 0.0007-0.003), 19 families (p = 0.0056), leave-one-out (worst 0.018), independent coding. Fails multiplicity over all 163 tests (q = 0.114) and replication at Mohenjo-daro (p = 0.31). Marshall p = 0.88 (6 ticked fish, each in a different block). Harappa untestable (3 families).
- **Power.** See planted control.
- **Verdict.** Weakened by red team; local lead, not a claim. Frozen as TF1.
- **Folder.** `experiments/reg_findspot`, `experiments/redteam_fish_block`, `experiments/fish_marshall`.
- **Reopen with.** Block or house findspots for more ticked-fish seals (HARP, Marshall house lists).

### 10b.16 Chronology from decimal depth (reg_chrono)
- **Route.** With decimal register depths, does sign use change within one site, and which slot turns over?
- **Test.** Omnibus sum z² over signs vs depth rank within area; per-sign BH; class shares; markers; opener vs closer.
- **Null.** Depth rank permuted within area × object type, 10,000 times.
- **Planted control.** 20% of signs shifted at OR 2: caught 0.92-0.94. Opener plants caught 0-10% (test blind to opener turnover); closer plants 25-95%.
- **Result.** Harappa p = 0.029 (Holm 0.057), seals only p = 0.006; Mohenjo-daro p = 0.087, gone with blocks as strata. Per-sign trends not shared (rho 0.13). M162 earlier at Harappa (Holm 0.062). Jar OR 2 shift excluded at Mohenjo-daro.
- **Power.** 0.92-0.94 for broad strong change.
- **Verdict.** Inconclusive. Broad strong change excluded; at most a weak drift on Harappa seals. README chronology line updated accordingly.
- **Folder.** `experiments/reg_chrono`.
- **Reopen with.** HARP 3B vs 3C seals; an opener-sensitive turnover index.

### 10b.17 Cycle 6 routes completed after the atlas was written
- **Carver hands (carver_hands).** Seals alike in animal carving do not share frame or core more than others: 4/4 null, frame within/between upper bound 1.01-1.11; a 20% group-specific closer was detectable at 92-100%. No real clusters at about 8 px/mm (silhouette 0.04-0.05). Untestable for true hands; reopen with ≥ 30 px/mm scans. Prereg `carver_hands.md` (amendment A1 appended after the run).
- **Craft assemblage (assemblage).** No sign tied to a craft at two sites (0/49 primary, 0/193 with seals), power about 0-4.5%. Inconclusive; reopen with HARP trench craft coding. Prereg `assemblage.md`.

### 10b.18 Survey ideas: closing slot and counted human figures (slot_function)
- **Question.** (A) Is the seal-versus-label signal carried by the last sign more than the first (Rao 2018; Born et al. 2022)? (B) Are human-figure signs counted kinds of people, preceded by numerals and commoner on tablets (Rao 2018)?
- **Result.** (A) ICIT last-sign AUC 0.771 vs first-sign 0.714 (CI of the difference 0.035-0.080), last sign above a within-text shuffle (p = 0.005); same direction on M77 held-out (+0.043, CI crosses 0). The middle signs predict as well as the last sign. (B) Numerals precede human figures no more than matched controls (ratio 0.98); human-figure share on tablets vs seals OR 1.14, p = 0.22; M77 points the other way.
- **Power.** Planted checks fell just short: 77/100 (A) and 79/100 (B1) against a bar of 80. False positives 1/100.
- **Verdict.** A untestable, kept as a lead. B not supported.
- **Prereg.** `slot_function.md`.

### 10b.19 Carver groups and shared text (carver_text)
- **Question.** Do seals grouped as one carver's work share more text than chance? (Hint-informed, single dataset, no independent replication.)
- **Result.** Sealed run p = 0.0098 (ratio 1.31, CI 1.10-1.62; 289 pairs, 44 hands). The red team's replica gave 0.0105 at 200k reshuffles and a reimplementation gave 0.017. Fixing two label errors gives 0.008. Adding text length to the strata gives 0.05, masking catalogue neighbours gives 0.04, and leaving out one hand gives 0.005-0.026. The grouping was not blind to the inscriptions.
- **Power.** 0.83 at 40% planted excess (MDE about 40%).
- **Verdict.** Not confirmed. Possible weak effect, p about 0.01-0.02; the text-length confound is still open.
- **Prereg.** `carver_text.md`; red team `carver_text_redteam.md`; `experiments/carver_text/GATES.md`.
- **Reopen with.** New texts (CISI vol. 3, post-2010 finds) for A; a fuller Wells-to-Mahadevan mapping of human-figure signs for B.

---

## 11. Red-team reversals

These claims looked positive and failed. They show where the traps are.

1. **v1 split leakage.** 45% of held-out texts had a near copy in dev. Order prediction fell from 63% to 40.2% (vs 5.7% chance) on the clean split.
2. **Dholavira regional.** 0.71 vs 1.19 became "not regional" once the comparison sites were added.
3. **Left-to-right direction.** 134/150 became 31/34 on copy-free lines. Jar 33 vs 3 became 5 vs 0 (p = 0.03, q = 0.18).
4. **7+fish.** p 0.0025, then 0.017, then 0.07 on seals.
5. **M99 seal-specific.** q = 1e-6 became 1.08×, p = 0.07.
6. **Rod register.** 9 vs 0.5 became 6 vs 0.34, Mohenjo-daro only.
7. **Copper picture.** 272 pairs became 18 legends. Sign level 0.485 became 0.030.
8. **Template test.** 67% vs 25% was circular.
9. **Functional-reading lexicon null.** q = 0.085.
10. **3+fish.** Failed held-out (2/22).
11. **Counted items.** Code bug in `ll_spike`.
12. **Long texts.** Rigged null.
13. **Number-names.** M59 gives 15/16 hits.
14. **Rank signs.** M336 is a W706 carving variant. M249 weakened. Zebu +42% became +11% (split luck).
15. **CONN = dumu.** Built into the grammar; 0/48 grammar-free.
16. **naming_sim outlier.** Construct-dependent.
17. **half_life P3.** Family-driven.
18. **1+12 numeral.** Came from 3 families.
19. **Allograph perplexity.** z −3.6 became p = 0.67.
20. **Typology spec A.** IA 30/30 and NONLING 30/30 from the same machinery.
21. **Malayalam reads Sanskrit.** 36% through loanwords.
22. **M99|M402 homophone.** Did not replicate.
23. **M12 ligature.** Below the bigram null.
24. **paragorth AAB repeats.** p = 0.023; did not replicate in Wells.
25. **shaunmortal F23.** Retracted.
26. **tamil-full-80.** Also "passed" on planted Sanskrit and English.

Cycles 7-10:

27. **Cross-site short formula layer (identifiers S3).** 145 objects on repeated 1-3 sign texts vs 151 expected under a bigram null; 0.89 vs 0.18 locality contrast was a length artefact (equal length: 0.51 vs 0.53).
28. **Seal cores more novel than personal names (identifiers).** Ur III cores built the same way are more novel (0.96-0.995 vs 0.91-0.92); survives only against single names.
29. **No identifier repulsion as evidence against identifiers.** Power 0.03-0.07 among contemporaries; real Ur III identifiers cluster.
30. **Repeated 4+ sign texts are re-cut seals of one holder, local like Ur III (red-team reading).** Withdrawn by local_repeats: 43% same-site pairs vs 45% random; the 0.18 came from small reference sites.
31. **Numeral formula as a new find; "other 20 objects exceed chance" (local_repeats).** The formula is the known M162 count frame (Wells W390 lumps five signs); the residual is 20 vs 18.6 expected under a fair null (p = 0.42).
32. **"Texts grow, never shrink" (local_repeats).** p = 9e-9 shrank to 6 vs 1.8 expected (p = 0.005 trigram; 0.07 bigram); the singleton comparison measured commonness.
33. **Graded omission order on small seals (space_and_sealing T4, reg_size).** Closer slopes equal a keep-one-closer random-deletion null (−0.0212 vs −0.0212); only "about one closer per text" stands.
34. **reg_size "new" seals.** 41 of 138 were T4 seals counted twice (register-ICIT link gap).
35. **Ticked fish cluster by block (reg_findspot F3).** Weakened: q = 0.114 over all 163 tests; not replicated elsewhere at Mohenjo-daro (p = 0.31).
36. **Connective M99 dropped first on small seals (T4).** Did not replicate on register seals (+0.002, p = 0.41); not significant against the keep-closers null.
37. **"Related-language recovery is flat with more text; not a search artefact" (decipherability, search_scaling; corrected 2026-11-20).** The sealed search_scaling verdict compared against the true key, not the truth-climbed key. Against the truth-climbed key, Latin/Italian at 2.5k is search-limited (0-1 of 200 restarts above it), and 1,000 restarts with swap moves reach 0.62-0.66 at 10k-30k. Only Finnish/Estonian is limited by the objective.

Survived the red team: the Gulf result (n restated to 12) and ticked fish (strengthened). Copper sign face is exploratory. In cycles 7-10 no positive result survived a red team unweakened.

---

## 12. Summary table

| # | Route | Verdict | Power | Reopen with |
|---|---|---|---|---|
| 1.1 | Published phonetic keys | Unsupported; untestable by fit at stated power (yj_ic_refute 2026-11-23: planted power 10-25% on the real corpus) | Fit cannot certify; refute power low on formulaic Indus text | Forward prediction or non-text covariation |
| 1.2 | Ventris grid | Refuted | Synthetic ARI 0.86 | Long texts with inflection |
| 1.3 | Phonetic complements | Untestable | 40% | Larger corpus |
| 1.4 | Homophones | Untestable | 8/80 | Multi-impression names |
| 1.5 | Ligatures | Refuted (these signs) | 0 events | Spelled-out duplicate |
| 1.6 | Determinatives | Untestable | 20% | Long texts |
| 1.7 | Substitution X↔YZ | Refuted ≥20% | P ≤ 0.08 | Multi-impression names |
| 1.8 | Fit to candidate language | Untestable | Planted z 0.3-2.8 | ~10 anchors |
| 1.9 | Cognate decipherment | Untestable | Gate failed | Word division + lexicon |
| 1.10 | Gulf phonetic names | Untestable (power 0.22 at n = 28, 2026-11-23) | Low, n = 12-28 | A known name in context (Meluhha photos) |
| 1.11 | Mismatch solvability law | Refuted (KILL) | 1 replicate | None |
| 2.1 | Family classifier | Untestable | LOSO 0.621 | Bilingual |
| 2.2 | Family from names | Untestable | 0/7 | Valid naming statistic |
| 2.3 | Head direction | Refuted | CI [0.36, 0.54] | Larger held-out |
| 2.4 | External grounds | Weakened (Vedic, Sumerian, Munda) | n/a | aDNA, loanwords |
| 2.5 | 7+fish | Refuted | 0/13 held-out | None |
| 2.6 | 3+fish | Refuted | 2/22 held-out | Larger corpus |
| 3.1 | Language vs code | Untestable | LOCO 0.61 | Long texts |
| 3.2 | Short-label calibration | Untestable | 0.69 vs 0.80 gate | Emblem corpus |
| 3.3 | Entropy statistics | Refuted | Fails controls | None |
| 3.4 | F5 discriminator | Untestable | n/a | Long texts |
| 4.1 | Two-inventory names | Refuted | 0.60-0.85 vs 0.075 | None |
| 4.2 | Naming outlier | Weakened | Construct-dependent | New core definition |
| 4.3 | Genre match | Untestable | 0/6 | More genres |
| 4.4 | Closer = servant of | Refuted | C1 53-85% | Bilingual |
| 4.5 | CONN = son of | Refuted | 0/48 | None |
| 4.6 | Closer = ownership | Untestable | Gate 0.25 vs 0.75 | Discriminating references |
| 4.7 | Fish = deity | Untestable | AUC 0.32-0.54 | Valid statistic |
| 4.8 | Tool cluster | Refuted | p = 0.66 | None |
| 4.9 | Fixed compounds | Refuted | Missed by 0.003 | None |
| 4.10 | Genres from signs alone | Untestable at this corpus size | Methods blind below ~0.5 bits/text; Indus object type is 0.15 | Much larger corpus or a stronger model |
| 4.11 | M99 as relator | Untestable at this corpus size | Known answer found 3/100 at Indus size | About 4x more texts |
| 5.1 | Administration (14) | Refuted | Large effects only | CISI 3.1 lots |
| 5.2 | Rank ladder | Refuted | MDE rho 0.12 | More measured seals |
| 5.3 | Tablet archives | Refuted (T1, T3) | 0.96-0.98 | CISI 3.1 lots |
| 5.4 | Toponyms | Refuted | 0.83 at OR 3 | New off-home sealings |
| 5.5 | Roofed signs | Refuted at OR 3 | 0.96-0.99 | Citadel finds |
| 5.6 | Copper calendar | Inconclusive | Ring 0.38 | More copper tablets |
| 5.7 | Context C1-C5 | Refuted / untestable | Mixed | Foreign finds |
| 5.8 | Titles on door sealings | Untestable | 0.004-0.012 at 3× | 40-80 door sealings |
| 6.1 | Weight series | Refuted | n/a | Inscribed weights |
| 6.2 | Tall = 10 | Refuted | n/a | None |
| 6.3 | Numeral class | Refuted | PPC 9/9 fail | Class with 12 spike |
| 6.4 | Numeral base | Refuted | 1.00 | None |
| 6.5 | M328 measures | Refuted | ≥0.98 at rho 0.3 | Hi-res photos |
| 6.6 | Counted items | Refuted | n/a | None |
| 6.7 | Long texts as lists | Untestable | n/a | More long texts |
| 6.8 | Magnitude | Untestable | 0.15 | ~40 objects |
| 6.9 | Number-names | Weakened | 14/24 without M59 | New texts |
| 7.1 | Animal in text | Refuted | V ≈ 0.3 | None |
| 7.2 | Logograms | Refuted | 17 tests | None |
| 7.3 | Self-labels | Refuted | 1/78 | More bangles |
| 7.4 | Modifier paradigm | Refuted | ≥0.8 at +0.5 | None |
| 7.5 | Referent coherence | Refuted | n/a | None |
| 7.6 | Direction from text | Untestable | n/a | n/a |
| 7.7 | Allograph perplexity | Refuted | Fails control | None |
| 7.8 | Jar sign marks vessels | Untestable | 47% for 1.5x | HARP sherd data |
| 8.1 | Linear Elamite | Refuted | ~0.7 | More LE values |
| 8.2 | Proto-cuneiform | Refuted (strong) | 0.92-0.94 | None |
| 8.3 | Tamil Nadu graffiti | Refuted | n/a | None |
| 8.4 | Potters' marks | Untestable | 0.22-0.33 | Dated Early marks |
| 9.1 | Meluhhan names | Untestable | n = 2-5 | New texts |
| 9.2 | Mesopotamian sealings; image detector | Untestable; gate failed (recall 0.44, 0/5 controls) | n/a | Photos of 2 tablets; early-period stamp labels |
| 9.3 | Bilingual | Untestable | n/a | A find |
| 10.1 | Sign turnover | Refuted (strong) | 1.0 strong | Dated strata |
| 10.2 | Dholavira style | Refuted | n/a | None |
| 10b.1 | M328 on offering scenes | Untestable | Power 0 | ≥ 600 dpi scene tablets |
| 10b.2 | Bangle oval | Untestable | n = 0 (19 needed) | HARP bangle list |
| 10b.3 | Firing stage | Underpowered | 0.06 | HARP sherd DB |
| 10b.4 | Seal texts as identifiers | Undecidable; formula layer reversed | 0.03-0.07 (repulsion) | Lot-level groups |
| 10b.5 | City-specific sign stock | Inconclusive; large stock excluded | 0.92 whole / 0.12 slot | 3× dated Harappa seals |
| 10b.6 | Name + title formula | Not supported | 0.94 at f = 0.5 | Register-split nulls |
| 10b.7 | Omission order | Reversed | Null rho median 0.52 | Independent measurements |
| 10b.8 | Closer marks used seals | Not supported | 0.51-0.75 at OR 2 | Lothal per-impression IDs |
| 10b.9 | Repeats as re-cut/office seals | Withdrawn / reversed | n = 15 families | Dated formula seals |
| 10b.10 | Line breaks | Untestable | 0.77 / 0.51 | 150-300 true wraps |
| 10b.11 | Detached signs as a class | Not supported; covariates inconclusive | ≤ 0.32 | Face position from photos |
| 10b.12 | Direction class / slot time / animal | Untestable / inconclusive / refuted (closer type) | 0.00-1.0 | Photo direction coding |
| 10b.13 | Grammar as predictor | Not validated | Bigram wins by 0.3 bits | Annotated positive control |
| 10b.14 | Household/office signature | Refuted (two cities) | 0.90-1.0 at half strength | HARP lots |
| 10b.15 | Ticked fish by block | Weakened (lead) | 0.44 / 0 replication | More located seals |
| 10b.16 | Depth chronology | Inconclusive | 0.92-0.94 broad | HARP 3B vs 3C |
| 10b.17 | Carver hands; craft assemblage | Untestable / inconclusive | 92-100% / 0-4.5% | ≥ 30 px/mm; craft coding |
| 10b.18 | Closing slot; counted human figures | Untestable (lead) / not supported | 77/100 and 79/100 gates | New texts; fuller sign bridge |
| 10b.19 | Carver groups share text | Not confirmed (possible weak effect) | 0.83 at 40% | Blind regrouping; text-length strata |

**Interim log (entered during cycles 7-10, now folded into 10b.4, 10b.7 and section 11):**

- [2026-11-14] Cross-site short formula layer on seals (identifiers S3): reversed by red team; short repeats = chance collisions under a bigram model (145 obs vs 151 expected). Identifier repulsion (S4): test has no power for contemporaries; Ur III real identifiers cluster, so repulsion is not diagnostic.
- [2026-11-15] Graded omission order on small seals (space_and_sealing T4, reg_size): reversed by red team; closer 'kept' slopes equal a keep-one-closer random-deletion null. Only 'about one closer per text regardless of length' stands.
