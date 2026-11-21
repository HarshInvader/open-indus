# Review 2: "Mohenjo-daro and Harappa seal texts: no detectable place signal beyond a within-city floor" (revised draft, 2026-11-21)

Reviewer: review sub-agent (second round). Scope: `docs/paper/uniformity/latex/main.tex` (commit 938ba07) with refs.bib, main.pdf (14 pp., about 7,000 words) and the three figures. Checked against `experiments/uniformity_paper/revision/RESULTS.md` and `results.json`, every earlier RESULTS.md, results.json and table.md the paper cites, and the "safe wording" and "do not write" lists. Nothing was edited, committed, pushed or sent.

## Verdict first

The revision fixed what mattered most in round 1. The tie now has pool-level bootstrap intervals and a TOST. The name bound uses a finer grid with an r = 0 baseline. The Ur III name claim rests on a role-by-role analysis. Pre-registration is described honestly. Latin is demoted. **The numbers are almost all right: 116 of 130 audited claims match their source exactly. No number is wrong in a way that changes a conclusion.**

What still needs work:

1. **Three wording errors in the headline claims.** (a) "drops it below the strictest floor": the no-personal-names gap is +0.030 *above* the Girsu reign floor, and only falls short of the 0.05 margin. The abstract, Results and the Table 2 caption all say "below". (b) "Bound any difference to about 0.11 AUC" should say what it is: a one-sided 95% upper limit for this pipeline's AUC gap. (c) "Above every within-city floor in every bootstrap interval" should say "all six structural floors", because random halves were not bootstrapped.
2. **One small-site number is wrong.** "At 19–37 texts per side" (L366) describes pairs of two small sites. The pairs the sentence is about, small sites against Mohenjo-daro or Harappa, have 37–67 per side.
3. **Unfinished business flagged by TODOs.** Yadav 2013 is still unread. So are the Parpola page and RIME 3/2 for the royal epithets. The M77–ICIT object overlap count is missing, and the M93 photo check is pending. A journal would send back a paper with live TODOs on its central novelty claim (L48).
4. **Length and density.** At 14 pages and about 7,000 words, with a 280-word abstract carrying 20 numbers, this is not a short paper. Part D lists the cuts.

**The title and abstract are now close to the evidence. They overreach in three small places** (1a–1c above), plus one sentence in the Introduction (L99, "Indus seals therefore do not carry…"). None needs new analysis.

Figures: all three scripts were rerun into `/tmp/fig_rev2.nq08/` with `.venv/bin/python -I` under `nice -n 20 taskpolicy -b`, with `_style.OUT` redirected so `latex/figures/` was untouched. **All three PNGs came out byte-identical to the committed files.** I read every plotted value from the scripts and checked it against results.json (rows marked "Fig." below).

---

## Part A: number audit

Sources: REV = `experiments/uniformity_paper/revision/RESULTS.md` (REVJ = its results.json); S1 = `experiments/uniformity_paper/step1/RESULTS.md`; S2 = `experiments/uniformity_paper/step2/RESULTS.md` (S2J = results.json); RT0/RT1/RT2 = `experiments/redteam_uniformity{,_step1,_step2}/RESULTS.md` (RT2T = table.md); CD = `experiments/chanhudaro_followup/RESULTS.md`; RR = `experiments/recchia_rerun/RESULTS.md`; LIT = `docs/paper/uniformity/LITERATURE.md`. "L" = main.tex line.

**Counts: OK 116 · MISMATCH 6 · UNTRACEABLE 2 · OVERCLAIM 6 (130 rows; 5 rows marked "(dup)" repeat an issue found earlier, so 9 distinct problems).**

### Abstract

| loc | claim | source | status | fix |
|---|---|---|---|---|
| L48 | "to our knowledge… not been tested against a calibrated within-site baseline" | LIT §1, §9 (Yadav 2013 unread) | UNTRACEABLE | The hedge is correct, but the claim still rests on an unread paper that is directly on the question. Read Yadav 2013 before submission. |
| L51 | Two overlapping editions; Δ medians +0.01 to +0.03; every 95% CI includes 0 | REVJ boot MDHA_* d_floor: +0.017, +0.010, +0.034; 2.5th −0.079/−0.089/−0.060 | OK | |
| L52 | Equivalence within ±0.05 not established | REVJ tost_floor false ×3 | OK | |
| L52 | "the data bound any difference to about 0.11 AUC" | REVJ m_star_floor 0.101, 0.102, 0.107 (max of \|q5\|, q95) | OVERCLAIM | "Bound" reads as a hard limit. m* is the 95th percentile, a one-sided 95% upper limit, and it covers only differences this pipeline turns into AUC. Write "the one-sided 95% upper limit on the gap is 0.10–0.11 AUC". |
| L52 | Unicorn 0.13–0.14 | REVJ m* 0.143, 0.134 | OK | |
| L53 | LR and JSD agree, one family at the margin | REV R5 | OK | Matches the safe sentence. |
| L54 | Ur III "above every within-city floor in every bootstrap interval (lowest 2.5th percentile +0.107)" | REVJ boot REF_ur3_*, REF_cdli_*: 2.5th min 0.107 | OVERCLAIM | Six *structural* floors were bootstrapped. Random halves were not (they are larger anyway). Write "above all six structural within-city floors". This was REVIEW_1 M6, and it has come back. |
| L55 | Removing owners, patronyms or patrons one at a time leaves it above every floor | REV R3: all 4 ORACC + 2 CDLI gated, min +0.114 | OK | These are point estimates with gates, not bootstrap. |
| L55 | "only removing all personal names drops it below the strictest floor" | REV R3 noPN G_reign **+0.030** (CDLI +0.037) | MISMATCH | The gap is positive: it is above the floor, but under the 0.05 margin. Write "brings the gap on the strictest floor (two Girsu reigns) under the 0.05 margin". |
| L56 | Latin weaker, confounded | REV R1, R4, R5 | OK | |
| L58 | Invented stock on more than 25–35% "would have been detected" | REV R2 smallest excluded 0.25–0.35 | OK | Nit: this is *exclusion* (≥95% of replicates above the observed gap), not 80% detection (0.18–0.31). Say "excluded". The unit is legends; one pool includes sealings. |
| L58 | Real Ur III frequencies only at 40–50% | REV R2 ur3emp excluded 0.40 / 0.50 / 0.50 | OK | Add "upper CI beyond 0.50 in two pools", as Results L318 does. |
| L58 | 99.8% of Ur III legends carry a name | RT2 A3 | OK | Fixed since round 1. |
| L59 | Diffuse: 5–10% (variants), 20–30% (shift) | REVJ diffuse: variants 80% at share 0.05–0.10; shift at 0.20–0.30 | OK | |
| L60 | Sealings and tablets differ | S2 Part 2 | OK | |
| L60 | Chanhu-daro "leans apart but not beyond its bootstrap intervals" | REV R1 CD Δcons CIs all include 0 | OK | Awkward. Write "…but its bootstrap intervals include zero". |

