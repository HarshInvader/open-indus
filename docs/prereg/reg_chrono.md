# Pre-registration: reg_chrono (sign use vs decimal depth within area, Mohenjo-daro and Harappa)

Registered 2026-11-15 in `experiments/reg_chrono/`. This file, `rlib.py` and `r1_main.py` are hashed into `docs/prereg/HASHES.txt` (tag reg_chrono) BEFORE any outcome statistic on real depths is computed.

## Disclosure: what was already seen
- Counts only: register rows linked to M77 with usable depth: Mackay 1938 FEM 635 objects (508 register decimal depth, 121 M77 integer fill-in where the register depth is missing, 6 where register and M77 differ by >1.5 ft so M77 is used); Vats 1940 EH 541 objects (489 / 19 / 33). FEM serial vs cleaned depth Spearman -0.998 (Mackay sorted by depth; the OCR drops many minus signs, so FEM serials 1-686 and all EH depths are forced to below-datum/below-surface).
- Units after family collapse: MD_FEM 514 (M77 locus 31 = DK-G 402, locus 32 = DK other 112; 511 seals); HAR_EH 447 (8 M77 loci = Vats mound/area sub-areas 40-47, 53; 217 seals, 131 tablets, 98 sealings). Marker carrier units MD/HAR: ticked fish 21/5, M99 153/75, jar M342 224/206, M162 48/23. Signs with >= 8 carrier units: 72 MD, 64 HAR.
- A smoke run of `r1_main.py --smoke` with depths shuffled globally (outcome-free) was used to debug code and read planted power; no real-depth statistic has been computed.
- Prior results that shape the design: half_life (core vs frame turnover equal; Harappa HARP~Vats sign shift rho 0.48), redteam_chrono (weakened to text families: rho 0.27 without cross-dig families; frequent signs show nothing; MD M77 depth rho -0.03), direction_time_animal E3 (on seals no global time signal p=0.21; opener not the changing slot, S_oc -0.098), site_signal (MD early vs late AUC 0.61, p=0.02).

## Data and units
- Sites never pooled. MD = Mackay 1938 FEM (depth below Mackay's datum). HAR = Vats 1940 EH (depth below local surface). Marshall MIC excluded from primary (sensitivity only). Chanhu-daro too small, not used.
- Depth cleaning (`rlib.clean_depth`): sign forced negative as above; if register and M77 integer level differ by > 1.5 ft, M77 is used (OCR misreads like -78.1 for -7.8); if register depth missing, M77 integer used.
- Area stratum: M77 locus code (MD: 31, 32; HAR: Vats sub-areas). Areas with < 15 units after collapse dropped. Depth is used ONLY as a within-area rank: rel = (rank - 0.5)/n in (0,1), 0 = deepest = oldest. Depth is ordinal; no absolute time is claimed.
- Distinct texts: within each area, texts are linked into families (project rule `corpus/build.py _close`: identical, <= 1 edit for texts >= 4 signs, or a >= 3-sign text contained in a longer one). One unit per family per area; its rel = mean rel of members; its text = longest member.
- Permutation stratum = area x coarse object type (seal / sealing / tablet / other). All nulls permute rel within stratum. Statistics use rel centred within stratum, so each is a within-area, within-type comparison.

## Tests
Statistic for an item (sign, class, marker): shift = mean centred rel over carrier units (presence) or share-weighted mean (classes). > 0 = more common in shallower = later levels. z against 10,000 within-stratum permutations; two-sided permutation p.

**T1 sign / slot-class trends**
- T1a omnibus per site: sum of z^2 over all signs with >= 8 carrier units vs its permutation distribution. Holm over the 2 sites.
- T1b per sign (>= 8 carriers), both sites in one BH family.
- T1c functional-role token shares (opener, connective, short/tall numeral, fish class, title, noun, closer, post-closer, from `experiments/functional_reading/lexicon.csv`; unlisted signs = noun) plus text length (Pearson r with centred rel). One BH family across both sites.
- T1d cross-site agreement: Spearman of per-sign z between MD and HAR over shared signs; one-sided null from permuted HAR z.
- T1e half_life Harappa markers on MD: late {M127, M387, M197, M341, M72, M293} minus early {M12, M375, M205, M347} mean z on MD_FEM; one-sided permutation p.

**T2 opener vs closer turnover.** Texts with no break and >= 2 signs. Within each stratum, split at median rel into deep / shallow halves. G = sum over strata of the 2 x K likelihood-ratio statistic for first-sign types (G_open) and last-sign types (G_close). z of each vs the permutation null; D = z_open - z_close; two-sided p from the same permutations (2,000). D > 0 = opener turns over more.

**T3 markers** (presence in text): ticked fish (M60, M66, M68, M71, M73), connective M99, jar M342, M162 count frame. Tested only where >= 5 carrier units. Holm over all tested marker x site cells.

**T4 planted power** (computed on the real units with real strata, depth fixed): carriers drawn with weight exp(beta*rel), beta = 1.5 ln OR (gives shallow-vs-deep-half odds ratio of about 0.9 x OR; OR 2 -> ~1.8).
- single sign at n = 10/20/40, OR 2/3/5: nominal p < 0.05 and Bonferroni over all T1b tests;
- omnibus: 20% of the tested signs get OR 1.5/2/3 (random direction), carrier counts kept;
- each tested marker at its own n, OR 2/3, at the worst Holm threshold;
- T2: in the shallow half, a fraction f of tokens of a fraction q of slot types (n >= 3) are replaced by new variant types; (q,f) = (0.3,0.5), (0.5,0.5), (0.3,0.3); power = share of plants with D in the planted direction and p < 0.05.

## Decision rules (fixed)
- **Sign use changes with depth (Q1 yes):** T1a Holm p < 0.05 at a site OR any T1b/T1c q < 0.05. "Where" = the q < 0.05 items; an item is "replicated" if the other site shows the same direction with one-sided p < 0.05.
- **Shared across cities:** T1d one-sided p < 0.05, or T1e p < 0.05.
- **No detectable change (Q1 no):** T1a p >= 0.05 at both sites and no q < 0.05. Read as "moderate change excluded" only for sites where omnibus power at OR 2 >= 0.8; otherwise inconclusive.
- **T2:** opener turns over more if D > 0, p < 0.05; closer more if D < 0, p < 0.05; else no difference; "excluded" only for plant cells with power >= 0.8.
- **T3:** a marker shifts with depth if Holm < 0.05; a marker null counts as "no OR-2 shift" only where its OR-2 power >= 0.8.

## Sensitivity (reported, not decisive)
`r1_main.py --kind`: `block` (MD with Mackay block as area, min 8 units), `mic` (FEM + Marshall MIC with MIC areas), `m77int` (all M77 objects with integer levels, both sites), `har_seal` / `har_nonseal` (Harappa by object class). Exploratory follow-ups after the frozen run are labelled as such.
