# Pre-registration: Dominik 2026 claim "W090 follows W740 but never W520" (board task #19, agent H4)

Written 2026-11-17 before any W090/W520/W740 bigram count was computed.

## Claim (Zenodo 23307028)
Excluding W033-conditioned W520 occurrences, W090 never immediately follows W520 (0/136), but follows W740 in 69/994. Order convention, denominators and corpus are not stated.
Bridge (shaunmortal `bridge_WM.json`): W090 = M1, W740 = M342 (jar), W520 = M211 (arrow), W033 = M89, W220 = M59.

## Units and order
- **Units.** Distinct sequences (`distinct()`), break-free runs.
- **"W520 conditioned by W033".** A W520 token immediately adjacent (either side) to W033. These are excluded, as the claim does.
- **Order.** "Follows" is ambiguous. We compute both reading order (our corpus order) and ICIT listing order (reversed). The PRIMARY order is the one whose ICIT denominators (W740 and W520 tokens that have a next sign) are jointly closer, in log ratio, to 994 and 136. This is decided from denominators only. The other order is reported as secondary.

## Tests
- **T1 replication (ICIT, primary order).** k_520/n_520 and k_740/n_740. Fisher exact one-sided (fewer W090 after W520). Family check: excluding all sequences containing W220.
- **T2 independent data.**
  - (a) M77 held-out split v2 (family-level split), via the bridge.
  - (b) ICIT sites absent or rare in M77 (every site except Mohenjo-daro, Harappa, Lothal, Kalibangan, Chanhudaro).
  - The claim is "supported" on a set if P(W090 | W520) < P(W090 | W740) with one-sided Fisher p < 0.05.
  - If n_520 is too small to reach p < 0.05 even at k = 0, the claim is "untestable" on that set. Power figure: (1 - p_740)^n_520.
- **T3 look-elsewhere check (ICIT, primary order).** Consider every ordered triple (X, Y, C) where:
  - X has >= 500 tokens with a next sign;
  - Y has 100-200 tokens with a next sign;
  - C follows X at rate >= 5%;
  - C follows Y 0 times.

  Count how many such zero-cells exist. Compare with a null that permutes the next-sign labels across all bigram tokens (preserving unigram follower frequencies), 1,000 permutations, and with a within-text sign-order shuffle (preserving text composition). Report the rank of the claimed contrast's Fisher p among all (X, Y, C) triples meeting the X/Y size bounds and the 5% rate.
- **T4 mechanism note (descriptive).** Where W520 and W740 sit in the text (final share), since a sign that is usually final has few followers of any kind.

## Decision
- Supported overall if T1 replicates (p < 0.01) AND at least one of T2a/T2b is supported.
- Zero-cells like this one being common under T3's nulls is reported as a caveat: the claim is sharp but not unusual.