### Introduction and data

| loc | claim | source | status | fix |
|---|---|---|---|---|
| L70 | Parpola 1994 as the standard statement | LIT §1, §10 | OK | Not quoted. The page TODO remains. |
| L72–73 | Yadav 2017 p. 19, pp. 20–21 | LIT §1 | OK | |
| L74 | Nair 2026, one positional statistic similar across sites | LIT (Nair 2026) | OK | |
| L79–80 | Wells 2015: sign 400 in 358 Harappa vs 79 MD texts, 325 on miniature tablets | LIT L76 | OK | |
| L82 | Kenoyer 2010 p. lvi; 2020 p. 219 | LIT §2 | OK | |
| L83 | Ameri via Petrie 2018: 467 | LIT L176 | OK | Correctly flagged. |
| L97 | Bootstrap bounds any difference to about 0.11 | REV R1 | OVERCLAIM (dup) | As at L52. |
| L99 | "Indus seals therefore do not carry an invented site-specific name stock on more than about a third of seals" | REV verdict 3 | OVERCLAIM | Stated as a fact about the seals, but it is a test result that depends on the model. Write "would have been detected had they carried…", as L321 does. |
| L106 | ICIT "transcribes most M77 objects again" | none (TODO L108) | UNTRACEABLE | The overlap count was never run. Count it (a small join on the concordance), or write "many". |
| L109 | 6203→ICIT 61.1 mismatch; 6204 and 6124 share 71.1 | REV R6 listing | OK | |
| L110 | Fuls 2024 p. 4: different object proportions | LIT L59 | OK | |
| L112 | No locus code contradicts the register; 101 of 198 unconfirmed | RT1 attack 4 | OK | Fixed since round 1. |
| L118 | 16 of 13,517 Umma texts with excavation number | S2 "Could not do" | OK | |

### Method

| loc | claim | source | status | fix |
|---|---|---|---|---|
| L130 | Binary sign + pair features, min_df 2, label-free | `site_signal/lib.py` | OK | |
| L131 | Bernoulli NB, grouped 5-fold ×3 | lib.oof_scores | OK | |
| L132 | Grouping unit per corpus; ORACC = one sealing on one tablet | `s2.py` L208/225 (`m{text_no}.{side}`, ICIT id); `build2.py` L133 (`{pid}.s{sn}`), L178 (CDLI seal id) | OK | Correct. (REVIEW_1 wrongly said ORACC grouped by seal id.) Consequence: in ORACC, impressions of one seal on different tablets can fall in different folds, which inflates Ur III AUCs. The CDLI check (L260) covers this. Say so in one clause. M77 groups by object *side*. |
| L134–137 | clean() uses the labels; planted names inserted after it | REVIEW_1 S12; rt2.py L505 | OK | |
| L139 | Smaller natural pool, capped at 227 | PR2 L14–15 | OK | |
| L141 | 30 / 50 / 200 draws | S1, S2, RT2, CD, PRREV | OK | Nit: bootstrap replicates use 5 + 5 draws each, and names use 60 replicates. Say "50 (step 2, red teams)" and describe the revision separately. |
| L145–147 | Rule; four labels (differs / not beyond / inconclusive / underpowered) | PR2; REVIEW_1 B3.7 | OK | |
| L149 | Pooled OOF AUC biased below 0.5 (Airola 2011) | refs.bib airola2011 | OK | |
| L151 | Δnull, Δcons definitions | prereg RT2 | OK | |
| L154–158 | Bootstrap: 200 replicates, independent resampling of between and within pools, copies keep group; TOST via 5th/95th | PRREV R1 | OK | See Part C3: independent resampling ignores the overlap of the MD side with the MD halves floor. That widens the interval, which makes "includes zero" easier to reach. It is not purely cautious. |
| L160–162 | Power and reference gate definitions | S2 | OK | q renamed to s, as asked in round 1. |
| L163 | Diffuse effects definitions | PRREV R2 | OK | |
| L165–167 | Name grid r = 0, 0.10, 0.20, 0.25…0.50; 60 replicates; detection and exclusion rules | REVJ names (keys 0.0–0.5) | OK | |
| L169 | LR and JSD; PS ≥ 0.80 | PRREV R5 | OK | |
| L173 | MD–Harappa known before every prereg; hash file public with results | BENCH; git log | OK | |

### Results 3.1: Mohenjo-daro and Harappa

