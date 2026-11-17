# Pre-registration: audit of the 'round seal' mislabel (board task #22, agent H8)

Written before any corrected rerun was looked at.

## Fact being audited
ICIT type SEAL:R is rectangular (388 objects, all at Indus sites, median w/h 2.23); only SEAL:C (32: 15 home, 17 foreign) is circular and SEAL:CY (9) is cylinder. Several scripts grouped ("SEAL:R","SEAL:C","SEAL:CY") as "round"; glib.icit_register maps SEAL:R to "round_seal", which (a) puts rectangular seals into "home round" controls and (b) drops them from glib's native "seal" reference pools.

## Correction
"round" = SEAL:C + SEAL:CY only. SEAL:R becomes an ordinary non-round seal ("square"/"seal" group in each script). Nothing else changes: same code, seeds, data, thresholds.

## Procedure
Each affected script is re-executed from experiments/round_label_audit/ twice under PYTHONHASHSEED=0: OLD (labels as written) and NEW (corrected), with all writes redirected into experiments/round_label_audit/out_{old,new}/. Grammar validate.py part (d) is re-executed alone (its other parts do not use the label). Scripts whose affected group contains no SEAL:R object (foreign-only filters: no foreign object is SEAL:R) are marked unaffected after a count check, not rerun.

## Decision rule per claim
A claim STANDS if under NEW its original pass criterion (same statistic, same threshold) still passes; WEAKENED if it passes but the effect or p moves by more than a third toward null; FAILS if the criterion no longer passes; UNTESTABLE if the corrected group has fewer than 6 texts. For the format control ("home round seals behave normally"), report the corrected home-circular n and the power to see an effect the size of the foreign one; with n<6 it is UNTESTABLE, not confirmed. For task #1 flags, report old vs new flag set and count vs expected (binomial p).
