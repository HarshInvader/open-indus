# Pre-registration: do title signs mark an administrative role on sealings? (Fable plan 3, R5)

Agent: sealing_function. Written 2026-11-14, BEFORE `sealings.csv` is built and before any title sign is cross-tabulated against a reverse (back) type or against multi-impression status in this project.

## What I already know about the data (disclosed)
- **Reverse-type data exist in usable form only for Lothal**: Frenez & Tosi 2005, Table 1 (paragorth transcription, already used by `experiments/administration/t4_lothal_backs.py`): 93 sealings L-124..L-216, impressions per sealing, back type, context. Back types: pottery 21, undiagnostic 18, wooden boxes 15, structures 10, lockers 9, pegs-on-wall 9, parallel canes 5, leather sacks 2, woven straw / other / wicker / single rope 1 each. 62 single, 25 x2, 4 x3, one x4, one x5. No open source gives reverse types for Kalibangan, Banawali, Harappa, Mohenjo-daro or Dholavira (harappa.com, Academia, ResearchGate and Taylor & Francis copies are blocked; CISI captions carry no reverse description; Rao 1985 reverse notes are "reed / stick / groove" for most and were judged unusable by paragorth S-DARK-71.1).
- I have read the administration t4 log (W-level back distributions of the 12 signs in >= 3 Lothal texts, incl. W390: pottery 2, structures 2; W002, W740, W220; no title tested there). I have read paragorth STRATEGIES S227, S-DARK-65.1-65.4, 71.1-71.3, 77.3 (co-sealing: no office stamp, hub seal W705-500-741-1-55-220-740-90 at chance on multi-impression sealings; a fixed IM77 "team" of jar-headed seals; back type predicts nothing once the elephant boxes are dropped).
- While inspecting the paragorth catalogue (`loop71_lothal_sealings.csv`) I saw these rows: L-146 parallel canes, W705-33-520 (= M336-M89-M211 block); L-180 parallel canes, IM77 M100-17-8-342 (contains M8); L-205 undiagnostic, 2 impressions, one ending W760-740 (IM77 M186-293-99-258-347-342, contains M347); L-211 wooden boxes, 3 impressions incl. W231-100-740 and W240-335-760-740; L-196 pottery and L-198 structures with W880-2-32-590-390 (M249-M161/162 block); L-202 undiagnostic with W220-590-390; L-192 pegs-on-wall, 2 impressions, W 0-892-0-0; L-206 pegs-on-wall, 2 impressions, the hub seal (no title). I have NOT seen the texts of the other peg sealings (L-152, 154, 155, 157, 173, 175, 179) or counted titles by back type.
- Expectation stated now: pegs-on-wall sealings with a transcribed text are very few (probably 3-5), so the primary test is expected to be **underpowered**; the likely verdict is "untestable at this n" unless the effect is very large.

## Title definitions (frozen; Wells numbers via `bridge_extended`, M numbers for the M77 replication)
| id | title | Wells (ICIT) | M77 |
|---|---|---|---|
| T347 | M347 | W760 (the bridge maps W760 to M347 or M358; accepted as is) | M347 |
| T8 | M8 | W100 | M8 |
| TB336 | M336-M89(-M211) block | adjacent W705 W33 | adjacent M336 M89 |
| TB249 | M249-M161 block | adjacent W590 W390 or W590 W405 | adjacent M249 then M161 or M162 |
A face "carries" a title if the sign or adjacent pair occurs in a break-free run of its sequence (fragments count). "Any title" = carries at least one of the four.
Closers for the co-sealing tests: jar = last sign W740 (M342); arrow = last sign W520 (M211).

