# Red team: do ticked fish really cluster by block at Mohenjo-daro?

Pre-registered in `docs/prereg/redteam_fish_block.md` (hash in `docs/prereg/HASHES.txt`, tag `redteam_fish_block`) before any test was run. Ledger rows `rtfb_*` in `docs/test_ledger.csv`. Code: `run.py` (all pre-registered attacks; log `run.log`, output `results.json`), `a5_power_blocksize.py` (one exploratory power check).

## Verdict: WEAKENED

The clustering is not an artefact. It survives depth control, text-family collapse, OCR repairs, an independent sign coding, and leave-one-out. It fails two of the pre-registered tests:
- It does not survive correction over every test reg_findspot ran (q=0.11).
- It does not replicate in the other Mohenjo-daro seals. That replication had only partial power, because M77 loci are whole excavation areas, not blocks.

Treat it as a solid local pattern in Mackay's DK-G area, not as a city-wide fact.

Baseline reproduced: G=36.2 against a null of 16.7, p=0.0009 (21 ticked-fish seals among 611).

## 1. Depth or period confound: rejected

- **Ticked fish do not trend with depth.**
  - In FEM, r=-0.03 (p=0.50). The ticked-fish median depth is 10.0 ft, against 11.0 ft for all seals.
  - Across all 1,232 M77 Mohenjo-daro seals, rho=-0.01 (p=0.72).
  - By 5-ft band the rate is 3/56, 7/218, 7/185, 3/132, 1/42.
- **Blocks do differ strongly in depth** (Kruskal-Wallis p=6e-32). Blocks 16 and 22 have median depths near 5 ft; blocks 1, 2 and 3 near 14-15 ft.
  - This does not matter, because the feature itself has no depth trend.
  - Block 12, the main cluster, sits at a median of 13.5 ft. Block 1 is at 14.5 ft and block 7 at 13.0 ft, and they hold 1 of 150 seals between them.
- **Re-tests with finer depth control:**

  | Depth control | p |
  |---|---|
  | 3-ft strata | 0.0013 |
  | 2-ft strata | 0.0007 |
  | 1-ft strata | 0.0013 |
  | Depth deciles | 0.0007 |
  | Sum of G within each 5-ft band | 0.003 |
  | Depth spline as covariate (parametric null) | 0.0008 |
  | Logistic LR test of block given the spline (df 16) | 0.003 |

## 2. Batch or single carver: rejected

- **The 4 house-12/V seals are not copies.**
  - Texts: `M152 M99 M53 M59 M87 M60`, `M87 M59 M71`, `M258 M342 M87 M60 M87 M272`, `M100 M17 M60`.
  - Pairwise edit distances are 3-5.
  - The seals come from rooms 91, 95 and 96 and lie 10.9-20.2 ft deep, so the deposits span about 9 ft. That does not fit a single carving event.
- Among all 21 ticked-fish texts, no pair is within edit distance 1.
- **Strict family rule** (same unit and the same sign + ticked-fish bigram):
  - Two pairs merge: the M87 M60 pair in 12/V, and the M99 M68 pair in block 6.
  - That leaves 19 families. The block test still gives p=0.0056.
  - M87 M60 is simply the commonest ticked-fish bigram (6 of 21 seals), so this merge is conservative.

## 3. Statistic, multiplicity, small counts, OCR

- **Multiplicity:**
  - Over the 21 reg_findspot confirmatory tests: BH q=0.015.
  - Over all 163 tests run (21 confirmatory, 140 single-sign scan, 2 E1): BH and Holm q=0.114.
  - **This fails the pre-registered bar.** The defence is that the 140 scan tests ask a different question (single signs, not a prior class), but the bar was set in advance.
- **Alternative statistics and unit definitions** (none of these selected after the fact):

  | Variant | p |
  |---|---|
  | Pearson chi-square | 0.003 |
  | Max standardized residual | 0.030 |
  | Minimum block size 5 | 0.012 |
  | Minimum block size 15 | 0.006 |
  | **Minimum block size 20 (only 7 units)** | **0.098** |
  | Streets excluded | 0.0001 |
  | 'Other' excluded | 0.004 |
  | No depth strata | 0.0006 |

  Only 1 of 8 variants exceeds 0.05, so this is not fragile under the pre-registered rule (which needed more than one).
