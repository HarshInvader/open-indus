# Formula dial: does formula reuse or key looseness remove refute power at Indus shape? (ready to seal; no code exists and no IC has been computed)

Status: **Sealed 2026-11-24** (v4). Drafted by Fable (brief 9, top pick); the coordinator approved starting it. Two fresh reviews returned FIX (10 items, then 6); all are applied (lists at the end). Main line (a), the claim bench.

## Why
- `yj_ic_refute` and `scott_ic_refute` both ended "untestable at stated power". Both blame formula reuse: on the real corpus, shuffling one frequent sign's value moves whole formulae, so the null is about twice as wide as on planted text.
- That cause was never tested with a key known to be right. Three explanations are open:
  - formula reuse in the text;
  - loose keys (more than one value per sign);
  - the plants themselves (Rigveda stream, 34-78% skipped) or the Sanskrit lexicon.
- This study turns the first two into dials on Linear B, where the true key is known and the refute standard was set (`lb_shape_ladder` R1: 20 of 20).
- **No Indus key is scored here. No outcome supports any key, and no outcome licenses a rerun of one** (see "What changes").

## What was seen before this draft
- **Sealed results:** `lb_certify`, `lb_shape_ladder` and its addendum 1, `yj_ic_refute`, `scott_ic_refute`. So the F0 one-value outcome (R1) is known.
- **Label-free counts.** Top-50 share = share of all adjacent sign pairs taken by the 50 commonest pairs. Excess = that share minus its mean under unigram shuffles of the same texts (signs shuffled across positions, text lengths kept).

  | source | corpus, at about 4,000 tokens | top-50 share | unigram baseline | excess |
  |---|---|---|---|---|
  | reviewer, sealed `build(k, "chunk")`, 20 draws, no IC | Linear B held-out chunks (F0) | 0.233-0.245 | | **0.129** (0.105-0.139) |
  | reviewer | M77 distinct texts (e_M) | about 0.274 | | **0.155** |
  | this draft, approximate, 20 draws | M77 distinct seal and sealing texts | 0.272 (0.261-0.286) | 0.118 | 0.154 |
  | this draft, approximate (all lines, own chunker; superseded) | Linear B chunks | 0.245 | 0.092 | superseded by 0.129 |

  - **The sealed-builder count decides.** Every one of the 20 F0 draws is 0.016-0.049 below e_M. So a gap exists, **gate G0 is expected not to apply**, and F1 will be a real tilt. This draft's earlier figure of 0.153 came from a different chunker on all lines and is withdrawn.
  - Sign inventories differ (this draft's draws: 301 types for M77, 166 for Linear B), which is why raw shares are not compared.
- **Earlier counts in brief 9** (whole lines, 13,100 tokens, raw share): random Linear B draws 0.207-0.223; lines weighted by exp(1 × f) 0.283-0.298; by exp(2 × f) 0.365-0.388. They show only that a tilt can move the share.
- **Scott's key, aggregates only (her prereg's parser, no values printed):** 345 keyed signs; 56 have more than one alternative (mean 1.18 per keyed sign); those 56 hold 16.7% of keyed tokens on distinct M77 texts. **24 of the 56 have alternatives of different consonant counts**, holding 5.7% of keyed tokens.
- **Yajnadevam's key, aggregates only** (`yj_ic_refute`'s own `load_key` and `corpus`, distinct ICIT texts, no IC):
  - 714 readable signs, 712 used; 3,249 texts and 12,811 keyed tokens.
  - **Every sign has exactly one value: mean 1.00 values per sign, and 0% of tokens on signs with more than one alternative.** Both key copies agree.
  - Consonants per value, by token share: none 12.5%, one 84.4%, two 1.9%, three or more 1.2%.
  - The "1.32 choices per sign" in atlas 1.1 counts free choices in his published readings (vowels, altered consonants). It is not a number of alternatives in the key.
  - In the bench his looseness sat in the matcher: the generous lexicon lets one key letter stand for 2-6 Sanskrit sounds. That applies equally to the shuffled keys, and this study has no dial for it.
- **Not seen:** any IC, null width or pass count under a tilt, under duplication, or under more than one value per sign.

