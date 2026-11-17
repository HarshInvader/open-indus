# One-to-many substitution (X <-> YZ): does a single sign ever trade places with a 2-3 sign spelling?

Substitution agent, 2026-11-14 (Fable 5.2 plan item 5). Pre-registration: `docs/prereg/substitution.md` (hash in `docs/prereg/HASHES.txt`, written before any held-out test). Numbers: `results.json`. Logs: `*.log`.
Unit: distinct M77 texts from `dev_heldout(version=2)` with no `#` and `|` removed (dev 1,675, held-out 564). ICIT was run separately in native Wells numbers (2,567 distinct texts), and its sites absent from M77 were bridged to M numbers for replication.

## Conclusion first

**No Maya-style phonetic substitution system shows up in the Indus texts. Held-out data confirms the null. The test has real but limited power, so this is a bounded negative. It does not close the phonetic route.**

1. **Dev is at chance.** 55 equations reach q<0.05, and 11 of them pass the system-consistency filter (SCEs). Planted corpora with no alternation give 12.5 ± 7.3 SCEs, and the detection threshold is 26.1. Indus has 3 shared spelling signs; the no-alternation corpora average 4.6.
2. **The only "system" is a paradigm, not a syllabary.** The recurring spelling is the fixed pair **M336 M89**. It stands in for several *different* fish signs (M59 k=8, M67 k=8, M249, M259). A phonetic spelling belongs to one word. One pair standing for many words is a slot filler: a name core of 1-2 word signs, as in typology and core_semantics.
3. **Held-out: 0 of 11 SCEs replicate** (pre-registered rule: at least 3). The best is M59 = M336 M89 (k=3 new frames, p=0.024, q=0.23). **ICIT new sites: also 0 of 11**, but only 63 of 243 new-site texts survive the W->M bridge. Among all 55 dev equations, 11 replicate in held-out. All 11 are slot/paradigm alternations: fish ↔ fish pair, fish ↔ M336 M89, closer ↔ closer + post-closer.
4. **Power.** Two planted controls at Indus genre size (q = 0.5: each alternating word is spelled phonetically half the time):
   - **Synthetic, n=1,675.** Rule D reaches 80% power at p=0.5 (alternating logograms make up 39% of word tokens). A decipherer-usable system (≥3 planted SCEs sharing a sign) needs p=0.75 (62% of word tokens).
   - **Indus dev with a system planted into it,** so the real confounds are kept: 80% power at p=0.3 (29% of tokens) for D, and p=0.1 (12%) for the oracle rule.
5. **Upper bound.** Indus's 11 SCEs are hard to reconcile with alternation covering ≥ about 20% of word tokens: P(n_SCE ≤ 11) = 0.00-0.08 for synthetic p ≥ 0.2, and 0.00 for the Indus-matched plant at p=0.1 (12% of tokens). Alternation on ≤ 10% of logograms (8% of tokens; P = 0.33) **cannot** be excluded.
6. **A real script would also "fail" this test.** Ur III Sumerian/Akkadian seal legends are genuinely logo-syllabic. Cut to 2,300 texts, the same pipeline gives about 450 significant equations per sample, and **0 of them are phonetic** (5 samples). They are word paradigms, e.g. dumu "son" = dub-sar "scribe". Only one phonetic equation (saga = sa6-ga) recurs at all. So a zero at Indus size says little about whether the script was phonetic.

**Verdict.** There is no evidence for logogram ↔ phonetic-spelling alternation in Indus. A heavy, Maya-like alternation that touches a fifth or more of the word tokens is unlikely. Light alternation is untestable with this corpus, and seal-legend genres hide it even in scripts known to be phonetic. The phonetic route is weakened, not closed.

## Method

