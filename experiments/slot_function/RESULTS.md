# slot_function: results

Prereg `docs/prereg/slot_function.md` (sha256 23d68e8a...), code `sf.py` (16280b7f...), both hashed 2026-11-18T22:09Z before any real outcome. Board #50. Raw output in `out/`.

## Verdicts

| Test | Gate | Real result | Verdict under the sealed rules |
|---|---|---|---|
| A1 last slot vs first slot | **failed** (77/100, bar 80) | ICIT AUC 0.771 vs 0.714, diff +0.057, 95% CI 0.035 to 0.080 | **UNTESTABLE** (lead) |
| A2 last slot vs shuffle null | same gate | ICIT p = 0.005 (null 95th pct 0.722); M77 held-out p = 0.018 | **UNTESTABLE** (lead) |
| B1 numerals before human figures | **failed** (79/100, bar 80) | Held-out ratio 0.98, p = 0.47 | **UNTESTABLE**, and null anyway |
| B2 human figures commoner on tablets | none | MH odds ratio 1.14, p = 0.22 (bar 1.5, p < 0.05) | **WEAKENED** by the rule; in practice null |

The script printed "SUPPORTED" for A because it does not apply the gate to its own verdict. The prereg does: a failed gate makes A untestable. We report it that way.

## Test A in detail (which slot carries the seal vs label signal)

- ICIT, 1,232 seals vs 509 labels (tablets, tags, rods, bangles, pots), 5-fold CV:
  - last sign alone: AUC 0.771
  - first sign alone: AUC 0.714
  - bag of middle signs: AUC 0.780
  - text length alone: AUC 0.672
- M77, fit on dev, scored on held-out (276 seals vs 32 labels):
  - last sign: 0.741
  - first sign: 0.698
  - middle: 0.712
  - length: 0.685
  - The difference is +0.043, the same direction as ICIT, but its CI (−0.023 to 0.104) crosses 0.
  - The last sign beats a within-text shuffle (p = 0.018).
- The planted check is specific but slightly underpowered:
  - With the plant in the first slot, the rule fired 0/100 times.
  - On unplanted shuffled data, it fired 1/100 times.
  - A last-slot plant on 15% of labels fired 77/100 times. The bar was 80.
- What it would mean if it holds: the last sign tells you more about the object type than the first sign does, and more than a random sign of the same text. This fits the old closer/terminal-marker idea (Rao 2018; Born et al. 2022 for header slots in Proto-Elamite). It does **not** show that the signal sits only at the end: the bag of middle signs predicts as well as the last sign.
- Status: a lead. Both corpora have now been used, so a confirmation needs new texts, for example CISI vol. 3 or new finds. Rerunning the same data under a looser gate would not count.

## Test B in detail (Rao 2018: human-figure signs as counted kinds of people)

- B1, held-out M77: 14.5% of human-figure tokens follow a numeral, against 14.9% for frequency- and position-matched control signs. That is no effect.
- Exploratory sub-class: figures holding an object (M18-M46), on dev only, ratio 1.86, p = 0.065. It does not replicate on held-out (ratio 1.14, p = 0.36).
- B2, ICIT: human-figure signs make up 5.7% of tablet tokens and 5.3% of seal tokens, MH odds ratio 1.14, p = 0.22. M77 points the other way (5.1% on miniature tablets vs 6.5% on seals).
  - Caveat: only 15 Wells signs map to M1-M46 through the bridge, so ICIT coverage of the human-figure class is partial.
- Conclusion: the open corpora show no sign that human-figure signs behave like counted nouns. Goes to the negative atlas.

## Deviations

- None from the prereg. The gate-B and gate-A misses are reported as the rules require, not re-run with other settings.
