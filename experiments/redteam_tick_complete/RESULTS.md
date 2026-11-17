# Red team of #30: ticked fish close the text (README #3), complete single-line texts

Board #31. Independent reimplementation from `corpus/load.py` only (no `signlist_robustness/harness.py`).
`run.py` holds the planned attacks. `run2.py` holds two follow-ups written after seeing `run.py` output, so they are exploratory.

## Conclusion first

**#30 survives.** On complete single-line held-out texts, ticked fish (M60/66/68/71/73) are text-final in 9 of 16 tokens (0.56, 95% CI 0.30-0.80). Plain fish are final in 3 of 144 (0.02). Every attack leaves p below 0.05:

- a null that shuffles signs inside each text;
- a length-matched null;
- dropping doubtful readings;
- seals only, or texts of 3+ or 4+ signs;
- leave-one-out;
- collapsing formula repeats.

The effect also shows up, on few tokens, at sites excavated after 1977, which are absent from M77: 4 of 6 ticked-fish tokens are final (p = 0.02-0.04).

**Weak points that remain:**
- 13 of the 16 held-out tokens are from Mohenjo-daro.
- Harappa (n = 2) and the other M77 sites (n = 1) are too small to test.
- Multi-line texts hold 1 ticked token, which is not final.
- Dholavira alone has 1 token, which is not final.
- The claim is about the end of single-line texts. It is untested for where a multi-line text ends.

## Results (M77 held-out v2, complete single-line texts, ≥2 signs)

The p-value columns are one-sided.
- **Within-text shuffle:** shuffles sign order inside each text, keeping length and inventory.
- **Length-matched band:** draws, for each ticked token, a band-frequency sign token (dev frequency 10-80) from a held-out text of the same length.
- **Length-matched all:** the same draw, from any sign.

20,000 draws each.

| attack | texts | ticked final | plain final | within-text shuffle p | length-matched band p | length-matched all p |
|---|---|---|---|---|---|---|
| A0 reproduce #30 | 393 | 9/16 | 3/144 | 0.007 | 0.0004 | 0.009 |
| A1 drop texts with any doubtful reading | 367 | 9/16 | 3/135 | 0.008 | 0.0002 | 0.009 |
| A2 seals only | 295 | 9/15 | 2/114 | 0.003 | <0.0001 | 0.002 |
| A2 length ≥ 3 | 324 | 8/13 | 2/137 | 0.002 | 0.0001 | 0.002 |
| A2 length ≥ 4 | 241 | 7/12 | 2/110 | 0.003 | 0.0001 | 0.003 |
| A4 Mohenjo-daro | 271 | 8/13 | 1/102 | 0.005 | 0.0004 | 0.006 |
| A4 Harappa | 82 | 1/2 | 0/27 | 0.57 | 0.61 | 0.61 |
| A4 leave-one-ticked-text-out, worst p | | | | | 0.002 | |
| B2 one ticked text per final bigram (drops 2452 = 2171 `M87 M59 M71`) | 392 | 8/15 | 3/143 | 0.015 | 0.001 | 0.018 |
| dev (where #3 was found, not independent) | 1,217 | 22/32 | 9/539 | <0.0001 | <0.0001 | <0.0001 |
| A2 multi-line complete, whole-text final | 26 | 0/1 | 0/8 | 1 | 1 | 1 |

On completeness, the held-out count here is 393, not #30's 415. This version requires at least 2 signs. The harness drops runs shorter than 2 when it counts, so the counts are the same.

The `complete` flag in `corpus/build.py` catches breaks at a text's edge, which never appear as `#` in `seq` (e.g. text 1002). So a sign before an edge break cannot count as final.

## Out-of-corpus replication (ICIT, Wells sign codes)

| set | texts | ticked final | plain final | within-text shuffle p | length-matched band p |
|---|---|---|---|---|---|
| post-1977 sites only (Dholavira, Nausharo, Banawali, Rakhigarhi, Bhirrana, Gola Dhoro, Kanmer, Farmana, ...) | 129 | 4/6 | 5/31 | 0.039 | 0.019 |
| Dholavira only | 67 | 0/1 | 2/18 | 1 | 1 |

`run.py`'s first ICIT set ("site not in M77") wrongly included Allahdino, Amri, Surkotada, Ur and others. M77 files these under "Other sites" or "West Asian finds". That set gave 5/8 (p = 0.007-0.028). It is superseded by the strict list above.

The 6 ticked tokens:
- Banawali 37.1 `W072 W308 W002 W236` (final)
- Bhirrana 52.1 `W820 W002 W236` (final)
- Gola Dhoro 158.1 `W861 W893 W140 W236` (final)
- Nausharo 5382.1 `W003 W226` (final)
- Dholavira 4221.1 (not final)
- Nausharo 5361.1 (not final)

Two of the finals share the ending `W002 W236`.

## Hypotheses

| attack | verdict |
|---|---|
| Completeness flags let edge-broken texts in | refuted: edge breaks are flagged; dropping doubtful readings changes nothing |
| Short texts make "final" cheap (genre or length) | refuted: length-matched and within-text nulls, length ≥ 3 and ≥ 4, seals only all hold |
| The result depends on the frequency band chosen for the null | refuted: band, all-sign and within-text nulls all p < 0.02 |
| n = 16 is carried by one or two texts or a repeated formula | refuted: leave-one-out worst p = 0.002; collapsing formulae p ≤ 0.018 |
| The result is specific to M77 or to one editor | weakly refuted: post-1977 ICIT sites 4/6, p 0.02-0.04, on 6 tokens |
| Holds at every site | untested: Harappa, Dholavira and other sites have 1-2 tokens each |

## Not checked

- Whether ticked fish close the whole text in multi-line texts (n = 1).
- Ticked-fish reading errors shared by M77 and ICIT. The ticks are small, and both editors used the same photographs.
- `run2.py` was written after seeing `run.py` output.
