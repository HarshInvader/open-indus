# Scorecard v1 (prereg `scorecard_v1`, hashed 2026-11-23T20:28:11Z, before any rating)

**Result** (with addendum 1 applied; v1.0 counts are in the section below).
- The rubric holds: two blind raters agreed at Cohen's kappa **0.842** over 65 claims (raw agreement 0.877, bar 0.8).
- A third fresh rater settled the 8 split rows, seeing both reasons. Those rows are flagged "split" on the page.
- **No claim reaches Anchored (A) or Predicted forward (F).**

| tier | all | calibration | sound keys | function claims | meaning claims (44) | our findings (11) |
|---|---|---|---|---|---|---|
| S survives refutation | 11 | 1 | 0 | 0 | 2 | 8 |
| R refuted | 7 | 0 | 1 | 1 | 5 | 0 |
| U benchable, untestable | 24 | 1 | 1 | 0 | 21 | 1 |
| P pending | 7 | 0 | 0 | 1 | 4 | 2 |
| N unbenchable | 16 | 0 | 4 | 0 | 12 | 0 |

- **Calibration.**
  - The true Linear B key rates S: it passes the refute test.
  - Noise-fitted keys rate U.
  - The scale therefore tells a true key from noise only at the refute level, which matches `lb_shape_ladder`: fit never certifies.
- **Sound keys.**
  - Yajnadevam: U. Planted power at the real null's width is 10-25%.
  - Pierson: R. His own validation fails on rerun: the same coverage on a token-shuffled corpus.
  - Fairservis, Rao, Kalyanaraman, Adelman: N. No key table is held, or the table sent is below the sealed gate.
- **Function claims.** Kriger & Hunt: R (uniqueness reverses). SIGIL: P.
- **Meaning claims.**
  - One rates S: Wells's "fish + number clusters are fixed units", which our #5 (six + fish) confirms on held-out data.
  - Five rate R: Mukhopadhyay's cup-vessel fee, licence pairing and emblem organisation; Kenoyer & Meadow's tablets as tokens; and Laursen and Parpola's Gulf seals in another language.
  - The rest are U (18), P (8) or N (12).
  - The Laursen and Parpola R rests on `round_own_order` (sealed): round texts show no order of their own (p = 0.83), where same-size home sets show it at power 0.995. This sits alongside our #4 (S): round seals break Indus order, but they do not follow another fixed order either.
- **Our findings.**
  - S: #1, #3, #4, #5, #6, #9, #10, #11.
  - P: #2 (descriptive) and #8 (exploratory).
  - U: #7 (direction labels).

## Prediction stated before rating
"No row above S except perhaps calibration. Most meaning claims at R, U or N. Our own findings mostly at S, with #8 at P."

This held. Not predicted: #2 at P and #7 at U.

## Files
- `rows.csv`: the 65 rows, hashed before rating.
- `rater_A.json`, `rater_B.json`, `rater_C.json`: every tier with a one-line reason.
- `final.json`: the combined tiers, built by `finalize.py`.
- Page: `site/scorecard.html` (noindex), built by `site/build.py` → `scorecard()`.

## Addendum 1: four stale catalogue rows re-rated (2026-11-23)
- **What went wrong.** Four rows were rated P because `CATALOGUE.csv` still called them untested. They had been tested days earlier:
  - fish = gems: `bead_workshops`, blind unit coding, too few units;
  - vel substitution and Murukan partners: `parpola_rules34`;
  - sign 193 = weight: `weight_sign`.
- **The fix.** The catalogue now points to those results. Two new blind raters re-rated only these rows, under a sealed addendum, and agreed 4/4:
  - fish = gems: **U**;
  - vel substitution: **U** (gate 2%);
  - Murukan partners: **S** (M403 → M87 fixed pair on held-out data and new sites; the squirrel half fails; the reading itself is not separated from "M403 + numeral 2");
  - sign 193: **U** (too rare).
- **v1.0 counts, before the addendum:** S 10, R 7, U 21, P 11, N 16.
- **Lesson.** A scorecard is only as current as its evidence pointers. v2 should take each row's status from the experiment folders, not from a hand-kept catalogue.

## v2 infrastructure: staleness check (2026-11-23)
`staleness.py` re-reads the evidence each row names and compares it to the evidence at the commit holding that row's current rating. It flags rows to re-rate and never changes a tier.
- **What counts as a change:**
  - for meaning claims, that catalogue row's claim, status and status detail;
  - for atlas references, the named section only;
  - for "our findings", the README table row;
  - for other paths, the whole file (a folder's RESULTS.md);
  - gitignored local files (REPLIES.md) are compared by modification time.
- A second pass flags catalogue rows still marked "testable" whose id is cited by any experiment's RESULTS.md or prereg.
- **Check on a known case:** against the v1.0 rating commit it flags exactly the four rows that addendum 1 fixed (fish-gem, vel, murukan, sign193), and no others.
  - A first draft that compared commit dates flagged 45 of 65 rows, because the catalogue and atlas files are edited often. That is why the check compares content.
- **Now:** 65 rows checked, 0 flags. Every tier on the page rests on the evidence as it stands.
- **Rule from here:** run `staleness.py` after any study that touches a row's evidence. Any flagged row is re-rated by two fresh blind raters under the v1 rules (as in addendum 1).
