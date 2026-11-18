# Pre-registration: redteam_round_seal_format (board #41, M6 red team of #39)

Written 2026-11-18 before any new statistic was computed. Agent: redteam-41. Folder: experiments/redteam_round_seal_format/. Own code (`run.py`); #39's code is read only to replicate its definitions.

## Claims attacked (experiments/round_seal_format/RESULTS.md)
- C1: round seals end in a grammar closer 14% (4/28) vs 45% of length/site-matched square seals (Holm p=0.003).
- C2: matching square seals on format (length x numeral-first x opener-first x closer-last) removes only 24% (CI 18-30%) of the round-seal KN order excess (+2.07 -> +1.58 bits/sign), so format does not explain the off-order.

## Things already seen before writing this (disclosed)
- Reading #39's code: its opener/closer sets are parsed with `.split()` on `wells_signs`, but multi-sign entries are `;`-separated, so "W817;W861", "W156;W154" and "W526;W527" are single strings that match nothing. Openers W817/W861 and closers W154/W156/W526/W527 were never counted. I fix this (split on `;` and whitespace) and report both versions.
- #39 deduplicates on (find-spot group, sequence) over ALL seals before splitting round/square, so a round text identical to an earlier square text is dropped (1924.1 W003 W390, 2419.1, 3669.1 W091). Sensitivity: keep them.
- foreign_corpus.csv notes: 148.1 and 3863.1 "drawing order reversed vs corpus"; 3882.1 reading direction disputed (M77 reads reversed); 3887.1 ICIT reading is a different text from Gadd/M77 (M65-M1-M1-M245-M245 preferred); 3898.1 last signs disputed (M77/Laursen W717-W005); 5222.1 drawing shows 5 signs (M51-M103-M345-M307-M342); 5230.1 middle element is a motif. 3882.1, 3888.1, 5557.1, 5468.1 are cylinders, not Gulf stamp seals.
- I saw #39's per-text d values in results.json (KN). I have not computed any statistic of my own.

## Data
Replicate #39: ICIT seals, round = SEAL:C/SEAL:CY minus 1387.1/1388.1/1388.2; distinct per (group, sequence); home/abroad/unprov; square pool = home non-round seals not sharing a round sequence. Corrected sign sets (split on `;`). Numerals = glib.NUM["ICIT"].

## A. Closer claim (C1). One-sided (round lower), 10,000 matched draws, site x length (cap 7) matching for home, length for abroad, as #39.
- A0 replication with #39's buggy sets (should give 4/28, p~0.0007).
- A1 corrected closer set (primary).
- A2 closer = W740 only.
- A3 closer = any sign whose Wells class in classes_wells.json is labelled closer.
- A4 data-driven closer: signs with >= 10 tokens in complete home square texts and >= 60% of them text-final.
- A5 complete texts only (ICIT complete flag, no '#') for both round and square.
- A6 keep the 3 round texts #39's dedup dropped.
- A7 shape subset: drop cylinders (SEAL:CY and foreign_corpus 'cylinder'); A7b: only foreign_corpus 'round Gulf'/'Dilmun' + the 3 register-confirmed home round seals (2911.1, 2912.1, 2977.1).
- A8 drop texts whose foreign_corpus reading_confidence is not 'confirmed' (home texts kept).
- A9 alternative readings: apply the foreign_corpus alternatives listed above (reverse 148.1, 3863.1, 3882.1; 3887.1 -> W235 W090 W090 W615 W615; 3898.1 -> W415 W803 W001 W717 W005; 5222.1 -> W255 W013 W745 W892 W740).
- A10 leave-one-out over the A1 text set: max p.
- A11 direction check: closer-FIRST rate, round vs matched squares (if round texts were read backwards, closers would sit first). Two-sided.
Verdict C1: SURVIVES if A1 p < 0.0125 (Holm-of-4 equivalent) and every A2-A9 has p < 0.05 in the same direction and A10 max p < 0.05. WEAKENED if A1 passes but any of A2-A10 fails. BROKEN if A1 fails or more than half of A2-A9 fail.

## B. Format claim (C2)
Order excess d per text = bits(real) - mean bits(<=200 distinct permutations), positive = off-order; home texts scored by 10-fold CV models trained on home ICIT texts (all types), abroad/unprov by the full home model. Three scorers:
- KN: Kneser-Ney bigram (q4_gulf.KN, as #25/#39).
- GR: Wells class bigram with the fixed classes of classes_wells.json; transition and emission counts re-estimated per fold with add-0.5 smoothing (BOS/EOS included).
- POS: glib.PositionModel(cap=4) per fold.
Format definitions (all with length, cap 9):
- F0 #39's key (num1, op1, clL) with corrected sets.
- F1 W090/W091 present anywhere.
- F2 any numeral anywhere.
- F3 closer-free (no closer sign anywhere).
- F4 first-sign Wells class label x last-sign Wells class label (UNK = own label).
- F5 F0 + number of signs outside the KN vocabulary (rare load, cap 2).
- F6 composite round-like: (no opener first) x (no closer anywhere) x (W090/W091 or numeral present).
Matching: draw from the stratum; if < 5 candidates, drop format dims from the right, then shorten length (count fallbacks). Length-only excess E_L and format-matched excess E_F (10,000 draws); fraction explained = 1 - E_F/E_L, bootstrap 95% CI over round texts (2,000).
Planted check (known answer): pseudo-round sets drawn from home squares with the round set's stratum composition under each definition (200 reps): mean E_L (what format alone produces) and mean fraction explained by E_F (should be ~1 if matching works).
Also: LOO over the scorable round texts for F0/KN fraction; fraction with A8 subset and A9 readings (KN, F0).
Verdict C2: SURVIVES if every scorer x definition (21 cells) has fraction < 0.5 and E_F p < 0.05. BROKEN if any definition reaches fraction >= 0.5 with E_F p >= 0.05 under >= 2 of 3 scorers. Otherwise WEAKENED (state which cells).

## C. Find-spot power (#41 item 4)
O2: 7 non-round seals abroad vs length-matched home squares (KN). Power to detect +0.5 bits/sign: 1,000 sets of 7 length-matched home squares with +0.5 added to each d (and +1.0), one-sided test at 0.05 with 2,000 null draws each.

## D. Shape reliability (descriptive)
Per round text: ICIT type, recorded dimensions, foreign_corpus shape, register confirmation. Count how many rest on the ICIT code alone.

Tests: A1-A11 (12 incl. A0, A7b), B 21 cells + checks, C power. Many are sensitivities of one claim; verdict rules above are fixed.
