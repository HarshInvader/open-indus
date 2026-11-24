# Wrong lexicon and matcher dial: does the refute bench detect language, and does a generous matcher remove its power? (SEALED; no code existed and no IC had been computed at sealing)

Status: **SEALED v5**, 2026-11-24 (v4 plus the pre-seal check's seven edits: K2 try cap 100,000; Od always run; K2 frozen at 13 cells, 260 draws). Drafted by Fable (brief 9, study 2, plus a second arm asked for by the coordinator). The review of v2 returned FIX on Arm A and REDESIGN on Arm B's rungs; the review of v3 returned FIX. Both sets of fixes are applied (lists at the end). A narrow pre-seal check of v4 returned SEAL-WITH-EDITS; its edits are applied. Main line (a), the claim bench.

## Why
- `lb_formula_dial` read "Both needed": the true Linear B key keeps refute power at Indus formula excess (F1 × 1.0: 16 of 20) and at 1.18 values per sign (17 of 20), and loses it with both (12 of 20).
- That leaves two things open.
  - **Arm A.** The refute standard has only ever been scored against the right language. If the true key also beats its shuffles against a wrong-language lexicon, a pass shows structure in the text, not the language.
  - **Arm B.** `yj_ic_refute` used a generous matcher: one key letter stands for several Sanskrit sounds. `lb_formula_dial` did not dial this. Does a matcher of that looseness remove refute power for a true key with one value per sign?
- **No Indus key is scored. No outcome supports or counts against any Indus key, and none licenses a rerun of one.**

## What was seen before this draft
- **Sealed results:** `lb_certify`, `lb_shape_ladder` (+ addendum 1), `yj_ic_refute`, `scott_ic_refute`, `lb_formula_dial` (all cells). So F0 and F1 with the sealed matcher at LMIN 4 are known: 20 and 16 of 20.
- **Label-free counts** (key files, lexicons and token counts only; no IC). They are in the tables below:
  - the generous matcher's looseness and density, from `yj_ic_refute`'s own code;
  - the sealed Linear B matcher's looseness, on held-out F0 from the sealed builder (56,100 key consonant tokens, 20 draws pooled);
  - lexicon density and rule LMIN at every step of the Arm B list;
  - density of each Arm A lexicon before and after thinning, and its overlap with Homer;
  - the share of key consonants in segments of 5 or more, on held-out F0 and on the `yj_ic_refute` corpus;
  - the sizes of the true key's value classes.
- **The v2 rungs were measured by the reviewer and withdrawn.** They targeted sounds per letter (g) and reached densities of 0.527-0.775 at 4 consonants, with rule LMIN 5-6, far looser than the generous matcher (0.339, LMIN 5).
- **The v3 type counts were recounted.** v3 counted modern Greek types in raw case and Latin-script types before dropping unmappable words. v4 uses one rule for all lists; the numbers that moved are listed at the end.
- **Not seen:** any IC of the true key against another lexicon, under a looser matcher, or at LMIN 5.

## Prior art
- **Repo.** `lb_certify`'s prereg dropped a planned Latin-fitted-key control. No sealed study scores a true key against a wrong-language lexicon, and none dials the matcher on a true key. Atlas 1.8 ranks languages by fitted keys, which is a different test (planted-language z 0.3-2.8).
- **Opened 2026-11-24:**
  - Luo et al. 2020, arXiv 2010.11054 (abstract only). A closeness measure that picks the related language for Gothic and Ugaritic. It fits a mapping; it does not test a stated key against shuffles with the wrong lexicon.
  - Tamburini 2025, doi:10.3389/frai.2025.1581129. No chance baseline and no wrong-language control.
- **Not opened today (unverified):** Raghavendra 2026 (SIGIL, arXiv 2608.02999). A search summary says fitted keys reach high dictionary coverage for English, Sanskrit and Tamil on one corpus. That concerns fitted keys, not a true key against shuffles.
- The search was short. "Not found" is weak evidence that this is new.

## Data (all already held)
- Linear B, the true key, the Homeric word list and the R1 set-up: as `lb_shape_ladder`.
- **F0 and F1 draws: `lb_formula_dial`'s sealed builder, unchanged, with its seeds.** F0 is R1's held-out set. F1 is the length-stratified tilt to M77's formula excess. Its 2 unbuilt draws of 20 stay unbuilt and count as non-passes, as in that study.
- Scored size: about 4,000 tokens per draw.
- Other word lists: texts in `experiments/decipherability/raw` (modern Greek, Finnish Kalevala, Indonesian, Hungarian, Spanish).

## Lexicon construction (frozen; one builder for every lexicon and rung)
- **Greek tokeniser:** tags removed (Homer only), then the sealed pattern for runs of Greek letters.
- **Word types (one rule for every list).** Each token is lower-cased, decomposed by NFD and stripped of combining marks. Unmappable words are dropped (Latin-script lists only; see below). The distinct strings left are the word types.
- **Sounds.** Each Greek consonant letter is one sound: π β φ κ γ χ τ θ δ λ ρ ζ μ ν σ. **ξ is κ + σ and ψ is π + σ.** ς is σ.
- **M0 letter of a sound:** p for π β φ; k for κ γ χ; t for τ θ; r for λ ρ; d, z, m, n, s for δ, ζ, μ, ν, σ.
- **The sealed skeleton rules run on M0 letters, before any expansion:** a final s, n or r is dropped; s, n, r or m before a consonant is dropped; a doubled consonant is single; 1 to 7 consonants are kept. The surviving sounds are stored.
- **Expansion.** A table gives, for each sound, the key letters that may stand for it. A word yields every combination.
- **q rule (frozen).** q may stand for the eight M0 sounds of p, t and k (π β φ τ θ κ γ χ) at every rung. It is never widened.
- **Checked (label-free):** at M0 this builder gives exactly the sealed skeleton set (10,491 skeletons, set-equal).
- **Density** = q-free skeletons of length L over 9^L. **Rule LMIN** = the smallest L with density ≤ 25% (frozen in `lb_shape_ladder`).

## Statistic, null and bars (as sealed)
- **Token IC:** the share of held-out key consonants inside a lexicon word of at least LMIN consonants.
- **N1:** values permuted across signs within frequency bins of 10 (dev plus held-out frequencies), inside each consonant-count class. 1,000 draws. All cells of a draw share R1's N1 seed.
- **Refute pass (per draw):** true IC above the N1 99th percentile. **A cell passes at ≥ 16 of 20. It fails clearly at ≤ 12,** the level of the sealed failing cell in `lb_formula_dial` (F1 × 1.18). 13-15 is "at the edge".
- **Scrambled-text control (every cell):** on a unigram shuffle of the same chunks, at most 1 of 20.
- **Width W, signal and margin:** as in `lb_formula_dial`.

## Arm A: other lexicons, sealed matcher (M0), LMIN 4, F0 only
### The lexicons
| label | source | role |
|---|---|---|
| H | Homeric, sealed (Iliad and Odyssey) | reference (20 of 20, sealed) |
| G | modern Greek, Wikipedia sample | **planted answer:** the right language from another source |
| Fi | Finnish, Kalevala | wrong, not Indo-European |
| Id | Indonesian, Wikipedia sample | wrong, not Indo-European |
| Hu | Hungarian, Wikipedia sample | wrong, not Indo-European |
| Es | Spanish, Wikipedia sample | **report only** (Indo-European, and too thin to match) |
| Od | Homeric, Odyssey only | **report only** (added after the v3 review, always run; too thin to match) |

- **The five letter-renamed Homeric lexicons of v2 (W0) are dropped.** Scoring the true key against a letter-renamed lexicon is the same as scoring a letter-renamed key against the true lexicon, which the null calibration (K2) already does.
- **Od** is there to help locate a failure of the planted answer. It is the sealed lexicon's own language and genre with about half the skeletons. Its density is well below H's, so it decides nothing.

### Mapping for Latin-script lists (frozen)
- **Tokeniser:** runs of letters. Types by the rule above.
- **Unmappable:** a word with any character outside a to z after that rule is dropped.
- Letter to Greek sound: p → π, b → β, f → φ, v → β; k → κ, g → γ, c → κ, q → κ; x → κ + σ; t → τ; d → δ; l → λ, r → ρ; z → ζ; m → μ; n → ν; s → σ.
- a e i o u are vowels.
- **h, j, w and y are skipped as if absent.** They are neither vowels nor breaks: the letters on either side of one are treated as adjacent.
- Then the same builder as above.

### Thinning (frozen)
- A lexicon denser than H at 4 consonants is thinned.
- Its word types are sorted by code point and shuffled once with Python's `random.Random(20261202).shuffle`. Types are removed from the end in steps of 500.
- **The kept size is the step whose density at 4 consonants is nearest 0.177,** not the first step inside a band. A tie goes to the larger size.
- A lexicon thinner than H cannot be raised.

### Measured (label-free, under the type rule above)
| lexicon | word types | density at 4 / 5, full | types kept | density at 4 / 5, thinned | share of its 4-consonant skeletons that are Homeric (full list) |
|---|---|---|---|---|---|
| H | 28,144 (30,747 raw forms in the sealed count) | 0.1770 / 0.0143 | all | same | 100% |
| G | 20,420 | 0.2076 / 0.0222 | 13,920 | 0.1768 / 0.0180 | 47.5% |
| Fi | 20,653 | 0.1881 / 0.0157 | 17,653 | 0.1756 / 0.0142 | 46.9% |
| Id | 14,025 | 0.1911 / 0.0131 | 12,025 | 0.1770 / 0.0113 | 41.5% |
| Hu | 17,967 | 0.2672 / 0.0327 | 8,967 | 0.1760 / 0.0185 | 30.8% |
| Es | 11,571 | 0.1585 / 0.0137 | all | 0.1585 / 0.0137 | 42.9% |
| Od | 16,145 | 0.1254 / 0.0082 | all | 0.1254 / 0.0082 | 100% |

- Words dropped as unmappable: Fi 0, Id 471, Hu 160, Es 147.
- **K3, matched density.** A lexicon is used for a reading only if, after thinning, its density is within 0.005 of 0.177 at 4 consonants and within 0.01 of 0.0143 at 5. G, Fi, Id and Hu meet the bounds. Es and Od do not and are report-only.
- **K3 abort.** The code recomputes the table. It aborts if a type count or kept size differs from the table, or a density differs by more than 0.0005.
- **Stated in advance: the wrong lexicons are not independent of Homer.** By chance 17.7% of 4-consonant strings are Homeric. The wrong lexicons share 31-47% of theirs with Homer, because languages favour the same common consonants. So a pass against a wrong lexicon may reflect that shared skew.
- **Stated in advance: on this measure modern Greek (47.5%) is no closer to Homer than Kalevala (46.9%).** The planted answer may therefore be weak. The readings below say what follows if it fails.

## Arm B: matcher dial (redesigned)
### Design
- **Anchor: lexicon density, not sounds per letter.** The generous matcher gave density 0.339 at 4 consonants and 0.092 at 5, with rule LMIN 5.
- **Near-partition style.** That matcher loads its looseness on four letters (n 6, s 5, t 4, d 4 sounds), leaves six letters exact, and lets only 3 sounds match two letters. Here the added looseness goes on **two letters only, d and t**. p and k keep their sealed 3 sounds, r its 2, and z, m, n, s stay exact.
- Greek has 15 consonant sounds and all belong to a key letter already, so a letter can only gain sounds that another letter also stands for. Overlap cannot be avoided; it is confined to d and t.
- **Frozen order of added pairs** (dentals first, then sibilants, then nasals, then liquids; d before t at each sound).

### Measured at every step (label-free; held-out F0, q fixed)
Distance = |ln(density at 4 / 0.339)| + |ln(density at 5 / 0.092)|.

| step | pair added | density at 4 / 5 / 6 | rule LMIN | sounds on d, t | g | token share on multi-sound letters | sounds matching 2+ letters (q aside) | distance |
|---|---|---|---|---|---|---|---|---|
| **0 (B0)** | none (sealed) | 0.177 / 0.014 / 0.0005 | 4 | 1, 2 | 2.19 | 0.671 | 0 | 2.51 |
| 1 | d ← τ | 0.252 / 0.026 / 0.0010 | 5 | 2, 2 | 2.27 | 0.745 | 1 | 1.57 |
| 2 | d ← θ | 0.269 / 0.029 / 0.0012 | 5 | 3, 2 | 2.34 | 0.745 | 2 | 1.38 |
| **3 (B1)** | t ← δ | 0.286 / 0.034 / 0.0014 | 5 | 3, 3 | 2.52 | 0.745 | 3 | 1.18 |
| 4 | d ← ζ | 0.289 / 0.034 / 0.0014 | 5 | 4, 3 | 2.59 | 0.745 | 4 | 1.15 |
| 5 | t ← ζ | 0.292 / 0.035 / 0.0015 | 5 | 4, 4 | 2.77 | 0.745 | 4 | 1.12 |
| 6 | d ← σ | 0.310 / 0.045 / 0.0021 | 5 | 5, 4 | 2.84 | 0.745 | 5 | 0.81 |
| 7 | t ← σ | 0.328 / 0.055 / 0.0029 | 5 | 5, 5 | 3.02 | 0.745 | 5 | 0.55 |
| 8 | d ← ν | 0.349 / 0.066 / 0.0039 | 5 | 6, 5 | 3.09 | 0.745 | 6 | 0.36 |
| **9 (B2)** | t ← ν | 0.366 / 0.077 / 0.0051 | 5 | 6, 6 | 3.27 | 0.745 | 6 | 0.26 |
| 10 | d ← λ | 0.374 / 0.084 / 0.0064 | 5 | 7, 6 | 3.34 | 0.745 | 7 | 0.19 |
| **11 (B3)** | t ← λ | 0.382 / 0.091 / 0.0078 | 5 | 7, 7 | 3.52 | 0.745 | 7 | 0.13 |
| 12 | d ← ρ | 0.393 / 0.100 / 0.0105 | 5 | 8, 7 | 3.59 | 0.745 | 8 | 0.23 |
| generous matcher (target) | | 0.339 / 0.092 / 0.0128 | 5 | largest letter 6 | 3.36 | 0.752 | 3 | 0 |

### Rungs (frozen from this table)
- **B0:** step 0, the sealed matcher.
- **B2 (top):** the step nearest the target by the distance above, among steps where no letter stands for more than 6 sounds (the generous matcher's largest) and rule LMIN is 5. **That is step 9:** density 0.366 / 0.077, g 3.27, token share 74.5%.
  - B2 is somewhat denser than the target at 4 consonants and somewhat thinner at 5.
- **B1 (intermediate):** step 3, the plain merger of the three dental sounds on both letters. Density 0.286 / 0.034.
- **B3 (report-only):** step 11, the step nearest the target on density alone (0.382 / 0.091). It puts 7 sounds on d and on t, one more than the generous matcher's largest letter. It is run on F0 and F1 at LMIN 5, and it limits the "no loss found" reading below.
- **Every rung is thinner than the target at 6 consonants** (0.0051 at B2 and 0.0078 at B3, against 0.0128).
- g is reported and not targeted.
- **Abort rule.** The code recomputes density and rule LMIN per rung. A rung whose rule LMIN exceeds 5, or whose density at 4 or 5 differs from the table by more than 0.002, is not run.
- **What the dial copies and what it does not.** It copies the lexicon density the matcher produces at 4 and 5 consonants, the token share on multi-sound letters, and (to B2) the cap on sounds per letter. It has twice the overlapping sounds (6 against 3), two loose letters where that matcher has four, a 9-letter alphabet against 16, and another language.

### LMIN
- Rule LMIN is 4 at B0 and 5 at B1, B2 and B3. So moving off B0 changes two things at once: the matches, and the word length that counts.
- **B0, B1 and B2 are scored at LMIN 5 and at LMIN 4.** B0 × LMIN 5 is the control that isolates the LMIN change: the sealed matcher, longer words only.
- **Measured (label-free):** 18.6% of key consonants on held-out F0 sit in segments of 5 or more consonants (35.6% in segments of 4 or more). On the `yj_ic_refute` corpus the figure is 47.4%. So LMIN 5 leaves far less of this text able to score than it left there.

### Cells
- B0, B1, B2 × F0, F1 × LMIN 5, LMIN 4: 12 cells. The two B0 × LMIN 4 cells repeat sealed results.
- B3 × F0, F1 × LMIN 5: 2 cells, report-only.
- True key, one value per sign, 20 draws.

**Primary cells (named now):** F0 × B2 and F1 × B2 at LMIN 5. **Control cells:** F0 × B0 and F1 × B0 at LMIN 5. **The control cells run before any B1, B2 or B3 cell.**

## Checks, run first and in this order
- **K1. The rebuilt matcher reproduces R1.** F0 × B0 × LMIN 4.
  - The lexicon equals the sealed skeleton set exactly.
  - 20 of 20, scrambled-text control ≤ 1 of 20.
  - Each draw's true IC, N1 mean and N1 99th percentile equal the sealed R1 values to 1e-9.
  - Failure: **STOP.**
- **K2. Null calibration with a fully wrong key.** This is a check on the null, not a planted answer.
  - **The wrong key.** The signs are grouped by consonant-count class. Within each class the values are shuffled across signs until no sign keeps a value equal to its own, with up to 100,000 tries. If no try succeeds, the draw is reported and counts as void in every K2 cell.
  - **A class with a single distinct value keeps it.** That covers the 15 vowel signs and the one 2-consonant sign (counted on all 20 draws). So the wrong key differs from the true key on the 55-57 one-consonant signs, which carry 10 distinct values.
  - One wrong key per draw, seeded below.
  - It is scored like the true key against its own N1, in the 7 Arm B cells at F0 (B0, B1, B2 at both LMINs; B3 at LMIN 5) and against the 6 Arm A lexicons other than H (H at LMIN 4 is the F0 × B0 × LMIN 4 cell): 13 cells, 260 draws.
  - By construction it passes about 1% of the time. Under "≤ 1 of 20" a cell would be voided falsely about 2% of the time, and one of many cells about a quarter of the time. So the rule is: **a cell is void at 3 or more of 20** (about 0.1% by chance), and the pooled pass rate over all wrong-key draws must be ≤ 3%.
  - A void cell is reported and removed from every reading. If the F0 × B0 × LMIN 4 cell is void, or the pooled rate exceeds 3%: **STOP.**
- **K3. Matched density.** As defined in Arm A, before any IC against another lexicon.
- **KG. The planted answer.** The true key against G must pass (≥ 16 of 20, control ≤ 1). It is a gate on how Arm A may be read, not a stop.

## Readings (frozen; worded for the bench, not for any claimant)
Let P(x) be the passes out of 20.

**Not interpretable (applies to both arms).** A cell whose scrambled-text control exceeds 1 of 20, or that K2 voided, is "not interpretable". It enters no reading, and a reading that names it cannot be drawn.

### Arm A
- **"The bench detects structure, not language."** P(Fi) ≥ 16, or at least two of Fi, Id, Hu have P ≥ 16; each counted cell interpretable.
  - Then a refute pass does not show the claimed language. A refute failure still counts against a key at tested power.
  - This reading does not need KG.
- **"Language-specific at this shape."** KG holds; Fi, Id and Hu are all interpretable; and all three fail clearly (≤ 12).
- **"Partly language-specific."** KG holds and neither reading above applies. Median margins are reported beside H's (+0.021).
- **"Uninterpretable: the bench does not carry to a second lexicon of the right language."** KG fails and the first reading does not apply. An all-fail then says nothing about language, because the right language failed too. It is recorded as a limit: the sealed standard is tied to its own lexicon. P and median margins of G and each wrong lexicon are reported side by side; a lead for G is described and supports no claim.
- **Es and Od** are reported with their densities and never enter a reading.

### Arm B
- **"LMIN 5 alone removes power."** P(F0 × B0) < 16 at LMIN 5. Then longer words, not extra matches, cost the power, and the B1, B2 and B3 cells cannot separate the two. The other Arm B readings are then reported as "not separable from the LMIN change". This holds on this text shape (18.6% of key consonants in segments of 5+; 47.4% on the `yj_ic_refute` corpus), so it says nothing about LMIN 5 there.
- **F1 control below the bar.** If P(F1 × B0) < 16 at LMIN 5, the F1 × B2 and F1 × B3 cells are "not separable from the LMIN change", and Arm B is read on F0 alone. Each reading below then uses its F0 cells only.
- **"Matcher looseness at this density removes power."** The F0 control passes and P(F0 × B2) ≤ 12.
- **"It removes power at Indus formula excess."** P(F0 × B2) ≥ 16, the F1 control is ≥ 16, and P(F1 × B2) ≤ 12.
- **"At the edge, not resolved."** A primary cell at 13-15 where its control passes. The sealed F1 cell is itself at the bar (16), so a drop of 1-3 cannot be told from noise; 12 is the level at which the sealed study called a failure.
- **"No loss found at this density."** Both primary cells ≥ 16 and both B3 cells ≥ 16.
- **"No loss at B2, not held at the denser step."** Both primary cells ≥ 16 and a B3 cell below 16.
- **B1** and the LMIN 4 cells are reported and decide nothing. B3 decides only between the last two readings.
- **Paired draws.** For each primary cell and its control, the report gives the number of draws that pass the control and fail the primary, and the number that fail the control and pass the primary. These are described and change no reading.

### What Arm B can and cannot say about `yj_ic_refute`
- **It can say:** whether a true key with one value per sign keeps refute power on Linear B with a Homeric lexicon at about 4,000 tokens, when the matcher is loosened to roughly the lexicon density, multi-sound token share and sounds-per-letter cap of that bench's matcher, with and without Indus formula excess.
- **It cannot say:**
  - whether Yajnadevam's key is right or wrong;
  - that the low planted power in that bench had this cause, or did not. The language, lexicon, alphabet size, pattern of overlap, plant and corpus size (about 12,000 tokens) all differ;
  - anything about his readings, which involve choices outside the key.
- **"No loss found" does not clear that bench's encoding of his stated latitude.** It shows one true key keeping power under one imitation of it.
- Whatever the outcome, atlas 1.1's entry for that key stays "untestable by fit at stated power".

## What changes
- **Method.** One or two lines for atlas 1.1 and the scorecard notes: whether a refute pass is language-specific, and what the matcher dial showed in this calibration.
- **Scorecard.** No tier changes.
- **Reruns: none licensed.** No outcome of this study permits scoring any Indus key again. That would need its own sealed design and kill test.
- **Next.**
  - If Arm A reads "structure, not language", the standard's wording on the scorecard page becomes "refute-only; language not tested".
  - If Arm B reads "no loss found", matcher looseness is not shown to be a cause in this calibration and is not ruled out for that bench. The plant, the lexicon and corpus size remain untested as well. The next study is chosen by a fresh ranking.

## Limits stated in advance
- K1's outcome is known, so it is a calibration check.
- The wrong lexicons share 31-47% of their 4-consonant skeletons with Homer, against 17.7% by chance.
- The planted answer (modern Greek, Wikipedia) is 2,700 years from the Linear B texts and overlaps Homer no more than Kalevala does.
- The Latin-letter mapping is crude (c is always κ; digraphs are ignored; h, j, w and y vanish).
- Density is matched at 4 and 5 consonants only. Sources differ in genre: two epics and four Wikipedia samples.
- **At every loosened rung d and t stand for the same sounds, so the dial merges two key letters; the generous matcher merges none.**
- **Added looseness covers about 25% of tokens, against 49.4% on that matcher's four loosest letters.** (d and t carry 25.0% of held-out F0 key consonants; n, s, t and d carry 49.4% of that corpus's.)
- **The dial is thinner than the target at 6 consonants** (0.0051 at B2, 0.0078 at B3, 0.0128 on the target).
- The dial is one imitation: two loose letters, six overlapping sounds at B2, a 9-letter alphabet. The order of added pairs is a judgement, fixed now.
- B1, B2 and B3 change LMIN from 4 to 5 together with the matches. The B0 × LMIN 5 control separates them only if it passes, and only 18.6% of key consonants sit in segments long enough to score at LMIN 5.
- The wrong key of K2 leaves the vowel signs and the one 2-consonant sign unchanged.
- About 4,000 scored tokens; one script.
- Bars are fixed and no multiplicity correction is made. The readings are descriptive.

## Seeds
- Draws, F0, F1 and N1: the sealed `lb_formula_dial` and `lb_shape_ladder` schemes, unchanged.
- Thinning shuffle, one per lexicon: `random.Random(20261202)`.
- Fully wrong keys: `random.Random(20261203 + 1000 × k)` for draw k.
- Scrambled texts: as sealed.

## Cost
- Arm A: 7 lexicons × 20 draws. Arm B: 14 cells × 20 draws. K2 adds one key per draw in 13 cells.
- About 420 jobs with 1,000 N1 keys each on real and scrambled text. **Estimate, nothing timed:** about 2.5 hours on 4 workers.
- Runs under the Indus compute lock, with `nice -n 20`, 4 workers and the memory guard.
- Code: `experiments/lb_wrong_lexicon/run.py`, hashed in `HASHES.txt` before any run. Order: label-free tables and aborts, K3, K1, K2, KG, the B0 × LMIN 5 controls, then the other cells.
- Changes after sealing go in `lb_wrong_lexicon_add1.md`, hashed before the affected step.

## Before sealing
| item | state |
|---|---|
| Generous-matcher looseness and density from `yj_ic_refute`'s code | done (0.339 / 0.092 / 0.0128, LMIN 5; g 3.36; 75.2% of tokens; largest letter 6; 49.4% on its four loosest letters) |
| Sound-level builder equals the sealed lexicon at M0 | done (set-equal, 10,491) |
| Density at 4, 5 and 6, rule LMIN, g and token share at every Arm B step; rungs frozen | done (B1 = step 3; B2 = step 9; B3 = step 11) |
| Arm A type counts, kept sizes, densities and Homer overlap under the single type rule | done (table above; G matches the reviewer's recount) |
| Segment shares at 5+ (18.6% on F0; 47.4% on the `yj_ic_refute` corpus) | done |
| Value classes of the true key (15 vowel signs, 55-57 one-consonant signs, 1 two-consonant sign) | done |
| Further fresh review of v4 | pending |
| Hash of this file and of `run.py` in `HASHES.txt` | pending |

## Notes for the implementer
- Load the sealed `run.py` files with the importlib loader, as `lb_formula_dial` does.
- **The sealed scorer reads LMIN as a module global.** Scoring at LMIN 5 means patching it. After the patch is in place, set it back to 4 and rerun K1, so that the patched path is shown to reproduce R1.
- Reproduce the label-free tables first and abort on any mismatch beyond the stated tolerances.
- Output JSON holds aggregates only.

## Review fixes applied
### v3 review (FIX)
1. One type rule for every list, with the sort and shuffle named. All type counts, kept sizes and thinned densities recomputed. K3 aborts on a density difference above 0.0005.
2. h, j, w and y are skipped as if absent.
3. K2's wrong key: shuffle within class until no sign keeps its value, up to 100,000 tries (1,000 left about 1 draw in 6 without a wrong key); a class with one distinct value keeps it.
4. B3 = step 11 added as a report-only rung on F0 and F1 at LMIN 5; it limits "no loss found". Density at 6 consonants added to the rung table. K2 covers 13 cells and 260 draws.
5. Arm B readings: the F1-control rule; the text-shape clause on the LMIN reading (both numbers verified); controls run first; paired discordant draws reported.
6. Arm A readings: the "not interpretable" rule sits above both arms; "language-specific" needs Fi, Id and Hu interpretable; the side-by-side clause added to "Uninterpretable".
7. Limits and wording: the three stated limits added (25.0%, 49.4% and the density at 6 verified); "his matcher" replaced; the LMIN-global note added.
8. Odyssey-only lexicon added as report-only cell Od, always run (16,145 types, density 0.1254 / 0.0082).

**Numbers that moved from v3 to v4:**

| lexicon | types, v3 → v4 | kept, v3 → v4 | thinned density at 4 / 5, v3 → v4 |
|---|---|---|---|
| G | 22,571 → 20,420 | 15,071 → 13,920 | 0.176 / 0.0172 → 0.1768 / 0.0180 |
| Fi | 20,713 → 20,653 | 18,213 → 17,653 | 0.178 / 0.0143 → 0.1756 / 0.0142 |
| Id | 14,558 → 14,025 | 12,558 → 12,025 | 0.177 / 0.0114 → 0.1770 / 0.0113 |
| Hu | 18,341 → 17,967 | 8,841 → 8,967 | 0.177 / 0.0175 → 0.1760 / 0.0185 |
| Es | 11,836 → 11,571 | all | 0.159 / 0.0137, unchanged |
| H | 30,747 raw forms; 28,144 under the type rule | all | unchanged |

Full-list densities and Homer overlaps did not move. No Arm B number moved; the density at 6 is new.

### v2 review (FIX on Arm A, REDESIGN on Arm B rungs)
1. Rungs re-anchored on density. Top rung B2 = step 9 (0.366 / 0.077, rule LMIN 5); intermediate B1 = step 3. g reported, not targeted.
2. Looseness concentrated on d and t; the rest exact; token share 74.5%.
3. Per-rung density and rule LMIN are in the prereg; a rung above LMIN 5 is not run.
4. Modern Greek added as the planted answer (KG), thinned to density.
5. Every lexicon thinned to the step nearest 0.177.
6. Non-independence from Homer stated in advance, with measured overlaps.
7. Spanish is report-only; "structure, not language" needs Kalevala or two non-Indo-European lexicons.
8. K2 relabelled a null-calibration check with a rule that does not void by chance; q rule frozen; W0 dropped as redundant with K2.
9. Skeleton rules run on M0 letters before expansion; ξ = κσ, ψ = πσ; tokenisers frozen.
10. The 13-15 band is kept and tied to the sealed fail level of 12; "Next" softened.

Added by the drafter in v3, not asked for: the B0 × LMIN 5 control cells, because every loosened rung has rule LMIN 5; and the note that modern Greek overlaps Homer no more than Kalevala does.
