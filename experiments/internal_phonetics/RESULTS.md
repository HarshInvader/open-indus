# Internal phonetics: does Indus spelling variation leak sound values?

Internal-phonetics specialist, 2026-11-14. Code in this folder; run from the repo root in this order: `run_controls.py 500 realistic`, `run_controls.py 500 strong`, `run_indus_dev.py`, `run_heldout.py`. Logs are `*.log`, numbers are in `results.json`, and the pre-registration is `docs/prereg/2026-11-14_internal_phonetics.md`, written before held-out was touched.
Unit: distinct M77 texts from `dev_heldout(version=2)` with no `#` and with `|` removed. Dev has 1,675 texts and held-out 564.

## Conclusion first

**None of the four mechanisms shows up in the Indus texts, and held-out confirms nothing. This is a weak negative, not a refutation.** At Indus size, with realistic copy rates, the planted controls show the tests have low power. Their false-positive rates are near zero for T1 and T4, but not for T2 and T3. Spelling variation alone cannot recover phonetic equivalences in this corpus.

| mechanism | power at realistic strength (strong) | false positives with mechanism absent | Indus dev | held-out | verdict |
|---|---|---|---|---|---|
| 1 Phonetic complements | 4/10 corpora meet the rule (9/10) | 0/10 (0/10) | 25 host-specific optional signs, but only 1 is transparent: M242, a text-final post-closer, so slot-optional. 1 < 3 | 0 significant of 14 tested | **not detected**. The formula collocations are not complements |
| 2 Homophone/allograph transitivity | 8/80 planted pairs (23/80) | 0.6 slot-paradigm pairs per corpus | 2 pairs at q<0.05: M65\|M72 (look alike), M99\|M402 (do not look alike) | neither replicates (k=1, p=0.23; k=0) | **inconclusive. No homophone sets** |
| 3 Ligature decomposition | 3/50 planted triples (16/50) | 2.9 (5.0) spurious triples per corpus | 1 triple (M12 ↔ M342 M176) against 6.7 in Indus-bigram corpora. 0 events for every graphic candidate | M12 triple absent; candidates 0 events | **no ligature decomposition**. M343-345, M348 and M190 are not written-out pairs |
| 4 Silent determinatives | 2/10 (7/10) | 0/10 (1/10) | no modifier class is dropped more often than chance | only fish marks: 2 vs 0.25 expected, p=0.026; dev fails, so not confirmed | **undecidable**. "Never dropped" cannot be tested either: the expected counts are below 0.3 |

**Candidate phonetic equivalence sets: none survive.** The only statistically supported alternation that recurs across frames is inside the fish paradigm: M65\|M72 on dev (7 independent contexts, q=0.04), M65\|M67 (7 contexts, q=0.08), and M59\|M70 and M65\|M70 (p≈0.04-0.06). These signs look alike, so if anything they are allograph-type or paradigm members, not homophones. Held-out cannot check them: the family split leaves only 31 multi-filler frames in held-out.

## Why held-out is nearly empty for these tests

The v2 split keeps near-copy families on one side. Held-out therefore contains few within-family variants:
- 31 frames with 2 or more fillers (dev has 221)
- 46 one-to-two-sign events (dev has 2,014)
- 0 to 3 substitutions at modifier positions per class

Every mechanism here is defined by variation within a legend family, so held-out can confirm only very strong effects. An independent test needs new near-copy families: a new excavation corpus, or ICIT texts from sites absent from M77, once the W↔M bridge covers more signs.

## Planted controls (`synth.py`, `run_controls.py`)

- **Synthetic corpus.** 1,675 distinct texts, mean length 4.4-4.5, about 340 sign types. The building blocks:
  - 380 logograms and 50 one-per-sound syllabograms
  - openers + connective, closers, and slot-optional post-closers and initial "fish"
  - 700 Zipfian words: logogram, logogram+logogram, syllabic, or logogram+syllable
- **Variants.** Each legend type is attested on 1+Geom(0.9) objects, with slot noise (fish or post-closer toggled, opener or closer swapped, one word swapped).
- **Calibration to Indus dev.** Share of texts with an edit-1 neighbour, by length:

  | text length | Indus | synthetic |
  |---|---|---|
  | 2-3 | 0.63 | 0.66 |
  | 4 | 0.60 | 0.51-0.54 |
  | 5 | 0.35 | 0.22-0.28 |
  | 6+ | 0.08 | 0.09-0.12 |

  Substitutions per text: 0.42 Indus vs 0.42-0.53 synthetic. Indels per text: 0.22 Indus vs 0.20-0.24 synthetic.
