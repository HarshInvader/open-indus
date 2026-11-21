# Uniformity paper, step 1: Linear B, name-free references, within-city floor

Prereg: `docs/prereg/uniformity_paper_step1.md`, hashed with `s1.py` and `build.py` in `docs/prereg/HASHES.txt` (tag `uniformity_paper_step1`, 2026-11-21T15:29:22Z) before any condition was scored. Every condition ran through the benchmark's own `clean()` + `draw_n()` + `score()` the way `redteam_uniformity/rt.py` calls them. There are 30 draws per condition. Numbers are in `table.md` and `results.json`; per-draw values are in `draws.jsonl`. Ledger: `ledger_rows.csv`.

## Verdicts

**A. Linear B supports the claim.** Knossos and Pylos tablet lines separate at **0.904** at Indus size and length mix. They still separate at **0.780** with series balanced and **0.793** with every name removed. Mohenjo-daro vs Harappa is 0.553 in this run. A genre-matched administrative script from two palaces carries its site; Indus seals do not.

**B. The "Indus seals just don't carry names" objection is answered, 2 of 3.**
- Latin with all proper nouns removed separates at **0.719**.
- Linear B with only listed common words, ideograms and numerals separates at **0.793**.
- Ur III Umma vs Girsu, name-free with one legend per owner, gives 0.618. Its pool is only 76 per side, and the power gate is 43%, so that case is **underpowered**, not a pass and not a failure. Without the owner de-dup it is 0.695 at 197 per side.
- One plain warning: Latin with names removed **and** the frame removed falls to **0.564**, which is at Indus level. Once names and the commonest words are gone, a label corpus can look as flat as Indus.

**How much naming Indus could hold.** Planted city-specific names are found 80% of the time only when **half the seals** carry one. The observed 0.55 is still compatible with a local name on up to **30%** of seals (one-sign names) or **20%** (two-sign names spelt from shared signs). So the Indus null rules out names on most seals. It does not rule out a minority of seals carrying local names.

**C. 0.55 is a same-city number.**
- Two areas of one city, Mohenjo-daro DK vs HR + VS, give **0.547**.
- Mohenjo-daro vs Harappa at the same size, from the same editor (M77), gives **0.514**.
- Between minus within = −0.033. By the frozen rule that means **no city signal above the within-city floor**.
- Deep vs shallow within DK gives 0.457.
- Harappa mound F vs AB gives 0.544, but at 48 per side it is underpowered (gate 47%).

## Prediction table

| id | prediction | result | verdict |
|---|---|---|---|
| P-A1 | A1 Knossos vs Pylos whole ≥ 0.65 | 0.904 (gate 100%) | supported |
| P-A2 | A8 series-balanced ≥ 0.65 | 0.780 (gate 100%) | supported |
| P-A3 | A7 strict name-free ≥ 0.65 | 0.793 (gate 93%) | supported |
| P-B1 | B2 Ur III Umma vs Girsu name-free + owner ≥ 0.65 | 0.618 (gate 43%) | **not met; underpowered** |
| P-B2 | B5 Latin name-free ≥ 0.60 | 0.719 (gate 100%) | supported |
| P-B3 | one-sign names: 80% power by r ≤ 0.3; spelt names by r ≤ 0.5 | 0.5 for both | **refuted** for one-sign names; supported for spelt |
| P-C1 | C1 within 0.45-0.60 | 0.547 | supported |
| P-C2 | C2 within 0.45-0.60 | 0.457 | supported (just) |
| P-C3 | C3 below its null q95 | 0.544 < 0.627 | supported, underpowered |

## Numbers (median AUC over 30 draws; Indus length mix)

### A. Linear B, Knossos vs Pylos (DAMOS)

| condition | per side | median | 95% of draws | null q95 |
|---|---|---|---|---|
| **A1 whole** | 227 | **0.904** | 0.888-0.918 | 0.562 |
| A2 frame removed | 227 | 0.948 | 0.938-0.959 | 0.540 |
| A3 syllabic words only | 227 | 0.971 | 0.964-0.979 | 0.549 |
| A4 ideograms + measures only | 75 | 0.731 | 0.703-0.753 | 0.595 |
| A5 tagged names removed | 227 | 0.893 | 0.881-0.904 | 0.552 |
| A6 syllabic, tagged names removed | 227 | 0.971 | 0.961-0.979 | 0.566 |
| **A7 strict name-free** (common words + ideograms + NUM) | 115 | **0.793** | 0.766-0.825 | 0.569 |
| **A8 series-balanced** | 116 | **0.780** | 0.748-0.807 | 0.598 |
| A9 words split into syllabic signs | 227 | 0.859 | 0.847-0.873 | 0.561 |
| A10 strict name-free + series-balanced | 75 | 0.684 | 0.638-0.725 | 0.596 |
| *Indus ICIT MD vs Harappa (C7, rerun)* | 227 | *0.553* | 0.506-0.589 | 0.547 |
| *Indus at 100 per side (rt)* | 100 | *0.520* | | |

