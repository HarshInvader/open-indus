# Key hunt: public sign-to-value keys not yet on the claim bench (2026-11-24)

The aim was to find public sign-to-sound (or sign-to-word) keys published 2015-2026, keyed to a standard sign list, that the claim bench has not scored. The standard is the refute-only IC fit test, which needs full sign coverage at Indus length (`experiments/lb_shape_ladder/RESULTS.md`; `docs/NEGATIVE_ATLAS.md` 1.1).

Skipped because they are already benched or blocked: Yajnadevam (and its derivatives: Bhaty 2024/2025, the Savirinc 714-sign "atlas"), Pierson/glossa-lab (Zenodo 20414696 included), Fairservis, S. R. Rao, Kalyanaraman, Adelman, Kriger & Hunt, SIGIL.

**Method.** Web search (GitHub, Zenodo, OSF, Mendeley Data, Kaggle, Hugging Face, ResearchGate, Academia, Medium), then the GitHub API for file trees. No logins were used. The Zenodo search API answered 403 (traffic block), so it was not retried; Zenodo records were opened one at a time instead. ResearchGate and Medium answered 403; those items are marked (unverified). To count signs, the PDF text was extracted from the web-fetch tool's session cache (it saves fetched binaries automatically). Nothing was saved into this repo except this file.

**Coverage numbers** come from a rough regex parse of each PDF's sign table, scored against `data/m77_texts.jsonl` (13,372 M-tokens) or `data/icit_texts.jsonl` (18,044 W-tokens). They are estimates (within a few points), not a transcription.

## Ranked table (most benchable first)

