# Pre-registration: tablet_archives (Fable 5.2 plan 3, R2: tablet deposits as allocation-tier archives)

Date: 2026-11-14. Written after building `experiments/tablet_archives/tablets.csv` and printing only a data audit (counts of tablets, tiers, deposits and copy-group sizes; see `build_tablets.py`). No test statistic had been computed when this was written. Scripts and this file are hash-frozen in `docs/prereg/HASHES.txt` (tag `tablet_archives`) before `t_tests.py` is run.

## Question
Do Harappa miniature tablets whose docket side reads "tall-stroke numeral (2/3/4) + M328 cup (W700)" behave like a Linear-B / Near Eastern administrative archive with allocation tiers (tier = 2/3/4)?

## What earlier work already tested (not redone here)
- m328_measure Q2: copies per identity vs N over all ICIT (rho +0.08, p = 0.19). Q3: N vs M77 locus at Harappa (p = 0.42). Secondary: N drifts with ICIT period/phase (p = 0.005; N = 4 dominates HARP Period 3).
- administration P11/t3: for one side-1 identity the side-2 tall value is not more constant than shuffled (held-out 2/7; ICIT 17/45 vs 12.5, p = 0.09). No rise of N with phase.
New here: (a) provenance at deposit level (mound | trench | HARP grid square | sub-period or Vats stratum) from the merged ICIT export, stratified by period so that the known period drift cannot drive a lot effect; (b) moulded-only multiplicity gradient with copy groups as units; (c) sign-level partition of obverse texts by tier and its transfer between mounds.

## Data and the loss of power (stated up front)
- 386 Harappa tablet objects with a pure docket side of tier 2/3/4 (TAB:B 194, TAB:I 192). Docket sites outside Harappa: ~6 objects in all ICIT, so **replication can only be within Harappa (second mound or period), not a second site.**
- **HARP lot (excavation-unit) numbers are not available.** They are printed only in the CISI 3.1 data list (pp. 423-441); the free Kenoyer & Meadow 2010 chapter (downloaded, `raw/harp_km2010`) explains the designation H<yr>-<reg>/<lot>-<item> but lists no objects. Fallback = deposit proxy. For Mound E/ET the export gives trench + sub-period but no grid, so ET "deposits" are whole trench-periods (coarse; e.g. ET Trench 11 Period 3 = the Meadow & Kenoyer 2000 dump of 22 incised copies). For Mound F the HARP grid square is often known (finer). 317 tablets have a deposit; only 24 deposits hold >= 3 tablets (189 tablets).
- 296 copy groups (type, obverse, tier); 26 groups have >= 2 copies; largest: 20 incised `W003 W861 / W003 W156` tier 4, 18 incised `W176 W740 W400` tier 3.

## Units
- Copy group = (object type, exact obverse text, tier), obverse without breaks. Damaged obverse = singleton unit.
- T1 unit = distinct (copy group, deposit) pair: copies of one group in one deposit count once.
- T2 unit = copy group with complete obverse; multiplicity = number of objects in the group.
- T3 unit = copy group with complete obverse; features = set of signs on the obverse.
- Stratum for every permutation null = object type (TAB:B / TAB:I) x period key (HARP sub-period string, or Vats stratum; missing = its own level). For copy groups, period key of the first member in file order.

## Tests (confirmatory, 5; Holm over the 5)
- **T1 lot stability.** Deposits with >= 3 units. Statistic G (likelihood-ratio chi-square) of tier x deposit. Null: tiers permuted among units within stratum (deposit sizes and type fixed), 10,000 reps. Tier-archive prediction: G larger than null (one-sided). Threshold p < 0.01. Secondary (not counted): same at trench level (mound | trench), Cramér's V.
- **T2 multiplicity gradient.** Moulded TAB:B copy groups. Statistic Spearman(tier, multiplicity); prediction negative (many low-tier copies, few high-tier). Null: tiers permuted within stratum, 10,000 reps, one-sided. Threshold p < 0.01. Secondary: TAB:I; both types; mean multiplicity and share of multi-copy groups per tier.
- **T3 obverse partition.** All copy groups with complete obverse. Statistic S = sum over signs present in >= 5 units of G(sign presence x tier). Null: tiers permuted within stratum, 10,000 reps, one-sided. Threshold p < 0.01. Secondary: leave-one-out naive-Bayes accuracy; share of recurring obverses (>= 2 objects) with one tier only.
- **T4a replication of T2** in each half: Mound F (incl. Vats Trench I/III/IV-V/VI, Granary) vs Mound E + ET. Pass = rho negative with one-sided p < 0.05 in both halves (all types pooled, since TAB:B in each half is small; stratum as above).
- **T4b replication of T3 by transfer.** For signs present in >= 3 units in both halves, mean tier per sign in F vs in E/ET; statistic Spearman across signs; null = tiers permuted within stratum within each half, 10,000 reps; pass = rho > 0 with one-sided p < 0.05.

## Decision rule
Tier archive SUPPORTED only if T2 and T3 pass (Holm-adjusted < 0.05 with raw thresholds above) AND T4a and T4b pass. If T1 also passes, the "lot-level archive" part is supported. Anything less: route CLOSED for the tier/entitlement reading at this resolution (with the stated power).

## Planted-answer power (run inside t_tests.py before the real statistics are printed)
- T1: per-deposit tier mix drawn from Dirichlet(alpha * global mix), alpha = 3 (moderate lot clustering); power = share of 200 plants reaching p < 0.01 (1,000-rep null each).
- T2: plant tiers so that groups with multiplicity >= 2 are tier 2 with prob 0.6 and tier 4 with prob 0.1 (rest as observed marginal); power as above.
- T3: plant 15 frequent signs each tied to a preferred tier; units containing a planted sign take its tier with prob 0.7; power as above.
A null result is called informative only where power >= 0.8.

## What would falsify / caveats
- A real tier system with tiers assigned per issue but batches mixed across deposits would show T2/T3 without T1; that is allowed by the rule.
- Coarse ET deposits weaken T1 (lot effect diluted). Vats strata are not HARP periods.
- Near-copy obverse families made in one batch can inflate T3; T4b (transfer across mounds) is the guard.
