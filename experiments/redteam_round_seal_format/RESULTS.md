# Red team of #39 round-seal format (board #41)

**Verdict C1, the closer deficit: SURVIVES.** Round seals end in a grammar closer far less often than matched square seals. It holds under every closer definition, shape subset, reading variant and leave-one-out drop I tried. The weakest version is "jar sign W740 only": 14% vs 33%, p = 0.023.

**Verdict C2, "format explains only 24% of the off-order": WEAKENED.** The 24% comes partly from a code bug in #39:
- #39's opener and closer sets never included W817, W861, W154, W156, W526 or W527. Its code split `"W817;W861"` on spaces, so those signs were never matched.
- With the bug fixed, the same matching removes **36%** of the Kneser-Ney order excess (CI 31-41%), not 24%.
- Under the Wells class-bigram grammar it removes 42%.
- Under a positional model it removes 54%, and what is left is not significant.
- The broadest format definition I pre-registered removes 42% (KN), 51% (grammar) and 71% (positional).

Under the two n-gram scorers, an order excess of +1.2 to +1.35 bits/sign remains after every format match (p = 1e-4). So "format does not explain the off-order" still holds for bigram order, but "only a quarter" overstates it. **Format explains roughly 35-50% of the bigram excess**, and most of what a position-only model can see.

**Shape labels:** "round" is not a single, cleanly recorded type, but that does not drive either claim.
- 7 of the 35 round texts are cylinders, not Gulf stamp seals.
- 5 of the 8 home round texts rest on ICIT's type code alone.
- Only 3 of 35 have recorded dimensions.

Dropping the cylinders, or keeping only foreign Gulf-type seals plus the 3 register-confirmed home seals, changes neither claim. These are true SEAL:C/CY records. README #4's error (SEAL:R, 97% rectangular) does not recur here.

**Disputed Gulf readings do not drive either claim.**
- Leave-one-out over the 28 closer-test texts: max p = 0.0005.
- Leave-one-out over the 31 scorable texts: the explained fraction stays between 35% and 37%.
- Keeping only "confirmed" readings, or switching to the foreign_corpus alternative readings, leaves both results unchanged. The alternatives are 3 reversed texts, 3887.1 replaced by the M77 text, and new ends for 3898.1 and 5222.1.

