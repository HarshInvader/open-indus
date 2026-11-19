# Ideas from the library, most promising first

Drawn from `library.json` (2026-11-19). These are ideas, not studies. None has been started, and none changes a sealed prereg; the ones touching the mismatch study are notes for its thread to weigh at the next amendment.

## 1. Measure the mismatch of each genre pair, and build the true-model control from the cipher's own genre

- **Source:** `korovina-2026-rongorongo-syllabic` (read in full). On enciphered Rapa Nui, a model from the same sub-corpus recovered about 26 syllables. A model from another genre of the same language recovered 10, and the worst pair 4.6. A pooled five-genre model recovered 17.
- **What is untested:** whether genre mismatch sits on the same ΔH-versus-recovery curve as language mismatch, or forms its own curve.
- **Open data:** yes. Any two genres of one language in the mismatch study's training pool will do, for example the Greek or Latin genre splits already used.
- **Bears on:** the mismatch study, directly.
  - The prereg lists "the same language across genres" as a training pair. This paper shows such a pair is not a near-zero-mismatch point.
  - Planted check PC1 (the λ=1 true model) must come from the same genre and sources as the ciphertext, or it will understate the ceiling.
  - For the thread to decide: record ΔH for every genre pair, and treat a pooled-genre model as a cheap anchor-free way to close part of the gap.

## 2. Add a fitted-surrogate null next to the shuffled negative

- **Source:** `rozanova-2026-voynich-units` (read in full). Each real text is compared with a surrogate fitted to the same corpus (an order-k generator).
  - The real-minus-surrogate differential was positive in all 25 right-language runs (+0.13 to +0.52) and near zero for Voynich (mean −0.0085).
  - Right-language recovery was 73.7–92.6%; wrong-language recovery was 0–23.4%.
- **What is untested:** whether our attacks beat a surrogate fitted to the same statistics. A shuffled text is a weaker null, because it destroys the n-gram structure the attack exploits.
- **Open data:** yes. The surrogate is fitted to the cipher corpus itself.
- **Bears on:** the mismatch study (beside planted check PC3) and any reopened "is it language" test. It also gives a second wrong-language point for the curve.

## 3. Use the Tamburini benchmarks for the real-script retrodiction

- **Source:** `tamburini-2025-csa-optmatcher` (read in full), which publishes cognate lists for three script pairs:
  - Cypriot syllabary and Arcadocypriot Greek: 693 pairs.
  - Linear B and Mycenaean Greek: 919 pairs.
  - Luvian and Hittite (same script, different language): cognate accuracy 47.5, a ready far-mismatch point.
- **What is untested:** whether our mismatch curve, fitted on synthetic pairs, predicts these published accuracies. Theirs are lexicon-level cognate matches, not running-text sign values, so use them as a second check, not a replacement.
- **Open data:** yes (github.com/ftamburin/CSA_OptMatcher).
- **Bears on:** stage 5 of the mismatch study (Cypriot, Linear B and Ugaritic retrodiction). Reusing a public benchmark makes the retrodiction comparable with other groups.

## 4. A "foreign word-signs" variant in the logogram-share slice

- **Source:** `zhou-anderson-2026-cuneiform-transfer` (read in full). Dictionary-free segmentation carried over between cuneiform languages with F1 above 0.95. On Hittite, where 34.7% of signs are foreign-script logograms, it fell 35 points.
- **What is untested:** whether logograms borrowed from another language add mismatch on top of native logograms, at the same logogram share.
- **Open data:** yes (ORACC, ETCSL and the Hittite corpora the paper used).
- **Bears on:** the logo-syllabic arm of the mismatch study. This is a possible later slice; stage 1 is sealed.

## 5. Report bits as well as rank for every structural test

- **Source:** `zenil-2026-undeciphered-structure` (read in full).
  - Indus row breaks were ranked with AUC 0.812 (0.742–0.871) but carried only 0.0092 bits per gap.
  - The data: 292 gaps in 47 inscriptions, with Mohenjo-daro held out.
- **What is untested:** our `line_breaks` test reports placement against a null, not information content.
- **Open data:** yes (our corpus, with positions).
- **Bears on:** the line_breaks prereg, and reporting in the mismatch study (recovery accuracy and per-sign information).

## 6. Do seal counts follow house size in Mohenjo-daro's DK-G South?

- **Source:** `green-2026-mohenjo-gini` (read in full).
  - The Gini of house areas fell from 0.39 (c. 2500 BC) to 0.23 (c. 2100 BC) in DK-G South.
  - The overall Gini was 0.44 (n = 162).
- **What is untested:** whether seal finds per house track house size, which tests "seals are elite markers".
- **Open data:** partly. House areas are in the paper. Seal find-spots per house need the Mackay/Marshall registers, which our find-spot table only partly covers.
- **Bears on:** the find-spot and administration line of work, not the mismatch study.

## 7. Do sign sequences follow the cattle route?

- **Source:** `mahala-2026-bovine-isotopes` (abstract only). Kanmer bovines were of possibly non-local origin, likely Haryana, more than 900 km away.
- **What is untested:** whether Kanmer inscriptions share more n-grams with Haryana sites than distance alone predicts.
- **Open data:** yes, if Kanmer's seals and sealings are in the corpus with site tags. Check the coverage first.
- **Bears on:** the regional-variation studies.

## 8. Treat site loss as a covariate when comparing sites

- **Source:** `gerrits-2026-hexagon-haryana` (read in full). Non-cropland fell from 35% (1915) to 14% (1975) to 4% (2021). Built-up land within 1 km of Rakhigarhi rose from 3.9% to 23.7%.
- **What is untested:** whether inscription counts per site in Haryana track excavation effort and site loss more than ancient use.
- **Open data:** partly. The paper's percentages are public; the rasters are withheld.
- **Bears on:** any per-site comparison of sign use.

## 9. Late-phase test cases with known dates

- **Sources:**
  - `gupta-kumar-2026-rakhigarhi-rgr3` (abstract only): a steatite seal in AMS-dated layers, c. 2000–1800 BCE.
  - `swaroop-2026-jognakhera-bara` (abstract only): the farming package continued after 4.2 ka.
- **What is untested:** whether late inscriptions differ in sign inventory or length from Mature ones, using objects with direct dates rather than period labels.
- **Open data:** no, until the RGR-3 seal's text is published.
- **Bears on:** the chronology work. Status: waiting.

## 10. Rotate held-out folds and add an untrained control to the restoration bench

- **Source:** `cullhed-2026-stoicheia`.
  - Released as ten rotated decontaminated folds, so every text is unseen by one model.
  - Pretraining added 5.6 CER points against a random-initialisation control.
- **What is untested:** our bench already removes near-copies, but it has no rotated folds and no matched untrained control.
- **Open data:** yes.
- **Bears on:** the restoration benchmark, not the mismatch study.

## Papers that should change a current plan (for the mismatch thread)

1. **Korovina 2026.** Genre mismatch is large. PC1 should use the cipher's own genre, and genre pairs need a measured ΔH (idea 1).
2. **Rozanova 2026.** Add a fitted-surrogate null and report real-minus-surrogate (idea 2).
3. **Tamburini 2025.** Use the published Cypriot, Linear B and Luvian cognate benchmarks as a second check in stage 5 (idea 3).
4. **Lee 2024** (`lee-2024-decipherment-aware-multilingual`). It narrows the novelty claim: a cross-perplexity ceiling lifted by dictionary anchors is already shown there. Cite it in the novelty note.
5. **Zhou and Anderson 2026.** Consider a foreign-logogram variant in the logogram-share slice (idea 4).
