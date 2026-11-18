# Pre-registration: how many name anchors would a reading need? (name_anchors)

Written 2026-11-17, before any run. Planning simulation; it makes no claim about Indus.

## Question
If outreach returns objects that tie a readable name (cuneiform or Linear Elamite) to an Indus-sign text, how many such
name-text pairs are needed before the goal's success test (b) can work: values fixed by the anchors must predict texts
they were not fitted to, under a pre-registered test, better than the same names attached to the wrong texts?
This is the open item "a bilingual-name simulator: anchors restricted to the signs of 1-3 specific names" in
experiments/decipherability/RESULTS.md.

## Simulation (reuses experiments/decipherability, unchanged)
- Planted scripts: `cells.planted(lang, "names", 10000, 0.2, rep)` for lang in san, tam, sux, lat, fin; rep 0-2
  (Indus size: ~10k tokens of short name texts, 20% logograms).
- Split planted texts 75/25 at random (seed = rep): dev and held-out.
- Anchors: m in {1, 2, 3, 5, 10} dev texts of 2-6 signs with >= 2 syllabic signs, drawn at random (seed 7*rep+m).
  The true values of their syllabic signs are fixed; their logograms are left free (a cuneiform spelling gives syllables).
- Wrong alignments: the same m names (their syllable value sequences) attached to m other dev texts of the same length,
  drawn at random; sign i of the wrong text gets value i of the name (first assignment wins on conflicts).
  19 wrong alignments per cell.
- Fit: `anneal(dev corpus, LM, sweeps=60, restarts=2, fixed=anchors)`. Score: held-out `Corpus.score(key, LM)`.
- Language models: K1 = the true language's lexicon; K3 = the true language's phonotactics; W = a wrong language's
  lexicon (san<->tam, sux->lat, lat->fin, fin->sux). W is the realistic Indus case: the language is unknown.

## Test and thresholds (fixed now)
- A cell passes when the correct alignment's held-out score ranks first of 20 (one-sided p = 0.05).
- Power(m, LM) = share of the 15 (lang, rep) cells that pass. Feasible m* = smallest m with power >= 0.8.
- Also reported: syllabic-sign token accuracy on non-anchor signs (correct anchors vs m = 0), and anchor coverage
  (distinct signs fixed, share of tokens).
- Reading of results: if m* > 10 under W, a handful of bilingual names cannot by itself satisfy success test (b)
  unless the language is also known; the outreach goal should then be stated as "names plus the language".
