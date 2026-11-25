# bilingual_behaviour count gate: FAIL

- **Rules:** `MINIMUM.txt`, sha256 `cd108774c180a643389b53fbe18cdf1cd52374ffd7068a8202d3da92107de7ed`, written 2026-11-25T19:22:09Z, before any seal count.
- **Run:** `python3 -I experiments/bilingual_behaviour/count_gate.py`. Output is in `count_gate.json`.
- **Scope:** per-pair counts only. No sign was crossed with an icon. No share, similarity, rank or p was computed.

## Counts

There are 1,651 eligible ICIT stamp seals (named icon code; 2,238 seal objects; no object had two conflicting codes).

| Pair | Picture → sign | Sign (ICIT) | Seals with sign, n | Icon | Seals with icon, N | Usable |
|---|---|---|---|---|---|---|
| P1 | A2 composite deer-buffalo → C4 | W749 | 0 | none | – | no |
| P2 | B1 unicorn → C1 shield | none (motif, not a W sign) | – | Bull1/Bult | 1,254 | no |
| P3 | B5 rhinoceros → A11 | W341 | 0 | Rhin | 25 | no |
| P4 | B7 hare → C2 | W753 | 0 | Hare | 1 | no |
| P5 | B9 markhor → C5 | W777 | 1 | Goat | 17 | no |
| P6 | B10 composite → A7 (sequence) | none | – | none | – | no |
| P7 | B19 horned archer → C6 | W777 | 1 | Anth | 2 | no |

- **Sensitivity family** W777/W780/W781/W782: n = 1, 1, 0, 0 (union 2 seals). Even pooled, this is below 5.
- **Descriptive, icon-free:** objects carrying each pair sign, by ICIT type class.
  - W341: 2 tablets.
  - W749: 6 tablets.
  - W753: 2 tablets.
  - W777: 6 tablets and 1 seal.
  - W780: 1 tablet and 1 seal.
  - W781: 2 tablets.
  - W782: 3 tablets.

  The paired signs are essentially copper-tablet-only signs.

## Verdict

**FAIL.** There are 0 usable pairs (minimum 3) and 0 usable sign-units (minimum 3). No pair sign reaches 5 seal occurrences, and the hare and archer pictures are not seal-field icons at N ≥ 5. The pairing-permutation null could not reach p ≤ 0.05 in any case (k ≤ 4 with a shared sign gives p_min 0.083). The study closes at the gate. No statistic will be computed.

**Reopen with:** a seal corpus in which the reverse signs occur (none is known), or a sign-to-ICIT transcription that maps C4/C2/A11/C5 onto commoner seal signs. The second must be argued from the drawings, not chosen to pass the gate.
