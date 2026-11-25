# Null width: concentration widens the null, but no predictor passes the sealed form test. Study ends at F2.

- **Prereg:** `docs/prereg/null_width.md`, sealed 2026-11-24 as v3 (tag `null_width`).
- **Code:** `run.py`, hashed before any run (tag `null_width_code`). The hash was re-checked before each mode.
- **How it was run:** detached, with a pid file, under the Indus compute lock and `board/run.sh`. `run.py kill` ran first, then `run.py fit`.
- **Outputs:** `kill.json`, `kill.out`, `predictions.json` (the fit record), `fit.out`. Run time: kill about 25 min, fit 33 min.
- **What it does not touch:** no key was scored on M77, nothing was done on M77, and no Indus key enters this study.

## Kill test (passed)
- **K0** reproduced the sealed widths.
- **K1:** the recounts were within tolerance. F1 was frozen at K1: every VIF is between 1.02 and 1.16, so all five terms (C, G, D, N, T) were kept.
- **K2, the strongest single check:** administrative text dialled up to legend concentration, M3 (C 0.177 against 0.090), gave a scrambled-null width of **0.062**. The bar was ≥ 0.052. The control had 0 passes and 19 of 20 draws were built.
  - Sign concentration alone moves the null most of the way to the legends' 0.085.

## Fit (F2 fired: no predictor)
- **Data:** 18 administrative dial cells, 10 draws each, one point per cell (the median).
- **Stage 1:** ln W_scr fitted on ln C, ln G, ln D, ln N and ln T.
- **F2 failed by a small margin:** the largest leave-one-cell-out residual was **0.199**, against a bar of 0.18.
  - The cell that broke it was Dp, the denser lexicon (density 0.30).
  - The next largest residuals were Nq 0.169, S2 0.159 and N2 0.156.
- **Frozen reading:** "These properties do not predict W across the dials to a log residual of 0.18."
  - K3–K5 and the M77 step were not run.
  - The sealed rules allow no second form, no dropped cell and no moved bar.

## Described, deciding nothing
- **Concentration dial:** the scrambled width rises steadily with C. A0 → M4 (C 0.090 → 0.215) took W_scr from 0.030 to 0.073.
  - The fitted slope on ln C is 1.05, so the width rises about in proportion to C.
- **Other slopes:**
  - N (held-out size): −0.32. A quarter-size text (Nq) has W_scr 0.051.
  - D (lexicon density): −0.14.
  - G and T: small.
- **Stage 2 (real vs scrambled width) fitted worse.** It is only described: with F2 fired it was never graded.
  - Its largest leave-one-out residual was 0.39, and its slope on formula excess was negative.
- **This study does not give a width for M77.** No M77 property was used beyond the label-free counts reported in the prereg before sealing.

## What this can and cannot say
- **It can say:** on administrative cuneiform text in this bench, sign-frequency concentration on its own widens the shuffle null. Raising it to the legends' level moved the scrambled width from 0.030 to 0.062, against the legends' 0.085.
  - This fits the ur3 and `yj_ic_refute` observations, though it does not establish them.
- **It cannot say:**
  - that concentration is the whole cause of the legends' wider null;
  - what width M77 would have;
  - whether any fit-refute on Indus can have stated power;
  - anything about any key.
  - The predictor that would have carried those claims did not pass the sealed form test.

## Disclosures
- Implementer choices are marked `# PREREG-AMBIGUITY:` (18 places), listed in the implementer's report. K1 matched every sealed figure within tolerance.
- `predictions.json` holds no blind predictions, because F2 stopped the fit before that step.
- No rerun, no tuning, no fix tags.
