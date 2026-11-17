# Project-wide multiple-testing ledger

Statistical audit, 2026-11-14. Code:
- `build_ledger.py`: the ledger rows and every correction.
- `v2_reruns.py`: own reimplementation of the cheap v1-only claims on `dev_heldout(version=2)`.

Outputs: `docs/test_ledger.csv` (one row per test), `results.json`, `v2_reruns.json`. Run from the repo root with `.venv/bin/python -I experiments/ledger/v2_reruns.py`, then `build_ledger.py`.

## Conclusion first

**Six of the nine README findings survive every correction scheme, including BH over all ~14,100 tests the project ran. Two survive only in weakened form, and the functional-reading claim needs restating.**

1. **Survive everything (global BH, hierarchical BH, and all-test BH with unlisted tests padded at p=1):**
   - #1 sign order;
   - #5 six + fish;
   - #6 object-type vocabularies;
   - #4 Gulf round seals;
   - #7 L-R reversals (the direction part only);
   - #3 ticked fish (survives on the ICIT test; the clean v2 replication survives global and hierarchical BH but not all-test BH).
2. **Need restating:**
   - **#7, jar in both directions.** "33 vs 3" counts copies. On the 34 copy-free L-R lines the jar is last 5 times and first 0 (p=0.031, q_global=0.18). It survives only under per-area correction.
   - **#9, functional reading.** Coverage of unseen texts survives on v2 (0.762 vs 0.438 for shuffles, z=20, q≈1e-89), but the shuffle margin shrinks from 43 to 32 points. **The test that the lexicon itself matters does not survive:** v2 coverage vs permuted role sets gives p=0.013, q_global=0.085. The parse shows that positional classes exist, not that these 11 role assignments are right.
3. **#8, copper sign face (8/8, p=1e-4), was never a confirmatory test.** It is all-data and has not been red-teamed. It survives all-test BH (q=0.02), but it should be labelled exploratory. The related red-team result, legend copies sharing one picture, survives (q=0.002).
4. **#2, logo-syllabic, is descriptive and has no test or null.** Typology's interval tests (v2 held-out) are the nearest support: core signs stand alone as whole cores 80% of the time vs at most 14% in every syllabic or name corpus.
5. **Per-area correction rescued six confirmatory results that fail global BH:**
   - ticked fish vs a frequency-matched null (q 0.11);
   - one ticked-fish pair (W231/W232);
   - 7 + fish depletion (q 0.11);
   - the functional-reading lexicon null on v2 (q 0.085);
   - numerals avoid marked fish on v2 (q 0.079);
   - jar last in copy-free L-R lines (q 0.18).

   None of these is a README headline except inside #7 and #9.

Counts:
- 275 ledger rows: 180 confirmatory and 95 exploratory, 241 with a p-value.
- Of 162 confirmatory p-values, 99 are nominally below 0.05. Survivors at q<0.05: 80 under global BH, 83 under per-area BH, 84 under hierarchical BH.
- The global BH uses m=553 after padding unlisted family members. The all-test BH uses m=14,108; 78 tests survive it.

## Method

**Ledger.** Every test that a RESULTS.md reported with a p-value, a z-score, counts or a CI got one row. Teams that reported "ran N tests" without listing them got a family summary row; the unlisted members are padded at p=1 in every correction, which is conservative.

Columns:
- claim, area, file, statistic, p_value (with source), ci, n;
- distinct-text unit (yes/no);
- split: `v1 leaky`, `v1 copies removed`, `v2`, `ICIT`, `ICIT new sites` or `none`;
- mode (confirmatory/exploratory);
- family and family_size;
- replicated_independently;
- the README claim the test supports;
- q_global, q_area, q_hier, q_all.

**p-value conventions:**
- z-scores are converted to one-sided normal p.
- Where only counts were reported, the ledger computes a one-sided binomial p (marked `ledger-computed`).
- Permutation floors are used as reported.
- Tests reported only as intervals (typology H1-H4, structure's frequency profile, context's numeral CIs) have no p and are excluded from BH.

