# Pre-registration: grammar of the Indus number signs (Fable 5.2 plan 3, R1)

Registered 2026-11-15 in `experiments/numeral_grammar/`, BEFORE any held-out (v2) or ICIT numeral-group composition was read. SHA-256 of this file and of `models.py` / `test.py` goes into `docs/prereg/HASHES.txt` (tag `numeral_grammar`) before `test.py heldout` runs.

## What was known when this was written

- Prior results: numeral_class (12 is 17.5x as common as 9-10; 8/32 adjacent short pairs are 1+12, 3 are 12+12, pooled M77, exploratory), pair_numeral_long + redteam_pnl (fixed formulas containing a numeral), shaunmortal F5/F7 (pair orders TT12 ST9 SS32 TS17, layout matters, tall and short are two classes), context Q6 (no weight series).
- Sign inventory: values read by eye from Mahadevan's drawings and the Wells glyph sheet (`common.py`). ICIT has a three-tier sign W056 that I read as 7/7/7 = 21 short strokes (3 tokens in ICIT in total; contexts not read). So a single short group >= 13 exists in the Wells list if this reading is right.
- DEV compositions (`explore_dev.py`, `explore_dev.log`): 798 numeral groups in 1,699 dev texts; 743 single signs, 55 two-sign groups, no longer groups. Pairs: S1+S12 7 (5 from one Lothal sealing family, 2 = M10 M97 M121), T3+T3 6, T3+T2 4, S1+T1 4, T3+S7 4 (all M336 M89 M112 M194), S1+S3 4, S12+S12 2, V8+T2 2, T1+S3 2, T2+S1 2, single cases incl. S12+T2, S1+S4/S5/S7/S8, S3+S4, S4+S7, A1+S3, A3+S5.
- Dev facts that bear on the models: (i) in all 7 dev 1+12 groups the 1 comes FIRST in reading order (small before big); never 12+n with n < 12 in the short class. (ii) short-1 (M97/M98) is the first member of 22 of 55 dev pairs and the second member of only 4, while it is 10% of single numerals. (iii) dev has short pairs with sums <= 12 not involving 12 (S1+S3, S1+S4, S3+S4, S4+S7...).
- Held-out and ICIT: only group COUNTS per site were computed (heldout 267 groups, 25 multi-sign; ICIT sites outside M77: 176 groups, 14 multi-sign, Dholavira 72/5). No composition looked at.

## Unit and data (frozen)

- Distinct texts (`distinct()`), break-free runs (`runs()`). A numeral GROUP = maximal run of adjacent numeral signs from `common.py` (classes S short, T tall, V chevron, A arc, D dotted (Wells only)). The connective M99/W002 is not a numeral and breaks a group (sensitivity: count it as S2).
- M77 held-out = `dev_heldout(version=2)[1]`. ICIT replication = distinct ICIT texts from sites other than Mohenjo-daro, Harappa, Lothal, Kalibangan, Chanhu-daro (W signs via `W_NUM`).
- Replication units (4): M77 held-out Mohenjo-daro; M77 held-out Harappa; M77 held-out other sites pooled; ICIT non-M77 sites pooled.

## Models (frozen; all parameters fit on DEV only)

Every model gives P(group) = P_len(k) x Q_M(group | k). P_len is shared (cancels). Leak: Q_M(x) = (1 - e) A_M(x) + e B(x), e = 0.01, where A_M is the model's allowed-outcome distribution (zero outside its allowed set, renormalised) and B is the unrestricted baseline (independent tokens, dev token frequencies, Dirichlet alpha 0.5 over the full support of `M_NUM` + `W_NUM` (class, value) tokens). Allowed distributions are dev counts + 0.5 over the allowed cells.