| loc | claim | source | status | fix |
|---|---|---|---|---|
| L181 | Between 0.52–0.55, five lists, two editors | RT1 safe wording | OK | |
| L182 | Floor gaps +0.005 / +0.014 / +0.042 | S2J part2 | OK | |
| L182 | Null gaps +0.043 / +0.014 / +0.054 | RT2 (b) | OK | |
| L183 | Power 98–100% at 15% | S2J power['0.15'] 0.98, 1.0, 1.0 | OK | |
| L186 | Medians +0.010 to +0.034; lower bounds −0.060 to −0.089 | REVJ boot | OK | |
| L187 | No pool passes TOST | REVJ | OK | |
| L188 | m* 0.101–0.107 | REVJ | OK | |
| L189 | "bound any difference to about 0.11 AUC" | REVJ | OVERCLAIM (dup) | As at L52. |
| L192 | LR +0.027, +0.013 | REVJ alt | OK | |
| L193 | LR sealtype +0.050, p 0.059; NB +0.042, p 0.078 | REVJ alt; S2J p_floor 0.0784 | OK | |
| L194 | JSD PS 0.28 / 0.28 / 0.68; power 88–100% | REVJ alt jsd_ps 0.276, 0.283, 0.676; power 0.98, 0.88, 1.0 | OK | Nit: sealtype jsd_p_b is 0.037. Report it, so readers see the margin is not only LR's. |
| L195 | Unicorn +0.050 / +0.049, p 0.137, power 98/96, CIs | REVJ unicorn, boot UNI_* | OK | |
| L196 | Unicorn bound 0.13–0.14 | REVJ | OK | |
| L199 | DK vs HR+VS 0.537 vs 0.517, Δ −0.020 | RT1 | OK | |
| L200 | −0.007; −0.006 | RT1 | OK | |
| L202 | Depth floor 0.464; +0.089 | S1 X_C8 − X_C2 | OK | |
| L203 | Against 0.5 the cities sit +0.05 higher | 0.553 − 0.5 | OK | |
| Table 1 | 10 Indus rows (Δ, CI, n) | REVJ boot d_floor / d_null; RT1; S1 | OK | All 30 cells match. |
| Table 1 | 7 Ur III rows | REVJ boot; S2J part1 G_rand +0.355, U_rand +0.404 | OK | |
| Table 1 | 2 Latin rows, 4 Chanhu-daro rows | REVJ boot | OK | The CD rows show Δfloor, while the text (L349) quotes Δcons. Say so in the caption. |
| Fig. 1A | Plotted between/within | S2J part1/part2; RT1 `_gaps` | OK | Byte-identical regeneration. |
| Fig. 1B | Bootstrap d_floor 2.5 / 50 / 97.5 for 17 rows | REVJ boot | OK | |
| Fig. 1 caption | "Every Indus interval… includes zero. Every Ur III interval lies above the margin. The Latin intervals include zero." | REVJ | OK | |

### Results 3.2: Ur III and Latin

| loc | claim | source | status | fix |
|---|---|---|---|---|
| L257 | Whole 0.86–0.88; reigns 0.62–0.72; collections 0.55–0.62 | S2J part1 (ORACC) | OK | CDLI whole is 0.853; say "ORACC". |
| L258 | Above all six structural floors, lowest 2.5th +0.107 | REVJ | OK | Here the paper correctly says "structural". |
| L259 | LR min +0.148; JSD PS 1.00, p 0.005 | REV R5 | OK | |
| L260 | CDLI one-per-seal gives the same pattern | S2 | OK | |
| L261 | BM-only gap ≥ +0.197 | REV R3 BM-only whole | OK | |
| L265 | Role tagger definitions | PRREV R3 | OK | |
| L266 | One role removed: above every floor, gates 100% | REV R3 | OK | |
| L267 | +0.136 (CDLI +0.114); +0.142 (+0.125); +0.189 (+0.178) | REV R3 | OK | |
| L268 | noOwnFath / noPrivate +0.085 / +0.077; CDLI +0.075 / +0.104 | REV R3 | OK | |
| L269 | "noPN +0.030 (CDLI +0.037), noAllNames +0.047 (+0.039) brings the gap below the strictest floor" | REV R3 | MISMATCH (dup) | The numbers are right; "below the floor" is wrong. Write "under the margin on the strictest floor". |
| L270 | Place names, gods, theophoric names removed: +0.102 or more | RT2 (a) | OK | |
| Table 2 | 10 rows × 4 cells | S2J; RT2T; REVJ roles | OK | All 40 cells match. |
| Table 2 caption | "Rows marked a fall below the Girsu reign floor" | REVJ roles G_reign +0.030, +0.047, +0.037, +0.039 | MISMATCH (dup) | Write "fall short of the 0.05 margin on the Girsu reign floor". |
| L299 | Name-free 0.599 vs 0.590 | S2J | OK | |
| L300 | nita kal-ga: 368 legends and 5 later | RT2 (a): "368 Umma legends" | OK | Add "Umma". The RIME 3/2 citation is still a TODO. |
| L303 | Latin +0.12 to +0.14; LR +0.143 to +0.151 | S2; REV R5 | OK | |
| L304 | CIs −0.026 / −0.046; JSD PS 0.00 | REV R1, R5 | OK | |
| L305 | Germania 182 of 191 stamps, 70 of 89 military | REV R4 counts | OK | |
| L306 | Classes: MIL/STAMP untestable, GRAF underpowered, REST +0.170 / −0.121 | REV R4 | OK | |
| L307 | 42% of kept tokens names/unclear | RT2 audit | OK | |

### Results 3.3: the bound

| loc | claim | source | status | fix |
|---|---|---|---|---|
| L312 | 99.8%, 1.86 names, 36% of tokens | RT2 A3 | OK | |
| L316 | Invented r80 18–31%; excluded 25–35% | REVJ names r80 0.178–0.313; r95 0.25–0.35 | OK | |
| L318 | ur3emp r80 36–50%; excluded 40–50%; upper CI >0.50 in two pools | REVJ r80 0.364–0.500; r95 0.40/0.50/0.50; r95_ci upper None for icit_seal, icit_sealtype | OK | |
| L320 | Baseline: 17–40% of replicates give Δ ≥ 0.05 at r = 0, "which is why the curves start well above zero" | REVJ detect['0.0'] 0.27 / 0.17 / 0.40 | MISMATCH (minor) | The number is right, but Fig. 2B plots `exceed_obs`, which starts at 45–55%, not `detect`. The text and the Fig. 2 caption ("start near 50%") describe two different metrics as "the curves". Say which is which. |
| L321 | "more than about a third… would have been detected; Ur III-like use on up to 40–50% would not" | REV verdict 3 | OK | Matches the safe wording. |
| L324 | Diffuse 5–10% / 20–30% | REVJ diffuse | OK | |
| Fig. 2A | Power curves at s = 0.10/0.15/0.20 | S2J part2 power | OK | |
| Fig. 2B | exceed_obs by r, three pools × three forms | REVJ names | OK | |
| Fig. 2C | Power by altered-token share | REVJ diffuse | OK | |

