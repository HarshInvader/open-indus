# Parpola rules 3 and 4: vēl as a fish stand-in, and Murukan's fixed partners

Prereg: `docs/prereg/parpola_rules34.md`, hashed 2026-11-20T22:11:14Z before any run (fix 1 hashed later; see Deviations). Code: `p34.py`, `run.py`. Exploratory: `posthoc.py`. Numbers: `results.json`. Logs: `*.log`. All counts are on distinct texts. Every job ran through `board/run.sh`.

## Conclusion

- **Rule 3 (M87 substitutes for fish M59): underpowered.**
  - The method found 1 of 50 planted stand-in pairs (2%). The bar was 80%. Even when half of a sign's tokens stood in, it found only 3 of 30.
  - The real pair does not pass anywhere: dev p = 0.22, held-out p = 0.31, new sites p = 0.23.
  - M87 does not take fish's slot. It sits next to fish: "M87 M59" is one of the commonest two-sign segments (44 in dev).
- **Rule 4 (M403 is followed by M87 or the squirrel): the M87 half passes, the squirrel half gets nothing.**
  - M403 is followed by M87 in 23 of 48 dev tokens (0.48; null 99th percentile 0.08; p = 0.0014).
  - This replicates on held-out (4 of 17; p = 0.003) and at post-1977 sites (W840 → W032 in 4 of 9; p = 0.0009).
  - The squirrel (M51/M52, W255) never follows M403: 0 of 74 tokens across all three sets.
- **Rule 4 is a fixed pair, not a reading.** It is the regularity Parpola built his reading on ("frequently postfixed"), so it confirms his starting observation, not "Muruka-vēl". The same repo reads M87 as the tall-stroke numeral 2 (`numeral_grammar`). "M403 + 2" fits the data just as well. Ladder level L1.
- **Red team, rule 4.** It passes both alternative nulls on dev. It fails the pre-registered near-copy collapse, so by the frozen rule it is labelled **fragile**. That collapse is degenerate: it chains 571 dev texts into one family. A non-chaining de-duplication (post hoc) keeps the result: 0.42, p = 0.0013.
- **Not to be repeated.** Rule 3's question cannot be answered with context overlap at this corpus size.

## Known-answer gates (dev, 50 planted trials each)

| | Planted | Detection at p < 0.01 | Bar | No-plant hit rate | Power at held-out size (p < 0.05) | Gate |
|---|---|---|---|---|---|---|
| Rule 3 | 25% of sign a's tokens relabelled from b | **1/50 = 2%** (strong 50%: 3/30 = 10%) | 80% | 2% | 20% | **fail → underpowered** |
| Rule 4 | partner x after head h in 30% of tokens | **48/50 = 96%** | 80% | 8% | 100% | **pass** |

- Rule 3 fails because the matched pool holds real look-alike paradigms: fish variants M65/M67/M72, numerals, and the M336 M89 pair. Their overlaps reach 0.97. A planted 25% stand-in never climbs above all of them.
- Rule 4's 8% no-plant hit rate is not a pure false alarm. Random head-partner pairs include real bigram preferences. That is why the heads null (alternative null A) matters.

## Results

### Rule 3: overlap of left and right contexts (cosine, subsampled)

| Set | n M87 / M59 | Overlap | Null median | Null 95% | Pairs | p | Kill (≤ median)? |
|---|---|---|---|---|---|---|---|
| Dev | 191 / 234 | 0.366 | 0.194 | 0.530 | 136 | 0.22 | no |
| Held-out | 57 / 67 | 0.343 | 0.264 | 0.526 | 153 | 0.31 | no |
| New sites (W032/W220) | 27 / 30 | 0.491 | 0.260 | 0.592 | 78 | 0.23 | no |

The pair sits above the median but far below the top. That is not a pass, and with a 2% gate it is not a clean refutation either.

### Rule 4: share of M403 followed by {M87, M51, M52}

| Set | M403 with a next sign | Share (M87 / squirrel) | Null 95% / 99% | Pseudo-sets | p | Kill? |
|---|---|---|---|---|---|---|
| Dev | 48 | **0.479** (23 / 0) | 0.042 / 0.083 | 692 | **0.0014** | no |
| Held-out | 17 | 0.235 (4 / 0) | 0.118 / 0.118 | 1,080 | **0.0028** | no (above 95%) |
| New sites (W840 → W032, W255) | 9 | 0.444 (4 / 0) | 0.000 / 0.111 | 1,080 | **0.0009** | no |

