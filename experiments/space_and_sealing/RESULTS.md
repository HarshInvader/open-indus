# Space and sealing: what small seals leave out, and whether sealings differ from seals (Fable plan 5, T4 and T6)

Pre-registration: `docs/prereg/space_and_sealing.md`. It was hash-frozen with `sas_lib.py`, `t4_space.py` and `t6_sealing.py` (`docs/prereg/HASHES.txt`, tag `space_and_sealing`) before any outcome was computed. Only coverage (`coverage.py`) was run first. There were no amendments. Ledger rows: `ss_*` in `docs/test_ledger.csv` (25 rows). Logs: `t4.log`, `t6.log`. Numbers: `t4.json`, `t6.json`, `results.json`. Run from the repo root with `.venv/bin/python experiments/space_and_sealing/<script>.py`.

## Findings first

1. **Small seals keep the closer and drop the connective, but this order is not yet replicated.**
   - Text length rises with face area: +1.05 signs per doubling of area (p = 0.0001; positive control passes).
   - On top of that, two kinds of sign hold their share as the face shrinks.
     - Non-jar closers (M211, the M169 family, M12/M15, M254...): -0.021 share per doubling, Holm p = 0.004.
     - Post-closers (M176, M1): -0.009, Holm p = 0.019.
   - One sign class loses share faster than the text shrinks: the connective (M99/M123), +0.013 per doubling, Holm p = 0.016. The effect is almost all M99; without it the slope is +0.004.
   - Opener, title, numeral, jar and ticked fish do not depart from uniform thinning. Their power to detect a change (MDE) is 0.005-0.019 share per doubling.
   - Full order, from dropped first to kept: connective > title > opener > ticked fish > numeral > jar > post-closer > other closers.
   - **The pre-registered replication fails (P3).** The order agrees between the two family halves at rho = 0.60 (p = 0.08). It agrees between catalogue and metrically measured sites at only rho = 0.31 (p = 0.25), and the metric sites have only 90 texts with no significant slope. So the order is a result for the 1930s Mohenjo-daro/Harappa/Chanhu-daro measurements, not a replicated finding.
2. **Short seal texts really are cut-down versions of longer ones (P4 supported).** 51% of 1-3 sign texts (144 of 283) appear, in order, inside a longer attested seal text. A null that swaps their core signs for others of the same frequency gives 35.5% (95th percentile 37.8%), p = 0.001.
   - The longer versions mostly **add** connectives (1.69 times their share), openers (1.51), post-closers (2.65) and ticked fish (1.75).
   - They seldom add the jar (0.41) or other closers (0.39). So the closer belongs to the short text's core, and the connective/opener frame is the optional part.
   - One clash: post-closers are "kept" by area (P2) but "added" by the longer versions (P4b). That class is not consistent.
3. **Space itself is not shown to be the cause (P5).** Among short texts, being contained in a longer text does not depend on face area once length is held fixed: -0.044 per doubling, p = 0.11, MDE 0.10. Short texts are abridged formulas, but this test cannot show that they were shortened *because* the seal was small.
4. **Sealings carry the same closers as seals (T6: no class supported).** This compares 127 end-preserved distinct sealing texts with 1,426 seal texts at the same sites (Mantel-Haenszel over site x length band).
   - jar: OR 0.89 (42/127)
   - M211: 1.14
   - M169 family: 1.10
   - ticked fish: 1.53 (4 texts)
   - M12/M15: 0.37 (fewer on sealings; depletion p = 0.04, descriptive)
   - M254: 0.29
   - Holm p = 1 for all six. No class replicates without Lothal.
   - Power to detect OR 2 without Lothal: jar 0.75, M211 0.74, M169 0.70, ticked fish 0.51. So "closer X marks seals that were actually used for sealing" is **not supported at stated power** for these four.
   - Secondary hint: sealings carry the connective more often (OR 1.82, two-sided p = 0.013, Holm 0.067; without Lothal OR 1.90). It is not significant after correction.
