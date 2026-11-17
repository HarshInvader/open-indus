# Direction, time and animal (Fable plan 6, tests 2, 3, 4)

2026-11-15. Pre-registered in `docs/prereg/direction_time_animal.md`. The prereg and the code (`dta_lib.py`, `e2_gate.py`, `e3_time.py`, `e4_animal.py`) were hashed into `docs/prereg/HASHES.txt` (tag direction_time_animal) before any outcome was computed. Before hashing, only counts and a smoke test on shuffled labels had been seen. Ledger rows `dta_*` are in `docs/test_ledger.csv` (family of 6 decisions plus 1 descriptive row). Units are distinct texts throughout. ICIT signs are mapped to Mahadevan numbers through `bridge_WM.json`.

Run from `experiments/direction_time_animal/` with `../../.venv/bin/python`: `e2_gate.py`, `e3_time.py` (and `--raw` for raw Wells ids), `e4_animal.py`. `e3x_power_strong.py` is exploratory and was run after the frozen run.

## Findings first

1. **E2 (reversed texts as a functional class): DROPPED at the gate.** Neither corpus records *how* an editor fixed a text's direction. So no L-R text has a direction known to be independent of slot signs (strict count G1 = 0). The generous proxy keeps texts an editor could not have oriented from the jar, a slot-marked first or last sign, or a copy of an R-L text. It leaves **31 distinct texts**: M77 13 of 150 L-R lines, ICIT 18 of 151 L-R texts. The bar was 100. No clustering statistic was computed.
   - Most L-R texts (about 88%) carry an orientation cue an editor could have used, so a clustering test on them would partly test the editors.
   - What it would take: physical direction coding (stroke overlap, line-end crowding) from CISI photographs for about 100 or more L-R texts.
2. **E3 (which slot carries the time signal): INCONCLUSIVE. Openers do not turn over more than closers, and seal texts show no overall early/late signal at all.**
   - The gate passed: 1,109 period-labelled seal units, 690 analysed texts of 3 or more signs. These are MD Early+Intermediate vs Late, and Harappa (Vats strata IV-VII vs I-III; HARP 3B vs 3C). Smaller strata come from Dholavira, Lothal and Kalibangan.
   - Frequency-matched drift, opener minus closer: **S_oc = -0.098 (95% bootstrap CI -0.157 to +0.157), one-sided p = 0.46.** The sign is opposite to the prediction.
   - Mean drift by slot: opener -0.009, medial +0.041, closer +0.087, so the closer is nominally the *most* time-variable slot.
   - S_om = -0.064 (p = 0.66) and S_mc = -0.040 (p = 0.35).
   - Global excess of time structure over all slot-signs: G 25.9 vs null 6.1, **p = 0.21**. On seals at these period resolutions, there is no detectable time signal to place in any slot.
   - By site:
     - MD (446 texts): opener -0.027, medial +0.016, closer -0.056; S_oc +0.05.
     - Harappa Vats (141 texts): the closer positive is driven by 6 closer signs.
   - Power. The frozen plant grid moves at most half of a chosen sign's out-of-period opener tokens (f ≤ 0.5). It turned out to barely shift opener drift: mean planted S_oc stayed negative, and **power was 0.00 in all four cells**. By the frozen rule that makes the verdict INCONCLUSIVE, not REFUTED.
   - The exploratory strong plant confines half of the opener types (n ≥ 5) to one period wherever swaps allow. It gives S_oc +0.34 and **power 1.0 (30/30)**. So strong, period-bound opener turnover is excluded. Mild turnover is not.
   - Raw Wells ids (no variant merging) give the same picture: S_oc -0.088, p = 0.46; global p = 0.10.
3. **E4 (text-only seals vs animal seals): no compensating sign class. Text-only seals are slightly longer at equal area, but the mix of sign roles is the same.**
   - The gate passed: 292 distinct text-only seals with face area (238 round, 45 square, 9 other) vs 1,108 iconic seals.
   - **O1 length (descriptive):** at matched site, period and area quintile, text-only seals carry **+0.81 signs** (permutation p = 0.0005; 260 vs 1,073 texts). Raw means are equal (4.75 vs 4.73) because text-only seals are smaller. As fixed in advance, this is ambiguous: at equal area, a seal without an animal has more room for signs. It fits space, not compensation.
   - **O2 role mix beyond length (primary):** strata are site × period × area × length, 216 text-only vs 742 iconic texts in 102 strata. T = 13.8, **p = 0.10** (Holm 0.17).
     - Largest shift: numeral share +2.7 points on text-only seals (z +2.0).
     - Second: unbridged signs +2.7 points (z +1.5).
     - Closers and connectives are slightly rarer (z -1.5 each).
     - The opener share is identical (z -0.15).
   - **O3 held-out sites:** a sign-bag classifier trained on MD and tested on other sites, and the reverse, gives AUC **0.569** vs a null of 0.522 (95th percentile 0.575), **p = 0.085** (Holm 0.17).
   - **Planted 10% compensating class:**
     - New closer class: O2 power 0.85, O3 power 0.98.
     - Extra opener sign: O2 power 0.50, O3 power 0.72.
   - **Verdict (frozen rule): REFUTED for a closer-type compensating class at 10% prevalence.** An added opener-type sign at 10% is *not* excluded (power below 0.8). The marginal numeral excess (p 0.10, z 2.0) is a lead, not a finding.

