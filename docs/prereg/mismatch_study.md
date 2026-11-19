# Pre-registration: mismatch_study (decipherment under language-model mismatch)

Written 2026-11-19 (UTC) by agent `paper`, before any run of this study. This is the plan in `docs/PLAN_decipherability_law.md` (Fable 5.2, plan 8), revised by the novelty check (`experiments/survey_2026/NOVELTY_decipherability.md`).

Only stage 1 code is sealed now: `experiments/mismatch_study/mm.py`. Later stages are fixed here in design. Their code will be hashed before they run, and must implement this document without change. A smoke test (600 tokens, 15 sweeps, nothing written to `out/`) checked only that the code runs, and that the bigram and trigram update steps equal full rescoring.

## 1. Claim under test

A script is attacked with a model of a related language, not the true one. The claim: sign-value recovery then plateaus at a level set by a measurable mismatch, not by corpus size, and anchors are what lift it. Already known and not claimed as ours:
- that mismatch hurts (Luo 2021; Knight 2006);
- that anchors help (Luo 2021; Kambhatla 2023);
- that a plateau appears in decipherment for translation (Dou & Knight 2013).

What would be new:
1. a quantitative boundary (recovery as a function of mismatch × size × script type) that predicts held-out language families;
2. the statistical-to-computational crossover;
3. an anchor exchange rate;
4. retrodiction of real decipherments.

## 2. Axes

- **Script type** (new axis, from the novelty check: Snyder 2010 recovered 73% of the Ugaritic alphabet with a Hebrew model):
  - alphabet: about 20 letter values;
  - syllabary: CV, C and V values, 95 in all;
  - logo-syllabic: the syllabary plus the most frequent words written as logograms, covering 30% of tokens.
  - Values come from the shared folding in `rt.py`.
- **Mismatch.** Interpolated models q = λ·true + (1−λ)·related (in probability), λ ∈ {1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.3, 0}, plus the real related language.
  - Metric: excess cross-entropy ΔH, in bits per value, of the attacker's bigram model over the true-language bigram model, on held-out true-language text.
  - Secondary metric: cognate share.
- **Size.** 1k, 2.5k, 5k, 10k, 30k and 100k tokens. Text length as in `rt.py` (about 4.5 signs per text).
- **Slices at 10k.**
  - anchors 0, 5, 10, 20, 40: the most frequent signs, given their true value and held fixed;
  - text length 5, 20 or continuous;
  - logogram share 0, 0.3, 0.6.

## 3. Language pairs (text language / model language)

- **Training pairs** (boundary fitted on these):
  - Latin / Italian, Spanish, Romanian;
  - Finnish / Estonian, Hungarian;
  - Tamil / Malayalam, Telugu;
  - the same language across genres.
- **Confirmation pairs for the crossover.** The crossover was found after the fact on Latin/Italian and Finnish/Estonian, so it must be confirmed on pairs never used for it: Spanish / Portuguese, Tamil / Malayalam, Estonian / Finnish (reverse direction), Indonesian / Malay.
- **Held-out families: Turkic** (Turkish / Azerbaijani), **Slavic** (Czech / Slovak), **Germanic** (Dutch / German). No text from these is downloaded, inspected or run until the fitted boundary (stage 3) is hashed.
- **Real scripts** (stage 5): Cypriot syllabary / Greek, Linear B / Greek, Ugaritic / Hebrew, each with its historically available anchors. Predictions are hashed before running.

## 4. Stage 1a: planted checks (run first; sealed code `mm.py`)

- **PC1, true-model control.** True-language model (K0), 2.5k tokens, all three script types, both pairs, attack A0. Pass: score-selected accuracy ≥ 0.90 in all 6 cells.
- **PC2, dialled-KL synthetic sources.** A sparse random bigram source over 95 values. The attacker gets q = λ·P + (1−λ)·R (R an independent source), exact probabilities, λ ∈ {1, 0.8, 0.6, 0.4, 0.2, 0}, 10k tokens, 2 replicates, attack A0. Pass needs all three:
  - mean accuracy ≥ 0.90 at λ = 1;
  - Spearman(λ, accuracy) ≥ 0.8;
  - the boundary-fitting routine `fit_boundary` recovers a planted logistic surface's boundary at 10k within 10%.
