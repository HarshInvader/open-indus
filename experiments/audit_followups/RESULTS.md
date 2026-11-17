# Three follow-up checks from the assumption audit (#27)

Board tasks #28 (A), #29 (B), #30 (C). H13, 2026-11-17. Pre-registration: `docs/prereg/audit_followups.md`. It and the three scripts were hashed in `docs/prereg/HASHES.txt` (tag `audit_followups`) before any of them ran. All runs went through `board/run.sh`.

## Verdicts

| check | question | verdict | what changes |
|---|---|---|---|
| A (#28) | Can README #1's order test tell grammar from a fixed format? | **Cannot separate**. For #1 as a sign of grammar: **weakened**. The order fact itself is untouched | README #1 now says codes pass the test too |
| B (#29) | How often do Mahadevan and Wells/Fuls read the same sign differently? | **Beyond the audit's tolerance**: 19% of signs differ (95% CI 17-21%), against the 10% the audit tested. For assumption A3: **weakened** | A new "known weakness" line in README. No finding changes status |
| C (#30) | Does #3 survive when a sign before a break or line end cannot count as final? | **Holds**: 9 of 16 ticked fish are final, against 2% of plain fish (p = 0.006) | README #3 notes that it holds on complete single-line texts |

---

## A. The order test on codes and fixed formats (#28)

**Verdict: cannot separate (pre-registered rule met).** Four of the seven real codes beat every reordering of their own tokens at least as often as Indus does: heraldic blazons, emoji sequences, named chess openings and weather reports (METAR). So README #1's test shows that order is fixed and structured. It cannot show that the structure is grammar. The order fact (0.40 against 0.057 by chance) was not in question and stands.

**Method.** `t1_order` from `signlist_robustness/harness.py`, unchanged. For each corpus and 5 seeds:
- sample up to 2,270 distinct whole units of 1-17 tokens (the Indus dev plus held-out size);
- split them 75/25 by near-copy family;
- fit the bigram on dev;
- on held-out runs of 3-7 tokens, measure the share whose real order beats every reordering.

S is that share standardised to the Indus run-length mix. Indus is M77, split v2, type unit: **S_I = 0.402** (raw 0.402 on 321 runs, 7.1x chance). The pre-registered bars were 0.75 x S_I = 0.30 and 0.5 x S_I = 0.20.

| corpus | kind | S (median of 5 seeds) | seed range | raw share / chance ratio |
|---|---|---|---|---|
| **Indus (M77 held-out)** | ? | **0.40** | - | 7.1 |
| METAR weather reports | code | 0.98 | 0.98-0.99 | 176 |
| chess openings | code | 0.63 | 0.22-0.70 | 28 |
| Old Babylonian seal legends | writing | 0.60 | 0.53-0.65 | 23 |
| emoji sequences | code | 0.60 | 0.00-0.81 | 26 |
| heraldic blazons | code | 0.49 | 0.38-0.66 | 22 |
| Ur III seal legends | writing | 0.47 | 0.44-0.47 | 31 |
| Linear B entry lines | writing | 0.34 | 0.26-0.43 | 6.6 |
| Egyptian verbless phrases | writing | 0.24 | 0.24-0.29 | 5.3 |
| pop chord phrases | code | 0.23 | 0.13-0.25 | 4.2 |
| ICD-10 codes | code | 0.13 | 0.11-0.41 | 15 |
| Latin labels and stamps | writing | 0.11 | 0.06-0.13 | 1.6 |
| Latin short inscriptions | writing | 0.10 | 0.06-0.16 | 1.9 |
| khipu | code | 0.09 | 0.06-0.14 | 1.3 |
| *sensitivity:* synthetic SIGIL / slot code / plates | code | 0.57 / 0.46 / 0.00 | | |
| *sensitivity:* Old Akkadian seals / Linear A labels | writing | 0.24 / 0.16 | | |

**Decision rule:**
- 4 of 7 codes reach 0.30. The rule needed 2, so "cannot separate" applies.
- The "separates" branch was not met: not every code is below 0.20, and only 3 of 6 writing corpora reach 0.30.
- Indus sits in the middle of both groups.
- Prediction: right. Field-ordered codes pass easily. Formulaic seal legends (Ur III, Old Babylonian) also pass, and free-word-order Latin barely beats chance.

**What it means.** On this test, high scores go with formulaic, fixed-slot text, whether it is language or not. Languages with freer order score low. "Real order beats every reordering" is therefore evidence of a fixed format. It is no evidence for language over code.

**Limits:**
- Emoji and ICD-10 vary a lot with the seed: some seeds have few qualifying runs. The verdict does not depend on them, because heraldry, chess and METAR alone give 3 codes above 0.30.
- Synthetic plates score 0: their tokens are one-off letters and digits, so the bigram has nothing to learn. Plates are sensitivity only.
- Comparison units are whole objects, while Indus runs exclude breaks. The length standardisation handles length, not other differences between genres.

## B. Mahadevan vs Wells/Fuls, sign by sign (#29)

**Verdict: beyond tolerance (pre-registered rule), so assumption A3 is weakened.**
- On objects matched without looking at their signs, the two editions disagree on **19.4% of compared signs (95% CI 17.4-21.4%)**. Half of the texts (50%) have at least one difference.
- This is above the 10% random noise at which the audit found every headline test still held.
- Direction is within tolerance. Reversing one edition's sign order aligns it better in **2.1% of texts (CI 0.9-3.4%)**. The labelled directions disagree on **2.9% (13 of 454)**. Both are under the 10% at which #7 and #10b missed their bars.
- No finding changes status. Read the caveats below before reading 19% as an error rate.

**How many texts could be matched, and the bias.**
- 491 rows of the 1930s excavation registers link to both an M77 text and an ICIT record, through serial and field numbers rather than signs. They cover 489 objects and 562 sides.
- 93 pairs (17%) have a normalised distance above 0.8 and are treated as probable link errors. For comparison, the median random pair scores 1.0, and 12% of random pairs fall at or below 0.8.
- That leaves **469 compared texts with 1,923 compared signs**. 123 more substitutions involve an M77 sign with no bridge entry and are left out.
- Who is in the sample:
  - sites: Mohenjo-daro 307 texts, Harappa 156, Chanhu-daro 6;
  - object types: 342 seals, 81 miniature tablets, 46 sealings;
  - nothing excavated after 1940, no pottery or copper tablets, no Lothal, Kalibangan or Dholavira.
- Mean length is 4.4 signs, against 3.9 for all of M77.
- So this is the best-documented part of the corpus: old, large-site, published with plates. Disagreement elsewhere is unlikely to be lower.
- Each M77 side was compared with its best-matching ICIT record, a small bias toward agreement (pre-registered).

**How the 19.4% splits** (per compared sign):

| kind | rate | 95% CI | count |
|---|---|---|---|
| different sign identity | 12.9% | 11.4-14.4% | 249 |
| missing or extra sign | 5.6% | 4.3-6.9% | 107 (87 only in M77, 20 only in ICIT) |
| order (adjacent swap) | 0.9% | 0.5-1.3% | 17 |
| line order (another order of M77's lines fits better) | 0.4% of texts | | 2 |
| direction (reversed sequence fits better) | 2.1% of texts | 0.9-3.4% | 10 |

**Exploratory (not pre-registered): about a third of the "different sign" cases are our own mapping, not the editors.**
- 47% of substitutions are (M77, Wells) pairs that recur 3 or more times.
- The four largest are plain fish: M67->W240 (39 times), M65->W235 (24), M72->W233 (22), M70->W231 (11). Ticked M66->W236 adds 3.
- `signlist_robustness/harness.py` hard-codes the fish pairing as M59/65/67/70/72 -> W220/231/233/235/240 (and ticked M60/66/68/71/73 -> W226/232/234/236/241). The data say the plain pairs are out of order: M65=W235, M67=W240, M70=W231, M72=W233.
- Every test that uses the fish uses them as whole sets (ticked vs plain; the fish class), so no landed result changes. Anyone who maps a single fish sign between lists must fix this first.
- Other recurring pairs (M328<->W033/W700 and M89, M245->W617, M155->W072) look like bridge swaps or consistent differences in how the two lists divide a sign. Those differences are what `signlist_robustness` already tests.
- Treating every recurring pair as an equivalence, disagreement is **12.8% (CI 10.9-14.8%)**: 6.9% different sign and 5.6% missing or extra. That is still above 10%.
- With a stricter link-error cut (0.5), the rate is 14.5%.
- So the honest range for real editorial disagreement on this sample is **about 13-19% of signs**.

**Exploratory: left-to-right labels.** 21 matched objects are labelled left-to-right by Mahadevan. Wells/Fuls label 13 of them right-to-left. In 6 of those (all two-sign side-2 texts of Harappa tablets) ICIT also gives the signs in the reverse order. M77's left-to-right labels are the basis of #7. Under ICIT's own labels, #7 is 19 of 23 lines (0.83, p = 0.0013), just missing the p < 0.001 bar (`signlist_robustness/raw/ICIT.json`). This fits the audit's finding that #7 depends on direction labels line by line.

**What this does and does not mean:**
- It is disagreement, not error. Errors shared by both editors are invisible, because ICIT drew on the same photographs and on M77. Bridge mismatches add spurious disagreement.
- It is not random noise. It concentrates on particular sign pairs (systematic) and on missing or extra signs at damaged edges.
- Systematic differences are the sign-list question, and `signlist_robustness` already reran every headline test on Wells/ICIT readings: #1, #6, #9, #10a and #11 pass there.
- The audit's sentence "corpus findings tolerate the plausible error rate" should change to: "they tolerate 10% random error; the editors disagree on 13-19% of signs, much of it systematic. The ICIT reruns, not the noise runs, are the evidence that the findings survive this."

## C. #3 on complete single-line texts only (#30)

**Verdict: holds (original bar: p < 0.05 and ticked share above plain share).** Some texts have a sign before a break or a line end. Restricting held-out to complete single-line texts takes it from 571 to 415, and the ticked fish still close the text:

| set | held-out texts | ticked fish final | plain fish final | null mean | p | bar |
|---|---|---|---|---|---|---|
| M77 type (primary), original | 571 | 11 of 19 (0.58) | 0.07 | 0.19 | 0.004 | pass |
| **M77 type, complete single-line** | **415** | **9 of 16 (0.56)** | **0.02** | 0.17 | **0.006** | **pass** |
| M77 token, complete single-line | 641 | 10 of 18 (0.56) | 0.02 | 0.16 | 0.010 | pass |
| ICIT type, complete single-line | 1,193 | 20 of 36 (0.56) | 0.05 | 0.19 | 0.026 | pass |
| ICIT token, complete single-line (base also failed, p = 0.087) | 1,830 | 20 of 41 (0.49) | 0.05 | 0.18 | 0.072 | fail |

The restriction barely moves the ticked share (0.58 -> 0.56). It lowers the plain-fish share (0.07 -> 0.02), so break-final and line-final positions had been inflating the comparison group, not the effect. The audit's worry (A16) is answered for #3. The sample stays small (16 ticked tokens).

## What was not checked

- **A** used `t1_order` only. A test built to separate grammar from format (for example, whether order constraints reach beyond adjacent signs) was not run. The comparison set still has no real emblem system of the seal genre (short_labels).
- **B** covers only register-matched 1930s objects. It cannot see errors the two editors share. The fish mapping fix has not been applied to `harness.py`, which belongs to another agent's folder. It is flagged for the lead.
- **C** reran T2 only, not the ICIT-native count (40 of 73) in README #3.

## Files

- `a_order_formats.py`, `b_editor_agreement.py`, `c_tick_complete.py` (pre-registered); `b2_explore.py` (exploratory, written after B ran).
- `out/*.json`: full outputs, including every matched pair in `out/b_editor_agreement.json`.
- `ledger_rows.csv`.
