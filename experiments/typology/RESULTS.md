# Typology: are Indus name cores spelled with syllables or built from whole-word signs?

Writing-system typologist, 2026-11-14. Pre-registration: `docs/prereg/2026-11-14_typology.md` (written after the dev runs and before the held-out run). Code (run from the repo root):
- `corpora.py`: core extraction and the reference corpora
- `metrics.py`
- `q1_typology.py [split N reps Nnat maxlen]`
- `q1c_fragmentation_control.py`
- `q2_gulf.py`

Logs: `q1_dev*.log`, `q1_heldout.log`, `q2_gulf.log`. Numbers: `results.json`, `q1_heldout_L3_N200.json`, `q2_gulf.json`.

Unit: distinct core types; distinct texts for Q2. Held-out = `dev_heldout(version=2)`.

## Conclusion first

1. **Indus name cores are not spelled like Linear B or Ur III names, and they are not fixed-slot compounds.** They look like **short, free-order combinations of signs that also stand alone as whole cores**, with recurrent fixed partners. That profile fits word signs (logograms, or logo-syllabic word signs), not syllabic spelling of names.
   - The registered verdict is formally **inconclusive**: 4 of 5 tests passed, and H3 missed its threshold by 0.003.
   - **Consequence for the program:** phonetic routes that need names to be spelled sign by sign get little support. The better target is what single core signs mean.
2. **Gulf round seals: the "small repetitive phonetic subset" prediction fails.** Once person and number signs are removed, Gulf texts use a sign set as diverse as home seals, or more so (27 of 35 residue signs occur in only one Gulf text). Excess reduplication is real (p = 0.004), but it comes entirely from two texts that double the jar W740. What *is* distinctive is how many person and number signs Gulf seals carry: 51% of tokens vs 25% on home seals.

## Q1. Syllabograms or name elements?

### Method

**Core.** Starting from the functional-reading parse (`readings.csv`, `lexicon.csv`), keep only noun and fish-class tokens. Strip openers, connectives, numerals, units, titles, title blocks, closers and clitics, plus opener-class, pre-jar and post-closer induced signs. Runs do not cross line breaks, and runs that touch `#` are dropped.
- Dev: 800 distinct cores.
- Held-out: 423 distinct cores, 238 of them 2-3 signs long, using 219 signs.

**Reference corpora,** each resampled to the Indus length mix and to the same N (200 cores per subsample, 500 subsamples):

| Corpus | Type | Source |
|---|---|---|
| Ur III seal-legend personal names | logo-syllabic | CDLI, `codelib/ur3_legends` |
| Linear B words, and Linear B person names (VIR/MUL lines and KN D- series) | syllabic | DAMOS |
| Proto-Elamite entry headings | | CDLI |
| Chinese full personal names | pure logographic | downloaded to `data/` from github.com/wainshine/Chinese-Names-Corpus |
| Chinese given names | pure logographic | same |
| Synthetic fixed-slot logographic code | synthetic | generated |
| Synthetic free-order logographic code | synthetic | generated |
| Synthetic syllabary names | synthetic | generated |

**Metrics.** Positional metrics are expressed relative to each sample's own cross-core token shuffle, where 1 means no structure:
- `H_rel`: normalised initial/medial/final entropy per sign;
- `fixed_excess`: share of tokens whose sign takes one position at least 90% of the time;
- `float_rel`: signs seen at two or more offsets from both ends;
- `partner_rel`: distinct co-occurring signs per occurrence. Below 1 means fixed partners.

Also reported: types per token (productivity), and anagram rate (the same multiset in a different order). The whole-word metrics use the natural length mix:
- share of length-1 cores;
- `standalone_tok`: share of sign tokens in longer cores whose sign also forms a core on its own.

The CIs below are the 2.5-97.5% range over Indus subsamples.

### Held-out results (N = 200; dev at N = 200 and N = 400 agrees)

