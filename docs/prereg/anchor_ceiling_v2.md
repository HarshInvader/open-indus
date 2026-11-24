# anchor_ceiling v2: the same question with a method that can see a planted tie (sealed before any v2 run)

Agent `paper`. Main line (b). This is v2 of `anchor_ceiling.md`, decided by Fable on 2026-11-24 after the v1 kill test failed, then revised after a fresh Fable review (10 fixes applied).

## Disclosure
- **v1's kill test failed** on its plants (`experiments/anchor_ceiling/kill.json`).
  - At strength 1.0: power 0.0, and median adjusted Rand -0.0004.
  - The v1 verdict stands: "the method cannot see a perfect tie at Indus size". No v1 real run happened, and none will.
- **The v1 null corpus was stopped unread.**
  - It shuffled one anchor at a time against the real truth, so it would have shown the real site and class association.
  - It wrote no output and none was read.
- **Seen before this design (planted data only, draw 0, one plant, strength 1.0):**
  - Average-link clustering chained (cluster sizes 62, 6, 5, 4, 1, 1, 1).
  - k-means (k = 7) on unit-normalised profiles reached a dev adjusted Rand of 0.25 with all A3 dimensions, and 0.71 with picture dimensions only.
- **v1 bar defect.** Goods and person (5 words each) were scoreable in ≥ 4 draws in only 10 and 9 of 20 plants, so the bar was unreachable.
- **v1 smoothing defect.** Add-0.5 per value gives rare anchor values positive log-ratios for rare words.
- **Word counts seen for this design** (no anchors):
  - 44 union words have ≥ 2 held-out documents in ≥ 4 draws (the "pool").
  - Of the kept words, the pool holds place 16, admin 10, land 5, occupation 3 and person 3.
- **Unchanged from v1:**
  - the frozen truth (κ 0.881), the words, the draws, the rungs, the leak rule, the field list;
  - the outcome bands, readings and limits, except as changed below.
- **The real word × anchor association is still unseen.**
- **This is the last version.** A v2 failure closes the Linear B calibration, and main line (b) falls back to function (L1).

## Changes
1. **Smoothing.**
   - share(v) = (count(v) + α · base(v)) / (n + α), with α = 2.
   - The profile is log(share / base).
   - base(v) is computed from dev documents only, for dev and held-out profiles alike, over dev-observed values only.
2. **Blocks.**
   - Each anchor variable is one block, and each block is unit-normalised.
   - A word's profile is the concatenation of its rung's blocks.
3. **Clustering.**
   - **Candidates:** exactly two methods, on the same vectors:
     - k-means (scikit-learn, `n_init` = 20, `random_state` = 0) on the concatenated profile;
     - Ward linkage on the same vectors.
   - Held-out words go to the nearest centroid by cosine.
   - **Selection (method choice only):**
     - 10 plants from selection seed 20261201, at strength 1.0, rung A3.
     - The statistic is the median over plants of the per-plant median held-out adjusted Rand over draws. Pick the higher; a tie goes to k-means.
     - **The selection result stops nothing and changes nothing but the method.**
     - It is written to `select.json` and hashed before the kill test.
4. **Scoreable fields.**
   - A field is scoreable if it has ≥ 3 held-out kept words in ≥ 4 of 5 draws. For the real truth that is place, admin, land, occupation and person (from word counts only). Goods is not scoreable.
   - k = 6 (5 scoreable fields + 1), fixed in every draw, with a fixed field list.
   - **In a draw,** a field with fewer than 3 held-out words is unscored there. To be recovered (≥ 4 of 5 draws), it must therefore pass every remaining draw.
5. **Plant.**
   - Each scoreable field gets its real size.
   - It takes its real pool count from the 44 pool words (place 16, admin 10, land 5, occupation 3, person 3).
   - The remainder comes from the other 48 union words (9, 4, 3, 5, 2).
   - The draw is repeated until every field is scoreable in ≥ 4 draws.
   - The v1 picture plant rule is kept.
6. **Order.**
   - The supervised gate runs on the plants first. If it fails, the study stops before the blind kill test.

## Kill test (fresh plant seed 20261202, 20 plants, strengths 1.0 / 0.6 / 0.3)
- **Supervised gate** (strength 1.0). Both must hold:
  - (a) leave-one-word-out nearest true-field centroid on dev recovers every field in ≥ 80% of plants;
  - (b) true-field dev centroids assign held-out words with median adjusted Rand ≥ 0.8, and every field is recovered in ≥ 80% of plants.
- **Blind bar** (strength 1.0): median adjusted Rand ≥ 0.8, and every scoreable field is recovered in ≥ 80% of plants.
  - This is expected to be hard, given the disclosed dev values.
  - **No bar changes after `select.json`.**
- **Null corpus (gate).**
  - Each document's whole anchor tuple (site, class, picture, hand) is permuted across documents, 200 times, with the real truth.
  - The A3 "any field recovered" rate must be ≤ 0.05.
- **Report:**
  - the smallest powered strength;
  - the planted pair AUC (same-field against different-field, dev) per strength. The capped claim is stated in those units.
- **Stop readings:**
  - supervised failure: "profiles too thin at this size";
  - blind-only failure: "blind clustering fails";
  - null failure: "the method finds fields in noise".
  - In every case, no anchor claim is made.

## Real run (only after the kill test passes and `kill2.json` is committed)
- As in v1, with the v2 method:
  - rungs A1-A4;
  - 1,000 within-bin permutations;
  - recovered = F1 ≥ 0.5 and above the null's 95th percentile in ≥ 4 of 5 draws;
  - the supervised control and pair AUC reported.
- **Per-rung added-anchor shuffle nulls** (v1 fix 7) run here, as part of the real run. A rung is read only if its own null passes.
- **Bands count scoreable fields** (5): high ≥ 3, middle 1-2, low 0.
- **Calibration scope.**
  - The plant touches pictures only, so A1 and A2 readings, including "A2 alone ≥ 20%", are **uncalibrated**.
  - One exclusive picture value per field is cleaner than any real tie, so the plant is an easy case.

## Code
- **`core2.py`** imports `core.py` unchanged. It overrides `profiles`, `cluster`, `assign`, `run_rung` and `score_draw`, with a fixed k = 6, a fixed field list and a method argument.
- **Scripts:**
  - `select2.py` writes `select.json`;
  - `kill2.py` writes `kill2.json` (supervised gate first, then blind, then the null corpus);
  - `run2.py` writes `result.json` and refuses to run unless `kill2.json` passed and is committed.
- **Seal:** the code is sealed before `select2.py` runs; `select.json` is hashed before `kill2.py` runs.
