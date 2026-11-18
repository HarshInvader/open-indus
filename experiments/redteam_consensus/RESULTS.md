# Red team #38: does the consensus corpus result (#35, N3) hold up?

Pre-registration: `docs/prereg/redteam_consensus.md` (sha256 in `docs/prereg/HASHES.txt`, 08:07Z, before any outcome below was computed). My own code: `measure.py` (aligner, rule re-derivation, cross-validation), `tests.py` (corpora, noise, reruns). The tests themselves are the frozen bars in `signlist_robustness/harness.py`. All compute went through `board/run.sh`.

## Verdicts

- **Claim A (13% disagreement, down from 19%): SURVIVES.** The corrected rate does not come from fitting. Re-deriving the fixes on half the objects and measuring on the other half gives **14.0% (200 splits, range 12.2-16.0%)**. The fixes fitted to the same objects give 13.4%, so fitting lowers the figure by only 0.6 points. N3's own map scores 12.5% on the same halves, 1.5 points under out-of-sample. My aligner gives 12.6-13.2% across the cost settings. **The README may say about 13% (out-of-sample 14%, CI about 12-16%) instead of 19%.**
- **Claim B (the headline findings hold): WEAKENED**, for two of the three findings I reran.
  - **#3 (ticked fish at the end): SURVIVES.** It passes on my consensus corpus, but only just (p = 0.043), and it passes in 30 of 30 noise runs.
  - **#7 (left-to-right reversals): WEAKENED, as N3 said.** Neither edition can confirm the other. Lines that both editions label left-to-right number 8, 4 or 7 depending on the rule; they read as labelled 7/8, 4/4 and 7/7, but none of these reaches the bar. One bias is new: the objects that could be linked flatter #7 (20 of 20 lines read as labelled), while the unlinked objects do not (17 of 24 = 0.71, p = 0.03).
  - **#10b (fixed pair order): WEAKENED, more than N3 reported.** It passes my consensus corpus (35/44 = 0.80). Under noise aimed at rare signs at the measured rate, it passes only **3 of 5** runs, and **2 of 5** at 1.5 times the rate. N3 reported 9 of 10 and 3 of 5. Under noise clustered by text it passes 5/5 at both rates; under site-weighted noise, 4/5 and 3/5.

## A. The concordance fixes (attack 1)

**The fish fix is right, not tuned.**
- On the 395 equal-length register-linked pairs, I counted with no mapping at all which Wells sign stands at the same position. The new partners win clearly: M65=W235 22/23, M67=W240 37/38, M70=W231 9/9, M72=W233 20/23, M59=W220 40/46.
- I tried all 120 ways of pairing the five plain fish with the five Wells fish:
  - N3's pairing ranks 1st (12.6%).
  - The next best is 14.2%.
  - The old harness pairing ranks 28th (19.0% overall).
- The pairing is decided by large counts, not by a near-tie. It also fits Mahadevan's drawings (`out/fish_montage.png`): roofed, cross-headed, inner-stroke and slashed fish.

**Other fixes:**
- M389=W806: 14/18 (W803 takes 3). M387=W803: 9/9. M162=W390: 32/32. M216=W550: 6/6.
- The three Wells splits (M175, M205, M210) rest on 3, 3 and 3 observations. They are weak, but they hardly move the rate.

**Ticked fish M71 and M73 are untestable.** They have zero occurrences on the matched objects. The analogy is consistent with the drawings (each ticked form is its plain fish with side strokes), but it is unverified. It does not affect the rate or any test, because the tests run in Mahadevan's sign list.

**My own rule set finds the same changes.** It was written separately and run on all 469 objects. It finds every N3 primary change except M68, M71 and M73 (no data) and M175/M205 (below my threshold). It also finds the same three doubled signs (M245 to W617, M176 to W401, M375 to W792), plus two narrowings N3 did not make (M103, M358). On all 469 objects it gives 13.0%.

**The doubled-sign rule is not one-sided in practice.** All 10 matched cases of "X X" in Mahadevan have the Wells double sign in the ICIT reading. There are none without it, and no case where ICIT writes two single signs. Merging always, or only when ICIT has the double sign, gives the identical rate (12.58%). Never merging gives 13.55%.

## B. How sensitive is the 12.9%? (attack 2; my aligner, N3's corrected map, 469 objects)

