# Bench of the IIT Hyderabad masked-sign restoration release (board task #18, agent H7)

## Verdict: negative. Once near-copy leakage is removed, neural restoration adds nothing over a plain trigram, and every model's headline accuracy falls by about 10 points.

- **Leakage is large.** 107 of their 296 test texts (36%) have a near-copy (identical, one sign off, or contained) among the 1,282 training texts. 20 of them are exact copies, and 528 of the 1,403 masked positions sit in these texts. Their folds were hashed by object, not by text family.
- **Leakage inflates the scores.** On leaked texts their blend gets 57.8% Hit@1. On clean texts it gets 30.5%, a gap of 27 points (the pre-registered "material" bar was 5). Their reported 40.8% mixes the two.
- **Neural adds nothing on clean texts.** Transformer Hit@1 28.5% vs our 40-line trigram's 29.8%: −1.4 points (95% CI −4.0 to +1.3, p = 0.86). Their blend: +0.7 points (CI −1.0 to +2.3, p = 0.23). Their own KN-3 (29.7%) also ties the transformer (+1.3, CI −1.5 to +4.0).
- **The authors' own numbers already pointed this way.** KN-3 beat the transformer in their table (39.6 vs 37.5). The deposit is honest and well built; the leakage is the one problem.

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
- Corpus: their own rebuild of Mahadevan 1977 (M77) from the book: 1,585 complete, break-free texts (object sides; seals 1,132, sealings 209, tablets 159, others). Signs are M77 numbers 1..417. All 1,585 ids and all 296 test lengths match our M77. The corpus is not de-duplicated: moulded-tablet repeats stay in.
- Split: 5 folds hashed on object id; fold 0 test (303 texts), 1,161 train, 121 validation.
- Deposit: folds, masked positions, probability arrays for three models, Table S11 (360 damaged-text candidates). No corpus, no true signs.

## What failed or was not checked
- Their transformer was not retrained on a family-clean split (we do not run their code, and they did not deposit CV-fold probabilities). The clean-subset comparison is leakage-free for their trained models, because clean test texts have no near-copy in training. But clean texts are harder than average, so absolute numbers on them are not comparable to a random split.
- The family rule is our `splits_v2` rule (one edit or contained copy, texts of 4+ signs for edits). Looser families, such as shared formulae, would move more texts into "leaked".
- Table S11 restorations of damaged texts were not evaluated (no ground truth). Their 111 "intact parallel" cases are by construction the leaked-type situation, where any n-gram does well.

## Use for the project
For restoring a lost sign, a trigram fitted on our corpus is as good as anything in this release. Restoration accuracy on texts with no near-copy is about 30% Hit@1 and 51% Hit@5.

Files: `bench.py`, `results.json`, `ledger_rows.csv`, deposit in `raw/` (data only, MD5 checked).
