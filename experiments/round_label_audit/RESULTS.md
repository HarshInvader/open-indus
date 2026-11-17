# Audit: did the 'round seal' mislabel contaminate earlier results? (board #22, H8)

**Verdict: mixed.** The headline numbers for Gulf round seals do not change, because no foreign object is SEAL:R. What the mislabel broke is the **format control** behind headline #4's "it's not a format effect." The old "home round seals" were 97% rectangular seals (SEAL:R). With only true circular and cylinder seals at home (SEAL:C + SEAL:CY, 9 distinct texts), the home control no longer looks normal:
- Under the context Q4 Kneser-Ney bigram, home circular seals score **+1.84 bits/sign** over home square and rectangular seals (CI +1.04 to +2.74, p=1e-4). The old figure was +0.17.
- Foreign round seals beat home circular seals by only **+0.37 bits/sign** (permutation p=0.48). The old figure was +2.09.
- Bigram gain is **+0.18** for home circular, against −0.25 foreign and +1.36 home square or rectangular.

The Wells-grammar version gives a weaker result. Home circular seals (n=12) are +0.41 (p=0.18), while Gulf round seals are +1.77. So the evidence that Gulf round seals are anomalous *because they were found abroad*, and not because they are round or cylinder seals, is gone. It is now inconclusive at best. "Round and cylinder seals, wherever found, often break Indus order" fits the data as well. This matches H7's #21: final numerals are a round-seal effect too.

Task #1's flags get slightly *stronger* with the corrected native pool. glib had been dropping 388 rectangular seals from the "seal" reference. The count goes from 9 to 11 of 38: SUSA-01 and LURISTAN-01 move from borderline to flagged, and both are round Gulf seals. Under #11's red team, survivors go from 9 to 11 (binomial p from 1.1e-4 to 2.2e-6).

Pre-registration: `docs/prereg/round_label_audit.md` (sha256 in HASHES.txt, written before the corrected runs). Method: `runner.py` re-executes each original script read-only, with writes redirected to `out_old/` and `out_new/`. It runs each script twice under PYTHONHASHSEED=0, once with the old labels and once with SEAL:R treated as an ordinary seal. The old reruns reproduce the logged numbers exactly (q4: n=344, +0.172; validate (d): n=318, +0.182), so the harness is faithful.

## Facts
- ICIT seal types: SEAL:S 1,777 (w/h 1.0) · **SEAL:R 388, all at Indus sites, median w/h 2.23 (rectangular)** · SEAL:C 32 (15 home, 17 foreign; circular) · SEAL:CY 9 (8 home, 1 Susa) · SEAL 82 · SEAL:L 2.
- **No foreign object is SEAL:R.** Every foreign "round" group was therefore always SEAL:C/CY only. Only *home* round controls and glib's *native reference pools* were contaminated.
- Two kinds of contamination:
  - (a) Scripts using the tuple ("SEAL:R","SEAL:C","SEAL:CY") put rectangular seals into "home round."
  - (b) `glib.icit_register` maps SEAL:R to `round_seal`, so every glib-based reference pool with `register=="seal"` silently left out 388 rectangular seals. For example, validate (d) used 1,353 reference seals where 1,659 were available.

## Table of affected claims

