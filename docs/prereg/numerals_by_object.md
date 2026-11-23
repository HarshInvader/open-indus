# Do Indus tablets carry counted numerals more than seals do? (sealed 2026-11-23, before any Indus number)

Agent `paper`. Main line (b). Fable's pick after scorecard v1 (recorded in RESEARCH_STATE): the corrected rerun of "counted vs frozen numerals by object type".

## Why, and what changed since the NO-GO
- `count_index_rehearsal` (2026-11-21) stopped at NO-GO.
- It failed on its proto-cuneiform bars. Proto-cuneiform has no frozen numerals, so it cannot be a counted-vs-frozen known answer ("every number there is a count").
- Latin (power 0.995) and the planted Indus gate (0.986) passed.
- This study replaces the proto-cuneiform gate with a Latin object-type known answer. **This is a changed gate after a failed one.** The old NO-GO is reported beside every result here.
- The question also changes: from "which heads are counted" (head-level calls) to "do tablets use more count-like heads than seals at the same site" (an object-type contrast). The index itself is unchanged.

## Index (unchanged from `count_index_rehearsal`, code reused)
- A pair is a numeral sign directly before a non-numeral head, inside a break-free run. Short and tall stroke tables come from `stroke_signs.json`; M99 and M101 are not numerals.
- The index of a head is the expected number of distinct numeral values in 4 tokens, by rarefaction. A head needs at least 8 tokens in the pool the statistic uses.

## Data (shape measured before sealing; no index read)
- M77 distinct texts. Harappa: seals vs miniature tablets. Mohenjo-daro: seals vs copper tablets.
- Pair tokens (tablet, seal): Harappa (41, 136); Mohenjo-daro (30, 494). Of these, 415 tokens sit on heads with at least 8 tokens.
- Sealings, pots, rods and other sites are excluded.

## Statistic
- D = the mean index on tablet tokens minus the mean index on seal tokens, computed per site and pooled with weights equal to tablet token counts.
- Null: tablet/seal labels permuted among texts within site. 2,000 permutations on real data, 300 per draw elsewhere.
- **Pass (both needed):**
  1. one-sided p ≤ 0.01;
  2. D > 0 at both sites.

## Kill test (run first): Latin known answer at Indus sizes
- EDH Latin pairs by `cir.edh_pairs`, de-duplicated as in `count_index_rehearsal`.
- The "tablet" role is epitaphs (counted ages). The "seal" role is honorific, building/dedicatory and military diploma inscriptions (frozen unit numbers and titles).
- Whole texts are drawn until the Indus token counts per site are reached (41/136 and 30/494). The index is computed per draw.
- 200 draws, full pass rule. **Power must be ≥ 0.8. Otherwise STOP:** "untestable at Indus size".
- Feasibility was run before sealing (Latin only, 30 draws, `feasibility.py`): power 1.0. The Latin contrast is extreme, so this gate checks only that the pipeline works. The planted gate below sizes the test.

## Planted gate on the real Indus texts (sizes the null)
- **Label swaps within site; texts are never edited.** A tablet text and a seal text with a higher mean index and a similar token count (±1) swap labels. Swaps continue until the tablet mean index reaches its natural value + Δ (at most 400 tries per site, otherwise the draw is infeasible).
- Δ ∈ {0.25, 0.5, 1.0, 1.5} index units, 40 draws each, full pass rule.
- **c\*** = the smallest Δ with at least 20 feasible draws and power ≥ 0.8.
- If c\* is missing or > 1.0, the verdict is "untestable" and the real statistic is not reported as a test.
- The Latin mean D from the kill test is reported as the real-script reference gap on the same scale.

## Outcomes (frozen)
- **Pass:** "Indus tablets carry more count-like numerals than seals at the same site". A new S candidate on the scorecard after a red team (formula heads, M342/M59 dominance, chronology). Not an anchor.
- **Fail with c\* ≤ 1.0:** powered negative: "no tablet-seal gap of c\* index units or more". Claims that tablets are counting or accounting records (scorecard KM-tablets-tokens, MUK19 jar strokes) gain a sized null.
- **Kill fails or c\* > 1.0:** untestable at Indus size. Atlas entry; route closed.

## Limits stated in advance
- About 70 tablet tokens in all; the heads on tablets are few, so effective n is the number of distinct heads.
- The index pools over objects, so a head that is counted on tablets and frozen on seals gets a mixed value.
- Mohenjo-daro copper tablets have their own fixed text types (README #8). Copper repeats may look frozen by design.

## Cost
About 0.1 s per Latin draw and under a second per planted draw. Minutes in all on 4 workers under the Indus lock, with `nice -n 20` and the memory guard.
