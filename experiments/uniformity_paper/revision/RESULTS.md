# Uniformity paper: revision analyses for review 1, results

Prereg `docs/prereg/uniformity_paper_revision.md`, hashed with `rev.py` and `report.py` at 2026-11-21T19:24:19Z
(tag `uniformity_paper_revision`). Both code files are unchanged (sha256 6bcdecf7…, 8eb7544e…). Verdicts come
from `report.py` applied to `draws_*.jsonl` and are stored in `results.json`. Every number below is taken from
`results.json`. "Δ" is the median between AUC minus the median within-floor AUC unless a section says otherwise.

## Verdicts in plain English

1. **R1 bootstrap (MD vs Harappa tie).** The tie holds in the sense that every 95% interval for the
   MD–Harappa gap includes zero (median Δfloor +0.010 to +0.034). It does **not** pass equivalence at ±0.05. The
   smallest margin the data support is about **0.10–0.11 AUC** (unicorn seals 0.13–0.14). The paper may say "no
   difference beyond the floor, and any difference is below about 0.11 AUC". It may not say "equivalent within 0.05".
2. **R1 references.** Ur III Umma vs Girsu stays above the 0.05 margin under the bootstrap against all six floors:
   the lowest 2.5th percentile across them is +0.107. **Latin does not.** Its 95% intervals reach −0.026 and
   −0.046, and q5 is +0.009 / −0.023, so it is not "above margin". The four Chanhu-daro pairs have Δcons intervals
   that all include zero (median +0.088 to +0.126).
3. **R2 name bound.** Invented name stocks: 80% detection by r ≈ 0.18–0.31 of legends, exclusion (≥95% of
   replicates above the observed Δ) by r = 0.25–0.35. Real Ur III name frequencies spelled as shared common signs are
   much harder to catch: r80 = 0.36–0.50, and exclusion only at 0.40–0.50 (upper CI >0.50 in two families). The
   name bound the paper can state is **"a site-specific name stock in more than about a third of legends would have
   been detected; Ur III-like name use below about 40–50% of legends would not"**.
4. **Diffuse effects.** A local-variant effect reaches 80% power once about 5–10% of Harappa tokens are altered.
   A frequency shift needs about 20–30% of tokens replaced. Smaller diffuse differences are not excluded.
5. **R3 Ur III name roles. Yes: Umma vs Girsu survives removing owner names, patronyms, or patron/dedicatee
   names separately, against every structural floor.** All four ORACC floors and both CDLI floors pass, with
   every gate at 100%. Minimum Δ: noOwner +0.136 (CDLI +0.114), noFather +0.142 (CDLI +0.125), noPatron +0.189
   (CDLI +0.178). Removing owner and father together, or all private names, still leaves the two gated reign
   floors above the margin (min +0.085 / +0.077; CDLI +0.075 / +0.104). The collection floors are ungated at those
   sizes. Removing **all** names fails on the Girsu reign floor: +0.047 (CDLI +0.039). This repeats the step-2
   name-free result. The same-collection test (British Museum only) is above floor for whole legends (min +0.197)
   and for noPrivate (min +0.166, two gated splits). This removes a museum confound, not an archive one.
6. **R5 second classifier.** L2 logistic regression agrees with NB on Ur III and CDLI (above floor, min +0.153 /
   +0.148) and on Latin (+0.143). It agrees on the MD–Harappa tie for m77_seal (Δ +0.027) and icit_seal (+0.013).
   For **icit_sealtype it flips to "differs" by a hair**: Δ +0.0504 against the 0.05 margin, p_floor 0.059. NB gave
   +0.042 and p 0.078 ("same"). The **classifier-free Jensen–Shannon test agrees with NB on the Indus tie** in all
   three families. Between is not above floor (PS 0.28, 0.28, 0.68 against a 0.80 bar, powered 88–100%). It also
   agrees that **Ur III separates**: PS = 1.00 in all six floors, label-shuffle p = 0.005, the minimum at 200
   shuffles. It **does not agree for Latin**: within-province JSD is higher than between (PS 0.00 in both splits).
