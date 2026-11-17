# core_genre: red team of naming_sim, and what the Indus core statistics resemble

2026-11-15. Part A is an exploratory red team. Part B was pre-registered in `docs/prereg/core_genre.md` and hash-frozen before Indus was scored against any non-name genre. Statistics, distance and scales are naming_sim's own (`naming_sim/stats.py`, `realcmp_scales.json`), imported unchanged. Unit = distinct type. Held-out = `dev_heldout(version=2)`. Ledger rows: `cg_*`.

## Findings first

1. **The naming_sim outlier claim is WEAKENED.** It holds only under two conditions together: (a) cores defined by the functional grammar, and (b) name elements kept at their own inventory of thousands. Relax either one and the gap shrinks to the normal range.
   - **Inventory (A1).** Real names were rewritten with 286 signs: each element was mapped at random to a sign, with the Indus Zipf profile. This models homography, the way a logographic or rebus script with about 300 signs writes a stock of thousands of name elements. Under it, the two "robust" gaps disappear:
     - Sanskrit: pol_ex 0.16 and both_pos 0.71 (Indus 0.14 and 0.71).
     - Chinese given names: 0.12 and 0.73.
     - The gaps survive only if signs keep their slot identity (slot-preserving merge: pol_ex 0.41-0.97). naming_sim's generator analysis had assumed exactly this.
   - **Core definition (A2).** A grammar-free core was built by deleting numerals and positional frame signs (≥10 uses, ≥50% initial or final, derived on dev). Indus standalone then falls from 0.91 to 0.62 (held-out 0.85 to 0.63).
     - The same stripping rule applied to real name lists cuts their polarization sharply: Ur III 0.71 to 0.08, Chinese full 0.84 to 0.15.
     - So part of the low Indus polarization is a selection effect. Any slot-bound sign is classed as frame and removed before the core is measured.
   - **Combined.** Indus is compared with names under the same treatment on both sides, with the thresholds re-derived among the transformed name lists:
     - grammar-free cores plus merge: d_NN 0.92 on dev and 0.58 on held-out, against a median of 1.06 and a max of 1.73. That is **typical**.
     - merge alone: 0.81 and 0.87, against a median of 0.72 and a max of 1.34. That is **peripheral**.
     - Only the frozen setup gives "outlier" (1.69 on dev).
   - **Syllables (A3): this attack FAILS.** Names re-segmented into syllables have standalone 0.00-0.08, so syllable-level signs would *lower* standalone, not raise it. The high Indus standalone still argues for word signs.
   - **Numerals (A4) survive, but they say "label", not "not-a-name".** 41% of distinct dev texts carry a numeral (seals 43%; held-out 39%), against 0.1-0.6% of Ur III, OB and OAkk seal legends. But commodity and label genres carry numerals at the Indus rate: cuneiform tags 38%, Linear B entry lines 50%, Latin stamps/labels 22%, Rietstap blazons 63% (charge counts).
   - **Metric note.** naming_sim's scales come from the spread among name lists. They are tiny for standalone (0.044) and both_orders (0.015), so those two statistics dominate every distance. That magnifies inventory artefacts.
2. **Part B: Indus core statistics do not single out any genre, and personal names are not excluded** (pre-registered R1-R3). The comparison covered 29 real systems: 13 non-name writing genres, 5 codes and 11 name lists.
   - R1: Indus is **not an outlier** once non-name genres are included. It is peripheral in raw (d_NN 1.42 on dev, 2.28 on held-out) and typical in merge (0.88, 0.84) and sym (0.71, 0.30).
   - R2: genre vs name is **undecided**. The bootstrap share of resamples where the best genre beats the best name:

     | variant | dev | held-out |
     |---|---|---|
     | raw | 0.75 | 1.00 |
     | merge | 0.00 | 0.00 |
     | sym | 0.02 | 1.00 |

   - R3: **no single genre.** The nearest system changes with the variant and the split. Most of the nearest systems are small (cuneiform tags n = 120, Egyptian names 171, Plains 101, Linear A 228), where Indus statistics are noisy.
   - R4 (descriptive): the 5 codes (khipu, chess, chords, emoji, METAR) are **never** nearer than names (0 of 6 cells). Indus cores are unlike those codes.
   - **Lead (not pre-registered as decisive).** In the symmetric grammar-free variant, the nearest large system on both splits is **Linear B entry lines**: d = 1.15 on dev (tied with Plains, CI overlap) and 0.30 on held-out, the closest match in the whole study. Next come proto-cuneiform entries, Latin labels and Proto-Elamite entries.
     - Held-out Indus vs Linear B entries: standalone 0.61 vs 0.59, pol_ex 0.089 vs 0.090, both_pos 0.84 vs 0.77.
     - Administrative entry lines mix personal names, place names, offices and commodity words drawn from one stock. That fits the naming_sim reading (a), "one shared vocabulary". But in the merge variant the nearest systems are names (Sangam, Egyptian), so this stays a lead.

