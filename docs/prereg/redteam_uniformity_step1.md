# Prereg: red team of uniformity paper step 1

Written 2026-11-21, before any condition below was scored. Code: `experiments/redteam_uniformity_step1/rt1.py`, hashed with this file in `docs/prereg/HASHES.txt` (tag `redteam_uniformity_step1`). Seen before writing: pool sizes per condition (`experiments/redteam_uniformity_step1/sizes.log`), findspot-status counts and hand counts printed by `rt1.py sizes`, and the published numbers of `uniformity_benchmark`, `redteam_uniformity` and `uniformity_paper/step1`. No AUC of any new condition has been computed.

## Claim under attack

"Seal texts from Mohenjo-daro and Harappa cannot be told apart by sign use: the between-city AUC (0.51-0.55) equals the within-Mohenjo-daro split (DK vs HR+VS, 0.547). Readable administrative corpora at the same size separate their sites: Linear B Knossos vs Pylos 0.90 (0.78 series-balanced, 0.79 name-free), Latin Britannia vs Germania 0.72 name-free."

## Method (fixed)

Same as step 1: benchmark `clean()` + `draw_n()` (Indus length mix, balanced sides; one line per tablet for Linear B) + `score()` (frozen site_signal NB, one permuted-label AUC per draw). 30 draws per condition, seed 20261124. Size per side = the smaller side after cleaning, capped at 227, or borrowed from the matching condition (matched size). Statistic: median AUC over draws. Margin rule from step 1: between − within ≥ 0.05 = signal above the floor; |Δ| < 0.05 = no signal above the floor. "At Indus level" = median ≤ 0.589 (step 1 definition).

The only change of input: in attack 2, after a draw, each Linear B line's CV group is set to its scribal hand (from the DAMOS heading, e.g. `KN Fp(1) 1 (138)` → hand 138; suffixes -S/-R/? merged; unknown hand → own tablet group). That keeps any one hand out of the training folds when it is tested. The classifier is unchanged.

**Gates.** Planted-answer power gate as step 1 (same pool and size, labels permuted, `rt.plant` new100 at q = 0.15; detection = AUC ≥ max(0.65, own null q95); pass = ≥ 80% of draws) for: W1_lb_Kn_hands_p0, W1_lb_Py_hands_p0, W1_lat_ge_rlp_vs_bwhe_namefree, H_lb_serbal_handcv, F_lb_namefree_frame, F_ur3_ug_namefree_frame, F_lat_namefree_frame, L_md_area_confirmed. A condition whose gate fails cannot count toward a kill; it counts as "underpowered" (weakened).

## Attacks and conditions

### 1. Like-for-like floors

- Linear B within one palace (Knossos; Pylos): known scribal hands split into two groups (3 seeded random partitions, greedy balance by tablet count; unknown hands dropped). Variants: whole, series-balanced across the two groups, strict name-free (whitelist). Plus random tablet halves (pipeline floor). Note: hand 117 holds 193 of 435 Knossos tablets, so Knossos hand splits are close to "hand 117 vs the rest".
- Pylos room / archive and Knossos findspot are not in the DAMOS data on disk; hand groups stand in for office. Stated as a limit.
- Latin within one province: Germania, Rheinland-Pfalz vs Baden-Württemberg + Hessen (primary); Britannia, north and Wall zone vs rest; Germania random halves. Name-free (primary) and whole.
- Indus: M77 Mohenjo-daro DK vs HR+VS (C1 rerun), MD random halves.
- Between at the matched size of each within condition: Knossos vs Pylos (whole / series-balanced / name-free), Latin Britannia vs Germania (name-free / whole), M77 MD vs Harappa.
- Gap table: Δ = between − within at matched size for every corpus. Linear B Δ uses the median over the 3 partitions of between and within.

Primary reference gaps: LB whole Knossos-hands, LB whole Pylos-hands, Latin name-free ge_rlp_vs_bwhe. Indus primary gap: B1_md_h_at_C1 − W1_md_area_C1.

### 2. Scribe / series identity (Knossos vs Pylos)

H_lb_whole_handcv (227), **H_lb_serbal_handcv (116, primary)**, H_lb_namefree_handcv (115), H_lb_namefree_serbal_handcv (75), and H_lb_serbal_tabcv (A8 rerun with this seed, tablet CV).

### 3. Formula words

