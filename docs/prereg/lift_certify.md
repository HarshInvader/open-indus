# Lift certify: does the true Linear B key, with an outside lexicon, restore masked held-out signs better than a sign trigram, where noise-fitted keys do not? (SEALED; no study code existed and no key had been scored at sealing)

Status: **SEALED v3**, 2026-11-24. v1 was reviewed once (verdict: FIX, then run); v2 applied that review, and a narrow pre-seal check (SEAL-WITH-EDITS, eight edits) is applied in v3 (see Decisions and Review log). Drafted by Fable from `docs/fable_brief9.md` section 3, study 5. Main line (a), the claim bench. Kind ii (a read script used as a known-answer control).

## Question
- `lb_shape_ladder` showed that dictionary fit cannot certify a key at Indus shape: keys fitted to noise out-score the true key (0.254 against 0.204 at R1).
- **Q.** Does held-out prediction do better? With the true Linear B key and the Homeric lexicon added to a sign trigram, does top-1 restoration of a masked held-out sign rise by at least 3 points, while keys fitted to noise gain at most 1 point?
- **No Indus key is scored in this study. No Indus text is restored, masked or read with any key. No outcome supports or counts against any Indus key, and none licenses a run of one.**

## Why
- This is the only open study tied to the held-out-prediction clause of the 2027 bar.
- Fit rewards any key that finds dictionary words, real or not. Prediction of a hidden sign can only be helped by words that are really there. So lift might separate a true key from a fitted one where fit cannot.
- A pass would give the first certify statistic at Indus shape. A fail closes "certify by held-out prediction on existing texts" at the brief's bar, with a named cause.

## Kill tests, run first and in this order (strongest first)
All plants are synthetic. Their answers are known by construction.

1. **K0, planted language, full dose (the pipeline can see a lexicon).**
   - Text made only of lexicon words (generator below), cut to M77 lengths, same sizes as a real draw.
   - Bars, draws 1 to 5: true-key lift **≥ 10 points in 5 of 5**. The same key on the unigram scramble of that text: lift **≤ 1 in 5 of 5**. Twenty shuffled keys (N1): median lift **≤ 1 in 5 of 5**.
   - Any bar missed: the pipeline is broken. Stop.
2. **K1, planted language at the real dose (power).**
   - The same generator, diluted with filler taken from the Markov scramble of draw k (sealed function, new seed) until the true key's IC on the plant's held-out half equals the sealed R1 true IC of draw k (±0.01). 20 draws.
   - Bar: lift **≥ 3 points in ≥ 16 of 20**.
   - Missed: the study is **unpowered**. K2 and K3 then run once, record-only. No bar is graded and the verdict stays unpowered. A K3 lift of ≥ 3 in ≥ 16 of 20 is logged as "plant harsher than real text; K1 invalid as a power test" and needs a new prereg. K4 does not run. See Readings.
3. **K2, real text, negative controls.** Draws 1 to 20, real Linear B.
   - The true key on unigram-scrambled text (trigram and key both on the scramble): lift ≤ 1 in ≥ 19 of 20.
   - Shuffled keys (20 N1 draws per subsample): median lift ≤ 1 in ≥ 19 of 20.
   - Missed (with K1 passed): the lift statistic is not specific. Stop.
4. **K3, the kill named in the brief.** True-key lift **≥ 3 points in ≥ 16 of 20 draws.** Otherwise stop: no certify by prediction.
5. **K4, noise-fitted keys.** Run only if K1, K2 and K3 all pass. See "Certify reading".
- K2 and K3 are graded only when K1 passed. After a K1 fail they are record-only, as stated under K1.

