# Pre-registration: crib attack, planted validation (board task #3, agent H3)

Registered 2026-11-17 before the planted grid is run. No Indus data is used. Code: `experiments/crib_attack/{names,sim,attack,run_planted}.py` (hashed with this file, tag `crib_attack_planted`). One exploratory smoke run was made before this file: two shuffled-null searches at n = 20 (S = 68 for script A, 64 for script B). No planted outcome was seen.

## Method (frozen)
- Candidate names: Ur III seal-legend personal names (3,111 after dropping damaged ones, determinatives removed). Wrong-language control: Linear B personal names (575).
- Simulated script A (primary): CV syllabary. Clusters and codas are dropped or written with an echo vowel (each 50%). The attacker knows the rule and lists every spelling variant (6,718 spellings, 76 values). Script B (secondary): one sign per cuneiform sign value (CV/VC/CVC, 402 values).
- Planted corpus of n texts. 75% of texts carry a name: the name is drawn by frequency from the Ur III list and spelled in 2-5 signs, with each name sign misread (replaced by a random sign) at 20%, plus 0-2 frame logograms (12, Zipf) to a total of 3-6 signs. 25% of texts are 3-6 logograms only (40 logograms + frames). Sign ids are randomly permuted for each corpus.
- Attack: injective sign→value key found by simulated annealing (3 restarts, iterations min(15000, max(4000, 120n))). Text score = matched signs of the best (name spelling ≥ 2 signs, offset), counted only if matched ≥ 2 and ≥ k−1 for k ≥ 3 (exact for k = 2). Corpus statistic S = sum of text scores. Secondary E = number of texts with an exact full-name match (k ≥ 3) under the best key.
- Conditions: A_main (attacker list covers all true names); A_cov50 (attacker list = a random 50% of name types); B_main (script B). n ∈ {20, 30, 60, 120}. A_main: 10 planted, 10 wrong-language, 20 shuffled corpora per n; other conditions: 6/6/13.
- Shuffled null: a fresh planted corpus with its tokens pooled and redistributed over the same text lengths.

## Outcomes and gates (per condition and n)
- Power = share of planted runs with S above the 95th percentile of the shuffled-null S at the same n (same for E).
- False-positive rate (FPR) = the same share for wrong-language runs.
- Recovery = precision (correct / assigned signs) and recall (correct / syllable signs present).
- Search adequacy = share of planted runs with S_best ≥ S_true.
- Unicity point = smallest n at which the median S_true (true key) exceeds the 95th percentile of the null S_best.
- **The method works at n** if power ≥ 0.8 AND wrong-language FPR ≤ 0.2 AND median precision ≥ 0.5. The verdict for the real foreign corpus (n ≈ 20-30 per the meluhha/typology counts) follows from the A_main row at n = 20/30. If no n ≤ 120 passes, report that the method cannot work at any foreseeable n under this model, and give the unicity point if one exists.
