# Sealing function: do title signs mark a role by what the sealing closed? (Fable plan 3, R5)

Code: `build_table.py` (builds `sealings.csv`, `sealings_m77.csv`), `analyze.py` (pre-registered tests), `explore_t347.py` (post hoc). Logs: `analyze.log`, `analyze_run1_bug.log` (first run, before amendment A1), `explore_t347.log`. Machine-readable: `results.json`. Pre-registration: `docs/prereg/sealing_function.md`. It was hashed before any title was cross-tabulated against a back type, and amendment A1 was hashed with the code (`docs/prereg/HASHES.txt`, tags `sealing_function`, `sealing_function_A1`). Ledger rows: `sf_*` in `docs/test_ledger.csv`.

## Conclusion first

1. **The door-peg test cannot be run on the sealings that exist. The verdict is untestable, not refuted.**
   - Usable reverse-type data exist for one site only: Lothal (Frenez & Tosi 2005, Table 1).
   - Of the 93 Lothal sealings, 9 were pressed over a peg on a wall (a door closure). Only 3 of those 9 carry a legible inscribed impression in ICIT:
     - L-206: the warehouse's most-used seal, W705-500-741-1-55-220-740-90. This is not a title block.
     - L-179: a jar-final fragment.
     - L-192: a one-sign fragment, W892.
   - Two more peg sealings (L-173, L-175) were stamped with uninscribed geometric seals, according to Frenez & Tosi's notes. The other four have no transcribed text.
   - None of the 3 inscribed door sealings carries a title sign (M347, M8, M336-M89, M249-M161). The other diagnostic sealings carry titles in 6 of 52 cases. The Holm p-value is 1.0 for every title.
   - Planted power to detect a 3x enrichment is 0.004-0.012.
   - At realistic title rates (4-10% of sealings), 80% power would need about 40-80 inscribed door sealings and roughly 300-600 other diagnostic sealings. That is more than every Indus sealing known. **The route is closed by sample size, not by evidence.**
2. **Titles are not more common on fixed closures than on containers** (S0, secondary). Fixed closures are pegs, lockers and structures. Any title appears on 1 of 19 fixed-closure sealings and 5 of 36 container sealings, a ratio of 0.38 (p = 0.94). The direction is the opposite of "storeroom authority". The test is weak (55 sealings).
3. **No countersignature pattern.**
   - **S1:** title-bearing impressions sit on multi-impression sealings somewhat more often than random placement would give. ICIT, all sites: 12 of 22 vs 7.5 expected, p = 0.024. That misses the pre-registered Bonferroni bar of 0.0167, and the M77 transcription does not replicate it (16 of 38 vs 14.1, p = 0.31).
   - **S2:** on sealings with two or more different seals, a title seal is not paired with a non-title seal more often than random pairing gives. ICIT: 12 mixed pairs of 41 vs 10.9, p = 0.40. M77: 21 of 74 vs 19.6, p = 0.38.
   - No title "always accompanies" a second seal.
4. **One post hoc lead fails to replicate.** In ICIT, W760 (read as M347) sits on multi-impression sealings in 4 of 5 distinct texts vs 1.25 expected (p = 0.006). In M77, which transcribes M347 more often, it is 5 of 12 vs 4.5 expected (p = 0.50). The ICIT signal is three Lothal and Dholavira sealings plus one Mohenjo-daro tag (M-1385) stamped three times by the same die. Also, the bridge maps W760 to either M347 or M358. Treat it as noise.

**Reading.** At Lothal, the only site where we know what was sealed, title signs do not sort by what the sealing closed. Seals that carry titles also do not act as countersignatures. This agrees with paragorth S-DARK-65 and S-DARK-71:
- co-sealing is incidental;
- the warehouse's most-used seal sat on 7 different kinds of fastening;
- back type predicts nothing once the 10 elephant-seal boxes are set aside.

Our administration t4 test found the same for commodity signs. What is new here: the role question had never been put to the title signs themselves, and the result has a power statement. **The Near Eastern sealing-function method cannot give an L2 anchor with the Indus sealing corpus that exists.** It needs new excavated door sealings, at a scale no single site has produced.

## Data (`sealings.csv`, 238 objects; `sealings_m77.csv`, 223 objects)

