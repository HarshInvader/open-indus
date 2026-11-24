# Formula reuse × key looseness on the true Linear B key (`lb_formula_dial`)

Prereg `docs/prereg/lb_formula_dial.md`.
- Sealed v4 (tag `lb_formula_dial`) after two fresh reviews; code sealed separately (`lb_formula_dial_code`).
- Run from the repo root: `nice -n 20 .venv/bin/python -I experiments/lb_formula_dial/run.py kill`, then `full`.
- Outputs: `kill.json`, `full.json` and the `.out` logs.

**Reading (frozen): "Both needed."**
- **Formula reuse alone:** the true Linear B key keeps its refute power at Indus formula excess.
- **Looseness alone:** it also keeps its power at Scott-level looseness (1.18 values per sign).
- **Both together:** it loses its power.
- **Null width:** formula tilt barely widens the null (r = 1.07). The loss comes through the signal, not the null.

## Kill test
- **K1 passed.** Untilted, one value per sign: 20/20, scrambled 0/20, every per-draw value equal to the sealed `lb_shape_ladder` R1 to 1e-9.
- **D1 (duplication only) was unreachable** at the feasibility gate (needs about 3.5 × n_k tokens). Per the prereg it is removed from every reading.
- **G0 did not apply.** The F0 median excess over a unigram shuffle is 0.127, against 0.159 for M77 distinct seals.
- **F1 and F2 were reachable.** 18 of 20 draws were built for each; the 2 failed draws count as non-passes.

## Cells (passes of 20 at power read against the cell's own null; scrambled-text control in brackets)
| formula ↓ / values per sign → | 1.0 | 1.18 (Scott's shape) | 2.0 (stress; 1.78 actual) |
|---|---|---|---|
| F0: none added (R1) | **20** (0) | **17** (0) | 2 (1) |
| F1: Indus excess | **16** (1) | **12** (0) fails | 2 (0) |
| F2: 1.5 × Indus (stress) | 10 (0) | 6 (0) | 1 (0) |

- **Primary cells:**
  - F1 × 1.0 passes, exactly at the bar of 16;
  - F0 × 1.18 passes, at 17;
  - F1 × 1.18 fails, at 12.
- **Median margins** (true IC minus null p99): F0 × 1.0 +0.021; F1 × 1.0 +0.015; F0 × 1.18 +0.010; F1 × 1.18 +0.002.
- **Stress limits** (they decide nothing):
  - at 1.5 × Indus excess even the one-value key falls to 10/20;
  - at about 1.8 values per sign every row falls to 1-2/20.

## What it means
- **Scott's verdict.** Her key's shape (about 1.18 values per sign) on Indus-like formula reuse is a regime where **a fully right key would fail this bench**. So "untestable at stated power" (atlas 1.1) is what the standard predicts, and not a property of her key.
  - Limit: 24 of her 56 loose signs vary in consonant count, which this dial does not model. Her real looseness is larger than 1.18.
- **Yajnadevam's verdict is not explained.** His key has 1.00 values per sign, and F1 × 1.0 passes (16/20, at the bar). His power loss comes from what was not dialled: the generous matcher (one key letter for several sounds), his lexicon, or his plants. Next: `lb_wrong_lexicon` (brief 9, study 2) and a matcher dial.
- **Method limit, recorded.** At about 4,000 tokens the IC refute standard holds for a one-value key at Indus formula excess only at the bar (16/20, with a margin of 0.015). Any added looseness takes it below power.
- **No rerun of either key is licensed** (frozen rule). No scorecard tier changes.

## Limits (from the prereg)
- K1's outcome was known, so it is a calibration check, not a blind test.
- A tilt changes content as well as reuse.
- Excess over a unigram shuffle is one measure of formula reuse.
- About 4,000 scored tokens, against 10,000-12,000 in the real runs.
- One script, one lexicon (Homeric), one statistic.
- The three primary cells are read with fixed bars and no multiplicity correction.

## Implementer choices (disclosed)
- Failed draws count as non-passes out of 20.
- A τ draw fails if the excess at τ = 8 is still more than 0.005 short.
- All cells share R1's N1 seed.
- Donors for loose values are picked uniformly among signs with another value. At 2.0, 16 signs have no donor, giving 1.78 actual.
- The M77 target draws filter to seals before deduplication and cut to n̄ = 4,014 tokens.
