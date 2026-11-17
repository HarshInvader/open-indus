# Grammar: a validated positional grammar of the Indus seal text (fable plan 6, part B)

Pre-registration: `docs/prereg/grammar.md`, hashed 2026-11-15T04:52:41Z (tag `grammar`) before any held-out run.
Readable grammar: `docs/GRAMMAR.md`. Numbers: `results.json`, `validate_final.json`. Model: `grammar.json`.

## Findings

1. **The Indus text has real positional structure, and a 16-class grammar captures it on held-out text.** On
   441 complete held-out M77 texts the grammar scores 5.79 bits per sign. It beats position-only (6.38; diff
   -0.59 bits, 95% CI -0.68 to -0.50), unigram (6.29) and the same pipeline trained on shuffled texts (6.25;
   -0.46, CI -0.53 to -0.38). Shuffling the held-out texts themselves raises the grammar's cost to 7.07 bits.
2. **A plain sign bigram still predicts better (a1 failed, as expected).** Kneser-Ney bigram: 5.49 bits.
   The grammar is worse by +0.30 bits (CI +0.23 to +0.37). It uses 522 parameters against 2,734. BIC favours
   the grammar (67,510 vs 74,438); AIC favours the bigram (55,025 vs 63,803). The grammar is a compact
   description, not the best predictor.
3. **Restoration: good at the slot, weak at the exact sign.** Hiding one sign at every position (1,942 cases):
   - Exact sign in the top 5: grammar 0.35, bigram 0.48, position-only 0.25.
   - Functional slot correct at top 1: grammar 0.66, bigram 0.69, position-only 0.59.
   - Fine class in the top 5: 0.75.

   The grammar beats position-only (b1, b3 pass). It is clearly worse than the bigram on identity (b2 fails:
   -0.13, CI -0.16 to -0.11).
4. **Transfer: it holds at other sites, and on new ICIT sites it nearly catches up with the bigram.**
   - Trained on Mohenjo-daro, the grammar beats position-only at Harappa (-0.70 bits) and at the small sites
     (-0.59).
   - Trained on M77, it beats position-only at ICIT-only sites (-0.31).
   - The deficit to the bigram:

     | | Mohenjo-daro / M77 itself | Harappa | Small sites | ICIT-only sites |
     |---|---|---|---|---|
     | Grammar minus bigram (bits) | +0.39 | +0.42 | +0.27 | +0.06 (CI -0.04 to +0.15) |

   - So c-pos passes. c-big fails. c-gap fails only because of Harappa.
5. **Negative control passes.** Gulf round seals cost +1.80 bits per sign more than native Indus seals of
   equal length (7.30 vs 5.50; p = 0.0001; AUC 0.85; n = 18). Format alone accounts for only +0.18: Indus
   round seals score that much worse than Indus square seals. Foreign square seals are not significantly
   worse (+0.20, p = 0.36, n = 8).
6. **Positive control: half passes.** On Ur III seal legends the same pipeline recovers the slot structure:
   - NMI with the gold slots is 0.567. All 20 shuffled-training nulls stay at or below 0.469 (e1 passes).
   - It isolates the "son of" relator (KIN 1.00).
   - It splits "servant of" between two classes (SERV 0.59), so e2 fails and primary (e) fails. The dry run
     predicted this; the secondary KIN-only test passes.
   - At Indus training size, the Ur III class grammar ties the bigram (-0.09 bits, CI -0.26 to +0.05). On the
     Indus texts it loses by +0.30. Indus texts therefore carry more sign-specific pair structure than a
     16-class grammar holds, more than a real name-and-title genre does.
7. **Validated classes (stable across 200 bootstraps and across the M77 and Wells lists).**

   | class | signs | share of tokens | main signs |
   |---|---|---|---|
   | opener | 10 | 7.3% | M267, M391, M293 |
   | connective | 2 | 7.6% | M99, M123 |
   | medial | 85 | 34.8% | M59, M67, M336, ... |
   | closer | 7 | 14.1% | M342, M211, M15 |

   - Agreement between the two sign lists on bridged signs: 0.645. A permutation null gives a mean of 0.379
     (95th percentile 0.422).
   - Numeral and post-closer classes appear but are not stable, so they were dropped.
   - 36% of tokens stay unclassified.
8. **Object type and face size.** Text length grows by about 1.2 signs per doubling of seal-face area
   (slope CI 0.23 to 0.32, 931 seals). Per-object-type transitions helped in dev cross-validation (tablets
   +0.21 bits, copper +0.15). On held-out text they made things worse (+0.05 bits, CI +0.02 to +0.07), so a3
   fails.

