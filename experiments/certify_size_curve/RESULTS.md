# Certify size curve: stopped at K0 (reading 3). A planted language at quarter dose stays hidden up to 128,000 tokens, so more text does not rescue this score.

- **Prereg:** `docs/prereg/certify_size_curve.md`, sealed 2026-11-25 as v4 (tag `certify_size_curve`).
- **Code:** `run.py`, hashed before any run (tag `certify_size_curve_code`). The hash was re-checked before running.
- **Run:** `run.py kill`, once, detached with a pid file, under the Indus compute lock and `board/run.sh`, 4 workers. Wall time was 5.8 h. For about 2 h of that the run was starved of CPU by other projects' jobs.
- **Outputs:** `kill.json`, `kill.out`.
- **Scope:** no Indus key was scored, and no Indus text was masked or read.
- **2027 clause:** G is this study's gate. Hit@1 is reported beside it as the 2027-clause measure.

## Result
- **Checks before K0:** A1, A2, A6, A7 and A9 matched.
  - Pool T: 4,435 texts, 445,733 tokens, 207 sign types.
  - Median tokens per draw: 7,992 at 1 u, 31,963 at 4 u, 128,131 at 16 u.
  - F3 did not fire: trigram Hit@1 on the plants was 6.4–8.5%.
  - F6 projected 52.8 h for the whole study, under the 90 h stop, so nothing was dropped.
- **K0a, 1 u: passed, as designed.**
  - Full dose: G was 0.32–0.41 nats in 5 of 5 draws, with scramble and shuffled-key G of 0. Hit@1 lift was 3.1–4.9 points.
  - Low dose 0.25: 8 of 20 draws reached G ≥ 0.02. This is the miss the prereg requires as the known answer. F5 (dose 0.125) was not applied.
- **K0b, the same low dose at larger sizes: the gain bar missed.**

  | size | tokens (median) | gain bar G ≥ 0.02 | bar needed | median G | λ* = 0 | Hit@1 lift |
  |---|---|---|---|---|---|---|
  | 4 u | 31,963 | 3 of 10 | — | 0.007 | 4 of 10 | 0 to 0.37 |
  | 16 u | 128,131 | **2 of 10** | 8 of 10 | 0.005 | 5 of 10 | 0 to 0.39 |

  - The scramble and shuffled-key controls were exactly 0 in 10 of 10 draws at both sizes.
  - K0c, pure filler at 16 u: G = 0 in 5 of 5.
- **Frozen reading (reading 3):** "Even a planted language at the K0b low dose (0.25) stays hidden at 128,000 tokens. More text does not rescue this score. The restoration route stays closed up to that size for this score; a real-text null would add nothing. A control with no language also passed its bar at 4 u and 16 u."
- **Note on the last sentence of the reading.** The control that missed is bar C, at 5 of 10. The permuted lexicons had G = 0 in every draw, so no permuted lexicon ever gained. Of the 10 misses, 9 are draws where the true key's λ* was 0: the difference was then 0, which the sealed rule counts as a miss. The tenth is a 4 u draw where the true key's G was −0.003.
- **K3, record-only:** on real Old Assyrian text, the true key had λ* = 0 in 18 of 20 draws at 1 u and in 3 of 3 at 16 u. G was at most 0 everywhere.
- Nothing else ran (K1, K2, K4, the ceiling lexicon, set Q, pool L).

## What this can and cannot say
- **It can say:**
  - With this score, a planted language mixed in at a quarter is not reliably found by held-out restoration, even with 16 times the Indus-sized draw (about 128,000 tokens). Its gain did not grow from 4 u to 16 u.
  - The true Old Assyrian key with a Neo-Assyrian lexicon also showed nothing on real text at 1 u or 16 u. That was record-only.
  - So, for this score, no corpus size we can build here rescues the restoration route. For Indus, which has about 1.3–2.0 draws of text, the route stays closed.
- **It cannot say:**
  - that another score could not work. The full-dose gain was large;
  - how a real language's fit compares with the quarter-dose plant. K1 did not run;
  - whether the lexicon's distance from the text, or the corpus size, limits the real-text result. The ceiling lexicon did not run;
  - anything about any Indus key.

## Disclosures
- **Exit status:** the job wrapper recorded exit status 1 for the planned stop. `kill.json` shows status `done`.
- **Implementer choices:** marked `# PREREG-AMBIGUITY:` in `run.py`. The ones bearing on K0 are:
  - the plant block index, (k − 1) mod blocks;
  - the hash-set clean index;
  - F1 applying from K0a low dose onward;
  - first-in-file-order on Oracc value clashes.
- **Coordinator rulings before the run:** the 25% A2 tolerance was kept as sealed, and bar C was run as written (a zero difference counts as a miss).
- No rerun, no tuning, no fix tags.
