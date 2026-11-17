# New finds as an out-of-sample test

Written after the fact, from `results.json`, `results_leads.json` and the RESEARCH_STATE log (cycles 4 and 5). It was added during the v1.0 reproducibility audit because this folder had no RESULTS.md.

## Findings first

- **Verdict: untestable.** About 190 inscribed objects published after 2010 were checked. Almost all are already in ICIT, which absorbed publications up to about 2018, including the 2015 Dholavira report.
- Only 12 objects are truly new, and only 2 of them have a readable text: the Binjor terracotta seal M1 M342 M1 and the Khirsara graffito M137. None of the 13 frozen predictions (P1-P13) or 7 frozen leads (L1-L7) has enough texts to score.
- **Correction to the original brief:** only 38% of complete M77 seal texts end in the jar sign M342. The 80% figure refers to jar tokens that sit in line-final position.

## Frozen and ready

- The predictions are hash-frozen in `docs/prereg/HASHES.txt` and scored by `score.py`.
- The leads are in `docs/prereg/2026-11-15_leads_predictions.md` and scored by `score_leads.py`.
- To score new data, add rows to `new_texts.csv` and run `.venv/bin/python -I experiments/new_finds/score.py` and `score_leads.py`.

## What would unlock it

- Fuls' Corpus of Indus Inscriptions (2022-23).
- CISI 3.2 and 3.3.
- Indian Archaeology: A Review (IAR) 2012 onward.
- The 2021-24 Binjor and Rakhigarhi reports.
- harappa.com, through a normal browser.
