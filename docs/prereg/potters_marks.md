# Pre-registration: potter's-mark genealogy of frame signs (experiments/potters_marks; Fable 5.2 plan 2, item 7)

Registered 2026-11-15, BEFORE `experiments/potters_marks/tests.py` was run. Frozen inputs, hashed into `docs/prereg/HASHES.txt` (tag `potters_marks`): this file, `build_marks.py`, `marks.csv`, `tests.py`.

## What was seen before registering (contamination statement)
- I read the literature and coded every mark in `marks.csv` (233 rows, 931 marks) myself, knowing the hypothesis. M77 matches marked `study` are therefore not blind. To bound this, definition P2 below uses only identifications made by others (Kenoyer naming a Mahadevan number; the ICIT/Wells transcription mapped through the bridge).
- While coding I saw the functional-reading roles of about 35 signs (e.g. M342 CLOSER, M347 TITLE, M176 POST-CLOSER, M177 OPENER (8 texts), M294 TITLE 0.68, M328 NOUN 0.62/UNIT 0.38, M162 NOUN 0.56, M169 CLOSER 0.59). I knew that Kenoyer 2020 names M342 in Harappa Periods 1-2 and M342-M347 in Period 2, and that paragorth loop 57 (S-DARK-57) found "0 frame signs" with a different coding. No frame-vs-core count, Fisher test or vessel-class table was computed before this file was written.
- Literature found: per-mark vessel type exists only for Sarai Khola (Halim 1972) and one Kot Diji sherd (Khan 1965). Quivron 1980 (Mehrgarh, ~850 marks) states that the same marks occur on goblets, cups and jars and that motif choice does not depend on later use, but gives no per-mark counts. Harappa (Kenoyer), Balakot (Dales 1974) and ICIT give no vessel type per mark.

## Definitions (fixed)
- **Sign universe**: Mahadevan signs with >= 5 distinct dev texts in `experiments/functional_reading/lexicon.csv`, classed by modal role: FRAME = opener, connective, closer, post-closer clitic, title element, unit/measure, bracketed-fish closer; CORE = noun, fish-class noun; NUMERAL (reported, not tested: strokes trivially have stroke precursors).
- **Early** = `early == yes` in marks.csv (Ravi/Hakra, Kot Diji/Early Harappan, Sarai Khola IA-II, Mehrgarh IV-VII, Balakot I, Kalibangan I). Harappa 2/3 and Nausharo II = transitional; Kalibangan "lower levels" M342 = doubtful.
- **Precursor credit** (sign has >= 1 early mark):
  - **P1 (primary)**: early == yes, match confidence A or B, sequence position with a single candidate (no alternatives).
  - **P2 (independent of my judgement)**: early == yes, match_basis author or icit; alternatives each credited.
  - **P3 (loose)**: early in {yes, doubtful, transitional}, any confidence, alternatives each credited.

## Tests
**(a) Are frame signs more often attested early than core signs?**
Statistic: share of FRAME signs with a precursor minus share of CORE signs. Tests: one-sided Fisher exact; one-sided permutation of the frame/core label within tertiles of drawing complexity (ink pixels), 10,000 permutations; logistic regression precursor ~ frame + ink + log frequency (reported). Power by simulation (frame rate 2x and 3x the core rate) is reported with the result.
- SUPPORTED if P1 stratified-permutation p < 0.05 AND P2 frame rate > core rate.
- REFUTED (for "frame descends from pot marks more than core") if P1 frame rate <= core rate.
- Otherwise INCONCLUSIVE. P3 is sensitivity only.
- Also reported: credited marks for the named frame signs M342, M328, M211, M162, M169, M267, M391, M99.

**(b) Do the marks of one shape cluster on one vessel class?**
Data: Sarai Khola occurrences with a published vessel class (jar vs bowl; the one lid is excluded). Shape families fixed in `tests.py` (strokes, cross/T, V, W/N, chevron/arrow, Y/star, curvilinear, tree). Families with >= 3 typed occurrences enter. Statistic: chi-square family x class; null: vessel labels permuted across occurrences, 10,000 times. Per family: two-sided binomial against the pooled jar share, BH across families.
- SUPPORTED ("a mark is restricted to one vessel class") if chi-square permutation p < 0.05 AND at least one family has >= 80% of its occurrences in one class with BH q < 0.05.
- REFUTED at this power if permutation p >= 0.05 and no family passes; the power of the test (planted family of 4/6/10 occurrences all on jars) is reported with the result.
- Mehrgarh enters as Quivron's qualitative statement only.

**(c) Do Mature pottery inscriptions keep the association?**
Untestable unless a Mature corpus records vessel form per inscription. ICIT and M77 do not (checked: ICIT `shape` describes the inscribed field for 23 of 636 pottery rows and is '-' otherwise). Descriptive only: counts of the named frame signs on Mature pre-firing marks, graffiti and stamped pots vs seals (ICIT, distinct texts).

## Number of confirmatory tests
3 (a-P1 stratified permutation; b chi-square permutation; b per-family BH counted as one decision). Bonferroni alpha for the area = 0.017 reported alongside the pre-registered 0.05 rules.

## What would falsify
Grounding a frame sign in a container would need: the sign's early precursor present (P1 or P2) AND its early occurrences concentrated on one vessel class in (b). If no frame sign has typed early occurrences, the vessel-function route is untestable with open literature, whatever (a) shows.

## Amendment A1 (2026-11-15, after the first run)
The first run of `tests.py` completed tests (a) and (b) and then crashed in the descriptive vessel-by-match listing, because `build_marks.py` leaves `n_marks` empty for rows that did not set it (a `setdefault` bug; such rows mean 1 mark, and `credited()` in test (a) already counts them as 1). The only change: the descriptive listing now reads an empty `n_marks` as 1. Tests (a) and (b) are unchanged and seeded, so the rerun reproduces their numbers exactly; the first-run log values are kept in RESULTS.md for comparison.
