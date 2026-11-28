# S8: the round-seal order test under other sign lists

Contributor: m0x1n (starter task S8). Pre-registration: `docs/prereg/s8_round_signlists.md`, sha256 `f5cff2ca…`, committed before any list was scored.

## Conclusion

**Robust.** The round-seal order anomaly does not disappear under any of the 12 alternative sign lists. The 8 round seals found in the Indus area keep their weak sign order under every list. The KN order excess over matched home seals is between +1.27 and +1.64 bits/sign (76% to 98% of the baseline +1.67), and p ≤ 6e-4 in every case.

Coarser lists shrink the excess most: lumping the jar and man signs, all lumps together, and the coarsest image clusters. Even there, at least three quarters of it is left. The harness reproduces the published number, and its planted controls are calibrated under every list.

## Results

Same groups, units, KN scorer, order component d, rare load and N1 null (length × rare load) as `experiments/redteam_round_order/run.py`. The excess is the home round mean d minus the N1 null mean, from 10,000 draws. C1 and C2 come from 1,000 replicates of 8 N1-matched home seals (2,000 draws each): C1 scores each with one of its own permutations as "real" (power), C2 leaves them unshuffled (false-positive rate).

| Sign list | Labels | Texts made identical by the list | Excess (bits/sign) | Share of baseline | p | C1 power | C2 false positive | Survives? |
|---|---|---|---|---|---|---|---|---|
| **ICIT** (baseline, Wells) | 710 | 0 | **+1.67** | 1 | 3e-4 | 1.00 | 0.053 | (baseline) |
| M77 (via bridge) | 688 | 72 | +1.57 | 0.94 | 2e-4 | 1.00 | 0.049 | yes |
| parpola | 687 | 74 | +1.58 | 0.94 | 5e-4 | 1.00 | 0.047 | yes |
| lump_fish | 678 | 159 | +1.55 | 0.92 | 1e-4 | 1.00 | 0.042 | yes |
| lump_numerals | 687 | 73 | +1.55 | 0.93 | 1e-4 | 1.00 | 0.053 | yes |
| lump_jar_man | 676 | 99 | +1.37 | 0.82 | 6e-4 | 1.00 | 0.055 | yes |
| lump_all | 651 | 242 | +1.41 | 0.84 | 1e-4 | 1.00 | 0.048 | yes |
| split_s1 | 806 | 0 | +1.43 | 0.85 | 3e-4 | 1.00 | 0.061 | yes |
| split_s2 | 819 | 0 | +1.64 | 0.98 | 1e-4 | 1.00 | 0.056 | yes |
| split_s3 | 814 | 0 | +1.34 | 0.80 | 4e-4 | 1.00 | 0.042 | yes |
| img_hi | 671 | 130 | +1.37 | 0.82 | 2e-4 | 1.00 | 0.058 | yes |
| img_mid | 656 | 162 | +1.38 | 0.82 | 2e-4 | 1.00 | 0.046 | yes |
| img_lo | 635 | 219 | +1.27 | 0.76 | 5e-4 | 1.00 | 0.062 | yes |

p = 1e-4 is the floor at 10,000 draws.

**C0 harness check: passed.** On the baseline list the excess is +1.67, p = 3e-4, against the published +1.64, p = 1e-4. That is inside the pre-registered ±0.25, and p < 0.01. Folds and permutations come from different seeds than the original, so the numbers are not identical. The same 8 texts are selected (114.1, 2419.2, 2911.1, 2912.1, 2977.1, 3668.1, 4247.1, 5468.1), and 1,769 home seals serve as reference.

## Pre-registered hypotheses

| Hypothesis | Pass mark | Result | Verdict |
|---|---|---|---|
| The round-seal order excess is an artefact of the Wells sign list | It disappears (p ≥ 0.05) under at least one list where C1 ≥ 0.8 | It never disappears. The smallest excess is +1.27 (img_lo), and the largest p is 6e-4 | **Refuted: robust under all 12 lists** |
| The harness reproduces `rro_1` | Excess within ±0.25 of +1.64, p < 0.01 | +1.67, p = 3e-4 | supported |
| The null is calibrated under every list | C2 about 0.05 | 0.042 to 0.062 | supported |
| The test has power under every list | C1 ≥ 0.8 | 1.00 everywhere | supported |

## Caveats

- **Only bridged signs change.** The M77-based lists act on Wells signs through `bridge_WM.json` (plus the fish, M109 and M342 codes from `signlist_robustness/harness.py`). The bridge covers 87% of native ICIT tokens and 29 of the 37 tokens on the 8 round seals. Signs without a bridge entry keep their Wells label under every list. That is why `lump_all` has 651 labels here rather than 309 as on M77. Lumping is therefore weaker on ICIT than on M77, especially among rare signs. A fuller W-M concordance (Fuls 2023, see `signlist_robustness`) would make this a stronger test.
- **Units are fixed before relabelling.** Texts that a list makes identical (up to 242 under `lump_all`) are kept as separate texts, as the prereg fixed. This keeps the 8 round seals and the reference set the same under every list. It also means near-duplicate texts can sit in different CV folds, which helps the KN model on ordinary seals. That would make the excess, if anything, larger. It does not explain why the coarsest lists lower it.
- **KN only.** The Wells class-bigram grammar (`rro_2`) and the positional model were not rerun, because their class seeds are tied to Wells sign identities. The KN result is the primary `rro_1` test.
- **The data are one corpus.** All lists re-read the same ICIT transcriptions. This shows the finding does not depend on how signs are divided. It does not show that the readings themselves are right; that is starter task S1.
- Python 3.13.18, pinned packages. The run is deterministic and takes about 10 seconds on 4 cores.

## Files

- `run.py`: the test under all 13 lists, giving `results.json`. Optional arguments name single lists.
- `ledger_rows.csv`: 12 rows, mode `robustness`, family `s8:round_signlists`.

```bash
.venv/bin/python -I experiments/s8_round_signlists/run.py
```
