# Scorecard addendum 4 (sealed before rating): MC-PAR-murukan-partners after meaning_calibration

- **Flagged row.** `staleness.py` flags MC-PAR-murukan-partners, because its catalogue entry gained the meaning_calibration v2 result on 2026-11-24.
- **Tool fix.** `staleness.py` was also corrected to count the raters of addenda 2-4 (G/H/K2, I/J/K, L/M/N) as current. Before the fix it falsely re-flagged the three rows those addenda had already re-rated.
- **Rating.**
  - Two fresh blind raters, L and M, re-rate this one row under the v1 rubric (`scorecard_v1.md`). They see the row's evidence, including the calibration and its caveats. They do not see the current tier.
  - A third rater, N, settles a split.
  - `finalize.py` applies addendum 4 in the same way as addenda 2 and 3.
- **Not re-rated.** MC-WEL15-fish-number. It rests on README #5 (the six + fish test), not on the calibrated rule, so its evidence is unchanged. The calibration prereg's row table was wrong to list it as calibrated, and `RESULTS.md` says so.
- **Site.** There is no Latest-updates entry: no tier is expected to change, and the headline bar was missed. The scorecard page adds the note "Meaning rows other than MC-PAR-murukan-partners are not calibrated on a read script."
