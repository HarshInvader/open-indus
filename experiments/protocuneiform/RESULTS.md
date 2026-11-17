# Proto-cuneiform and Proto-Elamite look-alikes: does shape carry function into the Indus script?

protocuneiform agent, 2026-11-15. Pre-registration: `docs/prereg/protocuneiform.md`. Nine inputs (classes, parsers, freeze code, pools, frozen pairs, test code, prereg) were hashed into `docs/prereg/HASHES.txt` before any Indus statistic was computed. Code, run from the repo root with `.venv/bin/python -I`: `pc_corpus.py`, `pe_extract.py`, `pc_classes.py`, `s1_freeze.py` (blind shape step), `s2_test.py` (the single confirmatory run, log `s2.log`), `s3_report.py`. Numbers: `test_results.json`, `results.json`, `shape_control.json`. Ledger rows: `pc_*` in `docs/test_ledger.csv`. Downloads (untrusted, read as data only) are in `raw/pc_cdli`, `raw/pc_vkethana`, `raw/cdli_atf` and `raw/pe_pandey`.

## Findings first

1. **No. Indus signs that look like proto-cuneiform (PC) or Proto-Elamite (PE) signs do not behave like them.** None of the 5 pre-registered tests passed. The rule needed dev Holm p < 0.05, plus p < 0.05 on held-out v2 and on ICIT.
   - **H1, commodity look-alikes after numerals.** Look-alikes of PC commodity signs (grain, beer/dairy, vessels, textiles, livestock, goods) should follow a numeral more often. They follow one *less* often: 0.114 vs 0.154 for other look-alikes (dev p = 0.73). Held-out gives 0.111 vs 0.109 (p = 0.45) and ICIT 0.115 vs 0.134 (p = 0.61).
   - **H2, office look-alikes in the title/closer slot.** Look-alikes of PC office signs (EN, SANGA, NIN, GAL, PA, SZITA, ...) should sit in the last two positions more often. On dev they do: 0.66 vs 0.41, p = 0.041. That fails Holm (0.21) and fails held-out (0.51 vs 0.47, p = 0.38).
     - ICIT gives p = 0.013, but ICIT is mostly a second transcription of the same objects, so it does not count as independent support.
     - The effect rests on 5 signs, three of which carry it: M2, M139 and M194. M139 and M194 are both matched to one PC sign, SZITA.
   - **H3-H5, signature correlations.** PC counted-rate vs Indus after-numeral rate: rho −0.10 (dev). PE counted-rate vs after-numeral rate: rho +0.13 / −0.22 / +0.11 on dev / held-out / ICIT. PE header-rate vs Indus text-initial rate: rho +0.15 / +0.12 / +0.19, all n.s. (p = 0.13 / 0.22 / 0.11).
2. **The look-alikes are poor.** A computer matcher pairs any sign with *something*, but the pairs mostly do not look alike (contact sheets below).
   - Indus signs resemble each other more than they resemble any PC sign. Median nearest chamfer distance is 2.47 px Indus-to-Indus, 3.35 px Indus-to-PC and 3.71 px Indus-to-PE.
   - The matcher itself works. Among 64 PC sign variants that share a base sign, the nearest other PC image is the same base in 30 cases, against 0.31 expected by chance.
   - So the null is partly "there is no close graphic borrowing to test". That is itself informative: unlike Linear Elamite or later cuneiform, the archaic Mesopotamian and Elamite repertoires share no obvious sign forms with the Indus script beyond universal simple shapes (strokes, diamonds, ovals, triangles).
3. **Power is moderate, so small effects are not excluded.**
   - H1 has power 0.94 if every commodity look-alike were a counted item. It drops to 0.40 if 60% were and 0.12 if 30% were.
   - The PE correlation tests have power 0.92 at a true rho of 0.5 and 0.43 at rho 0.3.
   - What is excluded is a strong, systematic carry-over of function through shape. Borrowing of a few individual signs is not.
4. **Exploratory, all failing held-out.** With the full pool of 174 non-numeral signs instead of the best-matching third:
   - office look-alikes in the end slot: dev p = 0.023, held-out p = 0.55;
   - PE header-rate vs Indus initial rate: dev p = 0.044, ICIT p = 0.039, held-out p = 0.55;
   - raw-chamfer pairings give the same picture as the hubness-corrected ones.
   - No class of PC look-alike stands out on after-numeral rate. Dev means: vessel 0.17 (8 signs), office 0.13, unknown 0.12, livestock 0.075, grain 0.0 (3), against a pool baseline of 0.11.

**Verdict:** graphic resemblance between Indus signs and the PC/PE sign lists carries no detectable function. The time gap is the obvious reason: proto-cuneiform is about 700 years older than the Mature Harappan script, and Proto-Elamite about 500. There is also no evidence of script contact at that depth. A third reason is that simple shapes match by chance. This route joins Linear Elamite (`experiments/elamite_bridge`) as closed for look-alike-based meanings.

## Contact sheets

`classed_pairs.png`: the 23 look-alike-set pairs whose PC partner has a known function class. Each shows the Indus drawing, the PC partner (Englund), the PE partner (Pandey 2023 glyph), and the dev slot rates (after-numeral, end, initial).

![classed pairs](classed_pairs.png)

`contact_sheet.png`: the 48 best Indus-PC matches by hubness-corrected score, with their PE match. It was drawn before any Indus statistic. `contact_sheet_v1_raw_chamfer.png` is the pre-fix version with hubs.

![contact sheet](contact_sheet.png)

## Method

- **PC data.**
  - Sign images: Englund's CDLI proto-cuneiform list (`cdli-gh/proto-cuneiform_signs`, CC BY, 2,089 images). When a JPG stacks several exemplars, only the first is used.
  - Corpus: CDLI bulk ATF plus catalogue. Genre "administrative", Uruk IV/III: 4,965 texts, 28,967 lines. Lexical lists are excluded, because each entry starts with 1(N01).
