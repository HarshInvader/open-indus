# Pre-registration: line_breaks (Fable plan 6, test 1)

Agent: line_breaks. Written 2026-11-15, BEFORE any boundary score has been computed at an observed line-break position. Frozen together with `experiments/line_breaks/lb_lib.py` and `experiments/line_breaks/power.py` (hashes in `docs/prereg/HASHES.txt`, tag `line_breaks`).

## Hypothesis
When an Indus text wraps to a second line, the break falls at a slot/constituent boundary (as predicted by a model trained on single-line texts), not wherever the space ran out.

## What I already know (disclosed)
- Counts only (`count.py`, `count.json`): M77 has 122 multi-line object-sides, 117 distinct (seal 107, sealing 4, copper tablet 3, pottery 2, misc 1). Usable for a two-line break test (exactly 2 non-empty lines, complete, no `#`, >= 3 signs, no mixed direction): **74** (67 seals; 23 in held-out families). ICIT has 117 distinct multi-line texts; 82 are not matched by sequence to any M77 text, of which 39 are usable. Union estimate **113 usable texts**.
- I printed the first 40 usable M77 texts with their line split (`sample_multiline.txt`) to inspect the `|` coding. I have not scored them. Impression from that read: many second lines are one sign (35% of usable M77; frequent M393, M374, M242, M342), and some line 2 directions differ from line 1.
- Capacity check (break vs face width, no boundary score): on 57 ICIT two-line square seals with width, line 1 length sits at the median 43rd percentile of single-line text lengths on seals of the same width (+-2 mm); only 9% of line 1s reach the 90th percentile. Total two-line length is about the 90th percentile of single-line length. So line 1 is generally NOT filled to capacity. This bears on the capacity null (below) and on whether `|` is a wrap at all.
- Prior: structure §1 found line order of multi-line texts not recoverable (61/112), jar ends line 1 more often than line 2 (26 vs 14), and 40/112 last lines are a single sign: "second lines look like add-ons".

## Step 1: count and power gate (decisive; run first)
- Units: distinct texts, copy-free (`distinct()`), the usable set above. Primary set M77 (74); ICIT-only texts would be added only through the W->M bridge.
- Power: plant synthetic breaks on the usable texts (observed breaks never read). With probability f = 0.20 a text's break is moved to a true boundary, otherwise drawn uniform over positions 1..n-1. True boundary A = position with the highest end-start ratio (ESR, below); B = random slot-rule boundary. Detection = statistic above the 95th percentile of its uniform null. 300 replicates.
- **Gate:** proceed to Step 3 only if usable n >= 150 AND power(f = 0.20, mode A, actual n) >= 0.80. If either fails, report counts and power and STOP: no break-vs-score statistic is computed on observed breaks.

## Step 2: boundary model (single-line dev only)
- Training data: `dev_heldout(version=2)` dev texts with `n_lines == 1`, break-free runs.
- Score: ESR(a,b) = log2 P(</s>|a) + log2 P(b|<s>) - log2 P(b|a), interpolated Kneser-Ney bigram (D = 0.75). High ESR = "a ends a text and b starts one" is likely relative to "b follows a".
- Slot rule (secondary): boundary if a is a closer-class sign (majority final among non-standalone dev positions, n >= 5) or a jar M342, or b is an opener-class sign; never after a stroke numeral (structure sign_table stroke_type) and never next to M99/M123.

## Step 3 (only if the gate passes)
- Primary statistic: mean within-text percentile rank of ESR at the break position. Null 1 (uniform within text, i.e. within length strata): break uniform over 1..n-1. Null 2 (capacity): for ICIT seals with width, P(k) proportional to the share of single-line seals at that width (+-2 mm) whose length is >= k and < n (line 1 filled up to what fits). Test on held-out families (dev multi-line texts used only to check code); one-sided permutation p < 0.05 under both nulls = supported.
- Specific checks (descriptive, Holm over 3): break before jar/closer-class sign, after opener-class sign, inside numeral+fish or M99 pairs (predicted ~0).
- A confirm script would be frozen as an amendment before running.

## Interpretation fixed now
- Gate fails: "untestable with current data" for the hypothesis; not a refutation.
- If the `|` coding turns out to mark editorial splits (separate fields, signs placed beside the animal, different direction) rather than wraps, the test does not measure constituent boundaries; this is reported as a data-validity caveat with the share of affected texts.

## Multiplicity and ledger
Ledger rows `lb_gate`, `lb_power`, `lb_wrap` (descriptive), family `line_breaks`. One confirmatory test (Step 3 primary) if run.
