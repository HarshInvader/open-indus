# Pre-registration: are seal texts identifiers or shared labels? (Fable plan 4, section 4, ideas 1-2)

Agent: identifiers. Written 2026-11-15 BEFORE any statistic on M77 held-out, ICIT or the Ur III reference
was computed. Known at registration: M77 **dev** results only (`s3.py dev`, `s4.py` on dev, below), the
size of each dataset, and the facts that Ur III legends exist in CDLI with provenience and seal ids.

## Dev facts that shaped the thresholds (M77 dev, complete texts, one record per object)
- Seal texts almost never repeat: new-text rate (1 - Good-Turing/Chao-Jost coverage) 0.86 MD (n=715),
  0.94-0.97 at Harappa, Lothal, Kalibangan, Chanhu-daro. Tablets repeat: 0.46-0.52 (moulded/incised,
  Harappa and MD), copper tablets 0.12, Lothal true sealings 0.36. Seal Chao1 = 530-6,000 per site
  (unstable: f2 <= 35).
- Seal text duplicates are NOT local: a Harappa/Lothal/Kalibangan/Chanhu-daro seal matches an MD seal text
  as often as an MD seal does (cross-site/within-site ratio R = 0.67-1.06; vs Harappa 0.6-3.0, tiny counts).
- S4 dev seals, null A: nearest-neighbour edit distance not repelled (z +0.6, p 0.23); shared signs per pair
  lower than null (z -2.5, p 0.007; normalised z -1.9, p 0.02). Moulded tablets: no repulsion (z +1.9/+2.5
  toward clustering on shared signs). Slot-recombination null B makes real groups look CLUSTERED (z -6.3),
  because recombined texts never reproduce the corpus's own near-copies: null B is biased and is secondary.

## Units and data (frozen in `experiments/identifiers/id_lib.py`)
- Sample = one inscribed object (M77 `text_no`; ICIT id prefix); species = its full text (all sides, line
  breaks dropped). Objects with a break `#` or flagged incomplete are dropped.
- Classes: seal; true sealing (M77 'sealing' only at Lothal/Kalibangan/Other; ICIT TAG*); moulded tablet
  (M77 'sealing' at MD/Harappa; ICIT TAB:B); incised tablet (M77 'miniature tablet'; ICIT TAB:I); copper
  tablet (TAB:C / M77 copper). Cells analysed only with n >= 20 objects.
- Core / frame: functional_reading lexicon top role; FRAME = opener, connective, closer, title element,
  post-closer clitic, bracketed-fish closer. core key = text with frame signs removed; frame key = frame
  skeleton with each core run replaced by a slot X. ICIT signs mapped to M via bridge_WM for roles only.
- ICIT-only data: (a) **HARP** Harappa objects (ICIT objects with a recorded HARP period, excavated 1986+,
  after M77); (b) sites absent from M77 (all except MD, Harappa, Lothal, Kalibangan, Chanhu-daro, Unknown).
- Reference: Ur III seal legends (CDLI dump in `experiments/short_labels/raw/cdli`, read-only), one record
  per impression with provenience and CDLI seal id; physical-seal analogue = one record per base seal id.

## Estimators
Good-Turing / Chao-Jost (2012) coverage C and new-text rate 1-C; Chao1 (bias-corrected); ACE (k=10);
iNEXT interpolation/extrapolation S(m) to 2n; bootstrap 95% CIs (Chao 2014 augmented multinomial, 200).

## S3 tests
- **P1 (primary, positive control + contrast).** Within a site, seal new-text rate exceeds each tablet /
  sealing class by >= 0.20, with non-overlapping 95% bootstrap CIs. Datasets: M77 held-out and ICIT (all).
  Pass = holds in >= 80% of eligible (site, control) pairs in each dataset.
- **P2 (identifier prediction: no saturation).** In every site with >= 30 complete seals (M77 held-out and
  ICIT): completeness S/Chao1 < 0.25 and S(2n)/S > 1.7. Label prediction: completeness > 0.5.
