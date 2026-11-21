# Prereg: Parpola rules 3 and 4 (vēl substitution; Murukan fixed partners)

Written 2026-11-21, before any context of M87, M59 or M403 was counted. Code: `experiments/parpola_rules34/p34.py`, `run.py`. Source of the rules: `experiments/meaning_claims/RESULTS.md` ranks 3-4 and `CATALOGUE.csv` rows PAR-vel-substitution and PAR-murukan-partners. The claims come from Parpola 2010, pp. 23-29 (`experiments/news_read/raw/parpola-1994/parpola2010.txt`).

## 1. Not already tested

- Atlas 1.7 (`substitution`) tested one sign against a two-sign spelling (X ↔ YZ). It did not test the one-for-one pair M87 ↔ M59. Its M87 = M53 M171 equation is a different claim.
- Atlas 1.4 (`internal_phonetics`, homophones) used frame transitivity. M87|M59 was not among its candidates. That test could not separate paradigm members from homophones, and its power was 8/80. This prereg asks a narrower and simpler question: does M87 share M59's contexts more than frequency-matched pairs do?
- Atlas 4.7 (`core_semantics`, fish as deity names) is a productivity test on fish. It does not cover M403's partners.
- `bangle_oval` H3 covers only M403 on new bangles (n = 0). M403's next sign was never tested.

Both rules are therefore open.

## 2. Sign identities (fixed from the drawings, before any context count)

- Fish = M59 (W220). Vēl ("two long vertical strokes") = M87 (W032). Muruku ("intersecting circles") = M403 (W840). All three were checked against `data/sign_images`.
- Squirrel. Parpola describes a striped animal, head down, clinging to a long vertical stroke. That is M52, and M51 is the same animal without the stroke. M52 has 0 tokens in dev and 1 in held-out, so the squirrel set is **{M51, M52}**. Only frequencies were seen when choosing this, never M403's followers. In ICIT the squirrel is W255 (= M51 by the bridge). M52 has no Wells number.
- Disclosure: the meaning_claims catalogue already printed M403's text counts (66 texts; dev 49, held-out 17). No follower counts were seen.

## 3. Data and units

- M77 distinct texts, `dev_heldout(version=2)`: dev 1,699 texts, held-out 571.
- New sites: distinct ICIT texts from the post-1977 site list in `fish_tick_closer` (Dholavira, Nausharo, Banawali, Rakhigarhi and others), read in native Wells signs.
- Line breaks `|` are transparent. A break `#` makes that side's context unknown, and it is skipped. Text edges count as the context tokens `^` and `$`.

## 4. Rule 3: M87 substitutes for M59

