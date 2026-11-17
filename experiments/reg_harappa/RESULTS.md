# reg_harappa: do the Mohenjo-daro findspot results hold at Harappa?

Pre-registered in `docs/prereg/reg_harappa.md`. Its hash and the hashes of `prose.py`, `data.py`, `findspots.csv` and `test.py` went into `docs/prereg/HASHES.txt` (tags `reg_harappa` and `reg_harappa_data`) before any sign was set against a findspot. The 24 confirmatory ledger rows are `rh_f1_*` and `rh_f3_*` in `docs/test_ledger.csv`.

Run from the repo root:
- `.venv/bin/python -I experiments/reg_harappa/prose.py` writes `prose_refs.csv`
- `.venv/bin/python -I experiments/reg_harappa/data.py` writes `findspots.csv`, `prose_refs_checked.csv` and `data_summary.json`
- `.venv/bin/python experiments/reg_harappa/test.py --explore` writes `results.json`; its output is in `test.log`

## Findings first

1. **The Mohenjo-daro "no household or office signature" result replicates at Harappa (F1: 0 of 8 tests significant, all Holm p = 1).**
   - **Big square** (about the scale of a Mohenjo-daro house): 283 text families in 46 squares, giving 883 same-square and 5,983 other pairs.
     - Opener: shared in 1.7% of same-square pairs against 1.4% of other pairs (p = 0.56).
     - Closer: 9.5% against 11.4% (p = 0.24).
   - **Sub-square** (about room scale): 239 families, 138 same-unit pairs. Every p is 0.20 or higher.
   - **Power.** A unit signature carried by half the families would have been caught for opener, closer and core at both levels (power 0.90-1.0). A signature carried by a quarter of the families is excluded only for openers at big-square level (power 1.0).
   - The "whole text" test is blind here (power 0-0.18). The same was true at Mohenjo-daro.
   - There is no sign of the opposite pattern either, where texts in one unit would avoid each other's signs. The lowest lower-tail p is 0.12.
2. **No sign class clusters by findspot at Harappa (F3: 0 of 16 tests, all BH q ≥ 0.64).** Most of these nulls carry little weight, because power is low.
   - **Ticked fish: untestable, as expected.** Only 3 of 287 families carry one (6 of all 552 linked objects), and power is 0-0.28. So Harappa can neither confirm nor refute the Mohenjo-daro ticked-fish lead.
   - **Real nulls, where a planted 3x enrichment of one big square would have been caught every time (power 1.0):**
     - Numerals: p = 0.064, top square M12 with 14 of 17 families
     - Jar M342: p = 0.54
     - M99 has power 0.69 and p = 0.12, so it is a weaker null.
   - **Inconclusive (power below 0.5 for both planted patterns):** M267, M293, M391 and the M162 count frame at big-square level, and every class at sub-square level.
     - The +4-bearer plant, sized like Mohenjo-daro block 12, was caught at most 28% of the time at Harappa.
     - Sub-square units with at least 3 families hold only 110 families.
3. **What we can say about findspots at Harappa (step 1).**
   - The Vats tabulation gives only the mound or area (F, AB, D, G, H, J), the find number and the depth below the local surface. It has **no trench, square or locus column**.
   - Squares come from Vats's narrative chapters. There he lists finds in the form "Pl. XCVI, 429 … No. 10359; Square I 8/10; Depth 15 ft. 6 in. b.s." The grid is a big square (I8) divided into 25 numbered sub-squares.
   - **Coverage.** 552 Vats objects link to M77 (text_no = 4000 + EH serial): 260 seals, 170 miniature tablets, 121 sealings and 1 rod. Of these, 123 link to ICIT.
     - 295 have a verified square: Mound F 225, AB 43, D 19, J 5, H 3.
     - These fall in 47 big squares and 184 sub-squares, and collapse to 287 text families.
     - Sources of the squares: 279 come from formal find lists (269 with a find number matching the register, 23 of them after a one-character OCR fix; 10 matching on depth). 16 come from running narrative (9 with a matching find number; 7 on the same mound with a square named just before).
     - 125 narrative citations were rejected because their find number contradicted the register.
   - **Depth checks.** The register depth agrees with the M77 level within 1 ft for 485 of 522 objects, and with the narrative list depth for 262 of 284.
   - The Vats register has no house or room numbers. "Locus" at Harappa therefore means a grid square, not a building.

**What this means.** At a second city, with an independent excavator and a different recording system, objects found together still share no more signs than objects from elsewhere in the same mound and depth band. A strong household or office sign is excluded at Harappa as it was at Mohenjo-daro. That is now a two-site result. The ticked-fish block cluster cannot be checked at Harappa, because the sign hardly occurs there. Numerals and the jar are not concentrated in any square. For the rarer classes Harappa adds nothing.

## Tests (confirmatory)

