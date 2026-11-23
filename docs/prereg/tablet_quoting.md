# Do Indus tablets and pots quote same-site seal texts? (sealed 2026-11-23, before any Indus number)

Agent `paper`. Main line (b), non-textual anchors. This is Fable's top study after `animal_tie_power`, recorded in RESEARCH_STATE.

## Why
If a tablet or pot carries a run of signs that also stands on a seal from the same city, more often than it would with a seal from the other city, the run is tied to local people or offices. That is an object anchor: the same string travels between two kinds of objects with a known site. If no such excess exists at a power we can state, the tablets are tokens with their own vocabulary, a new atlas entry.

## Data (measured before sealing; `run.py shape`)
- ICIT (`data/icit_texts.jsonl`), Harappa and Mohenjo-daro only, texts marked complete, W-numbers only, distinct texts of at least 3 signs.
- Seals (SEAL types): Harappa 219, Mohenjo-daro 822. Sealings (TAG) are excluded.
- Targets: Harappa TAB:B 209, TAB:I 121, pot 11; Mohenjo-daro TAB:C 52, TAB:B 42, pot 15, TAB:I 1. A text found as two types keeps its first type in sort order.
- Ur III (rehearsal only): `experiments/tablet_quoting/data/ur3_sealed.jsonl`, built by `build_ur3.py` from ORACC epsd2/admin/ur3. Umma 14,458 and Girsu 2,635 sealed tablets. Legend = lines labelled "seal N"; body = the rest. Signs split on `-.{}` and spaces; damage marks dropped. Kept local (derived from a CC BY-SA corpus; large).

## Statistic
- **Formulae:** the 50 most frequent trigrams (counted once per text) over all seals and targets are removed from every text's trigram set before matching. Frozen in code.
- **T** = share of target texts with at least one trigram (contiguous, not a formula) that also occurs in a seal text from the same site, pooled over both sites. Per-site shares are reported too.
- Matching is on sign IDs, exact.

## Nulls
- **N1 (primary):** seal site labels permuted between the two cities within length bins (min(length, 7)); 2,000 permutations on the real data, 300 per rehearsal or plant draw. One-sided p = (1 + #null ≥ T) / (n + 1). Per-site excess = observed per-site share minus its mean under N1.
- **N2:** every target text regenerated, same site and length, from a bigram model fitted on all target texts (start sign drawn from target first signs); 1,000 draws on the real data, 300 per draw elsewhere. T must exceed N2's 99th percentile.

## Pass rule (all three)
1. N1 p ≤ 0.01;
2. per-site excess > 0 at both Harappa and Mohenjo-daro;
3. T > N2's 99th percentile.

## Kill test: Ur III rehearsal at Indus size (run first)
- Mohenjo-daro ↔ Umma and Harappa ↔ Girsu (larger seal site to larger archive).
- Per draw: distinct legends of at least 3 signs, shuffled and cut to the Indus seal count per site; each cut to a random Indus seal length (random start). Target texts: random sealed tablets, as many as the Indus targets per site, the body flattened and cut to a random Indus target length (random start); pairing between a tablet's own seal and body is discarded.
- 200 draws, full pass rule. **Power must be ≥ 0.8.** If it is below, STOP. Verdict: "untestable at Indus size: a real seal-to-document quoting system (Ur III) is not visible through Indus-sized, Indus-length texts". The Indus statistic is then not computed.

## Planted gate on the real Indus texts
- δ ∈ {0.02, 0.05, 0.10, 0.20} of each site's targets get a random non-formula trigram, taken from a random same-site seal, written over a random position (text length unchanged). 40 draws per δ, full pass rule with formulae frozen from the real texts.
- c\* = smallest δ with power ≥ 0.8. If c\* is missing or > 0.10, the verdict is "untestable (planted gate c\* > 0.10)" and the real statistic is not reported as a test.

## What each outcome means (frozen)
- **Pass:** "quoting found". An L1 candidate with an object anchor. It must then survive a red team (are the shared runs formula-like, do the hits come from objects listed twice, is it chronology) before any claim.
- **Fail with c\* ≤ 0.10:** powered negative: "tablets and pots do not quote same-site seal texts above c\* of targets". New atlas 5.x entry: tablets are tokens with their own vocabulary.
- **By-group (descriptive):** TAB:B, TAB:I, TAB:C and pot separately with N1 (2,000). Reported, not a test. Bigram (2-sign) runs are not run in this study.

## Limits stated in advance
- Mohenjo-daro has only 110 targets, so the per-site rule there is the weak link.
- The two sites differ in date range and in which tablet types they hold; the site permutation tests "same city", not "same object".
- Exact sign IDs: allographs or misreadings lower power; the Ur III rehearsal has the same issue through its own transliteration.
- The Ur III mapping is a proxy: Ur III bodies are not seal quotations by design, they share names and titles with legends.

## Cost
About 1.1 s per rehearsal draw single-threaded: about 1 minute for the kill test and about 2 to 4 minutes for the full run, on 4 workers under the Indus compute lock, with `nice -n 20` and the memory guard.
