# meaning_calibration (sealed before the kill test): does our fixed-partner test separate true from uninformed meaning claims in a read script?

Agent `paper`. Main line (a).
- Fable study 1 of 2026-11-23.
- Revised after two Fable reviews (2026-11-23 and 2026-11-24). The second review's eight fixes are applied, and it checked feasibility on DAMOS read-only.

## Why
- 44 of 65 scorecard rows are meaning claims. The scorecard's calibration rows test sound keys only, so S and R meaning rows carry no measured error rate.
- This study measures the error rate of the form behind the two S meaning rows. It asks:
  - how often the form refutes a **true** claim;
  - how often it lets an **uninformed** claim survive.
- Both are measured on a read script cut to Indus size.

## Which rows this can calibrate
| scorecard row | tier | test form | here |
|---|---|---|---|
| MC-PAR-murukan-partners | S | **F** fixed partner vs pseudo-partner sets (`p34.rule4`), dev then held-out | calibrated |
| MC-WEL15-fish-number | S | **F** (numeral + sign), dev then held-out | calibrated |
| MC-MUK19-stroked-jar-MET | R | **E** object-class enrichment, single stage on the full ICIT corpus | **not calibrated**. The Linear B sealing and vase classes are too small for 20 powered claims; Fable's check found 8-11 powered tokens even on the full corpus. Only a power report is given (below). |
| MC-MUK23-cup-vessel-fee, MC-MUK23-licence-pairing, MC-MUK23-emblem-organisation, MC-KM-tablets-tokens, MC-LAU10-other-language | R | bespoke tests (m328_measure, tablet_archives, animal_tie_power, round_own_order) | **not calibrated**, and listed as such |

## Corpus (`experiments/meaning_calibration/`)
- **Source.** Linear B, DAMOS (`sources/paragorth_Indus-/other-scripts/linear-a/data/damos_items.jsonl`). Items with no heading or no content are skipped.
- **Unit:** one document, which is the whole item.
- **Tokens:** whole words, ideograms, measure signs, and each numeral as its own token.
- **Dropped:**
  - line numbers, word dividers, and erased text (between the erasure brackets). Quoted writing (e.g. 'ZE') is real text: the quote marks are removed and the text is kept. Under-dots are stripped and the reading is kept;
  - the DAMOS face and position labels (`α`, `β`, `γ`, `supra`, `infra`, `sup.`, `inf.`, `mut.`, `vacat`, `v.`, `r.`, `lat.`, `sigillum`, `deest`, `fragmentum`) and any other token of a closed list fixed in `load.py` before sealing;
  - any token carrying a lacuna mark (`[` or `]`) becomes a break `#`, as in the Indus code path: adjacency is not counted across it;
  - empty documents.
- **Site:** the heading prefix. **Object class** (for E only): W = sealing, Z = vase, everything else = tablet. Series letters are never a covariate.
- **Indus shape.**
  - **dev:** 1,680 documents drawn to the Indus dev length histogram (`lvc_metrics.matched_sample`).
  - **held-out:** 565 further documents, disjoint from dev, drawn to the Indus held-out lengths.
  - **Draws:** 5 dev/held-out pairs, seeds 20261124 + k for k = 0..4.
  - A claim's verdict is the **majority over the 5 draws**; ties go to U.

## Form F: fixed partner (the `parpola_rules34/p34.rule4` code path)
- **Claim:** "head X is directly followed by a partner in P". P = one main partner plus up to 2 secondary partners.
- **Observed:** the share of X's next-tokens that are in P (`p34.share_next`: text end counts as a non-partner next-token; a break does not count).
- **Null (as p34.rule4):** pseudo-partner sets {x, y}.
  - x is any token within ½-2× the main partner's frequency.
  - y is any token within ½-2× the **summed** frequency of the secondaries. With no secondaries, the set is {x}.
  - X, P and pre-specified exclusions are left out. All pairs are used.
- **Eligible heads:** ≥ 10 dev and ≥ 3 held-out next-tokens in **every** draw.
- **Survives:** dev share ≥ 0.4 and p ≤ 0.01, then held-out p ≤ 0.05.
- **Refuted:** dev share ≤ the null median, with power ≥ 0.8 for that head.
  - Power is the planted-power estimate for heads with the same dev next-token count, from the kill test.
- **Otherwise:** U. A head that is not eligible in a draw scores U in that draw.