| Test | Observed (same vs other) | p | Corrected | Power q=0.5 / 0.25 | Verdict |
|---|---|---|---|---|---|
| F1 big square, opener | 0.017 vs 0.014 | 0.56 | Holm 1 | 1.0 / 1.0 | no sharing; q=0.25 excluded |
| F1 big square, closer | 0.095 vs 0.114 | 0.24 | 1 | 1.0 / 0.39 | no sharing; q=0.5 excluded |
| F1 big square, core | 0.041 vs 0.048 | 0.24 | 1 | 1.0 / 0.28 | no sharing; q=0.5 excluded |
| F1 big square, whole | 0.076 vs 0.072 | 0.84 | 1 | 0.18 / 0 | inconclusive |
| F1 sub-square, opener | 0.014 vs 0.016 | 1.0 | 1 | 1.0 / 0.44 | no sharing; q=0.5 excluded |
| F1 sub-square, closer | 0.101 vs 0.102 | 0.52 | 1 | 0.93 / 0.19 | no sharing; q=0.5 excluded |
| F1 sub-square, core | 0.054 vs 0.039 | 0.20 | 1 | 0.90 / 0.20 | no sharing; q=0.5 excluded |
| F1 sub-square, whole | 0.076 vs 0.076 | 0.60 | 1 | 0 / 0 | inconclusive |

| Class | Families with the class | Big square p | Power (3x / +4) | Sub-square p | Power (3x / +4) | Verdict |
|---|---|---|---|---|---|---|
| Ticked fish | 3 / 287 | 0.76 | 0 / 0.01 | 1.0 | 0 / 0.28 | untestable |
| M267 | 30 | 0.48 | 0 / 0 | 0.60 | 0 / 0.16 | inconclusive |
| M293 | 6 | 0.91 | 0 / 0.06 | 1.0 | 0 / 0.17 | inconclusive |
| M391 | 15 | 0.089 | 0 / 0.01 | 1.0 | 0 / 0 | inconclusive |
| Numerals | 185 | 0.064 | **1.0** / 0 | 0.70 | 0 / 0 | big square: null, 3x excluded |
| M342 (jar) | 134 | 0.54 | **1.0** / 0 | 0.77 | 0 / 0 | big square: null, 3x excluded |
| M99 | 49 | 0.12 | 0.69 / 0 | 0.65 | 0 / 0 | big square: null (moderate power) |
| M162 count frame | 19 | 0.47 | 0 / 0 | 1.0 | 0 / 0.15 | inconclusive |

Method notes:
- Power is the share of 200 plants reaching p ≤ 0.05/16. A 3x plant cannot be built when the class is already common, and it is too small to detect when the class is rare.
- The null and the statistic are imported unchanged from `reg_findspot/test.py`.
- Strata are mound × 5-ft band for the big-square level, and big square × 5-ft band for the sub-square level.

## Exploratory (not corrected, labelled)

- **Seals only** (140 families at big-square level). F1 p ranges from 0.14 to 1.0. In F3, numerals give p = 0.022 and M293 gives p = 0.025 (2 bearers) at big-square level. These are 2 of 16 uncorrected tests, about what chance predicts, so treat them as noise.
- **3-ft depth bands, F1 big square:** all p ≥ 0.09.
- **Mound level, all 552 objects** (families within mound). No class differs between mounds; p ranges from 0.15 to 0.85. All 5 ticked-fish objects come from Mound F (347 objects there), p = 0.48.

## Caveats and counterevidence

- **The sample is not random.** Squares exist only for objects Vats described in his narrative (53% of linked objects). These are mostly from Mound F (the granary and working-floor areas: M11, N9, I13, I9).
- **Units mix object types.** Harappa units combine seals, tablets and sealings. Mohenjo-daro F1 used seals only. A seals-only rerun gives the same null.
- **Depth control is weaker than at Mohenjo-daro.** Vats depths are below the local surface, so the 5-ft bands within a mound control time less well than Mackay's depths below datum.
- **Families may be imperfect.** Families collapse identical full texts within a big square (295 objects become 287 families). Near-identical moulded tablets that differ by one sign remain separate. This would favour F1 sharing, yet none was found.
- **The squares rest on OCR parsing.** All squares come from parsing the djvu OCR, corroborated by find number or depth. Mis-assignment would dilute any signal. It cannot create one, and F1 power was computed on the same units.

## Hypotheses tested

| Hypothesis | Verdict |
|---|---|
| Objects in one Harappa square/sub-square share opener/closer/core (locus signature) | refuted (q=0.5 excluded; opener q=0.25 excluded at big square) |
| Locus texts deliberately distinct | refuted (no lower-tail result) |
| MD F1 null replicates out of sample | **supported (replicated)** |
| Ticked fish cluster by locus at Harappa | untestable (3 families) |
| Numerals / jar M342 concentrated by big square | refuted at 3x strength |
| M99 concentrated by big square | null, moderate power (0.69) |
| M267 / M293 / M391 / M162 concentrated | inconclusive (power < 0.5) |

## Next experiments

- Find a site with many ticked fish and fine findspots. Chanhu-daro (3 of 44) and Lothal are candidates, but small. Marshall's HR/VS register for Mohenjo-daro is in progress in `fish_marshall`.
- Parse the remaining 257 linked Harappa objects with no square from Vats's plate descriptions in vol. II, if those give find numbers that can be tied to the narrative find lists.
- Add the non-seal finds that Vats lists in the same squares (pottery, weights). That would allow an assemblage test of class × context.
