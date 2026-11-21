# Review 1: "Two cities, one sign stock" (uniformity paper, draft of 2026-11-21)

Reviewer: review sub-agent. Scope: `docs/paper/uniformity/latex/main.tex` with refs.bib, main.pdf and the three figures, checked against every RESULTS.md, table.md, results.json and prereg it cites. Nothing was edited, committed or sent.

## Verdict first

The numbers are almost all copied correctly: 96 of 119 checked claims match their source exactly. The problems are in what three claims are made to carry:

1. **"The place signal in Ur III lives in personal names" goes further than the red team's own table.** With personal names removed (`noPN`), Umma vs Girsu still clears the Umma reign floor by +0.173 (ORACC, gate 98%) and +0.123 (CDLI, gate 98%). It fails only the Girsu reign floor (+0.027, p 0.137). The headline rests on one split.
2. **The "about 30%" name bound comes from a coarse grid.** No load between 30% and 50% was tested. Real-frequency names are excluded only from r = 0.5. What the data support is "half of seals or more is excluded; 30% is not".
3. **"Same" and "tie within ±0.05" are point-estimate rules, not equivalence tests.** Δ has no confidence interval. Draws subsample one fixed pool, and the Harappa side is nearly fixed. The usual analytic standard error of an AUC near 0.5 at 200 per side is about 0.03, so a ±0.05 margin is probably not met at 95% confidence.

Two process claims are also wrong as written. The prereg hashes were committed in the same commits as the results, so the file was not public before scoring. And the paper never says that the Indus Mohenjo-daro–Harappa number was known before every prereg; `uniformity_benchmark/RESULTS.md` says so in its caveats.

Figures: all three scripts were rerun at low priority into a temp folder, and every PNG came out byte-identical to the one in `latex/figures/`. Plotted values match results.json. Figure 1 mislabels one group, and Figure 3's legend is wrong.

---

## Part A: number audit

Sources: BENCH = `experiments/uniformity_benchmark/RESULTS.md`; RT0 = `experiments/redteam_uniformity/RESULTS.md`; S1 = `experiments/uniformity_paper/step1/RESULTS.md`; RT1 = `experiments/redteam_uniformity_step1/RESULTS.md`; S2 = `experiments/uniformity_paper/step2/RESULTS.md`; RT2 = `experiments/redteam_uniformity_step2/RESULTS.md` (RT2T = its `table.md`); CD = `experiments/chanhudaro_followup/RESULTS.md`; RR = `experiments/recchia_rerun/RESULTS.md`; PR2 = `docs/prereg/uniformity_paper_step2.md`; LIT = `docs/paper/uniformity/LITERATURE.md`. Line numbers are main.tex lines.

**Counts: OK 96 · MISMATCH 7 · UNTRACEABLE 3 · OVERCLAIM 13 (119 rows).** Rows marked "(dup)" repeat an issue found at an earlier location.

### Abstract

| loc | claim | source | status | fix |
|---|---|---|---|---|
| L47 | "It cannot." | RT2 (b), PR2 | OVERCLAIM | Absolute. ICIT seals + sealings is "underpowered", not "same", against the null, and there is no CI or equivalence test. Write "It does no better: the gap is under 0.05 in every pool." |
| L48 | Floor +0.005 to +0.042; null +0.014 to +0.054; two editions; 98–100% power at 15% | RT2 (b) table and safe wording | OK | Note that the two editions overlap in objects (see Part B1). |
| L50 | Ur III "exceed every within-city floor by +0.16 to +0.31" | S2 Part 1 | MISMATCH | The range covers the four *structural* floors. Random-halves floors give +0.355 and +0.404. Write "every structural within-city floor". |
| L50 | Latin +0.12 to +0.14 | S2 Part 1 | OK | |
| L52 | Survives removing place names, gods and theophoric names (+0.09 to +0.27) | RT2T rows noTGtheo: +0.093 to +0.267 | OK | |
| L52 | "...but not the removal of personal names" | RT2T noPN rows | OVERCLAIM | noPN clears Umma reigns (+0.173 ORACC, +0.123 CDLI, gates 98%). It fails only the Girsu reign floor. Write "and it no longer clears the strictest (Girsu reign) floor once personal names are removed". |
| L54 | Real-frequency names on no more than about 30% of seals; invented stocks 10–20% | RT2 A3, RT2T A3 | OVERCLAIM | The grid jumps from 0.3 to 0.5. ur3emp is first excluded at r = 0.5 (92–94% at 0.3). Write "names on half of seals or more are excluded; 30% is not", or rerun at r = 0.35/0.40/0.45. |
| L54 | "Ur III legends carry a personal name on 99.8% of seals" | RT2T A3 footnote: "99.8% of raw Umma + Girsu legends" | MISMATCH | These are raw legends (impressions, with repeats), not seals. Write "of legends". |
| L45 | "the claim has not been tested against a calibrated baseline" | LIT §1, §9 | UNTRACEABLE | Yadav 2013, "Sensitivity of Indus Script to Site and Type of Object", has not been read. Hedge with "to our knowledge" until it has. |
| L57 | Chanhu-daro +0.13 to +0.17, q = 0.06 | CD verdict, T0 | OK | Say that the bar is q_chance ≤ 0.05, not the q_floor ≤ 0.10 used in Methods (Part C, S4). |
| L59 | Recchia reimplementation too weak to confirm or reject | RR verdict | OK | |
| L60 | Linear B naive classifier learns scribes | RT1 | OK | |

### Introduction and data

