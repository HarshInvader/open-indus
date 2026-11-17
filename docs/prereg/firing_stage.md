# Pre-registration: pre- vs post-firing vessel marks (experiments/firing_stage)

Written 2026-11-15 after building `experiments/firing_stage/vessel_marks.csv` and BEFORE any enrichment statistic was computed. Frozen inputs hashed in HASHES.txt: this file, `build_table.py`, `vessel_marks.csv`, `test.py`.

## Contamination disclosure
While building the table I read Kenoyer 2021 Table 1 (painted script). So I know that painted vessels often carry M391 (W820) alone (Surkotada 2, Shikarpur 2, Kanmer, Balakot with M102), M343 (W741) 3 times and M267 (W861) 3 times, and that M342 appears once (on a bangle). The site split below puts the Gujarat/Kutch painted vessels in held-out, but my knowledge of them is not blind. The dev-side picture (Pakistan sites) I have NOT tabulated.

## Data limits stated in advance
- Firing stage is recorded per object only for: 29 painted vessels (Kenoyer 2021 + ICIT 'p'), 3 Harappa graffiti that Kenoyer 2021 Fig. 3 calls post-firing, 1 mixed vessel, and 4 literature items without usable transcriptions.
- Stamped (74) and moulded (3) vessels are pre-firing by class (Kenoyer & Meadow 2010; CISI 1).
- The 534 ICIT graffiti have NO recorded stage. CISI's 'graffito' covers both. Kenoyer (2020: 221) describes Mature Harappa inscribed pottery as "generally irregular post-firing graffiti" plus "refined and regular pre-firing script". So graffiti are a POST-LEANING PROXY, contaminated by an unknown share of pre-firing incisions. This contamination biases enrichment toward zero; it cannot create a false pre-firing set.
- Only 3 certain post-firing texts exist: too few for any test. A certain-post test is NOT run; they are listed.

## Units
Distinct (site, firing class, Wells sequence). Breaks '#' are not signs. Units with no readable sign are dropped. A unit "contains" sign s if s is anywhere in it. Signs are Wells numbers (ICIT and Kenoyer both give them); Mahadevan equivalents via `bridge_WM.json` are for reporting only. Bangle (Kenoyer 6.1) excluded. Mixed vessel excluded.

## Split (by site, fixed now)
- dev = sites in Pakistan and Baluchistan: Harappa, Mohenjo-daro, Chanhu-daro, Balakot, Gumla, Kot-Diji, Nausharo, Amri, Allahdino, Lakhanjo-daro, Naru-Waro-dharo, Nuhato, Rodji, Hissam-dheri, Bakkar Buthi, Tarkhanewala-dera, Rappwala Ther, Guddal A, Derawar Ther, Murda Sang (ICIT 'Bala-kot' = Balakot).
- held-out = every other site (India: Gujarat/Kutch, Rajasthan, Haryana, Punjab-India, UP, Maharashtra; abroad: Oman, Iran).

## Comparisons
- **P1 (all pre-firing vs graffiti):** pre = painted + stamped + moulded; post = graffiti (proxy) + certain post.
- **P2 (technique-matched, handwritten):** pre = painted only; post = same as P1. P2 removes the seal-impression confound (stamped vessels carry seal texts, and object-type registers are already known, README #6).
Bonferroni: alpha 0.025 each.

## Primary hypothesis
Some signs are >=5x enriched pre-firing, and the set replicates on held-out sites.
- Dev step: ratio r(s) = [(a+0.5)/(n_pre+1)] / [(b+0.5)/(n_post+1)], a/b = dev pre/post units containing s. Set S = signs with r>=5 and a>=3 (P1) or a>=2 (P2).
- Held-out step: statistic T = number of held-out pre units containing any S sign minus expected; ratio R_ho = share of held-out pre units with an S sign / share of held-out post units with an S sign (same 0.5 smoothing). Null: firing labels permuted among units WITHIN SITE (10,000 perms; sites with only one class are fixed). One-sided p on the count of pre units containing an S sign.
- PASS: S non-empty AND R_ho >= 2 AND p < 0.025. FAIL: S non-empty and (R_ho < 2 or p >= 0.025). INCONCLUSIVE: S empty, or held-out pre units < 10.
- Power: report the share of 1,000 planted datasets (a sign added to held-out pre units at the dev rate of the strongest S sign, post at its dev post rate) that pass.

## Secondary hypothesis
The pre-firing S set tracks vessel form. Among pre-firing units with recorded form, classes {dish/bowl, jar (any), pointed-base goblet}: Fisher-Freeman-Halton (via permutation, 10,000) of S-presence x form class. PASS if p < 0.05 and S non-empty. Size is never recorded: size is UNTESTABLE.

## Descriptive (no verdict)
- Per-sign table of pre/post counts (dev, held-out) for the top 15 signs by pre count.
- M342 (W740) and the opener signs M267 (W861) / M391 (W820) rates by class.
- Number of signs per unit by class.
Sensitivity: drop 5548.1 (possible duplicate); drop uncertain Kenoyer sign readings ('?').

## What would falsify
A dev set that fails held-out at adequate power (>=0.8) falsifies "a distinct pre-firing vocabulary at the size seen in dev". Low power means inconclusive, not refuted.
