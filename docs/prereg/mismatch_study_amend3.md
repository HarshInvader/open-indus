# Amendment 3 to mismatch_study (five papers from the library)

Written 2026-11-19 (UTC) by agent `paper`, before any stage-1 result was seen and before any stage-2 code exists. It changes nothing in stage 1 (`mm.py` 04ef0c0f…, `par.py` b577b30a…). Base prereg `mismatch_study.md` (a8d17cb2…), amendments 1 (3908358e…) and 2 (99c94f5c…). Sources: the full-text reads in `docs/library/library.json`. I opened each paper's page or abstract myself; the abstracts confirm the headline findings (Korovina: "accuracy dropping by more than half" under genre mismatch; Zhou & Anderson: the Hittite 34.7% / 35-point figure; Tamburini: 693, 919 and 47.5). The Korovina syllable counts and the Rozanova real-minus-surrogate differential come from the library's full reads, not the abstracts.

Decisions: adopt 1, 2, 3 and 4 (partly); decline 5 for now.

## 1. Genre mismatch (Korovina 2026, https://aclanthology.org/2026.lt4hala-1.16/): adopted

On enciphered Rapa Nui, a model from the cipher's own sub-corpus recovered about 26 syllables. A model from another genre of the same language recovered 10, and a pooled five-genre model 17. So genre alone can halve recovery.

- **Stage 1: no change needed.** The PC1 true model (K0) is already the cipher's own source: the odd paragraphs of the same work whose even paragraphs make the corpus (amendment 2, C3). PC1 therefore measures the same-genre ceiling.
- **Stage 2: genre becomes a planned mismatch point.** Same language, different genre, model from the other genre:
  - Finnish: Kalevala (epic verse) against Finnish Wikipedia (both already local);
  - Latin: Caesar against Latin Wikipedia (to fetch; Latin is not a held-out language).

  For each, we record ΔH and run the core-plane cells (all three script types, the stage-2 sizes, 10 seeds, thinned in the amendment-1 order).
- **Genre enters kill criterion 3.** The genre pairs join the test that one scalar ΔH orders all pairs within a script type with no per-pair corrections. If the genre points fall off the language-mismatch curve, ΔH is not a sufficient mismatch measure, and criterion 3 fails.
- **Why this matters for the existing pairs.** Caesar against Italian Wikipedia mixes genre and language mismatch. ΔH measures their sum, so the law stays in ΔH units. The genre pairs test whether that sum is all that matters.
- **Pooled-genre model.** At 10k, syllabary, we also run a model pooled from both genres of the true language. It is reported as a diagnostic and is not used in the fit.
- **Stage 6 (Indus) ranges widen.** The proxy model languages (Old Tamil, Sanskrit) are literary, while the Indus texts are seal legends, a different genre. So in stage 6, ΔH_high (amendment 2, A3) adds the largest genre ΔH measured in stage 2 for that script type. ΔH_low is unchanged.

## 2. Fitted-surrogate null (Rozanova 2026, https://arxiv.org/abs/2608.17096): adopted as a reported diagnostic

- **What is added.** Next to PC3 (unchanged, with the same pass rule), stage 2 runs the same attack, with the same model, on surrogate cipher texts fitted to the cipher corpus itself:
  - an order-1 surrogate (sign unigram);
  - an order-2 surrogate (sign bigram, including the boundary);
  - each with the same text count and text-length distribution.
- **What is reported.** The best objective per token on the real cipher minus that on the surrogate (mean over 3 surrogate seeds), per pair, size and script type.
- **Expectation, stated now.** The order-2 surrogate keeps exactly the statistics the bigram attacks (A0, A3) use. For those attacks the order-2 differential is therefore expected to be near zero by construction. It is informative for A1 (trigram) and A2, and for the order-1 surrogate with every attack.
- **Status.** A diagnostic, not a kill criterion. Stage 5 also reports it for real Linear B and Ugaritic.

## 3. Tamburini 2025 cognate benchmarks (https://doi.org/10.3389/frai.2025.1581129): adopted as a secondary check in stage 5

- The published cognate lists are Cypriot / Arcadocypriot (693 pairs) and Linear B / Mycenaean Greek (919 pairs), from github.com/ftamburin/CSA_OptMatcher. Before use, we check the repository licence. If it does not allow reuse, we cite the published accuracies only.
- **The check.** For each script, the law's hashed recovery prediction is reported beside the paper's published cognate accuracy, and beside our attack's lexicon-level accuracy on the same list where the data allow. This is a second check only. Their measure is lexicon matching, not running-text sign values, so it does not enter kill criterion 4.
- **Luvian/Hittite (47.5).** It goes on the mismatch curve only if open running text in both languages lets us compute ΔH. Otherwise it is reported as "not placed: no open text for ΔH", and is never placed by guessing a ΔH.

## 4. Lee 2024 (https://arxiv.org/abs/2406.07231): adopted, the novelty claim narrowed

Lee frames jointly trained multilingual models as decipherment. The paper draws an information-theoretic limit on unsupervised cross-lingual learning, and shows that token alignment helps where decipherment is hard: mismatched domains, word order and tokenisation.

- The general claim "unsupervised recovery has a ceiling set by mismatch, and a small dictionary lifts it" is therefore **not claimed as ours**.
- What remains claimed (base prereg, section 1):
  1. a quantitative boundary in ΔH × size × script type that predicts held-out families;
  2. the measured statistical-to-computational crossover;
  3. an anchor exchange rate in signs;
  4. retrodiction of real decipherments.
- Any paper cites Lee 2024 next to Luo 2021 and Dou & Knight 2013.

## 5. Foreign word-signs (Zhou & Anderson 2026, https://aclanthology.org/2026.emnlp-main.2169/): declined for now

On Hittite, where 34.7% of signs are foreign logograms, segmentation fell 35 points. Reasons for not adding a foreign-logogram variant now:
1. Their effect is on word segmentation, not sign-value recovery. In our setup, logograms are collapsed to one pseudo-sign fixed to LOGO (amendment 2, C5), so a foreign logogram would change nothing unless the model is changed too. That is a different study.
2. No sealed Indus hypothesis, and neither retrodiction target, depends on borrowed logograms.
3. It would double the stage-4 logogram-share slice before the core result exists.

We revisit it after stage 3 if the study survives and compute allows. Any such variant would be sealed in its own amendment.
