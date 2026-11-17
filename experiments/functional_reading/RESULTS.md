# Functional reading: a role grammar that "reads" every Indus text without phonetics

Synthesis grammarian, 2026-11-14. Code: `fr.py` (grammar, lexicon, reading layer), `g1_design_dev.py` (template design, dev only), `g2_tests.py` (held-out and ICIT tests), `g3_readings.py` (readings + lexicon), `g4_controls.py` (planted answer + lexicon null). Run from the repo root as `.venv/bin/python experiments/functional_reading/<script>.py` (the scripts import `fr` from their folder, so `cd` into the folder or add it to `PYTHONPATH`). Outputs: `readings.csv` (all 3,445 M77 object-side texts), `lexicon.csv` (413 entries), `results.json`, logs `g*_tests.log`.
Unit: distinct texts (`distinct()`/`dev_heldout()`), unless a file lists objects (readings.csv lists every object side, with a `split` column).

## Conclusion first

1. **A small functional grammar parses about three quarters of unseen texts, and the order it encodes is real.** It has 11 roles (opener, connective, short numeral, tall numeral, unit, fish-class noun, bracketed-fish closer, noun, title, closer, post-closer clitic) and a left-to-right template fitted on dev only. It fully parses **76.0% of held-out texts against 33.4 ± 1.6% of the same texts shuffled within the text** (z = 27.5). On ICIT texts from sites absent from M77 it parses **77.2% (shuffled 37.1%)**, and at **Dholavira 77.5% (shuffled 38.2%)**. The evidence-based role lexicon beats role sets permuted among the same signs: 0.760 vs 0.510 ± 0.131 held-out coverage, p = 0.01 (200 permutations).
2. **What the parse adds beyond a sign bigram is legibility, not prediction.** On every predictive test, a plain sign model is as good or better:
   - **Object type** (seal / tablet / copper / pottery): roles alone carry real information (held-out macro-AUC 0.672 vs label-permutation null 0.52, 95th pct 0.58). But a sign bag does better: 0.786, and parse features added to the bag give 0.784 (difference −0.002, 95% CI −0.027 to +0.025). On ICIT new sites: bag 0.658, parse 0.620, both 0.665.
   - **Masked signs** (2,197 held-out positions): bigram MRR 0.506, grammar 0.454, both combined 0.476, unigram 0.189. Predicting the *role* of a missing sign: grammar 60.1%, role of the bigram's best guess 62.6%, majority role 40.8%.
   - **Foreign texts:** round/cylinder seals found in the Gulf and West Asia fail to parse 53% of the time vs 22% for native new-site texts (AUC 0.66, p = 0.009). Grammar bits/sign separate them with AUC 0.71, the bigram with AUC 0.75. With all foreign objects pooled, parse failure alone is not significant (AUC 0.56, p = 0.11).
3. **What this deciphers:** the *syntax of the document*, not its words. For every text we can say which sign opens it, where the numerals are and which counting system they belong to, which sign closes it, whether it carries the tablet/rod clitic M176, whether it holds a shared title block, and whether it has the tablet-reverse docket formula. For 50.8% of tokens in distinct texts we can also name a *meaning category* (grade B or C): numeral class, measure unit, closer, register marker, fish-class name element. **Not one sign has a sound or a word meaning.** "Title", "unit" and "name element" are functional labels backed by distribution and object context, not translations.

## Method

**Roles and template (`fr.py`).** A probabilistic finite-state grammar over roles. Each sign may only be emitted by the roles its lexicon entry allows.
- **Hand-assigned roles and categories** (`HAND`, `NAMED_COMPOUNDS`) only where another team's result supports them. Each comes with its evidence and a grade:
  - A = replicated on held-out data or ICIT, or a structural fact on both corpora;
  - B = significant in one corpus, or consistent but small;
  - C = suggestive.
