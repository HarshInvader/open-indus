# Pre- vs post-firing vessel marks (Fable 5.2 plan 4, item S1)

## Findings first
1. **Too few vessels have a recorded firing stage to answer the question.** Of 650 inscribed vessels in the table, only 36 have a firing stage recorded for that object. Of these, 29 are painted, 3 are post-firing graffiti with a usable text, 2 are one vessel carrying both kinds, and 4 are literature items with no transcription. Stamped (74) and moulded (3) vessels count as pre-firing by class. The 535 ICIT graffiti have no recorded stage: CISI's "graffito" covers both. Vessel form is recorded for 86 vessels. Size is recorded for none.
2. **The pre-registered test fails, but at 6% power, so it refutes nothing.** For P1 (all pre-firing vs graffiti), dev (Pakistan sites: 61 pre, 273 post distinct texts) picks 6 signs that are at least 5x enriched pre-firing: W016, W540, W692, W697, W705 (M336) and W790 (M373/374). These come almost entirely from Harappa pointed-goblet stamps. On held-out sites (16 pre, 111 post), only 1 pre-firing text carries a set sign, against 5 post (R 1.80). The within-site permutation p is 1.0. Planting a sign at the dev rate passes only 5.9% of the time.
3. **The technique-matched test (P2, painted vs graffiti) is INCONCLUSIVE.** Dev has only 10 painted texts, and no sign qualifies.
4. **The vessel-form test (secondary) fails, and is confounded anyway.** Set signs occur on goblets 8/30, dishes 1/6 and jars 0/16 (p = 0.08). All goblets are stamped, so this measures technique, not form.
5. **Lead (post hoc, contaminated): painted pots carry opener-type signs, often alone, not the jar sign.** M391 (W820) appears on 4 of 25 painted texts against 7 of 384 graffiti (Fisher p = 0.003, uncorrected, 4 exploratory tests). On painted pots it stands alone 3 times; on graffiti it opens longer texts. M343 is 3/25 vs 6/384 (p = 0.013), and M267 is 3/25 vs 11/384 (p = 0.047). Jar M342 is 1/25 painted against 70/384 graffiti and 8/52 stamped. Caveats: I read Kenoyer's sign list before pre-registering, and 3 of the 4 M391 cases come from one region (Kutch: Surkotada, Shikarpur, Kanmer). Treat it as a regional habit until it shows up elsewhere.
6. **M342 is not a potter's sign.** Its rate on stamped vessels (8/52) matches graffiti (70/384), and it is nearly absent from painted ones. This fits potters_marks, where its Early Harappan ancestors were post-firing (owner/user) marks.

Bottom line: no L2 anchor. The pre-firing / post-firing contrast cannot be tested from published per-object data. The one hint, opener-type signs painted alone on pots in Kutch, is a lead, not a finding.

## Hypothesis table
| Test | Rule | Result | Power | Verdict |
|---|---|---|---|---|
| P1 all pre vs graffiti | dev set (r>=5, >=3 texts) replicates on held-out: R>=2, within-site p<0.025 | S = 6 signs; held-out 1/16 vs 5/111, R 1.80, p 1.0 | 0.059 | FAIL (underpowered) |
| P2 painted vs graffiti | same, >=2 texts | S empty (10 dev painted texts) | n/a | INCONCLUSIVE |
| Secondary: set tracks form | permutation chi2 p<0.05 | goblet 8/30, dish 1/6, jar 0/16; p 0.082 | n/a | FAIL (technique-confounded) |
| Size | | never recorded | | UNTESTABLE |
| Sensitivity: drop possible duplicate 5548.1 / drop uncertain readings | | same S; R 1.80 / 2.35, p 1.0 | | unchanged |

Units are distinct (site, class, Wells sequence). The null permutes labels within site. Only 5 held-out sites have both classes (Daimabad, Dholavira, Kalibangan, Kanmer, Shikarpur). The single held-out hit (Karanpura, W540) sits at a one-class site, which is why p = 1.

## Data (`vessel_marks.csv`, built by `build_table.py`)
Columns: site, period, field no., ICIT type, technique, firing, firing_conf (object / class), firing_basis, vessel_form, text (Wells), source, note, citation.
- ICIT: all 636 pottery rows. ICIT `POT:T:p` = painted: every row Kenoyer cites as painted (K-120, H-1007, G-8, G-10, Sktd-3..6) has this code. `POT:T:s` = seal-stamped and `POT:M` = moulded (both pre-firing). `POT:T:g` = graffito, stage unknown.
- Kenoyer 2021, "Painted Indus script on ceramics and steatite", *Ancient Pakistan* 32, Table 1. It lists 26 painted vessels with vessel form, location and M/W sign numbers; 16 match ICIT and 10 were added. Its Fig. 3 gives 8 Harappa post-firing jars; 3 match ICIT (541.1, 542.1, 543.1), 1 is mixed (728), and 1 is a possible match (4132.1). Downloaded to `raw/kenoyer_painted/`.
- Kenoyer & Meadow 2010 and Vats 1940: Harappa stamped vessels are pointed-base goblets, impressed before firing.
- Mackay 1943 (Chanhu-daro Nos 3 and 5), Mackay 1938 (DK 6986) and Vats 1940 (post-firing Nos 1, 3, 10, 12, 26, 28, 48, 62, 84, 86 "etc.") state the stage, but their texts are not transcribed here.
- Conflict: Kenoyer puts W741 on the Sktd-3/4 dishes and W820 on the Sktd-5/6 jars; ICIT gives the reverse numbering. The sign-form pairing follows Kenoyer.

## What a person must look up
1. **Kenoyer & Meadow HARP sherd database** (1,218 marked Harappa sherds, recorded as pre/post-firing with vessel form; Kenoyer 2020 Tables 3-4). This alone would make the test powered. Ask for the per-sherd stage, form, rim diameter and text.
2. **CISI vol. 3.1 (Parpola et al. 2010) object descriptions** for Harappa pottery H-1007 to H-1766. Check whether the captions or data list say before/after firing.
3. **Vats 1940 vol. 2, Pls. CII-CIV**: map the inscribed-pottery numbers to CISI H-numbers and record which are pre-firing. The text names only the post-firing ones, with "etc.".
4. **Lal et al. 2003 (Kalibangan, MASI 98)**: 89 ICIT graffiti, stage per sherd.
5. **Rao 1979/1985 (Lothal)**: 18 graffiti. **Bisht 2015 (Dholavira)**: pp. 232 ff. **Joshi 1990 (Surkotada)**. **Dales & Kenoyer 1986 (Mohenjo-daro pottery)**: pre-firing mould script, p. 570.
6. **Mackay 1943 Pl. XXXIX** and **Mackay 1938 Pl. LXIX 4-5**: transcribe the 3 literature items.
7. Unpublished painted pieces: Bagasra and Shikarpur (Ajithprasad, Bhan) and Balakot (Kenoyer).
About 40-60 certain post-firing texts would be needed at held-out sites to reach 80% power for a tick-sized effect.

## Next
- If the HARP data arrive, re-run `test.py` unchanged (pre-registered) with object-level stage.
- Freeze as a prediction: new painted inscriptions outside Kutch will carry M391/M343/M267 at least 5x more often than graffiti do, and M342 on under 5%.

## Files
`build_table.py`, `vessel_marks.csv`, `test.py`, `tests.json`, `tests.log`, `results.json`, `raw/kenoyer_painted/` (untrusted downloads). The pre-registration is `docs/prereg/firing_stage.md`. Ledger rows are fs_p1, fs_p2, fs_sec, fs_x1 and fs_x2.
