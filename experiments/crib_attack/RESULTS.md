# Crib attack on planted data (board task #3, H3)

## Verdict: the crib attack cannot work at our sample size. Keys fitted to noise beat the true key at every n up to 120 texts.

I planted real Ur III personal names in a simulated syllabic script, at the level of noise we expect: 25% of texts carry no name, 0-2 frame logograms per text, and 20% of signs misread. Then I ran the frozen attack. At n = 20, 30, 60 and 120 texts:
- The best key found on the planted corpus does not score above keys fitted to shuffled texts. Power is 0.00, 0.40, 0.10 and 0.50; the gate needs 0.80.
- Under the main statistic, the **true** key itself scores below the 95th percentile of keys fitted to noise (S_true 38 vs 71 at n = 20; 258 vs 278 at n = 120). So no search, however good, could pick out the true key. There is no unicity point at n ≤ 120.
- Recovered sign values are wrong. Median precision is 2-4% and recall 2-4%, which is chance level for 76 syllable values.
- The search is not the bottleneck. In 100% of planted runs the search found a key scoring at least as high as the true key: it finds a better-fitting wrong key every time.

The foreign corpus holds about 20-30 texts (meluhha: 23-30 objects; typology: 12 Gulf residues). At that size this method, with a list of thousands of candidate names, would give a fit to noise, not a reading. Running it on the real texts (task #4) as specified would be uninformative. The redesign that could work is in the last section.

Pre-registration: `docs/prereg/crib_attack_planted.md`, hashed with the code before the grid ran (tag `crib_attack_planted`). After a server restart I added checkpointing to `run_planted.py`; its new hash is logged under tag `crib_attack_planted_checkpointing_only`, and the method is unchanged.

## Numbers (condition A_main: CV script, attacker list contains every true name)

10 planted, 10 wrong-language (Linear B names) and 20 shuffled corpora per n. S = matched signs summed over texts (one misread allowed in names of 3 or more signs). E = number of texts with an exact full-name match of 3 or more signs.

| n | null S q95 | planted S_best med | true-key S med | power (S) | wrong-language FPR (S) | null E q95 | true-key E med | power (E) | precision med | recall med |
|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 71.0 | 66.0 | 38.0 | 0.00 | 0.00 | 14.1 | 7.5 | 0.10 | 0.03 | 0.04 |
| 30 | 88.3 | 87.5 | 63.5 | 0.40 | 0.10 | 15.1 | 9.0 | 0.00 | 0.02 | 0.03 |
| 60 | 159.2 | 154.5 | 128.5 | 0.10 | 0.00 | 22.2 | 20.5 | 0.00 | 0.02 | 0.02 |
| 120 | 278.0 | 278.0 | 257.5 | 0.50 | 0.00 | 23.0 | 38.5 | 0.50 | 0.04 | 0.03 |

Search adequacy (S_best ≥ S_true): 1.00 at every n. Gate "works at n" (power ≥ 0.8, FPR ≤ 0.2, precision ≥ 0.5): **fails at every n**. Numbers: `results.json`; raw runs: `out/A_main.json`.

What the table shows:
- **Why it fails: list size.** The list has 6,718 spellings over 76 syllable values. With a free key, almost any 3-6-sign text contains a near-match. Shuffled texts reach 3.5 matched signs per text at n = 20, against 1.9 for the true key, whose 25% name-free texts and 20% misreadings cost it points.
- **The gap closes slowly.** The null's score per text falls from 3.55 to 2.32 between n = 20 and 120, while the true key stays at about 2.15. A rough extrapolation puts the S-unicity point at about 200-250 texts, several times every Indus text known from outside South Asia.
- **The exact-match statistic E reaches unicity first.** The true key's median E (38.5) beats the noise q95 (23.0) at n = 120, but not at n = 60 (20.5 vs 22.2). So between 60 and 120 texts a true key would show itself through exact full-name matches. The current search does not optimise E, so power at n = 120 is only 0.5.
- **Wrong-language false positives were low (0-0.10).** Linear B names do not fit an Ur III list better than shuffled texts do. That control behaved as intended, though it says little while power is this low.

## Not done or not checked

- **Secondary conditions are still running.** A_cov50 (attacker list covers 50% of name types) and B_main (cuneiform-style CV/VC/CVC script) are being resumed under checkpointing; results will appear in `out/B_main.json` and `out/A_cov50.json`. Neither can rescue the verdict: the primary condition is the most favourable case (the attacker's list contains every true name), so A_cov50 can only be weaker. B uses a 402-value inventory and therefore has fewer repeated signs, but also far fewer spellings (3,045). It could in principle differ, so it should be read when it lands.
- Not run: vowel-less (consonant-only) matching, homophonous signs (many signs to one value), and n = 45 and 90 (dropped for run time; this deviation was registered).
- Name lists other than Ur III. The real owners' names may also be Meluhhan; then no list contains them, and the attack is even weaker (see the meluhha folder: only 2 secure Meluhhan names exist).
- Only 10 planted runs per cell, so each power estimate has a 95% CI of about ±0.3.

## Hypotheses

| hypothesis | verdict |
|---|---|
| A crib attack against a large name list recovers a planted key at n ≤ 60 | refuted (power ≤ 0.4, precision ≤ 0.04) |
| The true key out-scores keys fitted to noise at n ≤ 120 (main score S) | refuted (S_true < null q95 at every n) |
| With exact matches (E), the true key is unique by n = 120 | supported for the true key (38.5 vs 23.0); not reached by the search (power 0.5) |

## What would make the crib attack feasible (handed to #4 and new tasks)

1. **A short, specific list.** Unicity scales with list size. A list of tens of names, each tied to a specific seal (for example names of people at the find site and in the period), cuts the fit to noise by about two orders of magnitude compared with 6,718 spellings. Board task #2 should deliver per-site shortlists, not one big list.
2. **Anchored, not free, keys.** Fix 2-3 values from an outside source and search only the rest; `decipherability` found anchors raise recovery from 0.17 to 0.47-0.68.
3. **Score with E (exact matches of 3 or more signs) and search on E,** with a planted check at the real n before the real run.
4. **More texts.** Under the current design, unicity needs about 120 texts (E) to 200+ (S).

A redesigned pre-registration for #4, ready to hash only once a short list and a planted re-check exist, is in `prereg_real_draft.md` (not hashed: the gate it depends on has not been met).
