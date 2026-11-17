# Language vs non-linguistic code: does any structural property separate them at Indus size?

Language-vs-code specialist, 2026-11-14. Pre-registration: `docs/prereg/2026-11-14_language_vs_code.md` (script hashes frozen; written after calibration and dev runs, before held-out). Held-out = `dev_heldout(version=2)`. Unit: distinct break-free texts (dev 1,680 / 7,564 tokens; held-out 565 / 2,352 tokens).

Code (run from repo root with `.venv/bin/python`):
- `lvc_corpora.py`: all comparators. It also contains a rebuild of SIGIL from the paper's description.
- `lvc_metrics.py`: the 8 discriminators and their nulls, including a doublet-preserving Eulerian shuffle (unit-tested).
- `lvc_calibrate.py 25`: runs the battery on every comparator, size- and length-matched to Indus dev (1,680) and held-out (565), 25 replicates each. Output: `out/calib.jsonl`.
- `lvc_indus.py dev|heldout`: runs the battery on Indus. Output: `out/indus_*.jsonl`.
- `lvc_analyze.py dev|heldout [--heldout]`: power, leave-one-system-out (LOCO) classifiers, posterior and nearest systems. Output: `out/analysis_*.{log,json}`.

## Conclusion first

**At Indus size, none of the proposed discriminators separates writing-of-language from a structured non-linguistic code. The posterior for "writes language" stays at the prior (about 0.5).**

- **Accuracy.** Calibrated on 20 labelled systems, the best combined classifier reaches a leave-one-system-out balanced accuracy of only 0.61 at held-out size and 0.68 at dev size. In both cases 3 of the 6 codes are called "language". No single metric beats AUC 0.77, and that metric (abbreviation) also fires on codes.
- **Where Indus lands.** Indus sits on the decision boundary: raw P(language) = 0.49 on dev subsamples and 0.51 on held-out. Its nearest systems are, in order: the Indus bigram generator (a code by construction), Sanskrit and Tamil prose in simulated logo-syllabic writing, the slot code, Latin, and the SIGIL rebuild.
- **This extends Raghavendra's 2026 SIGIL result.** It covers not only entropy and n-gram statistics but also long-distance dependency, Menzerath-Altmann, vocabulary growth, open versus closed slots, the law of abbreviation and repetition.

## Comparators

| side | system | form |
|---|---|---|
| language, logo-syllabic (7) | Ur III seal legends (real, signs); Linear B tablet lines (real, signs); Latin EDH inscriptions; Caesar; Kalevala; Sanskrit and Tamil Wikipedia (simulated logo-syllabic writing: top words are logograms up to 30% of tokens, the rest are CV signs) | |
| language, pure word signs (7) | the same 7 texts with one sign per word (`W_*`) | This matches typology's finding that Indus cores are word signs |
| code (6) | Rietstap heraldic blazons (real); Inka khipu cord clusters (real); ICD-10-CM codes (real, 71k); Indian licence plates (synthetic, with state→district dependency); slot-independent emblem code; **SIGIL rebuild** (opener/dedication/office/ledger/terminal blocks, Pitman-Yor urns, deity→epithet licences, regional conventions, ligatures, issue marks) | |
| unlabelled | Proto-Elamite entry lines; paragorth's Indus bigram generator | |

- Long language units were cut into word-aligned chunks of 2-6 words, so that units of Indus length exist.
- Every comparator was resampled to Indus's exact text-length list.
- Vinča strings were not obtainable in machine-readable form.

## The discriminators and their power (held-out size, 565 texts)

Values are z-scores against a null built on the same sample. The null is a doublet-preserving shuffle for the dependency metrics and a token permutation for the others. Medians over 25 replicates; full tables, with 5-95% ranges, are in `out/analysis_heldout.log`.

