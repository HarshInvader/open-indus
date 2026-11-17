# Pre-registration: bench of the IIT Hyderabad masked-sign restoration release (board task #18, agent H7)

Written 2026-11-17 before any score was computed. Seen so far: the deposit README (their reported Hit@1 on the
exhaustive fold-0 positions: KN-3 39.56, transformer 37.49, blend 40.84), and an alignment check: all 1,585 deposit
text ids exist in our M77 (`text_no` or `text_no.side`), all complete, no breaks, and all 296 test-text lengths equal
our sign counts (seq without `|`).

Source: Zenodo 24164070 (CC BY 4.0 data, MIT code), in `experiments/bench_restoration/raw/dep`. Their code is NOT run.

## Data
- Truth at (text_id, position_0based) = our M77 sequence with `|` removed, reading order.
- Their predictions: `test_probabilities.npz` (kn3, transformer, blend; 1,403 x 417), rows = exhaustive positions.
- Their split: `fold_assignments.csv` (object-level hash folds). Train pool = train + validation (what their final
  models were fitted on).

## Steps
1. Rebuild check: Hit@1, Hit@5, MRR of their three models with our truth. Agreement within 1 point of their table
   counts as a faithful rebuild.
2. Leakage: a test text is LEAKED if any train-pool text is identical to it, or within one edit / a contained copy
   by our family rule (`corpus.build._close`, the rule behind `splits_v2`). Report share of test texts and positions.
3. Baseline: our own interpolated absolute-discount trigram (D = 0.75, unigram add-one), scoring each candidate by
   the probability of the whole text with the candidate in place (BOS/EOS padded), fitted on the train pool.
   Also a position-free unigram baseline.
4. Main comparison on CLEAN positions (test texts not leaked): Hit@1 of transformer minus the better of {their KN-3,
   our trigram}. Paired bootstrap over texts (10,000 resamples), 95% CI and one-sided p. Same on LEAKED positions,
   descriptive.

## Decision rule
- "Neural restoration adds something over n-grams once leakage is removed" only if transformer Hit@1 on CLEAN
  minus the best n-gram Hit@1 on CLEAN has 95% CI above 0 (one test; no correction needed). Same check for the blend,
  reported separately (two tests, Holm).
- Otherwise negative. Power statement: report the CI half-width (minimum detectable difference).
- Leakage is "material" if leaked-minus-clean Hit@1 gap for their best model is > 5 points.
