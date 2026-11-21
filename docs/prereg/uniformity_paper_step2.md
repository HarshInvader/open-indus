# Pre-registration: uniformity paper, step 2

Date: 2026-11-21. Written after pool counts were taken (`experiments/uniformity_paper/step2/sizes.log`, counts only) and before any condition was scored. Code: `experiments/uniformity_paper/step2/build2.py` (pools) and `s2.py` (conditions, run, report). Both are hashed with this file in `docs/prereg/HASHES.txt`, tag `uniformity_paper_step2`.

## Claim under test

"Indus seal texts show no measurable spatial or group structure at any scale (city, excavation area, random half), while readable seal-type corpora show between-site > within-site structure."

Step 1 and its red team left two gaps. The references were not seal-type corpora with their own within-site floor (Linear B was dropped; only Latin had a floor). And the Indus side covered only Mohenjo-daro vs Harappa.

## Method (fixed for both parts)

- Every condition goes through the benchmark's own `clean()` (drop strings found at both sides, then the non-chaining greedy de-dup of `fish_tick_closer_v2/dedup.py`), `draw_n()` (Indus length mix, balanced sides) and `score()` (frozen site_signal NB pipeline plus one permuted-label AUC per draw). No new classifier. `corpus/build.py::_close` is not used.
- 50 draws per condition, seed 20261125, at most 227 texts per side.
- **Matched size.** Each between condition and its within floor are drawn at the same n per side: the smaller of the two pools' natural sizes.
- Δ = median between AUC − median within AUC. Margin 0.05 (step-1 frozen rule).
- p_floor = (1 + number of within draws ≥ median between) / 51. p_chance = (1 + number of permuted-label AUCs ≥ median between) / 51.

## Part 1: seal-type references with their own within-site floors

### Corpora

1. **Ur III seal impressions (ORACC epsd2/admin/ur3)**, Umma vs Girsu: the step-1 `ur3pos` pool. Within-city splits, using the ORACC catalogue of the tablet that carries the impression:
   - `U_reign`, `G_reign`: Šulgi + Amar-Suen vs Šū-Suen + Ibbi-Suen.
   - `U_coll`: British Museum vs Yale (YBC + NBC).
   - `G_coll`: British Museum vs Istanbul "L" (Lagash collection, from the Tello excavations).
   - `U_rand`, `G_rand`: random halves (crc32 of id).
2. **Ur III seals, one entry per physical seal (CDLI)**: `object_type = seal (not impression)` entries (mostly composites from all impressions), Umma vs Girsu. ATF converted to ORACC spelling; parts of speech looked up in the ORACC lemmatised corpora (88% of tokens found; unknown forms count as names, as in step 1). Reign of each seal = majority reign of the CDLI tablets listing it in `seal_id` (early = Šulgi + Amar-Suen, late = Šū-Suen + Ibbi-Suen). Splits `U_reign`, `G_reign`, `U_rand`, `G_rand`. This is a replication of corpus 1, not a separate family.
3. **Latin instrumentum owner/maker marks (EDH)**: step-1 `lattr` labels with type of monument in {tile, instrumentum domesticum, signaculum, amphora, lamp, vessel} and type of inscription "owner/artist inscription". Britannia vs Germania. Within splits: the red team's `ge_rlp_vs_bwhe` (Rheinland-Pfalz vs Baden-Württemberg + Hessen) and `br_north_vs_south`, plus random halves of each province. Strictly stamped marks can only be identified from the editors' commentary, which exists for Germania (242) but hardly for Britannia (13). Stamped-only is therefore run as within-Germania floors only, with no between.
4. **Old Babylonian seal impressions (ORACC epsd2/admin/oldbab)**: parsed exactly as `ur3pos`. The pair is Nippur vs Isin, the two largest proveniences. There is no archive or collection metadata, so the floors are random halves of each city.