**What counts as confirmatory:** a hypothesis fixed before the data that tested it were seen. That covers pre-registered tests, frozen predictions, held-out tests of a dev-derived claim, and independent red-team or revalidation re-tests. Dev-only tests, all-data tests and screens are exploratory.

**ICIT is a second transcription of mostly the same objects,** so an ICIT re-test counts as confirmatory but is never marked "replicated independently". ICIT tests restricted to sites absent from M77 (Dholavira and others) count as new objects.

**Corrections:**
- **Global:** BH over all confirmatory tests project-wide.
- **Per area:** BH within each team folder. This is the correction teams effectively applied, or less.
- **Hierarchical (Benjamini & Bogomolov 2014):**
  1. A Simes p for each of 37 families.
  2. BH across families at 0.05; 20 families are selected.
  3. Within selected families, BH at 0.05·20/37, reported as q scaled by 37/20.
- **All tests (sensitivity):** BH over every test, exploratory included, plus the ~13,900 unlisted screening tests at p=1. The largest blocks are context's 11,232-test register screen, the 835-test sign × picture scan and the 444 positional and structure screens.

## Defensible findings (q from `docs/test_ledger.csv`)

| # | Finding | Best confirmatory evidence | p | q_global | q_hier | q_all |
|---|---|---|---|---|---|---|
| 1 | Sign order is grammatical | v2 held-out: 129/321 best-of-permutations vs 5.7% | 1e-73 | 8e-72 | 2e-72 | 2e-70 |
| | | copy-free held-out, 5 fixed signs deleted (red team) | 2e-100 / 5e-11 | 2e-98 / 1e-9 | <1e-9 | <1e-7 |
| | | Dholavira only (new objects) | 4e-19 | 1e-17 | 4e-18 | 3e-16 |
| 5 | Six + fish (M109 M59) is a fixed expression | v2 held-out 7/10 vs 3% | 2.8e-9 | 6e-8 | 1e-8 | 1e-6 |
| | | M77 12/25; ICIT 13/33 | 9e-9 / 4e-9 | 2e-7 / 7e-8 | 4e-8 | 3e-6 |
| 6 | Object types have their own vocabulary | v2 AUCs (exact Mann-Whitney): seal, copper, tablet, sealing, pottery | 3e-15 to 1e-4 | 8e-6 to 1e-3 (pottery) | <3e-4 | <0.021 |
| | | rod formula M342-M176 (red team); W407 on copper; W740-W400 on tablets | 1e-6; 1e-9; 1e-5 | 1e-5; 2e-8; 1e-4 | <5e-5 | <0.003 |
| | | 10 of 17 M77 register markers replicate on ICIT | 3e-27 to 2e-4 | <0.003 | <0.001 | <0.042 |
| 3 | Corner ticks move a fish sign to the closing slot | ICIT within-text shuffle 40/73 | 1.1e-7 | 2e-6 | 7e-7 | 4e-5 |
| | | v2 held-out 11/19 | 0.004 | 0.029 | 0.007 | 0.54 |
| 4 | Gulf round seals break Indus order | ledger re-run: perm-percentile 0.59 vs 0.90 for length-matched peripheral seals, site held out | 5e-4 (perm floor) | 0.005 | 0.002 | 0.086 |
| | | functional reading: Gulf round bigram bits AUC (ICIT) | 5e-4 | 0.005 | 0.014 | 0.086 |
| | | context Q4 (+2.17 bits; exploratory, splices across breaks) | 1e-4 | n/a | n/a | 0.02 |
| 7a | L-R lines are real reversals | 31/34 copy-free lines (red team) | 4e-7 | 6e-6 | 3e-6 | 1e-4 |
| | | same with positional signs removed; ICIT copy-free 18/23 | 0.002; 0.005 | 0.016; 0.035 | 0.007; 0.012 | 0.30; 0.62 |
| 9a | Positional role classes generalise | v2: role grammar coverage 0.762 vs 0.438 (ledger) | 2e-91 | 1e-89 | 2e-90 | 2e-88 |
| | | v2: K=3 positional classes from dev agree on 78% of held-out signs vs 42% (ledger) | 1e-4 (floor) | 0.001 | 5e-4 | 0.02 |

