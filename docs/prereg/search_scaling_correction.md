# Correction to search_scaling and decipherability (atlas 1.8): logged deviation

Written 2026-11-20 (UTC) by agent `paper`. No data was rerun. This changes the stated verdicts of two closed entries after later evidence, and is logged here as a deviation with the reason.

## What was claimed
1. **search_scaling (sealed verdict H0).** Related-language recovery at 2.5k tokens is "not a search artefact".
2. **decipherability (atlas 1.8, README, RESULTS.md).** Related-language recovery is 10-26%, "flat from 2.5k to 230k tokens". A mostly wrong key outscores the true key, "so better search cannot help". Related-language decipherment is "not identifiable at any corpus size".

## Why these claims are wrong or too strong
1. **The search_scaling verdict used the wrong comparison.** It compared restarts with the *true* key. The relevant reference is the *truth-climbed* key: a greedy climb from the true key under the same objective, which is what the objective actually prefers near the truth.
   - Recomputed from `experiments/search_scaling/out/runs.jsonl` against `climb_score` in `experiments/redteam_decipherability/out/runs.jsonl`. Same cipher and model (`ss.setup` = `rt.one_run`, q = 0, K2, 2.5k, 200 restarts).
   - Number of the 200 blind restarts that score above the truth-climbed key:

     | Pair | rep 0 | rep 1 | rep 2 |
     |---|---|---|---|
     | Finnish / Estonian | 190 | 195 | 171 |
     | Latin / Italian | 0 | 0 | 1 |

   - **Finnish / Estonian:** a statistical failure. The objective prefers wrong keys, so more search cannot fix it.
   - **Latin / Italian:** a search failure, close to a tie. In rep 2, a key that is 20% right (−10,899) beats the 77%-right truth-climbed key (−10,915).
   - The search also had no swap moves (see `mismatch_study_fix1.md`).
2. **"Flat with more text" is falsified by our own stronger attack.** `mismatch_study` stage 1 ran a related model (Latin with Italian, syllabary) with 1,000 restarts plus swap polish (A3). It recovered 0.62 at 10k and 0.66 at 30k (one replicate each). The weaker attacks scored 0.13-0.37 on the same cells. So the 10-26% plateau measured weak search, not a limit of the data. That study's sealed verdict is KILL.

## Corrected statements
- **search_scaling:** at 2.5k, Latin / Italian is search-limited (near-tie). Finnish / Estonian is limited by the objective. The sealed H0 verdict is withdrawn for Latin.
- **Atlas 1.8 / decipherability:**
  - Whether related-language recovery is limited by the objective or by search depends on the pair.
  - With heavy search it can rise well above the weak-search plateau at 10k-30k (Latin / Italian 0.62-0.66).
  - "Not identifiable at any corpus size" and "more text never helps" are withdrawn.
- **What still stands:**
  - The Indus verdict stays "Untestable", for a different reason. Indus's relatedness to any candidate is unknown, the planted-language power is z 0.3-2.8, and the corpus has about 400 signs.
  - The shuffle trap ("beats a shuffle" proves nothing) stands.

## Follow-up
A small sealed check at Indus size (2.5k, 1,000 restarts with polish, anchors 0/5/10) decides how the reason is worded. It does not decide whether Indus is testable.
