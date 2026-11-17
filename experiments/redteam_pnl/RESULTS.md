# Red team: pair_numeral_long claims A (number-names), B (counted items), C (long texts)

2026-11-14. Independent reimplementation from `corpus/load.py`, `dev_heldout(version=2)`, distinct texts. I wrote `a_numbernames.py` before opening `experiments/pair_numeral_long/*.py`. I opened `f2_numerals.py` only afterwards, to find out why B differed. Claim C reuses the frozen functional grammar (`experiments/functional_reading/fr.py`) as the parser, because "parses" in the claim means parses under that grammar. I wrote the long-text selection, the nulls and the statistics myself.

Run from repo root: `.venv/bin/python experiments/redteam_pnl/{a_numbernames,c_long,c2_joined}.py`. Logs: `a.log`, `c.log`, `c2.log`. Machine-readable results: `results.json`, `a_results.json`, `c_results.json`, `c2_results.json`.

## Verdicts first

| claim | verdict | one line |
|---|---|---|
| A. fixed number-names | **survives, weakened** | Replicates exactly (29/40 vs 0.325) and on ICIT new sites (15/20, p=1.6e-4). But half of it is tall-2 + fish M59, and the "number + following head" framing is post hoc: numerals are just as fixed relative to the sign *before* them (34/40). |
| B. counted items M162/M169/M328 | **fails (confirmatory)** | A code bug set M328's "dev modal value" to 5, a value M328 never takes in dev. With the true mode the held-out result is 13/25, and Fisher vs lexemes gives p=0.079, which is above the registered alpha of 0.0125. |
| C. long texts = one stretched template | **fails** | The concatenation null loses by construction. A plain bigram chain trained on short texts, with no template, parses exactly as often as the real long texts (0.64 vs 0.67, p=0.49) and has no more resets. Joining lines drops acceptance from 0.67 to 0.38. |

## A. Fixed number-names

**Reimplementation.** Each record is a numeral sign directly before a non-numeral sign, inside a break-free run. The stroke values come from `stroke_signs.json`, with M99/M101 excluded. A head counts as lexeme-like if it has at least 8 dev tokens, a modal share of at least 0.6, and BH q < 0.05 against a permutation null drawn from the pooled numerals of the same system. This reproduces the same 12 lexeme heads and the same held-out result: **29/40 = 0.725**.

**Is 0.33 the right expectation?** Yes. The pooled held-out numeral distribution gives 0.325, and the dev pool gives 0.346. A within-system permutation gives p ≤ 2.5e-4, and the binomial gives p = 2.6e-7.

**Attacks:**
- **Segmentation.**
  - Treating M99/M101 as short-2 gives 51/64: many fish become "short 2 + fish" names.
  - Dropping the doubtful tall-3 forms (M88 dotted, M92 roofed, M93/M94 slanted) gives 29/40.
  - Dropping the bracketed short forms M111/M122 gives 29/40.
  - Summing contiguous numeral clusters gives 27/39.
  - None of these changes the conclusion.
- **One head drives it.** Tall-2 + M59 is 15/16 of the held-out hits.
  - Without M59: 14/24 = 0.58, p = 0.008. That is still above chance, but no longer different from the count-like heads (13/25, Fisher p = 0.44).
  - Three of the advertised names have **zero** held-out tokens: tall 3 + M211, short 7 + M197, short 3 + M403.
  - M287 fails its own test (2/10).
- **Families and mould copies.**
  - Collapsing held-out tokens into families that share a 3-gram leaves 18/23 families keeping the dev value (p = 9e-6), with a largest family of 8 tokens.
  - Restricting held-out to seals only gives 23/33.
  - Families and moulds do not explain it.
- **Preceding vs following was chosen post hoc.** Running the same pipeline with the numeral *after* the sign gives 34/40 kept vs 0.39 expected. The fixed pairs are M336 + tall 3, M403 + tall 2, M391 + short 1 and M99 + tall 2.
  - Tall 3 + M211 is really the title block M336-M89-M211: 39/41 dev tokens are preceded by M336 (shaunmortal F28).
  - So the evidence is for **fixed multi-sign formulas that contain a numeral**. It is not specifically for "numeral + the noun it qualifies".
  - For comparison, non-numeral heads keep their dev-modal predecessor 20/39 = 0.51 of the time. Numeral pairs are more fixed than ordinary collocations, but not uniquely so.
- **ICIT (independent transcription).** I identified numerals on the Wells side (bridge entries mapping to M numerals, W2 excluded) and bridged heads W→M.
  - New-site texts (412 distinct, outside the five big M77 sites): **15/20 vs 0.33, p = 1.6e-4**. Without M59 the figure is 11/13. This is the strongest support.
  - All ICIT texts: 260/308 = 0.84. These are mostly the same objects as M77, so this checks the transcription, not the sample.

**Verdict: survives, weakened.** Some numeral + sign combinations really are frozen. The defensible statement is: "certain numeral signs occur inside fixed multi-sign formulas (tall-2 + fish, the M336-M89-M211 block, M103-M403, M112-M194/M197)." The individual names other than M59 rest on 0-4 held-out tokens each.

## B. Counted items