Reading the q_all column:
- Findings #1, #5, #6, #7a and #9a survive even when every unlisted screening test is counted.
- #3 survives through its ICIT test.
- #4 is at q=0.086 under all-test padding. It reaches q<0.05 under global and hierarchical BH, plus context's exploratory q_all=0.02.

## Claims to demote

| Claim (where) | Problem | Ledger evidence |
|---|---|---|
| Jar closes L-R texts "33 vs 3" (README #7) | counts copies of R-L lines; copy-free lines give 5 vs 0 | p=0.031, q_global 0.18; survives only per area (q 0.036) |
| Functional reading: the 11-role lexicon is right (README #9) | beats permuted role sets only weakly, on v1 and on v2 | v1 p=0.01, q 0.066; v2 p=0.013, q 0.085 |
| Functional reading predicts object type better than a bag of signs | refuted by its own team | delta -0.073 [-0.114, -0.037] |
| "Parses 76% vs 33% for shuffles" (README #9) | v1 leaky; shuffle baseline 0.33 rises to 0.44 on v2 | v2 0.762 vs 0.438 |
| Ticked fish final at sites absent from M77 | 5/10 | p=0.07, q 0.36 |
| Ticked fish vs frequency-matched null | per-area only | p=0.018, q_global 0.11 |
| 7 + fish depleted | per-area only; red team calls it a base-rate effect | p=0.017, q_global 0.11 |
| M99 enriched on seals, W002 on seals | null | p=0.07, 0.23 |
| Copper legend "names the picture" (logograms T3, README #8) | all-data, exploratory, never red-teamed; ICIT overlaps M77 objects | p=1e-4, exploratory only; q_all 0.02 |
| Held-out order "63% vs 5.5%" and "1e-24" direction magnitudes (structure) | v1 copies; the 1e-24 is over lines that are 77% copies | v2 40% vs 5.7%; copy-free 31/34 |
| Template fit 66.8% vs 24.8% (structure) | circular: classes defined by the positions the shuffle destroys | exploratory |
| Dholavira regional pairing (structure) | broken by a site-held-out control | red team |
| Seal animal predictable from text (context Q1 held-out) | v1 p=0.035 disappears on v2 | v2 bal. acc 0.194 vs 0.145, p=0.093 |
| Goat-antelope legends are short (context) | exploratory, ICIT only (M77 p=0.062) | q_all 1 |
| Numerals avoid marked fish (language P4) | weakened on v2 | v1 p=0.003 -> v2 p=0.012, q_global 0.079 |
| M99 never dropped, M176 droppable (phonetic_grid) | v1 held-out pairs were leaked near-copies; v2 has too few within-family events to test (internal_phonetics counts 46) | untestable on v2; keep as dev-only |
| Held-out substitution classes 91 vs 36 (novel_methods) | same leak; held-out swaps were copies | untestable on v2 |
| Allograph merges validated by perplexity (structure) | non-look-alike merges do as well | p=0.67 control |
| Gulf reduplication (typology G2/G3) | two texts doubling the jar | G3 survives global (q 0.029) but fails hierarchical and per-area; G2 q 0.066 |
| Yajnadevam strict match p=0.040 (language) | one of 4; fails every correction | q_global 0.22 |
| Finnish/Estonian z=2.3 on real Indus (decipherability) | best of 22 runs | q_global 0.17 |

## README claims that used split v1 only

| README claim | v1 evidence | Re-tested by red team / v2? | Ledger re-run on v2 (own code) |
|---|---|---|---|
| #9 functional reading coverage | 0.760 vs 0.334 | no | **0.762 vs 0.438, z=20.3; Dholavira 0.786 vs 0.458.** Reproduces v1 at 0.763 |
| #9 lexicon vs permuted roles | p=0.01 | no | **p=0.013 (300 perms), fails global BH** |
| #7 jar in both directions | 33 vs 3 (all lines) | red team checked direction only | **copy-free 5 vs 0, p=0.031** |
| #8 copper sign face | no split | no | not a split question; flagged as exploratory |
| Positional classes (structure, behind #9) | 87.5% vs 47% | no | **78.2% vs 41.7%, p<1e-4** |
| Animal emblem not written (refuted list) | v1 weak positive p=0.035 | no | **p=0.093: the weak positive disappears, which supports the README** |
| Gulf (#4) | red team gave no exact p | yes (percentile only) | **p=5e-4 vs length-matched site-held-out peripheral seals** |
| #6 register AUCs | v2 | yes | exact Mann-Whitney p added: 3e-15 (seal) to 1e-4 (pottery) |

## Proposed README edits

```diff
@@ What we can defend
-Ranked by strength after an independent red-team reimplementation and a re-test on a held-out split with zero near-copy leakage (`experiments/revalidation/`).
+Ranked by strength after an independent red-team reimplementation, a re-test on a held-out split with zero near-copy leakage (`experiments/revalidation/`), and a project-wide multiple-testing ledger (`docs/test_ledger.csv`, `experiments/ledger/`). q = Benjamini-Hochberg over all 553 confirmatory tests (unlisted tests padded at p=1).
@@
-| 1 | **Sign order is grammatical, not positional.** ... | clean held-out: 40% of 321 runs vs 5.7% chance; red team 42% vs 3% | structure, redteam |
+| 1 | **Sign order is grammatical, not positional.** ... | clean held-out: 40% of 321 runs vs 5.7% chance (q<1e-70); red team 42% vs 3% | structure, redteam |
-| 3 | **Corner ticks on a fish sign move it to the closing slot** ... | ICIT native: final in 40 of 73 vs 26% expected, p=1e-7; clean held-out 11/19 final vs 7% for plain fish, p=0.004 | novel_methods, redteam |
+| 3 | **Corner ticks on a fish sign move it to the closing slot** ... | ICIT native: final in 40 of 73 vs 26% expected, p=1e-7 (q=2e-6); clean held-out 11/19, p=0.004 (q=0.03). Not yet seen at sites absent from M77 (5/10, p=0.07) | novel_methods, redteam |
-| 4 | **Gulf round seals break Indus sign order** ... | +2.17 bits/sign (95% CI 1.63-2.70); permutation percentile 0.53 vs 0.87-1.00 at every Indus site | context, redteam |
+| 4 | **Gulf round seals break Indus sign order** ... | +2.17 bits/sign (95% CI 1.63-2.70); permutation percentile 0.59 vs 0.90 for length-matched peripheral seals with their site held out, p=5e-4 (q=0.005; n=10 seals) | context, redteam, ledger |
-| 6 | **Each object type has its own vocabulary** ... | clean held-out AUC: copper 0.87, tablet 0.76, pottery 0.73, seal 0.72, sealing 0.67 (all above permutation 95th pct 0.55-0.61) | context, redteam |
+| 6 | **Each object type has its own vocabulary** ... | clean held-out AUC: copper 0.87, tablet 0.76, pottery 0.73, seal 0.72, sealing 0.67 (q from 1e-3 to 1e-13) | context, redteam |
-| 7 | **Left-to-right texts are real reversals**, and the jar M342 closes texts in both directions. | 31 of 34 copy-free lines; jar last 33 vs first 3 | structure, redteam |
+| 7 | **Left-to-right texts are real reversals.** The jar M342 also tends to close L-R lines, but on copy-free lines the count is small. | 31 of 34 copy-free lines (q=6e-6); jar last 5 vs first 0 on copy-free lines (p=0.03, q=0.18; 33 vs 3 counts copies) | structure, redteam, ledger |
-| 8 | **Copper tablets come in about 18-64 fixed text + picture types**; a one-sign face can stand in for the picture, consistently within a legend. | same legend -> same sign face 8/8, p=1e-4 | context, logograms |
+| 8 | **Copper tablets come in about 18-64 fixed text + picture types**; a one-sign face can stand in for the picture, consistently within a legend. | legend copies share one picture 0.90 vs 0.39, p=2e-4 (red team, q=0.002); same legend -> same sign face 8/8, p=1e-4 (all-data, exploratory, not red-teamed) | context, logograms |
-| 9 | **Functional reading of every text**: 11 roles (...). Parses 76% of unseen texts vs 33% for shuffles, and 77% at sites absent from M77 incl. Dholavira. | ... | functional_reading |
+| 9 | **Positional role classes generalise; the full 11-role reading is a working hypothesis.** 11 roles (...). Parses 76% of clean held-out texts vs 44% for shuffles (q<1e-80), and 77% at sites absent from M77 incl. Dholavira. The specific role assignments beat permuted role sets only weakly (p=0.013, q=0.085). | ... | functional_reading, ledger |
@@ What is refuted or unsupported
-- **Animal emblems are not written in the seal text** (context).
+- **Animal emblems are not written in the seal text** (context; the weak v1 held-out signal, p=0.035, is gone on the clean split, p=0.09).
+- **No relational administrative reading holds:** no person graph, no precinct-bound offices, no dated tallies, no Lothal commodity logograms (0 of 14 pre-registered tests, administration).
+- **Spelling variation leaks no sound values** (no complements, homophones or ligatures; weak negative given low power, internal_phonetics). **Sign pictures do not predict grammar,** and copper substitution signs do not resemble the pictures they replace in a blind test (iconography).
@@ Known weaknesses
-- Wave-1/2 held-out tests used split v1, which leaked near-copies; the top claims were re-run on v2 (`experiments/revalidation/`).
-- About 13,000 tests sit behind about 60 headline claims across teams, with no project-wide correction. Only claims that replicated on an independent transcription or on clean held-out data are ranked above.
+- Wave-1/2 held-out tests used split v1, which leaked near-copies. The top claims were re-run on v2 (`experiments/revalidation/`, `experiments/ledger/`). Claims that rest on held-out near-copy pairs (phonetic_grid's M99/M176 drop rates, novel_methods' substitution classes) cannot be tested on v2 and stay dev-only.
+- About 14,100 tests were run. `docs/test_ledger.csv` lists 275 of them with global, per-area, hierarchical and all-test BH q-values. Findings 1, 3, 5, 6 and the direction part of 7 survive BH over all tests; 4 and 9 survive BH over confirmatory tests.
-- Iconic judgements of sign drawings (e.g. M184 = rhinoceros, M346 = goat-antelope) were not blind and use drawings, not photographs.
+- Iconic judgements of sign drawings (e.g. M184 = rhinoceros, M346 = goat-antelope) did not survive a blind test with photographs (iconography: 5/24 vs 3.3 expected, p=0.22), though the raters were language models.
```

## Caveats

- **Transcription.** Most p-values are transcribed from RESULTS.md files, not recomputed. Where a team gave counts but no p, the ledger computes a one-sided binomial p against the stated base rate, which ignores clustering within texts.
- **Mode and family size are judgement calls.** The rules are stated above, and each row's mode and family can be changed in `build_ledger.py`. Families of unknown size (e.g. "about 50 tests") were set to the stated number.
- **Permutation floors (p=0.01 with 100 permutations, 1e-4 with 10,000)** cap how small some q-values can get. The Gulf re-run is at its floor (1/20,001); its normal-approximation p is 6e-6.
- **Not included:** `experiments/cognate_decipher` had no RESULTS.md when this ledger was built. Typology's interval criteria H1-H4 carry no p and are excluded from BH.
