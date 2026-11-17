# Short-label calibration: does the language-vs-code battery work on the right genre?

Short-labels agent, 2026-11-15. Pre-registration: `docs/prereg/short_labels.md` (hashes frozen in `docs/prereg/HASHES.txt`; written after calibration, before any Indus run). Held-out = `dev_heldout(version=2)`, 565 distinct break-free texts. Ledger rows `sl_s1`-`sl_s4`, `sl_x_edge`.

## Conclusion first

**The genre-matched set makes no difference. Real short labels of writing cannot be told apart from real codes at Indus size. Indus still lands on the boundary.**

- **Accuracy.** The primary set is 6 real short-label writing corpora against 7 real codes, every unit whole and never cut, at 565 texts with the Indus length mix. The language_vs_code classifier, unchanged, scores a leave-one-system-out balanced accuracy of **0.69**. It calls 4 of 6 writing systems "language" and 2 of 7 codes "language". A label-permutation null gives **p = 0.20**. Leave-one-family-out also gives 0.69.
  - At 150 texts it falls to 0.59. That set adds Linear A labels and Old Akkadian seals, and both are called "code".
  - The pre-registered power gate (≥ 0.80, ≤ 1/7 codes called language, p < 0.05) **fails**.
- **Indus.** On the full held-out set, raw P(language) is **0.503**. That puts Indus at the 54th percentile of the calibration systems, and the calibrated posterior is 0.65.
  - The dev subsamples give 0.49, with a 5-95% range of 0.47-0.51. The held-out value is inside it, so the score is stable but uninformative.
  - Its nearest systems: on held-out, Egyptian verbless phrases (L), then Billboard chord phrases (C), then Ur III and Old Babylonian seal legends (L). On dev, chord phrases come first.
- **One cell crossed 0.80, and it is a forking path.** Of 30 cells (2 sizes × 3 sets × 5 classifiers), only one reached the bar: an unregularised logistic with synthetic codes added (0.82; 2 of 10 codes called language). It puts Indus on the code side: 0.25 on held-out, 0.09 on dev.
  - At 150 texts the same classifier flips Indus to the language side (0.64 on held-out, 0.27 on dev).
  - This is the best of 30 cells and is not stable, so it is not evidence.
- **Changing the genre changed little.** The old set of 14 chunked-prose languages and 6 codes gave 0.61. The genre-matched set gives 0.69, and the union of everything gives 0.68 (p = 0.08). The language_vs_code verdict was not an artifact of chunking prose or of its six codes.

## What was obtained, and what was not

All downloads are in `raw/<source>/` and were parsed as text only. Units are whole objects or entries, never cut. Only units of 1-17 signs are sampled (17 = longest distinct Indus text). Duplicates are collapsed.

| system | source (open) | unit, token | usable units | used at |
|---|---|---|---|---|
| **Writing** | | | | |
| Ur III seal legends | CDLI open ATF dump (github cdli-gh/data), `@seal` sections + seal objects | whole legend; cuneiform signs (determinatives count as signs; numerals as N:unit) | 6,068 | 565, 150 |
| Old Babylonian / Old Assyrian seal legends | same | same | 3,290 | 565, 150 |
| Old Akkadian / ED IIIb / Lagash II seal legends | same | same | 168 | 150 |
| Linear B entry lines | DAMOS (codelib copy) | tablet line; syllabograms, ideograms, NUM | 12,623 | 565, 150 |
| Linear A nodules, roundels, sealings, vessels | lineara.xyz (GORILA) | whole inscription; signs | 244 | 150 |
| Egyptian verbless phrases (titles, names, offering captions), before 1550 BC | TLA v18 Earlier Egyptian (Hugging Face, CC BY-SA) | sentence with no verb; individual hieroglyphs | 3,310 | 565, 150 |
| Latin stamps, owner/maker marks, labels, instrumentum | EDH API (all 81,882 records) | whole text, diplomatic (abbreviated) words | 4,055 | 565, 150 |
| Latin other inscriptions | EDH | whole text, diplomatic words | 16,741 | 565, 150 |
| **Codes** | | | | |
| Unicode emoji sequences | unicode.org emoji-test.txt | fully-qualified sequence; code points | 3,963 | both |
| Named chess openings | lichess chess-openings | opening; SAN moves | 3,574 | both |
| Pop chord phrases | McGill Billboard SALAMI annotations | phrase; chord relative to tonic | 3,700 | both |
| METAR weather reports | aviationweather.gov cache | report; binned groups | 2,373 | both |
| Heraldry, khipu, ICD-10 | reused from language_vs_code | | | both |
| Licence plates, slot code, SIGIL rebuild | synthetic, reused | | | sensitivity only |

