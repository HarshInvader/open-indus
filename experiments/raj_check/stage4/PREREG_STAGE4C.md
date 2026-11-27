# raj_check stage 4c: why does a fresh Old Tamil list score ~0? (prereg T8)

2026-11-27. Written and hashed before any stage-4c run or agent. Known: T0–T7 so far, in particular the fresh Old Tamil list (T7, +4.2 ± 185, 4 of 10) and the exploratory swaps X1/X2 (fresh names with the paper's picture words −72.5; the paper's names with fresh picture words +276.4), and an independent review (Fable) that found:
- 512 of the paper's 1,125 names appear, as the same string, in the fresh list; only 226 of those have the same segmentation;
- our compiler prompts added an instruction the paper's prompt does not have: "Keep honorific and gender endings as their own member" (logged as deviation 8 in `DEVIATIONS_4B.md`). 43% of fresh names end in the honorific ār, against 9% in the paper's list; mean members per name 3.04 against 2.24.

## Question
Is the gap between the paper's list (+223) and the fresh list (+4) due to **which names** are chosen, or to **how names are cut into parts** (including the honorific endings), or to **the part labels**?

## Runs (Raj's `contest.py` unchanged; seeds 0–9, real and null; picture words: the paper's `words_tamil_new.json` for every run, since X1/X2 showed they do not drive the gap; number words and drop_parts tiru, aiyaṉ as the headline)
| Run | Names | Segmentation and part labels |
|---|---|---|
| C1 | the 512 shared names | the paper's (`names_model_clean.jsonl`, `morphemes.jsonl`) |
| C2 | the 512 shared names | the fresh list's (`names_tamil4b.jsonl`, `parts_tamil4b.jsonl`) |
| C3 | the 512 shared names | fresh segmentation; the paper's label where the part exists in `morphemes.jsonl`, else the fresh label |
| C4 | the fresh list (1,125) | fresh, with drop_parts extended by ār, ar, aṉ, āṉ, aḷ |
| C5 | the paper's list (1,125) | the paper's, with the same extended drop_parts |
| C6 | the paper-only names (613) | the paper's |
| C7 | the fresh-only names (613) | the fresh list's |

Shared means the same `name` string in both files.

## Readings fixed now
- **Segmentation** (C1 − C2): "how names are cut matters" if ≥ 100; "does not matter" if |C1 − C2| < 50; otherwise "unclear".
- **Labels** (C3 vs C2): descriptive.
- **Honorific endings** (C4): "the endings explain the fresh list's low score" if C4 ≥ 178.4; "they do not" if C4 ≤ 111.5; otherwise "partly". C5 descriptive (does removing the same endings hurt the paper's list?).
- **Selection** (C6 − C7): "which names are chosen matters" if ≥ 100; "does not matter" if |C6 − C7| < 50; otherwise "unclear".

## Also in this stage: a faithful fresh Old Tamil list (T8b)
A fresh agent compiles Old Tamil names with the paper's REP-1 Sanskrit name-compiler prompt with only the language, sources and examples changed, and **no added instructions** (prompt saved as `agents/tamil_faithful_compiler_prompt.txt`; diff against the paper's prompt in `agents/tamil_faithful_compiler_prompt.diff`). Then the v2 labeler (origin rule), a checker (as 4b), inputs committed, then the contest with the fresh picture words of T7 and, as a second run, the paper's picture words. Reading as T7: "the paper's list is not special" if D ≥ 178.4, "special" if D ≤ 111.5, otherwise "partly".

## Limits stated now
With seed sd of 100–200, the standard error of a difference of two 10-seed means is about 60–90, so a difference of 100 is a modest bar; results near the lines are reported as such. The shared names are not a random sample of either list.
