# Pre-registration: red team of experiments/identifiers (C1 formula layer, C2 core novelty, C3 no repulsion)

Agent: redteam_identifiers. Written 2026-11-15 BEFORE running any of the checks below. Known at registration:
the identifiers RESULTS.md, results/logs, code; a descriptive dump of the 68 repeated ICIT seal texts with
their CISI numbers, sizes and emblems (`experiments/redteam_identifiers/repeated_dump.txt`; looked at by eye,
no statistic computed); the CDLI catalogue has a `date_of_origin` column. Code in
`experiments/redteam_identifiers/`. Does not edit `experiments/identifiers/` (imports `id_lib` read-only).

Data unit throughout = identifiers' unit: complete ICIT seals, one record per object, full text (sides joined).

## C1 "repeated seal texts are a short formula layer shared across cities at random"
- **C1a duplicate audit.** Flag repeat pairs that could be one object recorded twice: same CISI number; or
  same site + same emblem + same width and height (both non-zero). Also flag ICIT objects with no CISI
  number ('-') that repeat a text at the same site. Recompute objects-on-repeated-texts and the
  multi-site share without flagged duplicates (keep one per flagged set). *Inflated* if >= 25% of
  repeated objects are flagged.
- **C1b generative collision null (primary).** Simulate the 1,560-seal corpus 500 times keeping every
  object's site and text length, texts drawn from:
  - N1 positional unigram: first sign ~ initial-sign distribution, last ~ final, middle ~ medial
    (length-1 texts ~ pooled sign distribution). Fit on the same distinct texts as N2.
  - N2 (primary) global bigram with START/END, length-conditioned exactly (backward messages), fit on
    DISTINCT complete ICIT texts of all object classes (each distinct text counted once, so repeats do
    not feed their own bigrams more than once), add-0.01 smoothing.
  - N3 per-site bigram: same, fit on the site's distinct texts, interpolated 50/50 with N2.
  Statistics: objects on repeated texts by length band (1, 2, 3, 4-5, 6+) and total for lengths 1-3;
  number of repeated texts; share of repeated texts at > 1 site.
  Verdict for "formula layer": **artefact** if the observed count of objects on repeated texts of length
  1-3 is <= the 97.5th percentile of N2; **real excess** if above the 97.5th percentile of both N1 and N2
  (report observed / null mean). Cross-site: if observed multi-site share sits inside N2's 95% interval
  and N3 makes repeats more local, "shared across cities" is what a shared grammar predicts.
- **C1c length-matched locality vs Ur III.** Leave-one-out locality ratio, length-stratified:
  R_LOO = sum over target objects of [text occurs at reference site] / sum over target objects of the
  reference site's own leave-one-out match rate for texts of the same length (Indus: length in signs;
  Ur III: length in written cuneiform signs of the legend, and separately in words). All ordered site
  pairs with n >= 100 (Indus: sites with >= 40 seals). Bootstrap CI over target objects (500).
  Also unstratified R_LOO, and Ur III restricted to legends no longer than the longest Indus repeat.
  *Comparison holds* if length-matched Indus R_LOO > Ur III R_LOO with non-overlapping 95% CIs.
  Also check whether identifiers' Chao-bootstrap CIs contain their own point estimates.

## C2 "seal cores are more novel than real personal names" (91-92% vs Ur III name lines 54-75%)
- **C2a same recipe.** Build an Ur III "core" the way Indus cores were built: drop the frame words from the
  whole legend, where frame = the most frequent words taken until their token share equals the frame-token
  share of Indus seal texts. Compare new-text rate at m = 100 objects (same estimator).
- **C2b length-matched.** New rate at m = 100 within length strata (in written signs) for Indus cores and
  Ur III name lines; compare strata with >= 100 objects on both sides.
- **C2c inventory matched.** Recode Ur III name-line signs onto an inventory of the Indus core size by
  quantile-matching cumulative token mass (rank r Ur III sign -> Indus sign with the same cumulative mass;
  many-to-one when Ur III has more types). Recompute name-line new rate at m = 100.
- *Gap survives* if Indus core new rate exceeds the Ur III comparator by >= 0.10 in C2a, in every
  comparable C2b stratum, and in C2c. *Fails* if any of C2a/C2c closes the gap below 0.05.

## C3 "no identifier repulsion" (S4 null)
- **C3a detectable effect.** From identifiers' ICIT null A: minimum detectable shift in NN-NED (2.5 null SD)
  as a relative change; share of units whose within-bin nearest neighbour is closer than NED 0.5 (the
  maximum the planted repulsion can act on); share of weight in the two largest bins.
- **C3b local repulsion.** Plant repulsion only among true "contemporaries": random sets of h = 5 and
  h = 10 units inside each bin, strength 1.0, NED < 0.5 (identifiers' planted rule, applied inside sets);
  30 reps x 200 permutations of null A. *Meaningless for contemporaries* if power < 0.5.
- **C3c real identifier positive control.** Same S4 statistic and null A on Ur III seal legends (unit =
  distinct legend per bin, written-sign sequences) with bins = provenience + reign (from `date_of_origin`),
  site = provenience; bins of >= 3 distinct legends; subsample bins to <= 250 legends to match Indus bin
  sizes. If Ur III personal seals show no repulsion either, the S4 null carries no evidence against
  identifiers.
- Verdict on C3: *survives* only if C3b power >= 0.8 and C3c shows repulsion; *weakened* if one fails;
  *fails (uninformative)* if both fail.

## Multiple testing
Family of 3 primary verdicts (C1b, C1c, C2, C3 combined = 4 rows in the ledger). Everything else descriptive.
