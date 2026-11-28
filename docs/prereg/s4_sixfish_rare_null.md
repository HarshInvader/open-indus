# Pre-registration: S4, give "six then fish" a rare-sign-matched null

Contributor: m0x1n. Written 2026-11-28, before any matched null was computed.

## Claim under test

README #5: two-tier six followed by fish (M109 M59) is a fixed expression. Held-out (split v2): M109 is followed by M59 in 7 of 10 cases, against a base rate of 3.1% (ledger `rv_6f`, binomial p = 2.8e-9). The base rate is the share of M59 among all next signs in the corpus. It ignores where in a text the pair sits, how long the texts are, and how many rare signs they carry. The round-seal result survived a null matched on rare-sign load (`redteam_round_order`). This one has not had that check.

Disclosure: to confirm I am counting the same thing, I recomputed the raw count before writing this. Held-out: 7 of 10 M109 tokens with a next sign are followed by M59; the share of M59 among all next signs is 0.0296. Dev: 5 of 15. No null of any kind has been computed.

## Units and definitions

- M77 object-side texts, `distinct()`, `dev_heldout(version=2)`; `site == "West Asian finds"` dropped.
- Adjacency only inside break-free runs (`runs()`), so no pair crosses a line end or a break.
- A **slot** is an M109 token at position j of a run of length L that has a next sign (j < L − 1). The outcome is whether the next sign is M59.
- **Rare load** of a run: the number of its tokens whose sign occurs fewer than 10 times in the **dev** texts. Dev counts are used for both dev and held-out, so the held-out texts cannot set their own rarity.
- Text length is the run length L, capped at 9. Rare load is capped at 3.

## Primary test (T1, held-out)

**Null N1 (matched slot).** For each M109 slot (L, j, r), draw a held-out run that does not contain M109, has the same (min(L, 9), min(r, 3)) and has at least j + 2 signs. If L > 9, use the same capped stratum and position min(j, L' − 2). Read whether the sign at position j + 1 is M59. Fallback when a stratum has fewer than 5 runs: lower r, then L, as in `redteam_round_order`'s `key_for`. Each null replicate draws once per slot. The statistic is the number of slots followed by M59; 100,000 replicates; one-sided p = (1 + #null ≥ obs) / (1 + N).

This asks whether M59 follows M109 more often than M59 sits in the same slot of comparable runs without M109. It removes position, length and rare-load effects.

Pass: p < 0.05.

## Secondary tests

- **T2 within-run shuffle (held-out).** Shuffle signs within each run that contains M109, 100,000 times. Statistic as in T1. This asks whether M59 follows M109 more than chance placement of the same signs in the same runs. Pass: p < 0.05.
- **T3 dev**, N1 as in T1, with dev runs as the null pool. Descriptive: the claim was found on dev-era data.
- **T4 ICIT native**: W016 followed by W220, N1 built from ICIT native distinct texts (the same region rule as S3), rare load from ICIT counts, all texts. Descriptive replication: ICIT shares objects with M77.

Holm over T1 and T2.

## Planted control (power and calibration at our sample size)

Use all held-out runs. Pick carrier signs with 8 to 20 held-out tokens that have a next sign, excluding M109 and M59; take up to 20 of them in order of frequency, ties broken by sign number.
- **(i) No plant.** Run T1 with each carrier as "M109" and M59 as the partner. Report the share of carriers with p < 0.05. Some carriers really do pair with M59, so this is an upper bound on false positives. I will also report it with carriers whose raw M59 rate exceeds 20% excluded.
- **(ii) Plant.** For each carrier, set the next sign to M59 at a random 60% of its slots (seeded). That gives about 6 of 10, like the claim. Run T1. Report power, the share with p < 0.05, using 20,000 replicates per carrier.

Pass for the control: power ≥ 0.8. If power is below 0.8, the T1 result is reported as underpowered, whichever way it goes.

## Verdict rule

- **Survives** if T1 passes after Holm.
- **Weakened** if T1 fails and T2 passes.
- **Refuted as a fixed pair beyond position, length and rare load** if both fail.

I will report the matched-null rate next to the 3.1% base, and whatever the result.
