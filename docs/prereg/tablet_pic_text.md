# Does a tablet's text predict its picture class? Whole objects, class level only

Agent `paper`. Main line (b), level L1. Fable's ranked study 2 of 2026-11-24. Drafted 2026-11-24.
**Status: sealed 2026-11-24 with the pre-seal results below.** Formerly a draft. No association statistic has been computed. Run code: `experiments/tablet_pic_text/run.py`.
Revised after a fresh Fable review (10 fixes applied).

## Why
- Seals: unicorn vs other from text gives AUC 0.516 (`context/q1_animal.py`). Sized in `animal_tie_power`: a +20-point single-sign tie is excluded.
- Tablets have no held-out test. `scene_text` tested sign × element pairs: 0 of 4,080 at q < 0.05, with low power.
- `anchor_ceiling` v2 and atlas §3.6: per-sign held-out profiles at 2-5 documents are untestable. So this study makes **no per-sign claim**. It asks one whole-text question per tablet type.

## Prior art (from an agent's search)
- Parpola 2008, copper tablets: the text often predicts the motif (qualitative). On seals he finds no direct relation.
- Oakes 2019 (doi:10.1080/09296174.2017.1406294, **unverified**): sign × field-symbol residuals on seals, no held-out test.
- GitHub `ADITYA-WORK-MAITI/indus-text-vs-animal` (anonymous): seals AUC 0.51.
- Kenoyer & Meadow 2010 (**unverified**): the same sequence occurs on tablets from different moulds.
- No held-out test exists for moulded or incised tablets.

## Disclosure: what was seen before this design
- **ICIT tablet records with a picture code** (`symbol` not `None`, `-` or `Unknown`). ICIT records are sides (`id` N.1, N.2, N.3), and `symbol` is copied to every side:
  - TAB:B 393 of 1,108 records = 300 objects (215 with one inscribed side, 77 with two, 8 with three).
  - TAB:I 150 of 952 records = 102 objects (58, 40, 4).
  - TAB:C 135 of 230 records = 130 objects.
- **Seen under the old side-level unit:** TAB:B 231 distinct site-texts, 16 with more than one class; TAB:I 93 and 8; TAB:C 55 and 5.
- **Seen in this revision (row building):** text types under two classes. With the six undefined codes kept: TAB:B 5 of 131, TAB:I 2 of 48. Final rows: TAB:B 2 of 59, TAB:I 1 of 24.
- **These multiplicity counts are outcome-adjacent.** They hint that one text mostly keeps one class. The number of texts with ≥ 2 pictured copies was not measured, so the hint has no denominator.
- **Code counts per type** (labels only): all codes were listed to write the mapping below.
- **Site counts** (records whose code is not `-`): TAB:B Harappa 905 of 1,056; TAB:I Harappa 899 of 928; TAB:C Mohenjo-daro 207 of 208.
- **Copper is already known in-repo, in sample** (M77 pictures, `context` Q2b, `copper_series` H3a/H3c):
  - identical-text tablets share the picture 0.62 against 0.06 null;
  - different legends that share signs do not: nearest neighbour 0.03 against 0.06 null (p = 0.81); Jaccard p = 0.12.
- **Text-only and label-only counts made for this revision:** rows per class, family sizes, strata sizes, vocabulary sizes (all below).
- **Not seen:** any text × picture statistic on TAB:B or TAB:I.

## Unit (fix 1: whole object)
- **Why:** under the old side-level unit, 55 of 264 TAB:B and 36 of 85 TAB:I objects gave two text types with one class by construction, in different families.
- **Object** = all ICIT records sharing the `id` prefix N. Sides are ordered by side number.
- **Object text** = the texts of all its inscribed sides, in side order. `seq` in Wells signs; `|` and `#` are not signs.
- **Empty-sign records are dropped** (7 on TAB:B, 4 on TAB:I, before the code drop). An object with no signs left is dropped (4 TAB:B, 1 TAB:I).
- **Text type:** identical all-sides text within site × ICIT type, among complete objects.
  - Complete = every side has `complete` true and no `#` (the `scene_text` A2 rule).
  - A broken object joins a text type only if every one of its segments is contiguous inside a side of exactly one complete text. No minimum length.
  - Other broken objects are dropped and counted.
