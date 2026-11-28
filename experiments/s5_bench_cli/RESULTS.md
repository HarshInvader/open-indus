# S5: the sound-key bench as a one-command tool

Contributor: m0x1n (starter task S5). Pre-registration: `docs/prereg/s5_bench_cli.md`, sha256 `c744ee69…`, committed before the tool was run on any real key.

## Conclusion

**Anyone can now score a proposed reading with one command.** You need a key CSV in the same format as the [submission form](../../.github/ISSUE_TEMPLATE/submit-reading.yml) and a word list:

```bash
.venv/bin/python -I experiments/s5_bench_cli/bench.py my_key.csv --lexicon my_dictionary.txt --out my_key.bench.json
```

The tool prints the key's SHA-256 first, then scores the key on held-out texts. Each score is checked two ways: against the key's own values shuffled among signs of similar frequency, and against keys fitted to noise with the same freedom. The planted-key check is part of its test suite. Both pre-registered acceptance checks pass:

1. **Planted key.** In a synthetic language of the corpus's size, the true key passes and a deranged key does not. The output is identical across runs.
2. **Real-key regression.** Pierson's K185 does not pass, which matches the verdict reached by hand in `experiments/bench_pierson/`.

## How it scores (fixed in the prereg)

| Step | What |
|---|---|
| Texts | M77 distinct, split v2, break-free runs of 2+ signs (1,656 dev, 548 held-out). `--signlist ICIT` uses native ICIT with a 75/25 split by near-copy family. |
| **W**, signs per word | Inside each run of consecutive keyed signs, the fewest dictionary words that spell it (spans up to 4 signs). Higher means the values join into real words more often. (`bench_pierson` S3) |
| **J**, junction log-probability | A letter bigram learned from the submitted dictionary, applied across each pair of adjacent keyed signs. (`bench_pierson` S2, with the model taken from the user's own dictionary) |
| N1 | The key's own values shuffled within 5 frequency bins, 1,000 times |
| N2 | 3 restarts × 2 noise corpora (unigram-shuffled, Markov) of keys hill-climbed (3,000 swaps) with the key's own values, scored on noise held-out. Keys fitted on real dev and scored on real held-out are reported too. |
| Pass | For a score: N1 p < 0.025 **and** above every N2 key. The key passes if either score passes. |

Every report says the bench can refute a key but not confirm one. It also warns when a key is too small for N1 (a frequency bin with fewer than 2 signs) or covers under 5% of held-out tokens.

## Acceptance check 1: planted key (`test_bench.py`)

The synthetic language has 40 CV syllables and 300 words of 2 to 3 syllables with Zipf frequencies. 2,300 texts of 1 to 2 words are written in 40 signs and split 75/25. The test settings are 300 shuffles, 1,500 swaps and 2 restarts. Full numbers are in `planted_check.json`.

| Key | W held-out | N1 mean | N1 p | best N2 key | W passes | J passes |
|---|---|---|---|---|---|---|
| True key | **2.34** | 1.17 | 0.003 (floor) | 1.40 | **yes** | no |
| Deranged key | 1.14 | 1.11 | 0.11 | 1.40 | no | no |

The test also checks that two runs with the same seed give identical JSON, and that the CSV reader rejects bad rows: a repeated sign, an empty value. All 4 tests pass in about 26 seconds.

J has no power in this planted language, by construction. Every syllable is CV, so every junction is vowel-to-consonant whatever the key. That is a limit of the toy language, not of the score. It is also a reminder that J measures only phonotactics at sign boundaries.

## Acceptance check 2: K185 regression (`validate_k185.py`)

The key is K185 (200 signs, HIGH confidence, first reading per sign); 187 of the signs occur in the corpus, covering 70.8% of held-out tokens. The lexicon is the Tamil lemmas plus the LM vocabulary in `bench_pierson/keys/`, 1,529 words. The Wiktionary lists `bench_pierson` used are not in the repository.

| Score | K185 held-out | Own values shuffled | N1 p | Best noise-fitted key | Fitted on real dev | Verdict |
|---|---|---|---|---|---|---|
| W | 1.003 | 1.014 | 0.98 | 1.18 | 1.13 to 1.17 | fail |
| J | −3.72 | −3.54 | 0.88 | −2.50 | −2.39 to −2.42 | fail |

**K185 does not pass**, as `bench_pierson` found by hand: there S3 had held-out 1.011 against a null of 1.018, p = 0.75. Keys fitted to noise again score far above the real key. The tool reaches the same verdict in 7 seconds.

## Caveats

- **The bench can refute a key, not confirm one.** `bench_pierson`'s planted Tamil corpus showed that single-junction scores have little power on real-language data at this size. The planted check here uses a cleaner toy language, so passing it shows the machinery works. It does not show the bench can find a true historical key.
- **Values are compared as plain letters.** Diacritics are stripped and case is ignored. Alternatives in one cell (`a/b`) are not supported, which follows the form's "one value per sign" rule.
- **The dictionary is the submitter's choice.** A huge or permissive word list inflates W for every key, real and null alike. N1 and N2 use the same list, so the comparison stays fair, but scores from different lexicons should not be compared with each other.
- Python 3.13.18, pinned packages. Deterministic for a given `--seed`.

## Files

- `bench.py`: the tool, usable as a library (`bench()`) or from the command line.
- `test_bench.py`: planted-key and input tests, run with `python -m unittest`. Writes `planted_check.json`.
- `validate_k185.py`: real-key regression. Writes `k185_key.csv`, `k185_lexicon.txt` and `k185_result.json`.
- `results.json`: both acceptance checks in one machine-readable file.

```bash
.venv/bin/python -I -m unittest discover -s experiments/s5_bench_cli -p "test_*.py" -v
.venv/bin/python -I experiments/s5_bench_cli/validate_k185.py
```
