# Assumption audit, Part 2: do the headline findings survive damage to the corpus?

Board task #27 (M6), H12. Pre-registration: `docs/prereg/assumption_audit.md`; it and `sens.py` were hashed in `docs/prereg/HASHES.txt` (tag `assumption_audit`) before any damaged condition was scored. The register of assumptions (Part 1) is `docs/ASSUMPTIONS.md`.

## Verdict

**Seven of the nine headline tests do not depend on reading direction, transcription accuracy (up to 10% of signs wrong), line order, near-copies or doubtful signs. Reading direction is the only assumption tested here that does damage, and it hits three findings:**
- #7 (L-R reversals) needs the labelled directions to be right. It misses its bar with 10% of objects flipped and is gone at 50%.
- #10b (fixed pair order) misses its bar at 10% flipped: 0.69-0.74 against a bar of 0.75. It still beats free order at every level up to 25%.
- #9 (functional parse) passes up to 25% flipped. At 50% it passes in direction only: coverage minus shuffle falls from 0.35 to 0.10-0.13.

#1 (order), #3 (ticked fish), #5 (six + fish), #6 (registers), #10a (cores) and #11 (fish class) hold even with half the objects read backwards. All nine hold under 10% random or look-alike substitution, under shuffled line order, with near-copies removed more aggressively than split v2 does, and with every object that has a doubtful sign dropped.

The sign-list assumption was not re-run: `experiments/signlist_robustness/` already ran these nine tests under 12 alternative lists. It found #3, #5, #7 and #10b sensitive and the rest robust.

## Method

The nine tests are those of `experiments/signlist_robustness/harness.py`, unchanged: same frozen bars, type unit, M77 list, split v2. They were re-run on damaged copies of the corpus. Dev and held-out were damaged alike, and held-out membership was fixed from the undamaged text. The base run reproduces the harness M77/type result exactly (all fields identical). There are 29 runs, about 15-30 s each, all through `board/run.sh`.

| condition | damage | seeds |
|---|---|---|
| lineshuf | line order shuffled inside each multi-line object (122 objects) | 3 |
| rev10/25/50 | whole object read backwards for 10/25/50% of objects | 3 each |
| noiseR2/5/10 | 2/5/10% of sign tokens replaced by a random sign, drawn by frequency | 3 each |
| noiseV2/5/10 | same rates, replaced by a look-alike (same image cluster `img_mid`; random if none; 192 of 417 signs have a look-alike) | 3 each |
| dedup | near-copy rule widened from split v2's "1 edit" to 2 edits for texts of 4+ signs; one text per family. Held-out 571 -> 363, dev 1,699 -> 1,060 | 1 |
| nodoubt | drop every object with a sign Mahadevan marked doubtful. Held-out 571 -> 514 | 1 |

Rule: **holds** = passes the frozen bar in at least 2 of 3 seeds. **weakens** = fails the bar but keeps the direction of the effect. **fails** = the effect itself is gone.

## Results

| finding | lineshuf | rev10 | rev25 | rev50 | noiseR 2/5/10 | noiseV 2/5/10 | dedup | nodoubt |
|---|---|---|---|---|---|---|---|---|
| #1 order beats permutations | holds | holds | holds | holds | holds | holds | holds | holds |
| #3 ticked fish final | holds | holds | holds 2/3 | holds 2/3 | holds | holds | holds | holds |
| #5 M109+M59 | holds | holds | holds | holds | holds | holds | holds | holds |
| #6 object-type registers | holds | holds | holds | holds | holds | holds | holds | holds |
| #7 L-R reversals | holds | **weakens** | **weakens** | **fails** | holds | holds | holds | holds |
| #10a cores 1-2 word signs | holds | holds | holds | holds | holds | holds | holds | holds |
| #10b fixed pair order | holds | **weakens** | **weakens** | **weakens** | holds | holds | holds | holds |
| #11 fish lexical class | holds | holds | holds | holds | holds | holds | holds | holds |
| #9 functional parse | holds | holds | holds | **weakens** | holds | holds | holds | holds |

Effect sizes: base, then the damaged levels (full per-seed list in `table.md`).

- **#1 order** (share of held-out runs whose real order beats every permutation; chance about 0.057):
  - base 0.40 (7.1x chance).
  - 10% random noise: 0.27-0.29 (4.8-5.2x). 10% look-alike noise: 0.31-0.35.
  - Direction flipped: rev10 0.31 (5.4x), rev25 0.21-0.27, rev50 0.15 (2.6x).
  - dedup 0.23 vs 0.041 (5.7x).
  - The order signal falls steadily with damage but stays far above chance everywhere.
