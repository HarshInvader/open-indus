# meaning_calibration v2, addendum 1: the claims stage (sealed before any claim is scored)

## Done before this seal
- The v2 kill test passed on 2026-11-24.
  - Planted pair power was 0.987, and coverage was at least 0.967 in every draw.
  - False alarm was 0 of 1,000.
  - One-partner plants were testable only 46% of the time (reported only).
- **Pools** (`pool.py`):
  - 63 heads were eligible in every v2 draw. A's pool is 60 of them, keeping the class mix.
  - The inventory has 4,443 tokens. The opaque IDs were assigned at random with a fixed seed.
- **Writer A** wrote 30 claims (`claims/A_claims.json`, hashed when written). A read only `A_pool.json` and `A_inventory.txt`.
- **Decoys** (`decoys.py`): 30, one per A head.
  - **Only 15 of 30 are class-matched.** A used 20 of the 24 ideogram heads, so the other 16 ideogram claims fell back to numerals, as the prereg allows.
- **Writer B** wrote 30 claims on opaque IDs (`claims/B_claims.json`, hashed with this file). B read only `B_decoys.json` and `B_inventory.json`.
- No claim has been scored.

## Scoring rules
- **Code:** `run.py`, which uses `fcore2.verdict2` unchanged.
- **R rule power:** the v2 kill test's power for each bin (`kill2.json`).
- **Majority over 5 draws.** U-resolution counts as U. A tie between the top two verdicts scores U.
- **AUC scores:** S = 2, U = 1, R = 0. Ties count 0.5.
- **Chance baseline:** for each decoy, 50 partner sets of B's size, drawn uniformly from the whole inventory with the decoy excluded. The seed is fixed.
- **Bars, verdicts and strata:** as in `meaning_calibration.md`.
  - False-refutation: one-sided 90% Clopper-Pearson upper bound ≤ 0.15.
  - AUC ≥ 0.75.
  - A U share above 0.6 marks the test "underpowered".
- **Stratum note.** Most of A's ideogram claims predict a numeral partner, and numeral-after-ideogram is a Linear B convention. The ideogram and non-ideogram strata are reported separately for that reason.
