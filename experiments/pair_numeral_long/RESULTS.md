# Pair graph, numeral distributions, long texts (Fable 5.2 plan F1, F2, F6)

2026-11-14. Pre-registration: `docs/prereg/pair_numeral_long.md` (hash-frozen in `docs/prereg/HASHES.txt` before any held-out text was read; the code was dry-run on a dev-only split first). Held-out = `dev_heldout(version=2)`. Unit: distinct texts. Ledger rows `pnl_*` in `docs/test_ledger.csv`.

Code (run from repo root): `common.py`, `f1_pairs.py dev|heldout`, `f1_sensitivity_dev.py`, `f2_numerals.py dev|heldout`, `f6_long.py dev|heldout`. Outputs: `f1_dev.json`, `f1_sensitivity_dev.json`, `f1_ref_small_n.json`, `f1_heldout.json`, `f2_dev.json`, `f2_heldout.json`, `f6_dev.json`, `f6_heldout.json`, the `*_heldout.log` files and `results.json`.

## Findings first

1. **F1: name-core pairs come from one inventory, not two.** Signs do not split into "first" and "second" sets. 80% of held-out signs (degree 3 or more) appear in both positions. The polarization excess is +0.075 (95% CI -0.05 to +0.21; orientation null p = 0.11).
   - Real two-inventory name systems at the same size score much higher: Chinese clan + given 0.85, Ur III 0.74, Sanskrit 0.60 (5th percentiles 0.71 / 0.61 / 0.36).
   - There is no blazon-type alternation either (max-cut excess +0.05, swap-null p = 0.20).
   - A sign's position preference barely predicts the order of new pairs: 62/106 = 0.585 (CI 0.49-0.67), against 0.83-0.95 in the two-inventory references.
   - Together with core_semantics (91% fixed order per pair), this points to **compounding**: one stock of word-signs, each pair lexicalised in its own order. Emblem x individual, and modifier x head with fixed classes, are **refuted** at the strength real two-slot naming systems show.
   - Caveat: Chinese two-character given names (one inventory, weak lean, 0.23 [-0.03, 0.44]) are *not* excluded, and neither is a weak minority of two-slot pairs (a simulated 25% mixture gives 0.13).
2. **F2: most numeral + sign combinations are frozen number-names, a few are counts, and none are calendrical.**
   - **Lexeme-like:** one numeral value dominates. Examples: tall 2 + M59 fish (65/71), tall 3 + M211 (39/41), tall 2 + M60/M244/M284, short 7 + M194/M197 (100%), short 3 + M190/M403 (100%), short 3 + M15, short 1 + M25. On held-out data, dev lexeme heads kept their value in 29/40 cases (0.725, CI 0.57-0.84) against 0.33 expected (p = 5e-5).
   - **Count-like:** the value spreads over 3-9 values. Examples: short + M162 (3-8), short + M169 (1-9), tall + M328 (1-4, the docket unit). On held-out data these heads took their dev modal value only 10/25 times (Fisher vs lexemes, p = 0.0096). So **M162, M169 and M328 are the best candidates for counted things (commodities or units)**. The rest are name or title elements with a fixed numeral.
   - **Short M59 (3, 6, 12, 4) and the jar M342 (7 or 12)** sit in between: a few favoured values. Jar after short strokes was 7 or 12 in 4/4 held-out cases (p = 0.004, n tiny).
   - **No sign has a near-uniform distribution up to a cap**, so there is no Mixtec-style calendar naming. The only recurring cap is 12 (M59, M342), and 12 is the largest single short-stroke sign, so it reflects the limit of the notation, not a cycle. This failed the registered clause "no shared cap", but the failure does not mean what a calendar would need.
3. **F6: long texts are one extended seal template. They are neither strings of labels nor new syntax.**
   - Held-out texts of 10+ signs (n = 21) parse in full 67% of the time. Concatenated short texts parse 21% of the time and shuffles 17% (p = 0.001).
   - "Closer, then restart" boundaries are rare inside a line: 0.22 per 10 signs vs 0.89 for label lists (p = 0.001). The six long ICIT texts from new sites agree: 0.15 vs 0.94.
   - Long texts show *fewer* reversed and novel sign pairs than label lists (reversed 0.022 vs 0.064; novel 0.39 vs 0.54). So there is no sign of new ordering beyond the short template.
   - Long-text acceptance (0.67, CI 0.43-0.86) cannot be told apart from short-text acceptance (0.81). Any template residue is too small to detect with n = 21.

## Pre-registered tests (12)

