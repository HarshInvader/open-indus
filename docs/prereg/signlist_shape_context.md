# Pre-registration: sign list from shape plus context (400 vs 700 signs)

Agent N4, board task under M5. Folder `experiments/signlist_shape/`. Written and hashed before any outcome below was computed. Code frozen with it: `experiments/signlist_shape/sl.py` (hash appended alongside). Run scripts written after hashing may only wire these functions to the data as described here.

## Question

How many distinct signs does the Indus script have: about 400 (Mahadevan 417, Parpola ~386) or about 700 (Wells ~676; ICIT uses 712 W labels)? Combine what signs look like (Mahadevan's drawings) with how they are used (training texts only), and let held-out texts decide.

## Closed work this must not repeat

- `experiments/signlist_robustness`: 12 lists compared for whether headline findings survive. It did not ask which list the texts prefer. Its image lists (img_hi/mid/lo) used blurred silhouettes only, no context.
- NEGATIVE_ATLAS 7.7 (allographs by perplexity): perplexity-chosen merges beat random merges, but context-matched merges of signs that do NOT look alike did as well. So a context-only control is mandatory here, and a merge only counts as an allograph proposal if it beats that control.

## Data

- Indus training: distinct M77 dev texts of `dev_heldout()` (v2 split), break-free runs (`runs()`), 1,699 texts. Test: the 571 v2 held-out texts, runs. Held-out is used only for the final scores of frozen partitions.
- ICIT (W numbering): distinct texts, family split re-implemented exactly as `signlist_robustness/harness.py: icit_split()` (edit-1 clusters, 75/25, seed 0).
- Mahadevan<->Wells bridge `sources/shaunmortal_indus/data/bridge_WM.json`.
- Known-answer scripts (local, already in repo): proto-cuneiform (PC) lines `experiments/protocuneiform/pc_lines.json` with Englund sign images `raw/pc_cdli/archsigns/*.jpg`; Proto-Elamite (PE) lines `pe_lines.json` with Pandey glyphs `pe_signs/*.png`. Variant labels: CDLI `NAME~x` (PC `NUN~a`, `NUN~b`; PE `M321~j`). Truth: two signs are the same sign iff their names agree after stripping the `~...` suffix (PE: also strip; PC/PE `@`-modified and compound `|...|`/`+` signs are their own base). Numerals (`n(N..)`), `,`, `X`, `...` are dropped from sequences.

## Method (frozen)

1. **Shape.** Ink mask -> first exemplar (PC only) -> size-normalised 64x64. Two distances: HOG cosine (16-px blocks, 9 bins) and symmetric mean chamfer distance. Shape similarity S_shape = mean of the two pair-percentile ranks (1 = most alike pair). No rotations (sign lists already orient signs).
2. **Context.** PPMI vectors of left and right neighbours (with text boundaries), alpha 0.75, training texts only. S_ctx = pair-percentile rank of cosine similarity.
3. **Candidates** (mode `both`): pair (i, j) with j among i's 5 nearest by shape, ranked by S_shape + S_ctx. Control modes: `ctx` (5 nearest by context, ranked by S_ctx) and `shape` (ranked by S_shape alone).
4. **Language model.** Class-based interpolated Kneser-Ney trigram (D = 0.75) over the classes of a partition, times emission P(sign | class) (add-0.5). Every partition is scored on the same fine sign tokens incl. end-of-text; signs unseen in training are context only, not scored. So lists of different sizes are compared on identical tokens.
5. **Greedy merge.** One pass over the top 300 candidates; accept a merge if 5-fold CV log-likelihood on the TRAINING texts rises. Output: accepted merges and the resulting partition.
6. **Merge path for list size.** Apply mode-`both` candidates in rank order (all of them, not just accepted), recording the partition every 10 merges. Held-out log-likelihood is computed at each point; preferred size = argmax; uncertainty = 1,000 bootstrap resamples of held-out texts (argmax per resample, 95% interval). The same is done with the greedy-accepted partitions.

## Tests

**K1 known answer, real variants.** PC and PE, each at Indus size (2,300 distinct training lines, 700 held-out, seed 0) and at full size (all distinct lines, 80/20). Pool = signs with an image and >= 1 training token. Report pairwise precision/recall of the greedy partition against truth (pairs within pool), the same for the `ctx` and `shape` controls, and the expected precision of a random merge (share of true pairs among candidates). Also: held-out LL of the TRUE merge (all variants -> base) minus the fine list, to calibrate whether likelihood even prefers merging true variants, and the merge-path argmax size vs the true base count.

**K2 known answer, planted allographs in Indus.** In the dev corpus pick 30 signs with >= 20 dev tokens (seeded draw); each token of a picked sign becomes X.a or X.b at random (free variation); X.b's drawing = X's drawing under a random affine (rotation +-10 deg, axis scales 0.85-1.15, shear +-0.15) plus 1-px dilation or erosion. Run the procedure. Recall = planted pairs re-merged / 30; precision = re-merged planted pairs / accepted merges touching any planted variant. 3 seeds. This is the power figure at our sample size.

Pass bar for using the method on Indus: K2 recall >= 0.6 with precision >= 0.8 (mean over seeds). K1 is reported as is (real variants are not all free allographs, so its recall ceiling is unknown); K1 precision of `both` must exceed the random-merge rate and the `ctx` control's precision, otherwise "shape + context" adds nothing over context alone.

**I1 Indus merges.** Greedy (`both`) on dev. Held-out LL per token of: M77 (417 labels), greedy `both`, greedy `ctx`, greedy `shape`, and the signlist_robustness lists img_hi/img_mid/img_lo, lump_all, parpola, lump_fish, lump_numerals, lump_jar_man (read from its variants.json, not edited). Differences vs M77 with 95% bootstrap CI over held-out texts. A merge list is "preferred" over M77 if the CI of the difference is above 0. The shape+context list is an allograph proposal only if it also beats the `ctx` control's held-out LL (CI above 0) or, failing that, is reported as "no better than context alone" (as in atlas 7.7).

**I2 Indus splits (the 700 side).** ICIT: compare the fine W list with the list lumped by the bridge (W signs sharing an M sign join one class; unbridged W stay single). Held-out ICIT LL per token, bootstrap CI. Per bridge component with >= 2 W signs: held-out LL with only that component split (others lumped) minus all-lumped; count components where the split helps (CI above 0) and give the W-list size the held-out texts prefer (all lumped + helpful splits). Context-only: no W drawings exist locally.

**I3 list size.** The merge-path argmax on M77 (from 417 down) with bootstrap interval, and the I2 preferred W size. Answer phrased as: the held-out texts prefer N labels (95% interval a-b); a value near 400 or near 700 or neither.

**H1 headline dependence.** Re-run the 9 signlist_robustness headline tests (its harness, imported read-only, outputs written to my folder) under the greedy `both` partition. Report any test that changes verdict vs M77.

**Contact sheet.** Top 30 proposed merges (greedy `both`, ranked by accepted order / score) with drawings side by side, `contact_top30.png`.

## Caveats stated in advance

- Held-out likelihood is a bias-variance criterion: with ~7,600 training tokens it may favour merging rare signs even when they are distinct. K1's true-merge calibration tells us how far to trust it. A preferred size is a statement about what our corpus can support, not proof of the writers' inventory.
- Mahadevan's drawings are normalised; real allographs may look less alike on objects than in his list.
- 1 confirmatory analysis per item above; I count tests and report them all. Nothing here is tuned on held-out texts.