7. **R6 M93. Merging M93 into its nearest end-sign class does not remove the Chanhu-daro gap.** Base Δcons is
   +0.159 against Harappa and +0.101 against Mohenjo-daro. The variants give: →M94 +0.148 / +0.130; →M89
   +0.136 / +0.061; →M86 M87 (the ICIT reading) +0.166 / +0.163. Dropping M93 entirely gives +0.088 / +0.056.
   That is the largest drop (about 45% of the gap), but still above 0.05 in both pairs and short of the "half"
   rule. Verdict for every variant: "does not remove". M93 explains part of the gap, not all of it.
8. **R7 unicorn seals only. The MD–Harappa tie holds within unicorn seals, at the margin.** Δ is +0.050 in both
   families: icit_seal +0.0504, p_floor 0.137, power 98% at q = 0.15; icit_sealtype +0.049, p_floor 0.137, power
   96%. The rule verdicts are "same" (sealtype) and "underpowered" (seal). The seal verdict is the step-2 label for
   a gap at the margin that is not beyond the floor, even with power met. Bootstrap 95% CI −0.076 to +0.150 (seal)
   and −0.068 to +0.162 (sealtype). So: no difference beyond the floor, and equivalence is not shown.
9. **R4 Latin by object class. No single object class can be shown to carry place.** Military (n 9 / 6) and
   stamps (Britannia has 9 stamped legends) are untestable, as pre-registered. Graffiti are underpowered (gates
   32% / 40%) and sit below their within-province floors (Δ −0.359 / −0.133). The REST class (graffiti plus
   unflagged) is "above floor" by the family rule on its one gated split (br_north_vs_south +0.170, gate 80%). But
   on the other split it is −0.121 (gate 76%, ungated). That is not a robust carrier. Germania holds 182 of the
   191 stamps and 70 of the 89 military marks, so the whole-legend Latin result (step 2) likely rests on
   class composition. Together with R1 (Latin CI includes zero) and the JSD disagreement, **Latin should be
   demoted from a full reference to a weak, composition-confounded one**.

## Sentences safe for the paper

- "Pool-level bootstrap intervals (200 replicates) for the Mohenjo-daro–Harappa gap include zero in every seal
  family (median Δ +0.010 to +0.034; 95% CI lower bounds −0.060 to −0.089). Equivalence at ±0.05 is not
  established; the data bound any difference to about 0.11 AUC." [Reworded 2026-11-21, see correction note at end.]
- "Umma and Girsu remain separable above every within-city floor under the same bootstrap (lowest 2.5th [reworded 2026-11-21, see note at end]
  percentile +0.107 AUC)."
- "Removing owner names, patronyms, or patron and dedicatee names one at a time leaves Umma vs Girsu above all four
  ORACC and both CDLI within-city floors (minimum Δ +0.114, all planted gates 100%); only removing every name
  brings it below the Girsu reign floor (Δ +0.047)." [Reworded 2026-11-21, see correction note at end.]
- "A logistic-regression classifier and a classifier-free Jensen–Shannon permutation test reproduce the Ur III
  separation (LR minimum Δ +0.148; JSD between above within in every draw pair). The JSD test finds no
  Mohenjo-daro–Harappa difference beyond the floor in any family. Logistic regression agrees for two families and
  puts the third at the margin (Δ +0.050, p 0.06)."
- "Within unicorn seals alone, Mohenjo-daro and Harappa differ by Δ +0.05 AUC, not beyond the within-site floor
  (p 0.14, power 96–98%)."
- "Recoding the Chanhu-daro end mark M93 as M94, M89, or M86 M87 leaves the Chanhu-daro gap in place (Δcons
  +0.06 to +0.17); dropping it lowers the gap by about 45% (to +0.088 / +0.056)."
- "Simulated site-specific name stocks are detected at 80% power once they occupy 18–31% of legends; name use with
  real Ur III frequencies, spelled with shared common signs, is detected only at 36–50% (upper CI >0.50)."
- "Diffuse planted differences reach 80% power when about 5–10% of tokens carry local variants, or when 20–30%
  of tokens are redrawn from a shifted frequency profile."
- "The Latin reference is weaker than reported in step 2: its bootstrap interval includes zero, it is not
  reproduced by the Jensen–Shannon test, and no object class carries it on its own at testable sizes."

Not safe: "equivalent", "identical", "no difference" without the floor qualifier; Latin as a clean positive
control; "M93 explains the Chanhu-daro difference".

## Deviations