- **Dev-only positional induction** for frequent signs that have no hand entry (n ≥ 5 dev texts): opener-class, closer-class, pre-jar title, post-closer. These get role grade C and no meaning.
- **Everything else is "unknown noun".**
- **Transitions.** The strict template says:
  - texts open with an opener, numeral, noun, fish or closer;
  - connectives follow openers;
  - numerals precede a head;
  - closers are followed only by closers or clitics;
  - clitics are final.

  Starting from that, `g1_design_dev.py` greedily added single transitions that increased *coverage minus shuffled coverage* in 5-fold CV **within dev**. It kept two: noun→connective (pre-opener nouns before M99, e.g. `M219 M381 M99 …`) and noun→clitic. The template was then frozen. Probabilities were fit by EM on dev.
- **Reading layer.** It groups the Viterbi roles into constituents: OPENER (+connective), NUMBER-NAME, NUMBER+NOUN, COUNT+MEASURE, TITLE-BLOCK, REGISTER formula, FORMULA (dev bigram with conditional share ≥ 0.5), CLOSER, DOC-TYPE CLITIC. It glosses them with category names only.
- **Lines that do not parse** are cut greedily into parsable pieces. They are marked `!cut@` in `parse_roles` and their confidence is halved.

**Bridge.** ICIT W signs are mapped to M signs through `bridge_WM.json` (first M listed). Unbridged signs become `OOV` and are allowed only as unknown nouns. Results are given both for fully bridged texts and for texts with OOV signs.

## Findings with numbers

### (a) Parse coverage (`g2_tests.py`, 20 within-text shuffles each)

| set | n | parsed | shuffled | z |
|---|---|---|---|---|
| dev, in-sample (reference) | 1,588 | 0.812 | 0.322 | 68 |
| dev, 5-fold CV (design) | 1,588 | 0.807 | 0.329 | |
| **held-out, no break** | 525 | **0.760** | 0.334 ± 0.016 | 27.5 |
| held-out, break edges open | 533 | 0.764 | 0.341 | 27.0 |
| held-out seals / tablets+sealings / copper / pottery | 371 / 110 / 14 / 17 | 0.757 / 0.791 / 0.929 / 0.765 | 0.301 / 0.372 / 0.464 / 0.621 | 29.7 / 12.9 / 5.1 / **1.8** |
| ICIT new sites, fully bridged | 104 | 0.788 | 0.338 | 13.0 |
| ICIT new sites, OOV = noun | 189 | 0.772 | 0.371 | 13.8 |
| **Dholavira**, fully bridged / OOV = noun | 42 / 80 | 0.762 / 0.775 | 0.296 / 0.382 | 8.2 / 9.0 |

- **Lexicon null** (`g4_controls.py`): the hand role sets were permuted among the hand-assigned signs, then refit on dev. Held-out coverage 0.510 ± 0.131 vs real 0.760; 1 of 200 permutations reached it (p = 0.01).
- **Main causes of parse failure in held-out texts:** an opener that is not first (M267 16, M391 9, M150 5: "pre-opener" material such as `M238 M267 M99 M104 M169`), M99 at text start (4), and bare numerals. The noun→opener edge would recover these, but on dev it raised shuffled coverage as much as real coverage, so it was rejected.
- **Pottery** is barely distinguishable from its shuffles (z = 1.8). Pottery marks are short, so order constrains them little. The grammar describes seals and tablets, not graffiti.

### (b) Object type from the parse (logistic regression, class-balanced, fit on dev)

| features | held-out macro-AUC | bal. acc. | ICIT new sites macro-AUC |
|---|---|---|---|
| sign bag (+ length, lines) | **0.786** | 0.582 | 0.658 |
| parse roles only (role counts, role bigrams; no sign identities) | 0.672 | 0.394 | 0.619 |
| parse roles + constituent labels + slot fillers | 0.713 | 0.431 | 0.620 |
| sign bag + parse | 0.784 | 0.543 | **0.665** |