- **One row = site × type × all-sides text of the object × coarse class.** Never one row per copy or per side.
  - A text type under two classes gives two rows. They are kept, since they are evidence against a tie. Sensitivity: drop them, as `q1.build` does.
- **Family (CV group):** text types linked within a tablet type, across sites, on the all-sides sign sequence: identical, or edit distance ≤ 1 with both ≥ 4 signs, or a ≥ 4-sign text contained in the other (every segment contiguous).
  - Chaining check (text only, done): the largest family holds 2 of 61 TAB:B rows (3.3%). The 4-sign bar stays.

## Opaque codes (fix 6, frozen now)
- **Rule A:** a code defined as a tablet form or as "no picture" is dropped. If that is TAB:I Bult, TAB:I is cancelled.
- **Rule B:** a code with no written definition is dropped.
- **Search result:** no ICIT code list exists in this repo. Searched `sources/` (all five), `docs/`, `data/`, `corpus/`. `sources/shaunmortal_indus/data/icit_iconography.csv` holds codes only, no legend.
- **Bult, Mult, Comp, Othr, Gavi, Phyt are undefined.** Only downstream guesses exist, and they disagree:
  - Bult: "unicorn" in `experiments/context/common.py` `icit_animal`; "bull" in `sources/paragorth_Indus-/tools/strat_gulfmotif.py`.
  - Gavi: "gharial" in `common.py`; "bull" in `strat_gulfmotif.py`.
  - Mult and Comp: "composite" in `strat_gulfmotif.py`; "animal" in `experiments/detached_signs/d2_covariates.py`.
  - Phyt: "plant" in `strat_gulfmotif.py` and `experiments/logograms/l3_iconic_seals.py`.
  - Othr: "other picture" in `experiments/logograms/l1_copper_catalogue.py`; on copper it covers the ox-antelope legend (`logograms/RESULTS.md`).
- **Applied:** all six, and Gavi+Bult, are dropped under Rule B.
- **TAB:I is cancelled.** Its test was Bult against the others. Without Bult it has 25 rows (Fish 17, rest 8), 7 signs and 2 bigrams in ≥ 5 rows. Reported descriptively only.
- Rule A was not triggered, since Bult has no definition at all.
- **If the ICIT code list is found before sealing,** defined picture codes return and Rule A is applied. Counts with all six kept (Othr dropped): TAB:B 136 rows (multiple 25, plant 22, bovine 22, aquatic 21, figure 19, Bult 12, geometric 8, other animal 7), 117 families; TAB:I 50 rows (Bult 21, Fish 17, rest 12), 46 families.

## Frozen mapping, ICIT code → coarse class (objects in brackets)
- **TAB:B (300 objects, 140 kept):**
  - bovine: Bull1, Bull1:I, Bull1:S, Bull1:U, Bull, Bull2, Gaur, Zebu (60)
  - figure: Scene, Anth (31)
  - geometric: Cros, Xcrs, Maze, Tri4, Xhch, Crs, T, Swas, T-A-T, Box, Strokes (27)
  - other animal: Rhin, Goat, Goat:4, Goat:6, Elep, Bird (14)
  - aquatic: Fish, Turt (7)
  - plant: Pipal (1)
  - dropped, undefined: Mult 58, Gavi 43, Phyt 43, Bult 14, Othr 2 (160)
- **TAB:I (102 objects, 35 kept, cancelled):** Fish 24; rest: S590, Pipal, Goat, Goat:2, X, Gaur (11); dropped: Bult 55, Gavi 9, Mult 1, Gavi+Bult 1, Othr 1.
- **TAB:C (130 objects):** descriptive only. Othr 54 and Comp 8 are undefined.

