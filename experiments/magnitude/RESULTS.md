# R4: do numerals on an object track a measurable property of that object?

Pre-registered in `docs/prereg/magnitude.md` before any report was downloaded or any text linked to a measurement. The prereg, `run.py` and `extract.csv` are hash-frozen in `docs/prereg/HASHES.txt` (tags `magnitude`, `magnitude_A1`). Run: `.venv/bin/python experiments/magnitude/run.py` (log `run.log`). Data: `magnitude.csv` (26 objects, provenance per row), `extract.csv` (hand extraction), `results.json`. Ledger rows `mg_*`. Report scans are in `raw/<source>/` (archive.org OCR, untrusted, read with `python -I`).

## Findings first

1. **No test could be run at the registered size. The question stays open; it is not closed.** The published reports do not record the measurements this test needs, object by object.
   - (a) Copper/bronze tools: only **3** inscribed tools have a published mass, all from one Mohenjo-daro hoard (Mackay 1938 p.454). Mackay himself says the weights cannot be trusted, because the tools were separated in a chemical bath that "reduced their weight considerably". The prereg needs n ≥ 8, so: untestable.
   - (b) Pottery: **0** inscribed vessels have a capacity. Inscribed pottery in Marshall, Mackay and Vats is almost all sherds.
   - (c) Stoneware bangles: **0** inscribed bangles have their own diameter. Mackay 1938 (p.536) gives only the range for the whole class: inside 2.08-2.50 in (53-64 mm). So the oval M373/M374 lead cannot be tested either.
   - (d) Ivory/bone rods: **13** have a length (10 Mohenjo-daro, 3 Harappa). Spearman(numeral value, length) = **−0.50**, permutation p = 0.26, power **0.15** for a true rho of 0.5. Verdict: inconclusive (underpowered), and the sign points the wrong way for a measure.
2. **Linking worked, and it is exact.** Each Mohenjo-daro and Chanhu-daro tool ties to its ICIT/M77 text in two independent ways: Mackay's own description of the signs, and dimensions that match ICIT to the millimetre. For example, CXXVII 1 is described as "four and seven digits", restored length 11.4 in = 289.6 mm. That is M-2124, M77 2926, M104 M110, ICIT length 289.6. ICIT's implement and rod dimensions turn out to be copied from these reports.
3. **Mackay already proposed this test in 1938.** He read the inverted-U arc (M312-M315) as "10":
   - blade-axe CXXVI 5 = "76" (M108 + M315 = 6 + 7 arcs), 1,910 g;
   - chisel tang CXXVI 2 = "19" (M104 M106 + M312), 165 g, broken.
   - In 1943 he read the Chanhu-daro axe C-40 as "35 or 36". He concluded the numbers more likely count implements than give weight.
   - The three weighed tools are not monotone under either reading. Primary V (strokes only): 7, 6, 10 for 1910, 262, 165 g. Mackay's reading: 77, 6, 20. With n = 3 this means nothing.
4. **Exploratory lead (post hoc, one pair): the same text gives the same length.** Rods CX 51 (M-2106, bone) and CX 52 (M-1651, ivory) carry the same five-sign text (W240 W838 W585 W740 W400), and Mackay says they were found apart. Their lengths are 77.5 and 78.0 mm. Two random rods in this table differ by ≤0.5 mm with probability 3/78 = 0.04. Same-text rods could be standard gaming or tally pieces, but this rests on one pair, so it is not evidence yet.

## Tests (prereg decision: pass at p ≤ 0.0125 AND replicate at a second site)

| id | class | n | result | verdict |
|---|---|---|---|---|
| T1 | implements, V vs mass | 3 | 1910/262/165 g vs V 7/6/10 | untestable (n<8; masses corrupted) |
| T1b | implements, V vs length (secondary) | 9 (4 complete; 4 sites; types mostly singletons) | pooled rho −0.33, p 0.38 (descriptive) | untestable |
| T2 | pottery, V vs capacity | 0 | none | untestable |
| T3 | bangles, V vs inner diameter | 0 | none | untestable |
| T3o | oval M373/M374 bangles vs diameter | 0 | none | untestable (lead stays open) |
| T4 | ivory/bone rods, V vs length | 13 | rho −0.50, p 0.26; MD-only −0.23, p 0.54; power 0.15 | inconclusive |

Amendment A1: the first run grouped rods by a free-text material label instead of by class as registered (rho −0.18, p 0.66). This was fixed to class and logged in the prereg. Neither version is significant.

## Caveats
- V counts stroke numerals only, as frozen. Arcs (Mackay's tens) are reported in `V_mackay_tens` and were not tested.
- Link grades:
  - A: report description plus dimensions both match the text record.
  - B: one route only, e.g. M-2122 = CXXVI 3 rests on the "arrow" sign plus elimination; ICIT-only dimensions also count as B.
  - C: no measurement found (Harappa H-380, H-381, H-1518, H-1520). C rows were excluded.
- Rod lengths come from ICIT, which copied them from the reports, but whether each rod is complete was not checked object by object.

## What a person must look up (to make R4 decidable)
1. Harappa inscribed implements (H-380, H-381 daggers; H-1518..1520; M77 4901, 4902, 5601): length and mass. Sources: Vats 1940 vol. 2 pl. CXXIII 16, 25; Kenoyer & Meadow 2010; museum registers.
2. Present-day masses of M-2118, M-2121..M-2124 (Karachi National Museum) and of Chanhu-daro C-40 and C-94 (MFA Boston).
3. Kalibangan K-121/K-122: type, completeness and mass (ASI Kalibangan memoirs).
4. Inner diameter of each inscribed stoneware bangle, especially the W790 oval ones (M-1630, M-1631, M-1644, M-1645, H-1010, H-2578). Sources: the table in Kenoyer's "Painted Indus script on ceramics and steatite" (harappa.com blocks automated access); Blackman & Vidale 1992; the HARP bangle database.
5. Whole inscribed vessels with height × rim diameter or capacity, and pre- vs post-firing status. Sources: the Kenoyer & Meadow Harappa sherd database (1,218 marked sherds); Vats pl. CII-CIV entries for whole jars.
6. Completeness and length for all ~37 inscribed rods, plus the other same-text pairs (M-2107/2108, M-2089/2090, M-2086/2102, M-2109/2111). This tests the same-text → same-length lead as a fresh prediction.

Power needed: about 40 objects in one class for power 0.8 at rho 0.5 and alpha 0.0125 (Fisher-z approximation; more if many objects carry no numeral), plus at least 5-8 at a second site.
