# Pre-registration: reg_size (independent-object replication of space_and_sealing T4)

Agent: reg_size. Written 2026-11-14, BEFORE any sign-class share or text length has been related to face area on the new objects. Frozen together with `experiments/reg_size/rs_lib.py` and `experiments/reg_size/rs_test.py` (hashes in `docs/prereg/HASHES.txt`, tag `reg_size`).

## What I already know (disclosed)
- T4 (`experiments/space_and_sealing`, 952 distinct complete texts on ICIT square steatite seals): length +1.05 signs per doubling of area; connective (M99/M123) share +0.013/doubling ("dropped first", Holm 0.016); non-jar closers -0.021 (Holm 0.004) and post-closers -0.009 (Holm 0.019) "kept". T4's own replication failed (catalogue vs metric rho 0.31; family halves 0.60).
- Coverage only (`coverage.py`, `coverage.json`), run before this document:
  - Replication set (FEM + EH): 1,344 register rows -> 139 objects, **138 distinct complete texts** (Mohenjo-daro 85, Harappa 53) on square seals whose texts are NOT in T4's analysed set. Removed: 142 objects that are themselves T4 objects (ICIT id), 199 whose text equals a T4 text, 387 not square, 278 without dims, 74 incomplete texts, and smaller groups (types, material, links). Stricter set (also drop texts within one edit of any T4 text): 59 texts. Marshall MIC adds 15, Mackay CE adds 12.
  - **Measurement agreement (objects in both register and ICIT):** FEM 158 objects, 93% of sides within 0.3 mm of ICIT, median |diff| 0.03 mm, log-area reliability 0.95; EH 18 objects, 94% within 0.3 mm, reliability 0.999; Marshall 21 objects, 64% within 0.3 mm, reliability 0.69. **So ICIT's dimensions for these sites are the register measurements themselves** (inch figures converted). This replication is therefore independent in OBJECTS and TEXTS, not in MEASURER: it uses the same 1930s measurers (Mackay, Vats) on seals T4 did not see. The ~5% large disagreements are link or OCR errors; they set the measurement error of the new set at roughly that level.
  - **Text agreement:** for 221 register objects with both an M77 and an ICIT text, the M77 text classified with the bridge-translated classes gives the same counts as the ICIT text with T4's classes in all 8 classes for 81% of objects (per class 92-100%).
  - **Power** (from T4 data only: draw 138 T4 texts, compare with the remaining T4 texts, 1,000 draws), assuming T4's effects are true: all three signs right 0.71; rho >= 0.5 0.54; both 0.45. **The test is underpowered**; a failure is weak evidence against T4, a pass is meaningful.
- Smoke test with area shuffled across rows (pipeline check, no outcome seen).

## Data and frozen definitions
- **Objects:** `experiments/old_registers/registers.csv`, sources Mackay 1938 FEM (Mohenjo-daro) and Vats 1940 EH (Harappa). Square seal = max/min side <= 1.25, both sides 0.35-3.2 in, register type FEM "B" / EH "a" or blank; FEM material steatite or blank (EH records colour only, no material: declared deviation from T4's steatite filter). Inches x 25.4 -> mm; area = l x w.
- **Texts:** M77 text by Mahadevan's serial rule (`m77_text_no`), side-0 seal record, complete (`complete` true, no `#`).
- **Classes:** T4's frozen Wells classes (`sas_lib.CLASSES`, allographs `sas_lib.NORM`) translated to Mahadevan numbers through `bridge_WM.json`: an M sign belongs to class c if any Wells sign it is bridged to (after NORM) is in c; no M sign falls in two classes; unbridged M signs are core. Two M signs are also bridged to a non-class Wells sign (M161 -> W064/W390, M358 -> W752/W760); they are counted in the class.
- **Exclusion of T4 texts:** object excluded if any linked ICIT id is a T4 object; text excluded if its canonical sequence equals a T4 analysed text (canonical token = connected component of the Wells-Mahadevan bridge graph plus NORM; unbridged tokens compare equal to each other, which is conservative).
- **Unit:** distinct M77 text; area = mean log area over its objects; site = modal site.
- **Model (T4's exactly):** slope of each class's token share (class tokens / text length) on log area centred within strata, per doubling of area; permutation null = log area permuted within strata (10,000). **Strata = site** (the registers give no period; T4's sensitivity s4 used site-only strata). New objects form their own strata ("site#register").

## Predictions (primary)
- **P1 positive control:** text length rises with area, one-sided p < 0.05. If P1 fails the replication is uninterpretable.
- **R1 signs:** connective slope > 0 (loses share on small seals), other-closer slope < 0 and post-closer slope < 0 (hold their share).
- **R2 order:** Spearman rho between the 8 new slopes and T4's 8 P2 slopes (`t4.json`) >= 0.5. One-sided permutation p (area permuted within strata, T4 slopes fixed) is reported but is not part of the pass rule (8 items: rho 0.5 alone is weak).
- **Verdict:** P1 and R1 and R2 -> **replicated** (new objects, same measurers). P1 and exactly one of R1/R2 -> **partial**. P1 and neither -> **not replicated**, read against power 0.45.
- Reported with the primary (not decisive): per-class MDE; directional one-sided p for the three key classes with Holm over 3; z of the difference new - T4 per class.

## Sensitivities (reported, not decisive)
s1 also drop texts within one edit of any T4 text (59 texts); s2 + Marshall MIC; s3 + MIC + Mackay CE; s4 seals with an animal field symbol only (E4: text-only seals carry +0.81 signs at equal area); s5 strata site x register-depth tercile (time proxy); s6 single-line texts; s7 ICIT Wells text with T4's classes where the object links to exactly one complete ICIT text.

## Secondary: combined data (T4 + new)
Same model on T4's 952 rows (their site|period strata) plus the new rows (own strata). Report 8 slopes, Holm over 8, the order, and bootstrap stability (1,000 resamples of texts within strata): rank median and 95% interval per class, share of resamples keeping the three key signs, P(connective slope above both closer classes), mean Spearman of bootstrap slopes with the point estimate. **Stable order** = mean Spearman >= 0.8 AND each of the three key signs kept in >= 90% of resamples. Combined data are dominated by T4 (952 of ~1,090 texts), so this is not an independent test.

## Claim restriction
Omission order only (which sign classes thin first as the face shrinks). No status, rank or office claim (status-by-size is closed: rank_ladder, redteam_rank).

## What would falsify
T4's order on new objects: R1 sign reversal for the connective or a closer class with P1 passing, and rho < 0.5. Because power is 0.45, a single failure lowers but does not end T4's claim; a pass with P1 is a replication on new objects by the same measurers, not a measurer-independent one.

## Multiplicity and ledger
Confirmatory rows: P1, R1, R2, verdict (one family, 3 decisions + verdict); secondary rows: combined Holm and stability. Rows `rs_*` in `docs/test_ledger.csv`.
