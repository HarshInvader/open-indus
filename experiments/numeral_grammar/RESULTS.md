# Grammar of the Indus number signs (Fable 5.2 plan 3, R1: the Proto-Elamite method)

2026-11-15. Pre-registration: `docs/prereg/numeral_grammar.md`. It was hash-frozen in `docs/prereg/HASHES.txt` together with `common.py`, `models.py` and `test.py` before any held-out or ICIT numeral group was read. Held-out = `dev_heldout(version=2)`. Replication = ICIT texts from sites outside the five M77 sites. Unit: numeral groups (maximal runs of adjacent number signs) in distinct texts. Ledger rows `ng_*` in `docs/test_ledger.csv`.

## Findings first

1. **The 12-sign is not a higher unit, and the system is not base 12, 8/16 or 10.** On held-out data, every unit model loses to plain tally by a wide margin:
   - **Additive base 12:** log10 LR −49.0 with 12 first, −49.3 with 12 second.
   - **Base 8/16:** −63.8.
   - **Base 10:** −62.6.

   ICIT sites outside M77 agree (−27 to −44), and no replication unit favours any unit model (0 of 4). If the 12-unit model were true, this test would have detected it (power 1.00 by simulation). The result holds with the leak set 20 times looser (base 12: −17.5) and under both other variants (connective counted as 2; tall-1 merged with short-1).
2. **Adjacent numerals are not added together.** If 12 were a unit, a short count would sit next to it. On held-out data 7 of the 8 signs next to 12 are **tall** strokes, a different class: T3+12, T1+12 (twice), T3+T3+12, 12+T1, and 1+12+T2. Restricted to groups that contain 12, the unit model still loses (log10 LR −11.2). An additive notation would also never write two short counts that one sign could hold, yet there are 15 such held-out pairs (1+4 four times, 1+3, 1+5, 3+3, 4+4, 3+4...). These groups are two numbers side by side, not one sum.
3. **"12+12" is one block of strokes, not two 12s.** All three M77 texts with M121 M121 are written by Wells as a single sign, W056:
   - Harappa seal H-14;
   - Lothal seal L-115;
   - the Kalibangan moulded tablets K-69 to 75 and K-156.

   W056 is three rows of about 7-8 strokes. The CISI photograph of K-69 shows one continuous 3 x 8 block with no gap (`cisi_K69_K70_block.png`). So the "no stroke group of 13 or more" ceiling is broken once, by a stroke field of about 21-24 on 3 distinct texts, or else this is two 12s with no space between them. Either way, it is not a 12-unit followed by a small count.
4. **The "1 + 12 = 13" lead was a fixed formula.** The dev 1+12 cases are 3 families. Five are one Lothal sealing text (M209 M343 M98 M121 M59), and two are M10 M97 M121. Held-out has no new short 1 + 12 pair (P1 untestable, n = 0).
5. **The best description (weak): two numbers side by side, with position preferences.** M5 was the only model built after seeing dev. It gives separate first- and second-position distributions. It beats tally on M77 held-out by log10 LR +3.2 (MD +1.9, Harappa +0.7, other +0.7), so it formally passes the registered rule. But it loses on the ICIT new sites (−3.3). The dev pattern behind it is short-1 coming first (21 of 25 dev pairs), and it did not confirm on held-out: 11 of 16, p = 0.105.
6. **No metrogram slot (number-unit-commodity).** Signs that dev marks as following numerals are still preceded by numerals more often than other signs on held-out (27/70 vs 14.5% base rate, p = 7e-7). Individually, though, only 2 of 10 keep a share of at least 50%. M190 holds (4/4), but it always follows short 3, so it is a fixed formula, not a unit word. The common number + X + Y frames end in the jar closer (number, head, M342), which is the seal template, not a Linear B entry. Tall and short numerals side by side have no fixed order (held-out 8 of 13 tall-first, p = 0.58).

