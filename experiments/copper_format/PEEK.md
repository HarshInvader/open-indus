# copper_format: peek disclosure

Written 2026-11-25 by the plan-13 planner, from its own transcript only. The data was not re-opened or re-printed to write this.

## What was printed

- **File:** `data/icit_texts.jsonl`.
- **Command:** an inline Python heredoc run with `.venv/bin/python -` from the repo root. It was not saved as a script. It did this:
  - kept rows with `type == 'TAB:C'` and both `width_mm` and `height_mm` above 0 (204 of 230 rows);
  - grouped them by `tuple(seq)`, the ICIT sign sequence;
  - kept groups with 4 or more measured rows (12 groups, 100 rows);
  - for each group printed: the row count, the first 6 signs of the key, and the first 6 entries of the sorted set of distinct `(width_mm, height_mm)` pairs.
- **So the view was partial.** At most 6 distinct size pairs per legend were shown, sorted by width. No row ids, CISI numbers or side-B kinds were printed, and the sizes were not crossed with `datasets/open/copper_tablets.csv`.

## The 12 legends, exactly as printed

Keys are ICIT `seq` tuples. The planner never mapped them to the `T01`-`T18` type codes of `copper_tablets.csv`, so the type code of each is **unknown**. Keys printed with 6 signs may be longer in the file (the print cut at 6); whether they are is **unknown**.

| # | Measured rows | Key (first 6 signs) | Size pairs shown (width, height) |
|---|---|---|---|
| 1 | 27 | W503 W615 W752 W740 | (28.6, 28.6), (31.0, 23.5), (32.0, 22.0), (32.0, 24.0), (32.0, 26.0), (32.5, 21.5) |
| 2 | 14 | W806 W845 W061 W407 W850 W900 | (30.0, 14.5), (31.0, 25.0), (31.5, 14.0), (32.0, 24.0), (33.0, 23.0), (33.5, 13.5) |
| 3 | 4 | W415 W220 W845 W407 | (27.0, 25.0), (27.4, 28.4), (28.0, 28.0), (29.5, 26.0) |
| 4 | 4 | W706 W033 W923 W740 W001 | (35.5, 21.0), (36.0, 21.0), (36.0, 24.0), (37.0, 20.5) |
| 5 | 12 | W235 W705 W033 W845 W407 W321 | (31.0, 15.0), (31.0, 16.0), (32.0, 25.0), (32.5, 25.5), (33.0, 23.5), (33.0, 25.0) |
| 6 | 7 | W231 W017 W585 W095 W520 W032 | (28.0, 13.0), (32.0, 14.0), (32.0, 22.0), (32.5, 15.0), (33.0, 14.0), (36.8, 23.6) |
| 7 | 6 | W798 W240 W845 W061 W407 | (31.0, 21.0), (31.8, 22.2), (31.8, 22.9), (32.0, 22.0), (34.0, 24.0), (35.0, 23.0) |
| 8 | 4 | W235 W233 W222 W740 | (36.0, 21.0), (37.0, 20.0), (37.0, 22.0), (38.5, 21.0) |
| 9 | 6 | W905 W032 W597 W142 W617 | (23.0, 23.0), (30.0, 23.0), (30.5, 23.0), (32.0, 22.0), (32.5, 23.0) |
| 10 | 4 | W017 W585 W388 W740 | (34.0, 21.0), (34.8, 24.1), (35.0, 21.0), (36.0, 23.0) |
| 11 | 6 | W777 | (28.0, 13.0), (32.0, 14.0), (32.5, 15.0), (32.5, 16.0), (33.0, 14.0), (34.3, 26.2) |
| 12 | 6 | W706 W033 W923 W740 | (32.0, 20.0), (32.5, 22.5), (34.0, 20.0), (35.0, 22.0), (35.5, 22.5), (36.0, 25.0) |

## The single-sign row that looked mostly narrow

- **Legend:** row 11, key `('W777',)`, 6 measured rows.
- **What was seen:** five of the six size pairs shown have a height of 13 to 16 mm; one is 26.2 mm.
- **Row ids (ICIT id or CISI number):** unknown. They were not printed.

## Also seen, and relevant

- **Rows 2, 5 and 6 showed mixed heights too:** some pairs near 13.5 to 16 mm beside pairs near 22 to 25.5 mm within one legend. The plan's disclosure mentioned only the single-sign row; this is the fuller statement. The planner did not see which tablets of those legends carry a picture or a sign face.
- **From `datasets/open/copper_tablets.csv` (no sizes):** the header and first row (M77 1701, picture, type T05); counts by `source`, `kind` and `how`; and the kind counts per type for the 16 types holding two or more kinds, including the sign-face counts for T02, T03, T05, T06 and T15.
- **A count only:** 168 of the table's 190 ICIT rows link to a measured ICIT row.

## Consequence for the gate

The planner has seen that a short side of about 13 to 16 mm exists as a distinct format in at least four legends (rows 2, 5, 6, 11), and that the single-sign legend is mostly in that format. It has not seen the kind-by-size cross within any legend. The study's minimum and bars should be hashed by someone who treats this as prior knowledge; the plan's tighter bar (p ≤ 0.005) was set for this reason.
