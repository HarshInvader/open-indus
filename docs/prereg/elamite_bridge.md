# Pre-registration: do Indus signs that look like Linear Elamite signs behave like syllables?

Agent: elamite_bridge. Written 2026-11-15, after the calibration in `experiments/elamite_bridge/eb_calibrate.py` (Linear B, Egyptian; no Indus sign identities used) and BEFORE any Indus test below has been run. The only Indus facts looked at so far are the raw ICIT token counts of the candidate signs (to know which pass the frequency floor) and the check that W853 is initial in 10 of 11 occurrences (confirming that Fuls's numbers are ICIT/Wells numbers).
Code: `experiments/elamite_bridge/eb_test.py` implements exactly the tests below. Hashes in `docs/prereg/HASHES.txt`.

## Source of the sign set (external, fixed before looking at Indus distributions)
Fuls, A. 2024. Comparison of Linear Elamite and Indus Writing Systems. *Iranian Journal of Archaeological Studies* 14(1): 3-16, Fig. 9 (checked against the figure image). 21 Indus signs (ICIT numbers) are paired with graphically similar Linear Elamite signs:
850 a (graphic universal), 502 li, 455 hi, 370/371 la, 012 na, 058 -, 360 ši, 440 še, 330 -, 323 ni, 400/402 ni, 684 š, 167 n, 625 - (graphic universal), 899/900 pa (graphic universal), 913 - (graphic universal), 335 po, 032 zu (graphic universal), 615 zo, 794 -, 831 r, 482 re.
Values are Desset et al. 2022 (ZA 112: 11-60), as reported by Fuls.

## Metric (fixed)
Unit: ICIT texts, `distinct()` on the full sequence, split into break-free runs with `runs()`.
For each sign with >= 10 tokens: D = log(distinct left+right neighbour types + 1) minus the OLS prediction from log(token count), fitted over all signs with >= 10 tokens (`eb_core.diversity_residuals`).

Calibration (already run, `calibration.json`), Indus-length chunks at the ICIT token count (13,190):
- Linear B: syllabograms vs logograms AUC 0.91 (5-95%: 0.89-0.94). A random set of 12 true syllabograms beats frequency-matched random sets of all signs (mixed rest) at p < 0.05 in 73% of draws.
- Egyptian: 26 uniliteral phonograms vs all other signs AUC 0.67 (0.63-0.71); same power 0.73.
So D carries real information about phonetic vs logographic use, with moderate power for a ~12-sign set.

## Hypotheses
### H1 (primary) Complex look-alikes are syllable-like
Set C = Fig. 9 Indus signs minus Fuls's graphic universals (850, 625, 899, 900, 913, 032), keeping signs with >= 10 tokens.
Statistic: mean D of C. Null: 20,000 random sets of the same size drawn from all signs with >= 10 tokens, matched on frequency quintile. One-sided p (C higher).
**Supported** if p < 0.05 after Holm over {H1, H4}. Report AUC of C vs all other signs.

### H2 (secondary, descriptive) All look-alikes
Same test with all Fig. 9 signs with >= 10 tokens.

### H3 (replication, descriptive) M77
Map the C signs to Mahadevan numbers with `sources/shaunmortal_indus/data/bridge_WM.json`, keeping only W signs that map to exactly one M sign (and M signs claimed by only one C sign). Same test on M77 distinct texts. Direction must agree with H1 for any positive claim.

### H4 (primary) External key: sound values carry over
Key: the 20 Indus signs with a Desset value in Fig. 9 (16 distinct values). Count adjacent pairs in ICIT distinct break-free runs where both signs are in the key and the value pair (reading order) occurs as an adjacent syllable pair in the Linear Elamite corpus (HLED, 45 documents, `sources/paragorth_Indus-/data/derived/linear-elamite-corpus-hled.json`, transliterations split on `-` and spaces; word and line boundaries break pairs; damage brackets stripped; X and ... dropped and break pairs). Null: 20,000 permutations of the values among the 20 key signs. One-sided p (more attested pairs).
**Supported** if p < 0.05 after Holm over {H1, H4}. Prior result to replicate (paragorth ANCHORS §11, different code and corpus): 2 attested vs 4.1 +- 2.7, P = 0.83.

## Predictions (written now)
- H1: not supported. Graphic look-alikes chosen across two ~hundreds-sign lists are mostly chance resemblances.
- H4: not supported.

## Interpretation fixed in advance
- H1 supported: the look-alikes combine freely like syllabograms. That is compatible with borrowed syllabic signs but does not show borrowing or give values (it would justify a sound-value test on those signs only).
- H1 not supported: the look-alikes do not behave like syllabograms in the one metric that separates syllabograms from logograms in Linear B. With power ~0.7 this weakly argues against a borrowed syllabic layer; it cannot exclude it.
- H4 is the direct test. Not supported = no sign of Linear Elamite sound values in Indus sequences.

Tests counted: 2 confirmatory (H1, H4), 2 descriptive (H2, H3), 2 calibration runs.
