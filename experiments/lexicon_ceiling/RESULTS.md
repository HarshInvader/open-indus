# Lexicon ceiling: reading 1. With a lexicon from the same archive, the true key gains on real text at Indus size (18 of 20 draws). The restoration limit is the lexicon, not the score or the corpus size.

- **Prereg:** `docs/prereg/lexicon_ceiling.md`, sealed 2026-11-25 as v2 (tag `lexicon_ceiling`), after one fresh review. Per the coordinator's ruling it is a new study; it does not reopen `certify_size_curve`.
- **Code:** `run.py`, written without being run and hashed before the run (tag `lexicon_ceiling_code`). The wrapper checked the hash, and `run.py` checked the prereg hash and the sealed `certify_size_curve` code hash.
- **Run:** `run.py kill`, once, detached with a pid file, under the Indus compute lock and `board/run.sh`, 4 workers. Wall time was 19 min.
- **Outputs:** `kill.json`, `kill.out`, `ledger.json` (the per-draw exclusion ledger).
- **Scope:** no Indus key was scored and no Indus text was read.
- **2027 clause:** G is the gate. Hit@1 is reported on every cell as the 2027-clause measure.

## Result
- **Leakage checks before any gain:** V1, V2, V3 (canaries that could fail) and A8 all held.
  - Exclusion 2 removed 2 to 19 near-copy tablets per draw.
  - With an empty near-copy set, the new builder reproduced the sealed builder on all 20 draws.
- **Other checks:** A1 reproduced the sealed numbers exactly. F3 did not fire: trigram Hit@1 was 6.3–7.6%. A6 had zero deviation.
- **K0b, full-dose plants on the ceiling list: passed.** G was 0.38–0.50 and Hit@1 lift 3.9–5.9 points, with scramble and N1 at 0.
  - The permuted copies had a maximum G of 0.04–0.08. So the pre-stated rule FC switched the control to P2, the median of five.
  - K0b tests the code path, not power.
- **K0a, the true Old Assyrian key on real text at 1 u with the ceiling lexicon: passed.**
  - T = 18 of 20 draws reached G ≥ 0.02 (bar 16). G was 0.012–0.090, median about 0.06, with λ* = 0.25 in every draw.
  - P = 0 under the rule in force (P2), and also 0 under P1, the strict rule: every permuted copy had G = 0.
  - The shuffled-key count S was 0, and bar C held in 20 of 20.
  - **Hit@1 lift was 0.10 to 2.19 points, median 0.75.**
- **Record-only cells:**
  - The true key on the scramble had G = 0 in 20 of 20.
  - Order-1 filler had G = 0 in 5 of 5.
  - The deliberate leak, with the draw's own tablets left in the source, gave a median G of 0.068 against 0.061 without them.
- **Lexicon coverage of held-out word tokens of 4 to 7 consonants:** the ceiling list held 91.0%; the Neo-Assyrian list used by `certify_size_curve` held 31.8%.
- **Dose D:** −0.005 to 0.097 with the ceiling list, against −0.067 to +0.012 with the Neo-Assyrian list.
- **Frozen reading 1:** "The score works on real text with a matched lexicon, so the limit for Indus is that no matched lexicon can exist."

## What this can and cannot say
- **It can say:**
  - The `lift_score` / `certify_size_curve` score does have power on real text at Indus draw size (about 8,000 tokens), when the lexicon covers about 90% of the held-out words.
  - With a related but distant lexicon (32% coverage), the same key showed nothing, and more text did not help (`certify_size_curve`).
  - So the restoration closure is about lexicon match, not about the score or the corpus size.
  - For Indus, no lexicon of known match can exist, so the route stays closed. Its reason is now stated correctly.
- **Excluding the draw's own tablets barely changed G** (0.061 against 0.068 with them left in). So the gain does not come from memorising those tablets.
- **It cannot say:**
  - how much match a lexicon needs. Only two points exist: 32% and 91%;
  - anything for another script or archive. This is one script, one archive and an oracle key;
  - anything a claimant could reach. The list uses the editors' word division and includes names, so it is an upper bound no claimant could hold;
  - anything about any Indus key, and it licenses no run of one.
- **Hit@1 stays small** (median 0.75 points), even here. A G pass alone does not meet the 2027 clause.

## Disclosures
- **Implementer choices:** 28 places are marked `# PREREG-AMBIGUITY:` in `run.py`. The ones bearing on K0 are:
  - the near-copy sign count and candidate rule;
  - draw 4's A1 reference;
  - the plant vocabulary order;
  - the median of five taken as the third sorted value;
  - K0b's bars being read before FC.
- **FC switched to P2,** by the rule written before the data. Under P1 the verdict would have been the same, since P = 0.
- **The `certify_size_curve` and `lift_score` results and frozen readings are unchanged.** Their atlas entries get a pointer line.
- No rerun, no tuning, no fix tags.
