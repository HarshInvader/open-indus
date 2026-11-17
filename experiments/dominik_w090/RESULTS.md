# Dominik 2026: "W090 follows W740 but never W520" (board task #19, M5, agent H4)

## Verdict: mixed (inconclusive, leaning not special). The contrast exists in reading order on the main corpus, but it does not replicate where we can test it independently, and contrasts this sharp are common in the Indus corpus.

1. **The pre-registered primary order fails.** The rule picked ICIT listing order: its denominators, 1,257 W740 and 160 W520 tokens with a next sign, are closest to the claim's 994 and 136. In that order W090 follows W520 1/160 and W740 3/1,257 (Fisher p = 0.93). So by the pre-registered rule, the claim does **not** replicate.
2. **In reading order the contrast is there (secondary analysis, chosen after seeing the primary).**
   - ICIT distinct sequences: W090 after W520 1/40 (2.5%) against W740 90/388 (23%), p = 0.0005. Without W220 families, 1/29 against 70/346, p = 0.015.
   - M77 dev: 0/21 against 57/204, p = 0.0015.
   - It is carried by Mohenjo-daro: 1/26 against 46/165, p = 0.004. Harappa alone gives 0/11 against 28/165, p = 0.14.
   - The claim's own numbers (69/994) match neither order. Their corpus or units differ, and the inputs are withheld.
3. **Independent data cannot test it.**
   - M77 held-out (family split v2): 0/8 against 10/62, p = 0.27. Even at the same rate a zero would occur with probability 0.24.
   - ICIT sites outside the five big ones: 0/1 against 7/27.
   - W520 rarely has a follower in reading order, because 80% of W520 tokens are text-final.
4. **Sharp zero cells are the norm here.** Take every triple (X frequent, Y with 100-200 followers, C following X at >= 5%).
   - In reading order, 24 of 57 such triples have a zero cell, and 25 reach Fisher p <= 0.001. The claimed contrast ranks 18th of 57.
   - Shuffling sign order within texts gives about 10 zero cells, so the corpus has more than chance (p = 0.005). That is a general fact about Indus sign order, not a fact about W520.
   - In listing order the count is 48 of 60.

## Signs
Bridge (`bridge_WM.json`): W090 = M1 ("man"), W740 = M342 (jar), W520 = M211 (arrow), W033 = M89, W220 = M59 (fish). W520 tokens adjacent to W033 are excluded, as in the claim.
- M342 followers in M77 reading order: M176 73, M1 67, M98 12.
- W740 followers in ICIT: W400 115, W090 90.

So "jar, then man-sign" is a real recurring pair.

## Numbers
`results.json` (pre-registered run) and `secondary_reading_order.json` (secondary). Units are distinct sequences in break-free runs: 3,504 distinct ICIT inscriptions. Seven contrast tests in the primary run (T1 x 4, T2 x 3) and five in the secondary.

| set | order | W520 then W090 | W740 then W090 | Fisher p (one-sided) |
|---|---|---|---|---|
| ICIT all | listing (primary) | 1/160 | 3/1257 | 0.93 |
| ICIT all | reading | 1/40 | 90/388 | 0.0005 |
| ICIT no W220 | reading | 1/29 | 70/346 | 0.015 |
| M77 dev | reading | 0/21 | 57/204 | 0.0015 |
| M77 held-out | reading | 0/8 | 10/62 | 0.27 |
| ICIT other sites | reading | 0/1 | 7/27 | 0.75 |
| ICIT Mohenjo-daro | reading | 1/26 | 46/165 | 0.004 |
| ICIT Harappa | reading | 0/11 | 28/165 | 0.14 |

## Caveats
- The order choice is the weak point.
  - The pre-registered denominator rule chose an order in which the claimed numerator (69) cannot be reproduced (3).
  - Reading order reproduces the size of the effect but not the denominators.
  - A reader could fairly say the rule was badly designed. That is why the reading-order result is reported in full, labelled secondary.
- ICIT has no family split, so `distinct()` sequences are the unit there. M77 uses the v2 family split.
- Not checked: Dominik's W033 conditioning beyond simple adjacency, and their 2,022-family reference (withheld).

## Hypotheses

| hypothesis | verdict |
|---|---|
| W090 never follows W520 but follows W740 (prereg primary order) | not replicated (p = 0.93) |
| Same, reading order, main corpus | present (p = 0.0005), mostly Mohenjo-daro |
| Same, independent held-out data | untestable (power 0.24 at n = 8) |
| The contrast is unusual among sign-pair contrasts | refuted: rank 18 of 57; 25 triples at p <= 0.001 |
