# Known-script certification: the dictionary-fit score cannot recognise Linear B's true key at Indus size (prereg `lb_certify`, hashed 2026-11-23T18:19:03Z; code 18:20:06Z)

**Verdict: STOP at the kill test. The instrument fails on a script whose answer is known.**

We wrote Linear B with opaque signs, at Indus text lengths, with no word division. We kept 74% of the true key. Scored against Homeric Greek, the true key is **not** above keys whose values are shuffled. Keys fitted to pure noise score higher, but mostly by changing segment shape (see the diagnostic below), not by fitting better. The partial-key control is not monotonic either, though with one draw per level it had little power.

Dictionary fit (CPW), with a lexicon this generous and segments this short, therefore cannot refute or certify a key: it does not separate a known right answer from wrong ones.

| key, scored on held-out Linear B (1,130 chunks) | CPW (consonants per dictionary word) |
|---|---|
| true key (74% token coverage) | **2.258** |
| true values shuffled within frequency bins: mean / 99th percentile (1,000) | 2.230 / 2.301 |
| keys hill-climbed on a unigram-shuffled corpus (3) | 2.37-2.43 |
| keys hill-climbed on a bigram-Markov corpus (3) | 2.45-2.47 |
| keys hill-climbed on real dev text (3) | 2.49-2.53 |
| partial true keys, 25% / 50% / 75% right | 2.194 / 2.206 / 2.177 (not monotonic) |

## What this means for the claim bench (main line a)
- **A wrong key can outscore the right one on CPW.** A key fitted to meaningless text scores higher on a real script's held-out texts than the script's true key. Most of that gap comes from the hill-climb moving empty values onto rare signs and so lengthening consonant runs, not from better dictionary matches. It still shows CPW is gameable, as on planted corpora (`experiments/language`, `experiments/bench_pierson`).
- **Fit to this dictionary, at this shape, is not evidence for or against a key.** That holds for CPW with a saturated lexicon at about 2.5 consonants per scored segment, with no word division. Where fit starts to work is the next study (`lb_shape_ladder`). This holds both ways:
  - A claimed Indus key that reads many dictionary words proves nothing, because noise-fitted keys read more.
  - A claimed key that fails this score is not refuted by that failure alone, because the true Linear B key also fails.
- **Atlas 1.1 must be reworded.** Its "refuted" verdicts on Yajnadevam and the others rest partly on this score. They become **unsupported: no evidence for the key**, not "shown wrong". Atlas 1.1's "Linear B z 11.5" came from a different set-up (shuffle null, word division kept). It does not transfer to Indus shape.
- **The scorecard needs evidence that does not come from fit.** Two kinds qualify:
  - forward predictions on new finds;
  - covariation with non-textual features: objects, iconography, numbers.

  This supports Fable's "tripod" tier and main line (b).

## Limits
- One subsample, one coverage, one score family (CPW/LONG). The prereg stops here by design.
- The lexicon is Homeric, not Mycenaean. Spelling rules are approximated, and the glides j/w are dropped.
- A Mycenaean lexicon would help the true key, but it is not what an Indus claimant has: they use a later, related language, as here.
- LONG is near ceiling (0.977 for the true key), so it is uninformative.
- A different score could do better, for example one that needs word division or uses a language model. None is available for any Indus claim language at Indus shape. This is the open question for the next study.

## Diagnostic (Fable review, 2026-11-23, in memory, not sealed)
- **The lexicon is saturated.** Without q it contains 9/9 single consonants, 80/81 pairs and 492/729 triples, so any run of 1-2 consonants is always a word. It thins only at 4 consonants (18%).
- **Scored segments are short.** 39% of keyed tokens carry no consonant (vowel signs, j/w) and 26% are breaks. The mean scored segment is 2.47 consonants, and only 476 of 1,130 held-out chunks are scored. This is harsher than a typical Indus claim, which gives about one consonant per sign.
- **CPW has little range.** For the true key's shape the ceiling is 2.469, and uniform random consonants score about 2.09. Noise-fitted keys reach 2.53, above that ceiling, which is possible only by changing shape.
- **Monotonic control, 40 draws per level:** 2.213 / 2.206 / 2.238 / 2.246, then the true key at 2.258. That is a weak rise drowned by per-draw noise (sd 0.04-0.07).

So the safe reading is: this instrument, at this shape, fails. The atlas downgrade stands, since it moves in the cautious direction. The follow-up `lb_shape_ladder` sets the shape at which a fit score begins to discriminate.
