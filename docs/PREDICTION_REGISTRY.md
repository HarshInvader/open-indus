# Prediction registry

This is one index of every hash-frozen prediction in `docs/prereg/`. For each prediction it gives the pass and fail bars, the minimum n, and the script that scores it. A future excavator can use it to score new finds without reading the whole project.

Hashes are SHA-256, copied from `docs/prereg/HASHES.txt`. All timestamps are UTC, 2026-11-15. Hash status was checked against the files on disk on 2026-11-14 (local time) for Parts A1-A3, B1-B24 and C, and re-checked for every file on 2026-11-15 after cycle 10 (see Counts):

- **MATCH.** The file on disk equals the frozen hash.
- **CHANGED.** Text was added after hashing. Read the amendment section of that prereg; it is hashed separately where noted.
- **NOT IN HASHES.** The prereg predates HASHES.txt. Its RESULTS say its scripts were frozen, but there is no hash line to check against.

Wilson 95% intervals are used wherever a prereg says "CI". "Min n" is the n below which a prediction is reported as not evaluable, not as failed.

---

## Part A. Forward predictions for new finds

These predictions were written to be scored on texts found after registration. They are the ones an excavator should use. A1-A3 are the three original preregs; A4 adds the predictions frozen in cycles 7-10.

### How to score a new find

1. Add one row per object to `experiments/new_finds/new_texts.csv`. Columns:
   - `obj_id, file, site, object_type, field_symbol, pub_year, citation`
   - `status` (new / duplicate of a known text)
   - `icit_match`
   - `seq_M`: Mahadevan numbers in reading order, separated by spaces
   - `sign_conf`: one confidence per sign (low / medium / high)
   - `direction`
   - `scored`: yes only if at least half the signs are medium confidence or better
   - `notes`
2. Run `python experiments/new_finds/score.py`. It scores P1-P15 and writes `results.json`.
3. Run `python experiments/new_finds/score_leads.py`. It scores L1-L7 and writes `results_leads.json`.
4. Score PK1-PN by hand from site and medium. No frozen script exists for these.

**Current state.** About 190 post-2010 objects were checked. 12 are truly new and 2 are scorable. Every prediction is below its minimum n.

### A1. `2026-11-14_new_finds_predictions.md`
- **Hash.** `b30497e184b142bf720026b71f2445f2842a0c4e0018c2003f90c53be93a2489` (00:00:35Z). MATCH.
- **Scorer.** `experiments/new_finds/score.py`. This file is not itself in HASHES.txt.
- **Frozen inputs.**
  - `experiments/new_finds/baselines.py` (`0a299687a72a...`)
  - `ref_tables.json` (`97a40ef09ed7...`)
  - `baselines.json` (`6798451647f5...`)
  - `experiments/functional_reading/fr.py` (`76dd84850bae...`)

| id | prediction | pass bar | min n |
|---|---|---|---|
| P1 | complete seal texts of 2+ signs end in jar M342 (or M342 M176) | share in [0.20, 0.60] and CI contains 0.38 | 8 texts |
| P1c | M342 tokens are line-final or followed only by M176 | ≥ 0.65 | 5 tokens |
| P2 | the 849 majority-order pairs in `ref_tables.json` keep their order | ≥ 0.75 and binomial p < 0.05 vs 0.5 | 8 pair tokens |
| P3 | ticked fish (M60, M66, M68, M71, M73) are final | ≥ 0.50 and above the plain-fish share | 3 tokens |
| P4 | M109 is followed by M59 | ≥ 0.30 | 2 tokens |
| P5 | `fr.py` full-parse rate | CI contains 0.77 and above the mean of 20 shuffles | 10 texts |
| P6 | first sign is attested as initial | ≥ 0.85 | 8 texts |
| P7 | last sign is attested as final | ≥ 0.85 | 8 texts |
| P8 | tokens are known signs (not NEW) | ≥ 0.93 | 30 tokens |
| P9 | M267 / M391 stand first | ≥ 0.60 | 4 tokens |
| P10 | M176 is line-final | ≥ 0.70 | 3 tokens |
| P11 | mean text length | in [3.0, 6.5] | 8 texts |
| P12 | reading direction right-to-left | ≥ 0.85 | 8 texts |
| P13 | fish partner is in {M53, M387, M343, M171, M389} | ≥ 0.20 | 8 pairs |
| P14 | fish stands first (exploratory) | reported only | none |
| P15 | foreign round seals fail the template more often (exploratory) | reported only | none |

- **Overall rule.** Supported if ≥ 75% of evaluable predictions pass. Contradicted if ≤ 50% pass.
- **Falsifiers.**
  - P2 < 0.6 with n ≥ 20.
  - P5 < 0.55 with n ≥ 20.
  - P8 < 0.85.

### A2. `2026-11-15_toponym_predictions.md`
- **Hash.** `269c5c78c17978a4da5b382dd47eda2746e30e136f44c579c6ed7a59e4258f3a` (01:08:00Z). MATCH.
- **Scorer.** None frozen. Score by hand. `score_leads.py` covers K1 only, as L5. The machinery of the retrospective test is in `experiments/toponyms/common.py` and `confirm.py`.
- **Items.**
  - K1: M93 = W031 W032 (home Chanhu-daro)
  - K2: W920 W060 (Chanhu-daro)
  - K3: W806 W154 (Harappa)
  - K4: M254 (Lothal)

| id | prediction | pass | fail | min n |
|---|---|---|---|---|
| PK1-home | K1 texts come from Chanhu-daro | ≥ 50% | < 20% | 3 texts |
| PK1-travel | K1 off-home texts are on mobile media (sealings) | ≥ 50% | 0 of ≥ 3 | 2 off-home texts |
| PK-home | pooled K1-K4 home enrichment | O/E ≥ 2 and binomial p < 0.05 | O/E < 1 | 5 texts |
| PK-travel | pooled mobile share off-home vs the same sites' other texts | ≥ 20 points higher | difference ≤ 0 | 5 off-home texts |
| PN-null | no other sequence shows ≥ 3 new occurrences, O/E ≥ 2 at one site and ≥ 2 off-home sealings | none found | one or more found | none stated |

### A3. `2026-11-15_leads_predictions.md`
- **Hash.** `4e0169cf63e69d16a553f36ab0b4d39646cea6fa723a29f05bc10ad959d5c108` (02:15:02Z). MATCH.
- **Scorer.** `experiments/new_finds/score_leads.py` (`3fa207d6c94d...`).
- **Frozen inputs.**
  - `experiments/roof_context/lead_baselines.json` (`9d248f0127ff...`)
  - `experiments/roof_context/r2_lead_baselines.py` (`0dc0f227ff62...`)

| id | prediction | pass | fail | min n |
|---|---|---|---|---|
| L1 | roofed signs {M65, M66, M92, M138, M159, M163, M334, M203, M196, M14} are initial more often than their bases {M59, M60, M89, M137, M158, M162, M333, M202, M195, M12} | share ≥ base + 0.10 and Fisher p < 0.05 | roofed ≤ base | 8 roofed + 8 base tokens |
| L2 | bangles carry M373 / M374 | ≥ 0.08 and binomial p < 0.05 vs 0.01 | < 0.03 with n ≥ 15 | 10 bangle texts |
| L2b | M403 on bangles (exploratory) | reported only | none | none |
| L3 | ticked fish are final | ≥ 0.50 and above plain fish | ≤ plain fish | 5 tokens |
| L4 | the numeral before M59 is tall two (M87) | ≥ 0.40 | < 0.20 | 5 tokens |
| L5 | M93 texts come from Chanhu-daro | ≥ 50% | < 20% | 3 texts |
| L5b | M93 is line-final or alone on its line | ≥ 0.70 | < 0.40 | 3 tokens |
| L6 | frozen slot values are kept (M211 T3; M59/M60/M342/M284 T2; M194/M197 S7; M15/M190/M403 S3; M25 S1) | ≥ 0.60 and binomial p < 0.05 vs 0.325 | ≤ 0.40 | 8 pairs |
| L6b | L6 without M59 / M60 | ≥ 0.50 | ≤ 0.33 | 6 pairs |
| L7 | seals without an animal are smaller | median ratio ≤ 0.90 and Mann-Whitney p < 0.10 | ratio ≥ 1.0 | 4 no-animal + 8 animal seals |

