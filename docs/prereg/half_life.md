# Pre-registration: stratigraphic half-life of sign classes (Fable plan 2, item 9)

Agent: half_life. Written 2026-11-15, BEFORE any statistic comparing sign classes over time was computed. Facts known at registration time: dataset sizes per period and object type, and the number of signs with n >= 5 per role class per dataset (`experiments/half_life/h0_describe.log` and an inline count). Earlier project results known: context Q5 (no sign innovation survives BH across HARP/MD/DHO/KAL; best W690 earlier, q=0.20), shaunmortal F9/F17 (no drift MD Intermediate vs Late, HARP 3B vs 3C), m328_measure (tall-stroke value before M328 shifts by HARP period, N=4 dominates Period 3/3B; p=0.005).

## Question
Do name-core signs turn over faster across strata than frame signs (opener, connective, title element, closer, post-closer clitic)? Name-core model prediction: cores behave like PERSONS (period-bound), frame signs like OFFICES (persist). The reverse (frame signs more period-bound than cores) damages the model.

## Data (frozen in `hl_lib.py`)
Unit = distinct (dataset, period, sequence); mould copies within a period count once.
- **HAR** (ICIT, HARP excavations): 3B (+3B?) < 3B/C < 3C. 485 units, 92% tablets in 3B/3B-C.
- **MD** (ICIT): Early < Intermediate < Late (period level only). 758 units.
- **DHO** (ICIT): stage 4 < 5 < 6. 112 units. **KAL** (ICIT): period II Early+Middle < Late. 101 units. **LOT** (ICIT): Rao phase II < III < IV. 83 units.
- **HAR_VATS** (M77 Harappa, Vats 1920-34 excavations, independent of HARP): depth (level) ranked within locus (loci with >= 15 objects and >= 3 depth values), tertiles, deepest = oldest. 520 units.
- **MD_M77** (M77 Mohenjo-daro, same tertile rule): SECONDARY only; same objects as MD.
- ICIT signs mapped to Mahadevan via `bridge_WM.json` (first M); unbridged signs stay W and get no role.
- Roles: top-weight role in `experiments/functional_reading/lexicon.csv`. FRAME = OPENER, CONNECTIVE, CLOSER, TITLE ELEMENT, POST-CLOSER CLITIC, BRACKETED-FISH CLOSER. CORE = NOUN, FISH-CLASS NOUN. NUM = numerals + unit (reported separately, not in the core/frame contrast).

## Measures
- **Per-sign drift D** (sign-level turnover): G statistic of the sign's per-period count of units vs expectation from period sizes within object type; D = (G_obs - mean G_null) / n, null = period labels permuted within object type (1,000 perms). E[D] = 0 under no time structure for every n, so D is a frequency-neutral effect size. Signs with n >= 5 units in the dataset.
- **Persistence deficit** (survival measure): rarefy each period to the smallest period size of that dataset (200 reps); for each class, the share of signs present in period t that recur in t+1, minus the same share under the type-stratified period permutation. Negative = faster turnover than sampling explains. Bootstrap CIs (units resampled within period, 200).
- **String level** (persons vs offices proper; a person is a core STRING, not a word sign): maximal runs of CORE-class signs ("core strings") vs maximal runs of FRAME-class signs ("frame strings") within each text; same D statistic per string with n >= 3 units.

## Tests
- **P1 (primary, sign level).** S1 = mean D(CORE) - mean D(FRAME), pooled over sign x dataset pairs in HAR, MD, DHO, KAL, LOT, HAR_VATS. Null: within dataset, CORE/FRAME labels shuffled among signs within frequency quintiles (n bins), 10,000 shuffles. One-sided for S1 > 0.
- **P2 (primary, string level).** S2 = same contrast for core strings vs frame strings (n >= 3), same null (quintiles of string frequency).
- Holm over P1, P2. **Supported** if Holm p < 0.05 for P1 or P2 and neither is reversed at two-sided p < 0.05. **Damaging (reverse)** if S1 or S2 < 0 with two-sided p < 0.05. Otherwise **inconclusive**; if planted power (below) < 0.8 the verdict is "inconclusive, underpowered".
- **P3 (relative chronology exists).** Per sign, time shift = mean relative period (0..1) of its units minus the type-stratified expectation. Spearman correlation of shifts between independent dataset pairs with >= 10 shared signs (n >= 5 in both): HAR vs HAR_VATS, HAR vs MD, HAR_VATS vs MD, and pooled (Fisher z mean). Null: shift recomputed under period permutation within type in each dataset (2,000). Supported if pooled one-sided p < 0.05. Not counted toward P1/P2 Holm.
- **P4 (period-restricted signs).** For each sign with n >= 5 in a dataset: exact permutation p (5,000) of the drift G; BH within the whole P4 family (all datasets). Report signs with q < 0.10 and whether direction replicates in another dataset. "Datable innovation" = q < 0.05 and same-direction shift in an independent dataset.
- **Power (planted).** Swap model: a fraction f of CORE signs is made period-bound by exchanging, with probability m, each occurrence outside a random home period with a random token (non-planted sign) from a unit of the same object type in the home period (frequencies preserved). Report detection rate of P1 at alpha 0.05 for (f, m) in {(0.5, 0.5), (1.0, 0.5), (0.5, 1.0)}, 100 reps each. For P4, report the n at which a fully period-restricted sign reaches q < 0.05.

## Sensitivity (reported, not decisive)
Seals only; MD_M77 in place of MD; HAR 3B vs 3C only (drop 3B/C); D with n >= 10.

## Falsifiers
Name-core model damaged: frame signs/strings drift more than frequency-matched core signs/strings (reverse at p < 0.05). Name-core model supported: core strings period-bound beyond frequency-matched frame strings.
