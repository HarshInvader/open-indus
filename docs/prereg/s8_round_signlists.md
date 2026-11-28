# Pre-registration: S8, rerun the round-seal order test under other sign lists

Contributor: m0x1n. Written 2026-11-28, before any variant was scored.

## Question

The corrected round-seal finding (ledger `rro_1`, `experiments/redteam_round_order/`) says the 8 round seals found in the Indus area have much weaker sign order than ordinary home seals. The measure is the KN order component: +1.64 bits/sign excess over home seals matched on length and rare-sign load, p = 1e-4, Holm 3e-4. It was computed under one sign list only, Wells/ICIT. The headline findings were checked under 12 other lists in `experiments/signlist_robustness/`, but this one came later and was not. Does the excess survive each list, and where, if anywhere, does it disappear?

## Data and units, as in `redteam_round_order/run.py`

- ICIT inscriptions, `clean()` from `experiments/context/q4_gulf.py`: breaks removed, lines read on.
- Groups: native (not foreign, not Unknown) vs foreign, distinct by (group, sequence). Native texts identical to a foreign text are removed.
- Home seals: native, type SEAL other than SEAL:C/SEAL:CY, with at least one distinct permutation.
- Home round: native SEAL:C/SEAL:CY minus 1387.1, 1388.1 and 1388.2. The 8 texts are 114.1, 2419.2, 2911.1, 2912.1, 2977.1, 3668.1, 4247.1 and 5468.1.
- **Units are fixed on the original Wells sequences before relabelling.** The same texts, and the same 8 round seals, are used under every list. After relabelling, some texts may become identical; I report how many but do not drop them, so the 8 round seals cannot vanish or merge.

## Sign lists (13)

The M77-based partitions are frozen in `experiments/signlist_robustness/variants.json`. They are carried to Wells signs through `sources/shaunmortal_indus/data/bridge_WM.json`, using the first M sign of each W entry. The font-verified fish codes in `signlist_robustness/harness.py` override the bridge: M60/66/68/71/73 → W226/232/234/236/241 and M59/65/67/70/72 → W220/231/233/235/240. M109 → W016 and M342 → W740 also override it. A W sign with no bridge entry keeps its own label. Two W signs that land on the same label become one sign.

1. `ICIT`: Wells labels unchanged (baseline; must reproduce `rro_1`).
2. `M77`: Mahadevan's identity partition through the bridge.
3. Through the bridge: `parpola`, `lump_fish`, `lump_numerals`, `lump_jar_man`, `lump_all`, `img_hi`, `img_mid`, `img_lo`.
4. `split_s1`, `split_s2`, `split_s3`: every W sign whose bridge M sign is split in `variants.json` becomes 2 or 3 allographs (the same k), token by token at random. The seed is fixed per variant.

I report the share of native tokens whose W sign has a bridge entry. Lists 2 and 3 change only those signs.

## Test, the same under every list

- **KN order component.** `Q.KN`, 10-fold CV over native texts. d = bits of the real order minus the mean bits over up to 200 distinct permutations of the text's own signs: all of them when L ≤ 5, else 200 random shuffles. Folds and permutations come from seeded NumPy streams that are fixed per text, so every list sees the same folds. Permutations are drawn on the relabelled sequence.
- **Rare load r**: tokens whose sign is seen fewer than 10 times in the fold's training texts.
- **Null N1**: 10,000 draws of 8 home seals matched on (min(L, 9), min(r, 3)), with `key_for`'s fallback as in `run.py`. Excess = mean d (home round) minus mean of null means. p = (1 + #draws ≥ obs) / 10,001.

## Pass marks and wording

- Under a list, **the excess survives** if excess > 0 and p < 0.05.
- **It disappears** if p ≥ 0.05. I will name every such list and say what it lumps or splits.
- I will also give each list's excess as a share of the baseline excess.
- Verdict for S8: **robust** if it survives under all 12 alternatives, **sensitive** if it fails under 1 or 2, **fragile** if it fails under 3 or more.
- No multiplicity correction across lists, which follows `signlist_robustness`: this is a robustness grid of one finding, not 12 findings.

## Planted controls, per list

- **C0 harness check.** Baseline `ICIT` must give an excess within ±0.25 of +1.64 and p < 0.01. Folds and permutations differ from `run.py`, so it will not be exact. If it fails, I will report the grid as unreliable.
- **C1 power.** 1,000 replicates: 8 home seals drawn N1-matched to the round seals, each scored with one of its own permutations as "real". Report the share flagged at p < 0.05, with 2,000 null draws each. This must be ≥ 0.8 under a list for a failure there to count as "disappears" rather than "untestable".
- **C2 calibration.** The same drawn seals, unshuffled. Report the flag rate (should be about 0.05).

## What I will report if it fails

Every list's excess, p, C1 and C2, whichever way they go. A list where the excess disappears is reported as such, even if it is only one list.
