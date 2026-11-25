# Disguised-script tournament: closed at the gate before sealing (plan 12, family 2)

- **Ruling:** the coordinator closed it on 2026-11-25, on a fresh review of the unsealed draft. The draft itself stays unpublished and gitignored, with status DRAFT v1. No method was run, no text was disguised, and no accuracy was computed.
- **The planned test:** compare decipherment methods with identity and language hidden, on read scripts of Indus shape. Pick a winner on 3 training cells and grade it once on 5 held-out cells against our bench (the `mismatch_study` A3 attack). Run a leak probe so that agents cannot name the script.

## The two findings that stand
1. **Only 3 independent script families exist at Indus shape on open data:** cuneiform, Brahmic, and Linear B. The draft found 14 eligible cells: 8 cuneiform from the CDLI dump, 5 Brahmic from Wikipedia counted by akshara, and Linear B. With at most 2 held-out cells per family, only 5 cells can be held out. The gate must then be 5 of 5, and the p-value at family level is 1/8, not 1/32.
2. **Counts on these corpora must handle numerals and damage explicitly.**
   - The draft's scratch counter deleted readings it could not match to the sign list in the middle of a line. That joins signs that were never adjacent.
   - Most of those readings are numerals: 90.5% in Ur III (741,438 of 818,984), 89% in Old Akkadian and 46% in Neo-Assyrian.
   - Linear B syllabograms fall to 20,970 tokens once damaged lines are dropped. That is **2 draws of 8,000 tokens, not 3**.

## Why it was closed rather than fixed
The fresh review (Opus, adversarial) listed 9 must-fixes:
1. the counts above;
2. the bench reads logogram status from the true values (an oracle) and uses a fixed list of 95 European syllables, so it cannot run blind;
3. the menu and scorer normalisation were undefined;
4. CPU was underestimated by 2 to 4 orders of magnitude, because swap polish grows roughly as S⁴;
5. language choice by objective per token favours models with few values;
6. designers would know the held-out set, which inventory size gives away, and the split was chosen by eye;
7. the leak probe counted naming the family as a hit, so base-rate guesses would end the study;
8. the statistics were loose, and power was about 27% even for a true +0.10 Hit@1 advantage;
9. there was no planted test of the comparison itself.

- **The review's estimate:** under 5% chance of a pass, and about 50% that the leak probe ends it.
- **Bearing on the 2027 bar:** none, even if it passed.
- **Prior art:** it already shows method rankings vary across benchmarks. Tamburini 2025, doi:10.3389/frai.2025.1581129, compares 3 systems on 7 benchmarks with the language and the word division given.
- **Decision:** close at the gate. Do not build a slim version.

## Lessons carried into later studies
- Count with the real tokenisation, never with a scratch counter.
- State the number of independent families, and say whether the held-out unit is the script or the family.
- Add a planted test of the comparison itself.
- Estimate CPU and power before sealing.