## Prior art
- **Repo.** Controls already used at Indus shape: shuffled keys, scrambled text, keys fitted to noise, partial keys, coverage (74, 90, 95, 100%). A search of the four preregs and RESULTS files found no formula dial and no values-per-sign dial on a true key.
- **Opened 2026-11-24:**
  - Tamburini 2025, doi:10.3389/frai.2025.1581129. Benchmarks on Ugaritic, Linear B, Cypriot, Phoenician and Luvian word lists. No significance test against shuffled keys, no comparison of the true mapping with near-optimal wrong ones, no corpus-shape analysis.
  - Luo et al. 2020, arXiv 2010.11054 (abstract only). Decipherment of undersegmented scripts with a language-closeness measure. It ranks languages; it does not test a stated key.
  - Zenil and Uthamacumaran 2026, arXiv 2610.08861 (abstract only). Structural tests; no key-level test in the abstract.
- **Not opened today (unverified):** Raghavendra 2026 (SIGIL, arXiv 2608.02999), benched earlier in the repo; Berg-Kirkpatrick and Klein 2013, opened for atlas 1.11.
- The search was short. "Not found" is weak evidence that this is new.

## Data (all already held)
- Linear B syllabic words, the Homeric skeleton lexicon, sign readings and key rules: exactly as `lb_shape_ladder` R1.
  - Indus-length chunks, no word division, every sign keyed.
  - j and w removed; q matches p, t or k.
- Only the held-out half is scored, as at R1. The dev half is unused: there is no fitted-key null here.
- **Size.** The held-out half is about 4,000 tokens (n_k). The real runs scored 10,000-12,000. Null widths here are therefore not comparable with W_real in absolute terms. Only ratios between cells of this study are read.

## Statistic: token IC only
- **Token IC, as sealed.** The share of all held-out key consonants that lie inside a lexicon word of at least 4 consonants. LMIN = 4.
- **The type-IC arm of draft v1 is dropped (review fix 1).** Both real runs already scored distinct texts, so counting each distinct text once changes nothing for them. No replacement statistic is proposed here: one that targets reuse inside distinct texts would need its own design and kill test.

## Cells
12 corpus-and-key cells, 20 draws each (k = 1-20).

| dial | rungs |
|---|---|
| formula | F0, F1, F2, D1 |
| values per sign | 1.0, 1.18, 2.0 |

**Primary cells (named now):** F1 × 1.0, F0 × 1.18, F1 × 1.18. All other cells are reported and decide nothing, except where a reading below names them.

## How the formula rungs are built
For draw k, let H_k be the held-out chunks of `lb_shape_ladder` subsample k, and n_k their token count.
- **F0.** H_k, unchanged.
- **Formula measure.** Excess, as defined above. Pairs are counted only inside a chunk (Linear B) or inside a run between line breaks (M77; never across "|"). The baseline is the mean of 20 unigram shuffles that keep chunk or run lengths.
- **Targets (label-free, computed before any IC).**
  - e_M is **one global number**, not one per draw: the median excess over 20 random draws of distinct M77 seal and sealing texts, each cut to n̄ tokens, where n̄ is the median of n_k over k = 1-20. Expected about 0.155.
  - F1 target: e_M, tolerance 0.005.
  - F2 target: 1.5 × e_M, tolerance 0.005.
  - Why 1.5: the claim "refute holds up to x" needs one rung clearly above Indus. The value is arbitrary and fixed now. F2 decides no primary reading and is dropped if unreachable.
- **Gate G0 (label-free, before any IC).** If the median excess of F0 over the 20 draws is within 0.005 of e_M, or above it, then F1 is not built: F1 is set equal to F0 and reading "already at Indus excess" applies. Expected not to apply (median 0.129 against 0.155). Under G0, r = 1 and F1 × 1.0 is K1's pass, so the readings "Formula reuse explains" and "Both needed" would be impossible.
- **F1 and F2 (length-stratified tilt).**
  - **Pool: every line of the corpus that is not in subsample k's dev half** (about 27,300 tokens), cut into Indus-length chunks by the R1 chunker with a fixed re-chunk seed (see Seeds). The narrower choice, only lines that hold a chunk of H_k, carries about 7,700 tokens: too little to draw about 4,000 by weight within length strata, least of all at F2. No dev text enters, and nothing here is fitted, so the wider pool leaks nothing.
  - Each chunk gets weight exp(τ × f), where f is the share of its adjacent pairs among the pool's 50 commonest.
  - Chunks are drawn without replacement by weight **within each chunk-length stratum**, taking exactly as many chunks of each length as H_k has. So the length distribution and n_k equal F0's exactly.
  - If a stratum of the pool is too small, the draw fails and counts against the feasibility gate.
  - **τ search (frozen).** Each pool chunk gets one fixed uniform number u per draw; chunks are ranked within a stratum by −log(u) / weight, so the same u serve every τ.
    - Bounds: τ in [0, 8]. Start at the midpoint and bisect, raising τ when the excess is below target.
    - Stop at the first τ whose excess is within 0.005 of the target.
    - Cap: 30 iterations. A draw that has not stopped by then, or whose excess at τ = 8 is still below target, fails and counts against the feasibility gate.
    - The search sees only the excess.