**Bug in the original.** In `f2_numerals.py`, `ll_spike` clamps w to 1e-9 for values with zero count. For M328 (dev tall values {1:1, 2:4, 3:6, 4:3}), a "spike" on the unseen value 5 makes everything else uniform. That fit has a higher likelihood than a spike on 3, so `spike_value` = 5, and this is what the code then uses as the "dev modal value" in N2. As a result, M328 scores 0/5 instead of 3/5, and the B test is biased toward passing. The registered alpha is 0.0125.

| | original | reimplementation (true dev mode) |
|---|---|---|
| held-out count heads at dev mode | 10/25 | **13/25 = 0.52** (M162 3/8, M169 5/10, M328 3/5, M249 2/2) |
| Fisher one-sided vs lexeme 29/40 | p = 0.0096 (pass) | **p = 0.079 (fail)** |

Other checks:
- **Families.** 11/21 3-gram families are at the dev mode, so families do not drive the result either way.
- **M249 is not a counted item.** It scores 2/2 on held-out and 17/25 at value 2 in ICIT, which makes it lexeme-like.
- **ICIT new sites.** Only 1 count-head token, so untestable.
- **All ICIT texts.** Count heads 43/74 = 0.58 vs lexeme heads 0.84 (p = 2e-6). These are the same objects, though, and M249 inflates the count-head figure.
- **Best descriptive support: minimal pairs.** These are distinct M77 texts that are identical except for the numeral before the head. There are 5 such frames for M162 and 3 for M328, against 0 for every lexeme head except M15 and M287 (1 each). Substitutable values are what counting predicts. This was not pre-registered.

**Verdict: fails as a confirmatory result.** "M162/M328 take variable values" is plausible descriptively (dev spread, minimal pairs), but the registered held-out test does not pass once the bug is fixed. The set {M162, M169, M328} should not be carried forward as "counted items" without a new pre-registered test.

## C. Long texts

**Reimplementation.**
- Long means 10+ signs, or multi-line with 8+.
- Held-out: n = 21, 16 of them multi-line, none with breaks. Acceptance is 0.667, the same as claimed. Dev: n = 47, acceptance 0.532.
- Resets (closer-only sign followed by a non-closer in the same line): 0.24 per 10 signs.

**Is the concatenation null fair? No, it is guaranteed to lose.**
- In the frozen grammar, a closer (J) can only be followed by J or P.
- 45% of held-out short texts (58% of dev) end in a closer-only sign.
- So any concatenation of 2-3 short texts almost always puts a closer mid-line, and then fails to parse.
- The exact-fill concat null gives 0.31 (p = 0.007) and the truncated fill gives 0.19.
- L1 and L2 test the same fact twice: "long lines rarely contain a closer before the end".

**Stronger nulls (300 draws, per line, length-conditioned):**

| null (held-out lines) | acceptance | resets /10 | p (null ≥ real acceptance) |
|---|---|---|---|
| real long texts | 0.667 | 0.24 | |
| concat, exact fill | 0.31 | 0.69 | 0.007 |
| concat, truncated | 0.19 | 0.86 | 0.003 |
| **bigram trained on dev short texts** | **0.64** | **0.17** | **0.49** |
| bigram trained on all dev lines | 0.64 | 0.15 | 0.46 |
| sampled from the grammar itself | 1.00 | 0.00 | 1.00 |

Dev gives the same picture: real 0.53, bigram 0.54.
- A first-order Markov chain with no template, trained only on 1-6 sign texts, reproduces long-text acceptance and resets exactly. Real long texts sit at the bigram level, far below what template-generated texts look like.
- So "one stretched template" is not distinguished from "short-text local sign transitions strung together". All the data show is that long texts are not literal concatenations of whole short texts.

**Multi-line handling.**
- The grammar parses each line separately, so a closer at the end of line 1 followed by a new opener on line 2 counts as parsed.
- Joined into one run, held-out acceptance drops from 0.667 to **0.381**: 6 of 16 multi-line texts parse only line by line.
- Joined-run acceptance is above the concat null (0.16, p = 0.017) but *below* the bigram null (0.53).
- 16/21 held-out long texts are multi-line, so the per-line result mostly reflects how texts are laid out on the object.
- Only 4/5 single-line long held-out texts parse.

**Verdict: fails.** The claim needs (a) a null that is not killed by closer placement, and (b) handling of line breaks. Under either, it does not hold.

## Tests run

24 comparisons: A 11 (base, 4 segmentation variants, families, leave-one-out, after-direction, seals-only, ICIT ×2); B 5; C 8. No multiplicity correction is applied to the attacks themselves. The verdicts rest on effect sizes and on whether the registered thresholds still pass.

## Next experiments

1. A: re-register "numeral-containing fixed formulas" with the 3-sign window (prev, numeral, next). Score it on ICIT new sites and on future finds, excluding M59 as a separate test.
2. B: pre-register the minimal-pair test (numeral substitution in otherwise identical frames) on ICIT new sites. Fix `ll_spike` to restrict the spike to observed values.
3. C: any future "long-text syntax" claim must beat a length-conditioned bigram (or trigram) null trained on short texts, and must report joined-line and per-line results separately.
