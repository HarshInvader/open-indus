# Red team: rank_ladder size claims (C4 title signs, C11 emblems)

Independent reimplementation, written from the claims in `experiments/rank_ladder/RESULTS.md` and `docs/prereg/rank_ladder.md` without reading their code. Data: ICIT square seals (`SEAL:S`) with both dimensions, pooled to 1,378 distinct texts. Control: residual log face area within site x sign count (1..7+) x lines (1, 2+) strata, permuted within strata. Run from the repo root: `.venv/bin/python experiments/redteam_rank/r1_replicate.py` (then r2..r5). Logs `r*.log`, numbers in `results.json`.

## Verdicts

| Claim | Verdict | Key numbers |
|---|---|---|
| A. The 5 dev-picked signs replicate as a group | **Survives in the 1930s catalogue data** | Their split reproduced exactly: S = 3.09, p = 0.001. My own family split: S = 6.6. 300 random re-splits: the group replicates (p < 0.05) in 95% of them. |
| A. W590 (M249) seals ~22% smaller | **Survives, but only in catalogue data** | All data -22% (n = 77, z = -4.8). Mohenjo-daro -26%, Harappa -22% (p = 0.049). Metric sites -8% (n = 14, 95% CI -24% to +12%, MDE 32%): not tested. |
| A. W704-706 (M336) seals ~19% larger | **Fails as stated** | All of the effect is one Wells variant: W706 +64% (n = 36, z = +6.0). The common form W705 is -2% (n = 69), in the same block (W705/W706-W033-W520). W704+W705 together: 0%. |
| B. No-animal seals ~34% smaller | **Survives statistically; the status reading is weakened** | -31% (n = 49). It holds on complete texts (-33%), in Mohenjo-daro (-39%), in Harappa (-27%, p = 0.049) and on metric sites (-17%, p = 0.06). This is the only claim with near-support from independent measurements. |
| B. Zebu seals ~42% larger | **Weakened** | All data +28% (p = 0.002), but 33 of 39 texts are from Mohenjo-daro. Harappa +5% (n = 4), metric sites n = 2. My random held-out gives +11% (p = 0.42). Without the 5 largest zebu seals it falls to +19% (p = 0.04). |

## Attacks, in order

**1. Glyph width.** Sign width does not explain the effects. Widths come from the Mahadevan drawings via the bridge (they are drawn at a common height; M249 is 65 px and M336 64 px wide, against a median of 69).
- I replaced sign count with total glyph width quintiles, with longest-line width, and with glyph tercile inside sign count. I also ran OLS with sign count, total width, line width, site, lines and emblem together.
- W590 stays at -23% to -25%, W70x at +18% to +26%, no-animal at -32% to -35%, zebu at +29% to +31%. All have p <= 0.003.
- Both width and height shrink or grow (W590: width -11%, height -13%). So this is a whole-seal effect, not a wider text line.

**2. Shape, type and fragments.**
- Only 4.7% of square seals are more than 10% off square. Using near-square seals only, complete texts only, or steatite only changes nothing.
- On rectangular seals (`SEAL:R`, n = 305) W590 is -1% (n = 18) and W70x +11% (n.s.). The effect belongs to the square-seal class.
- The data record neither the boss nor face vs whole object, so neither can be tested.

**3. Measurement source.** This is the weak point.
- Every significant result comes from Mohenjo-daro, Harappa and Chanhu-daro, which use one 1930s catalogue measurement set (STATE F36).
- On the metrically measured sites (n = 207 texts) the only estimates are W590 -8% (CI -24% to +12%), no-animal -17% (CI -31% to +1%), W70x n = 3 and zebu n = 2.
- My inch-grid flag does not separate measurers inside Mohenjo-daro or Harappa: the effect is present both on and off the grid.
- Period controls leave all four effects in place: site x phase strata, and Mohenjo-daro Intermediate levels alone (W590 -24%, W70x +33%, none -32%, zebu +31%, all p < 0.01).

