# sealing_crop count gate: FAIL. Only 63 sealing impressions qualify, short of the 80 the study needs before any skip

- **Rules:** `MINIMUM.txt`, written 2026-11-25T19:13:16Z before any count. sha256 `ffa2b73988c4cd93e22bf8b1a720f3588a9225b83d29e52475c84dfda8024779`.
- **Script:** `count_gate.py`, run once with `python3 -I`. Output: `count_gate.json`.
- **Data:** ICIT metadata in `data/icit_texts.jsonl`, plus the list of CISI vol 1-2 photo boxes in `experiments/scene_text/work/faces.json`.
- **What was not done:** no image was opened, no share was coded, and no count was crossed with any outcome. No prereg was written. `HASHES.txt` was not touched.

## Counts

**ICIT sealings and tags (type TAG\*).** 262 rows on 213 objects.

| Site | Rows with a CISI number | Rows with a local photo | Eligible (primary) | Inclusive, record only |
|---|---|---|---|---|
| Lothal | 89 | 75 | 32 (28 objects) | 72 (57 objects) |
| Kalibangan | 28 | 26 | 18 (13) | 21 (16) |
| Mohenjo-daro | 22 | 18 | 12 (10) | 17 (13) |
| Harappa | 18 | 3 | 0 | 3 (3) |
| Banawali | 1 | 1 | 1 (1) | 1 (1) |
| Rakhigarhi, Nausharo, Chanhu-daro, Desalpur, Hulas | 7 | 0 | 0 | 0 |
| **Total** | **165** | **123** | **63 (52 objects)** | **114 (90 objects)** |

Notes on the table:

- **Dholavira and the other rows without a CISI number have no local photo.** Dholavira alone has 76 TAG rows.
- **Most Harappa sealings are CISI vol 3 finds** (for example H-1719 to H-1722), and vol 3 is not on disk.
- **Primary eligibility needs an animal or icon recorded in ICIT** (rule b), plus at least one transcribed sign. The symbol values among the 63 rows are Bull1 42, Elep 11, Bull 5, Mult 2, Scene 1, CompBull 1 and Zebu 1.
- **Of the 51 photographed rows that fail rule b,** 43 have ICIT symbol "-" (the field is not filled) and 8 have "None".

**Calibration seals.** These are intact seals with a local photo: complete = true, a named animal, at least one transcribed sign, and not sharing a CISI number with any eligible sealing.

- **All seal types:** 744 square seals (SEAL:S) and 752 seals in all.
- **Square seals by site:** Mohenjo-daro 524, Harappa 147, Kalibangan 27, Lothal 23, Chanhu-daro 10, Banawali 9, Nausharo 4.

## Checks (from MINIMUM.txt)

| Check | Needed | Found | Result |
|---|---|---|---|
| C1 eligible candidates | ≥ 107 (80 / 0.75) | 63 | fail |
| C2 candidates outside Lothal | ≥ 34 (25 / 0.75) | 31 | fail |
| C3 sites with ≥ 7 candidates | ≥ 3 | 3 (Lothal, Kalibangan, Mohenjo-daro) | pass |
| K1 calibration seals, ≥ 2 sites | ≥ 30 | 744 | pass |

**Verdict: FAIL.** The study closes at the gate. The failure does not depend on the skip allowance. At a 0% skip rate, 63 is still below the bare minimum of 80, so no rater could rescue it.

## Disclosures

- **Implementer reading of rule b.** The ICIT symbol "Unknown" counts as not determinable. "Mult", "Scene" and "Othr" count as named icon codes, as the rule is literally worded. Dropping those 3 rows would only lower the count.
- **The inclusive set would clear C1 and C2** (114 rows; 42 outside Lothal). That set includes rows whose design type is not recorded in ICIT. MINIMUM.txt makes it record-only, so it cannot be used for the verdict.
  - Choosing it now, after the counts were seen, would be a post-count change.
  - A future version could make the rater decide the design type from the impression outline. That would need its own MINIMUM, written with the disclosure that these counts are already known.
- **Downloads from the prior-art step** (two open PDFs) are in `raw/`, which git ignores.
