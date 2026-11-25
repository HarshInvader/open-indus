# Null width: which label-free text properties set the width of the shuffle null, and what width does M77's shape imply? (SEALED; no code existed and no study IC had been computed at sealing)

Status: **SEALED v3**, 2026-11-24 (v2 plus the pre-seal check's eight edits). Reviewed once (verdict FIX), then a narrow pre-seal check (SEAL-WITH-EDITS); both are applied (see the review log at the end). Drafted by Fable. Main line (a), the claim bench. Kind iii (read scripts used as known-answer controls).

## Question
- The refute bench passes a key when its IC beats the 99th percentile of its own shuffles (N1). The gap between that percentile and the N1 mean is the **null width W**. A true key passes only if its signal (true IC minus N1 mean) is above W.
- **Q1.** Which properties of a text, countable without scoring any key, set W?
- **Q2.** Can a predictor fitted only on dialled Ur III administrative text predict W on Ur III seal legends? Linear B is reported beside it as an extrapolation and is not graded.
- **Q3.** If it can: what W does M77's shape imply, and what signal would a true key need there?
- **No Indus key is scored, on any text. No IC of any key is computed on M77. No outcome supports or counts against any Indus key, and none licenses a rerun of one.**

## Why
- `ur3_legend_refute`: the true reading fails on seal legends (0 of 20) and passes on administrative text (20 of 20). The legend signal is the larger one (0.085 against 0.059). The null is what moved: W 0.111 against 0.040, 2.8 times wider.
- On unigram-scrambled text the widths are 0.085 against 0.032, 2.65 times. So most of the widening survives the removal of word order. Formulae are not the main cause.
- `lb_formula_dial`: tilting Linear B to Indus formula excess left the scrambled width flat (0.025) and moved the real width by 1.07 times.
- `yj_ic_refute`: the real-text null was 2.1 to 2.7 times wider than the planted one.
- If W can be read off a text's shape, the signal a key needs on Indus-shaped text can be stated before any key is benched. If it cannot, that is worth knowing too.

## What was seen before this draft
- **Sealed results:** `lb_certify`, `lb_shape_ladder` (+ addendum 1), `lb_formula_dial`, `lb_wrong_lexicon`, `yj_ic_refute`, `scott_ic_refute`, `ur3_legend_refute` (all cells, per-draw W on real and scrambled text).
- **Read from sealed output, 2026-11-24** (medians of 20 draws; W = N1 p99 minus N1 mean):

| text | lexicon, LMIN | W real | W scrambled | N1 mean | true signal |
|---|---|---|---|---|---|
| administrative, M77 chunks (K3) | OB spelled, 3 | 0.040 (0.035-0.046) | 0.032 (0.026-0.037) | 0.477 | 0.059 |
| legends, M77 chunks (L1) | OB spelled, 3 | 0.111 (0.094-0.120) | 0.085 (0.071-0.098) | 0.509 | 0.085 |
| legends, whole (L2) | OB spelled, 3 | 0.113 | 0.086 | 0.600 | 0.073 |
| Linear B F0 | Homer, 4 | 0.031 | 0.025 | 0.151 | 0.051 |
| Linear B F1 / F2 (tilted) | Homer, 4 | 0.033 / 0.041 | 0.026 / 0.025 | n/a | n/a |

- **Label-free counts, run 2026-11-24 with scratch scripts outside the repo.** Sign and reading counts, consonant counts of the known cuneiform and Linear B values, segment lengths, bigram shares. No lexicon was matched against any text and no IC was computed. They fill the two "Measured" tables below.
- **Seen and used in choosing the form.** The drafter divided the sealed scrambled widths by the label-free C (defined below): 0.35 (administrative), 0.48 (legends), 0.16 (Linear B). Dividing again by G gives 0.40, 0.51, 0.45. So the choice of C and G as multiplying terms was informed by these three sealed points. The coefficients are not: they are fitted on administrative dial cells only.
- **A consequence, stated now:** a one-constant C × G rule predicts a legend-to-administrative ratio of 2.08, against 2.65 observed. That is 22% short, outside the 15% tolerance below. The kill test can therefore fail.
- **Not seen:** W on any dialled text; W on legends tilted down; any IC on M77; any fit.
- The scratch scripts are not the study code. The sealed code must recompute both tables before any IC (abort A2).

## Prior art
- **Repo.** No sealed study predicts W. `lb_formula_dial` reports r (real over scrambled width) for a formula tilt only. `yj_ic_refute`'s red team noted the wider real null and blamed formulae; `ur3_legend_refute`'s scrambled control says formulae are the smaller part.
- **Opened 2026-11-24** (abstract or page text only, as noted):
  - Goldstein and Rinott, "A permutation test for matching and its asymptotic distribution", arXiv math/0511427 (abstract only). A normal approximation with explicit bounds for a statistic under a uniform random permutation, where baseline similarity is unknown. This is the setting of N1: the claimed pairing of signs and values against all pairings. The variance formula was not read.
  - Petrini et al., "Direct and indirect evidence of compression of word lengths", arXiv 2303.10128, doi:10.53482/2023_54_407 (abstract only). A closed-form random baseline for a frequency-weighted sum when one attribute is permuted across word types. Same structure as N1's mean. The abstract gives no variance.
  - Wikipedia, "Design effect" (en.wikipedia.org/wiki/Design_effect), section on Kish's effective sample size. Unequal weights shrink the effective sample size. C below is the same idea: a few heavy signs carry the sum, so the null has few effective terms.
  - Wikipedia, "Unicity distance" (en.wikipedia.org/wiki/Unicity_distance), and von zur Gathen, "Unicity distance of the Zodiac-340 cipher", IACR ePrint 2021/1620 (abstract only). Cryptanalysis states how much text removes spurious keys, as a function of key entropy and language redundancy. Neither gives the spread of a dictionary score under key shuffles.
- **From memory, not opened (unverified):** Hoeffding's 1951 combinatorial central limit theorem gives the variance of a sum Σ a(i, π(i)) under a uniform permutation; for a product form it is proportional to the sum of squared centred weights. That would make W scale with the square root of a Herfindahl sum. The study tests the scaling and does not rely on it.
- **Not found:** a predictor of permutation-null width for a dictionary-match score from sign-frequency concentration, in cryptanalysis or decipherment. The search was short (three queries). "Not found" is weak evidence that this is new.

## Data (all already held)
- Ur III legends and administrative runs, the true reading-level key, and the OB, Old Akkadian and pooled lexicons: exactly as sealed `ur3_legend_refute` (drop rule, numeral cut, 5% CRC sample, 14 letters).
- Linear B, its true key and the Homeric lexicon: as sealed `lb_shape_ladder` R1 (= `lb_formula_dial` F0).
- M77 seals and sealings, distinct sequences, runs between breaks: as `lb_formula_dial` `m77_target`.

## Properties (frozen definitions; all label-free)
Each is computed per draw on the held-out half, with bins from development plus held-out frequencies, as N1 uses them.
- **C, movable consonant-mass concentration.** m_s = sign s's share of held-out key consonants (its tokens times its consonant count). u_s = the share of signs in s's N1 bin (frequency bin of 10 inside its consonant-count class) that hold the same value as s, itself included. **C = √ Σ m_s² (1 − u_s).** A sign that N1 cannot change adds nothing.
- **G, readable share.** Share of held-out key consonants in segments of at least LMIN consonants.
- **D, lexicon density at LMIN.** Skeletons of length LMIN over (letters)^LMIN.
- **N, size.** Held-out key consonants.
- **T, keyed types.** Keyed sign types in development plus held-out.
- **E, formula excess.** The sealed `lb_formula_dial` function on the held-out chunks.
- **H, sign concentration (reported, not in the predictor).** Σ p_s² over held-out keyed sign tokens. It needs no key at all. Entropy, top-10 share and effective types (1 / H) are reported beside it.
- C, G and N use the consonant counts of the known key. They use no lexicon and no IC.

### Measured: properties (median of 20 draws; range where it matters)
| text | H | effective types | top-10 share | T | C | G | consonants per segment | N | E |
|---|---|---|---|---|---|---|---|---|---|
| **administrative chunks (F0)** | 0.0113 (0.0101-0.0121) | 89 | 0.248 | 508 | **0.091** (0.085-0.095) | 0.885 | 3.86 | 4,450 | 0.164 |
| administrative, whole runs | 0.0109 | 91 | 0.243 | 499 | 0.091 | 0.914 | 4.67 | 4,519 | 0.161 |
| **legend chunks (L1)** | 0.0262 (0.0245-0.0278) | 38 | 0.431 | 433 | **0.179** (0.174-0.187) | 0.932 | 5.07 | 6,020 | 0.255 |
| legends, whole (L2) | 0.0254 | 39 | 0.424 | 436 | 0.176 | 0.988 | 12.2 | 6,001 | 0.252 |
| **Linear B F0** (LMIN 4) | 0.0243 | 41 | 0.367 | 73 | **0.157** | 0.355 | 2.51 | 2,797 | 0.127 |
| M77, 4,014 tokens (no key) | 0.0221 | 45 | 0.339 | 309 | n/a | n/a | n/a | n/a | 0.159 |
| M77, all 9,052 tokens (no key) | 0.0222 | 45 | 0.338 | 395 | n/a | n/a | n/a | n/a | 0.162 |

- Legends are 2.3 times administrative text in H and 1.97 times in C. Their G, T and E differ by far less.
- **M77's sign concentration sits near legends and Linear B, not near administrative text** (45 effective types against 38, 41 and 89).
- Linear B has legend-like C and a narrow null. Its G is 0.355 and its N is under half. So C alone cannot be the predictor.

## Design
### Dials on administrative text (frozen)
- Every dial starts from the sealed F0 draw k (`ur3_legend_refute` `build`, same seeds). Every dial except N2 keeps F0's development half and changes only the held-out half, the lexicon (D) or the keyed set (T). Lexicon OB spelled, LMIN 3, unless the dial says otherwise.
- **N2 rebuilds both halves.** The sealed `build` picks 4,600 chunks and then splits them, so N2's development half is new and about twice F0's size. N2 is the only cell that does not keep F0's development half.
- **Pool.** All chunks of the texts outside draw k's development half, rechunked with M77 lengths. Median 36,300 chunks against 1,146 needed.
- **Tilted draw.** Length-stratified weighted draw without replacement that matches F0's held-out length counts, as `lb_formula_dial` `tilt_draw`. Weight exp(τ f) for a chunk statistic f. τ is bisected on [0, 12], at most 30 steps, and sees only the label-free target. A draw whose length stratum is short, or that does not stop, is unbuilt.

| dial | cells | chunk statistic f / rule | target (tolerance) |
|---|---|---|---|
| **M**, consonant-mass concentration | M1, M2, M3, M4 | share of the chunk's key consonants on the pool's 10 heaviest signs | C² = 0.0132 (±0.0005), 0.0200 (±0.0008), **0.0319 (±0.0008, the legend value)**, 0.0462 (±0.0012) |
| **Hs**, sign concentration | Hs1 | share of the chunk's tokens on the pool's 10 most frequent keyed signs | H = 0.0262 (±0.0005, the legend value) |
| **Ex**, formula excess | Ex1, Ex2 | share of the chunk's pairs in the pool's top 50 (sealed measure) | E = 0.210, 0.255 (±0.005) |
| **N**, size | N¼, N½, N2 | first quarter or half of F0's held-out chunks; N2 = F0 rebuilt with 4,600 chunks (both halves rebuilt) | by construction |
| **S**, segment length | S3, S2 | every held-out chunk cut into pieces of at most 3 or 2 signs; 1-sign pieces dropped | by construction |
| **D**, lexicon density | D¼, D½, D+ | skeleton kept if CRC32 of its text mod 4 is 0 (¼) or below 2 (½); D+ is the pooled spelled lexicon run at LMIN 3 | about 0.045, 0.090, 0.300 |
| **T**, keyed types | T432, T300 | only the top 432 or 300 types by frequency are keyed; the rest are breaks | by construction |

- **Fit cells:** A0 (F0 itself) and the 17 cells above, draws 1 to 10. 18 cells, so at most 18 fit points (one cell median each).
- T is not dialled below 300: coverage would fall under the 90% rule (see table).
- The Hs cell exists to separate H from C. It reaches the legend H while C stays at 0.126.

### Measured: the dials span the needed range (scratch count, no IC)
| cell | built | H | C | G | T | E | coverage |
|---|---|---|---|---|---|---|---|
| A0 (F0) | 20 / 20 | 0.0113 | 0.091 | 0.885 | 508 | 0.164 | 0.986 |
| **M3 (to legend C)** | **19 / 20** | 0.0255 | **0.179** | 0.848 | 461 | 0.226 | 0.972 |
| M2 | 19 / 20 | 0.0187 | 0.142 | 0.867 | 479 | 0.200 | 0.978 |
| M at τ = 12 (limit) | n/a | n/a | 0.270 (0.260-0.282) | n/a | n/a | n/a | n/a |
| **Hs1 (to legend H)** | 19 / 20 | **0.0263** | 0.126 | 0.837 | 475 | 0.196 | 0.989 |
| Hs to 0.0340 (over legends) | 19 / 20 | 0.0341 | 0.142 | 0.815 | 467 | 0.201 | 0.990 |
| Ex2 / Ex1 | 10 / 10 each | 0.0139 / 0.0127 | 0.101 / 0.095 | 0.882 / 0.883 | 489 / 495 | **0.253** / 0.211 | 0.988 |
| N½ / N¼ | 20 / 20 | 0.0116 / 0.0117 | 0.093 / 0.094 | 0.887 / 0.889 | 469 / 445 | 0.152 / 0.151 | 0.985 |
| S3 / S2 | 20 / 20 | 0.0115 / 0.0119 | 0.092 / 0.094 | 0.820 / 0.632 | 504 / 498 | 0.175 / 0.195 | 0.986 |
| T432 / T300 | 20 / 20 | 0.0117 / 0.0123 | 0.093 / 0.097 | 0.867 / 0.847 | 432 / 300 | 0.164 | 0.966 / 0.943 |
| T200 / T100 / T72 (not run) | 20 / 20 | 0.0137 / 0.0188 / 0.0230 | 0.105 / 0.126 / 0.143 | 0.794 / 0.660 / 0.575 | 200 / 100 / 72 | 0.164 | 0.889 / 0.751 / 0.667 |
| legends tilted down: LD1 / LD2 | 16 / 20 each | 0.0187 / **0.0112** | 0.152 / **0.109** | 0.924 / 0.909 | 450 / 467 | 0.235 / 0.217 | 0.969 / 0.953 |

- **The count gate passed.** Administrative text reaches the legend values of C, H and E, each in at least 19 of 20 draws (10 of 10 for E). M1, M4, N2 and the D cells were not built in scratch; M4's target (C 0.215) is inside the measured limit of 0.270.
- **Not reachable on administrative text:** Linear B's T (72) and G (0.355, against 0.632 at S2). The Linear B prediction is an extrapolation in both. It is reported, not graded.
- Legends reach 0.932 in G, above the dial range's top (0.885 to 0.889) by 5%.

### What is measured in each cell (frozen)
- **N1 exactly as sealed** (`permute_in_class_bins`, bins of 10, 1,000 draws), on the real held-out text and on its unigram scramble. W_real and W_scr = N1 p99 minus N1 mean.
- **The fit needs no true-key score.** The true reading's IC is also computed in every cuneiform cell and reported as signal and pass. It enters only check K5.
- Seeds for N1 and the scramble are those of `ur3_legend_refute` for draw k, in every cell.

### Predictor (form frozen; coefficients fitted once)
- **Stage 1, scrambled width:** ln W_scr = b0 + b1 ln C + b2 ln G + b3 ln D + b4 ln N + b5 ln T.
- **Stage 2, formula factor:** ln (W_real / W_scr) = g0 + g1 E.
- **Prediction:** Ŵ_scr from stage 1; Ŵ_real = Ŵ_scr × exp(g0 + g1 E). A cell's predicted width is the median over its built draws of the per-draw prediction.
- **Fit procedure:** ordinary least squares on cell medians (one point per built cell), both stages. A cell's point is the median over its built draws of ln W_scr (stage 1), of ln (W_real / W_scr) (stage 2) and of each property. No weights, no trimming, no draw removed. One fit. The fallbacks below are the only permitted changes.
- **Reported with the fit:** coefficients with 95% intervals from a bootstrap over draw index k (resample the 10 draws, recompute every cell median; 2,000 resamples, seed below); leave-one-cell-out residuals; the same fit with ln √H in place of ln C (report only).
- **Q1 is read from the fit:** a property "tracks W" if its interval excludes 0 and the absolute value of its coefficient times its dialled log range (of fit-cell medians) is at least 0.10 (a 10% change in W). Otherwise it is "not shown to matter in this range".

## Calibration fallbacks (written before any calibration)
The fit is the calibration. These rules are applied in this order, each at most once (F1 may repeat until it holds), and each is logged. **Any other change after the first IC of any cell in this study, K2 included, is seen (to the form, the cells, the features, the tolerances, the seeds or the draws) makes the study INVALID.** An invalid study is labelled so and is not rerun under this name.
- **F0, unbuilt cells.** A fit cell with fewer than 8 of 10 draws built is dropped. If M2 or M3 is dropped: stop (abort A4). If a dial loses all its cells, its term is dropped and reported "not tested".
- **F1, collinearity.** Variance inflation factors are computed on the stage 1 design matrix. If any exceeds **5**, the term with the highest factor is dropped, except ln C, which is never dropped (then the next highest goes). Refit; repeat until all are at most 5. A dropped term is reported "not separable from" its closest partner. F1 is computed at K1, before any IC other than K0's reproduction of sealed values, and the resulting form is frozen then.
- **F2, form.** The residual is |ln (predicted median / observed median)| of stage 1. If the largest leave-one-cell-out residual exceeds **0.18**: **no predictor**. The frozen reading "not predicted" then applies, and checks K3 to K5 and the M77 step are not run. There is no second form.
- **F3, formula factor.** If g1 is negative, or the largest leave-one-cell-out residual of stage 2 exceeds 0.10, stage 2 becomes a constant: the median of W_real / W_scr over the fit points.
- **Not permitted, as examples:** adding a term or an interaction; a new dial or rung; refitting with legends or Linear B; changing bins, LMIN or N1; moving the 15% tolerance or the 0.18 bar of F2; dropping draws; trying a second form.

## Checks, run first and in this order (strongest kill first)
1. **K0, pipeline unchanged.** The study code reproduces sealed `ur3_legend_refute` per draw to 1e-9 on draws 1 to 3 of K3 (administrative) and of L1 (legends): N1 mean, p99, scrambled mean and p99, true IC. A0's fit points and the legend targets are then the sealed values.
2. **K1, tables.** The sealed code recomputes both "Measured" tables and builds every cell. F0 and F1 are applied here, on label-free counts, and the form is frozen. K1 computes no IC.
3. **K2, the one-cell kill.** M3 is scored on 20 draws before any other dial cell; at least 16 of 20 draws built, else abort. Administrative text at the legends' C must show a scrambled width at least half-way, in log terms, from 0.032 to 0.085: **median W_scr ≥ 0.052.** Below that the concentration account is dead and nothing else runs.
4. **Fit.** The other fit cells run; the fit is made on the form frozen at K1; F2 and F3 are applied.
5. **K3, planted known answer (sealed widths).** The fitted predictor, given only label-free properties, must give **legend chunks (L1): W_scr within 15% of 0.085 and W_real within 15% of 0.111** (|ln ratio| ≤ 0.14, medians of 20 draws). L2 (0.086, 0.113) is reported. **Linear B F0 is reported, not graded:** its predicted W_scr and W_real are printed beside the sealed 0.025 and 0.031, with the ratio. It is an extrapolation in T and G, and no pass or fail is attached.
6. **K4, blind widths.** Legends tilted down in sign concentration (the Hs statistic with weight exp(−τ f), where f is a unit's share of the pool's top-10 keyed signs, pool and tilted draw built from legends as for the dials; LD1 to H 0.0188, LD2 to H 0.0113, each ±0.0005; 20 draws). Their W has never been computed. The prediction file is committed and hashed before LD1, LD2, V1 or V2 is scored; it also holds Ŵ for V1 and V2. Both medians of W_scr and of W_real must be within 15%. A cell with fewer than 12 draws built is "not run" and K4 then rests on the other. If both are not run, or V1 or V2 builds fewer than 16 of 20 draws, the M77 step is not run.
7. **K5, pass follows from predicted width.** Two validation cells outside the fit, 20 draws each: **V1** = the M2 draw cut as S3; **V2** = the first half of the M3 draw's chunks. In each:
   - median Ŵ_real within 15% of the median measured W_real;
   - with S_k the true reading's signal in draw k, the predicted pass count P̂ = number of draws with S_k > Ŵ_real,k must be within 3 of the measured pass count P.
8. Only then the M77 step.

## The M77 step (label-free; no key scored)
- Runs only if K3, K4 and K5 all pass.
- **Nothing is scored on M77.** No IC, no N1, no lexicon match, no claimed or fitted key. The step counts M77's shape and puts the counts into the fitted formula.
- M77 has no key, so C, G and N need a stated key shape. Three are frozen. **Sc is primary and the only shape that gets S_min. Sa and Sb are reported as sensitivity rows.**
  - **Sa, administrative shape.** The r-th most frequent M77 sign takes the consonant count and u_s of the r-th most frequent keyed sign of administrative draw k (ties by sign name).
  - **Sb, legend shape.** The same from legend draw k.
  - **Sc, flat.** Every sign has one consonant and no bin-mate shares its value, so u_s = 1 / (size of s's bin). Then C ≈ √(0.9 H).
- A transplant copies only each sign's consonant count and u_s; no value string is assigned to any M77 sign or written to disk.
- These are shapes, not readings. Nothing from them is matched against a lexicon.
- Text: distinct M77 seal and sealing texts, split in half at random 20 times; the held-out half's runs are the chunks. D is the primary lexicon's 0.180 at LMIN 3. E is M77's own.
- **Output:** for every shape, the median Ŵ_scr and Ŵ_real with the ×/÷ 1.15 band. For Sc only, the **implied minimum signal** S_min = Ŵ_real × 1.15 × q80, where q80 is the pooled 80th percentile of W_real,k over its cell median across the fit cells. A true key whose signal sits at S_min would pass about 16 of 20 draws.
- Beside it, the signals true keys have shown: 0.059 (administrative), 0.085 (legends), 0.051 (Linear B). Signal rose with width on these texts, so they are not a forecast for M77.
- **Range rule.** If an M77 property under a shape lies outside the fit cells' range of cell medians by more than 10%, that shape's row is marked "extrapolated". If the shape is Sc, no S_min is given.
- Scratch count under Sa (now a sensitivity shape), seen before drafting: C 0.115, G 0.931, N about 5,100, T 395, E 0.160. C, N, T and E are inside the dial range; G is 5% above it.

## Readings (frozen; worded for the bench)
- **K2 fails:** "Raising consonant-mass concentration on administrative text to the legend level does not widen the scrambled null half-way. Concentration does not account for the legends' wider null." No fit, no M77 step.
- **No predictor (F2):** "These properties do not predict W across the dials to a log residual of 0.18." No M77 step.
- **K3 fails:** "A predictor built on administrative dials does not reach the legends' width. The form, or a property other than C, G, D, N, T and E, is responsible." The miss and its sign are reported. No M77 step.
- **K3 passes, K4 fails:** "The predictor matches the legends at their own shape but not when they are moved. Not shown to be general." No M77 step.
- **K5 fails with K3 and K4 passed:** "Width is predicted; pass or fail is not." The M77 step is not run.
- **All pass:** "The shuffle null's width on the Ur III benches tracks [the properties that met the Q1 rule] and can be predicted from label-free shape to within 15%. On M77's shape the predicted width is [Ŵ_real under Sc]; a true key would need a signal of at least [S_min] on this bench (token IC, N1, a cuneiform-like lexicon at density 0.18, LMIN 3, under the flat shape). Signal rose with width on the read texts, so the signals listed are not a forecast for M77." If Sc is marked "extrapolated", the S_min clause is replaced by "no minimum signal is stated".
- **Linear B** is an extrapolation and sets no scope. Its predicted and sealed widths are reported and change no reading.
- K3 is a known-answer check, not a blind one: its targets were seen and helped choose the form. K4 and K5 are blind.
- No reading says anything about any Indus key. A predicted W above the signals seen so far would say that fit-refute lacks stated power at M77's shape on this bench. It would not say any key is wrong.

## Aborts
- **A1.** K0 does not reproduce: stop.
- **A2.** A recomputed property in the first table differs from its table value by more than 5% (G, C, H, T, N) or 0.01 (E), or a cell marked 19 / 20 or 20 / 20 builds fewer than 16: stop and redraft.
- **A3.** A scrambled-text control (true reading on the scramble) passes in more than 1 of 20 draws in K2, V1 or V2: stop.
- **A4.** M2 or M3 is dropped under F0, or M3 builds fewer than 16 of 20 draws at K2: stop.
- **A5.** The Indus compute lock is not held, or free memory is below the 20% guard: do not start.
- **A6.** Any step would compute an IC, an N1 or a lexicon match on M77: stop. The code path for the M77 step must not import the scorer.
- No rerun, no tuning, no fix tags after any IC is seen.

## Seeds
- F0 draws, N1, scramble and scramble N1: the sealed `ur3_legend_refute` seeds (base 20261126) for draw k, in every cell. Linear B: sealed `lb_shape_ladder` seeds.
- Study base 20261130. Pool rechunk: base + 1000k. Tilt uniforms: base + 100,000 + 1000k + cell index (cells in the order of the dial table, then LD1, LD2).
- N2: `build` with 4,600 chunks and the sealed draw seed.
- Lexicon thinning: CRC32 of the skeleton's letters joined as text; no seed.
- Bootstrap over draw index k: base + 900,000. M77 splits: base + 800,000 + k.
- Excess baseline: 20261129 + k, as `lb_formula_dial`.

## Limits stated in advance
- **One bench family.** One statistic (token IC), one null (N1), bins of 10. A different null has a different width law.
- **The fit lives on one corpus and one lexicon.** Legends share period, script, key and lexicon with it. Linear B is the only other script, is out of range in two properties, and is reported without a grade. Nothing here shows the predictor holds outside cuneiform.
- **A tilt changes content as well as concentration.** M3 also raises E to 0.226 and lowers G to 0.848. The fit separates them only as far as the other dials allow (F1 guards this).
- **D+ changes lexicon content as well as density.** D¼ and D½ thin the OB spelled lexicon; D+ swaps in the pooled spelled lexicon (OB, Old Akkadian and Rimanum forms). Its effect on W cannot be put down to density alone.
- **N2 changes the development half as well as N** (see the dials).
- **C needs consonant counts.** For a read script they are known. For M77 they are assumed (Sc primary, Sa and Sb as sensitivity), so Q3's answer is conditional on the shape, and on a cuneiform-like lexicon at density 0.18.
- **The form was chosen after seeing three sealed widths** (see "What was seen").
- K3's 15% is wide against the draw-to-draw spread of W (about ±12%) and narrow against the gap to be explained (2.65 times).
- Dial cells use 10 draws; each W is a 99th percentile of 1,000 shuffles.
- The fit has at most 18 points for up to 6 stage 1 coefficients. Intervals will be wide.
- S_min treats a key's signal as fixed across draws. Real signals vary, so S_min is a floor.

## Cost
- 18 fit cells × 10 draws, M3's 10 further draws, LD1, LD2, V1, V2 × 20 draws: about 280 draw-cells of 2,000 N1 scores each, less the sealed A0.
- At the sealed run's speed (about 6 minutes per 20 draws with 4 small workers): about 1.5 hours, plus about 10 minutes of label-free building. Under the Indus compute lock, through `board/run.sh`.
- Outputs: small JSON files with per-draw summaries. No permutation arrays are saved.

## Decisions (settled by the review of v1)
1. **Linear B gets no dials and is demoted.** It is reported, not graded, and sets no scope.
2. **The rank transplant is sensitivity only, and Sc is primary.** Only Sc gets S_min.
3. **The K2 bar stays at 0.052** (half the log gap).
4. **No T cells below 300 types.** The bench's 90% coverage rule holds inside this study.
5. **The fit uses cell medians**, one point per built cell, not per-draw points.
6. **The tolerance is 15% for K3 to K5 and 0.18 for F2.**

## Before sealing
- A fresh review of v2. Code written and hashed after sealing, before any IC.

## Review log
- **2026-11-24, v1, fresh review: FIX.** v2 applies it. No IC was run between v1 and v2, and no number in the tables changed.
  - Fit on cell medians; bootstrap over draw index k.
  - F1 computed at K1, before any IC; the form is frozen then.
  - F2: linear-form fallback deleted; bar 0.18; above it, no predictor.
  - INVALID clause now starts at the first IC of any cell, K2 included. K2 needs 16 of 20 draws built.
  - Linear B reported, not graded; it sets no scope.
  - K4 prediction file committed and hashed before LD1, LD2, V1 or V2 is scored; it also holds Ŵ for V1 and V2.
  - M77 step: Sc primary and alone gets S_min; Sa and Sb are sensitivity rows; a transplant copies only consonant count and u_s.
  - "All pass" reading says "tracks", names the bench, and says the listed signals are not a forecast for M77.
  - N2 stated to rebuild its development half; D+ stated to change lexicon content.
  - "Open questions" replaced by "Decisions".
- Pre-seal check of v2: SEAL-WITH-EDITS, eight edits (Sc's C ≈ √(0.9 H); K0 exception to "before any IC"; LD tilt frozen; unbuilt K4/K5 cells; per-draw prediction median; A2 floor 16; three readings narrowed; Q1 absolute value). Applied; sealed as v3.
