# Pre-registration: rank ladder (Baer's method) — experiments/rank_ladder

Date: 2026-11-15. Written AFTER dev-only runs (`t1_transitivity.py dev`, `t1b_within_class.py dev`, `t2_status.py dev`, `t3_emblem.py dev`, `t4_explore_dev.py`) and BEFORE any held-out run. Code frozen with this file (hashes in `docs/prereg/HASHES.txt`) except output formatting.

## Data, unit, split
- ICIT (native Wells numbers), because width/height/material/emblem/site/phase live there. M77 (via `bridge_WM.json`) only for the transitivity replication.
- Unit: distinct texts. Physical variables of all objects with one text are pooled (mean log face area, modal emblem/material/site), so repeated title strings (STATE F27) count once.
- Size analyses: square seals (SEAL:S) with a measured face. Control strata: site x sign count (1..7+) x lines (1, 2+). Outcome: residual log area. Inference: residuals permuted within strata.
- Held-out: **ICIT family split** (`experiments/rank_ladder/icit_family_split.json`, seed 2026, sha256 afba6af6...). Distinct texts within one edit or contained in one another are one family (same rule as corpus `splits_v2`); whole families go to one side, site-stratified, 30% of 3,504 distinct texts (1,083 texts, 962 of 2,571 families). Justification: (a) near-copies and repeated title strings never straddle the split, so a sign-size link cannot be carried over by one text family; (b) the metadata exist only in ICIT; (c) 30% rather than 25% because the size tests have few carriers per sign. For transitivity the project's M77 `dev_heldout(version=2)` is also used.
- Caveat fixed in advance: Mohenjo-daro/Harappa dimensions are the 1930s catalogue measurements (STATE F36); held-out uses the same measurement set, so it replicates across texts, not across measurers.

## Frame signs (25 features; list frozen in `common.py: FRAME`)
Openers W817, W861, W820, W920; connectives W002, W060; title elements W760 (M347), W100 (M8), W176 (M48); title blocks W704-706 (M336), W033 (M89), W255 (M51), W590 (M249); handled jar W741 (M343, F12 reference); closers W740, W520, W390, W405, W407, W527, W368, W151, W154/156; post-closers W400 (M176), W090 (M1).

## Dev results (dev only)
- T1 precedence (all frame signs): M77 dev 6/525 cyclic triads (1.1%) vs within-text-shuffle null 22.5% (p=0.005); ICIT dev 2/694 (0.3%) vs 22.4%. Best linear order violated by 5.7% / 5.5% of pair observations (null 44%).
- T1b within slot class (OPEN, TITLE, CLOSE; null permutes only same-class signs): agreement M77 0.93, ICIT 0.94 vs null 0.56-0.57 (p=0.005); 0 cyclic triads in TITLE (14 and 19 triads).
- T2: positive control length slope +10.6% area per sign (p=0.0005). Global frame-sign x size test p=0.001 (24 features). Dev p<0.01: W590 (M249) -21% (n=64), W400 (M176) -30% (n=35), W70x (M336) +19% (n=91), W405 +39% (n=20), W390 -12% (n=105). W741 (M343) -10% (p=0.02, direction of F12). All five survive adding emblem and multiplicity strata and glyph-footprint strata (dev S1). Ladder score vs size rho=-0.08 (p=0.016); title-class ladder rho=-0.06 (p=0.26); frame count rho=-0.02 (p=0.53). Emblem: no-animal seals -27% (p=0.0005), zebu +23% (p=0.035), gaur -12% (p=0.07). Non-steatite square seals with dims: 29 dev (faience 14, clay 7, silver 1, copper 1, ivory 1...), -15% (p=0.06).
- T3: emblem x frame global chi-square p=0.52 (null). Unicorn vs other animal: best W390 depleted on other-animal seals (14 vs 25.5, p=0.003; not Bonferroni for 24). Composite frame count lower on other-animal seals by 0.15 features (p=0.044).

## Confirmatory tests (held-out unless stated)

| # | Hypothesis | Prediction | Test | Threshold |
|---|---|---|---|---|
| C1 | Frame-sign precedence is a transitive ladder | supported | frozen dev linear order predicts held-out pair observations (M77 HO v2 and ICIT HO), binomial vs 0.5 | share >= 0.85 and p < 0.001 in both |
| C2 | Order holds INSIDE slot classes beyond the template | supported | t1b heldout: within-class agreement with dev orders vs within-class shuffle of held-out texts | p < 0.01 in both corpora |
| C3 | Pipeline positive control: area rises with sign count | supported | t2 heldout length slope | p < 0.01, slope > 0 |
| C4 | Dev-selected size signs (W590-, W400-, W70x+, W405+, W390-) replicate | supported (power ~0.7 if true effects are half the dev size) | t5 H3: S = sum sign_dev * z_HO / sqrt(5), permutation, one-sided | p < 0.05; per-sign one-sided Holm reported |
| C5 | F12: handled jar W741 sits on smaller seals | weakly supported | t5 H3f one-sided | p < 0.05 |
| C6 | Some frame sign tracks size (global) | supported | t2 heldout global sum z^2 | p < 0.05 |
| C7 | Ladder position tracks status (later frame signs on smaller seals) | inconclusive (dev rho -0.08) | t5 H5 Spearman, one-sided negative | p < 0.05 |
| C8 | Frame signs co-vary with emblem type (emblems mark offices) | not supported | t3 heldout global chi-square, emblem permuted within site x length | p < 0.05 |
| C9 | Other-animal seals carry fewer frame signs than unicorn seals | inconclusive | t5 H6b one-sided | p < 0.05 |
| C10 | Frame signs predict unicorn vs other animal | not supported | t3 heldout classifier AUC vs label-permutation null | AUC > null 95th pct and p < 0.05 |
| C11 | Emblem marks status: no-animal seals smaller, zebu seals larger | supported for 'none', inconclusive for zebu | t5 H8 one-sided each, Holm over 2 | Holm p < 0.05 |
| C12 | Material (rare vs steatite) tracks frame signs | untestable | held-out non-steatite square seals with dims expected < 10 | reported descriptively only |

Interpretation fixed in advance:
- C1-C2 passing does not by itself show rank: a syntactic template is also transitive. Rank needs C4/C6 (signs track size) AND C7 (the order tracks size).
- If C4/C6 pass but C7 fails: some titles go with bigger or smaller seals, but the precedence order is syntax, not a status ladder.
- C8-C10 failing: emblems do not mark offices expressed by titles.
- Sensitivity, not confirmatory: S1 (glyph footprint strata replace sign count); S2 (sites measured metrically, not MD/Harappa, dev+HO pooled).
- Count: 11 testable confirmatory tests; Holm across them reported.
