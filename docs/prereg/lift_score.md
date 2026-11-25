# Lift score: does a word-and-fragment likelihood, added to a sign trigram, give the true Linear B key a held-out restoration gain that keys fitted to noise do not get?

Status: **v3, sealed** 2026-11-25 (tag `lift_score`). Revised after a fresh review ("FIX, then seal") and a coordinator decision on the 2027 clause; see "Decisions" and the review log. Drafted after `lift_certify` stopped at K0. Main line (a), the claim bench. Kind ii (a read script used as a known-answer control). A label-free pilot on planted text was run before this draft, and the reviewer ran a wrong-lexicon check on the same pilot plants; both are disclosed in full below.

## Question
- `lift_certify` showed that one score (trigram plus λ × lexicon-covered consonants, top-1 hit rate) gives no restoration lift even on text made only of lexicon words.
- **Q1.** Does a different score pass that planted test at Indus shape? The score here is a word-level likelihood, summed over all segmentations of the chunk, with word fragments at the chunk edges and word weights learned from the development half.
- **Q2.** If it does: on real Linear B, is the true key's gain at least 0.02 nats per masked sign, while keys fitted to noise gain at most 0.005?
- **No Indus key is scored in this study. No Indus text is restored, masked or read with any key. No outcome supports or counts against any Indus key, and none licenses a run of one.**

## Why
- This is the only open study tied to the held-out-prediction clause of the 2027 bar.
- **G is this study's own gate, not the 2027 measure.** G (with bars A to C) grades K0 to K4. Hit@1 stays the measure for the 2027 held-out-prediction clause and is reported on every cell. **A G pass alone does not meet the 2027 clause.** (Coordinator decision, 2026-11-25.)
- `lift_certify` named four causes for its K0 failure: chance coverage at 81% of positions, about 19 candidates tied at the maximum, 8.6% of positions inside an intact planted word, and a count of covered consonants as the only signal. Each is a property of that score, not of the route.
- This study gets one sealed attempt. See "Route rule".

## Count gate
- **Need:** about 1,000 clean held-out positions per draw. The pilot's per-position standard deviation of the gain is 0.3 to 0.6 nats at λ ≤ 0.5, so 1,000 positions give a per-draw standard error of at most 0.019 nats, below the 0.02 bar.
- **Have:** 1,376 (1,278-1,524) clean positions per Linear B draw, as measured for `lift_certify` and reproduced by its check A2. **Passed, narrowly:** a true gain of exactly 0.02 would clear the bar in about half the draws; the 16-of-20 bar needs a true gain of about 0.035.

## Kill tests, run first and in this order (strongest first)
All plants are synthetic. Their answers are known by construction. G is the gain defined under "Frozen scoring".

