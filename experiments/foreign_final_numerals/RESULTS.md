# Numerals at the end of foreign-found Indus texts (board #15, M1, agent H6)

## Verdict: not supported under the pre-registered rule. A strong but fragile signal sits on Gulf-type seals

**Primary set** (the 9 readings #12 accepts): 2 of 9 texts end in a numeral, against 0.28 expected from length-matched home seals. p = 0.030 (the larger of the two reading directions for SUSA-02 and BAHRAIN-01). However, dropping one text raises p to 0.24. Both hits are Bahrain seals (BAHRAIN-06, BAHRAIN-07), so the pre-registered robustness bar (leave-one-out p < 0.10) fails.

Power for the primary set is 0.81 at a true final-numeral rate of 30%. Under the pre-registered rule that makes the verdict **refuted**. In plain terms, the confirmed readings are too few for a two-text effect to count.

**Secondary set** (adds the 11 "sensitivity only" readings, n = 20): 6 of 20 vs 0.72 expected, p = 5×10⁻⁵, leave-one-out max p = 0.0006. **All 40 foreign texts** (descriptive, as in #10): 9 vs 2.08, p = 0.00025. These sets use readings #12 has not confirmed, so they cannot carry a claim. They do show where the effect comes from.

**Where it sits (post hoc, not pre-registered):** 6 of the 9 numeral-final texts are **round Gulf-type seals** (UR-02, UR-04, BAHRAIN-04, BAHRAIN-06, BAHRAIN-07, UNPROV-04). That is 6 of 21 Gulf-type round seals (29%) against 3 of 19 other foreign objects (16%) and 4.6% of home seals. The order-breaking survivors of #11 carry no more of it than the rest: 2/8 vs 7/32.

For the crib attack (#4), the final numeral looks like a feature of the Gulf/Dilmun round-seal genre (perhaps a count or a title slot), not evidence about a name ending. **Keep final numerals out of the name-matching window, or test #4 with and without them.**

## Numbers
| Set | n | numeral-final | null mean | p | leave-one-out max p |
|---|---|---|---|---|---|
| Primary, as read | 9 | 2 | 0.28 | 0.029 | 0.240 |
| Primary, SUSA-02/BAHRAIN-01 reversed | 9 | 2 | 0.28 | 0.030 | 0.237 |
| Secondary | 20 | 6 | 0.72 | 5e-5 | 0.0005 |
| All foreign (descriptive) | 40 | 9 | 2.08 | 0.00025 | n/a |

- **Home pool:** 1,508 distinct ICIT seal texts (non-foreign, known sites, length ≥ 2); 4.6% are numeral-final.
- **Null:** length-matched draws (pool L±1 if fewer than 30 texts at length L), 20,000 draws.
- **Power** (planted final-numeral rate r): primary 0.55 / 0.81 / 0.98 at r = 0.2 / 0.3 / 0.5; secondary 0.80 / 0.97 at r = 0.2 / 0.3.
- **Tests run:** 2 confirmatory (primary, secondary), each in 2 directions. Holm over the two keeps the secondary (p = 1e-4) and not the primary (0.030 × 2 = 0.06).

## Caveats
- **UR-02's last signs are disputed** (ICIT W328-W004-W002, M77 …W005). Both readings end in a numeral, so it stays a hit either way.
- **BAHRAIN-07's last block has 9 or 12 strokes.** It is a numeral either way.
- **UR-04 and UNPROV-04 have breaks** (`#`), so their last legible sign may not be the text's real last sign. They appear only in the descriptive set.
- **The home pool has few round seals.** The comparison is not shape-matched; a home round-seal subset is the obvious control.
- **Numeral = W001-W059**, as in #10. Some of these are stroke signs used in non-count roles.

## Files
`test.py`, `results.json`, `ledger_rows.csv`. Prereg: `docs/prereg/foreign_final_numerals.md` (sha256 bf037edd…).

## Next
- Shape-matched control: Gulf-type round seals vs home round/Gulf-like seals.
- Confirm the readings of UR-02, UR-05, BAHRAIN-04 and UNPROV-08 (#12 marked them "sensitivity only"). That decides whether the secondary result can be promoted.