| # | Claimant, year | URL opened | Licence | Sign list | Signs with a value | Est. token coverage | Values | Format | No login? | Benchable now? |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Jessica Scott (Dunn), *MahaSamVani: The Lexicon of the Indus Script (LIS)*, v3, 2026-07-24 (v1 2026-05-19) | https://zenodo.org/records/21522783 ; v1 https://zenodo.org/records/20277942 | CC BY-NC-ND 4.0 | M77 order, entries 1-417 (M342 = *Pa*, M59 = *Mi[na]*, M211 = *sru*) | ~350 of 417 (66 blank "-" or "?"; 15 carry "?") | ~95% of M77 tokens | Sanskrit acrophonic CV/CVC syllables and some words; some slashed alternatives (*Bha/Ba*, *Ca/ka*) | PDF, text extractable (614 kB) | yes | **Nearly.** Needs a ~1 h transcription to CSV. Not 100%: about 5% of tokens are blank. |
| 2 | S. K. Venkatesan (GitHub `Sukii`), *A Dravidian decipherment of Indus script* (key index), 2025, PDF rebuilt 2026-10-29 | https://github.com/Sukii/decipher-ivc ; PDF https://raw.githubusercontent.com/Sukii/decipher-ivc/main/ivc-script-decipherment.pdf | none stated (all rights reserved by default) | M77 numbers, with base-sign codes B1-B38 and agglutination formulas | ~290 of 417 (rough parse) | ~91% of M77 tokens | Old Tamil syllables or words with DEDR numbers; often several per sign (M97 = *-il, -da, -ta, -ul*) | PDF table (29 pp.), text extractable; no CSV | yes | Partly. Transcribable, but there are many choices per sign and coverage is not full. |
| 3 | Field-Cady (M. Carlson), `indus_dravidian_mapping_100.csv`, 2026-01 | https://github.com/field-cady/indus_valley_script_corpus (already in `sources/field-cady_indus_valley_script_corpus/`) | MIT | Wells/ICIT | 100 (a 25-sign file also exists) | ~82% of ICIT tokens | one Dravidian syllable per sign (W740 = *al*, W220 = *i*) | CSV | yes | Machine-readable today, but below full coverage. It is an optimal-transport fit to Dravidian surnames (`align_ot_100.py`), not an argued claim. Already scored by thewisecrab: "no support from sign order". |
| 4 | Logan Ross, *Reading the Indus Valley Script*, 2026-04-01 | https://zenodo.org/records/19362548 | CC BY-NC 4.0 | "Parpola IDs" from the mayig/CISI JSON (P324 = jar, P122 = fish; **not** Parpola 1994 numbers; a crosswalk is needed) | 182 claimed (Table 3: 30 structural; Table 11: 152) | 100% of his own 178-seal, 1,003-token subset only | mostly meanings ("seal of", "MEEN = star/lord"), produced by small LLMs via Chinese | PDF tables | yes | No. The values are semantic, the sign IDs are non-standard, and the coverage is of a small subset. |
| 5 | Mahaveer H. Muhammad (Abro), *The Alphabet of Sindhu Prakrit*, 2022-06-14 | https://data.mendeley.com/datasets/hmg4rnczvt/1 (one 119-page PDF) | CC BY 4.0 | M77 (grid figure "Classification of Signs According to Mahadevan's List") | claims "all 400+" signs; values are in prose and in NFM-font glyphs | not computed | alphabetic letters (vowels, consonants, aspirates) | PDF with private-use font glyphs, so hard to transcribe | yes | No, not without a long manual transcription through the NFM font map. A later ResearchGate version, *THE INDUS SCRIPT: Recognition as an alphabet* (https://www.researchgate.net/publication/396643766), returned 403 (unverified). |
| 6 | "Dominik (Researcher)", *Indus Script: Preliminary Lexical and Functional Decipherment* v1.0, 2025-10-12 | https://zenodo.org/records/17330061 (later versions 18294244 etc. drop the catalogue) | CC BY 4.0 (record notes a mismatch with the files) | own G001-G417; the record warns against mapping it to Wells | 337 catalogue entries; 25-row CSV | not computable (no crosswalk) | functional roles and meanings; "optional sound hypotheses" | DOCX + 25-row CSV | yes | No. There is no standard sign list and it is mostly not phonetic. (We already tested a separate Dominik claim: `experiments/dominik_w090`.) |
| 7 | Paras Duhan, *Deciphering the Indus Script Via Comparative Analysis*, 2026-10-05 | https://zenodo.org/records/23150464 | CC BY 4.0 | none (the key is in images: Pictures 3-4) | small (several seals read) | low | Tamil-Brahmi-like phonetic values | PDF/DOCX images | yes | No. |
| 8 | Bonta, *A Partial Decipherment of the Indus Valley Script*, 2nd ed. 2023 | https://www.academia.edu/105134798 (unverified: Academia login wall, not opened) | ? | ICIT and M numbers (per search snippet) | ~60 | partial | early Sanskrit | PDF behind login | no | No. It is partial and behind a login (Savirinc round 49 lists it as pending for the same reason). |
| 9 | Anurag K. N. Shukla, "Shukla model", 2025-26 | https://github.com/anu1441979-Anurag/Anurag-Kamal-Narayan-Shukla-Chhindwara-model-decoding-Indus-script | none | own IS_01... IDs | unknown (only IS_01-07 visible) | ? | Sanskrit words | notebook dict | yes | No. |
| 10 | Others seen and dropped | "Initial Decipherment of Indus script" (RG 339942891, 2020, 403, unverified); "520 Indus Script Symbols, Deciphered" (Medium, 403, unverified); Ganguly *A Study of the Indus Signs* (https://zenodo.org/records/812202; ©2012, so out of range, and the table is images); cyphersolver partial keys Parpola 27 / Kak 7 / Mahadevan 5 (https://github.com/dbourdeau/cyphersolver, `targets/indus/keys/`; too small, Savirinc "not testable") | | | | | | | | | |

## Notes per candidate

**1. Scott (Dunn) LIS.** This is the best find. The "Lexical List" runs 1-417 in Mahadevan order, and the paper says it grounds "all sign references in Mahadevan's authoritative concordance". The M-numbering is inferred from content: M342 = *Pa* (jar), M59 = *Mi[na]* (fish), M1 = *Nara* (man). Before scoring, check about 10 entries against the M77 plate.

The rules are stated, which makes the key fairly fixed:
- the value is the first syllable of the Sanskrit object word (CV or CVC);
- alternations b/v, r/l, d/t and s/ts are allowed;
- composite signs are read inside-out, top to bottom.

To bench it:
- transcribe one value per sign (taking the first alternative), and record the slash alternatives as the claimant's own freedom when computing choices per sign;
- about 5% of tokens are blank (`-` or `?`), so on the lb_shape_ladder the key sits between the 74% point (fails) and the 100% point (passes); a ~95% ladder point needs to be run, or the blanks need a declared treatment.

ND licence: scoring is fine, but ask before publishing the transcribed CSV. Supersedes the earlier "Dunn 2026, ~6 matches" entry in `experiments/literature/RESULTS.md`, which was her Linear Elamite paper.

**2. Venkatesan (Sukii/decipher-ivc).** This is a serious, M77-keyed Dravidian syllabary. There is a base-sign table (B1-B38 with M77 numbers), then "Syllabic development" rows: M77 sign, agglutination formula, syllable, DED number. It also reads whole M77 lines in `ivc-readings.pdf`.

- Many signs carry two to four values, so choices per sign will be high. The bench must count them.
- The parse here (~290 signs, ~91% of tokens) is rough. A proper transcription may find more signs in the "logo-synonyms" and "signs and affixes" sections.
- There is no licence, so use it for scoring only and do not redistribute.
- It is credited to joint work with M. V. Bhaskar (*Sasanam*, 2025, Tamil, print).

**3. Field-Cady PDR-100.** This is the only candidate that is machine-readable today, and it is already on disk. It is a computational alignment, not a published claim, and covers 82% of tokens. Under our standard a fit test cannot refute a key at 82% coverage, so benching it would add little.

**4. Ross.** An LLM-assisted dictionary that is mostly semantic. "P" IDs come from mayig's CISI JSON. It covers only a 178-seal subset.

**5. Abro.** Claims full M77 coverage as an alphabet, but the values sit in running text with NFM glyphs. It would only be worth a transcription if 1 and 2 are done.

**6-9.** Not benchable under the standard: non-standard numbering, mostly non-phonetic, partial, or behind a login.

## Bottom line

No candidate is benchable as-is at full coverage. Two near-full, M77-keyed phonetic keys exist and are openly downloadable:
- Scott (Dunn) LIS: ~95% of tokens.
- Venkatesan: ~91% of tokens, with many values per sign.

Each needs a transcription from its PDF to CSV, and a declared rule for blanks and for alternative values, before an IC run.
