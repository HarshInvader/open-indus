# Checking Raj (2026) "Indus Script Read as Early Dravidian, with AI Assistance" v0.7

Preregistration, 2026-11-27. Written and hashed before any control below was run. Only the reproduction of their seed 0 (T0) had been run when this was written: Tamil, real names, seed 0, held-out 217.05, identical to their stored `outputs/headline/tamil_real_0.json`.

Source: Zenodo 10.5281/zenodo.24383779 (CC BY 4.0), all files in `sources/raj_zenodo_24383779_v0.7/` (md5 equal to Zenodo's). Corpus: the ICIT copy in yajnadevam/lipi @ fc8813a, sha256 b8dcb325…5ee4, equal to the hash in their README.

We test their claims on their own code and data, and add the controls they did not run. We report every result, including results that support them.

## T0. Reproduction (their claim: Tamil +223 ± 103, 10 of 10; Sanskrit −13 ± 45)
Run their `code/contest.py` unchanged, configs `cfg_headline_tamil.json` and `cfg_headline_sanskrit.json`, seeds 0–9, modes real and null. Reproduced if every held-out value equals their stored file to 0.01.

## T1. Do the pictures matter? (picture-permutation control)
Their claim (§6): "The pictures are part of the reason." The score should then depend on which sign carries which picture words.
Method: before the contest, permute the picture-word dictionary (`words_tamil_new.json`) among the non-number signs, keeping each list intact. 50 permutations (perm seeds 1–50), each run with their seeds 0–9, real and null. Statistic per permutation: D = mean over seeds of (real − null), as in their headline. Observed D_obs comes from T0.
- Supports them: D_obs above the 95th percentile of the permuted D values (p = (1 + #{D_perm ≥ D_obs}) / 51 ≤ 0.05).
- Against them: p > 0.05, meaning the score does not depend on the sign–picture match, so it is not evidence that the signs depict Tamil words.
- Also reported: the share of D_obs above the permuted median, (D_obs − median) / D_obs.

## T2. Is the score about the inscriptions at all? (fake-seal controls)
Two kinds of fake corpus, built from the seal texts the script selects (same filter, applied before the split):
- T2a: each seal's signs shuffled into random order (same signs and lengths; order destroyed).
- T2b: meaningless seals. Signs drawn independently from the corpus sign frequencies, with real seal lengths.
20 fake corpora each (fake seeds 1–20), each run with seeds 0–9, real and null, Tamil. Statistic as in T1.
- Supports them: D_obs above the 95th percentile of both fake distributions.
- Against them: Tamil scores on meaningless seals as high as on real ones (D_obs not above the 95th percentile).
- Also reported: the mean D on fakes and the share of fake corpora with D > 0. A large positive D on meaningless seals means the method "finds Tamil" where there is no language.

## T3. Object marks: chance base rate
Their claim (§11.1): three readings name the object their sign gathers on (840 armlet on bangles, 061 copper and 705/706 smith on copper tablets). We use their scan: 296 signs × 15 object types, 101 pairs passing Bonferroni (`REP-7_object_marks/outputs/object_marks.json`, recomputed here with their code).
Object-naming rule, fixed now. A reading's English gloss (`Indus_Sign_Readings_v0.7.csv`) names an object type if it contains, as a whole word, one of these:
- BNGL: armlet, bangle, bracelet, ring
- TAB:C: copper, metal, metal-work, smith, bronze
- POT:T:g / POT:T:s: pot, jar, vessel, pitcher, potter
- SEAL / SEAL:S / SEAL:R / SEAL:C: seal, stamp
- TAG / TAG:L: tag, label, token
- ROD: rod, stick, staff
- IMPL: tool, axe, knife, chisel, implement
- TAB:B / TAB:I: tablet, token
Statistic: the number of the 101 passing pairs whose sign's reading names that pair's object type (a sign group such as 705/706 counts once per sign that passes on its own). We compute the observed count, then 100,000 permutations of the readings among all read signs in the scan (signs with 5 or more rows that have a reading).
- Supports them: observed count above the 99th percentile of the permutation counts (p < 0.01).
- Against them: p ≥ 0.05.
Also reported: copper-tablet duplication. The number of distinct sign sequences among the copper-tablet rows that carry 061 and 705/706, and the Fisher test recomputed on distinct texts (each distinct text counted once on each object type).

## T4. Stage 2 (separate plan, written after stage 1): a wrong language with a picture-rich naming style
Their Akkadian control (REP-3) had 0.5 picture options per sign against Tamil's 2.5, as they note. The fair control is a language with no proposed Indus link whose names, like Tamil's, are built from drawable things. Planned: Japanese surnames, using their translator and labeler prompts with only the language changed. Its plan will be hashed before any run.

## Comparison with Yajnadevam (descriptive, not a test)
Same corpus file (lipi @ fc8813a). We compare method, freedom and evidence type with his published key (xlits.csv) and our earlier checks (`experiments/yj_note_counts`, NEGATIVE_ATLAS 1.1).

## Execution
Their code runs unchanged except for an environment hook added in `code/contest_ctl.py` (picture permutation, fake seals; the diff against `contest.py` is saved). nice 20, at most 4 processes.
