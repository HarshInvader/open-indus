# HARP pack readiness check (2026-11-24)

Question: on the day the HARP sheet arrives, can the sealed pack be scored with no code changes?

**Verdict: ready for a CSV sheet with Wells or W/M-prefixed sign codes and CISI numbers. Not ready for the likely case: an Excel file, bare or non-Wells sign numbers, or no CISI numbers.** No real HARP data was read. None is in hand.

## 1. Hashes
All 7 files tagged `harp_pack` in `docs/prereg/HASHES.txt` match: `harp_pack.md`, `loader.py`, `score.py`, `power.py`, `test_loader.py`, `power.json`, `fixture/harp_fixture.csv`. There are no mismatches. `tablets.csv` also matches its `tablet_archives` hash.

The prereg names or relies on these files, which have no hash:
- `power.log` (named in the prereg): `cfc5d0a6...c5601beb`
- `data/icit_texts.jsonl` (used by C6; untracked and gitignored): `a7925650...44ee51b`
- `sources/shaunmortal_indus/data/bridge_WM.json` (read on every load; untracked): `03fb6181...89c549`
- `corpus/load.py`: `3c3cb564...1359d9`

## 2. Schema and the synthetic run
- The schema is written down in the prereg's loader section and in `CANON` in `loader.py`.
- `test_loader.py` passes: ALL OK.
- I built a 1,276-row sheet of made-up values in `/tmp/harp_synth_*`, with HARP-style headers. It had 900 sherds and 376 docket tablets keyed by real `tablets.csv` CISI ids. Three sherds carried ICIT pottery CISI ids.
- I ran `.venv/bin/python -I experiments/harp_pack/score.py <path>`. It finished in about 1 s with exit 0.
- All 12 headers mapped. Units were converted (cm to mm). C1, C2, C6, C7 and C9 were all eligible and Holm-scored, and C5 was scored too. As expected for random data, every kept test came out FAIL and C5 came out PASS.
- The pack reads any path. No in-repo path is required.
- The folder was deleted afterwards.

## 3. Power citations in `sizing_census/RESULTS.md`
- The sealed-side figures match `power.json`:
  - C6 curve: 0.84-1.00
  - C9: 0.82 at n 120 (pessimistic) and 0.39 at n 72
  - the minimum sizes 184 / 146 / 146
- The headline route figures are the census calculator's own output, not the pack's. The pack's values at the same n are:

| test | census | pack |
|---|---|---|
| C6 | 0.82 | 0.84 |
| C1 | 0.96 | 0.95 |
| C2 | 0.84 | 0.815 |

  None of these changes a verdict.

## 4. Blockers
1. **`openpyxl` is not installed in `.venv`**, and neither is `xlrd`. An `.xlsx` file fails to load. The fix is to install it, or to export the sheet to CSV, which the prereg does not cover.
2. **Only the first worksheet is read.** `load(..., sheet=0)` is not exposed on the command line. If objects and sherds sit on separate tabs, a code change or an amendment is needed.
3. **The `sign_scheme` argument is not reachable from the `score.py` command line.**
   - A scheme written in the header, such as "Signs (Mahadevan)", is ignored.
   - So bare numbers without a scheme column make C1, C2, C6, C9 and C5 UNTESTABLE.
4. **There is no hook to apply a sign concordance** (Parpola or a HARP code) in `loader.py`. The prereg's concordance amendment would need code.
5. **Joining to ICIT needs CISI numbers.**
   - Without them C7 has zero units, and C6 runs only as an exploratory test.
   - Neither ICIT nor `tablets.csv` holds HARP field numbers, so a field-number-to-CISI table would be needed.
6. **Minor:** the prereg says `raw/` and `score.py` says `raw/harp/`. A unit written as "Length in" after a space is not parsed; "(in)" is.
