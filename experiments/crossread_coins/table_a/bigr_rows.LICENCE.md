# Licence note for `bigr_rows.csv`

- **What it is:** transcriber A's rows from the BIGR type export, built by `../transcriber_a.py`. One row per distinct pair of legends under a name, with the number of types that carry it.
- **Source:** Coins of the Bactrian and Indo-Greek Rulers (BIGR), American Numismatic Society, https://numismatics.org/bigr/ . The export is `../raw/bigr/query.csv`, SHA-256 `847add2aebcc64ac2907cca31d58c0e13968f00db003c92e13e036e9e26ad8bc`.
- **Licence:** Open Database License 1.0 (ODbL), https://opendatacommons.org/licenses/odbl/1-0/ . This file is a derived database and is offered under the same licence.
- **Attribution:** contains information from Coins of the Bactrian and Indo-Greek Rulers (BIGR), which is made available under the Open Database License (ODbL) 1.0.
- **Changes made:** rows were selected by script, grouped and counted. The Kharosthi legend was cut into aksharas and its spaces were removed. The Greek legend is as BIGR gives it. The columns `name_id` and `same_person` were added by the script.
- **Kept apart:** no row from Wikipedia (CC BY-SA 4.0) is in this file. The two files are joined in memory only.
