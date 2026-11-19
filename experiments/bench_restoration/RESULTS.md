# Bench of the IIT Hyderabad masked-sign restoration release (board task #18)

## Verdict (revised 2026-11-19 after retraining their own code): near-copies inflate their headline accuracy by about 6-7 points of Hit@1, not 10. Their main comparison (KN-3 at least as good as the transformer) survives.

**Retraining (pre-registered: `docs/prereg/bench_restoration_retrain.md`, code `retrain.py`, both hashed before any full run).** We ran the deposit's own `restore_transformer_ebuds.py` unchanged, with default settings (5 seeds, early stopping, refit, KN-3 blend tuned on validation), on our M77 readings of their 1,585 texts. Hit@1 is exhaustive: every position of every test text.

| split | test texts | KN-3 | transformer | blend |
|---|---|---|---|---|
| their paper (their readings) | 303 | 39.56 | 37.49 | 40.84 |
| orig: their folds, our readings | 303 | 42.21 | not completed* | not completed* |
| sizectl: their test set, 177 train/val texts dropped that are unrelated to any test text | 303 | 41.71 | 39.00 | 43.42 |
| purge: their test set, the 177 train/val texts dropped that are near-copies of a test text | 303 | 35.44 | 33.10 | 36.16 |
| family: whole near-copy families kept in one split | 322 | 35.45 | 35.66 | 36.41 |

\* The orig retrain hit the 2-hour job limit twice: once during seed 3 of 5 while sharing the machine, and once alone in the last of its 5 refits. It is not rerun, because restoration work is closed. The orig row was a descriptive reproduction check only; KN-3 is deterministic and comes from the same code. It is 2.6 points above their 39.56 on the same split, which measures the effect of reading differences.

- **P1 leakage, CONFIRMED.** Purge is below sizectl by 6.3 (KN-3), 5.9 (transformer) and 7.3 (blend) points. The sealed bar was at least 5 for all three. Both splits drop the same number of training texts, so the gap is the near-copies themselves, not less data.
  - Post hoc robustness check (not pre-registered, `posthoc_kn_draws.py`): 100 more random size controls give KN-3 41.1 to 42.9 (mean 42.0). The gap to purge is at least 5.7 points in all 100.
- **P2 no neural gain, CONFIRMED.** Transformer minus KN-3: −2.3 points on purge and +0.2 on family. Both are inside the sealed ±3 band. The blend adds about 1 point over KN-3 on both.
- **P3 family agrees with purge, CONFIRMED.** Every model is within 2.6 points.

**Corrections to our first bench (below), from the retraining and from reading the deposit's build code:**
- **The deposit does remove repeated texts:** exact repeats under the authors' readings (`build_ebuds.py`, rule `duplicate_text`). Our earlier line "not de-duplicated" was wrong.
- **Our "20 exact copies" exist only under our readings.** On those 20 texts their models score about 34% Hit@1, while our trigram (trained on our readings) scores 80% (`posthoc_tiers.py`, post hoc). So under their readings these are not copies. The leakage is the 87 test texts with a one-edit or containment near-copy. On those, their models score 53-61%, against 29-31% on clean texts.
- **The first bench's 27-point leaked-vs-clean gap, and its "about 10 points" headline, mixed leakage with clean texts simply being harder.** The retraining isolates leakage at about 6-7 points.
- **Our readings differ from theirs on some texts.** With our readings of their own split, their deterministic KN-3 scores 42.2 in a short timing run, against their 39.56. So every absolute number above is "under our M77 readings". The comparisons between splits all use the same readings.
- **Wording.** "No detectable neural gain at this corpus size", not "neural adds nothing". The clean-subset CI allows a gain of up to about 1-2 points.

**What the authors could do (suggestions, not errors):** split by near-copy family, or purge near-copies from training; report results on clean and leaked test texts separately. **What we still lack:** their paper (Table S11 is "as submitted", so it is presumably under review) and their sign readings, which would let us rerun on their exact sequences.

---

## First bench (2026-11-17, scored subsets of their deposited predictions; superseded where it conflicts with the above)

## Numbers (pre-registered: `docs/prereg/bench_restoration.md`, sha256 2879c7b4..., logged before scoring)

Rebuild check (all 1,403 positions, truth from our M77): KN-3 39.91 / transformer 36.99 / blend 40.77 Hit@1 vs their 39.56 / 37.49 / 40.84. That is within 0.5 points, so the rebuild is faithful.

| model | all Hit@1 | clean Hit@1 (875 pos, 189 texts) | leaked Hit@1 (528 pos, 107 texts) | clean Hit@5 | clean MRR |
|---|---|---|---|---|---|
| their KN-3 | 39.9 | 29.7 | 56.8 | 50.6 | 0.397 |
| their transformer | 37.0 | 28.5 | 51.1 | 48.2 | 0.379 |
| their blend | 40.8 | 30.5 | 57.8 | 51.9 | 0.409 |
| our trigram (abs. discount, whole-text score) | 41.8 | 29.8 | 61.6 | 51.4 | 0.402 |
| unigram frequency | 10.5 | 8.2 | 14.2 | 20.6 | 0.157 |

Paired bootstrap over clean texts (10,000 resamples), Hit@1 difference in points:
- transformer − best n-gram (ours): −1.37, 95% CI [−4.02, +1.32], one-sided p = 0.86
- blend − best n-gram: +0.69, [−0.96, +2.31], p = 0.23 (Holm over the two: neither passes)
- KN-3 − transformer: +1.26, [−1.47, +4.03]
Power: the CI half-width is about 2.7 points for the transformer and 1.6 for the blend. A neural gain larger than about 3 points of Hit@1 on clean texts would have been detected.

## What the release is (task item 1)
- Corpus: their own rebuild of Mahadevan 1977 (M77) from the book: 1,585 complete, break-free texts (object sides; seals 1,132, sealings 209, tablets 159, others). Signs are M77 numbers 1..417. All 1,585 ids and all 296 test lengths match our M77. Exact repeats (under their readings) were removed; near-copies (one sign off, or contained) were not.
- Split: 5 folds hashed on object id; fold 0 test (303 texts), 1,161 train, 121 validation.
- Deposit: folds, masked positions, probability arrays for three models, Table S11 (360 damaged-text candidates). No corpus, no true signs.

## What failed or was not checked
- Their transformer was not retrained on a family-clean split (we do not run their code, and they did not deposit CV-fold probabilities). The clean-subset comparison is leakage-free for their trained models, because clean test texts have no near-copy in training. But clean texts are harder than average, so absolute numbers on them are not comparable to a random split.
- The family rule is our `splits_v2` rule (one edit or contained copy, texts of 4+ signs for edits). Looser families, such as shared formulae, would move more texts into "leaked".
- Table S11 restorations of damaged texts were not evaluated (no ground truth). Their 111 "intact parallel" cases are by construction the leaked-type situation, where any n-gram does well.

## Use for the project
For restoring a lost sign, a trigram fitted on our corpus is as good as anything in this release. Restoration accuracy on texts with no near-copy is about 30% Hit@1 and 51% Hit@5.

Files: `bench.py`, `results.json`, `ledger_rows.csv`, deposit in `raw/` (data only, MD5 checked).
