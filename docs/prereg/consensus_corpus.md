# Pre-registration: consensus corpus and the nine headline tests at the real transcription error rate

Board task #35 (M6), agent N3, 2026-11-18. Folder `experiments/consensus_corpus/`. Written and hashed before any of the conditions below was scored. Only the descriptive steps (concordance, disagreement rate, corpus sizes) have been run; they fix inputs, not test outcomes.

## Question

The two editions disagree on far more signs than the 10% random noise at which the assumption audit (#27) found the nine headline tests robust (#29: 19.4%). Do the nine tests still hold (a) on the signs both editions agree on, (b) when the matched texts are read the way Wells/Fuls read them, and (c) under noise at the measured disagreement rate with the measured error structure?

## Inputs fixed before scoring

- **Corrected concordance** (`concordance.py`, `out/concordance.json`, `corrected_concordance.csv`). It is the harness ICIT mapping plus rules R1-R6:
  - R1-R5 are applied to mapping-free same-position co-occurrence on the 395 equal-length register-matched pairs. They fix the fish pairing (M65=W235, M67=W240, M70=W231, M72=W233, M66=W236; ticked M68/M71/M73 by analogy) and add M389=W806.
  - They add three alternates (M175, M205, M210) and narrow three one-to-many entries (M162, M216, M387).
  - R6 adds Wells' single signs for doubled Mahadevan signs: M245+M245=W617, M176+M176=W401, M375+M375=W792 as primary; others provisional.
  - The primary map is used everywhere below. Provisional entries are reported only in the disagreement rate.
- **Measured disagreement** (`disagree.py`, primary map, 469 register-matched texts): 12.9% of compared signs (CI 11.1-14.9%). It splits into identity 7.3%, M77-only sign 4.0%, ICIT-only sign 1.0% and adjacent order 0.6%; whole-text direction differs in 2.1% of texts. `out/error_model.json` holds the full structure: per-sign substitution counts and targets, inserted and deleted signs, and position of deletions and insertions.
- Tests: `experiments/signlist_robustness/harness.py` T1-T9, unchanged. They run with the same frozen bars, M77 sign space, type unit and split v2, called the way `experiments/assumption_audit/sens.py` calls them, with sens.py's helpers imported. Held-out membership is fixed from the original M77 text (`key0`), as in sens.py.

## Conditions (`corpora.py`, `run.py`)

Links between an M77 side and an ICIT record:
- **reg**: the 469 register-matched texts (#29).
- **seq**: for every other M77 side, the best same-site ICIT record by normalised alignment distance under the primary map, accepted at <= 0.5. This link is made through signs, so it is biased toward agreement; the bias is stated, not corrected.
- **ext** = reg + seq.

Partial-agreement policy (fixed now):
- **Sign level.** A sign the editions disagree on (substitution, M77-only, transposed pair) becomes a break `#`. A sign only ICIT has adds a `#` at its position. A text with any mask counts as incomplete.
- A sign with no concordance entry is unverifiable, not disputed, so it is kept.
- **Text level.** A text with any disagreement is dropped.
- **Direction lines (T5).** In consensus corpora a linked object's lines are kept only if the object has no disagreement and both editions give the same direction label.

| condition | what | role |
|---|---|---|
| base | M77 as published (must reproduce sens.py base) | check |
| cons_sign_ext | ext texts, disputed signs masked; unlinked texts dropped | **(a) primary consensus** |
| cons_text_ext | ext texts with no disagreement only | (a) strict |
| cons_sign_reg | reg texts masked, all other texts unchanged | (a) secondary |
| icit_ext | ext texts take ICIT's reading (mapped to M space; ICIT segments and direction labels for T5); others M77 | **(b) either-edition pair with base** |
| icit_reg | same, reg texts only | (b) |
| match_m77 / match_icit | the 469 reg texts only, M77 reading vs ICIT reading | (b) same texts, two readings (low power, expected) |
| struct100_s1..10 | structured noise at the measured rate (f = 1.0) on the whole corpus | **(c) primary** |
| struct50_s1..5 / struct150_s1..5 | f = 0.5 (errors split evenly between editions) / f = 1.5 (allowance for errors both share, about the uncorrected 19%) | (c) bracket |
| unif100_s1..5 | sens.py random-by-frequency substitution at the same total rate, no structure | (c) comparison |

The structured noise model (`run.py` class Noise), scaled by f:
- **Reversal.** Each object is reversed with probability 2.1%·f.
- **Deletion.** Each sign is deleted at the measured position-specific rate: text-initial, medial or final.
- **Substitution.** The per-sign rate is shrunk to the mean: (s_x + 10·0.073)/(n_x + 10). The target is drawn from that sign's observed ICIT substitutes (mapped to M space) with probability s/(s+1); otherwise sens.py's look-alike draw is used.
- **Insertion.** Insertions happen at the measured position-specific rates. The inserted sign comes half from the observed ICIT-only signs and half from a frequency-weighted random draw.
- **Transposition.** Adjacent pairs inside a run are transposed at 0.6%·f.
- Lines for T5 are damaged the same way, with independent draws.
- **Calibration.** The full M77 corpus has more short texts and a different sign mix than the matched texts. So all component rates are multiplied by one constant c (`run.py` `calibration()`, cached in `out/noise_calib.json`). It is chosen so that f = 1 realises the measured 12.9% as edit distance per M77 sign on the whole corpus. A check before calibration gave 10.9% at c = 1.


## Verdict rules (per finding; tests map to README findings as in sens.py: T1 #1, T2 #3, T3 #5, T4 #6, T5 #7, T6 #10a, T7 #10b, T8 #11, T9 #9)

- **Pass** means the harness `survives` flag is true (frozen bar).
- **Direction** uses the same rules as `assumption_audit/summarise.py` `effect()`: T1 share > chance; T2 ticked share > plain and > null mean; T3 k/n > base; T4 mean AUC > 0.60; T5 share > 0.5; T6 len1 > 0.14 and standalone > 0.11; T7 share > 0.5; T8 at least 1 sub-test; T9 coverage > shuffle.
- For a seeded family:
  - **holds** if it passes in >= 80% of seeds (struct100: >= 8 of 10; 5-seed families: >= 4 of 5);
  - **weakens** if it misses that but keeps direction in >= 80% of seeds;
  - **fails** otherwise.
  - The pass fraction across seeds is reported as the **power to keep passing** at that error level.
- For a single corpus: **holds** = pass; **weakens** = direction kept but bar missed; **fails** = direction lost; **NT** = test undefined.
- **Underpowered.** For T2, T3, T5 and T7 (count tests), power is computed by simulation (2,000 draws). The base effect size is used at the condition's own n and null, so a miss there can be told from a loss of effect. If such a test misses its bar where power < 0.8, the cell is labelled **underpowered** instead of weakens or fails. T1, T4, T6, T8 and T9 report their margin over the bar.
- **Overall verdict at the real error rate**, per finding:
  - **holds** if it holds on cons_sign_ext, icit_ext and struct100.
  - **fails** if it fails (direction lost) on any of the three.
  - **weakens** otherwise.
  - "Underpowered" cells do not count against a finding, but they are named.
  - struct50, struct150, cons_text_ext, the reg variants, matched-only and unif100 are sensitivity analyses. They are reported and do not change the overall verdict.

## Predictions (written before scoring)

- P1. #1, #6, #10a, #9 and #11 hold everywhere in the primary three. These are large-n or large-margin tests that held at rev50 and at 10% noise.
- P2. #7 (L-R reversals) weakens or fails on icit_ext. ICIT relabels 13 of 21 matched L-R objects, and #7 already missed its bar at 10% reversal. It holds on the consensus corpus if enough lines survive, and is otherwise underpowered.
- P3. #10b (pair order) weakens under struct100. It sat at 0.79 against a 0.75 bar and dropped below the bar at 10% reversals.
- P4. #3 and #5 hold under struct100 but may become underpowered on cons_text_ext (fewer ticked fish and six-fish tokens survive).
- P5. Structured noise at 12.9% is no harsher than uniform noise at the same rate for most tests, because much of the structure is deletion at text edges. Exception: #3, where final-sign deletion acts directly on the measured quantity.

## Multiple comparisons

These are robustness reruns of already-registered tests (mode `robustness`), not new claims. There are 9 tests × 11 condition families. No new p-values enter the ledger as claims.

## Limits declared in advance

- Errors both editors share are invisible.
- The seq links are made through signs.
- f = 1 treats every disagreement as an M77 error, which is conservative for M77 but ignores errors in ICIT.
- Unmapped signs (5% of M77 tokens on matched texts) are left out of the rate.
- The matched texts are 1930s Mohenjo-daro, Harappa and Chanhu-daro objects only.