### Results 3.4: limits

| loc | claim | source | status | fix |
|---|---|---|---|---|
| L337 | Sealings 0.613 / 0.608; +0.104 / +0.120 | S2J | OK | |
| L338 | Strict de-dup +0.091 / +0.167 | RT2 (d) | OK | |
| L339 | 367 Harappa sealings, 162 strings, 49 impressions | RT2 (d) | OK | |
| L340 | Format test gates 2–4% | RT2 (d) | OK | |
| L343 | Tablets 0.774; 197 of 299 copper | S2 | OK | |
| L344 | Moulded +0.150, 96%; 42 at MD | RT2 (d) | OK | |
| L347 | CD +0.13 to +0.17, power 96–98%, q_chance 0.06 | CD | OK | |
| L348 | Step-2 rule: CD "differs" from Harappa in both editions | S2J part2: m77 q_floor 0.098, sealtype 0.074 | OK | |
| L349 | Δcons medians +0.088 to +0.126; all CIs include 0 | REVJ boot CD_* | OK | |
| L353 | M93 on 20% of CD seals; 0 of 251 HA, 0 of 1,026 MD | CD sign profile | OK | |
| L354 | All 11 M77 occurrences at CD (10 seals, 1 sealing) | REV R6 listing | OK | The novelty claim was correctly dropped. |
| L355 | W031 W032 final line: 5/59, 0/440, 0/1,352 | REV R6 | OK | Omission: LIT L111 records the *reversed* pair W032 W031 on 3 MD seals and 6 Harappa tablets. A reader will ask whether that is the same mark read the other way. Mention it. |
| L356 | Recodings leave Δcons +0.06 to +0.17 | REV R6: 0.061–0.166 | OK | |
| L357 | Drop: about 45% lower, +0.088 / +0.056 | REV R6 | OK | |
| L360 | 1 of 50 at Jhukar; gates 26% / 16% | CD | OK | |
| L361 | Mackay pp. 145–149, local seal-making, "one new sign" | LIT L189–201 | OK | |
| L363 | "Smaller sites are underpowered or inconclusive" | S2J: MD–Dholavira sealtype "same", Δ +0.047, power 90% | MISMATCH (minor) | One pair is gated "same". Write "underpowered, inconclusive or not beyond the floor". |
| L364 | Power 48–96% at s = 0.15 | S2J | OK | Fixed since round 1. |
| L365 | Inconclusive: HA–Kal +0.125 (96%), HA–Dhol +0.109 (92%), HA–Lothal +0.068 (90%) | S2J | OK | |
| L366 | "At 19–37 texts per side" | S2J n_side for small site × MD/HA: 37–67 | MISMATCH | 19–37 is the range for pairs of two *small* sites (S2 footnote). Write "37–67 per side". |
| Fig. 3 | Δ labels, gate/verdict line styles, † on HA–CD | S2J part2 icit_sealtype | OK | The legend uses the verdict names now. |

### Discussion, limitations, appendix

| loc | claim | source | status | fix |
|---|---|---|---|---|
| L379 | "any difference is below about 0.11 AUC" | REV R1 | OVERCLAIM (dup) | As at L52. |
| L381 | Almost every Ur III legend carries a name | RT2 A3 | OK | |
| L385 | Stock on more than a third "unlikely"; 40–50% not excluded | REV verdict 3 | OK | |
| L387–389 | Finding 10, inconclusive, transcription-sensitive | README row 10: typology 4/5, "formal verdict inconclusive" | OK | Fixed since round 1. README cites the typology prereg (4/5) and core_semantics (8/9); the paper gives only the former. Fine. |
| L392–394 | Kenoyer p. lvi; Jamison style groups cross sites | LIT | OK | |
| L396–398 | LB 0.904; 0.883/0.861 vs 0.876/0.886; 0.524 | S1 A1; RT1 | OK | |
| L409 | Bound at about 0.11 | REV | OK | Here it is framed as a limitation; fine. |
| L414 | Depth floor +0.089 | S1 | OK | |
| L421 | LB syllabic split 0.86 | S1 A9 | OK | |
| L423 | LR one pool "differs" +0.050, p 0.059 | REV R5 | OK | |
| L458 | "each hash line was committed together with that step's results" | git: revision prereg + hashes in f8c33a1 (21:27Z); first revision run 21:28Z (run.log); results commit ba88e25 at 22:16Z | OK (understated) | For the revision run this is no longer true: hashes were committed before any score existed. Say so. It is the one run a reader can check. |
| L460–463 | Known-before, CD bar change, revision known facts | BENCH; CD prereg; PRREV | OK | |
| L492–498 | Recchia: counts, 45/120, p values, "normalisation", 48% | RR | OK | "Weighting" was corrected as asked. |

### Safe-wording and do-not-write checks