| loc | claim | source | status | fix |
|---|---|---|---|---|
| L70 | Parpola 1994 as the standard statement, as cited by Kenoyer 2010 and Jamison 2017 | LIT §1 | OK | Not quoted; the TODO is correct. |
| L72–73 | Yadav 2017 p. 19 and pp. 20–21 quotes | LIT §1 | OK | |
| L79–85 | Wells p. viii; Kenoyer 2010 p. lvi; Kenoyer 2020 p. 219; Ameri via Petrie p. 467; Petrie p. 465 | LIT §2–3 | OK | Ameri is correctly flagged as seen only through Petrie. |
| L105 | "at most about 30% ... against 99.8%" | RT2 A3 | OVERCLAIM (dup) | As at L54. |
| L120 | Every M77 locus code agrees with the registers; 101 of 198 HR+VS texts not confirmed | RT1 attack 4 | OK | "Agrees" means no contradiction among linked codes. Locus 33 has 33 unlinked field numbers, so say "no locus code contradicts". |
| L126 | 16 of 13,517 Umma texts have an excavation number | S2 "Could not do" | OK | |

### Method

| loc | claim | source | status | fix |
|---|---|---|---|---|
| L141 | Binary sign and pair features, min_df 2 | `site_signal/lib.py` design() | OK | min_df is counted on the whole draw, test folds included. It is label-free, but say so. |
| L142 | "grouped five-fold CV repeated three times" | lib.oof_scores | UNTRACEABLE | The grouping unit is not stated (the TODO is still in the comment). From code: Indus = text, ORACC Ur III = CDLI seal id (else P-number), Latin = text, Linear B (step 1) = tablet. State this per corpus. |
| L149 | Matched n = smaller natural pool size | PR2 L15 | MISMATCH | Omits the cap of 227 per side (PR2 L14). Ur III whole runs at 227, not its natural size. |
| L151 | 30 / 50 / 200 draws | S1, RT1, S2, RT2, CD | OK | |
| L155 | "differs": Δ ≥ 0.05, q_floor ≤ 0.10, gate | PR2 L85 | OK | |
| L156 | "same": Δ < 0.05 and gate | PR2 L86 | OK | This is a point-estimate rule, not an equivalence test (Part B3). |
| L159 | Random halves of small pools score below 0.5 | S1 C note; S2 | OK | Also cite the known negative bias of pooled cross-validated AUC under the null (B3). |
| L166–167 | Power definition; gate 80% at q = 0.15 | S2 Part 2 | OK | The letter q is used for both stock share and BH q-value. Rename one. |
| L168 | Reference gate: new100 at 0.15, permuted, AUC ≥ max(0.65, null q95) | S2 Part 1 | OK | |
| L173 | A name load is excluded when ≥ 95% of draws exceed the observed gap | RT2T A3 header | OK | |
| L176 | Hashes written "into a public file before any condition was scored" | `git log -- docs/prereg/HASHES.txt` | OVERCLAIM | Hash lines were committed with the results (step 2: d7ad778; RT2 + CD: ae300d2; RR: ecbcc0d). Timestamps are self-recorded. Write "hashed into a timestamped file in the repository; the file became public with the results". |
| L175–184 | Prereg section, read as a whole | BENCH caveats: "Only references were blind. The Indus number was known before the prereg." | OVERCLAIM | Omission. Say that the Mohenjo-daro–Harappa result (0.49, then 0.55) was known before every prereg, and that only the reference conditions and red-team attacks were blind. |
| L180–181 | 0.49 first benchmark; like-for-like 0.55 | BENCH; RT0 attack 1 | OK | |
| L182 | Linear B "does not carry place once scribes are held out" | RT1 | OVERCLAIM | RT1 shows the place signal cannot be separated from scribes (0.524 with series balanced and hands held out). It does not show the absence of place. Write "cannot be shown to carry place beyond its scribes". |
| Table 1 | Eight verdicts | each RESULTS | OK | |

### Results 3.1: the tie

| loc | claim | source | status | fix |
|---|---|---|---|---|
| L214 | Between 0.52–0.55, five lists, two editors | RT1 safe wording | OK | |
| L217 | +0.005 / +0.014 / +0.042 vs MD halves | S2 Part 2; RT2 (b) | OK | |
| L218 | Null gaps +0.043 / +0.014 / +0.054 | RT2 (b) | OK | |
| L220 | q_chance 0.29 | RT2 (b) | OK | |
| L222 | 98–100% power | RT2 (b) | OK | |
| L225 | DK vs HR+VS 0.537, cities 0.517, Δ −0.020 | RT1 table | OK | |
| L226 | Random halves 0.539 | RT1 | OK | |
| L227 | Confirmed only −0.007; near-copies dropped −0.006 | RT1 attack 4 | OK | |
| L228 | Five lists −0.03 to +0.07, four of five within ±0.05 | RT1 attack 5 | OK | |
| L229 | Exception from a low within (0.474), not a high between (0.540) | RT1 attack 5 | OK | |
| L230 | 93% at 15% | RT1 attack 6 | OK | |
| L233 | DK deep vs shallow 0.46 | S1 C2 (0.457) | OK | |
| L234 | Against the depth floor the cities look "slightly separated (0.09 higher)" | S1 C note; X_C8 0.553 − X_C2 0.464 | OVERCLAIM | This understates it. +0.089 exceeds the paper's own 0.05 margin, and the comparison is exploratory (C8 failed by construction and was rerun at 200). Say that the gap would be "differs"-sized under the rule, that it is exploratory, and why the depth floor is discounted. |
| Fig. 1 values | Every plotted between/within value | S2 results.json part1/part2; RT1 `_gaps` | OK | Regenerated output is byte-identical; values were checked against JSON. |
| Fig. 1 label and caption | Group "Ur III, personal names removed"; caption "Ur III without personal names does not" | S2 `namefree` = all proper-noun POS, unknown forms and name determinatives removed (PR2 L32; s2.py ur3_variant) | MISMATCH | The row shows *all names* removed, not personal names. With only personal names removed (RT2 noPN), Umma vs Girsu clears 3 of 4 floors. Relabel "Ur III, all names removed (step-2 tagging)" and fix the caption. |

