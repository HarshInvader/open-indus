# Identifiers or shared labels? Unseen-species counts (S3) and identifier repulsion (S4)

Pre-registered: `docs/prereg/identifiers.md` (hash-frozen with the code in `docs/prereg/HASHES.txt` before any held-out, ICIT or Ur III run). Ledger rows `id_p1`..`id_r2` in `docs/test_ledger.csv` (family of 8).

## Conclusion first

1. **Almost every seal text is unique, and the supply never runs out.** Per site, 93-97% of a newly found seal carries a text never seen before (1 - coverage), and the estimated total (Chao1) is 10-20 times the number observed. Tablets reach only 23-59%. Matched at 100 objects, Indus seal texts are as unique as real Ur III personal seal legends (new rate 0.97-0.99 vs 0.98-1.00). Seen alone, this looks like identifiers.
2. **The few seal texts that do repeat are not local, unlike real personal seals.** Of 1,560 complete ICIT seals, 181 carry one of 68 repeated texts. These repeats turn up at other cities as often as at home:
   - Cross-site ratio R = 0.89 (95% CI 0.46-1.14), or 1.40 (0.81-1.65) with Mohenjo-daro as the reference.
   - For catalogued Ur III seals, a known personal-identifier system, R = 0.18 (0.10-0.19).
   - The share of repeated texts found at more than one site is 0.66, against 0.67 if sites were assigned at random (p = 0.50).
   - The repeats are short: 45% of 2-sign seals carry a repeated text, against 2 of the 422 seals with 6-8 signs (0.5%).
   - Best reading: a shared vocabulary combined into texts that are mostly unique, plus a small set of short formulas used across the whole civilisation. The repeating part looks like labels; the rest looks like individual combinations.
3. **Indus "cores" are more varied than Ur III personal names.** At 100 objects, the non-frame part of a seal text is new 91-92% of the time. An Ur III personal-name line is new 54-75% of the time. Frames repeat (new 46-53%) and are shared across sites (R 0.95).
4. **The estimator is calibrated out of sample, and the tablet control exposes a trap.** Seal predictions held in every check: dev to held-out, 7/8 cells inside the 95% interval; post-1977 HARP Harappa seals, 3.7% matched vs 6.2% predicted; new sites, 9.6% vs 10.8%. Tablet predictions failed badly: only 9% of HARP moulded tablets match a pre-HARP Harappa tablet, against 45% predicted. Mould texts are local in time and place, so the apparent "saturation" of tablets is batch clustering, not a small closed list. Any Chao count on clustered finds underestimates the true total.
5. **No identifier repulsion (S4).** Seals found at the same site and period are not more distinct than seals from the same site at large:
   - ICIT: nearest-neighbour edit distance 0.625 vs 0.630 null, z = -1.1; shared signs z = +0.05; Holm p = 0.53.
   - M77 held-out: z = -0.2.
   - The test works: the tablet control clusters strongly, as moulds predict (moulded z = -4.2, p = 0.001; incised p = 0.046).
   - Power against strong planted repulsion is 0.83 (ICIT) and 1.0 (M77 dev). Against half-strength repulsion it is only 0.23-0.60.
   - So deliberate, strong distinctiveness is excluded; mild repulsion is not. A dev-only hint (fewer shared signs, p = 0.007) did not replicate.

**Net:** the data fit neither pure model. Seal texts behave like unique combinations of a shared vocabulary that were not designed to be told apart within a site or period, with a short-formula layer shared across cities. This is consistent with the project's "one shared vocabulary" lead (naming_sim, core_genre). It is not consistent with Ur III-style personal legends, whose rare duplicates stay local.

## Data and methods (short)
- A sample is one object; a species is its full text, with all sides joined. Damaged or incomplete texts are dropped.
- Classes: seal; true sealing; moulded tablet (TAB:B, and M77 "sealing" at Mohenjo-daro and Harappa); incised tablet; copper tablet.
- Estimators:
  - Good-Turing/Chao-Jost coverage
  - Chao1
  - ACE
  - iNEXT interpolation and extrapolation
  - Chao augmented bootstrap
- Core/frame split from the functional_reading lexicon.
- Ur III reference: 20,675 seal impressions from CDLI with provenience and seal ids (`ur3_extract.py`, read-only raw data). The physical-seal analogue is one record per base seal id.
- S4 groups:
  - ICIT: site + period/phase (HARP 3B, 3B/C, 3C; Vats strata; MD Early/Intermediate/Late; Dholavira stages ...).
  - M77: site + locus.