**Status.** Scored on the current `new_texts.csv` (2 scorable texts), every lead is inconclusive.

### A4. Forward predictions added in cycles 7-10 (2026-11-14 to 11-15)

Only `bangle_oval.md` is a hashed prereg. The other three were registered by their entry in this file, after the experiment that produced them; they have no hash line of their own. Score every one of them only on objects that are not in the discovery data named in the "origin" column.

**A4a. `bangle_oval.md`**
- **Hash.** `b8638e891402fe9a31a9be4c679e7ad8012948c27c3db80763382f18b137c88b` (03:14:00Z). MATCH.
- **Scorer and frozen inputs.** `experiments/bangle_oval/b0_baselines.py`, `baselines.json`, `b1_power.py`, `power.json`. No end-to-end scorer; apply the rules below by hand.
- **Origin.** self_label lead (oval on 6/41 ICIT bangle texts, q = 0.008), already frozen as L2. Discovery set excluded: all 50 ICIT `BNGL` rows (41 texts).
- **Unit.** Distinct (sequence, site) texts on new bangles of any material. Oval = M373/M374 (W790); the diamond M261/W850 does not count.

| id | prediction | pass | fail | min n |
|---|---|---|---|---|
| BO-H1 | oval on new bangle texts | one-sided binomial p < 0.05 vs p0 = 0.0106 pooled (MD 0.0096, Harappa 0.0106) and share ≥ 0.08; strong pass ≥ 0.15 | share < 0.03 with n ≥ 15, or upper 95% bound < 0.15 with n ≥ 20 | 10 texts |
| BO-H2 | oval texts are mostly one-sign, or the oval keeps one slot | ≥ 50% one-sign, or one slot in ≥ 2/3 of multi-sign cases | otherwise | 4 oval texts for a p-value |
| BO-H3 | M403 (W840) share on new bangles (exploratory) | reported vs 0.026 | none | none |
| BO-H4 | workshop alternative: oval confined to one site or series | Fisher two-sided by site and by series | none (4-14% power; a null is not evidence) | none |

- **Data that would score it.** HARP inscribed-bangle list (Kenoyer/Meadow), Fuls 2023 catalogue, CISI 3.x. About 19 new texts give 80% power if the true rate is 15%.
- **Current state.** 0 eligible new bangles (`experiments/bangle_oval/RESULTS.md`; open_journals also found 0). Not evaluable.

**A4b. Registered by entry in this file**

| id | origin | prediction and scoring rule | data that would score it | status |
|---|---|---|---|---|
| W1 | scene_text exploratory lead: W621 (= M242) on 5 Mohenjo-daro scene-seal types vs 0.40 expected (q = 0.20); 0 of 8 uncoded ICIT scene seals carry it | In any newly published Mohenjo-daro scene-seal set (or CISI vol. 3), W621 occurs at ≥ 3× its rate on non-scene seals of matched size. Scored only on new objects. No min n or scorer frozen; `experiments/scene_text/s3_join.py` holds the machinery | CISI vol. 3 HARP scene tablets and seals; new Mohenjo-daro scene seals | not scored |
| FS1 | firing_stage post hoc lead, not blind: M391 on 4/25 painted texts vs 7/384 graffiti (3 of 4 from Kutch); jar M342 on 1/25 painted vs 70/384 graffiti | On newly recorded painted (pre-firing) vessel inscriptions, M342 occurs on < 5% of texts (vs about 18% of post-firing graffiti), and M391/M343/M267 together on ≥ 15%. Scored only on vessels not in `experiments/firing_stage/vessel_marks.csv`. The RESULTS file words the same lead as "≥ 5× the graffiti rate, outside Kutch" | Kenoyer & Meadow HARP sherd database (1,218 marked sherds); Kalibangan report Part I; new painted finds outside Kutch | not scored |
| TF1 | reg_findspot F3 (Mackay 1938 DK-G, block p = 0.0007); red team: robust to depth, families, OCR, coding, but q = 0.114 over all 163 tests and not replicated elsewhere at Mohenjo-daro (p = 0.31) | Ticked-fish seals (M60/M66/M68/M71/M73) cluster by building block in any independent Mohenjo-daro or Harappa register with block or house findspots: block-label permutation p < 0.05 at family level | HARP trench/lot findspots; Dales 1960s; Marshall house lists from MIC vol. I | fish_marshall scored it on Marshall 1931 seals with ICIT findspots: p = 0.88 at power 0/200, so not evaluable. Harappa (Vats) untestable: 3 families |

**A4c. Proposed in a RESULTS file but not frozen.** These have no registered rule. Do not score them as predictions without a new prereg.
- site_signal: Harappa prefers leaf variant W806 and closer W154.
- space_and_sealing: sealings carry the connective M99 more often than seals (OR 1.82, Holm 0.067).
- reg_size: "closers take a larger share on small seals; connective flat". Superseded: redteam_size reduced it to "about one closer per text".
- reg_chrono: on Harappa seals, M162 earlier and M65, M389 later; texts longer in shallower levels.
- direction_time_animal: higher numeral share on text-only seals (+2.7 points).

---

## Part B. Experiment preregistrations (retrospective tests)

These froze a test before it was run on existing data. Most are already scored; the outcome column gives the result, and `docs/NEGATIVE_ATLAS.md` gives detail. The listed scorer re-runs on an enlarged corpus. Where a prereg has many sub-tests, the table gives the confirmatory ones. "Unit" stands in for min n where the prereg sets eligibility rather than a fixed n.

### B1. `pair_numeral_long.md`
- **Hash.** `3907f98d5bc0d29883e7ffecc20a840ffd8b7409cb4bf98e50afbdb8f45b4fad` (00:44:00Z). MATCH.
- **Scorers.** `experiments/pair_numeral_long/f1_pairs.py`, `f2_numerals.py`, `f6_long.py`, `common.py`.

| id | prediction | pass | unit / min n | outcome |
|---|---|---|---|---|
| F1-T1 | no two-inventory split | POL excess < 0.30 and CI upper < 0.50 | held-out 2-sign core types | pass (+0.075): two-inventory refuted |
| F1-T2 | no blazon-type alternation | max-cut excess < 0.10 and swap-null p > alpha | held-out pair types | see RESULTS |
| F1-T3 | position does not set order the way two inventories do | Wilson upper < 0.83 | pair types unseen in dev | see RESULTS |
| F2-N1 | numeral + lexeme head is a frozen number-name | share at dev spike ≥ 0.6, above pooled expectation, permutation p < alpha | lexeme-like heads | 29/40; 14/24 without M59 (weakened) |
| F2-N2 | count-like heads vary | modal share < 0.6 and below N1 (Fisher) | count-like heads | failed on red team (code bug) |
| F2-N3 | no calendar naming | 0 calendar-like heads (n ≥ 8); no shared cap in {7, 12, 13, 20} | heads with n ≥ 8 | see RESULTS |
| F2-N4 | jar M342 after short strokes takes 7 or 12 | share of {7, 12} ≥ 0.6, binomial p < alpha | held-out | see RESULTS |
| F6-L1 | long texts are not lists of short labels | acceptance > concat null | held-out long texts | failed on red team (rigged null) |
| F6-L2 | few label boundaries inside lines | resets per 10 signs < null | same | see RESULTS |
| F6-L3 | long texts carry residue beyond the template | upper bound < short acceptance | same | see RESULTS |
| F6-L4 | new ordering among known signs | reversed bigram share > null (dev predicts FAIL) | same | see RESULTS |
| F6-L5 | new combinations | novel bigram share > null | same | see RESULTS |

