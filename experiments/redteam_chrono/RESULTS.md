# Red team: Harappa relative chronology (half_life P3)

**Verdict: WEAKENED.** I reimplemented the test without reading the half_life code, and the headline number reproduces: HARP~Vats rho = 0.474 over 57 signs, p = 0.001. Three things undercut the strong reading ("a relative chronology of sign use"):

1. **Shared text families carry about half of the signal.** 40% of units (HARP 211/517, Vats 229/651) belong to 75 text families found in both excavations. Drop those families and rho falls to 0.27 (p = 0.061, n = 38 signs). On the same 38 signs with the full data, rho is 0.48. Dropping only *identical* texts, as half_life did, leaves near-copies in place, so rho stays at 0.44.
2. **No test within a single object type is significant.**
   - Seals only: rho 0.10, n = 14 (no power; HARP has 33 seal units).
   - Tablets only: rho 0.12 to 0.24, p 0.10 to 0.29.
   - Matched within-type combination: p = 0.10.
   - This looks like lost power, not an object-type confound. Random subsamples of the same size give rho 0.29 (5-95%: 0.06 to 0.49). But the claim can't be shown inside one object type.
3. **It doesn't carry over to other sites, and no single sign marker survives correction.**
   - Pooled across MD/KAL/LOT/DHO: p = 0.48. MD by M77 depth: rho -0.03.
   - Best marker q = 0.25 across 57 signs.

What survives: a weak, Harappa-only ordering. Part of it is real time agreement *of text families*: a family's mean relative date in HARP correlates with its date in Vats (rho 0.27, p = 0.02, n = 75 families). That is the same text (often one moulded-tablet batch) turning up at the matching relative level in both digs. It isn't a broad change in which signs scribes used.

## Reimplementation (independent)
- Unit: a distinct (dataset, relative period, object type, sign sequence). ICIT signs mapped to M through `bridge_WM.json`; unbridged signs kept as W.
- HARP: ICIT Harappa, period 3, phase B/B? = 0, B/C = 0.5, C = 1; 517 units.
- Vats: M77 Harappa level, depth tertile within locus (loci with ≥15 objects and ≥3 levels); 651 units.
- Shift per sign: mean over the sign's units of (relative period minus its object-type mean).
- Statistic: Spearman rho over signs with n ≥ 5 in both datasets.
- Null: periods permuted within type in both datasets, 2,000 permutations.
- Families: the project's own rule from `corpus/build.py` (≤1 edit for texts ≥4 signs, or the shorter text of ≥3 signs contained in the longer), applied to the union of both datasets.
- Code: `rc_lib.py`, `r1`–`r7_*.py`; logs `r*.log`; all numbers in `results.json`.

## Attacks (rho, n signs, one-sided permutation p)

| # | attack | result | effect on claim |
|---|---|---|---|
| 0 | reproduction | 0.474, n 57, p 0.001 | reproduces |
| 1 | object type | seals only 0.10 (n 14, p 0.37); tablets only 0.12 (p 0.29); HARP incised ~ Vats tablet 0.19 (p 0.20); HARP moulded ~ Vats tablet+sealing 0.24 (p 0.10); matched within-type combination p 0.10; fine-type strata 0.40 (p 0.004); no stratification 0.43 (p 0.003) | not shown within any one type; power-matched random subsamples give 0.29 (5-95% 0.06-0.49), so this reads as low power, not a confound |
| 2 | families / moulds | 341 families in 517 HARP units, 417 in 651 Vats units. One unit per family×period×type: 0.40 (p 0.004). Family-weighted: 0.30 (p 0.02). One unit per family: 0.24 (p 0.08). **Drop the 75 cross-excavation families: 0.27 (p 0.061); with n ≥ 3: 0.27 (p 0.031)** | biggest hit: about half of rho comes from shared text families |
| 3 | area / locus | strata type×mound 0.49 (p 0.001); type×trench 0.34 (p 0.01); HARP mound ET alone 0.23 (n 48, p 0.08); E and F alone n = 11 (no power) | survives; HARP phase is largely trench-bound, so separating phase from trench is only partial |
| 4 | Vats depth→time | absolute depth pooled over loci 0.27 (p 0.03); loci ≥30 objects 0.53; Vats' own stratum labels (ICIT "Stratum I-VII", within mound) ~ HARP 0.39 (p 0.001); Vats depth tertiles ~ Vats strata 0.45 | mapping is valid within locus; pooling depths across mounds halves rho, as datum differences predict |
| 5 | selection / null | n ≥ 3: 0.42; ≥ 8: 0.45; ≥ 10: 0.43 (p 0.01); **≥ 15: -0.04 (n 23, p 0.57)**; null stratified by type×length: 0.43 (p 0.002) | null is fine; the signal sits entirely in mid-frequency signs (5-14 units), which are the ones most exposed to single families; frequent signs show no agreement |
| 6 | cross-site | Harappa consensus vector vs MD ICIT 0.21 (p 0.11, 5/5 strong markers same direction); MD M77 depth -0.03; KAL -0.30 (n 9); LOT -0.02; DHO -0.23; pooled Stouffer over independent sites z 0.06, **p 0.48** | does not generalise; MD ICIT is the only lean in the right direction |
| 7 | text-level prediction | Vats shifts → HARP text phase 0.13 (p 0.001), 0.12 without shared families (p 0.04); HARP → Vats 0.06 (p 0.03), 0.04 without shared (p 0.23) | real but tiny; useless for dating a single text |

