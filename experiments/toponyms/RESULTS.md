# Toponym test (Jemdet Nasr city-seal method, Fable plan F7)

Code: `common.py`, `explore.py` (discovery only), `confirm.py` (pre-registered), `sensitivity.py` (post hoc). Logs: `explore_*.log`, `confirm_dryrun.log`, `confirm_final.log`, `sensitivity.log`. Machine-readable: `results.json`, `confirm_final.json`, `sensitivity.json`. Pre-registration: `docs/prereg/toponyms.md`, hashed with `common.py` and `confirm.py` before the final run (`docs/prereg/HASHES.txt`, tag `toponyms`; hashes re-checked after the run, unchanged). Frozen predictions: `docs/prereg/2026-11-15_toponym_predictions.md` (hashed). Ledger rows: `topo_*` in `docs/test_ledger.csv`.

## Conclusion first

1. **No Indus sequence behaves like a travelling place name.** Sequences that are concentrated at one site do not turn up elsewhere on clay sealings (the objects that move) more often than other texts at those sites. Confirmation half: ICIT 66 off-home sealings vs 71.9 expected (p = 0.82); M77 held-out 11 vs 14.6 (p = 0.84). On all of ICIT (56 candidates, 3,863 off-home units): 171 vs 184.7, observed/expected 0.93 (about 0.79-1.07). The test had the power to see a real effect: planted power was 0.83 (ICIT) and 0.73 (M77) at odds ratio 3 at the confirmatory alpha, and 0.93 at odds ratio 2 on full data. Per the pre-registered rule this counts as **refuted at stated power**.
2. **The reverse pattern is absent too.** Sequences found on seals at only one site and on sealings only at other sites are rarer than chance: ICIT 7 vs 13.0 expected (p = 0.96), M77 12 vs 19.4 (p = 0.96).
3. **Some local vocabulary does exist, but it stays at home.** Sequences enriched at one site in the discovery half stay enriched in the independent half of ICIT: 56 vs 35.9 expected (ratio 1.56, p = 0.0005, passes alpha 0.00625). This did **not** replicate on M77 held-out (9 vs 6.8, p = 0.26; power only 0.73 at ratio 2). The ICIT result is mostly one item. Without the stroke-numeral candidates it weakens to 40 vs 30.5 (p = 0.031, post hoc).
4. **The strongest single local item is a Chanhu-daro end mark: M93 (Wells writes it W031 W032).** It occurs in 10 of 10 M77 texts at Chanhu-daro (9 seals, 1 sealing found there), and 8 of 9 in ICIT. The ninth is a bare numeral pair on a Kalibangan pot, probably not the same item. It replicated in both splits (M77 dev to held-out 2/2; ICIT A to B 3/3). It sits at the end of the text or alone on line 2. None of the roughly 190 sealings found at other sites carries it. So it is a Chanhu-daro scribal habit, or possibly a local name that never left. The data cannot tell those apart, because almost no Chanhu-daro sealings survive.
5. **The Dholavira signboard signs are not Dholavira signs.** Its 8 distinct signs are not enriched at Dholavira (38 vs 39.1 expected, p = 0.61). Three of its 8 bigrams recur elsewhere (Lothal, Harappa, Mohenjo-daro), never at Dholavira. W820, its first and repeated sign, is the common opener, most frequent at Mohenjo-daro. This is exploratory: the signs were fixed in advance, but the dry run saw the result before the prereg.

Reading: the vocabulary is pan-Indus with small local habits (Chanhu-daro end mark, Harappa W806 W154, Lothal W527/W575), and nothing local travels on sealings. This agrees with paragorth S11, S105 and S308 (no city signs; within-Mohenjo-daro quarter groups are a weak lead) and with context Q3 (sealing texts do not travel more than seal texts). It adds what they lacked: a held-out replication, a travel test with demonstrated power, and the reverse test.

## Method