| item | n |
|---|---|
| ICIT sealing objects (TAG*), all sites | 238 (Lothal 97, Dholavira 69, Kalibangan 18, Mohenjo-daro 17, Harappa 15, 16 other sites) |
| with a recorded reverse type | 93 (all Lothal; Frenez & Tosi 2005) |
| reverse diagnostic | 75 (pottery 21, wooden boxes 15, structures 10, lockers 9, pegs-on-wall 9, parallel canes 5, sacks 2, 4 singletons) |
| diagnostic + legible inscribed impression | 55 (door 3) |
| multi-impression objects (Lothal: Frenez & Tosi count; elsewhere: ICIT faces) | 49 (Lothal 32, Dholavira 6, Kalibangan 4, Harappa 3, Mohenjo-daro 3, Rupar 1) |
| M77 sealing objects outside Harappa / with 2+ different sides | 223 / 51 |
| titles on ICIT sealings (objects) | M347 (W760) 5, M8 (W100) 7, M336-M89 (W705-W033) 3, M249-M161 (W590-W390) 5 |

Each row of `sealings.csv` gives:
- site and object (CISI number);
- the ICIT ids and every face text in reading order;
- the impression count, back type, back class (DOOR / FIXED_OTHER / CONTAINER) and context from Frenez & Tosi;
- Frenez & Tosi's per-sealing note and Rao's reverse note, taken from paragorth's open catalogue (`loop71_lothal_sealings.csv`);
- the source of the reverse type.

Harappa's M77 "sealings" are excluded. They are moulded tablets with count sides (context Q2, paragorth S-DARK-65.4).

## Pre-registered tests

| id | hypothesis | observed | null / power | p | verdict |
|---|---|---|---|---|---|
| H1 | a title is >= 3x enriched on door-peg sealings (Lothal) | 0/3 door vs 6/52 other carry any title; each title 0/3 | power at ER 3: 0.004-0.012 | 1.0 (Holm, all 4) | **untestable at this n** |
| H1 robustness | distinct (text, back) pairs; elephant text removed | 0/3 door in both | - | 1.0 | same |
| S0 | any title enriched on fixed closures (pegs + lockers + structures) | 1/19 vs 5/36 (ER 0.38) | 2.1 expected | 0.94 | not supported |
| S1 | title impressions sit on multi-impression sealings (ICIT) | 12/22 (0.55) | 7.5 | 0.024 (bar 0.0167) | not supported |
| S2 | title + non-title pairs exceed random pairing (ICIT) | 12 of 41 pairs | 10.9 | 0.40 | not supported |
| S1 (M77) | replication | 16/38 (0.42) | 14.1 | 0.31 | not supported |
| S2 (M77) | replication | 21 of 74 pairs | 19.6 | 0.38 | not supported |

