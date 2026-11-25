# Layout word division: K0 INCONCLUSIVE. Neither agent can measure cuneiform sign gaps blind (G2 failed twice, including the sealed F2 re-run). The gap route for Indus stays closed until expert boxes exist.

- **Prereg:** `docs/prereg/layout_word_division.md`, sealed 2026-11-25 as v2 (tag `layout_word_division`) after one fresh review. This is plan 12, family 1.
- **Code:** written without being run and hashed before any run (tag `layout_word_division_code`). Every step checked the prereg and code hashes. The blind label keys (`key_main`, `key_f2`) and all four rater outputs were hashed before any alignment.
- **Runs:** each step ran once, in the sealed order.
  - `score.py selftest`, then `synth.py render` and `check`.
  - A detached photo fetch (97 of 97), then crops and the R2 check.
  - Main round: bundle, raters, validate, measure, G2 and gates.
  - The F2 round, the same way.
  - The record-only Dencker AUC, then `score.py k0`.
- **Outputs (aggregates only):** `out/selftest.json`, `out/synth_check.json`, `out/gates_main.json`, `out/gates_f2.json`, `out/k0_f2.json` and `out/k0_f2.out`. The Dencker boxes and the values per gap stay in `raw/`, which is never committed.
- **Scope:** no Indus image was boxed and no Indus text was read.

## Result
- **§5.2, the planted check of the scorer, passed.**

  | Planted δ | 0 | 0.03 | 0.06 | 0.10 | 0.20 |
  |---|---|---|---|---|---|
  | AUC on true boxes | 0.50 | 0.60 | 0.71 | 0.82 | 0.96 |

  - The false-reject rate of the null at δ = 0 was 2% (bar ≤ 5%). F3 did not fire.
  - The pipeline therefore detects a gap cue when the boxes are accurate.
- **R2:** 8 bad crops (an edge view inside the crop, or a whole photo of all views) were replaced by the sealed rule, the next tablet in hash order. That left 258 face crops plus 40 synthetic lines, 298 images per rater.
- **G2, the agents against the Dencker expert boxes** (16 calibration tablets, 224 gold pairs, 471 gold boxes). The bars are recall ≥ 0.85, gap ICC against gold ≥ 0.70, and agent-to-agent ICC ≥ 0.70.

  | Round | Rater | Recall | ICC against gold | Agent-to-agent ICC | Crops boxed of 298 |
  |---|---|---|---|---|---|
  | main | A (Opus) | 0.16 | 0.61 | 0.72 | 144 |
  | main | B (Fable) | 0.79 | 0.24 | | 291 |
  | F2 | A (Opus) | 0.13 | 0.61 | 0.83 | 142 |
  | F2 | B (Fable) | 0.58 | 0.31 | | 235 |

  - **G2 failed in both rounds.**
  - F2 (2x upsampled crops, plus the "one box per sign, include touching wedges" paragraph) did not help. Recall fell for both raters.
- **G2b (agent agreement on S2) passed,** with ICC 0.98 in both rounds. It rested on only 15 faces, because A skipped so many.
- **G3 passed.**
- **§5.3, the measurer check on synthetic lines:** only 1 or 2 of the 40 lines came back with the right box count. The attenuation ratio is therefore undefined; the code reports −1.0, which means nothing. The agents also fail on clean synthetic glyphs.
- **Verdict under the sealed rule (§7 F2): INCONCLUSIVE,** with the note "no blind measurer of cuneiform layout at this precision". The ICC bar of 0.70 was not lowered.
- **The record-only S1 Dencker AUC, description under D5:** 0.66 (95% bootstrap 0.56 to 0.70). Within-line shuffle p = 0.001, on 33 lines, 232 gaps and 89 boundaries.
  - **The Dencker boxes are not blind:** they were drawn by students who could see the transliteration.
  - **Coverage is small:** only 4 tablets serve as bootstrap clusters, so the interval is not reliable.
  - It hints that gaps in Neo-Assyrian carry some boundary information when the boxes are expert. It is not a test and cannot count toward anything.

## Rater behaviour (a finding about the measurers, not about the script)
- **Opus declines about half the faces:** it skipped 154 of 298 in the main round and 156 in F2. Fable boxes nearly everything but places boxes poorly: its ICC against gold was 0.24 and then 0.31.
- **Fable's skips rose from 7 to 63 under F2,** with the upsampled crops and the stricter paragraph. Opus's skips did not change.
- When both raters did box the same pairs, they agreed with each other (ICC 0.72 to 0.98) more than either agreed with the experts. So their errors are shared, not random. This is consistent with both reading the rotated crops in the same coarse way.

## What this can and cannot say
- **It can say:**
  - Current frontier agents, working blind from rotated photos, cannot box cuneiform signs well enough to measure inter-sign gaps. The precision needed is ICC ≥ 0.70 against expert boxes at about 0.1 sign height.
  - So the gap-as-word-boundary route cannot be tested in read cuneiform with blind agent measurement. It cannot be taken to Indus either, where no gold boxes exist at all.
- **It cannot say:**
  - that gaps do not mark word boundaries. Nothing decisive was measured, and the expert-box AUC of 0.66 is a non-blind description;
  - anything about any Indus sign or text.
- **Bearing on the 2027 bar:** none.
- **The gap route for Indus is closed** until an expert or validated measurer exists. That means human-drawn boxes for read cuneiform and for Indus, drawn blind to readings.

## Disclosures
- **Implementer choices:** the code has 35 `PREREG-AMBIGUITY` markers, all listed in the code-writer's report and visible in the files. The one that bears on G2 is that the G2 gap is the raw gap in crop pixels, with the normalised ICC reported beside it. Both fail.
- **A failed first launch:** the first attempt to run the F2 alignment commands failed before executing anything (a shell quoting error). The commands were then run once. No output existed from the failed attempt.
- **R2 overrides:** recorded in `raw/r2/override_r2_1.json`. The manifest stores the override file's sha256.
- **No re-runs beyond the sealed F2, no tuning, no fix tags.**
