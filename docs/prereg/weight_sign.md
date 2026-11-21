# Pre-registration: the "weight" sign (meaning_claims rule 2)

Written 2026-11-20, before any count of a candidate sign in weight versus other units was computed in this experiment. Code: `experiments/weight_sign/`. Hash tag: `weight_sign`.

## Status in one paragraph

This test is **exploratory at best**. M197 has already been seen in this data: it was the assemblage test's nearest miss near weights (Harappa 10 texts vs 5.1 expected, Mohenjo-daro 3 vs 0.4; `experiments/assemblage/RESULTS.md`, ledger `as_r2`). That null did not control for how many finds a unit has, and at Harappa the weights sit in find-rich squares. The only data the assemblage test did not use is tiny, so a planted-answer gate is expected to fail on it. If it fails, the verdict is "underpowered", whatever the real numbers show.

## 1. Which sign is Parpola 193?

- **Source.** Parpola's sign list as reproduced on Wikiversity ("Indus Script", Sign 193: "Weight", "Metrology"), the source used in the meaning-claims catalogue. Its drawing (`experiments/weight_sign/raw/sign193_*.png`, downloaded from the public Wikimedia file) shows four variants. Each is a horizontally hatched triangle hanging from a crossbar or inside a frame, like a pan hanging from a balance beam.
- **Concordance.** The repo has no Parpola-to-Mahadevan table:
  - `bridge_WM.json` is Wells to Mahadevan.
  - The `parpola_graphemes` V-numbers in `sources/field-cady…/features/` run to V805, so they are not Parpola's 1994 numbers.
  
  I therefore matched the drawings to Mahadevan's (`data/sign_images/`):
  - **M206** (W504): hatched triangle under a serifed T. This matches variants 1 and 2.
  - **M208** (W505): the same triangle under a T capped by a table-like bar. This matches variants 3 and 4.
  - **M207**: M206 inside four short strokes. It has no Wells number.
  - **M197** (W575): a box on a three-sided frame, with no triangle and no hatching. **It does not match Parpola 193.** The meaning-claims catalogue's guess "possibly M197" was wrong.
- **Mapping certainty.**
  - High for M206 and fair for M208.
  - M204 (the hatched triangle with no bar) is a separate sign in Mahadevan and is not included.
  - The candidate set is P193 = {W504, W505}. M207 is absent from the Wells-coded data.
- **Counts.**
  - M206 + M207 + M208 appear in 9 distinct M77 texts.
  - W504 + W505 appear in 9 distinct ICIT texts.
  - The catalogue's own kill condition ("the mapped sign is not M197 and has < 30 texts") is therefore already met for Parpola's sign. We run the test anyway, so that the record shows the power figure.
- **Candidates tested (k = 2).**
  - P193 = {W504, W505}.
  - M197 = {W575}. It is kept because rule 2 named it and it is the assemblage near miss.
  - Bonferroni: α = 0.05 / 2 = **0.025** (one-sided).

## 2. Data

All objects (seals and non-seal objects). This is the assemblage's "all" set, where M197 was the near miss. Texts are counted as distinct sign sequences within each unit, so repeated moulded tablets count once per unit. A text found in two units counts in each; this is a caveat.

- **Primary data ("fresh"): data the assemblage test did not use for weights.**
  - (a) Mohenjo-daro DK-G houses that hold weights in Hemmy's Appendix I in Mackay 1938 (pp. 607-612). Coded from OCR by `build_weights.py` before any text was joined. Only 13 of about 220 weights have a house-level locus readable in either OCR, which gives 10 houses.
    - Every house the assemblage had already labelled WEIGHT is removed, together with its texts.
    - The comparison pool is the other DK-G houses with texts.
    - Those texts were seen by the assemblage test as "not weight", so this set is new coding at an already-seen site, not new objects.
  - (b) Chanhu-daro squares, with WEIGHT from the assemblage coding (unfinished weights, Mackay 1943). The assemblage could not test WEIGHT there for any sign.
  - Seen in a dry run (structure only, no sign-by-context counts):
    - DK-G: 89 houses, 6 Hemmy weight houses with texts, 36 of 561 texts in weight houses.
    - Chanhu-daro: 19 squares, 4 weight squares.
    - Candidate texts: P193 1 + 0; M197 4 + 1.
