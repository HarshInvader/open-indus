# Pre-registration: graphic modifier paradigm (experiments/modifiers)

Written 2026-11-15, after dev analysis only. Held-out v2 and ICIT have not been touched by any statistic in this area. Frozen inputs, hashed in HASHES.txt:
- `experiments/modifiers/decomp.csv` (= `decomp_frozen.csv`): blind base+modifier table for Mahadevan signs, made from the drawings only, before any distributional number was computed (hash b0c84964...).
- `experiments/modifiers/w_decomp.csv`: the same modifier categories located in Wells numbering from font renders only, before any statistic.
- `experiments/modifiers/common.py`, `experiments/modifiers/m6_confirm.py`: the test code. Run once: `.venv/bin/python experiments/modifiers/m6_confirm.py`.

Contamination note: before decomposing, the analyst had read README finding #3 (ticked fish move to the closing slot) and the novel_methods exp3 family list (enclosure, roof, jar strokes). The decomposition is blind to new distributional statistics, not to these published results.

## Unit and statistic
Distinct texts with no `#` break, `|` removed, length >= 2. For each modifier class: pairs (derived, base) with confidence high or medium and >= 1 token of each sign in the set; >= 3 distinct bases are needed for a test, otherwise the class is reported as "untestable" together with its power.
Statistic T: Mantel-Haenszel z (derived vs base, stratified by base) for a binary token feature, taken at its leave-one-base-out minimum (0 if dropping any single base flips the sign). Null: 2,000 fake modifier classes with the same structure, with bases and derived forms replaced by random signs of matched token frequency (0.5-2x). On dev this test gave 5-7% false positives at p<0.05 on random pairings (the negative control) and recovered ticks (the positive control, p=0.001).
Features: final (text-final share), init (text-initial share), seal (share on seals/sealings).

## Confirmatory predictions (one-sided, alpha 0.05 each, in each confirmation set)
- C1, positive control: TICKS4 (four corner ticks, all bases) raises the final share. Dev: T=+9.8, 8 bases up and 3 down, p=0.001.
- C2: TICKS4 on NON-fish bases raises the final share (dev: M250<-M249, M388<-M387, M404<-M403 and others; T=+3.6, p=0.006). This would show that ticks are a general modifier, not a fish-specific convention.
- C3: CANOPY (flat bar with drop ends over a base) raises the final share. This is weak on dev (T=+1.9, p=0.04, q not significant), so a failure is the expected outcome.
- C4: inserted strokes in a container sign (jar or cup: M343-5<-M342, M329/M330/M336<-M328, M335<-M333) lower the final share. Dev: T=-7.3, p=0.013, mostly the jar. This one is already known in part ("jar + strokes is not jar").

## Paradigm prediction (two-sided, BH within each set)
Every other modifier class with >= 3 testable bases (BRACKET, COMB, DOUBLE, FRAME, HATCH, INSERT overall, LEFTPOST, OUTLINE, PAIRBARS, PAIRTICKS4, ROOF, THROUGH, INNERCHEVRON, HAT, RAYS4) shows no consistent shift in final, init or seal share (q >= 0.1). Dev: 0 of 36 such tests passed BH.

## Confirmation sets
1. M77 held-out v2 (`dev_heldout(version=2)`), the primary set.
2. ICIT, native Wells codes (`w_decomp.csv`), all sites. This is an independent transcription and sign list, but mostly the same objects as M77 (dev included), so it replicates across sign lists, not across objects.
3. ICIT sites absent from M77: genuinely new objects, expected to be badly underpowered.

## Decision
- The paradigm claim ("several modifiers form a derivational/inflectional system") needs at least two modifier classes other than ticks to be confirmed in set 1 or set 2, with the same direction in the other set. Otherwise: "ticks are the only demonstrated functional modifier".
- C2 confirmed in sets 1 and 2 means ticks are a general "closing-slot" modifier across base families.
- Power: report the power of each test to detect +0.2 and +0.5 shifts in final share at the observed token counts.
- If held-out has fewer than 3 testable bases for a prediction, the verdict is "untestable", and that is reported as such.
