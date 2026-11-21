# Uniformity benchmark (Fable 5.2 plan 11, candidate 1)

Prereg: `docs/prereg/uniformity_benchmark.md`, hashed with `build.py` and `run.py` in `docs/prereg/HASHES.txt` (tag `uniformity_benchmark`, 2026-11-21T07:57:43Z) before any reference AUC was computed. Ledger: `ledger_rows.csv`.

## Conclusion first

**Indus 0.49 sits below every reference corpus. The Indus null is now calibrated, and it is strange.**

- The frozen `site_signal` classifier, run unchanged on real corpora at Indus size, finds the site or phase in every pair: median AUC 0.66 to 0.89.
- Indus Mohenjo-daro vs Harappa gives 0.49. That is below the lowest reference, Latin labels with the frame removed (0.66), and far below Ur III seals (0.81 to 0.89).
- **K1 does not fire.** All 3 name-bearing pairs reach 0.65 with the frame removed (2 were needed). So the pipeline can see real local name stocks at this size. The README line "no large city-specific sign stock" stands, and it now rests on real controls, not only on a planted one.
- **K2 fires, just.** Latin with the frame removed reaches 0.657 (bar 0.65; 61% of draws reach it). Every real corpus we tested shows site signal, including the empire-wide control. The wording changes: the Indus null is not what a name-bearing script normally looks like, even one with an empire-wide name stock.
- **Prediction P3 is refuted.** Latin was predicted to sit between 0.50 and 0.65. It gives 0.71 whole. P1 and P2 pass.
- On the planted-stock scale: Indus matches a local stock of about 0% of tokens. The references match 24% to 53%.

## Numbers (200 draws each, 621 texts, 311 vs 310, Indus length mix)

| pair | variant | median AUC | 95% range of draws | null mean / q95 | p | draws ≥ 0.65 | planted-stock share |
|---|---|---|---|---|---|---|---|
| Ur III Umma vs Girsu | whole | **0.885** | 0.862-0.906 | 0.50 / 0.55 | 0.005 | 100% | 0.53 |
| | frame removed | **0.884** | 0.866-0.899 | 0.50 / 0.55 | 0.005 | 100% | 0.52 |
| Ur III Puzriš-Dagan vs Nippur | whole | **0.807** | 0.797-0.817 | 0.50 / 0.55 | 0.005 | 100% | 0.41 |
| | frame removed | **0.838** | 0.828-0.847 | 0.50 / 0.55 | 0.005 | 100% | 0.45 |
| Latin labels, Britannia vs Germania | whole | **0.713** | 0.689-0.737 | 0.50 / 0.56 | 0.005 | 100% | 0.31 |
| | frame removed | **0.657** | 0.618-0.690 | 0.50 / 0.57 | 0.005 | 61% | 0.24 |
| Proto-cuneiform Uruk IV vs Uruk III | whole | **0.834** | 0.806-0.864 | 0.50 / 0.55 | 0.005 | 100% | 0.45 |
| | frame removed | **0.877** | 0.860-0.892 | 0.50 / 0.55 | 0.005 | 100% | 0.51 |
| **Indus Mohenjo-daro vs Harappa** (old, `site_signal` P1) | whole | **0.49** | | 0.50 / 0.56 | 0.61 | | ~0 |
| Indus early vs late Mohenjo-daro (old) | whole | 0.61 | | | 0.02 | | |

- p is the smallest possible with 200 null draws.
- Secondary design at the Indus site ratio (483 vs 128, n = 611): Umma vs Girsu 0.814, Uruk IV vs III 0.786. Britannia (475) and Puzriš-Dagan (329) have fewer than 483 texts, so their 200 draws are recorded as failed, as the prereg rule says.
- Planted-stock curve (Indus P1 sample, site labels permuted, 50 repeats per step): AUC 0.49 at 0%, 0.57 at 15%, 0.62 at 20%, 0.71 at 30%, 0.80 at 40%, 0.87 at 50%.

## Prediction and kill table