| list | item | paper | result |
|---|---|---|---|
| REV not safe | "equivalent", "identical", "no difference" without floor | title and abstract use "no detectable… beyond a within-city floor" | complies |
| REV not safe | Latin as clean positive control | L303–307, L419 | complies |
| REV not safe | "M93 explains the Chanhu-daro difference" | L358 "part of the gap, not all" | complies |
| REV safe | Name roles: "only removing every name brings it below the Girsu reign floor (Δ +0.047)" | Paper says "all personal names" (+0.030), which is accurate, since noPN already fails | complies. **The REV safe sentence itself says "below the floor" for a positive Δ, and the paper copied that wording.** Fix both. |
| RT2 safe | "site signal sits in personal names" | not used; L271 "spread across all name roles" | complies. RT2 RESULTS.md still carries the stale sentence; mark it superseded. |
| RT2 do-not-write | name-free legends carry no place; tablets copper artefact; sealings show place; Latin name-free numbers | L301, L344, L341, L307 | complies |
| S2 do-not-write | "uniform across all sites"; readable corpora separate without names; tablet AUC as place | L367, L301, L343 | complies. S2 RESULTS.md L31 still says "16-84%"; fix the source. |
| RT1 do-not-write | LB as place evidence; "readable corpora separate" with LB | L396–401 | complies |
| RT1 do-not-write | "cities share a vocabulary while references don't" as a general contrast | L379–380 contrasts Indus with Ur III only; L419–420 says other seal corpora are untested | complies, narrowly. It now rests on one clean reference. |
| RT0 | "unusually uniform"; 0.49 as comparator; "across cities" as if all pairs tested | not written; title names two cities | complies |
| CD | "Chanhu-daro differs"; "separate scribal tradition"; "period excluded" | L346–360 | complies |
| RR | "does not replicate" without power; "no geographic information"; "identical in LSA space" | App. B | complies |

---

## Part B: REVIEW_1 items, resolution

**Tally: must-fix M1–M10: 8 resolved, 2 partly, 0 not. Should-fix S1–S13: 7 resolved, 5 partly, 1 not. Could-fix (6): 3 resolved, 3 not.**

### Must fix

| # | item | status | evidence |
|---|---|---|---|
| M1 | Ur III "place lives in personal names" | **resolved** | Role-by-role analysis (REV R3). Table 2 gives smallest and largest gated Δ. Fig. 1 relabelled "all names removed". The text now says "spread across all name roles". Residual: "below the floor" for +0.030 (Part A). |
| M2 | Name bound on a coarse grid | **resolved** | Grid 0, 0.10, 0.20, 0.25…0.50, 60 replicates, CIs on r80 and the exclusion rate (L165, L316–321). The r = 0 false-positive rate is reported (L320). |
| M3 | Equivalence wording | **resolved** | Pool-level bootstrap, 200 replicates, TOST, m* (L153–158, L185–189, Table 1). "It cannot" is gone. The title no longer says "one sign stock". Residual: "bound" (Part A). |
| M4 | Pre-registration description | **resolved** | L171–173 and App. A: known-before, hashes public with results, CD bar change, one day, agents of one model family. |
| M5 | Small sites and Fig. 3 | **resolved** | 48–96% (L364). Inconclusive pairs named (L365). Fig. 3 legend uses verdict names and marks HA–CD with †. Residual: new n-range error (L366). The source S2 RESULTS L31 is still stale. |
| M6 | Abstract precision | **partly** | "99.8% of legends" fixed; "It cannot" dropped. But "every within-city floor" (L54) still lacks "structural". |
| M7 | Methods gaps | **resolved** | Grouping unit per corpus (L132), cap 227 (L139). |
| M8 | Novelty (M93, L45) | **partly** | M93 novelty claim dropped and replaced with "can be read off the 1977 concordance" (L354). L48 hedged. But Yadav 2013 is still unread (TODO L48, L76, L425), and so is Wells 2011. |
| M9 | README finding 10 | **resolved** | L387–389 give "inconclusive" and the transcription sensitivity. |
| M10 | Depth floor | **resolved** | L201–204: +0.089, exploratory, beyond the margin, listed in Table 1. |

### Should fix

| # | item | status | evidence |
|---|---|---|---|
| S1 | Owner vs patron names | **resolved** | REV R3: noOwner, noFather, noPatron, noOffice, noOwnFath, noPrivate, BM-only. |
| S2 | LR, JSD, diffuse effect | **resolved** | REV R5 and diffuse; L59, L169, L191–194, Fig. 2C. |
| S3 | M93 as local variant; photos | **partly** | Merge test done (R6). Photo check is listed in HUMAN_LEADS but not done (TODO L359). The complementary-distribution test (M93 in the M342-final slot) was not run. |
| S4 | Chanhu-daro bar | **resolved** | L348 and App. A L461 state both rules. |
| S5 | Edition independence | **partly** | Wording fixed (L106–107). Overlap count not run (TODO L108). |
| S6 | Unicorn and chronology | **partly** | Unicorn done (R7, L195). Period matching not done; now stated as a limitation (L415). |
| S7 | Area floor without DK-G | **not** | Not run. Gokhale & Ameri 2026 is still in refs.bib but not cited. |
| S8 | Latin sub-genres | **resolved** | R4 class split (MIL, STAMP, GRAF, REST); Latin demoted (L303–307). |
| S9 | Between-archive framing | **resolved** | L118, L262, L416. |
| S10 | Citations | **partly** | Airola 2011 added; Yadav 2013 and Mahadevan 2018 bib entries added (but not read). Rao 2009 and Gokhale 2026 still uncited. RIME 3/2 still a TODO (L300). |
| S11 | Recchia "weighting", 48% | **resolved** | L494, L498. |
| S12 | clean() asymmetry | **resolved** (wording) | L134–137. The optional no-clean rerun was not done. |
| S13 | Title | **resolved** | New title; no "same" or "one sign stock". |

### Could fix

| item | status |
|---|---|
| Fig. 2B r = 0 and sealtype pool; panel A "Harappa side" | resolved |
| Rename stock-share q | resolved (s) |
| LB wording "cannot be shown to carry place beyond its scribes" | resolved (L463) |
| AUC gaps on RT0 "local share" scale | not done |
| Bib keys for oracc, cdli, edh, damos | not done (still 4 BibTeX warnings in main.blg) |
| Count of ORACC impressions grouped by P-number | not done. Now more relevant: grouping is per sealing (`{pid}.s{sn}`), not per seal. |

---

## Part C: referee reports (new personas)

### C1. Field archaeologist: Indus craft production and seal manufacture

*Persona: a South Asian archaeologist who has excavated at an Indus site and published on steatite working, seal-cutting workshops and the chaîne opératoire of seal production.*

