# Amendment 2 to mismatch_study (time-depth error, Ugaritic, reimplementation spec)

Written 2026-11-19 (UTC) by agent `paper`. Sealed before any run of the study. It changes nothing in stage 1. Base prereg `mismatch_study.md` (a8d17cb2…), amendment 1 (3908358e…), stage-1 code `mm.py` (04ef0c0f…).

## A. Time-depth calibration: error carried, not hidden (fixed before stage 3)

1. **Spread.** For each dated lineage in amendment 1, B2, we report ΔH per 1,000 years for each script type, and the spread across lineages (min, max, SD).
2. **Leave-one-lineage-out error.** We refit the years → ΔH mapping (ΔH = r·years through the origin, and separately an intercept model; we report both and use the one with the lower error) with each dated lineage left out, then predict its ΔH. The error is E = mean |predicted − observed| / observed ΔH.
3. **Ranges, not numbers.** Every anchors-needed entry in the Indus table is computed at ΔH_low and ΔH_high:
   - ΔH_low = r_min·years_low;
   - ΔH_high = r_max·years_high;
   - r_min and r_max are the smallest and largest leave-one-out rates.

   The entry is the resulting range of anchors, and an open upper end is shown as "> the largest anchors level tested".
4. **The years rule.**
   - **If E > 0.30**, or fewer than 3 dated lineages yield usable data, the Indus results are stated **only in mismatch units**: "if ΔH ≤ x bits/value, k anchors". No years appear.
   - **If E ≤ 0.30**, years may appear, always with the ΔH range beside them.
5. **Sister-language pairs.** Finnish/Estonian, Tamil/Malayalam and Spanish/Portuguese have split dates from the literature. They enter the spread table but not the fit, because their dates are reconstructions, not attested stages.

## B. Ugaritic: no per-script patch

- The Ugaritic prediction uses only the alphabet-type law fitted on the training pairs in stage 3. That means its ΔH (Ugaritic consonantal text against a Hebrew consonantal model, both folded to the shared consonant alphabet), its size and its historical anchors.
- Nothing is fitted, tuned or added for Ugaritic: no script-specific term, no refit after seeing it.
- Snyder et al. 2010 recovered 73% of the alphabet with a Hebrew model. Our related-model recovery in the syllabic regime is 4–26%. The law must reconcile these through the script-type axis alone.
- **Kill under criterion 4 (law framing)** if either holds:
  - the hashed prediction says "not solvable" (below 0.5) with the historical anchors;
  - the run on real Ugaritic with those anchors lands outside the prediction's interval.
- The same holds for Linear B.

## C. Reimplementation specification (enough to rebuild stage 1 without the code)

The red team must land inside these bands:
- planted checks: the same pass/fail;
- kill test: cell means within 0.10.

They may use any implementation. Where this spec and `mm.py` differ, the red team follows this spec, and the difference is reported.

**C1. Text folding (Latin-script languages).**
- Lower-case; Unicode NFKD; drop combining marks.
- Replace y→i, x→ks, z→s, w→v, c→k, q→k.
- Keep a–z only; collapse runs of a repeated letter to one.
- Keep only consonants {p b t d k g m n l r s f v h j} and vowels {a e i o u}.
- Words are maximal letter runs. Paragraphs are split on newlines. Gutenberg headers are removed.

**C2. Value inventories.**
- **Alphabet:** the 20 letters.
- **Syllabary** — syllabify each folded word left to right:
  - each vowel takes the immediately preceding consonant, if any, to form CV;
  - other consonants stand alone as C;
  - a vowel with no preceding consonant is V.
  - Values: 15×5 CV + 15 C + 5 V = 95.
- **Logo-syllabic:** the syllabary, plus the most frequent word types (greedy by frequency, until they cover ≥ 30% of word tokens) written as one logogram sign each.
- All inventories add a LOGO value and a boundary #.

**C3. Simulated corpus.**
- Split the text language's paragraphs alternately: even paragraphs make the corpus (half A), odd ones the true-language model (half B).
- Cut half A into chunks of 1 or 2 consecutive words within paragraphs. P(1 word) = clip(2 − 4.5/w̄, 0, 1), where w̄ is the mean values per word, giving about 4.5 signs per text.
- Shuffle the chunks; drop repeated chunks; take chunks until the token count reaches the target size.
- Each distinct value becomes one sign, and each logogram word one sign. Sign ids are randomly permuted.
- Seeds come from the pair, size, script type and replicate.

**C4. Language models.**
- **Bigram:** over values with the boundary, add-0.1 smoothing.
  - Trained on the model language's text cut into 1–2-word chunks (P = 0.5 each). Each chunk is bounded by # on both sides.
  - The logogram set is chosen on the model text by the same 30% rule.
- **Trigram (A1):** P(c|a,b) = (n(abc) + 2·P_bigram(c|b)) / (n(ab·) + 2), with two # at the start.
- **Related model (K2):** Latin text uses an Italian model; Finnish text uses an Estonian model (Wikipedia intros).
- **True model (K0):** half B.

**C5. Collapsed cipher and objective.**
- All logogram signs are merged into one pseudo-sign whose value is fixed to LOGO. The boundary is fixed to #.
- A key maps each syllabic sign to one of the 95 (or 20) values. Many-to-one is allowed.
- Objective = Σ over sign bigrams (or trigrams, for A1) of count × log P_model(key values), plus the channel term Σ_s c_s log c_s − Σ_v C_v log C_v. Here c_s is the count of sign s, and C_v is the summed count of the signs mapped to value v.
- **Accuracy** = the token-weighted share of syllabic-sign tokens whose sign is mapped to its true value. Logograms are excluded.

**C6. Attacks.**
- **A0.** Annealed Gibbs over signs in random order per sweep. Temperatures fall linearly from 3.0 to 1.0 over 290 sweeps, then 10 greedy sweeps. 4 random restarts; the answer is the restart with the highest objective.
- **A1.** As A0, with the trigram objective and 8 restarts.
- **A2.** EM on an HMM:
  - hidden values follow the model bigram (fixed, # at both ends of each text);
  - each syllabic value emits signs by a free distribution, initialised from Dirichlet(1);
  - LOGO emits only the logogram pseudo-sign;
  - 60 iterations, 10 restarts, the answer is the restart with the highest likelihood;
  - key = for each sign, the value with the largest expected count.
- **A3.** A0 with 1,000 restarts × 100 sweeps (the same schedule shape).
- **Attack gate:** ≥ 0.90 under K0, syllabary, 10k, both pairs.

**C7. Planted checks.**
- **PC2 synthetic source.** 95 values. Each row of P mixes 0.7 × Dirichlet(0.05) with 0.3 × a shuffled Zipf(1) unigram, scaled to 0.8, with P(#) = 0.2. R is an independent draw of the same kind. The attacker gets Q = λP + (1−λ)R, floored at 1e-9 and renormalised.
  - Texts: 3–7 values, drawn uniformly. Corpus: 10k tokens.
  - ΔH = the mean log2 P/Q per value on fresh text from P.
  - Boundary fit: a least-squares logistic in ΔH and log10 n. The planted surface is (a, b, c) = (2, −4, 0.8), with noise SD 0.05.
- **PC3 negative.** The K0 training text's values are shuffled across the whole training text (unigram kept). Frequency-rank baseline: map the i-th most frequent sign to the i-th most frequent model value.
- **Thresholds:** as in the base prereg, sections 4 and 5.
