# Detached signs: a layout class, but not a class apart from the text

2026-11-14. Pre-registered in `docs/prereg/detached_signs.md`. The prereg was hashed with `ds_lib.py`, `d1_detach.py`, `d1_detach.json`, `d2_covariates.py` and `d3_inline.py` (tag `detached_signs` in `docs/prereg/HASHES.txt`) after the layout step and before any covariate or slot test was run. Ledger rows are `ds_*` in `docs/test_ledger.csv`.

## Findings first

1. **Detachment is real, and it holds out of sample.** Some signs stand alone on a line far more often than their frequency predicts.
   - The class was defined on dev only (BH q < 0.05 over 112 signs, plus p < 0.05 within multi-line texts). It is **M242, M374, M93, M326 and M393**.
     - M242: 8 of 22 dev tokens stand alone, against 0.11 expected (p = 7e-14).
     - M374: 5 of 5 stand alone (p = 3e-12).
   - Held-out families: 5 of 17 class tokens are detached, against 0.09 expected (p = 8e-9). The sign-level picture is mixed:
     - replicate: M374 2/2, M393 2/2, M242 1/4;
     - do not replicate: M93 0/2, M326 0/6.
   - ICIT-only texts (no match to any M77 text): 3 of 39 detached, against 0.15 expected (p = 4e-4). W621 (= M242) is 2/7.
   - The firm core is **M242, M374 and M393**.
2. **The detached sign is the end of the text, not something outside it.** This is exploratory and was found post hoc.
   - Every detached core token sits on the **last** line: M242 9/9, M374 7/7, M393 4/4.
   - When M242 is written inline, it is the last sign in 11 of 14 single-line texts. Twenty frequency-matched signs would give 1.86 (p = 6e-8).
   - M393 is last in 2/2. M93 is last in all 4 of its inline cases inside multi-line lines. M374 never occurs inline in M77 (0/7).
   - So "detached" mostly means **a final sign given its own line**. That is a layout habit for closing signs. It does not show a separate emblem-like field.
   - Counterpoint: in ICIT-only texts W621 is last in 2/4 inline cases and medial in 2. W790 is spread across slots, but it also lumps in the diamond M261.
3. **No non-textual covariate on the clean (confirmatory) data. Verdict: INCONCLUSIVE, because of low power.**

   | test | set | result | p (control signs) | Holm | power |
   |---|---|---|---|---|---|
   | H1 scene vs animal field | M77 held-out | 0 carriers on scenes vs 0.09 exp | 0.45 | 1 | 0.09 |
   | H1 | ICIT-only | 0 vs 0.0 | 0.90 | 1 | 0.74* |
   | H2 object type | M77 held-out | 14/16 seals, as expected | 0.44 | 1 | 0.03 |
   | H2 | ICIT-only | G = 6.4 | 0.60 | 1 | 0.01 |
   | H3 material | ICIT-only | steatite 13 vs 12.3 | 0.94 | 1 | 0.08 |
   | H4 seal size | ICIT-only | +0.02 log-area (7 seals) | 0.46 | 1 | 0.32 |

   - *The H1 ICIT power figure is not meaningful. The control null's 95th percentile is 0, so a single planted hit counts as detection.
   - Carriers are ordinary seals in the expected proportions. All six tests are stratified by site × length × multi-line, and the null is 2,000 sets of frequency-matched non-class signs.
4. **Overlap with earlier leads.** Removing the shared objects removes the signal, so the earlier leads were not reconfirmed here.
   - **Removed from the confirmatory sets:**
     - every ICIT `BNGL` row, which was the discovery data for the oval;
     - all 408 objects in the scene_text coded catalogue, plus its 5 W621 scene-seal hits (M-295, M-296, M-306, M-310, M-1186);
     - M77 held-out texts with M242 on a scene seal (the logograms objects).
   - After removal, only 8 (M77 held-out) and 5 (ICIT-only) scene seals remain. Bangles cannot be tested at all.
   - **With the shared objects kept (exploratory only):**
     - scene preference: M77 all 7 vs 4.05 (p = 0.06); ICIT-only 1 vs 0.15 (p = 0.02);
     - bangles 5 vs 0.91 in all-ICIT object type (p = 0.07).
   - These are the old leads seen again. They are not new evidence.
5. **Co-occurrence: no information.** One text carries two class signs (M326 + M93), against 0.89 expected (p = 0.60). The null expects fewer than one such text, so avoidance cannot be tested.

**Plain reading.** Line layout does pick out a few signs, mainly M242, M374 and M393, that scribes often set on a line of their own. But the main one, M242, is otherwise a regular text-final sign. The class does not follow object type, material, seal size or scene imagery once the objects behind the earlier leads are removed. The data cannot separate "a determinative or emblem" from "a closing sign that gets its own line on roomy faces". The second is the simpler account.

## Hypotheses

| id | hypothesis | result | verdict |
|---|---|---|---|
| L1 | Some signs are detached beyond line-length chance (dev) | 5 signs, q < 0.003 | supported |
| L2 | Detachment replicates (held-out, ICIT-only) | pooled p = 8e-9 / 4e-4; M93 and M326 fail alone | supported for the core (M242, M374, M393) |
| H1-H4 | Class tied to scene, object type, material or size beyond frequency (overlap removed) | 0/6 tests, all Holm p = 1 | inconclusive (power ≤ 0.32) |
| S1 | Class signs never appear inline | M242 inline 17/26 tokens, M326 mostly inline; M374 never | refuted except for M374 |
| S2 | Inline class signs take an ordinary slot | M242 text-final 11/14 vs 1.86 | refuted: they take the final slot (exploratory) |
| S3 | Class signs co-occur / avoid each other | 1 vs 0.89 | untestable |

## Caveats

- The class was defined from `|` in M77. line_breaks showed that `|` mixes true wraps with editorial line splits, so "detached" inherits that noise.
- M93 and M393 have no Wells counterpart, so the ICIT tests use only W621, W790 and W384. W790 also covers the diamond M261, which dilutes the oval.
- I saw the scene_text, logograms and bangle results before freezing the prereg. That is why the confirmatory sets exclude those objects.
- Findings 2, 4 (overlap kept) and 5 are exploratory, and the slot result was noticed after the d3 run. Treat finding 2 as a lead with p = 6e-8 on 14 tokens from one site (Mohenjo-daro).
- Carriers are few: 16 in M77 held-out and 29 in ICIT-only. A real odds-ratio-3 effect would be missed more than 90% of the time on H2 and H3.

## Next experiments

- Check whether other closers (M211, M176, M342) are also set on their own line on large faces, beyond what face size predicts. If they are, detachment is a layout rule for closers and not a sign class. The current dev data give M342 2/776 detached, which argues for a specific habit for M242, M374 and M393.
- Recode face position from CISI photos for the core signs: is the sign under the animal, or in the text band? This needs the hi-res scans in HUMAN_LEADS.
- The covariate test can only be re-run with new scene seals and bangles (CISI vol. 3, Fuls 2023).

## Files

- `ds_lib.py`: helpers (detachment flag, ICIT-only filter).
- `d1_detach.py` → `d1_detach.json`: the layout step.
- `d2_covariates.py` → `d2_covariates.json`, `d2.log`: the confirmatory covariates plus the exploratory runs.
- `d3_inline.py` → `d3_inline.json`, `d3.log`: inline slots, co-occurrence, and a catalogue of the class tokens.
- `results.json`: the key numbers.
