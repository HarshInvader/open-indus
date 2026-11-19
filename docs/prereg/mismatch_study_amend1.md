# Amendment 1 to mismatch_study (target, time-depth calibration, Indus stage, real-script stage)

Written 2026-11-19 (UTC) by agent `paper`. Sealed before any run of the study. The base prereg (`mismatch_study.md`, sha256 a8d17cb2…) and the stage-1 code (`mm.py`, 04ef0c0f…) are unchanged. Nothing here alters stage 1, its planted checks or its kill rules. This adds what the study must deliver, and the stages needed to reach it.

## A. The target result (written before any data)

The result we aim for would change how both communities work. It is a **quantitative, falsifiable law for when an undeciphered script is solvable**: a closed-form boundary in three quantities that can be measured before any attempt.
1. How far the best available language model is from the true language, as excess cross-entropy, mapped from time depth.
2. Corpus size.
3. The number of known sign values (anchors).

Each is conditioned on script type. The law is fitted on one set of language families, and must predict held-out families it never saw. It must also **retrodict the real decipherments**: given only what Ventris (Linear B) and Bauer, Dhorme and Virolleaud (Ugaritic) actually had, it must say they were solvable. Applied to the Indus script at its real size, the law yields **a table of the anchors needed under each language hypothesis**. For example: "if the language is a Dravidian relative 4,000 years from Old Tamil, at least k signs must be known from a bilingual or a name before any phonetic claim is testable; with fewer, every proposal, including correct ones, is indistinguishable from a wrong key."

For decipherers, this turns "is it solvable?" into a calculation, and gives a standing test that rejects proposals made below the boundary. For computational linguistics, it is an identifiability result for unsupervised learning under model misspecification, with a measured statistical-to-computational crossover.

The paper exists only if the sealed kill criteria pass. If they fail, the failure, with the boundary we did measure, is the result.

## B. What the design must add to reach it

### B1. Text handling for Indic and other non-Latin scripts (fixes a defect found before any run)

`rt.paragraphs` keeps only Latin letters, so on Tamil, Malayalam and Sanskrit Wikipedia it yields 1,000–1,800 stray Latin words. Stage 2+ code must transliterate first, with `experiments/decipherability/langdata.indic_words` (Devanagari, Tamil, Malayalam). It is extended with the Telugu block (U+0C00) by the same rules as Malayalam, and the result is checked on 20 hand-verified words per language before use. Stage 1 is unaffected: Latin, Italian, Finnish and Estonian.

### B2. Time-depth calibration (new stage 2b)

Indus hypotheses are stated in years of divergence, not ΔH. So we calibrate ΔH against known separations, using pairs of the same lineage at dated stages:

| Pair | Approx. separation |
|---|---|
| Classical Latin (Caesar) / Italian | about 1,900 years |
| Homeric Greek / Modern Greek (Wikipedia) | about 2,700 years |
| Sangam Old Tamil / modern Tamil | about 2,000 years |
| Classical Sanskrit / Hindi | about 1,500–2,000 years |

Plus sister-language pairs with literature-dated splits: Finnish/Estonian, Tamil/Malayalam, Spanish/Portuguese.

- Output: ΔH per script type as a function of separation, with a fitted rate and a prediction interval.
- The separations and their sources are listed in the stage-2b code header before ΔH is computed. They are not tuned.
- Data still to be fetched: Modern Greek and Hindi Wikipedia; Sangam texts (Project Madurai, open).

### B3. Indus stage (new stage 6, after the law is hashed)

Simulated scripts at the Indus parameters, applied to the hashed law:
- **Sign inventory** about 400, reached by setting the logogram share, at the share where distinct signs ≈ 400.
- **Corpus** 10k–14k tokens; mean text length about 5 signs.
- **Language hypotheses**, each with a proxy model language and a time-depth band from B2:

| Hypothesis | Proxy model language | Time-depth band (years) |
|---|---|---|
| Dravidian | Old Tamil / Malayalam | 4,000–4,500 |
| Indo-Aryan | Sanskrit | 3,500–4,500 |
| Sumerian-like isolate | ETCSL Sumerian, if openly usable | nominal |

A Munda hypothesis needs a usable corpus. Without one, the table marks it "no model available".

Output: anchors needed for recovery ≥ 0.5, with intervals propagated from the law's fit and the B2 band. These are conditional statements only. No reading is proposed.

### B4. Real-script retrodiction (stage 5, made concrete)

- **Linear B.**
  - Data: DAMOS sign groups (in the repo) and a Homeric Greek model (in the repo).
  - Anchors: those Ventris could fix from Cretan place names before reading Greek, as documented in `experiments/mismatch_study/raw_real/SOURCES.md`.
  - Script parameters: the measured inventory and logogram share.
- **Ugaritic.**
  - Data: an open transliterated Ugaritic corpus and an open consonantal Hebrew text.
  - Anchors: the 1930 ones (Bauer, Dhorme, Virolleaud), as documented.
  - The script is an alphabet, which tests the script-type axis.
- **Cypriot syllabary.** Run only if an open corpus exists. Otherwise it is reported as "no open data", and criterion 4 rests on Linear B and Ugaritic.
- For each script, before running, hash the law's prediction: solvable or not given the historical anchors, and the predicted recovery with its interval.
- **Validation:** the prediction is checked against the attack actually run on the real corpus with those anchors.

### B5. Order and parallelism

1. Stage 1: planted checks, then the kill test.
2. If it survives, in parallel:
   - stage 2 (core plane);
   - stage 2b (calibration);
   - data preparation for stage 5.
3. Stage 3 (fit and hash), then the held-out families and real-script predictions, then the runs.
4. Stage 6.

The full core plane is large: 3 script types × 8 λ × 6 sizes × 7 training pairs × 10 seeds. If it exceeds about 24 laptop-hours, the owner is asked about paid compute. Until then, the plane is thinned in the order fixed here: seeds 10 → 5 first, then the 1k and 100k sizes. Thinning never touches held-out or real-script cells.

## C. Unchanged

Evidence rules, kill criteria 1–6, held-out families (not downloaded until the boundary is hashed), and the process rule: no substituting a minor audit for a failed study.
