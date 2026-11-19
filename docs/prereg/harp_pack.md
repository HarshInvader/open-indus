# Pre-registration: HARP prediction pack (sealed before the HARP spreadsheet arrives)

Registered 2026-11-19, before any HARP (Harappa Archaeological Research Project) per-object data has been seen. Kenoyer replied on 2026-11-18 that he holds an Excel sheet of inscribed objects and marked sherds (with pre/post-firing) and may share it after a reminder around 2027-01-05 (RESEARCH_STATE log). This file, `experiments/harp_pack/loader.py`, `score.py`, `power.py`, `test_loader.py` and `power.json` are hashed in `docs/prereg/HASHES.txt` (tag `harp_pack`) before that reminder is sent. Any result computed from the sheet under the rules below counts as confirmatory. Anything else computed from it is exploratory and must be labelled so.

## Bottom line

- **Kept (Holm family): C1 (jar sign rarer on pre-firing marks), C2 (opener-type signs commoner on pre-firing marks), C6 (jar sign on new Harappa pottery vs seals), C7 (docket tier x HARP lot), C9 (numeral value vs rim diameter).** These have planted power of at least 0.8 at the likely size, at alpha = 0.05/13.
- **Dropped now for low power: C3 lot-split pre-firing vocabulary (power 0.34), C4 sign x vessel form omnibus (0.28), C10a numeral vs bangle diameter (0.00), C10b oval bangle diameter (0.00), C11 numeral vs implement mass (0.00, n about 4 < 8), C12 numeral vs rod length (0.00 by the n >= 8 rule; 0.03 if the rule were ignored), C13 ticked-fish findspot clustering (0.00), C14 oval on new bangles (0.00).** They will not be run as confirmatory tests on this sheet, whatever it contains.
- **Not counted in this family:** C5 (F3b, jar sign on storage jars). It stays registered under its own rule in `forward_predictions.md` and is scored there; the planted power of that rule on this sheet is given below.

## What was seen before writing (contamination disclosure)

- The texts of most HARP inscribed objects are already in ICIT, including 2,717 Harappa object-sides, 386 docket tablets with tiers (`experiments/tablet_archives/tablets.csv`) and 350 Harappa pottery records. Earlier runs on these are known: tablet tier is not tied to a deposit proxy (tablet_archives T1, p = 0.83); stroke count does not track tablet size (m328_measure, rho -0.17); M342 on pottery vs seals is 0.80x in ICIT at Harappa/Lothal/Kalibangan and 1.36x in the consensus corpus at Harappa (m342_offsite, descriptive); M391/M343/M267 on painted vessels and M342 nearly absent there (firing_stage lead FS1, Kutch-heavy). **What is new in the sheet** is per-object lot, firing stage, vessel form and measurements, plus marked sherds not in ICIT. The tests below are about those new links.
- The power simulation used ICIT Harappa statistics only (sign frequencies and lengths of graffiti; Harappa seal texts; docket tiers). No HARP field was simulated from real HARP values, because none are in hand.
- C8 (tablet mass vs docket tier) was considered and excluded without a power run: mass and size of a tablet are near-proxies and the size result is known (rho -0.17), so it would not be a blind test.

## Expected spreadsheet and the column-mapping rule (`loader.py`)

