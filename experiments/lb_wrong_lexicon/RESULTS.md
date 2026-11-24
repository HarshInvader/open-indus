# Wrong lexicon and matcher dial: partly language-specific; at LMIN 5 the bench loses power before looseness is added

Prereg `docs/prereg/lb_wrong_lexicon.md`, sealed 2026-11-24 as v5 (tag `lb_wrong_lexicon`); code `run.py` hashed before any run (tag `lb_wrong_lexicon_code`), hash re-checked before each mode. Run from the repo root under the Indus compute lock: `nice -n 20 .venv/bin/python -I experiments/lb_wrong_lexicon/run.py kill`, then `full`. Outputs: `kill.json`, `kill.out`, `full.json`, `full.out`. Full run 357 s.

No Indus key is scored. No outcome here supports or counts against any Indus key, and none licenses a rerun.

## Kill test (all passed)
- **K3, matched density:** G, Fi, Id, Hu met their bounds (thinned density at 4 consonants 0.176-0.177). Es (0.159) and Od (0.125) are below, as expected; both are report-only.
- **K1, reproduction:** true key vs Homer at LMIN 4, 20/20, scrambled control 0, values equal to `lb_formula_dial` to 1e-9. Same again after the LMIN global was patched to 5 and restored.
- **K2, null calibration:** wrong keys in 13 cells, 260 draws. No void cell; pooled wrong-key pass rate 0/260. No draw needed more than the 100,000-try cap.
- **KG, planted answer** (run first in `full`): true key vs modern Greek 17/20, control 0. **KG holds.**

## Arm A: does the bench detect the language?
True key, F0 text, LMIN 4, all lexicons thinned to Homer's density (except where noted).

| lexicon | role | passes / 20 | scrambled | median margin |
|---|---|---|---|---|
| H Homer | sealed lexicon | 20 | 0 | +0.021 |
| G modern Greek | planted right answer | 17 | 0 | +0.011 |
| Id Indonesian | wrong | 14 (edge) | 1 | +0.008 |
| Hu Hungarian | wrong | 10 | 0 | −0.001 |
| Fi Finnish (Kalevala) | wrong | 6 | 0 | −0.004 |
| Es Spanish | report-only (density 0.159) | 20 | 0 | +0.017 |
| Od Odyssey only | report-only (density 0.125) | 20 | 0 | +0.021 |

**Frozen reading: "Partly language-specific."** KG holds; Fi and Hu fail clearly; Id sits at 14, so neither "language-specific" (all three ≤ 12) nor "structure, not language" (Fi ≥ 16 or two of three ≥ 16) applies.

Described, deciding nothing:
- The two non-Indo-European lexicons that are furthest from Greek (Finnish, Hungarian) fail; Indonesian is at the edge.
- **Spanish, a wrong Indo-European language, passes 20/20 with a margin above modern Greek's**, at a lower density (0.159 vs 0.177, so not matched). It is report-only by the sealed rule, so it enters no reading. It does mean a refute pass on this bench should not be read as identifying the language, only as consistent with it.
- The Odyssey-only list (same language, thinner) passes 20/20 with H's margin.

## Arm B: does a generous matcher remove power?
All primary cells use rule LMIN 5, because every loosened rung needs it.

| cell | F0 (no formula excess) | F1 (Indus formula excess) |
|---|---|---|
| B0 control (no added looseness), LMIN 5 | **8** | 6 / 18 built |
| B1 (step 3), LMIN 5 | 8 | 8 / 18 |
| B2 (step 9; primary), LMIN 5 | 7 | 5 / 18 |
| B3 (step 11; report-only), LMIN 5 | 9 | 5 / 18 |

Report-only, LMIN 4: B0 20 / 16; B1 19 / 17; B2 18 / 15.

**Frozen reading: "LMIN 5 alone removes power."** The control with no added looseness passes only 8 of 20 at LMIN 5. So on this text shape, scoring only words of 5+ consonants costs the power, and the loosened cells cannot separate looseness from that. All other Arm B readings are "not separable from the LMIN change". The F1 control is also below the bar, so Arm B is read on F0 alone.

Paired draws (described only): B2 vs its control on F0, 4 draws pass the control and fail B2, 3 the reverse; on F1, 3 and 2. Adding looseness at LMIN 5 moves almost nothing beyond what LMIN 5 already did.

At LMIN 4 (report-only), looseness at B2 density costs 2 passes on F0 (20 → 18) and 1 on F1 (16 → 15).

## What this can and cannot say about `yj_ic_refute`
- **It can say:** on Linear B with a Homeric lexicon at about 4,000 tokens, a true key with one value per sign loses refute power once the scorer counts only words of 5+ consonants. That happens before any matcher looseness is added, and adding looseness at roughly the density, token share and sounds-per-letter cap of that bench's encoding of his stated latitude does not lower it further in a way this test can see.
- **It cannot say:**
  - whether Yajnadevam's key is right or wrong;
  - whether matcher looseness explains the low planted power in `yj_ic_refute`. The LMIN 5 effect holds on this text shape, where 18.6% of key consonants sit in segments of 5+; on the `yj_ic_refute` corpus the figure is 47.4%, so LMIN 5 may cost far less there. Language, lexicon, alphabet size, overlap pattern, plant and corpus size (about 12,000 tokens) also differ;
  - anything about his readings, which involve choices outside the key.
- So the question the coordinator asked, whether matcher looseness explains that result, is **not answered** by this design. A test that could answer it would keep LMIN fixed at a value where the bench has power and vary only looseness, or rerun the dial on a text shape with about 47% of consonants in long segments.

**Note from the saved `yj_ic_refute` results (added 2026-11-24, recomputed from its `full.json`, not from this study).** At the real corpus's null width the planted Sanskrit key passed 5/20 under the generous matcher and 2/20 under the strict one. The real-text null was 2.1 times (generous) and 2.7 times (strict) wider than the planted null; both observations point to the corpus rather than the matcher as the source of the low planted power.

## Limits (from the prereg)
- At every loosened rung d and t stand for the same sounds, so the dial merges two key letters; the generous matcher merges none.
- Added looseness covers about 25% of tokens, against 49.4% on that matcher's four loosest letters.
- The dial is thinner than the target at 6 consonants (B2 0.0051, B3 0.0078, target 0.0128).
- The planted answer (modern Greek, Wikipedia) is 2,700 years from the Linear B texts and overlaps Homer barely more than Kalevala does; it still passed.

## Disclosures
- Implementer choices, listed in the implementer's report and marked `# PREREG-AMBIGUITY:` in `run.py`: Latin word runs are Unicode letter runs; K3 runs before K1 (label-free, following the prereg's "Cost" order); the Kalevala file is used whole, Gutenberg header included; g is a token-weighted reconstruction (report-only); KG runs at the start of `full`. K3 matched the sealed table on every usable lexicon, so the counting guesses did not change the data.
- F1 builds 18 of 20 draws, as in `lb_formula_dial`; F1 cells are out of 18.
- No rerun, no tuning, no fix tags.