## What was seen before this draft
- **Sealed results:** `bench_restoration` (and its retrain), `lb_certify`, `lb_shape_ladder` (+ addendum 1), `lb_formula_dial`, `null_width`, `ur3_legend_refute`.
- **Label-free counts, run 2026-11-24 with a scratch script outside the repo.** It used the sealed `lb_shape_ladder` `build` (draws 1 to 20), the near-copy rule `corpus.build._close`, and consonant counts of the known Linear B values. It loaded no lexicon, trained no trigram and scored no restoration.
- **Review, 2026-11-24:** trigram-only Hit@1 on clean Linear B positions, draws 1-20: 14.0% (11.8-16.8). A key-free simulation with synthetic bonuses at the 58/43 rates gave lifts of 0.1-0.45 points. No lexicon was loaded.
- **Not seen:** any lift from a key (true, shuffled, fitted or planted), on real or planted text; any lexicon match beyond the sealed IC values.

### Measured: count gate (median of 20 draws; range)
| count | Linear B R1 draws | Indus M77, held-out quarter (`splits_v2`) |
|---|---|---|
| held-out sign tokens | 4,015 (3,935-4,148) | n/a |
| held-out texts of ≥ 4 signs | 465 (438-489) | 315 of 571 |
| positions in those texts | 2,348 (2,217-2,478) | 1,811 (1,553 in complete texts) |
| **clean positions** (no identical, one-edit or contained copy in the training half) | **1,376 (1,278-1,524)**, in 282 texts | 1,807 (the split is by family) |
| clean positions in a segment of ≥ 4 consonants (LMIN) | 678 (590-752), **49%** | 66% if a key had Linear B's consonant load (0.70 per sign); 100% at one consonant per sign |
| the same, where the masked sign itself carries a consonant | 558 (489-621), **40%** | n/a |

- **Gate: about 900 clean held-out positions. Linear B has 1,376. Passed.** M77 has 1,807, short of the brief's estimate of 2,400.
- 41% of Linear B positions in texts of 4+ signs are lost to near-copies. Linear B chunks repeat more than the brief assumed.
- The M77 column is a count only. Nothing is run on M77 in this study.
- A masked sign's value is shared by 9 sign types on average (token-weighted). The lexicon holds consonant skeletons, so it can point to a consonant series at most, never to one sign.

### Measured: ceiling on the lift
- **Hard ceiling.** The lexicon can change a ranking only where a word of ≥ 4 consonants can cover the masked sign: 40% to 49% of clean positions. With the trigram-only Hit@1 of 14.0% on clean Linear B positions (draws 1-20, seen in review), the largest possible lift is 0.40 to 0.49 × 86.0 = **34 to 42 points**. A 3-point lift is not ruled out by construction.
- **Information estimate (sealed numbers, a heuristic, not a bound).**
  - At R1 the true key covers 20.4% of held-out consonants with lexicon words; shuffled keys cover 15.2%. All covered consonants lie in segments of ≥ 4 (35% of consonants).
  - So inside reachable segments the lexicon marks 58% of true consonants and 43% of chance ones. The excess is 15%.
  - Excess × reachable share with a consonant: 0.15 × 0.40 = **6% of clean positions** where the lexicon holds real information.
  - If every one of those were a trigram miss turned into a hit, with no losses elsewhere: 0.06 × 86.0. The product (5.2 points) is not a bound. Simulation puts the expected lift below 1 point.
- **So the gate passes, narrowly, and the kill is expected to fail.** K1 exists to settle this cheaply on planted text before the real key is scored.

