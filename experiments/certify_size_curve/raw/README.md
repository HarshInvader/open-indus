# Raw data for `certify_size_curve`

Two outside sources, both Oracc open data under CC0 1.0 (public domain dedication, https://creativecommons.org/publicdomain/zero/1.0/). Downloaded 2026-11-24. The prereg is `docs/prereg/certify_size_curve.md`.

## Files here

| file | bytes | SHA-256 | what it is |
|---|---|---|---|
| `ogsl/ogsl.zip` | 248,486 | `46d8a29c11c351baa922c912c4472d6fb7ec7f79e76d4d473f29d58d4caf860f` | Oracc Global Sign List, as downloaded |
| `saao/neoass_skeletons.tsv` | 43,122 | `3ab28cf9dae963f5930298e13e75ddde3790ea41ad5119f4c7faa76f14aa8823` | derived lexicon: 3,632 consonant skeletons |

## Sources

- **Sign list:** https://oracc.museum.upenn.edu/json/ogsl.zip (CC0). The study reads the member `ogsl/ogsl-sl.json`.
- **Lexicon:** https://oracc.museum.upenn.edu/json/saao.zip (State Archives of Assyria online, CC0), member `saao/gloss-akk-x-neoass.json`.
  - SHA-256 of `saao.zip`: `29bcf61b55ef291a97180f836ca620e13a1bcab802dad7ff64e2baf2e9d7a17f` (65,783,820 bytes).
  - **`saao.zip` is not committed because of its size** (66 MB; the one glossary inside is 133 MB unpacked). Only the derived file is kept.

## Rebuild

Download `saao.zip` from the URL above into a new, empty directory outside the repo. Then, from the repo root:

```
python3 -I experiments/certify_size_curve/build_lexicon.py PATH_TO/saao.zip
```

- The script stops if the archive's SHA-256 differs from the value above, or if the skeleton counts differ from the prereg (3,632 in all; 1,612 / 896 / 259 / 48 at 4 / 5 / 6 / 7 consonants).
- It writes `raw/saao/neoass_skeletons.tsv` and prints its SHA-256, which must equal the value in the table.
- It reads the glossary only. It reads no text and scores nothing.

## The derived file

- UTF-8, tab-separated, one header row, rows sorted by skeleton.
- Columns: `skeleton` (letters P T K S Š M N L R H W), `consonants` (its length), `normalised_forms` (distinct normalised forms that give it), `headwords` (glossary entries that give it).
- All lengths are kept. The study uses lengths 4 to 7 and the first column only.
- Rule: every normalised form of every headword; name classes and numerals left out; long vowels shortened; b p to P, d t ṭ to T, g k q to K, s ṣ z to S, ḫ to H; y, j and the glottal stop dropped; a doubled consonant written once.

The study code loads only the two files in the table and checks both hashes first.
