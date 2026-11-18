# How many name anchors would a reading need? (name_anchors)

Pre-registration: `docs/prereg/name_anchors.md`. It was hashed in `docs/prereg/HASHES.txt` with `run.py` before the full run. Code: `run.py`. Raw cells: `cells.jsonl` (15 cells = 5 languages × 3 replicates). Summary: `results.json`.

## Conclusion first

**Anchors work as a test only if the language is guessed right.**

Suppose a seal ties a readable name to an Indus-sign text. Its values fixed in a planted script of Indus size (10k tokens of short name texts, 20% word signs). We then asked whether the correct name-to-text match beats the same names attached to 19 wrong texts on held-out texts (p = 0.05):

- **True language's word list:** one name pair already passes 87% of the time. Two pass 93%, three or more 100%. Pre-registered m* = **1**.
- **True language's sound patterns only (no word list):** m* = **2**. Power is 0.80 at two pairs and 1.00 at five.
- **Wrong language, the realistic Indus case:** power stays at **0.27-0.40 for 1 to 10 pairs** and never reaches 0.8. m* = **none**. The correct match's median rank is 2-5 of 20.

Anchors also do not unlock the rest of the script under a wrong language. Accuracy on the other syllable signs stays at 0.08-0.11, against 0.05 with no anchors. Under the right word list it rises from 0.22 to 0.53 with one pair and 0.77 with ten.

## Table (15 cells per row)

| name pairs m | signs fixed | tokens covered | power: right word list | power: right sound patterns | power: wrong language | other-sign accuracy (right list / wrong) |
|---|---|---|---|---|---|---|
| 0 | 0 | 0 | | | | 0.22 / 0.05 |
| 1 | 4.3 | 11% | 0.87 | 0.53 | 0.27 | 0.53 / 0.08 |
| 2 | 8.5 | 23% | 0.93 | 0.80 | 0.27 | 0.67 / 0.08 |
| 3 | 10.4 | 29% | 1.00 | 0.93 | 0.40 | 0.67 / 0.08 |
| 5 | 16.9 | 39% | 1.00 | 1.00 | 0.33 | 0.72 / 0.11 |
| 10 | 26.9 | 59% | 1.00 | 1.00 | 0.40 | 0.77 / 0.09 |

## What it means for the project

- **Under the frozen rule in `docs/prereg/anchor_objects.md` (section 4), an anchor-grade object is reported as "anchor recorded, not yet testable".** The rule measures m* under the wrong-language model, and that m* does not exist. That outcome is fixed now, before any reply.
- **The same simulation points to a sharper use of an anchor: as a test of language hypotheses.** With the right language, even one or two correctly matched names stand out clearly. With a wrong one, they do not.
- That suggests a follow-up, not yet pre-registered and not run: name candidate languages in advance (for example Proto-Dravidian, Indo-Aryan, Munda), fix an anchor's values, and ask under which language the correct match ranks first. That would turn a single bilingual name into evidence about the language.
  - It needs its own planted-language test first. Can it pick the true language among 4-5 candidates with 1-3 anchors? Note that the "wrong language" here was an unrelated one; a related language will sit in between.
- **For outreach:** the one request that could give an anchor-grade object is still the Owen / Messina tablets (seal impressions in the Meluhhan household at Irisagrig). It is worth pursuing. Even one such object would be enough to start testing language hypotheses, though not enough to claim sound values.

## Caveats

- Planted scripts are simplified. Syllable signs are CV, a word sign stands for a whole word, and the texts are name lists drawn from real languages.
- 15 cells per row: a power of 0.87 has a 95% CI of roughly 0.60-0.98.
- "Wrong language" pairs are fixed (san↔tam, sux→lat, lat→fin, fin→sux). With a Sanskrit word list, Tamil cells pass from m = 3 in some replicates, and san/tam share many loanwords and sounds. A related-language case was not designed in.
- Search is limited to 60 sweeps × 2 restarts. A better search would help the right-language cases more than the wrong ones.
