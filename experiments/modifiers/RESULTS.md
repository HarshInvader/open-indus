# Graphic modifiers: is there a paradigm beyond the corner ticks?

Modifier-paradigm agent, 2026-11-15. Fable 5.2 plan item 4. Pre-registration: `docs/prereg/modifiers.md`. Hashes for the decomposition tables, the pre-registration and the confirmation code are in `docs/prereg/HASHES.txt`.
Unit: distinct texts with no `#` break, line breaks removed, length 2 or more. Dev has 1,603 texts, held-out v2 has 523, ICIT (native Wells codes) has 2,396, and ICIT sites absent from M77 have 235.

## Findings first

1. **There is no modifier paradigm. Corner ticks are the only graphic modifier with a confirmed grammatical effect.** I split 145 signs into base + modifier across 17 modifier classes, blind to distribution. 13 classes had 3 or more testable bases. On dev, 1 of 39 class × feature tests passed correction: ticks raise the text-final share (q=0.039). In both confirmation sets the other classes were null as predicted: held-out 0 of 33 at q<0.1, ICIT 0 of 42.
2. **Ticks (positive control) replicate.**
   - held-out: robust T=+4.6, p=0.0015, 6 bases up and 3 down;
   - ICIT: T=+11.8, p=0.0005;
   - new-site ICIT: T=+1.2, p=0.076, with only 3 bases. Not confirmed there (underpowered).
3. **Do ticks also work on non-fish bases? Inconclusive.**
   - On dev, ticks raise the final share on non-fish bases too (T=+3.6, p=0.004). On held-out they do not (T=+0.7, p=0.14). On ICIT T=+2.9, p=0.021, but only 4 of 9 bases go up.
   - The positive cases sit in the oval family:

     | pair | final share, held-out | final share, ICIT |
     |---|---|---|
     | M404←M403 (ICIT W842) | 1.0 vs 0.06 | 1.0 vs 0.06 |
     | M388←M387 (ICIT W804) | 0.5 vs 0.13 | 0.57 vs 0.00 |
     | M390←M389 | 1.0 vs 0.00 | – |

   - The box M250←M249 goes the other way on held-out.
   - Every derived form has 1-7 tokens.
   - The earlier redteam conclusion that ticks work only on fish rested on lumping brackets with ticks. Brackets are null here: dev T=+1.0, p=0.19; held-out and ICIT null.
4. **Strokes inside a jar or cup move the sign away from the end.** This is confirmed on held-out (T=−2.0, p=0.019, 3 of 3 bases down). ICIT has too few bases for the test (k=2), but its CMH z is −19 (W741-5 vs W740). This restates the known "jar + strokes ≠ jar" result. It is a container-specific effect: inserted strokes on non-container bases do nothing (dev T=0).
5. **Leads that were not confirmed:**
   - **A roof over a base makes the sign more often text-initial.** Held-out: 5 bases up, 0 down, p=0.0065 (q=0.21). ICIT: 6 up, 0 down, p=0.04. Dev: 5 up, 4 down, p=0.29. This was not a primary prediction, so it is the top lead for a new pre-registered test. Most of the tokens come from M65←M59 (roof fish), whose initial share on dev is 0.31 vs 0.11.
   - **A canopy raises the final share.** ICIT p=0.029, but one pair drives it (W679←W645). Held-out p=0.77.
6. **Power.** The power figures below are for the calibrated statistic itself, planted at the observed token counts (`power_partners.json`).
   - **A tick-sized effect** (+0.5 final share) would have been detected in ICIT for 11 of 13 classes (power ≥0.8). The exceptions are PAIRTICKS4 (0.76) and INNERCHEVRON (k=3, 1.0 but unstable). On held-out, power is ≥0.9 for COMB, DOUBLE, HATCH, INSERT, OUTLINE, ROOF and THROUGH, and 0.35-0.69 for BRACKET, CANOPY, LEFTPOST, PAIRTICKS4 and INNERCHEVRON.
   - **A moderate effect** (+0.2) had power of only 0.2-0.76, except INSERT (0.84-1.0) and ticks (0.58-0.94).
   - **So the null is firm for large slot effects only.** Moderate shifts cannot be excluded for most classes.
   - **Untestable in any set** (fewer than 3 bases with tokens): HAT on the man sign (one base, M1, with 4 hats), RAYS4, and FRAME on held-out. LEFTPOST, PAIRBARS and FRAME are thin everywhere.
7. **Partner choice.** I used the left and right neighbour role class, from the frozen functional_reading lexicon, as a sign-flip consistency test of the partner-difference vectors over bases. Only ticks shift partners consistently: dev p=0.012 and ICIT p=0.006, with held-out p=0.078. The partner shift is the same fact as the final shift: their right neighbour becomes end-of-text. No other class reaches p<0.1. **Object-type register (seal share):** no class shifts it after correction. The nominal hits are INSERT on ICIT (p=0.010) and OUTLINE and INNERCHEVRON on ICIT (p=0.016-0.03); none was predicted.

