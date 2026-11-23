# Yajnadevam's key under the IC refute standard: untestable with this lexicon and corpus (prereg `yj_ic_refute`, hashed 2026-11-23T18:39:50Z; code hash checked before the run)

**Sealed verdict: "untestable with this lexicon".** The generous-matcher power gate failed on its partial-key condition. The red team (below) agrees with the label but for different reasons: the gate itself overstated power about fourfold. The key is **not refuted and not supported**. Atlas 1.1 stays "unsupported".

## Numbers

**Power gate (20 planted-Rigveda corpora per matcher):**

| matcher | LMIN | planted key beats shuffles | shuffled-stream false positives | partial keys 0 / 25 / 50 / 75 / 100% | gate |
|---|---|---|---|---|---|
| generous (primary) | 5 | 19/20 | 1/20 | 0.251 / 0.249 / 0.260 / 0.269 / 0.288 | **fail** (no strict rise) |
| strict | 5 | 20/20 | 1/20 | 0.200 / 0.201 / 0.204 / 0.216 / 0.234 | pass |

**His key, on 3,249 distinct ICIT texts and 11,752 key consonants (whole corpus):**

| key | matcher | IC | shuffled: mean / 99th pct | p | beats shuffles |
|---|---|---|---|---|---|
| upstream fc8813a (primary) | generous | 0.265 | 0.236 / 0.295 | 0.25 | no |
| upstream fc8813a | strict | 0.233 | 0.203 / 0.259 | 0.22 | no |
| older copy (field-cady) | generous | 0.264 | 0.239 / 0.293 | 0.27 | no |
| older copy | strict | 0.232 | 0.204 / 0.262 | 0.22 | no |

**Pass-meaning control.** Three keys hill-climbed on meaningless (unigram-shuffled) Indus text score IC 0.43, and all 3 beat their own shuffles (p = 0.001). That is why a pass would have meant nothing.

The kill test (planted corpus 0, generous) passed: 0.286 against a 99th percentile of 0.267.

## Red team (own check plus an independent code read, 2026-11-23)

1. **The planted gate overstates power (this decides the verdict).**
   - On the real corpus, his key's shuffled-value spread is about twice as wide as on planted corpora: sd 0.025 against 0.012 (generous), 0.024 against 0.009 (strict).
   - The real corpus is formulaic. Its top 50 sign bigrams make up 23.8% of bigrams, against 9.0% when planted (3,815 distinct bigrams against 5,946). Permuting one frequent sign therefore moves whole formulae.
   - At the real corpus's spread, the planted Sanskrit key would beat shuffles in only **5/20 (generous) and 2/20 (strict)**. So the stated power of 19-20/20 is really about 10-25%, and a non-pass by his key is weak evidence against it.
2. **The sealed gate failure itself is noise.**
   - The "0% right" partial key is still 11% right by chance, and keeping 25% of sign types barely moves IC at LMIN 5.
   - Across corpora the 0→25% step is −0.002 ± 0.013. A strict rise holds in only 27% (generous) or 62% (strict) of resamples.
   - The label is right, but this condition was a poor gate.
3. **Bug: the strict lexicon drops unreadable consonants instead of dropping words.**
   - Under strict, `build_lexicon` keeps only the 16 key letters, so 64.7% of Monier-Williams headwords lose consonants (e.g. Darma → rm). The planted stream loses 24% of its consonants the same way.
   - Generous has the same bug for G (gh) only, affecting 2.0% of headwords.
   - The same lexicon code is in `experiments/language/a1_key_null.py` `--strict`, so the old strict CPW result in atlas 1.1 is affected in the same way.
   - **Exploratory (unsealed) rerun with the bug fixed:** dropping words that contain an unreadable consonant gives strict LMIN 4 (density 0.22). His key scores 0.455 against a shuffled 99th percentile of 0.457-0.461, p ≈ 0.026 (3 seeds). Still not above the bar, but close. This is a lead for nothing: fitted keys pass easily.
4. **The planting skips about a third of the stream** (34-36%) while searching for a matching sign value. Only the final 0.5% miss rate was reported. This makes planted text less like running Sanskrit, which partly offsets point 1.
5. **Clean:** the corpus build matches the prereg; key case handling drops nothing; the verdict logic matches the prereg; seeds and caches are sound.

## What this means
- **No published Indus key can currently be refuted by dictionary fit with the tools we hold.**
  - Yajnadevam's is the only full-coverage key, and on the real, formulaic corpus the planted power is about 10-25%.
  - Pierson's key is below the coverage standard.
  - Fairservis and Rao tables are not held.
- **A rerun would need three changes**, sealed before any rerun:
  - a fixed strict lexicon;
  - a planting step that keeps the corpus's formulae (e.g. rewrite each distinct sign by a fixed planted value, so repeated formulae stay repeated), or a power claim stated at the real null's width;
  - a token-weighted partial ladder.

  Even then, the best result possible is "refuted at about X% power". It can never support the key.
- **For the scorecard:** the dictionary-fit row of every published Indus key reads "untestable by fit at stated power". Evidence must come from outside fit: forward predictions, or ties to objects and pictures.
