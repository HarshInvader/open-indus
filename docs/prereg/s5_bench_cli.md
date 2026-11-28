# Pre-registration: S5, a one-command sound-key bench

Contributor: m0x1n. Written 2026-11-28, before the tool was run on any real key.

This is a tool, not a new hypothesis. I pre-register it anyway because its acceptance checks give numbers, and because the bench's thresholds should be fixed before anyone sees how a key does on them.

## What the tool does

`experiments/s5_bench_cli/bench.py KEY.csv --lexicon WORDS.txt [--signlist M77|ICIT]`

- **Key**: a CSV with columns `sign,value`, one value per sign, which is the format of the submission form. The tool prints and records the key's SHA-256 before it computes any score.
- **Texts**: M77 distinct texts, `dev_heldout(version=2)`, break-free runs of 2 or more signs. With `--signlist ICIT`: native ICIT, distinct, with a 75/25 split by edit-distance-1 families (seed 0), as in `signlist_robustness`.
- **Scores**, both computed on held-out texts:
  - **W, signs per word.** Inside every run of 2 or more consecutive keyed signs, find the fewest dictionary words that spell it (spans of up to 4 signs). W is keyed signs divided by words. A key whose consecutive values spell real words more often scores higher. This is `bench_pierson`'s S3.
  - **J, junction log-probability.** A letter-bigram model (add-one) is trained on the lexicon. J is the mean log P(first letter of the next value | last letter of the previous value) over adjacent keyed signs. This is `bench_pierson`'s S2, with the model learned from the submitted dictionary.
- **N1, own values shuffled**: the key's values permuted among its signs within 5 frequency bins (by dev frequency), 1,000 times. p = (1 + #null ≥ obs) / 1,001.
- **N2, keys fitted to noise with the same freedom**: 3 restarts on each of 2 noise corpora, a unigram-shuffled and a first-order Markov resample of the dev runs. Each restart starts from a random permutation of the key's values and hill-climbs (3,000 swaps) on noise-dev, then is scored on noise-held-out built the same way from the held-out runs. As in `bench_pierson`, keys fitted on real dev and scored on real held-out are reported as a description.
- **Verdict for a score**: **passes** if N1 p < 0.025 (Bonferroni over W and J) **and** the key's held-out score is above every N2 key. **The key passes** if at least one score passes. Every report states that the bench can refute a key but cannot confirm one (board R, 2026-11-17).

## Acceptance checks, fixed now

1. **Planted key (unit test, run by `python -m unittest`).** A synthetic language: 40 CV syllables and 300 words of 2 to 3 syllables, drawn with a fixed seed. 2,300 texts, each 1 or 2 words, are written in 40 syllable signs and split 75/25. Then:
   - (a) the true key passes on W;
   - (b) a key with its values deranged among the signs does not pass on W or J;
   - (c) the scores are identical across two runs with the same seed.
2. **Real-key regression.** Pierson's K185 from `experiments/bench_pierson/keys/`: first alternative per sign, written to CSV. Lexicon: the Tamil lemmas plus the LM vocabulary in that folder, transliterated with `bench_pierson/common.py`'s rules. The Wiktionary lists `bench_pierson` used are not in the repository. Expected: **does not pass**, matching `bench_pierson`'s verdict. If it passes, I will report a disagreement with `bench_pierson` and not present the tool as validated.

If check 1(a) fails, the tool has no power on the planted language and I will say so. If 1(b) fails, it is miscalibrated and I will say so. Either way I report the numbers.