- The dev share passes the "mostly" bar of 0.4. The held-out share (0.24) does not; it is half the dev rate. The prereg sets the bar on dev, so the frozen verdict is "supported (fixed partner)". The weaker held-out share is a caveat.
- The pair is not one copied text. In dev, 23 different texts from 4 sites (Mohenjo-daro, Harappa, Chanhu-daro, Lothal) carry it. They include 16 seals, 3 sealings, 3 tablets and 1 bronze tool, with 13 different left neighbours (counting the text start). Most end in the formula "M403 M87 M342".

## Red team

| Check (dev; held-out for reference) | Rule 3 | Rule 4 |
|---|---|---|
| Alt null A (rule 3: 50 position-matched pairs; rule 4: 46 frequency-matched heads, same partners) | p = 0.24 (held 0.37) | **p = 0.021** (held 0.018) |
| Alt null B: within-text order shuffle, 1,000 times | p = 1.0; shuffled overlap 0.82 > observed 0.37 (held 1.0) | **p = 0.001** (held 0.08) |
| Robustness: no edge tokens (rule 3) | p = 0.13 (held 0.42) | n/a |
| Near-copy collapse, pre-registered rule | p = 0.48 | **p = 1.0 (share 0/16): fails** |
| Post hoc: greedy de-dup without chaining | p = 0.40 | p = 0.0013, share 0.42 (held 0.0032) |

- **Rule 3, shuffle.** The signs share texts but not slots. Shuffling raises their overlap from 0.37 to 0.82. That is the opposite of a substitution, but given the 2% gate it is descriptive only.
- **Rule 4, collapse.** By the frozen rule this is "fragile", and the failing check is the near-copy collapse. Why it fails: the `fish_tick_closer` collapse uses union-find on "contained or within one edit". The 3-sign sealing "M403 M87 M342" is contained in every text that carries the formula, and chaining then joins 571 of 1,698 dev texts into one family. Its single kept text has no M403. That removes any recurring formula by construction, which is exactly what is being tested. **Note for the lead:** `fish_tick_closer` used this collapse as its primary unit, so a 571-text family may have affected it too.
- Rule 4 holds against frequency-matched heads at p ≈ 0.02 on both splits, but not at 0.01. Part of the effect is that M87 follows many signs often, though M403 takes it far more than other heads.

## Hypotheses

| Hypothesis | Verdict |
|---|---|
| R3: M87 is a slot substitute for fish M59 | **Underpowered** (gate 2%); point estimates are not significant on all three sets |
| R4a: M403's next sign is concentrated on M87 | **Supported (fixed pair, L1)**; red team: fragile on the pre-registered collapse (diagnosed artefact), robust to both alternative nulls on dev |
| R4b: M403's next sign is the squirrel (Muruka-ppiḷḷai) | **Not supported**: 0 of 74 tokens on dev, held-out and new sites; the gate shows a 30% partner would have been seen |
| "Muruka-vēl" as a reading | Not tested; the pair fits "M403 + numeral 2" equally |

Tests run: 2 primary (α = 0.01 each), 4 replications, 10 red-team checks, and 1 post hoc check (`posthoc.py`, not pre-registered).

## Deviations

1. The prereg says "Written 2026-11-21". The actual UTC time of the hash was 2026-11-20T22:11:14Z.
2. Fix 1, hashed: `run.py` could not import `p34` under `python -I`. I added one `sys.path` line; there was no logic change. The gate was then run.
3. The prereg says dev has 1,699 texts. `prep` drops one text that is all breaks, so 1,698 were used.
4. `posthoc.py` was written after the collapse check failed. It is exploratory and does not change any verdict.

## Next experiments

- Rule 3 needs frames, not context overlap. That means multi-impression texts of one owner with M87 in one copy and M59 in the other. This is the same "reopen" condition as atlas 1.4 and 1.7.
- To separate "M403 + numeral 2" from "Muruka-vēl", test whether M403 takes other tall-stroke counts (M86, M88/89, M95) in the same slot more than a matched null does. If M403 also takes 1, 3 and 4 tall strokes, M87 is a count. This should be pre-registered first.
- Fix the near-copy collapse: either no chaining, or skip containment for texts with ≤ 3 signs. Then re-check `fish_tick_closer`.
