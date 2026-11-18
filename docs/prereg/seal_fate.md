# Pre-registration: seal_fate (board #33, agent N1), 2026-11-18

Question (the Indus version of Proskouriakoff's test): does what happened to an inscribed object go with what its text says?

## State at registration
- Fate codes exist (`experiments/seal_fate/fate.csv`, from `code.py` on `remarks.csv`, scheme in `CODING_SCHEME.md`). They were made from the excavators' remarks only, with pictogram counts masked; no sign content was opened.
- No M77 or ICIT sign sequence for any coded object has been looked at. Known so far: link counts only (from `registers.csv` text numbers).
- Fates the 1930s registers record often enough to test (linked objects): Harappa BROKEN 64 of 251 (Vats 1940 finds lists); Mohenjo-daro OPEN (street, lane, alley, between blocks) 151 of 639 vs ROOM 480 (Mackay 1938 tabulation); Mohenjo-daro BROKEN_PROXY (a dimension printed as `?`) 34 of 645.
- Too rare to test (reported as counts only): BURNT 0, CUT 0, REUSED 0, HOARD 1, BURIAL <= 5, DRAIN/WELL/GATE 0, SURFACE 7 + 0, UNFINISHED 11 + 1, WORN 4 + 5, FEM prose BROKEN 4.

## Data and definitions (fixed now)
- Link: Vats serial -> M77 text 4000 + serial; FEM serial -> 2000 + serial (Mahadevan App. V, as in old_registers). One row per serial.
- Text: all M77 lines and sides of the object, in reading order, `|` dropped; tokens = signs other than `#`. Length L = number of tokens.
- Objects with L = 0 are dropped.
- Distinct texts: within each fate value, keep one object per distinct token sequence (Rule 1). An identical text in both groups stays in both.
- Sign classes (from docs/GRAMMAR.md and earlier experiments, fixed before any outcome):
  - OPENER = M267, M391, M293, M150, M286, M412, M146, M395, M305
  - CLOSER = M342, M211, M15, M254, M12, M14, M388
  - FISH = M59-M75 (17 signs, includes M64)
  - NUMERAL = M86-M121 minus M90, M92, M93
- Statistic for a set of objects: for each class, the share of its tokens that fall in the class (4 shares).

## Confirmatory tests (4; Holm across them, alpha 0.05)
- **H1 Harappa: broken vs intact, sign classes.** Omnibus T = sum over the 4 classes of z^2, where z compares the broken group's class share with a truncation null. Null: for each broken object of length L, draw an intact Harappa object of the same type (seal vs other) with length >= L and keep a random contiguous window of L tokens; repeat for 5,000 pseudo-broken sets. Two-sided via z^2. p = (1 + #null T >= obs) / (1 + 5,000).
- **H2 Mohenjo-daro: BROKEN_PROXY vs the rest, sign classes.** Same test as H1 on FEM objects. This is the held-out replication of H1. A per-class direction counts as replicated only if both H1 and H2 have that class with |z| >= 1.96 and the same sign.
- **H3 Mohenjo-daro: OPEN vs ROOM, sign classes.** Omnibus T as above over the 4 class shares (OPEN group). Null: OPEN/ROOM labels permuted within strata of object type x 5-ft depth band (FEM level; missing level = its own band), 5,000 times. Objects that are neither OPEN nor ROOM are dropped.
- **H4 Mohenjo-daro: OPEN vs ROOM, text length.** Difference in mean L (OPEN minus ROOM), same permutation null, two-sided.
(No length test for breakage: breakage removes signs by itself.)

## Exploratory (not counted in the verdict except as leads)
- E1 per-sign scan: every sign on >= 8 objects in the test set. Presence rate in the fate group vs the H1/H2 truncation null (broken) or the H3 permutation null (OPEN). BH at q 0.10 within each scan. A broken-scan lead needs the same direction at p < 0.05 at the other site.
- E2 Harappa UNFINISHED (n ~ 11) and WORN, descriptive only.

## Power and calibration (run before reading H1-H4 results, reported with them)
- Planted control: in the fate group, replace non-class tokens with class signs (drawn by class frequency) until the class share is multiplied by r = 1.5, 2, 3; one class at a time; 200 plants per (test, class, r). Power = share of plants with omnibus p < 0.05 (null draws reused for H1/H2 because the truncation null does not depend on the broken texts; 1,000 permutations per plant for H3). Report power for every test.
- Calibration of the truncation null: 200 sets of pseudo-broken objects made from intact objects by the same truncation; false-positive rate at 0.05 must be <= 0.08, else H1/H2 are reported as unreliable.
- Inter-coder consistency: a hand recode of a 20% sample (seed 7) after this file is hashed and before outcomes are computed; Cohen's kappa per code. kappa < 0.6 on a code marks its tests unreliable.

## Verdict rules
- Positive: an H with Holm-adjusted p < 0.05, and for H1 the per-class direction replicates in H2. A positive gets an M6 red-team task.
- Negative: no H passes, and power >= 0.8 at r = 2 for the test; then "no fate-text link of that size".
- Inconclusive: no H passes and power < 0.8 at r = 2.
- What would falsify a positive: the effect disappears when Harappa objects are restricted to seals only, or when FEM objects are stratified by block as well as depth (both run as robustness checks if anything passes).