**Summary.** The paper asks whether inscriptions on seals from Mohenjo-daro and Harappa can be told apart by their sign content more easily than two random halves of Mohenjo-daro. The answer is no, with an upper limit of about 0.1 AUC. A planted-name exercise argues that a large city-specific name stock would have shown. Sealings, tablets and Chanhu-daro are treated as exceptions. The statistical work is careful, and the authors are frank about what was blind. My concern is what a "site" means for a seal.

**Major issues.**

1. *A seal's findspot is its place of discard, not its place of making or use.* Seals were cut in workshops. Unfinished seals and steatite debitage are known from Mohenjo-daro, Harappa and Chanhu-daro (Mackay 1943: 145, which the authors cite). Seals moved with people. If carvers were few, trained in one tradition, or itinerant, sign content could be uniform across cities even if the *owners* differed. The paper's reading ("a pool shared by both cities", or "no names at all", L382–384) leaves out a third reading: **a shared carving and inscribing practice**, in which a small specialist group composed texts for owners anywhere. That reading predicts uniform texts *and* the regional variation in imagery and style the paper sets aside. Discuss it.
2. *The sign lists normalise exactly the variation a craft archaeologist would look for.* M77 and ICIT merge graphic variants into one sign. Local workshop habits (stroke order, allographs, ligature conventions) are removed before the classifier sees anything. The authors say this once (L411). It belongs in the abstract's scope sentence, because the title's "no detectable place signal" is about *normalised sign identities*. The M93 case is the proof. Mahadevan treats a three-stroke final mark as one sign, ICIT as two common signs, and the "difference" moves with the editor. The reversed pair W032 W031 occurs on Mohenjo-daro seals (LIT L111) and is not mentioned. That is the first thing I would check.
3. *Harappa has no within-city floor of its own.* Every Mohenjo-daro–Harappa floor splits Mohenjo-daro. Harappa has well-documented mounds (AB, E, ET, F) and HARP phasing (Periods 3A–3C) in ICIT. A Harappa mound split or Vats-vs-HARP split is the obvious second floor. It would also address chronology, which is now only a limitation (L415).
4. *Chanhu-daro is a craft town.* Bead-making and seal-making dominate its excavated record. If its seals include workshop products for export, "place" there means place of production. The paper's "leans apart" result is then a production-centre effect, not a regional dialect. Say which unfinished or uninscribed seals are in the 40-odd, and whether dropping them changes the gap.
5. *Sealings versus seals.* The text now says sealings are the better place-of-use evidence and point the other way (L341). Good. But the abstract still leads with seals and mentions sealings in a single clause at the end. For an archaeologist, a paper whose best place-of-use evidence differs should not have a title that reads as a null.

**Minor issues.** Give site, excavator and stratigraphic context counts for the Harappa seals in each edition (Vats vs HARP). "Copper tablets, a Mohenjo-daro object class" is right; cite the excavation report. Petrie et al. 2018 and Jamison's style groups deserve one more sentence: style groups crossing sites is a carving-practice result, and it fits point 1. The M93 photo check must be done before submission; it is cheap and decisive.

**Recommendation: minor revision** (for the data analysis), with a major addition to the discussion.

**Top 3 changes:** (1) add the shared-carvers reading and say plainly that sign lists erase graphic variants; (2) a Harappa-side within-city floor (mound or excavation campaign), with period where ICIT gives it; (3) check M93, its reversed-pair twin at Mohenjo-daro, and unfinished seals at Chanhu-daro on the photographs.

### C2. Journal editor: JDMDH (fit, clarity, reproducibility, length)

*Persona: a section editor at the Journal of Data Mining and Digital Humanities, judging a submission sent as a short paper.*

**Summary.** A computational test of a long-standing humanities claim (Indus uniformity), with calibrated baselines, planted-signal power checks, pre-registration and adversarial review. The fit is good: the method lesson (between-site scores mean little without a within-site floor at matched size, L401), illustrated by the Linear B scribe trap, is portable to any DH classification-by-provenance study. That lesson may matter more to our readers than the Indus result.

**Major issues.**

1. *Length.* At 14 pages and about 7,000 words, with two dense tables and three multi-panel figures, this is a full article. As a short paper it needs to lose about half. Cut: Appendix B (Recchia) down to two sentences in the text; the small-site paragraph and Fig. 3 (the paper itself says "for orientation only"); Latin down to two sentences; the Linear B lesson to one paragraph or a box; and the Table 1 rows that are not cited (null rows could go to a supplement). Keep Fig. 1, Table 2 and Fig. 2B–C.
2. *The abstract is a results dump.* About 280 words carry 20 numbers. A DH reader needs the question, the design (floor, power, reference), the answer and the bound. Aim for about 150 words and at most 4 numbers. The sealing and Chanhu-daro sentences can go to the body.
3. *Live TODOs and unread sources.* Seven TODO comments remain in the source. Three are substantive: Yadav 2013 (directly on the question, L48 and L76), the Parpola page and RIME 3/2. A paper whose novelty sentence depends on not having read the most relevant prior study cannot go out. Read it by hand, then keep or drop the "to our knowledge" sentence.
4. *Jargon density.* Readers meet M77, ICIT, Δ, Δnull, Δcons, q_floor, q_chance, p_floor, PS, m*, r80, s, gate, floor and TOST within four pages. Define each once in a small box or table, and use at most three of them in the main text. "PS" in particular is undefined beyond a clause.
5. *Reproducibility is strong, but the review copy cannot show it.* Code, prereg hashes, per-draw JSONL and a ledger exist, and the figures rebuild byte for byte from results.json. But the repository URL is withheld, and third-party corpora are rebuilt by scripts. Provide an anonymised archive (code, results.json, draws, environment lock file, the rebuild scripts and their source URLs with access dates) for reviewers. State compute needs (one laptop core, about N hours) and seeds. Name the Python and package versions.

