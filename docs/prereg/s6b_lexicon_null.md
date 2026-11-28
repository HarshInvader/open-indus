# Pre-registration: S6b, pin down the functional-reading lexicon-null p (README #9)

Contributor: m0x1n. Written 2026-11-28, after S6 (`docs/prereg/s6_q_determinism.md`) and before any run of the change below.

## Why

S6's Run C (20 master seeds, fixed code) showed that ledger row `lr_fr_lex` (README #9: "p=0.013, q=0.085") moves between 0.0033 and 0.027 with the random seed. It is estimated from only 300 lexicon permutations (section A of `experiments/ledger/v2_reruns.py`, v2 block), so at p ≈ 0.01 it rests on about 3 exceedances. README #9's q sits near 0.05 to 0.1, so the Monte Carlo error decides how the finding reads.

## Change (the only one)

In section A, the v2 block's lexicon-permutation null uses **10,000** permutations instead of 300, and reports `lexicon_null_hits`, `lexicon_null_n` and an exact 95% Monte Carlo interval. The v1 reproduction block keeps 300. Nothing else changes: not the statistic, the lexicon, the role sets or the split.

## Procedure

- **Run D.** The updated script under `INDUS_SEED` = 1 ... 20 (each with `PYTHONHASHSEED` = seed + 100), with the same harness as S6 (`experiments/s6_q_determinism/sweep.py D`). The q columns are recomputed on the committed ledger with `merge_rows.py`.
- **Report** min, median and max over the 20 seeds of `lr_fr_lex` p, q_global, q_hier and q_all, and the same for `lr_gulf` (which should not change from Run C).

## Pass marks

- **H4:** the max/min ratio of `lr_fr_lex` p over Run D is below 1.5 (Run C: 8.0).
- **H5 (descriptive, no pass mark):** whether `lr_fr_lex` q_global is below 0.05 under all 20 seeds, under none, or under some. Whichever it is, it is reported as the honest reading of README #9.

## Planted control

Not applicable (no new claim). The check is that the 300-permutation runs in S6 Run C reproduce the spread that motivated this, which they already did: 0.0033 to 0.027.

## If it fails

If H4 fails, I report the range and the number of permutations that would be needed.