## Claims (hashed before any test is run)
**Pool**
- The script lists the eligible heads (expected 70-78: about 35 ideograms, 25 words and 13 numerals).
- It draws 60 of them, keeping the class mix, as Writer A's pool. The rest, plus A's unused heads, form the decoy pool.

**Writer A** (fresh agent, knows Mycenaean Greek and Linear B)
- **Sees:** the 60-head pool with conventional transliterations, the full token inventory with no counts, and form F. It never sees the corpus.
- **Writes:** 30 claims. Each picks a head, gives its correct meaning, and states the partner set P that meaning implies, taken from the inventory.
- **Why A picks:** it mirrors claimants, who choose signs they believe they can read.

**Uninformed claims**
- For each of A's 30 heads, the script draws a decoy head from the decoy pool. It is class-matched when possible, otherwise any eligible head.
- **Writer B** (fresh agent, blind to A and the corpus) sees only:
  - opaque IDs;
  - each token's class (ideogram, measure, numeral, word) and length in syllables;
  - the inventory as opaque IDs with class.
- B invents a plausible meaning for each decoy, in the style of Indus claims, and derives P from it.
- **Chance baseline.** Each decoy is also scored against 50 random partner sets of B's size, drawn from the inventory. Their survival rate is reported.

## Kill test, run first (before any claim file exists)
- **F power.**
  - On each draw, plant partners: the token after a head is replaced by a partner of matched frequency, at **ceil(0.4·n)** of the head's n next-tokens, in dev and held-out alike.
  - Up to 40 eligible heads per draw are planted, and the full dev + held-out rule is applied.
  - Power is reported by dev next-token count bin (10-19, 20-49, ≥ 50) and by class.
- **F false alarm.** Random eligible heads with random partner sets of size 1-3, on a within-text shuffled corpus (`p34.shuffle_within`); 200 per draw.
- **F passes** if both hold:
  - false alarm ≤ 0.05;
  - pooled planted power ≥ 0.8 over the eligible heads.
- **If F fails,** the study stops and reports: "the form behind our S meaning rows is underpowered at Indus size in a read script". No parameter is tuned after the kill test runs.
- **E power report (no claims, no verdict).**
  - Full corpus, single stage, as `strokedjar_test.py`. The null is object-class labels permuted within site, 10,000 draws.
  - It reports how many tokens reach power ≥ 0.8 for a 2× enrichment on sealings and on sealing + vase.
  - The null mean is the exact expectation of the within-site permutation; power = P(Poisson(2·mean) ≥ Poisson 99th percentile of the mean), as in the stroked-jar test.
  - Power counts only if the null's 99th percentile is ≥ 1. A null mean of 0 scores U.

## Main measures (if F passes)
- **False-refutation rate:** the share of A's 30 claims rated R, with a one-sided 90% Clopper-Pearson upper bound. **Bar: bound ≤ 15%** (at most 1 of 30).
- **Discrimination:** AUC of the ordered verdict (S > U > R) between A's claims and B's; ties count 0.5. **Bar: ≥ 0.75.**
- **Reported:**
  - the U share; a U share above 60% for A's claims makes the form "underpowered", whatever its AUC;
  - the false-survival rate (B's claims rated S) next to the chance baseline;
  - the ideogram-head stratum separately, since numeral-after-ideogram is a Linear B convention.

## Verdicts, stated in advance
- **Both bars met:** the two calibrated S rows show the measured rates (true-claim survival; uninformed-claim survival vs chance). Every other meaning row is marked "uncalibrated".
- **False-refutation bound over 15%:** a README caution says F refutes true claims at this size. No current R row uses F, so no tier changes.
- **AUC under 0.75:** the two S rows get "a test that lets y% of uninformed claims survive at this size".
- **Scorecard changes go through a sealed addendum.** Raters see this result, and no row is hand-edited.

## Caveats stated now
- Linear B is accounting text with a visible numeral system, so transfer to seals is not guaranteed.
- AUC compares a fluent reader with an uninformed one. That is the gap that matters for Indus claims, but it does not prove that any given claimant is right.

## Code (sealed with this file)
- `experiments/meaning_calibration/load.py` (tokeniser), `fcore.py` (draws, form F, verdict, planting), `kill.py` (kill test and E power report).
- The claim-writing step and `run.py` come after the kill test, and only if F passes. `run.py` must use `fcore.verdict` unchanged and is sealed by addendum before any claim file is scored.
