# Sign mapping by two blind agents: Parpola's fig and Mukhopadhyay's stroked jars (sealed 2026-11-23, before any mapping)

Agent `paper`. Coordinator instruction 2026-11-23, option (a). Catalogue rows PAR-vata-min and MUK19-stroked-jar-MET.

## Why
- Neither claimant gives Mahadevan numbers.
- Searched and found nothing: Mukhopadhyay 2019 (opened; the signs appear as inline glyph images) and her 2021 and 2023 papers.
- Parpola 2010 pp. 19-21 and the harappa.com summary are not available here (harappa.com returned a Cloudflare block, which was not bypassed).

## Inputs (identical for both agents; `.local/signmap_inputs/`, not published)
- **Mukhopadhyay.** The 8 inline glyph images from the MET section of doi:10.1057/s41599-019-0274-1, with the surrounding sentence.
  - img1-3 are "the stroked-jar signs" she classes as MET.
  - img4-7 are the graphemic series; img8 is the sign "discovered after the compilation of IDF-80".
- **Parpola.** No image could be obtained. The claimant's words only: a sign for the fig (banyan) tree, Dravidian *vaṭa*, read with the fish sign as *vaṭa-mīn* "north star".
- **Reference.** `mahadevan_descriptions.csv`: one-line shape descriptions of all 417 Mahadevan 1977 signs (from `site/data/sign_depictions.csv`).
- Agents may not use corpus statistics, sign frequencies, co-occurrence with fish, or any repo results. Matching is by shape only.

## Rule
- Two fresh agents work blind to each other. Each returns, per item: up to 3 candidate M numbers in order, a confidence (high/medium/low) and a one-line reason.
- **Agreement:** both agents' first choice is the same M number. Report the agreement rate over the 9 items (img1-8 and the fig).
- **Use:** only agreed first choices with at least medium confidence from both.
- **Stroked jar (MUK19):** at least 2 of img1-3 must be agreed, otherwise the claim is untestable by mapping.
  - With at least 2 agreed, count ICIT texts containing them. The catalogue's own gate requires 30 or more; below that, untestable by count.
  - At 30 or more, the catalogue rule runs as a separate sealed prereg (enrichment on pottery against the within-site object-type null).
- **Fig (PAR):** the fig item must be agreed, otherwise untestable by mapping.
  - If agreed, count M77 texts with fig directly followed by M59 or any fish sign in the catalogue's partner set.
  - The catalogue's rule (fixed pair beyond a frequency-matched null, held-out) runs as a separate sealed prereg only if there are at least 10 such pairs in dev.
- No mapping is changed by hand.

## Scorecard addendum 2 (same seal)
- FUN-sigil is flagged by `staleness.py`: atlas 3.3 changed after `sigil_heldout`.
- Two fresh blind raters re-rate FUN-sigil only, under the v1 rubric. A third settles a split.
- `finalize.py` gains the addendum-2 files in the same way as addendum 1.

## Addendum 1: the stroked-jar test (sealed before it was run)
- **Mapping and count gate (done).**
  - Both mappers agree on img1-3 as M343, M344 and M345, all at high confidence. They disagree on the fig, so the fig is untestable by mapping.
  - Agreement on first choices: 8/9 items.
  - ICIT distinct texts with any stroked-jar sign: 263, which passes the count gate (30 or more).
- **Already seen before this seal.** `self_label` reported M343 on ICIT pottery graffiti at 6 observed against 15.67 expected. M344 and M345 on pottery graffiti were not computed there (only stamped pottery: 0 vs 0.52 and 0 vs 0.46).
- **Primary test.**
  - ICIT pottery graffito. The pooled sign SJ means a text has any of M343, M344 or M345.
  - Null: object-class labels permuted within site, 10,000 draws (`self_label/s2_test.perm_test`). Ratio = observed / null mean.
- **Verdicts.**
  - Survives: ratio ≥ 2 and p ≤ 0.01.
  - Refuted: ratio ≤ 1 (the catalogue's kill condition) and power ≥ 0.8. Power is the chance that a true 2× effect, as Poisson(2·mean), clears the null's 99th percentile.
  - Anything else: inconclusive.
- Per-sign numbers are reported only. The M77 held-out split is not used.
- Code: `experiments/signmap/strokedjar_test.py`.

## Scorecard addendum 3 (sealed before rating)
- MC-MUK19-stroked-jar-MET and MC-PAR-vata-min are flagged by `staleness.py` after the catalogue update.
- Two fresh blind raters (I, J) re-rate these 2 rows under the v1 rubric. A third (K) settles a split.
- Addendum 2 (FUN-sigil: raters G, H) and addendum 3 are applied by `finalize.py` in the same way as addendum 1.