Descriptive S1 shares in ICIT (share of each class's faces that sit on multi-impression sealings):
- M8: 1 of 7 (p = 0.94)
- M336-M89: 2 of 3 (p = 0.38)
- M249-M161: 3 of 5 (p = 0.34)
- jar-final: 22 of 61 (p = 0.22)
- arrow-final M211: 5 of 12 (p = 0.19)

Closers do not mark a co-sealing role either.

**Amendment A1.** The first run coded the M336-M89 block as "W705 W33". ICIT writes three-digit numbers ("W033"), so the code matched nothing. It was corrected before any result for that block was read. The first run is kept in `analyze_run1_bug.log`.

## Caveats

- **One site, one observer.** Every reverse type comes from Frenez & Tosi's study of Lothal photographs. Rao's 1985 descriptions ("reed", "stick", "groove") cannot check it (paragorth S-DARK-71.1).
- **Transcriptions miss impressions.** Wells records 2+ faces for only 14 of the 31 Lothal sealings that Frenez & Tosi count as multi-impression (paragorth S-DARK-65.1). We used Frenez & Tosi's count for multi status, so S1 at Lothal does not depend on what Wells transcribed. S2, however, can only see the impressions that were transcribed.
- **Title definitions are sign-list dependent.** W760 is either M347 or M358 under the bridge. M8 = W100 is a frequent sign that may be more than a title.
- **Lothal is a port warehouse.** Its sealing practice need not represent Harappa or Mohenjo-daro, where almost no sealings survive.

## Hypotheses

| hypothesis | verdict |
|---|---|
| Title signs mark storeroom authority (door-peg enrichment) | untestable (power <= 0.012; about 40-80 inscribed door sealings needed) |
| Titles prefer fixed closures over containers | not supported (ER 0.38, p = 0.94) |
| Title seals act as countersignatures on multi-seal sealings | not supported (S1 p = 0.024 vs bar 0.0167, no M77 replication; S2 p = 0.40) |
| M347 seals co-seal (post hoc) | does not replicate (ICIT p = 0.006, M77 p = 0.50) |

## What a person must look up (to move this from untestable)

1. **Frenez & Tosi 2005**, "The Lothal sealings" (Studi in onore di Enrica Fiandra, pp. 65-86) and **Frenez 2024**, *South Asian Studies* 40(2): 214-234 (doi 10.1080/02666030.2024.2401206). Needed: the seal identity or text of each impression on L-152, L-154, L-155, L-157 (pegs) and L-150, L-158, L-209 (lockers). None of these is in ICIT. Frenez 2024 lists door sealings L-179 and L-206; confirm whether it adds any.
2. **Rao 1985**, *Lothal* vol. II, pp. 325-327 and plates CLXIII ff. Needed: photographs of the reverse of every Lothal sealing, so that a second observer can classify the backs blind.
3. **Kalibangan**: Lal et al., *Excavations at Kalibangan* (ASI Memoir 2003; 2015 volume), sealing catalogue. Needed: the reverse descriptions for K-81 to K-89 and the other 26 ICIT sealings. K-89 has four different seals, which makes it the best co-sealing object outside Lothal.
4. **Dholavira**: Bisht 2015, *Excavations at Dholavira*. Needed: the reverse descriptions for 69 ICIT sealings, whose types include TAG:PC (pot cap).
5. **Banawali** (Bisht), **Kanmer** (Kharakwal et al. 2012; three sealing pendants), **Shikarpur** (sealings with three seal impressions and thread or knot marks), **Gola Dhoro** (Bhan et al.). Needed for each: reverse type plus seal text.
6. **Harappa and Mohenjo-daro**: Frenez 2018 ("Private person or public persona?", *Walking with the Unicorn*, pp. 166 ff.) and Frenez's "Mirrored signs". Both discuss M-425/M-426 and other early tags; reverse types are needed. Ameri's work on seal use is also relevant; no open copy was found.
   - harappa.com (Cloudflare 403), Academia, ResearchGate and Taylor & Francis all blocked automated download, and the browser extension was not connected. A human with a normal browser can fetch items 1 and 6.

Even all of this together is unlikely to reach about 40 inscribed door sealings. The decisive data would come from future excavation of a burnt storeroom deposit.

## Next experiments

- None on this route until new sealings are published. Freeze as a new-finds prediction: "no title sign will be enriched >= 3x on door-peg sealings" (sealed null), and score it if a door-sealing deposit appears.
- If a human retrieves items 1-2, rerun `analyze.py` unchanged. Adding the peg texts would raise n_door to at most 7-9, which is still underpowered. The run is worth doing only to confirm the descriptive picture.

## Sources

- Frenez, D. & Tosi, M. 2005. The Lothal sealings: records from an Indus civilization town at the eastern end of the maritime trade circuits across the Arabian Sea. In *Studi in onore di Enrica Fiandra*, 65-86. Table 1 via paragorth transcription (`sources/paragorth_Indus-/data/derived/lothal-sealings-frenez-tosi2005.json`).
- Frenez, D. 2024. Were the cretulae (clay sealings) from the Indus port town of Lothal part of an administrative archive? *South Asian Studies* 40(2): 214-234.
- Frenez, D. 2018. Private person or public persona? Use and significance of standard Indus seals as markers of formal socio-economic identities. In Frenez et al. (eds), *Walking with the Unicorn*, Archaeopress.
- Rao, S.R. 1985. *Lothal: a Harappan port town (1955-62)*, vol. II. ASI Memoir 78.
- Joshi, J.P. & Parpola, A. 1987. *Corpus of Indus Seals and Inscriptions* 1 (CISI). Captions carry no reverse descriptions (`experiments/iconography/raw/cisi`).
- Mukhopadhyay, B.A. 2023. Semantic scope of Indus inscriptions... *Humanities and Social Sciences Communications* 10: 972 (`raw/mukhopadhyay2023/`). It adds no reverse data beyond Frenez & Tosi.
- paragorth/Indus- STRATEGIES S227, S-DARK-65.1-65.4, 71.1-71.3, 77.3 and `loop71_lothal_sealings.csv`: prior co-sealing work, built on here and not redone.