- **Mining** (`common.mine`). Text A = …L X R…, text B = …L Y R…, where Y is 2-3 signs and X is not in Y; plain insertions belong to internal_phonetics T1.
  - L tier: flanks of 2+1 or 1+2 tokens (text edges count), with ≥2 real signs.
  - W tier: whole-text frames, a subset of L (for k=2 this is internal_phonetics' T3 event set).
  - Dev: 20,778 L events and 4,118 W events.
- **Independent frames.** Events of one equation are merged when they share a text or a 2+2 context, so a family of near-copies counts once. The support k of an equation is its number of independent frames.
- **Nulls.**
  - (i) Frame-matched: Y strings are permuted among frame units within (slot, length), which keeps every frame and both marginals. This gives a per-equation Poisson tail at the null mean, then BH.
  - (ii) Within-text shuffle, as the brief asked: 10 shuffles give **20 equations at q<0.05** on average. So null (i) is anti-conservative at the per-equation level: slot formulas and Zipf frequency make "one sign vs a frequent pair" recur by chance.
  - Because of (ii), every decision is calibrated on planted corpora, not on q.
- **SCE filter.** q<0.05, and no sign of Y is X or a 1↔1 paradigm partner of X (a sign filling the same exact 2+2 frame). This removes fish = fish + fish type alternations. Planted syllabic spellings pass it.
- **System score.** Counts spelling signs shared by ≥2 SCEs with different X.
- **Rule D.** n_SCE above the 95th percentile of no-alternation corpora of the same size (FPR 0.08 in 12 runs).

## Planted controls (`sim.py`, `run_power.py`, `power_summary.py`; 12 corpora per cell)

- **A. Synthetic Indus-genre corpora** (internal_phonetics' `Synth`, imported unchanged).
  - Mean length 4.4-4.5 and about 340 sign types; Zipfian words (55% logogram, 15% logogram+logogram, 20% syllabic, 10% logogram+syllable).
  - Openers, connectives, closers and post-closers; near-copy families calibrated to Indus edit-1 neighbour rates.
  - A fraction p of logogram signs gets a 2-3 syllable spelling from the same 50 syllabograms the syllabic words use. Each occurrence uses it with probability 0.5.
- **B. Indus dev with a planted system.** A fraction p of Indus signs (≥2 tokens) gets a spelling from 50 new pseudo-syllabograms. Each occurrence is respelled with probability 0.5.

| corpus | p (token share) | n_SCE | planted SCEs | planted eqs in ≥2 frames | power D | oracle power | P(n_SCE ≤ 11) |
|---|---|---|---|---|---|---|---|
| synthetic 1,675 | 0 | 12.5 ± 7.3 | 0 | 0 | 0.08 | 0 | 0.58 |
| | 0.1 (8%) | 17.8 | 0.8 | 1.4 / 24 | 0.17 | 0 | 0.33 |
| | 0.2 (19%) | 30.0 | 2.4 | 3.7 / 52 | 0.42 | 0.25 | 0.00 |
| | 0.3 (26%) | 38.3 | 3.0 | 5.2 / 75 | 0.75 | 0.33 | 0.08 |
| | 0.5 (39%) | 48.5 | 4.3 | 7.7 / 119 | 0.83 | 0.58 | 0.00 |
| | 0.75 (62%) | 76.8 | 7.5 | 11.1 / 179 | 1.00 | 0.83 | 0.00 |
| | 1.0 (82%) | 97.2 | 8.7 | 14.2 / 236 | 1.00 | 0.83 | 0.00 |
| synthetic 2,300 | 0 / 0.3 / 1.0 | 24.2 / 57.9 / 174.8 | | | 0.08 / 0.67 / 1.00 | 0 / 0.50 / 1.00 | |
| synthetic 2,300, 4× more copies per name (mult 0.6) | 0 / 0.3 / 1.0 | 42.6 / 87.7 / 222.9 | | | 0.08 / 0.92 / 1.00 | 0 / 1.00 / 1.00 | |
| Indus dev + plant | 0.1 (12%) | 32.1 | 7.0 | 8.2 / 28 | 0.58 | 1.00 | 0.00 |
| | 0.3 (29%) | 65.2 | 15.8 | 18.3 / 81 | 1.00 | 1.00 | 0.00 |
| | 0.5 / 1.0 | 116 / 273 | 27 / 50 | | 1.00 | 1.00 | 0.00 |

**What limits power.** Even with every logogram alternating, only 6% of planted equations (14 of 236) ever appear in two independent frames at Indus size. Short texts and about 10% near-copy families leave few aligned pairs. More copies per name help a lot (oracle power 1.0 at p=0.3 with mult 0.6), so a corpus of re-attested names, such as sealings of the same person, would be the place to look. At 2,300 texts the p=0 baseline rises faster than the planted signal, so rule D's 80% point moves up to p=1.0.

**Plant caveat.** The Indus-matched plant uses pseudo-syllables that never double as word signs. That makes it easier than a real system, so its bound (12%) is optimistic and the synthetic bound (about 20%) is more realistic.

## Indus dev: top candidates (L tier, frame-matched null; examples are M77 text numbers)

| equation | k | λ | q | example (X text \|\| Y text) | reading |
|---|---|---|---|---|---|
| M321 = M89 M211 | 2 | 0.002 | 0.001 | 2844 M336 M321 M176 \|\| 1251 M72 M336 M89 M211 M176 | SCE; M336 + {M321 \| M89 M211}; held-out 0 |
| M87 = M53 M171 | 4 | 0.09 | 0.001 | 2429 \|\| 1429 | core sign ↔ lexicalised pair; held-out k=2, q=0.004 |
| M59 = M336 M89 | 8 | 0.93 | 0.002 | 2532 \|\| 1326, 3016, 4028 | SCE; fish ↔ the M336 M89 pair; held-out k=3, q=0.23 |
| M102 = M53 M171 | 4 | 0.14 | 0.003 | 1365 M102 M59 M211 \|\| 2183 M53 M171 M59 M211 | numeral-type ↔ pair |
| M72 = M171 M59 | 8 | 1.2 | 0.005 | 4056 \|\| 1198 | fish ↔ X + fish |
| M99 = M402 M123 | 2 | 0.009 | 0.005 | 7054 M267 M99 M102 \|\| 2635 M267 M402 M123 M102 M15 | opener formula (cf. M99\|M402, internal_phonetics) |
| M402 = M99 M59 | 2 | 0.012 | 0.006 | 1103 \|\| 4232 | opener formula |
| M216 = M70/M65 M222 | 2 | 0.012 | 0.006 | 1096 M267 M99 M67 M216 M254 \|\| 1447 M53 M67 M70 M222 M254 | M222 is M216 with an inner mark; fish + marked form ≈ plain form. Held-out k=1, q=0.02; ICIT W550 = W231 W555 is the same equation |
| M12 = M342 M176 | 4 | – | 0.02 | 5123 \|\| 8201 | closer ↔ closer + post-closer (internal_phonetics T3); held-out k=3, q=0.01 |
| M211 = M342 M1 | – | – | – | held-out k=6, q=0.004 | closer formula |

- **ICIT (native Wells):** 100 at q<0.05, 20 SCEs. The same structure appears in Wells numbers: W240/W235/W231/W070 (fish) = W705/W706 W033 (= M336 M89), W233 = W415 W220 (M72 = M171 M59), W550 = W231 W555 (M216 = M70 M222).
- **Wells-only artefact:** the strongest equations (W706 = W233 W705, q=1e-9) involve W705 and W706, which are both M336 in the bridge. They are a Wells split of one Mahadevan sign, so they are X ↔ X + fish insertions, not substitutions.

## Hypotheses

| # | hypothesis | verdict |
|---|---|---|
| H0 | Recurrent X ↔ YZ equations exceed chance on dev (rule D) | **not supported** (11 vs 12.5 ± 7.3 null; threshold 26.1) |
| H1 | Dev SCEs replicate in held-out / new sites with shared signs (prereg) | **refuted at this power** (0/11 and 0/11) |
| H2 | Recurrent equations form a shared-syllable system | **not supported**: the shared sign comes from one pair (M336 M89) standing for many fish signs |
| H3 | Alternation covers ≥20% of word tokens | **unlikely** (P ≤ 0.08 synthetic, 0.00 plant) |
| H4 | Alternation covers ≤10% of logograms | **untestable** at this size (power ≤ 0.17) |
| H5 | Single sign ↔ two-sign core substitutions exist (paradigm) | **supported**, and replicates in held-out (11/55). These are word ↔ compound or slot-formula alternations, as in typology/core_semantics |

**Tests run:**
- Dev: W tier 142 and L tier 831 recurrent equations; 10 within-text shuffles.
- ICIT: 1 native run.
- Planted corpora: 216.
- Real scripts: 6 runs (Ur III ×6, Linear B ×1).
- Confirmatory: 11 × 2 (H1) and 55 × 2 (H2, descriptive).

## Caveats

- The per-equation q is anti-conservative (shuffled texts give 20 at q<0.05). Only planted-calibrated counts and held-out replication carry weight.
- The SCE filter and the "M336 M89 = paradigm" reading were set on dev, and the M336 M89 exclusion was written into the prereg before held-out.
- Power depends on q = 0.5 and on the synthetic family structure. A script that alternates rarely per word (q around 0.1), or only in some genres, would be invisible here.
- ICIT new-site replication is thin: only 63 of 243 texts survive the W->M bridge.
- The phonetic labelling of Ur III equations uses an automatic transliteration match. It may miss some true equivalences (e.g. CVC vs CV-VC spellings with different index signs), so "0 phonetic" is a lower bound.
- Linear B (2,300 lines, mean 4.6) was run descriptively. Its top equations are syllable fragments (i = si-jo); it has no logogram ↔ spelling alternation in frame to test.

## Next experiments

1. Re-attested persons: sealings and moulded tablets with several impressions per name. Power rises sharply with copies per name (oracle power 1.0 at p=0.3 with mult 0.6).
2. Bridge more Wells signs, or run every test in native Wells numbering with the Wells-split pairs (W705/W706) merged, to make the new-site replication real.
3. Test M216 / M222 (+ fish) on CISI photographs: is M222 a fish-marked M216, i.e. a graphic modifier rather than phonetics?
4. Real control with a known alternation rate: Maya or Luwian hieroglyphic name labels, if a machine-readable corpus can be obtained. None was available offline.
