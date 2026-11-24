# Ur III seal legends: the true reading does not beat its shuffles (0 of 20)

Prereg `docs/prereg/ur3_legend_refute.md`, sealed 2026-11-24 as v3 (tag `ur3_legend_refute`). Code `run.py` was hashed before any run (tag `ur3_legend_refute_code`), and the hash was re-checked before each mode.

Run from the repo root under the Indus compute lock and `board/run.sh`: `run.py kill`, then `run.py full`. Outputs: `kill.json`, `kill.out`, `full.json`, `full.out`.

The first `kill` start stopped at abort A5, the memory guard (14.6% free). Nothing was computed and no output was written. It started again once memory was free; this is not a rerun.

No Indus key is scored. No outcome here supports or counts against any Indus key, and none licenses a rerun.

## Kill test (all passed)
- **K0, pipeline unchanged.** Linear B and Homer give 20 of 20, scrambled 0, equal to `lb_shape_ladder` R1 to 1e-9.
- **K1, tables.**
  - Counts match: 4,819 legends, 52,907 tokens, 39,192 sample lines from 3,475 texts.
  - Chunk excess medians: legends 0.255, administrative 0.165. No A2 failure.
- **K2, null calibration.** Wrong-key passes: 1 of 20, which is at the bar.
- **K3, planted known answer.**
  - The true reading on administrative text, cut to M77 lengths, passes 20 of 20, scrambled 0.
  - Null width W 0.040, signal 0.059, margin +0.019.
  - Partial keys rise strictly: 0.429, 0.446, 0.471, 0.501, 0.536.
  - So the bench has power on cuneiform at about Indus formula excess and this size.

## Legend cells

| cell | text | lexicon | LMIN | passes / 20 | scrambled | width W | signal | margin |
|---|---|---|---|---|---|---|---|---|
| **L1 (primary)** | legends, M77 chunks | OB spelled | 3 | **0** | 0 | 0.111 | 0.085 | −0.025 |
| L2 | legends, whole | OB spelled | 3 | 0 | 0 | 0.113 | 0.073 | −0.042 |
| L3 | legends, M77 chunks | Old Akkadian spelled | 3 | 12 | 0 | 0.087 | 0.086 | +0.004 |
| L4 | legends, M77 chunks | citation forms | 3 | 13 (not interpretable: scrambled 2) | 2 | 0.116 | 0.120 | +0.004 |
| L5 | legends, M77 chunks | OB spelled | 4 | 13 | 0 | 0.118 | 0.120 | +0.006 |

**Frozen reading, L1 clear fail with K3 passed:**
- On a formulaic, name-heavy seal corpus, a true reading does not beat its shuffles.
- Fit-refute has no stated power on seal legends at 1.6 × Indus excess.
- This does not decide Indus-level corpora.
- The cause is not separated: excess, names missing from the lexicon, and lexicon period are all candidates.

The key is an editor-resolved oracle with a same-convention lexicon, so this fail is strong for this corpus.

## Described, deciding nothing
- **The true reading scores well on the legends; the null is what moves.**
  - The legend signal (0.085) is larger than on the administrative kill text (0.059).
  - The null width is 2.8 times wider (0.111 against 0.040), so the margin turns negative.
  - That is the same direction as the note from `yj_ic_refute`'s saved results, where the real-text null was 2.1–2.7 times wider than the planted one.
  - This study does not separate why the null widens.
- **The report-only cells move towards the bar, not over it:**
  - the Old Akkadian lexicon reaches 12;
  - LMIN 4 reaches 13.
  - None passes, and they decide nothing.

## What this can and cannot say
- **It can say:** on Ur III seal legends, at about 4,500 scored tokens and 1.6 times Indus formula excess, the IC refute bench does not let even an editor's true reading beat its shuffles. On administrative text from the same period, at about Indus excess, the same bench and lexicon pass it 20 of 20.
- **It cannot say:**
  - whether a key would pass on a corpus at Indus excess made of seal legends;
  - why `yj_ic_refute` or `scott_ic_refute` lost power. The scripts, lexicons and rules differ;
  - anything about any Indus key.
- **Brief 9's hope that a pass would show the Yajnadevam and Scott failures came from their own rules does not hold.** The read seal corpus fails too.

## Limits (from the prereg)
- The key works at reading level: the editor resolved each sign's readings. The readings are normalised by CDLI.
- The lexicon is close to the text in language and convention, but 100–300 years later. ĝ and g are merged.
- The kill text holds names and shares tablets with many legends.
- Held-out sizes: about 4,520 tokens (legends) and 3,550 (administrative).

## Disclosures
- Implementer choices are marked `# PREREG-AMBIGUITY:` in `run.py`. The main ones:
  - K2 and K3 use the primary lexicon at LMIN 3;
  - free memory for A5 is free + inactive + speculative pages from `vm_stat`;
  - the lock check requires `board/run.sh`;
  - extraction follows the drafter's scratch code wherever the prereg is silent.
- K1 matched every sealed count, so these choices did not change the data.
- No rerun, no tuning, no fix tags.
