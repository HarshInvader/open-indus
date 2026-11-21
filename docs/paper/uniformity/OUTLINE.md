# Paper 2 outline (draft): Indus seal texts carry no place signal

Status: outline only. Numbers marked PENDING wait on `experiments/redteam_uniformity_step2/` and `experiments/chanhudaro_followup/`. Every number must come from a RESULTS.md that passed its red team.

## Working title

"Two cities, one vocabulary: Indus seal texts from Mohenjo-daro and Harappa show no place signal, unlike name-bearing seal legends"

## Main point (one sentence)

Seal texts from Mohenjo-daro and Harappa differ no more than two parts of one city. Readable seal legends from different cities do differ, but only while they carry names. So Indus seals behave like name-free legends.

## Supporting points

1. **The two Indus cities match their own floor.**
   - The between-city AUC (0.51-0.55) equals the within-Mohenjo-daro split by excavation area and by random halves.
   - Gap −0.02 to +0.04 across both editions and five sign lists, with findspot-confirmed seals only and with near-copies removed.
   - A 15% local stock would be caught 93-100% of the time.
   - Sources: step 1, redteam step 1, step 2.
2. **Readable seal legends carry place, through names.**
   - Ur III impressions and one-per-seal entries, and Latin owner/maker marks, separate their sites above their own within-site floors: +0.12 to +0.31, gates 100%.
   - With names removed, Ur III between-city equals within-city across reigns (+0.009). Without names, date carries as much signal as place.
   - PENDING: which part of the names carries place (theophoric elements and toponyms vs personal names), from redteam step 2.
3. **What this rules in and out.**
   - Ruled out: a large city-specific sign stock, or site-specific names on more than about 20-30% of seals (planted-names test; PENDING the refined bound from redteam step 2).
   - Still open:
     - seals that write no local names;
     - names drawn from a shared, non-local pool;
     - a centrally taught standard.
   - The data cannot yet separate these.
4. **Limits and exceptions.**
   - Chanhu-daro differs from Harappa above the within-site floor but not above its own null. PENDING: place, period or workshop.
   - Sealings differ between the two cities (+0.10 to +0.12). PENDING: duplicates or format.
   - The tablet difference is an object-type effect.
   - Smaller sites are underpowered.
5. **Methods lesson for comparing scripts.**
   - A "site" contrast needs a within-site floor.
   - Linear B Knossos vs Pylos looked like strong place signal (0.90), but scribe groups inside one palace separate as much. With scribes held out it is 0.52.
   - Without floors, cross-corpus comparisons overstate place.

## Sections

1. Introduction: the long-held claim that Indus writing is uniform (Parpola; Yadav et al.), with no calibrated test so far.
2. Data:
   - ICIT and M77, with M77 locus codes checked against the 1930s registers;
   - Ur III (ORACC, CDLI), Latin (EDCS-derived), Old Babylonian, Linear B (DAMOS).
3. Method:
   - the frozen classifier, matched size and length mix;
   - between minus within;
   - planted-stock power;
   - pre-registration and red teams.
4. Results: points 1-4.
5. Discussion: what "behaves like name-free legends" means; point 5.
6. Limits.
7. Data and code availability: repo paths, prereg hashes.

## Figures

1. Between vs within dot plot, one row per corpus and split, with the Indus rows highlighted.
2. Planted-stock and planted-names power curves.
3. Site map with pair gaps; Chanhu-daro marked.

## Literature still to read before drafting

Ameri 2013 (regional diversity in Harappan seals); Fuls (site-specific signs); Yadav et al. clustering; Kenoyer and Possehl on standardisation; Rao et al. on West Asian seals.

## Venue

Short paper: JDMDH or Digital Scholarship in the Humanities.

## After the literature review (2026-11-21)

- **Novelty statement:** see LITERATURE.md. The uniformity claim is old (Parpola 1994; Yadav et al. 2017; Nair 2026). What is new is the calibrated test: within-site floors, power, name-bearing vs name-free readable references, the Linear B scribe trap, and separating object type from place.
- **Main conflict to answer:** Recchia & Louwerse 2016 (Cognitive Science 40:2065-2080, doi:10.1111/cogs.12311). They summed LSA site vectors for five sites (seals n = 1,936, sealings n = 723) and showed that MDS of those vectors matches geography.
  - Planned test: rerun their five-site geography test with a site-label permutation null and with object type held fixed, then check whether the fit depends on the outer sites (Lothal, Kalibangan) and on sealings rather than on Mohenjo-daro vs Harappa seals. Queued after the step-2 red team (one compute job at a time).
- **Must read before submission:** Recchia & Louwerse (full text), Yadav 2013 (Scripta 5), Mahadevan & Bhaskar 2018 (toponyms).
- **Consistency checks with the literature:**
  - Yadav et al. 2017 single out Harappa sealings, which matches our sealing difference.
  - Mackay 1943 records local seal-making at Chanhu-daro and sign-less Jhukar seals, which fits the Chanhu-daro lead.
  - The M93 end mark at Chanhu-daro appears to be unreported.

## Revised main point after red team 2 (2026-11-21)

Replaces "Indus seals behave like name-free legends"; red team 2 broke that, since the name-free comparison is a tie, not a clean result.

**Main point:** Seal texts from Mohenjo-daro and Harappa differ no more than two halves of one city. In readable seal legends the city shows through owners' personal names. So Indus seals cannot be carrying site-specific personal names the way Ur III seals do: at most about 30% of seals could carry them, against 99.8% in Ur III.

**Supporting points:**
1. The between-city result ties with the within-city floor and with a shuffled-label null (step 1 and step 2, with three red teams).
2. In readable seals, place lives in personal names. With place names and gods removed the signal remains (+0.09 to +0.27); without personal names it ties with the reign floor (red team 2).
3. A planted-names bound on Indus: names drawn from real Ur III frequencies are ruled out above about 30% of seals, invented name stocks above 10-20%.
4. Limits:
   - Sealings and moulded tablets differ between the two cities.
   - Chanhu-daro is a near-miss (q = 0.06), partly from its own end mark M93, which looks unreported.
   - Linear B is a scribe trap.
   - Recchia & Louwerse 2016: rerun in progress (`experiments/recchia_rerun/`).

**What it means:** Indus seals either name their owners from a shared pool across cities, or don't name individuals at all (offices, titles, commodities). It also fits earlier finding #10, that seal cores are not spelled-out names.
