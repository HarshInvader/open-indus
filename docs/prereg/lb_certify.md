# Known-script certification: does fit to a lexicon rank Linear B's true key above noise-fitted keys at Indus shape? (sealed 2026-11-23, before any number)

Agent `paper`. Main line (a), the claim bench. This is Fable's top study on 2026-11-23; see RESEARCH_STATE, "Main-line plan".

## Why
Atlas 1.1 refutes published Indus keys using a bench. That bench "detects Linear B at z 11.5", but only against shuffled keys. On planted Sanskrit and Tamil corpora, true keys lost to noise-fitted keys (`experiments/language`, `experiments/bench_pierson`). No one has scored a real script's real key against noise-fitted keys at Indus shape.

So the scorecard does not yet know what textual fit can show. The possibilities are:
- "refute" (the true key beats shuffles);
- "certify" (the true key beats keys fitted to noise);
- neither.

## Data (all already held)
- **Linear B words:** `sources/paragorth_Indus-/data/codelib/linear_b.jsonl` (DAMOS-derived lines).
  - Kept: syllabic word tokens, meaning lowercase syllables joined by "-".
  - Dropped: logograms, numerals and "*NN" signs.
- **Text building:**
  - Each line becomes one text: its words' syllables concatenated with word division removed, as in Indus.
  - Each text is cut into chunks whose lengths are drawn from the length distribution of M77 seal texts (length 2 or more).
  - A sign is a syllable string. Its identity is opaque to every key.
- **Subsample:** 2,300 chunks. Dev and held-out are split 50/50 by source line, so chunks of one line never straddle the split.
- **Lexicon:** every word form in Homer, `experiments/cognate_decipher/ext/greek/homer_00{1,2}.xml`, reduced to a Linear B-spelling consonant skeleton.
  - Diacritics are stripped.
  - Letter mapping: β π φ→p; γ κ χ→k; θ τ→t; δ→d; λ ρ→r; ζ→z; ξ→k s; ψ→p s; μ→m; ν→n; σ ς→s.
  - A word-final s, n or r is dropped.
  - An s, n, r or m directly before another consonant is dropped.
  - Doubled consonants are written once.
  - At most 7 consonants per skeleton.

## Keys
- **True key:** each syllable sign maps to its consonants. The glides j and w are removed from every key value, because they have no Homeric reflex; this applies equally to all keys. q may match Greek p, t or k. All other letters must match exactly.
- **Coverage:**
  - The true key is masked to 74% token coverage (primary) and 57% (secondary): signs are added in random order until the coverage is reached.
  - Masked signs count as breaks.

## Score
- From `experiments/language/a1_key_null.py`, unchanged in logic:
  - **CPW** = key consonants per lexicon word, using the segmentation with the fewest words;
  - **LONG** = the share of texts that can be covered with words of 2 or more consonants.
- Primary statistic: CPW on held-out.

## Nulls
- **N1:** the true key's values permuted within frequency bins of 10 signs, 1,000 draws.
- **N2:** hill-climbed keys, from a random permutation of the true key's values: 3,000 swaps per restart, 3 restarts. Each is fitted on one of:
  - (a) real dev;
  - (b) a unigram-shuffled dev;
  - (c) a bigram-Markov dev.

  Each fitted key is then scored on the real held-out set.

## Planted controls (must pass, or the run is void)
- **Monotonic:** keys with 25%, 50% and 75% of the true values (the rest permuted) must score in increasing CPW on held-out.
- **Permuted true key:** passes "refute" at most 5% of the time. This is the N1 tail by construction and is reported.

## Thresholds
- **Refute-admissible:** true CPW on held-out above the 99th percentile of N1.
- **Certify-admissible:** true CPW on held-out above the 95th percentile of all N2 held-out scores, (a) to (c) pooled.

## Kill test first (one subsample, 74% coverage)
- If the true key is neither refute-admissible nor certify-admissible here: STOP.
  - The verdict is "textual fit cannot even refute at Indus shape".
  - Atlas 1.1 is downgraded from "refuted" to "unsupported".
- Otherwise run 20 subsamples at each coverage. A criterion "holds" if it is met in at least 80% (16/20) of subsamples at that coverage.

## Verdicts
- **Only refute holds:** publish the rule "textual fit can reject a key but is inadmissible as proof".
- **Certify holds:** add certification as a scorecard tier, and re-run the benched Indus keys against it.

## Deviations from Fable's sketch (decided before running)
- The bench_pierson Tamil-specific scores S1-S3 are not used: they need a language model, and none exists for Mycenaean. CPW and LONG are language-neutral.
- The Latin-fitted-key control is replaced by the monotonic control.
- 20 subsamples instead of 50, for compute.
- Linear Elamite is not run.

## Seeds and code
- Seed 20261125.
- Code: `experiments/lb_certify/run.py`, hashed before it runs.