Names + frame (commonest 38.3% of tokens, benchmark rule) removed: **F_lb_namefree_frame** (LB whitelist + frame, 109), F_lb_nonames_frame (tagged names + frame, 227), **F_ur3_ug_namefree_frame** (145), F_ur3_pn_namefree_frame (70), F_ur3_ug_namefree_owner_frame (56), **F_lat_namefree_frame** (B7 rerun, 132). Indus with the commonest signs removed by the same rule: F_icit_frame (206), F_m77_city_frame (173), and the gap F_m77_city_frame_at_area − F_m77_area_frame (142). Top-k types removed (k = 10, 20) for LB name-free, Ur III Umma-Girsu name-free, Latin name-free and ICIT. Primary set = the three bold rows.

### 4. Indus findspot validity

Each M77 MD seal in the C1 split is linked to old-register rows via `m77_text_no`; area from the field-number prefix (DK; HR or VS), else the findspot field. Status before cleaning: confirmed 632, uncertain 128, contradicted 12, mixed 8 (DK: 535 confirmed / 47 uncertain; HR+VS: 97 confirmed / 81 uncertain / 12 contradicted / 8 mixed). Conditions: L_md_area_confirmed (confirmed only, 85 per side) with L_md_h_at_confirmed at that size; L_md_area_xnear / L_md_h_xnear: every text of ≥ 3 signs within one edit of, or contained in, a text on the other side is dropped from both sides (dedup.near, threshold 3), 138 per side. Counts of cross-split near pairs (≥ 2 and ≥ 3 signs) are reported for the C1 and city pools.

### 5. Sign lists

Within and between at matched size under ICIT raw, ICIT A1, ICIT A2 (CISI area split, 90 per side) and M77, M77 lump_all (M77 area split, 169 / 162 per side). Δ per list.

### 6. Power of within-vs-between

M77 MD vs Harappa at 169 per side (C1 size), real labels, Harappa texts only: each token replaced with probability q ∈ {0.10, 0.15, 0.20} by a Harappa stock. `old20` (primary) = 20 existing common signs, uniform (benchmark calib recipe); `new100` = 100 new symbols, Zipf (rt.plant form). Detection = draw AUC − median(W1_md_area_C1) ≥ 0.05; also reported paired by draw index.

## Verdict rules (fixed now)

**BROKEN** if any of:
- K1. H_lb_serbal_handcv ≤ 0.589 with its gate passing: Linear B is at Indus level once scribe and series are controlled.
- K2. Indus Δ (between − within) ≥ 0.10 in L_md (confirmed only), or Δ ≥ 0.05 in ≥ 3 of the 5 sign lists: the "between equals within" sentence is false.
- K3. Indus with the frame removed (F_icit_frame or F_m77_city_frame) ≥ 0.65 and above its own null q95: the cities differ in their less common signs.
- K4. Power: at q = 0.20 (old20), fewer than 50% of draws meet the margin: the within-vs-between comparison cannot see a stock covering a fifth of Harappa's tokens.

**STANDS WEAKENED** if no kill fires and any of:
- W1. Any primary reference gap (LB Knossos hands, LB Pylos hands, Latin ge_rlp name-free) has Δ < 0.05, or any primary reference floor (median within) ≥ 0.70: "between equals within" is then not a property that sets Indus apart, and the paper must say the distinctive fact is the low level at both scales.
- W2. 0.589 < H_lb_serbal_handcv < 0.65, or H_lb_namefree_serbal_handcv ≤ 0.589, or a gate in attack 2 fails.
- W3. ≥ 2 of the 3 primary formula-removed references are at Indus level (Latin was 0.564 in step 1, so one more is enough): the paper must state the "Indus seals lack site-varying formula words" reading as an equal alternative to "the cities share a vocabulary".
- W4. Indus Δ ≥ 0.05 in L_md_area_confirmed, L_md_xnear, the frame-removed M77 pair or any 1-2 of the 5 sign lists; or the confirmed-only floor differs from C1 by ≥ 0.05.
- W5. Power: at q = 0.15 (old20), fewer than 80% of draws meet the margin.

**STANDS** if nothing above fires.

Supporting readings (not kills): reference Δ ≥ 0.05 on all three primaries means the references show "cities differ more than parts of one site" and Indus does not.

## Known weaknesses (stated before scoring)

- Many within-site LB series-balanced and name-free splits are small (28-115 per side); they are secondary.
- The Latin "within one province" split covers several towns, so it is a stricter floor than "two areas of one city". Britannia north vs south has only 54 per side name-free.
- Hand groups are a proxy for office; room / findspot data for Pylos and Knossos are not on disk.
- The planted stock in attack 6 is added on top of real labels; Harappa's side of every draw is nearly fixed (200 texts), so draws understate uncertainty.
- Ur III has no within-city provenance, so it gets no floor; only attack 3 uses it.
