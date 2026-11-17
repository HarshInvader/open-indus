# Pre-registration: assemblage co-occurrence (Fable 5.2 plan 3, R7)

Registered 2026-11-14 in `experiments/assemblage/`, BEFORE any inscribed text was joined to a craft context. What had been looked at when this was written: the findspot fields of the merged ICIT export (counts of inscribed objects per findspot unit and object type, no signs), and report passages (Vats 1940, Mackay 1938, Mackay 1943, Marshall 1931 vol. II, Frenez & Tosi 2005) to see how craft evidence is recorded. No sign was looked at by findspot. Hash of this file goes into `docs/prereg/HASHES.txt` (tag `assemblage`); the craft coding table `experiments/assemblage/craft_units.csv` and its builder are hashed (tag `assemblage_coding`) before `test.py` joins texts to it.

## Question

Is any sign tied to a craft or facility? If a sign names a craft product, workshop, guild or facility, texts found where that craft was practised should carry it more often than texts elsewhere at the same site, and the same sign should do so at a second site (local habits stay home, so one site is not enough).

## Data

- Inscribed objects and findspots: `sources/paragorth_Indus-/data/derived/merged-corpus-reading-order.json` (ICIT export with `area-section`, `block-house`, `room-grid`; signs in Wells numbers). Lothal sealing contexts: Frenez & Tosi 2005 Table 1 (paragorth transcription, `lothal-sealings-frenez-tosi2005.json`), W/W1/W2 = warehouse, O = outside.
- Craft evidence: coded from the excavation reports only, blind to texts, into `craft_units.csv` (one row per findspot unit x craft indicator, with report page/line citation).

## Units

- Harappa (Vats 1940 grid): Vats big square, e.g. `I13` from `room-grid` `-I13/7`. HARP trenches without a grid square are excluded (no open craft data per trench).
- Mohenjo-daro: area | block | house (house blank = block-level unit).
- Chanhu-daro: Mackay 1943 square, e.g. `8/C`.
- Lothal: each Frenez & Tosi sealing is its own unit (warehouse vs outside).
- Other sites: included only if the coding yields craft units.

## Craft contexts (indicator classes)

BEAD (unfinished beads, bead blanks/cores, stone drills), SHELL (shell waste, cores/columellae, unfinished shell objects, raw conch), COPPER (crucible, slag, ore, furnace, casting waste), SEALCUT (unfinished seals, steatite/faience working), WEIGHT (weights, finished or unfinished), KILN (pottery/stoneware/faience kilns), STORAGE (granary, warehouse). A unit is in context c if the reports record at least one indicator of class c there.

## Objects

- **Primary:** non-seal inscribed objects (sealings/tags, tablets, pottery, copper tablets, bangles, rods, implements, misc.). Seals travel with people.
- **Secondary (reported, counted separately):** all inscribed objects including seals.
- One record per distinct sign sequence per unit (moulded copies in one unit count once).

## Test

- Statistic per (sign, context, site): T = number of distinct-text records containing the sign in units of context c.
- Null (spatial permutation, site fixed): context labels are permuted among the site's linked units, within area strata (Harappa mound letter of the area field; Mohenjo-daro area-section; Chanhu-daro and Lothal unstratified), keeping unit contents intact. 10,000 permutations; one-sided p = (1 + #null >= obs)/(1 + n).
- Eligibility (does not use context labels for signs): sign occurs in >= 5 distinct-text records among a site's linked units; context has >= 2 linked units and >= 1 non-context linked unit at that site. A (sign, context) pair is testable if eligible at >= 2 sites. K = number of testable (sign, context, site-pair) combinations.
- **Decision rule (primary):** a pair is REPLICATED if at two sites p <= sqrt(0.05/K) each AND observed/expected >= 2 at both. (Under the null, both p values fall below a with probability a^2, so this holds the family-wise rate at 0.05 over K.)
- **Global test (secondary-confirmatory):** G = number of testable (sign, context, site-pair) combinations with p <= 0.05 at both sites and O/E >= 2 at both; null distribution from the same joint permutations; pass at p <= 0.05.
- **Power:** a synthetic sign at the median eligible frequency is planted with odds ratio 3 and 5 for context units at two sites (Harappa and Mohenjo-daro if both have the context; otherwise the two best-populated sites); power = share of 200 replicates passing the per-pair rule with the observed K.

## Interpretation (fixed now)

- **Supported:** >= 1 REPLICATED pair in the primary set. It would still need red-team and a check that the sign is not an object-type register artefact (README #6) before entering README.
- **Refuted at stated power:** 0 replicated pairs AND G not significant AND planted power at OR 3 >= 0.5.
- **Inconclusive:** 0 replicated pairs with power < 0.5.
- **Untestable:** K = 0 (no context reaches eligibility at two sites). Then the deliverable is `assemblages.csv` plus a list of the look-ups a person must do.

## Known risks

- Report coding is selective: only illustrated or noteworthy objects get findspots, so absence of an indicator is weak evidence. Units without indicators are "not recorded", not "no craft".
- Few non-seal inscribed objects have house/square findspots outside Harappa (Vats) tablets. Expect K to be small or zero.
- Harappa tablets repeat texts across units; within-unit dedup removes copies only within a unit.
- Exploratory looks after the run (other units, HARP trenches, seals) are labelled exploratory.