- Labels permuted on train, roles only: macro-AUC 0.520, 95th percentile 0.577.
- Paired bootstrap, parse (slot fillers) − bag: −0.073 [−0.114, −0.037] on held-out; −0.038 [−0.091, +0.010] on ICIT.
- **Verdict:** abstract document structure alone predicts object type (roles only, 0.67 ≫ null). This confirms that registers are *structural*, not only lexical: tablets end in J+P, and dockets are T+U. But the parse loses information compared with the sign identities, so the claim "parse beats sign bag" is **refuted**.
- Held-out counts: seal 391, tablet 120, copper 20, pottery 20. ICIT counts: seal 192, tablet 80, pottery 58; copper tablets occur only at Mohenjo-daro.

### (c) Missing-sign prediction (each position of 461 clean held-out runs of ≥3 signs masked in turn; 2,197 positions)

| model | MRR | top-1 | top-10 | median rank |
|---|---|---|---|---|
| unigram | 0.189 | 0.103 | 0.339 | 21 |
| role grammar | 0.454 | 0.378 | 0.602 | 4 |
| KN bigram | **0.506** | **0.390** | **0.726** | **2** |
| grammar + bigram (log-linear 1:1, fixed in advance) | 0.476 | 0.367 | 0.692 | 3 |

- Combined − bigram MRR: −0.030 [−0.039, −0.021].
- Role-of-gap accuracy: grammar 0.601, bigram 0.626, majority role 0.408.
- **Verdict:** the role grammar captures most of what the bigram knows (it reaches 84% of the bigram's MRR gain over unigram) but does not add to it. This matches the novel_methods finding that a slot template captures 57% of the bigram's bits gain. The functional grammar is a **compressed, readable description of adjacency**, not a source of new predictive structure.

### (d) Foreign texts

| comparison | n native / foreign | parse fail native vs foreign | AUC parse-fail (p) | AUC grammar bits (p) | AUC bigram bits (p) |
|---|---|---|---|---|---|
| M77 held-out "West Asian finds" vs native held-out | 533 / 4 | 0.24 vs 0.50 | 0.63 (0.24) | 0.64 (0.19) | 0.78 (0.03) |
| ICIT foreign, all objects, vs ICIT new-site native | 286 / 30 | 0.22 vs 0.33 | 0.56 (0.11) | 0.66 (0.004) | 0.72 (0.001) |
| ICIT foreign round/cylinder seals vs new-site native | 286 / 17 | 0.22 vs **0.53** | **0.66 (0.009)** | 0.71 (0.002) | 0.75 (0.0005) |

The parse reproduces the context team's Gulf result: round seals abroad break Indus order. It does so with an interpretable reason, for example no closer, or a numeral without a head. Example: `9801 M173 M10 M97 M121 M185 M97 M297 M57` parses only as a run of nouns and numerals, with no opener, title or closer. The bigram still discriminates better. The square-seal West Asian texts (e.g. 9822) parse as ordinary Indus texts, in line with the context team's finding.

### Controls
- **Planted answer** (`g4_controls.py`). A synthetic corpus was sampled from the fitted grammar: 2,258 distinct texts, true role of every token known. The full pipeline was re-run on 75% of it.
  - Coverage on the remaining 25%: 0.993; shuffled 0.379.
  - Token role accuracy 0.970: hand-labelled signs 0.991, positionally induced signs 0.914, default nouns 0.941.
  - For 90% of the 40 induced signs, the induced role set contains the true majority role.
  - So the machinery can recover roles at this corpus size **if** the corpus is generated by such a grammar. This is a check that the method works, not evidence that Indus is such a grammar. Real held-out coverage (0.76) is well below the planted ceiling (0.99), so about a quarter of real texts lie outside the template.
- **Tests run:** 11 coverage comparisons, 4 classifiers × 2 test sets plus 6 bootstraps and 1 permutation null, 4 masked models plus 1 bootstrap plus 3 role baselines, 3 × 5 foreign AUCs, 2 controls: about 50 in all. Survivors under Bonferroni (α ≈ 0.001):
  - all held-out, ICIT and Dholavira coverage margins except pottery;
  - roles-only object type vs null;
  - grammar < bigram and combined < bigram on masked signs (CIs exclude 0);
  - ICIT foreign grammar and bigram bits.

  These do not survive: foreign parse failure (p = 0.009), the lexicon null (p = 0.01, at the permutation floor) and every M77 West-Asian test (n = 4).

## Lexicon summary (`lexicon.csv`)

- **Signs:** 372 entries.
  - Role grade A: 38 (openers M267/M391, M99, jar M342, M176, M1, M211, M169, M328, strokes, M343/344/345, M403).
  - Role grade B: 23 (fish paradigm, bracketed fish, M123, M293, M150, M347, M8, M162, M15, M254, M12, M190, M407, M18, M387).
  - Role grade C: 64, almost all induced from dev positions.
  - Unassigned ("unknown noun"): 247.
- **Sequences:** 41 (5 grade A: 6+fish, M336-M89 title block, M51-M130 title block, M103-M403, M342-M176).
- **Meaning categories on signs:** 34 at grade B (numeral class and system, measure unit M328, register markers, the closer), 25 at grade C (fish-class name element, title elements M347/M8, M190 unit, emblem-logogram candidates M362/M363/M346/M184). 313 signs have none.
- **Token shares** (distinct M77 texts):
  - role grade A 40.6%, B 20.2%, C 12.0%, unknown noun 26.7%, unseen 0.5%;
  - meaning category B 34.1%, C 14.5%, none 51.4%.
- **Readings** (`readings.csv`): 3,445 object sides. 2,904 (84.3%) parse fully. Confidence bands: high 1,334, medium 1,267, low 844. Confidence is the mean grade weight of a text's signs, halved if the text does not parse.

## Twenty informative inscriptions (structured readings)

Notation: role tags after each sign; [CONSTITUENT: signs]. HO = held-out (never seen in fitting). Glosses use categories only.

1. **4348 (Harappa moulded tablet, HO side 1).** Side 1: `[NUMERAL: M121 (12)] [TITLE-BLOCK: M51+M130+M149] [CLOSER: jar M342] [DOC-TYPE CLITIC: M176]`. Side 2: `[COUNT+MEASURE: M87 (tall 2) + M328]`. *Reading:* "12 · title block · closing word · tablet clitic // 2 units." This is the full two-sided pattern: an identity text with a seal-style title block on the front, a tall-stroke + cup docket on the back (shaunmortal F15). Confidence: front medium, back high.
2. **4718 (Harappa miniature tablet).** Side 1: `[NOUN M343] [NOUN M162] [NOUN M343] [NUMERAL M86] [TITLE-BLOCK M336+M89+M211]`. Side 2: `[COUNT+MEASURE: M89 (tall 3) + M328]`. The same title block that closes seal names (F28) appears here on a tablet front, with docket value 3 on the back.
3. **1087 (Mohenjo-daro seal, 13 signs).** `[NUMBER+NOUN M87+M244] [NOUN M28] [NOUN M162] [CONNECTIVE M99] [FISH M65] [FISH M67] [NUMBER-NAME M87+M59] [TITLE-BLOCK M51+M130+M149] [CLOSER M342]`. The longest seal legend parses as a pre-opener stretch, then connective, fish-class names, a number-name, title block and closer. Two independent "counted" elements: tall-2 + M244, tall-2 + fish.
4. **2251 (MD seal).** `[OPENER M267+M99] [TITLE-BLOCK M336+M89+M211]`. The minimal "formula + title" text: opener formula and a shared title block with no individual element. Fits F26's repeated "title" texts.
5. **1326 (MD seal, HO).** `[OPENER M267+M99] [FISH M72] [FISH M65] [TITLE-BLOCK M336+M89+M211]`. Same frame with an individual part of two fish-class elements: [opener][individual][title block + closer], exactly as F28/F29 predict.
6. **4116 (Harappa seal, HO).** `[OPENER M391+M99] [NUMBER-NAME: 6 (M109, 3-over-3) + fish M59] [CLOSER M12]`. The 6+fish compound (language team: 12/28, p = 1e-4) in its usual slot after the opener formula. The compound is grade A; its meaning (Parpola's Pleiades) is grade C and untested.
7. **4356 (Harappa moulded tablet).** Side 1: `[NUMBER-NAME 6+fish] [CLOSER M211] [DOC-TYPE CLITIC M176]`. Side 2 (HO): `M336 M267 M341 [COUNT+MEASURE M89+M328]`. This side does **not** parse, because M267 is not first. The front reuses the seal number-name; the back has the docket after unparsed material.
8. **6211 (Chanhu-daro seal, HO).** `[OPENER M267+M99] [NUMBER+CLOSER: tall-2 M87 + bracketed fish M60]`. The bracketed fish fills the closer slot (novel_methods T6). No jar is needed.
9. **7038 (Lothal seal).** `[OPENER M391+M99] [NUMBER-NAME tall-2+fish M59] [BRACKETED-FISH CLOSER M73]`. Plain fish inside, bracketed fish at the end, in one text: the bracket marks position, not a different word class.
10. **1705 (MD copper tablet, side 1).** `[FISH M65] [TITLE-BLOCK M336+M89] [REGISTER M407+M169] [NOUN M183] [CLOSER M169]`. This is the "hare" legend (context Q2b), read as fish-name + shared block + the copper closing formula. The legend labels its picture as a whole; no sign here means "hare".
11. **2904 (MD copper tablet, HO, 2 lines).** `[NOUN M171] [TITLE M8] [CLOSER M342] || [FORMULA M171+M59] [REGISTER M407+M169]`. A seal-type line (title + jar) plus a copper-register line.
12. **1529 (MD ivory rod).** `[FISH M67] [NUMBER-NAME M103+M403] [CLOSER M342] [DOC-TYPE CLITIC M176]`. Rods take the M342-M176 ending (context: 9 vs 0.5 expected) and the bound numeral compound M103→M403 (F7).
13. **3039 (MD seal).** `[OPENER M267+M99] [NUMERAL tall-1 M86] [NUMBER-NAME M103+M403] [CLOSER M342]`. Tall and short numerals together in one text, each in its own system.
14. **1021 (MD seal, HO).** `[OPENER M293+M123] [NOUN M345 jar+3] [FISH M65] [FISH M67] [TITLE-BLOCK M51+M130+M149] [CLOSER M342]`. The second opener family (M293-M123). The jar-with-strokes M345 is mid-text: a name element, not the closer.
15. **1549 (MD seal, HO).** `[OPENER M391] [NOUN M341] [CONNECTIVE M99] [NUMBER-NAME tall-2+fish] [TITLE-BLOCK M51+M130+M149] [CLOSER M342]`. A noun between opener and connective (the dev-chosen noun→connective edge).
16. **1468 (MD seal).** `[OPENER M391+M99] [NUMBER-NAME tall-2+fish] [FISH M72] [TITLE M8] [CLOSER M342]`. The most common full template: opener, number-name, individual, title, jar.
17. **2822 (MD sealing, HO).** `[CLOSER M342] [DOC-TYPE CLITIC M176]`. The ending formula alone, as a complete text on a tablet: the register marker without an identity.
18. **9822 ("West Asian finds" seal).** `[NOUN M173] [NOUN M403] [CONNECTIVE M123] [NUMBER-NAME 3+fish] [TITLE-BLOCK M249+M162] [CLOSER M342]`. It parses: a seal found abroad written in ordinary Indus grammar, as the context team found for square seals abroad.
19. **9801 ("West Asian finds" seal).** `M173 M10 [NUMBER+NOUN M97+M121+M185] [NUMBER+NOUN M97+M297] M57`. Formally accepted, but only as a string of nouns and numerals with no opener, closer or title, and two numeral stacks in a row (1+12). This is the profile of the anomalous Gulf texts.
20. **1003 (MD seal; fails to parse).** `[NUMBER+NOUN M86+M55] ! [OPENER M267+M99] [NUMBER-NAME 12+fish M72] [TITLE-BLOCK M336+M89+M211]`. The commonest failure: material *before* the opener formula. Either a second phrase (an owner's prefix?) or a sign that is really an opener. The template does not cover it.

## What this does and does not decipher

**Does (with the stated grades):**
- It assigns a functional role to 73% of tokens (grades A-C) and identifies the document parts: opener formula, connective, numeral (and which of the two stroke systems), unit, title block, closer, tablet/rod clitic, docket formula.
- These parts are stable on unseen texts, on another transcription and at a city absent from M77 (Dholavira).
- It turns the independent results of four teams (positional classes, two stroke systems, registers, bracketed fish, 6+fish, title blocks, side-1/side-2) into one consistent reading of every text, with confidence and an evidence trail per sign (`lexicon.csv`).

**Does not:**
- **No sign has a sound or a lexical meaning.** "Title block", "unit", "fish-class name element" are categories of distribution and context. M328 is a "measure/commodity unit" because tall strokes count it on tablet reverses, not because we know what it measures. M342 is "the closing word of title/office-type legends", not "of" or "-an".
- 26.7% of tokens are "unknown noun". These include most of the individual part of names, which is where identity lives (F26). The categories therefore read the *frame* of a text, not its *content*.
- The grammar adds no predictive power beyond a sign bigram (tests b and c). It is a readable re-description of adjacency plus outside context, not hidden structure.
- About 24% of held-out texts fall outside the template, mostly through pre-opener material. Pottery graffiti are not constrained by it.
- A functional slot grammar of this kind fits a language-writing system and a non-linguistic labelling system equally well. Nothing here decides whether the script writes language.

**What would falsify it:** new texts (e.g. CISI vol. 3 or Rakhigarhi) parsing at shuffled-level rates; tall strokes counting short-only heads on new tablets; M176 appearing on seals at tablet rates; bracketed fish in initial position in a larger sample.

## Hypotheses tested

| # | Hypothesis | Verdict | Key number |
|---|---|---|---|
| H1 | A role template built from other teams' evidence parses unseen texts far above shuffled order | **Supported** | held-out 0.760 vs 0.334 (z = 27.5); ICIT new sites 0.772 vs 0.371; Dholavira 0.775 vs 0.382 |
| H2 | The evidence-based role assignments beat permuted assignments | **Supported** (at the permutation floor) | 0.760 vs 0.510 ± 0.131, p = 0.01 |
| H3 | Abstract role structure carries object-type information | **Supported** | roles-only macro-AUC 0.672 vs null 0.52 |
| H4 | Parse predicts object type better than a sign bag | **Refuted** | 0.713 vs 0.786 (Δ −0.073 [−0.114, −0.037]) |
| H5 | Grammar predicts masked signs better than a bigram, or adds to it | **Refuted** | MRR 0.454 / 0.476 vs 0.506 |
| H6 | Parse failure flags foreign (Gulf round-seal) texts | **Supported, weakly** (does not survive Bonferroni) | 53% vs 22% failure, AUC 0.66, p = 0.009; bigram AUC 0.75 |
| H7 | The pipeline recovers planted roles at Indus size | **Supported** (machinery check) | token role accuracy 0.97; induced signs 0.91 |
| H8 | Pottery graffiti follow the same template | Inconclusive / no | z = 1.8 (n = 17) |

## Next experiments
1. **Pre-opener phrase.** Test a two-phrase template (noun phrase + opener phrase) with its own lexicon for pre-opener signs. Validate on dev CV against the shuffle margin; the single noun→opener edge failed that test.
2. **Separate dev models per register** (seal vs tablet grammar) and test whether register-specific grammars beat the sign bag on object type.
3. **Score new lots blind:** freeze `fr.py` and `lexicon.csv` (hash them), then parse CISI vol. 3 or newly published texts. Coverage and the slots of numerals and closers are the predictions.
4. **Extend the bridge** so all Dholavira texts can be parsed without OOV nouns. Check whether Dholavira's lower bigram predictability (structure §6) sits in the "unknown noun" slots, as a regional-names hypothesis predicts.
5. **Get pottery-specific evidence** (tall strokes as counts, F33) before giving graffiti their own template.
