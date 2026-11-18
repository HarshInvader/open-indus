# Pre-registration: can 1-3 name anchors pick the language? (language_id, board #32)

Written 2026-11-18 after name_anchors and before any code for this test existed. Planning simulation, no Indus claim.

## Question
name_anchors showed that correctly matched name anchors pass a held-out test under the right language and not under a wrong one.
Can that difference pick the right language out of several candidates named in advance? And can it do so when only a
RELATIVE of the true language is available? The relative case is the realistic one for Indus: Proto-Dravidian is
reachable only through its daughters.

## Design (reuses experiments/decipherability and experiments/name_anchors/run.py conventions, unchanged)
- True languages: san, tam, lat, fin (the four with a relative lexicon). Sumerian is excluded: it has no relative.
  Replicates 0-2, giving 12 cells. Planted corpus: `cells.planted(lang, "names", 10000, 0.2, rep)`, split 75/25 with seed = rep.
- Anchors: m in {1, 2, 3}. The names are drawn exactly as in name_anchors (seed 7*rep+m), with 19 wrong alignments each.
- Candidate language models (word lists), 5 per condition:
  - EXACT: the K1 lexicon of the true language plus the K1 lexicons of the other four of san, tam, sux, lat, fin.
  - RELATIVE: the K2 lexicon of the true language (Pali/Prakrit for san, Malayalam for tam, Italian for lat, Estonian for fin)
    plus the same four unrelated K1 lexicons. The true language itself is not a candidate.
- For each candidate c: fit dev with the correct anchors fixed and with each of the 19 wrong alignments fixed
  (`anneal`, 60 sweeps x 2 restarts), and score held-out. Statistic z_c = (correct - mean(wrong)) / sd(wrong).
- Pick = the candidate with the largest z_c.

## Thresholds (fixed now)
- Power(m, condition) = share of the 12 cells where the pick is the true language (EXACT) or its relative (RELATIVE).
  Chance is 0.2.
- "Feasible" = power >= 0.8 at m <= 2 in RELATIVE. If it is feasible, `docs/prereg/anchor_objects.md` gets an amendment, before
  any reply arrives, adding a language-ID test for anchor-grade objects. If it is not, no amendment is made.
- Also reported: the median rank of the right candidate, and how often its z clears 1.645.
