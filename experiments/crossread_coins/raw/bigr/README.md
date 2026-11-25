# BIGR type export for `crossread_coins`

One outside file. The prereg is `docs/prereg/crossread_coins.md` (sealed v2), section "Data sources and licences".

| file | bytes | SHA-256 | what it is |
|---|---|---|---|
| `query.csv` | 2,047,926 | `847add2aebcc64ac2907cca31d58c0e13968f00db003c92e13e036e9e26ad8bc` | the full type export, 2,109 type rows, as downloaded and unchanged |

## Source and attribution

- **Database:** Coins of the Bactrian and Indo-Greek Rulers (BIGR), American Numismatic Society, https://numismatics.org/bigr/
- **Export URL:** `https://numismatics.org/bigr/query.csv/?q=*:*`
- **Fetched:** once, on 2026-11-25, with the User-Agent `open-research-site/1.0`. The hash equals the one sealed in the prereg.
- **Licence:** the site states that "Coin type data are made available with an Open Database License". That is the Open Database License 1.0 (ODbL), https://opendatacommons.org/licenses/odbl/1-0/
- **Attribution:** contains information from Coins of the Bactrian and Indo-Greek Rulers (BIGR), which is made available under the Open Database License (ODbL) 1.0.
- The site says that images and data about physical specimens belong to their holding institutions. This file holds type data only. No image and no specimen record is copied here.

## What the licence asks of this repo

- Keep this notice with the file and with any copy of it.
- A table derived from this file is offered under the ODbL as well. That is `../../table_a/bigr_rows.csv`, which carries its own note.
- Rows from this file are never mixed in one file with rows from Wikipedia (CC BY-SA 4.0). The two are joined in memory only.

## Use

`experiments/crossread_coins/transcriber_a.py` reads the columns `RecordId`, `Authority`, `Obverse Legend` and `Reverse Legend`. It stops if the SHA-256 differs from the value above.