- **PE data.**
  - Sign images: glyphs rendered from Pandey's 2023 Unicode proposal (L2/23-196), whose names follow the CDLI/Dahl list. All 1,636 glyphs were rendered.
  - Corpus: CDLI ATF, Proto-Elamite administrative: 1,443 texts, 10,297 lines.
- **Pools.** Non-compound, non-numeral signs with at least 20 line occurrences and an image: PC 274, PE 120. The Indus pool is the 196 signs with at least 5 distinct M77 texts, chosen by frequency only.
- **PC function classes** (`pc_classes.py`) come from the standard archaic readings (Englund 1998; Green & Nissen 1987), assigned before matching:
  - commodity (GRAIN_FOOD 4, LIQUID_DAIRY 7, VESSEL 12, TEXTILE 5, LIVESTOCK 20, OTHER_GOODS 16);
  - OFFICE_PERSON 33; PLACE_INST 30;
  - UNKNOWN 147, left blank rather than guessed.
- **PE function.** PE meanings are mostly undeciphered, so PE enters only through data-driven signatures:
  - counted-rate: the share of a sign's lines that carry a numeral;
  - header-rate: the share of its occurrences in a first line without a numeral.
  - Calibration caveat: the PC counted-rate barely separates PC classes (0.66-0.82), because almost every PC case carries a number.
- **Shape step.**
  - Distance: symmetric chamfer on thinned, size-normalised drawings, minimised over 8 rotations and reflections of the PC/PE sign. Uruk III signs are rotated 90°, and Indus is read right-to-left.
  - Ranking uses CSLS hubness correction. This was decided after the v1 sheet showed hubs (one PE sign was top match for 27 Indus signs) and before any Indus statistic.
  - Look-alike sets: the best third of Indus signs by top-1 score, 66 each for PC and PE. Numerals are excluded as targets, which leaves 60 PC and 54 PE pairs on dev.
- **Indus signatures** are measured on distinct texts, counting signs with at least 3 occurrences:
  - AN: the share of occurrences directly after a numeral (numerals are the 26 NUMERAL-role signs of `functional_reading/lexicon.csv`);
  - INIT: the share that are text-initial;
  - END2: the share in the last two positions.
- **Nulls.**
  - Primary: PC/PE labels or signature values permuted across the whole PC/PE pool, keeping the Indus-to-partner map (this preserves the many-to-one hub structure). 10,000 permutations.
  - Secondary: random pairing. Both nulls agree everywhere (see `test_results.json`).

## Hypotheses

| id | hypothesis | dev | held-out v2 | ICIT | verdict |
|---|---|---|---|---|---|
| H1 | PC commodity look-alikes follow numerals more | 0.114 vs 0.154, p=0.73 | p=0.45 | p=0.61 | **refuted** (wrong direction) |
| H2 | PC office look-alikes sit in end slot | 0.66 vs 0.41, p=0.041 (Holm 0.21) | p=0.38 | p=0.013 (same objects) | **not supported** |
| H3 | PC counted-rate ~ Indus after-numeral | rho −0.10, p=0.76 | +0.19, p=0.12 | −0.04, p=0.58 | **refuted** |
| H4 | PE counted-rate ~ Indus after-numeral | +0.13, p=0.15 | −0.22, p=0.93 | +0.11, p=0.24 | **refuted** |
| H5 | PE header-rate ~ Indus initial | +0.15, p=0.13 | +0.12, p=0.22 | +0.19, p=0.11 | **not supported** (weak, consistent sign; power ~0.4 for rho 0.3) |

Tests: 15 confirmatory p-values (5 hypotheses × 3 sets; the decision family is the 5 dev tests), 34 exploratory, 5 power simulations, 1 matcher calibration.

## Caveats and counter-evidence

- **Time gap.** PC (3350-3000 BCE) and PE (3100-2900 BCE) are 500-700 years older than Mature Harappan writing. Any borrowing would have passed through Early Harappan or Iranian-plateau intermediaries that left no texts.
- **Chance shapes.** Many Indus signs are strokes, diamonds, ovals or triangles. Their "look-alikes" are geometric universals, which dilutes any real signal.
- **Hubs.** Two of the five office look-alikes (M139, M194) share one PC partner, SZITA. The label-permutation null accounts for this, but it means the effective n is smaller than the sign count.
- **Drawings, not photographs.** These are standardised drawings: Mahadevan's for Indus, Englund's for PC, a Unicode font for PE. Dahl warns against arguing from standardised forms, and that applies here too.
- **Class labels.** The PC class labels come from later Sumerian readings and leave 54% of the pool unknown. A wrong label weakens H1/H2 but cannot create a false positive under the permutation null.
- **Slot measures.** "Counted item = after a numeral" is the only commodity signature the Indus texts offer. Earlier work showed most Indus numeral+sign pairs are fixed number-name formulas, not counts (`pair_numeral_long`, `redteam_pnl`). So a real commodity sign might not show up as AN in seal texts at all. This is the main reason a null here is not decisive about borrowing.

## Next experiments

1. Close this route for look-alike meanings, as with Linear Elamite. Do not repeat it with other shape metrics: the matcher works, and the shapes simply do not match well.
2. If anything, test the one weakly consistent direction (H5: PE header-like signs vs Indus openers) on fresh data only, such as new ICIT/Fuls-catalogue sites. Freeze it now as a low-prior prediction rather than re-testing on M77.
3. A better PC/PE comparison would be structural rather than graphic: PE tablets have header + entries + total. Ask whether any Indus object type (tablets, copper plates) shows a header/entry/total layout with numerals. That needs no shape matching.