**4. Duplicates and independence.**
- The family split is sound. Adding multiplicity strata, keeping single-object texts only, or jackknifing over families (41 for W590, 61 for W70x) leaves |z| >= 4.0 and >= 3.4.
- W590 texts are no more often repeated than other texts (4%).
- W590 is -23% inside the W590-W390 block and -22% outside it, so the effect is the sign, not the block. W390 without W590 is -7% (n.s.).

**5. Multiple testing.**
- Screening all 76 signs with >= 15 texts gives 10 with |z| > 2.58, against 0.8 expected. The SD of z across signs is 1.77. So many signs go with seal size, and title signs are not special as a class.
- W590 ranks 2nd and W70x 5th. Bonferroni over 76 signs: W590 p = 1e-4, W70x p = 0.01. If z is deflated by the 1.77 SD, W590 drops to two-sided p of about 0.007 and does not survive a full-screen correction.
- The top sign of the whole screen is **W706** (z = +6.0). W692 (M150, +39%) and W595 (M252, +46%) are also strong, and none of the three was claimed.

**6. Allographs: the decisive attack on M336.**
- STATE line 249 lists W705 and W706 as distributional allographs. W706 sits on seals 26% larger than W705 inside the pair (z = +3.5).
- The handled-jar variants split the same way: W742 is +41% and W745 +56% relative to W741 (z = 4.4 and 3.0).
- The other 9 pairs show no split.
- When the same title is written with one graphic variant on large seals and another on ordinary ones, the size signal follows how the sign was cut, not which office it names. That points to carving space, workshop or carver hand.

**7. Zebu context.**
- At Mohenjo-daro, zebu seals come from both excavators (M77: 27 FEM/Mackay, 14 MIC/Marshall). They are not from one context: locus 31 holds 48% of zebu seals against 40% of unicorn seals.
- They are over-represented in deep levels (<= -10 ft: 48% vs 32%, p = 0.046), but the size effect holds inside the Intermediate period.
- Their dev/held-out +42% looks like split luck. On mine it is +11%.

## What each claim would mean if it survives

- **W590 / M249 on smaller seals.** Seals carrying the M249 block were cheaper objects. This fits F27 (repeated title strings sit on smaller seals) and a lower-grade office. But the same pattern would come from one workshop or carving tradition making small seals and favouring M249. The allograph result (attack 6) makes the workshop reading at least as likely. M249 as a lower office stays a lead, not a reading.
- **M336.** There is no evidence that M336 is a higher office. If W706 really differs from W705, the claim narrows to "the W706 form is cut on large seals", which is a fact about carving.
- **No animal.** Text-only or geometric square seals are a smaller design class. Status is one reading. Simply needing less field space is another, and this test cannot tell them apart.
- **Zebu.** At Mohenjo-daro, zebu seals are large and finely cut. Nothing yet shows that this holds elsewhere.

## Next experiments

1. Look at the Wells drawings of W705 vs W706 and W741 vs W742/W745. Prediction, to freeze first: the large-seal variant is the more detailed one, i.e. a bigger field leads to a more elaborate variant.
2. Measure W590, W705 and W706 seals from CISI photographs with scale bars. That is independent of the 1930s tables, and about 20 per group would detect 20%.
3. Repeat the 76-sign screen with a mixed model that has a random effect per text family and per Mohenjo-daro locus (joined from M77), to see whether the z inflation of 1.77 is driven by locus or workshop.

## Files

- `data.py`: table, glyph widths, family split (project near-copy rule)
- `stats.py`: within-strata permutation and OLS tests
- `r1_replicate.py`: reproduction on their split and on mine
- `r2_attacks.py`: attacks 1-4 and 6
- `r3_multiplicity.py`: 76-sign screen and 300 re-splits
- `r4_allographs.py`: allograph pairs and metric-site CIs
- `r5_zebu_context.py`: M77 excavator, locus and depth