### Results 3.2: readable seals

| loc | claim | source | status | fix |
|---|---|---|---|---|
| L249 | Whole Ur III 0.86–0.88 | S2 Part 1 | OK | |
| L250 | Reigns 0.62–0.72; collections 0.55–0.62 | S2 | OK | |
| L251 | +0.16 to +0.31, every gate | S2 | OK | |
| L252 | CDLI +0.17 / +0.22 | S2 | OK | |
| L254 | Latin 0.66–0.71 vs 0.52–0.58; +0.12 / +0.14 | S2 | OK | |
| L255 | OB gates 78% / 56% | S2 | OK | |
| L257 | "The place signal in Ur III lives in personal names." | RT2T noPN: U_reign +0.173 (98%), U_coll +0.159 (50%), G_reign +0.027 (86%), G_coll +0.174 (78%); CDLI U_reign +0.123 (98%) | OVERCLAIM | On the Umma reign floor, the gap after removing personal names (+0.173) is *larger* than after removing theophoric names (+0.102). Write "Personal names carry much of it: without them the gap falls below the strictest floor (Girsu reigns) but still clears the Umma reign floor." Report all four noPN rows. |
| L259 | noTGtheo min +0.102 / +0.093, gates 100% | RT2 (a) | OK | |
| L261 | noPN +0.027 (86%) / +0.028 (92%) | RT2 (a) | OK | |
| L262 | Size control +0.164, gate 90% | RT2 (a) | OK | The control is at the step-2 name-free size (68). The Girsu reign control (+0.213) has gate 76% and is left out; mention it. |
| Table 2 | +0.158/+0.165; +0.137/+0.126; +0.102/+0.093; +0.027/+0.028; +0.052/underpowered | RT2 A1/A2 table | OK | Add a column with the *largest* gated gap so readers see that noPN still clears Umma floors. |
| L283 | 0.599 vs 0.590, Δ +0.009 | S2 | OK | |
| L284 | Girsu reigns 0.698 > 0.604, gate 62% | S2 | OK | |
| L285 | Strict tagging +0.052, gate 80% | RT2 (a) | OK | Add p_floor 0.078: this is not significant either. |
| L286 | Gaps −0.09 to +0.05 | RT2 safe wording | OK | |
| L289 | nita kal-ga (Šulgi, Amar-Suen) vs lugal kal-ga (Šu-Suen, Ibbi-Suen) | RT2 (a) | OK | Matches the source. It needs an Assyriological citation (RIME 3/2) and the exceptions (5 late legends). |
| L293 | Ur III kept tokens 0% / 4% names | RT2 audit | OK | |
| L294 | Latin 42% / 22% | RT2 audit | OK | |
| L296 | noUNIT +0.084 / +0.163 | RT2 (a) | OK | |

### Results 3.3: the bound

| loc | claim | source | status | fix |
|---|---|---|---|---|
| L306 | 99.8%, 1.86, 36% of tokens | RT2T A3 | OK | |
| L307 | Ur III-like load excluded in every pool and form | RT2 A3 | OK | |
| L308 | Real-frequency names compatible on "at most 30%" | RT2T A3 | OVERCLAIM (dup) | Grid issue, as at L54. |
| L309 | Invented stocks 10%, or 20% for two-sign names in ICIT seals | RT2T A3 | OK | Same grid caveat (0.1 → 0.2 → 0.3). |
| L310 | Step 1 gave 20–30% | S1 reverse power | OK | |
| L311 | Tighter for invented (10–20%), same for real (30%) | RT2 A3 | OK | |
| Fig. 2 | Panel A power curves; panel B A3 curves | S2 and RT2 results.json | OK | Values match. Panel A plants in "Harappa seals", but one pool is seals + sealings. Panel B leaves out ICIT seals + sealings and the r = 0 baseline (about 50%); add both. |

### Results 3.4: limits