## Prior art
Opened 2026-11-24, abstract or metadata page only.
- Assael et al. 2019, Pythia, "Restoring ancient text using deep learning: a case study on Greek epigraphy", arXiv 1910.06262. Character restoration of Greek inscriptions, scored by character error rate against human epigraphists.
- Assael et al. 2022, Ithaca, "Restoring and attributing ancient texts using deep neural networks", Nature, doi:10.1038/s41586-022-04448-z. 62% restoration accuracy alone; historians rise from 25% to 72% with it.
- Fetaya et al. 2020, "Restoration of fragmentary Babylonian texts using recurrent neural networks", arXiv 2003.01912. Recurrent language model for breaks in Achaemenid Akkadian.
- Lazar et al. 2021, "Filling the gaps in ancient Akkadian texts: a masked language modelling approach", arXiv 2109.04513. 89% hit@5 on about 1M tokens, with pretraining on other languages.
- Papavassileiou et al. 2023, "A generative model for the Mycenaean Linear B script and its application in infilling text from ancient tablets", doi:10.1145/3593431 (Crossref record). A bidirectional recurrent model against n-grams for Linear B infilling.
- Luo, Cao and Barzilay 2019, "Neural decipherment via minimum-cost flow: from Ugaritic to Linear B", arXiv 1906.06718. Cognate matching to a known lexicon; 67.3% of Linear B cognates.
- Luo et al. 2021, "Deciphering undersegmented ancient scripts using phonetic prior", arXiv 2010.11054. Joint segmentation and cognate alignment on undivided text.
- **In all the restoration papers the script is already read.** Restoration measures the language model, not a key. The decipherment papers score a key by cognate matches, which is fit.
- **Not found:** restoration lift used as a test of whether a key is right, or compared between a true key and keys fitted to noise. The search was short. "Not found" is weak evidence that this is new.
- Repo: `bench_restoration` (a trigram equals the released neural models on clean M77 positions; a 3-point gain was detectable at 875 positions).

## Data (all already held)
- Linear B syllabic signs, the true key (consonants of each sign, j and w dropped) and the Homeric skeleton lexicon: exactly as sealed `lb_shape_ladder` R1. LMIN = 4.
- Draw k = `build(k, "chunk")` with the sealed seeds: about 2,300 chunks of M77 seal lengths, split in half by source line. The development half trains everything. The held-out half is scored.
- M77 enters only as the list of text lengths used for chunking, as sealed.

## Frozen scoring
### Masking
- One sign hidden at a time. Every position of every held-out chunk that has ≥ 4 signs and is clean.
- **Clean:** no development chunk is identical to it, one edit from it, or contains or is contained in it (`corpus.build._close`).
- **Candidates:** every sign type in the draw (development plus held-out), 71 to 73 types.

### Baseline B (sign trigram)
- As `bench_restoration` `ours_scores`: absolute discount 0.75, back-off trigram to bigram to add-one unigram, start and end marks.
- A candidate's score is the sum of the log probabilities of the (up to three) trigrams that contain the masked position.
- Trained on the development half of draw k. No tuning.
- **Hit@1:** the true sign has the top score. Ties are broken by development frequency, then sign name.

### Key plus lexicon
- For candidate c, read the whole chunk with the key, c in the masked place. cov(c) = `ic_seg` of that consonant string (sealed function): the most consonants coverable by lexicon words of ≥ 4 consonants.
- **Combined score: S(c) = B(c) + λ × cov(c).** λ is in nats per covered consonant.
- A key changes nothing where the chunk cannot reach 4 consonants.

### λ, set inside the pipeline on development text only
- Grid: **0, 0.25, 0.5, 1, 2, 4.**
- Five folds of the development half, by CRC32 of the source line id mod 5. For each fold: trigram trained on the other four; every clean position (clean against those four folds) in chunks of ≥ 4 signs is masked.
- λ* = the grid value with the highest pooled development Hit@1. Ties go to the smaller λ. λ* = 0 is allowed and gives a lift of exactly 0.
- **λ* > 0 only if its pooled development Hit@1 exceeds that of λ = 0 by ≥ 0.5 points; otherwise λ* = 0.**
- The same rule is applied to every key, in every cell: true, shuffled, noise-fitted, planted.
- Held-out text never enters the choice of λ.

### Lift
- **Lift = Hit@1 of S minus Hit@1 of B, in points, on all clean positions of the draw.** One number per key per draw.
- Reported beside it, grading nothing: lift on reachable positions only, Hit@5, mean reciprocal rank, λ*, and counts of positions gained and lost.

