# meaning_calibration: kill test (prereg `docs/prereg/meaning_calibration.md`, sealed 2026-11-24T09:02:39Z)

## Verdict: the kill test FAILED, so the study stops as sealed
- **F planted power: 0.455** (71 of 156 planted heads survive; 44 more could not be planted). The bar was 0.8.
- **F false alarm: 0 of 1,000** on within-text shuffled draws. The bar was ≤ 0.05.
- **Sealed outcome.** "The form behind our S meaning rows is underpowered at Indus size in a read script", as sealed. No claims were written, and no parameter was changed.

| dev next-tokens of head | planted | power |
|---|---|---|
| 10-19 | 64 | 0.75 |
| 20-49 | 51 | 0.45 |
| ≥ 50 | 41 | 0.00 |

Draws: 5 × (1,680 dev + 565 held-out documents). Eligible heads per draw: 77-84; eligible in every draw: 62 (22 ideogram/measure, 17 numeral, 23 word).

## Why (exploratory diagnosis, after the verdict)
- **All 85 planted failures have the same cause: the p-value floor.**
  - With a one-partner claim, the null holds every token within ½-2× of the partner's frequency. The p34 rule uses pairs only when there are secondary partners.
  - For a frequent partner that is 7-98 tokens, so p ≤ 0.01 cannot be reached.
  - Planting at ceil(0.4·n) makes a frequent head's partner frequent, so power falls to 0 as frequency rises.
- **Every planted head with ≥ 99 pseudo-partners survived** (71 of 71).
- **So the failure is the test's resolution, not the signal.** At Indus size the rule cannot pass a one-partner claim about a frequent partner, whatever the data say.
- **Indus rows.**
  - MC-PAR-murukan-partners used a main partner plus the squirrel set, so its null is pairs and is large (gate 48/50).
  - MC-WEL15-fish-number rests on the six + fish test (README #5), not on this rule.
  - Neither S row is changed by this result.

## E power report (no claims, no verdict)
- Full corpus, single stage. The null is the within-site permutation of object class.
- Tokens reaching power ≥ 0.8 for a 2× enrichment:
  - sealings (134 documents): 5 of 467;
  - sealing + vase (188 documents): 6 of 467.
- All of them are numerals, measure signs or OVIS:m, so object-class enrichment cannot be calibrated on Linear B.
- MC-MUK19-stroked-jar-MET stays uncalibrated, as the prereg says.

Files: `kill.py`, `fcore.py`, `load.py`, `kill.json`, `kill_draws.json`, `kill.out`.

---

# v2 (prereg `meaning_calibration_v2.md` sealed 09:05Z; addendum 1 sealed before scoring)

## Kill test: PASSED (confirmatory, as disclosed)
- **Planted pair claims:** power 0.987, with coverage of at least 0.967 in every draw.
- **False alarm:** 0 of 1,000 on shuffled draws.
- **One-partner plants:** testable only 46% of the time. They are reported only and do not count toward the bar.

## Claims stage
**Claims**
- Writer A (knows Linear B) wrote 30 true claims, blind to the corpus.
- Writer B wrote 30 uninformed claims on opaque IDs, one for each decoy head.
- A chance baseline adds 50 random partner sets per decoy.

**Scoring:** `fcore2.verdict2`, majority over 5 draws of 1,680 + 565 documents.

| | S | U | R |
|---|---|---|---|
| A: true claims (30) | **3** | 27 (25 of them U-resolution in every draw) | **0** |
| B: uninformed claims (30) | **0** | 22 | 8 |
| Chance partner sets (1,500) | **0** | 1,494 | 6 |

**Sealed measures**
- **False-refutation:** 0 of 30. The one-sided 90% upper bound is 7.4%, so the bar (≤ 15%) is **met**.
- **AUC:** 0.67. The bar (≥ 0.75) is **not met**.
- **Share of true claims scored U:** 0.90, over the 0.6 limit, so the form is **underpowered** at this size, whatever its AUC.
- **Uninformed survival:** 0 of 30 (90% bound 7.4%). Chance survival: 0 of 1,500.

**Strata**
- **Ideogram heads:** all 16 are U.
- **Non-ideogram heads:** 3 S and 11 U. The 3 S are e-ke → o-na-to/pe-mo/ko-to-na, o-na-to → pa-ro/ke-ke-me-na/e-ke, and pe-mo → GRA/T.

## What it means
- **When the rule decides, it is right.**
  - Every S was a true claim (3 of 3), and no uninformed or random claim survived (0 of 1,530).
  - Every R was an uninformed claim (8 of 8 decisive B claims, plus 6 chance sets), and no true claim was refuted.
- **But it seldom decides on true claims.**
  - Most true claims name very frequent partners: numerals and measures after ideograms. A partner like `1` has almost no tokens within ½-2× of its frequency, so the null is too small (U-resolution).
  - The test is blind exactly where Linear B's strongest true regularities sit.
- **Sealed verdict.** The AUC bar is not met and the form is underpowered. The sealed consequence for the two S rows ("lets y% of uninformed claims survive") has y = 0 of 30 (bound 7.4%). The caution is therefore that the test **abstains**, not that it is lenient.
- **For the Indus S rows.**
  - MC-PAR-murukan-partners passed this rule's resolution gate on Indus (its null had pairs, gate 48/50). On this calibration, a pass under the rule had 0 false survivals in 1,530 tries.
  - MC-WEL15-fish-number rests on README #5, not on this rule.
  - Neither row's tier changes. Any annotation goes through a sealed scorecard addendum.

Files: `run.py`, `result.json`, `run.out`, `claims/`, `claims_input/` (`A_inventory.txt` and `B_inventory.json` are regenerated by `pool.py`).

## Caveats (from Fable's review of the result)
- **Precision rests on very few decisive true claims.**
  - The 3 S claims are one formula cluster (e-ke, o-na-to and pe-mo partner each other), so the effective n is about 1.
- **The claims behind "0 of 1,530" never saw the corpus.** Neither B's claims nor the random sets were fitted to it. A claimant who picked the pair after seeing the corpus (Parpola) is not bounded by this.
- **The murukan pass may not be covered.** In the Indus murukan row, the squirrel secondary is 0 of 74, so the row passed as a one-partner signal under a pairs null. The v2 plants always place some secondaries, so they do not cover a secondary that never occurs.
- **The draws are not independent.** All 5 resample one corpus.
- **Decoys and Writer A's choices.** Only 15 of 30 decoys are class-matched. Writer A chose mostly frequent-partner claims.
- **The genre differs.** Linear B is accounting text, not seal legends.
- **The prereg's row table is wrong about fish-number.** It lists MC-WEL15-fish-number as "F, calibrated", but that row rests on the six + fish test (README #5), a different rule. So it is **not calibrated** here.
