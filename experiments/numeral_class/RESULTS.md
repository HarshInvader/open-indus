# What kind of quantity do the short-stroke numerals count? (Fable 5.2 plan 2, item E3)

2026-11-15. Pre-registration: `docs/prereg/numeral_class.md`, hash-frozen in `docs/prereg/HASHES.txt` before any reference distribution was built. `refs.py`, `data/refs.json` and `fit.py` were hashed before `fit.py` first ran. Unit: short-numeral tokens in distinct texts (distinct sequence within site and object type). Ledger rows `nc_*` in `docs/test_ledger.csv`.

## Findings first

1. **No reference class wins, so this line is closed (pre-registered verdict: NO WIN).** The pooled M77 leader is "numerals inside personal names" (Sanskrit), but only by log10 BF 0.56 (factor 3.6) over regnal years. The leader changes with the slice:
   - Mohenjo-daro: generic decaying counts
   - Harappa: names
   - Lothal: commodity counts
   - Kalibangan: generic counts
   - ICIT pooled: regnal years
   - ICIT tablets: Rigveda numbers

   None of the four conditions of the decision rule holds.
2. **No class even fits.** For every class, the best-fitting variant fails the posterior predictive check (9/9, p < 1e-4; 0 of 10,000 simulations as extreme). The closest is a generic geometric decay with 12 read as "12 or more" (G = 120).
3. **"Know nothing" beats every class.** A flat prior over the values ("any distribution") scores 11.7 log10 units better than the best reference class (exploratory). The names and regnal-year samples lead only because they are small (61 and 57 values), which makes their predictions vague, not because they match. In plain terms, no real quantity we could measure looks like the Indus numerals.
4. **The two peaks are what no quantity produces.**
   - **12:** it is 17.5 times as common as 9 and 10. In all 14 real reference samples this ratio is 0.0 to 1.1. Commodity counts, dates, ages, names and ritual numbers all thin out above 10. Reading 12 as "12 or more" does not rescue any class either. So 12 behaves like the top of the notation (as pair_numeral_long found) or a special word, not like a quantity.
   - **7:** the spike at 7 (log spike +1.45 over 6 and 8) appears in no commodity-count source (all negative, -0.10 to -0.67). Only Rigveda numbers spike harder (+3.05; regnal years +0.88, Latin names +0.6). Rigveda numbers have almost no 12, though (0.5%).
   - Most of the Indus 7 spike comes from the fixed formulas short7 + M194/M197. Remove those formulas and it halves (+0.78), and generic counts then lead by log10 BF 5. They still fail the predictive check (p < 1e-4), because of 12 and the gap at 8-10.
5. **What is left once 7 and 12 are taken out looks like an ordinary decaying count.** With 7 and 12 removed, generic geometric decay leads by log10 BF 5.3, but it still fails the fit check (G = 46, p < 1e-4), mostly because 8-10 are rarer than any smooth decay predicts. Values 8-11 are not written as two signs either: only 32 pairs of adjacent short numerals exist.
6. **Lead (exploratory, tiny n):** 8 of those 32 adjacent pairs are 1 + 12 (= 13?), and 3 are 12 + 12. Numbers above 12 may be written as 12 + n. That fits a 12-based ceiling, and possibly a 13-month year, but n = 8.

So the stroke values are not a sample of any one kind of quantity. They look like a mix of three things: (a) a few fixed number words (7 and 3 in formulas, as pair_numeral_long found), (b) a small decaying tail of real small counts, and (c) a ceiling sign 12. This agrees with the earlier findings that numerals form fixed formulas and that 12 is the largest single short-stroke sign. It adds one new fact: no external quantity class reproduces the mix.

## Pre-registered decision

| condition | result | pass |
|---|---|---|
| 1. Pooled M77: top class BF > 10 over every other | names (E) vs regnal (D), log10 BF 0.56 | no |
| 2. Per site (>= 40 tokens: same top, BF > 10; 15-39: not beaten by BF > 10) | MD top = generic (H, log10 BF 4.3 over D); Harappa top = names (1.84); Lothal (n = 37) commodity beats names by 7.7 log10; Kalibangan (n = 25) generic beats names by 1.7 | no (3 of 4 sites fail) |
| 3. Per object type | seals: names 0.19 over regnal; tablets (n = 46): names 0.24 over legion numbers | no |
| 4. ICIT pooled: same top, BF > 10 | top = regnal years (D), log10 BF 2.25 over names | no |
| Adequacy (PPC on the pooled winner) | names: G = 638, p < 1e-4; every class fails | no |

**Verdict: NO WIN.** Line closed for these classes.

## Data

- **Indus (M77):** short-stroke signs from `stroke_signs.json`. Value 2 (M99/M100/M101) is excluded, because M99 is the connective. Pooled counts: 1:157, 3:139, 4:65, 5:39, 6:35, 7:69, 8:7, 9:4, 10:1, 12:52 (n = 568).
- **ICIT replication:** W001-W019, W055 (n = 746).
- **Reference samples** (`data/refs.json`; full value counts per sample):

