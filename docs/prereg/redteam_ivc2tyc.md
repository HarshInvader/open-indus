# Pre-registration: red team of ivc2tyc (board task #20, agent H4)

Written 2026-11-17 before any similarity was computed.

**Claim** (arXiv 2503.21074, github oohalakkadi/ivc2tyc): Tibetan-Yi Corridor (TYC) scripts are visually closer to Indus than proto-cuneiform (PC) or proto-Elamite (PE) are.

**Seen before writing this:** one montage of 8 random glyphs per dataset. Indus images are bold, thick-stroked drawings. PC and PE are thin-line drawings. Standard Yi is a bold font and Ba-Shu has bold filled shapes. This motivates the style hypothesis below.

## Data
The repo's `datasets/` folders, used as data only (no code from the repo is run):
- `indus` (715);
- PC (2,089) and PE (1,510);
- TYC: `ba-shu` 281, `naxi_dongba` 2121, `old_naxi` 2380, `standard_yi` 1138, `yi` 2922.

Equal samples of 280 glyphs per script, 20 resamples (seeded).

## Preprocessing
- Composite any alpha channel on white, then grayscale and Otsu binarise (ink = dark).
- Crop to the ink bounding box, pad to square, resize to 64x64.
- **RAW:** the binary image as given.
- **NORM (style-normalised):** morphological skeleton, dilated to a fixed 3 px stroke at 64 px.
- **THICK (planted style swap):** the skeleton dilated to the median Indus stroke width. Applied to PC and PE only.

## Embedding and similarity
- **Embedding:** 32x32 downsample, flatten, PCA to 50 dimensions. PCA is fit on a pooled, balanced sample (280 per script) separately for each condition.
- **Primary similarity:** for each Indus glyph, the maximum cosine similarity to the glyphs of script S, averaged over Indus glyphs (NN-sim).
- **Secondary similarity:** cosine similarity of centroids.
- **Style features:** ink fraction, stroke width (ink pixels / skeleton pixels), connected components.

## Tests
- **H1.** On RAW, is the nearest script to Indus a TYC script, and is TYC-pooled NN-sim above both PC and PE? This checks whether the claim's direction reproduces with a simple embedding.
- **H2.** Stroke width per script. Is Indus closer in stroke width to the TYC sets than to PC/PE?
- **H3.** On NORM, compute D = NN-sim(Indus, TYC pooled) - max(NN-sim(Indus, PC), NN-sim(Indus, PE)), with a 95% interval over the 20 resamples. Also give the rank of each single script.
- **H4.** RAW Indus against THICK PC/PE versus RAW TYC. If thickening PC/PE makes them closer to Indus than TYC, stroke rendering alone can produce the claimed ranking.
- **H5 base rate.** With 5 TYC scripts and 2 Bronze Age scripts, the chance under exchangeable scripts that the single closest script is a TYC one is 5/7 = 0.71. Pooled "TYC" also mixes five sets, so it is reported per script as well.

## Decision
- **The claim survives** if, on NORM, D's 95% interval is above 0 AND the closest single script is a TYC one.
- **The claim is broken** if D <= 0 on NORM, or if H4 reverses the ranking.
- Anything else is mixed.
