# Red team of seal_fate H2 (board #37): closer excess on Mohenjo-daro "?"-dimension seals

## Verdict: WEAKENED, close to failing. Most of the excess is mechanical.

- seal_fate's null said the "?" seals carry 1.97x the expected share of closers. Under the end-anchored null the task asked for, the ratio falls to **1.37x (closer share 0.173 vs 0.126, z = +2.06, p = 0.049)**. That is a bare pass at alpha 0.05 and would not survive any correction.
- Compare each "?" seal with intact texts broken the way that seal is broken (Mahadevan's own break marks), and the excess is 1.26x, **p = 0.081**. Compare with whole intact texts of the same length and it is 1.18x, **p = 0.30**. By the pre-registered rule that makes the verdict WEAKENED, not SURVIVES.
- The excess comes from two plain facts:
  - "?" seals carry short texts: mean 3.9 signs vs 4.9 in the pool (Mann-Whitney p = 0.003). Short texts end in a closer more often.
  - 13 of the 34 lost the start of the text and kept the end. This is about 1 in 5 among other broken seals (Harappa 12/62, Fisher p = 0.054).
- Inside each break pattern, "?" seals and other seals carry closers at about the same rate:
  - intact texts: 0.169 vs 0.139
  - start lost: 0.234 vs 0.185
  - end lost: 0.00 vs 0.03
- Recommendation: treat the lead as closed for sign content. Do not cite H2 as a fate-text link.
- The one remaining crumb: the jar sign M342 alone stays about 1.5x high under every null (p = 0.012-0.024 raw). The other six closers are *under*-represented (0.8x), and M342 was not a pre-registered test on its own. It is a candidate for a fresh pre-registered test on new data, not a finding.

## Is "?" really breakage?

- **The "?" is in the printed book, not an OCR artefact: 34 of 34.** I viewed every one of the 34 rows on the Mackay 1938 table scans (`experiments/old_registers/work/rep_png/fem_0392`-`0412.png`). Each one prints "?" in the dimension cell. Some OCR strings were garbled ("? X ■>. X 0-14" is printed "? × ? × 0·14"), but the "?" is real every time.
- **It goes with breakage, strongly.**
  - 20 of 34 "?" seals carry a break mark in Mahadevan's M77 transcription, against 85 of 574 other Mohenjo-daro seals (odds ratio 8.2, Fisher p = 2e-8).
  - That makes 20/34 = 59% confirmed broken by both page and transcription, which passes the pre-registered "at least half" bar.
  - The other 14 have a complete text. Their seals may be chipped away from the inscription, or the "?" may mean something else. For example, seal 650 is "0·75 × 0·75 × ?": the face is fully measured and only the thickness is missing.
- **Not checked:** CISI photographs. The repo holds only 25 CISI pages, and none were matched to these 34 seals.

## Numbers

All runs: 34 distinct "?" texts (133 signs), pool of 574 distinct Mohenjo-daro FEM texts (489 with no break mark used as intact sources), 10,000 null draws. Code: `redteam.py`; log: `run.log`; data: `results.json`, `q_objects.csv`.

The break-pattern rates used by the nulls come from Mahadevan's break marks, reported as NONE / START lost / END lost / BOTH / INTERIOR:

| Group | NONE | START lost | END lost | BOTH | INTERIOR |
|---|---|---|---|---|---|
| Harappa broken (Vats), 62 | 29 | 12 | 14 | 4 | 3 |
| Mohenjo-daro "?", 34 | 14 | 13 | 7 | 0 | 0 |
| Mohenjo-daro pool, 574 | 489 | 36 | 41 | 3 | 5 |

| Null | Closer share obs / null | Ratio | z | p (two-sided) |
|---|---|---|---|---|
| N0 seal_fate's random window (my reimplementation) | 0.173 / 0.088 | 1.97 | +4.01 | 0.0002 |
| **N_B end-anchored, Harappa broken-seal rates (primary)** | 0.173 / 0.126 | 1.37 | +2.06 | **0.049** |
| N_B2 Harappa rates, all assumed truncated | 0.173 / 0.107 | 1.62 | +2.89 | 0.0067 |
| N_B3 rates from all broken M77 seals | 0.173 / 0.113 | 1.53 | +2.60 | 0.011 |
| **N_A each seal's own M77 break pattern** | 0.173 / 0.138 | 1.26 | +1.81 | **0.081** |
| **N_L whole intact texts, same length** | 0.173 / 0.147 | 1.18 | +1.19 | **0.30** |
| N_B, seals only (all 34 are seals) | 0.173 / 0.126 | 1.37 | +2.08 | 0.045 |

- **Reproduction.** I reimplemented seal_fate's null and recover its result: z = +4.0 vs their +3.57, p ≈ 0.0002. My pool is 574 texts vs their 570, a small difference in the length filter.
- **N_B2 and N_B3 still give p ≈ 0.01.** But they assume every "?" seal lost signs, and 14 of 34 have a complete text in M77, so they overstate truncation. N_B uses the real mix of broken seals, intact texts included.
- **M342 alone:**
  - N_B 1.71x, p = 0.009
  - N_A 1.50x, p = 0.024
  - N_L 1.61x, p = 0.012

  The other closers combined are 0.6-0.8x under N_B, N_A and N_L, none significant.
- **Holm across the 8 pre-registered secondary tests.** Nothing passes. The smallest are N_B2 0.054, M342 under N_B 0.060, and N_B3 0.067.
- **Calibration and power of N_B.**
  - False-positive rate 0.054 at 0.05, from 500 pseudo groups.
  - Power to detect a closer share raised by x1.5: 0.78. By x1.7, the size claimed: 0.98. By x2: 1.0.

  So if the claimed 1.7x effect were real on top of the mechanics, N_B would have shown it at about p < 0.01 almost every time. The observed 1.37x, near the edge of significance, sits much closer to "mechanical only".

## Other cheap explanations

- **Seals vs sealings.** Ruled out: all 34 "?" objects are seals in M77, and the seals-only rerun is unchanged.
- **Text length.** This is the main driver, together with which end survives (see above).
- **Site area.** No cluster. Block 7 holds 7 of 34 "?" seals vs 65 of 574 in the pool (Fisher p = 0.11). "Between blocks" and Block 9 are at pool rates.
- **Level.** Not checked separately. seal_fate's H3 found no depth effect on sign classes.

## Decision rule (pre-registered: `docs/prereg/redteam_seal_fate.md`, sha256 in `docs/prereg/HASHES.txt`)

- FAILS if p ≥ 0.05 under N_B.
- WEAKENED if p < 0.05 under N_B but p ≥ 0.05 under N_A or N_L, or the "?" proxy fails.
- SURVIVES only if all three nulls give p < 0.05 and the proxy holds.

Result: N_B p = 0.049, N_A p = 0.081, N_L p = 0.30, proxy holds (20/34 confirmed). That is **WEAKENED**.

## What failed or was not checked

- **N_B's p is fragile.** It sits on the threshold, and a 500-draw pilot gave 0.022. With 10,000 draws the Monte Carlo error is about ±0.002, but a different, equally defensible choice of break rates could move it either side of 0.05.
- **Reading order.** Break position is taken from M77 reading order. If Mahadevan's reading direction is wrong on some seals, START and END would swap for them.
- **14 "?" seals with a complete M77 text.** It is unclear why their dimensions were unmeasurable. CISI photos would settle this.
- **I used seal_fate's group labels** (`fate.csv`) and register links as given, and did not re-derive them from the OCR. All 34 rows were confirmed on the page images.

## Next experiments

- Close H2 as a fate-text link.
- If anyone wants to pursue M342, pre-register "M342 share on broken seals vs an own-break-pattern null" and test it on ICIT post-1977 sites (Dholavira, Banawali, Rakhigarhi) that have breakage notes. Do not use Mohenjo-daro again.
