# Consensus corpus: the nine headline tests at the real transcription error rate

Board task #35 (M6), N3, 2026-11-18. Pre-registration: `docs/prereg/consensus_corpus.md`. It and all six scripts were hashed in `docs/prereg/HASHES.txt` (tag `consensus_corpus`, 06:42Z) before any test condition was scored. All compute went through `board/run.sh`.

## Verdict

**All nine headline tests hold at the real disagreement rate.** They pass on the signs both editions agree on, on Wells/Fuls's readings of the same objects, and under noise that copies the measured error pattern. That is the pre-registered verdict for every finding. Two qualifications:

- **#7 (left-to-right reversals) cannot be checked on the consensus corpus.**
  - When only lines are kept whose direction both editions label the same way, and whose signs both read the same, 8 left-to-right lines remain (7 of 8 read better as labelled; power about 0).
  - #7 passes on ICIT's own readings and labels (24 of 28, p = 9e-5) and under measured noise (8 of 10 seeds).
  - But it is supported only by direction labels the two editions mostly do not share. "Holds" here means "not contradicted", not "confirmed by both editions".
- **#10b (fixed pair order) has the thinnest margin.**
  - It passes in 9 of 10 seeds at the measured rate (agreement 0.72-0.88 against a bar of 0.75).
  - It drops to 3 of 5 seeds at 1.5 times the rate, and its power on the strict consensus corpus is 0.65.
  - #3 is the next weakest: on the primary consensus corpus it passes at p = 0.039 against a bar of 0.05.

**The disagreement rate itself, after correcting our own mapping, is 12.9% of signs (95% CI 11.1-14.9%), not 19.4%.**
- About a third of the old figure was our mapping, not the editors: the fish pairing, M389, three one-to-many entries, and Wells' single signs for doubled Mahadevan signs.
- The corrected rate is still above the 10% the audit tested, so the stress test was rerun at the measured rate and structure. It is passed.

## 1. Corrected concordance and the real disagreement

Full documentation is in `CONCORDANCE.md` (every change, with its evidence and drawing check). Files: `corrected_concordance.csv` and `out/concordance.json`.

**Evidence.** The 469 register-matched objects of #29. They are linked by excavation registers, not signs: 1930s Mohenjo-daro, Harappa and Chanhu-daro; 342 seals, 81 tablets, 46 sealings. On the 395 whose two readings have equal length, same-position counts need no mapping at all.

**What changed:**
- **The plain fish were cross-wired.** The correct pairs are M65=W235, M67=W240, M70=W231, M72=W233 (22/23, 37/38, 9/9 and 20/23 same-position). Mahadevan's drawings match: roofed, cross-headed, inner-stroke and slashed fish.
- **The ticked fish follow the same pattern**: M66=W236 (3/3), M68=W241, and M71=W232 and M73=W234 by analogy.
- **M389 was unmapped.** It is W806 (14/18).
- **Three one-to-many entries were narrowed** (M162, M216, M387). Three Wells splits were added as alternates (M175, M205, M210).
- **Mahadevan writes some signs twice where Wells has one "double" sign.** M245 M245 = W617, M176 M176 = W401, M375 M375 = W792, plus 6 single cases. This one convention had been counted as a substitution plus a missing sign.

