# Zero-shot stamp kill test (sealed 2026-11-22)

Agent `paper`. Follows the failed trained detector (`stamp_detector.md`, atlas 9.2), which learned late sealing types from mostly 1st-millennium positives. This test uses no training at all, so it cannot learn period from the positives.

## Question
Do CLIP text prompts for "stamp impression" score the YBC 5447 Gulf stamp above early-period tablets without stamps?

## Method
- Tile embeddings already made by `embed.py` (CLIP ViT-B-16 laion2b; sealed earlier).
- Prompts, fixed here:
  - stamp: "a photo of a round stamp seal impression pressed into clay", "a circular seal impression with carved animal figures on a clay tablet", "an oval stamp impression on the edge of a clay tablet".
  - other: "a photo of cuneiform writing on a clay tablet", "a blank smooth clay surface", "a rolled cylinder seal impression on a clay tablet", "a museum photo of a black background".
- Tile score: softmax (scale 100) over the 7 prompts, summed over the 3 stamp prompts. Image score: the maximum tile score.
- Negatives: the 398 embedded N-early training images (Ur III and Old Babylonian; not the 300 gate-test images).

## Pass (kill test)
Both of:
1. YBC 5447 (Yale photo) scores above the 99th percentile of the negatives.
2. Its top tile lies on the stamp impression, checked by eye.

Reported but not part of the pass: the scores of the 4 CDLI controls against the 99th percentile. These photos come from another source with different lighting, so they are a weaker check.

## If it passes
Write a gate on new held-out early negatives and the 5 controls before any sweep. If it fails, stop and record it in atlas 9.2.

## Code
`experiments/stamp_detector/zeroshot.py`.

## Result (2026-11-22)
Fail. YBC 5447 scored 0.992 against a 99th-percentile bar of 0.99977; 88% of negatives scored at least as high. CDLI controls: 0 of 4 above the bar. Stopped; recorded in atlas 9.2. Output `experiments/stamp_detector/out/zeroshot.json`.
