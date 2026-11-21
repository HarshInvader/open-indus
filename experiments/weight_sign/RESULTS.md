# Is there a "weight" sign? (meaning_claims rule 2)

Pre-registered in `docs/prereg/weight_sign.md` (hash tag `weight_sign`, 2026-11-20T22:19:38Z) before the real run. The log is in `run.log` and the numbers in `results.json`.

## Conclusion

**Verdict: underpowered.** Our data cannot test whether any Indus sign means "weight".

- **Parpola's sign 193 is not M197.** Its drawing is a hatched triangle hanging from a bar, like a pan on a balance. That is M206 (W504), with M208 (W505) and M207 as variants. M197 is a box on a frame.
- **Parpola 193 is too rare to test.** It is in 9 distinct texts in the whole corpus. Only 1 linked text falls in the fresh data and 3 in the seen data. None of the 3 seen texts lies in a weight unit (1.0 expected). This proves nothing either way.
- **M197 cannot be tested on fresh data.** Only 5 fresh texts carry it. A planted sign 3× enriched near weights at that frequency is found 7% of the time; the bar was 80%.
- **On the already-seen data, M197 still looks enriched once unit size is controlled.**
  - Under the find-density-matched null: 13 texts in weight units vs 8.5 expected, p = 0.0014, Mantel-Haenszel rate ratio 9.9.
  - The red-team null agrees (p = 0.0008).
  - This counts for nothing. The data was already seen, the gate there detects only 25%, and the negative control failed: the jar M342 is also "enriched" under the same null (p = 0.003).

## Step 1: the sign mapping

- **Source.** Parpola's sign list on Wikiversity, Sign 193, "Weight, Metrology". The drawing is saved in `raw/sign193_*.png`.
- **No Parpola concordance exists in the repo.** The field-cady `parpola_graphemes` V-numbers run to V805, so they are not Parpola's 1994 numbers. I matched the drawings by eye against `data/sign_images/`.

| Mahadevan | Wells | Matches Parpola 193? | Distinct M77 texts |
|---|---|---|---|
| M206 | W504 | yes (variants 1-2: hatched triangle under a serifed T) | 7 |
| M208 | W505 | yes (variants 3-4: same, capped bar) | 1 |
| M207 | none | variant (M206 inside four strokes) | 1 |
| M197 | W575 | **no** (box on a three-sided frame, no triangle) | 55 |

- I tested two candidates, P193 = {W504, W505} and M197, with α = 0.025 each.
- The mapping of M206 is clear. M208 is likely. Leaving M204 (the bare hatched triangle) out is a judgement call, and it changes nothing at these counts.

## Step 2: the data, and what was already seen

- **Fresh (primary).**
  - Mohenjo-daro DK-G houses with weights in Hemmy's list (Mackay 1938, App. I).
    - The OCR gives a readable house for only 13 of about 220 weights, so 10 houses were coded; 6 of them have texts.
    - Houses the assemblage had already labelled WEIGHT were removed with their texts.
  - Chanhu-daro squares with unfinished weights.
  - These are new labels, but the Mohenjo-daro texts were seen before as "not weight". This is new coding at a seen site, not new objects.
- **Seen (secondary).** The assemblage's Harappa and Mohenjo-daro units.
  - M197 was its nearest miss there.
  - At Harappa, 30 of 60 squares and 484 of 597 texts are in weight units, so nearly everything is "near weights".

## Step 3: results

| Data | Candidate | Texts | Obs in weight units | Exp (N1) | Rate ratio | p N1 | p N2 (red team) | Gate power | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| fresh | P193 | 1 | 0 | 0.10 | 0 | 1.0 | 1.0 | 0.005 | untestable |
| fresh | M197 | 5 | 1 | 1.37 | 0 | 1.0 | 1.0 | 0.068 | underpowered |
| seen | P193 | 3 | 0 | 1.03 | 0 | 1.0 | 1.0 | 0.025 | untestable |
| seen | M197 | 27 | 13 | 8.48 | 9.9 | 0.0014 | 0.0008 | 0.245 | underpowered (exploratory) |

