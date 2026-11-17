# Red team of #23: is the round-seal order anomaly real? (board #25, H11)

**Verdict: it survives, with one correction to the wording.** I matched ordinary home seals on rare-sign load as well as length, then re-scored with two more order measures and ran planted controls. The 8 round seals found in the Indus area still have much weaker Indus sign order than ordinary seals, and as weak as the round seals found abroad.

The correction: "no more Indus-like than shuffles" is too strong. 6 of the 8 texts still beat most shuffles of their own signs. Their order is weak, not absent: about 10% of the order gain an ordinary seal shows.

The anomaly sits in which sign follows which (KN bigram, Wells grammar). It is not clear in where signs sit (first, middle, last): the positional model gives p=0.077.

By the pre-registered rule the verdict is SURVIVES. For #4 this changes nothing: a crib attack on off-order foreign seals still needs the home round seals as its control.

Pre-registration: `docs/prereg/redteam_round_order.md`. Its sha256 was appended to `docs/prereg/HASHES.txt` before any new score was computed. Code: `run.py` (pre-registered) and `posthoc.py` (not pre-registered). Outputs: `results.json`, `posthoc.json`, `run.log`, `posthoc.log`. `out/scores.pkl` is a 58 MB cache and can be deleted. Ledger rows: `ledger_rows.csv`.

## Setup
- **Groups:** the same as #23. 3,177 distinct native ICIT texts; 1,769 home square and rectangular seals have a distinct permutation.
- **Home round texts (8):** 114.1, 2419.2, 2911.1, 2912.1, 2977.1, 3668.1, 4247.1, 5468.1.
- **Foreign round texts:** 16.
- **Order component:** d = bits of the real order minus the mean bits over up to 200 shuffles of the same signs. The same shuffles were used for all three scorers.
- **Scorers:**
  - KN bigram: 10-fold CV.
  - Wells class-bigram grammar (GR): glib.ClassBigram, K=20, 5-fold CV.
  - Positional model (POS): glib.PositionModel, which uses only P(sign | position) and P(stop).
- **Rare load:** the number of tokens in the text whose sign is seen fewer than 10 times in the fold's training data.
- **Null N1:** draws of home seals matched on (length, rare load).
- **Rare load of the groups:** 27% of tokens on home round seals and 25% abroad, against 14% on ordinary home seals. So rare signs were a fair suspect.

## Pre-registered results
### Primary tests: home round (n=8) vs home seals, null N1
| scorer | home round mean d | matched null | excess | p | Holm p |
|---|---|---|---|---|---|
| KN | -0.17 | -1.81 | **+1.64** | 1e-4 | **3e-4** |
| Wells grammar | -0.38 | -1.22 | **+0.84** | 0.010 | **0.020** |
| positional | -0.27 | -0.71 | +0.44 | 0.077 | 0.077 |