1. **K0, planted language, full dose.** Fresh plants, draws 1 to 5 (new seeds; not the pilot's plants and not `lift_certify`'s).
   - True key: **G ≥ 0.10 nats in 5 of 5.**
   - The same key on the unigram scramble of that text: **G ≤ 0.005 in 5 of 5.**
   - Twenty shuffled keys (N1): **median G ≤ 0.005 in 5 of 5.**
   - **K0 is a replication of the pilot at half its lowest gain** (bar 0.10; the pilot's lowest full-dose G was 0.208). **K1 is the real test.**
   - Any bar missed: stop. The route rule applies.
2. **K1, planted language at the true key's real dose (power).** 20 draws.
   - Dose statistic D: the cross-fitted lexicon log-likelihood ratio per consonant on the development half (defined below). It uses no held-out text and no masking.
   - The target for draw k is D of the true key on the real development half of draw k. This is the first real-text number the study computes. It sets a dose and grades nothing.
   - The plant is diluted with Markov filler until its D is within 0.005 of the target.
   - Bar: **G ≥ 0.02 in ≥ 16 of 20.**
   - Missed: the study is **unpowered** and the route rule applies. K2 and K3 then run once, record-only, and K4 does not run. A K3 pass after a K1 fail is logged as "plant harsher than real text; K1 invalid as a power test"; the route stays closed and the K1-fails reading stands.
3. **K2, real text, negative controls.** Draws 1 to 20, real Linear B.
   - True key on unigram-scrambled text (the scramble as in `lift_certify/run.py`; trigram, word model and key all on the scramble): G ≤ 0.005 in ≥ 19 of 20.
   - Shuffled keys (the first 20 sealed N1 keys per draw): median G ≤ 0.005 in ≥ 19 of 20.
   - Missed (with K1 passed): the gain is not specific. Stop.
   - True key with each of five letter-permuted lexicons (seeds base + 70,000 + j, j = 1..5, no letter fixed). Also run on the K0 plants, record-only. On real text these cells are graded by bar C under "Certify reading".
4. **K3, the true key on real text.** **G ≥ 0.02 in ≥ 16 of 20.** Otherwise stop: no certify by prediction with this score.
5. **K4, keys fitted to noise.** Run only if K1, K2 and K3 all pass. See "Certify reading".
- K2 and K3 are graded only when K1 passed.

## What was seen before this draft
- **Sealed results:** `lift_certify` (stopped at K0), `bench_restoration`, `lb_certify`, `lb_shape_ladder` (+ addendum 1), `lb_formula_dial`, `null_width`, `ur3_legend_refute`.
- **Pilot, 2026-11-24, scratch script outside the repo. Every run is listed here.**
  - Planted text only. The true key and shuffled keys were scored on plants. No key was scored on real Linear B text. Nothing was run on Indus text.
  - Plants: the `lift_certify` generator with pilot seed base 990000, on builds 21, 22 and 23 of the sealed `build` function (outside the sealed draws 1-20). Those builds supply chunk lengths, the split, sign frequencies and, for dilution, their Markov scramble.
  - Code reused by import: `lift_certify/run.py` (draw, plant, trigram, clean rule, folds, ranks).
- **Reviewer's planted-text check, 2026-11-24.** Run during review on the same pilot plants (base 990000, builds 21-23) with the true key and the frozen score, but with wrong lexicons. Planted text only. Listed under "Review check" below.
- **Not seen:** any gain of any key on real text; the true key's D on real text; any noise-fitted key under this score.

### Pilot run 1: eight scores on one plant (build 21, full dose, 2,195 clean positions)
Trigram Hit@1 4.1%. If the consonant value were known, Hit@1 would be 22.0%.

| score | Hit@1 lift (points) | log gain G (nats; SE) |
|---|---|---|
| (a) word likelihood over segmentations, uniform type weights, edge fragments | 1.1 | 0.082 (0.007) |
| the same without edge fragments (whole words only) | 0.0 | 0.000 |
| (b) Homer token-frequency weights | 1.1 | 0.046 (0.004) |
| (c) thinned lexicon, words of 5 to 7 consonants | 1.2 | 0.062 (0.006) |
| **(e) weights learned from the development half, α = 0.01** | **4.0** | **0.330 (0.022)** |
| (e) with α = 0.1 | 3.8 | 0.296 (0.017) |
| (e) without edge fragments | 1.1 | 0.089 (0.012) |
| oracle: the plant's own 500 words and weights | 5.0 | 0.499 (0.023) |

- (d), scoring only positions in chunks of ≥ 4 consonants, changes the denominator and not the ranking: Hit@1 lifts of 1.6, 6.2 and 7.7 for (a), (e) and the oracle in an earlier pass of the same plant.
- **No lexicon score can meet `lift_certify`'s 10-point K0 bar.** The oracle reaches 5.0 points. Chunks cut words, and a sign's value is shared by about nine sign types.
- **Edge fragments carry almost all the signal.** Without them both scores fall to near zero.
- The log gain separates the scores far better than Hit@1 does (15 standard errors against about 6).

### Pilot run 2: the chosen score on three plants
| | build 21 | build 22 | build 23 |
|---|---|---|---|
| full dose: G (SE) | 0.330 (0.022) | 0.208 (0.012) | 0.229 (0.020) |
| full dose: Hit@1 lift | 4.0 | 3.3 | 3.1 |
| full dose: λ* | 1 | 0.5 | 1 |
| full dose: D | 0.211 | 0.184 | 0.176 |
| true key on the unigram scramble: G | 0 | 0 | 0 |
| five shuffled keys (N1): G | 0 (all five) | 0 (all five) | 0 (all five) |
| half dose (w = 0.5): G (SE) | 0.098 (0.013) | 0.040 (0.006) | 0.039 (0.006) |
| half dose: D | 0.055 | 0.020 | 0.021 |
| quarter dose (w = 0.25): G | 0.027 | 0 | 0 |
| quarter dose: D | −0.009 | −0.028 | −0.040 |

- Score (a) on the same plants: G 0.082, 0.082, 0.068 at full dose; 0.015 and 0 at half dose.
- A chunk-level mixture of (e) with a null model was also tried: G 0.336, 0.209, 0.236 at full dose; 0.116, 0.049, 0.053 at half; 0.028, 0, 0 at quarter. It is not adopted: the gain over (e) is small and it adds a parameter.
- The oracle at half dose (builds 22, 23): G 0.127 and 0.079.

### Pilot run 3: the `lift_certify` dilution rule does not set a dose
- The `lift_certify` K1 rule was tried: dilute until the true key's IC on the plant's held-out half is within 0.01 of 0.204.
- Builds 22 and 23 stopped at the first midpoint (w = 0.5, IC 0.211 and 0.212). Build 21 ran to w = 0 without landing (IC 0.219).
- IC is flat in the dose. Fixed-dose plants gave IC 0.20-0.23 at w = 0.25 and 0.21-0.24 at w = 0.5. So IC cannot match a dose, and this study uses D instead.
- **Unintended cell:** build 21's bisection ended on a pure Markov scramble of build 21, and the true key was scored on it. Result: λ* = 0 and G = 0 for scores (a), (e) and the oracle. Trigram Hit@1 was 15.2%. This is scrambled text, not real text, but it was not planned.

### Review check: wrong lexicons on the pilot plants
- Run by the reviewer, not by the drafter. Pilot base 990000, builds 21 to 23, true key, frozen score.
- Wrong lexicons: two letter-permuted copies of the lexicon (seeds 777 and 778) and one random lexicon of the same word lengths (seed 99). The Greek rows repeat pilot run 2.

| G (nats) | full dose | half dose |
|---|---|---|
| Greek lexicon, builds 21 / 22 / 23 | 0.330 / 0.208 / 0.229 | 0.098 / 0.040 / 0.039 |
| letter-permuted seed 777, builds 21 / 22 / 23 | 0 / 0.017 / 0.004 | 0 / 0 / 0 |
| letter-permuted seed 778, builds 21 / 22 / 23 | 0.067 / 0.043 / 0.027 | 0 / 0 / 0 |
| random same-length lexicon, builds 21 / 22 / 23 | 0.078 / 0.096 / 0.027 | 0.014 / 0 / −0.015 |

- **A wrong lexicon reached 0.02 in 6 of 9 full-dose cells and 0 of 9 half-dose cells.** (Recounted by the drafter from the reviewer's saved outputs; the review summary said 5.)
- **Random-lexicon D at full dose was 0.07-0.10, against 0.18-0.21 for Greek.** So D is not specific to the lexicon.
- Consequence: the permuted-lexicon cell is graded (bar C), on five permutations per draw.

### Other checks
- The window model sums to 1 over all strings of 1 to 5 consonants (random word weights, ρ = 0.1 and 0.7).
- Lexicon size, 4 to 7 consonants: 9,636 skeletons (2,845 / 3,861 / 2,314 / 616).

## Prior art
Each paper below was opened as a full open-access PDF on 2026-11-24.
- **Snyder, Barzilay and Knight 2010,** "A statistical model for lost language decipherment", ACL. https://aclanthology.org/P10-1107.pdf
  - Word-level likelihood: each lost word is built from morphemes paired with known-language morphemes, with Dirichlet-process weights that favour a few frequent pairs over a character-edit base.
  - Segmentation is summed out: the likelihood of a word sums over its prefix, stem and suffix splits.
  - Words with no cognate are scored by a uniform character model. A sparsity prior limits how many letters one letter may map to.
  - Needs word-divided text. 29 of 30 letters and 60.4% of cognates; accuracy is higher by token than by type.
- **Berg-Kirkpatrick and Klein 2011,** "Simple effective decipherment via combinatorial optimization", EMNLP. https://aclanthology.org/D11-1029.pdf
  - The score is the summed edit distance between matched word pairs under an alphabet matching.
  - Density is stated outright: without limits the objective "can always be driven to zero", so the lexicon matching must be one-to-one and cover a fixed share τ of the smaller lexicon. τ trades precision for recall.
- **Berg-Kirkpatrick and Klein 2013,** "Decipherment with a million random restarts", EMNLP. https://aclanthology.org/D13-1087.pdf
  - Key scored by language-model likelihood. The best of a million restarts scored above the gold key (−1466.5 against −1467.4) with lower accuracy (89% against 92%). Large likelihood gains track accuracy; small ones near the top do not.
  - They used synthetic ciphers matched to the target as planted controls.
- **Luo, Cao and Barzilay 2019,** "Neural decipherment via minimum-cost flow: from Ugaritic to Linear B", ACL. https://arxiv.org/pdf/1906.06718
  - Character mapping by a sequence model; word matching by a minimum-cost flow that enforces one-to-one pairs and a set coverage, with edit distance in the costs. 67.3% of Linear B cognates.
  - Needs divided words and a word list made mostly of cognates.
- **Luo, Hartmann, Santus, Cao and Barzilay 2021,** "Deciphering undersegmented ancient scripts using phonetic prior", arXiv 2010.11054 (journal venue unverified). https://arxiv.org/pdf/2010.11054
  - The closest model to ours. The likelihood of an undivided inscription sums over all taggings into matched spans (a known word, by edit-distance alignment) and unmatched characters (uniform, 1/alphabet size), by dynamic programming.
  - Coverage is controlled over the whole corpus, not per text, because per-text coverage varies too much.
  - Results fall as word division is removed. Whether segmentations mean anything for a language with no relative is left open.
- **What this study takes:** the span-marginal likelihood with a uniform out-of-vocabulary model (Luo 2021; Snyder 2010), and weights that favour frequent items (Snyder 2010).
- **What none of them has:** chunks that cut words (hence the edge fragments here), exact-match skeletons in place of edit distance, and a test of the score against keys fitted to noise. The 2013 paper shows the danger such a test addresses.
- **Not found:** a restoration gain used to tell a true key from a fitted one. The search was short.
- Restoration papers (Pythia, Ithaca, Fetaya 2020, Lazar 2021, Papavassileiou 2023) are listed in `lift_certify.md`; they were not reopened.

## Data (all already held)
- Linear B syllabic signs, the true key (consonants of each sign, j and w dropped) and the Homeric skeleton lexicon: exactly as sealed `lb_shape_ladder` R1.
- **Word list W:** the lexicon's skeletons of 4 to 7 consonants. Alphabet: the ten key letters d k m n p q r s t z.
- Draw k = `build(k, "chunk")` with the sealed seeds: about 2,300 chunks of M77 seal lengths, split in half by source line. The development half trains everything. The held-out half is scored.
- M77 enters only as the list of text lengths used for chunking, as sealed.

## Frozen scoring
### Masking, candidates and baseline
- As `lift_certify`: one sign hidden at a time, at every position of every clean held-out chunk of ≥ 4 signs. Clean means no development chunk is identical, one edit away, or containing or contained (`corpus.build._close`).
- Candidates: every sign type in the draw.
- **Baseline B:** the `bench_restoration` trigram (absolute discount 0.75, back-off to bigram and add-one unigram, start and end marks), trained on the development half. B(c) is the sum of the log probabilities of the up to three trigrams that contain the masked position.

### Word model (the one primary score)
- A chunk read with a key is a string x of n consonants. The model treats x as a window cut at a random place from an endless stream of units.
- **Units:** a word w of W, with probability (1 − ρ) p(w); or a single consonant c, with probability ρ q(c). Mean unit length E = ρ + (1 − ρ) Σ p(w) |w|.
- **q:** the consonant frequencies of the training text read with the key, add-one over the ten letters.
- **Window probability,** by a forward pass. f(i) is the probability of x[1..i] with a unit ending at i.
  - f(0) = 1/E.
  - f(i) = f(i−1) ρ q(x[i]) + Σ over L = 4..7 of f(i−L) (1 − ρ) p(x[i−L+1..i]) + (1/E)(1 − ρ) Suf(x[1..i]).
  - P(x) = f(n) + Σ over i = 0..n−1 of f(i) (1 − ρ) Pre(x[i+1..n]) + (1/E)(1 − ρ) Inf(x).
  - Suf(s): total p of words that end in s and are longer than s. Pre(t): total p of words that begin with t and are longer than t. Inf(x): total p, counted once per place, of words that hold x strictly inside (touching neither end).
- **Fitting (EM, per key, per training text):** start at p uniform over W and ρ = 0.5. Fifteen iterations. Each iteration adds the posterior count of every unit use: whole words, single consonants, and the words behind each suffix, prefix and infix fragment (each counted as one token). Then p(w) = (n(w) + α) / (N + α |W|) with **α = 0.01**, and ρ = single-consonant count / all units, held in [0.001, 0.999].
- **Evidence for a string:** LLR(x) = log P(x) − Σ log q(x[i]). An empty string scores 0.
- For candidate c: cov(c) = LLR of the whole chunk read with the key, with c in the masked place.
- **Combined score: S(c) = B(c) + λ × cov(c).**

### Gain G (the graded statistic)
- The probability of the true sign under a score is its softmax share over all candidates.
- **G = mean over all clean positions of [log p_S(true sign) − log p_B(true sign)], in nats per position.** One number per key per draw.
- Reported beside it, grading no bar of this study: **Hit@1 and Hit@1 lift on every cell and key (the 2027-clause measure)**, Hit@5, mean reciprocal rank, G on positions in chunks of ≥ 4 consonants, the standard error of G, λ*, ρ and D.

### λ, set on development text only
- Grid: **0, 0.25, 0.5, 1, 2, 4.**
- Five folds of the development half, by CRC32 of the source line id mod 5. For each fold, the trigram and the word model (q, ρ, p) are fitted on the other four folds under the key being scored. Every clean position (clean against those four folds) of the fold's chunks of ≥ 4 signs is masked.
- λ* = the grid value with the highest pooled mean log p_S(true sign). Ties go to the smaller λ.
- **λ* > 0 only if that pooled mean exceeds the λ = 0 value by ≥ 0.01 nats; otherwise λ* = 0 and G is exactly 0.**
- For held-out scoring the trigram and the word model are fitted on the whole development half.
- The same rule is applied to every key in every cell. Held-out text never enters the fit of the word model or the choice of λ.

### Dose statistic D (K1 only)
- With the same five folds: D = Σ of LLR(x) over every chunk of each fold, under the word model fitted on the other four folds, divided by the number of consonants. Nats per consonant.
- w = 1 and w = 0 are evaluated first for F2. All 20 K1 dose targets are written to disk before any K1 plant gain is computed.
- D is not specific to the lexicon: a random lexicon gave 0.07-0.10 on full-dose pilot plants.

### Planted generator (K0, K1)
- As `lift_certify`, with new seeds: 500 lexicon skeletons of 4 to 7 consonants drawn uniformly, weights 1 / rank; each consonant written with a sign of exactly that value, drawn by sign frequency in draw k; zero-consonant signs follow at the rate that matches draw k's share. The stream is cut to draw k's chunk lengths and split as draw k is.
- **K1 dilution:** each chunk is replaced, when its fixed uniform u ≥ w, by the chunk at the same index of a Markov scramble of draw k (sealed `markov`, applied once to dev followed by ho). w is bisected on [0, 1], at most 12 steps, until the plant's D with the true key is within 0.005 of the target.
- The bisection sees only D on planted text. It sees no gain.

## Certify reading (K4)
- **N2, as sealed:** 9 keys per draw from `lb_shape_ladder` `fit`. They maximise IC.
- **N3, fitted to this score's own model:** 3 keys per draw, hill-climbed on the real development half (3,000 swaps inside consonant-count classes from a shuffled key, the sealed `fit` loop) to maximise the summed LLR of the development chunks under the word model with uniform p, ρ = 0.05 and uniform q.
- Each noise key gets its own word model and λ* by the frozen rules.
- **Bar A:** in ≥ 16 of 20 draws, the mean G of the 9 N2 keys is ≤ 0.005.
- **Bar B:** in ≥ 16 of 20 draws, the true key's G is above the largest G of all 12 noise keys.
- **Bar C:** in ≥ 16 of 20 draws the true key's G with the Homeric lexicon is above the largest G of the five permuted lexicons. Certify by gain passes only if K3 and bars A, B and C all hold.

## Calibration fallbacks (written before any calibration)
Calibration here means: the λ grid, the K1 dilution, and the K0 plant. These rules are the only changes allowed. Each is applied at most once per cell (F2: once per K1 draw) and logged. **Any other change after the first gain of any study cell is seen (to the word model, α, the EM start or iteration count, the grid, the 0.01 λ margin, the statistic, the bars including bar C, the masking, the clean rule, the trigram, the plants, the filler, the dose statistic or its 0.005 tolerance, the permuted lexicons, the seeds or the draws) makes the study INVALID.** An invalid study is labelled so and is not rerun under this name.
- **F1, grid edge.** If λ* = 4 for the true key in 3 or more of the 5 K0 draws, the values 8 and 16 are added to the grid for every key in every cell. K0 is graded on the original grid and is not regraded.
- **F2, dose out of range or unbuilt.**
  - Target below the plant's D at w = 0 (minus 0.005): the dose is zero. The draw counts as a K1 miss and is logged "no dose above filler".
  - Target above the plant's D at w = 1 (plus 0.005): w = 1 is used and the draw is flagged "real text richer than the full plant".
  - Target in range but not landed in 12 steps: the draw is unbuilt. K1 needs ≥ 18 of 20 built, and its bar becomes ≥ 80% of built draws (rounded up). Fewer than 18: abort.
  - The filler is never changed.
- **F3, K0 too easy for the trigram.** If the trigram's Hit@1 on the K0 plant exceeds 60% in any draw, the sublexicon is raised once from 500 to 2,000 words and K0 is rebuilt, before any K0 gain is computed. The larger sublexicon then also applies to K1.
- **F4, thin draw.** A real draw with fewer than 900 clean positions is kept and flagged. If the median falls below 900: abort.
- **Not permitted, as examples:** a second score or a backup score; tuning λ, α or ρ on held-out text; grading Hit@1 in place of G; another lexicon or length range; dropping edge fragments; scoring a subset of positions as the primary; moving any bar; dropping draws; another filler or dose statistic; another permuted lexicon, or fewer or more than five; dropping or regrading bar C; rerunning K0 or K1; grading any bar after a K1 fail.

## Route rule
- **One score, one sealed attempt.** There is no backup score. In the pilot the only other score with any gain, (a), was three to four times weaker at full dose and at zero by half dose.
- **If K0 or K1 fails, the route "certify by held-out restoration on existing texts" is logged closed for this corpus size** (about 13,100 sign tokens in chunks of M77 length). No further score is drafted; reopening needs more text. The line moves to `certify_size_curve`.
- The pilot's choice of score is disclosed above, so a K0 fail on fresh plants would mean the pilot's result did not hold up.

## Indus rule
- **No Indus step is run in this study.**
- M77 supplies text lengths only, as in the sealed R1 set-up.
- No Indus key (claimed, fitted or shuffled) is scored on any text. No M77 sign is masked or restored. The study code must not load `splits_v2` or any key file from the claim bench.
- A pass does not license a run on Indus. That would need its own prereg and the coordinator's OK.

## Cells
| cell | text | keys | draws |
|---|---|---|---|
| K0 | planted, full dose, and its unigram scramble | true, 20 N1; true with each of 5 letter-permuted lexicons (record-only) | 5 |
| K1 | real development half (D only); planted at matched D | true | 20 |
| K2 | real, and its unigram scramble | true, 20 N1; true with each of 5 letter-permuted lexicons (graded by bar C) | 20 |
| K3 | real | true | 20 |
| K4 | real | 9 N2, 3 N3 (bars A and B); bar C read from the K2 permuted cells | 20 |

## Readings (frozen; worded for the bench)
- **K0 fails:** "The word-and-fragment score did not pass its planted test (state which bar: gain or control). By the one-attempt rule, certify by held-out restoration on existing texts is closed for this corpus size (about 13,100 sign tokens in chunks of M77 length). This is a rule, not a proof that no score could work: the oracle gain was 0.50 nats." Nothing else runs.
- **K1 fails:** "Unpowered. A planted language diluted to the true key's own dose (cross-fitted lexicon likelihood per consonant) does not raise restoration by 0.02 nats per sign at Indus shape. By the one-attempt rule, certify by held-out restoration on existing texts is closed for this corpus size. No further score is drafted; reopening needs more text." K2 and K3 run once, record-only. The line moves to `certify_size_curve`.
- **K2 fails (K1 passed):** "The gain is not specific to the key or to the text." Nothing else runs.
- **K3 fails with K1 passed:** "The true Linear B key with a Homeric lexicon does not raise restoration by 0.02 nats per sign, though a planted language at the same dose does. The cause is not isolated: the plant differs from real text in lexicon match, dose layout and sign order."
- **K3 passes, bar A or B fails (bar C either way):** "A gain exists but keys fitted to noise show it too. No certify by prediction."
- **K3 passes, bars A and B hold, bar C fails:** "The gain comes from the sign grouping and the fragment model, not from the lexicon. It cannot certify sign values."
- **All pass:** "On Linear B at Indus shape, a held-out restoration gain separates the true key from keys fitted to noise by these two fitters (3,000-swap IC; 3,000-swap fragment likelihood). This is a candidate certify statistic on this bench (one script, one lexicon). N3 was fitted to a fixed-weight proxy, not to G; no key fitted to G or to the learned-weight model was tried, and a new prereg with such a fitter is needed before 'certify' is used. A G pass alone does not meet the 2027 held-out-prediction clause; the Hit@1 figures are reported beside it." It says nothing about any Indus key.

## Aborts
- **A1.** The study code does not reproduce the sealed R1 true IC and N1 mean of draws 1 to 3 to 1e-9: stop.
- **A2.** The recomputed median clean positions differ from 1,376 by more than 5%: stop and redraft.
- **A3.** F2 or F4 abort conditions.
- **A4.** The Indus compute lock is not held, or free memory is below the 20% guard: do not start.
- **A5.** Any step would read an Indus key or restore an Indus sign: stop.
- **A6.** The window model does not sum to 1 (to 1e-9) over all strings of 1 to 4 consonants for the fitted K0 draw-1 model: stop. This check sees no gain.
- No rerun, no tuning, no fix tags after any gain is seen.

## Seeds
- Draws, N1 and N2: the sealed `lb_shape_ladder` seeds (base 20261124) for draw k.
- Study base **20270101** (not `lift_certify`'s 20261201, not the pilot's 990000). Plant sublexicon: base + k. Filler Markov scramble: base + 10,000 + k. Unigram scrambles (K0, K2): base + 20,000 + k. N3 start keys and swaps: base + 30,000 + 10k + restart. Plant spelling: base + 50,000 + k. Dilution uniforms: base + 60,000 + k. Lexicon letter permutations: base + 70,000 + j, j = 1..5 (five for the study, the same five in K0 and K2; each a permutation of the ten consonant letters with no letter fixed, applied to every lexicon word).
- N1: the first 20 keys of draw k's sealed R1 N1 stream, the same 20 in K0 and K2.
- Development folds: CRC32, no seed.

## Limits stated in advance
- **The statistic changed, and so did the K0 bar.** `lift_certify` graded Hit@1 with a 10-point K0 bar and a 3-point real-text bar. The pilot showed that bar is out of reach of any lexicon score here. G is a log score. A gain of 0.02 nats is a 2% drop in the perplexity of the hidden sign: small. It does not count as the 2027 held-out prediction on its own; Hit@1 is that measure (coordinator decision).
- **The score was chosen on a pilot.** Three plants, eight scores, two values of α. K0 on fresh plants guards against that choice being luck; it does not make the bars independent of the pilot.
- **The expected result is a stop at K1.** In the pilot the gain was gone at a quarter dose and at D ≤ 0. Run 3 suggests the true key's lexicon fit on real text may be no higher than on a Markov scramble of it. If the real D is near zero, K1 fails or reports "no dose above filler".
- **The lexicon's role is reduced.** Word weights come from the development half; the lexicon only says which strings may carry weight. Bar C tests whether a real-text gain needs the Greek lexicon.
- **On full-dose plants a wrong lexicon reached 0.02 nats in 6 of 9 review cells.** The 0.02 bar alone therefore does not show that a lexicon is right; bar C is the guard.
- **Edge fragments make the model close to a consonant n-gram model** of the lexicon. Most chunks hold 3 to 5 consonants, so most are scored as a piece of one word.
- **The plant is kinder in lexicon match and word reuse, harsher in within-series sign choice.** A K1 pass does not promise a K3 pass.
- **N3 is a weak adversary.** It is fitted to a fixed-weight version of the model, not to G itself, which would cost about 10 seconds per swap. Stronger fitting could only raise noise-key gain.
- **One script, one lexicon.** Homeric against Mycenaean.
- **Per-draw noise.** A standard error of 0.008 to 0.016 nats at 1,376 positions. The λ margin sets most noise keys to exactly 0.

## Cost
- One key on one draw (six word-model fits, about 2,800 masked positions): about 10 seconds in plain Python, from the pilot.
- K0: 135 key-draw cells. K1: 20 draws, each up to 14 D evaluations and one gain. K2: 540. K3: 20. K4: 240, plus the sealed N2 fits and N3.
- About 3 hours of processor time if every step runs (v1's 2.5 hours plus 125 permuted-lexicon cells), under an hour on 4 small workers; about 40 minutes if K1 fails.
- Under the Indus compute lock, through `board/run.sh`. Outputs: small JSON files with per-draw summaries. No per-position arrays are saved.

## Decisions (from the review of v1)
1. **Coordinator decision (2026-11-25):** G does not replace Hit@1 for the 2027 clause; changing the metric before sealing would move the goalposts. G with bars A to C is this study's pre-registered gate for K0 to K4. Hit@1 is reported on every cell as the 2027-clause measure, and a G pass alone does not meet the 2027 clause. Everything else stays as drafted, including the route rule.
2. Keep the bars and add bar C.
3. A K1 fail closes the route.
4. The permuted cell is graded (bar C).
5. D stays, at ±0.005.
6. N3 is not fitted to G now; that is required before "certify" is used.

## Review log
- 2026-11-24: DRAFT v1 written. Not reviewed. Not sealed. No study code exists.
- 2026-11-24: Fresh review of v1 returned "FIX, then seal". The reviewer ran a wrong-lexicon check on the pilot plants (see "Review check").
- 2026-11-24: DRAFT v2. Changes: review check disclosed; study base moved to 20270101; K0 stated as a replication and K1 as the real test; five graded letter-permuted lexicons and bar C; D tolerance 0.005 and 12 bisection steps, targets written before plant gains; K0-fail, K1-fail and all-pass readings reworded; new reading for a bar C fail; a K1 fail now closes the route; open questions replaced by decisions; fallbacks and cost updated to match. Not sealed. No study code exists. Nothing was scored for this revision.
- **Pre-seal check (2026-11-24):** four blocking fixes applied (stale count item, reading overlap on bar C, route-rule wording after a K1 fail, clean rule for λ masking) plus three wording fixes. No numbers or bars changed.
- Open items closed: (a) the coordinator decided decision 1 (G is the study gate; Hit@1 is the 2027 measure, reported on every cell; a G pass alone does not meet the clause); (b) the drafter's recount from the reviewer's saved outputs gives 6 of 9, now in the table.
- 2026-11-25: v3 sealed (tag `lift_score`). No study code existed at sealing. Nothing was scored after the pilot and the review check.
