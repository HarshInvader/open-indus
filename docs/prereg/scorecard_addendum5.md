# Scorecard addendum 5 (sealed before rating): the six R rows after r_symmetry

- **Flagged rows.** `staleness.py` flags exactly these 6 rows, after their catalogue entries gained the r_symmetry results:
  - MC-MUK23-cup-vessel-fee
  - MC-MUK23-licence-pairing
  - MC-KM-tablets-tokens
  - MC-MUK23-emblem-organisation
  - MC-MUK19-stroked-jar-MET
  - MC-LAU10-other-language
- **Rating.**
  - Two fresh blind raters, O and P, re-rate these 6 rows under the v1 rubric (`scorecard_v1.md`). They see each row's evidence and `experiments/r_symmetry/RESULTS.md`, including the cup-vessel-fee note. They do not see current tiers.
  - A third rater, Q, settles a split.
  - `finalize.py` applies addendum 5 in the same way as addenda 2-4. The rater files are added to `staleness.py`'s list of current raters.
- **Site.** A Latest-updates entry is added only if a tier changes.
