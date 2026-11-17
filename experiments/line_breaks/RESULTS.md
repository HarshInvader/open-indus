# Line breaks as constituent boundaries (Fable plan 6, test 1)

2026-11-15. Pre-registered in `docs/prereg/line_breaks.md`, hashed with `lb_lib.py` and `power.py` (`docs/prereg/HASHES.txt`, tag `line_breaks`) before any boundary score was computed at an observed break. Ledger rows `lb_gate`, `lb_power`, `lb_wrap`.

## Findings first

1. **Untestable with current data. The power gate fails, so we stopped.** No statistic comparing break positions with boundary scores was computed.
   - Only **74** usable multi-line texts in M77 (67 seals; 23 in held-out families). Adding ICIT texts not in M77 gives about **113**. The bar was 150.
   - Planted test (20% of breaks moved to a true boundary): power **0.77** at n = 74 when the boundary is the model's best position, and **0.51** when it is a slot-rule boundary. The bar was 0.80. At n = 150 power would be 0.94 and 0.68; the slot-rule version needs about 300 texts (0.89).
   - The false-positive rate at no planted effect is 0.067 (300 runs).
2. **Many `|` breaks are probably not wraps, which weakens the test even with more data.**
   - Of 117 distinct multi-line M77 texts: 60 have two multi-sign lines running the same way; **39 end with a one-sign line**; **12 have lines running in different directions**.
   - The one-sign second lines are mostly signs that almost never occur inside running text: M242 (9), M374 (7, never in a single-line text), M393 (4), M93 (4, the Chanhu-daro end mark). 18 of 40 such signs occur in fewer than 5 single-line texts. These look like signs placed apart on the face (a separate field), not overflow.
   - Line 1 is not filled to capacity. On 57 ICIT two-line square seals with a recorded width, line 1 sits at the median **43rd percentile** of single-line text lengths on seals of the same width (within 2 mm). Only 9% reach the 90th percentile. A pure "ran out of room" layout would put line 1 near the top.
   - So the `|` in the corpus mixes true wraps with editorial line splits (separate sign groups, reversed lines). Structure §1 reached the same view ("second lines look like add-ons"), and line order could not be recovered (61/112).

**What this means.** This was meant to be the one source of segmentation evidence that does not come from sign distributions. It cannot be used. There are too few multi-line texts, and about half of them are not clean wraps. That leaves the slot model neither confirmed nor broken.

## Method (as frozen)

- **Units.** Distinct texts with exactly 2 non-empty lines, flagged complete, no `#`, at least 3 signs, and no mixed direction.
  - From 117 distinct multi-line texts, the exclusions were: 24 incomplete, 8 without exactly 2 lines, 5 mixed direction, 5 with fewer than 3 signs, and 1 with a break.
  - ICIT texts were matched to M77 by sequence through the W->M bridge. 39 usable ICIT texts are not in M77.
- **Boundary model.** Fitted on single-line dev texts only: `dev_heldout(version=2)`, n_lines = 1, 1,614 texts.
  - **End-start ratio (ESR):** ESR(a,b) = log P(end | a) + log P(b | start) - log P(b | a), using a Kneser-Ney bigram.
  - **Slot rule:** a boundary falls after a closer or jar, or before an opener. Never after a stroke numeral, and never next to M99/M123. 19% of positions qualify.
- **Statistic.** The mean within-text percentile rank of ESR at the break. The null places the break uniformly within the text (length-stratified).
- **Capacity null.** Defined in the prereg (line 1 filled up to what fits at that face width) but not run, because of the gate.

## Hypotheses

| hypothesis | result | verdict |
|---|---|---|
| Enough multi-line texts for the test (n >= 150) | 74 (union about 113) | fails |
| 80% power for a 20% planted excess | 0.77 (ESR) / 0.51 (slot) | fails |
| Breaks fall at slot boundaries above the capacity and uniform nulls | not computed | **untestable** |
| `|` marks a wrap with line 1 at capacity | line 1 at the 43rd percentile; 39/117 one-sign later lines; 12/117 mixed direction | not supported (descriptive) |

## Caveats

- Before freezing, I eyeballed 40 line splits to check the `|` coding, and I ran the capacity check. Both are disclosed in the prereg. Neither used boundary scores.
- The capacity check relies on ICIT widths: the 1930s Mohenjo-daro and Harappa measurements, plus later reports.
- Power is computed for the uniform null. The capacity null would be at least as hard to beat.

## Next experiments

- Rerun only with more two-line texts, about 150 clean wraps for the ESR version or 300 for the slot version. The CISI vol. 3 volumes and the Fuls 2023 catalogue are the only plausible sources.
- Recode the layout from photographs: true wrap, separate sign group, or reversed line. Use only true wraps. From the counts above, at most about 60 of the current 117 texts qualify.
- The one-sign second-line signs (M374, M393, M242, M93) may be a "field-placed sign" class. Check their face position on CISI photos before treating them as text.

## Files

- `count.py` produces `count.json` and `sample_multiline.txt`.
- `lb_lib.py` is the frozen model and statistic.
- `power.py` produces `power.json` (frozen).
- `validity.py` produces `validity.json`.
- `results.json` holds the key results.
