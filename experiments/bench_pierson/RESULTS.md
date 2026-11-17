# Bench of Pierson's May 2026 Proto-Dravidian key (board task #5)

Started by H4 (prereg, code, full run); H4's session ended before the write-up. H7 checked the run and wrote this.

## Verdict: negative. The key does not beat its own shuffles, and the author's validation numbers are reached by keys fitted to noise.

- On held-out M77 texts the 185-reading key (K185, 200 Mahadevan signs with HIGH readings) is not better than the same readings shuffled among signs of similar frequency on any of the three scores (p = 0.16, 0.11, 0.75; Bonferroni alpha 0.0167).
- Keys fitted with the same freedom to shuffled or Markov-resampled sign strings score far higher than the real key on every score (Tamil-bigram hit rate 0.97 vs the key's 0.59).
- The author's "92.8% coverage" is a property of sign frequencies, not of the readings: the same coverage appears on a token-shuffled corpus, and the 200 most frequent signs would cover 96%.
- The author's "Uniform 0.0%" baseline is a case artefact: an uppercase uniform alphabet can never match a lowercase bigram list. A fair uniform lowercase baseline hits 27%, and the fair baseline (readings shuffled) hits 49% vs the key's 55% on held-out.
- Caveat on power: our planted Tamil corpus showed that at this sample size S1 and S2 cannot detect even a TRUE key (planted p = 0.28, 0.16), and S3 detects it against shuffles (p = 0.008) but not against keys fitted to noise. So this bench can reject the author's validation as non-diagnostic, but it could not have certified a correct key either. Formally, per the prereg decision rule, no score passes the power gate; the key fails conditions (ii) and (iii) on all three scores anyway.

## Setup (pre-registered: `docs/prereg/bench_pierson.md`, sha256 d5415aad..., code hashes for run.py b1451917... and fixed common.py 346a94f5... in `docs/prereg/HASHES.txt`, both logged before the full run)

- K185: author's audited anchor file (glossa-lab commit bbecc1cd, 2026-05-27), HIGH entries with Mahadevan numbers present in M77: 200 signs. K161 (public v4 table, HIGH+MEDIUM) as robustness.
- Corpus: M77 distinct texts, `dev_heldout(version=2)`, break-free runs of 2+ signs, 10,005 tokens.
- Scores: S1 author's Test 1 (first-letter pair in the 944-bigram Tamil LM set); S2 junction log-probability; S3 signs per dictionary word (Proto-Dravidian Wiktionary + Tamil Treebank lemmas).
- Nulls: N1 readings permuted within 5 frequency bins (1000 perms); N2 hill-climbed keys (3000 swaps, 3 restarts) on real dev, unigram-shuffled dev, Markov-resampled dev.

## Numbers

### Power gate (planted Tamil Treebank lemma corpus, 1,470 chunks, 200 keyed signs, 57% coverage)
| score | true key heldout p (N1) | true key dev | noise-fitted median (unigram / Markov) | gate |
|---|---|---|---|---|
| S1 | 0.28 | 0.597 | 0.888 / 0.954 | fail |
| S2 | 0.16 | -3.82 | -2.81 / -2.41 | fail |
| S3 | 0.008 | 1.006 | 1.012 / 1.016 | fail (N2) |

### K185 on M77
| score | heldout obs | N1 mean (sd) | p | dev obs | N2 unigram median | N2 Markov median | fitted-on-dev scored on heldout |
|---|---|---|---|---|---|---|---|
| S1 bigram hit | 0.547 | 0.491 (0.055) | 0.16 | 0.587 | 0.969 | 0.982 | 0.87-0.92 |
| S2 junction logP | -3.80 | -3.97 (0.15) | 0.11 | -3.74 | -2.42 | -2.08 | -2.50 to -2.76 |
| S3 signs/word | 1.011 | 1.018 (0.010) | 0.75 | 1.020 | 1.162 | 1.269 | 1.14-1.19 |

K161 gives the same picture (heldout p = 0.25, 0.14, 0.72; noise-fitted keys far above it).

### Author's own validation, checked
| author claim | check | result |
|---|---|---|
| 92.8% Holdat coverage | M77 coverage of the 200 keyed signs; same on token-shuffled corpus; top-200 signs | 74.1%; 74.1% (identical); 96.1% |
| Tamil LM 57.8% vs Uniform 0.0% | uppercase uniform hit rate; lowercase uniform; permuted readings | 0.0% (case artefact); 27.4%; 49.1% vs key 54.7% heldout (p = 0.16) |
| M77 replication 70.5% | our S1 on M77 dev / heldout | 58.7% / 54.7%, not above shuffles |
| SA-fitted readings fit Tamil bigrams | keys fitted to shuffled strings | reach 97% S1, beating the key by 38 points |

The author's own 10-trial scramble null (50.1%) agrees with ours (49-51%); 7.7 points above it is inside our null spread (sd 5.5 points).

## Hypotheses
| hypothesis | verdict |
|---|---|
| K185 readings carry a Dravidian signal on held-out M77 (S1/S2/S3) | refuted / not supported (p >= 0.11, below noise-fitted keys) |
| 92.8% coverage is evidence for the readings | refuted (frequency-only, same on shuffled corpus) |
| Uniform 0.0% baseline is meaningful | refuted (case artefact) |
| Our bench has power to confirm a true key at this size | refuted for S1, S2; partial for S3 (N1 only) |

## What failed or was not checked
- The author's other tests (Parpola 80% agreement, entropy 4.11 bits, 97.7% uniqueness, PD inventory) were not re-run; uniqueness and entropy are known to be non-specific (see experiments/bench2026, SIGIL).
- Holdat corpus itself not used; author's fitting corpus overlaps M77 sites, so our heldout is not truly unseen by the author (would weaken a pass, not this fail).
- Readings with diacritics: only the first letter (S1) or stripped letters (S2, S3) are used; 5% of pins are non-ASCII.
- N2 uses only 3 restarts; the gap (key vs fitted) is so large that more restarts would not change the verdict.

## Next
- A more powerful bench needs either longer texts or a stronger score; the planted test says single-junction phonotactics cannot discriminate keys at ~2,300 short texts. Do not use S1-type "bigram hit rate" as evidence for any key.

Files: `run.py`, `common.py`, `out/bench.json`, `out/full.log`, `results.json`, `ledger_rows.csv`.
