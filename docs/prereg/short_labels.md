# Pre-registration: language vs code with a genre-matched short-label calibration set (experiments/short_labels)

Written 2026-11-15 after all calibration runs, BEFORE any Indus sign (dev or held-out) was put through
the battery in this experiment. Held-out Indus texts were used only for their length list.
Held-out = `dev_heldout(version=2)`, 565 break-free distinct texts. The battery (`lvc_metrics.py`) and
classifier are reused unchanged from language_vs_code.

Frozen hashes (sha256):
- experiments/short_labels/cdli_extract.py 99a6f476d603aed043e1d3c9c9e6e95858b04542dad0e06fda49ed2517395fdb
- experiments/short_labels/build_corpora.py 8dd46a726c8cf2042b9339f948c977bcb107594ee04d049c3dc6e49c0bfde55d
- experiments/short_labels/sl_corpora.py ac1e3d0c1c3862608054770bb756c35c1c2495ebc922025115c5e0d85137e36e
- experiments/short_labels/sl_calibrate.py 694523c0ad8a62a8fc630216b837eca8289b9f5f776be0b1405cba4face0d714
- experiments/short_labels/sl_indus.py 31c5045ade87f54a794e9a16c39b3d2df504e91001659ebf2a07e4e93edf9c78
- experiments/short_labels/sl_analyze.py 3e7cf0c761410786307833dea88f2aeef7e6fdb584e7ad5955f79fc4575fe2dc
- experiments/language_vs_code/lvc_metrics.py 559339420af22d1739a156577e01b68601eac546556b9d9d768b4234f30de9ca
- experiments/short_labels/out/calib.jsonl 226e7fe511385defdccaaa2ccf54fec90429128c8788bdca16b186f885d6efad

Run order: `sl_indus.py dev`, `sl_indus.py heldout`, `sl_analyze.py --indus`.

## Calibration set (primary = `genre_real`: real, whole, uncut units of length 1-17)
- Writing (L): Ur III seal legends (CDLI, signs); Old Babylonian/Old Assyrian seal legends (CDLI, signs);
  Linear B entry lines (DAMOS, signs); Earlier Egyptian verbless phrases = titles, names, offering
  captions (TLA v18, hieroglyphs); Latin stamps/owner marks/labels/instrumentum (EDH, diplomatic words);
  Latin whole short inscriptions (EDH, words). Size B adds Old Akkadian seal legends and Linear A
  nodules/roundels/vessels (too few for size A).
- Codes (C): Rietstap heraldic blazons, Inka khipu cord clusters, ICD-10-CM codes, Unicode emoji
  sequences, named chess openings (SAN moves), McGill Billboard chord phrases, METAR weather reports.
- Sensitivity sets: `genre_plus_synth` (+ licence plates, slot code, SIGIL rebuild) and `all`
  (+ the language_vs_code chunked-prose corpora).
- Sizes: A = 565 texts with the held-out Indus length list; B = 150 texts (fixed subset of that list).

## Calibration result already observed (no Indus involved)
Primary (size A, genre_real, 8 metrics, logistic C=0.3 as in language_vs_code):
leave-one-system-out balanced accuracy 0.69; languages called L 4/6; codes called L 2/7;
label-permutation p = 0.20 (200 permutations). Leave-one-family-out 0.69.
Other cells (secondary, 2 sizes x 3 sets x 5 classifiers = 30 cells): range 0.38-0.82; the only
cell >= 0.80 is genre_plus_synth / size A / unregularised logistic (C=100): 0.82, 2/10 codes -> L.
That is the maximum over 30 cells and is treated as a forking path, not as power.

## Tests
- **S1 power gate (primary).** The battery counts as a discriminator on genre-matched data only if, at
  size A on `genre_real` with the all-8 classifier: LOSO balanced accuracy >= 0.80 AND codes called
  L <= 1/7 AND permutation p < 0.05. Already determined: **fails (0.69, 2/7, p = 0.20)**. Fixed
  consequence: the Indus classification below is reported but is not evidence either way.
- **S2 Indus held-out score (descriptive).** Classifier trained on all primary systems at size A,
  applied to the full held-out set. Report raw P(L), its percentile among the calibration systems'
  LOSO P(L), and the Laplace-calibrated posterior (prior 0.5). Prediction: Indus is not more extreme
  than every calibration system on either side (percentile strictly between 0 and 1).
- **S3 stability.** Held-out raw P(L) (size A, primary) lies inside the 5-95% range of 40 dev
  subsamples of the same size. Pass/fail reported.
- **S4 secondary cell.** For the one cell that crossed 0.80 (genre_plus_synth / A / C=100), report
  Indus held-out P(L). Pre-stated reading: it would need to replicate on the dev subsamples (median on
  the same side of 0.5) AND survive a fresh comparator set before it means anything.

## Falsification / what would change the conclusion
A classifier with LOSO balanced accuracy >= 0.80, <= 1/7 codes called language and permutation
p < 0.05 on real genre-matched systems would overturn "no power at Indus size". Adding Pictish (Lee
et al. 2010 data) or another real emblem system would be the next comparator test.

## Amendment (before any Indus run; nothing scored)
`sl_indus.py` crashed on import because `sl_calibrate.py` parsed `sys.argv` at module level. The
argv line was moved inside `__main__` (no change to sizes, seeds or length lists; calib.jsonl unchanged).
New hash: sl_calibrate.py 9b7b812138fbfcbd90ee0a724bd21ebee49b922e31abe4bc05c4d4c028c0ee67
