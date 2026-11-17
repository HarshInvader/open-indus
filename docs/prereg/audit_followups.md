# Pre-registration: three follow-up checks from the assumption audit (#27)

Board task #28 (check A) plus two checks recommended in `docs/ASSUMPTIONS.md` (A3, A16). Written 2026-11-17 before any of the three was run. Code: `experiments/audit_followups/{a_order_formats,b_editor_agreement,c_tick_complete}.py`, hashed with this file in `docs/prereg/HASHES.txt` (tag `audit_followups`). Every run goes through `board/run.sh`.

## A. Does README #1's order test separate grammar from a fixed format? (A12, board #28)

**Test.** `signlist_robustness/harness.py` `t1_order`, unchanged: a bigram (add-0.1) trained on dev runs; for each held-out run of 3-7 signs with at least 6 distinct orderings, does the real order score strictly above every other ordering? Share of such runs, against chance (mean of 1/number of orderings).

**Indus.** M77, split v2, type unit (the base of the audit: 0.40 vs 0.057 expected).

**Comparison corpora** (`experiments/short_labels/sl_corpora.py`, whole units of 1-17 tokens, distinct units only):
- Primary writing (6): cun_seal_ur3, cun_seal_ob, linb_line, egy_nom, lat_label, lat_short.
- Primary real codes (7): heraldry, khipu, icd10, emoji, chess_eco, chords, metar.
- Sensitivity only: cun_seal_oakk, lina_label (pools smaller than Indus), plates, slot, sigil (synthetic codes).

For each corpus and each of 5 seeds: sample min(pool, 2,270) distinct units (Indus dev + held-out size), split 75/25 by near-copy family (edit distance ≤ 1 clusters, as the ICIT split), run t1_order. Because the share depends on run length, the **primary statistic S** is the share standardised to the Indus held-out run-length mix (lengths 3-7, weights = Indus qualifying runs per length; lengths absent in a corpus dropped and weights renormalised). Corpus value = median S over the 5 seeds. S_I = Indus S.

**Decision rule (fixed now):**
- **Cannot separate** (README #1 cannot claim grammar from this test): at least 2 of the 7 primary real codes reach S ≥ 0.75 × S_I.
- **Separates** (modest support for a linguistic reading of #1): every primary code has S < 0.5 × S_I, and at least 4 of the 6 primary writing corpora reach S ≥ 0.75 × S_I.
- Otherwise **undecided**.

**Prediction.** Cannot separate: field-ordered codes (METAR, ICD-10, chess openings) have fixed order by construction.

**What it changes.** Cannot separate: #1 keeps "fits a grammar or a fixed formula equally" (already applied) and nothing in the project may cite #1 as evidence of language. Separates: README may add that the test separates codes from writing in our calibration set. Undecided: no change. The structural fact (#1's 0.40 vs 0.057) is not retested and does not change.

## B. Sign-by-sign disagreement between Mahadevan (M77) and Wells/Fuls (ICIT) (A3)

**Matching.** Objects linked in `experiments/old_registers/registers.csv` to both an M77 text number and an ICIT record. These links come from register serials and field numbers, not from the signs, so matching does not select for agreement. Each M77 side is compared with the best-matching ICIT record of that object (lowest distance; a small bias toward agreement, stated).

**Comparison.** M77 signs mapped to Wells labels through the bridge with harness.py's overrides; two tokens agree if their label sets overlap. Breaks and line marks removed. Optimal string alignment gives:
- **different sign** (substitution, both sides mapped);
- **missing/extra sign** (insertion or deletion);
- **order** (adjacent transposition; and, per text, whether some other order of M77's lines would align better);
- **direction** (per text: does the reversed M77 sequence align better than the forward one; and the labelled directions where both editions give one);
- substitutions involving an M77 sign with no bridge entry are counted as **unmapped**, reported, and left out of the rate.

**Link errors.** A pair with normalised distance > 0.8 is a probable link error, reported and left out of the primary rate. A random-pair baseline is reported beside it.

**Primary statistic.** Disagreement rate per compared M77 token (different + missing/extra + order), with a 95% bootstrap CI over texts. Also each component, the share of texts with any disagreement, and direction disagreement per object.

**Reading against the audit (fixed now):**
- **Within tolerance:** upper 95% CI of the per-token rate < 10% (the audit's highest noise level, at which every headline test held) and direction disagreement per object < 10% (the level at which #7 and #10b missed their bars).
- **Beyond tolerance:** point estimate ≥ 10% for tokens, or ≥ 10% for direction.
- Otherwise **undecided**.

This measures where two editors differ, not the true error rate: shared errors are invisible (ICIT drew on the same photographs and on M77), and bridge mismatches add spurious disagreement. Selection bias: only seals from the 1930s Mohenjo-daro, Harappa and Chanhu-daro registers can be matched.

## C. README #3 on complete single-line texts only (A16)

**Test.** harness.py `t2_tick`, unchanged (M77, split v2, type unit; ticked fish M60/66/68/71/73 vs plain M59/65/67/70/72; null = random sets of signs with dev frequency 10-80, 2,000 draws, rng seed 7), with the held-out set restricted to texts marked complete and containing no '|' and no '#'. A sign before a break or a line end can then never count as final.

**Pass bar = the original bar:** p < 0.05 and ticked final share > plain final share.

**Secondary (reported, not decisive):** token unit; ICIT variant with ICIT's own completeness flag.

**What it changes.** Pass: #3 holds; README adds "holds on complete single-line texts". Fail with ticked share still above plain: weakened; README notes it. Ticked share at or below plain: fails; #3 is withdrawn pending review.