- **Secondary data ("seen"): the assemblage's own units and WEIGHT labels at Harappa (60 Vats squares) and Mohenjo-daro (200 houses).** Every result here is labelled "already seen, exploratory".
  - At Harappa, 30 of 60 squares and 484 of 597 texts are in weight units.
  - All 10 Harappa M197 texts were already known to be in weight units.

## 3. Statistic and nulls

- **Strata.** Site × unit-size bin. Size is the unit's number of distinct texts, binned as 1, 2, 3-4, 5-9, 10-19 and 20+ (fixed cut points).
- **T** = the number of texts carrying the sign that lie in weight units, summed over sites.
- **N1 (primary, find-density matched).** Texts are shuffled among units within the same site × size bin. Every unit keeps its number of texts, so the null expectation is set by sign shares among units of the same size. Draws are exact hypergeometric, 10,000 permutations. p = (1 + #{null ≥ obs}) / (1 + N).
- **Effect size.** The Mantel-Haenszel rate ratio (RR) over the same strata: the sign's share of texts inside weight units against its share outside.
  - This replaces observed/expected. At Harappa 81% of texts are in weight units, so observed/expected can never exceed 1.23 there.
  - This change was made after the dry run, which showed only the data structure and marginal counts. Observed/expected is still reported.
- **N2 (red team).** WEIGHT labels are permuted among units within the same site × size bin, with texts staying in their units. This keeps any clustering of a sign inside one unit, such as repeated seals of one owner.
- **N0 (comparison only).** The old assemblage null: labels permuted within mound strata, with no size control. It is reported so the find-density effect can be seen.

## 4. Gates (run on each data set before reading the real result)

- **Known-answer gate.**
  - Plant a synthetic sign 3× as likely in texts from weight units as elsewhere (rate ratio 3). Its expected count per site equals M197's real count in that data set.
  - Run the full decision rule under N1 (400 replicates × 2,000 permutations).
  - Detection = p ≤ 0.025 and RR ≥ 2. **At least 80% detection is required.**
  - The same gate is also run at the P193 frequency, and that gate decides P193's verdict. A non-decisional pipeline check plants at 10% of texts.
- **Negative control.**
  - Apply N1 to the jar M342 (W740) and to the 10 most frequent other signs in the data set.
  - **The control fails if M342 has p ≤ 0.025, or if 2 or more of the 10 common signs do** (about 2.6% chance under a calibrated null).
  - If the control fails, N1 has not removed find density and the verdict is "inconclusive".

## 5. Decision rule (per candidate, per data set), in this order

1. Fewer than 5 candidate texts in the data set: **untestable**.
2. Gate power below 0.80: **underpowered**.
3. Negative control failed: **inconclusive**.
4. N1 p ≤ 0.025 and RR ≥ 2: **signal**. It is "fragile" if N2 p > 0.025. On seen data it is at most "exploratory signal".
5. RR ≤ 1.2: **refuted in this data**. On seen data this is exploratory.
6. Otherwise: **inconclusive**.

The overall verdict comes from the primary (fresh) data. The seen data is reported as a secondary, exploratory check. No threshold will change after the real run.

## 6. What would change the answer

- A clean reading of Hemmy's Appendix I from page images, which would give about 220 weights with house loci instead of 13.
- Weight findspots from Marshall 1931 vol. II, ch. XXIX.
- HARP trench craft coding for Harappa.
- For Parpola 193 itself, nothing in reach: 9 texts in the whole corpus cannot reach 80% power for any plausible effect in unit data.
