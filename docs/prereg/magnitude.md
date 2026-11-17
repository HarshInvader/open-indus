# Pre-registration: do numerals or signs on an object track a measurable property of that object? (Fable 5.2 plan 3, R4)

Registered 2026-11-15, BEFORE any excavation report was downloaded and BEFORE any measurement was linked to any text. Work dir `experiments/magnitude/`. Looked at before writing: ICIT/M77 inscription lists for classes IMPL (23 side-records), BNGL (50), ROD (42), POT:T:* (~630), M77 bronze implement (17) and ivory/bone rod (26) texts, which give sign content but no measurements (ICIT width/height are present for a handful of implements and rods; these were seen in a listing but no correlation was computed). Prior results declared: numerals vs cubical weight series closed (context Q6); stroke count vs tablet size closed (m328_measure, rho -0.17); oval M373/W790 on bangles 6/41 (self_label lead, frozen in docs/prereg/2026-11-15_leads_predictions.md).

## Hypotheses
- H-num: on an inscribed object, the numeral value written on it rises (or falls) monotonically with a physical magnitude of that object (mass, length, capacity, inner diameter).
- H-oval: stoneware/ceramic bangles carrying the oval M373/M374 (ICIT W790) differ in inner diameter from other inscribed bangles (a size/type mark).

## Variables (frozen)
- Numeral value V of an object = sum of stroke-numeral values over all sides (M77: `stroke_signs.json` short+tall, excluding M99/M101 connective; ICIT: W001-W019, W031-W037, W055 with the mapping used in experiments/numeral_class/fit.py, tall W031-W037 = 1-7). Objects without any numeral get V = 0 and are kept (V = 0 vs >0 is part of the ranking). Secondary: number of stroke signs (count of numeral tokens) and V restricted to objects with V > 0 (reported, not decisive).
- Magnitude by class: (a) implements: mass (g) primary, length (mm) secondary; (b) pottery: capacity (litres) primary, height or rim diameter secondary; (c) bangles: inner diameter (mm); (d) rods/dice/other: length (mm).
- Firing: pottery inscription pre-firing vs post-firing, as stated in the report or ICIT type (POT:T:p = pre-firing incised? ICIT codes are ambiguous; only the report statement counts).
- Provenance: every measurement row carries source, volume, page/plate, excavation number, and how it was linked (CISI number, excavation number, or text match). Rows linked only by visual sign-match get link_grade = C and are excluded from the primary test.

## Tests
| id | class | statistic | null | pass |
|---|---|---|---|---|
| T1 | implements | Spearman(V, mass) within implement type (axe, blade, spearhead, chisel...): ranks taken within type, then pooled (type fixed effect) | V permuted within type x site, 10,000x | two-sided p <= 0.0125 |
| T2 | pottery | same with capacity, within vessel form; also the interaction: rho(pre-firing) vs rho(post-firing) (difference reported; the decision uses pre-firing if n_pre >= 8, else all) | V permuted within form x site | p <= 0.0125 |
| T3 | bangles | Spearman(V, inner diameter) within material | permuted within material x site | p <= 0.0125 |
| T3o | bangles | Mann-Whitney inner diameter, oval-bearing vs other inscribed bangles | label permutation within site | two-sided p <= 0.05 (single frozen lead) |
| T4 | rods/other | Spearman(V, length) within class | permuted within class x site | p <= 0.0125 |

Bonferroni over T1-T4 (0.05/4). Linked n per class must be >= 8 objects with a measurement for the test to run; otherwise the class is UNTESTABLE and only the linked table is delivered.

## Decision rule
- SUPPORTED (numeral class = unit of that magnitude): a class passes at p <= 0.0125 AND the same direction holds at a second site with one-sided p <= 0.05 (n >= 5 there).
- REFUTED for a class: n >= 15 and power >= 0.8 for |rho| = 0.5 (simulated at the observed n and tie structure) and p > 0.0125.
- Otherwise INCONCLUSIVE (underpowered). If all testable classes are refuted, "numerals measure the bearer" is closed for those classes.
- Power is reported for every test: P(p <= 0.0125) under a planted monotone relation with rho = 0.5 at the observed V distribution and n.

## Things fixed in advance
- No re-coding of V after linking. No exclusion of outliers. Broken objects: magnitude used only if the report gives a complete measurement; otherwise excluded (and listed).
- Any amendment is logged here with a timestamp before it is run.

## Amendment A1 (2026-11-15T02:37:34Z)
Code bug found after the first run of run.py: T4 stratified rods by a free-text type label (round rod (bone) / round rod (ivory) / rod (ivory)), not by class as registered ("within class; permuted within class x site"). This split the two hand-entered Mohenjo-daro rods into singleton strata. Fixed to stratum = class. First-run values (reported for transparency): rho_fe -0.175, p 0.66; MD-only rho 0.0 (degenerate). Nothing else changed.
