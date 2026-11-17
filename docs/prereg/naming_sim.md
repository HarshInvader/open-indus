# Pre-registration: naming_sim (Fable 5.2 plan item 11, naming-system typology by simulation)

Registered 2026-11-15 in `experiments/naming_sim/`. Script hashes are in `docs/prereg/HASHES.txt` (tag naming_sim).

## What was already seen before this was written (disclosure)

- Indus dev core statistics at n = 800 types (they are the targets, and were known from typology, core_semantics and pair_numeral_long): len1 0.256, standalone 0.907, both_orders 0.063, hfi 0.454, pol_ex 0.145, both_pos 0.714, cls_self (fish) 0.43.
- The Indus dev generator fit (`fits/indus_dev.json`). Only its frequency profile (V, zipf) is used downstream.
- Real-list statistics (`raw_stats.json`), identifiability of the generators (`identify.json`), leave-one-tradition-out validation (`validate.json`), self-recognition (`selfcheck.json`), real-list calibration (`realcmp_calib.json`), and the numeral-element shares (`numerals.json`, including the Indus dev figure of 41% of texts with a numeral+sign formula).
- NOT yet run: `realcmp.py indus` (Indus vs real lists), `score.py` (Indus vs generators), and any held-out (`dev_heldout(version=2)`) naming statistic.

## Calibration facts that constrain what can be claimed

1. The generators are identifiable from each other on their own simulations: LDA CV accuracy 0.998 at n = 800 and n = 423.
2. However, the generator family does not reproduce real onomastica. 10 of 13 real lists (and Indus) are rejected by their OWN fitted generator (p <= 0.02). In leave-one-tradition-out validation, a real list landed on a relative in 1 of 7 cases. **So generator-based ranking (score.py) is SECONDARY and descriptive. It may not decide the verdict.**
3. Model-free real-list comparison: 0 of 7 family members (Germanic x3, Chinese x2, South Asian x2) have a family member as nearest neighbour (chance about 1 in 7 per list). The statistics capture name-structure type, not tradition or language family. **No family-level or language-level conclusion may be drawn from the Indus ranking.** The real-list nearest-neighbour distances run from 0.60 (median 0.87) to a maximum of 1.21.

## Statistics (frozen: `stats.py`)

PRIMARY = len1, standalone, both_orders, hfi, pol_ex, both_pos, computed on distinct name types; definitions are in the `stats.py` docstring. SECONDARY = cls_self (class self-compounding; Indus class = fish family; reference class = animal elements). Distance = `realcmp.distance`: RMS of z-differences over the PRIMARY statistics, scaled by the across-system SD of real-list means (`realcmp_scales.json`). Sample size is matched pairwise: n = min(nA, nB, 800) for dev and min(nA, nB, 423) for held-out.

## Tests

| id | question | rule | outcome labels |
|---|---|---|---|
| P1 | Is Indus inside the range of real naming systems? (dev) | d_NN(Indus dev) vs real-list NN distribution: > 1.21 (max) = outlier; 0.87-1.21 = peripheral; <= 0.87 (median) = typical | outlier / peripheral / typical |
| P2 | Same on held-out | d_NN(Indus held-out, n <= 423) with the same thresholds | replicates P1 if same label |
| P3 | Which statistics separate Indus from its nearest systems | report statistics with \|z\| >= 2 vs each of the 3 nearest systems; predicted: standalone (Indus higher), pol_ex (Indus lower), both_pos (Indus higher) | prediction met if all three appear for the nearest system, on dev and held-out |
| P4 | Key comparison: Germanic dithematic vs Sanskrit compound vs Chinese given names | report the distances of Indus to old_english, old_high_german, old_norse, sanskrit, sangam, chinese_given. Declared UNDECIDABLE in advance at the family level (calibration fact 3); reported for the type question only | descriptive |
| P5 | Ranking stability | leave-one-statistic-out nearest system (6 runs), dev and held-out | stable if one system is nearest in >= 5 of 6 runs on both splits |
| S1 | Generator ABC (score.py) | posterior and GOF per system, dev and held-out | descriptive only (calibration fact 2) |
| S2 | Lexical class self-compounding | Indus cls_self (dev and held-out) above the maximum cls_self of every real list with a definable animal class (`raw_stats.json`: max -0.095, old_english) | pass if both splits exceed it |

**Overall verdict rule.**
- If P1 and P2 both give "outlier": **no tested naming system produces the Indus core statistics.**
- If both give "typical" or "peripheral" and P5 is stable: name the nearest structural type, but make no family claim.
- Anything else: **undecidable.**

Multiple testing: P1, P2, P3, P5 and S2 are 5 registered decisions. They are threshold rules, not p-values, so the ledger records them as decisions with no p-value.

## Run
```
.venv/bin/python -I experiments/naming_sim/realcmp.py indus
.venv/bin/python -I experiments/naming_sim/score.py
```
