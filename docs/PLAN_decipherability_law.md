# Plan: decipherment under language-model mismatch (2026-11-19)

The owner asked for a paper that leading researchers would call a breakthrough, within days. This plan was made with Fable 5.2 (brief `docs/fable_brief7.md`, answer `experiments/fable52_plan8.md`). The novelty check against the actual papers is being written to `experiments/survey_2026/NOVELTY_decipherability.md` and will update the odds below.

## Honest verdict first

- **Fable's estimate that leading researchers in both communities call it seminal within days: about 2%.** Indus specialists reserve "breakthrough" for readings, and we have none. Seminal status is conferred over years.
- **Best honest target:** a solid top-venue computational paper (ACL, EMNLP or TACL) with the Indus script as its main application. Working title: "More text does not help; here is what does, quantified".
- **"No paper" is a live outcome, at about 50%.** The rule stands: a paper goes out only if the sealed kill criteria pass.

## Top pick: the mismatch study

**Claim to test.** Suppose a script is attacked with a model of a related language, not the true one. Then sign-value recovery plateaus at a level set by the mismatch, not by corpus size. Known values (anchors) are what lifts it. The study delivers an exchange rate: anchors needed, as a function of mismatch and corpus size.

**What may be new.** Pending the novelty check:
- a measured plateau against one scalar mismatch measure, flat in corpus size;
- the split between statistical failure (the objective prefers wrong keys) and computational failure (right keys score best but search can't reach them), and where the crossover sits;
- the anchor exchange rate;
- retrodiction of real decipherments (Cypriot syllabary, Linear B, Ugaritic);
- wrong-language nulls as a required standard for claims.

**Already known** (not claimed as ours):
- size requirements under the true model (Shannon's unicity distance; Ravi & Knight 2008);
- that restarts and model order matter (Berg-Kirkpatrick & Klein 2013; Nuhn et al. 2013);
- the spirit of the shuffle trap (Sproat's critique of Rao et al.);
- the theory that a wrong-model maximum-likelihood estimate converges to a "pseudo-true" key (White 1982).

## Evidence already in hand (exploratory, not confirmatory)

**The deciding measurement Fable asked for.** In the red-team runs (`experiments/redteam_decipherability/out/runs.jsonl`), we compared the key reached by climbing from the truth with the best blind key. Count of runs where the truth-climbed key scores higher:

| Pair | 2.5k | 10k | 30k |
|---|---|---|---|
| Latin text, Italian model | 6/6 | 6/6 | 6/6 |
| Finnish text, Estonian model | **0/6** | 3/6 | 6/6 |

- For Finnish/Estonian, failure is **statistical at 2.5k** (the objective's best keys are wrong), mixed at 10k, and **computational by 30k**.
- For Latin/Italian it is computational at every size tested.
- So there is a statistical-to-computational crossover that moves with corpus size and mismatch. Fable flags this as possibly the real finding. It was found after the fact, so the sealed study must confirm it on new pairs.

**Search scaling** (`experiments/search_scaling`, sealed): 200 restarts at 2.5k give best-of-n accuracy of 0.07, 0.10, 0.12, 0.14 and 0.17 for n = 1, 4, 10, 50 and 200. Not a search artefact at 2.5k (sealed verdict H0). Every restart outscored the true key.

## Sealed design (to be hashed before any run)

- **Mismatch axis.** Interpolated models q = λ·true + (1−λ)·related, λ in 8 steps, plus real sister languages.
  - Metric: excess cross-entropy, in bits per syllable, on held-out text.
  - Secondary metric: cognate share.
- **Training pairs.**
  - Latin with Italian, Spanish and Romanian.
  - Finnish with Estonian and Hungarian.
  - Tamil with Malayalam and Telugu.
  - The same language across genres.
- **Held-out families.** Turkic, Slavic and Germanic. Untouched until the fitted boundary is hashed.
- **Core plane.** λ × size (1k, 2.5k, 5k, 10k, 30k, 100k), 10 seeds, 50 restarts.
- **Slices at 10k.**
  - anchors 0, 5, 10, 20, 40;
  - text length 5, 20, continuous;
  - logogram share 0, 0.3, 0.6.
- **Every cell records:**
  - blind best score vs truth-climbed score (statistical vs computational);
  - basin radius: start with k% of the key correct and see where the climb ends. This is the anchor estimator.
- **Planted checks.**
  - a true-model control at ≥ 0.9 everywhere;
  - synthetic Markov sources with dialled KL, so the fit must recover a known boundary;
  - a shuffled-language negative.
- **Real scripts.** Cypriot syllabary with Greek, Linear B with Greek, Ugaritic with Hebrew, given the historically available anchors. Predictions hashed before running.
- **Indus, Linear A, Rongorongo.** Conditional statements only, e.g. "if the language is within Δ of candidate X, at least k anchors are needed".
- **Red team.** An independent reimplementation must land inside pre-set bands.

## Kill criteria (sealed with the design)

1. The boundary fitted on training pairs predicts held-out families with mean absolute error ≤ 0.10 and ≥ 90% of cells on the correct side. Otherwise no "law".
2. **Attacker-invariance.** The plateau holds within 0.10 across at least three attacks: a trigram or higher model; EM or beam search; ≥ 10^4 restarts. If any attack lifts related-model recovery above 0.5 at ≤ 30k, kill.
3. One scalar mismatch measure orders all pairs, with no per-pair corrections. Otherwise kill.
4. Linear B and Ugaritic land on the solvable side given their historical anchors. One miss kills the "law" framing.
5. The statistical-versus-computational call is unambiguous in ≥ two thirds of cells. Otherwise no paper.
6. The red-team reimplementation lands inside the pre-set bands.

## Odds (Fable 5.2; to be revised after the novelty check)

| Outcome | Odds |
|---|---|
| Clean result (held-out prediction and attacker-invariance pass) | 35% |
| Top-venue acceptance, given a clean result | 45% (about 15% overall) |
| PNAS | 3% |
| Called seminal by both communities | 1-3% |
| Any finished paper in 5 days | 50% |

The likeliest failure is attacker-invariance: a stronger attack (a higher-order model, beam search, many restarts) might lift recovery and break the plateau.

## Order of work

1. Finish the search_scaling write-up. The job is still running and holds the compute lock.
2. Read the novelty check and revise this plan if prior work already covers a piece.
3. Write and hash the sealed design and code. Order: core plane first, then slices, then real scripts.
4. Run under the compute lock at background priority. Ask the owner before any paid GPU. A ≥ 10^4-restart attack may need it.
5. Red team, then verdict against the kill criteria. Write the paper only if the criteria pass. If they fail, add an atlas entry.
