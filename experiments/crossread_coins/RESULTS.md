# Cross-read on coins: stopped at the count gate (F4). The open sources give 28 names with both legends; the sealed gate needs 30.

- **Prereg:** `docs/prereg/crossread_coins.md`, sealed 2026-11-25 as v2 (tag `crossread_coins`), after one fresh review.
- **Steps done after sealing, in the sealed order:**
  1. The comparer `compare.py` was written and hashed before any table B existed (tag `crossread_coins_compare`). It was never run.
  2. The BIGR export was copied to `raw/bigr/`, and its sha256 matches the prereg.
  3. Transcriber A, `transcriber_a.py`, was run. Its table is in `table_a/`: BIGR rows (ODbL) and Wikipedia rows (CC BY-SA) are in separate files, each with a licence note.
- **Not done:** transcriber B, the comparison, the title list, the test code and any test statistic T. No T was computed on any pair, real or planted.

## Why the study stops
- **Transcriber A holds 28 distinct names** with a usable pair: 26 from BIGR and 2 from Wikipedia (Azes, Azilises). See `table_a/summary.txt`.
  - Most Wikipedia ruler pages give name forms, not full legends: 12 of the 27 pinned pages give a passage with both legends.
- **The comparison can only remove names.** A name passes only if A and B agree, so at most 28 names can pass.
- **F4, sealed:** "If fewer than 30 names pass the table protocol, the study does not run. No smaller K0 replaces it." Decision 7 ruled that the gate has no fallback.
- So the study stops here. Running transcriber B would not change the outcome.

## What this can and cannot say
- **It can say:** on openly licensed sources, the bilingual Indo-Greek and Indo-Scythian coin legends give too few distinct names for the sealed cross-read test at 15 pairs with 20 sets. The "cuneiform on both sides" caveat on `anchor_crossread` stays.
- **It cannot say** whether the rule transports across scripts. That was not tested.
- **Bearing on the 2027 bar:** none.

## What would reopen it
These are leads for the owner. Nobody was contacted.
- Gandhari.org lists 337 coin legends, but the pages opened state no licence. Permission or a licence statement would be needed.
- Whitehead 1914, the Lahore catalogue, is public domain in the United States, but not where the term is life plus 70 years.
- Bopearachchi 1991 and Mitchiner are not open.
- A new prereg would be needed. Lowering the gate is not allowed under this one.

## Disclosures
- **Reviewer's estimate:** the fresh review expected about 21 names from BIGR. A found 26, using a field-based same-person proxy plus one hand-marked type. Either way the count is under 30.
- **Comparer choices:** `compare.py` fixes eight choices the seal leaves open, listed in its docstring. It never ran.
- The pinned Wikipedia wikitext (27 revisions) was kept outside the repo. The revision ids are in `wikipedia_rows.csv`.