- **M1 plain tally, ceiling 12.** Single signs: any token with value <= 12. Groups of k >= 2: independent tokens (dev frequency of tokens inside multi-sign groups), any order, every token <= 12.
- **M2a additive base-12, big first (as specified by the lead).** S12 is a unit. Single signs: as M1. Allowed pairs: (S12, S n) n = 1..11, and (S12, S12). Longer: S12 ... S12 then optionally one S n < 12. Everything else is a violation.
- **M2b additive base-12, small first (dev-informed order).** Same, with (S n, S12) instead of (S12, S n); longer groups: optional S n < 12 then S12s.
- **M3 base 8/16, weight-like.** Units are any token of value 8 or 16. Single signs: values <= 8 (and 16). Allowed pairs: (unit, x) with x of value 1-7, and (unit, unit). S9, S10, S12, V9 single signs are violations.
- **M4 base 10.** Unit = any token of value 10. Single signs: values <= 10. Allowed pairs: (10, x <= 9), (10, 10). S12 single signs are violations.
- **M5 ordered juxtaposition (dev-derived, the only model built after seeing dev).** Two-sign groups are two numbers side by side, with separate first-position and second-position token distributions (dev counts + 0.5 over support); single signs as M1. This encodes "short-1 is a prefix to numerals" without a hand-set rule. Longer groups: first token from the first-position distribution, the rest from the second.

## Primary test (decides R1)

T1. Held-out log10 likelihood of all held-out numeral groups (singletons + multi-sign). The 12-unit claim WINS if the better of M2a/M2b beats M1 by log10 LR >= 1 on pooled M77 held-out AND has LR > 1 in at least 3 of the 4 replication units AND beats M3 and M4 by >= 1. A tie (|log10 LR| < 1) or a loss kills it. Same rule for M3 and M4 against M1. M5 vs M1 is reported with the same margin as a dev-derived hypothesis.

T2 (scope B, 12 only). Restricted to groups that contain an S12 and have k >= 2: Q_M(group | contains S12). M1: product of M1 token probabilities restricted to groups containing S12, renormalised over two-sign groups with an S12; M2a/M2b: allowed distribution over their 12 cells (dev + 0.5) with the same leak. Reported as log10 LR; margin 1. Power is reported by simulation.

## Secondary predictions (each a yes/no on held-out + ICIT replication, pooled unless said)

- P1 (order). Among two-sign groups with exactly one S12 and a short partner: M2a predicts 12 first in >= 90%; M2b predicts small first in >= 90%; M1 predicts 50% (binomial two-sided test, alpha 0.05).
- P2 (partner set). Every partner of S12 inside a group is a short count 1-11 or another 12 (M2). A tall/chevron/arc partner is a violation.
- P3 (no big single group). No single sign with value >= 13 in held-out + all ICIT (M2 and M1 both require this). W056 (if read 21) would falsify the ceiling; its contexts are checked descriptively.
- P4 (counts next to the unit differ from stand-alone counts). Distribution of S partners of S12 vs held-out stand-alone short counts: Fisher-Freeman-Halton style permutation test, alpha 0.05; M2 predicts difference, M1 predicts none.
- P5 (additivity). Under M2, short + short pairs without 12 whose sum is <= 12 should be absent (one sign could write them). Count them in held-out; M2 predicts 0 (allowing 1 as leak).
- P6 (dev-derived, short-1 prefix). Among held-out two-sign groups containing exactly one S1, S1 is first in >= 75% (binomial vs 0.5, one-sided alpha 0.05), and S1's share among pair members exceeds its share among single numerals (Fisher one-sided alpha 0.05).

## Part 3 (exploratory on dev, single confirmatory check each on held-out)

- C1 cross-class pairs (short vs tall): order share tall-first in dev; held-out tests whether order is fixed (>= 80% one way; binomial).
- C2 unit / metrogram slot: on dev, list signs with >= 6 dev tokens whose preceding sign is a numeral in >= 50% of tokens. Held-out check: each listed sign with >= 3 held-out tokens keeps a numeral-preceded share >= 50% (pooled binomial vs the held-out base rate of numeral-preceded tokens). Also on dev: is the sign after a numeral followed by a fixed third sign (number-unit-commodity frame)? Reported descriptively.
- C3 multi-sign groups vs single numerals: do two-sign groups take the same following signs as single numerals? Descriptive.

## Multiplicity and power

Confirmatory tests: T1 (3 comparisons), T2, P1-P6, C1, C2 = 12; Bonferroni alpha 0.05/12 noted alongside raw p. Power for T1/T2/P1 by simulating held-out-sized samples from the fitted M2a/M2b (counts per unit fixed at the observed held-out group counts).