| id | prediction | result | verdict |
|---|---|---|---|
| F1-T1 | POL excess (2-sign cores) < 0.30, CI upper < 0.50 | +0.075 [-0.048, +0.214], n = 160 types | pass |
| F1-T2 | max-cut excess < 0.10, p > 0.0167 | +0.046, p = 0.20 | pass |
| F1-T3 | order-rule accuracy Wilson upper < 0.83 | 0.585 [0.49, 0.67] | pass |
| F2-N1 | lexeme heads keep dev value, share ≥ 0.6, p < 0.0125 | 29/40 = 0.725, p = 5e-5 | pass |
| F2-N2 | count heads spread: modal share < 0.6 and < N1, p < 0.0125 | 10/25 = 0.40, p = 0.0096 | pass |
| F2-N3 | no calendar-like head; no shared cap in {7, 12, 13, 20} | 0 calendar-like; cap 12 shared by 2 heads | **fail** (cap clause; notation ceiling) |
| F2-N4 | jar after short strokes in {7, 12} ≥ 0.6, p < 0.0125 | 4/4, p = 0.0044 | pass (n = 4) |
| F6-L1 | long texts parse more than concatenations | 0.667 vs 0.214, p = 0.001 | pass |
| F6-L2 | fewer label boundaries | 0.224 vs 0.886, p = 0.001 | pass |
| F6-L3 | residue: long acceptance CI upper < short rate | 0.857 vs 0.805 | **fail** (power) |
| F6-L4 | more reversed bigrams than label lists | 0.022 vs 0.064 (opposite direction) | **fail** (expected from dev) |
| F6-L5 | more novel bigrams than label lists | 0.392 vs 0.543 (opposite direction) | **fail** |

That gives 8 of 12 passes. F1 supports compounding. In F2, the count / number-name split is supported and calendar naming is not. In F6, the long texts look like one extended template, and syntax beyond the template is not supported.

## Details and caveats

**F1.**
- *Pairs:* adjacent signs inside cores (frozen typology / core_semantics definition), counted once per distinct text. Metrics use distinct pair types.
- *Nulls:* orientation randomised per pair type (for POL), plus directed and undirected degree-preserving edge swaps (for di-cut and max-cut).
- *Dev sensitivity:* the result holds under loose cores, whole-text pairs, and whole-text pairs with function signs removed. In those three settings POL excess is +0.08 to +0.12, about 0.9 of signs appear in both positions, and max-cut excess is about 0.
- *Planted controls at matched n:* POL excess recovers the known two-slot structure in Chinese clan+given (0.85), Ur III (0.74) and Sanskrit (0.60). It gives about 0 for simulated one-inventory compounding. Simulated blazon is caught by max-cut (+1.0), not by POL.
- *Power:* at held-out n, POL separates Indus from clan+given, Ur III and Sanskrit, but not from Chinese given names.
- *Small lean:* the pooled data show a small but real positional lean (+0.074, p = 0.003), driven by fish-first pairs (see core_semantics).

**F2.**
- *Values:* the stroke count of the numeral sign directly before the head. Short 2 = M100 only, because M99 is the connective.
- *n is small:* held-out has about 40% of dev's numerals. Several lexeme heads (M197, M403, M211) have no held-out tokens.
- *M287 is bimodal:* short 3 in dev (13/15), short 5 in held-out (7/10). All the 5s are one family, "M106 M287 M342", which the v2 family split put entirely in held-out. M287 is either two fixed compounds or a counted item with a few favoured values. Treat it as unresolved.
- *Layout:* as STATE F7 found, the modal value is usually tied to one particular numeral sign (for example M112, the 4-over-3 layout of 7, before M194/M197). "Number-name" therefore means numeral sign + head as a unit.
- *Caps 13 and 20:* these can't be written with one stroke sign, so this design cannot detect them.

**F6.**
- *Long texts:* 10 or more signs, or multi-line with 8 or more. There are 47 in dev and 21 in held-out, mostly seals.
- *Grammar:* the frozen functional grammar, fit on dev.
- *Nulls:* the label-list null rebuilds each line from whole short held-out texts.
- *Reference:* we did not build heraldic, khipu or Linear B long-entry references. The concatenation null is the simulated label list.
- *Breaks:* lines are parsed separately, so multi-line texts that join two templates across a line break count as parsed. Part of what looks like long-text integration may be line-level layout.

## What this opens and closes

- **Closed:** the idea that seal texts are emblem (clan/office) + individual pairs, or fixed modifier + head slots. Also calendrical naming of the Mixtec "8 Deer" type, and the reading of long seals as concatenated labels.
- **Narrowed:** name cores are compounds of one word-sign stock. Long seals are the same template, extended. Neither supplies new syntax to work with. This supports the earlier verdict that the seal genre is too formulaic for internal language-vs-code tests.
- **Opened:**
  - (a) The counted-item set {M162, M169, M328} (and maybe M287) as commodity or unit words. Test them against object metrology (plan F10) and against which signs appear on sealings that travelled.
  - (b) The frozen number-names list (tall 2 + M59/M60/M244/M284, tall 3 + M211, short 7 + M194/M197, short 3 + M190/M403/M15) as lexical items. Hash it as predictions for new finds.
  - (c) Plan F11 simulation: test whether Chinese-given-name-like one-stock compounding versus Sangam- or gotra-type naming can be told apart at all.
