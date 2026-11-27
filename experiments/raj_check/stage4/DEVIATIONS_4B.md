# Stage 4b: departures from the plan, logged as they happened (before any 4b contest run)

1. **Checker samples drawn per language.** The plan says 50 names and 50 words per language, seed 20261127. `build_4b.py sample` first drew all four languages from one random stream; before anything was sampled it was changed to one stream per language (seed string `20261127-<lang>`), so a language can be checked as soon as its list is ready. Sample sizes unchanged.

2. **Malayalam list is short.** The compiler stopped at 631 confident names (asked for 1,260–1,540) rather than pad the list. The plan's rule applies: all names are used, and the count is reported.

3. **Loans: one rule for every language.** The labeler prompt says `sanskrit_loan` is judged "by origin, not meaning", yet also opens with "choose by the meaning". The Tamil labeler applied origin first (115 of 961 parts marked loans); the Malayalam and Telugu labelers applied meaning first (6 of 602 and 37 of 1,263). Since loans are dropped, mixed rules would penalise one language against the others. Decision, taken before any 4b run: the **main run uses origin first for all languages** (the prompt's literal rule and the plan's "loans are dropped"); the Malayalam and Telugu labelers were rerun with the same prompt plus one clarifying sentence (`*_labeler_prompt_v2.txt`); Kannada gets the v2 prompt from the start. Their first labels are kept as `labels_<lang>_meaningfirst.jsonl`, and one extra Tamil labeler produced meaning-first labels (`tamil_labeler_prompt_meaningfirst.txt`), for a **sensitivity run** (tag `<lang>4bm`), reported alongside but not used for the plan's readings.

4. **First Malayalam labeler launch was empty.** The first launch received a placeholder instead of the prompt and did nothing (no files read or written); it was relaunched with the prompt.

5. **Tamil meaning-first labeler (sensitivity run only)** labelled 327 parts glossed only "name" as personal_name with one script line instead of one by one (the same label it chose after reading the list), and used its own knowledge to give 47 other "name" parts place, clan or god labels. Reported as is; it affects only the sensitivity run.

6. **Telugu checker** passed the list (words 4 of 50 wrong, names 0 of 50), but judged 49 of the 50 names from memory, not from sources. The Telugu result is reported with this caveat.