M197 in the seen data, site by site:

- **Harappa: all 10 texts are in weight units, against 7.8 expected (p = 0.047).**
  - The rate ratio is infinite because no M197 text lies outside weight units.
  - Chance alone puts all 10 there about 1 time in 8, because 81% of the texts are there.
- **Mohenjo-daro: 3 of 17 texts are in the 5 weight houses, against 0.66 expected (p = 0.023), rate ratio 5.6.**
- **Neither site passes α = 0.025 on its own.**

The new null works. The old null did not:

- **The old assemblage null (N0) reproduces the old numbers exactly:** Harappa 10 vs 5.14, Mohenjo-daro 3 vs 0.42. So the pipeline matches the assemblage.
- **Under N0, 8 of the 10 most common signs come out "enriched near weights" at p ≤ 0.025.** Under N1 none do. Matching on unit size removes most of the find-density artefact.
- **The jar M342 still passes under N1 in the seen data:** 212 vs 198 expected, rate ratio 1.41, p = 0.003. Something besides unit size, such as level or date, still links some signs to weight units at Harappa and Mohenjo-daro. By the frozen rule the negative control failed there.
- **In the fresh data the negative control passed:** M342 p = 0.16, and 0 of 10 common signs reached p ≤ 0.025.

Pipeline check (not part of the decision): a sign planted at 10% of texts is found 90% of the time in the seen data and 79% in the fresh data. The method works when there is enough data.

## Tests run

| id | hypothesis | verdict |
|---|---|---|
| ws_map | Parpola 193 = M197 | refuted by drawing (it is M206/M208) |
| ws_p193_fresh | P193 enriched near weights, fresh data | untestable (1 text) |
| ws_m197_fresh | M197 enriched near weights, fresh data | underpowered (gate 0.07) |
| ws_p193_seen | P193, seen data | untestable (3 texts) |
| ws_m197_seen | M197, seen data | underpowered; exploratory signal only; negative control failed |
| ws_nc | jar and 10 common signs not enriched under N1 | passed (fresh), failed on M342 (seen) |

- **Count.** 4 candidate tests (2 candidates × 2 data sets). Each data set also carries 11 negative-control tests under N1 and N0. Bonferroni within each data set: α = 0.025.

## Caveats

- **Effect size changed after the dry run.** I replaced observed/expected with the Mantel-Haenszel rate ratio, because observed/expected cannot exceed 1.23 at Harappa. The dry run showed only the data structure and marginal counts, and the change was made before hashing.
  - It also showed that all 10 Harappa M197 texts sit in weight units. That was already implied by the assemblage result.
- **Texts are distinct within a unit.** A text found in two units counts once in each.
- **Hemmy's table was parsed from two poor OCRs.** House numbers are often garbled, so most weights were lost. Missed weight houses fall into the comparison pool, which biases toward no effect.
- **Weights are a proxy.** Only recorded weights count, and the reports record finds selectively.

## Next experiments

- Read Hemmy's Appendix I (Mackay 1938, pp. 607-612) and Marshall 1931, ch. XXIX from page images, to get about 370 weights with house loci instead of 13.
  - This is the only route to a fresh test of M197 with useful power.
  - M197 has 31 ICIT texts at Mohenjo-daro, and the gate needs about 10% of texts at a 3× effect.
- Code the HARP trench craft areas at Harappa (see `experiments/assemblage/RESULTS.md`, item 1).
- Before any rerun, find out why the jar is linked to weight units after size matching (level? date? area?). Then add that variable as a stratum in a new prereg.
- Close Parpola 193 as untestable on unit data. A sign in 9 texts cannot reach 80% power for any plausible effect.
- Fix the meaning-claims catalogue row PAR-sign193-weight to read M206/M208, not M197. I did not edit that folder.