**Minor issues.** The figure tick labels at 6.3–6.8 pt are below most journals' minimum size; enlarge them. Fig. 1A and 1B use different row sets, which is confusing; consider making B its own figure. Table 1's caption should say that CD rows show Δfloor. The "Analysis by AI agents" disclosure is good; keep it. "An earlier, unsettled finding from this project" (L387) cites a README; cite an archived version (with a DOI) or drop it. Check the journal's anonymity rules before citing the project's own preprint. Fix the four BibTeX warnings (oracc, cdli, edh, damos need `key`).

**Recommendation: major revision (resubmit as a short paper after cutting), or accept as a full research article after minor revision.** The science is ready before the form is.

**Top 3 changes:** (1) cut to about 3,500–4,000 words with a 150-word abstract; (2) resolve every TODO, above all reading Yadav 2013; (3) put an anonymised reproducibility archive with an environment lock file in the review package.

### C3. Bayesian statistician: sceptical of AUC site classifiers and absence-of-evidence claims

*Persona: a Bayesian statistician who works on model criticism and dislikes using cross-validated AUC as an evidence measure.*

**Summary.** The authors infer "no detectable place signal" from a near-chance cross-validated AUC gap between two sites, against a within-site floor. They support it with a bootstrap interval, power simulations and two alternative statistics. This is much better than a bare null, and the wording is mostly disciplined. My objections are about what the bound means, what was conditioned on, and whether the contrast with Ur III is itself tested.

**Major issues.**

1. *The headline contrast is never tested directly.* The paper's logic is "Ur III separates, Indus does not". But the Indus upper limits (97.5th percentiles +0.106, +0.106, +0.123) overlap the Ur III lower limits (2.5th percentiles +0.107 to +0.220). Overlapping marginal intervals do not settle it either way. Report the distribution of Δ_UrIII − Δ_Indus from the saved bootstrap replicates (`draws_boot.jsonl`; the two pools were resampled independently, so pairing replicates is valid). This needs no new runs. Without it, "Ur III scored the same way shows its city clearly" is a comparison of two significance verdicts.
2. *"Bound" is a frequentist upper limit of a pipeline-specific statistic, not a bound on place signal.* m* is the 95th percentile of a bootstrap distribution of a difference in medians of pooled out-of-fold AUCs from a Bernoulli NB on binary features with min_df 2. A large difference in *frequency* among shared signs can leave AUC unmoved. The diffuse-shift simulation shows this: 20–30% of tokens must be redrawn to reach 80% power. State the bound on the scale the reader cares about. The planted-effect calibration already gives the mapping (gap ↔ share of altered tokens), so report "consistent with up to about X% of tokens differing in a local-variant pattern, or Y% under a frequency shift". Better still, report a posterior or likelihood over that share.
3. *Absence of evidence is conditional on the generative model of names.* The name bound assumes Indus names would be spelt as one new sign, or as fixed pairs of common signs with Ur III frequencies. Real logo-syllabic name systems spell names with variable, multi-sign, partly shared strings, and homographs across cities. The "real frequency" form is already the hardest to catch (40–50%, upper CI beyond 0.50). Any less favourable spelling model would push it higher. The paper should say "under these three spelling models". Ideally it would also give one adversarial model (names spelt from the same common-sign pairs at both sites, differing only in frequency), and report the r at which that is excluded, or that it never is.
4. *Interval construction is not purely conservative.* Resampling the between pool and the within pool independently ignores that the Mohenjo-daro side of the between comparison and the Mohenjo-daro halves of the floor are the same texts. Positive correlation between b and w is discarded, which inflates Var(Δ). That widens the upper limit (cautious for the bound) but also makes "every interval includes zero" easier to obtain. For a paper whose headline is a failure to detect, that is the wrong direction. Each replicate also uses only 5 + 5 draws, so Monte Carlo noise is added to the sampling spread. Run a joint resample (resample MD once per replicate, then form both halves and the between side from it) and more draws per replicate, at least for the three headline pools. This *is* new compute, but small.
5. *Garden of floors.* Six Indus floors are reported: random halves, area, area confirmed, area de-duplicated, depth, and the null. One (depth, exploratory) gives +0.089, beyond the margin. Table 1 lists it, which is right. But the inference picks random halves as primary because step 2 pre-registered it, after the MD–Harappa number was known (L173). A hierarchical treatment would be more honest: Δ against each floor as draws from a distribution of plausible floors, reporting the spread across floors as well as within. At minimum, state in the abstract that one of five floors puts the gap beyond the margin.
6. *The detection criterion has a 17–40% false-positive rate.* With no names planted, 17–40% of replicates already give Δ ≥ 0.05 (L320). "Detected at 80%" therefore mixes signal with a high baseline, and r80 is a power figure on a test of unknown size. The exclusion rule (share of replicates above the observed gap) is the defensible one; lead with it and drop r80 from the abstract.

**Minor issues.** Pooled out-of-fold AUC below 0.5 is a symptom, not just a bias to note: per-fold AUC or a proper scoring rule (log loss, Brier) under the same CV would be less fragile at n ≈ 40–200. p_floor and PS are empirical shares over draws from one pool, not p-values; call them "shares". The JSD "label-shuffle p = 0.005, the minimum at 200 shuffles" should be written as p ≤ 0.005. LR's "differs" at +0.0504 against a 0.05 margin is a coin flip at the third decimal, and the text handles it sensibly. The unicorn "underpowered" label at 98% power (REV R7) is a rule artefact; the paper wisely avoids the label, but the prereg rule should be fixed for future runs.

**Recommendation: major revision** (most of it is reporting; items 1 and 4 need computation, item 1 none beyond existing replicates).

**Top 3 changes:** (1) bootstrap the Ur III-minus-Indus gap from the saved replicates and report it; (2) restate the bound on a token-share scale and as conditional on the spelling models; (3) jointly resample the overlapping Mohenjo-daro texts and check whether "includes zero" survives.

---

## Part D: synthesis

### Is it ready to submit as a short paper?

