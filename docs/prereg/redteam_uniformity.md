# Prereg: red team of the uniformity benchmark

Written 2026-11-21, before any condition below was scored. Code: `experiments/redteam_uniformity/rt.py`, hashed with this file in `docs/prereg/HASHES.txt` (tag `redteam_uniformity`). Seen before writing: pool sizes per condition (`rt.py sizes`), the benchmark's published numbers, and the old Indus P1 number (0.49).

## Claim under attack

`experiments/uniformity_benchmark/RESULTS.md`: the frozen site_signal classifier separates sites in every real reference corpus at Indus size (0.71 to 0.89), while Indus Mohenjo-daro vs Harappa gives 0.49, so Indus seal writing is unusually uniform across cities.

## Method

Every condition goes through the benchmark's own `clean()` (drop strings found at both sites, then the non-chaining greedy de-dup of `fish_tick_closer_v2/dedup.py`), `draw_n()` (Indus length mix, balanced sides) and `score()` (frozen NB pipeline, one permuted-label AUC per draw). Indus texts are put into the reference format. 30 draws per condition. Statistic: median AUC over draws; null = permuted-label AUCs over draws.

1. **Like-for-like.** Indus ICIT seals (complete, no breaks), Mohenjo-daro vs Harappa, through the same clean and draw. Harappa has 232 texts after cleaning, so the main size is 227 per side. References at 227 and 130 per side. Also the exact old P1 pool (strict exclusion) at 130 per side.
2. **Vocabulary.** References with tokens cut to 400 classes: top-399 types + UNK; top-400 with the rest dropped; top-200 kept + the rest hashed into 200 classes. Ur III also split into sign readings. Top-400 also combined with frame removal.
3. **Label leaks.** Ur III: one legend per seal owner (first line), owners at both sites dropped; all tokens with {d} or {ki} dropped; both plus signs + top-400 + frame removal. Latin: labels with military/unit words or Roman numerals dropped. Proto-cuneiform: sign variant marks (~, @) removed.
4. **Indus transcription.** ICIT with allograph merges A1, A2; M77 (Mahadevan) seals; M77 with the lump_all list. No variant-splitting list beyond Wells/ICIT exists in the repo; ICIT A0 is the splitter.
5. **Other Indus pairs.** Harappa and Mohenjo-daro each vs Dholavira, Lothal, Kalibangan, Chanhu-daro (ICIT seals); M77 sealings MD vs Harappa; M77 Lothal vs Harappa; Harappa seal vs sealing; Harappa seal vs miniature tablet; MD earlier vs late. Size = smaller side. References at 35 and 50 per side as small-n baselines.
6. **Power.** Indus like-for-like pool, labels permuted inside each draw, then each site gets its own Zipf-weighted local stock replacing a share q of tokens (q = 0.05 to 0.3): 100 new symbols per site, or 40 existing common signs per site. Classifier-free "local share" (tokens whose type is seen ≥2 times, ≥90% at one site) is recorded for every draw so references and plants sit on one scale.

## Verdict rules (fixed now)

- **Broken** if any of: Indus like-for-like median ≥ 0.60; or 2 or more of the 3 name-bearing references fall below 0.60 under the strongest combined control they can be put through (vocabulary + leak + frame); or power at the reference-like local share (lowest name-bearing reference, after controls) is below 50% for reaching 0.65.
- **Stands** if all of: Indus like-for-like median below its null q95; all 3 name-bearing references ≥ 0.65 under every control; power ≥ 80% at the reference-like local share; no other Indus pair at its size exceeds the small-n reference range.
- **Stands weakened** otherwise.

Tests: about 95 conditions, descriptive medians; no p-value decisions, so no multiple-test correction. Any condition added after scoring is labelled exploratory.
