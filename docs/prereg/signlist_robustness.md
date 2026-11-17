# Pre-registration: do the ranked findings survive other sign lists?

Registered 2026-11-15, BEFORE any test was run under any variant. The sign-list variants were built and
inspected (`experiments/signlist_robustness/variants.py`, `variants.json`: label counts and cluster
membership only, no test statistics). Code: `experiments/signlist_robustness/harness.py` (hashes appended
to `docs/prereg/HASHES.txt` before the first run).

## Question
Every ranked finding (README #1, #3, #5, #6, #7, #9, #10, #11) was measured on Mahadevan 1977 (M77) sign
identities. Does each finding survive when signs are lumped and split differently?

## Variants (frozen)
| id | what |
|---|---|
| M77 | baseline (identity); also checks that the harness reproduces the published numbers |
| ICIT | Wells/Fuls native W numbering, its own corpus (5,679 inscriptions) |
| parpola | M77 relabelled with every lump Parpola makes relative to Mahadevan, observed by aligning 150 CISI Mohenjo-daro seals (Parpola P codes) with ICIT and the Wells-Mahadevan bridge. Partial (108 M signs covered). Parpola splits of an M sign cannot be applied token by token and are listed, not applied |
| lump_fish | all 12 plain fish -> one sign; all 5 ticked fish -> one sign |
| lump_numerals | stroke numerals lumped by (system, value), layout ignored (M108 = M109 = short six) |
| lump_jar_man | jar M342 = M343 = M344 = M345; man variants; bearers; man+stick; man+jar; birds |
| lump_all | all of the above + trees, rakes, ovals, leaf-in-oval, arcs (incl. opener M293 with M287), U-cups, M347/M348, and the Mahadevan-Wells unified clusters (309 labels) |
| split_s1, s2, s3 | every sign with >= 50 M77 tokens (67 signs) split into 2 or 3 allographs, token by token at random; three seeds |
| img_hi, img_mid, img_lo | average-linkage clusters of Mahadevan's drawings (blurred 32x32 silhouettes + aspect) cut at 360, 300, 240 labels |

**Sign-specific tests under a variant.** A sign set S (e.g. ticked fish) is the set of labels whose members
include an S sign. If a label contains signs from both sides of a tested contrast (e.g. a ticked and a plain
fish), the test is **NT (not testable: the contrast is erased by definition)**. For random splits, S = all
allographs of S (so the test probes the rest of the corpus).
Lexicon roles (functional grammar) for a label = union of the hand-assigned roles of its members; if no member
has a hand role, dev-positional induction decides as in `functional_reading/fr.py`. ICIT signs get hand roles
through the bridge (first M sign of the W entry); ticked fish W226/W232/W234/W236/W241, plain fish
W220/W231/W233/W235/W240, two-tier six W016, fish W220, jar W740 (codes from `redteam/r1_fish.py`, `r2_sixfish.py`).

**Splits.** M77 variants keep the v2 family split by text identity (`dev_heldout(version=2)`); held-out texts whose
variant sequence equals a dev variant sequence are dropped (lumping can create copies). ICIT: distinct
flattened sequences are clustered at edit distance <= 1 and families are split 75/25 at random (seed 0).

**Units.** TYPE = one count per distinct sign sequence (primary). TOKEN = every object-side record, mould
duplicates included, in both training and test. Survival is judged on TYPE; TOKEN is reported.

## Tests and survival criteria (held-out unless stated)
| id | finding (README #) | statistic | survives if |
|---|---|---|---|
| T1 | order beats permutations (#1) | add-0.1 bigram on dev; held-out complete runs of 3-7 signs with >= 6 distinct permutations; share where true order is strictly best | share >= 2 x chance AND one-sided p < 0.001 (normal approx to the Poisson-binomial) |
| T2 | ticked fish to final slot (#3) | final share of ticked-fish tokens in held-out runs (len >= 2) vs 2,000 frequency-matched sign sets (same number of labels) from the dev 10-80 band | p < 0.05 AND ticked share > plain-fish share |
| T3 | M109 + M59 fixed (#5) | held-out tokens of label(M109) followed by label(M59), binomial vs dev base rate of label(M59) | k >= 3 AND p < 0.01 |
| T4 | registers (#6) | logistic regression on sign presence (dev) -> held-out per-class AUC vs 500 label permutations | >= 4 of the classes with n >= 5 above their permutation 95th percentile AND mean AUC >= 0.65 |
| T5 | L-R reversals (#7) | KN bigram on R-L lines; copy-free L-R lines (not within edit 1 of any R-L line) scored as labelled vs reversed | share >= 0.70 AND binomial p < 0.001 |
| T6 | name cores of 1-2 word signs (#10a) | cores = maximal N/F runs in the functional parse; held-out len-1 core share and standalone token share | len-1 share >= 0.28 AND standalone >= 0.22 (2 x the maxima of syllabic references, 0.14 / 0.11) |
| T7 | fixed pair order (#10b) | HD3: adjacent core pairs with a dev majority (incidence >= 2, >= 2/3); held-out agreement | share >= 0.75 AND p < 0.001 |
| T8 | fish lexical class (#11) | SC1 set coherence, SC5 fish+fish, SC7 partner-set transfer (2,000 reps) | >= 2 of 3 with p < 0.05. NT if the fish family is one label |
| T9 | functional parse vs shuffle (#9) | held-out full-parse rate vs 20 within-text shuffles | difference >= 0.20 AND z >= 5 |

**Verdict per finding.** ROBUST: survives in every testable variant (for random splits: >= 2 of 3 seeds).
SENSITIVE: fails in 1-2 testable variant families but never reverses sign. FRAGILE: fails in >= 3 families or
reverses. Variant families: ICIT, parpola, lumps (4 variants, each its own family), splits (3 seeds = one
family), images (3 cuts = one family; fails if >= 2 of 3 fail).

These are robustness re-tests of findings already in the ledger, not new claims; ledger rows use mode
`robustness` and are excluded from the project FDR family. No threshold will be changed after running.
README #2 (logo-syllabic sign count), #4 (Gulf seals) and #8 (copper types) are not re-tested here.

**Calibration note (added before any non-M77 variant was run).** The M77 baseline was run once to check the
harness: T1-T5 reproduce the published numbers exactly (40.2% vs 5.7%; 11/19; 7/10; 31/34; AUCs above null).
The reimplemented core extraction gives len-1 0.39 / standalone 0.84 (published 0.34 / 0.80), HD3 85/107 = 0.79
(published 115/138 = 0.83), parse 0.75 vs shuffle 0.40 (published 0.76 vs 0.33). Thresholds unchanged.
