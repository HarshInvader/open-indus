# Pre-registration: are the foreign-found Indus texts structured like names or seal legends? (board task #10, H2)

Written before the foreign texts are scored on these measures.
Code: experiments/name_structure/compare.py.
Name data: experiments/onomasticon/names.csv (task #2).

Foreign set: experiments/foreign_corpus/foreign_corpus.csv rows with >= 2 legible Wells signs. Each text is its
Wells signs with "#", "|" and "?" removed; texts of length >= 2 are kept. This is the primary set. The T1/T2
survivors of task #11 are reported descriptively only.

Comparators. All are written-sign sequences: a cuneiform sign is one unit, determinatives are dropped.
- C1: Ur III personal seal legends (identifiers/ur3_occ.jsonl, all lines joined, distinct legends).
- C2/C3/C4: distinct Akkadian, Amorite and Sumerian personal names from names.csv (written form split on - and .).
- C5: Indus home seals. These are ICIT seals at non-foreign sites, distinct, from glib icit_units with register "seal".

Length matching. For each foreign text of length L, draw a comparator text of length L. If none exists, use the
nearest length available (L-1 or L+1 first). 2,000 matched samples of size n per comparator.

Statistics on a set of texts:
- S1: share of sign tokens whose sign occurs in only one text of the set.
- S2: share of texts with a repeated sign.
- S3: share of texts whose final sign is also the final sign of another text in the set (shared endings).
- S4: the same for initial signs.
- S5: S3 - S4 (edge asymmetry; a recurring theophoric suffix such as -ilum or -El gives S5 > 0).

Assignment: z-distance D_c = sqrt(sum_k ((obs_k - mean_ck)/sd_ck)^2) over S1-S4 for each comparator c.
The foreign set "resembles" the comparator with the smallest D, but only if (a) that comparator is not rejected
(every per-statistic two-sided p > 0.05/4) and (b) the assignment has power.

Power (planted). For each comparator X, draw 500 length-matched sets of size n = 30 and of size n = n_foreign from
X, with a fresh draw that is not one of the reference samples, and assign each by the rule above. Power = share
assigned back to X. If X's power at n_foreign is < 0.8, a foreign assignment to X is reported as
"untestable/undecided".

Descriptive, not tested:
- the position (initial, interior or final) of person signs (W090-W175) and numerals (W001-W059) in foreign
  texts versus home seals;
- which foreign signs sit in final position and recur there across texts (candidate theophoric/closer slot),
  with their home final-position rate.

Tests: 4 statistics x 5 comparators = 20 p-values, Bonferroni within each comparator.
