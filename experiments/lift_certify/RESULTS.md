# Lift certify: stopped at K0. The sealed score cannot restore signs even on planted lexicon text.

- **Prereg:** `docs/prereg/lift_certify.md`, sealed 2026-11-24 as v3 (tag `lift_certify`).
- **Code:** `run.py`, hashed before any run (tag `lift_certify_code`). The hash was re-checked before running.
- **Run:** `run.py kill`, detached with a pid file, under the Indus compute lock and `board/run.sh`.
- **Outputs:** `kill.json`, `kill.out`.
- **Scope:** no Indus step exists in this study, and no Indus key was scored.

## Result
- **Checks before K0:**
  - A1 reproduced the sealed R1 true and N1 ICs exactly.
  - A2 counts held: median 1,375.5 clean positions, reachable share about 49%.
  - F3 did not fire: the trigram-only Hit@1 on the plant was 4.4-5.4%, far below 60%.
  - F4 did not fire.
- **K0, full-dose planted language, draws 1-5: failed.**
  - The bar was a true-key lift of at least 10 points in 5 of 5 draws.
  - The true key's chosen λ* was 0 in every draw, so the lift was 0. In draw 1, development Hit@1 fell as λ rose: 110 → 110 → 110 → 107 → 95 → 81 for λ 0 to 4.
  - The scramble and N1 bars were met, at lift 0.
- **Frozen reading:** "The pipeline cannot restore signs from a lexicon even on text made of lexicon words." Nothing else runs. K1-K4 were not run.

## Diagnosis (after the stop, from code reading and draw-1 counts; decides nothing)
- **Code faithful:** an independent check of `run.py` against the prereg found no bug.
  - The bonus has the right sign and is computed on the masked candidate through the true key.
  - Masking does not leak, and the λ rule matches the prereg.
- **Cause: the frozen design.** The bonus (λ × lexicon-covered consonants, via the sealed `ic_seg` on the full Homeric lexicon) fails to pick the right consonant value.
  - At λ = 1 the top candidate changed at 526 positions. 20 became correct, 57 took the right value with the wrong sign, and 449 took a wrong value; 314 of those cover more consonants than the true sign.
  - Net effect: 20 gained, 21 lost.
- **Why the bonus can't separate candidates:**
  - At the full lexicon's density, chance matches give some coverage at 81% of positions.
  - On average 19 candidates, spread over 3.9 values, tie at the maximum.
  - Chunks cut to M77 lengths from a continuous word stream leave only 8.6% of positions inside an intact planted word.
- **Room was there.** Series ambiguity alone does not block the bar: a perfect value-level bonus would reach about 22% Hit@1 against the trigram's 4.4%.

## What this can and cannot say
- **It can say:** this score (trigram plus λ × lexicon-covered consonants, Hit@1, LMIN 4, the full Homeric lexicon) gives no restoration lift even when the text is made only of lexicon words. So it cannot serve as a certify statistic at this shape and lexicon density.
- **It cannot say:**
  - whether restoration lift by another score could certify a key, for example a word-level likelihood, a thinner lexicon, or positions inside reachable segments only;
  - anything about any key.
- **The route is not closed.** The held-out-prediction route is closed only for this score. Testing another score needs a new prereg; it cannot rerun under this name.

## Disclosures
- **Implementer choices:**
  - The `bench_restoration` trigram was copied line for line, because that module loads data when imported.
  - The sealed build and N1/N2 random streams were replayed.
  - Twelve `# PREREG-AMBIGUITY:` points are listed in the implementer's report; none bears on K0's failure.
- No rerun, no tuning, no fix tags.
