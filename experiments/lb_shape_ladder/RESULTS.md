# Shape ladder: dictionary fit can count against a key at Indus length, but never for it (prereg `lb_shape_ladder`, hashed 2026-11-23T18:27:33Z; code hash checked before the run)

**Verdict.** All three planted controls pass.
- **Refute (true key above shuffled keys)** works from **R1** upward: Indus-length chunks, no word division, every sign keyed, mean 2.51 consonants per segment. It works in 20 of 20 subsamples.
- **Certify (true key above keys fitted to noise)** passes at **no rung**. It comes closest with word division, at 14 of 20 against a bar of 16.

## Numbers (held-out Linear B, Homeric skeleton lexicon, IC with LMIN = 4; means over 20 subsamples)

| rung | shape | consonants per segment | true key IC | shuffled keys: mean / 99th pct | best noise-fitted key | refute (of 20) | certify (of 20) | true key on scrambled text: refute (of 20) |
|---|---|---|---|---|---|---|---|---|
| R0 | Indus chunks, 74% keyed | 1.77 | 0.088 | 0.063 / 0.087 | 0.114 | **13** (fail) | 0 | 0 |
| R1 | Indus chunks, 100% keyed | 2.51 | 0.204 | 0.152 / 0.182 | 0.254 | **20** | 0 | 0 |
| R2 | whole lines, undivided | 4.40 | 0.457 | 0.371 / 0.417 | 0.567 | **20** | 0 | 0 |
| R3 | whole lines, word-divided | 2.25 | 0.140 | 0.068 / 0.097 | 0.134 | **20** | 14 | 0 |

Kill test (R3, subsample 0): true 0.150, against a shuffled 99th percentile of 0.099 and a best fitted key of 0.146. It passed.

**Partial keys** (0/25/50/75% right, then the true key, mean of 40 draws each) rise strictly in every subsample at R1-R3. At R0 they rise in 18 of 20. At R1 the means are 0.124 / 0.136 / 0.153 / 0.176 / 0.204.

## What this sets for the scorecard (main line a)

1. **Refute is a working standard at Indus shape.**
   - The test: score a claimed key with IC against its own values shuffled within frequency-and-consonant-count bins.
   - It recognises a real script's real key at Indus text length, with no word division, if the key covers nearly every sign. The true key's margin over the shuffled 99th percentile is +0.02.
   - On scrambled text the true key never passes, so the test is not driven by letter frequencies.
   - Our earlier failure (`lb_certify`) came from the score, not the shape. CPW with a lexicon that accepts any 1-3 consonant run, and a null that let shape change, could not see the key. IC, which counts only 4+ consonant words, with a null that keeps shape fixed, can.
2. **Refute needs full coverage.**
   - At 74% coverage (R0) it fails: 13 of 20.
   - Keys that leave many signs unread fall below the standard and can be neither supported nor refuted by fit.
3. **Certify never works on undivided text.**
   - At R1 and R2, keys hill-climbed on meaningless text (unigram or Markov shuffles of the dev half) score about 25% higher than the true key on real held-out text.
   - So no amount of dictionary fit in a claimed Indus reading can count as evidence the key is right.
   - Only evidence from outside fit can do that: forward predictions, or ties to objects and pictures (the tripod tier).
4. **Consequence for atlas 1.1.**
   - The benched keys can now be tested in a sealed rerun with IC and the shape-preserving null, as a refute-only test.
   - A full-coverage claimed key that does not beat its own shuffles, where the true Linear B key does 20 of 20 times, is evidence against it. That holds only if the claimant's lexicon passes the same density rule for LMIN.
   - Until that rerun, atlas 1.1 stays "unsupported".

## Deviations and limits
- **Memory guard.** Free memory read 18% at the start of the full run, below the 20% guard. The job used 4 small Python workers and finished normally. The kill test started at 21%.
- **One script, one lexicon.** The lexicon is Homeric, not Mycenaean. A claimant's later, related language is the same kind of mismatch, but its density differs. LMIN must be recomputed for each lexicon by the frozen rule (smallest L with 25% or less density).
- **Margins are modest.** At R1 the true key's mean is 0.204 against a 99th percentile of 0.182. A claimant key with looser value rules (more free choices per sign) needs its own planted-power check before a failure counts.
- **Scope.** The certify result is for hill-climbing with 3,000 swaps. Stronger fitting would only widen the gap.
