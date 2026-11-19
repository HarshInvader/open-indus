# Pre-registration: leakage of random object splits on M77 alone

Date: 2026-11-19. Descriptive measurement for the paper (docs/paper/latex/main.tex, Section 5). It replaces figures that were measured on a third-party release's text set, so that the paper rests on our own corpus only.

## Question
In M77, what share of test texts has a near-copy in training when the corpus is split at random by object?

## Data
`corpus.load.m77_texts()`; object = `text_no` (sides of one object share it); sequence = signs with line breaks removed; texts shorter than 2 signs are not test texts.

Two scenarios:
- **A (all texts):** every text is a unit.
- **B (exact repeats removed first):** keep the first text (lowest text_no, then side) of each exact sequence, as a modeller who de-duplicates would. Exact-copy leakage is then zero by construction.

## Rules (same definitions as experiments/redteam_bench_restoration/rt.py)
Copy if: exact; or within k sign edits (k = 1, 2) with the shorter text at least 4 signs; or, where containment is allowed, the shorter text (3+ signs) is a contiguous run of the longer. Primary rule: within 1 edit, or contained.

## Splits
200 splits. Object fold = sha256("leak:{s}:{text_no}") first 8 hex digits mod 5; fold 0 is test (about 20%).

## Outputs
For each scenario and rule: median share of test texts with a copy in training, 2.5 and 97.5 percentiles. No hypothesis test; nothing in the paper depends on a pass bar. Expected from the earlier deposit-based figure: primary median about 30-40%. If the result falls outside that range, the paper reports this measurement, not the earlier one.