Obtained but not used:
- **Linear B nodules and labels (W series).** Only 80 undamaged distinct texts survive, too few even for the 150-text size.
- **CDLI tags and bullae** (1,395) and **bricks** (516). Mean lengths are 29.7 and 45.8 signs; under 70 of each fall in Indus range.
- **Proto-cuneiform entry lines** (21,488). Kept as an unlabelled reference.

Not obtained:
- **Pictish** (see below).
- **Livestock brands.** The Hawaii open CSV has brand images only, with no component sequences.
- **Mason's, potter's and merchant's marks; Vinča signs; tamgas; kamon; Chinese clan emblems; Maya name glyphs; Old Persian seal legends.** No open machine-readable sequence data was found.
- **Kudurru, totem-pole and barn-star corpora** (Sproat 2014). Only example texts are published.

The writing side therefore has seal legends, entry lines, labels and name phrases. The code side has no real emblem or mark system of the seal genre beyond heraldry. **That missing comparator is still the gap.**

## Findings

### 1. Power on the genre-matched set (565 texts, primary)

The language_vs_code classifier is reused unchanged: 8 metrics, logistic regression with C = 0.3, class-balanced. "Called L" means LOSO P(L) > 0.5. All values below are leave-one-system-out.

| set | languages | codes | LOSO BA | L called L | C called L | perm p | LOFO BA |
|---|---|---|---|---|---|---|---|
| **genre_real (primary)** | 6 | 7 | **0.69** | 4/6 | 2/7 | 0.20 | 0.69 |
| + synthetic codes | 6 | 10 | 0.73 | 4/6 | 2/10 | 0.10 | 0.73 |
| + old chunked prose | 18 | 10 | 0.68 | 12/18 | 3/10 | 0.08 | 0.71 |
| genre_real at 150 texts | 8 | 7 | 0.59 | 6/8 | 4/7 | 0.30 | 0.59 |

Misclassified systems in the primary set:
- **Writing called code:** Old Babylonian seal legends (0.499) and Linear B entry lines (0.49).
- **Codes called writing:** emoji (0.63) and heraldry (0.64).
- **At 150 texts,** Linear A labels (0.45) and Old Akkadian seals (0.48) are also called code. These are the two smallest real label corpora of writing.

Single metrics, primary set (AUC = chance that a writing system scores above a code):

| metric | AUC | note |
|---|---|---|
| heaps | 0.81 | Separates the Latin word-token corpora (0.83-0.84) from everything else. It tracks token granularity. Sign-level writing sits at 0.37-0.43, with chords and khipu at 0.34. |
| abbrev | 0.71 | Positive for word-level and Ur III corpora, negative for khipu, METAR and chords. Also granularity. |
| repeat | 0.67 | |
| mal_surp, mal_seg, open_edge | 0.48-0.52 | Chance. |
| edge_ldd, skip_cmi | 0.24 | **Inverted** (finding 3). |

### 2. Indus

Primary classifier trained on all 13 systems at 565 texts:

| Indus sample | raw P(L) | 5-95% | percentile among systems | calibrated posterior |
|---|---|---|---|---|
| held-out, full (565) | **0.503** | n/a | 0.54 | 0.65 |
| dev, 40 subsamples of 565 | 0.491 | 0.469-0.512 | 0.38 | 0.36 |
| held-out, 40 subsamples of 150 | 0.517 | 0.49-0.54 | 0.53 | 0.56 |
| dev, 40 subsamples of 150 | 0.505 | 0.49-0.53 | 0.40 | 0.56 |