| Claim (where) | Group defined by | Old | Corrected | Status |
|---|---|---|---|---|
| #4 Gulf round seals +2.17 bits/sign (context q4_gulf) | tuple, foreign only | +2.17 [1.63, 2.70], n=18 | same; vs home square+rect +2.21 [1.66, 2.73] | **Stands** (number unchanged) |
| #4 "not format: +2.09 over home round seals" (context q4_gulf) | tuple → home round = 344 (335 rect) | +2.09 [1.53, 2.60], p=1e-4 | vs 9 home circular/cyl: **+0.37, perm p=0.48** | **Fails** |
| Home round vs home square (context q4_gulf) | tuple | +0.17 (n=344, p=0.011) | **+1.84 [1.04, 2.74], n=9, p=1e-4** | **Reversed**: true round seals at home are anomalous too |
| Bigram-gain decomposition (context q4_gulf) | tuple | home round +1.37 vs foreign −0.25 | home circular **+0.18** (n=9) vs foreign −0.25 vs home sq+rect +1.36 | **Weakened**: home circular sits near foreign |
| redteam r4 "Home round seals behave normally" (MD 149, Harappa 70, site held out) | tuple | perm-pct 0.93 / 0.92, gain +1.09 / +1.25 | MD **n=3**: perm-pct 0.59, gain −0.22, bits 7.78; Harappa n=1 | **Fails / untestable** (n<6); the 3 MD circular seals look like the foreign ones |
| redteam r4 foreign round perm-pct 0.53 vs peripheral sites ≥0.87 | tuple, foreign; peripheral = round+square (rect counted either way) | 0.53 | 0.53, peripheral unchanged | **Stands** (compares findspot groups, not format) |
| context q4b: foreign round share 0 bigrams; home round subsets +1.81 | tuple | home-round reference from 300+ rect seals | corrected home round has <17 texts with ≥2 signs: **crashes** (cannot draw n=17) | **Untestable** |
| typology q2 robustness "baseline = home round/cyl" | tuple | pool 343, G2 p=0.040, G3 p=0.025 | pool **9**, degenerate (with-replacement draws) | **Untestable**; primary G2/G3 (all home seals) unaffected |
| grammar validate (d): Gulf round worse, p<0.01 | glib register | +1.80, p=1e-4 (ref 1,353) | +1.77, p=1e-4 (ref 1,659); PASS | **Stands** |
| grammar validate (d) home round control | glib register | n=318, +0.18, p=0.011 | **n=12, +0.41, p=0.18** | Changed. Its meaning was wrong before: it was a rectangular-seal control |
| #1 foreign texts break Indus order (foreign_corpus/score.py) | glib native pool | 9/38 flagged | **11/38** (+SUSA-01, LURISTAN-01) | **Stands, slightly stronger** |
| #11 red team of #1 (redteam_foreign/attack.py) | glib native pool | 9 survivors, p=1.1e-4; one-misreading p=0.002 | **11**, p=2.2e-6; p=2.2e-4; T7 order-driven 9→10 | **Stands** |
| #15 foreign final numerals (foreign_final_numerals/test.py) | glib `types={"seal"}` home pool 1,508→1,840 | primary 2/9 p=0.030; secondary 6/20 p=5e-5 | primary p=**0.044** (LOO 0.28); secondary 5e-5 | **Unchanged** (primary was already "refuted" by its rule) |
| #10 name structure (name_structure/compare.py) | glib `types={"seal"}` | D(home seals)=3.08, nearest Akkadian | D=3.18, nearest Akkadian; power 0.86→0.89 | **Stands** |
| ledger v2_reruns F; functional_reading g2 (foreign round) | tuple / prefix, foreign only | n/a | no SEAL:R abroad | **Unaffected** (count check) |
| roof_context `icit_class` | comment calls SEAL:C "cylinder" and drops 32 circular seals from "seal" | n/a | n/a | Label wrong, effect tiny (32 of ~2,300); not rerun |
| rank_ladder, redteam_rank, reg_size, space_and_sealing, direction_time_animal, redteam_chrono | SEAL:S only, or SEAL:R treated as its own (rectangular) type | n/a | n/a | **Unaffected** |

## Corrected home circular and cylinder seals (KN bits/sign, CV)
Chanhu-daro W632 W390 W400 W375 (6.52) · Harappa CY 7 signs (5.24) · Mohenjo-daro W001 W140 (6.34), W832 W256 (5.33), W016 W405 W001 W255 W324 (7.94), 8 signs (6.82), 7 signs (6.44) · Dholavira W255 W368 W001 W091 W806 (7.31) · Rakhigarhi CY W688 W317 W002 W361 (9.84). Several carry W001/W002 strokes and person-like signs, the same pattern as the Gulf seals. Some may be imported Gulf-type seals. That has not been checked.

## What failed or was not checked
- n=9 to 12 home circular seals is small. The KN test still has a CI clear of zero (+1.04 at the lower end), but the grammar version is not significant (p=0.18). The two scorers disagree on how anomalous home circular seals are. They agree that the old control was mislabelled.
- I did not check whether the home circular seals are Gulf imports (style, material, find context). If they are imports, the "foreign" reading survives with a different meaning.
- The README, RESEARCH_STATE and ledger texts were not edited (lead only). Proposed ledger rows are in `ledger_rows.csv`.

## Files
`runner.py` (read-only re-execution, writes redirected), `run_all.sh`, `d_gulf.py` (validate part d alone), `fmt_control.py` and `fmt_control.json` (corrected format control), `logs/`, `out_old/`, `out_new/`, `results.json`.
