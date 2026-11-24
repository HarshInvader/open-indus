# Tablet picture × text, whole objects, class level: STOP, untestable at this object count

Prereg `docs/prereg/tablet_pic_text.md`, sealed 2026-11-24 (tag `tablet_pic_text`; code fix `tablet_pic_text_fix1` changes JSON output only). Run from the repo root: `.venv/bin/python -I experiments/tablet_pic_text/run.py rows | gate | kill`. Outputs: `gate.json`, `kill.json`, `kill.out`.

**The real association between tablet text and picture was never computed.**

## Result
1. **The label gate removed one of the two test classes.**
   - The test compared ICIT's "figure" code (Scene, Anth) with the `scene_text` blind raters' consensus "scene or human" on 44 moulded-tablet objects: both 7, ICIT only 11, raters only 0, neither 26.
   - κ = 0.43 against a bar of 0.6, so figure moved to "rest".
   - The misses run one way: the raters never saw a figure that ICIT lacks. That may be rater misses on low-resolution photos rather than ICIT error. The frozen rule was applied regardless.
2. **That made the study underpowered by construction.**
   - Bovine is the only eligible class: 21 of 61 rows (34%). Both the powered and gross bands need ≥ 50% of rows. **STOP:** no real run, no Linear B control.
3. **The sizing run (bovine vs rest, plants on block-permuted labels, one fixed 1,000-permutation null) confirmed the STOP.**

   | nominal δ | realised δ | feasible / 40 | power at p < 0.025 | mean excess AUC |
   |---|---|---|---|---|
   | 0.05 | 0.095 | 38 | 0.03 | 0.047 |
   | 0.10 | 0.143 | 34 | 0.03 | 0.077 |
   | 0.20 | 0.238 | 20 (not counted) | 0.40 | 0.173 |
   | 0.40 | 0.429 | 1 (not counted) | (1 of 1) | 0.249 |

   - Bovine c\* = none on the counted rungs (δ ≤ 0.14 realised).
   - At δ = 0.24, about Linear B's full-line tie (+23 points, `animal_tie_power`), only 20 draws were feasible and power was 0.40.
   - Null: mean AUC 0.48, 99th percentile 0.72.
   - False alarms: A (permuted within strata) 4/400, B (block-permuted) 13/400. Both pass the bar of ≤ 16, so the pipeline is not leaky.

## Reading
- **Untestable at this object count.** With 61 mould-level rows, a single-sign bovine tie at Linear B strength would be caught less than half the time. Weaker ties would almost never be caught.
- Nothing is said about whether tablet texts track their pictures.
- No scorecard row changes. Main line (b) is unchanged.
- **What would reopen it:**
  - more pictured TAB:B objects: CISI vol. 3, the HARP tablets;
  - the ICIT picture-code list, which would return 75 rows lost to undefined codes (Mult, Gavi, Phyt, Bult);
  - better photos, so the figure class can pass the gate.
- At roughly twice the rows with figure restored, both classes would hold about 65% of rows. The band rule could then be met, though power at δ 0.24 is still uncertain.

## Disclosures
- **ICIT code list not found.** The open help PDF has no picture codes, and the ResearchGate page for Fuls' corpus returned 403 (not bypassed).
- **Families: 59, not the draft's 57.** The code follows the written flattened-sequence rule. A per-side reading gives 55.
- The plant rung is overshot by `ceil` (nA = 21), so realised δ is shown above.
- The first kill run crashed on JSON serialisation after the null was computed. Nothing was written. The fix was hashed before the rerun.
