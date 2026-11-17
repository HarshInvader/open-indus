# Crib attack known-answer test on Linear Elamite (board task #17, H10)

## Verdict: negative. On a real deciphered script the frozen crib method recovers nothing.

I ran the method frozen in #26, unchanged, on the real Linear Elamite words, whose answer is known (Desset et al. 2022). The cribs were a short list of Elamite royal and divine names as attested in cuneiform. **No cell of the pre-registered grid recovers sign values.** The grid crossed 2 spelling rules, 2 samplings, n = 20/30/45 and 0 or 3 anchors.
- **Primary cell** (frozen CV rule, random words, n = 45): pass share 0.00 at a = 0 and a = 3, median precision 0.13 and 0.03, recall 1-3%.
- **Best case** (bare-consonant rule, i.e. the convention guessed right, name-rich "seal" sampling, n = 45, a = 3): median precision 0.65, but pass share is only 0.17. The real E (6) does not beat the Akkadian wrong-language list (6), and the true key's E (4) is below the shuffle 95th percentile in 100% of subsets.
- **The wrong-language list fits as well or better.** An Akkadian list of equal size gets median E ≥ the Elamite list's in all 24 cells.

**Why: real texts carry far fewer names than the planted model assumed.** #26 passed only when about 75% of texts carried a name from the list. In Linear Elamite:
- Under the true values, only **2 of 224** distinct words carry a crib spelling with the frozen CV rule (Napiriša twice), and **4** with the bare-consonant rule.
- A second cause is a spelling-rule flaw (below). After fixing it, and with the full 21-name list (70 spellings), the post-hoc best case is still **15/224 (7%)**.
- So even the sample richest in names that the corpus allows holds at most about 15 name-bearing words. The planted gate needed about 31 of 41.

The bottleneck is the share of texts that carry a listed name, not the search. The true key itself never beats the noise.

**Consequence for #4: do not run it.** A method that cannot recover Insušinak or Puzur-Inšušinak values from the real script they were first read from will not recover Indus values. The Indus case is weaker on every input: n = 9-11 safe texts, no proven owner-name list, and an unknown spelling convention.

Pre-registration: `docs/prereg/crib_le_known_answer.md` (tag `crib_le_known_answer`). It was hashed together with the crib list, `le_run.py` and the #26 `method.py`, which has the same hash as frozen.

## Setup
- **Data.** HLED (45 documents), split into 224 distinct words of 2-9 fully legible signs. A sign is a HLED token, so 'k' and 'k2' are separate signs (72 signs). The answer is the token value without its index, with s/š/ṣ merged on both sides.
- **Cribs.** `crib_names.csv` holds 21 cuneiform-attested Elamite royal, divine and place names and one title. It was capped at 30 spellings as frozen in #26, which kept 9 names: Puzur-Inšušinak, Inšušinak, Šušun, Šinpi-hiš-huk, Šilhaha, Eparti, Napiriša, Humban and Kiririša. The wrong-language list is short_Akkadian_top150, capped at the same size.
- **Grid.** 6 random word subsets per cell. Each subset got 1 search with the real list, 1 with the wrong list and 20 on shuffled tokens. That is 3,168 searches, about 2 CPU-hours, run through `board/run.sh` with Pool(2).

