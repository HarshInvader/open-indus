# Decipherability: is any phonetic reading of the Indus script identifiable?

Decipherability theorist, 2026-11-14. Figure: `phase_diagram.png`. Tables: `out/summary.md`. Numbers: `results.json`. Raw cells: `out/names.jsonl`, `out/prose.jsonl`, `out/anchors.jsonl`, `out/indus_run.json`.

## Conclusion first

1. **The limit is knowing the language, not the amount of text.** We planted five real languages in a simulated logo-syllabic script and ran a strong key search on them.
   - With a perfect model of the language, about 2,500 sign tokens are enough to read 89–99% of sign values. That is a Shannon-style unicity distance of a few hundred to about 2,000 tokens, well under Indus's 10,005.
   - With a related language's lexicon only, or with phonotactics only, the search reads 10–26% of sign values.
   - That share barely moves between 2,500 and 230,000 tokens. Collecting 23 times the Indus corpus does not fix it.
   - In 88–100% of those runs, a key that is mostly wrong scores higher than the true key. The objective itself prefers wrong answers, so better search cannot help. In Shannon's terms, with a mismatched language model the unicity distance is not finite anywhere in the range we tested.
2. **Even with each language's full lexicon, picking the right language does not reach p < 0.01 on name/title texts.**
   - We set the true language against 8 wrong language models and calibrated each model on corpora planted in the other languages. The true language came out on top in 60–100% of corpora at logogram shares ≤ 0.4 (chance is about 11%). That is useful as a ranking.
   - Only Finnish ever cleared p < 0.01, and Finnish is our most synthetic case (20% of corpora, the same at every size).
   - The obstacle is not sampling noise. Some language models fit any short-word corpus better than others, and that per-token bias does not shrink as the corpus grows.
   - Every language model, wrong ones included, beats the frequency-matched shuffle by z > 7. "Beats a shuffled corpus" therefore proves nothing about the language.
3. **Indus sits where nothing is identifiable** (10,005 tokens, names/titles, logogram share unknown).
   - Run on the real corpus, no candidate language model stands out from how it behaves on wrong-language planted corpora. Calibrated z values: Tamil 0.45–0.76, Proto-Dravidian roots and Santali uncalibrated but in the same gain range, Sanskrit about 0, Sumerian 0.3–0.5, Latin about 0, Finnish 1.8–2.3.
   - True languages planted at this size give calibrated z of only 0.3–2.8 (Finnish 5.7). So a null Indus result is what we would expect even if the right language were among the candidates.
4. **What would change this, in order of value:**
   - (a) **A lexicon close to the true language** (dated, same stage, not reconstructed or with only sound-shifted cognates). This moves best-key recovery from about 0.2 to about 0.8.
   - (b) **Anchors.** About 10–20 sign values known from a bilingual name (counted by token frequency) raise total correct reading from 0.17 to 0.47–0.68 even with a related-language lexicon. But the signs that are not anchors stay at 0.30–0.36: anchors are read, they do not unlock the rest.
   - (c) **Longer, continuous texts.** In prose lines, the best key under the true lexicon is 96–99% right from 2,500 tokens, and phonotactics alone reaches 0.6–0.85 best-key accuracy at 10–45k tokens. Names and titles are the worst genre.
   - More seals of the same kind come last: they have almost no value.

## Setup

### Planted languages and text genres (`langdata.py`)
All material is real language, reduced to one shared phoneme alphabet (16 consonants, 5 vowels; length, aspiration, retroflexion and gemination are not written). It is then written as akshara-like units: CV, bare C, bare V, for 101 possible syllable values. The most frequent word types become logograms, one sign per word, until the target share of word tokens is reached. Logogram types are capped at 320 so the inventory stays near Indus's 417 signs; because of the cap, a target of 0.6 achieves 0.49–0.54 in names.

| code | planted name/title texts | decipherer's "full lexicon" (K1) | related language (K2) |
|---|---|---|---|
| san Sanskrit | Rigveda names and epithets, 1–3 word chunks (real) | MW headwords + sa.wikipedia | Pali + Prakrit lexicons |
| tam Tamil | **synthetic** template: [title] name(+case) [title] over Tamil lemmas | ta.wikipedia (lemmas excluded) | Malayalam lexicon + ml.wikipedia |
| sux Sumerian | Ur III seal legends, CDLI (real: names, titles, patronyms) | Sumerian word-form lexicon | none (isolate) |
| lat Latin | EDH Italian inscriptions, 1–3 word chunks (real) | Caesar, *Bellum Gallicum* | it.wikipedia |
| fin Finnish | **synthetic** template over Kalevala names | fi.wikipedia | et.wikipedia |