1. **Report invocation.** The prereg's `rev.py report` imports `experiments/uniformity_benchmark/report.py`,
   because `import cd` puts that directory first on `sys.path`, and that module has no `main`. The hashed
   `revision/report.py` was run instead with
   `python -I -c "import sys; sys.path.insert(0,'experiments/uniformity_paper/revision'); import report; report.main()"`.
   No code changed.
2. **Chunking.** Each job ran on its own: memory guard (≥20% free) → `compute.lock.indus` → `board/run.sh` →
   `timeout -s INT 90m`. No job reached the timeout. Roles resumed from 3,100 saved draws and finished at 9,000 in
   20 min. The other jobs took 1–18 min each. Unicorn (1 min) ran in the foreground. Draws are seeded per
   (job, condition, draw), so resumed draws are the same as an uninterrupted run would give. One process, single
   worker, `taskpolicy -b nice -n 20`.
3. **Lock.** `open-citizen-science/.local/compute.lock.mind` (owner line dated 07:44Z) was re-checked at 21:27Z.
   No self_model / kill_trained process was running, so it was treated as stale and left in place. The only other
   heavy process was an unrelated `wandb_akt_train.py`.
4. **NaN cells.** Latin MIL and STAMP draws at n ≤ 9 sometimes lose one class after empty-row removal, and the
   AUC is undefined (2 NaN draws, 150 unscorable). Those cells are reported as untestable. NaN upper CIs from
   the R2 bootstrap (the line never reaches the bar by r = 0.50) are written as ">0.50".
5. Not a deviation, but a note on the rules: the R2 rate-0 row shows that 17–40% of bootstrap replicates give
   Δ ≥ 0.05 with no names planted. That is the false-positive rate of the bootstrap design, and it is why the
   detection lines start above zero.

## Tables

### R1 bootstrap (200 replicates; Δfloor = b − w; Δcons = b − max(w, null))

| Comparison | n/side | Δfloor median | 95% CI | q5 / q95 | TOST ±0.05 | m* | Δcons median | Δcons 95% CI |
|---|---|---|---|---|---|---|---|---|
| MD–HA m77_seal | 200 | +0.017 | −0.079, +0.106 | −0.063 / +0.101 | no | 0.101 | +0.012 | −0.081, +0.101 |
| MD–HA icit_seal | 172 | +0.010 | −0.089, +0.106 | −0.078 / +0.102 | no | 0.102 | −0.001 | −0.089, +0.094 |
| MD–HA icit_sealtype | 227 | +0.034 | −0.060, +0.123 | −0.045 / +0.107 | no | 0.107 | +0.026 | −0.060, +0.097 |
| Unicorn icit_seal | 145 | +0.042 | −0.076, +0.150 | −0.053 / +0.143 | no | 0.143 | +0.023 | −0.076, +0.132 |
| Unicorn icit_sealtype | 145 | +0.038 | −0.068, +0.162 | −0.055 / +0.134 | no | 0.134 | +0.026 | −0.079, +0.113 |
| Ur III U_reign | 227 | +0.171 | +0.107, +0.230 | +0.117 / +0.222 | above | | +0.171 | +0.107, +0.230 |
| Ur III U_coll | 171 | +0.248 | +0.161, +0.347 | +0.179 / +0.326 | above | | +0.248 | +0.161, +0.346 |
| Ur III G_reign | 199 | +0.251 | +0.175, +0.320 | +0.190 / +0.310 | above | | +0.251 | +0.175, +0.320 |
| Ur III G_coll | 157 | +0.307 | +0.220, +0.401 | +0.228 / +0.386 | above | | +0.305 | +0.220, +0.365 |
| CDLI U_reign | 227 | +0.170 | +0.109, +0.225 | +0.116 / +0.220 | above | | +0.170 | +0.109, +0.225 |
| CDLI G_reign | 197 | +0.218 | +0.141, +0.301 | +0.152 / +0.279 | above | | +0.218 | +0.141, +0.301 |
| Latin ge_rlp_vs_bwhe | 128 | +0.129 | −0.026, +0.287 | +0.009 / +0.248 | not above | | +0.128 | −0.026, +0.228 |
| Latin br_north_vs_south | 73 | +0.142 | −0.046, +0.335 | −0.023 / +0.312 | not above | | +0.120 | −0.046, +0.252 |
| CD–HA m77_seal | 44 | +0.162 | −0.031, +0.358 | | | | +0.103 | −0.046, +0.267 |
| CD–MD m77_seal | 42 | +0.127 | −0.039, +0.290 | | | | +0.088 | −0.079, +0.235 |
| CD–HA icit_sealtype | 40 | +0.154 | −0.058, +0.344 | | | | +0.126 | −0.065, +0.297 |
| CD–MD icit_sealtype | 38 | +0.150 | −0.042, +0.313 | | | | +0.108 | −0.067, +0.246 |