Rare-sign matching cuts the KN excess only from +1.92 (length-only null, which reproduces #23's +1.96) to +1.64. Rare signs explain about 14% of it.

### Planted controls
1,000 replicates of 8 texts each.

| control | KN | GR | POS |
|---|---|---|---|
| C1: rare-matched home seals, shuffled within text (power) | **1.00** | 1.00 | 0.83 |
| C2: rare-matched home seals, unshuffled, flag rate under N1 | **0.049** | 0.051 | 0.046 |
| C2: same texts, flag rate under the length-only null | 0.143 | 0.165 | 0.060 |
| C2b: top-quartile rare-load seals, unshuffled, under N1 | 0.072 | 0.059 | 0.032 |
| C2b: same texts, under the length-only null | 0.176 | 0.165 | 0.042 |

- #23's length-only null is mildly confounded: it flags 14-18% of ordinary rare-sign-heavy seals.
- The rare-matched null is calibrated, at about 5%.
- At the round seals' rare load the tests still catch shuffled texts every time.

### Sensitivity
**Leave-one-out (N1):**
- KN: excess +1.44 to +1.72, max p 6e-4.
- GR: +0.74 to +0.99, max p 0.026.
- POS: max p 0.18.

No single text carries the result.

**Broken texts.** Four of the 8 contain a break or are marked incomplete in ICIT: 2419.2, 3668.1, 4247.1, 5468.1. The cleaning step joins signs across the gaps. For example, 5468.1 `W688 W317 # W002 W361` gets an invented `W317→W002` pair.
- The 4 complete texts alone, against complete home seals: KN +1.46 (p=0.005), GR +0.88 (p=0.034), POS +0.37 (p=0.22).
- Adding a broken-text stratum to the null: KN +1.56, GR +0.77.

The broken texts are not the cause.

**2977.1 reading direction.** This text is marked boustrophedon in ICIT, and M77 2604 has its two lines in a different order. Reading it reversed gives KN +1.75, p=1e-4.

**No-near-copy reference** (#23's Jaccard rule, 1,164 seals): KN +1.40, GR +0.68 (p=0.02), POS +0.39 (p=0.11).

**Foreign vs home round.** I standardised d by the rare-matched null, then compared the two round groups:
- KN +0.11 (p=0.66),
- GR +0.48 (p=0.13),
- POS +0.05 (p=0.87).

The foreign anomaly itself also survives rare matching: KN +1.75, GR +1.32, POS +0.49 (p=0.005), all against home seals. So the two round groups do not differ, and the foreign anomaly is not a rare-sign effect.

## Post hoc checks (not pre-registered)
- **Leave-two-out, all 28 pairs:** KN worst p=0.002 (dropping 4247.1 and 5468.1). GR worst p=0.057 (dropping 114.1 and 2977.1), with 26 of 28 pairs at p<0.05. The grammar result is the softer one.
- **Median instead of mean:** KN +1.61 (p=0.001), GR +0.90 (p=0.011).
- **Shuffle percentile.** Only 2 of 8 texts have real order no better than half their shuffles (KN q≥0.5), against 7% expected for matched seals (p=0.09). Mean KN q is 0.38, against 0.10 for matched seals. The two texts are 2419.2 and 5468.1, both broken.

So the round texts mostly still prefer their real order, but by a small margin. This is why I correct #23's "shuffle percentile ~0.5" wording. Fold assignment matters for small texts: my q for 2911.1 is 0.0, while #23 had 1.0. That text has 2 signs and one rare sign.

## Are the 8 really round or cylinder seals? (documentary, local sources only)
| ICIT | catalogue | shape evidence | reading |
|---|---|---|---|
| 114.1 | Chanhu-daro C-32 | ICIT type SEAL:C only; our Chanhu-daro report OCR is unreadable | — |
| 2419.2 | M-2039 | ICIT SEAL:C, 19.1x19.1 mm, two sides; side 2 starts broken | fragment |
| 2911.1 | M-415 | Mackay: "round seal with perforated boss" | M77 2500 agrees |
| 2912.1 | M-416 | Marshall: one dimension only (0.94 in, i.e. a diameter) | M77 1309 agrees |
| 2977.1 | M-500 | Mackay: "round, thin, no boss, inscribed on both sides" | M77 2604: line order differs |
| 3668.1 | M-1369 | ICIT SEAL:C only; CISI 2 register row gives no shape | M77 1478 agrees; end broken |
| 4247.1 | Dholavira | ICIT SEAL:C only | start broken |
| 5468.1 | Rakhigarhi | ICIT SEAL:CY, 27.5 mm | break mid-text |

Three objects are round by a printed excavation register: M-415, M-500 and M-416. The other five rest on ICIT's type code alone. CISI's example of Late Harappan round seals is C-45 to C-50. C-32 is outside that run, but this does not establish its date or its form. I could not confirm any of the five from a photo or description.

## Hypotheses
| hypothesis | verdict |
|---|---|
| The round-seal order anomaly is a rare-sign artefact | refuted (KN +1.64 under rare-matched null; null calibrated at 5%; power 1.0) |
| It is specific to the KN scorer | refuted for adjacency (grammar +0.84, Holm p=0.02); positional placement not significant (+0.44, p=0.077) |
| It rests on one or two texts | refuted for KN (LOO max p 6e-4, leave-two-out max p 0.002); GR borderline on one pair (0.057) |
| It comes from broken/joined texts or 2977.1's direction | refuted (complete-only +1.46, p=0.005; reversed 2977.1 +1.75) |
| Round texts are "no more Indus-like than shuffles" | partly refuted: weak but mostly present order (mean q 0.38 vs 0.10; 2/8 at q≥0.5) |
| Foreign round seals differ from home round seals in order | not supported (KN +0.11, p=0.66; GR +0.48, p=0.13) |

## What was not checked
- I did not confirm shape for 5 of the 8 objects. C-32, M-2039, M-1369, Dholavira 4247.1 and the Rakhigarhi cylinder are SEAL:C/CY on ICIT's word alone. CISI vol. 3, the Dholavira and Rakhigarhi reports, and photos are not held.
- Sign-by-sign readings were not checked against photos.
- **Compute cuts:**
  - grammar fits used 2 restarts instead of 5, and 5 folds;
  - planted controls used 1,000 replicates against 2,000 null draws each;
  - leave-one-out used 5,000 draws, and leave-two-out used 3,000.

  Total about 1 CPU-minute.
- n=8 stays the ceiling. A planted test at this size has full power, but per-object claims are descriptive.
