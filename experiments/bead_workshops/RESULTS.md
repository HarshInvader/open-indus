# Bead and lapidary workshop units, coded blind to signs (for meaning-claims rule 1)

## Verdict

**There are too few workshop units outside Chanhu-daro for a confirmatory test of "fish signs mean gems or beads".**

- **Primary set** (high or medium confidence, at sites not yet seen): 4 units holding 32 inscribed objects.
  - Mohenjo-daro: 3 units, 29 objects (28 of them seals).
  - Harappa: 1 square, 3 objects.
  - Lothal: 0 units.
- **Power with the primary set.** Assume a 30% fish base rate and a true 1.5x enrichment. A simple binomial test then has about 48% power. Allowing for clustering within units, which a density-matched null would face, power falls to about 21%. At a 2x enrichment the figures are 95% and 56%.
- **Adding low-confidence units** brings the total to 297 objects, but power under clustering is still only 48% at 1.5x. Most of those units are single unfinished items in find-rich squares, so any real enrichment would be diluted.
- **Mohenjo-daro has no bead factory in these sources.** Mackay (1938, OCR line 100859) says of the 1927-31 work: "no actual bead factory has as yet come to light". The Mohenjo-daro units here are a jeweller's hoard, a goldsmith's hoard and the "Palace" craft rooms, not bead workshops.

No test was run. Fish counts per unit were not looked at (see BLINDNESS.md).

## What was coded

Rules: `CODING_RULES.md`, written before coding. Script: `build_units.py`. Each piece of evidence carries an OCR quote, and the script checks that the quote appears at the cited line.

Per site, counting inscribed objects by object ID (not distinct texts), with signs never read:

| site | units coded | joinable target units | primary units (high+medium) | inscribed objects, primary | inscribed objects, all joinable | status |
|---|---|---|---|---|---|---|
| Mohenjo-daro | 9 | 7 | 3 | 29 (28 seals) | 73 | new |
| Harappa | 8 | 8 | 1 | 3 (1 seal) | 224 | new |
| Lothal | 0 | 0 | 0 | 0 | 0 | no source |
| Chanhu-daro | 8 | 8 | 5 | 28 (21 seals) | 35 | seen, not confirmatory |

The primary units:

| unit | craft | why | inscribed objects | listed finds |
|---|---|---|---|---|
| Mohenjo-daro `DKG. (S)\|1\|I` (Mackay's "Palace") | FAIENCE; LAPIDARY; SHELL | rule (b), three single finds: a jeweller's stand (DK 8994), a partly made shell bracelet (DK 6183), and kilns in room 33 that Mackay calls an artificer's workshop (use uncertain: glazing or crucible) | 26 (25 seals) | 58 |
| Mohenjo-daro `DKG. (N)\|15\|VI` | JEWELLER | hoard in room 28 with "pieces of lump silver ... ready for working" (Mackay 1938, OCR line ~102530) | 3 | 9 |
| Mohenjo-daro `HRB\|2\|VIII` | JEWELLER | goldsmith's hoard HR 4210-4212 with waste metal (Marshall 1931 vol. II, OCR line ~25910) | 0 | 0 |
| Harappa `J12` | SHELL (+ BEAD low) | Vats: "a shop or workshop"; shell cores and waste, inlay blanks, an unfinished steatite bead, unfinished seals | 3 | 32 |

Low-confidence units: Mohenjo-daro has 4 joinable (`1|VI` frit slab, `3|V` unfinished spacer, `18|-` unfinished shell ladle and bead half, `DKC|16|-` jeweller or dealer hoard) and 2 that cannot be joined (Trench E (M) House I hoard, VS House XXII shell segment). Harappa has 7 low squares. M10 has one unfinished agate bead; M11 and K8 one unfinished pendant each. I14 has the finished-jewellery hoard 8060. H14, I13, I14 and J13 hold the Trench IV furnaces, which Vats lists as possibly used for faience and carnelian etching among other uses.

`unit_density.csv` lists every resolvable unit at the three sites with its inscribed count and a listed-find count from the same report. This is the pool for a density-matched null:

| site | units | inscribed objects | listed finds |
|---|---|---|---|
| Mohenjo-daro | 236 | 921 | 772 |
| Harappa | 121 | 726 | 1,757 |
| Chanhu-daro | 21 | 61 | not counted |

## Planted power (sign-blind)

From `power.py`, results in `power.json`. Fish base rate p0 = 0.30, one-sided α = 0.05, planted enrichment of 1.5x or 2x.

- "binom" treats objects as independent texts.
- "clustered" gives each unit its own fish rate (beta distribution, intra-unit correlation 0.1) and calibrates the critical value under that clustered null.

| scenario | objects | units with texts | binom 1.5x | clustered 1.5x | binom 2x | clustered 2x |
|---|---|---|---|---|---|---|
| primary, new sites | 32 | 3 | 0.48 | 0.21 | 0.95 | 0.56 |
| all Mohenjo-daro joinable | 73 | 6 | 0.85 | 0.41 | 1.00 | 0.89 |
| all new incl. low | 297 | 12 | 1.00 | 0.48 | 1.00 | 0.96 |
| hypothetical 100 texts in 10 units | 100 | 10 | 0.91 | 0.68 | 1.00 | 1.00 |
| hypothetical 200 texts in 20 units | 200 | 20 | 1.00 | 0.93 | 1.00 | 1.00 |

With independent texts, 80% power needs about 67 texts at 1.5x and about 17 at 2x. With clustering, roughly 20 units of about 10 texts each are needed at 1.5x. The real figures are worse than the table for three reasons:

- Objects are not distinct texts. Repeated tablets and impressions must be merged, which can only be done when the test is run.
- One unit, the Palace, holds 26 of the 29 Mohenjo-daro primary objects, so the primary test is close to n = 1 unit.
- The low-confidence units are mostly find-rich squares with one unfinished item. Harappa M11 alone has 143 objects. If only a third of their objects relate to the workshop, a 1.5x effect shrinks to about 1.17x.

## Caveats and judgement calls

- **Jewellers are not bead makers.** Two of the three Mohenjo-daro primary units are precious-metal hoards. They fit "gems or beads" only loosely. A test restricted to BEAD and LAPIDARY evidence would have no primary unit at Mohenjo-daro.
- **The Palace unit (`DKG. (S)|1|I`) is the weakest link.** Its medium rating rests on two single finds plus kilns of unknown use. The shell bracelet was assigned to House I after counts were printed, based on Mackay's own list headings (BLINDNESS.md). Treat it as a sensitivity case, not the anchor.
- **Listed finds are published finds.** Mackay lists only illustrated objects, Vats lists notable items, and Marshall's house citations are found by regex on noisy OCR. `HRB|2|VIII` gets 0 listed finds because its OCR reads "House \TII". Use the proxy for ranking, not as an exact density.
- **Unit keys copy `experiments/assemblage/test.py`.** Corpus records with a block but no house are not counted at house level. `n_inscribed_block` gives the block total.
- **Found in passing:** `experiments/assemblage/build_coding.py` starts Mackay's object list at OCR line 11859. The list actually starts at 11503 (Block 1, House I), so Block 1 craft entries were missed there. That is another agent's folder, so it is not fixed here.

## What would make the test feasible

1. **Harappa HARP trenches.** The corpus gives trench-level findspots for about 540 inscribed objects: E Trench 11 (310 records), Trench 54 (120), Trench 10W/11 (111). Kenoyer and Vidale's published craft-area work (stone bead, steatite and faience working in Mound E/ET) could code these trenches. This is the only route to the 20-unit scale. Coding by trench would also need a trench-level null.
2. **Mohenjo-daro.** Three sources would add units:
   - Marshall 1931 vol. I (the HR, VS and DK chapters) and the Mackay 1938 vol. II plate lists, for findspots of the unfinished beads DK 1421, DK 2936, SD 254, SD 2325 and HR 2399, and of the ten on Mackay's plates;
   - the surface-survey craft maps of Pracchia, Tosi and Vidale (1985);
   - Vidale's (1989) work on specialised production sites.
3. **Lothal.** The bead factory and the lapidary's house are described in Rao 1979/1985, which is not in the repo. Corpus Lothal objects carry only SRG register numbers (102 of 202 have none), so a locus-to-register table is also needed.

## Hypotheses

| id | hypothesis | result | verdict |
|---|---|---|---|
| bw_c1 | enough sign-blind workshop units outside Chanhu-daro for an 80%-power test of a 1.5x fish enrichment | 4 primary units, 32 objects; power 0.21-0.48 | not met (data limit) |

## Files

- `CODING_RULES.md`: the rules, written first
- `build_units.py`: the coding, quote-verified, with sign-blind counts
- `bead_evidence.csv`: 39 evidence rows
- `bead_units.csv`: 25 units
- `unit_density.csv`: 378 units with inscribed and listed-find counts
- `power.py`, `power.json`: the planted-power estimate
- `results.json`: per-site summary
- `BLINDNESS.md`: what was and was not looked at
- Hashes are in `docs/prereg/HASHES.txt` under the tag `bead_workshops_coding`.
- Date note: CODING_RULES.md says "2026-11-21" (the session's local date). The UTC hash timestamp, 2026-11-20T22:13:50Z, is authoritative. The file was not edited after hashing.
