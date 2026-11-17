# Rank ladder: do Indus title signs track status on the object? (Baer's method)

Pre-registration: `docs/prereg/rank_ladder.md`, hash-frozen in `docs/prereg/HASHES.txt` with the code and the split before any held-out run. Ledger rows `rl_c1`..`rl_c12` in `docs/test_ledger.csv`. Machine-readable: `results.json`.

Code (run from the repo root, `.venv/bin/python experiments/rank_ladder/<script> dev|heldout`):
- `common.py`: frame-sign list, distinct-text seal table, ICIT family split
- `t1_transitivity.py`: precedence and transitivity
- `t1b_within_class.py`: order inside each slot class
- `t2_status.py`: signs vs seal size and material
- `t3_emblem.py`: signs vs animal emblem
- `t5_confirm.py`: pre-registered combined tests and sensitivity checks
- `t4_explore_dev.py`: dev-only checks that shaped the prereg

Logs are `*_dev.log` and `*_heldout.log`.

## Findings first

1. **There is no status ladder.** The frame signs (openers, connectives, titles, closers, post-closers) do fall in a nearly transitive order, but that order does not track seal size.
   - Transitivity, dev: 6 of 525 triads are cyclic in M77 (1.1%) and 2 of 694 in ICIT (0.3%), against 22% when signs are shuffled within each text.
   - Held-out, the frozen dev order predicts 83% (M77, n = 522) and 82% (ICIT, n = 839) of pair observations, p < 1e-50. That misses the pre-registered bar of 85%.
   - The order also holds inside each slot class, beyond the bare opener < title < closer template: held-out agreement 0.75 / 0.74 against 0.50 for shuffles (p = 0.002). Inside the title class alone it is weak: 0.64-0.67 held-out, against 0.90-0.93 on dev.
   - Ladder position against seal size: held-out Spearman -0.077, one-sided p = 0.056. The test could detect rho of about 0.12 (MDE). Dev gave -0.08.
   - Reading: the order is syntax (a template), not Baer's rank sequence.
2. **A few title signs do go with bigger or smaller seals, beyond what text length predicts.** Seal face area rises 8-11% per sign (positive control, p = 0.0005), so sign count, site and number of lines were held fixed in every size test.
   - The five signs picked on dev replicate as a group on held-out: S = 3.08, p = 0.0009. This survives Holm across the 11 confirmatory tests.
   - The clearest single sign is **W590 (M249, head of the M249-M161 title block): seals about 22% smaller.** Dev -21% (n = 64), held-out -23% (n = 15), per-sign Holm p = 0.046.
   - **W704-706 (M336, head of the M336-M89-M211 title block): seals about 19% larger.** Dev +19% (n = 91), held-out +19% (n = 16), one-sided p = 0.07. It passes (p = 0.014) when glyph widths replace sign count as the control.
   - Did not replicate: W400 (M176, post-closer) went from -30% on dev to -4% on held-out (it is a tablet/rod clitic and rare on seals). W405 (+26%, n = 5) and W390 (-10%) kept their direction but were not significant.
   - W741 (M343, the handled jar; STATE F12): -13%, one-sided p = 0.034. This does not survive Holm. It is also not independent of F12, because it uses the same 1930s measurements.
   - Global test (does any of 22 frame signs track size?): p = 0.04. This does not survive Holm.
3. **Animal emblems do not go with particular titles.** On held-out, the global emblem x frame-sign test gives p = 0.75 (dev 0.52). Frame signs predict unicorn vs other animal with AUC 0.53, against a permutation 95th percentile of 0.56; seal length alone gives 0.57. The dev hint that rarer-animal seals carry fewer frame signs (-0.15 signs, p = 0.044) did not replicate (+0.01, p = 0.58; MDE 0.22). So emblems do not mark offices that the text also writes.
4. **The emblem itself tracks seal size.** At equal text length and site:
   - seals with no animal are about 34% smaller (held-out n = 12, Holm p = 0.0008; dev -27%);
   - zebu seals are about 42% larger (n = 14, Holm p = 0.0018; dev +23%).
   This replicates and extends the animal control in STATE F12 (unicorn larger, gaur and no-animal smaller). The physical object carries a status gradient (zebu > unicorn > gaur > no animal); the title text mostly does not.
5. **Material cannot be tested.** Only 29 dev and 9 held-out square seals with measured faces are not steatite (faience 18, clay 8, terracotta 6, silver 2, copper 2, ivory 1). The dev hint (-15%, p = 0.06) has an MDE of 27-48%. Across all seal shapes, no frame sign is enriched on non-steatite seals (dev 50 seals, held-out 19; best p = 0.11).

**Bottom line.** Baer's ladder is not there. Frame-sign order is a near-transitive template, and its position does not follow seal size. Two title-block heads sit on differently sized seals: M336 on larger ones, M249 on smaller ones. That is the second and third sign-to-object correlate after F12, and a lead toward the M336 block and the M249 block being different offices or grades. The strongest status signal on the object is the animal (zebu largest, no animal smallest), and the animal is independent of the titles.

## Data and design

- **Corpus.** ICIT in native Wells numbers, because width, height, material, emblem, site and phase exist only there. M77 equivalents come from `bridge_WM.json` and are used only for the transitivity replication.
- **Unit.** Distinct texts. The measurements of all objects carrying one text are pooled (mean log face area; modal emblem, material and site), so title strings repeated on many seals (F27) count once.
- **Sample sizes.** Size tests use square seals (SEAL:S) with measured faces: 961 dev and 417 held-out distinct texts. Emblem tests use 1,074 dev and 492 held-out.
- **Size control.** The outcome is residual log area within site x sign count (1..7+) x lines (1, 2+) strata. Residuals are permuted within strata (4,000-10,000 permutations).
  - Sensitivity S1 replaces sign count with glyph footprint: the summed widths of the Mahadevan drawings. Wide signs might need a bigger seal regardless of status.
