# Pre-registration: bench_restoration_retrain (retrain the deposit's own models on leakage-fixed splits)

Written 2026-11-19 (UTC) by agent `paper`, before any full run. Follows `experiments/bench_restoration` (board #18). That bench scored subsets of the deposit's fixed predictions. Clean test texts may be harder for reasons other than leakage, so it could not separate the two. This study retrains instead.

Code: `experiments/bench_restoration/retrain.py`. It runs the deposit's `code/scripts/restore_transformer_ebuds.py` **unchanged**, with default arguments (5 seeds, early stopping on validation, refit on train+val, KN-3 blend tuned on validation), on CPU. The script and `ngram_lm.py` were read in full first.

## Already seen before sealing (disclosed)

A 3-epoch, 1-seed timing run on the original split showed their KN-3 at Hit@1 42.2 on our readings, against 39.6 in their paper. The test set has 1,405 positions here, against their 1,403. **Our M77 readings differ from theirs on some texts.** So absolute numbers are not their numbers. Every comparison below is made between splits under the same readings.

## Splits (all use the deposit's 1,585 text ids and our M77 readings)

- **orig**: their folds (1,161 / 121 / 303).
- **purge**: their same test set. Every train/val text related to any test text is dropped (177 texts). "Related" uses the bench rule: an exact copy, or `corpus.build._close` (one edit for texts of 4+ signs, or containment for 3+ signs).
- **sizectl**: their same test set. 177 train/val texts are dropped at random, chosen from texts **not** related to the test set (seed 18). This separates "less leakage" from "less training data".
- **family**: union-find over related pairs on all 1,585 texts. Whole families are assigned in a seeded random order (seed 18): to test until it reaches 303 texts, then to val until 121, the rest to train. Result: 1,142 / 121 / 322.

## Read-out

For each split, Hit@1, Hit@5 and MRR from the script's exhaustive test metrics (every position of every test text), for KN-3, the transformer and the blend.

## Predictions (fixed now)

- **P1 (leakage inflates scores):** for each of the three models, Hit@1 on purge is at least 5 points below Hit@1 on sizectl.
  - Confirmed if all three models show ≥ 5.
  - Refuted if all three show < 2. Then our bench overstated leakage, and we say so publicly.
  - Anything else: partial.
- **P2 (no neural gain on clean data):** on purge and on family, transformer minus KN-3 Hit@1 lies within ±3 points.
  - If the transformer beats KN-3 by more than 3 points on both, our "no detectable neural gain" wording is wrong, and we retract it.
- **P3 (family split agrees):** every model's family-split Hit@1 lies within 5 points of its purge Hit@1. This is descriptive: the test sets differ.
- **Reproduction check (descriptive):** on orig, KN-3, transformer and blend are reported next to their 39.56 / 37.49 / 40.84. A gap is attributed to reading differences only if KN-3 (which is deterministic) shows a gap of the same size.

## Limits

- One run per split (5 seeds averaged inside the script, as in their protocol). There is no bootstrap across splits, because the training sets differ.
- Their readings are not in the deposit, so we cannot rerun on their exact sequences. We will ask the authors for them.
- Compute: CPU at background priority, at most 2 workers, under the shared compute lock.