### R2 planted names (60 replicates; observed step-2 Δ 0.005 / 0.014 / 0.042)

| Family | Form | r80 [95% CI] | Smallest excluded rate [95% CI] |
|---|---|---|---|
| m77_seal | sign | 0.275 [0.246, 0.300] | 0.30 [0.25, 0.30] |
| m77_seal | spelt | 0.250 [0.225, 0.269] | 0.25 [0.20, 0.25] |
| m77_seal | ur3emp | 0.450 [0.383, >0.50] | 0.40 [0.35, 0.50] |
| icit_seal | sign | 0.313 [0.260, 0.367] | 0.35 [0.25, 0.40] |
| icit_seal | spelt | 0.264 [0.235, 0.282] | 0.25 [0.25, 0.30] |
| icit_seal | ur3emp | 0.500 [0.438, >0.50] | 0.50 [0.40, >0.50] |
| icit_sealtype | sign | 0.250 [0.192, 0.277] | 0.30 [0.25, 0.40] |
| icit_sealtype | spelt | 0.178 [0.144, 0.208] | 0.25 [0.20, 0.30] |
| icit_sealtype | ur3emp | 0.364 [0.300, 0.400] | 0.50 [0.40, >0.50] |

Detection share at r = 0: 0.27 / 0.17 / 0.40 (false-positive rate of the design).

### Diffuse effects (50 draws; power = share with AUC − step-2 within ≥ 0.05)

| Family | Kind | v = .10 | .20 | .30 | .50 | Altered-token share at .10 / .20 / .30 / .50 |
|---|---|---|---|---|---|---|
| m77_seal | variants | 0.46 | 0.96 | 1.00 | 1.00 | 0.05 / 0.10 / 0.15 / 0.25 |
| m77_seal | shift | 0.16 | 0.60 | 1.00 | 1.00 | 0.10 / 0.20 / 0.30 / 0.50 |
| icit_seal | variants | 0.40 | 0.82 | 0.96 | 1.00 | 0.05 / 0.10 / 0.15 / 0.25 |
| icit_seal | shift | 0.28 | 0.66 | 1.00 | 1.00 | 0.10 / 0.20 / 0.30 / 0.50 |
| icit_sealtype | variants | 0.82 | 1.00 | 1.00 | 1.00 | 0.05 / 0.10 / 0.15 / 0.25 |
| icit_sealtype | shift | 0.60 | 0.90 | 1.00 | 1.00 | 0.10 / 0.20 / 0.30 / 0.50 |

### R3 Ur III name roles (Δ per floor; gate in brackets; * = gated)

| Corpus / variant | Verdict | U_reign | U_coll | G_reign | G_coll |
|---|---|---|---|---|---|
| ORACC noPN | not above floor | +0.171 (98%)* | +0.178 (52%) | +0.030 (90%)* | +0.199 (76%) |
| ORACC noOwner | above floor | +0.136 (100%)* | +0.207 (100%)* | +0.149 (100%)* | +0.209 (100%)* |
| ORACC noFather | above floor | +0.143 (100%)* | +0.169 (100%)* | +0.142 (100%)* | +0.273 (100%)* |
| ORACC noPatron | above floor | +0.189 (100%)* | +0.257 (100%)* | +0.244 (100%)* | +0.296 (100%)* |
| ORACC noOwnFath | above floor | +0.163 (100%)* | +0.191 (52%) | +0.085 (86%)* | +0.223 (76%) |
| ORACC noPrivate | above floor | +0.184 (96%)* | +0.199 (62%) | +0.077 (100%)* | +0.240 (72%) |
| ORACC noOffice | above floor | +0.193 (100%)* | +0.219 (100%)* | +0.234 (100%)* | +0.273 (100%)* |
| ORACC noAllNames | not above floor | +0.183 (100%)* | +0.187 (44%) | +0.047 (88%)* | +0.182 (76%) |
| CDLI noPN | not above floor | +0.131 (98%)* | | +0.037 (80%)* | |
| CDLI noOwner | above floor | +0.114 (100%)* | | +0.146 (100%)* | |
| CDLI noFather | above floor | +0.125 (100%)* | | +0.153 (100%)* | |
| CDLI noPatron | above floor | +0.178 (100%)* | | +0.222 (100%)* | |
| CDLI noOwnFath | above floor | +0.143 (100%)* | | +0.075 (82%)* | |
| CDLI noPrivate | above floor | +0.156 (100%)* | | +0.104 (80%)* | |
| CDLI noOffice | above floor | +0.186 (100%)* | | +0.207 (100%)* | |
| CDLI noAllNames | not above floor | +0.158 (96%)* | | +0.039 (80%)* | |
| BM-only whole | above floor | +0.197 (100%)* | +0.256 (100%)* | +0.278 (100%)* | +0.338 (100%)* |
| BM-only noPN | above floor | +0.181 (88%)* | +0.130 (52%) | +0.039 (72%) | +0.162 (62%) |
| BM-only noPrivate | above floor | +0.166 (90%)* | +0.186 (56%) | +0.081 (76%) | +0.217 (84%)* |