**No, not yet. It is close on substance and far on form.** The numbers are sound: 116 of 130 audited claims are exact, every figure reproduces byte for byte, and no error changes a conclusion. The remaining gaps are (a) a handful of wording errors in the headline sentences, (b) unread prior work behind the novelty claim, (c) two cheap analyses that referees will ask for, and (d) length: it is twice the size of a short paper.

### Title and abstract

**The title is now supported.** "No detectable place signal beyond a within-city floor", for *seal texts* of *two named cities*, is what the evidence shows. Two optional refinements: "sign content" instead of "place signal" would carry the sign-list normalisation caveat (C1.2), and "seal texts" already excludes sealings.

**The abstract claims slightly more than the evidence in three places, all fixable by rewording:**
- "the data bound any difference to about 0.11 AUC": this is a one-sided 95% upper limit on a pipeline statistic (C3.2).
- "above every within-city floor": should be the six structural floors.
- "drops it below the strictest floor": the gap stays positive (+0.030) and only falls under the 0.05 margin.

It also leaves out that one exploratory floor (depth) puts the gap beyond the margin (C3.5), and that the name bound depends on the spelling model (C3.3). Neither omission is fatal. Both belong in one clause each.

### Remaining must-fixes

| # | fix | type | what exactly |
|---|---|---|---|
| R1 | "below the floor" for +0.030 / +0.047 | rewording | L55, L269, Table 2 caption, and the REV safe sentence: "under the 0.05 margin on the Girsu reign floor". |
| R2 | "bound any difference to about 0.11" | rewording | L52, L97, L189, L379: "one-sided 95% upper limit of 0.10–0.11 AUC for this pipeline". Add one clause on the token-share equivalent from Fig. 2C. |
| R3 | "every within-city floor" for Ur III | rewording | L54: "all six structural floors". |
| R4 | L99 "Indus seals therefore do not carry…" | rewording | "would have been detected had they carried…". |
| R5 | Small sites: "19–37 per side"; "underpowered or inconclusive" | rewording | L366: 37–67. L363: add the MD–Dholavira pair that is not beyond the floor. |
| R6 | Fig. 2B baseline vs L320 | rewording | State that the plotted curves (exceed_obs) start at 45–55%, and that 17–40% is the Δ ≥ 0.05 detection rate. |
| R7 | Name bound conditional on spelling model | rewording | Abstract and L321: "under the three spelling models tested". |
| R8 | Read Yadav 2013 (and Wells 2011 if possible); Parpola page; RIME 3/2 | reading | Then keep or drop "to our knowledge" (L48) and remove every TODO. A journal cannot receive live TODOs. |
| R9 | M77–ICIT object overlap count | small analysis | One join on the concordance. Replace "most" (L106) with the number. |
| R10 | Ur III-minus-Indus gap | small analysis, no new runs | Pair saved bootstrap replicates (`draws_boot.jsonl`) and report a CI for Δ_UrIII − Δ_Indus per Indus pool against U_reign (the lowest Ur III floor). This is what the paper's central contrast needs. |
| R11 | Length | editing | About 3,500–4,000 words and a 150-word abstract for a short paper: shrink App. B, the small sites and Fig. 3, Latin and Linear B; move the null rows of Table 1 to a supplement. Alternatively, submit as a full article. |
| R12 | Revision prereg timing | rewording (favourable) | App. A L458: the revision hashes were committed (f8c33a1, 21:27Z) before the first revision run (21:28Z). Say so. |

### Should do before submission (referees will ask)

- **Joint resampling of the overlapping Mohenjo-daro texts** (C3.4; new compute, small). It checks whether "every interval includes zero" survives once the b–w correlation is kept.
- **A Harappa-side within-city floor** (mound or Vats vs HARP; C1.3; new analysis). It also gives a partial period control.
- **M93 photo check**, including the reversed W032 W031 pair on MD seals (C1.2; human task, already in HUMAN_LEADS).
- **Discuss the shared-carvers reading** and the sign-list normalisation in the Discussion (C1.1–2; rewording).
- Cite or drop Rao 2009 and Gokhale 2026. Fix the four bib keys. Enlarge figure text to at least 7 pt.
- Fix the stale source files: RT2 RESULTS safe wording ("sits in personal names"), S2 RESULTS L31 ("16-84%"), REV safe sentence ("below the Girsu reign floor").

### Notes on verification

- Figures: copies of `make_*.py` and `_style.py` were run from `/tmp/fig_rev2.nq08/figures/` with `REPO` and `OUT` repointed. Outputs were compared with `cmp`: three of three identical.
- All REV numbers were read from `revision/results.json` (`boot`, `names`, `diffuse`, `roles`, `latin`, `alt`, `m93`, `unicorn`); S2 numbers from `step2/results.json` part1/part2, including `n_side` for the small-site check.
- Grouping units come from `step2/s2.py` (`m{text_no}.{side}`, ICIT id) and `build2.py` (`{pid}.s{sn}` for ORACC, seal id for CDLI).
- Prereg timing comes from `git log` on `docs/prereg/HASHES.txt` and `uniformity_paper_revision.md`, and the timestamps in `revision/run.log`.
- Literature claims were checked against LITERATURE.md, not against the primary sources (same limit as REVIEW_1).

---

## Note added 2026-11-21 (implementation pass)

- **R12 was wrong as stated.** The revision hash lines carry a self-recorded time of 19:24:19Z, and `draws_boot.jsonl` was first written 9 s later. But the commit that made them public (f8c33a1, 21:27:11Z) came after the bootstrap, planted-name and diffuse jobs had finished, and while the name-role job was running (`draws_roles.jsonl` first written 21:15:31Z). The 21:28Z line in `run.log` restarts the roles chunk; it is not the first run. `rev.py` was not in that commit. The paper (App. A) now states this timing. The hashes still match the code.
- R10 was computed from saved replicates (prereg `docs/prereg/uniformity_paper_contrast.md`); R9 was counted from existing link tables. See `experiments/uniformity_paper/revision/RESULTS.md`.