**Verdict for the plan item:** "If only the ticks work, they are an isolated convention." That is the outcome. Ticks mark the closing slot; the jar/cup strokes are a container-specific change. No second modifier gives a consistent slot, partner or register shift across bases, so no functional gloss per modifier can be read off.

## Method

### 1. Blind decomposition (`decomp.csv`, frozen and hashed before any statistic)
- **Sources.** Contact sheets of all 417 Mahadevan drawings (`m0_sheets.py`, `sheets/sheet_*.png`) were classified by eye, using only the drawings. CISI photos were not consulted: there was no time to locate 145 signs on plates. Checking the ticks on photos remains open (redteam item).
- **Classes:**
  - TICKS4: 4 corner ticks
  - PAIRTICKS4: paired corner ticks
  - BRACKET: parentheses
  - PAIRBARS: 2 long flanking bars
  - ROOF: chevron above
  - CANOPY: flat bar with drop ends
  - INSERT: short inner strokes
  - THROUGH: stroke through the base
  - INNERCHEVRON
  - HATCH
  - DOUBLE
  - OUTLINE: double-line
  - COMB: comb or rake attached
  - LEFTPOST: post joined at the left
  - FRAME: base inside an oval, box or diamond
  - HAT: object on the head of the man sign
  - RAYS4
- **Format.** Each row has a confidence (high, medium or low) and a base family. Tests use high and medium.
- **Contamination.** I had read README #3 and the novel_methods exp3 family list before decomposing. The table is blind to new statistics, not to those results.
- **Wells table (`w_decomp.csv`).** The same classes were located in Wells numbering from font renders of all 712 ICIT codes (`m0b_wsheets.py`), then frozen before any statistic. It has 154 pairs, including Wells-only pairs such as W219 (fish doubled) and W817 (oval with chevron).
- **Cross-check against a different sign list.** In the Mahadevan-Wells bridge, 53 of my pairs have both signs bridged. Wells merges only 3 of them (M417/M415, M167/M161, M169/M161). So the modified forms are distinct signs in both sign lists, not Mahadevan splitting. Mahadevan's own variant groupings are not in the repo, so I used the bridge as the cross-check instead.

### 2. Statistic
- **Why not the obvious test.** With 3-5 bases, an exact sign-flip test over bases cannot go below p=0.06-0.25. The first null I tried, replacing each derived sign by a frequency-matched random sign, measures "different from a random sign", not "shifted". It made a +0.012 ROOF shift look significant, so I dropped it (`m1_dev.log` keeps both).
- **Primary statistic T.**
  - Take the Mantel-Haenszel z for derived vs base, stratified by base.
  - Recompute it with each base dropped in turn, and keep the value closest to zero (0 if the sign flips).
  - Compare T with 2,000 fake modifier classes of identical structure. In each fake class, every base and every derived form is replaced by a random sign of matched token frequency (0.5-2×).
  - This null captures between-sign heterogeneity, the rarity of derived forms and the frequency of bases.
- **Controls on dev.**
  - Negative control: 100 fake classes of random pairings give p<0.05 in 7% (final) and 5% (initial) of cases.
  - Positive control: ticks give p=0.001.
  - Sign-flip negative controls (500 fakes each) give a false-positive rate of 0-5%.
- **Calibration of the simpler rule.** The plain CMH rule ("|z| ≥ 2.58 and robust to dropping one base") gives 5-14% false positives on random pairings (`rule_fpr.json`), which is why T is calibrated empirically.

### 3. Dev results (`m5_dev_calibrated.log`; reproducible seeds. The pre-registration quotes an earlier run with unseeded hashes: 0.006 / 0.04 / 0.013, same conclusions)

| class | k | final: T, up/down, p | initial: p | seal: p |
|---|---|---|---|---|
| TICKS4 | 12 | +9.8, 8/3, **0.001** (q=0.039) | 0.36 | 1.0 |
| TICKS4 non-fish | 7 | +3.6, 4/2, 0.004 | 1.0 | 1.0 |
| CANOPY | 7 | +1.9, 3/2, 0.044 | 1.0 | 1.0 |
| INSERT, jar/cup only | 3 | −7.3, 0/2, 0.017 | 1.0 | 0.042 |
| INSERT, all | 14 | −3.8, 2/9, 0.13 | 0.52 | 0.13 |
| BRACKET | 6 | +1.0, 0.19 | 1.0 | 1.0 |
| COMB | 11 | −1.0, 0.22 | 1.0 | 0.40 |
| DOUBLE | 8 | 0.40 | 0.19 | 1.0 |
| ROOF | 9 | 1.0 | 0.29 (z=+4.6, not robust) | 0.35 |
| HATCH, THROUGH, OUTLINE, FRAME, LEFTPOST, PAIRBARS | 3-6 | all p ≥ 0.13 | | |