Expected columns (any order, any names): lot; mound / trench / grid; stratum or period; object type; vessel form; firing stage and/or technique; length, width, thickness, height, rim diameter, inner diameter (any unit); mass; inscription id (CISI number, H-####); HARP field number (H<yr>-<reg>/<lot>-<item>); sign transcription; sign scheme.

Tolerant mapping, frozen in code:
1. Header normalised: lower case, a trailing unit in brackets or after a space is read off ("Max Length (cm)" -> `maxlength`, cm), then only [a-z0-9] kept.
2. Tier 1: exact match to a synonym list (`CANON` in loader.py). Tier 2: the header contains a synonym of at least 4 characters; the longest synonym wins. A header hitting two canonical columns equally is left unmapped and listed.
3. Two headers on one canonical column: the better tier wins; a tie stops the loader (`AmbiguousColumns`). The fix is a `column_map.json` next to the sheet, hashed and logged here as an amendment **before** `score.py` is run. Choosing among candidate columns may use only header names and the loader report (counts per normalised category), never a test statistic.
4. Units: lengths to mm (cm x10, m x1000, in x25.4), mass to g (kg x1000, mg /1000), from the header or per cell.
5. Values: object type -> POT / SEAL / SEALING / TAB:I / TAB:B / TAB / BNGL / ROD / IMPL / TAG / OTHER. Firing -> `pre_hand` (painted, or incised before firing), `pre_stamp` (stamped, moulded, seal-impressed), `post`, `NA` ("pre or post", blank). Vessel form -> storage_jar ("storage", "large jar"), jar_other, bowl_dish, goblet_beaker, other, NA. Period -> 1..5 with sub-period letters (roman numerals converted; "3B/C" kept), Vats strata as `Vats-<roman>`. Lot key = lot column (prefixed by the season year from the field number when present), else lot parsed from the field number.
6. Signs: W### and M### tokens; M mapped to Wells via `bridge_WM.json`. Bare numbers are used only if a scheme column or argument says Wells or Mahadevan. If the sheet uses another numbering (e.g. Parpola or a HARP code), all sign tests are UNTESTABLE until a concordance is built blind to the firing, form, lot and size columns and hashed as an amendment.
7. Join to ICIT by normalised CISI number. Tablets join to `tablets.csv` by CISI number.

`test_loader.py` checks all of this on a synthetic messy sheet (`fixture/harp_fixture.csv`): 23 checks, all pass.

## Units of analysis (rule 1: distinct texts)

- Sherd tests: a unit is a distinct (class, lot, sign sequence). Copies of one text in one lot count once; the same text in different lots counts separately (independent marking acts). A sherd without a lot gets lot `NA|<period>`, so identical texts without a lot collapse within period. Only rows with at least one readable sign are used.
- Tablet test: a unit is a distinct (copy group, lot), as in tablet_archives T1.
- Sensitivity, reported but not decisive: units = distinct sequence within class (ignoring lot).

## Tests

Family alpha 0.05, Holm over the kept tests that are eligible (meet their minimum n). A test passes only if its Holm-adjusted p < 0.05 **and** its effect bar is met. A test FAILS if it is eligible and either its kill criterion is met or its Holm p >= 0.05. Otherwise INCONCLUSIVE. A test below its frozen minimum n is UNTESTABLE (reported, never run as a verdict). Minimum n values are the smallest simulated size with power >= 0.8 (table below), written to `power.json` and read by `score.py`.

| id | hypothesis (origin) | units / data | statistic and null | pass | kill |
|---|---|---|---|---|---|
| C1 | Jar sign M342 (W740) is rarer on pre-firing handwritten marks than on post-firing graffiti (FS1; firing_stage) | sherd units, classes pre_hand vs post | count of pre units containing W740; null = firing labels permuted within period (exact stratified hypergeometric, lower tail). RR = smoothed pre rate / post rate | RR <= 0.5 and Holm p < 0.05 | RR >= 0.8 |
| C2 | Opener-type signs M391/M343/M267 (W820/W741/W861/W817) are commoner on pre-firing handwritten marks (FS1) | as C1 | count of pre units containing any of them; same null, upper tail | RR >= 2 and Holm p < 0.05 (FS1's ">= 15% of pre texts" is reported, not gated) | RR <= 1.2 |
| C6 | Jar sign M342 is commoner on Harappa pottery than on Harappa seals of the same length (m342_offsite, reopened on new sherds) | sherds not in ICIT (rows with an ICIT Harappa pottery CISI dropped; among rows without one, up to c rows per text dropped, c = ICIT Harappa pottery records without a CISI number carrying that text); seals = ICIT Harappa seals, distinct texts | R = observed / expected, expected from the seal rate in each stratum (readable signs 1-5 / 6+ x broken / complete); p = labels permuted within stratum (exact, upper tail) | R >= 1.25 and Holm p < 0.05 | R < 1.25 |
| C7 | Docket tier (2/3/4 tall strokes + M328) is tied to the HARP lot (tablet_archives T1 at true lot level) | docket tablets of tablets.csv joined to sheet lots; lots with >= 3 units | G of tier x lot; null = tiers permuted within object type x period (sheet period, else tablets.csv period key), 2,000 perms | Holm p < 0.05 | Holm p >= 0.05 at eligible n: lot-level tier archive closed |
| C9 | The numeral value on a sherd tracks the vessel's rim diameter (magnitude T2, rim as the size measure) | sherd units with rim diameter, collapsed to (lot, text) with median rim; V = sum of stroke values (magnitude W_NUM) | Spearman on within-stratum ranks (form x period), null = V permuted within stratum, 2,000 perms, two-sided; needs >= 8 units with V > 0 | Holm p < 0.05 | Holm p >= 0.05 at eligible n |

C6 runs as confirmatory only if the sheet carries CISI numbers (at least one sherd row matches an ICIT Harappa pottery CISI). Otherwise it is exploratory, because seen ICIT texts could not be removed.

C5, scored under forward_predictions.md (not in this family): jar sign on storage jars vs other forms (all jars vs non-jars if the sheet never says "storage"). PASS (not a self-label) if RR < 1.5; FAIL if RR >= 2 and Fisher p < 0.05; minimum 5 jar-bearing texts with form.

Candidates dropped for power (never run as confirmatory on this sheet; `score.py` still contains the C3 and C4 functions because they were power-tested, but `run_all` runs only the kept list in `power.json`):

| id | hypothesis (origin) | why it cannot reach 0.8 |
|---|---|---|
| C3 | A pre-firing vocabulary found in half the lots (sha256 parity of lot key) replicates in the other half (firing_stage primary, lot split replacing the site split); rule as firing_stage (S = ratio >= 5, >= 3 dev pre units; held-out R_ho >= 2, stratified hypergeometric) | 0.34: about 100 dev pre units; a sign on 6% of pre units rarely qualifies in dev and then rarely clears alpha in held-out |
| C4 | Some signs track vessel form (firing_stage secondary; potters_marks (c)); sum of G over signs in >= 10 units, form permuted within period x firing | 0.28: an omnibus over ~25 signs dilutes a 3-sign, +10-point effect |
| C10a | Numeral value vs bangle inner diameter (magnitude T3) | about 10 inscribed Harappa bangles; none of the 7 in ICIT has a numeral |
| C10b | Oval M373/M374 bangles differ in inner diameter (magnitude T3o) | about 10 bangles, 2-3 with the oval; power 0.00 |
| C11 | Numeral value vs implement mass (magnitude T1) | about 4 inscribed Harappa implements; magnitude.md needs n >= 8 |
| C12 | Numeral value vs rod length (magnitude T4) | about 7 rods; below n = 8 |
| C13 | Ticked-fish seals cluster by HARP lot / trench (TF1, reg_findspot F3) | ticked fish are 6 of 417 Harappa seal texts; about 3-4 among ~200 seals with findspots |
| C14 | Oval on new bangles (BO-H1) | about 3 bangles not already in ICIT; BO-H1 needs 10 |

## Power (planted answers; `power.py`, results in `power.json` and `power.log`)

Synthetic sheets are built from real ICIT Harappa statistics, an effect of the stated size is planted, and the frozen `score.py` functions are run. Power = share of planted sheets passing at alpha = 0.05/13 = 0.0038 (Bonferroni over all 13 family candidates, stricter than the Holm the real run uses). Size check = share of unplanted sheets passing.

Scenarios (assumptions, not knowledge):
- **Central (the decision scenario):** 975 readable sherd rows (80% of 1,218); 20% pre-firing handwritten; form known for all; rim diameter for 30%; about 60 lots per period; 740 readable sherd rows not in ICIT; 80% of docket tablets have a lot; tablet lots from a Chinese restaurant process within period (theta 60, ~40 lots with >= 3 units); about 200 seals with findspots; 10 bangles, 4 implements, 7 rods.
- **Pessimistic (reported only):** 600 readable rows, 10% pre-firing, form for 70%, rim for 20%, 400 new rows, 50% of tablets with a lot, finer lots (theta 120), 120 seals with findspots.

Planted effects: C1 pre-firing jar rate 0.04 vs base ~0.16 (FS1: 1/25 painted vs 70/384 graffiti). C2 pre-firing trio share 0.15 vs base ~0.05 (FS1's stated bar). C3 one sign on 6% of pre units and 0.5% of post. C4 three frequent signs each +10 points in one form class. C5 jar rate on storage jars 2x other forms. C6 jar rate 1.5x the seal rate of the length stratum (m342_offsite plant). C7 per-lot tier mix ~ Dirichlet(3 x global mix) (tablet_archives plant). C9 latent rho 0.5 between V and rim (magnitude plant). C10a/C11/C12 rho 0.5. C10b oval bangles 1 SD larger. C13 ticked-fish rate tripled in one area of >= 20 seals (reg_findspot plant). C14 true oval rate 0.15 (BO-H1).

Results (200 planted sheets per exact test, 100 per permutation test with 999 permutations; 60 unplanted sheets for size):

| id | central power | pessimistic power | size (no plant) | mean effect under plant (central) | frozen minimum n (power >= 0.8 on the size curve) | decision |
|---|---|---|---|---|---|---|
| C1 | 1.00 | 0.49 | 0.00 | RR 0.26 | 146 pre-firing units | KEPT |
| C2 | 0.92 | 0.41 | 0.00 | RR 2.98 | 145 pre-firing units | KEPT |
| C3 | 0.34 | 0.04 | 0.00 | - | - | DROPPED |
| C4 | 0.28 | 0.10 | 0.00 | G 271 vs 230 null | - | DROPPED |
| C6 | 1.00 | 0.99 | 0.00 | R 1.47 | 184 new pottery units | KEPT |
| C7 | 0.95 | 0.28 | 0.00 | G 166 vs 97 null | 184 tablet units in lots with >= 3 | KEPT |
| C9 | 1.00 | 0.82 | 0.02 (1/60) | rho 0.42 | 146 sherd units with rim (and >= 8 with V > 0) | KEPT |
| C10a | 0.00 | - | - | no numerals on ICIT Harappa bangles | - | DROPPED |
| C10b | 0.00 | - | - | - | - | DROPPED |
| C11 | 0.00 (n 4 < 8) | - | - | - | - | DROPPED |
| C12 | 0.00 (n 7 < 8; 0.03 ignoring the rule) | - | - | - | - | DROPPED |
| C13 | 0.00 (3.6 ticked fish expected) | 0.00 (2.0) | - | - | - | DROPPED |
| C14 | 0.00 (3 new bangles < 10) | - | - | - | - | DROPPED |
| C5 (own rule, not in family) | 0.39 (P(FAIL) at true RR 2) | 0.56 | P(PASS) under RR 1: 0.98 | RR 1.96 | 5 jar texts (its own rule) | scored under forward_predictions only |

Notes. C1, C2 and C7 lose power fast below the central size (pessimistic 0.28-0.49); the frozen minimum n makes them UNTESTABLE rather than weakly tested if the sheet is that small. C7's minimum n equals the full central size (0.74 at 75% lot coverage). C9's size 1/60 at alpha 0.0038 is within Monte Carlo error at 60 reps. C2's pass bar is RR >= 2 rather than FS1's ">= 15% of pre texts", because a planted share of exactly 0.15 gives 50% power by construction; the 15% figure is reported. C6's bar R >= 1.25 is m342_offsite's detection bar for the same reason.

## Procedure in January

1. Save the sheet unchanged in `experiments/harp_pack/raw/` (gitignored if the owner asks; never published without Kenoyer's permission). Record its sha256 in HASHES.txt.
2. Run `loader.py` alone and read only its report (header mapping, category counts). Resolve ambiguities by a hashed `column_map.json` or a sign concordance amendment, if needed. No statistic before this is frozen.
3. Run `board/run.sh .venv/bin/python -I experiments/harp_pack/score.py <sheet>` once. Report every kept test, C5, and the list of dropped tests, whatever the outcome.
4. Any positive gets an M6 red-team task. Ledger rows go to `experiments/harp_pack/ledger_rows.csv`.

## What would falsify

- C1 FAIL: jar sign not rarer on pre-firing marks -> FS1's jar half is wrong at Harappa. C2 FAIL: opener-type signs are not a pre-firing (production) vocabulary at Harappa. C3 FAIL with S non-empty: no replicable pre-firing vocabulary. C4 FAIL: no sign tracks vessel form at the planted strength. C6 FAIL: M342 is not a vessel marker (route closed, with m342_offsite). C7 FAIL: lot-level tier archive closed. C9 FAIL: numerals on sherds do not measure vessel size.
- Low power is never read as a refutation. If the real sheet is smaller than the frozen minimum n, the test is UNTESTABLE.