| variant | rate | 95% CI |
|---|---|---|
| harness map (reproduces #29) | 19.0% | 17.0-21.0 |
| corrected, swaps allowed (as N3) | 12.6% | 10.7-14.6 |
| v1 plain edit distance, no swaps | 13.2% | 11.2-15.3 |
| v2 cheap gaps (0.6) / dear gaps (1.5) | 12.6% / 12.8% | 10.7-14.6 / 10.9-14.9 |
| v3 longest common run, both readings | 10.5% | 8.9-12.1 |
| v4 unmapped signs counted as disagreements | 17.4% | |
| denominator = mean length of both readings | 12.8% | |
| **split-half out-of-sample (my rules)** | **14.0%** | 12.2-16.0 |
| relinked under the corrected map, cut 0.8 / 0.5 / 1.0 | 12.8% (475) / 8.5% (435) / 28.0% (562) | |

**What drives the figure:**
- **The alignment method barely matters** (10.5-13.2%). What matters is how the link-error cut and the unmapped signs are handled.
- **The 0.8 cut does real work.** Random pairs fall under it 11.6% of the time, so it is needed. But some of the 93 dropped register pairs may be true links that were read very differently. Keeping all 562 gives 28%, and that figure is mostly link errors.
- **Sites differ.** Harappa is 17.5% and Mohenjo-daro 10.8%. By object type: sealings 24%, tablets 18%, seals 11%.
- **The honest statement** is "about 13%, 14% out-of-sample, with Harappa and sealings worse".

## C. Is the consensus corpus biased toward easy texts? (attack 3)

**Yes, in composition. It matters only for #7.**
- **Sign-linking keeps the easy cases.** Of the register pairs, those that sign-linking would have admitted (distance at most 0.5, 433 of 469) disagree on 8.6% of signs. The 36 it would have missed disagree on 67%. So the 2,741 sign-linked texts are close to agreement by construction.
- **The 214 unlinked M77 sides differ from the linked ones.** They are shorter (3.5 vs 3.9 signs). Rare signs (corpus frequency under 10) make up 23% of their tokens, against 4.8%. They come more from Lothal, Kalibangan and West Asia.
- **Running the tests on the uncorrected M77 text, split into linked and unlinked sides:**
  - #3: linked 0.58 final; unlinked has no ticked fish to test.
  - #10b: linked 0.78 vs base 0.79; unlinked has 2 occurrences.
  - So the selection does not flatter #3 or #10b.
  - #7: linked 20/20, unlinked 17/24 (0.71), base 31/34. The L-R lines that disagree with their label sit in the objects the consensus corpus throws away.

## D. Reruns (attack 4; frozen bars)

| condition | #3 ticked final (bar p<0.05) | #7 L-R reversals (bar 0.70, p<1e-3) | #10b pair order (bar 0.75, p<1e-3) |
|---|---|---|---|
| base M77 | 0.58, p=0.004 pass | 31/34 pass | 0.79 (107) pass |
| D1 my consensus corpus (reg + sign links, own masking) | 0.47, p=0.043 pass | 7/8, p=0.035 underpowered | 0.80 (44) pass |
| D2 only register links masked | 0.56, p=0.005 pass | 27/30 pass | 0.83 (83) pass |
| D3a both editions say L-R, disputed signs masked | | 4/4, p=0.06 underpowered | |
| D3b ICIT's own L-R lines | | 7/7, p=0.008 underpowered | |
| rare-sign noise x1.0 / x1.5 (5 seeds) | 5/5 / 5/5 | 4/5 / 4/5 | **3/5 / 2/5** |
| clustered-by-text noise x1.0 / x1.5 | 5/5 / 5/5 | 5/5 / 5/5 | 5/5 / 5/5 |
| site-weighted noise x1.0 / x1.5 | 5/5 / 5/5 | 5/5 / 5/5 | 4/5 / 3/5 |

**Notes on the noise:**
- The realised edit rates at x1.0 were 12.1-12.5% (`out/noise_rates.json`).
- My noise has no whole-text reversals. N3 showed that those are what hurt #7, so my #7 noise rows are milder than N3's.
- #10b's failures sit just under the bar (shares 0.71-0.74, every p < 1e-4). The direction of the effect is never in doubt; whether it clears the frozen 0.75 bar is.

## What was not done

- **No sign-independent link beyond the 469 register objects.** M77 carries no CISI or excavation numbers. Measuring disagreement on later sites needs a plate or CISI concordance for M77 text numbers; that is a data task.
- **Only #3, #7 and #10b were rerun.** #1, #5, #6, #9, #10a and #11 were not attacked here.
- **Shared errors between the editions remain invisible**, as N3 says.
- **Tests run:** 3 findings in 37 conditions (107 ledger rows), plus the descriptive A/B measurements.

Files: `out/measure.json`, `out/tests.jsonl`, `out/noise_rates.json`, `out/fish_montage.png`, `ledger_rows.csv`.
