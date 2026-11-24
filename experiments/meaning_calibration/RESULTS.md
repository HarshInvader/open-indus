# meaning_calibration: kill test (prereg `docs/prereg/meaning_calibration.md`, sealed 2026-11-24T09:02:39Z)

## Verdict: the kill test FAILED, so the study stops as sealed
- **F planted power: 0.455** (71 of 156 planted heads survive; 44 more could not be planted). The bar was 0.8.
- **F false alarm: 0 of 1,000** on within-text shuffled draws. The bar was ≤ 0.05.
- **Sealed outcome.** "The form behind our S meaning rows is underpowered at Indus size in a read script", as sealed. No claims were written, and no parameter was changed.

| dev next-tokens of head | planted | power |
|---|---|---|
| 10-19 | 64 | 0.75 |
| 20-49 | 51 | 0.45 |
| ≥ 50 | 41 | 0.00 |

Draws: 5 × (1,680 dev + 565 held-out documents). Eligible heads per draw: 77-84; eligible in every draw: 62 (22 ideogram/measure, 17 numeral, 23 word).

## Why (exploratory diagnosis, after the verdict)
- **All 85 planted failures have the same cause: the p-value floor.**
  - With a one-partner claim, the null holds every token within ½-2× of the partner's frequency. The p34 rule uses pairs only when there are secondary partners.
  - For a frequent partner that is 7-98 tokens, so p ≤ 0.01 cannot be reached.
  - Planting at ceil(0.4·n) makes a frequent head's partner frequent, so power falls to 0 as frequency rises.
- **Every planted head with ≥ 99 pseudo-partners survived** (71 of 71).
- **So the failure is the test's resolution, not the signal.** At Indus size the rule cannot pass a one-partner claim about a frequent partner, whatever the data say.
- **Indus rows.**
  - MC-PAR-murukan-partners used a main partner plus the squirrel set, so its null is pairs and is large (gate 48/50).
  - MC-WEL15-fish-number rests on the six + fish test (README #5), not on this rule.
  - Neither S row is changed by this result.

## E power report (no claims, no verdict)
- Full corpus, single stage. The null is the within-site permutation of object class.
- Tokens reaching power ≥ 0.8 for a 2× enrichment:
  - sealings (134 documents): 5 of 467;
  - sealing + vase (188 documents): 6 of 467.
- All of them are numerals, measure signs or OVIS:m, so object-class enrichment cannot be calibrated on Linear B.
- MC-MUK19-stroked-jar-MET stays uncalibrated, as the prereg says.

Files: `kill.py`, `fcore.py`, `load.py`, `kill.json`, `kill_draws.json`, `kill.out`.