- The calibrated posterior jumps between 0.36 and 0.65 as Indus crosses 0.5 by about 0.01. This is what having no power looks like.
- Indus held-out metric values: edge_ldd -2.03, skip_cmi 2.32, mal_surp -5.14, mal_seg -1.21, open_edge -0.14, heaps 0.39, abbrev -5.30, repeat -0.17.
- Nearest systems on standardised medians, held-out: Egyptian verbless phrases 1.15, chord phrases 1.36, Ur III seals 2.06, Old Babylonian seals 2.07, Linear B lines 2.21.

### 3. Exploratory: opener-closer dependency is a code trait, not a language trait

The intuition is that grammar links the start of a text to its end. On real, uncut units the evidence points the other way:
- **Codes have it.** Heraldry (+5.3), ICD-10 (+7.5), khipu (+5.1) and METAR (+6.0) show strong opener→closer dependency beyond adjacent transitions.
- **Most short writing does not.** Ur III seals (-2.2), Egyptian (-2.4) and both Latin sets (-4.3, -6.4) show none, or less than the shuffle. The exceptions are Old Babylonian seals (+1.0) and Linear B lines (+2.8).
- **Indus** (held-out -2.03, dev -1.27) sits on the writing side of this metric.
- **But codes sit there too.** Chords (-2.65) and emoji (-5.1) are on the same side.

This was seen after the data and is a single metric with a leave-one-out balanced accuracy around 0.69, so it is a hypothesis for a fresh pre-registration, not a result (ledger `sl_x_edge`, exploratory).

## Pictish: the direct precedent

Lee, Jonathan & Ziman (2010, Proc. R. Soc. A 466:2545) did what this experiment does: they classified a short-symbol system using statistics calibrated on known writing and non-writing.
- **Their corpus.** Pictish symbol "texts": symbols read top to bottom off complete stones, mostly 2-3 symbols each.
- **Their method.** A two-parameter decision tree on di-gram entropy (Ur) and di-gram repetition (Cr), calibrated on many languages and some non-linguistic sets (including heraldry).
- **Their verdict.** Pictish is writing, at the word level.

Sproat (Computational Linguistics 2010; Language 2014) built independent non-linguistic corpora: Pictish (283 texts, 984 tokens, 104 types, mean 3.5), Vinča, kudurru deity symbols, totem poles, heraldry, barn stars and weather icons. He found that Lee et al.'s cut-offs depend on corpus size and text length, and that several known non-linguistic systems fall on the "writing" side of their tree.

Three lessons, all of which this experiment reproduces:
1. **A classifier validated on long texts and large corpora does not transfer to 2-5-symbol units.** Our accuracy drops from 0.69 at 565 texts to 0.59 at 150.
2. **The verdict depends on which non-linguistic systems are in the calibration set.** Adding synthetic codes moves our best cell from 0.70 to 0.82, and that cell then calls Indus a code. At 150 texts the same classifier calls Indus language.
3. **The decisive comparator is a real emblem system of the same genre.** We could not obtain the Pictish data, or any comparable corpus of marks or emblems.
   - The Strathclyde database is offline. The Wayback Machine holds only its search page; the per-stone pages were never archived.
   - Lee et al.'s and Sproat's corpora are not public.
   - So Pictish could not be added here. If Sproat's XML corpora or the Lee et al. symbol lists can be obtained (by request), they are the next comparators to add.

## Pre-registered tests

| test | prediction | result | verdict |
|---|---|---|---|
| S1 power gate | LOSO BA ≥ 0.80, codes called L ≤ 1/7, perm p < 0.05 | 0.69, 2/7, p = 0.20 | **fail**: no power on genre-matched data |
| S2 | Indus percentile strictly between 0 and 1 | 0.54 | pass (not evidence, since S1 failed) |
| S3 | held-out P(L) inside the dev 5-95% range | 0.503 in 0.469-0.512 | pass |
| S4 | the one cell ≥ 0.80 must replicate on dev and survive fresh comparators | dev 0.09 and held-out 0.25 agree at 565 texts, but flip at 150 (0.27 vs 0.64) | **not supported** |

