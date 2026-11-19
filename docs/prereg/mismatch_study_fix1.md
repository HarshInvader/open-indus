# Fix 1 to mismatch_study stage 1 (planted check PC1 failed; search fixed and resealed)

Written 2026-11-19 (UTC) by agent `paper`, after run 1 of stage 1 and before any kill-test cell ran. This follows the base prereg, section 4: "If any planted check fails, stage 1b does not count. The failure is reported, the code fixed, and the fix resealed with a note."

## What failed (run 1, sealed code mm.py 04ef0c0f…, par.py b577b30a…)

| Check | Result | Pass rule |
|---|---|---|
| PC1 true-model control | **fail**: alphabet 0.60 (Latin), 0.77 (Finnish); syllabary and logo-syllabic 0.998–1.000 | ≥ 0.90 in all 6 cells |
| PC2 dialled-KL | pass: accuracy 1.0 at λ = 1, 0.8, 0.6; Spearman 0.88; planted boundary 1.30, recovered 1.27 | |
| PC3 shuffled negative | pass: 0.18 vs baseline 0.30 (Finnish); 0.06 vs 0.16 (Latin) | |
| Attack gate | pass: A0, A1, A2 ≥ 0.998 on both pairs | |

The driver stopped as sealed, and the kill test did not run. Run-1 outputs are kept unchanged in `experiments/mismatch_study/out/run1_failed/`.

## Diagnosis (post hoc, on the failed PC1 cells only)

- **A search failure, not a statistical or coding one.** In both alphabet cells, the true key scores far above the key A0 found:
  - Latin: −6,514 against −7,399;
  - Finnish: −6,336 against −6,697.
- A greedy climb started from the true key stays there at accuracy 1.0, and the same attack recovers 1.0 at 10k tokens.
- 16 fresh restarts reached the truth only once for Latin, and never for Finnish. The anneal stalls in optima that single-sign moves cannot leave, because exchanging two signs' values takes two moves through a worse key.

## The fix (mm.py, function `polish`, called at the end of every `gibbs` search)

After the anneal and the 10 greedy sweeps, the search alternates two steps until neither improves the full objective:
- every pairwise swap of two signs' values, each kept only if the full objective rises;
- a greedy single-sign sweep.

The objective, the schedule, the restarts and the selection by objective are unchanged.
- **Which attacks change:** A0, A1, A3 and A3+ (all use `gibbs`). EM (A2) is unchanged.
- **Direction:** the attacker can only get stronger, so the kill test becomes harder to survive, not easier.
- **Pre-seal test** (post hoc, 8 restarts, failed cells only):
  - Latin alphabet: 5 of 8 restarts reach the true key;
  - Finnish alphabet: 7 of 8.

  On a related-model syllabary cell, the polish raised the objective and left accuracy unchanged.
- **Cost:** about 2 extra seconds per syllabary restart, so A3+ costs about twice as much.

## For the red team (amends amendment 2, C6)

Add to A0, A1 and A3: "after the anneal, alternate all pairwise value swaps between signs (kept if the full objective rises) with greedy single-sign sweeps, until neither improves".

## Rerun

All planted checks and the gate are rerun from scratch with the fixed code, under the same rules and thresholds. Then the kill test runs, as sealed. No threshold, cell or seed changes.