### B2. `signlist_robustness.md`
- **Hash.** `ce0ddc0b2dec7f60eb71a25beed79fa8b5cdf1d025af53c834930a9931d759c0` (00:57:13Z). **CHANGED, and no amendment section is logged.** Compare with the hashed version before relying on its text.
- **Scorers.** `experiments/signlist_robustness/harness.py`, `variants.py`, `variants.json`.
- **Variants.** 13 sign lists.

| id | finding | survives if | outcome |
|---|---|---|---|
| T1 | order beats permutations | share ≥ 2 × chance and p < 0.001 | 13/13 lists |
| T2 | ticked fish to final | p < 0.05 and ticked share > plain | sensitive (types), fragile (tokens); effect 0.54-0.63 vs 0.06-0.15 |
| T3 | M109 + M59 fixed | k ≥ 3 and p < 0.01 | sensitive (fails lump_all only) |
| T4 | object-type registers | ≥ 4 classes above permutation 95th percentile and mean AUC ≥ 0.65 | 13/13 |
| T5 | L-R reversals | share ≥ 0.70 and p < 0.001 | sensitive (small-n p misses) |
| T6 | name cores are 1-2 signs | len-1 share ≥ 0.28 and standalone ≥ 0.22 | 13/13 |
| T7 | fixed pair order | share ≥ 0.75 and p < 0.001 | see RESULTS |
| T8 | fish lexical class | ≥ 2 of 3 with p < 0.05 | passes where testable |
| T9 | functional parse beats shuffle | difference ≥ 0.20 and z ≥ 5 | 13/13 |

### B3. `toponyms.md`
- **Hash.** `95610a58ca76c026a4b19f8170ca0eb49497f04a1755977ecb035ea98699a7cf` (01:00:36Z). MATCH.
- **Scorers.** `experiments/toponyms/confirm.py`, `common.py`.

| id | prediction | support if | outcome |
|---|---|---|---|
| T1 | candidates are enriched at their home site | permutation p ≤ alpha | not supported |
| T2a | off-home occurrences are on sealings | p ≤ alpha and S2 > 0 | ICIT 66 vs 71.9 (p = 0.82) |
| T2b | same, broad mobile media | p ≤ alpha and S2 > 0 | not supported |
| T4 | reverse: seal-only at one site, sealing-only elsewhere | p ≤ alpha | 7 vs 13.0 |

### B4. `substitution.md`
- **Hash.** `475ec43ecce2cd469dfac39a92d15a0432d079f51dc331e6e91b563774e90aec` (01:01:37Z). MATCH.
- **Scorers.** `experiments/substitution/run_heldout.py`, `common.py`.

| id | prediction | pass | outcome |
|---|---|---|---|
| S-D | count of SCEs above the null | above threshold 26.1 | 11 vs 12.5 ± 7.3 |
| S-HO | SCEs replicate on held-out and at new sites | ≥ 1 replicates | 0/11 and 0/11 |

### B5. `modifiers.md`
- **Hash.** `9496c3afd0a915ee146b205c1e95cbb95ecf78eaae9e2e9880a70579d62223de` (01:11:20Z). MATCH.
- **Scorers.** `experiments/modifiers/m6_confirm.py`, `common.py`, `decomp_frozen.csv`.

| id | prediction | pass (one-sided, alpha 0.05, per confirmation set) | outcome |
|---|---|---|---|
| C1 | four corner ticks raise the final share (positive control) | T > 0, p < 0.05 | ticked fish strengthened |
| C2 | ticks on non-fish bases raise the final share | same | see RESULTS |
| C3 | canopy raises the final share (expected to fail) | same | see RESULTS |
| C4 | strokes inside a container sign lower the final share | T < 0, p < 0.05 | see RESULTS |
| PAR | a paradigm shift shared across a modifier class | BH within set | 0/33 held-out, 0/42 ICIT |

### B6. `rank_ladder.md`
- **Hash.** `f953764b1943d883d325477994e8ae0cd5b8709dec2b7e9b4cd7294febea6c88` (01:21:08Z). MATCH.
- **Scorers.** `experiments/rank_ladder/t1_transitivity.py`, `t1b_within_class.py`, `t2_status.py`, `t3_emblem.py`, `t5_confirm.py`, `common.py`.

| id | prediction | threshold | outcome |
|---|---|---|---|
| C1 | frame-sign order is a transitive ladder | share ≥ 0.85 and p < 0.001 in both corpora | 83%: fail |
| C2 | order holds inside slot classes | p < 0.01 in both | see RESULTS |
| C3 | area rises with sign count (pipeline control) | p < 0.01, slope > 0 | see RESULTS |
| C4 | dev-selected size signs replicate | p < 0.05 | weakened on red team |
| C5 | handled jar W741 on smaller seals | p < 0.05 | see RESULTS |
| C6 | some frame sign tracks size | p < 0.05 | 10/76 vs 0.8 expected |
| C7 | ladder position tracks status | p < 0.05 | rho −0.077 |
| C8 | frame signs co-vary with emblem | p < 0.05 | p = 0.75 |
| C9 | other-animal seals carry fewer frame signs | p < 0.05 | see RESULTS |
| C10 | frame signs predict unicorn vs other | AUC > null 95th percentile | see RESULTS |
| C11 | no-animal seals smaller; zebu larger | Holm p < 0.05 | zebu weakened (split luck) |
| C12 | material tracks frame signs | descriptive | untestable (n < 10) |

### B7. `short_labels.md`
- **Hash.** `85bf2081624f78e15719ad4eb751c75e724daaf375eee78e98957a8b41ba282c` (01:23:11Z). **CHANGED**: the amendment was added before any Indus run, and `sl_calibrate.py` was rehashed (`9b7b812138fb...`).
- **Scorers.** `experiments/short_labels/sl_analyze.py`, `sl_indus.py`.

| id | prediction | pass | outcome |
|---|---|---|---|
| S1 | power gate on genre-matched labels | balanced accuracy ≥ 0.80 | 0.69: fail |
| S2 | Indus held-out P(language) | descriptive | 0.503 |
| S3 | held-out P(L) inside the dev 5-95% range | inside | see RESULTS |
| S4 | the one cell that crossed 0.80 | descriptive | see RESULTS |

### B8. `genre_alignment.md`
- **Hash.** `4efa2b7ccdc0eab01d8adf3b784121a4fd7754a9d2b519460769805de6de1672` (01:32:45Z). MATCH.
- **Scorers.** `experiments/genre_alignment/ga_indus.py`, `ga_core.py`, `ga_slots.py`, `controls.json`.

| id | prediction | reference | outcome |
|---|---|---|---|
| P1 | closer = "servant of" | Ur III, OB | not supported (Ur III SERV 0.22) |
| P2 | core = owner name | Ur III, OB | see RESULTS |
| P3 | title = title | Ur III, OB | reliability 0.33 |
| P4 | connective = kin relator | Ur III, OB | later 0/48 grammar-free |
| P5 | opener = "seal of" | OB | see RESULTS |

### B9. `copper_series.md`
- **Hash.** `32c4484cc0932bf06f3ad02d63a39efdb2320a61d729533080673f892c4b1598` (01:36:23Z). MATCH.
- **Scorers.** `experiments/copper_series/tests.py`, `build_types.py`, `types.csv`.