## Rows and eligibility (fix 3, frozen)
- **TAB:B:** 139 objects with signs → 22 broken objects dropped, 2 joined → 117 objects in 59 text types → **61 rows, 57 families** (53 of one row, 4 of two).
- **Rows per class:** bovine 21, figure 19, geometric 8, other animal 7, aquatic 5, plant 1.
- **Eligible class:** ≥ 15 rows. **Eligible: bovine and figure** (40 of 61 rows). The other 21 rows are "rest".
- **Vocabulary:** 13 signs and 3 bigrams occur in ≥ 5 rows.
- **Strata, site × length bin:** Harappa 6 / 13 / 22; Mohenjo-daro 3 / 3 / 9; other sites 1 / 1 / 3 (bins 1-2, 3-4, ≥ 5 signs).
- **Rows by inscribed sides:** one 39, two 21, three 1.
- **Size** (width and height) is known for 72 of the 117 objects. The review counted 174 of 298 before the code drop.
- **Label reliability gate (labels only, before sealing):** where `scene_text` has consensus rater codes, compare them with the coarse class (figure ↔ scene or human). A class with κ < 0.6 is moved to "rest".

## Features and model (fix 10, frozen)
- Text only: signs present, initial sign, final sign, bigrams. Initial and final are taken per side.
- **Vocabulary:** items in ≥ 5 rows, built once from all rows. Labels are not used.
- No length features, no stroke classes, no site, no object size.
- **One multinomial L2 logistic model** (C = 0.3, balanced class weights). Classes: bovine, figure, rest. "Rest" is a class.
- **CV:** `StratifiedGroupKFold`, 5 folds, groups = families, seed 20261124.
- **Score:** out-of-fold probabilities pooled over the 5 folds, then one-vs-rest AUC per eligible class. "Rest" gets no score term.
- **Under permutation:** folds are rebuilt on the permuted labels with the same seed. Every permutation runs the full pipeline.
- **Seeds:** CV 20261124; main null 1; stricter null 2; plants 3; false-alarm A 4, B 5; Linear B subsample 0.
- **p = (1 + b) / (1 + N),** with b = null values ≥ the real value.

## Main test
- **One confirmatory test: TAB:B,** macro pooled out-of-fold AUC over bovine and figure. The bar stays p < 0.025.
- **Null:** 1,000 permutations of class labels within site × length bin (1-2, 3-4, ≥ 5 signs). Sites with < 5 rows pool into "other".
  - Length is the confound control: inside a bin, length cannot produce signal.
  - A length-only model is reported beside the main one.
- **Effect size:** excess AUC = real AUC minus the null mean.
- **Reported, not tests:** per-class AUC, leave-Harappa-out, conflicts dropped, exact-text grouping, TAB:I and copper tables.

## Positive control: Linear B (fix 2)
- **Gate C1 is deleted.** Copper fails its own rule: under 30 rows, largest class under 15, 7 signs and no bigram in ≥ 5 rows.
  - C1 also passed only through near-copies straddling folds, which the main CV closes.
  - `context/RESULTS.md` calls the ICIT copper `symbol` unreliable.
- **Control:** Linear B subsample 0 of `animal_tie_power`, cut to the TAB:B row count (61), through the identical family-grouped pipeline: same features, model, CV, null and p rule.
- **Pass:** it beats its null's 99th percentile.
- **If the control fails:** the method is broken. No tablet claim of either sign is made.
- **Copper is descriptive.** A table of legend × picture from M77 pictures. No gate, no test.

