# Bench of two more 2026 claims: Kriger & Hunt "registration codes" and Adelman "convergent Dravidian" (board task #6, H5)

## Verdict

**Negative for the registration-code reading. The Dravidian key could not be benched.**

- Kriger & Hunt's four testable signature results were re-run on our corpus, on the same population they used: Mohenjo-daro unicorn seals, 646 objects (603 distinct texts) against their 179.
  - **Uniqueness is reversed.** The texts are *less* unique than chance, not more.
  - **The edge pattern replicates, but the project already knew it.** Edges have lower entropy than the middle. Opener and closer signs were established long ago (Mahadevan), and SIGIL shows the pattern is not specific to codes.
  - **The numeral claims fail.** Numerals do not concentrate in the penultimate slot. Their "digit 2 dominates" result is mostly the M99 connective, not counting.
  - **The near-duplicate claim does not survive.** Near-duplicates do differ at edges, which contradicts "never at edges". They differ there a little less often than positional structure alone predicts, but this falls short of the pre-registered threshold on unicorn seals, and the tendency is absent on other seals.
- **Adelman 2026 (Academia.edu).** The full text is behind a login (HTTP 403), so no sign-value table is available and there is nothing to bench sign by sign. The abstract claims "systemic coherence to the rarest sign, ~100%". That is the free-choice signature this project has already shown to be uninformative: §1.1 in the atlas, and Yajnadevam in `experiments/language`.

Pre-registration: `docs/prereg/bench2026_kriger_hunt.md` and the script `experiments/bench2026/kh_tests.py`. Both sha256 hashes were appended to `docs/prereg/HASHES.txt` before any outcome was computed. The planted control was run before the real statistics.

## Sources actually read
- **Kriger & Hunt, Zenodo 19103880 (paper 1) and 20040472 (paper 3, "credit cards").** Only the abstracts, via the Zenodo API. The PDF downloads returned 403 ("unusual traffic") and the 403 was not bypassed. Paper 2 is PhilArchive KRIWWP and returned a Cloudflare challenge, so it was not read either. Every claim tested below is stated in the abstracts.
- **Raghavendra, arXiv 2608.02999 (SIGIL).** Full text.
- **Tiwari 2026, NLP4DH, pp. 314-319.** Full text.
- **Adelman, Academia.edu 178522550.** Abstract snippets from a search engine only.

## Kriger & Hunt: results (populations and nulls as pre-registered)

U = M77 Mohenjo-daro unicorn seals. These are complete, with no breaks and line breaks removed. S = all other M77 seals (825 objects), used for replication. UR = 4,060 distinct Ur III seal legends, word level, used as a linguistic name-genre comparator. Each test used 2,000 null draws (500 for UR).

| Test | Their claim | U (unicorn, Mohenjo-daro) | S (other seals) | Verdict |
|---|---|---|---|---|
| K1 uniqueness (object level) | 98.3% unique vs null 91.2% | **88.2%** unique. N1 random redeal: 99.2% (5-95%: 98.3-100). N2 positional redeal: 97.5% (96.6-98.5). Real is below every draw of both nulls. | 86.8% vs N1 98.4%, N2 97.5%. Real is again below every draw. | **Reversed.** Texts repeat more than chance (formulas and duplicates), not less. This agrees with joyboseroy and atlas 10b.4. |
| K2 positional entropy, length-5 texts | Edges constrained, middle diverse | Middle minus edges = +0.86 bits (n = 120). Within-text shuffle null 0.00 (95th pct 0.25), p < 0.0005. | +0.88 bits (n = 160), p < 0.0005 | **Replicated, but not new and not diagnostic.** The Ur III comparator shows the opposite sign (−4.9 bits, because the personal name leads), so this comparator does not show non-specificity. SIGIL does: a sound-free emblem system reproduces positional concentration (arXiv 2608.02999 §§5-8). The pattern fits Mahadevan's opener and closer classes, which is long known (atlas 3.3, 10b.6). |
| K3a numerals in penultimate slot | Concentrated there | 19.0% of numeral tokens vs 18.7% under within-text shuffle (95th pct 21.4), p = 0.46 | 20.8% vs 19.8%, p = 0.25 | **Not replicated.** |
| K3b "2" is 66.9% of numerals | Read as a count distribution | Value 2 = 55.6% of 505 numeral tokens. M99 (connective double stroke) alone is 195 tokens. Without M99, value 2 = **27.7%**. | 46.6%, and 20.3% without M99 | **Formula artefact.** Their "digit 2" is mainly the M99 connective of the opener formula, below the pre-set 0.30 bar. Numeral share of tokens replicates: 16.6% here vs their 15.4%. |
| K4 Hamming-1 near-duplicate pairs, edge share | Never at edges (p = 0.008) | **20 of 80** pairs differ at the first or last sign: share 0.25. N2 positional null mean 0.45 (5th pct 0.25). p(≤ obs) = 0.060. | 52 of 94 = 0.55 vs null 0.46, p = 0.84 | **Not supported at the pre-registered rule.** "Never at edges" is false: 20 edge pairs. On unicorn seals, edge changes are somewhat rarer than positional structure predicts. The result sits exactly at the null's 5th percentile (p = 0.06), short of the pre-set "< 5th pct" bar and not Holm-significant across the 4 tests. It is absent on other seals. |

