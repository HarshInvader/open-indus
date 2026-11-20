# Carver hands × text: one confirmatory test

Sealed 2026-11-20 (UTC) by agent `paper`, on the coordinator's decision. This was written before the test on real hands was run. Code: `experiments/carver_text/confirm.py` (uses `ct.py` and `parse.py`). Hashes are in HASHES.txt.

## Question
Do unicorn seals cut by the same carver or workshop carry related text?

The hands are expert-defined: Jamison 2017's 56 groups, built from 11 iconographic attributes, with inscribed characters left out of the grouping (ch. 7).

## Prior art and novelty
- **Jamison 2017** (PhD thesis, https://search.library.wisc.edu/digital/AC3N6TSMX73CAE8O, opened and read): defines the hands and never tests text against them.
- **arXiv 2604.23582** (https://arxiv.org/abs/2604.23582, abstract opened): reuses the attribute data, with no text test.
- **Jamison & Uesugi, "Mohenjo-daro and Interregional Connections in the Indus Civilization: Evidence from Inscribed Seals"**: both copies (harappa.com, academia.edu 86751036) returned 403. It could not be checked, and was not bypassed.
  - A search summary says its groups do not "seem to" share signs (unverified).
  - If it reports a sign-sharing test, the novelty narrows to "the first stratified, near-copy-excluded test".
- **Novelty sentence:** the first statistical test of whether expert-defined carver hands predict shared text on Indus seals.

## Disclosed prior look
- During the power gate (`experiments/carver_text/GATES.md`), a first power estimate wrongly planted a 20% hand-specific sign into the **real** hands, not reshuffled ones.
- It gave power ≈ 0.95, with within-hand rarity-weighted sharing ratios of 1.36-1.47 against the stratified null.
- The same plant into reshuffled hands gives power 0.17. So the difference hints that real hands already share rare signs above chance.
- No test of real hands without planting has been run. Because of this look, alpha is 0.01, not 0.05, and only one statistic is tested.

## Data
`parse.py` joins Jamison Appendices 7.1/9.1 to ICIT (`data/icit_texts.jsonl`) by CISI number:
- 450 linked unicorn seals with text (the pool);
- 147 of them in 44 hands with ≥ 2 linked members.

## The test (one statistic, no subgroups)
- **Statistic.** For a pair of seals: the sum over shared sign types of log(N / df). Here df is the number of pool seals that contain the sign, and N = 450 (rarity weights are label-free). The test statistic is the mean over within-hand pairs, excluding near-copy pairs (≤ 1 edit, or one text contained in the other).
- **Null.** Hand labels reshuffled within site × size-tercile strata (seal face area, terciles within site, unknown size as its own bin). This keeps every hand's size. 10,000 reshuffles, one-sided.
- **Alpha.** 0.01.
- **Reported alongside:** the ratio of observed to null mean, with a 95% bootstrap CI over hands. This is descriptive and not used for the verdict.

## Planted check (same run)
- On reshuffled hands, plant a hand-specific sign (drawn from signs with 5-50 tokens) in 0%, 40% or 50% of each hand's seals. 200 replicates, 1,000 reshuffles each.
- **Pass:** a rejection rate ≤ 0.025 at 0%, and ≥ 0.8 at 40% or at 50%.
- The smallest passing share is the stated detectable effect.

## Verdicts
- **VOID:** the planted check fails in this run.
- **POSITIVE (p ≤ 0.01):** "Expert hands share rare signs above chance (hint-informed, single dataset, no independent replication)."
- **NULL:** "No effect of ≥ X% detectable (hint-informed, single dataset, no independent replication)", where X is the detectable share above.

## After the run
- The result goes to the red team before any write-up.
- No second statistic, no subgroup (site, period, multi-site hands) and no re-clustered arm will be tested as confirmatory. Any such look is labelled exploratory.
- Licensing: the Jamison thesis is © the author. Only derived counts are published; the joined table stays local.
