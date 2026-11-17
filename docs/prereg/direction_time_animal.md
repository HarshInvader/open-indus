# Pre-registration: direction_time_animal (Fable plan 6, tests 2, 3, 4 = E2, E3, E4)

Registered 2026-11-15 in `experiments/direction_time_animal/`. This file and the code (`dta_lib.py`, `e2_gate.py`, `e3_time.py`, `e4_animal.py`) are hashed into `docs/prereg/HASHES.txt` (tag direction_time_animal) BEFORE any outcome statistic is computed.

## Disclosure: what was already seen
Only counts (no outcome statistic):
- ICIT direction labels: R/L 4,266, L/R 215, NR 386, '-' 776, other 36. L/R by type: tablets 135, seals 49, pottery 24, other 7. M77 lines: left-to-right 235 (miniature tablet 87, seal 69, sealing 61, pottery 10, copper 6, other 2); 'symmetrical' 7, 'doubtful' 12. Neither corpus records WHICH criterion fixed a direction.
- Period-labelled ICIT seal units (distinct site x period x sequence, half_life period mapping): 874 (MD 660: Early 36, Intermediate 339, Late 285; Dholavira 85; Lothal 55; Kalibangan 41; Harappa HARP 33). Harappa seals also carry Vats stratum labels I-VII (about 250). Complete seal texts of 3+ signs among the 874: 524.
- Seals with face area: text-only (symbol None) SEAL:S 67, SEAL:R 295, SEAL 10; iconic SEAL:S 1,404. Text-only seals by site: MD 250, Harappa 107, Dholavira 37, Lothal 35, other ~20. Area quantiles text-only median ~400 mm2 vs animal ~660 mm2 (overlap large).
- Prior results that shape the design: half_life (core vs frame turnover equal, S=-0.034, p=0.75), redteam_chrono (chronology weakened to text families), site_signal (MD early vs late AUC 0.61), slot_novelty (opener and medial open, closer closed), rank_ladder/redteam_rank (no-animal seals ~31% smaller), space_and_sealing (length +1.05 signs per area doubling).

## E2: minority-direction texts as a functional class

**Gate (decides whether E2 runs at all).** E2 may only use minority-direction (L-R) texts whose direction was fixed by a criterion independent of slot signs (sign asymmetry, line-end crowding, seal vs impression). Count:
- G1 strict: L-R texts with a recorded non-sequence criterion. Expected 0 (no such field exists in ICIT or M77; CISI photographs are not in the repo).
- G2 generous proxy (upper bound): distinct L-R texts (ICIT L/R or M77 left-to-right, union by object) that an editor could NOT have oriented from slot signs or copies: no jar (M342 / Wells W740 and its bridge equivalents), first and last sign (in reading order) not slot-marked, and the sequence (or its reverse) not attested as an R-L text. Slot-marked sign = seen >= 10 times in R-L texts of its corpus with initial rate >= 0.4 or final rate >= 0.4. Texts of 1 sign excluded (no direction).
- G3 cross-editor: L-R in BOTH M77 and ICIT for the same object (reported only; two editors agreeing does not make the criterion independent).
- **Rule:** if G2 < 100, E2 is DROPPED and reported as such; no clustering statistic is computed. If G2 >= 100, run on G2 texts: Fisher/chi-square of L-R share by object type, material, iconography (symbol None vs iconic, seals only) and site, each against R-L texts of the same corpus, Holm over 4; support = clustering with non-seal types/materials (p_Holm < 0.05); refute = no clustering with power >= 0.8 for a 2x odds ratio.

## E3: which slot carries the time signal

**Gate:** >= 800 period-labelled seal texts (all lengths). If met, run and report power from planted turnover; if not, report power only.

Data: ICIT seals (`type` starts with SEAL; cylinder SEAL:CY and round SEAL:C excluded), distinct (stratum, period, sequence) units. Analysed texts: no '#' break, line breaks dropped, >= 3 signs. Signs mapped to Mahadevan through `bridge_WM.json` (variants merged; unbridged keep W id); sensitivity: raw Wells ids.
Strata (site and type fixed): dataset x seal shape (SEAL:S, SEAL:R, SEAL). Binary periods fixed in advance:
- MD: Early + Intermediate = early, Late = late.
- HAR_VATS (Harappa, ICIT phase 'Stratum I-VII'; Stratum I = top = latest): IV-VII early, I-III late.
- HAR_HARP: 3B, 3B/C early, 3C late.
- DHO: stage 4 early, 5-6 late. LOT: II-III early, IV late. KAL: II early+middle early, late late.
Slots: opener = first sign, closer = last sign, medial = every interior sign.

