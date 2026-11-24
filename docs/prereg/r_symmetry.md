# r_symmetry: do our refutations (R rows) survive other sign lists and the other edition? (sealed before any run)

Agent `paper`. Main line (a). Fable's study 2; design drafted by Fable on 2026-11-24, then revised after a fresh Fable review (10 fixes applied).

## Question
- Each R row in `experiments/scorecard_v1/final.json` rests on one edition and one sign list.
- The README's positive findings were checked under 12 alternative lists and the other edition. The R rows never were.
- Is any refutation an artefact of that choice?

## Variants (frozen, reused)
- **Sign lists.** The 12 lists in `experiments/signlist_robustness/variants.json`, applied with `harness.Variant(name).tok()`.
- **ICIT-native tests.** Signs go W → M through `bridge_WM.json` (first M sign), then `tok()`. A W sign with no M partner keeps its own label (11% of tokens).
- **Other edition.** M77 for the ICIT-native rows, ICIT for the M77-native rows.

## Rows
| row | native | lists | other edition |
|---|---|---|---|
| MC-MUK23-cup-vessel-fee (`m328_measure/l2_quantity.py` Q1-Q3) | Q1, Q2 ICIT; Q3 M77 (`m77_units`) | all | M77 for Q2; ICIT period/phase lots for Q3 (the existing `Q3_secondary_icit_phase`). Q1 is not run: M77 has no sizes |
| MC-MUK23-licence-pairing (`tablet_archives` T3) | ICIT | all | M77: 242 Harappa objects with a docket side and another side |
| MC-KM-tablets-tokens (T1, T3) | ICIT | T3: all. T1 uses no obverse signs, so only the tier-lumping lists apply | M77, with `locus` as the deposit |
| MC-MUK23-emblem-organisation (`context/q1_animal.py`) | M77 | all | ICIT square seals (`common.icit_animal`) |
| MC-MUK19-stroked-jar-MET (`signmap/strokedjar_test.py`) | ICIT | the 7 lists that keep M343-M345 apart from M342 | M77 pottery graffiti (126 texts), if the count gate (30 texts) passes |
| MC-LAU10-other-language (`round_own_order/run.py`) | ICIT | all | Not run: only 7 of 32 round texts link to M77 |
| FUN-kriger-hunt | — | — | **out of scope**: `kh_tests.planted()` covers K4 only, so K1 and K3 have no plant and no cell can be gated |
| KEY-pierson | — | — | **out of scope** (below) |

**Out of scope, listed in the output table so all 8 R rows are accounted for:** FUN-kriger-hunt (above) and KEY-pierson. Its key is defined per Mahadevan sign, so no other list applies, and its R rests on its own failed power gate, not on a list-dependent statistic.