### Planted generator (K0, K1)
- 500 lexicon skeletons of 4 to 7 consonants, drawn uniformly (seeded), given weights 1 / rank.
- Each consonant is written with a sign that has exactly that value, drawn by the sign's frequency in draw k. After each such sign a zero-consonant sign follows with the probability that makes their token share equal draw k's.
- The word stream is cut into chunks with draw k's chunk lengths and split in half as draw k is.
- **K1 dilution:** each chunk is, with probability 1 − w, replaced by the chunk at the same index of a new Markov scramble of draw k: the sealed function `markov` (first-order sign chain, same lengths) applied once to dev followed by ho in `build` order, with its own `random.Random(base + 10,000 + k)`. The sealed run scrambled only the development half; the function is unchanged. Each chunk gets one uniform u, drawn once; it is replaced when u ≥ w, at every bisection step. No other filler is built. w is bisected on [0, 1], at most 20 steps, until the true key's IC on the plant's held-out half is within 0.01 of the sealed R1 true IC of draw k.
- The bisection sees only IC on planted text. It sees no lift.

## Certify reading (K4)
- **N2, as sealed:** 9 keys per draw from `lb_shape_ladder` `fit` (3,000 swaps, 3 restarts, on the real development half and on its unigram and Markov scrambles). They maximise IC.
- **N3, fitted to the statistic itself:** 3 keys per draw, hill-climbed on the real development half to maximise the cross-fitted development Hit@1 at λ = 1 on a fixed sample of 300 development positions. 500 swaps inside consonant-count classes, starting from a shuffled key.
- Each noise key gets its own λ* by the frozen rule. **N3 is fitted at λ = 1 and graded at its own λ*.**
- **Bar A (the brief):** in ≥ 16 of 20 draws, the mean lift of the 9 N2 keys is ≤ 1 point.
- **Bar B:** in ≥ 16 of 20 draws, the true key's lift is above the largest lift of all 12 noise keys.
- **Certify by lift passes only if K3, bar A and bar B all hold.**

## Calibration fallbacks (written before any calibration)
Calibration here means: the λ grid, the K1 dilution, and the K0 plant. These rules are the only changes allowed. Each is applied at most once and logged. **Any other change after the first lift of any cell is seen (to the score, the grid, the 0.5-point λ margin, the bars, the masking, the clean rule, the trigram, the plants, the filler, the seeds or the draws) makes the study INVALID.** An invalid study is labelled so and is not rerun under this name.
- **F1, grid edge.** If λ* = 4 for the true key in 3 or more of the 5 K0 draws, the values 8 and 16 are added to the grid, for every key in every cell. The 0.5-point margin over λ = 0 applies to the widened grid unchanged. This is decided at K0, on planted text, before any real-text lift. K0 is graded on the original grid and is not regraded.
- **F2, unbuilt dilution.** A K1 draw whose bisection (with the Markov filler) does not land within 0.01 is unbuilt. The filler is not changed to make it land. K1 needs ≥ 18 of 20 built, and its bar becomes ≥ 80% of built draws (rounded up). Fewer than 18: abort.
- **F3, K0 too easy for the trigram.** If the trigram's Hit@1 on the K0 plant exceeds 60% in any draw, the sublexicon is raised once from 500 to 2,000 words and K0 is rebuilt. This is checked on trigram-only scores before any K0 lift is computed. The 2,000-word sublexicon then also applies to K1.
- **F4, thin draw.** A real draw with fewer than 900 clean positions is kept and flagged. If the median falls below 900: abort.
- **Not permitted, as examples:** tuning λ on held-out text; changing or dropping the 0.5-point λ margin; a second way of combining key and trigram; a different LMIN or lexicon; changing the discount; scoring a subset of positions as the primary; moving the 3-point, 1-point or 16-of-20 bars; dropping draws; another filler; rerunning K1; grading any bar after a K1 fail.

