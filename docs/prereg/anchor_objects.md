# Pre-registration: what each requested object can and cannot give (anchor_objects)

Written 2026-11-17, after the outreach emails were sent and BEFORE any reply or image has arrived.
Purpose: fix, in advance, how images or data from the outreach are read, what counts as an anchor, and what is
concluded from each possible outcome, so nothing is decided after seeing the answer.

## 1. Reading gate (applies to every image received)
- Two readers who have not seen this file's hypotheses transcribe every Indus-like sign against Mahadevan 1977
  (M numbers) and Wells (W numbers), from the images alone, independently. A third person compares them.
- A sign counts as read only if both readers give the same M or W number. An object passes the gate if >= 80% of its
  signs are read. Below that it is recorded as "unreadable at this resolution" and nothing further is run.
- Readings are hashed into docs/prereg/HASHES.txt before any comparison with names or other texts.

## 2. What counts as an anchor
- Anchor-grade (A): Indus signs and a readable name (cuneiform or Linear Elamite) on the SAME seal face or the SAME
  impression, or a tablet that says "seal of PN" and carries an impression whose legend is in Indus signs.
- Candidate (B): a tablet naming a Meluhhan (na-na-sa3 / Na-na-za, sa6-ma-ar, or "dumu/lu2 me-luh-ha") that carries an
  Indus-sign impression without stating whose seal it is.
- None (C): anything else, including Indus-like signs with no readable name, or a name with no Indus signs.

## 3. Object by object: possible outcomes and fixed conclusions
| object | asked of | best possible grade | what follows |
|---|---|---|---|
| BM 120573 (Indus-type seal, cuneiform legend sak-ku-si / ka-lu-si) | British Museum | C | It carries no Indus signs, so it fixes no sign value. A firm reading adds one name to the Meluhhan crib list (experiments/onomasticon) and nothing else. |
| Sb 9382, Susa "text O" | Louvre | C, or B only if a readable Linear Elamite name stands next to an Indus sign group | Without a parallel text it fixes no values. If the Indus-like signs pass the gate, test only: are they in Indus order (grammar.md positional classes, rank among 1,000 shuffles, p < 0.05)? |
| CUSAS 40/2 1582 and Nisaba 15 0371 (Irisagrig Meluhhan household) | D. I. Owen / Messina | A or B | The only route here to a sound value. See section 4. |
| HARP database, Fuls corpus, CISI vol. 3 | Kenoyer, Fuls, publishers | none (no names) | Run the already-frozen tests unchanged: firing_stage, tablet_archives, magnitude, reg_findspot, new_finds predictions P1-P13, leads L1-L7, scene_text, line_breaks. |

## 4. If an anchor-grade (A) impression appears
- Record every alignment of the name's syllables to the signs (both reading directions; each sign syllabic or a
  word sign), hashed before scoring. Never pick one after looking at other texts.
- Success test (b) cannot be run on one name. The number of name-text pairs it needs is taken from
  experiments/name_anchors/results.json (m_star, fixed before any reply). With fewer pairs than m_star under the
  wrong-language model W, the result is reported as "anchor recorded, not yet testable", with no sign value claimed.
- With at least m_star pairs: fix their values, fit the rest under each candidate language, and score held-out Indus
  texts against the same names attached to 19 wrong texts of equal length (the name_anchors design). Pass = the true
  alignment ranks first (p = 0.05) under a language named in advance, then an independent red team.

## 5. What would change this plan
Only an object of a kind not listed here. It would get its own pre-registration before any analysis.
