# Roof modifier vs context: is a roofed sign a "house of X"?

Pre-registration: `docs/prereg/roof_context.md`, hashed with `common.py`, `r1_test.py`, `r0_power.py` and `power.json` before any roofed-sign × context table existed. Single confirmatory run: `r1_test.py` (log `r1.log`, numbers `r1_results.json`, summary `results.json`). Ledger rows: `rc_*` in `docs/test_ledger.csv`. Fable 5.2 plan 2, item 8.

## Findings first

1. **"House of X" is not supported.** Roofed signs are not more common where buildings and storerooms were sealed or run. The pre-registered verdict is **neither**: no context effect, and the position effect misses its bar on all M77 data.
2. **Sealings vs seals: the effect runs the wrong way.**
   - ICIT clay sealings carry roofed forms *less* often than their unroofed bases: 4 observed vs 9.1 expected, OR 0.25, z = −2.56, one-sided p = 0.997.
   - M77 Lothal/Kalibangan sealings also go the wrong way (z = −1.49, 0 bases up, 3 down).
   - The roof fish M65/W235 is on 5 of 159 sealing tokens, against 23 of 280 for plain fish.
   - Without the fish bases, too few tokens are left to say anything (k = 3, z = +0.76).
3. **Citadel vs lower town: null.** The citadels are Mohenjo-daro SD+L, Harappa AB and Dholavira Castle+Bailey.
   - Merged ICIT area field: OR 1.41, 13 vs 10.9 expected, p = 0.19 (fake-modifier null p = 0.22).
   - M77 locus codes: OR 1.02, p = 0.46.
   - Counting Harappa Mound F as non-domestic: OR 1.00.
   - Power to detect a 3× enrichment was 0.96 and 0.99, so a strong building or institution association is excluded. A 2× effect is not (power 0.61-0.73).
4. **Door/storeroom sealing backs at Lothal: untestable.** Only 2 roofed sealings have a diagnostic back. This was stated in advance.
5. **Position: an opener-like shift, but it does not pass its own bar on all data.**
   - The roofed form is more often text-initial than its base: M77 8 bases up, 2 down, p = 0.071; ICIT 6 up, 0 down, p = 0.036.
   - Without fish: M77 p = 0.10, ICIT p = 0.014.
   - Pooled M77: roofed forms are initial in 69 of 213 cases (0.32), bases in 84 of 750 (0.11).
   - New facet: when a roofed form and its own base share a text, the roofed form comes first 15 vs 7 times (M77) and 13 vs 8 times (ICIT), p = 0.13 and 0.38. That is almost entirely the bigram M65 M59 (roof fish + fish).
   - These are the data the lead came from, so they can only describe it. The lead is now frozen for new finds as L1.

**Plain reading.** The roof does not tag sealed doors, storerooms or citadel buildings. At most it is a positional variant: the roof fish M65 tends to open the fish block (M65 M59), much as ticks close it. That makes it a slot convention inside the fish class, not a building word.

## Table of hypotheses

| hypothesis | result | verdict |
|---|---|---|
| A: roofed signs enriched on clay sealings vs seals | ICIT OR 0.25 (p = 0.997); M77 z = −1.49 | refuted (wrong direction) |
| A2: roofed signs on Lothal door/storeroom backs | 2 roofed sealings | untestable |
| B: roofed signs enriched in citadel / non-domestic loci | ICIT OR 1.41 (p = 0.19); M77 OR 1.02 | refuted for ≥3× effects; 2× not excluded |
| C1: roofed form more text-initial than base | M77 p = 0.071, ICIT p = 0.036 (same data as discovery) | lead (descriptive); frozen as L1 |
| C2: roofed form precedes its base in the same text | 15:7 and 13:8 | inconclusive |
| "House of X" (context + position) | neither leg passes | not supported |

## Caveats
- **Most roofed tokens are one sign.** The roof fish accounts for about 85% of them. The other roofed forms have 1-12 tokens each, so "roof" as a class is close to "roof fish".
- **Context fields are coarse.** Area-section is a mound or sector, not a building. A room-level test (block-house/room-grid fields) was not run.
- **Mohenjo-daro and Harappa "sealings" in M77 are mostly moulded tablets.** They were excluded from A, as the prereg stated.
- **Number of tests.** 2 primary context tests (Bonferroni α = 0.025), 2 replicates, 3 sensitivities, 4 descriptive position tests and 2 C2 counts.

## Task 2: all open leads frozen for new finds
- `docs/prereg/2026-11-15_leads_predictions.md` is hashed in `HASHES.txt` (tag `leads_predictions`) together with `experiments/new_finds/score_leads.py` and `lead_baselines.json` (from `r2_lead_baselines.py`). It freezes:
  - L1 roofed forms initial;
  - L2 lens/oval on bangles, plus L2b M403 (exploratory);
  - L3 ticked fish final;
  - L4 tall-2 + M59;
  - L5/L5b M93 at Chanhu-daro, and line-final;
  - L6/L6b number-name heads that survived redteam_pnl (M287 dropped);
  - L7 no-animal seals smaller.
- Each has a pass bar, a fail bar and a minimum n. The scorer passes a planted dataset. On the current `new_texts.csv` (2 scorable texts) every lead is inconclusive.
- **W790 photo check (CISI vol. 2).** M-1645 shows a single lens/oval, and M-1644 shows a plain oval beside interlocking lenses (W840 = M403). M-1646's diamond is coded separately as W850. So the bangle sign is M373 or M374, not the diamond M261. The scan resolution cannot separate M373 from M374, so L2 counts both. Interlocking lenses M403 also turned up on 5 of 41 bangles; this was seen post hoc and is exploratory. H-1010 and H-2578 need CISI vol. 3.

## Next
- Score L1-L7 once Fuls 2023 or CISI 3.x texts are transcribed.
- A room-level co-find test if a "house" reading is ever revived.
- Close the roof-as-institution route.