| item | rule | result | verdict |
|---|---|---|---|
| P1 | Umma vs Girsu ≥ 0.80 whole, ≥ 0.65 frame removed | 0.885 / 0.884 | supported |
| P2 | Uruk IV vs III ≥ 0.70 | 0.834 | supported |
| P3 | Latin between 0.50 and 0.65 | 0.713 | **refuted** (higher) |
| P4 | Indus unchanged, nothing new scored | not rescored | as planned |
| added | Puzriš-Dagan vs Nippur ≥ 0.65 frame removed | 0.838 | supported |
| K1 | fewer than 2 name-bearing pairs ≥ 0.65 frame removed | 3 of 3 reach it | **not triggered**: README line stays, now calibrated |
| K2 | Latin ≥ 0.65 frame removed | 0.657 | **triggered** (narrowly): reword as "every real corpus tested shows site signal" |
| K3 | Latin at chance | no | not triggered |

## What this means

- Real name-bearing seals carry their city at Indus size, even after the commonest 38% of words are stripped out. The Ur III signal does not live only in the governor's "servant of" line: removing the frame (which took out dumu, dub-sar, ensi₂, the god Šara and more) left Umma vs Girsu at 0.88.
- Even Roman labels, written with an empire-wide name stock, separate two provinces at 0.66-0.71. Part of that is military: legion names and numbers are tied to provinces (the frame took LEG and some numerals but not all). Ordinary names alone may sit lower. We did not split them.
- Indus seal texts show none of this. Against these references, "no city-bound vocabulary" is a measured statement. It favours texts built from one shared, civilisation-wide stock of terms over texts that carry local personal names, gods or officials. It does not prove the texts lack names: names drawn from one shared stock with no local preference would also give 0.49.

## Caveats

- **Length mix is only roughly matched.** The references have fewer texts in some length bins, so bins were filled from neighbours by the prereg rule. Mean length per draw: Indus 4.7 signs; references whole 4.1-5.3; frame removed 3.0-3.8 (`achieved_mix.json`). Shorter texts are harder to classify, so this works against the references, not for them.
- **Different units.** Cuneiform and Latin use words, proto-cuneiform and Indus use signs. A word carries more than an Indus sign may.
- **Different design from Indus P1.** References are balanced (311:310); Indus P1 was 483:128. At the Indus ratio the two references that could be drawn still give 0.79-0.81.
- **Puzriš-Dagan** has 329 texts (316 with the frame removed), so its side of each draw changes little; the 95% ranges for that pair understate the true uncertainty.
- **Germania is a region** (mostly Germania Superior and Inferior, part of Raetia), not one province. EDH has no province field; site comes from the modern country.
- **Only references were blind.** The Indus number was known before the prereg.
- Dropped before running: Old Babylonian (no second site with 310 legends), Linear B (no site field in the repo copy), Latin Dacia (too few), Proto-Elamite (95% Susa).

## Files

- `build.py` builds `data/{ur3,pc,lat}.jsonl` from ORACC Ur III, `pc_lines.json` and EDH.
- `run.py` (`sizes`, `run`, `calib`): frozen pipeline, draws, null, planted curve. Output `draws.jsonl`, `calib.json`, `run.log`, `calib.log`.
- `report.py` → `results.json` (summary, predictions, kill rules, Indus rank). `achieved_mix.py` → `achieved_mix.json` (descriptive).

## Tests run

8 primary reference AUCs (4 pairs × 2 variants), 2 secondary (Indus ratio; 2 more failed by size), 1 planted curve. No new Indus test.

## Next

- Split Latin labels into military (legion, cohort) and civilian, to see how much of the 0.66-0.71 is unit names.
- Add the time axis properly: proto-cuneiform phases at 0.83 against Indus Mohenjo-daro bands at 0.61.
- Red team (M6): attack the reference build, the frame rule and the length filling; an independent agent should rerun Umma vs Girsu from the CDLI copy (`experiments/identifiers/data/ur3_occ.jsonl`).
