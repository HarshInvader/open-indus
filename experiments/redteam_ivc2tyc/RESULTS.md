# Red team of ivc2tyc: are Tibetan-Yi Corridor scripts visually closer to Indus than Bronze Age scripts? (board task #20, agent H4)

## Verdict: mixed. Under the pre-registered rule the claim technically survives, but its whole advantage comes from one small set (Ba-Shu, 281 glyphs). Proto-cuneiform is closer to Indus than four of the five corridor scripts, in every condition.

1. **The direction reproduces with a simple embedding (H1).** On the raw images, pooled TYC beats the best Bronze Age script: D = +0.028, 95% interval over 20 resamples [0.010, 0.044]. Ba-Shu is the closest single script in 20 of 20 resamples.
2. **It survives style normalisation (H3, the primary test).** All glyphs were skeletonised and redrawn at a 3 px stroke. D = +0.029 [0.005, 0.055], and Ba-Shu is still closest in 20/20. By the prereg rule (D > 0 and the closest script is a TYC one), the claim survives.
3. **But the advantage is Ba-Shu alone.**
   - NORM nearest-neighbour similarity: Ba-Shu 0.581, proto-cuneiform 0.536, Standard Yi 0.526, Old Naxi 0.503, Yi 0.488, Naxi Dongba 0.461, proto-Elamite 0.426.
   - Proto-cuneiform beats Old Naxi, Yi and Naxi Dongba in all three conditions. On RAW and THICK it also beats Standard Yi.
   - The paper's headline pairing is Naxi Dongba, and it is among the least Indus-like sets in every condition.
4. **Stroke rendering moves the result (H4).**
   - Indus strokes are bold, with a median width of 2.6 px at 64 px. Proto-cuneiform (1.5 px) and proto-Elamite (1.9 px) are thin line drawings.
   - Redrawing only PC and PE at Indus stroke width shrinks D to +0.013, and the interval crosses zero [−0.011, 0.028].
   - The ranking did not reverse, so the prereg "broken" condition is not met. Still, about half of the raw gap is drawing style.
5. **The base rate is high (H5).** Five of the seven candidate scripts are TYC, so under exchangeable scripts the closest one is TYC with probability 5/7 = 0.71. "A TYC script is nearest" is weak evidence by itself.

## Numbers
280 glyphs per script and 20 seeded resamples. Embedding: 32x32 downsample, then PCA to 50 dimensions. NN-sim is the mean over Indus glyphs of the maximum cosine similarity to the other script. Files: `results.json`, `out/run.log`.

| script | stroke width px (median) | NN-sim RAW | NN-sim NORM | NN-sim THICK |
|---|---|---|---|---|
| Indus | 2.60 | – | – | – |
| Ba-Shu (TYC) | 3.54 | 0.570 | 0.581 | 0.577 |
| proto-cuneiform | 1.46 | 0.513 | 0.536 | 0.537* |
| Standard Yi (TYC) | 4.14 | 0.474 | 0.526 | 0.477 |
| Old Naxi (TYC) | 2.23 | 0.489 | 0.503 | 0.501 |
| Yi (TYC) | 2.92 | 0.477 | 0.488 | 0.489 |
| Naxi Dongba (TYC) | 2.18 | 0.460 | 0.461 | 0.469 |
| proto-Elamite | 1.88 | 0.419 | 0.425 | 0.433* |
| TYC pooled | – | 0.541 | 0.565 | 0.550 |
| **D = TYC pooled − best Bronze** | | **+0.028 [0.010, 0.044]** | **+0.029 [0.005, 0.055]** | **+0.013 [−0.011, 0.028]** |

\* redrawn at the Indus stroke width (3 px); the other scripts are raw in THICK.

**Centroid cosine (secondary similarity)** is unstable. Signs flip between conditions: proto-cuneiform is +0.20 RAW, −0.60 NORM, −0.31 THICK; Ba-Shu is −0.29, +0.47, −0.26. Nothing should be built on it.

**Post hoc pooling check** (`secondary_pooling.py`, run after the primary results were seen and labelled so). TYC pooled without Ba-Shu against Bronze pooled (PC+PE):
- RAW: +0.022 [−0.005, 0.046]
- NORM: +0.023 [0.002, 0.047]

But proto-cuneiform alone (NORM 0.550 in this run) matches or beats TYC-without-Ba-Shu (0.543). Pooled comparisons mostly reflect which sets go into the pool. Proto-Elamite drags the Bronze pool down.

## The paper's own statistics
- **Their own table disagrees with their framing.** Their summary has Old Naxi (0.878) and Naxi Dongba (0.852) below proto-cuneiform (0.887).
- **Their tests are pseudoreplicated.** Their t-tests (t ≈ 2,000–3,400, p = 0) treat every glyph pair as an independent observation. The units are scripts, and there are seven of them.

## What failed or was not checked
- We used a simple PCA embedding, not their CNN. A learned embedding could rank differently; our point is that the ranking depends on one set and on stroke rendering.
- The image sets differ in source and rendering:
  - Standard Yi is a font;
  - Ba-Shu glyphs are bold filled shapes;
  - PC and PE are line tracings.
  Skeletonisation removes stroke width but not the drawing conventions (filled areas, curves against wedges).
- Licence per dataset was not checked. The repo is MIT, but the images come from various sources. Used locally as data only; no code from the repo was run.
- No test of the historical claim itself (contact or descent). Visual similarity at this level cannot speak to it.

## Hypotheses
| hypothesis | verdict |
|---|---|
| H1 direction reproduces on raw images | yes (D +0.028 [0.010, 0.044]) |
| H2 Indus stroke width closer to TYC than to PC/PE | yes (2.6 px vs TYC 2.2–4.1, PC/PE 1.5–1.9) |
| H3 TYC closer than Bronze after style normalisation | survives by the prereg rule (D +0.029 [0.005, 0.055]), carried by Ba-Shu |
| H4 thickening PC/PE reverses the ranking | no reversal; D drops to +0.013 [−0.011, 0.028] |
| TYC scripts as a group are closer than proto-cuneiform | refuted: PC beats 3–4 of 5 TYC sets in every condition |

Pre-registration: `docs/prereg/redteam_ivc2tyc.md` (hashed with `run.py` in `docs/prereg/HASHES.txt` before the run).
