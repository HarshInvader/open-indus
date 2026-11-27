# raj_check stage 5: how far can picking names alone move the score? (prereg T9)

2026-11-27. Written and hashed before any stage-5 run. Known: T0–T8 (paper's Tamil list +223; rebuilt Tamil lists +4 and +49; the paper's names the 4b list lacks +218 vs the 4b list's own −96; Japanese surnames +134.5).

## Question
Stage 4 showed the score depends on which names are in the list. How much? We deliberately pick names from a language with no Indus link (Japanese) to maximise the score, and test the picked list on seals the picking never saw. This is a demonstration of selection power, openly labelled as deliberate picking. It is not evidence for Japanese, and it does not claim the paper's list was picked this way (its archive does not say how the list was made).

## Design (Raj's `contest.py` unchanged; inputs as T4 Japanese: names, parts, picture words)
1. **Seal halves.** The unique seal texts that `contest.py` keeps (after its own filters) are split at random (seed 20261127) into half A and half B. Two corpus files are written, each holding only the rows of one half. `contest.py` then splits each half again into fit and test halves, as it always does.
2. **Picking, on half A only.** From the 1,125 T4 Japanese names, a local search picks 562 names (half) to maximise the objective: mean D over seeds 0–4 on corpus A. Start: a random 562 (seed 1). Each step proposes swapping one name in for one name out, at random (seed 2), and keeps the swap if the objective rises. Stop after 1,500 proposals.
3. **Test, on half B (never seen by the picking).** Seeds 0–9 on corpus B for:
   - J_pick: the picked 562 Japanese names;
   - J_rand: 5 random 562-name Japanese subsets (seeds 11–15), median;
   - T_paper: the paper's full Tamil list (1,125);
   - T_rand: 5 random 562-name subsets of the paper's Tamil list (seeds 11–15), median.
4. Also reported, clearly marked as not held out: J_pick on the full corpus, seeds 0–9.

## Readings fixed now (all on half B, seeds 0–9)
- **"Picking alone lifts a wrong language to the paper's Tamil level"** if J_pick ≥ T_paper.
- **"Picking lifts it part of the way"** if J_rand < J_pick < T_paper and J_pick − J_rand ≥ 0.5 × (T_paper − J_rand).
- **"Picking does not generalise"** otherwise (the search only fitted half A).
Descriptive: J_pick − J_rand (the lift from picking), T_rand vs T_paper.

## Limits stated now
Half-corpus runs have fewer seals (about 475), so D values are smaller and noisier than full-corpus values; compare only within half B. One search, one start. Seeds 0–4 and 0–9 on B use different seal splits from A, but the names and picture words are the same as T4.