- **Prediction.** M87 and M59 have more similar left and right contexts than frequency-matched sign pairs.
- **Metric.** overlap(a, b) = ½ [cos(left-context counts) + cos(right-context counts)]. Both signs are subsampled to n_sub = ⌊0.5 · min(n_a, n_b)⌋ occurrences, and the score is averaged over 20 seeded draws. This keeps frequency from driving the score.
- **Null (primary).** Every unordered pair of signs whose token count lies in [0.5 · min(n87, n59), 2 · max(n87, n59)]. M59, M87, M403, M51 and M52 are excluded, and the same metric and n_sub are used. Dev pool: 17 signs, 136 pairs. p = (1 + #null ≥ obs) / (1 + N). On dev the minimum p is 0.0073, so passing at p < 0.01 means beating every matched pair.
- **Pass.** Dev p < 0.01. Then held-out p < 0.05 against the same null rebuilt on held-out. ICIT new sites (W032 vs W220) are run if both signs have ≥ 10 tokens; there the bar is p < 0.05.
- **Kill.** Held-out overlap at or below the median of the held-out matched pairs. Also: dev p ≥ 0.01 with the gate passed.
- **Known-answer gate.** In dev, pick a random pair (a, b) from the matched pool, with a the rarer sign. Relabel k random tokens of b as a, with k/(n_a + k) = 0.25, so a quarter of a's tokens stand in b's slots. This is the realistic rate: Parpola gives one attested substitution, and a 25% share would already make M87 a frequent fish stand-in. Run the full procedure on (a, b). Use 50 trials; detection means p < 0.01. **The gate passes at ≥ 80% detection.** Also reported, but not part of the gate: the false-alarm rate with nothing planted (same pairs), detection at a 50% stand-in share, and power at held-out size (a 34% subset of dev, p < 0.05).
- **Disclosure.** A 2-trial smoke test of the gate code, run to debug it, gave p = 0.27 and 0.43 at the 25% rate. The 25% rate was chosen before that run and is not changed. The 50% level was added afterwards as a reported power level only.

## 5. Rule 4: M403's next sign is M87 or the squirrel

- **Prediction.** The share of M403 tokens whose next sign is in {M87, M51, M52} is above the frequency-matched null. Parpola's wording "mostly" is pre-registered as a share ≥ 0.4.
- **Statistic.** share = #(M403 followed by a partner) / #(M403 with a known next token). Text-final M403 counts as not followed by a partner. M403 before a break is skipped.
- **Null (primary).** Pseudo-partner sets {x, y}. x has a count in [n87/2, 2 · n87] and y has a count in [n_sq/2, 2 · n_sq], where n_sq = n51 + n52. M403, M87, M51 and M52 are excluded, and x ≠ y. The statistic is the share of M403 followed by x or y. p is the rank p.
- **Pass.** Dev p < 0.01. Then held-out p < 0.05 against the same null on held-out. New sites: W840 followed by {W032, W255}, run if W840 has ≥ 10 tokens, with a bar of p < 0.05.
- **Verdict levels.** "Supported (fixed partner)" needs dev p < 0.01, held-out p < 0.05 and a dev share ≥ 0.4. "Association only" means the p-values pass but the share is < 0.4.
- **Kill.** Held-out share inside the null's central 90% (5th to 95th percentile). Also: dev p ≥ 0.01 with the gate passed.
- **Known-answer gate.** In dev, pick a random head h from signs within ×2 of M403's count, a partner x from the M87-matched pool and y from the squirrel-matched pool. In 30% of h's tokens, make x the next sign: replace the next token, or insert x if h is final or before a break. Run the full procedure for h with partner set {x, y}. Use 50 trials; detection means p < 0.01. **The gate passes at ≥ 80% detection.** 30% is below Parpola's own fixed-pair example, six + fish at 12/25 = 0.48. False alarms and held-out-size power are reported as in rule 3.

## 6. Gate failure

If a rule's gate is below 80%, its verdict is **"underpowered"**, whatever the dev and held-out numbers. They are still run and reported.

## 7. Red team (at least two alternative nulls per rule; run on dev and held-out)

- Rule 3, alt null A: the 50 pool pairs whose position profiles (initial / medial / final / single) are closest to (M87, M59). This tests whether the overlap is only a shared position.
- Rule 3, alt null B: shuffle sign order within each text, 1,000 times. This tests whether the overlap is only co-occurrence in the same texts.
- Rule 3, robustness: the metric without edge tokens.
- Rule 4, alt null A: other heads within ×2 of M403's count, with the same true partner set. This tests whether M87 and the squirrel simply follow everything.
- Rule 4, alt null B: shuffle within texts, 1,000 times. This tests whether the order matters beyond the signs sharing texts.
- Both rules: the primary null on dev after near-copy collapse (the `fish_tick_closer` rule), per `split_leakage`.
- **Survives the red team** if dev p < 0.05 under both alternative nulls and in the collapsed run. Otherwise the result is "fragile", and the failing null is named. The red team cannot rescue a failed primary test.

## 8. Multiple comparisons

There are two primary tests (one per rule), each at α = 0.01 on dev, so the family-wise error is ≤ 0.02. Replications and the red team are confirmatory checks of a single direction. No other signs or pairs are tested. Nothing in this file is changed after the hash. Any deviation goes in RESULTS.md under "Deviations".
