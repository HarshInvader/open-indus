# Do Indus tablets and pots quote same-site seal texts? (prereg `tablet_quoting`, hashed 2026-11-23T20:24:34Z)

**Verdict: untestable at Indus size. The kill test failed, so the study stopped as sealed.**
- The Ur III rehearsal used real seal legends and real tablet bodies from Umma and Girsu, cut to Indus counts and lengths. It passed the full rule in only 30.5% of 200 draws, against a bar of 80%.
- A real seal-to-document system therefore does not show through Indus-sized, Indus-length texts with this statistic.
- The Indus statistic was **not computed**, and the planted Indus gate was not run.

## Kill test (200 draws; `kill.json`, `kill.out`)
| | value |
|---|---|
| power (all three rules) | **0.305** |
| rule 1, site-permutation p ≤ 0.01 | 0.375 of draws (median p 0.023) |
| rule 3, above the bigram null's 99th percentile | 0.83 |
| rule 2, positive excess at Girsu (Harappa slot) / Umma (Mohenjo-daro slot) | 0.99 / 0.79 |
| mean T / site-permutation null / bigram null | 0.092 / 0.072 / 0.055 |

- Rule 1 is the bottleneck. Same-archive sharing exists in Ur III (Girsu slot: +2.5 points on a base of 7.6%), but at about 3-sign targets and 4-sign seals it is too faint for p ≤ 0.01.
- Dropping rule 2 does not rescue power (0.355).
- These figures are diagnostics, read after the stop. They do not change the verdict.

## What this means
- No claim either way about Indus tablets quoting seals. Seal-to-tablet quoting goes on the scorecard as **"benchable, but untestable at Indus size"**.
- For a future attempt to be powered, it would need longer targets (none exist in the corpus), more targets at Mohenjo-daro, or a different unit, such as whole-text identity between tablets and seals. Each is a new prereg, not a rerun.
- Fable's odds before the run put the Ur III gate at 75%; it failed.

## Data note
`data/ur3_sealed.jsonl` (21,791 sealed Ur III tablets; derived from ORACC epsd2/admin/ur3, CC BY-SA) stays local. `build_ur3.py` rebuilds it from the ORACC zip.
