# Pre-registration: bench of Pierson's May 2026 Proto-Dravidian key (board task #5, agent H4)

Written 2026-11-17 before any score of the key on our corpus was computed.

## Key under test
- Primary K185: `experiments/bench_pierson/keys/anchors_bbecc1cd_20260527.json`, the author's audited anchor file at
  glossa-lab commit bbecc1cd (2026-05-27, "AUDIT: Revert Phase 312 kol mass-assignment"): 605 entries, 400 HIGH.
  This is the state the preprint v3 ("185 Proto-Dravidian readings") reports. We use HIGH entries whose number is
  a Mahadevan number (M1..M417) and that occur in M77. Sign numbers were checked to be Mahadevan's by frequency
  rank (their M342 584, M267 400, M099 389, M211 249, M391 193 tokens in Holdat = our top signs).
- Secondary K161: the public v4 table `research/indus/indus-anchor-model/data/public/anchor_table_397.csv`
  (HIGH + MEDIUM, 161 signs). Reported as robustness, not counted in the verdict.
- Reading of a sign: the reading string, parenthetical notes removed, split on "/" into alternatives.
  First alternative = the "pin" reading used by the author's Test 1.

## Corpus
M77 distinct texts, `dev_heldout(version=2)`; break-free runs (`runs`) of >= 2 signs, reading order.
Only adjacent pairs where both signs are keyed are scored.

## Scores (all fixed now)
- S1 (author's Test 1, replicated): share of adjacent keyed pairs whose first-letter pair (first character of the
  first alternative, raw) is in the author's Tamil letter-bigram set (`dravidian_tamil_lm.json`, 944 bigrams).
- S2 junction phonotactics: mean log P(first letter of next reading | last letter of this reading), letters
  NFKD-stripped of diacritics, add-one smoothed bigram counts from the same LM file, first alternative.
- S3 dictionary bench (analogue of the Yajnadevam CPW bench): fewest-word segmentation of each run, a word being
  1+ consecutive signs whose readings (any alternative per sign, diacritics stripped, concatenated) form a lexicon
  word; a single sign is always allowed. Score = signs per word (higher = more cross-sign words).
  Lexicon: Wiktionary Proto-Dravidian lemmas + nouns (ours, `experiments/language/ext/wikt`), plus Tamil Treebank
  lemmas and LM vocabulary transliterated to Latin. Words of 3+ letters only.

## Tests
- T1 key vs permuted key (N1): readings permuted among keyed signs inside 5 dev-frequency bins, 1000 permutations,
  one-sided p, on heldout. Also reported on dev.
- T2 keys fitted to noise (N2): hill-climb swaps of the key's own readings among keyed signs to maximise each
  score, 3 restarts, on (a) dev, (b) dev unigram-shuffled within texts' lengths, (c) dev bigram-Markov resample.
  Fitted-on-dev keys are also scored on heldout.
- T3 coverage check: key token coverage on M77 distinct texts versus the coverage of the same number of most
  frequent signs, and on a token-shuffled corpus (expected identical: coverage depends only on sign frequencies).
- T4 the author's "Uniform 0.0%" baseline: check whether it is a case artefact (uppercase uniform alphabet vs
  lowercase pins).
- Power gate: planted corpus of Tamil Treebank lemma sequences cut to Indus lengths, each lemma type written with
  one sign, same number of texts as heldout. A score counts only if the TRUE planted key beats N1 at p < 0.05 there
  and beats keys fitted to planted-noise.

## Decision rule
3 scores x heldout, Bonferroni alpha = 0.0167. The key "beats chance" on a score only if (i) the score passes the
power gate, (ii) heldout p < 0.0167 vs N1, and (iii) the key's dev score is above the median of keys fitted to
noise (N2 b, c) with the same freedom. Otherwise the verdict is negative (or "no power" if the gate fails).
Caveat known in advance: the author fitted on Holdat, which overlaps M77 sites and texts, so our heldout is not
truly unseen by the author; a pass would therefore be weaker than it looks, a fail is not weakened.