- When a real corpus runs out at large sizes, it is extended by recombination: formula words (frequency ≥ 10) are kept, and rare "name" words are replaced from the empirical name pool. Only distinct texts are used.
- Prose genre: running text (Caesar, Kalevala, sa/ta Wikipedia) cut into lines of 4–12 signs with no word dividers.
- Knowledge levels:
  - **K0** oracle: a language model trained on disjoint texts of the same genre (upper bound).
  - **K1** the true language's lexicon or text from another source.
  - **K2** a real related language (real sound changes, not simulated ones).
  - **K3** phonotactics only: syllable transitions built from phoneme bigrams, with no words.

### Search (`decipher.py`)
- **Generative model.** Values come from a syllable-bigram language model with word boundaries and a LOGO token. Each sign is emitted by its value through a many-to-one key. The score is the exact corpus log-likelihood, which includes the maximum-likelihood channel term Σc log c that penalises homophony (Knight et al. 2006; Ravi & Knight 2008/2011).
- **Optimiser.** Tempered Gibbs / simulated annealing over the whole key: each sign's conditional is scored over all 102 values at once, with per-token temperature, 150 sweeps, 4 restarts and a greedy polish.
- **Generous assumptions.** The decipherer is told the true logogram share, the scripts have no polyphony, and text edges are word edges in the names genre.
- **Search check.** For each true-language model we also polish starting from the true key. "Best key" = the highest-scoring key found by either route. "Blind" = what a decipherer would actually get.
- **Nulls.** The same search on 2 frequency-matched shuffles (tokens permuted across texts, text lengths kept), and on all wrong-language models.

### Identification test (`analyze.py`)
- We compute gain = (best score on the real corpus − mean best score on shuffles) / tokens for every model on every corpus.
- Each model's gain is z-scored against its gains on corpora planted in the *other* languages: same size and logogram cell, leaving the corpus itself out.
- "Identified at p < 0.01" means the true model's z exceeds a one-sided 99% prediction bound (t, 7 degrees of freedom) and beats every wrong model. "Ranked first" drops the significance requirement.

Number of experiments run:
- 280 name cells (5 languages × 7 sizes × 4 logogram shares × 2 replicates)
- 120 prose cells
- 30 anchor cells
- each grid cell runs up to 12 language models × (1 real + 2 shuffles) searches
- 22 runs on real Indus

## Findings

### F1. With a perfect model, the unicity distance is small. With a realistic model, there is none (names, mean over 5 languages × 2 replicates)

| tokens | logo share | K0 blind | K1 blind / best key | K2 blind / best | K3 blind / best | wrong key beats true: K1 / K2 / K3 |
|---|---|---|---|---|---|---|
| 2,500 | 0.21 | 0.98 | 0.45 / 0.78 | 0.12 / 0.17 | 0.15 / 0.21 | 0.5 / 1.0 / 1.0 |
| 10,000 | 0.00 | 0.92 | 0.51 / 0.78 | 0.12 / 0.19 | 0.14 / 0.37 | 0.2 / 1.0 / 1.0 |
| **10,000** | **0.21** | 1.00 | 0.58 / 0.77 | 0.10 / 0.26 | 0.18 / 0.28 | 0.2 / 1.0 / 1.0 |
| **10,000** | **0.39** | 1.00 | 0.69 / 0.80 | 0.25 / 0.37 | 0.20 / 0.39 | 0.2 / 0.88 / 1.0 |
| 10,000 | 0.52 | 0.99 | 0.69 / 0.83 | 0.19 / 0.42 | 0.17 / 0.39 | 0.3 / 0.88 / 1.0 |
| 50,000 | 0.21 | 0.99 | 0.57 / 0.79 | 0.18 / 0.32 | 0.19 / 0.25 | 0.2 / 0.88 / 1.0 |
| 230,000 | 0.21 | 1.00 | 0.72 / 0.86 | 0.22 / 0.34 | 0.26 / 0.36 | 0.2 / 1.0 / 0.9 |
| 230,000 | 0.49 | 1.00 | 0.71 / 0.82 | 0.22 / 0.40 | 0.23 / 0.62 | 0.2 / 1.0 / 1.0 |