- About a third of the Knossos-Pylos gap is series mix. Balancing series letters takes A1 from 0.90 to 0.78, and the strict name-free version from 0.79 to 0.68. Both stay well above Indus at similar sizes (0.52 at 100 per side).
- Splitting words into syllabic signs, so the unit matches Indus signs, still gives 0.86.
- The highest numbers come from syllabic words (0.97), not ideograms (0.73). Most of the site signal is in the words, and removing tagged names barely moves it (0.893). The name lists tag only 15-20% of syllabic tokens, though, so A5 and A6 keep most personal names. A7 and A10 are the true name-free versions.
- **Proto-Elamite was not run.** Only 22 transliterated tablets have a secure non-Susa findspot (Anšan), under the pre-registered bar of 40.

### B. Name-free references

| condition | per side | median | 95% of draws | null q95 | gate |
|---|---|---|---|---|---|
| B1 Ur III Umma vs Girsu, name-free | 197 | 0.695 | 0.676-0.721 | 0.576 | |
| **B2 Umma vs Girsu, name-free + owner de-dup** | 76 | **0.618** | 0.594-0.657 | 0.576 | **43%** |
| B3 B2 + frame removed | 56 | 0.722 | 0.693-0.768 | 0.620 | |
| B1 Puzriš-Dagan vs Nippur, name-free | 105 | 0.778 | 0.768-0.792 | 0.562 | |
| B2 PD vs Nippur, name-free + owner | 40 | 0.775 | 0.741-0.813 | 0.632 | 27% |
| B3 PD vs Nippur, + frame | 25 | 0.730 | 0.678-0.776 | 0.626 | |
| B4 Latin, transcription tokens, nothing removed | 227 | 0.715 | 0.685-0.737 | 0.551 | |
| **B5 Latin name-free** | 174 | **0.719** | 0.694-0.749 | 0.568 | 100% |
| B6 Latin name-free, military labels dropped | 105 | 0.664 | 0.633-0.683 | 0.587 | |
| B7 Latin name-free + frame removed | 132 | **0.564** | 0.534-0.609 | 0.598 | |

- B4 reproduces the benchmark's Latin whole number (0.713 at 311 per side; 0.668 at 227 in rt). So the re-tokenising from the transcription is sound: 1,585 of 1,596 labels give the same tokens as the diplomatic text.
- Ur III loses most legends once names go. Many legends become generic strings ("dub-sar dumu") that occur at both cities, and `clean()` drops them. The pools shrink to 76 and 40 per side, which is too few for the gate. The Ur III name-free answer is underpowered, not negative. Every Ur III name-free number is above its own null q95, and 4 of 6 exceed 0.69.
- Latin name-free keeps its full separation (0.719 vs 0.715 whole). Removing the frame as well brings it to 0.564. Most of what separates the two provinces without names is common formula words (legion and unit words, F(ecit), OF(ficina)), which the frame takes.

**Reverse power test** (Indus ICIT pool, 227 per side, labels permuted, a share r of seals given a local name from a 100-name stock per site):

| share of seals with a local name | 0.1 | 0.2 | 0.3 | 0.5 | 0.75 | 1.0 |
|---|---|---|---|---|---|---|
| one new sign per name: median / detected | 0.535 / 0% | 0.568 / 0% | 0.613 / 17% | 0.706 / 97% | 0.834 / 100% | 0.929 / 100% |
| two shared signs per name: median / detected | 0.525 / 0% | 0.579 / 3% | 0.639 / 30% | 0.731 / 97% | 0.861 / 100% | 0.946 / 100% |

- Detection means AUC ≥ max(0.65, null q95).
- The 80% line is at 50% of seals for both forms.
- The observed 0.553 lies inside the planted draw range up to 30% (one-sign) and 20% (two-sign).

### C. Within-city floor (M77 seals)

