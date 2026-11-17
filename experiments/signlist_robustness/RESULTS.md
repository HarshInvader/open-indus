# Do the ranked findings survive other sign lists?

Pre-registration: `docs/prereg/signlist_robustness.md` (hash-frozen in `docs/prereg/HASHES.txt` before any variant was run). Code (run from the repo root):
- `variants.py` builds the sign lists (`variants.json`)
- `harness.py [variant ...]` runs every test (`raw/<variant>.json`)
- `summarise.py` builds `table.md`, `grid.md` and `results.json`

The ledger has 108 rows (`slr_*`, mode `robustness`).

## Findings first

1. **No ranked finding collapses.** Across 12 alternative sign lists, every test kept its direction. Wherever a test failed its pre-registered bar, the effect was still clearly present.
2. **Robust under every sign list** (type unit):
   - **#1 order beats permutations:** 13/13 lists. Worst is the coarsest image list, 31% vs 5.5% chance.
   - **#6 object-type registers:** 13/13. Every class is above its permutation null; mean AUC is 0.70-0.75.
   - **#10a name cores are 1-2 word signs:** 13/13. Len-1 share is 0.32-0.44 and standalone share 0.80-0.89, against a bar of 0.28 / 0.22.
   - **#9 functional parse beats shuffle:** 13/13. Under coarse lumping the margin over shuffle shrinks from 0.35 to about 0.22.
   - **#11 fish lexical class:** passes wherever it is testable. It is not testable where the fish are lumped into one sign.
3. **These findings do NOT survive every list** (verdicts follow the pre-registered rules):
   - **#3 Ticked fish to the final slot: SENSITIVE on types, FRAGILE on tokens.**
     - The effect size never changes: 0.54-0.63 final vs 0.06-0.15 for plain fish, in every list.
     - The p-value misses 0.05 in three places: lump_fish (p = 0.09), lump_all on tokens (p = 0.07), and ICIT on tokens (31/57 final, p = 0.09).
     - Why: when the 5 ticked fish become one label, the frequency-matched null draws one random sign, not five. Single signs vary much more, and closer-like signs often sit last. So this is lost power, not lost effect. By the frozen rule it still counts as a failure.
   - **#5 M109 + M59: SENSITIVE.** It fails only under lump_all: 7/32, p = 0.025.
     - That list merges two-tier six with three (M102, M103, M108, M109; the unified cluster W16) and all plain fish into one sign. The test then becomes "any 3-or-6 + any fish".
     - It survives lumping six-by-value (M108 = M109) and lumping all fish. So the claim needs 6 kept apart from 3, which every real list does.
   - **#7 L-R reversals: SENSITIVE.**
     - ICIT on types: 19/23 = 0.83, p = 0.0013, just short of p < 0.001. It passes on tokens: 23 copy-free lines.
     - lump_all on tokens: 26/34, p = 0.0015.
     - The share stays at 0.77-0.94 everywhere. These are small-n p-value misses.
   - **#10b fixed pair order: SENSITIVE.**
     - Under the two coarser image lists, held-out agreement is 0.736 and 0.705 (bar 0.75), though still far from free order (p < 1e-5).
     - Merging drawings that look alike blends pairs that have different orders. So "91% fixed" is partly a property of Mahadevan's fine splits.
4. **The Parpola test is weak.** A free Mahadevan-Parpola concordance was not found online; the one known table is in Fuls 2023, behind a paywall.
   - I aligned 150 CISI Mohenjo-daro seals (Parpola codes) with ICIT. That gives 598 tokens and 108 M signs, at 92% purity.
   - Parpola differs from Mahadevan on only one of those signs: he lumps M287 with the opener M293.
   - So "survives Parpola" means only that his list matches Mahadevan's on the frequent seal signs.
5. **Types vs tokens.** Keeping mould duplicates changes no conclusion. On tokens #3 gets weaker (ICIT and lump_all fail), and #10b gets stronger (0.85 vs 0.79 on M77).

## Table: survives? (type / token)

Y = meets the pre-registered bar; N = fails; NT = not testable, because the list erases the contrast by definition. Full statistics and p-values for every cell are in `table.md`; machine-readable values are in `results.json`.