- "Wrong key beats true" means the blind search found a key with under 50% of values right that scores above the true key. The fraction for K1 comes almost entirely from Finnish, where the modern-Wikipedia lexicon fits Kalevala names poorly (K1 best-key accuracy 0.16–0.48).
- Under K1, Sumerian, Latin and Tamil reach 0.92–1.00 best-key accuracy at 10k tokens; Sanskrit reaches 0.67–0.84.
- Excess log-likelihood of the best wrong-ish key over the true key: K1 0.05–0.14 nats/token, **K2 0.64–0.89**, K3 0.17–0.41. This gap does not shrink with corpus size: it is a per-token property of model mismatch.
- Shannon estimate U = S·log2(102) / (log2 102 − H), with H = the true stream's cross-entropy under the decipherer's model. For K0 it gives U ≈ 250 (no logograms) to 1,900 tokens (share 0.4), which fits the near-perfect K0 recovery at 2,500 tokens. For K2 the redundancy left after mismatch is ≤ 0, so U = ∞. That matches the flat K2 rows.

### F2. Language identification does not reach p < 0.01 on name/title texts, and size does not help

| | names, all sizes, share ≤ 0.4 | names, share 0.5 | prose, 10k, share 0 |
|---|---|---|---|
| true language ranked first (calibrated, of 9) | 0.70–1.00 | 0.20–0.70 (falls with size) | 1.00 |
| true language identified at p < 0.01 | 0.20 (Finnish only) | 0.20 | 1.00 (0.50–0.75 at other sizes) |
| related language (K2) ranked first, true lexicon absent | 0.12–0.38 | 0.25–0.38 | 0.25 |
| wrong models significant vs calibration (false positives) | 0.00–0.01 | 0.00 | 0.00–0.04 |
| min z of true model vs shuffle | > 7 | > 7 | > 7 |

- Typical calibrated z of the true K1 model at 10k tokens, share 0.2: Sumerian 2.8 / 1.5, Tamil 1.1 / 1.3, Latin 0.9 / 0.9, Sanskrit 0.5 / 0.3, Finnish 5.8 / 5.7. At 230k tokens the values are nearly the same (Sumerian 2.3 / 3.0, Tamil 2.0 / 1.9, Latin 1.3 / 1.3, Sanskrit 0.5 / 1.1).
- With only 5 candidate languages, a ranking alone can give at best p = 1/5 to 1/9. Reaching p < 0.01 needs a calibrated null, and between-language heterogeneity makes that null wide.
- K2 identification sits at the floor: only Estonian→Finnish works. Pali/Prakrit does not pick out Sanskrit, Malayalam does not pick out Tamil, and Italian does not pick out Latin.

### F3. Genre matters more than size (prose vs names)
Prose lines, mean 8 signs, 4 languages:
- K1 best-key accuracy is 0.96–0.99 at every size from 2,500 tokens, against about 0.8 for names.
- K3 phonotactics best-key accuracy rises from 0.29–0.61 at 2,500 tokens to 0.60–0.95 at 25–45k.
- K2 best-key accuracy rises from 0.19–0.50 to 0.60–0.62.
- Blind K2 search stays at 0.05–0.13: the search cannot find these keys, so the gains would need anchors or better optimisers.

Function words, repetition and morphology supply the redundancy that names lack.

### F4. Anchors (10k tokens, names, logogram share 0.2 and 0.4, 3 replicates × 5 languages)

| known values K | tokens covered by anchors alone | total read right K1 / K2 / K3 | non-anchor tokens right K1 / K2 / K3 |
|---|---|---|---|
| 0 | 0.00 | 0.60 / 0.17 / 0.17 | 0.60 / 0.17 / 0.17 |
| 5 | 0.16 | 0.78 / 0.37 / 0.40 | 0.74 / 0.25 / 0.28 |
| 10 | 0.26 | 0.84 / 0.47 / 0.48 | 0.78 / 0.30 / 0.30 |
| 20 | 0.52 | 0.89 / 0.68 / 0.67 | 0.77 / 0.35 / 0.31 |
| 40 | 0.81 | 0.95 / 0.88 / 0.87 | 0.73 / 0.36 / 0.28 |

- Anchors are drawn token-weighted, so they behave like the frequent signs in a name.
- **With the right lexicon**, 5–10 anchors mainly rescue the search: non-anchor accuracy rises from 0.60 to 0.74–0.78. Sumerian goes from 0.47 to 0.99 with 10 anchors.
- **With a related lexicon or phonotactics**, anchors lift the non-anchor signs only from 0.17 to about 0.30–0.36, then plateau.
- For the field, a bilingual matters mainly as a **test**. A key fixed by a bilingual's 10–20 values, which then reads further texts into words of a *specific* dated language, is evidence. Anchors do not substitute for knowing the language.