- **P3 (identifier prediction: duplicates are local).** Cross-site ratio R = (share of target-site seals
  whose text occurs at the reference site) / (reference coverage), targets Harappa, Lothal, Kalibangan,
  Chanhu-daro, Dholavira vs reference MD; Harappa vs MD reversed too. ICIT, seals.
  Identifier-with-local-duplicates predicts pooled R < 0.5; shared-label predicts R within [0.7, 1.4].
  Also reported for core and frame keys (frame expected ~1 under both). The Ur III reference gives the
  empirical R of a known personal-identifier system (impression, seal and name-line level); P3 verdict is
  stated relative to that reference as well.
- **V1 (calibration, dev -> held-out).** The v2 split is by text family, so held-out texts never occur in
  dev by construction: a cross-split match rate cannot be tested. Instead: predict the held-out's own
  new-text rate per (site, class) from random species subsets of the dev abundance list with the held-out
  object count (1000 draws, 95% PI). Calibrated = observed inside the PI in >= 80% of cells.
- **V2 (calibration, ICIT-only by date).** Predicted share of HARP Harappa objects whose text already
  occurs among pre-HARP Harappa objects = coverage of the pre-HARP set (95% PI from coverage bootstrap +
  binomial). Seals, moulded tablets, incised tablets; seal core and frame keys also. Calibrated = inside PI.
  Below PI for tablets = mould texts are local in time/space (a finding, not an estimator failure).
- **V3 (calibration, ICIT-only sites).** Same for seals from sites absent from M77 vs the five old sites.

## S4 tests (repulsion)
- Groups: M77 = site + locus; ICIT = site + period (+phase) (HARP 3B, 3B/C, 3C; Vats strata; MD Early /
  Intermediate / Late; Dholavira stages; others as recorded). Unit = distinct (group, text); groups with
  >= 3 distinct texts. Statistics, weighted by group size: mean nearest-neighbour normalised edit distance
  (NN-NED; primary) and mean pairwise shared-sign count normalised by the shorter length (SHN; primary 2).
- **Null A (primary):** group labels permuted among units within site (keeps group sizes and the site's
  text pool). 1000 permutations. Repulsion = observed NN-NED above / SHN below null.
- **Null B (secondary, reported only):** each text keeps its frame skeleton; core runs refilled from texts
  of the same site with the same slot count. Known bias toward 'clustering' (dev).
- **R1 (primary):** seals, ICIT (all groups) and M77 held-out. Holm over {NN-NED, SHN} within dataset.
  Supported = Holm p < 0.05 for either metric in ICIT AND same direction in M77 held-out; refuted
  (clustering) = one-sided clustering p < 0.05 on NN-NED in ICIT.
- **R2 (internal control):** moulded and incised tablets, same test: expected NOT repelled (p_repel > 0.05).
  If tablets repel as much as seals, the effect is a property of the grouping, not of seals.
- **Power:** planted repulsion (sequential redraw of each group from the site pool, rejecting a candidate
  within NED < 0.5 of a member with probability 0.5 or 1.0) and planted clustering (0.5), 30 reps, 200
  permutations, on M77 dev seals and ICIT seals. Verdict 'inconclusive, underpowered' if power < 0.8 at
  strength 1.0 and the result is null.

## Falsifiers / interpretation
- Identifier reading supported if P1, P2 pass and P3 R < 0.5 (or near the Ur III seal-level R), and R1 is
  supported. Shared-label reading supported if seals saturate (P2 completeness > 0.5) or R1 shows clustering.
- A mixed reading (unique combinations of a shared vocabulary) is expected if P2 passes but P3 gives R ~ 1:
  the repeating fraction of seal texts would then be shared short labels, the rest unique combinations.

## Multiple testing
Confirmatory family = P1, P2, P3, V1, V2, V3, R1, R2 (8). Ledger rows in `docs/test_ledger.csv`.

## Caveats known in advance
Co-finding at one locus/period is not contemporaneity (periods span centuries; M77 loci are large areas).
M77 MD/Harappa 'sealings' are moulded tablets; a moulded tablet repeats by design (mould copies), so
the tablet classes are a positive control for saturation, not a functional comparator. ICIT is mostly a
second transcription of M77 objects; only HARP and new-site items are independent.
