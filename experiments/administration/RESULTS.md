# Administrative archaeology: relational readings without sounds

Code: `t1_person_graph.py`, `t2_offices_locus.py`, `t2b_icit_locus.py`, `t3_docket.py`, `t4_lothal_backs.py` (run from the repo root, `dev|heldout` argument where relevant). Logs: `*_dev.log`, `*_heldout.log`, `t2b.log`, `t4.log`. Machine-readable: `results.json`. Pre-registration: `docs/prereg/2026-11-14_administration.md`, frozen with `prereg_freeze.sha256` (it covers the prereg and the scripts) before any held-out, ICIT-locus or Lothal run. Held-out = `dev_heldout(version=2)`.

## Conclusion first

**None of the four relational readings survives. 0 of 14 pre-registered confirmatory tests support the alternative hypothesis, which is what the prereg predicted for 13 of them.** The one positive prediction (P3, compounds) failed on held-out.
1. **No person graph.** The second line or second side of a seal is no more often a complete text elsewhere than a random window of the same length. Held-out: 2/28 = 0.07 against a null of 0.12 (p = 0.88). Dev: 0.145 against 0.138. Same-site attestation is at null. No "son-of" sign can be identified: second lines start with tall-stroke numerals (M87, M89) and M197, not with any constant marker. The dev excess of one-line "compounds" (two complete texts joined, 5.2% against a bigram null of 2.5%) disappears on the family-split held-out (1.8% against 2.4%, p = 0.68). That excess was near-copy family containment (STATE F22), not persons joined into one name.
2. **Offices are not tied to precincts.** Title blocks (M336-M89, M51-M130-M149, M249-M161, M387-M59, M171-M59), openers (M267, M293, M391, M150, M216) and register signs (M176, final M342, final M211) were tested against excavation area within site × object type × length strata:
   - M77 dev: 0 of 20 tests survive BH.
   - M77 held-out: 0 of 12.
   - ICIT area-section with the HARP mounds ET/E and Dholavira: 0 of 26.
   - **Mahadevan's citadel vs lower-town contrast for M267 vs M293 is refuted.** Citadel shares at Mohenjo-daro (SD + L): M267 5/161, M293 2/50, M391 2/88 (p = 0.86). Harappa AB: 6/65, 2/10, 2/31 (p = 0.53). Dholavira Castle + Bailey: p = 0.40.
   - Copies of one seal text do not share a locus. A naive dev result (p = 0.003) came from double-counted sides of multi-sided seals and from publication-campaign confounding. Corrected: dev p = 0.12, held-out p = 0.96.
   - STATE F18's Mound-F enrichment of M176 is an object-type effect: within-type strata give p = 0.18 in ICIT.
3. **The docket number is variable, not a rank, and it shows no bundling or dating signal.**
   - Same side-1 identity: the side-2 tall value is no more constant than shuffled. Held-out: 2/7 identities have a single N vs 2.2 expected (p = 0.70). Dev: 3/18 vs 4.9. ICIT: 17/45 vs 12.5 (p = 0.09).
   - The apparent fixedness at object level (p = 0.003) is mould copies. This confirms STATE F39.
   - Bundling: short-stroke values are not capped when tall strokes co-occur. The maximum is 12 either way. Held-out mean difference +0.54 (p = 0.85).
   - No trend with phase: HARP periods rho = +0.07 (p = 0.35, n = 165); Vats strata rho = −0.07 (n = 85); M77 level within locus rho = −0.01 (n = 188). Tall strokes are not year counts.
4. **Lothal sealing backs carry no commodity logogram.**
   - 55 sealings with a diagnostic back (Frenez & Tosi 2005 via paragorth): 12 signs tested, none survives BH. Best is the jar W740, p = 0.008, q = 0.10. The tree W390 (M161-169) has p = 0.65 and the cup W700 p = 0.99.
   - Same text, same back type: 50 pairs vs 13.3 expected (p = 0.0005), but all of it is the elephant-seal text W817-W002-W048-W740 on wooden boxes. Without it: 5 vs 6.0 (p = 0.70). This replicates paragorth S226.