- S4 primary null (A): group labels permuted within site. A secondary slot-recombination null (B) was reported but is biased, as the prereg warned: recombined texts never reproduce real near-copies, so real groups always look "clustered" under it (seals z = -6.3).

## Results tables

### S3 (ICIT unless noted; seals)
| site | n | S | new-text rate | Chao1 | S(2n)/S | core new | frame new |
|---|---|---|---|---|---|---|---|
| Mohenjo-daro | 970 | 929 | 0.93 | 18,480 | 1.94 | 0.75 | 0.30 |
| Harappa | 268 | 259 | 0.94 | 4,742 | 1.94 | 0.83 | 0.34 |
| Dholavira | 69 | 67 | 0.94 | 1,108 | 1.94 | 0.85 | 0.34 |
| Lothal | 54 | 53 | 0.96 | 1,380 | 1.96 | 0.85 | 0.59 |
| M77 held-out MD | 281 | 264 | 0.90 | 3,779 | 1.92 | 0.78 | 0.43 |

Controls: Harappa moulded tablets 0.59 (n=385), incised 0.58 (n=274); MD copper tablets 0.23 (n=159); Lothal sealings 0.32 (n=28). Chao1 for seals is unstable because doubletons (f2) are few; read it as "thousands", not as a number.

### Hypotheses
| test | prediction | result | verdict |
|---|---|---|---|
| P1 seal vs tablet new-text rate | seals >= tablets + 0.20, CIs separate | ICIT 5/5; M77 held-out 1/2 (n=20 tablets) | pass ICIT, fail held-out (power) |
| P2 no saturation | completeness < 0.25 | 0.05-0.13 everywhere | pass, but weak (Harappa moulded tablets 0.24 too) |
| P3 repeats local (identifier) | R < 0.5 | R 0.89 (0.46-1.14); Ur III 0.18 | **refuted; shared-label pattern** |
| V1 dev -> held-out | inside 95% PI in >= 80% of cells | 7/8 | pass |
| V2 HARP vs pre-HARP | inside PI | seals yes; tablets far below | seals pass; tablet texts local |
| V3 new sites | inside PI | 6/6 | pass |
| R1 seal repulsion | Holm p < 0.05 | p = 0.53; held-out null | **not supported** (strong repulsion excluded, power 0.83) |
| R2 tablet control | no repulsion | tablets cluster | pass |

## Caveats
- **Co-finding is not contemporaneity.** ICIT periods span centuries, and M77 loci are large areas (locus 31 at MD holds 675 lines). Repulsion between true contemporaries could be diluted. This is the main reason a weak effect is not excluded.
- **Mould copies.** Tablets are a saturation control by design. V2 shows their duplicates are batch-local, so the control "saturates" only within a deposit.
- **Ur III seal ids:** CDLI assigns seal numbers partly by legend, so seal-level uniqueness is partly by construction. That bias pushes Ur III R up (a travelling seal counts as a cross-archive match), so the contrast with Indus is conservative.
- **ICIT is mostly a second transcription of M77 objects.** Only the HARP (n=27 seals, 247 tablets) and new-site (n=166 seals) checks are independent data.
- **Small cells.** M77 held-out tablets n=15-24; Kalibangan, Lothal and Chanhu-daro seals n=42-54.
- **Exploratory, not pre-registered:** the length breakdown, the multi-site permutation and the matched-n comparison with Ur III names.

## Next experiments
- Re-run S4 with lot/stratum-level groups once HARP context data arrive (true contemporaneity raises power for mild repulsion).
- Test whether the repeating short formulas (e.g. W003 W156, W016 W390, W061 W740, W817 W002) behave as titles or labels: their emblem, seal size, and sealing use vs unique texts.
- Unseen-species counts on other real comparators of seal genre (Linear B nodules, Old Babylonian, Harappan-period Gulf seals) to place Indus on an identifier-label axis.

## Files
`id_lib.py` (data, estimators), `s3.py` (dev / confirm), `s3_extra.py` (P3 CIs, exploratory), `s4.py` (repulsion, power), `ur3_extract.py`; logs `s3_confirm.log`, `s3_extra.log`, `s4_heldout.log`, `s4_icit.log`, `s4_power_*.log`; `results.json`.