**Kill and survive thresholds (each row's own, unchanged)**
| row | kill condition met | claim's survive bar met |
|---|---|---|
| stroked jar | pooled ratio ≤ 1 | ratio ≥ 2 and p ≤ 0.01 |
| other-language (round) | not found: excess < 0.3 or p ≥ 0.01 | found: excess ≥ 0.3 and p < 0.01 |
| licence-pairing, tokens (T1, T3) | p ≥ 0.01 | p < 0.01 in the claim's direction |
| cup-vessel-fee (Q1-Q3) | p > 0.0125 | p ≤ 0.0125 in the claim's direction |
| emblem-organisation | unicorn-vs-other AUC permutation p ≥ 0.05 (`animal_tie_power.md`, T1 binary) | p < 0.05 |
- "Direction" is not used separately: each survive bar above already names the claim's direction.

**Fixed before running**
- **M77 tier rule (licence-pairing, tokens).** Tier 3 = any of the five tall-three signs (`fr.TALL`: M88, M89, M92, M93, M94). ICIT has a single sign for it (W033).
- **Not testable (NT) by construction:**
  - stroked jar under `lump_jar_man`, `lump_all` and `img_hi`/`img_mid`/`img_lo`, which merge M343-M345 with the plain jar M342;
  - Kriger-Hunt K1 under `split_s1`-`split_s3`, where random token splits break duplicate texts;
  - any cell where the tested contrast falls inside one label.
- **Sign sets under a variant** (tier, cup, jar, numeral sets): `V.labels_of(set)`. If a label also holds a sign outside the set (e.g. `img_mid` puts M89 with M109), the cell is NT.
- **W → M rule.** Rows whose native code uses `self_label/s2_test.icit_set()` (all M partners) keep that rule. Other ICIT rows use the first M partner, as above.
- **Shape-only pass, before power.** A cell whose test inputs (the per-text features the statistic reads) are identical to native is **INVARIANT**. It is reported, but it is not testable and not a family.

## Kill test, run first
- **Reproduce first.** Each row's statistic is reproduced on its native cell before any variant runs: T3 S = 101.0, round excess -0.10, jar ratio 0.74, and each other row's published value. A mismatch stops that row.
- **Power per cell.** For every row and variant, the effect is planted at the size the original prereg used, in native labels. The variant mapping is applied and the test is run.
  - Reused plants: `plant_t1`, `plant_t3`, `power_spearman`, `power_lot`, `animal_tie_power/run.py:plant` (+20 points), the home-set draw `homeset()`, and Poisson 2× for the jar.
- **Power ≥ 0.8:** the cell is testable. **Below 0.8:** NT (the list masks the effect).
- A reproduce mismatch makes the row **UNCHECKED**.
- All powers are printed and committed before any real statistic is computed in a variant cell.

## Verdict per row (original thresholds, unchanged)
- **Families.** The 3 splits count as one family, and the 3 image cuts as another. Each lump, parpola and the other edition are one family each.
  - A split or image family is testable if at least 2 of its members are. The majority of its testable members decides, and a 1-1 tie counts as "kill not met".
- **Too few families.** A row with fewer than 2 testable, non-invariant families is **UNCHECKED**.
- **R HOLDS:** in every testable family the original kill condition is met and the direction is kept.
- **R WEAKENS:** in some families the kill condition is not met, but fewer than 3 and no more than half of the testable ones. The claim's own survive bar is not met anywhere.
- **R ARTEFACT:** the claim's survive bar is met in any testable family, or the kill condition fails in 3 or more families, or in more than half of the testable ones.

## Scorecard
- **HOLDS:** no re-rating. One evidence line is added to the row's catalogue entry and checked by `staleness.py`; a flag goes to the addendum anyway.
- **WEAKENS, ARTEFACT or UNCHECKED:** sealed scorecard addendum 5. Two fresh blind raters re-rate the row under `scorecard_v1.md` without seeing the current tier, a third settles a split, and `finalize.py` applies it.
- **Ledger mode** `robustness`, outside the FDR family.

## Code plan (`experiments/r_symmetry/`)
- `maps.py`: `w_to_label(V, w)`, built on `harness.Variant` and `W2M_ALL`.
- `run.py`: imports
  - `l2_quantity` (`icit_units`, `identities`, `m77_units`, `strat_perm_spearman`, `perm_chi2`);
  - `experiments/self_label/s2_test.py` (`icit_set`, `m77_set`, `perm_test`); not the `protocuneiform` file of the same name;
  - `q1_animal` (`build`, `featurize`);
  - `animal_tie_power/run.py` (`auc_bin`, `plant`).
- `t_tests.py`, `round_own_order/run.py` and `strokedjar_test.py` run code at import, so their statistic functions are copied verbatim, then checked by the reproduce-first step.
- `summarise.py`: one table, row by variant, power first and then the result.
- **Modes:**
  - `shape`: the invariance pass.
  - `power`: the kill test.
  - `test`: the variant statistics. It runs the other-edition cell first and refuses to run unless `power.json` exists and is committed.
