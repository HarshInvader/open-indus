# Frozen predictions: all open leads, for future finds (2026-11-15)

Frozen by sha256 in `docs/prereg/HASHES.txt` (tag `leads_predictions`), together with the scorer `experiments/new_finds/score_leads.py` and the old-data baselines `experiments/roof_context/lead_baselines.json` (`r2_lead_baselines.py`). Do not edit; append a new file instead.

## Scope and rules (same as `2026-11-14_new_finds_predictions.md`)
- Test set: Indus inscriptions published after ICIT/M77 coverage, checked against both corpora and excluded if already present. Distinct texts. Foreign round seals excluded.
- Transcription into Mahadevan numbers in `experiments/new_finds/new_texts.csv` (`seq_M`, with `|` for a line break and `?` for an uncertain sign), sign by sign, before scoring. Primary set = `scored == yes`; sensitivity set = every readable new text. Both are reported.
- Every prediction is scored separately: PASS, FAIL, "neither" (between the bars), or INCONCLUSIVE (below minimum n). No threshold may change after hashing. Run: `.venv/bin/python experiments/new_finds/score_leads.py`.
- Transcriber bias: whoever transcribes knows these predictions. The rule is to transcribe from the publication's own sign list where there is one, and to rerun on high-confidence signs only.
- Overlap with earlier frozen files: L3 restates P3 (2026-11-14) and L5 restates PK1-home (toponyms). The earlier entries stay authoritative; L3 and L5 add a higher minimum n (L3) and a position test (L5b).

## Status of each lead when frozen

| id | lead | old-data evidence | status |
|---|---|---|---|
| L1 | a roof over a sign makes it more often text-initial | modifiers: held-out 5 up / 0 down (p=0.0065), ICIT 6/0 (p=0.04), dev 5/4; roof_context C1 on all data: M77 p=0.07, ICIT p=0.036. Pooled M77: roofed 69/213 = 0.32 initial vs bases 84/750 = 0.11. Mostly roof fish M65 | lead; found on these data, so only new finds can confirm |
| L2 | lens/oval M373 (ICIT W790) on bangles | self_label: 6/41 ICIT bangle texts vs 0.45 expected (q=0.008); Harappa 2/6. Other ICIT 1-3 sign texts: 16/1,775 = 0.009 | single lead, 7 objects |
| L3 | ticked fish close the text | README #3; modifiers ticks confirmed held-out and ICIT. M77: 32/56 = 0.57 final vs plain fish 58/909 = 0.06 | established |
| L4 | tall-2 + fish M59 is a fixed formula | numerals before M59 in M77: tall-2 65/110 = 0.59 (next: short-3 16, short-6 12). redteam_pnl: held-out 15/16 | survives red team |
| L5 | M93 (slanted tall strokes) is a Chanhu-daro end mark | toponyms: M77 10/10 Chanhu-daro, ICIT 8/9; M77 line-final or alone 10/11 | local convention lead |
| L6 | numeral + head number-name formulas keep their numeral value | redteam_pnl: held-out 29/40 vs 0.325 expected; ICIT new sites 15/20 (p=1.6e-4). Heads frozen below | survives, weakened (half is M59) |
| L7 | seals with no animal are smaller | rank_ladder / redteam_rank: -31% (n=49); metric sites -17% (p=0.06). ICIT square seals: median 21.6 mm (n=51) vs 26.7 mm (n=1,235), ratio 0.81 | survives, weakened |

## W790 checked on CISI photographs (for L2)

In the Wells font, W790 is a single pointed lens. W850 is a diamond and W840 is two interlocking lenses (= M403). The Mahadevan-Wells bridge lumps W790 with M261 (diamond), M373 (lens) and M374 (small oval). On the CISI vol. 2 plates (pdf pages 277, 281 and 282, book pp. 242, 246, 247):
- M-1645: one small horizontal lens or oval. This is M373 or M374; at ~100 ppi the two cannot be told apart.
- M-1644: two signs, interlocking lenses (W840 = M403) and a plain oval (W790).
- M-1646: a clear diamond, which ICIT codes as W850. So ICIT does separate the diamond, and the bangle W790 tokens are not M261.
- M-1630 and M-1631: an oval-like curve at the reading end, but too faint to confirm.
- H-1010 and H-2578 are in CISI vol. 3, which we do not have.

**Conclusion:** the bangle sign is the lens/oval, M373 or M374, not the diamond. L2 therefore counts M373 and M374 and excludes M261. Interlocking lenses M403 are also on bangles (ICIT 5/41 vs 25/1,775 other short texts). That was seen only now, post hoc, so it is frozen as exploratory L2b. The oval family on stoneware bangles may be one workshop habit.

## Predictions

Units: complete texts = new texts with 2 or more readable signs. Numerals use the shaunmortal stroke table: tall M86-M96; short M97-M122 without M99, M100, M101 and M113.

| id | prediction | pass | fail | min n |
|---|---|---|---|---|
| L1 | Roofed forms {M65, M66, M92, M138, M159, M163, M334, M203, M196, M14} stand text-initial more often than their bases {M59, M60, M89, M137, M158, M162, M333, M202, M195, M12} | roofed initial share >= base share + 0.10 AND Fisher one-sided p < 0.05 | roofed share <= base share | 8 roofed AND 8 base tokens |
| L2 | New inscribed bangles carry the lens/oval M373 or M374 | share of bangle texts with M373/M374 >= 0.08 AND binomial vs 0.01 p < 0.05 | share < 0.03 with n >= 15 | 10 bangle texts |
| L2b | (exploratory) M403 on bangles | reported only | - | - |
| L3 | Ticked fish {M60, M66, M68, M71, M73} are text-final | ticked final share >= 0.50 AND > plain-fish final share | ticked share <= plain share | 5 ticked tokens |
| L4 | A numeral directly before M59 is tall-2 (M87) | share >= 0.40 | share < 0.20 | 5 numeral+M59 tokens |
| L5 | Texts with M93 come from Chanhu-daro | >= 50% Chanhu-daro | < 20% | 3 texts |
| L5b | M93 is line-final or alone on its line | share >= 0.70 | share < 0.40 | 3 tokens |
| L6 | Numeral + head pairs keep the frozen value: M211 tall 3; M59, M60, M342, M284 tall 2; M194, M197 short 7; M15, M190, M403 short 3; M25 short 1 (M287 dropped, it failed held-out). Only same-system numerals count | kept share >= 0.60 AND binomial vs 0.325 p < 0.05 | kept share <= 0.40 | 8 pairs |
| L6b | Same, without M59 and M60 | kept share >= 0.50 | <= 0.33 | 6 pairs |
| L7 | Square or round stamp seals with no field animal are smaller than animal seals (larger face dimension, mm; needs `width_mm` / `height_mm` columns) | median ratio <= 0.90 AND Mann-Whitney one-sided p < 0.10 | ratio >= 1.0 | 4 no-animal AND 8 animal seals |

## What would change the verdicts
- L1 PASS would promote "roof = opener variant" to a confirmed slot effect. roof_context found no context link (sealings, citadels), so even a pass would not support "house of X". L1 FAIL closes the roof lead.
- L2 FAIL with n >= 15 closes the bangle lead. A PASS at a site other than Mohenjo-daro or Harappa would argue against a single workshop mark.
- L4 or L6 FAIL would mean the number-name formulas belong to Mohenjo-daro and Harappa conventions, not to the script as a whole.
- L5 off Chanhu-daro on a sealing should be read together with PK1-travel.
- L7 FAIL on independently measured seals would make the old result look like an artefact of the 1930s measurements.