## Kill test first (before any real statistic)
- **Label-swap plants on the real tablets**, as `animal_tie_power` Leg A. Texts are never edited.
  - **Each draw starts from block-permuted labels** (defined below), so the real association is never read and near-copies keep a shared picture.
  - Pick a class A and a tie sign g (uniform over the 13 signs in ≥ 5 rows). Inside each stratum, swap labels between A rows lacking g and non-A rows having g, until the share of A carrying g is its natural rate + δ.
  - Ladder: δ = 0.05, 0.10, 0.20, 0.40. 40 draws per rung, per eligible class.
  - **A rung counts only with ≥ 30 of 40 feasible draws.** A rung below 30 has no power value. Infeasible draws are reported.
  - **Plants use one fixed 1,000-permutation null,** computed once. No fresh null per draw.
- **Power** = share of feasible draws that pass the main test. **c\*** = smallest counted δ with power ≥ 0.8, per class.
- **Calibrated scale.** Mean planted excess AUC per rung is set against Linear B's excess: 0.131-0.139 for full lines (δ 0.23-0.24 on the seal ladder), 0.042-0.074 with formula words removed.
- **Bands (frozen):**
  - powered: eligible classes with c\* ≤ 0.20 together hold ≥ 50% of rows. Here that needs both bovine and figure;
  - gross ties only: the same share is reached only at c\* = 0.40;
  - underpowered: neither. STOP, no real run.
- **Block null (fix 8).** Each family's label vector is its rows' labels in row order. Label vectors swap among families of the same size, within the stratum of the family's first row. Rows are ordered by site, then text.
- **False-alarm checks** (fix 9: 400 draws each, bar ≤ 16 passes at p < 0.025):
  - A: labels permuted within strata, tested as real;
  - B: block-permuted labels, tested as real. This keeps "near-copies share a picture" and removes any text tie. If B fails, the block null replaces the main null and the kill test is rerun.
- `kill.json` is committed before the real run.

## Frozen readings
- **Positive** (kill passed, control passed, p < 0.025 on TAB:B). It stands only if (fix 5):
  - p < 0.05 survives a second null, stratified also by inscribed-side count (one, two or more) and material. Strata under 5 rows pool on material first, then on side count;
  - p < 0.05 survives each leave-one-class-out run (bovine out, figure out).
  - If both hold: "the first held-out function tie on tablets". It is L1, not a reading, and names no sign.
  - Otherwise: **"format-confounded, no claim".** Size cannot be a stratum: it is known for 72 of 117 objects.
  - Red team before any wording: leave-one-site-out, conflicts dropped, block null.
  - RESEARCH_STATE: main line (b) gets its first L1 positive. Next is a frozen prediction for CISI vol. 3 tablets.
  - Scorecard: no row moves by itself. Run `staleness.py`; flagged rows are re-rated blind.
  - Atlas 5.7: "the seal null does not extend to tablets".
- **Powered null** (kill passed, control passed, p ≥ 0.025): "no sign-level tie shared across unrelated legends at ≥ c\*; a whole-legend label, as on copper, is untested and open."
  - In the gross band, the same sentence with δ ≥ 0.40 only.
  - RESEARCH_STATE: next is study 3 (edition sweep).
  - Scorecard: c\* becomes the floor for any tablet picture × text claim. Rows below it stay U.
  - Atlas 5.7 gains a tablet line. Name-like texts under an emblem are still not excluded.
- **Underpowered:** "untestable at this object count". A new atlas entry, no scorecard change, main line (b) unchanged. Reopen with CISI vol. 3.
- **Control failed:** "method broken". Nothing is said about tablets.
- TAB:I gets no reading.

## Limits stated in advance
- **Same text, different mould.** ICIT has no mould id. A text type stands in for a mould, so two moulds with one text and one class count once. The count of moulds is a lower bound.
- **ICIT picture codes.** One coder, no reliability figure, no code list in hand. 160 of 300 TAB:B objects are lost to undefined codes.
- **Scope.** The test covers bovine and figure tablets against the rest. It says nothing about the dropped codes.
- **Small sample.** 61 rows, 13 signs. The kill test may well stop the study.
- **Site.** TAB:B is almost all Harappa. A result is about Harappa workshops.
- **Class level.** A positive says the vocabulary differs by picture class. It cannot say which sign carries it.
- **Plants** tie one sign to one class. Ties spread over several signs are harder to see and are not planted.
- **Format.** Text and picture may both follow the tablet's shape or size. Length bins, side count and material control only part of that.