| id | prediction | pass | outcome |
|---|---|---|---|
| H1a | closed series | coverage ≥ 0.90 and Chao1 CI contains a cycle length | Chao1 65 (45-140) |
| H1b | even counts | Gini inside the uniform 95% range | 0.55 vs ≤ 0.27: fail |
| H1c | ring structure | Hamiltonian cycle and lower degree CV | ring power 0.38 |
| H1d | numerals give position | distinct contiguous values 1..m, m ≥ 4 | p = 0.77 |
| H2a | numeral minimal pairs | above expectation | 0/3 |
| H2b | skewed counts | Gini above uniform 97.5th percentile | see RESULTS |
| H2c | value vs frequency | Spearman p < 0.05 | see RESULTS |
| H3a | fixed picture per type | modal ≥ 80%, p < 0.05 | see RESULTS |
| H3b | pictures track seal popularity | rho > 0, p < 0.05 | rho −0.23: fail |
| H3c | same picture, shared signs | p < 0.05 | see RESULTS |

### B10. `elamite_bridge.md`
- **Hash.** `502a153368731215280adfb71dcea540312f2bc5f4c37f938dba54a9722f51a4` (01:45:35Z). MATCH.
- **Scorers.** `experiments/elamite_bridge/eb_test.py`, `eb_core.py`, `calibration.json`.

| id | prediction | pass | outcome |
|---|---|---|---|
| H1 | complex look-alikes are syllable-like | Holm p < 0.05 | Holm 0.099 |
| H2 | all look-alikes (descriptive) | none | see RESULTS |
| H3 | M77 replication (descriptive) | none | see RESULTS |
| H4 | Desset sound values carry over | Holm p < 0.05 | 1 vs 3.4 ± 2.5 (p = 0.90) |

### B11. `closer_ownership.md`
- **Hash.** `d8582b1721db8105cf3def1e7ede3f7e3c1c1a86a7afd1c418cfa0816457dceb` (01:45:52Z). MATCH.
- **Scorers.** `experiments/closer_ownership/co_core.py`, `co_lib.py`.

| id | prediction | threshold (held-out and ICIT) | outcome |
|---|---|---|---|
| P1 | closer on short legends | short ≥ 0.40 | see RESULTS |
| P2 | closer alone beside one content block | name-only ≥ 0.20 | see RESULTS |
| P3 | closer not commoner on long legends | long difference ≤ 0 (expected to fail) | see RESULTS |
| P4 | fingerprint nearer own/title than servant | ≥ 80% of bootstraps | see RESULTS |
| P5 | gate: "servant of" never stands alone | SERV short ≤ 0.10 and name-only ≤ 0.05 | gate failed (0.25 vs 0.75): untestable |

### B12. `m328_measure.md`
- **Hash.** `55968912eff36e0012aa792f7d8c1ae078f5e588bd95d05944d28f4a5347d175` (01:57:21Z). MATCH.
- **Scorers.** `experiments/m328_measure/l1_shape.py`, `l2_quantity.py`, `l1_key.json`.

| id | prediction | pass | outcome |
|---|---|---|---|
| PC | photo crops of M328 rank its drawing first | ≥ 3 of 5 | 0/2: shape leg inconclusive |
| L1a | S1 ranks M328 first of 8 | rank 1 | inconclusive |
| L1b | same-shape threshold | d ≤ max photo-drawing d | inconclusive |
| L1c | nearest neighbours | descriptive | descriptive |
| Q1 | N tracks tablet size | rho > 0, p ≤ 0.0125 | rho −0.17 (p = 0.99) |
| Q2 | N tracks batch size | p ≤ 0.0125 | +0.08 |
| Q3 | N tracks find-spot locus | p ≤ 0.0125 | p = 0.42 |
| Q4 | count vs name-like values | AIC rule | fixed values, ΔAIC 203 |

### B13. `self_label.md`
- **Hash.** `b57ced69d7ad4a26262ebfb547bb7551120eed6acc3d361b5608d627a481f631` (01:58:11Z). MATCH.
- **Scorers.** `experiments/self_label/s2_test.py`, `frozen_candidates.json`.

| id | prediction | pass | outcome |
|---|---|---|---|
| SL-pair | a frozen sign-object pair is confirmed | C1 ICIT q < 0.05, C2 second site p < 0.05, C3 register percentile ≥ 0.90, C4 same direction on M77 held-out | 1/78 |
| SL-decision | ≥ 2 distinct signs confirmed | ≥ 2 | null (1 = single lead) |

### B14. `naming_sim.md`
- **Hash.** `8515104eaec4c8e3fafedc7ae3e7ef0617a4f15a2e9b653d2e4e534daa0c0583` (02:02:55Z). MATCH.
- **Scorers.** `experiments/naming_sim/realcmp.py`, `score.py`, `stats.py`.

| id | prediction | rule | outcome |
|---|---|---|---|
| P1 | Indus inside the range of naming systems (dev) | d > 1.21 outlier; 0.87-1.21 peripheral; ≤ 0.87 typical | outlier (1.57), later weakened |
| P2 | same on held-out | same label | outlier (2.59) |
| P3 | separating statistics | all three predicted appear | see RESULTS |
| P4 | Germanic vs Sanskrit vs Chinese | declared undecidable | undecidable |
| P5 | ranking stability | same nearest in ≥ 5/6 runs | see RESULTS |
| S1 | generator ABC | descriptive | descriptive |
| S2 | animal-class self-compounding | above −0.095 on both splits | see RESULTS |

### B15. `half_life.md`
- **Hash.** `f2c2d7f686d4d675a6ed36d2f2e4941bc88f29653e5ecf3565df4c715def65a1` (02:05:29Z). MATCH.
- **Scorers.** `experiments/half_life/h1_main.py`, `hl_lib.py`.

| id | prediction | pass | outcome |
|---|---|---|---|
| P1 | core signs drift more than frame signs | Holm p < 0.05 | S = −0.034 (p = 0.75) |
| P2 | core strings drift more than frame strings | Holm p < 0.05 | see RESULTS |
| P3 | relative chronology replicates across datasets | Spearman p < 0.05 | family-driven (red team) |
| P4 | period-restricted signs | BH q < 0.10 | 0/302 |

### B16. `roof_context.md`
- **Hash.** `8904bdbc219b1b04e12c11944b0ae032710cc79e7184174ae05028c8481d8043` (02:09:26Z). MATCH.
- **Scorers.** `experiments/roof_context/r1_test.py`, `r0_power.py`, `power.json`.

| id | prediction | power at OR 2 / OR 3 | outcome |
|---|---|---|---|
| A-ICIT | roofed signs enriched on sealings | 0.52 / 0.86 | OR 0.25 |
| A-M77 | same, M77 sealings | 0.33 / 0.56 | see RESULTS |
| B-ICIT | roofed signs enriched in citadel | 0.61 / 0.96 | OR 1.41 (p = 0.19) |
| B-M77 | same, M77 loci | 0.73 / 0.99 | see RESULTS |

### B17. `numeral_class.md`
- **Hash.** `b6ecd1a93184e05317b8cdb67a5c9a9b02f747c393f005b9d9432d3ba9b86810` (02:10:35Z). MATCH.
- **Scorers.** `experiments/numeral_class/fit.py`, `refs.py`, `data/refs.json`.

| id | prediction | pass | outcome |
|---|---|---|---|
| NC-win | one reference class (A-I) wins on likelihood and passes the posterior predictive check | win + PPC | no win; PPC fails 9/9 |

