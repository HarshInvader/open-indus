# Stamp-impression detector on Yale CC0 tablet photos: gate and sweep (DRAFT, not yet sealed)

Agent `paper`, on the coordinator's decision of 2026-11-20. Prior art, licences and controls: `docs/prereg/stamp_detector_priorart.md`. Code: `experiments/stamp_detector/` (`harvest.py`, `sheets.py`, `embed.py`, `gate.py`). Hashes go in HASHES.txt when this is sealed.

## Why and what is new
- **The gap.** Catalogues hide non-cylinder seals. CDLI records YBC 5447's Gulf stamp only as "(not given)" (atlas 9.2). A digraphic object, an Indus or Gulf stamp on a tablet that names people, is the one find that changes the odds of a decipherment.
- **Novelty.** This is the first search of a cuneiform photo archive for stamp-seal impressions by image, rather than through catalogue tags.

## Honest odds
- **Gulf positives.** There is one Gulf-stamp positive control (YBC 5447). The detector is trained and gated on stamp impressions in general, which are mostly 1st millennium.
- **What a flag means.** A sweep flag is only a lead for expert review. It is not evidence of a Gulf or Indus seal.
- **Chance of a real find.** The prior that any Yale Ur III or Old Babylonian tablet carries an unrecorded Gulf or Indus stamp is low, probably below 10% for the whole collection. A null sweep narrows the search to unphotographed edges and other collections. It does not close the hunt.

## Data
- **Source.** The Yale Peabody Museum Babylonian Collection, through the open Peabody API (`peabody.collections.yale.edu`, robots.txt disallows only `/view/results/`).
- **Images.** IIIF manifests, each checked for a CC0 rights statement, at 1 request per second. The LUX host is behind a bot challenge and is not used.
- **What is published.** Images stay local. Only derived counts, catalogue numbers and links are published.
- **Positives (P).** Yale tablets and tags whose catalogue record mentions "stamp" (280) and on which an eye labeller marked a stamp impression as visible (`labels_pos.csv`, spot-checked by `paper`).
- **Controls (C).** YBC 5447 (Yale 2021 photo, CC0), plus CDLI photos P257839, P272900, P257073 and P269244 (local study use only).
- **Negatives.**
  - (N-early) A seeded random sample of Yale Ur III and Old Babylonian tablets with images. These are the sweep population, so they are excluded from the sweep tally.
  - (N-late) A seeded random sample of Neo-Babylonian tablets, used in training only, so that the detector cannot learn "late tablet" instead of "stamp".

## Detector
- **Tiles.** Each image is resized to 1600 px wide and tiled at 192 px (stride 96) and 320 px (stride 160). Background, the left label strip and the bottom scale band are skipped. Each tile is embedded with CLIP ViT-B-16 (laion2b).
- **Classifier.** Multiple-instance logistic regression with 3 rounds. Round 1 treats all tiles of positive images as positive. Rounds 2 and 3 keep the top 3 tiles of each positive image. All tiles of negative images are negative.
- **Image score.** The maximum tile probability.
- **Threshold.** Fixed on the training set alone, using 5-fold out-of-fold scores, at the score that flags 1% of training N-early images.

## Gate (on the held-out test set; run once)
- **Split.** By object, seed 20261120.
  - P: 60% train, 40% test.
  - C: all test.
  - N-early: 400 train, 300 test.
  - N-late: train only.
- **Pass needs both of:**
  1. Recall at least 0.80 on P_test ∪ C.
  2. False flags at most 0.02 of N-early test images (at most 6 of 300).
- **How flags are reviewed.** Every flagged N-early test image is reviewed by eye. A flag that shows a real stamp impression counts as a find, not a false flag, and is reported as such.
- **Reported, but not part of the gate:** recall on C alone, whether YBC 5447 was recovered, and recall by period.
- **Fail.** Stop, and record it in atlas 9.2.

## Sweep (only if the gate passes)
- **Scope.** All Yale Ur III and Old Babylonian (including Early OB) tablets with CC0 images, minus the gate images.
- **Output.** Every flag gets a review-queue row: catalogue number, photo link, date and named parties from the catalogue record, score and tile location.
- **No retraining after the sweep starts.**
- **Caps.** 2 days of work and 4 workers.
