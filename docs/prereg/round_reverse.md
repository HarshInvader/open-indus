# Prereg: round-seal reversal (Fable 5.2 plan 11, candidate 6)

Written 2026-11-21, before any reversed text was scored. Code: `experiments/round_reverse/run.py`, hashed with this file (tag `round_reverse`).

## Seen before writing

- Set sizes only: 35 round texts (10 home, 18 abroad, 7 unprovenanced), 32 with 2 or more signs, 28 with a readable last sign, 1 palindrome.
- The old forward numbers from board #41: Kneser-Ney order excess +2.10 bits/sign matched on length, +1.35 matched on format (F0), n = 31.

## Question

Round Gulf-type seals put person signs first and numerals last. Home seals do the reverse. Are round texts just home texts read in the wrong direction? If so, reading them backwards should make them look like ordinary Indus order.

## Method

- Units, order models and the matcher are copied unchanged from `experiments/redteam_round_seal_format/run.py`: Kneser-Ney bigram (KN, primary), Wells class grammar (GR) and positional (POS) models fitted on distinct home texts, 10-fold out-of-fold for home texts.
- Order excess of a text: d = bits of the text minus the mean bits of up to 200 permutations of its own signs.
- Set excess E = mean d of the round set minus the mean d of square home seals matched on length (and, for F0, on numeral-first, opener-first, closer-last).
- Each round text is reversed sign by sign. Format features are recomputed on the reversed text. The reversed text of a home seal is scored by the same out-of-fold model as the forward text.
- Primary set: every round text the models can score (2 or more signs; n = 31 under KN in #41). The "28 round texts" of README #4 (readable last sign) are reported as a secondary set.
- Ratio = E_reversed / E_forward, with a paired bootstrap CI over texts.

## Controls

- C1. Direction sensitivity: 400 home square seals reversed. Their mean d should rise clearly, showing the models see direction.
- C2. Planted direction error: square seals matched to the round set's length strata, written backwards, then read forwards again, 100 repeats. Reversal should remove most of the planted excess (ratio below 0.5 in at least 80% of repeats). If it does not, the test cannot see a direction error and the result is uninformative.

## Prediction

Reversal does not remove the off-order. Plan 11 puts the chance of a hit at 1 in 12.

## Decision rule (KN, F0 matching, primary set)

- **Dent**: ratio below 0.5 and the reversed excess not significant (p of 0.05 or more). Then finding #4 is largely a reading-direction effect on round seals.
- **Partial**: ratio below 0.5 but the reversed excess still significant. Finding #4 is partly a direction effect.
- **No dent**: ratio 0.5 or more. Direction does not explain finding #4.
- GR and POS are reported as checks. If control C2 fails, the verdict is "uninformative" whatever the ratio.

One primary test. Others descriptive.