### B18. `core_genre.md`
- **Hash.** `02059ecc505bb854d5ed3498b6b0c70371a59e8a4ce8fb4da612247e60accbac` (02:17:10Z). MATCH.
- **Scorers.** `experiments/core_genre/partB.py`, `genres.py`, `common.py`.

| id | prediction | rule | outcome |
|---|---|---|---|
| R1 | outlier status per variant | ≤ median typical; > max outlier | typical with both treatments (0.92 / 0.58) |
| R2 | non-name genre nearer than names | ≥ 0.95 on both splits in 2 of 3 variants | not met |
| R3 | one named genre | nearest on both splits, 2 of 3 variants, LOSO ≥ 4 | none |
| R4 | codes vs names (descriptive) | descriptive | 0/6 |

### B19. `potters_marks.md`
- **Hash.** `dfd830049dd77b3b61cb7f8bf36a9122a0d6b2dbd32f2ea19b7e1ccd1ccae6b4` (02:20:59Z). **CHANGED**: Amendment A1 added after the first run. `tests.py` was rehashed as `potters_marks_A1` (`7f485e4a6016...`).
- **Scorers.** `experiments/potters_marks/tests.py`, `marks.csv`.

| id | prediction | pass | outcome |
|---|---|---|---|
| (a) | frame signs have early precursors more than core signs | stratified permutation p < 0.05 and frame > core | OR 1.26 (power 0.33) |
| (b) | mark shapes cluster on one vessel class | permutation p < 0.05 | p = 0.23 (power 0.22) |
| (c) | Mature pottery keeps the association | per prereg | untestable |

### B20. `protocuneiform.md`
- **Hash.** `7a44de2c8b8a298c2f75e682fed27d7407375645ce2de709352255098932ecf6` (02:26:45Z). MATCH.
- **Scorers.** `experiments/protocuneiform/s2_test.py`, `frozen_pairs.json`.
- **Rule.** Supported only if dev Holm p < 0.05, held-out p < 0.05 and ICIT p < 0.05, all in the same direction.

| id | prediction | outcome |
|---|---|---|
| H1 | look-alikes of commodity signs are more often counted | 0.114 vs 0.154 |
| H2 | look-alikes of office/person signs are more often text-final | dev 0.041, Holm 0.21; held-out 0.38 |
| H3 | proto-cuneiform counted rate predicts Indus counted rate | not supported |
| H4 | Proto-Elamite counted rate predicts Indus counted rate | not supported |
| H5 | Proto-Elamite header rate predicts Indus initial rate | not supported |

### B21. `magnitude.md`
- **Hash.** `62df97dd2935c87dd04f3adad37a408394c34d0ab45d25d5e5563e6fa249b0cd` (02:28:18Z). **CHANGED**: Amendment A1 (02:37:34Z). `run.py` was rehashed as `magnitude_A1` (`dedf9d787dd2...`).
- **Scorers.** `experiments/magnitude/run.py`, `extract.csv`.

| id | prediction | pass | outcome |
|---|---|---|---|
| T1 | numeral tracks implement mass | p ≤ 0.0125 | n = 3: untestable |
| T2 | numeral tracks pottery capacity | p ≤ 0.0125 | n = 0 |
| T3 | numeral tracks bangle diameter | p ≤ 0.0125 | n = 0 |
| T3o | oval-bearing bangles differ in diameter | p ≤ 0.05 | n = 0 |
| T4 | numeral tracks rod length | p ≤ 0.0125 | rho −0.50, n = 13, power 0.15 |

### B22. `numeral_grammar.md`
- **Hash.** `6412bcf4a4d489bab5b82025cd1e3109bc6c5b232264cab16293ea960ea079e5` (02:28:57Z). MATCH.
- **Scorers.** `experiments/numeral_grammar/test.py`, `models.py`, `common.py`.

| id | prediction | pass | outcome |
|---|---|---|---|
| T1 | additive base 12 beats a plain tally | log10 LR ≥ 1 pooled and LR > 1 in ≥ 3 of 4 replications | −49: fail |
| P1 | 12 first (M2a) or small first (M2b) | ≥ 90% | see RESULTS |
| P2 | partners of 12 are short counts | no tall partner | 7/8 tall: fail |
| P3 | no single group ≥ 13 | none | W056 open |
| P4 | counts next to 12 differ from lone counts | p < 0.05 | see RESULTS |
| P5 | no short + short pairs summing ≤ 12 | ≤ 1 | 15: fail |
| P6 | short one stands first | ≥ 75% | see RESULTS |
| C1 | cross-class order fixed | ≥ 80% one way | see RESULTS |
| C2 | unit slot keeps numeral before it | ≥ 50% | see RESULTS |

### B23. `tablet_archives.md`
- **Hash.** `d459189670f3bd892a6ac5f6f69080bdad63e9305ea11814639aae282e099df5` (02:37:14Z). MATCH.
- **Scorers.** `experiments/tablet_archives/t_tests.py`, `tablets.csv`.

| id | prediction | pass | outcome |
|---|---|---|---|
| T1 | tiers cluster by deposit | p < 0.01 | p = 0.83 (power 0.98) |
| T2 | fewer copies of high tiers | rho < 0, p < 0.01 | +0.057 (power 0.42) |
| T3 | obverse signs partition by tier | p < 0.01 | p = 0.75 (power 0.96) |
| T4a | T2 replicates in both mound halves | p < 0.05 each | see RESULTS |
| T4b | T3 transfers between halves | p < 0.05 | rho −0.37 |

### B24. `sealing_function.md`
- **Hashes.**
  - `6eebb0ca87f13f8301bb33027a8ab1ff65dc8477c4746033d3b21f3a65614dc1` (02:39:32Z): CHANGED, superseded.
  - `66efb0513cc86a2cf0004907e6e75e77bcd9d19eb388a87ea295b2a063f76e39` (02:44:28Z, `sealing_function_A1`): MATCH.
- **Scorers.** `experiments/sealing_function/analyze.py` (`ec805dd75515...`), `build_table.py`.

| id | prediction | pass | outcome |
|---|---|---|---|
| H1 | a title is enriched on door sealings | a ≥ 2, ER ≥ 3, Holm p < 0.05 | 0/3 door sealings; power 0.004-0.012: untestable |
| S0 | titles on fixed closures | p < 0.0167 | 1/19 vs 5/36 (p = 0.94) |
| S1 | titles on multi-impression sealings | p < 0.0167 | p = 0.024 (miss); M77 p = 0.31 |
| S2 | title + non-title pairing | p < 0.0167 | p = 0.40 / 0.38 |

### B25. `carver_hands.md`
- **Hash.** `820757545da25af772cdad168436c975c749e6b0c8a94d62c0d11c0a9ae33a52` (02:31:01Z). **CHANGED**: Amendment A1 was appended after c3 ran; the hash covers the text before it.
- **Scorers.** `experiments/carver_hands/c3_test.py` (`9c1181233515...`), `clusters.csv`, `work/features.npz`.

| id | prediction | statistic | outcome |
|---|---|---|---|
| CH-P1 | carver-style neighbours (kNN) share slot content | Δ, E_F, E_C vs texts shuffled within site × size group | null (no slot p < 0.05) |
| CH-P2 | same-cluster seals share slot content | same | null |
| CH-P3 | same ICIT style letter shares slot content | same | null (lowest p 0.10, core) |
| CH-P4 | W705 / W706 variant marks a hand | same | null |

### B26. `scene_text.md`
- **Hash.** `64520666361703b19409e22cb905e363a2d8e21a8d1a15d7e279d6dbd346daf9` (02:45:31Z). Amendments A1 (03:05:00Z) and A2 (03:06:06Z) hashed; the file on disk matches the A2 hash (`7619c4293321...`). Rater codes hashed before any join (tag `scene_text_codes`).
- **Scorers.** `experiments/scene_text/s1_locate.py`, `s2_catalogue.py`, `rater_instructions.md`, `work/crop_key.csv`, `s3a_codes.py`, `s3_join.py`.