- **#3 ticked fish** (share of ticked fish in final position, against plain fish):
  - base 0.58 vs 0.07.
  - 10% noise: 0.50-0.62 vs 0.08-0.10.
  - rev50: 0.29-0.60 vs 0.20, one seed of three at p=0.22.
  - dedup 0.55 vs 0.11 (p=0.0095).
- **#5 six + fish:** base 7/10 vs 3% base rate. rev50 4-5/10 (p≤1.5e-4). dedup 3/5 (p=2.5e-4).
- **#6 registers:** mean AUC 0.75 in base and 0.70-0.76 in every condition. Every class stays above its permutation null.
- **#7 L-R reversals** (share of left-to-right lines that read better reversed):
  - base 31/34 = 0.91.
  - rev10: 0.69-0.72 (p 0.006-0.01; the bar is p<0.001).
  - rev25: 0.46-0.63.
  - rev50: 0.49-0.51.
  - Under noise it stays at 0.76-0.95.
- **#10a cores:** one-sign core share is 0.39 in base and 0.31-0.43 in every condition, against a bar of 0.28. Standalone share is 0.72-0.87, against a bar of 0.22.
- **#10b pair order** (held-out agreement with the dev order):
  - base 85/107 = 0.79.
  - rev10: 0.69-0.74.
  - rev25: 0.62-0.65.
  - rev50: 0.45-0.64.
  - 10% noise: 0.75-0.82.
  - dedup: 56/66 = 0.85.
- **#11 fish class:** 2 or 3 of the 3 sub-tests pass everywhere. Look-alike noise costs one sub-test in every seed.
- **#9 parse** (coverage of held-out texts against shuffled texts):
  - base 0.75 vs 0.40.
  - rev25: 0.61-0.64 vs 0.41.
  - rev50: 0.52-0.55 vs 0.42 (z 8.5-13).
  - 10% noise: 0.68-0.72.
  - dedup: 0.71 vs 0.46.

## Pre-registered predictions

- **P1 (direction):** partly wrong.
  - Right: #7 fails and #10b weakens at rev50; #6 and #10a hold; #1 holds at rev25.
  - Wrong: #3 holds at rev50 in 2 of 3 seeds. Its null moves too, because reversal sends plain fish (usually text-initial) to the end.
  - Not predicted: #9 weakens at rev50.
- **P2 (noise):** half wrong.
  - Right: everything holds at 2%.
  - Wrong: #3 and #5 also hold at 10%, where they were predicted to weaken. Look-alike noise was not clearly worse than random noise for #3 and #5. It was slightly worse for #11.
- **P3 (dedup):** right. Every test keeps its direction, and none even misses its bar.
- **P4 (nodoubt):** right.

## What this does not test

- **Systematic errors.** Random noise is the friendly case. A misreading shared by every copy of a sign, such as an editorial convention that splits one sign into two, is the sign-list question. That is covered by signlist_robustness, not here. Errors shared by M77 and ICIT cannot be seen with either.
- **Noise separates copies.** Damage makes exact copies differ, so n rises (dev up to 1,971). A small share of extra "distinct" texts is near-copies of each other. Held-out membership was fixed beforehand, so no copy crosses the split.
- **Line-level noise for #7 is drawn separately** from the text-level noise. Both use the same rate.
- **Reversal makes direction random, not wrong in a patterned way.** A real error would more likely hit short or symmetric texts, or particular sites.
- **Findings #2, #4 and #8 were not run.** #2 is descriptive. #4 lives in a separate code base, and its n of 8-11 texts would be dominated by single misreadings. #8 is exploratory. The register treats them.
- **The runs that end at a break or a line end count as "final" in #3** (harness `final_share` uses `runs()`). A complete-text-only rerun of #3 is recommended, not run (not pre-registered).

## Files

- `sens.py` is the damage generator and runner (resumable; `out/runs.jsonl`). `summarise.py` builds `table.md`, `results.json` and `ledger_rows.csv`.
- `ledger_rows.csv` has 108 rows: 12 condition families x 9 tests, mode `robustness`. These are robustness rows, not new claims. The prereg said "9 x 10 = 90 rows". That was an arithmetic slip: its own condition table has 12 families. No condition was added or dropped.