Tests run: 4 confirmatory, plus 30 descriptive classifier cells and 1 exploratory metric reading.

## Hypotheses

| hypothesis | verdict |
|---|---|
| language_vs_code failed because its languages were chunked prose rather than short-label registers | **refuted**: real whole short labels give 0.69, against 0.61 before |
| language_vs_code failed because of its particular 6 codes | **refuted**: 7 different real codes give the same result, and adding them all gives 0.68 |
| The 8-metric battery separates short-label writing from codes at Indus size | **refuted** (0.69 at 565 texts, 0.59 at 150, p = 0.20) |
| Indus writes language / is a code | **undecided**: P(L) 0.50, at the 54th percentile of the systems |
| Opener→closer dependency marks codes rather than writing in short units | **open** (exploratory, AUC 0.76 inverted) |

## Caveats

- **Tokens differ by script.** Latin corpora use words, the rest use signs. Heaps and abbreviation largely detect this.
  - Cuneiform readings are lower-cased transliterations. Different readings of one sign stay distinct, which inflates the inventory a little.
  - METAR groups and chords were binned by hand-written rules.
- **The Egyptian corpus is sentence-level, not a whole-object register.** Only the verbless sentences (names, titles, captions) are kept. TLA v18 includes only fully intact sentences.
- **Strict damage filters.** Linear A/B and EDH units with any damaged sign are dropped, which biases toward short, clear texts.
- **Small systems.** At 150 texts, Old Akkadian (pool 168) and Linear A (244) subsamples overlap heavily, so their variance is understated.
- **Emoji are short** (mean 2.3). Length matching falls back to the nearest available lengths for that system.
- **Squashed probabilities.** The C = 0.3 classifier with corpus-balanced weights squashes P(L) toward 0.5 (range 0.39-0.64). Its decisions, not its probability scale, are what counts. The unregularised version is reported as a sensitivity check.

## Files

All paths are under `experiments/short_labels/` unless shown in full.
- `cdli_extract.py`: CDLI seal legends, tags, bricks and proto-cuneiform → `data/`.
- `build_corpora.py`: Linear A/B, TLA, EDH, emoji, chess, chords, METAR → `data/`.
- `sl_corpora.py`: the registry (label, family, set) and the length-limited pools.
- `sl_calibrate.py [R]`: the battery (`../language_vs_code/lvc_metrics.py`, unchanged) at 565 and 150 texts, 40 replicates → `out/calib.jsonl`.
- `sl_indus.py dev|heldout`: Indus runs.
- `sl_analyze.py [--indus]`: LOSO, LOFO, permutation null, Indus scores, nearest systems → `out/analysis*.{log,json}`.
- `results.json`: key numbers.

Run order from the repo root: `cdli_extract.py`, `build_corpora.py` (both with `python -I`), then `sl_calibrate.py 40`, `sl_indus.py dev`, `sl_indus.py heldout`, `sl_analyze.py --indus`.

## Next experiments

1. **Get a real emblem or mark corpus of the seal genre.** Ask Sproat for the XML corpora (Pictish, kudurru, barn stars, totem poles), or Lee and Jonathan for the Pictish symbol lists. Transcribe a published mason's-mark or potter's-mark catalogue. This is the one comparator class still missing.
2. **Pre-register the opener-closer finding** (finding 3) on fresh systems, for example Akkadian and Elamite seal legends from CDLI, or Proto-Elamite tablets split by register.
3. **Stop adding statistics.** Two calibration sets, built independently, put the ceiling for these 8 structural metrics at Indus size at about 0.6-0.7. Effort is better spent on tests that need meaning: productive morphology, modifiers that move a sign to another slot (README #3), and external correlates.
