# Pre-registration: graffiti marks beside Tamil-Brahmi (board task #7, agent H6)

Written 2026-11-17, BEFORE any association between mark and word is tested.

## Data
Sherds carrying BOTH a Tamil-Brahmi (Tamiḻi) text and a graffiti mark, from Rajan & Sivanantham 2026,
*Inscribed Potsherds of Tamil Nadu: Graffiti and Tamiḻi*, Vol. II, Appendix I (1,570 Tamiḻi sherds),
taking the authors' own flags in the reading column: `#`, `Graffiti`, `குறியீடு` ("symbol").
Plus any further published sherds (Sri Lanka, Mahadevan 2003) added before the test is run.

## Gate (fixed)
Run the association test only if at least 30 sherds have a legible text AND a mark identified to a
graffiti sign number (Rajan & Sivanantham base sign 1-42 or variant). Otherwise report count + power only.

## Test, if the gate is passed
- Word classes: (a) ends in -ṉ/-ṇ (male name ending), (b) other. Secondary: words beginning the same
  name stem, titles in the corpus title list (none chosen yet; to be fixed before testing).
- Statistic: for each mark sign with >= 3 occurrences, Fisher exact test of mark vs word class (a);
  family-wise correction by Holm over all mark signs tested. Permutation null: shuffle mark labels
  across sherds within site (10,000 draws) for the max-statistic.
- Planted control: the power simulation in `experiments/tn_brahmi_graffiti/power.py`.
- Success: Holm-corrected p < 0.05 within site, and the same direction at a second site.
- Any positive is stated as an Early Historic (c. 500-100 BCE) association between a graffiti mark and
  Tamil words. It says nothing directly about Indus signs, which are 1,000+ years earlier.
