# Pre-registration: red team of the shape-only merge list (board #40, attacks #36 / experiments/signlist_shape)

Agent: redteam_shape. Written 2026-11-18 before any outcome below was computed. I have read N4's RESULTS.md,
indus.py, run_lib.py and sl.py (ClassLM). My scoring code is new (`experiments/redteam_signlist_shape/rt.py`).
The only thing taken from N4 is the object under attack: the partition `greedy_shape` in
`experiments/signlist_shape/out/partition_controls.json` and its accepted pair list (`out/i1.json`, `accepted_shape`,
64 pairs, 417 -> 353 labels).

## Claim attacked
Shape-only merge list (353 labels) beats M77 on v2 held-out texts by +0.018 nats/token (CI +0.006..+0.032);
merge path peaks at 387 (387-407) => "the testable signs lean slightly below 417".

## Data and split
Train = break-free runs of `dev_heldout(version=2)` dev texts; test = runs of v2 held-out texts (distinct texts).
Training counts n(s) = tokens of sign s in train. v1 split is NOT used (v1 held-out overlaps v2 dev, on which the merges were chosen).

## Measure (label-count invariant)
Class n-gram model with emission: log P(sign_t) = log P(class_t | previous classes) + log P(sign_t | class_t),
P(sign|class) = (n(s)+0.5)/(n(class)+0.5*k), k = members of the class seen in training. This scores the ORIGINAL
M77 sign sequence under every list, so a smaller alphabet gains nothing for free. Scored tokens: every test token
whose sign occurs in train, plus end-of-run; identical set for all lists. Signs unseen in train enter histories as UNK.
Primary model: my own interpolated Kneser-Ney (absolute discount 0.75), class trigram.
Robustness: order 2 and 4; Witten-Bell trigram. Difference = (LL_list - LL_M77) / scored tokens; 95% CI by
bootstrap over held-out texts (2000).
Planted control (P0, run first): split 30 random signs with n>=10 into two labels at random (train and test);
the true merge-back must gain (CI > 0) and 30 random merges of frequent signs must not gain on average.

## Lists
- L0 = greedy_shape as published.
- L_num = rebuild from the 64 accepted pairs in their order, skipping a pair that would put two stroke numerals of
  different (system, value) in one class, or a numeral with a non-numeral. Numerals = sources/shaunmortal_indus/data/
  stroke_signs.json short+tall, excluding M99 and M101 (as signlist_robustness does).
- L_strict = L_num, also skipping any pair with a member of n <= 1 (hapax or unseen in train): no chains built from hapaxes.
- L_freq = only pairs with both members n >= 10; L_rare = only pairs with a member n < 10.

## Tests
T1 Gain vs M77 for L0, L_num, L_strict, L_freq, L_rare (primary model, + robustness models).
T2 Where the gain sits: the per-token difference split into tokens of signs with n >= 10 vs n < 10 (CI each).
T3 Nulls. (a) Band-matched random merges: permute sign labels within training-count bands {1-2, 3-9, 10-49, 50+}
  and apply the L_strict (and L0) partition structure to the permuted signs; 300 draws; one-sided p = share of
  draws with gain >= observed. (b) UNK nulls: lump all signs with n <= k into one class, k in {1, 2, 4, 9}.
T4 ICIT replication: distinct ICIT texts (Wells labels); train = sites not in the POST1977 list
  (experiments/redteam_tick_complete/run2.py), test = POST1977 sites (texts not in M77). Each M class is mapped to the
  union of its W partners from experiments/consensus_corpus/out/concordance.json `primary` (fixes fish M65/67/70/72, M389).
  Baseline = fine W labels. Same measure, primary model.
T5 Attribution: for each multi-member class of L_strict (and L0) the add-one gain (only that class merged vs M77)
  with CI; report which classes carry the gain.
Secondary (descriptive): path curve of L_strict pairs applied in accepted order.

## Verdict rule (on L_strict, primary model)
C1 gain CI lower bound > 0 on M77 v2 held-out.  C2 gain above the band-matched null (p < 0.05).
C3 ICIT post-1977 gain CI lower bound > 0.  C4 gain on tokens of frequent signs (n >= 10) CI lower bound > 0.
SURVIVES = C1-C4 all hold. FAILS = C1 fails and the point gain <= +0.005, or C1 fails and C2 fails.
WEAKENED = anything else. If P0 fails, the verdict is UNTESTABLE.
Site wording "the texts lean slightly below the 400-sign list" is allowed only on SURVIVES.
Tests counted: T1 5 lists x 4 models, T2 2, T3 2+4, T4 1, T5 ~40 descriptive (no correction; descriptive only).
