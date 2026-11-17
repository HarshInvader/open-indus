# Harappa tablet deposits as allocation-tier archives (Fable 5.2 plan 3, R2)

Pre-registration: `docs/prereg/tablet_archives.md`. It was hash-frozen together with `build_tablets.py`, `t_tests.py` and `tablets.csv` (`docs/prereg/HASHES.txt`, tag `tablet_archives`) before any test statistic was computed. Ledger rows `ta_t1`..`ta_t4b` are in `docs/test_ledger.csv`.

Run from the repo root:
- `.venv/bin/python -I experiments/tablet_archives/build_tablets.py`
- `.venv/bin/python -I experiments/tablet_archives/t_tests.py`

Output: `tablets.csv`, `t_tests.log`, `results.json`.

## Findings first

**The tablets do not behave like a tier archive. 0 of 5 pre-registered tests pass, so the route is closed.** The docket "2, 3 or 4 tall strokes + cup (M328)" is not tied to a deposit or to how many copies were made, and the obverse texts do not split by it. Two of the three main tests had high power. The multiplicity test had low power, but its result points the wrong way.

1. **Deposits are not uniform in tier.** Within object type × period, the tier mix does not vary between deposits more than chance: G = 42.8 over 22 deposits and 153 units, p = 0.83. The test had power 0.98 against moderate lot clustering. At trench level p = 0.18. The two mounds do differ in raw counts: Mound F leans to tier 3 (75 of 152) and Mound E/ET to tier 4 (73 of 131). That fits the period drift already reported by m328_measure. It disappears once period and type are held fixed.
2. **There is no inverse gradient between tier and number of copies.**
   - Moulded copy groups: Spearman rho = +0.057, one-sided p = 0.64 (138 groups). The sign is wrong for the hypothesis.
   - Mean copies per group by tier: tier 2 1.16, tier 3 1.12, tier 4 1.24.
   - Incised groups also go the wrong way, with the most copies at tier 4: means 1.17 / 1.72 / 2.05, rho = +0.09.
   - Power was only 0.42, because only about 12% of groups have more than one copy. So this null alone is not decisive, but the direction is opposite to the prediction in every cut.
3. **The obverse texts do not split by tier.**
   - Sign × tier association over 46 signs: S = 101.0, p = 0.75 (237 copy groups), with power 0.96.
   - A leave-one-out naive-Bayes classifier predicts tier from the obverse signs at 0.26, below its permutation null of 0.35 and below the majority-class rate of 0.41.
   - 26 of the 209 distinct obverse texts occur with two or three different tiers. For example, incised W176 W740 W400 appears 30 times, with tiers 2, 3 and 4.
4. **No replication in the second mound.**
   - The multiplicity gradient is wrong-signed in both halves: rho F +0.03, rho E/ET +0.26.
   - Per-sign mean tiers in Mound F do not predict those in Mound E/ET: rho = −0.37 over 17 shared signs, p = 0.91.
   - A second site is not possible: the docket formula is a Harappa phenomenon, with about 6 objects elsewhere in all of ICIT.

**Reading.** The 2/3/4 docket acts like a formula variant whose share drifts by period and mound. It does not behave like a grade or entitlement linked to a name, a deposit or a production run. This adds to m328_measure (not a measure) and administration P11 (not fixed per identity).

## Provenience and loss of power (stated early, as the prereg requires)

- **HARP lot numbers are not available.**
  - They appear only in the CISI 3.1 data list (pp. 423-441), which we could not obtain.
  - The free Kenoyer & Meadow 2010 chapter (`raw/harp_km2010/k.pdf`, from the Wayback snapshot of harappa.com, 2022-07-23) explains the designation H‹yr›-‹reg›/‹lot›-‹item›, but it lists no objects. harappa.com itself is behind a Cloudflare block.
  - ICIT ids and CISI numbers do not encode lot numbers.
- **Fallback deposit proxy.** A deposit is mound | trench | grid square | HARP sub-period (or Vats stratum), taken from the merged ICIT export (`area-section`, `room-grid`, `time`). ICIT rows align with it 2,507 of 2,528 times.
  - Mound F often has HARP grid squares, which gives fine deposits.
  - E/ET has no grid, so a deposit there is a whole trench-period. This is coarse, and it dilutes any lot effect. For example, "ET Trench 11, Period 3" is the Meadow & Kenoyer 2000 dump of 22 incised copies.
- **Coverage.**
  - 386 docket tablets (194 moulded, 192 incised); 317 have a deposit.
  - Only 22 deposits hold 3 or more units, 153 units in all.
  - 296 copy groups; just 26 of them have 2 or more copies.
- The deposit tests still reached power 0.98 against planted Dirichlet(3) clustering. The loss mainly hurts the multiplicity test (power 0.42).

## Pre-registered tests

| id | hypothesis | observed | null | p (Holm) | power | verdict |
|---|---|---|---|---|---|---|
| T1 | tier mix differs between deposits (within type × period) | G = 42.8, 22 deposits | permute tiers within type × period | 0.83 (1) | 0.98 | refuted |
| T2 | moulded copies scale inversely with tier | rho = +0.057 | same | 0.64 (1) | 0.42 | not supported (wrong sign; low power) |
| T3 | obverse sign set partitions by tier | S = 101.0, 46 signs | same | 0.75 (1) | 0.96 | refuted |
| T4a | T2 gradient replicates in F and E/ET | +0.03 / +0.26 | same, per half | 0.99 (1) | - | refuted |
| T4b | sign mean-tier transfers F → E/ET | rho = −0.37, 17 signs | permute within half × type × period | 0.91 (1) | - | refuted |

Decision rule (prereg): support needs T2 + T3 + T4a + T4b. None pass, so the route is **closed**.

Secondary results (not counted):
- Unstratified deposit test: p = 0.80.
- Cramér's V: in `results.json`.
- Recurring obverse texts with a single tier: 21 of 47, against a null of 11.8. This uses objects as units, so mould copies inflate it; it is descriptive only and matches F39 / administration P11.

## Caveats

- Copy groups are defined by an identical transcribed text. True mould identity needs the photos, so different moulds with the same text count as one group. Kenoyer & Meadow note that numeral dockets were often made from different moulds.
- Vats strata are not HARP periods. The stratification treats them as separate levels.
- Damaged obverses (59 groups) enter T1 only.
- Inline dockets, where tall strokes + W700 come at the end of a longer side (for example W413 W575 W335 W711 W033 W700, 10 objects), were excluded by the prereg.

## Next experiments

1. If the CISI 3.1 data list (lot numbers per H-number) becomes available, re-run T1 at true lot level. This is the only finer cut left, and the planted-power estimate says even modest lot clustering would show.
2. Treat the docket tier as a period/mound marker in seriation (R6), not as a semantic grade.
3. Mould identity from photographs (CISI 3.1 plates) would let T2 count real production runs.