n per side: whole-size variants 116–227. Name-poor variants: ORACC 45–117, CDLI 62–120, BM 47–107.

### R4 Latin by object class

| Class | Split | n | between | within | Δ | gate | Verdict |
|---|---|---|---|---|---|---|---|
| MIL | ge_rlp_vs_bwhe | 9 | 0.778 | 0.365 | +0.413 | 14% | underpowered |
| MIL | br_north_vs_south | 6 | 0.760 | 0.800 | −0.040 | 8% | |
| STAMP | ge_rlp_vs_bwhe | 9 | NaN | 0.408 | n/a | 50% | untestable (Britannia 9 stamps) |
| STAMP | br_north_vs_south | 1 | n/a | n/a | n/a | n/a | |
| GRAF | ge_rlp_vs_bwhe | 21 | 0.516 | 0.875 | −0.359 | 32% | underpowered |
| GRAF | br_north_vs_south | 31 | 0.589 | 0.722 | −0.133 | 40% | |
| REST | ge_rlp_vs_bwhe | 64 | 0.570 | 0.691 | −0.121 | 76% | "above floor" (one gated split; not robust) |
| REST | br_north_vs_south | 66 | 0.579 | 0.409 | +0.170 | 80% | |

Class counts: Germania STAMP 182, GRAF 122, UNFL 88, MIL 70; Britannia UNFL 142, GRAF 101, MIL 19, STAMP 9.

### R5 logistic regression and Jensen–Shannon

| Contrast | n | LR b / w | LR Δ | LR p_floor | LR power | LR verdict | JSD b / w | JSD PS | JSD power | JSD verdict | NB (step 2) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| MD–HA m77_seal | 200 | 0.548 / 0.521 | +0.027 | 0.294 | 1.00 | same | 0.322 / 0.330 | 0.28 | 0.98 | not above floor | same |
| MD–HA icit_seal | 172 | 0.516 / 0.503 | +0.013 | 0.431 | 0.98 | same | 0.373 / 0.382 | 0.28 | 0.88 | not above floor | same |
| MD–HA icit_sealtype | 227 | 0.551 / 0.500 | +0.050 | 0.059 | 1.00 | differs | 0.358 / 0.351 | 0.68 | 1.00 | not above floor | same |

| Reference | LR verdict (min–max Δ) | JSD verdict (PS per split) | NB (step 2) |
|---|---|---|---|
| Ur III ORACC | above floor (+0.153 – +0.289, gates 100%) | between > floor (1.00 ×4, p 0.005) | above floor |
| Ur III CDLI | above floor (+0.148 – +0.164, gates 100%) | between > floor (1.00 ×2, p 0.005) | above floor |
| Latin | above floor (+0.143 – +0.151, gates 96% / 90%) | not above floor (0.00 ×2; within JSD 0.734 / 0.787 > between 0.722 / 0.723) | above floor |

### R6 M93 merge test (m77_seal, 50 draws; within floor 0.474 HA / 0.476 MD)

