# Licences and picture rights

{{NAME}} works to {{GOAL_LC}}, in the open. That means everything we may share is shared, and everything we may not share is rebuilt from its public source instead of being copied here.

> **Status: draft.** The licences below are proposals. Nothing here is legal advice. The open questions are listed in `PUBLISHING_CHECKLIST.md`, and none of them is settled until it is marked done there.

## In short

| What | Where | Proposed licence |
|---|---|---|
| Code | `*.py`, `*.sh`, `corpus/`, `scripts/`, `board/board.py`, `site/build.py`, `site/assets/site.js` | MIT |
| Writing | `README.md`, `docs/`, every `RESULTS.md`, the website text | CC BY 4.0 |
| Our own result data | `results.json` files, `docs/test_ledger.csv`, `docs/prereg/`, `experiments/old_registers/registers.csv` | CC BY 4.0 |
| Our own drawings | the logo files and `site/assets/seal-illustration.svg` | CC BY 4.0. The name and logo as a mark are not licensed for others to use as their own. |
| Indus texts (the corpus) | `data/`, built by `corpus/build.py` | **Not included.** Rebuild from the public sources. |
| Sign drawings | `data/sign_images/`; 11 of them inside `site/assets/glyphs.css` | **Unclear.** See below. |
| Seal photographs | `site/assets/img/`, `experiments/plate_corpus/crops/plate_*.png` | **Public domain in India; US status uncertain.** See below. |

## The Indus texts

The sign-by-sign texts come from two scholarly works.

- **Mahadevan 1977.** Iravatham Mahadevan, *The Indus Script: Texts, Concordance and Tables*, Archaeological Survey of India. It was made available online by the Roja Muthiah Research Library (indusscript.in). We read it through an export by paragorth (`Indus-`, MIT for that project's own code and tables). That export says the corpus itself is Mahadevan's work, not covered by its licence.
- **ICIT.** The Interactive Corpus of Indus Texts by Bryan Wells and Andreas Fuls. We read it through the field-cady export of yajnadevam/lipi, which is MIT for its own code. No terms for the data are stated.

**Neither source states terms that allow the data to be republished, so the corpus files are not in this repository.**

- `corpus/build.py` lists the sources and rebuilds `data/` from them byte for byte.
- Most of our results quote only short sign sequences, cited by catalogue number. About 18 result files list many whole texts. The largest is `experiments/functional_reading/readings.csv`, which covers every text. Whether those files can be published, or must be rebuilt locally like `data/`, is an open question in `PUBLISHING_CHECKLIST.md`.
- If the holders of either corpus are willing to grant open terms, we will add the files.

## Sign drawings

`data/sign_images/` holds Mahadevan's 1977 drawing of each sign, as served by indusscript.in. The terms are not stated, so the folder is not in this repository.

The website shows 11 of these drawings: M59, M60, M65, M66, M67, M99, M109, M176, M267, M342 and M391. They are embedded in `site/assets/glyphs.css`, small and as outlines, to illustrate findings about those signs.

**Whether that use is allowed is an open question.** If it is not, the 11 drawings can be redrawn from scratch.

## Seal photographs

Every photograph on the website is a crop from an excavation report published by or for the Archaeological Survey of India between 1931 and 1940:

- Marshall, *Mohenjo-daro and the Indus Civilization*, 1931;
- Mackay, *Further Excavations at Mohenjo-daro*, 1938;
- Vats, *Excavations at Harappa*, 1940.

Each caption names the report and the seal number. The images are shown in greyscale and are never enlarged beyond the resolution of the scan.

- **India.** Works by the government, or published under its authority, enter the public domain 60 years after publication. By that rule these reports are in the public domain in India.
- **United States.** Status uncertain. A foreign work that was still protected in its home country on 1 January 1996 can have had its US copyright restored.
  - The 1938 and 1940 reports were still within the Indian 60-year term on that date. Their US protection could therefore last 95 years from publication, to the end of 2033 and 2035.
  - The 1931 report was published in London, and its UK status has not been checked. Whatever that status, US copyright for any work published in 1931 ends on 1 January 2027.
  - GitHub and most hosting are in the US, so this needs an answer before the site is published.

**Not used anywhere:** pictures from the *Corpus of Indus Seals and Inscriptions* (CISI, 1987 onward), which is in copyright. Catalogue numbers from CISI appear in our data as references only.

## Software we depend on

`requirements.txt` includes PyMuPDF, which is licensed under the AGPL-3.0. A few scripts in `experiments/new_finds/tools/` import it to read PDF pages. Our code stays MIT. Anyone who redistributes those scripts together with PyMuPDF must also meet the AGPL terms.

## Other people's work in this repository

- **Repositories we read.** The cloned repositories in `sources/` are not part of this repository. We link to them and credit them in `CITATION.cff`.
- **Other scripts' corpora.** Some experiments hold transcriptions of cuneiform and Proto-Elamite texts, for example `experiments/protocuneiform/pe_lines.json` and `experiments/sealing_hunt/meluhha_atf.txt`. Each names its source. Their terms are to be checked before publishing.
- **Word lists.** Some experiments use dictionaries or word lists made by others, for example Tamil lemma lists and Sanskrit or Dravidian vocabularies. Each is cited in its experiment's `RESULTS.md`. Before publishing, any list whose terms do not allow redistribution is removed from the public copy. The script that uses it says where to get it.

## Contributions

By opening a pull request you agree that your contribution is released under the licence of the files it adds to: MIT for code, CC BY 4.0 for writing and data. Do not add material you do not have the right to share.