- **Held-out split.** ICIT family split (`icit_family_split.json`, seed 2026, sha256 afba6af6…).
  - Distinct texts within one edit of each other, or contained one in the other, form one family. Whole families go to one side, stratified by site.
  - 30% of 3,504 distinct texts are held out (1,083 texts in 962 of 2,571 families).
  - Why: near-copies and repeated title strings cannot leak a sign-size link across the split. The metadata exist only in ICIT. 30% rather than 25% because carriers per sign are few.
  - Transitivity also uses the project's M77 `dev_heldout(version=2)`.
- **Frame signs.** 25 features taken from the `functional_reading` role lexicon (listed in `common.py: FRAME` and the prereg).

## Pre-registered tests

| # | Hypothesis | Held-out result | p | Verdict |
|---|---|---|---|---|
| C1 | Frame-sign precedence is a transitive ladder (bar: share >= 0.85 in both corpora) | M77 0.83 (432/522); ICIT 0.82 (686/839); pairs 40/48 and 67/79 | <1e-50 | bar missed; direction strong |
| C2 | Order inside slot classes beyond the template | 0.75 / 0.74 vs 0.50 | 0.002 | **supported** (Holm) |
| C3 | Area rises with sign count (positive control) | +8.3% per sign | 0.0005 | **supported** (Holm) |
| C4 | Dev-selected size signs replicate | S = 3.08; W590 -23% (Holm 0.046) | 0.0009 | **supported** (Holm) |
| C5 | W741 (M343) on smaller seals | -13%, n = 37 | 0.034 | nominal only |
| C6 | Some frame sign tracks size (global) | 32.1 vs 20.1 | 0.040 | nominal only |
| C7 | Ladder position tracks size | rho -0.077 (MDE 0.12) | 0.056 | not supported |
| C8 | Frame signs x emblem (global) | 187.9 vs 203.3 | 0.75 | not supported (as predicted) |
| C9 | Fewer frame signs on rare-animal seals | +0.01 (MDE 0.22) | 0.58 | not supported |
| C10 | Frame signs predict unicorn vs other | AUC 0.53 (null p95 0.56) | 0.23 | not supported (as predicted) |
| C11 | Emblem tracks size: none smaller, zebu larger | -34% / +42% | 0.0008 / 0.0018 (Holm) | **supported** (Holm) |
| C12 | Material tracks frame signs or size | 9 held-out non-steatite seals | - | untestable |

Holm across the 11 testable confirmatory tests: C2, C3, C4 and C11 survive. Treating C1 as a fail by its bar, 4 of 11 support the alternative hypothesis. My predictions were right on 9 of 11: C1 missed its bar, and C9 went null where I had marked it inconclusive.

## Power (held-out, 80% power, two-sided alpha 0.05)

- **Per frame sign, size:** MDE 13% (W740, n = 151) to 49% (n = 11). Most title signs have 13-40 held-out carriers, so their MDE is 24-40%. A null on a single title sign therefore rules out only large effects. Effects of 10-15% (the F12 size) are invisible per sign held-out.
- **Ladder rho:** MDE 0.12 to 0.14. A weak ladder (rho of about 0.08, as on both dev and held-out) is neither excluded nor shown.
- **Emblem x title:** per-cell expected counts are 1-5, so only strong associations (a title mostly on one animal) are excluded. The classifier AUC test excludes any frame-sign profile that separates unicorn from other animals with AUC above about 0.56.

## Caveats and counter-evidence

- **One measurement set.** Dimensions for Mohenjo-daro and Harappa are the 1930s catalogue measurements (STATE F36). The held-out split replicates across texts, not across measurers. On the metrically measured sites alone (S2: Dholavira, Lothal, Kalibangan and others; n = 256, dev and held-out pooled, exploratory):
  - W590 is -11% (p = 0.09, same direction);
  - W70x is -4% (n = 6, wrong direction);
  - W741 is +11% (wrong direction, as in F37).
  An independent measurement of W590 and W70x seals is the real test.
- **Size is a proxy.** Bigger seals may reflect workshop, period or use as well as the owner's rank. Phase is recorded for only part of the data. In the dev phase subset the W590 and W70x effects held (-16% and +19%), but phase was not part of the confirmatory control.
- **Glyph width.** M336 and M249 drawings have the same aspect ratio (0.60 and 0.61), so their opposite size effects are not a "wide sign" artefact. The footprint control gives the same result (S1).
- **Precedence is not independent of the role lexicon.** The frame-sign classes were defined from position in the first place, so some transitivity is built in. That is why C2 (order within a class) and C7 (order vs size) are the informative tests.
- **The transitivity null** (signs shuffled within each text) is weak against any template. Transitivity alone says "ordered slots", not "ranks". The pre-registration stated this in advance.

## Next experiments

1. **Independent measurements for the M336 vs M249 contrast.** Measure the faces of every seal carrying W590 or W704-706 from CISI photographs with scale bars, or from museum records. With about 20 per group, a 20% effect is detectable.
2. **What M336 and M249 blocks share and differ in.** Look at continuations, sites and the emblem on large vs small seals (zebu seals with M336?). The held-out cell TB_W70x|zebu is 3 vs 1.0 expected, p = 0.06: a hint only.
3. **Emblem as rank.** Zebu > unicorn > gaur > no animal in size. Test carving quality and boss type from CISI photos as further status proxies, and test whether zebu or elephant seals cluster in time (HARP phase) or space.
4. **Material.** This needs a larger set of non-steatite seals with dimensions, e.g. the Fuls 2023 corpus or CISI vol. 3.