## Indus rule
- **No Indus step is run in this study.**
- M77 supplies text lengths only, as in the sealed R1 set-up. The M77 column of the count table is label-free and is not recomputed by the study code.
- No Indus key (claimed, fitted or shuffled) is scored on any text. No M77 sign is masked or restored. The study code must not load `splits_v2` or any key file from the claim bench.
- A pass does not license a run on Indus. That would need its own prereg and the coordinator's OK.

## Cells
| cell | text | keys | draws |
|---|---|---|---|
| K0 | planted, full dose, and its scramble | true, 20 N1 | 5 |
| K1 | planted, real dose | true | 20 |
| K2 | real, and its unigram scramble | true, 20 N1 | 20 |
| K3 | real | true | 20 |
| K4 | real | 9 N2, 3 N3 | 20 |

## Readings (frozen; worded for the bench)
- **K0 fails:** "The pipeline cannot restore signs from a lexicon even on text made of lexicon words." Nothing else runs.
- **K1 fails:** "Unpowered. At the true key's own dictionary coverage (IC 0.20 against 0.15 by chance), a planted language does not lift restoration by 3 points at Indus shape. With this score (trigram plus λ × covered consonants, Hit@1, 3-point bar), restoration lift is unpowered at this shape and lexicon density. The route is closed at the brief's bar, not for every possible statistic." K2 and K3 then run once, record-only. No bar is graded and the verdict stays unpowered. A K3 lift of ≥ 3 in ≥ 16 of 20 is logged as "plant harsher than real text; K1 invalid as a power test" and needs a new prereg. Atlas 1.1 records the route closed at the brief's bar, with this cause.
- **K2 fails (K1 passed):** "The lift is not specific to the key or to the text." Nothing else runs.
- **K3 fails with K1 passed:** "The true Linear B key with a Homeric lexicon does not lift restoration by 3 points, though a planted language at the same coverage does. The cause is not isolated: the plant differs from real text in lexicon match, dose layout and sign order."
- **K3 passes, bar A or B fails:** "Lift exists but keys fitted to noise show it too. No certify by prediction."
- **All pass:** "On Linear B at Indus shape, held-out restoration lift separates the true key from keys fitted to noise by these two fitters (3,000-swap IC; 500-swap lift). This is a certify statistic on this bench (one script, one lexicon, LMIN 4)." It says nothing about any Indus key.

## Aborts
- **A1.** The study code does not reproduce the sealed R1 true IC and N1 mean of draws 1 to 3 to 1e-9: stop.
- **A2.** A recomputed gate count (clean positions, reachable share) differs from the table by more than 5%: stop and redraft.
- **A3.** F2 or F4 abort conditions.
- **A4.** The Indus compute lock is not held, or free memory is below the 20% guard: do not start.
- **A5.** Any step would read an Indus key or restore an Indus sign: stop.
- No rerun, no tuning, no fix tags after any lift is seen.

## Seeds
- Draws, N1 and N2: the sealed `lb_shape_ladder` seeds (base 20261124) for draw k.
- Study base 20261201. Plant sublexicon: base + k. Filler Markov scramble: base + 10,000 + k. Plant spelling: base + 50,000 + k. Dilution uniforms: base + 60,000 + k. Unigram scrambles (K0, K2): base + 20,000 + k. N1: the first 20 keys of draw k's sealed R1 N1 stream, the same 20 in K0 and K2. N3 start keys and swaps: base + 30,000 + 10k + restart. N3 position sample: base + 40,000 + k.
- Development folds: CRC32, no seed.

