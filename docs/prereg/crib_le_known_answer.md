# Pre-registration: crib attack known-answer test on Linear Elamite (board task #17, H10)

Written 2026-11-17 before any search was run on Linear Elamite. The method is the frozen #26 method (experiments/crib_attack_v2/method.py, hashed under crib_attack_v2_planted), unchanged. Code: experiments/crib_le_known_answer/le_run.py; crib list: experiments/crib_le_known_answer/crib_names.csv (both hashed with this file). Before writing this I had read HLED documents 1-2 (Puzur-Sušinak lion table) while checking the file format, and run `le_run.py --describe` (corpus and list sizes only).

## Data and answer
- Linear Elamite: HLED (45 documents, local). Units = distinct words of 2-9 fully legible signs (224). Sign = HLED token ('k' and 'k2' are different signs; 72 signs). Answer = token without index (Desset et al. 2022 values). Values normalised s/š/ṣ -> s and ṭ -> t on both sides.
- Crib list: 21 Elamite royal, divine, place names and one title as attested in CUNEIFORM (not taken from LE), in a fixed order with the anchor names of the decipherment first; capped at 30 spellings (frozen #26 regime: 27). Wrong-language list: short_Akkadian_top150 capped at the same size (26).
- Attacker spelling rules: **CV** (frozen #26 rule: coda consonant dropped or written C + echo vowel; primary) and **C** (coda consonant dropped or written as a bare consonant sign; the LE convention, i.e. the attacker guesses the convention right; secondary).
- Sampling of n words: **random** (n distinct words at random; primary) and **seal** (75% drawn from words that contain a crib spelling under the TRUE values, the rest random; best case mirroring #26's p_name = 0.75; uses the answer only to compose the sample).

## Grid
rule {CV, C} x sampling {random, seal} x n {20, 30, 45} x anchors a {0, 3} (a = the most frequent signs of the sample fixed to their true values) x 6 random subsets. Per subset: 1 search on the real words with the Elamite list, 1 with the Akkadian list (wrong language), 20 searches on token-shuffles of the same words. About 3,200 searches, about 2 CPU-hours, board/run.sh, Pool(2), resumable out/runs.jsonl.

## Statistics and decision
- Per subset: pass if E_real > 95th percentile of the 20 shuffle E values AND E_real > E_wrong.
- Precision = correct / signs used in the best key's exact-match windows (anchors excluded); recall = correct / non-anchor signs present. Correct = same normalised value.
- A cell (rule, sampling, n, a) **recovers** iff >= 80% of subsets pass AND median precision >= 0.5.
- Prediction from #26: CV-random fails at n = 20 and 30; n = 45 is the decisive size.
- **Verdict for the method:** "works on a real script" iff the primary cell (CV, random, n = 45, a <= 3) recovers. If only the C-rule or seal-sampling cells recover, the verdict is "works only if the spelling convention is guessed / the sample is name-rich", and #4 inherits that condition. If no cell recovers, the method fails on a real script, and #4 should not be run.
- Also reported: E_true (the true key's score) against the shuffle q95, i.e. whether the answer is identifiable at all with this list.
