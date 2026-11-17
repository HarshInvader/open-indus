# Pre-registration: language vs non-linguistic code (experiments/language_vs_code)

Written 2026-11-14 after all calibration and Indus-dev runs, BEFORE any held-out Indus sign was read
(held-out texts were used only for their length list, to size-match the calibration samples).
Held-out = `dev_heldout(version=2)`, 565 break-free distinct texts, 2,352 tokens.

Frozen script hashes (sha256):
- lvc_corpora.py 18ca70959f70a3a5c3157d70201db22e8dfbb36d63c0357df5b30161f57741d6
- lvc_metrics.py 559339420af22d1739a156577e01b68601eac546556b9d9d768b4234f30de9ca
- lvc_calibrate.py 7cfbdaad515c08c2252a574586491353fc86cc804eaa55aad79bfafe849681e9
- lvc_indus.py c8378ff60eaacdd0158dceae982fadf38a12fcb10a6911450d02de75f1f6a09a
- lvc_analyze.py 68fddaa77d373d279c95196c25ec88918248f9029dec60df7b2e9b3cf52b9b04

Run: `lvc_indus.py heldout` then `lvc_analyze.py heldout --heldout`.

## Discriminators (each a z or effect vs a structure-preserving null on the same sample)
edge_ldd (opener-closer MI beyond adjacent transitions, doublet-preserving shuffle), skip_cmi
(I(X_i;X_i+2|X_i+1)), mal_surp and mal_seg (Menzerath-Altmann analogues), open_edge (interior vs edge
vocabulary openness), heaps (inventory growth exponent), abbrev (law of abbreviation on induced
segments), repeat (texts with a repeated sign vs token permutation).

## Calibration status at held-out size (565 texts, Indus length mix), already observed on dev side
20 labelled systems: 14 language (7 logo-syllabic, 7 pure word-sign), 6 code (heraldry, khipu, ICD-10,
licence plates, SIGIL rebuild, slot code). Classifier 'all' (8 metrics, class-balanced logistic C=0.3):
leave-one-system-out balanced accuracy 0.61; languages called L 10/14; codes called L 3/6.

## Tests
- **T1 power gate.** The battery counts as a discriminator only if LOCO balanced accuracy at held-out
  size >= 0.80 AND codes called L <= 1/6. Already determined: **fails (0.61, 3/6)**. Consequence,
  fixed in advance: whatever the held-out classification, it is not evidence either way.
- **T2 frozen classifier on held-out Indus.** Classifier 'all' trained on all 20 labelled systems at
  held-out size. Prediction: raw P(language) in [0.40, 0.60] (undecided band; dev subsamples gave
  0.49, 90% 0.47-0.51). Calibrated posterior (prior 0.5, Laplace sens 11/16, FPR 4/8) is reported.
- **T3 replication of Indus values.** Each of the 8 held-out metric values falls inside the 95%
  range of the 25 dev subsamples of the same size (edge_ldd [-3.39,0.13], skip_cmi [-0.03,3.41],
  mal_surp [-7.29,-3.56], mal_seg [-4.96,-1.94], open_edge [-0.127,-0.012], heaps [0.295,0.481],
  abbrev [-11.13,-2.85], repeat [-0.83,-0.48]). Pass if >= 6/8.
- **T4 directional descriptions** (Bonferroni over 4, one-sided |z| >= 2.24):
  a) no opener-closer dependency beyond adjacent transitions: edge_ldd < 2.24 (pass = absence);
  b) Menzerath on segments: mal_seg <= -2.24;
  c) abbreviation-type relation on segments: abbrev <= -2.24;
  d) longer texts use more frequent signs: mal_surp <= -2.24.
  None of these is diagnostic (each is matched by >= 2 code systems in calibration); they only
  describe Indus.

## Falsification
T3 < 6/8 would mean dev-derived Indus profiles do not transfer and the comparison is unstable. A
discriminator with LOCO balanced accuracy >= 0.80 and <= 1/6 code false positives at Indus size,
found later on new comparators, would overturn the "no power" conclusion.
