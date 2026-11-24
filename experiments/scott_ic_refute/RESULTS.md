# Scott (Dunn) key, refute-only IC bench (prereg `docs/prereg/scott_ic_refute.md`, sealed 2026-11-24)

Key: J. Scott Dunn, *MahaSamVani: The Lexicon of the Indus Script* v3, doi 10.5281/zenodo.21522783 (CC BY-NC-ND). It was scored locally. No key values appear here.

## Sealed verdict: untestable at stated power (K1). Her key was not scored.
| step | result | bar |
|---|---|---|
| 0. coverage (distinct M77 tokens) | **94.4%** of 10,005 (all texts 94.1%) | ≥ 90%: met |
| K2 saturation, LMIN 4 | density 0.122; random-key mean IC **0.703** (first alternative only 0.644, swaps off 0.623) | ≤ 0.25 and ≤ 0.50: **failed** |
| K2 saturation, LMIN 5 (the one allowed fallback) | density 0.024; random-key mean IC 0.428 (0.363, 0.334) | met, so LMIN = 5 |
| W_real (her key's shuffles on the real corpus) | **0.061** | — |
| K1, fully right planted key beats max(W_planted, W_real) | **0 of 5** | ≥ 3: **failed** |
| K3 (40 corpora, reported) | 0 of 40; a key right on 75% of tokens: 0 of 40 | ≥ 32 |
| plant | miss 0.07, stream skipped 0.78; top-50 bigram share 0.195 against 0.295 real | the plant is **not formula-faithful** (< 0.8 ×) |

- **Planted null widths:** median 0.035 (range 0.027-0.049), against 0.061 on the real corpus.
- **Partial ladder** (corpora 0-9, report only):
  - Mean IC rises 0.428 → 0.467 → 0.500 → 0.541 → 0.572 at 0 / 25 / 50 / 75 / 100% of tokens right.
  - The rise is strict in 10 of 10 corpora. The planted signal is there, but it is smaller than the real null's spread.

## What it means
- **A fully right key of her shape, on Rigveda text, would not beat its own shuffles on this corpus.**
  - The real corpus is formulaic, so shuffling a frequent sign's value moves whole formulae. That widens the null to about twice the planted width.
  - A fit test therefore cannot refute her key. It also cannot support it: no pass could mean anything (`yj_ic_refute`).
- **At LMIN 4, her rules let random keys "read" 70% of consonants as Sanskrit words.**
  - Her slashed alternatives and sound swaps make the dictionary fit nearly anything.
  - Even at LMIN 5, random keys fit 43%.
- **The plant is a weak stand-in.** It is not formula-faithful, and 78% of the stream was skipped. Both lower power, so X = 0 is an upper bound and is labelled as such.
- **This repeats `yj_ic_refute` for a second near-full key.** Dictionary fit cannot test published Indus phonetic keys at this corpus size. Evidence has to come from outside fit: forward predictions, or ties to objects and pictures.

Files: `values.py`, `run.py`, `result.json`, `run.out`. Inputs are local only (`.local/scott_lis/`).
