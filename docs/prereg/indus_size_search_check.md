# Indus-size search check (small Step 1)

Sealed 2026-11-20 (UTC) by agent `paper`, before any cell of this check has run. The code is `experiments/mismatch_study/step1.py`, which uses the sealed `mm.py` (1e7181f0…). Hashes are in HASHES.txt.

## Purpose, and what this can and cannot change
- This is a correction check on our own public claims (atlas 1.8, `search_scaling_correction.md`). It is not a novelty claim.
- Prior art already shows that more restarts raise decipherment accuracy (Berg-Kirkpatrick & Klein 2013, https://aclanthology.org/D13-1087.pdf). It also shows that a few known characters help (Luo et al. 2021, https://aclanthology.org/2021.tacl-1.5.pdf).
- **It cannot make Indus testable.** Indus's relatedness to any candidate language is unknown, it has about 400 signs, and the atlas 1.8 power failure (planted z 0.3-2.8) stands. The Indus verdict stays "Untestable" whatever happens here.
- **The only thing the result can change is the stated reason** in atlas 1.8, the README and the approach page (see the decision rule below).

## Design
- **Corpus.** `mm.build(pair, 2500, "syll", rep, model="K2")`: 2.5k tokens of short texts (1-2 words, about 5 signs each) enciphered as a syllabary.
- **Model.** The related-language model: Italian for Latin, Estonian for Finnish.
- **Cells.** 12 in all, 3 replicates each:
  - Latin/Italian with 0, 5 and 10 anchors;
  - Finnish/Estonian with 10 anchors only.
- **Anchors.**
  - Per (pair, rep), 10 signs are drawn with `random.Random(crc32("anch|pair|rep"))` from the signs that occur at least 5 times. The 5-anchor arm uses the first 5 of those 10.
  - Anchored signs are fixed to their true values in the initial key, skipped in sweeps and excluded from swaps.
- **Search.** The A3 attack (mm.gibbs, 100 sweeps, then the swap polish of fix 1), restricted to non-anchor signs.
  - Restarts run in chunks of 125, up to 1,000 per cell. Chunk c is seeded with `crc32("s1|pair|k|rep") * 1000 + c`.
- **Reference key.** The truth-climbed key is a greedy climb from the true key, then the same swap polish, both with the anchors fixed.
- **Scoring.**
  - Accuracy is token-weighted over non-anchor signs only.
  - The cell's key is the restart with the highest objective, never the one with the best accuracy.
- **Stop rule per cell, checked after each chunk.** Stop adding restarts once the best blind objective is at or above the truth-climbed objective while the selected key's accuracy is below 0.5.

## Labels per cell
- **solved:** the selected accuracy is ≥ 0.5.
- **objective-limited:** the selected accuracy is < 0.5 and the best blind objective is ≥ the truth-climbed objective.
- **search-limited:** after 1,000 restarts the best blind objective is still below the truth-climbed objective, and accuracy is < 0.5.

## Decision rule (wording only)
The Latin/Italian cells with 0 anchors decide it (3 replicates).
- **If 2 or more of the 3 are "solved":**
  - The reason becomes: "At Indus size, heavy search can recover a close related language. Whether it works depends on how close the language is, which is unknowable for Indus."
  - "More text never helps" stays withdrawn.
- **If 2 or more of the 3 are "objective-limited":**
  - The reason becomes: "At Indus size, even a close related language's objective prefers wrong keys, so more search cannot help. More text helped Latin at 10k-30k."
- **Otherwise (mixed or search-limited):**
  - The reason becomes: "At Indus size the result is mixed. Search depth matters, and so does closeness."

The anchor arms are reported as a description: accuracy and labels at 0, 5 and 10 anchors. Finnish with 10 anchors shows whether anchors rescue a pair that is limited by its objective. Neither enters the decision.

## Not done
- No 10,000-restart arm.
- No other pairs.
- No Indus run.
- No paper.
