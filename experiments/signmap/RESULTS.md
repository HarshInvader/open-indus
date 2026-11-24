# Sign mapping by two blind agents, and the stroked-jar test (prereg `docs/prereg/signmap_figfish_strokedjar.md`, sealed 2026-11-24 03:58:03Z; addendum 1 03:59:53Z)

## Mapping
- **Why it was needed.** Neither claimant gives Mahadevan numbers.
  - Mukhopadhyay 2019 shows the signs as inline glyph images, and her 2021 and 2023 papers give no numbers either.
  - Parpola 2010 could not be obtained here (harappa.com returned a Cloudflare block, which was not bypassed).
- **Method.** Two fresh agents, blind to each other, matched by shape only against one-line descriptions of all 417 Mahadevan signs. No corpus statistics were allowed. Files: `mapper_1.json`, `mapper_2.json`, `count_gate.py`, `result.json`.
- **Agreement on first choices: 8/9 items.**

| item | mapper 1 | mapper 2 | used |
|---|---|---|---|
| Mukhopadhyay stroked jar 1 (img1) | M343 (high) | M343 (high) | yes |
| stroked jar 2 (img2) | M344 (high) | M344 (high) | yes |
| stroked jar 3 (img3) | M345 (high) | M345 (high) | yes |
| img4-6 (byte-identical repeats of img1-3) | same | same | yes |
| img7-8 (4-stroke jar, identical; no Mahadevan match) | M345 (low) | M345 (low) | no (low confidence) |
| Parpola's fig (words only, no drawing) | M326 (low) | M325 (low) | **no: disagree** |

- **Image caveat.** Both agents noticed that img4-6 repeat img1-3 byte for byte, and img7 equals img8. The extracted inline images may not match the paper's intended series one to one. The three claimed signs (img1-3) are unaffected.

## Fig + fish (PAR-vata-min): untestable by mapping
There is no claimant drawing or number, and the two blind mappers disagree on the fig sign. No fig sign can be fixed, so the pair cannot be counted. Reopen with Parpola's own sign number (for example from his 1994 sign list).

## Stroked jars (MUK19-stroked-jar-MET): refuted
- **Count gate.** 263 distinct ICIT texts contain M343, M344 or M345, which passes the bar of 30.
- **Primary test.** ICIT pottery graffiti (384 texts). Object-class labels permuted within site, 10,000 draws.

| sign | observed | expected | ratio | p (enrichment) |
|---|---|---|---|---|
| **pooled M343/M344/M345** | **17** | **23.0** | **0.74** | 0.96 |
| M343 | 6 | 15.7 | 0.38 | 1.00 |
| M344 | 6 | 4.8 | 1.25 | 0.34 |
| M345 | 5 | 2.5 | 2.00 | 0.09 |

- **Verdict.** The ratio is 1 or less on pottery, which is the catalogue's own kill condition. Power to see a true 2× effect is 0.96. **Refuted.**
- **Caveats.**
  - M343 drives the pooled result, and its pottery count was already reported by `self_label` before this test was sealed. This is stated in the prereg.
  - Without M343 (exploratory): M344 + M345 together are 11 vs 7.3 (1.5×), short of the claimed 2×.
  - M345 alone reaches 2× on 5 texts, which is not significant. It is noted only as a lead for anyone with more pottery graffiti.
  - The same short-mark effect that makes the plain jar M342 rarer on jars (`self_label`: pottery marks lack the seal formula) may also depress M343.