- **Unit.** Distinct (site, medium, sequence). Medium for ICIT: SEAL* = seal, TAG* = sealing, TAB:B/I = tablet, TAB:C = copper, POT* = pottery, everything else = other. M77 uses object_type mapped the same way. Near-copy families follow the v2 rule (identical; <= 1 edit with both texts >= 4 signs; a >= 4-sign text contained in another). Enrichment counts one unit per (site, family), so a seal and its impressions, or one mould's tablets, count once per site. Travel and reverse tests use (site, medium, family).
- **Split.** M77: dev / held-out v2. ICIT: text families shuffled (seed 20261114) and alternated into halves A (discovery, 1,899 units) and B (confirmation, 2,018). A site hold-out would leave the small sites no home to replicate on. ICIT and M77 overlap in objects, so they count as one replication, not two.
- **Enrichment null (site-size-aware).** Site labels are permuted among units within medium, which keeps every site x medium total. This controls Harappa and Mohenjo-daro dominance and object-type registers (README #6). Candidate = obs >= 3, obs/exp >= 2, p < 0.05 in discovery. That gave 25 ICIT and 33 M77 candidates out of 631 / 835 site x feature tests. The discovery tests alone are weak: 0 ICIT tests reach q < 0.1, and 13 have p < 0.01 against 6.3 expected.
- **Travel.** S1 = pooled (observed − expected) off-home sealing units, with each unit's expectation set by its own site's sealing rate. Null A permutes medium labels within site. S2 is the register control: it compares the off-home excess with the home excess. Secondary: a frequency-matched feature null; a version with Mohenjo-daro and Harappa homes dropped; a broad mobile set (sealing + tablet + pottery).
- **Power.** Planted answers on the confirmation data. T1: off-home occurrences moved to the home site until the home ratio reaches 1.5, 2 or 3. T2: off-home mobile odds multiplied by 2, 3 or 5, with site rates recomputed. 30 replicates x 200 permutations each. An earlier version of the power code did not recompute site rates after planting, which gave falsely low power (0.03 at OR 5). It was fixed in the dry run, before the prereg.

## Pre-registered tests (alpha 0.05/8 = 0.00625)

| id | hypothesis | ICIT (half B) | M77 (held-out v2) | verdict |
|---|---|---|---|---|
| T1 | enrichment replicates | 56 vs 35.9, p = 0.0005; power 1.0 at ratio 1.5 | 9 vs 6.8, p = 0.26; power 0.13 / 0.73 at ratio 1.5 / 2 | ICIT supported; M77 not |
| T2a | off-home units on sealings | 66 vs 71.9, p = 0.82; power 0.40 / 0.83 / 1.0 at OR 2 / 3 / 5 | 11 vs 14.6, p = 0.84; power 0.27 / 0.73 / 1.0 | refuted |
| T2b | off-home units on sealings, tablets or pottery | 437 vs 508.8, p = 1.0 | 22 vs 29.3, p = 0.95 | refuted (opposite direction) |
| T4 | reverse (seal at one site, sealings elsewhere) | 7 vs 13.0, p = 0.96 | 12 vs 19.4, p = 0.96 | refuted |

Secondary checks:
- Frequency-matched null for T2a: ICIT p = 0.76, M77 p = 0.89.
- Small-site homes only: ICIT p = 0.80, M77 p = 0.77.
- S2 (register-controlled): ICIT p = 0.26, M77 p = 0.09. Not significant, and S1 is negative in both.
- Broad-media S2 is positive (ICIT p = 0.017; full data p < 0.001). This comes from home occurrences sitting on seals even more than expected, not from off-home tablets or pots. Off-home units are under-represented on the broad mobile media in absolute terms (O/E 0.86).

Pre-registered verdict: no corpus passes T1 and T2. M77 fails T1 and T2a with T2a power 0.73 at OR 3, so it counts as refuted at stated power. ICIT passes T1 alone, which means local vocabulary, not travel.

## Exploratory (post hoc, not counted)

| check | result |
|---|---|
| Full-ICIT travel, 56 candidates | 171 vs 184.7 off-home sealings, p = 0.88; power 0.93 at OR 2 (alpha 0.05) |
| ICIT T1 without numeral candidates | 40 vs 30.5, p = 0.031 |
| ICIT T1 without Chanhu-daro homes | 33 vs 25.7, p = 0.06 |
| Enrichment among small sites only (Mohenjo-daro, Harappa removed) | 14 tests p < 0.01 vs 2.4 expected; 7 at q < 0.1 (top: W111 Nausharo, W031 W032 Chanhu-daro, W550 W527 and W527 Lothal, W740 W400 Kalibangan) |
| Signboard bigrams elsewhere | W820 W611 Lothal (other), W388 W820 Harappa (pottery), W645 W031 Mohenjo-daro (other); none at Dholavira |

## Frozen predictions

Four items replicated individually (O_home >= 2, O/E >= 2 on the confirmation half). They are frozen in `docs/prereg/2026-11-15_toponym_predictions.md`:
- K1: M93 = W031 W032, Chanhu-daro.
- K2: W920 W060, Chanhu-daro.
- K3: W806 W154, Harappa.
- K4: M254, Lothal.

Each has a "home" prediction and a "travel" prediction for new finds. The file also freezes the general null: no new sequence will be site-enriched and travel on sealings. The toponym reading comes back if PK1-travel or PK-travel passes, or the null fails.

## Caveats

- **Sealings are scarce outside Lothal, Dholavira and Kalibangan.** Mohenjo-daro and Harappa sealing rates are about 1%, and Chanhu-daro has one. A toponym of a site whose sealings were never exported, or were not excavated, cannot show travel. The power figures assume the observed site mix.
- **M77 "sealing" at Harappa and Mohenjo-daro is mostly moulded tablets** (context Q2). The M77 T2a is partly a tablet test.
- **The candidate rule admits numerals and register signs.** Examples: W740, the jar, at Lakhanjo-daro; W031 and W032. It was not tuned after the dry run, by design. Such candidates add noise to T2 but cannot create a false positive, because their off-home units follow the general site mix.
- **Travel here means same-text-family occurrences at a different site.** Imported sealings with a never-seen text cannot be linked to a home.
- **All results rest on Wells' and Mahadevan's sign lists.** A place name written with a site-specific variant that these lists lump together would be invisible.

## Hypotheses

| hypothesis | verdict |
|---|---|
| Some sequences are enriched at one site beyond size and object mix, and replicate | supported (ICIT); inconclusive (M77, underpowered) |
| Site-enriched sequences travel on sealings or other mobile media (toponym or ethnonym) | refuted at stated power |
| Reverse: one-site seals whose texts appear on sealings elsewhere | refuted |
| Dholavira signboard signs are Dholavira-specific | not supported (exploratory) |

## Next experiments

1. **Chanhu-daro end mark K1.** Check the CISI photographs of the 10 texts to see whether M93 is a numeral pair or a distinct ligature. Look for Chanhu-daro sealings in later reports.
2. **Look for local names at a finer scale.** Repeat the travel test inside Mohenjo-daro by quarter (paragorth S308 lead: 9 quarter-bound groups, p = 0.02), using sealings and tablets found in other quarters.
3. **Use foreign finds as the travel set.** Test whether square seals found abroad carry home-site-enriched sequences of a particular Indus city (Lothal or Dholavira for the Gulf).
