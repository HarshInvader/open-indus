# Pre-registration: m99_relator (board #42, Fable plan 7 item 2 / G1)

Written 2026-11-18 by agent N6, before any Indus statistic below was computed (dev or held-out). Folder: experiments/m99_relator/. Code frozen with this file: rel_lib.py, rel_control.py, rel_indus.py (hashes in docs/prereg/HASHES.txt).

## Question
Is M99 a relator, a sign that joins two independent units ("X M99 Y")? closer_ownership found that M99's match to Sumerian dumu ('son of') does not survive without the grammar. This is a different, relational test that does not use the grammar's slots.

## Statistic (frozen; chosen on Ur III, disclosed below)
Unit: distinct texts, line breaks dropped, break-free only. Near-copies are collapsed by greedy leader clustering: texts sorted by (length descending, sequence), each joins the first leader within one edit (Levenshtein <= 1, which implies length difference <= 1), else becomes a leader. There is no chaining, so the giant family noted in #34 cannot form. Only cluster leaders are hosts.

For a host t = L s R with s at a mid position (L, R non-empty):
- **D2 (primary)** = 1 if L (the whole left part) is the END of some other text AND R (the whole right part) is the START of some other text. "Other" = a pool text in a different cluster from the host.
- **A (secondary, Fable's literal wording)** = mean of [L is a whole text elsewhere] and [R is a whole text elsewhere].
Score of a sign = mean over its mid occurrences in hosts.

**Matched comparison.** Candidates are signs with >= 8 mid occurrences in the hosts. The 20 nearest candidates to the target in (log occurrence count, mean len L, mean len R), squared Euclidean distance, ties by name. pct = share of these with a D2 score strictly below the target's.

**Shuffle null.** Each pool text is shuffled within itself (lengths, sign frequencies and clusters kept); the target's D2 score is recomputed; p = (1 + #null >= obs) / (1 + B).

**Flag** = pct >= 0.95 AND at least 10 matched candidates AND shuffle p < 0.05.

## Known-answer control (gate; run first)
Ur III (5,180 distinct legends) and Old Babylonian (2,760) seal legends from experiments/genre_alignment/data, word level, words treated as signs. Each replicate draws a pool of 1,285 legends (= the number of break-free distinct Indus consensus texts) and 314 hosts (= held-out break-free distinct texts). In the primary (harsh) condition the 314 hosts are drawn in random order, skipping any legend whose mid dumu occurrences would push the total above 49 (= the mid M99 count among held-out hosts), so the remainder are dumu-free legends. (A first smoke test that dropped dumu hosts instead left only 84 hosts and 8 candidates, far below the Indus configuration; corrected before freezing.) 100 replicates with B = 100 shuffles per corpus (natural-count condition: 30 replicates, reported only).
- **Gate**: dumu flagged in >= 80% of harsh replicates in BOTH Ur III and OB, AND the pooled title false-flag rate <= 0.10 in each corpus. Titles: Ur III dub-sar, ensi2, lugal, ugula, nu-banda3, sagi, szabra, sukkal, sipa, gudu4, muhaldim, aga3-us2; OB dub-sar, lugal, ensi2, sanga, ugula, lukur, dam-gar3, gudu4, sukkal, gudu4-abzu, sza13-dub-ba (each counted only in replicates where it has >= 8 mid occurrences).
- arad/arad2 ('servant of') and u3 ('and') are relators too; their flag rates are reported, not gated.
- **If the gate fails, the Indus test is not run and the verdict is UNTESTABLE** (rel_indus.py refuses to run).

**Disclosure.** I chose D2 after seeing, on the full Ur III corpus, that whole-text attestation (A) does not separate dumu from dub-sar (0.119 vs 0.112), while D2 ranked dumu 1st of 52 frequent mid-words and left titles low (dub-sar 0.007). Ur III is therefore not an independent check of the statistic; OB is, and the gate requires both. No Indus outcome was looked at. Indus counts seen before writing this: 1,285 break-free distinct consensus texts, 971 dev / 314 held-out, mid M99 243 dev / 49 held-out, M123 83 / 23.

## Indus test (only if gate passes)
Corpus: experiments/consensus_corpus cons_sign_ext (primary consensus; disputed signs are breaks). Pool = all 1,285 break-free distinct texts. Hosts: held-out = texts whose records are all in dev_heldout(version=2) held-out (by key0); dev = all in dev; mixed texts are pool only. B = 1,000.
- **Primary (confirmatory)**: M99 flagged on held-out hosts.
- Dev result reported (development set, not used to tune anything).
- Secondary: M123; statistic A percentile; seal+sealing-only pool and hosts. No correction needed for the single primary test; secondaries are descriptive.

## Verdicts
- UNTESTABLE: gate fails.
- SUPPORTED (relational lead, not a reading): M99 flagged on held-out (pct >= 0.95, shuffle p < 0.05). Then an M6 red-team task is added.
- REFUTED (kill, per board): gate passes and M99 pct < 0.95 on held-out. If dev passes and held-out fails, say so (no replication).

## What would falsify a positive
A red team finding that the D2 excess comes from the near-copy rule, from the matching features, or from M99's texts being short formula copies (e.g. the opener + M99 + numeral + M161 formula in local_repeats).