## Full table (medians over 6 subsets)
| rule | sampling | n | a | E real med | E wrong med | shuffle q95 med | E true med | true>q95 | pass share | prec med | rec med | recovers |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CV | random | 20 | 0 | 3.5 | 4.5 | 4.0 | 0.0 | 0.00 | 0.00 | 0.00 | 0.00 | - |
| CV | random | 20 | 3 | 3.0 | 4.0 | 3.1 | 0.0 | 0.00 | 0.00 | 0.00 | 0.00 | - |
| CV | random | 30 | 0 | 4.0 | 6.0 | 5.0 | 1.0 | 0.00 | 0.00 | 0.00 | 0.00 | - |
| CV | random | 30 | 3 | 3.0 | 4.5 | 4.0 | 1.0 | 0.00 | 0.00 | 0.16 | 0.04 | - |
| CV | random | 45 | 0 | 4.5 | 5.5 | 5.0 | 0.0 | 0.00 | 0.00 | 0.13 | 0.03 | - |
| CV | random | 45 | 3 | 4.0 | 5.0 | 4.1 | 0.0 | 0.00 | 0.00 | 0.03 | 0.01 | - |
| CV | seal | 20 | 0 | 5.0 | 6.0 | 4.0 | 2.0 | 0.00 | 0.00 | 0.27 | 0.09 | - |
| CV | seal | 20 | 3 | 4.5 | 5.0 | 3.0 | 2.0 | 0.00 | 0.00 | 0.38 | 0.11 | - |
| CV | seal | 30 | 0 | 5.5 | 6.0 | 5.0 | 2.0 | 0.00 | 0.00 | 0.00 | 0.00 | - |
| CV | seal | 30 | 3 | 4.5 | 5.0 | 4.0 | 2.0 | 0.00 | 0.00 | 0.15 | 0.04 | - |
| CV | seal | 45 | 0 | 5.5 | 6.5 | 5.0 | 2.0 | 0.00 | 0.00 | 0.00 | 0.00 | - |
| CV | seal | 45 | 3 | 5.0 | 6.0 | 4.5 | 2.0 | 0.00 | 0.00 | 0.35 | 0.08 | - |
| C | random | 20 | 0 | 4.0 | 4.5 | 4.1 | 0.0 | 0.00 | 0.00 | 0.00 | 0.00 | - |
| C | random | 20 | 3 | 3.0 | 4.0 | 4.0 | 0.0 | 0.00 | 0.00 | 0.00 | 0.00 | - |
| C | random | 30 | 0 | 5.0 | 5.5 | 5.0 | 1.0 | 0.00 | 0.33 | 0.29 | 0.08 | - |
| C | random | 30 | 3 | 4.0 | 4.5 | 4.0 | 1.0 | 0.00 | 0.33 | 0.24 | 0.07 | - |
| C | random | 45 | 0 | 6.0 | 7.0 | 5.0 | 1.5 | 0.00 | 0.00 | 0.07 | 0.02 | - |
| C | random | 45 | 3 | 5.0 | 5.0 | 4.0 | 1.5 | 0.00 | 0.00 | 0.08 | 0.02 | - |
| C | seal | 20 | 0 | 6.0 | 6.0 | 5.0 | 4.0 | 0.00 | 0.00 | 0.14 | 0.05 | - |
| C | seal | 20 | 3 | 5.0 | 5.0 | 4.0 | 4.0 | 0.17 | 0.17 | 0.29 | 0.10 | - |
| C | seal | 30 | 0 | 7.0 | 7.0 | 5.0 | 4.0 | 0.00 | 0.17 | 0.45 | 0.14 | - |
| C | seal | 30 | 3 | 6.0 | 6.5 | 4.0 | 4.0 | 0.17 | 0.33 | 0.47 | 0.12 | - |
| C | seal | 45 | 0 | 6.5 | 8.0 | 5.0 | 4.0 | 0.00 | 0.00 | 0.55 | 0.15 | - |
| C | seal | 45 | 3 | 6.0 | 6.0 | 4.5 | 4.0 | 0.00 | 0.17 | 0.65 | 0.12 | - |

## The spelling-rule flaw (affects #26's frozen method and any Indus crib list)
The CV rule, inherited from #3, joins cuneiform syllables into phonemes before re-spelling them. That turns the CV-VC writing convention into a long vowel, which then needs an extra vowel sign:
- *na-ak* becomes na-a-k, while Linear Elamite writes na-k;
- *šu-šu-un* becomes su-su-u(-n);
- *hu-um-ban* becomes hu-u-m-ba(-n).

The short lists from #2 and #24 are cuneiform syllabifications too, so the planted gate in #26 never saw this problem. In #26 the planted names were spelled by the same rule the attacker used. Post hoc, with no search, I collapsed the echo vowel. Name-bearing words then rise:
- from 4 to 7 with the 30-spelling list;
- to 15 with all 21 names (70 spellings).

Both counts are still far below what the gate needs.

## Not checked
- I did not re-run searches with the corrected spelling rule. Under the true key the counts above cap E at 7-15 words, while shuffles already reach 4-5 at n = 45. A rerun cannot satisfy the planted gate's requirement of about 31 name-bearing texts, and extra runs would only be stretching.
- Longer units (lines or documents) were not used; #26 validated only short texts. Longer units would contain more name words, but also more windows for noise to fit.
- The crib list is mine, from standard cuneiform royal and divine names. Before hashing I had seen HLED documents 1-2 while checking the file format. A list built by someone blind to Linear Elamite could differ.
- 6 subsets per cell is a small number: a pass share has a 95% CI of about ±0.35. No cell came close to the pass rule, and true > q95 never exceeded 0.17.

## What data would make a crib attack feasible
1. **A text set in which most texts are names from the list.** Gulf-type seals, if they really carry owners' names, are the right genre. But it takes about 40 or more of them with secure readings, against 9-11 now. The source of more would be new Gulf, Iran or Mesopotamian finds, or sign-level checks of the 30 "sensitivity only" readings from good photos (Parpola 1994b, CISI 3.1).
2. **A name list specific to the objects.** For example, the owner of a named seal impression on a dated tablet. A pool of plausible names is not enough.
3. **The spelling convention fixed from outside.** For example, a single bigraphic object, which would also give true anchors.

Without (1), the method has no power, whatever the list or search.

## Hypotheses
| hypothesis | verdict |
|---|---|
| Frozen #26 method recovers Linear Elamite name-anchored values at n = 45 (CV rule, random words) | refuted (pass 0.00, precision ≤ 0.13) |
| Same with the convention guessed and name-rich sampling | refuted (pass ≤ 0.33, the true key never beats noise) |
| The planted gate's 75% name-bearing assumption holds on a real name-anchored script | refuted (2-15 of 224 words) |
