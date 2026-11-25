# Lift score: K0 passed, K1 failed (11 of 20). Certify by held-out restoration is closed for this corpus size.

- **Prereg:** `docs/prereg/lift_score.md`, sealed 2026-11-25 as v3 (tag `lift_score`).
- **Code:** `run.py`, hashed before any run (tag `lift_score_code`). The hash was re-checked before running.
- **Run:** `run.py kill`, once, detached with a pid file, under the Indus compute lock and `board/run.sh`, 4 workers, 55 min.
- **Outputs:** `kill.json`, `kill.out`, `k1_targets.json` (written before any K1 gain).
- **Scope:** no Indus key was scored, and no Indus text was masked or read.
- **2027 clause (coordinator decision):** G is this study's gate. Hit@1 is the 2027-clause measure and is reported below. A G pass alone would not have met the clause.

## Result
- **Checks before K0:**
  - A1 reproduced the sealed R1 figures.
  - A2: the median was 1,375.5 clean positions.
  - F3 did not fire: trigram Hit@1 on the plant was 4.1-5.5%.
  - A6 had zero deviation.
  - F1 and F2 did not fire, and all 20 K1 plants were built.
- **K0, full-dose plant, draws 1-5: passed.**
  - True-key G was 0.275, 0.283, 0.163, 0.248 and 0.184 nats, with λ* = 1 in every draw.
  - Scramble G and the N1 median G were 0 in all five draws.
  - Hit@1 lift was only 1.7-3.2 points.
  - The permuted-lexicon maximum G (record-only) was 0.012-0.058.
- **K1, plant diluted to the true key's own dose, draws 1-20: failed, 11 of 20 (bar 16).**
  - The real-text dose targets D were near zero: −0.021 to +0.035 nats per consonant. Plants landed at w = 0.125-0.625.
  - G ranged from −0.049 to 0.061. In 5 draws λ* = 0, so G = 0.
  - Hit@1 lift was between −0.19 and +0.60 points.
- **Frozen reading:** "Unpowered. A planted language diluted to the true key's own dose (cross-fitted lexicon likelihood per consonant) does not raise restoration by 0.02 nats per sign at Indus shape. By the one-attempt rule, certify by held-out restoration on existing texts is closed for this corpus size. No further score is drafted; reopening needs more text."
- **K2 and K3 (record-only, as the K1-fail rule requires):**
  - K2: the scramble and N1 controls were at or under their bars in 20 of 20 draws.
  - K3: the true Linear B key on real text had λ* = 0 in all 20 draws, so G = 0 and Hit@1 lift = 0. The trigram alone had a median Hit@1 of 14.0%.
  - K4 did not run.

## What this can and cannot say
- **It can say:**
  - This word-and-fragment score carries signal when text is made of lexicon words: K0 is a clean replication of the pilot.
  - At the lexicon fit that the true Linear B key actually reaches on real text (D near zero), the gain is not reliably there. On real text, the development folds never chose λ > 0.
  - So held-out restoration with a Homeric lexicon cannot certify a key at this draw size: 2,300 M77-length chunks, about 8,050 sign tokens (A2 counts 8,020-8,104 per draw).
- **It cannot say:**
  - that no score could work. The oracle gain on full-dose plants was 0.50 nats;
  - what happens at larger corpus sizes. That question goes to `certify_size_curve`;
  - anything about any Indus key.
- **Route:** closed for this corpus size under the sealed one-attempt rule. No further score is drafted. Reopening needs more text.

## Disclosures
- **Corpus-size wording:** the sealed prereg describes the corpus as "about 13,100 sign tokens in chunks of M77 length". The sealed draws hold about 8,050 sign tokens each (2,300 chunks at a mean of 3.5 signs). The frozen reading's words are kept; the size it refers to is the draw size.
- **Implementer choices:** 22 places are marked `# PREREG-AMBIGUITY:` in `run.py`. The ones bearing on K1 are the fold hash, the pooled λ* margin, the 15 EM rounds, the bisection order and the endpoint rule. All 20 bisections landed within tolerance.
- **Exit status:** the job wrapper recorded exit status 1 for the planned K1 stop. `kill.json` shows status `done`.
- No rerun, no tuning, no fix tags.