- **Mechanisms planted at "realistic" strength:**
  - comp: 6 logogram hosts take a syllabic complement after them, p=0.5
  - homo: 5 homophone syllabograms and 3 alternative logograms, used with p=0.4 (8 planted pairs)
  - lig: 5 ligatures, used with p=0.35
  - det: 4 silent determinatives, dropped with p=0.3, plus 4 lexical modified signs that are never dropped
- **"Strong" strength:** legend multiplicity Geom(0.6), 12 complement hosts, and rates of 0.5 for homo, 0.6 for lig and 0.5 for det.
- **Runs:** 10 seeds, each with the mechanisms ON and with them OFF.

Lessons from the controls, all of which shaped the final tests:
- **T1, strict edit-1 version (whole text identical except one inserted sign): no power.** At realistic strength 3/60 planted complements are detected; at strong strength, 20/120.
- **T1, local-insertion version.** Here x is optional when `g h x y` is written in one text and `g h y` in another; host specificity is tested against a within-slot permutation. This version finds about 35% of planted complements. It also flags word-internal collocations and slot formulae (connective after opener) in the OFF corpora: 1-5 per corpus.
- **The transparency filter separates complements from collocations.** Transparency is the overlap between the next-sign distribution after "h x" and after "h" when x is absent. Planted complements score 0.34-0.65 (median 0.5). Connectives score 0.10-0.38, syllable collocations about 0, and the corpus median is 0.11-0.15.
- **Final T1 rule:** at least 3 signs with q<0.05 and transparency of 0.40 or more. Power is 4/10 at realistic strength and 9/10 at strong. The false-positive rate is 0/20.
- **T2** detects few planted homophones and flags slot-paradigm alternants (closer↔closer) at a similar rate. **Distributional transitivity therefore cannot tell homophones from paradigm members.** Drawing dissimilarity does not rescue this, because paradigm members also look different. The global count of multi-frame pairs is uninformative: it falls *below* its frame-shuffled null in every synthetic corpus (p 0.23-1.0), and Indus gives 69 vs 58.7 ± 6.5 (p=0.07).
- **T3**'s hypergeometric screen is anticonservative. Slot alternations of the type "one sign vs a two-sign formula" recur by chance. It is only usable alongside a bigram-null count and a check of the drawings.
- **T4** detects silent drops only when the legend multiplicity is high (7/10 at strong strength).

## Mechanism 1: phonetic complements (`tests.t1_local`, `tests.t1_complements`)

- **Events.** Dev has 751 "host precedes x" events and 954 "host follows x" events. Both orientations were run, which covers both reading directions.
- **Exclusions:** M176, M1, and fish M59-M75 in first position.
- **Host-specific optional signs (q<0.05):** 25 of 120 tested. Almost all are fixed formulae:
  - Before the jar, in the "host follows" orientation: M347, M8, M296, M194, M135, M348, M358, M294, M149, M48 → M342.
  - After the opener+connective: M387, M389, M67, M65, M102, M86, M87 after M99. M267 and M391 before M99.
  - M171 before M59/M8; M211 after fish; M249/M162.
- **These are collocations.** Their transparency is 0.04-0.40, against a corpus 90th percentile of 0.40. Removing the sign changes what follows the host, so it is part of the unit, not an optional add-on.
- **The one transparent sign is M242 (0.72).** It sits after M342/M162/M211 at the end of the text. It is a post-closer, slot-optional like M176, not a complement. M387 after M99 scores 0.395 (borderline, and part of the `M267 M99 [_]` filler slot).
- **Strict edit-1 version:** 3 signs (M267 before M99, M171, M347 before M342), all formula collocations.
- **Held-out:** 0 of 14 tests significant.
- **Verdict:** no complement candidates. Caveat: a real complement system at the planted strength would be missed 60% of the time.

## Mechanism 2: frame transitivity, allograph vs homophone (`tests.t2_transitivity`)