5. **Surviving seals are almost never the dies that made the surviving sealings.**
   - 5 of 96 sealing texts (complete texts, or fragments of 3+ signs) match a seal text from the same site. That is the rate expected from texts that simply recur on different seals (4.9%).
   - Die-survival estimate f = 0.003, 95% CI -0.04 to +0.06.
   - Lothal has 58 seals and 33 sealing texts, with 1 match.
   - The only long same-site match (Mohenjo-daro sealing M-427 vs seal M-363, 6 signs) is not the same die: the emblem differs (unicorn vs none) and so does the handled-jar variant (W741 vs W745).
   - Seven complete sealing texts match a seal only at another site. These are short formulas, plus Lothal L-161 (the elephant box sealing), whose text is on Mohenjo-daro seal M-895, a unicorn seal, so a different die.
   - Reading: at most about 6% of the dies behind the surviving sealings are among the excavated seals. Seals and sealings sample different populations of dies, e.g. sealings arriving with goods from elsewhere, or seals discarded or destroyed away from where the sealings ended up.

**Bottom line.** Short Indus seal texts are abridgements that keep a closer plus core and shed the opener and connective frame. This fits a formula with optional framing (L1 structure, not meaning). The size link is real in the catalogue sites but not replicated, and space is not shown to be the cause. Sealings are a closer-neutral draw of seal texts, so no closer class marks administratively active seals. The non-textual anchor Fable hoped for is absent. The new fact is the die-survival bound: the seals we have are essentially never the seals that made the sealings we have.

## Data and coverage

| item | n |
|---|---|
| ICIT square seal objects (SEAL:S) | 1,777; steatite 1,460; material unknown 270 |
| steatite with both face dimensions | 1,277 (87.5%) |
| ...with a period or phase | 61% (Chanhu-daro 0%) |
| T4 distinct complete texts | 979; 952 analysed (42 site\|period strata with 2+ texts) |
| catalogue sites (MD, Harappa, Chanhu-daro) vs metric sites | 864 vs 115 (90 after strata filter) |
| ICIT sealing faces (TAG*) with legible signs | 242; complete 78 |
| T6 distinct sealing / seal texts (all legible) | 195 / 2,158 |
| sealing texts by site | Lothal 65, Dholavira 59, Harappa 17, Mohenjo-daro 16, Kalibangan 16, others ≤ 3 |

Lothal does not dominate the ICIT sealings as much as the plan assumed; Dholavira is about as large. Leave-Dholavira-out is reported too.

Controls applied to every test:
- **Allographs counted together:** W704/W706→W705 (M336), W742/W745→W741, W154/W156/W161→W151, W405-407→W390, and others (see `sas_lib.NORM`).
- **Duplicates:** the unit is the distinct text. Seal measurements are pooled per text.
- **Stratification:** site x period for T4; site x length band for T6.

## Pre-registered tests

| id | hypothesis | result | p | verdict |
|---|---|---|---|---|
| T4 P1 | length rises with area (positive control) | +1.05 signs/doubling | 0.0001 | pass |
| T4 P2 connective | share changes with area | +0.013/doubling (MDE 0.012) | Holm 0.016 | dropped first |
| T4 P2 other closers | " | -0.021 (MDE 0.018) | Holm 0.004 | kept |
| T4 P2 post-closer | " | -0.009 (MDE 0.009) | Holm 0.019 | kept |
| T4 P2 opener / title / numeral / jar / ticked fish | " | +0.003 / +0.007 / -0.004 / -0.009 / -0.001 | Holm ≥ 0.46 | no departure |
| T4 P3 | order replicates (rho ≥ 0.5, p < 0.05 in both) | catalogue vs metric 0.31 (p 0.25); family halves 0.60 (p 0.08) | - | **fails** |
| T4 P4 | short texts contained in longer texts beyond null | 0.509 vs 0.355 | 0.001 | **supported** |
| T4 P5 | small seals' short texts more often contained | -0.044/doubling (MDE 0.10) | 0.11 | not supported |
| T6 6 closer classes | enriched on sealings (MH) | OR 0.29-1.53 | Holm 1.0 | not supported |
| T6 support | enriched + leave-Lothal-out replicates | 0 of 6 | - | **not supported** (power 0.51-0.75 at OR 2) |
| T6 secondary (5 frame classes) | differ, two-sided | connective OR 1.82; others 0.88-1.55 | best Holm 0.067 | none |
| T6 die survival | estimate | f = 0.003 (CI -0.04 to 0.06) | - | matches = recurring texts |

Verdict for T4's main claim (omission order), using the pre-registered rule (P1 passes + a Holm-significant class + P3 passes): **not replicated**.

## Power

