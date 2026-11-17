# Pre-registration: proto-cuneiform / Proto-Elamite look-alikes (experiments/protocuneiform)

Written 2026-11-15, after the blind shape step and BEFORE any Indus distributional statistic was computed in this area. Frozen and hashed in HASHES.txt: `pc_classes.py`, `pc_corpus.py`, `pe_extract.py`, `s1_freeze.py`, `pc_pool.json`, `pe_pool.json`, `frozen_pairs.json`, `s2_test.py`, this file.

## Question
Proto-cuneiform (PC, Uruk IV-III, c. 3350-3000 BCE) and Proto-Elamite (PE, c. 3100-2900 BCE) are administrative scripts whose sign functions are partly known. If an Indus sign that looks like a PC/PE sign also behaves like it (a commodity look-alike counted after numerals; an office look-alike in the title/end slot; a PE header-sign look-alike at text start), graphic resemblance would carry meaning. If look-alikes behave like random pairings, it does not.

Honest priors: PC is ~700 years older than the Mature Harappan script (c. 2600-1900 BCE), PE ~500 years; no direct contact in script use is documented. Simple shapes (strokes, diamonds, lines, ovals) match by chance. The expected result is null.

## Inputs (non-Indus, done)
- PC sign images: Englund's CDLI sign list (github cdli-gh/proto-cuneiform_signs, CC BY), first exemplar of stacked drawings.
- PE sign images: glyphs rendered from Pandey 2023, Unicode L2/23-196 (CDLI/Dahl names).
- PC/PE corpora: CDLI bulk ATF + catalogue, genre "administrative"; PC = Uruk IV/III (4,965 texts, 28,967 lines); PE = Proto-Elamite period (1,443 texts, 10,297 lines).
- Pools: non-compound, non-numeral signs with >= 20 line occurrences and an image: PC 274, PE 120.
- PC function class (`pc_classes.py`) assigned from standard archaic readings only, before matching: GRAIN_FOOD, LIQUID_DAIRY, VESSEL, TEXTILE, LIVESTOCK, OTHER_GOODS (= commodity), OFFICE_PERSON, PLACE_INST, UNKNOWN (147 of 274 left unknown rather than guessed).
- PC/PE signatures from ATF: counted_rate = share of the sign's lines that carry a numeral; header_rate = share of its occurrences in the text's first line without a numeral. Calibration note (seen before any Indus data): PC counted_rate separates classes only weakly (livestock 0.82, place 0.66, median 0.73), because PC cases almost all carry numbers.
- PE meanings are mostly unknown, so PE enters only through data-driven signatures.

## Shape step (blind, done)
- Indus pool: 196 signs with >= 5 distinct M77 texts (frequency only). Mahadevan drawings.
- Distance: symmetric chamfer on thinned, bbox-normalised drawings, minimised over the 8 rotations/reflections of the PC/PE sign (PC signs were rotated 90 degrees in Uruk III; Indus is mostly read right-to-left).
- **Disclosure / change before testing:** v1 used raw chamfer; the v1 contact sheet (`contact_sheet_v1_raw_chamfer.png`) showed hubs (PE M352~n top match for 27 Indus signs; PC ZAG~a/HI for 10-11). v2 (primary) ranks by CSLS hubness correction: 2d(i,j) - r_S(i) - r_I(j), r = mean distance to 10 nearest on the other side. Raw chamfer kept as exploratory. No Indus distribution had been computed.
- Matcher positive control: among 64 PC sign variants that share a base sign, the nearest other PC image is a variant of the same base in 30 cases vs 0.31 expected by chance. The matcher sees shape; whether Indus-PC matches are meaningful is a different matter (median Indus->PC nearest distance 3.35 px vs Indus->Indus nearest 2.47 px: Indus signs resemble each other more than they resemble any PC sign).
- Look-alike sets (primary): the best third of Indus signs by top-1 CSLS score: 66 for PC, 66 for PE. Partner = top-1 CSLS match.

## Indus signatures (computed in s2_test.py, once)
Distinct texts. Numerals = signs with a NUMERAL role in `experiments/functional_reading/lexicon.csv` (26 signs); numerals are excluded as targets. Per sign, with >= 3 occurrences in the set:
- AN: share of occurrences directly preceded (same run) by a numeral (counted-item slot);
- INIT: share that are the first sign of the text;
- END2: share in the last two positions (title / closer region).

## Confirmatory hypotheses (look-alike sets, one-sided)
- H1: Indus look-alikes of PC commodity signs have higher mean AN than look-alikes of other PC signs.
- H2: look-alikes of PC OFFICE_PERSON signs have higher mean END2 than the others.
- H3: Spearman(PC counted_rate of partner, Indus AN) > 0.
- H4: Spearman(PE counted_rate of partner, Indus AN) > 0.
- H5: Spearman(PE header_rate of partner, Indus INIT) > 0.

Primary null: PC/PE labels or signature values permuted across the whole PC/PE pool, keeping the Indus->partner map (preserves hub structure), 10,000 permutations. Secondary null: random pairing (uniform random partner per Indus sign).

## Decision rule
Sets: M77 dev (v2), M77 held-out v2, ICIT (W->M by the bridge, first M; mostly the same objects, so a transcription check rather than new data).
A hypothesis is **supported** only if: dev Holm-adjusted p < 0.05 (over the 5) AND held-out p < 0.05 AND ICIT p < 0.05, same direction. 0 supported -> "graphic look-alikes carry no detectable shared function at this power". Power is reported from a planted simulation on dev (H1 with a fraction f of commodity look-alikes given top-quartile AN; Spearman tests with planted rho 0.3/0.5).

## Exploratory (labelled as such)
Full pool (all 196 minus numerals), raw-chamfer pairings, per-class means.

## Contamination
I have read earlier project results: M162/M169/M328 as counted-item candidates (later failed red team), the title block M336-M89-M211, the jar closer M342, openers M267/M391/M293. The pairing is algorithmic and was not adjusted for them; the only post-hoc change (CSLS) was made on shape grounds from the contact sheet.

## Falsification
If look-alikes do not differ from permuted pairings on all five, the "graphic borrowing with function" idea is unsupported for this PC/PE sign list and these slot signatures. It would not exclude borrowing of single signs, borrowing via intermediate scripts, or functions not captured by these slot measures.
