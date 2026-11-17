# Frozen predictions: site-bound sequences (toponym test, F7)

Frozen 2026-11-15 by sha256 in `docs/prereg/HASHES.txt` (tag `toponyms`). Written after `experiments/toponyms/confirm.py final`, following the freeze rule fixed in `docs/prereg/toponyms.md` (a candidate is frozen if it individually replicates on the confirmation half: O_home >= 2 and O/E >= 2). Do not edit; append a new file instead.

Scope: same test set and transcription rules as `docs/prereg/2026-11-14_new_finds_predictions.md` (inscriptions published after ICIT/M77 coverage; distinct texts; Mahadevan numbers; foreign round seals excluded). Each W-coded item is also given its Mahadevan form where one is known.

## Status of the candidates when frozen

None of them travels on current data. The confirmatory travel test failed (ICIT half B: off-home clay sealings 66 vs 71.9 expected, p = 0.82; M77 held-out 11 vs 14.6, p = 0.84). So the toponym reading is NOT supported. These are frozen as local-vocabulary predictions (P-home) and as a second chance for the toponym reading (P-travel).

| id | sequence | home | evidence (all data, site-family units) | home share of corpus |
|---|---|---|---|---|
| K1 | M93 = Wells W031 W032 (two stroke groups, written as a final or second-line mark) | Chanhu-daro | M77: 10/10 at Chanhu-daro (9 seals, 1 sealing found at Chanhu-daro). ICIT: 8/9 at Chanhu-daro; 1 pottery mark at Kalibangan (a bare numeral pair, probably not the same item). Replicated M77 dev to held-out (2/2) and ICIT A to B (3/3) | M77 2.9%, ICIT 1.9% |
| K2 | W920 W060 | Chanhu-daro | ICIT 5/56 at Chanhu-daro; 33 at Mohenjo-daro. Replicated 2 vs 0.59 | ICIT 1.9% |
| K3 | W806 W154 | Harappa | ICIT 9/14 at Harappa (4 Mohenjo-daro, 1 Dholavira). Replicated 6 vs 2.9 | ICIT 35% |
| K4 | M254 | Lothal | M77 10/65 at Lothal (mostly Mohenjo-daro). Replicated 2 vs 0.75 | M77 6.8% |

W031 and W032 on their own (stroke numerals; Chanhu-daro excess 6 vs 2.2 and 7 vs 3.1 on half B) are not frozen as separate items: their excess comes from K1.

## Predictions

| id | prediction | pass | fail | min n |
|---|---|---|---|---|
| PK1-home | New texts containing M93 / W031 W032 as a line-final or second-line mark come from Chanhu-daro | >= 50% of such texts are from Chanhu-daro | < 20% from Chanhu-daro | 3 texts |
| PK1-travel | If K1 appears away from Chanhu-daro, it is on a sealing, tag or tablet rather than a seal cut locally | >= 50% of off-home K1 texts on mobile media | 0 of >= 3 off-home K1 texts on mobile media | 2 off-home texts |
| PK-home (pooled K1-K4) | New texts with any of K1-K4 come from that item's home site at more than twice the home site's share of all new scored texts | observed / expected >= 2, one-sided binomial p < 0.05 | observed / expected < 1 | 5 texts |
| PK-travel (pooled K1-K4) | Off-home new texts with K1-K4 are on mobile media (sealing/tag, tablet, pottery) more often than the other new texts from the same sites | mobile share exceeds that of the same sites' other new texts by >= 20 points | difference <= 0 | 5 off-home texts |
| PN-null | The general null: in new finds, no sequence with >= 3 new occurrences shows O/E >= 2 at one site AND has >= 2 off-home occurrences on sealings | holds (no such sequence) | one or more such sequences | - |

## What would change the verdict

The toponym reading would be revived if PK1-travel or PK-travel passes, or if PN-null fails. More Chanhu-daro-type end marks (K1) found only at Chanhu-daro would confirm a local scribal convention, not a place name, unless they also turn up on sealings elsewhere.
