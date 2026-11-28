# Pre-registration: S3, re-implement the ticked-fish finding from its description alone

Contributor: m0x1n. Written 2026-11-28, before any count of fish signs was made.

## What I have and have not read

I have read the finding as stated in README.md (#3), the rules of evidence in docs/AGENT_BRIEF.md and CONTRIBUTING.md, the docstrings of corpus/build.py and corpus/load.py, and the record formats of data/*.jsonl. I have **not** opened `experiments/audit_followups/`, `experiments/redteam_tick_complete/`, `experiments/novel_methods/` or any other code or results file for this finding. While doing S6 I saw that `experiments/ledger/v2_reruns.py` lists 12 plain fish signs; I do not use that list. I also saw the W-to-M bridge entries for the ten fish signs (below), and nothing else.

## The claim under test (README #3, as I read it)

Signs M60, M66, M68, M71 and M73 (fish with corner ticks) take the closing slot of a text more often than the plain fish M59, M65, M67, M70 and M72.

Reported numbers I will set mine against:
(a) complete single-line held-out texts: ticked fish final in 9 of 16, plain fish 2%, p = 0.006;
(b) "clean held-out": 11 of 19 final, plain 7%, p = 0.004;
(c) ICIT native: 40 of 73 final, 26% expected, p = 1e-7.

## Definitions, fixed now

- **Texts.** M77 object-side texts (`m77_texts()`), made distinct with `distinct()`, split with `dev_heldout(version=2)`. Texts from `site == "West Asian finds"` are dropped.
- **Clean text.** `complete` is true, `n_lines == 1`, and no `#` or `|` in `seq`. So there is no break and no line end inside the text, and "final" cannot be an artefact of damage.
- **Final.** A fish token is final if it is the last sign of the text in reading order (`seq[-1]`).
- **Tokens.** Every occurrence of a fish sign in a clean text counts. A text with two ticked fish contributes two tokens. I also report the count of texts.
- **Ticked** T = {M60, M66, M68, M71, M73}. **Plain** P = {M59, M65, M67, M70, M72}.

## Tests

**T1 (primary, held-out).** In clean held-out texts, ticked final rate vs plain final rate. One-sided Fisher exact test (ticked greater). Pass: p < 0.05.

**T2 (length-matched null, held-out).** For each ticked token in a clean held-out text of length L, the chance of being final under random placement is 1/L. The statistic is the observed number of final ticked tokens. The null distribution is the Poisson-binomial with those 1/L, computed exactly. Pass: p < 0.05. One-sign texts are excluded from T2, because there "final" is forced.

**T3 (within-text shuffle null, held-out).** Shuffle the signs within each clean held-out text, 100,000 times, with seeded NumPy streams. The statistic is the difference in final rate, ticked minus plain. One-sided p = (1 + #null ≥ obs) / (1 + N). Pass: p < 0.05.

**T4 (dev, descriptive).** T1 on clean dev texts, to set beside held-out.

**T5 (ICIT, outside replication).** ICIT inscriptions, made distinct, from regions other than Persian Gulf, Mesopotamia, Iranian Plateau, Central Asia and Other. Clean means `complete` is true and the text is one segment with no `|` or `#`. The fish are mapped with `sources/shaunmortal_indus/data/bridge_WM.json`. Ticked: W226 (M60), W236 (M66), W241 (M68), W232 (M71); M73 has no W number in the bridge. Plain: W220 (M59), W235 (M65), W240 (M67), W231 (M70), W233 (M72). Statistic: as in T2 (final count vs the sum of 1/L), plus the Fisher comparison with plain. **T5b** repeats T5 on sites that are not in M77 at all: ICIT sites other than Mohenjo-daro, Harappa, Lothal, Kalibangan and Chanhu-daro, in any spelling.

## Planted control

On the clean held-out texts I keep every real text and fish position. I relabel fish tokens at random into a "ticked" class of the same size as the real ticked count:

- (i) relabel uniformly among all fish tokens (no effect), 2,000 times. The false-positive rate of T1 at α = 0.05 should be at most about 5%;
- (ii) relabel with final tokens over-weighted so that the expected planted final rate is 50%, 2,000 times. Report the power of T1 and T3.

If (i) exceeds 10%, or (ii) is below 50%, I will say the test is unreliable at this sample size and give the results only as descriptive.

## Multiple tests

T1 to T3 and T5 are four tests of one claim (T4 and T5b are descriptive). I report Holm-adjusted p over T1, T2, T3 and T5. The verdict follows T1 and T2 together, after adjustment.

## What would prove the finding wrong, and what I will report

The finding is refuted for held-out texts if T1 and T2 both fail. It is not replicated if my counts differ from (a) or (b) and I cannot explain the difference by a definition. Every count is reported next to the reported numbers, and every difference is explained or marked unexplained. I will report it whichever way it goes.