| Corpus | H_rel | fixed_excess | partner_rel | types/token | len-1 cores | standalone_tok |
|---|---|---|---|---|---|---|
| **Indus held-out** | **0.96 [0.91, 1.01]** | **0.01 [-0.02, 0.05]** | **0.89 [0.85, 0.93]** | **0.28 [0.27, 0.29]** | **0.34 [0.33, 0.35]** | **0.80 [0.73, 0.85]** |
| Indus dev | 0.93 | 0.02 | 0.87 | 0.26 | 0.26 | 0.45-0.68 |
| Ur III names (logo-syllabic) | 0.71 | 0.26 | 0.95 | 0.39 | 0.02 | 0.04 |
| Linear B words (syllabic) | 0.89 | 0.06 | 1.00 | 0.16 | 0.03 | 0.09 |
| Linear B person names | 0.70 | 0.21 | 1.00 | 0.29 | 0.01 | 0.06 |
| Proto-Elamite entries | 0.88 | 0.06 | 0.99 | 0.40 | 0.14 | 0.11 |
| Chinese full names (logographic) | 0.23 | 0.71 | 1.09 | 0.66 | 0.00 | 0.00 |
| Chinese given names (length 2 only, dev) | 0.85 | 0.11 | 1.01 | | 0.05 | 0.01 |
| Synthetic fixed-slot code | 0.51 | 0.50 | 1.04 | 0.42 | 0.07 | 0.09 |
| Synthetic free-order code | 1.02 | 0.00 | 1.02 | 0.41 | 0.07 | 0.08 |
| Synthetic syllabary names | 1.01 | 0.00 | 0.97 | 0.15 | 0.02 | 0.11 |
| Indus shuffled across cores (null) | 1.01 | 0.00 | 1.01 | 0.28 | | |

### Pre-registered tests (held-out)

| id | test | result | verdict |
|---|---|---|---|
| H1a | not fixed-position: H_rel ≥ 0.80 and fixed_excess upper bound < 0.10 | 0.96; 0.05 | **pass** |
| H1b | freer than real name stocks: H_rel lower bound > Ur III (0.71) and Linear B names (0.70) | 0.91 | **pass** |
| H2 | whole-word signs: len-1 share lower bound > 0.10, and standalone_tok lower bound > largest reference (0.11) | 0.33; 0.73 | **pass** |
| H3 | fixed partners: partner_rel upper bound < 0.93 | 0.933 | **fail (by 0.003)**; dev upper bound 0.90 |
| H4 | types/token between Linear B (0.16) and Ur III / Proto-Elamite (0.39 / 0.40) | [0.27, 0.29] | **pass** |

**Registered verdict: inconclusive.** The decision rule needed H1a, H2 and H3 all to pass. The direction is consistent on dev and held-out.

### Control for H2 (`q1c_fragmentation_control.py`)

Could a noisy parse that deletes core signs make syllabic names look like whole-word signs? To test this, signs were deleted at random from the reference corpora (each deletion splits the run).
- Even at 60% deletion, Linear B words reach only len-1 share 0.10 and standalone_tok 0.36.
- Ur III names reach 0.31 and 0.31.
- The synthetic syllabary reaches 0.12 and 0.70.
- None reaches Indus's 0.34 and 0.80 together.

### Interpretation

- **Positional freedom.** Indus core signs are positionally free (H_rel ≈ 1). Two things rule out a slot code like Chinese surname + given name, or the synthetic slot code (0.5): Indus has almost no fixed-position signs, and it is freer than Ur III and Linear B names, which have recurrent name-initial and name-final elements such as `ur-`, `lu2-` and `-jo`.
- **Positional freedom alone does not separate the hypotheses.** Both the syllabary and the free-order logographic code score about 1. This limitation was registered in advance.
- **What does separate them:**
  - **Standalone signs.** A third of Indus cores are a single sign, and 80% of tokens in longer cores are signs that also occur alone as a whole core. Syllabic name corpora show 2-11%, and even the logographic name corpora (Chinese, Proto-Elamite) show at most 14%.
  - **Productivity.** Types per token (0.28) is twice a syllabary's (0.15) but below logo-syllabic name spelling.
  - **Fixed partners.** partner_rel is below 1 on dev and held-out; no reference falls below 0.95. Signs come in recurrent pairs such as M171-M59, M178-M389 and M67-M244.
- **Overall picture:** short names or epithets made of one or two word signs, often in fixed pairs, in no fixed slot order. This fits "logographic name elements" better than "syllabograms", although the elements are not slot-bound.

**Caveats.**
- The cores depend on the functional-reading lexicon. "Unknown noun" may include undetected function words.
- The loose variant, which keeps numerals and titles, gives len-1 share 0.24, standalone_tok 0.52 and H_rel 0.90. That is still far from the syllabic references.
- Indus cores are short because seal legends are short. The length-matched sampling controls this for the positional metrics, but not for the whole-word metrics.
- Chinese given names could only be compared at length 2.
- Ur III names are split at hyphens, so logograms and syllables are mixed.

**Falsification.** Any of these would overturn the conclusion:
- a better segmentation (for example, bilingual-anchored) in which Indus names are mostly 3 or more signs and their signs rarely stand alone;
- a syllabic name corpus that, put through the same pipeline, shows standalone_tok above 0.5.

