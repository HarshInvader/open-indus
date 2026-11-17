# Pre-registration: administrative archaeology (experiments/administration)

Date: 2026-11-14. Written AFTER dev-only runs of t1/t2/t3 (`<script> dev`) and BEFORE any held-out run
(`<script> heldout`), before any run of t2b (ICIT locus replication) and before any run of t4 (Lothal backs).
Held-out = `dev_heldout(version=2)`. Code is frozen as of this file except for output formatting.
Unit everywhere: distinct texts or distinct (text, context) pairs, as stated in each script docstring.

## Dev results that motivate the predictions (dev only, no held-out seen)
- t1 A: second lines/sides (len>=2, distinct pairs) attested as complete texts elsewhere 11/76 = 0.145 vs window null 0.138 (p=0.47). B: same-site 7/11 vs 6.7 (p=0.56). C: non-trivial compounds A+B 52/1009 = 0.052 vs bigram null 0.025 (p=0.005); same-site compounds 22/52 vs 18.6 (p=0.24).
- t2: 20 feature x site tests, none survives BH (best Harappa TB M336-M89 on AB, p=0.047; Harappa end-M211 on Mound F, p=0.07). Repeated seal texts at the same MD locus: 47 vs 29 (p=0.003) with naive strata, 38 vs 33 (p=0.12) once multi-sided duplicates are removed and strata include the publication campaign. Citadel share M267 - M293 = -0.03 (p=0.45).
- t3: M77 distinct side1/side2 pairs: single-N identities 3/18 vs 4.9 null (p=0.90): N varies. Bundling: mean short value with tall - without = -0.42 (p=0.21), max short 12 with and without tall. Phase: no trend (all |rho| < 0.2, p > 0.35). (t3 ICIT parts and phase parts were run on all data in the dev run, so they are NOT confirmatory and are reported as descriptive.)

## Confirmatory tests (each: hypothesis, prediction, test, threshold)
Family-wise: 12 tests below; a result is "confirmed" at the stated threshold; we also report Holm across the 12.

| # | Hypothesis (H1) | Our prediction | Test | Threshold |
|---|---|---|---|---|
| P1 | Line 2 / side 2 of multi-line or multi-sided seals is a standalone name/text attested elsewhere above chance | **Not supported** | t1 A on held-out: attested rate vs same-site window null, one-sided | p < 0.05 |
| P2 | Second lines are attested at the SAME site above chance (household/kin graph) | **Not supported** | t1 B on held-out, site permutation within length strata | p < 0.05 |
| P3 | One-line texts are compounds of two complete texts above a bigram null | **Supported** (block structure: formula + title, not persons) | t1 C on held-out | p < 0.05 |
| P4 | Compound halves are attested at the same site as the compound above chance | **Not supported** | t1 C same-site, held-out | p < 0.05 |
| P5 | Title block M336-M89 is enriched on Harappa Mound AB (citadel) | **Not supported** (dev p=0.047 is one of 20) | t2 held-out, directional: obs on AB > stratified expectation; G-test p | p < 0.025 |
| P6 | Final M211 is enriched on Harappa Mound F | **Not supported** | as P5, Mound F | p < 0.025 |
| P7 | Any title block / opener / register feature clusters by area (13 features x 2 sites) | **None survives** | t2 held-out, BH | q < 0.05 |
| P8 | Copies of one seal text cluster at one locus (office/household), campaign-stratified null | **Not supported** | t2 (i) held-out, MD | p < 0.05 |
| P9 | Mahadevan: M267 vs M293 openers differ in citadel vs lower-town share at Mohenjo-daro | **Not supported** | t2 (ii) held-out MD; t2b ICIT at MD (SD+L), Harappa (AB), Dholavira (Castle+Bailey) | p < 0.05 (any of 4, Holm) |
| P10 | ICIT replication: features x areas (MD areas, Harappa mounds incl. HARP ET/E, Dholavira Castle/Bailey/Middle/Lower Town) | **No survivor**, except possibly M176 on Harappa Mound F (known, STATE F18) | t2b, BH over all feature x site tests | q < 0.05 |
| P11 | Side-2 tall value N is fixed for a side-1 identity (rank/name) | **Not supported** (N varies within {2,3,4}) | t3 (a) held-out M77 distinct pairs: single-N count and SS-within vs shuffle | p < 0.05 |
| P12 | Short-stroke values are capped when tall strokes co-occur (bundling bound) | **Not supported** | t3 (b) held-out, one-sided | p < 0.05 |
| P13 | Lothal sealings: any sign (incl. tree family W390 = M161-169, and W700 cup) predicts the fastening type on the back | **None survives** | t4: per-sign G statistic over back types, distinct (text, back type) pairs, back types permuted among sealings; BH over signs in >= 3 distinct texts | q < 0.05 |
| P14 | Lothal: same seal text -> same fastening type, after removing the elephant seal W817-W002-W048-W740 | **Not supported** (paragorth S226) | t4 same-text type-sharing vs permutation | p < 0.05 |

What would change the conclusions: P1/P2 confirmed -> a person/kin graph exists and line 2 is a relational name; P5-P10 confirmed -> offices tied to precincts; P11 confirmed -> side-2 numbers are ranks/names; P12 confirmed -> a positional number system with bundling; P13 confirmed -> a commodity logogram.
