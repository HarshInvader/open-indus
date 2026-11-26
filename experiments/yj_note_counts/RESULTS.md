# Counts quoted to Yajnadevam (descriptive, not a test)

2026-11-26. Replaces the one-off "review-only count" used in the internal blog review. No hypothesis, no p-values.
Run from the repo root: `python3 -I experiments/yj_note_counts/count.py > experiments/yj_note_counts/run.log`.
Numbers: `counts.json` (with sha256 of every input). Definitions are in the script header.

## Results

- **Repeats in 7–8-sign texts.** M77: 327 texts, 80 with a repeated sign, 97 extra repeated tokens. ICIT: 54 over 331 rows; 40 over 269 distinct sequences. His post "A Farmer's market full of fallacies and errors" (2026-07-04) says "the set of Indus inscriptions of that length show 96 repetitions"; ours is 97 on M77.
- **Share of texts (2+ signs) with any repeated sign.** M77 8.2% (259/3,162); ICIT distinct 4.5% (134/2,993); ICIT raw rows 3.6% (161/4,498); ICIT distinct with numerals removed 3.2% (87/2,744). His "about 17%" is not reached on any of these. The old one-off count gave 87/2,719 for the last row (same share); the denominator differs by the numeral set used.
- **Site counts (ICIT rows / objects).** Lothal 208 / 182, Dholavira 238 / 230, Bhirrana 6 / 6.
- **Six and seven + fish** (independent recount of `experiments/language` A2 P1). All M77 distinct texts: six-stroke (M108/M109) followed by fish 12 of 28; seven-stroke (M110–M112) 1 of 60; identical for plain fish M59 and the fish family. Pooled numeral rate 12.9% (fish family). Matches `experiments/language/out/a2_parpola.json` ("all"). The dev / held-out split differs from that file (now 5/17 and 7/11 for the six, under split v2; the stored A2 run reads 8/21 and 4/7), so only the all-text counts are quoted.

## Inputs

`data/m77_texts.jsonl`, `data/icit_texts.jsonl`, `experiments/functional_reading/lexicon.csv`, `experiments/language/a2_predictions.json`, and `sources/shaunmortal_indus/data/bridge_WM.json` (not in git; restored 2026-11-26 from github.com/shaunmortal/indus main @ 23c4884, sha256 in `counts.json`).
