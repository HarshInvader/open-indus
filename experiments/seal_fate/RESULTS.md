# Proskouriakoff test: object fate vs sign content (board #33, N1)

## Verdict

**Mostly negative, with one unreplicated lead.**

- Where a seal was dropped (a street or lane vs inside a room at Mohenjo-daro) does not go with what its text says. Neither the sign mix nor the text length differs. A 1.5x shift in any of the four sign classes would have been caught 82-100% of the time.
- Broken seals at Harappa carry the same sign mix as random fragments of intact seals.
- One pre-registered test passed. At Mohenjo-daro, seals whose register prints a dimension as "?" (a proxy for breakage) carry about 1.7x more closers (mostly the jar sign M342) than random fragments of intact seals (Holm p = 0.018). But it was meant as the replication of the Harappa breakage test, and Harappa shows no such effect (closer z = +0.98). By the pre-registered rule it is **not a positive**. The simplest explanation is mechanical: if breakage tends to spare the end of the text, fragments keep their closers. The red-team task below asks someone to test that.
- Most fates the brief asked about cannot be tested from these registers. The 1930s seal tables have no remarks column, so burnt, cut, re-used, hoard, burial, drain/well/gate and surface finds are recorded 0-10 times each.

Nothing here gives a sign a meaning or a sound.

## Data and coding

- **Remark sources** (`extract.py` → `remarks.csv`). The seal tabulations (FEM, EH, MIC, CE) hold only type, size, material, findspot, level and field number. So:
  - **Harappa:** I parsed Vats 1940 vol. I's per-trench lists of finds, where each seal has its own entry, e.g. "Unicorn seal, upper part broken. Pl. LXXXIX, 127 … No. 2476; Square N 9/9; Depth 15 ft. 10 in."
    - 305 EH serials have an entry.
    - Field-number check against the EH table: 209 agree and 43 disagree, mostly OCR digit slips (S/5, 3/8). 53 could not be checked.
  - **Mohenjo-daro:** I used the Mackay 1938 tabulation: findspot (street, lane, alley or "between blocks" vs block/house/room), level, and dimensions ("?" = could not be measured). I also used 9 sentences in the FEM seal chapter that name a seal number together with a condition word.
- **Blind coding.** `code.py` reads only `remarks.csv`. Every "[n] pictograms" phrase is masked to "[k]", including OCR variants. No sign sequence was opened until `test.py` ran after the pre-registration hash. The scheme was written first (`CODING_SCHEME.md`).
- **Consistency.** I re-coded a 20% sample by hand (61 Harappa and 138 Mohenjo-daro items, seed 7, shuffled order, codes in reverse order), after the hash and before outcomes (`recode_hand.py`, `kappa.json`).
  - Kappa: BROKEN 0.96 (1 miss: "lower half of an unfinished seal"), ROOM 0.98, and 1.0 for OPEN, BROKEN_PROXY, UNFINISHED, WORN, HOARD, BURIAL and SURFACE.
  - Caveat: the hand coder also wrote the rules, so this measures consistency, not independence.
- **Fate counts** (all coded objects). Harappa (Vats, 305 objects):
  - BROKEN 94
  - UNFINISHED 14
  - SURFACE 10
  - WORN 7
  - BURIAL 5 (area headers only)
  - HOARD 1
  - BURNT, CUT, REUSED, OPEN: 0

  Mohenjo-daro (FEM, 695 objects):
  - ROOM 509
  - OPEN 167
  - BROKEN_PROXY 43
  - prose BROKEN 5
  - WORN 5 (mostly false hits: "hair was worn")
  - SURFACE 2
  - BURNT, CUT, REUSED, HOARD, BURIAL, DRAIN/WELL/GATE: 0
- **Linked to M77 with text:** Harappa 249, Mohenjo-daro 636. All tests use distinct texts within each fate group.

## Tests (pre-registered: `docs/prereg/seal_fate.md`, sha256 in `docs/prereg/HASHES.txt`)

The sign classes were fixed in advance:
- openers: 9 signs from GRAMMAR.md
- closers: 7 signs (M342, M211, M15, M254, M12, M14, M388)
- fish: M59-M75
- numerals: M86-M121, minus M90, M92 and M93

The statistic is the sum of z² over the four class shares, which makes it two-sided.

