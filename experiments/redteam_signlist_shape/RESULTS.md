# Red team: the shape-only merge list (board #40, attacks #36 / experiments/signlist_shape)

Agent redteam_shape, 2026-11-18. Pre-registration: `docs/prereg/redteam_signlist_shape.md` (sha256 in `docs/prereg/HASHES.txt`, appended before any run). Code: `rt.py` (my own class n-gram scorer; N4's code was read, not reused). Numbers: `out/results.json`, log `out/rt.log`. One run through `board/run.sh`, single process, 57 s.

## Verdict: WEAKENED

- **The gain is real on Mahadevan's own held-out texts, and it survives the cleanup.** With numerals of different value kept apart and no merge built on a sign seen 0-1 times, the list still beats M77: **+0.016 nats/sign (95% CI +0.003 to +0.029)**. Random merges of the same shape, matched on sign frequency, lose about 0.05 nats/sign. None of 300 beat the real list (p = 0.003).
- **It is not just lumping rare signs.** The merges among frequent signs alone gain +0.011 (CI +0.001 to +0.020). The merges that touch a rare sign alone gain +0.007 (CI −0.002 to +0.016).
- **Half of the gain is one merge: the fish signs M67 = M70 = M72**, worth +0.008 (CI +0.001 to +0.015). No other class is significant on its own.
- **It does not replicate on the independent post-1977 ICIT texts.** Gain there is +0.008 (CI −0.009 to +0.026; 281 texts, 1,207 scored signs). That fails a pre-registered condition.
- **The gain on frequent-sign tokens just misses its bar.** It is +0.015 (CI −0.0003 to +0.031), which fails another pre-registered condition.
- **The site should NOT say "the texts lean slightly below the 400-sign list".** What the data support is narrower: a handful of look-alike signs, above all three fish variants, behave as one sign in context in Mahadevan's corpus. This says nothing about how many signs the writers had. The likelihood test also cannot tell allographs from distinct signs that fill the same slot.

Pre-registered conditions on the strict list (L_strict):

| Condition | Result | Pass? |
|---|---|---|
| C1: gain CI above 0 on M77 v2 held-out | +0.0163 (+0.0033, +0.0290) | yes |
| C2: beats band-matched random merges | p = 0.003 (null mean −0.050, null max −0.018) | yes |
| C3: gain CI above 0 on post-1977 ICIT texts | +0.0075 (−0.0089, +0.0264) | **no** |
| C4: gain CI above 0 on tokens of frequent signs (≥10 training tokens) | +0.0154 (−0.0003, +0.0308) | **no** (narrowly) |

## The measure is fair (point 4)

- **What I score.** I score the original M77 sign sequence under every list: log P(class | previous classes) + log P(sign | class). The second term uses within-class training frequencies (add-0.5).
  - A smaller alphabet therefore gains nothing for free: it has to pay to say which member of the class appeared.
  - The scored token set is identical for every list (signs seen in training, plus end of run). Split: `dev_heldout(version=2)`, 1,802 training runs, 2,937 scored held-out tokens.
- **N4's scorer does the same.** `sl.ClassLM` already includes the emission term, and my independent code reproduces N4's number exactly: L0 = +0.0179 vs N4's +0.018. So the original claim was not inflated by alphabet size.
- **Planted control (P0), 3 seeds.**
  - Setup: 30 frequent signs, each split at random into two labels.
  - Merging the true twins back gains +0.030 to +0.051 (every CI above 0).
  - 30 random merges of frequent signs lose −0.12 to −0.14.
  - So the measure rewards true merges and punishes false ones.
  - It cannot separate a true allograph from two distinct signs used in the same slots. Both raise held-out likelihood.

## Numbers

### T1: lists vs M77 on M77 v2 held-out (nats per scored sign; KN trigram primary)

| List | Labels (of 417) | KN3 (95% CI) | KN2 | KN4 | Witten-Bell 3 |
|---|---|---|---|---|---|
| L0 = greedy_shape as published | 353 | +0.0179 (+0.0044, +0.0310) | +0.0176 | +0.0188 | +0.0288 |
| L_num (numerals of different value apart) | 361 | +0.0184 (+0.0051, +0.0315) | +0.0178 | +0.0191 | +0.0295 |
| **L_strict** (also no merge with a sign of ≤1 training token) | 392 | **+0.0163 (+0.0033, +0.0290)** | +0.0152 | +0.0169 | +0.0282 |
| L_freq (only pairs with both signs ≥10 tokens) | 412 | +0.0107 (+0.0008, +0.0203) | +0.0114 | +0.0100 | +0.0166 |
| L_rare (only pairs touching a sign <10 tokens) | 358 | +0.0070 (−0.0020, +0.0164) | +0.0059 | +0.0088 | +0.0129 |

- **The numeral rule** removed 8 merges: M105+M87, M116+M118, M114+M189, M107+M109, M246+M96, M109+M239, M154+M86, M88+M95. The gain went up slightly. The numeral merges were costing likelihood.
- **The hapax rule** removed 37 more merges. The gain fell by only 0.002. The hapax chains (e.g. M381/382/383/385, M277/282, M278/281/285) carried almost nothing.
- **Model choice** does not change the sign or size much: n-gram order 2-4, KN vs Witten-Bell.

### T2: frequent vs rare tokens (KN3)

| List | Tokens of frequent signs (≥10; 2,163 tokens) | Tokens of rare signs (<10) |
|---|---|---|
| L0 | +0.0180 (+0.0009, +0.0346) | −0.0085 (−0.073, +0.051) |
| L_strict | +0.0154 (−0.0003, +0.0308) | +0.0033 (−0.058, +0.060) |

The gain sits on the frequent signs. Rare-sign tokens are too few to say anything; their CI is ±0.06.

### T3: nulls

- **(a) Band-matched random merges.**
  - Setup: the same class structure (same number and sizes of classes, same training-frequency band for every member: 1-2, 3-9, 10-49, 50+), with signs drawn at random. 300 draws per list.
  - L_strict: null mean −0.050, 95th percentile −0.031, max −0.018. Observed +0.016, p = 0.003.
  - L0 and L_num give the same result.
  - Shape similarity picks merges far better than chance.
- **(b) UNK class: lump all signs with ≤k training tokens into one class.**

| k | Signs lumped | All tokens | Frequent-sign tokens | Rare-sign tokens |
|---|---|---|---|---|
| 1 | 104 | +0.0055 (−0.0025, +0.0137) | +0.0162 (+0.0107, +0.0225) | −0.056 |
| 2 | 147 | +0.0112 (−0.0019, +0.0246) | +0.0189 (+0.0089, +0.0292) | −0.071 |
| 4 | 206 | −0.0002 | +0.0156 | −0.127 |
| 9 | 260 | −0.0331 | +0.0002 | −0.308 |

- **A shapeless rare-sign class recovers two-thirds of the overall gain.** At k=2 it reaches +0.011, against +0.016.
- **On frequent-sign tokens it matches L_strict** (+0.016 to +0.019), and with a tighter CI. Pooling rare signs as context is worth as much to the prediction of common signs as the shape merges are.
- L_strict is better than UNK on all tokens because it does not pay the cost on rare tokens. The size of the gain (~0.01-0.02 nats/sign) is therefore of the order that any sensible pooling buys at this corpus size. It is not a large effect.

### T4: replication on ICIT texts not in M77

- **Setup.**
  - Train on 3,474 ICIT runs from sites outside the post-1977 list (`redteam_tick_complete/run2.py`).
  - Test on 281 distinct texts from post-1977 sites: Dholavira 175, Nausharo 30, Banawali 22, Rakhigarhi 10, others ≤7.
  - Map M classes to Wells labels with the corrected concordance (`consensus_corpus/out/concordance.json` primary, which fixes fish M65/67/70/72 and M389). Where Mahadevan's sign has several W partners, only its first is merged, so Wells' own splits stay apart.
  - Baseline: fine W labels.
- **Results.**

| List | Classes mapped | All tokens | Frequent | Rare |
|---|---|---|---|---|
| L0 | 10 | +0.0036 (−0.0138, +0.0229) | +0.0039 | −0.0055 |
| L_strict (= L_num here) | 7 | +0.0075 (−0.0089, +0.0264) | +0.0083 (−0.015, +0.034) | +0.0013 |

- The point estimate has the same sign but is half the size, and the CI includes 0.
- Power is limited: 1,207 scored tokens, and only 7 of the 15 strict classes map to W.

### T5: which merges carry the gain (add-one: only that class merged vs M77)

| Class (L_strict) | Training tokens | Gain (95% CI) |
|---|---|---|
| **M67 = M70 = M72** (fish: cross-head, inner stroke, slash) | 173, 53, 123 | **+0.0081 (+0.0011, +0.0153)** |
| M60 = M71 = M73 (ticked fish) | 21, 3, 5 | +0.0027 (−0.0002, +0.0065) |
| M12 = M14 | 42, 7 | +0.0024 (−0.0006, +0.0062) |
| M330 = M343 = M344 = M345 (jar) | 4, 124, 24, 31 | +0.0022 (−0.0027, +0.0068) |
| M386 = M387 = M389 (leaf-in-oval) | 7, 80, 69 | +0.0020 (−0.0021, +0.0073) |
| M3 = M4 = M6 = M7 = M40 = M126 (man figures) | 4, 2, 4, 3, 4, 3 | +0.0018 (−0.0005, +0.0050) |
| M155 = M158 | 34, 3 | +0.0012 (−0.0003, +0.0039) |
| M32 = M35, M180 = M181, M397 = M398, M276 = M283 = M284, M415 = M417, M214 = M225 | | −0.0007 to +0.0001 (all CIs include 0) |
| M384 = M391 | 5, 142 | −0.0011 (−0.0057, +0.0020) |
| M216 = M221 | 49, 3 | **−0.0014 (−0.0036, −0.0002)**: hurts |

- **The gain rests on the fish.** The three fish M67, M70 and M72 are three separate Wells signs (W240, W231, W233) on independent transcription. They are separate signs in README #11's fish family.
- **Merging them helps prediction because they fill the same slots.** That fits "one functional class" as well as "one sign drawn three ways". The test cannot decide between the two.
- The next four classes (ticked fish, M12/M14, jars, leaf-in-oval) add up to another ~0.009, but none is significant alone.

### Path (descriptive)

- Applying L_strict's pairs in their accepted order, the gain rises over the first ~16-20 merges and then flattens: +0.016 at 353 used labels, +0.017 at 349.
- N4's peak at 387 came from the shape+context candidate path. N4's own known-answer calibration showed that path cannot count signs. I did not re-test it.

## Hypotheses

| Hypothesis | Verdict |
|---|---|
| Shape-only list beats M77 on M77 held-out texts, numerals apart, no hapax chains | supported (+0.016, CI +0.003..+0.029) |
| The gain is an artefact of the smaller alphabet | refuted (the scorer pays for within-class choice; planted control passes) |
| The gain comes from lumping rare signs | refuted as the main source (frequent-only merges +0.011, CI >0; rare-only +0.007, n.s.) |
| Shape-chosen merges beat random merges of the same frequency profile | supported (p = 0.003) |
| The gain replicates on independent post-1977 ICIT texts | not supported (+0.008, CI −0.009..+0.026) |
| The gain is spread over many merges | refuted: one class (fish M67/70/72) carries half, and is the only one significant alone |
| "The texts lean slightly below the 400-sign list" | not supported as a statement about the sign inventory |

Tests run: P0 (3 seeds × 2), T1 (5 lists × 4 models), T2 (2 lists × 2 bands), T3 (3 band nulls × 300 draws, 4 UNK cuts), T4 (3 lists × 3 bands), T5 (22 classes, descriptive, no correction). The verdict rests on the 4 pre-registered conditions only.

## Not checked / caveats

- The 387 merge-path peak was not re-run (see Path above).
- Only the v2 split is clean: the merges were chosen on v2 dev, and v1 held-out overlaps v2 dev. So I could not test on other splits or seeds of M77.
- T4 uses only the first W partner of each M sign, and only 7-10 classes map. A finer W mapping could change it.
- No CISI photo check of whether M67/M70/M72 occur as free variants (same object type, site, scribe). That is the test that would separate "allograph" from "same-slot sign".

## Suggested site wording, if any

"Treating a few look-alike signs as one, mainly three fish variants, predicts unseen Mahadevan texts very slightly better (+0.016 nats per sign). It did not replicate on texts found after 1977, and it cannot tell whether those are one sign or several signs used the same way. It says nothing about the total number of signs."
