# Pre-registration: self-labelling objects (experiments/self_label)

Written 2026-11-15, BEFORE any sign-by-object-class distribution was computed in this area. Frozen inputs, hashed in HASHES.txt:
- `experiments/self_label/shapes.py`: silhouettes of each object class, defined as line drawings in code from the objects' physical shape, plus the three shape routes.
- `experiments/self_label/s1_freeze.py` and its output `frozen_candidates.json`: top-3 signs per object class per route.
- `experiments/self_label/s2_test.py`: the test code, run once.

## Question
Does any sign depict the object it is written on (a "this is the jar / axe / bangle of X" label)? If so, the sign nearest in shape to an object class should be enriched on that class, beyond that class's own vocabulary register.

## Object classes (inventory from M77 object_type and ICIT type)
Testable (>= 5 distinct texts in a set): seal, sealing, miniature tablet, copper tablet, pottery graffito, ivory/bone rod, bronze implement (M77 and ICIT); stamped pottery (ICIT POT:T:s, pointed goblets) and bangle (ICIT BNGL, mostly stoneware) in ICIT only.
Not testable: weights (no inscribed weights in either corpus), beads (2 ICIT items). Copper tablets come from one site only (Mohenjo-daro, plus 1 Kalibangan), so they cannot pass the second-site criterion. That is decided now.

## Shape step (blind, done)
Pool: 196 signs with >= 5 distinct M77 texts (all object types pooled; frequency only).
Routes, ranked before any distribution was seen:
1. **Primary: chamfer**: symmetric chamfer distance between thinned, bbox-normalised line drawings (keeps orientation and aspect ratio).
2. **Secondary: catalogue**: keyword match in the blind referent catalogue's descriptions (`experiments/iconography/sign_referents.csv`, top-120 signs only), keywords fixed in `shapes.py`.
3. **Tertiary: Hu**: log Hu moments (first 4) of the hole-filled region. **Disclosure:** v1 computed Hu on 1-px outlines, which is numerically degenerate (distances of 45-75); I saw this on the contact sheet and fixed it to the filled region before any distribution was computed. The v1 output is kept as `frozen_candidates_v1_hu_bug.json`. The fixed Hu route still matches visibly poorly (e.g. rods, seal face) and is flagged as unreliable now, before testing.
Top-3 per class per route gives 78 distinct (class, sign) pairs (`frozen_candidates.json`).

Contamination note: while inventorying the object classes I printed the first ~20 texts of rods, implements, pottery graffiti, M77 miscellaneous and ICIT bangles/implements. So I had glimpsed, for example, that rods often end in M342 M176 and that M162 repeats on two rods. The shape ranking is algorithmic and was not changed in response to this. The silhouettes were drawn from object shape, and the only change after viewing the output was the Hu bug fix above.

## Test (s2_test.py)
Unit: distinct (sequence, object class, site). ICIT signs are mapped to Mahadevan numbers through the Wells-Mahadevan bridge: a text contains M-sign s if any of its W signs maps to a list containing s.
Statistic per (class C, sign s): the number of class-C texts containing s. Null: object-class labels permuted among texts **within site**, 10,000 permutations (this is the object-vocabulary null). One-sided p for enrichment.
Register control: s's percentile, by null z-score, among all pool signs present in >= 3 texts of the set on class C.
Sets: M77 dev, M77 held-out v2 (`dev_heldout(version=2)` membership), ICIT (all sites; an independent transcription, mostly the same objects).

## Confirmation rule (per pair)
A pair counts as a confirmed self-label if ALL of the following hold:
- C1: ICIT BH q < 0.05 across all testable frozen pairs;
- C2: one-sided p < 0.05 at a second ICIT site (any site other than the class's largest site, with >= 3 class texts), using a site-restricted label permutation;
- C3: register percentile >= 0.90 in ICIT (s is among the top 10% of signs enriched on C, not just part of a large register);
- C4: same direction (obs > exp) on M77 held-out v2, when the class is testable there.

**Decisive positive:** >= 2 distinct signs confirmed. **Null:** 0 confirmed. 1 confirmed = "single lead, not a reading".

## Global test (secondary)
For each route x set: the mean register percentile of the frozen signs vs random draws of the same number of pool signs per class (10,000 draws). One-sided. 3 routes x 3 sets = 9 tests; Bonferroni alpha 0.0056. This asks whether shape similarity predicts enrichment at all, even if no single sign passes.

## Falsification
If the nearest-shape signs are not enriched (global percentile ~0.5) and no pair passes, "signs as object labels" is unsupported at this data size for these classes. This would not exclude self-labels for classes we cannot test (weights, beads), or object words that are not drawn like the object.