| Test | n | Statistic | p | Holm p | Power (share x1.5 / x2 per class) | Verdict |
|---|---|---|---|---|---|---|
| H1 Harappa broken vs truncation null | 62 broken (217 signs), pool 172 intact | T = 4.52; z: opener +0.75, closer +0.98, fish −0.13, numeral +1.72 | 0.34 | 1.0 | opener 0.23/0.66, closer 0.91/1.0, fish 0.49/0.98, numeral 0.96/1.0 | not supported |
| H2 MD "?"-dimension vs truncation null (replication of H1) | 34 (133 signs), pool 570 | T = 15.5; closer z = +3.57 (share 0.18 vs 0.10); others within ±1.3 | 0.0044 | 0.018 | opener 0.18/0.76, closer 0.47/0.99, fish 0.42/0.98, numeral 0.67/1.0 | passes alone; replication rule fails (0/4 classes replicate) |
| H3 MD street/lane vs room, sign classes | 148 open, 452 room; strata type × 5-ft band | T = 4.52; largest z numeral +1.67 | 0.33 | 1.0 | 0.82-1.0 / 1.0 for all classes | refuted at stated power |
| H4 MD street/lane vs room, text length | same | mean 4.83 vs 4.85 signs (diff −0.01) | 0.96 | 1.0 | +0.25 sign 0.19, +0.5 sign 0.68, +1 sign 1.0 | refuted for differences ≥ 1 sign |

- **Truncation null.** Each broken object is replaced by a random window of the same length from an intact text of the same type, 5,000 sets.
  - Calibration on pseudo-broken sets: false-positive rate 0.055 (H1) and 0.050 (H2). The null is well calibrated for random-position breaks.
  - It is not calibrated for breaks that preferentially keep one end of the text, which is the main alternative explanation for H2.
- **Permutation null for H3/H4.** OPEN/ROOM labels are shuffled within object type × 5-ft depth band, 5,000 times.
- **Planted controls.** The class share in the fate group is raised by the stated factor over the null expectation, 200 plants each.
  - Power is low for openers on broken seals: openers are rare (about 5% of tokens).
  - H2 has only 0.47 power for a 1.5x closer shift, so its observed 1.7x is near the edge of what n = 34 can see.

**Exploratory per-sign scans** (BH within each scan; not part of the verdict):
- **Harappa broken:** M86 (one stroke) is on 7 broken texts against 0.84 expected (q = 0.007). At Mohenjo-daro the same sign shows nothing (p = 1.0). A single stroke is also what a damaged edge is easiest to read as, so this may be a transcription effect, not a fate effect.
- **Mohenjo-daro "?"-dimension:** the top sign is M342 (17 vs 9.3 expected, q = 0.24). This is the same signal as H2.
- **Mohenjo-daro street vs room:** nothing passes (best M121, q = 0.69).

## What failed or was not checked

- **Untestable fates.** Burnt, cut/deliberately broken, re-used, hoard, burial, drain/well/gateway/wall, and surface vs stratified: 0-10 cases each. The registers do not record them per object. Mackay's FEM prose and Marshall 1931 vol. I building descriptions mention some seals by field number in context. A hand pass over those, keyed by field number, is the only way to get these fates from material we already hold.
- **No deliberate-vs-accidental split.** No register says a seal was broken on purpose. CUT = 0.
- **Weak breakage proxy at Mohenjo-daro.** "?" in a dimension cell may be breakage, a worn edge or an OCR blank. Only 5 FEM seals are called broken in prose.
- **No Harappa findspot types.** Vats entries give squares, not streets or rooms, so H3/H4 have no second-site replication.
- **Marshall 1931 (MIC), Chanhu-daro (CE) and the non-Vats EH rows** carry no remarks and were not used.
- **Same-person coders.** The hand recode was done by the rule writer. A second, independent coder on `recode_sheet.csv` would make the kappas meaningful.
- **Uncorrected link mismatches.** 43 Vats-EH field-number mismatches were not corrected, and those objects are still in H1. Most look like OCR slips.
- **Post-hoc robustness checks were not run.** The prereg falsifiers (seals only, block strata) were written for H1/H3. For H2 I left the attack to an independent red team (board rule: never red-team your own result).

## Files

- `extract.py` → `remarks.csv` (masked remark text)
- `CODING_SCHEME.md`, `code.py` → `fate.csv` (blind codes, hashed)
- `recode_sheet.csv`, `recode_hand.py` → `recode.csv`, `kappa.json`
- `test.py` → `results.json`, `test.log`
- `ledger_rows.csv`

## Next step

The red team (board M6) should rerun H2 with a truncation null that keeps the text's end or start, at the rates real broken seals show. Harappa's 62 broken seals, whose M77 transcriptions mark the lost positions, give those rates. If an end-anchored null removes the closer excess, the lead is closed. If it survives, the next step is to check the "?" cells against the CISI photographs, to confirm these seals are really broken.