| id | prediction | pass | outcome |
|---|---|---|---|
| H1 | the cup sign is enriched on offering-scene types (M-478-480 excluded) | p < 0.05 and Mantel-Haenszel OR ≥ 3 | untestable: 0/1 offering type vs 0.59 expected; power 0 |
| H1b | same including M-478-480 | secondary | untestable (raters did not code M-478/479/480 as offering) |
| E | any sign × scene element (exploratory, BH) | q < 0.05 | 0/4,080 consensus, 0/5,780 lenient; lead W621 q = 0.20 (see A4b W1) |

### B27. `assemblage.md`
- **Hash.** `4071453e90504bbf7cf0d29d548c8b26dc0f3939e29cae50f7e5a4cceaaab5cc` (02:45:26Z). MATCH.
- **Scorers.** `experiments/assemblage/build_coding.py`, `craft_units.csv` (tag `assemblage_coding`).
- **Eligibility.** Sign in ≥ 5 distinct texts at a site; context with ≥ 2 linked units.

| id | prediction | pass | outcome |
|---|---|---|---|
| AS-P | a (sign, craft context) pair replicates | p ≤ sqrt(0.05/K) at two sites and O/E ≥ 2 at both | 0/49 non-seal, 0/193 all; power about 0-4.5%: inconclusive |
| AS-G | global count of two-site hits | permutation p ≤ 0.05 | G = 0 vs 0.01 (p = 1.0): inconclusive |

### Cycles 7-10 preregistrations (B28-B47)

All hashed in HASHES.txt before the outcome was computed, and all MATCH the file on disk unless noted. Outcomes follow each folder's `RESULTS.md`; where a red team ran, its verdict is given and overrides the original.

### B28. `firing_stage.md`
- **Hash.** `b60f221c8874...` (03:15:11Z). MATCH. **Scorers.** `experiments/firing_stage/build_table.py`, `vessel_marks.csv`, `test.py`.

| id | prediction | pass | outcome |
|---|---|---|---|
| P1 | dev pre-firing sign set (≥ 5× enriched) replicates on held-out sites | R ≥ 2, within-site p < 0.025 | fail: 1/16 vs 5/111, p = 1.0, power 0.059 (underpowered) |
| P2 | same, painted vs graffiti | same, ≥ 2 texts | inconclusive (10 dev painted texts) |
| SEC | set tracks vessel form | permutation p < 0.05 | fail, p = 0.082 (confounded with stamping) |

### B29. `identifiers.md` (A1: `s4.py` re-hashed 03:39Z)
- **Hash.** `7ab11b1ba77a...` (03:21:15Z). MATCH. **Scorers.** `experiments/identifiers/id_lib.py`, `s3.py`, `s4.py`.

| id | prediction | pass | outcome |
|---|---|---|---|
| P1 | seal new-text rate ≥ tablets + 0.20 | CIs separate | ICIT 5/5; M77 held-out 1/2 (power) |
| P2 | no saturation | completeness < 0.25 | pass (0.05-0.13), weak |
| P3 | repeats are local (identifier) | R < 0.5 | refuted, R 0.89; red team: comparison was a length artefact |
| V1-V3 | estimator calibration | inside 95% PI | seals pass; tablets far below (batch-local) |
| R1 | seal repulsion | Holm p < 0.05 | not supported, p = 0.53; red team: test uninformative (power 0.03-0.07) |
| R2 | tablet control clusters | no repulsion | pass |

### B30. `redteam_identifiers.md`
- **Hash.** `01068db16201...` (03:42:23Z). MATCH. **Scorers.** `experiments/redteam_identifiers/c1.py`, `c2.py`, `c3.py`.

| id | claim attacked | outcome |
|---|---|---|
| C1 | short cross-site formula layer | fails: 145 vs 151 expected under bigram null; length-matched locality 0.51 vs Ur III 0.53 |
| C2 | cores more novel than personal names | fails as stated; narrow version survives (single Ur III names 0.39-0.59 vs Indus 0.75-0.99) |
| C3 | no repulsion | uninformative (power 0.03-0.07; Ur III identifiers cluster) |

### B31. `site_signal.md`
- **Hash.** `17e8b3d1d173...` (03:56:38Z). MATCH. **Scorers.** `experiments/site_signal/lib.py`, `s1_confirm.py`.

| id | prediction | outcome |
|---|---|---|
| P1 | MD vs Harappa from whole text | AUC 0.49, p = 0.61 (planted 20% local stock caught 92%, exploratory) |
| P2 | site signal in the medial slot | AUC 0.51, p = 0.44; power 0.12: inconclusive |
| P3 | transfers across period bands | 0.47, p = 0.72 |
| P4 | 4-site classifier | 0.24 vs 0.25, p = 0.82 |
| P5 | dissimilarity grows with distance | r 0.90 (p = 0.042, 4 sites); 6 sites r 0.02 |

### B32. `space_and_sealing.md`
- **Hash.** `2bee6975e618...` (03:57:20Z). MATCH. **Scorers.** `experiments/space_and_sealing/sas_lib.py`, `t4_space.py`, `t6_sealing.py`.

| id | prediction | outcome |
|---|---|---|
| T4 P1 | length rises with area | pass, +1.05 signs/doubling |
| T4 P2 | class share changes with area | connective dropped, closers kept (Holm 0.004-0.019); red team: closer slopes equal a keep-one-closer null |
| T4 P3 | order replicates | fails (rho 0.31 / 0.60) |
| T4 P4 | short texts contained in longer | supported, 51% vs 35.5%, p = 0.001 |
| T4 P5 | containment depends on area | not supported, p = 0.11 |
| T6 | closer class enriched on sealings | 0/6, Holm 1 (power 0.51-0.75 at OR 2 without Lothal) |

### B33. `local_repeats.md`
- **Hash.** `1c352d28e96f...` (03:58:11Z). MATCH. **Scorers.** `experiments/local_repeats/lr.py`.

| id | prediction | outcome |
|---|---|---|
| T1 | same-text pairs differ in size | smaller difference than random, p = 0.015 (Holm 0.030) |
| T2 | same emblem | 0.67 vs 0.15, p = 0.0002 |
| T3 | period differs | untestable (1 dated pair) |
| T4 | same findspot area | 0.33 vs 0.15, p = 0.14 |
| T5 | one-sign-longer text at same site | 6/15 vs 8/1,017, p = 9e-9; red team: survives much smaller (6 vs 1.8 expected, p = 0.005) |

### B34. `slot_novelty.md`
- **Hash.** `387d357166f8...` (03:58:46Z). MATCH. **Scorers.** `experiments/slot_novelty/sn_lib.py`, `confirm.py`.

| id | prediction | outcome |
|---|---|---|
| H2a | one slot carries most novelty | not supported (top share 0.39 < 0.50) |
| H2b | closer closed (ratio ≥ 1.5) | fail on primary (1.39); passes MD held-out 1.56, ICIT new sites 1.70 |
| H2c | opener ≈ medial | supported |
| H2d | middle recombines common signs more than edges | supported |
| T3 | opener-closer MI beyond bigrams | MD p = 0.35, refuted at f ≥ 0.5 (power 0.94); Harappa no power |

### B35. `redteam_local_repeats.md`
- **Hash.** `62ac182ca62c...` (04:07:50Z). MATCH. **Scorers.** `experiments/redteam_local_repeats/rlib.py`, `r1.py`, `r2.py`.