## Q2. Gulf round/cylinder seals (`q2_gulf.py`)

**Data.**
- **Gulf set:** 23 distinct sequences, from ICIT foreign-site round, cylinder and SEAL:C seals plus `gulf_seals.csv` rows found abroad.
- **Residue:** person signs (W090-W175) and numerals (W001-W059) removed. 20 non-empty residues, 47 tokens.
- **Home baseline:** ICIT home seals, 10,000 residue-length-matched draws.

| id | statistic | Gulf | home (95%) | p | verdict |
|---|---|---|---|---|---|
| G1 | residue types/token (smaller set predicted) | 0.745 | 0.705 [0.60, 0.81] | 0.81 | **fail**: Gulf is more diverse |
| G2 | texts with a repeated sign | 0.100 | 0.008 | 0.010 | pass (α = 0.0125) |
| G3 | adjacent reduplication | 0.074 | 0.004 | 0.004 | pass |
| G4 | cross-text sign overlap (Jaccard) | 0.018 | 0.039 | 0.94 | **fail**: Gulf texts share fewer signs |

- **Registered rule** (G1 and (G2 or G3)): **not supported.**
- **Robustness.** Confirmed/probable rows only, home round seals as the baseline, and M77 "West Asian finds" all give the same pattern:
  - G1 p = 0.82-0.98;
  - G3 p = 0.003-0.025.
- **Where all the reduplication comes from:** `W740 W740` (Karzakan, where gulf_seals.csv notes "middle is a motif") and `W467 W550 W001 W740 W740` (no find-spot). W740 is the jar closer (M342). Doubling the jar is not syllable reduplication.

**What is distinctive about Gulf seals.**
- Person and number signs make up 51% of tokens (home seals 25%).
- Person signs alone make up 24% (home 7%).
- So the "person + numeral" block dominates the Gulf texts, as paragorth noted.

**Candidate "syllabogram" set** (residue signs in at least 2 Gulf texts, with Gulf/home rate ratio):
- W924 (41x)
- W831 (22x)
- W190 (20x)
- W350 (5x)
- W415 + W803 (2x; they occur together twice, both times opening an Ur seal (IM77 9846 and an ICIT Ur seal), each followed by W001)
- W220 (fish, 1.2x)
- W740 (jar, 0.3x)

Each of these appears in only 2-3 texts, so no repetitive core set exists.

**Name shapes.**
- Gulf residues are 1-4 signs long: AB ×6, ABC ×4, ABCD ×3, AA ×1, ABCC ×1.
- Any-repeat rate: Gulf 0.13, home 0.02, Ur III syllabically spelled names 0.16, Linear B names 0.05. The Gulf rate looks name-like, but n = 15 and both repeats are the jar.
- `cdli-meluhha-attestations.json` gives no Meluhhan-language personal name to match. The Ur III Meluhhans carry Sumerian names: ur-{d}lamma dumu me-luh-ha (×6), ur-{d}ig-alim. /nanasa/ is not in the file.
- **No shape match to Akkadian, Amorite or Dilmunite names can be tested at this n.**

## Hypotheses

| Hypothesis | Verdict |
|---|---|
| Indus core signs are fixed-slot name elements | **refuted** (H_rel 0.96, fixed_excess 0.01) |
| Indus names are spelled syllabically, like Linear B or Ur III names | **disfavoured** (standalone_tok 0.80 vs ≤0.14 in every reference; survives a 60% deletion control) |
| Cores = 1-2 free-order whole-word signs with fixed partners | **supported in direction**; registered verdict inconclusive (H3 missed by 0.003) |
| Gulf seals spell foreign names with a small repetitive sign subset | **refuted** (G1 p = 0.81, G4 p = 0.94); the reduplication is a doubled jar |
| Gulf seals are dominated by person + number blocks | **supported** (descriptive: 51% vs 25% of tokens) |

**Tests run:** Q1, 5 confirmatory plus about 40 descriptive comparisons; Q2, 4 confirmatory plus 16 robustness.

## Next experiments

1. Re-run Q1 on ICIT new-site texts (Dholavira) through the bridged parse, as an out-of-corpus replication of H2 and H3.
2. Treat single core signs as the semantic target. Cluster the 145 single-sign held-out cores by their co-occurrence with titles, field symbols and object type, to look for "name element" meaning classes (deity, animal, quality).
3. Gulf: move from residue statistics to the person + number block itself, asking whether the numeral after the person sign varies the way a counted rank or a clan number would. Get better readings of the four "missing" Gulf seals (6, 17, 20, 25).
