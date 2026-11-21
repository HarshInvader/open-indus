# Meaning claims from culture, archaeology and history

## Conclusion

Few untested ideas remain. We catalogued 44 published proposals about what Indus signs mean. 33 are new to the repo's literature catalogue.

- 20 were already tested by earlier experiments. None passed.
- 14 cannot be tested with our data.
- 10 can be turned into rules. Only one of them is a fresh L2 claim with a real chance of a decisive answer: Mukhopadhyay's "fish signs mean gems or precious goods" (2025).

No statistical tests were run. All counts below are descriptive and come from `counts.py` (output in `counts.json`). The catalogue is `CATALOGUE.csv`, built by `build_catalogue.py`.

## What the catalogue holds

Each row gives the author, year, signs (M77 and, where known, Wells/ICIT), claimed meaning, basis, source, status and, for testable rows, a rule, prediction, data, power estimate and kill condition.

| Status | Rows |
|---|---|
| Already tested (see the experiment named in the row) | 20 |
| Untestable with our data | 14 |
| Testable | 10 |

Why most ideas are closed:

- Office, title, emblem, toponym and licence ideas were closed by `administration`, `context`, `toponyms`, `identifiers` and `tablet_archives`.
- Measure and vessel ideas (M328, M342, the Wells 40-litre jar) were closed by `m328_measure`, `m342_offsite` and `self_label`.
- Meluhha trade goods have no scholarly sign link outside fringe rebus work. The candidate signs were not enriched on western objects (`meluhha`).
- Untestable rows need data we lack: vessel capacities, goblet volumes, gold-needle samples, or sites with fewer than 20 texts (Kanmer, the Kutch sites apart from Dholavira).

## Ranked testable rules

The ranking puts the chance of a decisive answer first and the ladder value second.

1. **Fish = gems or precious goods (Mukhopadhyay 2025). L2.**
   - Rule: inscribed objects from bead, lapidary or jeweller units carry fish signs more often than a null that permutes unit labels within each site and weights units by their total finds.
   - Base rate: fish signs appear in 27% of ICIT texts and 34% of M77 texts.
   - Data: only 31 objects come from coded bead units now. Mohenjo-daro jewellers' hoards need coding from the Mackay and Marshall OCR.
   - Power: about 0.6 at an odds ratio of 2 if the objects are independent. It is much lower with clustering.
   - Kill: a ratio of 1.2 or less at the confirmation site.
2. **Weight sign (Parpola sign 193, possibly M197/W575). L2.**
   - Rule: the sign is enriched on objects from units that contain weights, under a find-density null.
   - Data and counts: Harappa weight units hold 610 objects. M197 appears in 55 M77 texts. First check that sign 193 maps to M197.
   - Power: Mohenjo-daro alone is underpowered.
   - Kill: a ratio of 1.2 or less at Harappa.
3. **M87 substitutes for M59 (Parpola's vēl). L1.**
   - Rule: compare the left and right contexts of M87 and M59 with 50 frequency-matched sign pairs.
   - Counts: M87 appears in 232 texts and M59 in 289, so power is ample.
   - Kill: overlap at or below the median of the matched pairs on held-out data.
4. **Fixed partners of M403 (Muruka-vēl, Muruka-ppiḷḷai). L1.**
   - Rule: M403's next sign concentrates on M87 or the squirrel sign beyond a frequency-matched null.
   - Counts: M403 appears in 66 texts, 17 of them held out.
   - Kill: a held-out partner share inside the null's central 90%.
5. **Crop + numeral on storage jars (Kenoyer 2006, Mukhopadhyay 2019). L2.**
   - The rule is sound but has no power yet. Vessel form is recorded for about 20 of 650 inscribed vessels.
   - It needs a sherd register that records vessel forms.
6. **Laursen's "twins" prefix on Gulf seals. L1.**
   - Only 3 of our 46 foreign texts carry W032. Check the mapping first. If fewer than 8 texts carry the sign, it is untestable.
7. **Mukhopadhyay's class exclusivity. L0/L1.**
   - Claim: the two crop signs never share a line, and no line holds two PPF signs.
   - Test: a shuffle that preserves length and position.
   - Expected chance co-occurrence is only a few lines. Plant exclusive pairs first to measure power.
8. **Fig + fish as a fixed pair (Parpola's vaṭa-mīn). L1.** Identify the fig sign first.
9. **Bead-string sign (Mukhopadhyay 2025). L2.** It travels with rule 1, but the sign is likely too rare.
10. **Jar signs with infixed strokes as volume units. L2.** Run only if they appear in 30 or more texts.

Rules 1 and 2 are the only ones that could reach L2 with existing data. Rules 3 and 4 are cheap and decisive but sit at L1.

## Disclosures

- **Non-blind exposure.** While building `counts.py` I saw fish counts in the Chanhu-daro craft units: BEAD 10 of 28 objects carry fish, NONE 5 of 14. Chanhu-daro is therefore discovery data. Rule 1 must be confirmed at other units or sites.
- **Access gaps.** Every harappa.com PDF returned 403, including Mahadevan, Kenoyer & Meadow 2010 and Vidale. We did not work around the block.
  - We could not read the full texts of Wells 2015, Laursen 2010, Possehl 1996, Fairservis 1992 or Mukhopadhyay 2025. Rows that rely on secondary sources say so.
  - "Fish swam in the Great Bath" is marked UNVERIFIED.
- **Sign mapping.** Several rows need a sign number fixed from the original figures before any count: sign 193, the squirrel, the fig, the bead string, the twins and the stroked jars.
- **Brief.** `thread_rules.md` was not found in the repo. We followed `docs/AGENT_BRIEF.md` and the rules in the task.
