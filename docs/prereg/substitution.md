# Pre-registration: one-to-many substitution (X <-> YZ, Maya method)

Agent: substitution (Fable 5.2 plan item 5). Written 2026-11-14, after the dev analyses, the planted-answer power runs and the Ur III real-script check. No held-out text and no ICIT new-site text has been used in a test yet.
Code: `experiments/substitution/` (`run_heldout.py` implements exactly the tests below).

## Definitions (fixed on dev)
- Unit: distinct M77 texts, `dev_heldout(version=2)`, no `#`, `|` removed (dev 1,675; held-out 564).
- Event: text A = ...L X R..., text B = ...L Y R..., Y = 2-3 signs, X not in Y; flanks 2+1 or 1+2 tokens (text edges count), >= 2 real signs among the 3 flank tokens (L tier). Whole-text frames (W tier) are a subset.
- Independent frames: events of one equation are merged when they share a text or the same 2+2 context.
- Null: permute Y among frame units within (slot I/M/F, length of Y); per-equation Poisson tail at the null mean; BH.
- SCE (system-consistent equation): q < 0.05 AND no sign of Y is X or a 1<->1 paradigm partner of X (fills the same exact 2+2 frame as X elsewhere).
- Detection rule D: number of SCEs > 95th percentile of synthetic p=0 corpora of the same size (26.1 at n=1,675).

## Dev results (already known)
- 55 equations at q<0.05, 11 SCEs, 3 shared spelling signs (M89, M336, M99). Synthetic corpora with NO alternation give 12.5 +/- 7.3 SCEs and 4.6 shared signs; so the dev count is at chance (rule D not met: 11 < 26.1).
- Within-text shuffled Indus gives 20 equations at q<0.05: the per-equation null is anti-conservative, which is why D is calibrated on planted corpora, not on q alone.
- The SCE "system" is the compound M336 M89 standing for several different fish signs (M59, M67, M249, M259): one spelling for many words, the opposite of a phonetic spelling.

## Operating characteristics (12 corpora per cell; q=0.5 chance per occurrence of the phonetic spelling)
| corpus | alternating logograms p (token share) | power of D | oracle power (>=3 planted SCEs sharing a sign) | P(n_SCE <= 11) |
|---|---|---|---|---|
| synthetic, n=1,675 | 0 | 0.08 (FPR) | 0 | 0.58 |
| | 0.1 (8%) | 0.17 | 0 | 0.33 |
| | 0.2 (19%) | 0.42 | 0.25 | 0.00 |
| | 0.3 (26%) | 0.75 | 0.33 | 0.08 |
| | 0.5 (39%) | 0.83 | 0.58 | 0.00 |
| | 1.0 (82%) | 1.00 | 0.83 | 0.00 |
| Indus dev + planted system | 0.1 (12%) | 0.58 | 1.00 | 0.00 |
| | 0.3 (29%) | 1.00 | 1.00 | 0.00 |
Real script: Ur III seal legends cut to 2,300 texts: 0 of ~450 significant equations are phonetic (5 samples); 1 phonetic equation (saga = sa6-ga) recurs at all.

## Confirmatory hypotheses
### H1 Dev SCEs replicate in new texts
- New texts: (a) M77 held-out; (b) ICIT texts from sites absent from M77 (Dholavira, Nausharo, Banawali, Rakhigarhi ...), translated W->M with the shaunmortal bridge, keeping only texts whose every sign maps to exactly one M sign.
- For each of the 11 dev SCEs: k_new = independent frames among events where at least one text is new (mined on dev + new). p from the same null applied to new-text units; BH over the 11.
- **Phonetic system supported** only if >= 3 SCEs replicate (q < 0.05) in (a) or (b) AND at least 2 of the replicated SCEs share a spelling sign with different Y strings AND the shared sign is not the M336 M89 compound. Otherwise: not supported.
- Prediction (written now): 0-2 replicate; any that replicate are fish <-> M336 M89 / formula paradigm alternations.

### H2 All 55 dev q<0.05 equations (secondary, descriptive)
Same replication count; BH over 55. Replications here are expected to be slot/paradigm alternations and are NOT evidence of phonetics by themselves.

## Verdict rules
- If H1 passes: phonetic substitution system supported (needs red team).
- If H1 fails: "no X <-> YZ phonetic system detected". With the operating characteristics above this excludes, at roughly 5-10% error, a Maya-like system in which >= 20% of word tokens (synthetic) or >= 12% (Indus-matched plant) are logograms with an alternative 2-3 sign spelling used half the time. Smaller or rarer alternation (<= 10% of logograms) cannot be excluded, so this does NOT close the phonetic route.

## Multiple testing
Exploratory dev: W tier 142 recurrent equations tested, L tier 831; 2 ICIT runs; 216 planted corpora; 6 Ur III/Linear B runs. Confirmatory: H1 (11 tests x 2 new sets, one decision), H2 (55 x 2, descriptive).
