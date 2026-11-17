# Pre-registration: roof modifier vs context ("house of X"?) (experiments/roof_context)

Written 2026-11-15, BEFORE any roofed-sign x context (sealing/seal, citadel/lower town, Lothal back type) table was computed. Frozen with `experiments/roof_context/common.py` and `r1_test.py` in `docs/prereg/HASHES.txt` (tag `roof_context`). Fable 5.2 plan 2, item 8.

## Question
Does a roof (chevron/eaves) drawn over a sign mark a building or institution, "house of X"? If so, roofed signs should (1) be over-represented in the contexts where buildings and storerooms are sealed and administered, and (2) sit in a different text position from the unroofed base. Position alone would make the roof an opener variant, not a building word.

## Frozen roofed set (not changed)
Rows with modifier `ROOF` at confidence high/medium in the hash-frozen tables (sha256 checked by the code):
- Mahadevan (`experiments/modifiers/decomp.csv`): M65<-M59, M66<-M60, M92<-M89, M138<-M137, M159<-M158, M163<-M162, M334<-M333, M203<-M202, M196<-M195, M14<-M12.
- Wells (`experiments/modifiers/w_decomp.csv`): W235<-W220, W236<-W226, W44<-W33, W678<-W645, W83<-W80, W391<-W390, W361<-W360, W573<-W572.
M92 (roof over three tall strokes) stays in although it is a numeral; that is the frozen set.

## What I already know (contamination)
- The roof -> text-initial lead (modifiers: held-out 5 up/0 down, p=0.0065; ICIT 6/0, p=0.04; dev 5/4, p=0.29) was found on the same data. Every position test on existing data is therefore DESCRIPTIVE, not confirmatory. Only new finds can confirm position (frozen in `docs/prereg/2026-11-15_leads_predictions.md`).
- The modifiers run tested a "seal share" register (seal+sealing vs all other objects) for ROOF: dev p=0.35, not significant in held-out/ICIT. That is a different contrast from sealing vs seal and says nothing about locus. I have not seen roofed signs split by sealing/seal or by locus.
- Data facts checked before writing (marginals only): M77's "sealing" class at Mohenjo-daro and Harappa is mostly moulded tablets (matched to ICIT TAB:B/TAB:I), so it is not used as sealings. ICIT TAG* = clay sealings (mostly Lothal, Dholavira, Kalibangan). Only 2 Lothal sealings with a diagnostic back carry a roofed sign.
- Power (`r0_power.py`, `power.json`, marginals only, one-sided CMH alpha 0.05, planted odds ratio on roofed tokens):

| set | units | bases | roofed tokens | power OR 2 | power OR 3 |
|---|---|---|---|---|---|
| A ICIT sealing vs seal | 2,271 | 5 | 185 | 0.52 | 0.86 |
| A M77 Lothal/Kalibangan/other sealings | 254 | 4 | 20 | 0.33 | 0.56 |
| B merged ICIT citadel vs lower town | 2,614 | 6 | 180 | 0.61 | 0.96 |
| B M77 locus citadel vs lower town | 2,026 | 9 | 183 | 0.73 | 0.99 |

So a 3x enrichment is detectable in the primary sets; a 2x enrichment is a coin flip. Most roofed tokens are the roof fish (W235/M65).

## Tests
Unit: distinct (sequence, context, site[, object type]) units; '#' and '|' ignored (presence of tokens does not need complete texts).
Statistic: Mantel-Haenszel z, roofed form vs its own unroofed base, for the share of tokens in the context, stratified by base x stratum (site for A; site x object type for B). Positive = roofed higher.
Two nulls, both one-sided (roofed higher):
- label permutation: context labels permuted among units within stratum (5,000);
- fake modifier: same pair structure, each base and roofed sign replaced by a random sign of 0.5-2x its token count (2,000), capturing ordinary between-sign heterogeneity.
A test PASSES when BOTH nulls give p < 0.025 (Bonferroni over the two primary context tests) in the primary set AND the replicate set has z > 0.

- **A (sealing vs seal).** Primary: ICIT, class sealing = TAG*, seal = SEAL* except SEAL:C. Replicate: M77 seal vs sealing at Lothal, Kalibangan and "Other sites" only. Sensitivity: drop the fish bases (W220/W226, M59/M60).
- **A2 (door/storeroom).** Lothal sealings with Frenez & Tosi 2005 backs; door/storeroom = structures, pegs-on-wall, lockers. Fisher one-sided, roofed vs not. Minimum 3 roofed sealings; with 2 known now, A2 is expected to be UNTESTABLE and does not enter the verdict.
- **B (large non-domestic structures).** Primary: merged ICIT corpus area-section field (paragorth, as in experiments/administration t2b). Non-domestic = citadel mounds: Mohenjo-daro SD + L (Great Bath, granary, pillared hall), Harappa AB, Dholavira Castle + Bailey. Lower town = Mohenjo-daro HR, VS, DK*, MN; Harappa E, ET, D, J, G, H, F; Dholavira Middle Town, Lower Town, Annexe. Replicate: M77 locus codes mapped as in administration t2 (MD 1-15 citadel, 16-39 lower; Harappa 47-51 AB citadel, 40-46 and 52-54 lower). Sensitivities: Harappa Mound F (granary/work floors) counted as non-domestic; fish bases dropped.
- **C (position, descriptive).** C1: text-initial share, roofed vs base, with the modifiers calibrated robust statistic (`experiments/modifiers/common.calibrated_test`, feature `init`) on M77 all (dev+held-out v2) and ICIT all; position counts as present if one-sided p < 0.05 in both. Also with fish bases dropped. C2 (new facet, never computed): in texts containing both a roofed form and its own base, which comes first (two-sided sign test; minimum 5 texts).

## Decision rule
- House of X SUPPORTED: (A passes OR B passes) AND C1 position present.
- Opener variant: C1 position present, neither A nor B passes.
- Context only: A or B passes, no position.
- House of X is CONTRADICTED (not just unsupported) if both A and B primary z <= 0, given power >= 0.86 for a 3x effect.
- Sensitivities (no-fish, Harappa F) are reported but cannot turn a fail into a pass.

## Ledger
One row per primary test (A ICIT, A M77, B merged, B M77), C1 (2 rows, descriptive), C2, A2, in `docs/test_ledger.csv` with prefix `rc_`. Total confirmatory tests: 2 primary (A, B).
