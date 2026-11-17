# reg_chrono: does sign use change with decimal depth inside one site?

Pre-registered in `docs/prereg/reg_chrono.md`. The prereg, `rlib.py` and `r1_main.py` were hashed into `docs/prereg/HASHES.txt` (tag reg_chrono) before any statistic on real depths was computed. Ledger rows `rc_*` are in `docs/test_ledger.csv`. Units are distinct texts: one per text family per excavation area.

## Findings first

1. **Overall sign use changes with depth only weakly. The result is borderline, so INCONCLUSIVE under the frozen rule.**
   - At Harappa (Vats 1940), the omnibus test over 64 signs gives sum z² = 88.8 against a null mean of 64. That is p = 0.029, but Holm over the 2 sites gives 0.057, which misses the bar.
   - At Mohenjo-daro (Mackay 1938), the same test over 72 signs gives 89.9 against 72, p = 0.087.
   - No single sign passes BH across the 136 sign tests. The best is M112 (short numeral 7) at Mohenjo-daro, which runs later: z = 3.3, n = 10, q = 0.054. It goes the same way at Harappa (z = 1.8).
   - Power: a world where 20% of signs shift with an odds ratio of about 2 between deep and shallow levels is caught 92-94% of the time. That much change at both sites would have stood out more clearly than this. So **broad, strong change is excluded, and only a weak change is hinted.**
2. **The change is not shared between the two cities.**
   - Per-sign trends at Mohenjo-daro and Harappa do not agree: rho = 0.13 over 53 shared signs, p = 0.19.
   - half_life's Harappa markers, applied to Mohenjo-daro depth, point the wrong way: late signs M127, M387, M197, M341, M72, M293 vs early signs M12, M375, M205, M347 give p = 0.83.
   - The Mohenjo-daro hint disappears when Mackay's blocks are used as strata (p = 0.64).
   - The Harappa hint sits entirely in seals (seals only p = 0.006; tablets and sealings p = 0.42).
3. **Openers vs closers: the closer slot shows turnover between deep and shallow halves, but the test cannot see opener turnover, so the comparison is INCONCLUSIVE.**
   - Closer G exceeds its null at both sites: Mohenjo-daro p = 0.041, Harappa p = 0.011.
   - The opener does not: p = 0.21 and 0.052.
   - The difference is not significant: D = z_open − z_close = −0.94 (p = 0.50) at Mohenjo-daro and −0.74 (p = 0.60) at Harappa.
   - The planted-turnover check exposes a design flaw. Opener plants are detected 0-10% of the time, because there are 127-168 sparse opener types. Closer plants are detected 25-95% of the time. So "openers turn over less" **cannot** be claimed. Only "closers show some drift" is a lead.
4. **None of the known markers shifts significantly with depth (all Holm ≥ 0.06).**
   - **M162 count frame:** earlier (deeper) at Harappa, shift −0.14, n = 23, p = 0.008, Holm 0.062. Exploratory: this comes only from seals (n = 15, p = 0.0009). It is not seen at Mohenjo-daro (n = 48, p = 0.64).
   - **Jar M342:** flat at both sites (Mohenjo-daro p = 0.51, n = 224; Harappa p = 0.38). At Mohenjo-daro a shift of odds ratio 2 is excluded (power 0.92). At Harappa power is 0.79.
   - **Connective M99:** flat (p = 0.99 and 0.18; power 0.72 and 0.36).
   - **Ticked fish:** no power (n = 21 and 5; power ≤ 0.07). Untested in practice.
5. **Exploratory: texts get slightly longer in shallower levels at both sites.**
   - Mohenjo-daro r = 0.072 (z = 1.66); Harappa r = 0.094 (z = 2.07).
   - Combined by Stouffer, z = 2.64, p = 0.008. This combination is post hoc.
   - No role class (opener, numeral, closer, etc.) changes its share (all q ≥ 0.35).
   - At Harappa the connective share leans earlier (p = 0.017, q = 0.35).

**Bottom line for the README line "no change in sign use over time".** It should read "no *detectable* change in which slot classes or markers are used; at most a weak, site-specific drift in individual signs, mainly on Harappa seals". This agrees with redteam_chrono (a weak Harappa-only ordering, no carry-over to Mohenjo-daro) and E3 (no global time signal on seals). Decimal depth did not uncover a hidden chronology.

## Data
- **Mohenjo-daro:** Mackay 1938 FEM, 635 objects with usable depth. That is 508 register decimal depths, 121 filled from the M77 integer level and 6 overridden by M77 where the two differ by more than 1.5 ft (OCR misreads). This gives 514 family units in M77 loci 31 (402) and 32 (112). Almost all are seals.
  - The OCR drops many minus signs. Mackay sorted serials 1-686 by depth, so those depths are forced below datum. Cleaned depth vs serial: Spearman −0.998.
- **Harappa:** Vats 1940 EH, 541 objects. This gives 447 family units in 8 sub-areas (M77 loci 40-47, 53): 217 seals, 131 tablets, 98 sealings. Depth is below the local surface.
- Sites are never pooled. Depth is used only as a rank within area (0 = deepest). Permutations shuffle rank within area × object type.
- Marshall MIC is used only in a sensitivity run.