| class | sample | n values | source |
|---|---|---|---|
| A commodity counts | A1 Ur III admin texts <= 8 lines | 27,266 | CDLI ATF |
| | A2 Old Akkadian admin | 8,264 | CDLI |
| | A3 Proto-Elamite (N01/N14 groups) | 6,357 | CDLI |
| | A4 proto-cuneiform Uruk IV/III | 18,444 | CDLI |
| | A5 Linear B (integer after ideogram or measure) | 4,062 | DAMOS |
| | A6 tags, bullae, dockets, labels | 1,456 | CDLI |
| B month numbers | uniform 1-12 | model | |
| C day of month | `u4 N-kam` | 25,915 | CDLI |
| D regnal years | `mu N-kam`, Middle Babylonian and later | 57 | CDLI (most late tablets lack this ATF form; small) |
| E numerals in names | E1 Sanskrit person names, numeral first member | 61 | Monier-Williams |
| | E2 Chinese given names | 361 | naming_sim |
| | E3 Latin numeral names (Primus ... Decimus) | 11,203 | EDH |
| F ages | Latin epitaphs, `vixit annis N` | 7,451 | EDH |
| G ritual numbers | Rigveda cardinal forms 1-12 and compound first members | 942 | GRETIL (Aufrecht) |
| H generic counts | Benford; Zipf (a from 0 to 3); geometric (q from 0 to 1) | models | |
| I unit numbering (extra) | Roman legion numbers | 6,077 | EDH |

Not obtained: a Sangam numeral count (no lemmatised open corpus; Tamil number words are homographs of common words, so raw string counts are unusable). Age grades, ranks and generation numbers have no open data; they are represented only by the geometric "decaying ladder" model, as registered.

## Method

- Every reference is restricted to the Indus value set and renormalised.
- Real samples predict through a Dirichlet-multinomial with alpha = counts + 0.5, which carries their own sampling uncertainty.
- Models are integrated over a 2,001-point parameter grid.
- Open-ended classes are scored in two variants: EXACT, and CEILING (all values >= 12 pooled into 12).
- Class score = equal-weight average over its samples and variants.
- PPC: 10,000 Indus-sized draws from the best component's predictive, scored with the G statistic.

## Sensitivities (exploratory)

| slice | top class | log10 BF over runner-up |
|---|---|---|
| one numeral per text (n = 522) | names | 0.38 |
| distinct numeral + next-sign types (n = 207) | commodity (Linear B, ceiling) | 2.27 |
| fixed formulas removed (n = 483) | generic geometric | 5.13 (PPC still p < 1e-4) |
| ICIT seals (n = 512) | regnal | 2.35 |
| ICIT tablets (n = 119) | Rigveda | 1.51 |
| ICIT Harappa / MD / Dholavira | regnal / regnal / generic | 0.81 / 1.21 / 0.71 |

The leader flips between slices, every margin is below BF 10 except the formula-free slice, and that slice still fails the fit check.

## Caveats

- **Ceiling variant:** the CEILING variant assumes "12" can mean 12 or more. If 12 is a lexical number (for example a calendar or ritual 12), the right reference would be a source with a lexical 12. None of our real sources has one: the Rigveda's 12 is 0.5%. An Avestan, Babylonian astronomical or Jain/Vedic calendrical-ritual sample with month counts is the one class not tried.
- **Regnal-year sample:** it is small (57). A larger Neo-Babylonian sample would sharpen its prediction, and given the 12 problem would most likely make it worse.
- **Rigveda counts:** they use a frozen form list. "nava" (nine) is a homograph of "new", and sandhi forms of six are under-counted. That affects 6 and 9, not the 12 verdict.
- **Indus values:** they depend on Mahadevan stroke readings (shaunmortal). ICIT replicates the shape.

## Hypotheses

| hypothesis | verdict |
|---|---|
| Short strokes count commodities (labels, tags, admin) | refuted as a fit (PPC p < 1e-4; leads only at Lothal, n = 37) |
| Month numbers (uniform 1-12) | refuted (last place) |
| Day-of-month dates | refuted |
| Regnal / year numbers | inconclusive-to-refuted (tops ICIT only via a vague 57-value sample; fails PPC) |
| Numerals in personal names | refuted as a fit (leads pooled M77 only by BF 3.6, because the sample is small; PPC p < 1e-4) |
| Ages | refuted |
| Ritual / sacred numbers (Rigveda) | refuted as a whole; matches the 7 spike only |
| Generic decaying counts | refuted as a whole; best description of what is left once fixed formulas and 12 are removed |
| One class wins (pre-registered) | **refuted: NO WIN** |

## Next experiments

1. Treat 12 separately. Test whether 12 + n clusters (1 + 12, 12 + 12) behave as written numbers above 12, and whether the 12 sign is lexical (fixed partners such as jar M342 and fish M59) or a ceiling. A larger corpus (Fuls 2023) is needed for n.
2. If anyone pursues the calendrical-ritual 12, build a Vedic Brahmana or Babylonian sample that has a lexical 12 (months, Adityas) as one last reference class. Expect it to fail on the 1-6 decay.
3. Nothing else in this line: the values are formula-bound, so their distribution says what the notation and the formulas are, not what is counted.

Code: `refs.py` (python -I; parses untrusted downloads as text), `fit.py`, `explore.py`. Outputs: `data/refs.json`, `fit.json`, `fit.log`, `explore.json`, `explore.log`, `results.json`. Raw: `raw/gretil/rv.txt`. CDLI, DAMOS and EDH dumps were reused from `experiments/short_labels/raw/` and `sources/` (not copied).