## Data units (frozen)
- `sealings.csv` = every ICIT object of type TAG* (grouped by site + CISI number; one row per object with all its face texts), plus Frenez & Tosi fields (n impressions, back type, context) joined on CISI for Lothal, plus a separate list of M77 sealing objects with >= 2 sides at Mohenjo-daro, Lothal, Kalibangan and other non-Harappa sites (Harappa M77 "sealings" are moulded tablets with count sides; excluded).
- **Back classes** (Lothal): DOOR = pegs-on-wall. FIXED = pegs-on-wall + lockers + structures. CONTAINER = pottery, wooden boxes, leather sacks, parallel canes, woven straw, wicker, single rope, other. Undiagnostic dropped.
- **Multi-impression**: Lothal = Frenez & Tosi n >= 2 (their count does not depend on what Wells transcribed). Other sites = >= 2 ICIT faces on the object that are not the same text (an illegible second face counts).

## Primary hypothesis H1 (door-peg = storeroom authority)
A title is >= 3x enriched on DOOR sealings vs other diagnostic back types.
- Unit: Lothal sealing with a diagnostic back and >= 1 transcribed ICIT face. Per title t: a = DOOR sealings carrying t, b = other diagnostic sealings carrying t; ER = (a/n_door)/(b/n_other) (b = 0 -> infinite).
- Null: back labels permuted among these sealings within context stratum (W+W1 / W2 / O+?), 20,000 permutations; one-sided p = P(a_null >= a). Holm over the 4 titles.
- **Supported** if some title has a >= 2, ER >= 3 and Holm p < 0.05.
- **Power gate**: planted power at ER = 3 (title rate on DOOR set to 3x its observed non-door rate, other sealings unchanged, 500 replicates). If power < 0.5 for every title and H1 is not supported, verdict = **untestable at this n**, not refuted. If power >= 0.5 for a title and it fails, that title is **refuted at stated power**.
- Robustness (reported, not decisive): (i) unit = distinct (text, back) pair, as in t4; (ii) elephant-seal text W817-W002-W048-W740 removed.

## Secondary hypotheses (Bonferroni alpha 0.05/3 = 0.0167)
- **S0 (fixed closures)**: same as H1 with FIXED vs CONTAINER (Lothal), pooled "any title" statistic a = FIXED sealings with any title; same null.
- **S1 (titles accompany a second seal)**: unit = face (impression slot) on a sealing object, all ICIT sites. Statistic = number of title-bearing faces sitting on multi-impression sealings. Null = faces shuffled among all face slots within site (each sealing keeps its slot count and multi status), 20,000 reps; one-sided. "Always accompanies" is claimed only if the share of title faces on multi sealings is >= 0.8 with >= 3 title faces and S1 p < 0.0167. Per-title and closer (jar, arrow) shares reported descriptively.
- **S2 (countersignature asymmetry)**: unit = unordered pair of faces on the same sealing, among sealings with >= 2 legible distinct faces. Statistic = number of pairs with exactly one title-bearing face (title + non-title). Null = faces shuffled among the slots of these sealings within site, 20,000 reps; one-sided. A second directional statistic is reported: share of title faces whose partner carries no title vs the null.
- **Replication of S1/S2 on M77** (multi-side sealing objects outside Harappa, M-space titles). Reported with p; counts as transcription-robust, not independent (about 70% the same objects).

## Decision summary
- R5 "title marks an office by what it closed" is **supported** only if H1 passes. S0-S2 can add a role pattern (co-sealing) but cannot by themselves give an L2 anchor.
- All counts on distinct objects; Lothal repeated use of one seal is kept in the sealing-level primary because each sealing is a separate act, and checked by the distinct-pair robustness.
- Ledger rows: `sf_h1`, `sf_s0`, `sf_s1`, `sf_s2`, `sf_s1_m77`, `sf_s2_m77`, plus power rows.

## Amendment A1 (2026-11-14, after the first run, before reading any TB336 result)
ICIT writes Wells numbers zero-padded to three digits. TB336 was coded as "W705 W33", which matches nothing; corrected to "W705 W033" (the same block, W705 W033 = M336 M89). No other definition changed. Every other title already used three-digit numbers (W760, W100, W590, W390, W405). The first run (TB336 = 0 objects everywhere) is kept in `analyze_run1_bug.log`.