**Disagreement** (per compared sign, same alignment and link-error cut as #29, text bootstrap):

| mapping | total | identity | missing/extra | order (adjacent swap) | direction (reversed text fits better) | texts with any difference |
|---|---|---|---|---|---|---|
| harness (as in #29) | 19.4% (17.4-21.4) | 12.9% | 5.6% | 0.9% | 2.1% of texts | 50% |
| **corrected, primary** | **12.9% (11.1-14.9)** | **7.3% (6.1-8.6)** | **5.0% (3.8-6.3)**: 4.0% only in M77, 1.0% only in ICIT | **0.6% (0.3-1.0)** | **2.1% (0.9-3.4)** | **34.5% (30.3-38.8)** |
| corrected + provisional (2-observation entries) | 11.3% (9.5-13.1) | 6.0% | 4.6% | 0.6% | 2.1% | 31% |

**Other measurements:**
- On 2,741 further M77 texts linked to ICIT by their signs (best same-site record, distance at most 0.5), disagreement is 11.0%. That link is biased toward agreement, so this is a floor, but it now includes Lothal, Kalibangan and the smaller sites.
- 105 of 2,036 M77 tokens on matched texts (5%) still have no Wells partner and are left out of every rate.
- **Missing signs lean toward the text start.** Of 77 signs only M77 has, 30 are text-initial, 16 final and 31 medial. Per position that is 6.4% initial, 3.4% final and 2.8% medial: the start is over-represented 2.3 times.

**The 20 sign pairs that account for most of the remaining 250 disagreements** (primary mapping). Together they cover only 24%; after the correction, what remains is a long tail.

| kind | M77 | ICIT | count | share | cumulative |
|---|---|---|---|---|---|
| missing/extra | M342 (jar) | - | 5 | 2.0% | 2.0% |
| order | M89+M328 | W700+W033 | 5 | 2.0% | 4.0% |
| identity | M155 | W072 | 4 | 1.6% | 5.6% |
| missing/extra | M162 | - | 4 | 1.6% | 7.2% |
| identity | M230 | W463 | 4 | 1.6% | 8.8% |
| missing/extra | M86 | - | 3 | 1.2% | 10.0% |
| missing/extra | M153 | - | 3 | 1.2% | 11.2% |
| identity | M104 | W034 | 3 | 1.2% | 12.4% |
| missing/extra | M267 | - | 3 | 1.2% | 13.6% |
| identity | M389 | W803 | 3 | 1.2% | 14.8% |
| missing/extra | M242 | - | 3 | 1.2% | 16.0% |
| missing/extra | M87 | - | 3 | 1.2% | 17.2% |
| missing/extra | M59 | - | 3 | 1.2% | 18.4% |
| identity | M76 | W263 | 2 | 0.8% | 19.2% |
| identity | M294 | W927 | 2 | 0.8% | 20.0% |
| identity | M14 | W159 | 2 | 0.8% | 20.8% |
| identity | M72 | W220 | 2 | 0.8% | 21.6% |
| identity | M174 | W354 | 2 | 0.8% | 22.4% |
| identity | M125 | W065 | 2 | 0.8% | 23.2% |
| missing/extra | - | W621 | 2 | 0.8% | 24.0% |

One systematic case stands out: **9 of the 12 order swaps involve M328, all on Harappa objects**. M77 places M328 after a stroke or fish sign where ICIT places it before.

## 2. Corpora

`corpora.py` builds them; sizes are in `out/corpora_summary.json`. All are in M77 sign space, so the tests run unchanged.

| corpus | how | distinct texts (held-out) |
|---|---|---|
| base | M77 | 2,270 (571) |
| **cons_sign_ext** (primary consensus) | 3,210 linked sides (469 by register, 2,741 by signs). Every sign the editions disagree on becomes a break; unlinked sides dropped | 2,065 (491) |
| cons_text_ext (strict) | linked sides with no disagreement at all (307 of 469 register-linked, 1,897 of 2,741 sign-linked) | 1,293 (315) |
| cons_sign_reg | register-linked sides masked, rest unchanged | 2,295 (571) |
| **icit_ext** (either-edition pair with base) | every linked side read as ICIT reads it, with ICIT's direction labels for #7 | 2,060 (485) |
| icit_reg | same, register-linked only | 2,303 (571) |
| match_m77 / match_icit | the 469 register-linked sides only, read each way | 403 / 413 (115) |

**Partial-agreement policy** (pre-registered):
- Sign level is primary: a disputed sign becomes a break.
- Text level is strict: any dispute drops the text.
- Signs with no concordance entry are kept, as unverifiable rather than disputed.
- For #7, a linked object's lines count only if the object has no dispute and both editions give it the same direction.

## 3. The nine tests (frozen bars of `signlist_robustness/harness.py`, type unit, split v2, called as in `assumption_audit/sens.py`)

**Noise model ("struct")**, applied to the whole corpus. It copies the measured structure:
- per-sign substitution rates shrunk toward 7.3%, with each sign's observed ICIT substitutes as targets, and look-alikes otherwise;
- position-specific deletions and insertions;
- 0.6% adjacent swaps;
- 2.1% whole-text reversal.

It is calibrated (one constant, c = 1.14) so that f = 1 realises 12.9% edits per sign on the full corpus (`out/noise_calib.json`). f = 1 treats every disagreement as an M77 error, which is conservative. f = 0.5 is an even split between the editions. f = 1.5 allows for errors both editions share (about the uncorrected 19%). "unif" is the audit's random noise at the same 12.9%.

The base run reproduces the audit base. The one difference is a dev count of 1,698 vs 1,699 (one record empty after filtering), which moves one T4 null quantile by 0.001.

| finding | cons_sign_ext | icit_ext | struct x1.0 (10 seeds) | **overall** | cons_text_ext | struct x0.5 | struct x1.5 | unif x1.0 | match M77 / ICIT |
|---|---|---|---|---|---|---|---|---|---|
| #1 order beats permutations | holds 0.44 vs 0.06 | holds 0.34 vs 0.05 | holds 10/10 (0.27-0.36, about 5x) | **holds** | holds | 5/5 | 5/5 | 5/5 | holds / holds |
| #3 ticked fish final | holds 0.47 vs plain 0.08, p=0.039 (pw 0.88) | holds 0.53, p=0.005 | holds 10/10 (0.41-0.61, p 0.0005-0.034) | **holds** | holds, p=0.05 (pw 0.88) | 5/5 | 5/5 | 5/5 | underpowered (pw 0.12 / 0.30) |
| #5 six + fish | holds 7/9 | holds 7/11 | holds 10/10 | **holds** | holds 6/8 | 5/5 | 5/5 | 5/5 | underpowered (n=2) |
| #6 object-type registers | holds AUC 0.73 | holds 0.71 | holds 10/10 (0.71-0.75) | **holds** | holds 0.69 | 5/5 | 5/5 | 5/5 | holds / holds |
| #7 L-R reversals | **underpowered** 7/8 (pw 0.00) | holds 24/28, p=9e-5 | holds 8/10 (0.70-0.87) | **holds (not confirmable on consensus)** | underpowered 7/8 | 5/5 | 4/5 | 5/5 | underpowered |
| #9 functional parse | holds 0.79 vs 0.44 | holds 0.76 vs 0.42 | holds 10/10 (0.68-0.72 vs 0.40) | **holds** | holds | 5/5 | 5/5 | 5/5 | holds / holds |
| #10a cores | holds 0.45 / 0.70 | holds 0.45 / 0.68 | holds 10/10 | **holds** | holds | 5/5 | 5/5 | 5/5 | holds / holds |
| #10b fixed pair order | holds 35/44 = 0.80 (pw 0.81) | holds 68/81 = 0.84 | holds 9/10 (0.72-0.88) | **holds, thin** | holds 0.81 (pw 0.65) | 5/5 | **weakens 3/5** | 4/5 | underpowered |
| #11 fish class | holds 2/3 | holds 3/3 | holds 10/10 | **holds** | holds 2/3 | 5/5 | 5/5 | 4/5 | weakens / fails (n=115) |

"pw" is the simulated power to pass at the base effect size with that corpus's n. For a seeded family, the share of seeds passing is the power to keep passing at that error level (struct x1.0: 1.0 for every test except #7, 0.8, and #10b, 0.9). Full effect sizes per seed: `table.md`. Machine-readable: `results.json`.

**The matched-only pair (469 texts, 115 held-out)** answers whether the two readings of the same texts give different answers. Where the tests have power (#1, #6, #9, #10a), M77 and ICIT readings agree on every verdict. #11 passes 1 of 3 sub-tests on M77's reading and 0 of 3 on ICIT's; at n = 115 neither is informative.

## Pre-registered predictions

- **P1: right.** #1, #6, #9, #10a and #11 hold in all three primary conditions.
- **P2: half right.**
  - #7 is unconfirmable on the consensus corpus (8 lines).
  - Wrong: it does not weaken on icit_ext (24/28). The extended ICIT corpus has enough L-R lines under ICIT's own labels to pass.
- **P3: wrong.** #10b holds at the measured rate (9/10). It weakens only at 1.5 times the rate.
- **P4: wrong in direction.** #3 and #5 hold on the strict consensus corpus. #3 does so only just (p = 0.05, power 0.88).
- **P5: mostly right.**
  - Structured noise is about as harsh as uniform noise at the same rate for #1 (0.27-0.36 vs 0.26-0.28), #3 (0.41-0.61 vs 0.43-0.56) and #6. Text-final deletion did not hurt #3.
  - It is harsher for #7: 8 of 10 seeds pass vs 5 of 5, and the share falls to 0.70-0.87 vs 0.76-0.90. That comes from the 2.1% whole-text reversals, not from substitutions.

## Limits

- **Shared errors are invisible.** ICIT drew on the same photographs and on M77, so 12.9% is disagreement, not error. struct x1.5 is the allowance for shared error; every finding except #10b (3/5) still holds there.
- **2,741 of the 3,210 links are made through the signs themselves** (accepted at distance 0.5 or less). Texts where the editors disagree badly fail to link and drop out of the consensus corpus, so the consensus corpus is "texts that both editions read similarly". The register-linked texts (469) are unbiased but small; cons_sign_reg and icit_reg use only those, and every test holds there too.
- **ICIT readings put into M77 space keep about 5.8% of tokens as bare Wells labels** (761 of 13,073 in icit_ext), signs with no Mahadevan partner. They act as unknown signs, which slightly favours the null in sign-specific tests.
- **f = 1 attributes all disagreement to M77.** Neither edition is treated as the truth.
- The 105 unmapped tokens on matched texts are left out of the rate. If they disagreed as often as the rest, the rate would not change. If every one of them disagreed, the rate would be 17.4%, still inside the x1.5 bracket (19%) where everything but #10b holds.
- **The register sample is 1930s material from three sites.** The sign-linked texts extend coverage to Lothal and Kalibangan, but no post-1977 site is in M77.
- **#2, #4 and #8 were not run**, as in the audit.
- The fish fix was not applied to `signlist_robustness/harness.py` (another agent's folder). Nothing here needed it, because set-level tests are unaffected.

## Recommended README changes (for the lead)

1. **Known weaknesses, line 98.** Replace with:
   > "The two editions often read a sign differently. On 469 objects matched through the 1930s registers (not by their signs), Mahadevan and Wells/Fuls disagree on 13% of signs (95% CI 11-15%) once our own sign-mapping errors are fixed (the fish pairing and Wells' single signs for doubled Mahadevan signs); the uncorrected figure was 19%. Most of the rest is missing signs (often at the text start) and a long tail of single-sign differences. All nine headline tests still pass on the signs both editions agree on, on Wells/Fuls's readings of the same objects, and under noise copying this error pattern at the measured rate (`experiments/consensus_corpus/`)."
2. **#7.** Append:
   > "Neither edition confirms the other here: only 8 left-to-right lines have the same direction label and the same signs in both editions (7 of 8 as labelled, too few to test)."
3. **#10.** After "...assumes direction is known text by text", add:
   > "At the measured transcription disagreement (13%) it still passes in 9 of 10 noise runs, but at 1.5 times that rate in only 3 of 5; it is the headline finding most sensitive to transcription."
4. **#1, #3, #5, #6, #9, #11.** No change needed. Optionally add "holds at the measured 13% editorial disagreement" where the row already lists robustness.
5. **docs/ASSUMPTIONS.md A3.**
   - Change "transcription has random errors up to 10%" to "...the editions disagree on 13% (11-15%) of signs; all nine tests hold at that rate and structure".
   - Keep "medium-high" risk for claims on fewer than about 20 texts.

## Files

- `cooc.py`: mapping-free co-occurrence.
- `concordance.py`: corrected concordance (rules R1-R5).
- `disagree.py`: rates with confidence intervals, the R6 doubled-sign rule, the top-20 table and the error model.
- `corpora.py`: the consensus and either-edition corpora.
- `run.py`: the tests and the noise model.
- `summarise.py`: `table.md`, `results.json`, `ledger_rows.csv`.
- `CONCORDANCE.md`, `corrected_concordance.csv`, `out/concordance.json`: the mapping for other agents.
- `out/`:
  - `disagreement.json`, `error_model.json`, `alignments.json`, `seq_links.json`;
  - `corpora/*.json`, `runs.jsonl` (33 runs), `noise_calib.json`.
- `ledger_rows.csv`: 99 robustness rows (11 condition families x 9 tests, mode `robustness`, not new claims).