| # | metric | AUC (L above C) | languages | codes | Indus dev-subsample median [95%] | Indus held-out |
|---|---|---|---|---|---|---|
| 1a | edge_ldd: opener→closer MI beyond adjacent transitions | 0.45 | -0.2 to 9.6; 5 of 7 word-sign languages ≈ 0 | -2.2 to 7.3 (heraldry, ICD, khipu high) | -1.29 [-3.4, 0.1] | **-2.03** |
| 1b | skip_cmi: I(X_i; X_i+2 \| X_i+1) | 0.49 | -2.8 to 11.5 | -2.2 to 19.7 (plates, khipu high) | 2.18 | 2.32 |
| 2a | mal_surp: longer texts → more frequent signs | 0.45 | -17.8 to 4.9 | -16.2 to 10.2 | -4.85 | -5.14 |
| 2b | mal_seg: more segments → shorter segments | 0.38 | -16.8 to 4.9 | -9.8 to 2.2 | -3.40 [-5.0, -1.9] | -1.21 |
| 3a | open_edge: log(interior / edge types per token) | 0.24 | -0.68 to 0.21 | -0.98 to 1.09 | -0.07 | -0.14 |
| 3b | heaps exponent | 0.74 | logo-syllabic 0.05-0.44; word-sign 0.73-0.87 | 0.0-0.62 | 0.38 | 0.39 |
| 4 | abbrev: frequency vs length of induced segments | 0.77 | -6.8 to 7.7 | -17.4 to 4.2 | -6.65 | -5.30 |
| 5 | repeat: texts with a repeated sign vs permutation | 0.68 | -1.67 to 1.12 | -1.62 to 0.80 | -0.65 [-0.83, -0.48] | -0.17 |

Why each family fails:
- **Long-distance dependency (1a/1b).** Where it is present, it mostly comes from multi-sign words: syllables spelling one word create dependencies two signs apart. Written one sign per word, 5 of 7 languages show no opener-closer dependency at all in units of Indus length. Meanwhile ICD codes, heraldry and khipu show strong dependency.
  - Indus has none: edge_ldd -2.03 held-out, 0.77 on the full dev set. The opener choice does not predict the closer choice beyond adjacent transitions.
  - This is *compatible* with a language written in word signs, and equally with a slot code.
- **Menzerath (2a/2b).** Both signs of the effect occur on both sides. The Kalevala word-sign corpus and ICD-10 both show the strongest "Menzerath" effect on mal_surp. Most codes obey the segment version.
- **Open versus closed classes (3a/3b).** The Heaps exponent tracks sign *type* (word signs grow fast, syllables saturate), not language versus code. Indus (0.38) sits with the logo-syllabic languages and with the khipu, slot and SIGIL codes. open_edge separates heraldry (1.09) and the slot/SIGIL codes (0.2-0.4) from most languages, and Indus (-0.07 to -0.14) is on the language side. But ICD (-0.98) and khipu (≈0) are on the same side, and Ur III seal legends (0.21) are on the code side. So 4 of 20 systems are misclassified by the best single metric (LOCO 16/20).
- **Abbreviation (4).** Every word-sign language gives a positive z, because frequent induced segments are single words. Logo-syllabic languages and most codes give a negative one. The metric detects writing granularity, not language.

### Combined classifiers, leave one system out

| feature set | size | balanced accuracy | languages → L | codes → L | Indus raw P(L) | calibrated posterior |
|---|---|---|---|---|---|---|
| all 8 | dev 1,680 | 0.68 | 12/14 | 3/6 | 0.49 | 0.27 |
| all 8 | held-out 565 | 0.61 | 10/14 | 3/6 | dev-sub 0.49; **held-out 0.51** | 0.38; **0.58** |
| dependency only | 565 | 0.40 | 9/14 | 5/6 | 0.51 | 0.45 |
| Menzerath + abbreviation | 565 | 0.57 | 9/14 | 3/6 | 0.48 | 0.43 |

**Posterior method.** Prior 0.5 × Laplace-smoothed LOCO sensitivity and false-positive rate. The posterior swings between 0.27 and 0.58 as Indus crosses a boundary it sits on, which is what "no power" looks like.

