# How strong a sign-animal tie could the Indus tests have seen? (prereg `animal_tie_power`, hashed 2026-11-23T20:07:54Z; code hash checked before the run)

**Verdict.**
- **The unicorn-vs-other test is now sized.** It would catch, with power of 0.8 or more, one sign carried by an extra 20 points of the non-unicorn seals' texts (c\* = 0.20). At +10 points its power is 0.73. The real Indus result, AUC 0.516, sits at about +2 points.
- **A Linear B-strength tie would only just be caught.** On the like-for-like scale (excess over each null, see the red team), a Linear B line's words predict its commodity about as strongly as a +23-point Indus tie.
- **Once the formula words are gone (names only), Linear B's tie falls to about +7 to +11 points, below what the Indus test can reliably see.**

So the Indus null excludes "the seal text is about its animal, as a Linear B line is about its commodity", with a thin margin. It says nothing about "the animal is an emblem and the text is a name".

## Leg A: plants on the real Indus seals (1,149 M77 distinct seal texts; null 1,000 within-site permutations)

**T1, unicorn vs other AUC** (null mean 0.501, 95th percentile 0.550; real 0.516, p = 0.31):

| δ (extra share of non-unicorn texts carrying the tie sign) | 0.05 | 0.10 | 0.20 | 0.40 | 0.80 |
|---|---|---|---|---|---|
| mean planted AUC | 0.532 | 0.570 | 0.616 | 0.736 | infeasible |
| power | 0.20 | 0.73 | **1.00** | 1.00 | (0 of 40 feasible) |

**T2, the F14 statistic on M77** (sign × animal, stratified by site × length, exact; 30 tests on real data, Bonferroni bar 0.00167). The real data's smallest p is 0.00197, just above the bar, which matches F14's "none passes".

| target | power at δ 0.05 / 0.10 / 0.20 / 0.40 / 0.80 | c\* |
|---|---|---|
| shorthorn bull (78) | 0.18 / 0.60 / 0.95 / 1.0 / 1.0 | **0.20** |
| elephant (34) | 0.10 / 0.30 / 0.68 / 1.0 / 1.0 | **0.40** |
| tiger (12) | not in the F14 family (fewer than 20 texts) | untestable |

**T1, 8-class balanced accuracy (single-animal targets): not usable as sealed.**
- The real labels already beat this null (0.192 against null 0.126, p = 0.002; Q1 reported the same weak signal).
- Plants therefore start above the bar, and "power" at δ = 0.05 (bull 0.83, elephant 0.98, tiger 1.0) is mostly the existing signal.
- The mechanical c\* = 0.05 for these targets is an artifact and is **not** used.

## Leg B: Linear B at Indus shape (20 subsamples; about 460 distinct texts each; OVIS plus seven minorities at Indus sizes)

| words deleted (top share of tokens) | 0% | 10% | 20% | 35% | 50% |
|---|---|---|---|---|---|
| words coding: mean AUC / passes of 20 | 0.856 / 20 | 0.814 / 20 | 0.760 / 20 | 0.664 / 20 | 0.605 / 16 |
| syllabogram coding: mean AUC / passes of 20 | 0.856 / 20 | 0.831 / 20 | 0.799 / 20 | 0.754 / 19 | 0.718 / 15 |

- At 0%, 8-class balanced accuracy passes 20/20 in both codings (0.36-0.39), and the T2 sign × commodity family passes 20/20.
- **Control:** labels permuted within site pass 1/20 (words) and 0/20 (syllabograms), both under the bar of 2, so Leg B is valid.
- **Kill test:** AUC 0.871 against a null 99th percentile of 0.761.

**Mapping onto the Indus ladder.**
- As sealed (raw AUC; conservative coding = syllabograms, by 0.0001): every rung maps above δ 0.80 except names-only (0.37).
- **The sealed mapping is wrong, and we replace it** (see the red team). The excess over each run's own null gives:

| words deleted | 0% | 10% | 20% | 35% | 50% |
|---|---|---|---|---|---|
| Linear B excess AUC (words / syllabograms) | 0.139 / 0.131 | 0.120 / 0.121 | 0.103 / 0.108 | 0.070 / 0.083 | 0.042 / 0.074 |
| Indus-equivalent δ (words / syllabograms) | 0.24 / 0.23 | 0.21 / 0.21 | 0.17 / 0.18 | 0.10 / 0.13 | 0.07 / 0.11 |

The real Indus excess (0.015) corresponds to δ ≈ 0.02.

## Red team (own check, 2026-11-23)
1. **The sealed mapping used raw AUC, which is not comparable across scripts.**
   - Linear B's within-site null is about 0.72, because site alone predicts the commodity: Knossos sheep tablets dominate. Indus's null is 0.50.
   - Raw AUCs therefore overstate Linear B by about 0.2. The excess over each null is the fair scale. It is reported as an unsealed correction, and it reverses the headline from "Linear B is far beyond the ladder" to "Linear B is just inside it".
2. **The 8-class statistic has no clean zero point** (above). Single-animal sizing via T1 is therefore not established. Only T2 sizes single animals.
3. **The names-only rung is borderline:** 16/20 (words) and 15/20 (syllabograms). The prereg froze no pass count for Leg B rungs, so we report the counts and claim nothing.
4. **What was planted:** one tie sign per draw, chosen uniformly (58 different signs across pooled draws). Ties spread over several signs or bigrams were not planted and would be harder to see.
5. **Leg B is an upper bound.** A Linear B logogram is part of the record. Its unit is one line per tablet, with OVIS at 66% against unicorn's 82%. AUC is little affected by that prevalence difference.

## What changes
- **Atlas 5.7.** "Animal not named in the text" is now sized: excluded at power 0.8 for a single-sign tie covering an extra 20 points of non-unicorn texts. That is about the strength of a Linear B line's tie to its commodity, and it is not excluded for name-like texts.
- **F14 per animal:** excluded at c\* 0.20 (shorthorn bull) and 0.40 (elephant); untestable for tiger and the smaller classes.
- **README line "Animal emblems are not written in the seal text":** narrowed to "not written as strongly as a Linear B line names its commodity; name-like texts under an emblem are not excluded".
- **For the scorecard's tripod rows:** any claimed sign-animal tie must exceed these floors to be visible at all. A claimed tie below them can be neither confirmed nor refuted by the seal corpus.