**Bottom line.** "Indus cores match no personal-naming system" should be demoted from a finding to a construct-dependent observation. Once a ~300-sign script writes names (homography) and a grammar-free core is used, Indus core statistics fall inside the range of both personal names and administrative label genres. These statistics cannot tell names from labels at Indus inventory size. The numeral rate is the one feature that still separates Indus from personal seal legends, and it puts Indus with tags, commodity entries and labels.

## Part A details (`partA_redteam.py`, `partA_dist.py`, `partA_calib.py`)

Indus grammar cores: dev 800 types, 286 signs, 1,812 tokens. len1 0.256, standalone 0.907, both_orders 0.063, hfi 0.454, pol_ex 0.138, both_pos 0.714.

| variant (dev, n = min(800, list), 30 subsamples) | standalone | pol_ex | both_pos |
|---|---|---|---|
| Indus grammar cores | 0.91 | 0.14 | 0.71 |
| names raw (range of 11) | 0.00-0.13 | 0.30-1.00 | 0.00-0.60 |
| names truncated to their top-286 elements | 0.00-0.16 | 0.26-1.00 | 0.00-0.63 |
| names merged to 286 signs (Indus profile) | 0.00-0.68 | 0.12-0.51 | 0.36-0.73 |
| names merged within slot groups | 0.00-0.42 | 0.41-1.00 | 0.00-0.53 |
| Sanskrit merged | 0.68 | 0.16 | 0.71 |
| Sangam merged | 0.61 | 0.27 | 0.66 |
| Indus whole texts (no grammar) | 0.19 | 0.50 | 0.57 |
| Indus edge-stripped segments (no grammar) | 0.62 (ho 0.63) | 0.24 (ho 0.11) | 0.72 (ho 0.82) |
| Indus top-10-stripped segments | 0.70 (ho 0.62) | 0.22 (ho 0.17) | 0.68 (ho 0.73) |
| names as syllables (5 lists) | 0.00-0.08 | 0.29-1.00 | 0.00-0.59 |

Distance labels (naming_sim thresholds 0.87 and 1.21 unless re-derived):

| setup | d_NN dev | d_NN held-out | verdict |
|---|---|---|---|
| frozen (grammar cores, raw names) | 1.69 | 2.68 | outlier |
| truncation | 1.69 | 2.68 | outlier |
| slot-preserving merge | 1.57 | 1.83 | outlier |
| merge (re-derived median 0.72, max 1.34) | 0.81 | 0.87 | peripheral |
| sym: edge segments both sides + merge (re-derived 1.06 / 1.73) | 0.92 | 0.58 | typical |

Numerals: share of distinct units with any numeral.

| corpus | share |
|---|---|
| Indus dev, all texts (n = 1,699) | 0.41 |
| Indus dev, seals | 0.43 |
| Indus dev, sealings | 0.31 |
| Indus held-out | 0.39 |
| Ur III seal legends | 0.001 |
| OB seal legends | 0.002 |
| Old Akkadian seal legends | 0.006 |
| cuneiform tags | 0.38 |
| Linear B entry lines | 0.50 |
| Linear A labels | 0.06 |
| Latin stamps/labels | 0.22 |
| Egyptian verbless phrases | 0.04 |
| Rietstap blazons (number words) | 0.63 |

## Part B details (`genres.py`, `partB.py`)