- **Proto-Elamite** (unlabelled) comes out at P(L) 0.69-0.76, on the language side. Its status is itself disputed, so it adds no calibration.
- **My SIGIL rebuild is not identical to Indus.** It has negative skip_cmi and weaker Menzerath. But its exact urn parameters are unpublished, and the Indus-trained bigram generator (a code) is Indus's nearest neighbour. So "Indus differs from my SIGIL" says nothing about language.

## Pre-registered held-out tests

| test | prediction | result | verdict |
|---|---|---|---|
| T1 power gate | LOCO balanced accuracy ≥ 0.80 and ≤ 1/6 codes called L | 0.61, 3/6 | **fail**: battery has no power (fixed consequence: held-out classification is not evidence) |
| T2 | held-out P(L) in [0.40, 0.60] | 0.51 | pass |
| T3 | ≥ 6/8 held-out values inside the dev-subsample 95% ranges | 5/8 (mal_seg -1.21, open_edge -0.14, repeat -0.17 fall outside) | **fail**: the Indus profile itself is not stable across the family split |
| T4a | no opener→closer dependency (edge_ldd < 2.24) | -2.03 | pass (absence) |
| T4b | Menzerath on segments ≤ -2.24 | -1.21 | fail |
| T4c | abbreviation-type relation ≤ -2.24 | -5.30 | pass |
| T4d | longer texts use more frequent signs ≤ -2.24 | -5.14 | pass |

Tests run: 7 confirmatory. Descriptive work: 8 metrics × 22 corpora × 2 sizes × 25 replicates, plus 4 classifier variants and nearest-neighbour ranking.

## Hypotheses

| hypothesis | verdict |
|---|---|
| Long-distance (opener-closer) dependency separates language from code at Indus size | **refuted** (AUC 0.45; word-sign languages show none) |
| Menzerath-Altmann separates them | **refuted** (AUC 0.38-0.45; codes obey it) |
| Open-class growth / closed slots separate them | **refuted as a discriminator** (Heaps tracks word vs syllable; open_edge 16/20 at best, Ur III misclassified) |
| Law of abbreviation separates them | **refuted** (tracks sign granularity) |
| Any combination reaches usable power | **not supported** (balanced accuracy 0.61-0.68; half the codes called language) |
| Indus has opener→closer agreement beyond adjacency | **not supported** (held-out -2.03; dev 0.77) |
| Indus writes language / is a code | **undecided**: posterior ≈ 0.5 (0.27-0.58 across classifiers) |

## Caveats

- Only 6 code systems exist on the code side, and real codes of Indus-like genre (seal legends with no language) are not available; SIGIL is a rebuild. Language units from prose are chunked, which cuts real sentence-level agreement. However, Ur III seal legends and Linear B lines are real whole units, and they behave the same way.
- The z-scores scale with sample size and length mix, so comparisons are valid only within a size (this is why both sizes were calibrated).
- The T3 failure means held-out Indus differs from dev on 3 metrics (more texts with repeated signs, weaker segment structure). This matches the v2 family split putting different text families in held-out, and it is an extra reason not to read anything into the classification.

## What would give power (next experiments)

1. **Real comparators of the same genre.** Legends that write no language versus legends that do, on comparable objects: Mesopotamian seal legends versus uninscribed-seal motif strings; potters' and masons' marks; Proto-cuneiform administrative lines. The decisive comparator is a real emblem or seal-legend system known not to write language, not a synthetic code.
2. **Longer continuous Indus texts.** Dependencies and Menzerath become informative only in units well above 5 signs (decipherability reaches the same conclusion). Revisit when the copper-tablet and multi-line corpus is enlarged (CISI vol. 3).
3. **Features that need meaning, not statistics.** Productive morphology (a sign attaching to many unrelated bases with a consistent position shift), or the same element appearing in different syntactic roles across genres. The ticked-fish closer (README #3) is the best existing candidate. Test whether codes ever show a modifier that moves a sign to a different slot.