## Pre-registered tests

| test | Mohenjo-daro | Harappa | verdict |
|---|---|---|---|
| T1a omnibus (signs ≥ 8 units) | 89.9 vs 72, p 0.087 | 88.8 vs 64, p 0.029 (Holm 0.057) | inconclusive (borderline) |
| T1b best sign (BH over 136) | M112 later, q 0.054 | M389 later, M293 later, q 0.19 | none passes |
| T1c role classes + length (BH over 20) | all q ≥ 0.48 | all q ≥ 0.35 | no class shift |
| T1d cross-site rho | 0.13, p 0.19 | | not shared |
| T1e half_life markers → Mohenjo-daro | p 0.83 | | not shared |
| T2 D = z_open − z_close | −0.94 (0.78 / 1.72), p 0.50 | −0.74 (1.69 / 2.44), p 0.60 | inconclusive (opener blind) |
| T3 ticked fish | n 21, p 0.11 | n 5, p 0.72 | no power |
| T3 M99 | p 0.99 | p 0.18 | flat, underpowered |
| T3 jar M342 | p 0.51 | p 0.38 | flat; OR 2 excluded at Mohenjo-daro |
| T3 M162 | p 0.64 | earlier, p 0.008, Holm 0.062 | lead only |

Power (T4; planted on real units):
- **Omnibus**, 20% of signs shifted: OR 1.5 caught 0.64 / 0.76; OR 2 caught 0.92 / 0.94.
- **Single sign, nominal 0.05:** n = 10 at OR 2 is 0.13-0.16; n = 40 at OR 3 is 0.75-0.85.
- The per-sign Bonferroni power is reported as 0 in `r1_primary.json`. That is an artefact: the power runs used a 2,000-permutation null, whose minimum p (0.0005) is above 0.05/136. The real run used 10,000.
  - In practice, BH-level detection of a single sign needs a common sign (n ≥ 40) with OR ≥ 3-5.
- **Markers at OR 2:** jar 0.92 / 0.79; M99 0.72 / 0.36; M162 0.26 / 0.09; ticked fish 0.07 / 0.01.

## Sensitivity (not decisive)

| run | omnibus p | top item |
|---|---|---|
| Mohenjo-daro, Mackay block as stratum | 0.64 | none (best q 0.42) |
| Mohenjo-daro + Marshall MIC (all rows) | 0.20 | M112 later, q 0.14 |
| M77 integer levels only | Mohenjo-daro 0.19; Harappa 0.009 | M112 (Mohenjo-daro) and M293 (Harappa) later, q 0.052; M162 earlier at Harappa |
| Harappa seals only | 0.006 | M162 earlier q 0.012; M65 later q 0.028; M389 later q 0.048 |
| Harappa tablets + sealings | 0.42 | none |

- The M77-integer run at Harappa uses the same objects as Vats EH, so it is not independent.
- The Harappa-seal signal (M162 earlier; M65 and M389 later) is the most consistent thing here. It still comes from one excavation and a few dozen texts. M162 in early Harappa seals often follows M249 or a numeral before the jar: "M249 M162 M342" and "M102 M162".

## Caveats
- Depth rank within an area mixes time with building phase and pit cuts. A shallow object can be redeposited. Ranks are ordinal and do not give a common clock across areas.
- Mackay's two Mohenjo-daro loci are large (DK-G 402 units). Within-block strata kill the signal, which suggests that part of the depth trend is a between-block contrast. It does not show a clean time trend.
- Tests run: 136 sign + 20 class + 8 marker + 2 omnibus + 2 cross-site + 2 T2 (pre-registered). The exploratory and sensitivity runs add about 25 more. Nothing is replicated independently.

## Hypotheses

| hypothesis | verdict |
|---|---|
| Sign frequencies change with within-area depth | inconclusive (borderline at Harappa, p 0.029 / Holm 0.057) |
| Depth trends are shared between Mohenjo-daro and Harappa | not supported (rho 0.13) |
| Openers turn over faster than closers | inconclusive (test blind to opener turnover) |
| Ticked fish / M99 / jar / M162 shift with depth | none; jar OR-2 shift excluded at Mohenjo-daro; M162 Harappa lead (Holm 0.062) |
| Texts get longer over time | exploratory lead (Stouffer p 0.008) |

## Next experiments
- An opener-sensitive T2: pool rare opener types, or use a turnover index such as the share of shallow-half tokens whose type is absent in the deep half. Validate it on plants first.
- Freeze the predictions "M162 earlier; M65 and M389 later on Harappa seals" and "length grows with depth". Score them on HARP 3B vs 3C seals (ICIT), which are independent of Vats. Expect low power (33 seals).
- Parse Mackay's room lists to separate block contrasts from depth within a block.

## Files
- `rlib.py` loads the data and builds units; `r1_main.py` is the frozen run; `r2_explore.py` holds the exploratory follow-ups.
- `r1_primary.json` and `r1_{block,mic,m77int,har_seal,har_nonseal}.json` hold the full outputs; `r2_explore.json` holds the carriers of the leading signals; `results.json` is the summary.
- Logs are in `*.log`. `r1_smoke_primary.json` is the outcome-free shuffled-depth run used for debugging.
