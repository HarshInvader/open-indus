# M328 + tall strokes as a counted vessel or measure (Fable 5.2 plan 2, item E1)

Pre-registered in `docs/prereg/m328_measure.md` (amendment A1 was made before any score was computed). The prereg, both scripts and the blind key are hash-frozen in `docs/prereg/HASHES.txt` (tag `m328_measure`). Ledger rows `m3_*` are in `docs/test_ledger.csv`.

Run from the repo root:
- `.venv/bin/python -I experiments/m328_measure/l1_shape.py masks|score`
- `.venv/bin/python experiments/m328_measure/l2_quantity.py`

Logs: `l1.log`, `l2.log`, `x1_phase_explore.log`. Machine-readable results: `results.json`, `l1_results.json`, `l2_results.json`.

## Findings first

**The "measure" reading is dead.** The stroke count N before the cup sign does not track any physical quantity we can measure. The tests had power of at least 0.98 to detect a modest effect (Spearman 0.3). The one link we found runs the wrong way, and the counts behave like a fixed set of formula values, not like counts of a commodity. The shape leg cannot confirm that M328 is the vessel in the scenes. The one kneeling-scene vessel we could resolve is a round pot, not a U.

1. **Tablet size: no positive link; the link we found is reversed.** Over 275 ICIT tablet identities (mould copies collapsed), Spearman(N, length) = −0.17, one-sided p = 0.99. For area it is −0.22. Tablets with N = 4 are smaller (median 14 mm, against 16 mm for N = 2 and N = 3; Kruskal p = 2e-4). Exploratory: the negative link survives controlling for type and phase (rho −0.22, two-sided p = 0.03). A measure reading predicts the opposite direction, or nothing.
2. **Mould batch size: no link.** Copies per identity against N: rho = +0.08, p = 0.19 (n = 300). Power 0.99.
3. **Find-spot lot: no link.** On M77 Harappa loci, with units = distinct (locus × object text) so that mould copies count once: chi² = 28.2, p = 0.42 (n = 215). On the v2 held-out subset: p = 0.19 (n = 75). Power 0.985 against a planted 30% locus preference.
   - Secondary: N does shift with ICIT stratum/phase (p = 0.005). N = 4 dominates HARP Period 3 and 3B lots. The formula value drifts over time or batch. It does not follow the find-spot.
4. **The distribution is name-like, not count-like.** Over 300 identities, N = {1: 5, 2: 91, 3: 119, 4: 83, 6: 2}. A zero-truncated Poisson (count model) expects 55 ones and 27 fives. We see 5 ones and no fives. AIC: Poisson 922 against fixed-values categorical 719, so the fixed-values model wins by 203. This holds on the 31 distinct cup-side texts too (99.4 against 91.7). There is no clustering at "round" values beyond the 2/3/4 core. The {2, 4} share is 0.58 against 0.42 expected, which is only the avoidance of 1 and 5. This replicates STATE F38 (cup + {2, 3, 4}, with 1 rare and 5 absent).
5. **Shape leg: inconclusive. The method failed its positive control, and the evidence it does give points against identity.**
   - At CISI's ~100 ppi, the pot that Parpola describes in the M-478/479/480 B kneeling-worshipper scene is under 8 px and cannot be cropped. H-177 B shows no identifiable vessel.
   - The usable targets were S1, the H-180 B vessel held between a standing and a kneeling figure, and S2, a U-shaped object beside a figure on H-714 A.
   - The shape descriptor (convex-hull width profile + aspect ratio, scored blind on random IDs) put the M328 drawing at ranks 3 and 2, not 1, for the two retained M328 photo crops. PC failed 0/2, so the method cannot even recognise M328 itself in these photos.
   - For the record: both targets rank M328 7th of 8 drawings. S1's nearest neighbours are the round-topped sign M316, the oval M319 and the globular Harappan jars H-370 and H-167. The L1b threshold "pass" (d = 0.63 ≤ 0.85) is uninformative, because the photo-vs-drawing spread of M328 itself is that wide.
   - By eye, the H-180 B vessel is globular with a neck, like the real jars, not the open pointed U of M328.

Contact sheets:
- `contact_sheet.png`: every crop with its mask and convex hull (targets, M328 photos, 4 real pots, 8 sign drawings).
- `scenes_context.png`: the scenes at 2-3× zoom, including the unresolvable M-478 B.

## Hypotheses tested

| id | hypothesis | result | verdict |
|---|---|---|---|
| PC | the descriptor recognises M328 in tablet photos | 0/2 rank 1 | **failed** (Leg 1 has no power) |
| L1a | kneeling-scene vessel has M328's shape | M328 rank 7/8 (S1 and S2) | inconclusive (PC failed); leans against |
| L1b | vessel within M328's own variation | 0.63 ≤ 0.85 | uninformative |
| Q1 | larger N → larger tablet | rho −0.17, p = 0.99 | **refuted** (reverse direction) |
| Q2 | N tracks mould batch size | rho +0.08, p = 0.19 | **refuted** (power 0.99) |
| Q3 | N clusters by find-spot locus | p = 0.42; held-out p = 0.19 | **refuted** (power 0.985) |
| Q4 | count-like distribution | ΔAIC 203 for fixed values | **name-like** |
| Q3s | N varies by stratum/phase (secondary) | p = 0.005 | supported (period/batch drift) |

Leg 2 decision rule (prereg): Q1-Q3 are all null at power ≥ 0.8, and Leg 1 is not supported. **The measure reading is killed.**

## Caveats

- **Unit and split.** The prereg's 50/50 family split degenerated. Cup-side texts such as "W033 W700" are shared across most identities, so one family held 288 of 300 identities, and the half-replication is uninformative. Q3 used the M77 v2 held-out set as planned.
- **Sizes.** Harappa tablet sizes in ICIT mix 1930s inch-derived measurements (Vats) with HARP metric measurements (STATE F36). This can blur a size link. It cannot easily reverse one, and the negative link holds within phases.
- **Leg 1 rests on 2 targets and 2 control photos**, after 3 control crops were dropped for unusable masks (decided before scoring). A real answer needs high-resolution photographs (RTI or museum scans) of M-478/479/480 B and H-180 B, and human raters.
- **What the null does not exclude.** M328 may still depict a vessel or offering in some symbolic sense (Parpola's "N pots"). What fails is the idea that N counts a physical quantity: tablet size, batch, lot, or a smooth count distribution.

## What it means

The cup formula is better read as a fixed set of 2, 3 or 4 attached to an issue: a grade, class or formula variant whose share drifts by period. This agrees with F39 (N varies per issue and is not tied to the side-1 name) and with the failed counted-item red-team (redteam_pnl B).

## Next experiments

1. Get high-resolution images of M-478/479/480 B and H-180 B, and re-run Leg 1 with human blind raters. This is the only way to settle the shape question.
2. Model N against phase with HARP lot-level data: is the 2/3/4 shift a calendar or batch marker?
3. Retire E1 from the queue. Treat N + cup as a categorical tag and test it against find-context function (E5, sealing backs / door vs jar).
