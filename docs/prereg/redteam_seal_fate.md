# Pre-registration: red team of seal_fate H2 (board #37, agent redteam_seal_fate), 2026-11-18

Claim under attack (experiments/seal_fate, H2): the 34 distinct Mohenjo-daro FEM seals whose Mackay 1938 register prints a dimension as "?" carry closers at a share of 0.18 vs 0.10 expected under a random-window truncation null (closer z = +3.57, omnibus p = 0.0044, Holm 0.018).

## State at registration
- I have read seal_fate's RESULTS.md, prereg, code (only to locate inputs) and the 43 FEM register rows with "?" in the dimension cell (dimension text only, no signs).
- I have NOT looked at the sign sequences or M77 break markers of the "?" group, of the Harappa broken group, or of the pool. I know the M77 data format: per line, `signs_clean` in `sources/paragorth_Indus-/data/im77/im77_corpus_lines.csv` with `0` marking a broken/lost position (data/m77_lines.jsonl drops these, keeping only `complete`).
- All code is mine (`experiments/redteam_seal_fate/redteam.py`); it reads seal_fate's `fate.csv` and `experiments/old_registers/registers.csv` for the group labels and links only.

## Data (fixed now)
- Groups: same as seal_fate. "?" group = Mackay1938_FEM rows with BROKEN_PROXY = 1 linked to an M77 text with >= 1 sign; pool = FEM rows with BROKEN_PROXY = 0 and a linked text. Harappa broken = Vats1940_EH rows with BROKEN = 1. Distinct texts within each group (one object per distinct token sequence).
- Text of an object: all M77 lines of the text number, sorted by (side, line), concatenated; tokens = signs; `0` positions are kept as break marks for classification only.
- Break pattern of a text, from the raw `0` marks over the concatenated sequence: NONE (no `0`), START (a `0` before the first sign only, i.e. the end of the text survives), END (a `0` after the last sign only, the start survives), BOTH (a `0` at both edges), INTERIOR (`0` only between signs). Combinations with interior marks are classified by their edge marks (START/END/BOTH) if any, else INTERIOR. Reading order as stored in M77 (first sign read first; this is how seal_fate and corpus/ use it).
- Intact source texts for fragments: pool texts with pattern NONE.
- Classes: same 4 classes as seal_fate. CLOSER = M342, M211, M15, M254, M12, M14, M388.

## Nulls (each 10,000 pseudo "?" groups; each "?" object of length L replaced by one draw)
- **N_B (primary; the null the task asks for).** Fragment mode drawn per object from the break-pattern rates of real broken seals: the Harappa BROKEN group's distribution over {NONE, START, END, BOTH, INTERIOR}. NONE -> a whole intact pool text of the same object type with length exactly L (if fewer than 5 candidates, length L +- 1, then L +- 2). START -> the last L signs of an intact pool text of length > L. END -> the first L signs. BOTH -> a random interior window (not touching either end) of a text of length >= L + 2. INTERIOR -> first a signs + last (L - a) signs of a text of length > L, a uniform in 1..L-1 (L = 1: treat as START or END with p 0.5). Same object type (seal vs other) where possible, else any.
- **N_B2 (sensitivity).** Same draw rules, rates = Harappa-broken break-pattern rates computed only over texts that carry a break mark (NONE excluded, i.e. every "?" object assumed truly truncated).
- **N_B3 (sensitivity).** Same, rates from all M77 seals at all sites that carry a break mark.
- **N_A (secondary).** Each "?" object uses its OWN M77 break pattern (same draw rules). This conditions on what Mahadevan saw on the object.
- **N_L (secondary, text-length explanation).** Each "?" object replaced by a whole intact pool text of the same type and same length (no truncation at all).
- **N_0 (reproduction).** seal_fate's random-window null, reimplemented, to check I recover their z.

## Statistic and tests
- Primary statistic: CLOSER token share in the "?" group. Two-sided p = (1 + #|null - mean| >= |obs - mean|) / (1 + 10,000). Also z.
- Secondary, descriptive with Holm across them: closer share under N_B2, N_A, N_L; M342 share alone and non-M342 closer share under N_B; closer share under N_B for seals only (M77 object_type = seal); omnibus T (sum of z^2 over 4 classes) under N_B.
- Other cheap checks (descriptive): break-pattern table of the "?" group vs pool vs Harappa broken (chi-square / Fisher); text-length distribution of the "?" group vs pool (Mann-Whitney); "?" group by Mackay block/area vs pool (share by block, Fisher for the block with most "?"); object types in the group.

## Is "?" breakage? (descriptive, no p-value)
- For every "?" row I view the FEM tabulation page image (`experiments/old_registers/work/rep_png/fem_0*.png`) and record whether the cell prints "?" (vs an OCR misread of a digit/blank), and cross with the M77 break pattern of the object. Reported as counts: printed "?" yes/no/unreadable; M77 break mark yes/no.
- If fewer than half of the "?" objects both print "?" and carry an M77 break mark, the proxy is reported as weak.

## Calibration and power
- Calibration: 500 pseudo "?" groups drawn from N_B itself, tested against N_B; FPR at 0.05 must be <= 0.08, else report N_B unreliable.
- Power: plant closers into pseudo groups (replace non-closer tokens by closer signs drawn by frequency) to raise the closer share by x1.5 and x1.7 over the N_B mean; 500 plants each; power = share with p < 0.05.

## Decision rule (fixed now)
- **FAILS** (lead closed): closer excess p >= 0.05 under N_B.
- **WEAKENED**: p < 0.05 under N_B, but p >= 0.05 under N_A or N_L, or fewer than half the "?" objects are confirmed broken by both page and M77 marks.
- **SURVIVES**: p < 0.05 under N_B, N_A and N_L, and the "?" proxy holds by the rule above.
- Power at x1.7 is reported with the verdict; if FAILS with power < 0.5 at x1.7, it is reported as "fails, low power" (the lead is still closed for this data).