Reading: seal and tablet texts behave as identifiers drawn from a city-wide repertoire. They are not kin chains, precinct-bound offices, dated tallies or commodity labels, at the resolution these data allow.

## Pre-registered tests (held-out unless stated)

| # | Hypothesis | Observed | Null | p | Verdict |
|---|---|---|---|---|---|
| P1 | Line 2 / side 2 attested elsewhere | 2/28 (0.071) | 0.118 | 0.88 | refuted |
| P2 | ... at the same site | 1/2 | 1.67 | 0.99 | refuted |
| P3 | One-line texts = two complete texts (compounds) | 5/279 (0.018) | 0.024 | 0.68 | refuted (dev 0.052 vs 0.025 was family leakage) |
| P4 | Compound halves at the same site | 2/5 | 2.16 | 0.71 | refuted |
| P5 | M336-M89 on Harappa AB | n < 8 in held-out | - | untestable; ICIT AB 7 vs 4.8, p = 0.53 | refuted (ICIT) |
| P6 | Final M211 on Harappa F | 9 texts; ICIT F 25 vs 21.7 | - | 0.50 / 0.43 | refuted |
| P7 | Any feature × area (M77 held-out) | 0/12 survive BH | - | best M176 on MD SD, p = 0.011, q = 0.13 (not in ICIT) | refuted |
| P8 | Copies of a text share a locus | 1 pair | 2.43 | 0.96 | refuted |
| P9 | M267 vs M293 citadel contrast | M77 HO 0/21 vs 0/12; ICIT MD/H/Dh p = 0.86/0.53/0.40 | - | ≥ 0.40 | refuted |
| P10 | ICIT feature × area | 0/26 survive BH | - | best p = 0.05 | refuted |
| P11 | Side-2 N fixed per identity | 2/7 single-N | 2.16 | 0.70 | refuted |
| P12 | Short values capped by tall (bundling) | +0.54 | −0.09 | 0.85 | refuted |
| P13 | Sign predicts Lothal back type | 0/12 survive BH | - | best W740 q = 0.10 | refuted |
| P14 | Same text → same back, elephant seal excluded | 5 pairs | 6.0 | 0.70 | refuted |

Holm over the 14: nothing significant. Descriptive tests (not confirmatory, run on all data in the dev pass): t3 ICIT fixedness and the phase trends above.

## Caveats
- **Locus map.** M77 locus codes were mapped to named areas by matching identical texts to the ICIT area-section field. Mohenjo-daro: 1-7 SD, 8-15 L, 16-18 HR, 20-22 VS, 23-29 DK-A..E, 31 DK-G South, 32 DK-G North, 33-39 DK other. Harappa: 40-46 Mound F, 47-51 AB, 52-54 J/D. Purity is mostly > 85%. The mapping is documented in the t2 docstring; the per-code match counts come from a one-off check that was not saved as a script.
- **Citadel samples are small.** Mohenjo-daro citadel texts number 61/1529. The citadel test can exclude only large effects: an M267 vs M293 contrast of the size Mahadevan implied, rather than a few percentage points.
- **Power for t1.** Only 76 dev + 28 held-out distinct second lines of length ≥ 2. One-sign second lines (M242, M374, M393, M93) were excluded as uninformative. They behave like field marks or end signs, not names.
- **Lothal sample.** 55 sealings and back types are coarse. Frenez & Tosi's per-tag fingernail tallies are not in the table, so the counted-mark test could not be run.
- **Phase test.** It uses tablets with one tall value. Text identity is not controlled, because identities rarely recur across phases.

## Next experiments
1. Use the fingernail tallies beside the Lothal elephant-seal impressions (Frenez 2024 / Frenez & Tosi plates) to test whether physical tallies equal any written count.
2. Room-level Mohenjo-daro test (block-house/room-grid fields in the merged corpus): seal-tag co-finds in one room, as a household test at finer grain than area.
3. Line 2 as a field/end mark: test whether one-sign second lines (M242, M374, M393) pattern with the animal motif or seal size instead of the text.
