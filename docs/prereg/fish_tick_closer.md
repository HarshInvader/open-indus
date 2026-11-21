# Pre-registration: fish_tick_closer (plan 9, story 3, "the fish grid")

Written 2026-11-20 BEFORE any statistic below was computed. Frozen with the code in
`experiments/fish_tick_closer/` (sha256 of this file and of every `.py` file appended to
`docs/prereg/HASHES.txt` with a UTC timestamp before the first run on real held-out data).

## Hypothesis

The corner tick on a fish sign is the closer drawn inside the sign: ticked fish = plain fish + closer.
Fish pairs (plain / ticked): M59/M60, M65/M66, M67/M68, M70/M71, M72/M73.
Wells (ICIT) pairs, as used by `experiments/redteam_tick_complete/`: W220/W226, W235/W236, W240/W241,
W231/W232, W233/W234. The bridge file confirms all except W234 = M73, which is taken from that red team.

Closer set C (validated closers in `docs/GRAMMAR.md`): M342, M211, M15, M254, M12, M14, M388.
Wells via `bridge_WM.json`: W740, W520, W154, W156, W526, W527, W151, W161, W804.

## Known at registration

README #3 and `experiments/redteam_tick_complete/` (ticked fish are text-final in 9/16 clean held-out tokens;
4/6 on post-1977 ICIT sites). README notes 73 ticked tokens in ICIT. No context distribution, closer
co-occurrence count or JSD for this question has been computed by me or, as far as the repo shows, by anyone.

## Data sets (all distinct texts, near-copies collapsed)

- DEV: `dev_heldout(version=2)[0]`. HELD: `dev_heldout(version=2)[1]`.
- NEW: distinct ICIT texts from post-1977 sites (the strict list in `experiments/redteam_tick_complete/run2.py`:
  Dholavira, Nausharo, Banawali, Rakhigarhi, Farmana, Bhirrana, Gola Dhoro (Bagasra), Karanpura, Khirsara,
  Kanmer, Shikarpur, Lakhanjo-daro, Tarkhanewala-dera, Naru-Waro-dharo).
- Near-copies: within each set, texts are linked when `corpus/build.py::_close` says so (<=1 edit with both
  texts >= 4 signs, or the shorter, >= 3 signs, is a contiguous part of the longer). Each connected family keeps
  ONE text: the longest, ties broken by the lexicographically first sequence string. This is the primary
  analysis. A sensitivity run on all distinct texts (no family collapse) is reported but not used for the verdict.

## Prediction 1 (contexts)

Token definitions, per base b. Sequences are flattened over line breaks `|` (reading continues).
Left context of a token = the previous sign; `<S>` if the token is the first sign of the text. A token whose
previous symbol is `#` is dropped.
- A_b: left contexts of ticked-fish tokens T_b.
- B_b: left contexts of plain-fish tokens P_b whose next sign is in C.
- D_b: left contexts of plain-fish tokens P_b whose next sign is a known sign not in C, or which end a text
  flagged complete. Plain tokens followed by `#`, or ending an incomplete text, are dropped (follower unknown).

Statistic per base: Delta_b = JSdist(A_b, D_b) - JSdist(A_b, B_b), where JSdist is the Jensen-Shannon
distance (square root of the JS divergence, log base 2) between the raw empirical context distributions.
Delta_b > 0 means the signs before a ticked fish look more like those before "plain fish then closer".