**Bottom line for R1:** the Proto-Elamite route gives a clear negative. Indus number signs do not combine into larger numbers by any additive or unit rule we could test. Multi-sign numeral groups are rare: 7% of groups in M77 and 9% in ICIT, and only 3 of 1,065 M77 groups have more than two signs. They mix stroke classes freely and look like separate numerals placed next to each other. This agrees with the earlier findings: fixed formulas containing a numeral (pair_numeral_long, redteam_pnl), tall and short strokes as two separate classes (shaunmortal F2/F5), and 12 as a favoured top sign (numeral_class). The 12-sign is the largest stroke sign in common use, not a counting unit.

## Inventory (step 1)

- `inventory.csv`: every numeral sign in M77 and ICIT, with class, value, layout and distinct-text token count.
- `contact_sheet.png`: Mahadevan's drawings by class, plus the Wells numeral strip.
- `pairs.csv`: every adjacent numeral sequence, with counts in both corpora and examples.
- `inventory_summary.json`: summary counts.

Values were read by eye from the drawings. Corrections to `stroke_signs.json`:

- M122 is 12 in brackets (4/4/4), not 5.
- M113 is 7 in brackets (4/3).
- M101 is 2, written 1-over-1.
- M115 is 9 in one row.
- The chevrons M119/M120 are 8 (2/3/3) and 9 (3/3/3).
- M315 has 7 arcs.

| class | M77 signs (value) | distinct-text tokens |
|---|---|---|
| short | M97/98 (1), M100/101 (2), M102/103 (3), M104/105 (4), M106/107 (5), M108/109 (6), M110-113 (7), M114 (8), M115-117 (9), M118 (10), M121/122 (12). No 11 | 1: 157, 2: 28, 3: 114, 4: 53, 5: 33, 6: 31, 7: 68, 8: 7, 9: 4, 10: 1, 12: 53 |
| connective | M99 (two short strokes) | 547 |
| tall | M86 (1), M87 (2), M88/89/92/93/94 (3), M95 (4), M96 (5) | 133 / 248 / 182 / 9 / 16 |
| chevron | M119 (8), M120 (9) | 3 / 2 |
| arcs | M312-M315 (1, 2, 3, 7) | 2 / 2 / 1 / 1 |
| Wells only | W025-W028 dotted 5-8; W036/W037/W039 tall 6-8; W056 3-row block of ~21-24 | 1-6 each |

Group lengths (distinct texts):
- M77: 985 single, 77 pairs, 3 triples.
- ICIT: 1,339 single, 132 pairs, 11 triples.

Most common sequences (M77 / ICIT):
- T3+T3: 6 / 9
- S1+S3: 5 / 9
- S1+S4: 5 / 6
- S1+S12: 7 / 2
- T3+T2: 4 / 5. These are mostly the title block M336 M89 followed by tall 2.
- T3+S7: 4 / 4. All of these are M336 M89 followed by M112 M194.

Several "pairs" are therefore a title block next to a numeral formula, not one number.

## Pre-registered tests

| id | prediction | result | verdict |
|---|---|---|---|
| T1 M2a | base-12 unit, big first, beats tally by log10 LR ≥ 1 with ≥ 3/4 units | −48.98; units 0/4 | **refuted** |
| T1 M2b | same, small first | −49.26; 0/4 | **refuted** |
| T1 M3 | base 8/16 | −63.81; 0/4 | **refuted** |
| T1 M4 | base 10 | −62.63; 0/4 | **refuted** |
| T1 M5 | ordered juxtaposition (dev-derived) | +3.22; 3/4 (ICIT −3.29) | formal pass, weak |
| T2 | groups with 12 follow the unit grammar | M2a −11.2, M2b −11.5 (n = 7) | **refuted** |
| P1 | order of 12 + short count is fixed | 0 eligible pairs | untestable |
| P2 | partners of 12 are short 1-11 | 7/8 are tall | **refuted** |
| P3 | no single group ≥ 13 | W056 on 3 distinct texts (= M77 "12+12") | violated (reading-dependent) |
| P4 | counts next to 12 differ from stand-alone counts | n = 1 | untestable |
| P5 | no short+short pair with sum ≤ 12 | 15 pairs | **refuted** |
| P6 | short-1 is a prefix (≥ 75% first) | 11/16, p = 0.105 | not confirmed |
| C1 | short/tall pairs have a fixed order | 8/13 tall-first, p = 0.58 | **refuted** |
| C2 | dev numeral-bound signs stay ≥ 50% numeral-preceded | pooled 27/70 (p = 7e-7), but 2/10 signs individually | weak: no unit class |