| id | claim attacked | outcome |
|---|---|---|
| R1a | numeral formula beyond chance | survives (14 vs ≤ 1.14) but not new: the known M162/M169 count frame; residual 20 objects fail (p = 0.42) |
| R1d | M77 held-out | untestable by design (0 frame seals in held-out) |
| R2a | texts grow, never shrink | grow survives smaller (p = 0.005 trigram / 0.07 bigram); never shrink weak |
| R2b | not local | "not shown local" (non-formula lean local, p = 0.087) |

### B36. `line_breaks.md`
- **Hash.** `78c4865a0314...` (04:08:54Z). MATCH. **Scorers.** `experiments/line_breaks/lb_lib.py`, `power.py`.

| id | prediction | outcome |
|---|---|---|
| gate | n ≥ 150 two-line texts and power ≥ 0.80 | fail: 74 (about 113 with ICIT); power 0.77 / 0.51 |
| main | breaks fall at slot boundaries | untestable (not computed) |

### B37. `direction_time_animal.md`
- **Hash.** `21dfb1ceddb0...` (04:12:06Z). MATCH. **Scorers.** `experiments/direction_time_animal/dta_lib.py`, `e2_gate.py`, `e3_time.py`, `e4_animal.py`.

| id | prediction | outcome |
|---|---|---|
| E2 | L-R texts with independently fixed direction cluster | dropped at gate (31 vs 100 needed) |
| E3 | opener turnover > closer turnover | S_oc −0.098, p = 0.46; frozen power 0.00: inconclusive (strong opener turnover excluded, exploratory) |
| E4-O2 | text-only seals differ in role mix | p = 0.10 (Holm 0.17) |
| E4-O3 | sign bag separates text-only seals on held-out sites | AUC 0.57, p = 0.085 (Holm 0.17) |
| E4 | compensating class at 10% | refuted for closer type (power 0.85-0.98); opener type not excluded |

### B38. `detached_signs.md`
- **Hash.** `4c95aa39a011...` (04:23:21Z). MATCH. **Scorers.** `experiments/detached_signs/ds_lib.py`, `d1_detach.py`, `d2_covariates.py`, `d3_inline.py`.

| id | prediction | outcome |
|---|---|---|
| L1 | some signs detached beyond chance (dev) | supported (5 signs) |
| L2 | detachment replicates | supported for M242, M374, M393 |
| H1-H4 | class tied to scene, object type, material, size | 0/6, Holm 1, power ≤ 0.32: inconclusive |

### B39. `grammar.md`
- **Hash.** `518385ec7e77...` (04:52:41Z). MATCH. **Scorers.** `experiments/grammar/glib.py`, `step1_classes_seeds.py`, `validate.py`, `grammar.json`.

| id | prediction | outcome |
|---|---|---|
| a1 | beats bigram with fewer parameters | fail (+0.30 bits) |
| a2 | beats position-only and shuffled-trained | pass |
| a3 | register-aware beats pooled | fail |
| b1 / b2 / b3 | restoration | pass / fail / pass |
| c-pos / c-big / c-gap | transfer | pass / fail / fail (Harappa) |
| d | Gulf round seals worse, p < 0.01 | pass (+1.80 bits, p = 0.0001) |
| e | Ur III positive control | fail (SERV 0.59) → grammar not validated |

### B40. `reg_findspot.md` (data hashed as `reg_findspot_data`)
- **Hash.** `666f7130337c...` (05:16:22Z). MATCH. **Scorers.** `experiments/reg_findspot/data.py`, `findspots.csv`, `test.py`.

| id | prediction | outcome |
|---|---|---|
| F1 (8) | same house/room shares opener, closer, core, whole | 0/8 (house power 0.985-1.0; room 0.90-1.0 except whole 0.03) |
| F2 (3) | copies co-located or contemporary | same block 3 vs 2.1; same house 1 vs 0.36; depth 5.7 vs 5.9 ft: no |
| F3 (10) | class clusters by block/house | ticked fish block p = 0.0007 (q = 0.007); all others null. Red team: weakened |

### B41. `reg_size.md`
- **Hash.** `156471981753...` (05:17:56Z). MATCH. **Scorers.** `experiments/reg_size/rs_lib.py`, `rs_test.py`.

| id | prediction | outcome |
|---|---|---|
| P1 | length rises with area | pass (+1.14) |
| R1 | connective +, closers − | signs right; connective about 0 |
| R2 | rho with T4 ≥ 0.5 | 0.79 → "replicated". Red team: fails (mechanical), 41/138 texts double-counted |

### B42. `reg_chrono.md`
- **Hash.** `08450c1653aa...` (05:19:00Z). MATCH. **Scorers.** `experiments/reg_chrono/rlib.py`, `r1_main.py`.

| id | prediction | outcome |
|---|---|---|
| T1a | omnibus depth change | Harappa p = 0.029 (Holm 0.057), MD p = 0.087: inconclusive |
| T1b-e | single signs, classes, cross-site, half_life markers | none pass; rho 0.13 across sites; markers p = 0.83 |
| T2 | opener vs closer turnover | inconclusive (opener plants caught 0-10%) |
| T3 | ticked fish / M99 / jar / M162 | none Holm < 0.05; M162 Harappa Holm 0.062 |

### B43. `redteam_fish_block.md`
- **Hash.** `a3d2c0d946b4...` (05:24:17Z). MATCH. **Scorer.** `experiments/redteam_fish_block/run.py`.

| id | attack | outcome |
|---|---|---|
| A1 | depth confound | rejected (p 0.0007-0.003) |
| A2 | batch / carver | rejected (19 families, p = 0.0056) |
| A3 | multiplicity over 163 tests | fails (q = 0.114) |
| A4 | coding | rejected (97% agreement) |
| A5 | replication elsewhere at MD | not replicated (p = 0.31, power 0.44-0.83) → WEAKENED |

### B44. `redteam_size.md`
- **Hash.** `157d3c67350f...` (05:24:52Z). MATCH. **Scorer.** `experiments/redteam_size/rt_size.py`.

| id | attack | outcome |
|---|---|---|
| A1 | mechanical (keep-closers null) | fails: closer slope equals null (p = 0.998) |
| A2 | independence | weakened (41/138 double-counted; family bootstrap median rho 0.63) |
| A3 | confounds | survives |

### B45. `fish_marshall.md` (A1 hashed 05:45:09Z)
- **Hash.** `cd43999da546...` (05:31:37Z); file on disk matches A1 (`d7d35b720dde...`). **Scorer.** `experiments/fish_marshall/test.py`.

| id | prediction | outcome |
|---|---|---|
| primary | ticked fish cluster by block (Marshall 1931) | p = 0.88, power 0/200: inconclusive |

### B46. `reg_harappa.md` (data hashed as `reg_harappa_data`)
- **Hash.** `034cf0e806cc...` (05:46:21Z). MATCH. **Scorers.** `experiments/reg_harappa/prose.py`, `data.py`, `findspots.csv`, `test.py`.

| id | prediction | outcome |
|---|---|---|
| F1 (8) | same square/sub-square shares opener, closer, core, whole | 0/8 (power 0.90-1.0 at q = 0.5, except whole) |
| F3 (16) | class clusters by square | 0/16, q ≥ 0.64; numerals and jar real nulls (power 1.0 at 3×); ticked fish untestable |

### B47. `bangle_oval.md`
Indexed in Part A (A4a) because it is a forward prediction. H4 was run descriptively on the discovery set: site p = 0.28, series p = 0.15.

---

## Part C. Preregs not in HASHES.txt

These were written before HASHES.txt existed. Each says its scripts were frozen, but there is no line in HASHES.txt to check against. Treat them as weaker evidence of freezing.