- **Systems.** Units are distinct, with numerals removed and 1-8 elements. Systems:
  - Ur III seal legends (words; signs; title skeletons);
  - OB seal legends (signs);
  - Egyptian verbless phrases and no-proper-noun title strings (TLA lemmas);
  - Rietstap blazons;
  - Linear B entry lines;
  - Proto-Elamite and proto-cuneiform entry lines;
  - cuneiform tags;
  - Latin stamps/labels;
  - Linear A labels;
  - 5 codes;
  - 11 name lists.
- **Not obtained:** Chinese clan emblems, merchants' or masons' marks, Pictish symbol pairs, product marks (no machine-readable corpus). Hawaii cattle brands are images only.
- **Calibration** (reference systems only, before scoring Indus): the group of a system's nearest neighbour matches its own group (genre, code or name) in 19, 21 and 21 of 29 systems (raw, merge, sym). Chance is about 10, so p = 0.003, 0.0002 and 0.0002. The statistics carry some genre information.

| variant, split | label | d_NN | nearest (CI-tied) | nearest with n ≥ 400 | best genre < best name |
|---|---|---|---|---|---|
| raw, dev | peripheral | 1.42 | cun_tag (Egyptian names) | Ur III title skeletons 4.12 | 0.75 |
| raw, held-out | peripheral | 2.28 | Linear A labels | Ur III title skeletons 5.88 | 1.00 |
| merge, dev | typical | 0.88 | Sangam names | Sangam 0.88 | 0.00 |
| merge, held-out | typical | 0.84 | Egyptian names | Sanskrit 2.90 | 0.00 |
| sym, dev | typical | 0.71 | Plains names (Linear B entries) | Linear B entries 1.15 | 0.02 |
| sym, held-out | typical | 0.30 | Linear B entries | Linear B entries 0.30 | 1.00 |

With pooled scales (sensitivity check), the nearest systems are cun_tag, Sangam and Egyptian phrases on dev, and Linear A, Sanskrit and Latin labels on held-out. Different again.

## Hypotheses tested

| id | hypothesis | verdict |
|---|---|---|
| A1 | the pol_ex/both_pos gap survives at the Indus inventory | refuted under homography; supported only if slot identity is kept |
| A2 | the core statistics do not depend on the grammar's core definition | refuted (standalone 0.91 to 0.62; polarization partly a selection effect) |
| A3 | Indus standalone is inflated by syllable-level signs | refuted |
| A4 | the numeral rate separates Indus from personal-name legends | supported, but it matches commodity and label genres |
| A | naming_sim "outlier" verdict | **weakened** |
| B-R1 | Indus lies outside all 29 reference systems | refuted (typical or peripheral) |
| B-R2 | non-name genres are nearer than names | undecided |
| B-R3 | one named genre matches | no single genre (lead: Linear B entry lines) |
| B-R4 | codes are nearer than names | refuted (0 of 6 cells) |

## Caveats

- Random merging is one model of a ~300-sign script. It also makes systems more alike, which is why the thresholds were re-derived for the merged lists.
- The edge-stripping rule is crude. It removes slot-bound themes from names, such as Germanic second themes, which is itself part of the point.
- Small systems (n of 100-230) look nearest because statistics converge at small n. This was flagged in naming_sim too.
- Genre tokenization is mixed: words, signs and lemmas, as in the sources.
- Linear B entry lines are administrative, not seal legends. The lead fits a "labels from one stock" reading. It does not identify the genre.

## Next experiments

1. Pre-register a test of the Linear B lead on its own: Indus vs Linear B, Proto-Elamite and proto-cuneiform entries under fresh core definitions. Add Linear B personnel/name tablets (prosopography) as a names-in-administration control.
2. Find a feature that survives homography. Candidates: numeral position relative to the core, or a recurrence profile over multiple impressions. The six naming_sim statistics cannot tell names from labels at ~300 signs.
3. Report naming_sim statistics with scales pooled over names, genres and codes, so that standalone and both_orders stop dominating.

## Files

- Code: `common.py`, `partA_redteam.py`, `partA_dist.py`, `partA_calib.py`, `genres.py`, `partB.py`, `make_results.py`.
- Outputs: `partA.json`, `partA_dist.json`, `partA_calib.json`, `partB_calib.json`, `partB_score.json`, `results.json`.
- Pre-registration: `docs/prereg/core_genre.md` (hashes in `docs/prereg/HASHES.txt`).