## What E3 adds to half_life (reconciliation)

half_life compared lexicon *roles* (core nouns vs frame signs) pooled over positions and object types, at Harappa (mostly tablets) and MD. Its result was S = -0.034, p = 0.75: equal turnover. One way that null could hide a real split is cancellation inside "frame": frame pools openers, connectives and closers, so opener turnover and closer stability could cancel. E3 removes that escape. It tests *positions*, on *seals only*, with site and seal shape held fixed and frequencies matched. The answer is the same: the opener is not the changing slot (it is nominally the least changing), and strong opener turnover is excluded (exploratory power 1.0).

What is new:
- (a) The positional version of the turnover hypothesis is now tested directly, and it fails.
- (b) On seals alone, there is no detectable global early/late signal (p = 0.21). The chronology in redteam_chrono lived mainly in Harappa tablets and text families. The MD early-vs-late AUC of 0.61 (site_signal) did not come from slot-specific turnover here.
- (c) A planted-power reading says what is excluded: confining half the opener types to one period would be seen.

Exploratory: role-level drift on seals is largest for opener-role signs (mean D +0.135, n = 10) and clitics (+0.144, n = 6). Opener-role signs occurring *outside* the first position contribute to this (e.g. M267 as a closer, D +0.82, n = 6). Not tested; too few signs.

## Hypotheses

| id | hypothesis | result | verdict |
|---|---|---|---|
| E2 | L-R texts with independently fixed direction cluster by type, material, iconography or site | 31 qualifying texts vs 100 needed; 0 with a recorded criterion | **dropped (gate)** |
| E3 | opener turnover > closer turnover on seals (frequency-matched) | S_oc -0.098 (CI -0.16 to 0.16), p 0.46; frozen power 0.00; strong-plant power 1.0 (exploratory) | **inconclusive** (strong opener turnover excluded, exploratory) |
| E3b | medial or closer slot carries the time signal | S_mc -0.04, p 0.35; global time signal p 0.21 | not supported |
| E4-O1 | text-only seals longer at equal area and period | +0.81 signs, p 0.0005 | descriptive: space, not compensation |
| E4-O2 | different role mix beyond length | p 0.10 (Holm 0.17); numeral +2.7 points | null |
| E4-O3 | sign bag separates text-only from iconic on held-out sites | AUC 0.57 vs 0.52, p 0.085 (Holm 0.17) | null |
| E4 | compensating class of about 10% | power 0.85-0.98 for a closer class, 0.50-0.72 for an opener sign | **refuted for a closer-type class; opener-type not excluded** |

## Sensitivity

- E3 with raw Wells ids (no bridge, no variant merging): same picture.
  - S_oc -0.088 (CI -0.151 to 0.150), p = 0.46. S_om p = 0.65, S_mc p = 0.35.
  - Mean D: opener +0.016, medial +0.046, closer +0.092.
  - Global time signal p = 0.10.
  - Frozen power 0.00 in all cells. INCONCLUSIVE.

## Honest limits and deviations

- E3: the pre-registered plant grid was too weak to move the statistic, so the frozen power is uninformative. The strong-plant power is exploratory, added after the frozen run (`e3x_power_strong.py`, not hashed).
- E3: the bootstrap resamples texts, but the period-permutation null is recomputed on each resample. Duplicated texts are permuted separately in the null and kept together in the observed data, which biases resampled drift upward in thin slots. The CI is therefore wide and conservative, not centred on the point estimate. The closer slot has only 18 signs with n ≥ 5, so every slot contrast is thin.
- E3 periods are coarse (centuries). Vats strata are a within-Harappa depth order, not phases.
- E4: text-only seals are 82% round seals, iconic seals almost all square. Matching on area, site and period does not remove shape, which is itself a period and register marker. Any O2/O3 lead would need a square-only re-test, but only 45 square text-only seals exist.
- E2: the generous count is an upper bound for "independent". A text with no cue could still have been oriented from the photograph's sign shapes, which is the independent criterion we want. But we cannot tell which texts were.

## Next

1. E2 needs physical direction coding from photographs (stroke overlap, line-end crowding) for at least 100 L-R texts: a rater task on CISI crops (vol. 1-2 are in hand, but at about 100 ppi).
2. E4 numeral lead: re-test numeral share on text-only vs iconic seals in fresh data (CISI 3, new finds) and on square seals only. Freeze it as a prediction rather than re-test it on the same texts.
3. E3: no further slot-chronology work on seals is useful without finer stratigraphy (HARP lots, MD sub-phases with a known direction).
