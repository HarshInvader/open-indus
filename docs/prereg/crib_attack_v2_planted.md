# Pre-registration: crib attack v2, planted gate at the real sample size (board task #26, H10)

Written 2026-11-17 before any grid result was seen. Method validation only: NO Indus sign sequence is read; the only real-corpus input is the list of TEXT LENGTHS (n_legible) of the foreign objects (experiments/foreign_corpus/foreign_corpus.csv) and of the 8 home round seals named by #23. Code: experiments/crib_attack_v2/{names2.py, method.py, run_grid.py} (hashed with this file). A 4-search timing probe (`run_grid.py --time`) was run before writing this; its outputs are not used.

## Method (frozen)
- **Script model.** CV syllabary (spelling rule copied from #3: clusters/codas dropped or echo-voweled), values = all CV values of every list used, plus 12 Zipf frame signs and 40 logograms. Name text: one planted name spelled in CV, each name sign misread (random sign) with p = 0.2; rest of the real length filled with frame signs. 25% of texts carry no name. Planted names are drawn uniformly from the attacker's list (attacker list contains every true name: most favourable case).
- **Name lists (attacker).** Capped at <= 200 CV spellings (2-6 signs), names taken in file order: elamite30 (short_Elamite_core capped at 30 spellings), gulf (short_gulf_core, 66), elamite (short_Elamite_core, 81), akkadian (short_Akkadian_top150, 198), sumerian (short_Sumerian_top150, 200). Wrong-language plant source: short_Amorite_top150 (200 spellings).
- **Score E** = number of texts containing an exact full spelling of >= 3 signs from the list. Search: simulated annealing on E (constructive "make this window read as this name" moves + random un-assign), 3 restarts, 1500 + 60n iterations each.
- **Anchors** a in {0, 3, 6}: the a most frequent syllabic signs of the planted corpus fixed to their true values (in all three conditions; for shuffles, taken from the corpus before shuffling). Optimistic: real anchors would be fewer and less certain.
- **n and lengths.** n = 9 (readings_check 'yes' set), 11 (+SUSA-01, LURISTAN-01), 20 (random 20 of the 41 legible lengths, per run), 41 (all foreign texts with >= 2 legible signs), 49 (41 + 8 home round seals). Real lengths are mostly 2-5 signs; texts of 2 signs cannot score.
- **Conditions per cell (list x n x a):** planted (20 runs), wrong-language planted with Amorite names (10 runs; cut from 20 for the compute budget), sign-token shuffle of the planted corpus (40 runs).

## Statistics and gate
- null q95 = 95th percentile of E_best over the 40 shuffles of the cell.
- power = share of planted runs with E_best > null q95; FPR = share of wrong-language runs with E_best > null q95.
- unicity = median E_true (true key, no search) > null q95.
- precision = correct / assigned among signs used in the best key's exact-match windows (anchors excluded); recall = correct / syllabic non-anchor signs present.
- **A cell passes** iff power >= 0.8 AND FPR <= 0.2 AND median precision >= 0.5.
- **Go for #17** iff at least one cell with n in {20, 41, 49} and a <= 3 passes (these n bracket #17's 20/30/45). Otherwise **no-go**: land #26 as negative with the measured reason, and #17 is not run.
- I will report the smallest n and list size at which (i) a cell passes and (ii) unicity holds, with a = 0, 3, 6 separately.

## Search-adequacy check (pre-registered)
After the grid: re-run the shuffle condition for (sumerian, 41, 0) and (gulf, 41, 0), 10 runs each, at 4x iterations. If their median E_best rises by >= 2 over the grid's, the null is under-searched and any pass is void (reported as such).

## Laptop limits
board/run.sh, Pool(2), resumable out/grid.jsonl, about 2.7 CPU-hours estimated. Cuts made to fit: wrong-language reps 20 -> 10; one script model only (no cuneiform-style CVC script, no consonant-only matching, no coverage < 1 condition).