Variants (step-1 rules): `whole` (all word forms); `namefree` (ORACC proper-noun parts of speech, unknown forms and name determinatives removed; Latin editors' capitals removed); `namefree_owner` (one legend per owner, Ur III only).

### Tiers and families

- **Tier W (whole)** is the like-for-like comparison with Indus, where names cannot be removed.
- **Tier N (name-free)** answers the names objection.
- Families are Ur III (corpus 1; corpus 2 is reported as a replication), Latin (corpus 3) and Old Babylonian (corpus 4).
- Structural floors per family:
  - Ur III: `U_reign`, `U_coll`, `G_reign`, `G_coll`.
  - Latin: `ge_rlp_vs_bwhe`, `br_north_vs_south`.
  - Old Babylonian: `N_rand`, `I_rand` (random halves only, which is weaker).
  - Random-halves floors elsewhere are secondary.

### Power gate (planted answer)

Each between condition gets the step-1 gate: same pool and size, labels permuted, `rt.plant` new100 stock at q = 0.15. It is detected when AUC ≥ max(0.65, null q95 of the unplanted condition). The gate passes at ≥ 80%; otherwise that split is "underpowered".

### Decision rules (per tier)

- **Family "above floor"**: every gated structural split has Δ ≥ 0.05. "Not above floor": at least one gated structural split has Δ < 0.05. "Underpowered": no structural split passes its gate.
- **Part 1 verdict per tier**:
  - SUPPORTED: ≥ 2 families above and none not-above.
  - MIXED: ≥ 1 above and ≥ 1 not-above.
  - WEAK: exactly 1 above, the rest underpowered.
  - REFUTED: none above and ≥ 1 not-above.
  - UNDERPOWERED: otherwise.
- **Kill rule K-Ur3**: in either tier, if a gated Ur III structural split has Δ ≤ 0 (the within-city floor matches or beats Umma vs Girsu), Ur III is reported as the Linear B outcome: "group structure, not place". It may not be cited as a place reference.
- Expected from counts (stated before scoring): Old Babylonian name-free has 8-11 per side, and Latin name-free 29-42. Both will very likely be underpowered. That will be reported as such, not as a pass.

## Part 2: all-site Indus map

### Families and site pairs

A site enters a family if it has ≥ 40 complete texts of that object type in that editor, counted before cleaning. Within each family, all pairs are tested.

| family | sites | pairs |
|---|---|---|
| `m77_seal` (M77 seals) | Mohenjo-daro, Harappa, Lothal, Chanhu-daro, Kalibangan | 10 |
| `icit_seal` (ICIT SEAL:S + SEAL) | Mohenjo-daro, Harappa, Dholavira, Chanhu-daro (Lothal 37 and Kalibangan 36 fall short) | 6 |
| `icit_sealtype` (all ICIT SEAL*, the pool used in every earlier step: seals + sealings) | Mohenjo-daro, Harappa, Dholavira, Lothal, Chanhu-daro, Kalibangan | 15 |
| `icit_sealing` (SEAL:R) | Mohenjo-daro, Harappa | 1 |
| `m77_sealing` | Mohenjo-daro, Harappa | 1 |
| `icit_tablet` (TAB*) | Mohenjo-daro, Harappa | 1 |

M77 miniature tablets are excluded because Mohenjo-daro has none.

### Per pair

- **Between**: site a (more texts) vs site b, through `clean()`.
- **Within floor**: random halves of site a (crc32 of id), at the same n.
- **Power**: in the between pool at the same n, with real labels kept, site b's tokens are replaced with probability q by a 20-sign stock of the pool's common signs. This is `rt1.plant_harappa`'s old20 recipe with the side as a parameter. It runs at q = 0.10, 0.15 and 0.20. Power at q is the share of planted draws with AUC − within median ≥ 0.05. **Gate: power at q = 0.15 ≥ 80%.**
- **q-values**: Benjamini-Hochberg within each family, for p_floor (primary) and p_chance.
- **Pair verdict**:
  - "differs": Δ ≥ 0.05, q_floor ≤ 0.10 and the gate passes.
  - "same": Δ < 0.05 and the gate passes.
  - "differs (gate fails)": Δ ≥ 0.05 and q_floor ≤ 0.10 without the gate.
  - "underpowered": otherwise.

### Pre-registered question

Is the uniformity limited to the big cities, while craft or peripheral towns (Chanhu-daro, Lothal) differ? Only pairs in `m77_seal`, `icit_seal` and `icit_sealtype` count.

- **YES**: at least one pair involving Lothal or Chanhu-daro is "differs", and Mohenjo-daro vs Harappa is "same" in that family.
- **NO**: no pair involving Lothal or Chanhu-daro is "differs" or "differs (gate fails)", and at least 2 such pairs are "same".
- **UNDERPOWERED**: otherwise.

Dholavira and Kalibangan pairs are reported in the same table but do not enter this rule.

### Kill rule for the paper's Indus sentence

If any gated pair in any family is "differs", the claim "no measurable spatial structure at any scale" must be narrowed to the pairs that remain "same".

## Compute and logging

- Runs go through `board/run.sh` (repo lock, `taskpolicy -b nice -n 20`, one process), with Part 1 first and then Part 2.
- The shared marker `open-citizen-science/.local/compute.lock.indus` is held by the stamp_detector agent, whose live process is a network image harvest. This light single-process job runs alongside it, as step 1 and its red team did.
- Thresholds are not changed after scoring. Any deviation goes in RESULTS.md under "Deviations".