- **Leave-one-out:**
  - Leave-one-house-out: worst case is dropping 12/V, p=0.015.
  - Leave-one-block-out: worst case is dropping block 12, p=0.018.
  - Every other drop gives p ≤ 0.005.
- **OCR:**
  - 3 ticked-fish seals had their block read after stripping a junk prefix ('i 3', 'I 9'). Dropping them gives p=0.0013. Reading the prefix as a '1' (blocks 13 and 19) gives p=0.0028.
  - No ticked-fish seal had a repaired house numeral.

## 4. Allograph or catalogue coding: rejected

- **Among fish-bearing seals only** (211), ticked vs plain still clusters by block (p=0.025). So this is not a fish-rate effect.
- **Independent coding (Wells/ICIT) via the bridge:**
  - On 94 fish seals linked to ICIT, Wells and Mahadevan agree on ticked vs plain 97% of the time.
  - The 3 disagreements:
    - serial 520: M77 has M65, ICIT has W232 (= M71)
    - serial 226: M73 maps to W234, which is not in the bridge
    - serial 53: a bad ICIT link
  - On the ICIT-linked subset (266 seals), the Wells coding gives a block p of 0.030. The M77 coding on the same subset gives 0.16; with 9-10 ticked seals this is low power.
- **No catalogue batching.** Ticked-fish seals are not contiguous:
  - FEM serial nearest-neighbour gap: 14.0 against 17.8 for random sets (p=0.13)
  - CISI numbers: 43 against 69 (p=0.12)
  - The CISI numbers run M-54 to M-1050.

## 5. Replication: not replicated (partial power)

- **Mohenjo-daro outside FEM** (582 seals, 20 ticked fish, M77 locus units):
  - Result: p=0.31.
  - Pre-registered power: 0.83 for a 6x rate in a whole locus.
  - Exploratory check: 0.44 for a block-sized cluster (4 extra ticked fish in one locus).
  - So the replication's failure counts against the claim, but only moderately.
- **FEM itself at M77 locus resolution** (31 vs 32) shows nothing (p=0.84). The effect is visible only at block scale, which no other register provides.
- **Harappa:** 3 ticked-fish seals among 350. The test is untestable (power 0). Vats gives mound only, with no block-level findspots.
- **Chanhu-daro:** 3 ticked fish among 44, in squares 8/F, 9/D and 9/C. Descriptive only.

## Hypotheses tested

| Attack | Verdict |
|---|---|
| Depth/period confound | refuted (all depth controls p ≤ 0.003) |
| One batch / one carver / text family | refuted (19 families, p=0.0056) |
| Statistic chosen among several | mostly robust (1/8 variants p>0.05) |
| Multiplicity over all 163 tests | **fails** (q=0.114) |
| Leave-one-house/block-out | robust (max p=0.018) |
| OCR block repairs | robust (p ≤ 0.003) |
| Allograph / coding batch | refuted (97% agreement; independent coding p=0.03; no contiguity) |
| Replication in other MD areas | **not replicated** (p=0.31, power 0.44-0.83) |
| Replication at Harappa / Chanhu-daro | untestable |

## Suggested restatement

"In Mackay's DK-G area, ticked-fish seals are unevenly spread across blocks (p≈0.001, robust to depth, text families, OCR and coding). The pattern is concentrated in block 12, house 12/V. It does not survive correction over every findspot test run (q=0.11) and is not seen at the coarser area resolution of the rest of Mohenjo-daro. Status: local lead."

## Next experiments
- Block- or house-level findspots for Marshall's HR/VS seals (MIC register re-OCR, or CISI findspot fields) are the only real replication.
- Check the ticks on CISI photos of the 10 ticked-fish seals with CISI numbers (M-54, 57, 202, 227, 232, 367, 387, 762, 827, 1050), plus a matched set of plain fish.