- **PC3, shuffled-language negative.** A model trained on true-language text whose value order is shuffled (unigram kept), syllabary, 10k, both pairs. Pass: accuracy ≤ the frequency-rank baseline + 0.05 in both.
- If any planted check fails, stage 1b does not count. The failure is reported, the code fixed, and the fix resealed with a note.

## 5. Stage 1b: attacker-invariance kill test (kill criterion 2, run before anything costly)

Syllabary, related-language model (Italian for Latin, Estonian for Finnish).

Attacks. Each picks its answer by its own objective, never by accuracy:
- **A0:** bigram model plus channel term, annealed Gibbs, 4 restarts × 300 sweeps (the red-team attack).
- **A1:** trigram model (add-k back-off to the bigram, k = 2) plus channel term, annealed Gibbs, 8 restarts × 300 sweeps.
- **A2:** EM on a hidden-Markov model (values hidden, the model's bigram as fixed transitions, free P(sign | value)), 10 random restarts × 60 iterations. The answer is the highest-likelihood restart.
- **A3:** A0's search with 1,000 restarts × 100 sweeps, at 10k and 30k (replicate 0).
- **A3+:** the ≥ 10^4-restart attack runs only if the owner approves paid GPU. Without it, A3 is reported as 10^3 and labelled so.

Cells: A0, A1 and A2 at 2.5k, 10k and 30k × 3 replicates × 2 pairs; A3 as above.

**Attack gate.** Each of A0, A1 and A2 must reach ≥ 0.90 under the true model (syllabary, 10k, both pairs). An attack that fails its gate is uninformative and does not count. A3 counts if A0 passes.

**Kill rules (fixed now):**
- **KILL** if any valid attack's mean accuracy in any pair × size cell (≤ 30k) exceeds 0.50. The study stops, an atlas entry is written, and there is no paper.
- **Fewer than 3 valid attacks:** uninformative. Fix, reseal with a note, rerun the kill test.
- **Plateau check:** survival with all valid attacks within 0.10 of each other in every cell means the plateau is attacker-invariant. Survival with a spread above 0.10 means the core plane uses the strongest attack, chosen as the attack with the highest mean accuracy over cells, and the claim is stated relative to it.

## 6. Later stages (design fixed now; code sealed before each runs)

- **Stage 2, core plane.** λ × size × script type, 2 training pairs per family, 10 seeds, the strongest valid attack (50 restarts). Every cell records:
  - the best blind score against the score of the key climbed from the truth (statistical vs computational failure);
  - basin radius: starting at k% of the key correct, does the climb end ≥ 0.9.
- **Crossover confirmation (sealed prediction).** On the four confirmation pairs, related model, syllabary, 2.5k / 10k / 30k, 6 replicates. Count, per pair and size, the share of replicates where the truth-climbed key outscores the best blind key. Confirmed if both hold:
  - pooled share at 30k minus pooled share at 2.5k ≥ 0.33;
  - in at least 3 of 4 pairs the share does not fall from 2.5k to 30k.
- **Stage 3, the fitted boundary.**
  - Fit: logistic, accuracy ~ σ(a + b·ΔH + c·log10 n) per script type. A model with an anchor term is added in stage 4.
  - Hash the fitted parameters.
  - Then download the held-out families and predict them.
- **Stage 4, anchor slice** (board #51). Exchange rate: anchors needed to reach 0.5 recovery, as a function of ΔH and size.
- **Stage 5, real scripts.** Retrodiction with hashed predictions.
- **Indus, Linear A, Rongorongo:** conditional statements only.

## 7. Kill criteria (all sealed; a paper only if all pass)

1. The held-out families are predicted with mean absolute error ≤ 0.10 and ≥ 90% of cells on the correct side of 0.5.
2. Attacker-invariance, as in section 5.
3. One scalar mismatch measure (ΔH) orders all pairs within a script type, with no per-pair corrections.
4. Linear B and Ugaritic land on the solvable side given their historical anchors. One miss kills the "law" framing.
5. The statistical-versus-computational call is unambiguous in ≥ two thirds of cells. Unambiguous means all replicates agree, or ≥ 5/6 do.
6. An independent red-team reimplementation lands inside the pre-set bands: recovery within 0.10 and the boundary within 15%.

**Process rule.** If the study fails, the failure is the result: an atlas entry and a short note. The restoration audit is not substituted for it.

## 8. Compute

Laptop, background priority, at most 2 workers, under the shared compute lock, queued after the Open Mind DREAM extraction. Paid GPU only with the owner's approval.