| Variant | CD–HA b | Δfloor | Δcons | CD–MD b | Δfloor | Δcons | Verdict |
|---|---|---|---|---|---|---|---|
| base | 0.634 | +0.159 | +0.159 | 0.598 | +0.122 | +0.101 | |
| M93 → M94 | 0.638 | +0.163 | +0.148 | 0.622 | +0.146 | +0.130 | does not remove |
| M93 → M89 | 0.619 | +0.145 | +0.136 | 0.590 | +0.114 | +0.061 | does not remove |
| M93 → M86 M87 | 0.649 | +0.174 | +0.166 | 0.662 | +0.186 | +0.163 | does not remove |
| M93 dropped | 0.600 | +0.126 | +0.088 | 0.570 | +0.094 | +0.056 | does not remove |

n per side 43 (HA) / 41 (MD).

### R6 M93 listing (`m93_listing.json`; photo checks in `docs/HUMAN_LEADS.md`)

| M77 object | Type | M77 sequence | ICIT id / CISI | ICIT sequence | Note |
|---|---|---|---|---|---|
| 6108 | seal | M216 M123 \| M65 M294 M176 M211 M93 | none | | unlinked |
| 6113 | seal | M234 M342 M343 M225 M87 M261 \| M93 | 72.1 / C-76 | W456 W741 W740 W530 W032 W850 \| W031 W032 | |
| 6118 | seal | M149 \| M12 M93 | none | | unlinked |
| 6124 | seal | M267 M99 M65 M62 M342 \| M93 | 71.1 / C-53 | W861 W002 W235 W222 W740 \| W031 W032 | |
| 6133 | seal | M293 M123 M86 M250 M93 M404 | none | | unlinked; M93 not final |
| 6202 | seal | M65 M67 M342 M12 \| M93 | 70.1 / C-70 | W235 W240 W740 W151 \| W031 W032 | |
| 6203 | seal | M104 M149 M267 M99 M93 \| M103 M403 M162 | 61.1 / C-66 | W817 W002 W003 W390 | **suspect link**: sequences do not match |
| 6204 | seal | M267 M99 M65 M62 M342 \| M93 | 71.1 / C-53 | same as 6124 | **suspect link**: same ICIT object as 6124; one object or two? |
| 6218 | seal | M387 M375 M375 M342 \| M93 | none | | unlinked |
| 6233.1 | sealing | M59 M387 M87 M59 M17 M406 M162 M93 | 116.1 / C-34 (TAB:B) | W220 W803 W032 # # W844 W390 W031 W032 | |
| 6403 | seal | M87 M244 M403 M180 M99 \| M87 M326 M342 M93 | none | | unlinked |

M93 occurs only at Chanhu-daro in M77 (10 seals, 1 sealing). Its twin forms are spread across the major sites.
M77 texts containing each twin: M94 in 11 (Harappa, MD, Kalibangan; none at Chanhu-daro), M89 in 306, M86 in 148,
M87 in 349. ICIT seal texts whose last segment is
exactly W031 W032: Chanhu-daro 5 of 59, Harappa 0 of 440, Mohenjo-daro 0 of 1,352. The M77 numeral inventory
lists M93 and M94 both as "3 slant", 10 occurrences each.

### R7 unicorn seals (ICIT "Bull1", n 145; within = MD random halves)

| Family | between | within | Δ | Δnull | p_floor | power q .10 / .15 / .20 | Verdict |
|---|---|---|---|---|---|---|---|
| icit_seal | 0.552 | 0.501 | +0.050 | +0.042 | 0.137 | 0.88 / 0.98 / 1.00 | underpowered (step-2 label: gap at margin, not beyond floor) |
| icit_sealtype | 0.547 | 0.498 | +0.049 | +0.043 | 0.137 | 0.84 / 0.96 / 1.00 | same |

## Correction (2026-11-21, review 2)

Three sentences in "Sentences safe for the paper" overstate the results. They are left in place, marked, and replaced by these (found by `docs/paper/uniformity/REVIEW_2.md`, items R1-R3):

- For "bound any difference to about 0.11 AUC", write: "the one-sided 95% upper limit on the gap is 0.10-0.11 AUC for this pipeline" (m* is the 95th percentile of the bootstrap Δ).
- For "above every within-city floor", write "above all six structural within-city floors" (random halves were not bootstrapped).
- For "only removing every name brings it below the Girsu reign floor (Δ +0.047)", write: "only removing all personal names (Δ +0.030; CDLI +0.037) or every name (+0.047; CDLI +0.039) brings the gap on the strictest floor, two Girsu reigns, under the 0.05 margin". The gap stays positive, so it is not below the floor.