- **T4 P2:** 80% MDE per class is 0.005 (ticked fish) to 0.019 (numeral) change in share per doubling of area. The face areas span about 3 doublings, so shifts of 2-6 percentage points across the range are excluded for the null classes.
  - P3 on metric sites is weak: only 90 texts. A replication needs independent measurements of about 300 seals.
- **T4 P5:** MDE 0.10 per doubling in the containment probability.
- **T6:** planted OR 2 is detected with power 0.92 (jar), 0.85 (M211), 0.84 (M169) and 0.69 (ticked fish) on all sites. Without Lothal the figures are 0.75, 0.74, 0.70 and 0.51. At OR 3 every class is at 0.80 or higher. Only a weak enrichment (OR below about 1.7) remains possible. M12/M15 and M254 lean toward depletion, so enrichment is unlikely.

## Sensitivities (T4 P2)

- **Robust:** connective "dropped first" and non-jar closers "kept" hold when any of the following is dropped or changed:
  - the size-tracking carving variants (W706/W742/W745);
  - duplicate texts (one text per family, n = 711);
  - period (site-only strata);
  - two-line texts.
- **Metric sites alone:** every slope is n.s. (n = 90). Connective (+0.010) and title (+0.008) keep their direction. Non-jar closers keep theirs too (-0.031).
- **Leave one sign out:**
  - connective rests on M99 (W002);
  - the weak title trend rests on M336 (W705); without it the slope is negative;
  - "other closers" moves most without M12/M15 (W151) but stays negative.
- **T6:** complete texts only, site-only strata, and closer-as-final-sign-only all give the same picture: every OR is between 0.24 and 1.80, and no p is below 0.39 for enrichment.

## Caveats and counter-evidence

- **One measurement set.** 91% of T4 texts come from the 1930s catalogue sites. The redteam_rank warning applies: the effect could be measurer or workshop style, not space.
- **"Kept" closers may be genre, not abridgement.** Many short texts are core + non-jar closer formulas (e.g. W003 W390, W390 W740) that may be complete texts in their own right. P5's null fits this.
- **Jar.** The pre-registration expected the jar to be kept or neutral, because closer_ownership found it commoner on longer legends. It is neutral to slightly kept (-0.009, p = 0.09). On the longer versions it is rarely the added sign (0.41).
- **Sealing transcriptions are fragmentary.** Only 78 of 242 faces are complete. Closer tests use end-preserved texts, so the units differ by class.
- **Die-match denominators include sites with no excavated seals** (Hulas, Rupar, Ganweriwala, Tell Umma). Without them the rate is 5/91 = 0.055 and f is about 0.006, essentially the same. Matching is by text, so it is an upper bound on die identity: no confirmed same-die pair exists.

## Hypotheses

| hypothesis | verdict |
|---|---|
| Small seals omit optional frame slots in a fixed order | inconclusive: connective dropped first, closers kept (Holm), but not replicated across measurers or family halves |
| Short texts are contained subsets of longer texts with the same core | supported (51% vs 35.5%, p = 0.001) |
| Abridgement is caused by space (area beyond length) | not supported (p = 0.11) |
| A closer class marks seals used for sealing | not supported at stated power (OR 0.29-1.53; power 0.70-0.75 at OR 2 without Lothal for jar/M211/M169) |
| Surviving seals made the surviving sealings | refuted as a general pattern (f ≈ 0, CI upper 0.06) |

## Next experiments

1. **Independent face measurements** for about 300 square seals from CISI scale-bar photographs. These would re-run P2/P3 outside the 1930s catalogue, and the same data serve redteam_rank's W590/W706 follow-up.
2. **Connective on sealings.** OR 1.82 (Holm 0.067) is a hint that sealing dies carry the full opener-connective "personal" frame more often. Freeze it as a prediction for new sealing finds; do not chase it on the same data.
3. **Die survival at Lothal.** Frenez & Tosi's per-impression seal identities (HUMAN_LEADS item) would turn the text-level bound into a die-level count.

## Files

- `sas_lib.py`: classes, allograph map, tables (frozen)
- `coverage.py` → `coverage.json`: pre-outcome coverage
- `t4_space.py` → `t4.json`, `t4.log` (frozen)
- `t6_sealing.py` → `t6.json`, `t6.log` (frozen)
- `explore_matches.py` → `explore_matches.log`: post hoc list of matching texts
- `results.json`: summary
