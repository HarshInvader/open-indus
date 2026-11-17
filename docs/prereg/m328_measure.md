# Pre-registration: M328 (+ tall strokes) as a counted vessel/measure (Fable 5.2 plan 2, item E1)

Registered 2026-11-15, BEFORE any score in this file was computed. Work dir `experiments/m328_measure/`. What was looked at before writing this: CISI page photos (to find scenes and crops, see Leg 1), record counts and metadata availability (ICIT: 375 side-records with tall + W700, 329 with a width; M77: 310 objects with M328, loci available). No relationship between N and any physical variable was computed or looked at. Prior knowledge declared: STATE F38/F39 (cup formula values {2,3,4}, N not tied to side-1 text), redteam_pnl B (counted-item test failed, 13/25; 3 minimal pairs for M328). SHA-256 of this file and the scripts goes in `docs/prereg/HASHES.txt` (tag `m328_measure`) before the scoring runs.

Hypothesis H (measure reading): M328 depicts a vessel, and tall-N + M328 means "N vessels / N measures"; N therefore tracks a physical quantity.

## Leg 1: shape identity (scripted blind forced choice; single agent, no raters)

Data limits found before registration: CISI vol. 1-2 scans are ~100 ppi. The pot Parpola describes in the kneeling-worshipper scene of M-478/M-479/M-480 B (CISI 1 p.115) is not resolvable (under ~8 px); H-177 B (kneeling figure before tree) shows no identifiable vessel. These are EXCLUDED as unresolvable, not as non-matches. Usable scene vessels:
- **S1 (primary)**: H-180 B (CISI 1 p.209), vessel held between a standing figure and a kneeling figure.
- **S2 (secondary)**: H-714 A (CISI 2 p.318), U-shaped object beside a standing human figure (no kneeling figure).

Items:
- Sign lineup (Mahadevan drawings, `data/sign_images`): M328 plus 7 distractors chosen for vessel/U-like outlines before scoring: M342, M340, M347, M316, M319, M323, M332. Chance = 1/8.
- M328 photo crops (positive control): H-723 A, H-178 A, H-697 A (CISI 2/1), M-456 A (CISI 1 p.111), M-1402 A (CISI 2 p.188).
- Real Harappan pots (CISI photos, whole vessels): H-167 A (1), H-370 A (1), H-371 A (1), H-372 A (1).

Protocol: crop boxes are fixed in `l1_shape.py`. Crops are saved under random IDs; masks are made and inspected (contact sheet) BEFORE scoring; scoring runs on IDs only and the key is joined afterwards. Mask: grayscale, smooth, Otsu threshold, both polarities, keep the largest component that touches the crop border least, then fill its convex hull (outline shape, so a line-drawn U and a solid pot are comparable). Descriptor: width profile of the hull at 12 equally spaced heights (each as a fraction of max width) plus log(height/width). Distance d = RMS(profile difference) + |delta log aspect|. Secondary descriptor (reported, not decisive): log Hu moments 1-4.

| id | test | pass if |
|---|---|---|
| PC | each M328 photo crop ranks the M328 drawing first among the 8 drawings | >= 3 of 5 (binomial p = 0.017 at chance 1/8). If PC fails, the method has no power and Leg 1 = inconclusive |
| L1a | S1 ranks M328 first among the 8 drawings (S2 reported the same way) | S1 rank 1 |
| L1b | same-shape threshold: d(S1, M328 drawing) <= max d(M328 photo, M328 drawing) | yes |
| L1c | descriptive: nearest neighbours of S1/S2 among pots + signs | none |

Leg 1 verdict: SUPPORTED if PC passes and L1a and L1b pass for S1; REFUTED if PC passes and S1 ranks M328 4th or worse or fails L1b; otherwise INCONCLUSIVE. With one primary target this is at best weak evidence either way (the best possible p is 1/8); stated in advance.

## Leg 2: does N predict a physical quantity?

N = value of the tall-stroke sign immediately before the cup (ICIT W031-W037 -> 1-7 before W700; M77 M86-M96 values from `fr.TALL` before M328).

Units: an ICIT object = record id prefix (sides joined). Object identity = the tuple of all its side texts; copies with the same identity are collapsed to one unit (median dimensions). Objects whose sides give conflicting N are dropped. Type strata: TAB:B (moulded), TAB:I (incised), other.

| id | question | statistic | null | direction | pass |
|---|---|---|---|---|---|
| Q1 | tablet size | Spearman(N, length = max(width, height)) over identities with length > 0 | N permuted within type stratum, 10,000x | rho > 0 (one-sided) | p <= 0.0125 |
| Q2 | mould batch size | Spearman(N, number of objects with that identity) | same | two-sided | p <= 0.0125 |
| Q3 | find-spot lot | M77 Harappa: chi-square N x locus (loci with >= 5 units), unit = distinct (locus, full object text) | N permuted within object_type, 10,000x | greater | p <= 0.0125 |
| Q4 | count vs name-like distribution | distinct identities: AIC of zero-truncated Poisson (count model, 1 parameter) vs free categorical over observed values (fixed-values model) | none (model comparison) | | count-like if AIC_Poisson <= AIC_cat; name-like if AIC_cat < AIC_Poisson - 2 |

Bonferroni alpha 0.05/4 = 0.0125 over Q1-Q3 (Q4 is a model comparison).

Secondary (reported, not counted): Q1 with area (width x height); Q1 Kruskal-Wallis by N class (discrete size classes); round-value clustering = share of N in {2, 4} (binary series) vs ZTP expectation; ICIT stratum/phase as a second lot variable (chi-square, same null); entropy of M328's N vs N before other heads.

Held-out: no parameter is tuned, so every Leg 2 test is confirmatory on all data. Replication: identities are split 50/50 into two halves with seed 20261115 (families = identities sharing any side text, kept together); a passing test must keep its sign in both halves. Q3 is re-run on M77 objects whose texts fall in `dev_heldout(version=2)` held-out.

Power (reported): Q1/Q2 by simulation of a monotone effect of Spearman 0.3 at the observed n; Q3 by planting N-locus dependence.

## Overall decision rule

- Measure reading SUPPORTED only if Leg 1 is supported and at least one of Q1-Q3 passes with replication.
- Measure reading KILLED if Leg 1 is refuted or inconclusive AND Q1-Q3 are all null where power for rho = 0.3 is >= 0.8. If power is < 0.8, the result is reported as flat but underpowered.
- Q4 alone cannot support the measure reading (a name system can also vary), but a clear name-like result counts against it.

## Amendment A1 (2026-11-15, after inspecting masks, BEFORE any Leg 1 score was computed)

The first contact sheet showed the single Otsu rule fails on relief photos (it keeps only the lit flank of a stroke) and on pots (page text, wrong box). Changes, all decided from `contact_sheet.png` / `mask_diag.png` only:
- Pots: whole-vessel rule (non-white pixels, largest component, holes filled); boxes corrected to the vessel photos.
- Relief crops: local-contrast rule (both flanks of a stroke) by default; S1 (H-180 B, a solid round object) keeps the original Otsu "blob" rule, which is the only one that isolates it.
- M328 photo crops M-456 A, H-697 A, M-1402 A dropped: neither rule gives a usable outline at ~100 ppi. Two remain (H-723 A, H-178 A).
- PC threshold therefore becomes: both retained photos rank the M328 drawing first (p = 1/64 at chance 1/8).
