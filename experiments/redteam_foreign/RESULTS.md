# Red team of task #1: do foreign texts really break Indus sign order? (board task #11, H2)

## Verdict: the claim holds

**9 of the 39 scorable foreign texts stay flagged under every reading and direction we tested.** Chance would give 2.0 of 39 (binomial p = 1.1e-4). A reading-error null that assumes one misread sign in every non-confirmed text expects 2.9 (p = 0.002). In 9 of the 10 originally flagged texts, the flag comes from the order of the signs, not from unusual signs. Under the pre-registered rule (both p < 0.01) the verdict is **holds**.

One flag falls: **SUSA-02**. The M77 reading of the Susa cylinder looks like ordinary Indus in either direction (p 0.20-0.25). That reading leaves 4 of 8 signs unbridged, so it is weak, but the rule drops the text. The other disputed readings move the opposite way:
- **UR-02** with the M77/Laursen ending is strongly out of order (p = 0.005, against 0.089 as read by ICIT).
- **FAILAKA-01** read reversed is flagged (p = 0.02).
- **UR-05** as M77 reads it is flagged (p = 0.041).

These are candidates for the crib attack (#4) once their readings are checked against images (task #12).

Pre-registration: `docs/prereg/redteam_foreign_order.md` (sha256 in HASHES.txt, tag `redteam_foreign_order`). Code: `attack.py`. Numbers: `results.json`.

## Tests

| test | result |
|---|---|
| T1 reversed direction | BAHRAIN-01 p = 0.005 both ways (survives). SUSA-02 reversed p = 0.024 (survives T1). FAILAKA-01 reversed p = 0.02 (gains a flag). Calibration: 44% of native seals (n = 1,094) are flagged when reversed, so the test can tell directions apart. |
| T2 alternative readings | UR-02 (M77 ending) 0.005; UR-05 (M77) 0.041; SUSA-02 (M77) 0.254, reversed 0.203, so it drops out |
| Survivors of T1+T2 | **9/39**: UR-01, GIRSU-02, BAHRAIN-01, BAHRAIN-06, BAHRAIN-07, SALUT-01, UNPROV-02, UNPROV-03, UNPROV-07 (binomial p = 1.1e-4) |
| T3a all-register native reference | 12/39 flagged (p = 2.7e-7). LURISTAN-01 and SUSA-01 join, so a broader reference makes the flags stronger. |
| T3b 0.18 bits/sign format penalty | 10/39, the same set as before (p = 1.6e-5) |
| T4 bridge for M77-only texts | Native M77 held-out seals bridged the same way are flagged at 4.9% (n = 366), so bridging adds no false flags. One M77-only text is flagged (UNPROV-07). |
| T5 drop unprovenanced (unknown-WA) | 7/30 (p = 5.7e-4) |
| T6 misreading null | One random sign substitution in a native seal gives a flag rate of 8.2%. Expected flags under H0 = 2.9; observed 10 (p = 4.6e-4), and survivors 9 (p = 0.002). |
| T7 order versus inventory | The q statistic is the share of the text's own sign permutations that score better than the actual order. Native median q = 0, 90th percentile 0.22. Flagged foreign texts: median 0.51 (Mann-Whitney p = 1e-7). 9/10 are above the native 90th percentile. SALUT-01 is the exception: q = 0.08, so its flag comes from rare signs, not their order. |

So the flags are not explained by reading direction, a reference built only from square seals, the bridge, unprovenanced objects, or random misreadings, and they are about order. Seven of the 9 survivors are round Gulf seals. The others are GIRSU-02 (a square seal from Telloh) and SALUT-01 (a square seal of local stone).

## What this does not cover

- **Misreadings of visually similar signs were not modelled.** T6 substitutes signs at random by frequency. A random swap probably breaks order more than a real look-alike confusion would, so 8.2% is likely an upper bound for one error. Two or more errors in a text were not modelled.
- **No image was checked.** Readings are still corpus readings; task #12 (H1) owns that.
- **The T7 comparison is slightly uneven.** Natives are scored with their own CV fold model and foreign texts with the full model; foreign texts were never in training.
- **SALUT-01's flag is about its signs, not their order** (T7). Keep it out of any claim about foreign word order.
- **Not tested:** the extra sign seen in the drawings for UNPROV-02 and UNPROV-03. The sign's identity is unknown, so it could not be scored.

## For #4

- **Core set (9):** UR-01, GIRSU-02, BAHRAIN-01, BAHRAIN-06, BAHRAIN-07, UNPROV-02, UNPROV-03, UNPROV-07, plus SALUT-01 marked as flagged for its signs, not its order.
- **Sensitivity additions:** UR-02 (M77 ending), FAILAKA-01 (reversed) and UR-05 (M77), all depending on #12.
- **Drop SUSA-02** unless #12 confirms the ICIT reading.
