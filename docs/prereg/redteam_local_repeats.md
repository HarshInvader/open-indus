# Pre-registration: red team of experiments/local_repeats (R1 travelling numeral formula, R2 "texts grow, never shrink" + "not local")

Agent: redteam_local_repeats. Written 2026-11-14 BEFORE running any check below. Code in
`experiments/redteam_local_repeats/`; `experiments/local_repeats/`, `experiments/redteam_identifiers/` and
`experiments/identifiers/` are imported read-only, never edited.

Known at registration (stated so the reader can discount): local_repeats RESULTS.md, results.json, explore.json
and code (lr.py, lr_explore.py); redteam_identifiers RESULTS.md and c1.py (bigram null N2); numeral_grammar,
pair_numeral_long, redteam_pnl, firing_stage RESULTS.md; RESEARCH_STATE tail. While reading I already saw that
`sources/shaunmortal_indus/STATE.md` line 336 lists "opener + stroke + tree (M267-M99-M102-M161 x5,
M267-M99-M104-M161 x5, M391-M99-M102-M161 x4)" among repeated square-seal texts, and that the bridge maps W817 and
W861 both to M267, W002 to M99/M100 and W390 to M161/162/167/168/169. No statistic of my own was computed.

Unit (as local_repeats): complete ICIT seal objects (`id_lib.icit_objects()`, `complete`, `cls=="seal"`),
text = sides joined (W signs). Formula = length 4, opener in {W817,W861,W820}, W002, short numeral
(local_repeats' NUM set), W390. 4-5 sign repeated objects = objects whose text (length 4-5) is on >= 2 seals.

## R1 "a cross-site formula accounts for ~40% of the excess (14 objects, 5 sites, bigram null 0.15)"

- **R1a null choice (primary).** 500 simulated seal corpora each (keep every seal's length; only lengths 4-5 matter
  for the statistic but all seals are simulated). Statistics: objects on repeated 4-5 texts (all / formula / other)
  and number of formula-frame seals (any numeral). Nulls:
  - N2 = red-team global bigram (reproduction check: formula mean must be ~0.15).
  - TRI-A = interpolated trigram (lambda 0.6/0.3/0.1 over trigram/bigram/unigram ML with END), fitted on all distinct
    complete ICIT texts (self-inclusive, like N2). Exact length via sampling-importance-resampling (20 candidates per
    text, weights = END/no-END probabilities).
  - TRI-L = same, fitted on distinct complete ICIT texts EXCLUDING every seal text of length 4-5 (leave-out; the
    formula can only be learnt from other carriers and from longer texts).
  - SLOT-A / SLOT-L = positional slot bigram: slots first, second, middle, penultimate, last (length 3: first,
    middle, last); P(s1 | first), P(s_i | s_{i-1}, slot_i), add-0.01 backoff to slot unigram; fits as for TRI-A/L.
  - Model adequacy: 5-fold CV (folds over distinct texts) mean log-likelihood of held-out 4-5 sign seal texts,
    bigram vs trigram (joint with END) and bigram vs slot (conditional on length). Reported, not a verdict input.
  - Sensitivity (reported only): trigram lambdas 0.8/0.15/0.05 and 0.4/0.4/0.2.
  - **Rule.** Fair nulls = TRI-L and SLOT-L. *Survives* if formula objects (14) have p_ge < 0.025 under both fair
    nulls AND their mean expectation is < 1.5 (i.e. 0.15 was not badly understated). *Weakened* if p_ge < 0.025 under
    both but mean >= 1.5 under either, or p_ge < 0.025 under only one. *Fails* if p_ge >= 0.025 under both.
    The same rule is applied to the "other 20 objects" residual (secondary claim).
- **R1b novelty.** Search `sources/*/STATE.md`, `sources/*/*.md`, `experiments/*/RESULTS.md`, `docs/*.md` for prior
  statements of opener + M99/W002 + short numeral + M161/W390 as a repeated text. *Not new* if any prior record lists
  >= 2 of the formula texts as repeated seal texts. (I already know one such record exists; this check documents it
  and looks for others.) The published literature (Mahadevan 1977, Parpola 1994, Wells 2011) is not machine-readable
  here; I will state what the M77 concordance itself shows (Mahadevan published the texts, so the repeats were in
  print since 1977) and flag the rest as a human lookup.
- **R1c independence of the 14 objects.** Per object: ICIT type, CISI, material, w x h, emblem, period, findspot.
  Flags: (i) not a stamp seal in CISI terms (type not SEAL:*, material faience/terracotta/copper, or a "tablet"),
  (ii) missing CISI, (iii) same site + same emblem + dims within 0.5 mm (possible duplicate or one die),
  (iv) same text at the same site on other carriers (batch production). Also check M77: count M77 seal records
  (Mahadevan transcription, M signs) for the frame opener {M267,M391} + {M99,M100} + short numeral + {M161,M162,M167,
  M168,M169}, and which exact M closer/connective the frame uses. *Rule:* recompute R1a's p for formula objects with
  every flagged object removed (or collapsed to one per flagged group). If >= 3 of 14 are flagged, R1 is at least
  *weakened* on this axis; if the recomputed count is no longer > 97.5th pct of N2, *fails* on this axis.
- **R1d M77 held-out.** M77 seal objects (`id_lib.m77_objects()`, cls seal, complete), text in M signs.
  Count formula-frame objects and repeated formula families in dev vs heldout (`dev_heldout(version=2)`, object in
  split if all its sides are). Null: bigram and trigram (interpolated, as TRI) fitted on DEV distinct texts only, 500
  simulations of the heldout seal lengths. *Survives* if heldout formula-frame objects exceed the 97.5th pct under the
  dev-trigram null and >= 1 heldout formula text is repeated; *weakened* if only one holds; *fails* if neither.
  Caveat stated in advance: M77 heldout is not independent of discovery (the formula was found on all ICIT objects,
  which include M77's). ICIT sites absent from M77 are reported descriptively.

## R2a "texts grow, never shrink" (6/15 vs 8/1,017, p=9e-9; 0/15 shorter)

- **R2a-0 reproduce** the counts with local_repeats' functions (imported).
- **R2a-1 unit = (text, site).** Each family contributes one unit per site it occupies; hit = one-sign-longer
  complete text (any class) at that site. Fisher one-sided vs singleton (text, site) units of the same length band.
- **R2a-2 commonness-matched controls.** Commonness = mean per-sign log-probability under N2 (length-conditioned,
  fitted on all distinct complete ICIT texts). For each family unit (text, site): the 10 singleton seal texts of the
  same length at the same site with nearest commonness (fall back to all sites if < 10 at that site). Null: 10,000
  draws of one control per unit, family hit = any unit hit; statistic = families with a longer variant (obs 6).
  Same for shorter variants (obs 0). Also Mantel-Haenszel OR stratified by length x site group (MD / Harappa / other)
  x commonness tertile, units as above.
- **R2a-3 generative null.** Simulate the whole complete ICIT corpus (all classes; keep each object's site, class,
  text length) 300 times under N2 and under TRI-A; in each, repeated = seal text of length >= 4 on >= 2 seals;
  compute longer / shorter hits at same site for repeated vs singleton seal texts (length >= 4). Pool over sims:
  null share of repeated families with a longer variant, null OR. Report the observed share's percentile.
- **Rule (growth).** *Survives* if obs 6/15 exceeds the 97.5th pct of the matched-control null (R2a-2) AND the
  pooled generative-null repeated-family share under TRI-A is below 6/15 with exact binomial p < 0.025. *Weakened* if
  only one holds. *Fails* if neither.
- **Rule (never shrink).** "Never shrink" counts as evidence only if P(0 of 15 | matched-control shorter rate) < 0.05
  (binomial, using the control family-level rate). Otherwise *uninformative*.

## R2b "not local" (same-site pair share 0.43 vs 0.45 random; between/within ratio 1.10)

Variants (10,000 permutations each: reassign the family objects to sites drawn without replacement from all >= 4 sign
complete seals, family sizes fixed):
 V1 pair-weighted share (original); V2 family-weighted (mean over families of same-site pair share);
 V3 = V1 and V2 with the 5 formula families removed; V4 = V1/V2 removing the H-352/H-354 family (incised tablets) and
 any family whose objects R1c flags; V5 4-5 band only; V6 between/within per-possible-pair ratio with a family
 bootstrap 95% CI (all families and non-formula).
- **Rule.** "Not local" *survives* if no variant has p_more_local < 0.05. *Weakened* if one or more variants have
  p < 0.05 but the non-formula V3 family-weighted p >= 0.01. *Fails* if V3 (non-formula) has p < 0.01 on both
  weightings, i.e. once the formula is removed the remaining repeats are local.

## Multiplicity
Confirmatory family = 4 verdicts (R1a, R1d, R2a growth, R2b). Holm across their primary p-values. Everything else
is reported as diagnostic.