## Pre-seal results (2026-11-24, labels and text only; no association statistic computed)
- **ICIT code list:** not found. The open ICIT help PDF (TU Berlin, `help_onlinedatabase.pdf`, opened) defines no picture codes. The Fuls *Corpus of Indus Inscriptions* page on ResearchGate returned 403; not pursued. Rule B stands: 61 rows.
- **Label reliability gate** (`run.py gate`, `gate.json`): 44 kept TAB:B objects have `scene_text` codes. ICIT figure against consensus scene or human: both 7, ICIT only 11, raters only 0, neither 26. **κ = 0.43 < 0.6. Figure moves to "rest"** under the frozen rule.
  - The disagreement is one-sided (raters never saw a figure ICIT lacks). It may be rater misses on about-100-ppi photos (`scene_text` RESULTS lists such misses). The rule is applied as frozen anyway.
  - Bovine has no `scene_text` code and stays ungated.
- **Consequence:** the only eligible class is bovine, 21 of 61 rows (34%). The "powered" and "gross" bands need eligible classes holding ≥ 50% of rows, so **neither band can be reached. By the frozen bands the study is underpowered: STOP, no real run, no Linear B control.**
- **Row check:** `run.py rows` reproduces 139 objects, 22 broken dropped, 2 joined, 59 text types, 61 rows, 21 bovine, 19 figure, 13 tie signs, 3 bigrams. Families come out at **59** (57 of one row, 2 of two: the two texts under two classes), not the 57 stated above. The code follows the written linking rule. The earlier count is not reproduced.
- **Kill test kept as a descriptive sizing run** (amendment, made before any statistic): bovine vs rest, binary, all else as frozen. It gives bovine c\* at 61 rows, to decide whether CISI vol. 3 makes a reopen worthwhile. It cannot change the STOP. False-alarm checks A and B run as frozen.

- **Fresh Fable review of this amendment and `run.py` (2026-11-24).** STOP confirmed, no result-changing bug. Fixes applied:
  - plants overshoot through `ceil` (nA = 21: realised δ 0.095 / 0.143 / 0.238 / 0.429). Realised δ is recorded per draw and reported beside each nominal rung;
  - feasible plant draws with the frozen seeds are 38, 34, 20 and 1 of 40 (labels only), so the 0.20 and 0.40 rungs cannot count. **Bovine c\* can only come out 0.05, 0.10 or none.** A "none" means "not powered at δ ≤ 0.10", not "unpowered at every δ";
  - draws with an undefined AUC are counted apart from infeasible ones; `gate.json` is required.
- **Disclosed, not acted on:**
  - the gate rests on 18 figure objects; raters coded neither scene nor human on 8 of 13 "Scene" and 3 of 5 "Anth", a pattern closer to rater misses than ICIT error;
  - 140 objects share 131 CISI numbers, so gate objects are not fully independent; the gate runs on objects (including broken ones), not rows;
  - families: a per-side reading of "(every segment contiguous)" gives 55 families with one 4-row family. Neither reading gives the draft's 57. One bovine pair (Harappa `220 032 700 / 803 240 415 220 520` and `415 220 520`) is in two families under the frozen reading and can straddle folds;
  - plant swaps can split a near-copy pair's labels.

## Before sealing
- Look for the ICIT code list outside the repo. If found, redo the mapping and the counts.
- Run the label reliability gate.
- Hash this file and `run.py` in `HASHES.txt` (tag `tablet_pic_text`).

## Cost
- About 1,000 fits for the main null, 3,000 for the stricter null and leave-one-class-out, 1,000 for Linear B, 320 for plants, 800 for false-alarm checks. Under 1 s each.
- Under 1 hour on 4 workers, `nice -n 20`, under the Indus compute lock.