**Method.**
- Frames are contexts of texts with 3 or more signs that have 2 or more fillers: 221 on dev.
- k = number of distinct local contexts (left sign, right sign, slot) in which a pair co-fills.
- Null: curveball-randomised frame×filler membership within slot class, preserving sign degree and frame size, with 1,000 replicates. p is a Poisson tail at the null mean.
- Drawing similarity is my own blurred-cosine of the Mahadevan drawings (`common.glyph_sim`). Pairs at or above the 95th percentile among signs with 5+ tokens count as similar (≥0.58). The Wells-numbered `glyph_sim.npy` in sources/paragorth was not used, because it would need the 176-sign bridge.

**Dev pairs at q<0.05:**
- **M65\|M72**: k=7, λ=1.5, sim 0.77. Similar: fish variants.
- **M99\|M402**: k=2, λ=0.05, sim 0.07. Dissimilar.
  - It is the only "homophone-shaped" pair. Both occur directly after the opener (`M267 M99 …` / `M267 M402 …`).
  - The control shows that slot-paradigm alternants produce exactly this pattern.

With an empirical p, 8 further dissimilar pairs reached q≈0.048. All are slot paradigms (numerals M102\|M106, M112\|M245; closers M15\|M342; M204\|M205; M341\|M373; M124\|M348; M135\|M296). They come from a first run with a 1,000-replicate empirical p, since overwritten, and are exploratory only.

**Test cases (dev k, p):**

| pair | k | p |
|---|---|---|
| M65\|M67 | 7 | 0.006 |
| M65\|M72 | 7 | 0.001 |
| M59\|M67 | 5 | 0.07 |
| M67\|M72 | 4 | 0.07 |
| M59\|M70 | 3 | 0.06 |
| M65\|M70 | 3 | 0.04 |
| M59\|M65 | 3 | 0.31 |
| M59\|M72 | 2 | 0.43 |
| M70\|M72 | 2 | 0.11 |
| M67\|M70 | 1 | – |

- The marked fish M65, M67 and M72 alternate across frames more than the slot null predicts. Plain M59 does not alternate specifically with them. This fits novel_methods' "paradigm, not free allographs".
- **Openers:** M267\|M391 k=1, M267\|M293 k=0, M293\|M391 k=0. **The openers do not co-fill frames at all**: there is no frame where one is swapped for another with everything else identical, beyond 1 context. M267/M391 alternate only in shorter frames (novel_methods found 11 swaps, mostly in 2-sign texts, which are excluded here), so they are not demonstrably the same word.
- **Held-out:** M65\|M72 k=1 (p=0.23) and M99\|M402 k=0. Neither replicates (31 held-out frames).

## Mechanism 3: ligature decomposition (`tests.t3_ligatures`)

**Method.**
- Events: pairs of dev texts identical except that one sign A stands where two adjacent signs B C stand, with 2 or more shared context signs. Plain insertions (A ∈ BC) are excluded. Events are collapsed by near-identical context.
- Dev has 2,014 events. 76 triples recur in 2 or more independent families.

**Results.**
- **One triple at q<0.05: M12 ↔ M342 M176** (2 families, q=0.027).
  - M12 is a closer that replaces the closer formula "jar + post-closer". It is not drawn as jar + comb (sim −0.15, −0.14).
  - Indus-fitted bigram corpora give 6.7 such triples (range 0-19), so even this is below chance.
  - The top recurrent correspondences are slot-level: M86 ↔ M267 M99 (5 families; both are openers); M294/M244/M48/M347 ↔ M171 M8; M59 ↔ M336 M89.
- **Graphic candidates:**
  - **M343/M344/M345 ↔ M342 + 1/2/3 strokes:** 0 events in either order. The sequences M342-M99, M99-M342, M342-M102 and M102-M342 never occur at all in dev. M343 and M345 *do* stand for "M267 M99" (M345: 3 events, not significant), i.e. they alternate with the opener formula. This matches novel_methods' finding that M343-345 are initial/mid-text, not jar-like.
  - **M348** (cup with prongs + comb) ↔ M347 + M176: 0 events. The bigram M347 M176 occurs once.
  - **M190** ↔ M162 + M186: 0 events; the bigram never occurs.
  - **M103 M403:** replaced by 10 different single signs, once each, so there is no single-sign equivalent.