**Find-spot effect (#41 item 4):** the test of 7 square seals found abroad has power of only **0.27 against +0.5 bits/sign** (0.62 against +1.0). #39's "not detected, power 1.0" refers to full shuffling only. A moderate find-spot effect cannot be excluded.

Pre-registration: `docs/prereg/redteam_round_seal_format.md`, sha256 b3a27917…, appended to HASHES.txt before any statistic was computed. The bug was found by reading the code before pre-registering; this is disclosed there. Code: `run.py`, one run of about 20 s via board/run.sh. Outputs: `results.json`, `run.log`. Ledger: `ledger_rows.csv`.

## C1: closer deficit (round lower; one-sided; 10,000 site × length-matched draws as #39)
| variant | round | matched square | p |
|---|---|---|---|
| A0 replication (#39's buggy sets) | 4/28 = 0.14 | 0.45 | 1e-4 |
| **A1 corrected closer set (primary)** | 4/28 = 0.14 | 0.51 | **2e-4** |
| A2 W740 (jar) only | 4/28 = 0.14 | 0.33 | 0.023 |
| A3 any sign of a Wells-grammar "closer" class (128 signs) | 9/28 = 0.32 | 0.67 | 3e-4 |
| A4 data-driven closers (≥60% final in home squares; 14 signs) | 7/28 = 0.25 | 0.60 | 2e-4 |
| A5 complete texts only (both sides) | 3/17 = 0.18 | 0.52 | 0.002 |
| A6 plus 3 round texts #39's dedup dropped | 4/31 | 0.49 | 1e-4 |
| A7 no cylinders | 4/24 | 0.50 | 6e-4 |
| A7b Gulf-type abroad + register-confirmed home only | 3/19 | 0.54 | 9e-4 |
| A8 "confirmed" foreign readings only | 3/17 | 0.52 | 0.003 |
| A9 alternative readings | 4/29 | 0.51 | 1e-4 |
| A10 leave-one-out (28 drops) | max p 5e-4 (drop 148.1) | | |
| A11 closer *first* (reading-direction check, two-sided) | 2/28 vs 0.007 | | 0.03 |

A11 needs a caution. The 2 "closer-first" round texts are 122.1 (`W740` alone) and 5230.1 (`W740 | W740`, middle element a motif). Each consists of the jar sign and nothing else. They are not evidence of reversed reading.

Two notes on what the closer-last cases are:
- Of the 4 closer-final round texts, 2 are these jar-only texts.
- Only 3889.1 and 5222.1 end a real text with W740.

So closer-final round texts are rarer still than 14% suggests. The deficit is genuine. On the discovery set it remains not independently replicated, as #39 said.

## C2: share of the order excess explained by format (round n = 31)
Order excess per text, d, is real bits minus the mean of up to 200 permutations. Home texts are scored by 10-fold CV models and foreign texts by the full home model. Fraction = 1 − E_format / E_length. CI by bootstrap over round texts.

| format definition | KN: frac (CI); E_F, p | Wells grammar | positional |
|---|---|---|---|
| E_length (no format) | +2.10 | +1.64 | +0.45 |
| F0b #39 key, buggy sets (replication) | **0.23** (0.18-0.29); +1.62, 1e-4 | 0.28 | 0.35 |
| F0 #39 key, corrected sets | **0.36** (0.31-0.41); +1.35, 1e-4 | 0.42 (0.36-0.49) | **0.54** (0.35-1.07); p 0.075 |
| F1 W090/W091 anywhere | 0.05 | 0.01 | 0.16 |
| F2 numeral anywhere | 0.02 | 0.04 | 0.10 |
| F3 closer-free | 0.30 | 0.37 | 0.35 |
| F4 first × last sign class (16/31 fell back) | 0.15 | 0.19 | 0.30 |
| F5 F0 + rare-sign load | 0.37 | 0.42 | 0.54; p 0.069 |
| F6 round-like composite (no opener first, no closer, W090/091 or numeral) | **0.42** (0.37-0.47); +1.22, 1e-4 | **0.51** (0.43-0.60); +0.81, 1e-4 | **0.71**; p 0.16 |

The pre-registered rule required all 21 cells to sit below 0.5 with a significant remainder. Four cells fail: grammar F6, and positional F0, F5 and F6. No definition fails under 2 of 3 scorers, so the verdict is WEAKENED, not BROKEN.

**Planted check.** I built pseudo-round sets from home square seals with the round set's format mix, 200 reps per cell. Format-matching removes 96-103% of their excess under F0, F3, F5 and F6, so the matching can find a format cause when one exists. Format alone produces +0.77 (F0) and +0.88 (F6) bits/sign of KN excess, about 40% of the observed +2.10. That agrees with the main table.

**Robustness (KN, F0 corrected):**
- leave-one-out: 0.35-0.37;
- confirmed readings only: 0.37;
- alternative readings: 0.37 (grammar 0.41, positional 0.46);
- no cylinders: 0.36;
- Gulf-type + register-confirmed: 0.36;
- with the dedup-dropped texts: 0.37.

**Caveats:**
- F6 was pre-registered, but I wrote it after looking at the round texts. It is fitted to their look and may overstate what format explains.
- The positional model sees almost nothing except first-slot and last-slot preference, so format matching is bound to absorb most of its signal. Its result says the round seals' positional deviance is mostly format. It says little about bigram order.

## Find-spot power
- O2 replicates: 7 non-round seals abroad, +0.24 bits/sign, p = 0.31.
- Planted shift added to 7 length-matched home seals, 1,000 reps:
  - power 0.27 at +0.5 bits/sign;
  - power 0.62 at +1.0 bits/sign.

"Find-spot adds nothing" is therefore underpowered for any effect smaller than about 1 bit/sign.

## Shape reliability (descriptive)
Of the 35 round texts:
- 28 are SEAL:C and 7 are SEAL:CY (cylinders: 3882.1 Susa, 3888.1, 5557.1, 5468.1, plus the dropped 1924.1 and 3669.1).
- Dimensions are recorded for 3. Two of them have equal width and height: 2419.2 at 19.1 mm and 5231.1 at 25.5 mm.
- All 23 foreign and unprovenanced texts appear in foreign_corpus.csv as round, Gulf/Dilmun or cylinder, except 5557.1, which is not in that file.
- Home round texts confirmed in a printed register: 3 of 8 (M-415, M-416, M-500, per #25).

No SEAL:R object is in the set. The 97%-rectangular "home round" error behind README #4's correction does not recur. The remaining weakness is the 5 home texts that rest on the type code alone.

## Hypotheses
| hypothesis | verdict |
|---|---|
| Closer deficit is an artefact of closer definition, broken ends, shape labels or disputed readings | refuted (all 11 variants p ≤ 0.023; LOO max 5e-4) |
| Format explains only ~24% of the round-seal order excess | refuted as a number: 36% (KN) to 42% (grammar) with corrected sets, up to 51% (grammar, composite format) |
| Format explains most of the order excess | not supported for bigram order (KN/grammar remainder +0.8 to +1.35 bits/sign, p = 1e-4); supported for positional deviance (54-71%, remainder n.s.) |
| A few disputed Gulf readings drive either claim | refuted (LOO and reading variants stable) |
| A +0.5 bits/sign find-spot effect would have been detected | refuted (power 0.27) |

## For README #4
- No change to the headline.
- If any README text cites "format explains only a quarter", change it to "format explains about a third to a half of the bigram order excess. A clear excess of about +1.2 bits/sign remains."
- Add that the find-spot null is underpowered below about 1 bit/sign.

## Not done / limits
- No independent data. Same 35 texts as #34 and #39.
- The grammar's sign classes were fitted on all ICIT texts, including the round ones (35 of about 4,000). I re-estimated only its counts.
- I did not rerun #39's other tests (F1-F3, O1b, O3) with the corrected opener set. F2 (opener-first) will move a little, because W817/W861 openers now count.