Twelve confirmatory tests, Bonferroni alpha 0.0042. None of the refutations depends on a p-value: each is a likelihood loss of 11 to 64 log10 units, or a count that contradicts the model outright.

## Power and caveats

- **Power.** T1 power is 1.00 for M2a and M2b (2,000 simulations at the observed group counts per unit). T2 power is 1.00 at n = 7. P1 had no eligible pairs. With 25 multi-sign held-out groups and 14 at the new ICIT sites, finer claims are not testable: whether short-1 is a prefix, or whether partner distributions differ.
- **The leak setting doesn't matter.** Strict unit grammars lose mostly through pairs they forbid, so the size of the loss depends on the leak e. At e = 0.2 they still lose by 17-22 log10 units. They cannot win, because the pairs they allow are a small minority of what occurs.
- **Values and segmentation.** These come from drawings and two sign lists (Mahadevan, Wells), so the values carry their errors. The 12+12 vs W056 question is a segmentation call; a higher-resolution photograph of H-14, L-115 or K-69 would settle it.
- **Short-1 vs tall-1.** These differ only in length, so 1+12 and T1+12 may be the same thing. Merging them changes nothing (base 12 still loses by −44 to −48).
- **Same objects.** ICIT at the old sites is mostly the same objects as M77, so only the new-site ICIT texts count as replication. They have few groups.

## Hypotheses

| hypothesis | verdict |
|---|---|
| 12-sign is a higher unit (dozen/bundle) in an additive system | **refuted** |
| Adjacent numerals combine additively (12 + n, or n + n) | **refuted** |
| Weight-like base 8/16 | **refuted** |
| Base 10 | **refuted** |
| Plain tally with a 12 ceiling | best of the registered four. Its ceiling is broken once if W056 is one sign |
| Two numbers side by side, short-1 first | weak / not confirmed |
| Tall + short form one compound number with fixed order | **refuted** |
| A unit/metrogram sign follows numeral groups | **refuted** (only fixed formulas such as 3 + M190) |

## Next experiments

1. Settle W056: a high-resolution photograph of K-69 to 75 or H-14 (`docs/HUMAN_LEADS.md`). If it is one block of 24, it is the only stroke group above 12 in the corpus, and it occurs only in one formula (M171 M123 M67 M348 M342 / M336 M197 / M99 M172 M304 M307). Freeze as a prediction: no new 13+ stroke block outside these formulas.
2. Freeze as new-finds predictions:
   - no short 2-11 directly next to a 12 in the short class;
   - no additive short+short pair rule.
3. Close the numeral-arithmetic route. No summation structure exists (no totals, no bundling), so the Proto-Elamite method has nothing to work on in this corpus. Numerals should now be treated as parts of fixed formulas.

## Files

- **Code:** `common.py` (inventory, groups), `explore_dev.py` (dev discovery), `models.py`, `test.py dev|heldout`, `sens.py`, `inventory.py`.
- **Logs:** `explore_dev.log`, `test_dev.log`, `test_heldout.log`, `sens.log`.
- **Outputs:** `test_heldout.json`, `sens.json`, `results.json`, `inventory.csv`, `pairs.csv`, `contact_sheet.png`, `cisi_K69_K70_block.png`.
