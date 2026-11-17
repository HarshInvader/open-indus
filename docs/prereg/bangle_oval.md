# Pre-registration: bangle oval, confirmatory test on bangles not used to find it (2026-11-15)

Area: `experiments/bangle_oval/`. Fable 5.2 plan 4, item 2 (sprint S2). Hashed in `docs/prereg/HASHES.txt` (tag `bangle_oval`) with `b0_baselines.py`, `baselines.json`, `b1_power.py`, `power.json` BEFORE any sign of any candidate new bangle was looked at.

## Lead being tested
self_label: oval W790 (= M373/M374 per CISI photo check in roof_context) on 6/41 distinct ICIT bangle texts vs 0.45 expected (q=0.008); Harappa 2/6. M403 (W840) on 5/41, seen post hoc. Already frozen for future finds as L2/L2b (`2026-11-15_leads_predictions.md`); this file does not change L2, it adds the rules below for any sample assembled now.

## Discovery set (excluded from the new sample)
Every ICIT row with type BNGL (50 rows, 41 distinct texts), whatever its material (stoneware, shell, clay, terracotta, steatite, unrecorded). Any object whose CISI number or excavation number matches one of these is excluded.

## Search for an independent sample (done before this file, metadata only, no texts read)
1. ICIT non-BNGL rows: searched type, material, shape, cross-section, excavation number and notes for bangle / bracelet / ring / stoneware / shell / annular. Hits: none that is a bangle. Stoneware and shell rows are all BNGL except L-111 (shell rectangular seal). Unidentified MISC terracotta rows (Kalibangan K-456..K-476, Karanpura 5 rows) cannot be typed without CISI vol 3 / excavation reports; they are NOT eligible unless a publication calls them bangles.
2. CISI vol 1 (India collections): no bangle section (miscellaneous = copper objects, M-619 cone, M-620 shell ladle).
3. CISI vol 2 (Pakistan): the stoneware-bangle section M-1628..M-1647 and H-1009/H-1010 are all in ICIT (discovery). Not in ICIT: H-1008, captioned "t.c. BANGLE(?)" (p. 349); M-1648 "shell objects"; M-1655..M-1657 "faience / steatite ornament". Only H-1008 is a bangle candidate, and the caption marks it uncertain.
4. Literature (web; harappa.com PDFs return 403): published inscribed stoneware bangles are the Mohenjo-daro 1983-85 surface finds (Halim & Vidale 1984; CISI M-1628ff; ICIT '84-x'), Mackay/Marshall DK/HR/SD bangles, and HARP Harappa finds (H90-1575, H96-5674, H2000-x). Counts in secondary sources: ~22-23 (MD 18, Harappa 4, Balakot 1). All of these are ICIT BNGL rows. No inscribed bangle from another site found in print.

**So the eligible new sample is n = 0 confirmed, n <= 1 possible (H-1008).** Minimum n for a test is 10 (as L2). The confirmatory test below is therefore not run now; it is frozen for the first sample that reaches n >= 10 (Fuls 2023 catalogue, CISI 3.x, HARP bangle database, new excavations).

## Hypotheses and rules (for any future eligible sample)
Unit: distinct (sequence, site) texts on eligible new bangles (any material), >= 1 readable sign. Oval = M373 or M374 (W790); diamond M261 / W850 does not count. Transcription from photographs or the publication's own sign list, before scoring; uncertain signs scored both ways (primary = certain only).

- **H1 (primary).** Oval on >= 15% of new bangle texts vs < 1% of non-bangle texts at the same sites. Decision:
  - PASS: one-sided exact binomial p < 0.05 against p0 = the non-bangle W790 share at the same site(s) in ICIT (pooled 0.0106; MD 0.0096; Harappa 0.0106; other sites use the pooled value), AND observed share >= 0.08.
  - STRONG PASS (the point prediction): PASS and observed share >= 0.15.
  - FAIL: share < 0.03 with n >= 15, OR exact one-sided 95% upper bound < 0.15 with n >= 20.
  - otherwise "neither". n < 10: INCONCLUSIVE, descriptive only.
  - Why the share bar is 0.08 not 0.15 for PASS: if the true rate is 0.15, a ">= 0.15 observed" rule passes only ~50% of the time at any n (power.json). 0.15 is the predicted rate; 0.08 is the frozen L2 bar.
- **H2 (secondary, slot).** Among new bangle texts with the oval, >= 50% are one-sign texts OR the oval is in one fixed slot (all first, or all last) in >= 2/3 of multi-sign cases. Reported with n; no p-value unless >= 4 oval texts.
- **H3 (exploratory).** M403 (W840) share on new bangles, vs ICIT non-bangle 0.026 (98/3776). Reported only.
- **H4 (workshop-mark alternative).** If the oval marks one workshop rather than the object class, it should be concentrated: (a) site: oval share at Mohenjo-daro vs Harappa (Fisher two-sided); (b) series: within Mohenjo-daro, 1983-85 surface collection vs Mackay/Marshall excavated bangles; (c) area/period where recorded. Prediction of the 'bangle word' reading: oval present at >= 2 sites with no significant site difference; workshop reading: confined to one site/series. Power (power.json): Fisher has 4% power with 10 texts per site and 14% with 20, so a null on H4 is NOT evidence against a workshop. Run descriptively on the discovery set now (allowed: it describes the lead, it does not test it), and as a test on any future sample.

## What would change the verdict
- PASS at a third site (not MD or Harappa) would argue against a single-workshop mark. Even a PASS gives only "bangle-class sign", not "the word bangle".
- FAIL with n >= 15 closes the lead (same as L2).

## Ledger
Rows `bo_*` in `docs/test_ledger.csv`: H1 untestable (n=0), power statement, H4 descriptive on discovery set.