### 4. Confirmation (`m6_confirm.log`, `m7_newsites_fix.log`)

| prediction | held-out v2 | ICIT all | ICIT new sites |
|---|---|---|---|
| C1 ticks → final (positive control) | **confirmed**, p=0.0015 | **confirmed**, p=0.0005 | not confirmed, p=0.076 (k=3) |
| C2 non-fish ticks → final | not confirmed, p=0.14 | confirmed, p=0.021 (4 of 9 up) | untestable (k=0) |
| C3 canopy → final | not confirmed, p=0.77 | confirmed, p=0.029 (one pair) | untestable |
| C4 jar/cup strokes → less final | **confirmed**, p=0.019 | untestable (k=2; z=−19) | untestable |
| Paradigm: other classes null | null, 0/33 at q<0.1 | null, 0/42 at q<0.1 | null |

**Decision rule** (pre-registered): a paradigm needed 2 or more non-tick classes confirmed in one set with the same direction in the other set. 0 classes qualify.

**Deviation.** The hashed script's "ICIT sites absent from M77" filter compared raw site names ("Mohenjodaro" vs "Mohenjo-daro"), so it kept 1,400 texts. That set is effectively ICIT without Harappa, Kalibangan and Lothal; it is reported in `confirm_results.json` as `icit_newsites` and gives the same verdicts as ICIT all. `m7_newsites_fix.py` reruns the set with the project's standard name normalisation (235 texts, 51 sites). Nothing else was changed.

## Hypotheses tested

| hypothesis | verdict |
|---|---|
| Several graphic modifiers each shift slot or partners consistently across 3+ bases (paradigm) | **refuted for large effects** (power ≥0.8 for +0.5 in 11 of 13 classes on ICIT); moderate effects untested |
| Corner ticks move a sign to the closing slot | **supported** (dev, held-out, ICIT) |
| Ticks act on non-fish bases too | **inconclusive** (dev yes, held-out no, ICIT mixed; oval-family bases consistent) |
| Brackets/parentheses act like ticks | refuted at available power |
| Canopy → final | inconclusive (held-out no, ICIT one pair) |
| Strokes inside jar/cup → less final | supported (held-out; ICIT CMH); container-specific |
| Roof → more initial | lead only (held-out p=0.0065, ICIT p=0.04, dev mixed; not a primary prediction) |
| Hat on the man sign is a modifier | untestable (one base) |
| Any modifier changes object-type register | not supported after correction |

## Caveats
- **Thin data.** Derived forms are rare: most have 1-7 tokens per set. The non-fish tick case rests on about 16 dev and 9 held-out tokens.
- **ICIT is not independent data.** It is mostly a second transcription of the same objects (dev included). It replicates the result across sign lists, not across objects. On new-site objects (235 texts) almost nothing is testable.
- **One analyst.** The decomposition is one person's reading of the drawings, with no second rater and no photo check. Low-confidence rows were excluded from the tests.
- **Number of tests.** About 39 on dev, 4 primary tests × 3 sets, about 33-42 paradigm tests per set, plus controls and power runs.

## Next experiments
1. Pre-register "roof → text-initial" (M65←M59, M163←M162, M334←M333, M14←M12, W391←W390, W361←W360) and test it on new finds or the Fuls corpus. Also check whether roof fish M65 is a separate opener-class word or a positional variant.
2. Pre-register "ticks on oval-family bases → final" (M388, M390, M404, W804, W807, W842) for new data. Have a second, human rater redo the decomposition on CISI photos.
3. Get the Fuls Corpus of Indus Inscriptions or CISI 3.x. The derived forms need about 3× more tokens before moderate (+0.2) modifier effects can be tested.

## Files
- Code:
  - `m0_sheets.py`, `m0b_wsheets.py`: sheets
  - `common.py`: statistic
  - `m1_dev.py`: sign-flip screen and controls
  - `m2_dev_cmh.py`, `m3_dev_robust.py`, `m4_rule_fpr.py`: CMH, robustness, rule calibration
  - `m5_dev_calibrated.py`: primary dev
  - `m6_confirm.py`: pre-registered confirmation
  - `m7_newsites_fix.py`
  - `m8_power_partners.py`: power and partner check (post hoc)
  - `m9_summary.py`
- Data: `decomp.csv` / `decomp_frozen.csv`, `w_decomp.csv`, `results.json`, `*_results.json`, `*.log`.