## Limits stated in advance
- **One script, one lexicon.** Homeric against Mycenaean, LMIN 4, density 0.177.
- **The expected result is a stop at K1.** The review's simulation puts the true key's lift below 1 point.
- **The plant is kinder in dose layout and lexicon match, harsher in within-series sign choice.** A K1 pass does not promise a K3 pass. A K1 fail is strong, not conclusive.
- **The lexicon sees consonant series, not signs.** Nine sign types share a value on average.
- **Per-draw noise.** With about 1,376 positions, a lift has a standard error of roughly 0.6 points if 5% of positions change. A noise key can reach 1 point by chance; bar A uses the mean of 9 keys for that reason.
- **The 14.0% baseline in the ceiling was seen in review**, trigram only, with no key and no lexicon. The simulation's bonuses were synthetic; it is a guide, not a result.
- **Half the positions are out of the lexicon's reach.** The primary lift is still over all clean positions, as the brief set it.
- **N3 is a weak adversary** (500 swaps, 300 positions). Stronger fitting could only raise noise-key lift.
- **λ is one number per key.** A richer model of the lexicon term is not tried.

## Cost
- One lift: about 1,376 positions × 73 candidates, with `ic_seg` at the reachable half. Under 2 seconds. λ* costs about five times that.
- K0 to K3: about 5 + 20 + 40 + 20 key-draw cells with shuffles, under 20 minutes with 4 small workers. K4: the sealed N2 fits (about 6 minutes per 20 draws) plus N3 (about 3 minutes per draw). About 1.5 hours in all if every step runs; about 20 minutes if K1 fails (K2 and K3 still run once, record-only; K4 does not).
- Under the Indus compute lock, through `board/run.sh`. Outputs: small JSON files with per-draw summaries. No per-position arrays are saved.

## Decisions (from the review of v1, 2026-11-24)
1. **K1 fail.** K2 and K3 run once, record-only. No bar is graded and the verdict stays unpowered.
2. **Primary.** The primary lift is over all clean positions. Lift on reachable positions is reported beside it and grades nothing.
3. **N3 is graded** (bar B), fitted at λ = 1 and graded at its own λ*.
4. **Bars unchanged.** Bar A uses the mean of the N2 keys. Bar B uses the maximum of all 12 noise keys.
5. **Filler.** K1 uses Markov filler, from the Markov scramble of draw k (sealed function, new seed). There is no second filler.
6. **Run it.** The study runs once v2 is sealed, despite the expected stop at K1.

## Before sealing
- Seal v2 as it stands. Code is written and hashed after sealing, before any lift.

## Review log
- **2026-11-24, fresh review of DRAFT v1. Verdict: FIX, then run.**
  - Seen in review, key-free: trigram-only Hit@1 on clean Linear B positions, draws 1-20, 14.0% (11.8-16.8); simulated lifts of 0.1-0.45 points with synthetic bonuses at the 58/43 rates. No lexicon was loaded and no key was scored.
  - Changes in v2:
    - ceiling recomputed with the Linear B baseline (34 to 42 points); the product estimate (5.2 points) marked as not a bound; expected lift below 1 point;
    - K1 filler changed from unigram to the Markov scramble of draw k (sealed function, new seed); "another filler" not permitted;
    - λ rule: λ* > 0 needs a gain of ≥ 0.5 points over λ = 0 on development text;
    - on a K1 fail, K2 and K3 run once, record-only; K4 does not run;
    - K1-fail, K3-fail and all-pass readings reworded; the limit on the plant reworded;
    - N3 fitted at λ = 1 and graded at its own λ*;
    - open questions replaced by Decisions.
  - The fallback section was checked against the new λ rule and filler. F1 to F4 are unchanged in substance and no fallback was added.
  - Status after these changes: DRAFT v2, not sealed. No study code exists.
- Pre-seal check of v2: SEAL-WITH-EDITS, eight edits (filler = sealed `markov` function with a new seed on the whole draw; separate seeds for spelling, dilution, unigram scrambles and N1; unverified odds line deleted; F1/F2/F3 tightened; K4 needs K1, K2 and K3). Applied; sealed as v3.