## Pre-registered decisions

| test | result | numbers |
|---|---|---|
| a1 grammar beats bigram, fewer parameters | FAIL (expected) | +0.303 [+0.231, +0.372]; k 522 vs 2,734 |
| a2 beats position-only and shuffled-trained grammar | PASS | -0.589 [-0.676, -0.501]; -0.458 [-0.533, -0.381] |
| a3 register-aware beats pooled | FAIL | +0.046 [+0.023, +0.069] |
| b1 top-5 identity above position-only | PASS | 0.345 vs 0.252, +0.093 [+0.073, +0.113] |
| b2 top-5 within 0.03 of bigram | FAIL (expected) | 0.345 vs 0.479, -0.134 [-0.156, -0.111] |
| b3 slot label top-1 >= 0.60 and above position-only | PASS | 0.664; +0.077 [+0.048, +0.105] |
| c-big beats bigram on every target | FAIL (expected) | +0.42 / +0.27 / +0.06 / +0.14 / +0.12 |
| c-pos beats position-only on every target | PASS | all CIs below 0 |
| c-gap deficit smaller than in-domain on every target | FAIL (Harappa) | Harappa +0.03, others -0.12 to -0.33 |
| d Gulf round seals worse, p < 0.01 | PASS | +1.80 bits, p = 0.0001 |
| e1 Ur III NMI above all shuffled nulls | PASS | 0.567 vs max 0.469 |
| e2 KIN and SERV isolated >= 0.70 | FAIL (expected) | KIN 1.00, SERV 0.59 |
| e2-KIN (secondary, added after dry run) | PASS | 0.997 |
| e positive control (e1 and e2) | FAIL | |

By the pre-registered rule, the grammar is "validated as a description" only if a2, b1, b3, c-pos, d and e all
pass. Everything passed except e, which failed on SERV isolation alone. So, strictly, the grammar is **not
validated**. The falsification tests (a2, d) both passed, so the positional description is **not falsified**.
It is **not a better predictor than the bigram** (a1 and c-big both failed).

## What this means

- The opener → connective → medial → closer pattern is real and transfers across sites and sign lists.
- It is not the whole story. Specific sign pairs carry information that position classes miss: a bigram beats
  the grammar by about 0.3 bits per sign at the big sites.
- That gap nearly vanishes at small ICIT-only sites. There, the pairs memorised at Mohenjo-daro help less and
  the general positional pattern helps more.
- The Ur III control shows that the pipeline finds real slots when they exist, but it does not cleanly split
  every relator.
- Nothing here bears on sound or meaning.

## Method in brief

- **Data and units.** Distinct texts. M77 v2 split: dev 1,698 texts; held-out 571, of which 441 are complete.
- **Class induction.** Classes were induced on dev by the exchange algorithm, seeded from earlier role
  lexicons, with random restarts.
  - K = 16 was chosen by BIC and alpha = 3 by family 5-fold CV.
  - Classes were named by fixed positional rules.
  - Labels were kept only if bootstrap stability was >= 0.7 and the label agreed with an independent run on
    3,049 Wells-list ICIT texts.
- **Baselines.** All baselines share the vocabulary (signs seen at least twice in dev; the rest map to
  `<UNK>`). Bits are per sign plus the end of text. CIs come from 2,000 bootstraps of text families.
- **Code.** `glib.py` is the library. The pipeline steps are `step1_classes.py` (classes) and
  `step2_generative.py` (transitions, length, registers). Validation is `validate.py dry|final`. Restoration
  is `restore.py`.

## Caveats

- **Register-offset CV.** The dev cross-validation of register offsets used class assignments induced on all
  of dev, which leaks a little into the folds. The held-out a3 result is the clean one, and it is negative.
- **Seed initialisation.** Class induction starts from earlier experiments' role seeds. Agreement with the
  seeds is 0.565, so the seeds do not dictate the result. Even so, a fully unseeded run might name classes
  somewhat differently.
- **Disclosed changes.**
  - The class-keep rule was changed once on dev, from unweighted to token-weighted stability.
  - e2-KIN was added after the dry run.
  - Both are disclosed in the prereg before hashing.
- **Ur III gold slots.** The gold slots come from a rule tagger (genre_alignment), not hand annotation.
- **Small control sets.** The Gulf set is small (18 texts). The foreign square-seal comparison has 8 texts and
  little power.
- **c2 bridging.** In c2, ICIT signs without an M77 bridge count as `<UNK>`, which favours all models equally.
  The fully bridged subset (87 texts) gives the same picture.