### C1. `2026-11-14_administration.md`
- **Hash.** Frozen separately in `experiments/administration/prereg_freeze.sha256` (all entries verify): `709c15cdd8f24bda9d19389bf740b0686ce073eb97af80573e35695589e92eae`.
- **Scorers.** `experiments/administration/` t1-t4 scripts.
- **Bars.** P1-P4, P8, P9, P11, P12, P14 at p < 0.05. P5 and P6 at p < 0.025. P7, P10 and P13 at BH q < 0.05.
- **Outcome.** 0/14 positive.

| id | prediction |
|---|---|
| P1 | line 2 is a standalone name attested elsewhere |
| P2 | line 2 is attested at the same site |
| P3 | one-line texts are compounds of two complete texts |
| P4 | compound halves are attested at the same site |
| P5 | M336-M89 is enriched on Mound AB |
| P6 | final M211 is enriched on Mound F |
| P7 | any feature clusters by area |
| P8 | copies cluster at one locus |
| P9 | M267 vs M293 citadel share |
| P10 | ICIT feature × area replication |
| P11 | side-2 N fixed per side-1 |
| P12 | short-stroke cap with tall strokes |
| P13 | Lothal sign predicts fastening |
| P14 | same text gives same fastening |

### C2. `2026-11-14_core_semantics.md`
- **Scorers.** `experiments/core_semantics/`.

| id | prediction | pass |
|---|---|---|
| HD1 | no consistent head direction | CI contains 0.5 and lower bound > 0.30 |
| HD2 | same, hub metric | CI contains 0.5 and lower bound > 0.35 |
| HD3 | pair order fixed per pair | ≥ 75%, p < alpha |
| SC1 | fish form a substitution class | p < alpha |
| SC3 | fish are compound-forming | p < alpha |
| SC4 | fish combine like deity names | p < alpha |
| SC5 | fish compound with fish | p < alpha |
| SC6 | classes track object register | Mantel p < alpha |
| SC7 | fish partner set transfers | p < alpha |

- **Outcome.** HFI 0.47 [0.36, 0.54]. SC4 p = 0.014 vs alpha 0.0056.

### C3. `2026-11-14_internal_phonetics.md`

| id | prediction | realistic power | outcome |
|---|---|---|---|
| T1 | phonetic complements (≥ 3 signs pass) | 4/10 | 0/14 |
| T2 | homophone pairs at q < 0.05 | 8/80 | none |
| T3 | ligature triples at q < 0.05 | 3/50 | 1 vs 6.7 |
| T4 | silent determinatives, pooled | 2/10 | none |

### C4. `2026-11-14_language_vs_code.md`

| id | prediction | outcome |
|---|---|---|
| T1 | classifier passes the LOCO gate | fail (0.61 / 0.68) |
| T2 | Indus P(language) | 0.49 dev / 0.51 held-out |
| T3 | Indus values outside the code range | fail (5/8 inside the dev range) |

### C5. `2026-11-14_typology.md`

| id | prediction | pass |
|---|---|---|
| H1a | signs are not fixed-position | H_rel ≥ 0.80 and fixed_excess upper < 0.10 |
| H1b | freer than slot-morphology name stocks | lower bound > Ur III and Linear B means |
| H2 | cores built of standalone signs | len1 lower > 0.10 and standalone above all references |
| H3 | fixed partners above all references | partner_rel upper < 0.93 (failed by 0.003) |
| H4 | inventory between syllabary and logo-syllabic | interval ordering |
| G1 | Gulf: smaller sign set | p = 0.81 |
| G2 | Gulf: more repetition | one-sided |
| G3 | Gulf: more reduplication | one doubled jar |
| G4 | Gulf: same few signs recur | p = 0.94 |

---

## Counts

Checked against the files on disk on 2026-11-15 (after cycle 10).

- **Preregistration files.** 55 in `docs/prereg/` (35 at cycle 6, plus 20 from cycles 7-10).
  - All 55 now have a line in HASHES.txt. The 5 Part C files were added late, tagged LATE-HASH.
  - 50 match a hash line. Three of these match only their amendment hash: sealing_function (A1), scene_text (A2), fish_marshall (A1).
  - 5 have changed since their last hash line. Four log an amendment: short_labels, potters_marks, magnitude, carver_hands. signlist_robustness logs none.
- **Forward predictions for new finds.** 38: P1-P15 with P1c (16), PK (5), L (10), BO-H1 to H4 (4), W1, FS1, TF1 (3). Proposed but unfrozen leads (A4c) are not counted.
- **Retrospective predictions indexed in Parts B and C.** 256 rows (180 at cycle 6, plus 76 from cycles 7-10). None pending: carver_hands, scene_text and assemblage are now scored.

### Registration log for A4b (verbatim, as first entered)

- [2026-11-14, scene_text] Watch item W621 (M242) on scene seals: in any newly published Mohenjo-daro scene seal set (or CISI vol 3), W621 occurs on >=3x its rate on non-scene seals of matched size. Exploratory origin, q=0.20; scored only on new objects.
- [2026-11-14, firing_stage] On newly recorded PAINTED (pre-firing) vessel inscriptions, jar M342 occurs on <5% of texts (vs ~18% of post-firing graffiti), and M391/M343/M267 together on >=15%. Post hoc origin; scored only on vessels not in experiments/firing_stage/vessel_marks.csv.
- [2026-11-15, reg_findspot/redteam_fish_block] Ticked-fish seals (M60/M66/M68/M71/M73) cluster by building block in any independent Mohenjo-daro or Harappa register with block/house findspots (HARP, Marshall 1931 re-read, Dales 1960s): block-label permutation p<0.05 at family level. Origin: Mackay 1938 DK-G p=0.0009, q=0.114 over all tests.

### A5. `forward_predictions.md` (board #44, 2026-11-18)
- **Hash.** `e894904bf6eeced5b2f0e4da8c494f7ce6b80aa50b060c88633a231ad8158ccd` (10:39:18Z); amendment A1 `8ddf6eaf579663694c3cb466a41f42fe62f646e2ea5bdcde6f5424fa68143e0a` (10:41:04Z).
- **Scorer.** `experiments/forward_predictions/fp.py --mode forward` (hashed `1c789394...`), then `fp_a1.py --mode forward` for F4-A1. Reads scorable rows of `experiments/new_finds/new_texts.csv`; trains on all M77.
- **Trigger.** CISI vol 3 in hand; HARP spreadsheet; ≥ 20 new scorable texts; or ≥ 8 new round seals. Score once per trigger, report all.
- **Dry run.** Kalibangan held out: F3 FAILED (RR 1.12), the rest were below min n. The set is killed under the #44 rule, and F3 is retired.

| id | prediction | pass | fail | min n |
|---|---|---|---|---|
| F1 | round seals end in a closer | share ≤ 0.25, binomial p < .05 vs square rate | ≥ 0.40 | 8 |
| F2 | round seals: trigram excess vs square seals | ≥ +0.5 bits/sign, perm p < .05 | < 0 | 8 round |
| F3 | jar M342 on post-firing graffiti (length-aware) | RR ≤ 0.70, p < .05 | RR ≥ 1.0 | E ≥ 8 (RETIRED) |
| F3b | jar sign on storage jars vs other forms | RR < 1.5 | RR ≥ 2, p < .05 | 5 jar texts |
| F4-A1 | cup M328 after tall strokes: N = 5 absent | N=5 ≤ 0.02 and gain > 0 | N=5 > 0.05 or gain < 0 | 10 tokens |
| F4b | cup sign on offering-scene moulded tablets | OR ≥ 3, Fisher p < .05 | OR < 1.5 (≥ 10 types) | 5 types |
| F5 | plain fish M67=M70=M72 merge, class trigram gain | > 0, CI lower > 0 | CI upper < 0 | 30 fish tokens |