| finding | M77 | ICIT | parpola | lump_fish | lump_numerals | lump_jar_man | lump_all | split_s1 | split_s2 | split_s3 | img_hi | img_mid | img_lo | verdict (type) | verdict (token) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T1 order beats permutations (#1) | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | ROBUST | ROBUST |
| T2 ticked fish -> final slot (#3) | Y/Y | Y/N | Y/Y | N/N | Y/Y | Y/Y | Y/N | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | SENSITIVE | FRAGILE |
| T3 M109+M59 fixed (#5) | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | N/N | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | SENSITIVE | SENSITIVE |
| T4 object-type registers (#6) | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | ROBUST | ROBUST |
| T5 L-R reversals (#7) | Y/Y | N/Y | Y/Y | Y/Y | Y/Y | Y/Y | Y/N | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | SENSITIVE | SENSITIVE |
| T6 name cores 1-2 word signs (#10a) | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | ROBUST | ROBUST |
| T7 fixed pair order (#10b) | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | N/Y | N/N | SENSITIVE | ROBUST |
| T8 fish lexical class (#11) | Y/Y | Y/Y | Y/Y | NT/NT | Y/Y | Y/Y | NT/NT | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | Y/N | ROBUST | ROBUST |
| T9 functional parse vs shuffle (#9) | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | Y/Y | Y/N | ROBUST | ROBUST |

Key type-unit numbers, M77 → worst list:

| Test | M77 | Worst list |
|---|---|---|
| T1 order beats permutations | 0.40 vs 0.057 | img_lo: 0.31 vs 0.055 |
| T2 ticked fish final | 11/19 vs plain 0.07 | ICIT: 29/48 vs plain 0.15 |
| T3 M109 + M59 | 7/10 vs 0.031 base | lump_all: 7/32 vs 0.093 base |
| T4 registers, mean AUC | 0.75 | 0.70 |
| T5 L-R reversals | 31/34 | ICIT: 19/23 |
| T7 fixed pair order | 0.79 | img_lo: 0.705 |
| T8 fish class | 3/3 tests pass | img_lo: 2/3 |
| T9 parse vs shuffle | 0.75 vs 0.40 | img_lo: 0.83 vs 0.60 |

## The sign lists

Each list is given as its number of labels in M77, with M77 itself at 417.

| List | Labels | What changes |
|---|---|---|
| ICIT | own corpus, 5,679 texts | Wells numbering. Wells splits much more finely (e.g. one-row vs two-tier numerals, many fish variants). |
| parpola | 416 | See finding 4. |
| lump_fish | 402 | 12 plain fish become one sign; 5 ticked fish become one sign. |
| lump_numerals | 403 | Strokes lumped by system and value, so M108 = M109. |
| lump_jar_man | 378 | Jar M342 = M343-M345; man, bearer, man+stick, man+jar and bird groups. |
| lump_all | 309 | All of the above, plus trees, rakes, ovals, leaf-in-oval, arcs (M293 = M287), U-cups, M347/M348, and the shaunmortal Mahadevan-Wells unified clusters. |
| split_s1-s3 | +67 signs split | The 67 signs with 50 or more tokens each split, token by token at random, into 2-3 allographs. |
| img_hi / mid / lo | 360 / 300 / 240 | Average-linkage clusters of Mahadevan's drawings. They are sensible: jar with jar+strokes; plain fish M59/M70/M72 apart from ticked M60/M71/M73. At the coarsest cut M267 merges with 9 other diamonds and M391 with 9 ovals. |

## Method notes and caveats

- **Harness check.** The test logic was reused from earlier experiments (revalidate, r8_direction, fr.Grammar, h3_confirm/s2_classes); sign identities pass through a Variant object.
  - On M77, T1-T5 reproduce the published numbers exactly.
  - The reimplemented core extraction gives HD3 85/107 = 0.79 (published 115/138 = 0.83) and len-1/standalone 0.39/0.84 (published 0.34/0.80).
  - The parse rate is 0.75 vs 0.40 shuffled (published 0.76 vs 0.33). The shuffle rate differs, likely because shuffles here are seeded differently.
- **Sign-specific tests.** A test is NT when the list puts signs from both sides of a contrast in one label. For random splits, the target set is the union of allographs.
- **Lexicon roles** for a lumped label are the union of its members' hand roles. That makes parsing easier for shuffles too, which is why the T9 margin shrinks under coarse lumping.
- **Held-out splits.**
  - M77 lists keep the v2 split. Held-out texts that become identical to a dev text after lumping are dropped (`ho_dropped_as_copies` in results.json).
  - ICIT uses its own family split: edit-1 clusters, 75/25, seed 0. ICIT has no completeness flags, so fragments are included.
- **Data limits.** ICIT is mostly a second transcription of the same objects, so it is an independent sign list, not independent data.
- **Not tested:** #2 (sign count), #4 (Gulf), #8 (copper types). The image clustering uses one simple feature set (blurred silhouettes), not a learned similarity.

## Hypotheses tested

| Hypothesis | Verdict |
|---|---|
| #1, #6, #9, #10a, #11 are artefacts of Mahadevan's sign list | refuted (robust under all 12 lists) |
| #3, #5, #7, #10b are artefacts of the sign list | refuted as artefacts; but each misses its bar under 1-2 list families (#3 under 3 on tokens): sensitive |
| Parpola's list changes the results | untestable beyond the 108 seal signs covered; no difference there |

## Next experiments

- Get Fuls 2023 *A Catalog of Indus Signs* (it has M and P concordances) to build a full Parpola list.
- Re-run T2 with a null that respects the number of members in a lumped label, i.e. draw 5 signs and merge them. This is exploratory, because the frozen null is what failed.
- Make the image-cluster list from CISI photographs rather than Mahadevan's normalised drawings.