| loc | claim | source | status | fix |
|---|---|---|---|---|
| L328 | Sealings 0.613 / 0.608; +0.104 / +0.120 | S2 | OK | |
| L329 | Strict de-dup +0.091 / +0.167 | RT2 (d) | OK | |
| L330 | 367 complete sealings, 162 strings, 49 impressions | RT2 (d) | OK | Add "Harappa" before "367" for clarity. |
| L332 | Cross-object gates 2–4% | RT2 (d) | OK | |
| L333 | Descriptively leans toward format | RT2 (d) | OK | |
| L337 | Tablets 0.774 | S2 | OK | Say "ICIT". |
| L338 | 197 of 299 copper | S2 | OK | |
| L339 | Moulded +0.150, power 96% | RT2 (d) | OK | |
| L340 | 42 moulded at MD; Harappa late series | RT2 (d) | OK | |
| L343 | Chanhu-daro most separable | S2 | OK | |
| L344 | +0.13 to +0.17 above floor and null; power 96–98% | CD T0 | OK | |
| L345 | q = 0.06 vs bar 0.05 | CD T0; CD prereg | OK | Not reconciled with Methods L155 (q_floor ≤ 0.10). Under that rule both Harappa pairs have p_floor 0.005 (Part C, S4). |
| L346 | Same 40-odd seals | CD | OK | |
| L350 | 1 of 50 seals at Jhukar levels | CD | OK | |
| L351 | Strict de-dup +0.16 to +0.21 | CD T2 | OK | |
| L352 | Drop Square 9/D: +0.13 to +0.18 | CD T5 | OK | The ICIT rows are unchanged pools (+0.176 and +0.129). Say the M77 range is +0.13 to +0.14. |
| L353 | Unicorn only keeps most of it | CD T4 | OK | |
| L354 | About half from a few signs, mainly M93 | CD T3b | OK | |
| L355 | M93 on 20% of Chanhu-daro seals, ends 16% | CD sign profile | OK | |
| L356 | 0 of 251 Harappa, 0 of 1,026 MD seals | CD sign profile | OK | |
| L357 | Without these signs +0.06 to +0.08 | CD safe wording | OK | |
| L360 | M93 as a Chanhu-daro end mark "appears not to have been reported before" | LIT §4, §7 | UNTRACEABLE | The novelty rests on sources not read: M77's own concordance tables (by site), Fuls's site-frequency work, Wells 2011 and Yadav 2013. Check the M77 concordance (on disk) and CISI photos first, or drop the claim. |
| L361 | Depth split 17 per side, gates 26% / 16% | CD T1b | OK | |
| L363–364 | Small sites "never differ"; "power of 16–84% at q = 0.15" | S2 Part 2 table | MISMATCH | At q = 0.15 those pairs have power 48–96%. The 16 and 84 are from the q = 0.10 column (S2's own summary line has the same error). Several "underpowered" pairs pass the gate and fail only on q, with Δ ≥ 0.05: Harappa–Kalibangan M77 +0.125 (96%), Harappa–Dholavira S+S +0.109 (92%), Harappa–Lothal M77 +0.068 (90%). Call these "inconclusive", not "underpowered". |
| L365 | MD–Dholavira "same" +0.047 | S2 | OK | |
| L366 | Small-site floors 0.32–0.40 | S2 L29; S2 footnote and RT2 (c) say 0.32–0.47 | MISMATCH | Write 0.32–0.47. |
| L367 | Every small-site "differs" flips under the null | RT2 (c) | OK | |
| Fig. 3 | Pair Δ values on the map | S2 results.json | MISMATCH | Values match, but the legend reads "powered (gate passes)" vs "underpowered (*)". The dashed or asterisked set includes high-power pairs (MD–Chanhu-daro 98%, Harappa–Dholavira 92%) that are inconclusive on q. Harappa–Chanhu-daro is drawn thick, solid and without an asterisk, which shows the "differs" that the text disowns. Use the verdict names, and mark that pair as "differs vs floor, not vs null". |

### Results 3.5: Recchia

| loc | claim | source | status | fix |
|---|---|---|---|---|
| L383 | Bot challenge, not circumvented | RR limits | OK | |
| L386 | 1,823 vs 1,936; 716 vs 723 | RR | OK | |
| L389 | 45th of 120, p = 0.38; label null p = 0.61 | RR | OK | |
| L390 | Held across dimensionality, "weighting", ICIT and de-dup | RR sensitivity table | OVERCLAIM | No alternative term weighting was run; the variant is unit-length document vectors. Write "normalisation". (RR's own safe wording has the same slip.) |
| L391 | Sealings p = 0.025, geography p = 0.54 | RR | OK | |
| L395 | 30% at 15%; 80% only at 20% | RR planted gradient | OK | |
| L399 | 0.062 vs 0.062; 0.062 vs 0.067 | RR | OK | Add that 48% of between draws exceed the within q95. "Edge" is generous. |

### Discussion and limitations

| loc | claim | source | status | fix |
|---|---|---|---|---|
| L410 | 99.8%, 1.86 names per legend | RT2 A3 | OK | |
| L419 | "cannot be on more than about 30% of seals" | RT2 A3 | OVERCLAIM (dup) | Grid. |
| L422–423 | Cores: 34% single sign; 80% of signs stand alone | README finding 10 | OVERCLAIM | The numbers match, but README marks this finding "formal verdict inconclusive" and the most sensitive to transcription (passes in 3–9 of 10 noisy runs). Cite typology/core_semantics RESULTS with that caveat, or drop it. |
| L438–442 | LB 0.904; hand groups 0.883 vs 0.876, 0.861 vs 0.886; 0.524 held out | S1 A1; RT1 | OK | |
| L450 | 0.49 vs like-for-like 0.55 | RT0 | OK | |
| L458 | 10% stock found about half the time | RT1 attack 6 (47%) | OK | |
| L462 | Half of HR+VS findspots unconfirmed | RT1 attack 4 | OK | |
| L467 | Name-free verdict on one split at exactly 80% | RT2 limits | OK | |
| L472 | LB split into syllabic signs 0.86 | S1 A9 | OK | |
| L479 | Minimum p 0.020 at 50 draws | RT2 limits | OK | |

### Safe-wording and do-not-write checks

| list | item | paper | result |
|---|---|---|---|
| RT2 do-not-write | "Indus seals behave like name-free legends" / "name-free legends carry no place" | L287 says so explicitly | complies |
| RT2 | "tablet gap is a copper artefact" | L339–341 | complies |
| RT2 | "sealings show a place difference" | L331, L335 | complies |
| RT2 | Latin name-free numbers | L297 | complies |
| RT2 safe wording | "the site signal sits in personal names" | L51, L257 | The paper copies RT2's safe sentence, but RT2's own table (noPN on Umma floors) does not support it unqualified. **The safe wording itself overclaims; fix both.** |
| S2 do-not-write | "uniform across all sites", "no spatial structure at any scale" | L368–369 | complies. The **title** ("Two cities, one sign stock") is borderline, because sealings and tablets differ; consider "Two cities, one seal vocabulary". |
| S2 | "readable corpora separate their sites even without names" | not written | complies |
| RT1 | Linear B as place evidence | §4.2 uses it as a negative lesson | complies |
| RT0 | "unusually uniform" as a general fact; 0.885 range; proto-cuneiform as city control | not written | complies |
| CD | "Chanhu-daro differs"; "period excluded" | L347, L361 | complies |
| RR | "does not replicate" without power caveat; "no geographic information"; "identical in LSA space" | L394–399 | complies |

---

## Part B: referee reports

### B1. Referee 1: Indus archaeologist and epigrapher

**Summary.** The authors train a naive Bayes classifier on sign and sign-pair presence in Indus seal texts and ask whether it separates Mohenjo-daro from Harappa better than it separates two halves of Mohenjo-daro. It does not, in M77 or ICIT. The same machinery separates Ur III and Latin legends by city, and a planted-name exercise is used to argue that most Indus seals cannot carry city-specific names. Sealings, tablets and Chanhu-daro are reported as exceptions.

I am sceptical of computational work on this script, and I approached the paper expecting the usual problems: a corpus treated as a bag of tokens, sign lists taken on trust, and context ignored. The authors have done more than most. They separate object types, check M77 locus codes against the field registers, and are candid about Chanhu-daro. But the archaeology is still thin where it matters.

**Major issues.**

1. *"Two editions" are not two samples.* ICIT incorporates the objects published by Mahadevan and in CISI. Agreement between M77 and ICIT shows robustness to sign-list choice, not replication on new material. The paper should give the overlap in objects and stop calling the second edition a replication. The Parpola (CISI / Koskenniemi–Parpola) sign list is also missing from the "five sign lists"; the lists come from two editors only.
2. *Chronology is not controlled.* Most Mohenjo-daro seals come from the upper, late Mature Harappan levels that Marshall and Mackay cleared. M77's Harappa seals are largely Vats's, from poorly stratified contexts. ICIT adds HARP material phased 3A–3C. A null between cities could hide opposing period and place effects, and the depth floor (0.46) that would make the cities look different is set aside on a statistical argument. I want a period-matched comparison where phasing allows it: HARP periods against Mohenjo-daro by depth band.
3. *Seals vs sealings is the wrong way round for a place question.* A seal found at a site is a discard or a loss. A sealing records a seal *in use*, sometimes on goods from elsewhere. If any object type tells you about local practice, it is the sealings, and they differ. The paper treats the seal null as the result and the sealing difference as a limit. At minimum, the discussion should say that the place-of-use evidence points the other way, and why it is discounted (repetition: 49 impressions of one seal).
4. *Motif and field symbol.* Sign sequences correlate with the field symbol, and the unicorn share differs by site (Ameri, as cited by Petrie). The Chanhu-daro unicorn-only control is a good start. The main Mohenjo-daro–Harappa test should also be run within unicorn seals, so motif mix cannot mask or create a text difference.
5. *M93 at Chanhu-daro needs an epigrapher, not a classifier.* M77 took Chanhu-daro texts from Mackay's 1943 plates. A sign that occurs on ten Chanhu-daro seals and none of 1,277 seals from the two cities is exactly what a single report's drawing conventions could produce. Check every M93 against the CISI photographs. Then check whether M93 stands in the terminal slot that a common sign (M342?) fills elsewhere; removing M342 *raised* separation from Harappa (−0.025 in CD T3). If M93 is a local graphic variant of a terminal sign, that is a regional carving variant: the very thing the paper says it cannot test (L459). That would be a finding worth reporting properly.
6. *Within-city floor.* DK vs HR+VS mixes excavator, method and date, as the authors note. Gokhale & Ameri (2026, in your bibliography but not cited) put more than 15% of all seals in DK-G South, so the area floor may be one block against the rest. Report the floor without DK-G.

**Minor issues.** Mahadevan & Bhaskar (2018) on toponyms and Yadav (2013) on site sensitivity are named in Limitations but not cited, and both must be read. Rao et al. (2009) on West Asian seals is in refs.bib but never cited, and it is the obvious Indus-internal positive control. The title overstates the result given sealings and tablets. "Copper tablets" should be called a Mohenjo-daro object class, not a subtype artefact. The Jhukar argument relies on Mackay 1943: 143; cite the plate as well.

**Recommendation: major revision.**

**Three changes that would most move me:** (1) verify M93 on photographs and test it as a local variant of a common terminal sign; (2) run the main test within unicorn seals and, where possible, period-matched; (3) give the M77–ICIT object overlap and stop presenting the two editions as replication.

### B2. Referee 2: Assyriologist and epigraphist (Ur III seals, Latin instrumentum)

**Summary.** The readable comparisons carry much of the paper: Ur III seal legends from Umma and Girsu, and Latin owner and maker marks from Britannia and Germania, separate by place well above within-place floors. The red team then strips name classes to locate the signal. I was asked whether the readable data were handled fairly. Mostly yes, but the paper reads the Ur III result too personally and the Latin result too simply.

**Major issues.**

1. *"Personal names" includes the governor.* Ur III seal legends are of two main kinds. One is the plain owner seal (PN, dub-sar, dumu PN₂). The other is the dedicated seal, where the owner is the servant of the ensi₂ or the king (*arad₂-zu*, *in-na-ba*). In the second kind the patron's name is a personal name, but it is a place marker by construction: Umma and Girsu each had their own governor. A "place lives in personal names" result that does not separate *owner* names from *patron* names conflates personal identity with provincial office. Split the PN tag by legend slot (owner, father, patron), and rerun noPN with only owner and father names removed.
2. *The text overstates the noPN result.* RT2's own table shows that legends without personal names still separate Umma from Girsu above the Umma reign floor (+0.173, gate 98%; CDLI +0.123). They fail only the Girsu reign floor, which is high because of the royal epithet change. That supports "personal names carry much of the place signal, and without them place and date cannot be separated". It does not support "the signal lives in personal names".
3. *Between-city is also between-archive.* Most Umma and Girsu tablets came through the antiquities market in large lots. Museum collections stand in for archives only loosely (BM vs Yale, BM vs Istanbul L). The Ur III "between" therefore includes archive and scribal-office differences that the Indus "between" (two excavated cities) does not. The paper should say that the reference contrast is between-archive and between-city at once, and that random halves (+0.36 to +0.40) are not a fair floor for it.
4. *Reign is the date of the tablet, not of the seal.* Seals stayed in use across reigns, and reign labels come from the sealed tablet's year name. That is fine as a date floor, but the royal-formula explanation (nita kal-ga vs lugal kal-ga) should be checked against the inscriptions (Frayne, RIME 3/2) and limited to royal-dedication seals. The source itself notes 5 late *nita kal-ga* legends.
5. *Latin instrumentum mixes place of use, place of make and army deployment.* Tile stamps of legions record where units were stationed. Potters' stamps on terra sigillata record where the pot was made, not where it was found. Graffiti owner marks are local. "Germania" here is defined from the modern country, not a Roman province (BENCH caveat), and the within-floors are modern German states and a military north vs civil south in Britannia. The Latin result is a mix of personal, military and trade signals. Report it by sub-genre (stamps vs graffiti), or at least drop sigillata and legionary stamps and report what remains.
6. *Tagger audit.* The Latin audit (42% of "name-free" tokens are names or unclear) is honest, and limiting Latin to whole legends is right. For Ur III, theophoric detection relies on the {d} determinative inside a PN. Names built on divine elements written without the determinative, and some Lagaš names, will be missed. A 50-token audit of *kept* tokens is too small to estimate a leak rate below about 6%.

**Minor issues.** Give the ORACC project(s) used, and the CDLI seal-ID coverage: how many impressions fall back to P-number grouping? Grouping by P-number lets one seal's impressions sit in different folds, inflating both between and within. "Umma{ki}" and "Šara" are good examples of leaks; add Girsu's (lagaš{ki}, Ba-ba₆, Nin-ĝir₂-su). Old Babylonian (Nippur vs Isin) is too small to mention in the abstract-level argument. The first benchmark's Puzriš-Dagan vs Nippur pair (a different kind of contrast, institution vs city) could serve as a third Ur III pair.

**Recommendation: major revision.**

**Three changes that would most move me:** (1) split personal names by slot (owner, father, patron) and rerun the noPN test; (2) rewrite the Ur III claim to match the full noPN table and call the contrast between-archive as well as between-city; (3) split Latin into stamps and graffiti, or drop sigillata and legionary stamps, and report what remains.

### B3. Referee 3: computational and statistics reviewer

**Summary.** The paper's central claim is an *equivalence* claim: Mohenjo-daro vs Harappa AUC equals a within-city floor within ±0.05. It is supported by median AUCs over 50 subsampling draws, a power check on planted stocks, and a series of pre-registered red teams. The workflow (frozen pipeline, matched n, own floors, null, power gate) is better than most in this area. The inference does not yet support the strength of the wording.

**Major issues.**

1. *No uncertainty on Δ, and no equivalence test.* Δ is a difference of two medians over draws. The draws subsample one finite pool. The Harappa side is nearly the whole pool each time (200 of about 200–232), so the spread across draws is Monte Carlo variation of the resampling, not sampling uncertainty. The step-1 caveat says so ("draw ranges understate the uncertainty"). For orientation: the null SE of an AUC at 200 per class is √(401/(12·200·200)) ≈ 0.029. A difference of two such AUCs has an SE of about 0.04 before correlation, so a 95% interval is around ±0.08, wider than the ±0.05 margin. "Same" is defined as Δ < 0.05 with power ≥ 80% (PR2 L86). That is not an equivalence test. **Required:** a bootstrap over texts at the pool level (resample both pools with replacement, rerun the whole between/within procedure), a 90% CI for Δ, and a TOST against ±0.05. If the CI is wider than the margin, say "no difference detected" instead of "same".
2. *The p_floor statistic is non-standard.* p_floor = share of within *draws* ≥ the between *median* (s2.py L452). This compares a median with the spread of single draws, and inherits the understated variance. Use the bootstrap distribution of Δ, or a label permutation on the full pool.
3. *The sub-0.5 floors have a known cause.* Pooled out-of-fold AUC under the null is biased below 0.5 at small n (the known negative bias of pooled cross-validated AUC), regardless of the `clean()` step. The paper attributes the bias to the removal of shared strings. Cite the general result, and consider per-fold AUC.
4. *`clean()` filters on the labels.* Dropping every string found at both sites, before CV, is label-dependent preprocessing. It removes the most shared texts in exactly the comparison being scored. For the Indus null this biases toward separation, which is conservative. For the reference positives it inflates separation. Planted names are inserted *after* `clean()` (rt2.py L505), so planted strings that collide across sites are not removed, while real ones would be. State this, and report one reference condition without `clean()`.
5. *The power check covers one kind of effect.* The planted stock replaces tokens with 20 common signs: a presence/absence signal that Bernoulli NB detects well. Real regional differences could be frequency shifts among shared signs, positional preferences or pair order, and the power check says nothing about those. Add (a) at least one diffuse planted effect, such as a small Dirichlet reweighting of existing sign frequencies at one site; (b) logistic regression, which lib.py already supports; and (c) a classifier-free test, such as a permutation test on the Jensen–Shannon divergence of sign and pair frequencies against within-city halves.
6. *The planted-names bound is too coarse and probably too tight.* The grid is 0.05, 0.1, 0.2, 0.3, 0.5, so "at most 30%" means "excluded at 50%, not at 30%". The exclusion criterion (95% of draws above the observed gap) uses the same understated draw variance as point 1, which makes exclusion too easy. The ur3emp spelling maps each name to a random pair of common signs, so unrelated names can collide across cities: "realistic" names are partly made shared by accident. Rerun at r = 0.35, 0.40 and 0.45, add r = 0, and report the bound with bootstrap variance.
7. *The verdict labels conflate cases.* "Underpowered" covers both low power and "Δ ≥ 0.05 with q > 0.10 at high power". Harappa–Kalibangan (M77, Δ +0.125, power 96%) and Harappa–Dholavira (S+S, +0.109, 92%) are not underpowered; they are inconclusive *leaning different*. The text's "never differ" and the 16–84% figure hide this. Use four labels: differs / same / inconclusive / underpowered.
8. *Pre-registration claims.* The hashes were committed in the same commits as the results, so the "public file before scoring" claim cannot be checked by a reader. The Indus number was known before every prereg (BENCH). The Chanhu-daro follow-up raised its bar from q_floor ≤ 0.10 (step-2 rule, which Chanhu-daro met against Harappa in two editions) to q_chance ≤ 0.05, after seeing step 2. All eight runs were designed and scored within one day by agents from one model family. None of this invalidates the work, but the paper should describe it plainly. As written, "pre-registered" will read as more protection than it gave.
9. *Choice among floors.* The paper reports random halves as the primary Indus floor in step 2, the area split in step 1, and discounts the depth floor (which gives +0.09). Give one table of every floor tried, with Δ and its CI, and say which was primary in which prereg.

**Minor issues.** min_df is computed on the whole draw (transductive; label-free but worth stating). The letter q means both stock share and BH q-value. AUCs at 19–60 per side (small sites) have intervals of about ±0.1–0.15 and should not be mapped (Fig. 3). BH across the four Chanhu-daro pairs is fine under positive dependence, but say why. Translate AUC gaps into a classifier-free scale (RT0's "local share") so readers can judge size. State the grouping unit per corpus.

**What a tie within ±0.05 can support.** At these sample sizes it supports "no difference large enough to be detected by this pipeline; a planted presence-type stock of 15% of tokens would have been detected". It does not support "the cities write alike", or any claim about effects smaller than about 0.08 AUC, until a CI says otherwise.

**Recommendation: major revision.** I would reject in the current form if the equivalence language stays without intervals.

**Three changes that would most move me:** (1) a pool-level bootstrap CI for every headline Δ, with TOST against ±0.05, and the wording matched to the result; (2) a classifier-free divergence test plus one diffuse planted effect and one alternative classifier; (3) a finer, variance-honest planted-names grid, and a plain account of what was blind and when the hashes became public.

---

## Part C: synthesis

### Must fix before submission

| # | fix | type | what exactly |
|---|---|---|---|
| M1 | Ur III "place lives in personal names" (abstract L51–52, L257, Fig. 1 label and caption, Table 2) | rewording now, analysis later | Rewrite to match the full noPN table: three of four floors are still cleared, and only the Girsu reign floor fails. Relabel Fig. 1 as "all names removed". Add a "largest gated Δ" column to Table 2. New analysis (S1 below) can then strengthen it. Also correct RT2's safe wording. |
| M2 | Planted-name bound "about 30%" (L54, L105, L308, L419) | analysis | Rerun A3 at r = 0, 0.35, 0.40 and 0.45 for all three pools and forms. Until then write "names on half of seals or more are excluded; 30% is not". |
| M3 | Equivalence wording ("It cannot", "same", "tie within ±0.05") | analysis | Pool-level bootstrap (resample texts with replacement, rerun between and within, at least 200 reps) for the three Mohenjo-daro–Harappa Δs (floor and null). Report 90% CIs and TOST at ±0.05. If CIs exceed the margin, say "no difference detected" and give the CI. |
| M4 | Pre-registration description (L175–184, L176, Use of AI) | rewording | Hashes became public with the results. The Indus number was known before every prereg; only references and red-team attacks were blind. The CD bar changed from q_floor ≤ 0.10 to q_chance ≤ 0.05. All runs happened in one day. |
| M5 | Small sites (L363–366) and Fig. 3 | rewording and figure | Power at q = 0.15 is 48–96%, not 16–84%. Floors are 0.32–0.47. Name the pairs that are inconclusive at high power (Harappa–Kalibangan, Harappa–Dholavira, Harappa–Lothal). Fix the Fig. 3 legend; mark Harappa–Chanhu-daro as "differs vs floor only". Fix S2's summary line too. |
| M6 | Abstract precision | rewording | "every structural within-city floor"; "99.8% of legends"; drop "It cannot." |
| M7 | Methods gaps (L142, L149) | rewording | Grouping unit per corpus (Indus text, Ur III seal id, Latin text, Linear B tablet); the 227 per-side cap. |
| M8 | Novelty: M93 end mark (L360) and "not tested against a calibrated baseline" (L45) | reading, small analysis | Check M77's concordance tables (on disk) and ICIT for M93 by site and object type. Read Yadav 2013, Fuls's site frequencies and Wells 2011, or drop the M93 novelty sentence and hedge L45. |
| M9 | README finding 10 in the Discussion (L421–426) | rewording | Cite the typology and core_semantics RESULTS with their "inconclusive" and transcription-sensitivity caveats, or remove the paragraph. |
| M10 | Depth floor (L232–236) | rewording | Say that +0.089 exceeds the 0.05 margin and is exploratory, and give the reason for discounting it in the main text. |

### Should fix

| # | fix | type | what exactly |
|---|---|---|---|
| S1 | Owner vs patron names in Ur III | analysis | Tag PN tokens by legend slot (owner, dumu-father, arad₂-zu patron or ensi₂). Rerun noPN removing (a) owner and father only, (b) patron only. |
| S2 | Classifier robustness and effect form | analysis | Logistic regression (lib.py `model="lr"`) for the three Mohenjo-daro–Harappa pools. A Jensen–Shannon permutation test on sign and pair frequencies vs MD halves. One diffuse planted effect (Dirichlet reweighting of existing sign frequencies) in the power check. |
| S3 | M93 as a local variant | analysis and epigraphy | Check every M93 against CISI photographs. Test complementary distribution: is M93 at Chanhu-daro in the terminal slot that M342 (or another terminal) fills at the big cities? |
| S4 | Chanhu-daro bar | rewording | State both rules side by side. By the step-2 rule (q_floor ≤ 0.10) Chanhu-daro "differs" from Harappa; by the stricter follow-up rule (q_chance ≤ 0.05) it does not. Explain why the stricter rule governs. |
| S5 | Edition independence | small analysis, rewording | Count the M77–ICIT object overlap for MD and Harappa seals; call the second edition a robustness check, not a replication. |
| S6 | Motif and chronology controls | analysis | Rerun Mohenjo-daro–Harappa within unicorn seals. Where phasing exists (HARP periods, MD depth bands), run a period-matched comparison. |
| S7 | Area floor without DK-G | analysis | Rerun the DK vs HR+VS floor without DK-G South (cite Gokhale & Ameri 2026). |
| S8 | Latin sub-genres | analysis | Split EDH instrumentum into stamps and graffiti owner marks; drop terra sigillata and legionary stamps and report what remains. |
| S9 | Between-archive framing for Ur III | rewording | Say that the Ur III contrast is between archives as well as between cities. |
| S10 | Citations | rewording | Cite Rao et al. 2009 (in refs.bib, not cited) and Gokhale & Ameri 2026 (in refs.bib, not cited). Add bib entries for Yadav 2013, Mahadevan & Bhaskar 2018 and Oakes 2019 once read. Cite RIME 3/2 for royal epithets, and the pooled-CV AUC bias literature. |
| S11 | Recchia "weighting" (L390) | rewording | Write "normalisation", and add "48% of between draws exceed the within q95". |
| S12 | `clean()` asymmetry | rewording, optional analysis | State the label-dependent filtering and that planted names are inserted after it. Optionally rerun one reference condition without `clean()`. |
| S13 | Title | rewording | "one sign stock" is broader than "seals at two cities"; consider "Two cities, one seal vocabulary". |

### Could fix

- Fig. 2B: add r = 0 and the ICIT seals + sealings pool; label panel A "Harappa side" rather than "Harappa seals".
- Rename the stock-share q to avoid clashing with BH q.
- Report AUC gaps on RT0's classifier-free "local share" scale as well.
- Add keys to the oracc, cdli, edh and damos bib entries (4 BibTeX sort warnings in main.blg).
- Linear B: change "does not carry place" to "cannot be shown to carry place beyond its scribes" (L182).
- Report the per-corpus count of Ur III impressions grouped by P-number because no seal ID was available.

### Novelty claims the literature note does not support

1. **"The use of M93 as a Chanhu-daro end mark appears not to have been reported before" (L360; LIT §4 and §7).** The sources most likely to report it were not read: M77's own concordance (which tabulates every sign by site), Fuls's site-specific ICIT frequencies and Catalog (2023), Wells 2011, and Yadav 2013. Mackay's silence covers only 1943. Not supported until those are checked.
2. **"The claim has not been tested against a calibrated baseline" (L45).** LIT lists Yadav 2013, "Sensitivity of Indus Script to Site and Type of Object", as directly on this question and not accessed. Hedge, or read it first.
3. **LIT §7 item 3** says the references' "name-free text does not [separate]". The paper correctly does not repeat this, but the literature note is out of date and contradicted by RT2; update it. Its headline numbers (Δ −0.033 to +0.042, "20–30%" names, "Chanhu-daro does not beat its null, q 0.18–0.35") also predate RT2 and the Chanhu-daro follow-up.
4. **"Nothing we found in the prior work calibrates a site test this way"** (LIT §7 item 1, reflected at L75): acceptable as hedged, given that Yadav 2013 and Oakes 2019 are unread.
5. **Readable references**: LIT correctly states the Ur III and Latin floor comparisons as a gap, not a finding. The paper does not overclaim here.

### Notes on verification

- Figures: rerun with `.venv/bin/python -I` under `nice -n 20 taskpolicy -b`. `_style.OUT` was redirected to a temp folder, so `latex/figures/` was not touched. All three PNGs came out byte-identical to the committed ones.
- Prereg timing: from `git log -- docs/prereg/HASHES.txt` against the commits that added each RESULTS.md.
- Code facts (grouping key, `p_floor` definition, planting after `clean()`, min_df on the full draw, `namefree` vs `noPN` definitions) come from `site_signal/lib.py`, `uniformity_benchmark/run.py`, `uniformity_paper/step2/s2.py` and `build2.py`, and `redteam_uniformity_step2/rt2.py`.
- The SE figure in B3 is the standard Mann–Whitney null SE. It is an orientation estimate, not a computed CI; M3 asks for the real one.