Statistic. For each (slot, sign) with n >= 5 tokens in that slot: G = 2 sum O ln(O/E) over stratum x period cells, E = the sign's stratum count x the slot's period share within stratum. Drift D = (G - E0[G]) / n, E0 from 200 permutations of period labels among texts within stratum (whole texts move, so slots stay linked). D has mean 0 at every frequency under no time signal. Frequency matching: bins of slot-token count n in [5,9], [10,19], [20,49], [50+]; S_ab = sum_bins w_b (mean D_a - mean D_b) / sum w_b with w_b = min(#units of a, #units of b in bin); bins missing either slot dropped.
- PRIMARY S_oc = opener minus closer. Also S_om (opener - medial), S_mc (medial - closer).
- Uncertainty: 1,000 bootstrap resamples of texts within stratum x period (period labels travel with texts), D recomputed each time with 50 null permutations; percentile 95% CI; one-sided bootstrap p = share of resamples <= 0.
- Global time check: sum over all slot-signs of (G - E0G) vs the period-permutation null (one-sided p).
- Planted power (MD + all strata, observed texts): choose a fraction q of opener sign types (n >= 5) and give each a random home period; swap a fraction f of its opener tokens in non-home texts with opener tokens of unselected signs in home-period texts (frequencies preserved). Power = share of 100 plants with S_oc bootstrap p < 0.05 (bootstrap 200 in power runs). Grid: (q,f) = (0.3,0.5), (0.5,0.5), (0.5,0.3), (1.0,0.3).

Decisions:
- SUPPORTED (openers turn over, closers stable): S_oc > 0 with one-sided p < 0.05 AND opener has the highest mean D among the three slots.
- REFUTED-MEDIAL: medial highest with S_mc p < 0.05 and S_om <= 0.
- REFUTED-EQUAL: S_oc p >= 0.05 and power >= 0.8 at (q,f) = (0.5,0.5) -> opener turnover of that strength excluded.
- Otherwise INCONCLUSIVE.
Reconciliation with half_life (fixed in advance): half_life compared lexicon ROLES pooled over positions and object types (core vs frame). Frame pools openers with closers and connectives, so opener turnover and closer stability could cancel inside 'frame'. E3 tests POSITIONS on seals only. Exploratory: the same D split by lexicon role (OPENER vs CLOSER role signs, in any position).

## E4: text-only seals, matched on area and period

**Gate:** >= 100 text-only seals with face area (expected ~370). Distinct sequences within each group (text-only, iconic).
Data: ICIT SEAL:S, SEAL:R, SEAL with width_mm x height_mm > 0, no '#'. Text-only = symbol 'None'; iconic = symbol not in ('None', '-'). Signs mapped to M as in E3. Roles: top-weight role in `functional_reading/lexicon.csv` merged to OPENER, CONNECTIVE, NUMERAL (short, tall, unit), NOUN (noun, fish-class noun), TITLE ELEMENT, CLOSER (closer, bracketed-fish closer), CLITIC (post-closer), UNK (unbridged / not in lexicon).
Matching strata: site group (MD, Harappa, Dholavira, Lothal, other) x period (binary as in E3, or 'unknown') x area bin (5 bins at quintiles of text-only area). Only strata containing both groups are used.
- O1 length: stratified (weights = harmonic mean of group counts) mean sign count, text-only minus iconic; permutation of labels within strata (2,000). Fixed interpretation: a positive O1 alone is AMBIGUOUS (the animal takes face space, so text-only seals have more room at equal area); it is not support.
- O2 PRIMARY composition beyond length: strata additionally x length (2, 3, 4, 5, 6+). Per role r, stratified difference in token share; z_r from 2,000 within-strata label permutations; T = sum z_r^2, p = permutation share >= observed.
- O3 held-out sites: L2 logistic regression (C=1) on sign bag-of-words, trained on MD, tested on non-MD, and the reverse; mean AUC. Null: labels permuted within O2 strata (both folds), 200 permutations.
- Planted control: (a) prepend an OPENER-role sign (drawn by its frequency on iconic seals) to a random 10% of text-only texts; (b) append a novel pseudo-sign as closer to 10%. Strata recomputed after planting. Power = share of 100 plants with p < 0.05 for O2 and for O3 (O3 with 100 null permutations in power runs).
Decisions (Holm over O2, O3):
- SUPPORTED: O2 or O3 Holm p < 0.05, with a role/sign more common on text-only seals.
- REFUTED (no compensating class of ~10% prevalence): both null and power >= 0.8 for plant (a) or (b) in the test concerned.
- Otherwise INCONCLUSIVE. O1 reported as descriptive.
Distinct from the closed emblem x name split: that asked whether the animal pairs with part of the text; E4 asks whether the text changes when the animal is absent.

## Ledger
Rows `dta_*` in `docs/test_ledger.csv`: E2 gate, E3 S_oc (primary) + S_om/S_mc, E4 O1, O2, O3.