**Planted control for K4** (`kh_planted.json`). Serial-number-style variants were added to a positional-null corpus, each one differing from a base text in one middle slot. The test caught them with power 0.22 when 10 were planted and 0.67 when 25 were planted. The test therefore has moderate power. A real excess of about 25 middle-slot variant pairs would usually be seen. The U result (p = 0.06) is consistent with a small effect of that kind, so it should not be read as a strong negative on K4 alone.

**Ur III comparator.** At word level, near-duplicate Ur III legends differ at an edge 97.7% of the time (null 99.5%), mostly in the name. The Ur III result therefore says nothing for or against an Indus code reading. It is reported only because it was pre-registered.

**C5, duplicates as "replacement issuance" to the same holder (paper 3).** This was not re-tested. Existing results contradict it:
- Repeated seal texts cross sites at random: R 0.89, against 0.18 for Ur III personal seals (atlas 10b.4).
- Repeated 4+ sign texts are not local: 43% same-site pairs vs 45% at random (10b.9).
- A holder's replacement seal would stay at one site.

**Overall.** Neither signature result of the registration-code reading survives:
- Uniqueness is reversed.
- The near-duplicate locus is at most a borderline effect on one subcorpus.

What does replicate (edge constraint, numeral share) is generic positional structure. Codes, emblem systems and formulaic labels all share it. Nothing here refutes an identifier or code function. It shows only that these statistics do not support one. That matches the atlas 3.1 and 3.2 status (language vs code untestable with current comparators).

## Other 2026 papers: what changes in how we state headline claims

- **SIGIL (arXiv 2608.02999).**
  - A sound-free generative emblem system gets the Indus category on every one of the 6 exactly scorable published criteria. These cover repetition, directional asymmetry and lexical distribution.
  - Its optimised keys reach more than 93.5% dictionary coverage in English, Sanskrit and Tamil, but bootstrap keys agree on only 9.3% of sign values.
  - Consequences for how we write claims:
    1. No headline should use entropy, Zipf, positional, directional or classifier statistics as evidence *for* language, or *for* code.
    2. Any reported dictionary-coverage figure needs a key-stability number (bootstrap agreement per sign) next to it, and a grouped held-out figure.
    3. Positional-structure findings (opener, closer, numeral slots) should be phrased as "organization" and not as "grammar" or "syntax".
  - This is already the project's practice (atlas 3.3), but SIGIL is now the citation for it. Our `lvc_corpora.py` already rebuilds SIGIL.
- **Tiwari 2026 (NLP4DH).** Structure only: directional asymmetry, positional rigidity, BiLSTM perplexity. No external test changes anything for us. Three internal problems mean its numbers should not be cited as support:
  1. Positional rigidity is defined as R = 1 − H_i/H_1, so it cannot exceed 1. Table 2 nevertheless reports values of 1.78 for the heraldic baseline.
  2. Every synthetic "violation" set gets *lower* perplexity than the real test set (1.10-2.42 vs 2.60), which is the opposite of what the text claims.
  3. The forward-vs-reversed KL of 16-21 bits is driven by unsmoothed zero cells, not by a directional rule.

  Directionality is already established by better evidence (atlas 7.6, structure).
- **Adelman 2026.**
  - Not benchable: there is no public sign table.
  - Abstract-level claims and what we already have on each:
    - 387 functional signs from 592 raw is close to Parpola's 386 and adds nothing testable.
    - "~100% coherence to the rarest sign" is a free-choice red flag (atlas 1.1).
    - *pīlu* ← *pal/pīl* is Mukhopadhyay 2021's loanword argument, already in the literature map.
  - To bench it we would need the sign-by-sign value table as a public file. If the author releases one, it can go straight into the `experiments/language` key bench.

## Not checked or limits
- The Kriger & Hunt PDFs and code were not read (Zenodo 403), so their exact null and their 179-seal subset are unknown. Their 91.2% "null" is below our real-data uniqueness, which suggests a null that does not preserve text lengths or counts repeats differently. That cannot be confirmed without the PDF.
- K1 is object level, following their wording. The distinct-text version is uninformative by construction.
- Field-symbol coding follows Mahadevan's descriptions ("Unicorn …"). ICIT unicorn coding was not used.
- K2's Ur III comparator turned out not to be a fair specificity test, because the legend order is name first. A genre-matched non-linguistic comparator is still missing (atlas 3.2).
- Tests run: 4 primary on U, the same 4 on S, 2 on UR, and 1 planted control.

## Hypotheses table

| Hypothesis | Verdict |
|---|---|
| C1 seal texts more unique than chance (registration numbers) | Refuted (reversed; real 88.2% vs nulls 97.5-99.2%) |
| C2 constrained edges / diverse middle | Supported as description; not diagnostic of code (SIGIL) |
| C3a numerals concentrate in penultimate slot | Refuted (p = 0.46 / 0.25) |
| C3b "2" dominates the counts | Refuted as a count claim; M99 connective artefact (27.7% without M99) |
| C4 near-duplicates never differ at edges | Refuted as stated (20/80 at edges); weaker form inconclusive (p = 0.06, power 0.67 at k = 25) |
| C5 duplicates are same-holder replacements | Contradicted by prior results (10b.4, 10b.9); not re-run |
| Adelman Dravidian key beats chance | Untestable (no public table) |

## Next experiments
- **K4 on ICIT unicorn seals from sites and objects absent in M77.** The unicorn-only p = 0.06 is the one thread with any life. ICIT doubles the sample. Pre-register it with the same rule.
- **Bench Adelman's key** if a public table ever appears.
