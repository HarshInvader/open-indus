# Carver hands × text: red team (2026-11-20)

**Verdict: the POSITIVE stands only as fragile.** The sealed run printed p = 0.0098, so the sealed rule returns POSITIVE. The same code's exact p is about 0.0105, above alpha. No check reverses the direction, and none makes the result comfortably significant at 0.01.

Everything below except the sealed verdict is exploratory. Code: `experiments/carver_text/redteam/`.

## 1. Reimplementation

| Run | Observed | Null mean | p |
|---|---|---|---|
| Sealed run (10,000) | 1.193 | 0.908 | 0.0098 |
| Mine, written from the prereg text only (10,000) | 1.188 | 0.927 | 0.0182 |
| Mine, robustness (100,000) | 1.188 | 0.926 | 0.0174 (1,736 hits; 95% CI 0.0166–0.0182) |
| Replica of the sealed choices, robustness (200,000 over 3 seeds) | 1.193 | 0.907 | 0.0105 (95% CI 0.0101–0.0110) |

- **Monte Carlo error.** At 10,000 reshuffles the standard error near 0.01 is 0.001. Five 10,000-blocks of the replica gave 0.0080, 0.0103, 0.0105, 0.0115, 0.0116. A 10,000 run of the sealed code lands at or under 0.01 about 3 times in 10.
- **Why mine differs.** The prereg does not fix two choices, and both move p:
  - size-tercile ties (integer mm sizes tie often): boundary seals sent down, not up, gives 0.012;
  - the 4 seals with two ICIT rows: joining both rows, not taking the first, gives 0.014;
  - both together give 0.016–0.017.

## 2. Join and labels

- **Spot check.** 20 of 20 random linked grouped seals match the appendix for group and ICIT for CISI number and site. All 180 grouped ids match my own parse.
- **One member mis-assigned.** The appendix prints one seal of a four-seal hand under a misspelt group label. The parse keeps it as its own group, so it drops out. This is why the parse has 56 groups; the thesis text says 55. Fixed: 291 pairs, p = 0.012.
- **Missed join.** 24 of the 25 unlinked Kalibangan seals (9 grouped) match ICIT unicorn seal rows under the CISI "K-" prefix. Two seals appear under both spellings with identical attributes, which confirms the mapping. GATES calls these non-CISI numbers; they are not. With both fixes: pool 472, 49 hands, 301 pairs, p = 0.008.
- **No artificial pairs.** No ICIT row links to two seals.
- **Near-copies.** The rule excludes 0 of 289 pairs. Nothing obvious is missed: no kept pair shares half its sign types, and 3 are two edits apart.

## 3. Confounds (exploratory; base = sealed choices, 20,000 reshuffles)

| Diagnostic | Ratio | p |
|---|---|---|
| **Text length.** Grouped seals carry longer texts (5.6 vs 4.9 signs) | | |
| Strata + text-length bin | 1.15 | 0.051 |
| Reshuffle among seals in hands only | 1.21 | 0.026 |
| Site × text-length, among seals in hands | 1.26 | 0.002 |
| **Catalogue neighbours** (CISI numbers within 10; 69 of 289 pairs, score 1.46 vs 1.11) | | |
| Neighbour pairs masked | 1.24 | 0.038 |
| Neighbours masked + text-length bin | 1.10 | 0.14 |
| **Size.** 5 or 8 bins per site | 1.28 | 0.017 |
| Site only, no size | 1.41 | 0.004 |
| **Period.** Strata + ICIT period or phase (known for 128 and 243 of 450) | 1.31–1.32 | 0.007–0.009 |
| **Hands.** Leave one hand out (44 runs) | 1.27–1.37 | 0.005–0.026 |
| Three largest hands dropped (132 pairs) | 1.31 | 0.033 |
| Single-site hands (32) | 1.41 | 0.006 |
| Multi-site hands (12) | 1.07 | 0.37 |
| **Common signs.** Top 5 dropped / top 10 dropped | 1.39 / 1.59 | 0.019 / 0.006 |
| Only signs on ≤ 25 seals | 2.1 | 0.0008 |
| Same, three largest hands dropped | 1.30 | 0.21 |

- **Text length is the main confound.** Longer texts share more signs by chance, and the null draws partners from the whole pool. Adding length to the sealed strata takes p to 0.05. Other length-aware nulls give 0.002–0.026, so the answer depends on the null.
- **Findspot, lot and season cannot be tested.** The data has no such field. CISI number is the only proxy, and catalogue neighbours share more signs even outside hands (1.02 vs 0.86).
- **No single hand drives it.** Leaving one out never takes p above 0.05, but 33 of 44 leave-outs sit above 0.01. Three hands hold 57% of the excess.
- **Common signs are not the cause**, though the top 10 carry 54% of the score. The rare-sign signal is stronger, but it rests on 30 pairs in 12 hands and disappears without the three largest hands.
- **Cross-site hands show nothing** (ratio 1.07). The effect is within sites, where findspot cannot be ruled out.
- **Jamison was not blind to the texts.** The formal rule is iconographic and metric (at least 7 shared attribute styles and 5 similar proportions), and signs are left out of it. But the work was done from CISI photographs, and the group descriptions in ch. 9–11 comment on inscription length, spacing and layout, and in at least two groups on shared characters. Inscription carving style also sets the periods.

## 4. The one caveat

The sealed p crossed 0.01 by Monte Carlo luck. The same code's exact p is 0.0105, and equally valid readings of the prereg give 0.012–0.017. Report it as "p ≈ 0.01–0.02, not robust at alpha 0.01", with text length as the open confound.
