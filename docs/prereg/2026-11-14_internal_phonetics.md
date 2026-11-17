# Pre-registration: internal phonetics (spelling-variation mechanisms)

Agent: internal-phonetics specialist. Written 2026-11-14, after dev analyses and planted controls, BEFORE any held-out text was loaded into a test.
Code: `experiments/internal_phonetics/` (`run_heldout.py` implements exactly the tests below).
Held-out = `dev_heldout(version=2)`: 564 distinct clean texts (no `#`, `|` removed).

Disclosure: the T1 transparency threshold (0.40) and the T2 smoothed p-value were fixed after the realistic planted controls had run AND after a first look at Indus dev output. The threshold equals the Indus dev 90th percentile of transparency among adjacent sign pairs (computed in the dev script before the rule was adopted). On dev it excludes M387 (0.395), which is a candidate, so it does not favour a positive result.

## Planted-control operating characteristics (synthetic logo-syllabic corpora, 1,675 distinct texts, 10 seeds per cell)

| test | realistic strength: power | strong: power | false-positive rate (mechanism absent) |
|---|---|---|---|
| T1 rule (>=3 signs pass) | 4/10 | 9/10 | 0/10 and 0/10 |
| T2 planted pairs at q<0.05 | 8/80 | 23/80 | 0 planted-type hits; 0.6-0.7 slot-paradigm pairs per corpus |
| T3 planted triples at q<0.05 | 3/50 | 16/50 | 2.9 and 5.0 spurious triples per corpus |
| T4 pooled silent p<0.05 | 2/10 | 7/10 | 0/10 and 1/10 |

## Confirmatory hypotheses

### H1 Phonetic complements
- Dev result: 25 signs host-specific (q<0.05) in the local-insertion test, but only one passes transparency >= 0.40: M242 after M342/M162/M211. M242 is a text-final post-closer (like M176), so it is slot-optional, not a complement. Dev count = 1 < 3: **dev verdict negative**.
- Held-out test: run the identical pipeline (local wide insertions, both orientations, 20,000 within-slot permutations, BH over all sign×orientation tests, exclusions M176, M1, fish M59-M75 at position 1).
- **Threshold for "complements supported"**: >=3 signs with q<0.05 AND transparency >= 0.40 in held-out, at least one of which also passed on dev with the same host. Otherwise refuted at this corpus size (with the caveat of 40% power at realistic strength).

### H2 Frame-independent alternation (homophone / allograph classes)
- Dev result: 2 pairs significant (q<0.05, Poisson tail on the slot-stratified curveball null): M65|M72 (drawing similarity 0.77, above the 0.58 threshold: allograph-type, fish paradigm) and M99|M402 (0.07: dissimilar).
- Held-out test: `t2_transitivity(heldout, kmin=1, nnull=1000)`; for each of the two pairs, k_ho = number of distinct local contexts in which both fill a held-out frame, with p from the same null.
- **Threshold**: a pair replicates if k_ho >= 1 and p < 0.025 (Bonferroni over 2). Even if M99|M402 replicates, it is NOT called a homophone: the control shows the test flags slot-paradigm alternants at a comparable rate to real homophones. A homophone claim would need an independent phonetic argument.
- Test cases (descriptive, no threshold): fish M59/65/67/70/72 and openers M267/M391/M293 pairwise k_ho.

### H3 Ligatures
- Dev result: 1 triple at q<0.05 (M12 <-> M342 M176, 2 independent families), fewer than the 6.7 average produced by Indus-fitted bigram corpora. M12 is not drawn as jar + comb. Candidates M343/M344/M345 <-> M342 + strokes: 0 events; M348 <-> M347/M342 + M176: 0; M190 <-> M162 + M186: 0; M103 M403 replaced by 10 different single signs, each once.
- **Threshold**: M12 <-> M342 M176 replicates if >=1 held-out event with within-held-out hypergeometric p < 0.05. Compositional ligature hypotheses for M343-M345, M348, M190 are refuted if held-out shows 0 corresponding events (prediction: 0).

### H4 Silent determinatives
- Dev result: no modifier class shows more base<->modified swaps within near-copy pairs than expected (fish ticks 2 vs 1.5; other enclosures 1 vs 0.3; roof 3 vs 2.4; inner strokes 0 vs 0.03; fish marks 9 vs 6.5; ears 0 vs 0). "Never dropped" is not testable: expected counts are <0.1 for most classes.
- **Threshold**: a class is a silent class-marker if held-out pooled p_more < 0.05 (Poisson, obs vs slot-matched expectation) AND dev p_more < 0.05. Dev already fails, so no class can be confirmed; held-out is descriptive. "Lexical (never dropped)" requires obs=0 with p_never < 0.05 in held-out.

## Multiple testing
Confirmatory family: H1 (1 decision), H2 (2 pairs), H3 (1 triple + 5 zero predictions), H4 (6 classes, descriptive). Total exploratory dev tests: T1 143 sign×orientation tests (local + edit-1), T2 69 pairs, T3 76 triples, T4 39 pairs/6 classes.