- **Held-out:** 46 events. M12 triple absent; every candidate composition 0, as predicted.
- **Verdict:** no evidence that any compound-looking sign is an abbreviation of a written sign pair. The control power is low (6% at realistic strength), but these candidates have zero events and their component pairs are themselves unattested as sequences, so the negative is about as firm as this corpus allows.

## Mechanism 4: silent determinatives (`tests.t4_drops`)

**Method.**
- Base↔modified swaps in edit-1 substitution pairs (texts of 3+ signs, collapsed by context).
- Expected count = the base sign's share of all substitution partners in that slot.
- Modifier pairs are novel_methods/exp3's visual reading, with fish ticks split from other enclosures.

| class | dev obs / exp (p) | held-out obs / exp |
|---|---|---|
| fish ticks (M60, M66, M68, M71, M73) | 2 / 1.50 (0.44) | 0 / 0 |
| other enclosures (19 pairs) | 1 / 0.32 (0.27) | 0 / 0 |
| roof (5) | 3 / 2.43 (0.44) | 0 / 0.26 |
| strokes inside jar/cup (5) | 0 / 0.03 | 0 / 0 |
| fish internal marks (4) | 9 / 6.48 (0.21) | 2 / 0.25 (p=0.026) |
| ears, cup→jar (1) | 0 / 0 | 0 / 0 |

**Reading.**
- No modifier class is dropped within near-copy pairs more often than slot statistics predict.
- No class is shown to be "never dropped" either: expected counts are tiny, and p_never is ≥0.77 everywhere.
- Ticked fish (M60 etc.) do swap with their plain base in 2 dev pairs (M65↔M66, M72↔M73), at the chance rate. This is consistent with the red team's view that ticks are a modifier that moves a fish to the closer slot.
- The held-out fish-mark excess (M59↔M70, M59↔M72; 2 vs 0.25) is not a confirmation: as pre-registered, dev had to pass too.
- **Verdict: undecidable at this corpus size.** Power at realistic strength is 20%.

## Hypotheses

| # | hypothesis | verdict |
|---|---|---|
| H1 | At least 3 optional signs are tied to specific hosts (phonetic complements) | **not supported** (dev 1 transparent sign, a slot post-closer; held-out 0). Power 40% |
| H1b | Indus host-specific optional signs are collocation units (formulae), not transparent add-ons | supported (24/25 below transparency threshold) |
| H2 | Some dissimilar signs alternate across independent frames (homophones) | **inconclusive** (M99\|M402 on dev; not replicated; test cannot separate paradigm from homophone) |
| H2b | Marked fish M65/M67/M72 alternate frame-independently | supported on dev (q 0.04-0.08); held-out untestable |
| H2c | Openers M267/M391/M293 are one word spelled variously | not supported (they never co-fill frames of 3+ signs) |
| H3 | Compound signs = ligatures of written pairs (M343-345, M348, M190, M103+M403) | **refuted for these candidates** (0 events dev and held-out; component sequences unattested) |
| H4 | Sign-internal modifiers are silent determinatives (droppable) | **undecidable** (no excess drops; power 20%) |

**Tests run:**
- Controls: 2 strengths × 20 corpora × 4 tests.
- Dev: T1 143 tests, T2 69 pairs, T3 76 triples, T4 6 classes / 39 pairs.
- Held-out: the pre-registered set.
- BH within each test family.

## Caveats

- The synthetic corpus is a stand-in. Real logo-syllabic legends (Akkadian or Sumerian seals) would be a better control.
- The transparency threshold was set after seeing the controls and a first Indus dev output. This is disclosed in the pre-registration, and it does not favour a positive.
- The modifier families are novel_methods' visual reading of Mahadevan's drawings.

## Next experiments

1. Re-run all four tests on a corpus with more within-family variants. ICIT texts from sites absent from M77, in native Wells numbering, avoid bridge losses.
2. Power is limited by legend multiplicity. Pool M77 and ICIT families before splitting, and treat ICIT re-transcriptions as variant readings (a scribal-hand test), not new legends.
3. Test the M99\|M402 alternation and M402's drawing (a hatched element) on CISI photographs: is M402 a variant of M99 in some hands?
4. Real control: Sumerian/Akkadian seal legends from CDLI at matched size, where complements and determinatives are known.