## Addendum (2026-11-21, review 2): R9 edition overlap and R10 Ur III minus Indus contrast

See the two sections below; scripts `overlap.py` and `contrast.py`, outputs `overlap.json` and `contrast.json`.

### R10. Ur III minus Indus contrast (paired bootstrap, no new runs)

Prereg `docs/prereg/uniformity_paper_contrast.md`, hashed with `contrast.py` (tag `uniformity_paper_contrast`,
2026-11-21T22:40:46Z) before the contrast was computed. Arithmetic on `draws_boot.jsonl` only: each condition was
resampled with its own seed (`rng_for("boot", cond, rep)`), so Ur III and Indus replicates are independent and
D = Δfloor(Ur III) − Δfloor(Indus) can be formed replicate by replicate (200 differences). Output `contrast.json`.

Primary (Ur III = ORACC Umma vs Girsu against Umma reigns, the step-2 primary and lowest Ur III floor):

| Indus pool | median D | 95% CI | 5th pct | above 0 | above margin |
|---|---|---|---|---|---|
| M77 seals | +0.155 | +0.035, +0.261 | +0.049 | yes | no (by 0.001) |
| ICIT seals | +0.164 | +0.039, +0.279 | +0.062 | yes | yes |
| ICIT seals + sealings | +0.131 | +0.034, +0.240 | +0.051 | yes | yes |

All 200 × 200 combinations give the same picture (2.5th percentiles +0.029 to +0.041).

Secondary: against each of the six structural Ur III floors (ORACC and CDLI), all 18 contrasts have a 2.5th
percentile above zero (smallest +0.032, CDLI Umma reigns vs ICIT seals); 16 of 18 meet the margin rule (the two
misses are M77 seals vs ORACC Umma reigns, 5th pct +0.049, and ICIT seals + sealings vs CDLI Umma reigns, +0.048).
Unicorn pools against ORACC Umma reigns: median +0.122 and +0.128, but 95% CIs −0.007 to +0.267 and −0.017 to +0.256,
so the contrast is not established within unicorn seals.

**Verdict.** The central contrast holds as a direct test: the Ur III gap exceeds the Indus gap in every primary
pool, by +0.13 to +0.16 (medians), with every 95% interval above zero (lowest 2.5th percentile +0.034). Against the
0.05 margin it holds in two of three primary pools; in M77 seals the 5th percentile is +0.049.

Safe sentence: "Tested directly, the Ur III gap exceeds the Mohenjo-daro–Harappa gap by +0.13 to +0.16 AUC (paired
bootstrap medians), and every 95% interval excludes zero (lowest 2.5th percentile +0.034); within unicorn seals the
contrast is not established."

### R9. M77–ICIT object overlap (descriptive)

`overlap.py` (no scoring) counts seal objects shared by the two editions, using the existing link tables:
1930s register links (`audit_followups` b_editor_agreement, via `consensus_corpus/cooc.matched_pairs`) and sign
links (`consensus_corpus/out/seq_links.json`, best same-site ICIT record at distance ≤ 0.5). Output `overlap.json`.

| Site | M77 seal objects | linked to an ICIT record | ICIT seal records | ICIT seal records linked to an M77 seal | of which register links |
|---|---|---|---|---|---|
| Mohenjo-daro | 1,232 | 1,191 | 1,352 | 1,002 (74%) | 307 sides |
| Harappa | 350 | 333 | 440 | 261 (59%) | 29 sides |
| both | 1,582 | 1,524 | 1,792 | 1,263 (70%) | 336 sides |

Sign links are accepted only when the readings are close, so texts the editors read very differently fail to link;
the counts are approximate (a lower bound on true overlap, with some false links). 126 Mohenjo-daro and 17 Harappa
ICIT records are the best link for two or more M77 sides.

Two suspect Chanhu-daro links (sign links): M77 6203 (M104 M149 M267 M99 M93 | M103 M403 M162) → ICIT 61.1
(W817 W002 W003 W390), whose sequence does not match; and M77 6204 → ICIT 71.1, which is also the link for M77 6124.
6204 and 6124 have identical M77 readings (M267 M99 M65 M62 M342 | M93), so either M77 lists two seals with the same
text and ICIT has one, or one link is wrong. Both await the photo check in `docs/HUMAN_LEADS.md`.