- **D1 (pure duplication; a mechanism check, not an Indus analogue).**
  - The real runs used distinct texts, so whole-text copies are not how Indus reuse entered them. D1 exists only because a tilt changes content as well as reuse, and D1 changes reuse alone.
  - Start from F0. Mark 5% of its distinct chunks at random as formula chunks, and add whole copies of them in round-robin order until the excess reaches the F2 target.
  - Why 5%: at about 1,100 chunks this gives about 55 formula chunks, the same order as the 50 pairs the measure counts. Fixed now; no other share is tried.
  - Nothing is removed. The token count grows, and the growth is reported.
  - **N1 frequency bins for D1 are frozen at F0's.** D1 changes token frequencies, which would otherwise move the bins. So D1 is scored with exactly the same 1,000 shuffled keys as F0; the code checks this by hashing the keys.
- **Feasibility gate (label-free).** A rung is dropped, and reported as unreachable, if more than 2 of 20 draws miss the tolerance or fail a stratum, or if D1 needs more than twice n_k tokens. If F1 is dropped (and G0 did not apply), the study stops.
- **Reported per rung:** achieved excess and raw share, τ, distinct chunks, token count, chunk-length distribution, mean consonants per segment.

## How the values-per-sign rungs are built
- **1.0 (also Yajnadevam's shape on this dial).** The true key. His key has one value per sign, so the 1.0 cells are the ones that bear on it.
- **1.18 (Scott's shape).** Derived from her key's count: 56 of 345 signs loose, holding 16.7% of tokens. Each loose sign gains one extra alternative. Selection, frozen:
  - Eligible signs are visited in one random order. A sign is added unless that would take the loose set's share of held-out F0 tokens above 18%; such a sign is skipped.
  - Stop once the share is at or above 16%, or the signs run out. The achieved share and the mean values per sign are reported per draw.
  - A draw that ends below 16% counts as a failed draw for the 1.18 cells; more than 2 of 20 drops the rung.
- **The 1.3 rung of draft v2 is removed.** It rested on a guess (30% of tokens) and on reading "1.32 choices per sign" as alternatives in the key. The count above shows his key has none, so no rung between 1.18 and 2.0 has a derivation.
- **2.0 (stress rung).** Every sign gains one extra alternative.
- An extra alternative is the true value of another sign from the same consonant-count class, and must differ from the sign's own value. So every alternative of a sign has the same consonant count, and segment shape never changes.
- **A sign with no such donor** (alone in its class, or all others share its value) is not eligible and keeps one value, also at 2.0. The number of such signs is reported.
- **One loose key per draw and rung.** It is built once on F0 and reused unchanged on F1, F2 and D1 of that draw.
- **Scoring, as in Scott's scorer.** Covered consonants are maximised jointly over the segmentation and over each token's alternative, across the whole segment. Ties take the reading with fewer consonants. IC = total covered / total consonants of the chosen readings.
- **Scope of claims.** Results are stated only for the rungs tested, and only for equal-length alternatives. 24 of Scott's 56 loose signs have alternatives of different consonant counts, which this dial does not model. So a pass at 1.18 here is an upper bound on what her rules allow.

## Null and width
- **N1, as sealed.** Value sets are permuted across signs within token-frequency bins of 10, inside each consonant-count class. Whole alternative sets move together. 1,000 draws per cell and draw.
  - **Bin frequencies follow the sealed R1 convention: dev plus held-out tokens of subsample k.** For F0 this is R1's own binning, which K1's 1e-9 match requires. For F1 and F2 the frequencies are the dev half plus the tilted draw. For D1 the bins are frozen at F0's.
- **Width.** W = N1 99th percentile minus N1 mean, per draw. A cell reports the median W over its 20 draws.
- **Signal.** True-key IC minus the N1 mean. **Margin.** True-key IC minus the N1 99th percentile.
- **Refute pass (per draw).** Margin > 0.
- **Scrambled-text control (every cell).** On a unigram shuffle of the same chunks, the true key passes against its own N1 in at most 1 of 20 draws.

## Kill tests, run first and in this order
- **K1. Reproduce R1.** F0 × 1.0, all 20 draws.
  - Passes ≥ 16 of 20, with the scrambled-text control ≤ 1 of 20.
  - Each draw's true IC, N1 mean and N1 99th percentile equal the sealed `lb_shape_ladder` R1 values to 1e-9. If a quantity is not stored in the sealed output, the unchanged sealed code regenerates it first.
  - Failure: **STOP.** No other cell is run.
- **K2. D1 guard.** D1 × 1.0: median W on D1 must be ≥ 1.25 × median W at F0.
  - Failure: D1 shows nothing. It is reported and removed from every reading. The study goes on.
  - (Draft v1's K2 and K3 concerned type IC and are removed with it.)

## Readings (frozen; more than one may hold)
Let P(cell) be the passes out of 20, and r = median W(F1) / median W(F0) at 1.0.
- **"Already at Indus excess."** G0 applied. Then R1's 20 of 20 already stands at Indus formula excess, as this measure sees it. Formula reuse measured this way does not explain the real runs' wide nulls. F2 and D1 are still read as stress rungs.
- **"Formula reuse explains."** P(F1 × 1.0) < 16 and r ≥ 1.5.
  - Supporting, not required: D1 passed its guard and P(D1 × 1.0) < 16.
- **"Tilt lowers power, but not through null width."** P(F1 × 1.0) < 16 and r < 1.5. The loss is in the signal, which a tilt can cause by changing content. Formula reuse is not shown to be the cause. The signal at F1 and F0 is reported.
- **"Formula widens the null but power holds."** r ≥ 1.5 and P(F1 × 1.0) ≥ 16.
- **"Looseness explains" (Scott's shape only).** P(F0 × 1.18) < 16. It cannot apply to Yajnadevam's key, which has one value per sign.
- **"Both needed."** F1 × 1.0 and F0 × 1.18 each pass, and F1 × 1.18 fails.
- **"Neither."** All three primary cells pass. Then the Yajnadevam and Scott power losses come from their plants, their lexicon, or rule features not modelled here. Next study: `lb_wrong_lexicon` (brief 9, study 2).
- **"F2 dropped."** F2 was unreachable. The limit is stated only up to F1: "no claim above Indus formula excess".
- **Stress rungs.** F2 and 2.0 results, where reached, are stated as limits and decide nothing.
- **Any cell whose scrambled-text control exceeds 1 of 20** is reported as "pass not interpretable" and counts as a fail in every reading.

## What changes
- **Method.** One line for atlas 1.1 and the scorecard notes: the tested limits of the refute standard, and which cause the dials support.
- **Reruns of Yajnadevam and Scott: none licensed by this study.**
  - Draft v1's rerun rule rested on type IC, which is dropped.
  - Rule frozen now: no outcome of this study permits scoring either key again. A rerun would need a new statistic with its own sealed design and kill test, and at most one sealed rerun per key would follow from that.
- **If F1 × 1.0 or F1 × 1.18 fails:** atlas 1.1 records that the true Linear B key loses refute power at that rung and Indus formula excess, at about 4,000 tokens. It is worded as a tested limit of the standard, not as a verdict on either key.
- **Scorecard.** No tier changes. `KEY-scott` still goes through addendum 6.

## Limits stated in advance
- K1's outcome is known, so it is a calibration check, not a blind test.
- A tilt changes content as well as reuse. D1 changes reuse alone but by whole-text copies, which the real runs did not contain.
- Excess over a unigram shuffle is one measure of formula reuse. Indus formulae may differ in kind (long frozen sequences) from tilted Linear B.
- Scored size is about 4,000 tokens, against 10,000-12,000 in the real runs.
- Alternatives always share a consonant count here; 24 of Scott's 56 loose signs do not.
- One script, one lexicon (Homeric, not Mycenaean), one statistic.
- Yajnadevam's matcher looseness (one key letter for several sounds) is not dialled. A pass at 1.0 says nothing about it.
- Three primary cells are read with fixed bars and no multiplicity correction. The readings are descriptive.

## Seeds
- Subsamples k = 1-20 use the sealed `lb_shape_ladder` seed scheme unchanged, so F0 equals R1's held-out sets.
- Re-chunking of the tilt pool: 20261126 + 1000 × k, one chunking per k, shared by F1 and F2.
- Tilted draws and D1 formula chunks: 20261127 + 1000 × k + formula-rung index (F1 = 1, F2 = 2, D1 = 3).
- Loose keys: 20261128 + 1000 × k + looseness-rung index.
- N1 permutation seeds are shared across the four formula rungs within each draw and looseness rung.
- M77 target draws and all unigram baselines: 20261129 (M77), 20261129 + k (Linear B draws).

## Cost
- 240 jobs (12 cells × 20 draws), each with 1,000 N1 keys on real and scrambled text.
- At the timing sealed for `lb_shape_ladder` (about 0.004 s per scoring), roughly 1 hour on 4 workers at 1.0. **Estimate only for the looser rungs:** the lattice scorer is expected to cost 2-4 times as much at 2.0, so the whole run is put at 2-3 hours. Nothing was timed, because no scorer exists yet. The implementer times one F0 × 2.0 job on a shuffled key, with no score printed, and reports it; the timing changes no rule.
- Runs under the Indus compute lock, with `nice -n 20`, 4 workers and the memory guard.
- Code: `experiments/lb_formula_dial/run.py`, hashed in `HASHES.txt` before any run. Targets, G0 and the feasibility gate run first, then the kill tests, then the other cells.
- Changes after sealing go in `lb_formula_dial_add1.md`, hashed before the affected step.

## Before sealing
| item | state |
|---|---|
| Scott's loose-sign and mixed-length counts | done (56 of 345; 16.7% of tokens; 24 mixed-length, 5.7%) |
| Yajnadevam's values per sign and loose-token share | done (1.00; 0%); the 1.3 rung removed |
| Top-50 excess for M77 and Linear B with the sealed builder, no IC | done by the reviewer (e_M 0.155; F0 0.129, range 0.105-0.139); G0 expected not to apply |
| Tilt pool, N1 bin convention, τ search, 1.18 rule, e_M definition | done (frozen above) |
| Timing of one 2.0-rung job | left to the implementer as a stated estimate; no rule depends on it |
| Fresh reviews (v1: 10 fixes; v3: 6 fixes) | done, all applied |
| Hash of this file and of `run.py` in `HASHES.txt` | pending |

## Notes for the implementer
- Load the two sealed `run.py` files (`experiments/lb_certify`, `experiments/lb_shape_ladder`) with the importlib loader used in `experiments/lb_shape_ladder/coverage.py`. A plain import clashes on the module name.
- At 2.0 values per sign, enumerate nothing: use a lattice dynamic programme over positions and alternatives for the joint maximisation.
- Output JSON holds aggregates only.

## Review fixes applied (fresh review, FIX, 10 items)
1. Type IC dropped, with the rerun rule that depended on it. Stated above.
2. D1's N1 bins frozen at F0; the keys are identical and checked by hash. The 1e-9 equality on type-IC W went with type IC.
3. D1 guard added (K2: W ≥ 1.25 × F0).
4. Target is M77 distinct texts at n_k, tolerance 0.005. The all-sides figure is no longer used.
5. The matched quantity is excess over a unigram shuffle, not raw share.
6. Tilt stratified by chunk length, n_k fixed, re-chunk seed fixed.
7. 1.18 rung added; loose signs picked by token share; claims limited to tested rungs.
8. Joint maximisation with ties to fewer consonants; one loose key per draw reused across formula rungs; Scott's mixed-length signs counted (24 of 56).
9. Readings added for "F1 × 1.0 fails with r < 1.5" and "F2 dropped".
10. K1 also requires N1 mean and 99th percentile to match to 1e-9.

**v3 (coordinator, before sealing):** the 1.3 rung's 30% guess was replaced by a count of Yajnadevam's key. The count gives 1.00 values per sign, so the rung was removed and the 1.0 cells named as his shape.

**v4 (second fresh review, FIX, 6 items):**
1. F0 excess replaced by the sealed-builder 0.129; G0 stated as not expected; the two readings impossible under G0 named.
2. Tilt pool defined as all non-dev lines (about 27,300 tokens), with the reason.
3. N1 bins use dev plus held-out frequencies, as sealed R1 does.
4. τ search frozen: bounds, cap and stop rule.
5. 1.18 rule frozen: overshoot, undershoot and signs without a donor.
6. e_M is one global median; pairs counted within runs.

Also applied: the 4,000-token size statement; the D1 5% share and the F2 multiplier frozen with reasons; implementer notes. Added by the drafter, not asked for: gate G0, because this draft's own count puts F0 already at M77's excess.
