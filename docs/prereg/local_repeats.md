# Pre-registration: local_repeats (what are the repeated 4+ sign seal texts?)

Agent: local_repeats. Written 2026-11-15 BEFORE any tabulation of the repeated texts' metadata. Known at
registration: redteam_identifiers RESULTS (34 objects on repeated 4-5 sign seal texts vs 8 expected under a
bigram null, p=0.002; locality R_LOO 0.18 for >=4 signs); its `repeated_dump.txt` (I saw its first ~60 lines:
mostly 2-3 sign texts, plus one 4-sign text W820 W002 W003 W390 on 4 seals at 3 sites; no statistic computed);
field coverage over ALL ICIT seals (2,238 seal records: dims known 1,775, period known 933, CISI known 2,007;
merged corpus `sources/paragorth_Indus-/.../merged-corpus-reading-order.json` gives area-section 1,858 /
room-grid 1,268 seals by CISI). Ur III: CDLI seal ids `Sxxxxxx.n` (base = composite legend, suffix = a distinct
physical seal). Code in `experiments/local_repeats/`; other experiment folders are read-only imports.

## Unit and set
- Objects = identifiers' unit: `id_lib.icit_objects()`, `complete`, `cls == "seal"`, text = `flat(sp)` (W signs).
- Repeated set R = distinct texts of length >= 4 on >= 2 such seal objects. Reported in two bands, 4-5 and 6+.
- Same-site pairs = all object pairs within a text family found at the same site. Cross-site pairs are listed,
  labelled X, and excluded from (a)-(d) scoring (all four explanations need one site).

## Per-object table (descriptive, all of R)
ICIT id, CISI, site, type, symbol (ICIT field), width/height mm, material, period/phase (ICIT); merged corpus by
CISI: time, shape, cult object, area-section, block-house, room-grid; M77: all M77 objects at the same site whose
complete text, mapped W->M by the bridge, equals the family text (text_no, level, locus, field symbol; the link is
to the text, not one-to-one). Other carriers: every complete ICIT object of another class (sealing/TAG, tablets,
pottery...) with the same text. Longer variants: every complete ICIT text (any class, any site) of length L+1 that
becomes the family text when one sign is deleted (record site, class, inserted sign, position).

## Pair categories (decision order; fields compared as below)
- dims: `same` if both w,h > 0 and |dw|,|dh| <= 0.5 mm (w/h swap allowed); `different` if both known and
  max relative difference > 10%; `near` otherwise; `unknown` if either missing.
- symbol: same full string / different (subtype or base) / unknown ('-' or empty). 'None' is a value.
- period: both known (ICIT period not '-') -> same if (period, phase) equal, else different.
- findspot: area-section from merged corpus; same / different / unknown.
1. different site -> **X**.
2. same site, symbol same, dims `same`, type same, period and findspot not known-different -> **A/D candidate**;
   visual check of CISI photo crops (`experiments/carver_hands/work/boxes.csv` pages): **A** if one object
   (same photo, or indistinguishable incl. damage), **D** if visibly distinct objects, **A/D-unchecked** if no photos.
3. same site, period known and different -> **C** (diachronic).
4. same site, dims `different` or symbol different -> **B** (synchronic replacement / re-cut).
5. same site, symbol same, dims `near` -> **D** (template copy, near size).
6. otherwise (key fields unknown) -> **U** (undetermined).
The visual check is not blind (I know the texts); stated as a caveat.

## Tests (family of 5, Holm; 10,000 permutations; null = permute text-family labels among same-site seals with
## text length >= 4 and the needed field known, keeping family sizes per site)
- T1 size: median relative size difference of same-site same-text pairs (dims known). Size-matched if p_low < 0.05.
- T2 emblem: share of same-site same-text pairs with identical symbol. Emblem-matched if p_high < 0.05.
- T3 period: share of dated same-site same-text pairs with different (period, phase). Synchronic if p_low < 0.05;
  diachronic-compatible if not and >= 8 dated pairs; untestable if < 8.
- T4 findspot: share of same-site same-text pairs in the same area-section. Co-located if p_high < 0.05.
- T5 extension: share of R families with a one-sign-longer complete text at the same site vs share among singleton
  seal texts of the same length (4-5 / 6+) at the same sites; Fisher one-sided (greater). Secondary control: the same
  for one-sign-shorter texts (commonness bias would raise both; (c) predicts only longer).
Tests needing >= 8 pairs with the field; otherwise reported untestable.

## Scoring rules per explanation (verdict: supported / partly / not supported / untestable)
- (a) duplication: share of same-site pairs in A. supported >= 25%; partly 5-25%; not supported < 5%.
- (b) re-cut/replacement: supported if T1 NOT size-matched AND T3 not diachronic-beyond-null (synchronic or untestable)
  AND B is the plurality category among same-site pairs; partly if two of the three.
- (c) office of successive holders: supported if T3 diachronic-compatible AND (T5 p < 0.05 OR C is the plurality
  category); partly if T3 diachronic-compatible only; not supported if T3 synchronic; untestable if T3 untestable.
- (d) workshop templates: supported if T1 size-matched AND T2 emblem-matched AND D share >= 25%; partly if two.
- Same-site pairs < 8 -> every verdict untestable.

## Ur III reference (read-only, `python -I` for files in experiments/short_labels/raw/)
Legend = exact written-sign sequence (cun_signs as in redteam c1). Repeated = legend on >= 2 distinct physical seal ids
(full id incl. suffix). Report: share of pairs in the same archive; share of same-archive pairs in different reigns
(date_of_origin of the sealed tablet; earliest attestation per seal) vs random same-archive pairs of seals; share of
repeated legends with a one-word-longer legend in the same archive vs singleton legends; all and <= 7 written signs.
Reference only (it is a known personal-seal system, mostly type (b) with homonyms); no verdict rests on it.
