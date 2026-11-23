# Scorecard v1: one tier per claim, rated blind by two raters (sealed 2026-11-23, before any rating)

Agent `paper`. Main line (a). Fable's ranking puts it after the fit standard (`lb_certify`, `lb_shape_ladder`) and the anchor sizing (`animal_tie_power`, `tablet_quoting`), which are now done.

## Rows (`experiments/scorecard_v1/build_rows.py` → `rows.csv`, 65 rows)
- **Calibration (2):** the true Linear B key, and keys fitted to noise. They show what each tier means on a known case.
- **Published keys and function claims (8):** Yajnadevam, Pierson, Fairservis, Rao, Kalyanaraman, Adelman, Kriger & Hunt, SIGIL.
- **Meaning claims (44):** every row of `experiments/meaning_claims/CATALOGUE.csv`.
- **Our own findings (11):** README "What we can defend" rows #1-11.

## Tiers (rated as the first rule that applies, top to bottom)
| code | tier | rule |
|---|---|---|
| A | Anchored | An outside anchor (a bilingual, or a read script's object or text) confirms the claim on data not used to make it. |
| F | Predicted forward | A sealed prediction, made before the data were seen, was scored and passed. |
| S | Survives refutation | A pre-registered or held-out test that could have refuted the claim (power ≥ 0.8 stated, or a held-out replication) was run and the claim passed. No anchor, no forward prediction. |
| R | Refuted | A test of the claim's own prediction, with power ≥ 0.8 for the stated effect, failed; or the claimant's own numbers fail on rerun. |
| U | Benchable, untestable | The claim is stated precisely enough and the data are held, but every test run or possible on held data is below power 0.8, or cannot tell the claim from noise (for example, fit cannot certify a key). |
| P | Pending | Testable on data in hand, or exploratory only (no sealed or held-out test yet), and not yet decided. |
| N | Unbenchable | Not stated sign by sign or operationally, or the source or table is not held (login wall, not published, not yet sent). |

- A row is rated on the evidence files named in `rows.csv` and anything those files cite in this repo. No outside reading.
- Where a row's evidence shows mixed results (part refuted, part untested), the rater rates the claim's **central** prediction and notes the split.

## Raters and agreement
- Two raters, each a fresh agent with no access to the other's ratings or to my view. Each gets this rubric, `rows.csv` and the repo. Each returns one tier per row and a one-line reason.
- **Agreement:** Cohen's kappa (unweighted, 7 categories) over all 65 rows. **Bar: κ ≥ 0.8.**
- **If κ ≥ 0.8:** disagreeing rows are settled by a third fresh rater, who sees both reasons, and are flagged "split" on the page.
- **If κ < 0.8:** the page still publishes, headed "rubric not yet reliable (κ = x)", and each disagreeing row shows both tiers. One rubric revision is allowed, as a sealed addendum, with two new raters. No more.
- I do not change any rater's tier.

## The page
- `site/scorecard.html`, noindex, a results page and not a paper.
- Calibration rows go first. Then the tiers, with counts per tier and per group.
- Each row gives: tier, claimant, claim, a one-line reason and the evidence links.
- Standing floors are stated at the top: fit refutes only full-coverage keys at Indus length and never certifies one (`lb_shape_ladder`); single-sign animal ties are visible only above +20 points (unicorn vs other), 0.20 (shorthorn bull) and 0.40 (elephant) (`animal_tie_power`); seal-to-tablet quoting cannot be seen at Indus size (`tablet_quoting`).

## Expected (stated before rating)
No row above S except perhaps calibration. Most meaning claims at R, U or N. Our own findings mostly at S, with #8 (exploratory) at P.
