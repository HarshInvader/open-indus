# Are the foreign-found Indus texts structured like names? (board task #10, H2)

## Verdict: mixed, a weak lean that cannot be told apart from ordinary Indus seals

By the pre-registered rule, the 40 foreign texts look most like **Akkadian personal names** written in cuneiform signs: z-distance 1.78, nothing rejected, power 0.81 at n = 40. **But they are just as compatible with ordinary home Indus seals** (distance 3.08, nothing rejected at the Bonferroni level). Even with planted data, these two are confused 7-21% of the time. So these shape statistics do **not** show that the foreign texts are names rather than normal Indus seal texts.

Three traditions are clearly ruled out as structural models:
- **Ur III seal legends:** their texts start with a recurring sign far more often (0.70 vs 0.375, p < 0.001).
- **Sumerian names:** 0.78 vs 0.375, p < 0.001, because of recurring ur-, lu2-, lugal-, nin-.
- **Amorite names:** dominated by an initial ia-/su-mu-. This rejection is partly an artefact: the Amorite pool is small (103 names, only 2 with two signs).

A recurring theophoric element would sit at the **end**. On the foreign texts that slot is held mostly by the ordinary Indus closer, the jar W740: 7 of 40 texts, and W740 is final 76% of the time at home too. What is unusual is **numerals at the end**:
- W002 is final in 3 foreign texts but final in only 3.3% of its home uses.
- W033 is final in 2 foreign texts, against 6.5% at home.
- Overall, numerals are final in 21% of their foreign uses (9/43) against 5.5% at home (69/1,253). Person signs are initial in 34% of their foreign uses (11/32) against 20% at home (102/507).

Pre-registration: `docs/prereg/foreign_name_structure.md` (sha256 in HASHES.txt, tag `foreign_name_structure`). Code: `compare.py`. Numbers: `results.json`.

## Numbers

Foreign set: 40 texts with ≥ 2 legible Wells signs (lengths 2:9, 3:7, 4:7, 5:10, 6:2, 7:2, 8:3). Each comparator gets 2,000 length-matched samples of 40 texts.

| statistic | foreign | Akkadian names | Indus home seals | Ur III legends | Sumerian names |
|---|---|---|---|---|---|
| S1 share of tokens whose sign is in one text only | 0.299 | 0.283 | 0.309 | 0.289 | 0.335 |
| S2 texts with a repeated sign | 0.125 | 0.108 | 0.038 (p = 0.028) | 0.175 | 0.073 |
| S3 shared final sign | 0.55 | 0.586 | 0.619 | 0.465 | 0.437 |
| S4 shared initial sign | 0.375 | 0.517 (p = 0.14) | 0.374 | **0.702 (p < 0.001)** | **0.777 (p < 0.001)** |
| S5 final minus initial | +0.175 | +0.069 | +0.244 | −0.237 | −0.34 |
| z-distance D | | **1.78** | 3.08 | 4.77 | 6.40 |

- Amorite names: D = 12.9, rejected.
- Planted power (correct assignment) at n = 40: Ur III 0.90, Akkadian 0.81, Amorite 1.00, Sumerian 0.87, Indus home 0.86. At n = 30: 0.85, 0.74, 0.99, 0.82, 0.79.
- The main confusions are Akkadian ↔ Indus home (0.07-0.21) and Sumerian ↔ Ur III (0.10-0.14).
- Tests: 4 statistics × 5 comparators, with Bonferroni correction within each comparator.

The one feature that separates foreign texts from home seals is S2, the within-text repeat (0.125 vs 0.038). experiments/typology (Q2) already traced the Gulf repeat excess to two texts that double the jar W740. It is not syllable reduplication.

## Hypotheses

| hypothesis | verdict |
|---|---|
| Foreign texts are shaped like Ur III seal legends (formula + name + title) | refuted (initial-sign recurrence) |
| Shaped like Sumerian names | refuted |
| Shaped like Amorite names | refuted (pool-size caveat) |
| Shaped like Akkadian names | consistent, but not separable from home Indus seals |
| A recurring theophoric suffix at the final edge | not found: the final edge is the ordinary closer W740, and the unusual final elements are numerals |

## What failed or was not checked

- **The units are not the same.**
  - A cuneiform sign is mostly a syllable; an Indus sign is often a word sign.
  - These statistics are blind to sign identity, but they still depend on the size of the sign inventory.
  - So "looks like Akkadian names" means "has the same edge-recurrence and repeat profile". It does not mean "is syllabic".
- **No Dilmun cuneiform seal corpus was used.** We hold only 2-3 Dilmun legends (Rimum, Yagli-El), so that comparator could not be built.
- **The foreign readings are corpus readings,** not yet checked against images (task #12). The 9 texts that survived task #11 were not analysed separately; n = 9 has no power.
- **The person (W090-W175) and numeral (W001-W059) ranges are the typology folder's definitions.** The position profiles are descriptive and were not tested.

## Next

- Test the numeral-final pattern on the foreign texts as its own pre-registered question (it was found here descriptively): are numerals at the end of foreign texts more common than in home seals of the same length?
- If task #12 confirms the readings, rerun `compare.py` on confirmed readings only.