### F5. Real Indus run (`indus_run.py`)
- Same search on the 2,270 distinct M77 texts (2,413 break-free runs, 10,005 tokens, 417 signs), logogram share guessed at 0.2 or 0.4.
- Gains per token: Tamil K1 0.87–0.89, Santali 0.63–0.83, Latin 0.64–0.81, Malayalam 0.74–0.79, Finnish 0.70–0.71, Proto-Dravidian roots 0.59–0.70, Sumerian 0.59–0.60, Sanskrit 0.58–0.59.
- Against each model's gains on wrong-language planted corpora (10k tokens):
  - Tamil z = 0.45–0.76
  - Malayalam 0.31–1.05
  - Sanskrit −0.01 to 0.25
  - Sumerian 0.33–0.54
  - Latin about −0.2 to 0.4
  - Finnish/Estonian 1.0–2.3
- None exceeds the p < 0.01 bound (≈ 3.4). Finnish is highest only because the Finnish model has a narrow null.
- Tamil's raw gain is the highest, but Tamil also scores high on corpora that are not Tamil. Its own-language planted mean is 0.96–1.00, its wrong-language mean is lower, and Indus falls in between. This **is not evidence for Dravidian**.

## Hypotheses

| hypothesis | verdict |
|---|---|
| H1 A correct phonetic key for Indus is identifiable from internal evidence + the true language's lexicon at 10k tokens | **inconclusive, leaning no**: best key about 0.8 right, but the language is not identifiable at p < 0.01 on names |
| H2 Same, with only a related/reconstructed language (the realistic Indus case) | **refuted in simulation**: 10–26% recovery, wrong keys beat the true key 88–100% |
| H3 More inscriptions of the same kind (up to 23×) make it identifiable | **refuted**: flat from 2.5k to 230k tokens |
| H4 Beating a frequency-matched shuffle shows a language fits | **refuted**: every wrong language model beats the shuffle by z > 7 |
| H5 Anchors (bilingual names) unlock the rest of the key | **partly**: they help strongly with the right lexicon, only to about 0.35 non-anchor accuracy with a related one |
| H6 Longer continuous texts help more than more seals | **supported** |
| H7 Any tested language (Tamil/Malayalam/Proto-Dravidian/Santali/Sanskrit/Sumerian) fits real Indus better than wrong languages fit planted corpora | **not supported** (all z < 2.3) |

## Simulator assumptions (how this could mislead)
- **Optimistic for the decipherer.** One sign per syllable (no polyphony, no allographs), the true logogram share given, the logograms being exactly the most frequent words, text edges = word edges, a known reading direction, and no scribal errors. Real Indus is harder on every count, so the negative results are lower bounds on the difficulty.
- **Possibly pessimistic.**
  - Bigram language model only. Trigram or word-level models (Snyder et al. 2010 used lexicon matching with cognate edit models) would extract more from K1/K2.
  - Blind search under-reaches the best key by 0.1–0.4. The "best key" column uses the true key as a starting point, which is an upper bound.
  - K2 lexicons are small (Pali+Prakrit 5.3k types) and ASCII-folded.
- **Shared phoneme alphabet.** Length, aspiration and retroflexion are merged for every language, which makes all languages look more alike and hurts identification. Real scripts often write some of these.
- **Genre realism.**
  - Tamil and Finnish names are synthetic templates; Finnish behaves as an outlier throughout.
  - Latin and Sanskrit "names" are chunks of longer inscriptions and verse.
  - Mean text length is 6–10 signs (Indus 4.4), which is again optimistic.
- **Replication.** Only 2 replicates per name cell, so each cell estimate is ±0.1–0.2. The trends across 7 sizes are the robust part.
- **Uncalibrated models.** Proto-Dravidian and Santali models were run on Indus but have no planted calibration.

## What would falsify the main claim
A blind search, given only a related or reconstructed lexicon, recovers more than 50% of sign values on planted name corpora of ≤ 10k tokens. Or a fixed key scores above wrong-language and shuffle nulls on *new* Indus texts that were held out before fitting.

## Next experiments
1. Replace the bigram model with a word-level model plus a cognate edit channel (Snyder 2010 / Luo et al. 2019 NeuroDecipher) and redo K2. This is the strongest available counter to F1.
2. Add polyphony/allographs and Indus-like 4.4-sign texts, and use Indus's own sign-frequency profile as the inventory.
3. A bilingual-name simulator: anchors restricted to the signs of 1–3 specific names, rather than frequency-weighted draws.
4. A larger calibration panel (≥ 15 languages) so that p < 0.01 is reachable by ranking.
