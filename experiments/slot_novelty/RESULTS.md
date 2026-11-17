# slot_novelty: where seal-text novelty lives (T2) and whether openers predict closers (T3)

2026-11-15. Fable plan 5, tests 2 and 3. Pre-registered in `docs/prereg/slot_novelty.md`; the prereg, `sn_lib.py` and `confirm.py` were hashed into `docs/prereg/HASHES.txt` (tag slot_novelty) before any held-out or ICIT statistic was computed. Ledger rows `sn_t2a`..`sn_t3hp` (family of 6). Units are distinct, complete M77 seal texts of 3+ signs (held-out = `dev_heldout(version=2)`), with line breaks dropped. Replication set: ICIT seals from sites missing from M77.

## Findings first

1. **No single open slot. Novelty is in two places, the opener and the middle; the closer is the most closed slot.** The plan's prediction (H2a) is **not supported**. Pooled over lengths 3, 4, 5 and 6+, held-out productivity P = n1/N is:

   | slot | P |
   |---|---|
   | opener | 0.49 |
   | medial | 0.44 |
   | closer | 0.32 |

   - Opener over medial: 1.10 (95% CI 0.97-1.21).
   - Top-slot share: 0.39 against a 0.50 bar.
   - Same "mixed" label on Mohenjo-daro held-out (0.56 / 0.51 / 0.33) and on ICIT new sites (0.64 / 0.59 / 0.35).
   - The result is not "even" either. Max/min = 1.52 (CI 1.31-1.75). Shuffling signs inside each text gives max/min 1.16-1.42 and the label "even" 50/50 times.
2. **The two open slots innovate differently** (H2d passes on all three sets).
   - The middle innovates by **recombining common signs**: 56% of novel interior 2-sign windows use only common signs.
   - The edges innovate more through **rare signs**: only 39% of novel start windows and 44% of novel end windows use only common signs.
   - Mohenjo-daro: 0.55 vs 0.39 / 0.46. ICIT: 0.64 vs 0.54 / 0.59.
   - Opener equals medial at sign level (H2c passes everywhere).
3. **Closed closer: real but weaker than pre-registered** (H2b).
   - The closer is the lowest slot in all three sets.
   - On the primary set, min(opener, medial)/closer = 1.39 (CI 1.23-1.59), which misses the 1.5 bar. **FAIL on primary.**
   - It passes on Mohenjo-daro held-out (1.56) and ICIT new sites (1.70).
4. **T3: no opener-closer dependency beyond the adjacent-sign chain.**
   - Mohenjo-daro held-out (n=221): I(O;C) = 0.208 bits vs swap null 0.201 ± 0.023. Excess +0.007 bits, z = +0.30, p = 0.35 (Holm 0.70).
   - Fitted bigram-chain null: p = 0.33. K = 4 or 16 classes: p = 0.54 and 0.21.
   - Power against a planted template (the top-2 openers force the top-2 closers with probability f): 0.94 at f = 0.5 (+0.09 bits) and 0.31 at f = 0.25.
   - Pre-registered verdict: **REFUTED for templates of strength f ≥ 0.5.**
   - Harappa held-out (n=29) is uninformative: power 0.03-0.04, excess -0.011, p = 1.0.
   - ICIT new sites, pooled across sites (exploratory): z = +1.16, p = 0.13.

**What this means.** The texts do not look like a one-name-plus-fixed-title formula. They look like an open first position and an open middle, both drawing on one vocabulary, followed by a fairly closed final position. Openers carry no information about closers beyond what neighbouring signs pass along. This fits the project's "shared vocabulary combined into mostly unique texts" reading (identifiers, core_genre). It does not single out personal names.

## Controls and calibration (dev / reference data only)

- **Negative control.** Signs shuffled within each text label "even" (50/50 at n=276). The method does not invent unevenness.
- **Positive control: Ur III seal legends.**
  - Positional slots find the closed slot correctly. The medial position (dumu "son of", titles) is the lowest in every run (50/50), for both the word-level legends and the legends remapped onto the Indus inventory of about 400 signs.
  - Ur III also labels "mixed", because it has two name slots: owner first and father last.
  - Labelled slots confirm that names carry the novelty. Novel content: owner 0.63 and father 0.58, against title 0.37, servant-of 0.01 and kin 0.00.
- **Remapping to the Indus inventory weakens detection.** At word level, Ur III L4 max/min is 4.4. After remapping it drops to 1.5. Inventory size matters, so all Indus comparisons are made at equal N and with inventory-relative rarity.
- **T3 size check.** On data generated from the fitted chain, the false-positive rate is 0.05 (40 reps). In the confirm run at f = 0 it is 0.08 (100 reps).
- **T3 real-template control fails.** Ur III legends (n=600) show **no** excess either (p = 0.20), even though presentation seals (deity/king ... "your servant") are a real template. Their middle vocabulary is specific to the register, so the chain-preserving null absorbs the dependency.

## Hypotheses

| id | prediction | held-out all sites | MD held-out | ICIT new sites | verdict |
|---|---|---|---|---|---|
| H2a | one slot carries most novelty | mixed | mixed | mixed | not supported (not even either) |
| H2b | closer closed (ratio ≥ 1.5, CI > 1) | 1.39 | 1.56 | 1.70 | fail on primary; replicates in 2 sets |
| H2c | opener ≈ medial (ratio < 1.5) | 1.10 | 1.09 | 1.08 | supported |
| H2d | middle recombines common signs more than edges | 0.56 vs 0.39/0.44 | 0.55 vs 0.39/0.46 | 0.64 vs 0.54/0.59 | supported |
| T3 MD | excess opener-closer MI | p = 0.35 | | | refuted at f ≥ 0.5 (power 0.94) |
| T3 Harappa | excess opener-closer MI | p = 1.0 | | | inconclusive (no power) |

## Caveats

- **P depends on N.** Held-out strata are small (40-109 texts), so held-out P values sit above the dev values (dev pooled 0.22 / 0.21 / 0.11). Compare slots within a set, not P across sets.
- **The subsample CIs on P are shifted upward,** because an 80% subsample raises the hapax rate, so the observed point can sit at the edge of its CI. The ratio CIs, which drive the decisions, are much less affected.
- **H2b–H2d came from dev,** so they are confirmatory only on held-out. H2a was the plan's prediction.
- **A null T3 does not prove the texts are chains.** A template whose registers use their own middle signs is invisible to this test, as the Ur III control shows. The test only excludes frame links that skip over the middle.
- **Harappa cannot be tested on held-out at all** (29 texts). The dev Harappa MI was *below* the swap null (z ≈ -2.8). That is unexplained, possibly near-copy families. It is exploratory and did not show on held-out (z = -0.99).
- **Positional slots ignore grammar on purpose,** to avoid the core-definition artefact flagged in core_genre. So "opener" includes texts that start with a core sign.

## Next experiments

- T3 with register-split nulls: condition the swap null on emblem (unicorn vs others) or object size, so register vocabulary cannot carry the dependency.
- Opener rare-sign novelty: check whether rare openers are local (site-bound) while recombined middles travel. This links to T5 (site_signal).

## Files

`sn_lib.py` (data, statistics, nulls), `dev_explore.py`, `power_t2.py` (dev and controls; logs `dev_t2.log`, `dev_t3.log`, `dev_power_t2.log`), `confirm.py` (confirm.log, confirm.json), `results.json`.
