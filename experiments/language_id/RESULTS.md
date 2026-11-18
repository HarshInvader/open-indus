# Can 1-3 name anchors pick the language? (language_id, board #32)

Pre-registration: `docs/prereg/language_id.md`. It was hashed with `run.py` before the run. Raw data: `cells.jsonl` (4 true languages × 3 replicates). Summary: `results.json`.

## Conclusion first

**Pre-registered verdict: not feasible.** With only a relative of the true language among five candidates, 1-3 name anchors pick the right one in 50%, 58% and 67% of cells (chance is 20%). The bar was 80% at two anchors or fewer, so `docs/prereg/anchor_objects.md` gets no amendment.

**When the exact language is a candidate, anchors identify it.** One anchor picks the true language 83% of the time, and two or three anchors 100%.

| anchors m | exact language among 5 | only a relative among 5 |
|---|---|---|
| 1 | 0.83 | 0.50 |
| 2 | 1.00 | 0.58 |
| 3 | 1.00 | 0.67 |

## Exploratory (not pre-registered; 3 cells each, too few to test)

How often the relative was picked, out of 3, at m = 1, 2, 3:

| true language | relative used | m = 1 | m = 2 | m = 3 |
|---|---|---|---|---|
| Tamil | Malayalam | 2 | 3 | 3 |
| Latin | Italian | 3 | 1 | 3 |
| Sanskrit | Pali/Prakrit | 0 | 2 | 1 |
| Finnish | Estonian | 1 | 1 | 1 |

A very close relative (Malayalam for Tamil) behaves almost like the exact language. A more distant one (Estonian for Finnish) does not. For Indus, that would favour a hypothesis that can be written in a reconstructed proto-language, such as Proto-Dravidian, over a modern stand-in. This is a lead to pre-register, not a result.

## Caveats

- 12 cells, so power estimates are coarse (0.50 has a 95% CI of 0.21-0.79).
- The relative lexicons differ in size and genre from the K1 lexicons. In a real Indus test each candidate would be a reconstructed proto-lexicon, with its own noise.
- Search is limited to 60 sweeps × 2 restarts.
