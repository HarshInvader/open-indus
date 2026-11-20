# Direction 3 (substrate words vs donor family): prior-art read

2026-11-20, agent `paper`, read delegated to Fable. No compute was run.

## Closest work
- **Savirinc/indus-script, rounds 39-40 (Oct 2026; public repo, pre-registered, not peer reviewed).** https://github.com/Savirinc/indus-script, plus the reports for rounds 39 and 40 under `indus-lab/`.
  - **Method:** 124 glossed Kuiper words, scored on sound plus meaning against Proto-Dravidian, Munda and Burushaski, with Finnish and Basque as controls.
  - **Gate:** 41 known Dravidian loans; Proto-Dravidian was ranked first in 0.99 of resamples.
  - **Result:** Proto-Dravidian leads (A = +0.064, P(rank 1) = 0.80, short of the 0.90 bar), so the verdict was "no family attributable".
- **Witzel 1999.** http://michaelwitzel.org/wp-content/uploads/2014/06/ejvs0501article.pdf. Descriptive layers only, with no test against chance.
- **Kuiper 1991.** Not opened (unverified); only secondary sources were read.
- **Southworth 2005.** https://ccat.sas.upenn.edu/~fsouth/LASAcontents.pdf (contents page only). Qualitative.
- **Arora et al. 2022.** https://aclanthology.org/2022.acl-long.99.pdf. Run no donor test.

## Novelty
- The headline test has been done.
- What remains is a circularity control: drop every word with a proposed Dravidian or Munda etymology, then rerun to break the 0.80 tie.

## Kill test (only if the coordinator reopens this)
- **Gate.**
  - Positives: known Dravidian loans, plus Iranian or Greek loans as a second set with a known answer.
  - Negatives: shape-matched inherited Vedic words.
  - Pass needs AUC ≥ 0.80, the right donor ranked first in ≥ 90% of resamples, and Finnish and Basque near zero.
- **Kill.** Either the gate fails, or on the cleaned list no family is ranked first in ≥ 90% of resamples and beats both controls in ≥ 95%.
- **Blockers.**
  - There is no local DEDR.
  - The Munda lexicon is small (712 forms vs 6,088 for Proto-Dravidian).
  - Para-Munda and Language X cannot be tested.

## Decision
Recommend drop. The best outcome is a replication of an existing public null, plus a control that will most likely also come out null.