| condition | per side | median | 95% of draws | null q95 | gate |
|---|---|---|---|---|---|
| **C1 Mohenjo-daro DK vs HR + VS** | 169 | **0.547** | 0.488-0.585 | 0.587 | 100% |
| C4 Mohenjo-daro vs Harappa (M77), same size | 169 | 0.514 | 0.451-0.580 | 0.579 | |
| **C2 DK deep vs shallow (≤ −11 ft vs above)** | 204 | **0.457** | 0.411-0.493 | 0.568 | 100% |
| C8 Mohenjo-daro vs Harappa at 204 | 204 | failed: Harappa has 200 | | | |
| *X_C2 deep vs shallow at 200 (exploratory)* | 200 | *0.464* | 0.425-0.491 | 0.568 | |
| *X_C8 Mohenjo-daro vs Harappa at 200 (exploratory)* | 200 | *0.553* | 0.472-0.591 | 0.558 | |
| C3 Harappa mound F vs AB | 48 | 0.544 | 0.444-0.618 | 0.627 | 47% |
| C5 Mohenjo-daro vs Harappa at 48 | 48 | 0.486 | 0.387-0.582 | 0.582 | |
| C6 ICIT Mohenjo-daro DK vs HR + VS (CISI field nos.) | 90 | 0.517 | 0.458-0.627 | 0.580 | |
| C7 ICIT Mohenjo-daro vs Harappa | 227 | 0.553 | 0.506-0.589 | 0.547 | 100% |

- **Primary comparison:** Δ = C4 − C1 = −0.033. Two parts of one city differ as much as two cities 600 km apart.
- **Depth.** The depth split sits below 0.5 (0.46). That is a known small bias of the pipeline when both sides draw from one pool with shared strings removed. Read it as "no signal". Against the exploratory matched between-city value (0.553 at 200), the depth floor is 0.09 lower. So this floor is lower than the area floor, and against it the city pair looks slightly separated. The area floor is the pre-registered primary, and it shows no gap.
- The ICIT version of the area split (C6, 0.517 at 90 per side) agrees.

## Deviations

1. **C8 failed by construction.** The prereg borrowed C2's size (204), but M77 Harappa has only 200 seal texts after cleaning. Both were rerun at 200 per side in `s1_extra.py` (`draws_extra.jsonl`, `results_extra.json`). These rows are **exploratory**.
2. Nothing else changed after scoring. Thresholds, conditions and code are as hashed.
3. Compute lock. All runs went through `board/run.sh` (repo lock `board/compute.lock`, `taskpolicy -b nice -n 20`, one process). The shared marker `open-citizen-science/.local/compute.lock.indus` was held by the stamp_detector agent throughout. Its only live process was a network image harvest, so this light single-process job ran alongside it.

## Caveats

- **Linear B is a weaker match than it looks.** These are palace inventories, not seals. Lines come from dossiers kept by different scribes, and the two archives differ in date by up to two centuries (Knossos LM II-IIIA, Pylos LH IIIB end). Series balancing matches subject class only by Bennett letter. DAMOS editions may also differ in notation between sites, for example sex markers on ideograms (OVIS:m). The ideogram-only row (0.73 at 75 per side) is the one most exposed to that.
- **Name tags are partial.** Linear B name lists come from forms with a known Greek reading (471 names), so most personal names are untagged; A7 and A10 avoid this by keeping only listed common words. Latin proper nouns come from editors' capitals: AVG counts as a name, and a few gods' names count as common.
- **Ur III name-free is underpowered** at 76 and 40 per side. It needs a larger seal corpus, for example CDLI Ur III seals beyond ORACC.
- **Within-city floors mix area with excavator and date.** DK was dug by Mackay; HR and VS by Marshall's teams. M77 loci were checked against field-number prefixes: loci 31-34 are 616 DK field numbers and none from any other area.
- `clean()` drops strings found at both sides. That removes shared material from every condition alike, Indus included.
- 30 draws per condition. Harappa's side of each Indus draw is nearly fixed (200-232 texts), so draw ranges understate the uncertainty.

## What this means for the paper

- The cleanest sentence is now: **seal texts from Mohenjo-daro and Harappa differ no more than seals from two areas of Mohenjo-daro (0.51 vs 0.55), while readable administrative and label corpora carry their site even with names removed (Linear B 0.79, Latin 0.72).**
- The names objection is mostly answered. Names are not the only site signal in Linear B or Latin. But Latin without names and without its frame words falls to Indus level (0.56), and Ur III name-free is underpowered. The paper should say that the references' remaining site signal sits largely in common formula words.
- The power line limits what can be claimed. Up to about a fifth to a third of Indus seals could carry a city-specific name and still give 0.55.

## Files

- `build.py`: pools; `data/*.jsonl` are gitignored (third-party text); `sizes.json` and `sizes.log` hold the counts.
- `fetch.py`: DAMOS re-fetch (not run; the copy on disk was used).
- `s1.py` (`sizes`, `run`, `report`), `s1_extra.py` (exploratory).
- `draws.jsonl`, `draws_extra.jsonl`, `results.json`, `results_extra.json`, `table.md`, `ledger_rows.csv`, `run.log`.