Null: permute the closer label (B vs D) among the plain-fish tokens of base b, keeping group sizes;
9,999 permutations; one-sided p = (1 + #{Delta_perm >= Delta_obs}) / 10,000.
A base is testable only if |A_b|, |B_b|, |D_b| are all >= 3; an untestable base counts as not passing.

**P1 dev rule.** P1 passes on DEV if Delta_b > 0 with p < 0.01 in at least 4 of the 5 bases.

**P1 replication rule (HELD and NEW separately).** Per-base tests cannot reach 4/5 at p < 0.01 on sets this
small, so replication uses one pooled statistic: Delta_sum = sum of Delta_b over testable bases, with a
base-stratified label permutation (9,999). Replicates if one-sided p < 0.05 on HELD and p < 0.05 on NEW.
If a set has no testable base, it is "untestable" (counted as underpowered, not as negative).

## Prediction 2 (no second closer)

Texts: single-line (no `|`), complete, no `#`, >= 2 signs, family-collapsed as above.
Ticked-final text: final sign is any ticked fish. Outcome: none of the other signs is in C.
k = number of ticked-final texts with no other closer.

Primary null ("keep-one-closer", length-matched): the final slot holds one non-closer sign; we ask how often
the other n-1 slots hold no closer. For each ticked-final text of length n, the reference rate r_n is the share
of texts in the same set with the same length bin (2, 3, 4, 5, 6, 7+) whose final sign is not in C and not a
fish (plain or ticked) that have no closer among their other signs. Null count = sum of Bernoulli(r_n),
100,000 draws; one-sided p = P(null >= k). If a length bin has fewer than 5 reference texts, it is merged with
the next shorter bin (then the next longer one) until it has >= 5; if the whole pool has < 5, P2 is untestable
on that set (counted as underpowered). If there are no ticked-final texts, P2 is untestable on that set.
Reported alongside (descriptive): the same share for closer-final texts (no SECOND closer), the rate H predicts.

**P2 rule.** P2 passes if p < 0.01 on DEV, and p < 0.05 on HELD and on NEW.

## Known-answer gate (run first, before any real test)

For each set, 200 plantings (seeded). In each, for each base, choose round(0.30 * m_b) of the m_b
"P_b then C" pairs uniformly (where the pair has a defined left context, as in P1), replace the two signs with a
new merged sign X_b. Real ticked fish stay in the corpus but are not used. Then run P1 with X_b in place of T_b
(999 permutations per base in the gate), and P2 with X = any X_b in place of the ticked fish (10,000 null draws).
- P1 detection = the P1 rule for that set passes (DEV: >= 4/5 bases at p < 0.01; HELD/NEW: pooled p < 0.05).
- P2 detection = the P2 threshold for that set is met (DEV 0.01, HELD/NEW 0.05).
- Gate passes for a prediction on a set if detection >= 0.80.
- False-alarm check (calibration, same 200 seeds): plant X_b from the same number of plain-fish tokens drawn at
  random regardless of follower. If the false-alarm rate of a rule exceeds 0.10, that rule is miscalibrated and
  its real result is reported as invalid.

**If the gate fails on a set, the verdict for that prediction on that set is "underpowered", not negative.**
The real test is still run and reported, but its non-significance is not evidence against the hypothesis.

## Verdict rule (frozen)

- Supported: gate passes on DEV for P1 and P2; P1 and P2 pass on DEV; both replicate on HELD and NEW.
- Refuted (P1): DEV gate for P1 passes and fewer than 4 of 5 bases pass on DEV. Same logic for P2 on DEV.
- Not replicated: DEV passes, and a replication set fails where its gate passed.
- Underpowered: DEV gate fails, or DEV passes and every failing replication set had a failing gate.
- Overall verdict is the weaker of P1 and P2 (supported > underpowered > not replicated > refuted) and is
  reported per prediction as well.

## Kill conditions

- Gate detection < 0.80 on DEV (power under 0.8): the hypothesis cannot be judged; verdict "underpowered".
- Fewer than 4 of 5 bases at p < 0.01 on DEV with a passing gate: P1 is refuted at our sample size.
- P2 dev p >= 0.01 with a passing gate: P2 is refuted at our sample size.
- Red-team downgrade: if, on DEV, the pooled P1 result loses significance (p >= 0.05) under either red-team null
  below, the P1 verdict is reported as "fragile" next to the frozen verdict.

## Multiple testing

Confirmatory tests: 5 (P1 DEV bases) + 2 (P1 replication pooled) + 3 (P2 sets) = 10. The rules are
conjunctions, so the chance of a false "supported" is below each single threshold. In addition, Holm-adjusted
p-values over these 10 are reported. Gate, sensitivity and red-team tests are robustness checks, reported with
their counts, not used to rescue a failing rule. Ledger rows go to `experiments/fish_tick_closer/ledger_rows.csv`.

## Red team (run after the frozen tests; may not change the verdict except the "fragile" flag)

P1, on DEV, HELD, NEW, pooled Delta_sum:
- R1 length-matched null: closer labels permuted only within text-length bins (2, 3, 4, 5, 6, 7+).
- R2 within-text shuffle: in each text, fish and closer signs stay where they are and all other signs are
  shuffled among the other positions; 1,000 shuffled corpora; p = share with Delta_sum >= observed.
- R3 drop tokens whose left context is `<S>` (text start), then the frozen pooled test.
P2, on each set:
- R1' length-matched null with post-closer-final texts (final sign in M176, M1, M242, M139, M224, M93, M374
  or their Wells counterparts) removed from the reference pool.
- R2' within-text shuffle: shuffle sign order within every text in the set (1,000 corpora); statistic = share of
  ticked-final texts with no other closer; p = share of shuffled corpora with share >= observed.
- R3' plain-fish-final texts (length-matched) as the reference pool.

## What would falsify

A passing gate and a DEV failure of either prediction. A ticked-fish context that matches "plain fish, no closer"
as well as or better than "plain fish then closer" in most bases is direct evidence against the equation.

## Compute

All runs through `board/run.sh .venv/bin/python -I ...`, single process, background priority. Seeds fixed in code.