Tests run: about 45 correlation tests plus 57 per-sign marker tests (twice), all exploratory. No correction is applied across attacks. The verdict depends on the pattern, not on any one p.

## Chronological sign markers (Harappa only, low confidence)
The two excavations are combined by Stouffer z (each z is against its own within-type permutation null), with BH over 57 signs. **None reaches q < 0.05; the best is q = 0.25.** The directions below are leads only. "Both" means |z| ≥ 0.9 in each excavation separately. Fams = distinct text families carrying the sign (HARP/Vats).

| sign | direction | z (HARP / Vats) | combined p | fams | note |
|---|---|---|---|---|---|
| M293 | late | +0.9 / +3.1 | 0.004 | 10/15 | both; Vats-driven |
| M127 | late | +1.4 / +2.1 | 0.014 | 4/9 | both; few families |
| M387 | late | +2.0 / +1.3 | 0.021 | 11/10 | both; best balanced marker |
| M67 | late | +1.4 / +1.2 | 0.070 | 15/29 | both; many families |
| M197 | late | +1.3 / +1.2 | 0.077 | 3/9 | both; few families |
| M341 | late | +1.3 / +1.0 | 0.11 | 4/9 | both; few families |
| M12 | early | -1.3 / -1.2 | 0.078 | 6/11 | both |
| M347 | early | -1.1 / -0.9 | 0.16 | — | both, weak |
| M149 | early | -2.7 / -0.4 | 0.029 | 13/10 | HARP only |
| M391 | early | -2.5 / -0.1 | 0.064 | 10/22 | HARP only |
| M287 | late | +2.8 / +0.3 | 0.032 | 5/12 | HARP only |

With one unit per family×period, the same top signs remain (M293, M387, M149, M287, M67, M391, M12), with z reduced to 1.7-2.4. Compared with half_life's lists: late M127, M387, M197, M341, M293 and early M12, M347 agree. M72, M173 (late) and M375, M205, M1 (early) are weaker here (|z| < 1.3).

## Hypotheses

| hypothesis | result | verdict |
|---|---|---|
| HARP and Vats per-sign shifts agree (reproduction) | 0.474, p 0.001 | supported |
| agreement is not object-type mix | raw 0.43 ≈ stratified 0.47; within single types n.s. (low power) | inconclusive |
| agreement is not shared texts / moulds | without shared families 0.27, p 0.03-0.06 | weakened |
| agreement is not place (mound/trench) | type×mound 0.49, type×trench 0.34 | supported (partial separation only) |
| Vats depth tertiles track time | agree with Vats' own stratum labels (0.45) and with HARP via labels (0.39) | supported |
| same markers shift at other sites | pooled p 0.48 | refuted at current power |
| any single datable marker | min q 0.25 | not detected |

## What would change the verdict
- Upgrade: HARP lot/feature-level stratigraphy, or CISI 3.1 Vats-era tablets, giving ≥30 signs with agreement after shared families are removed; or MD sub-phases with a known direction confirming the late markers M387, M293, M127.
- Downgrade to fail: if the drop-shared-families rho goes to ~0 once families are linked more loosely (2 edits, or a common 3-sign core).

## Next
1. Treat P3 as **text-family chronology** at Harappa: date families, not signs. 75 families appear in both digs, and their relative dates agree (rho 0.27).
2. Retest HARP period by HARP lot when Kenoyer/Meadow lot data are available.
