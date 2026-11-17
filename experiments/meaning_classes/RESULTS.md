# Sign meaning classes from read scripts: held-out-script gate (board task #8, H5)

## Verdict

**The gate fails, so nothing was applied to Indus.**

The model sorts word types into NAME, CONTENT and FUNC using only how they behave in short texts. It is trained on two read scripts and tested on the third, at Indus scale.

- **Against the frequency-only baseline:** it beats the baseline by 0.12 macro-F1 on all three held-out scripts.
- **Against the shuffled-label null:** it beats the null 95th percentile only on Latin. It fails on Egyptian (p = 0.065) and cuneiform (p = 0.26).
- **Absolute performance is weak:** macro-F1 is 0.36-0.43, against about 0.33 for chance on three classes. What a word means leaves only a weak, script-specific trace in position and partner statistics, and that trace does not reliably cross scripts.

This repeats the pattern of atlas 2.1 (language family, 0.62): distributional fingerprints fitted on known systems do not transfer to an unseen one.

Pre-registration: `docs/prereg/meaning_classes.md` and the script `mc_gate.py`. Both hashes were appended to `docs/prereg/HASHES.txt` before any feature or score was computed. The corpora were built first (class counts only) by `build_corpora.py`.

## Data (all public, local copies)

| Script | Source | Unit | Labels | Units / tokens available |
|---|---|---|---|---|
| cun (cuneiform, Sumerian/Akkadian admin) | ORACC epsd2/admin/oakk JSON, CC0 (downloaded to `raw/oracc`) | tablet line | ORACC POS: PN/DN/GN… → NAME, N/V/AJ → CONTENT, n → NUM | 66,794 lines, mean 2.6 tokens |
| egy (Earlier Egyptian) | TLA v18 (`short_labels/raw/tla`), CC BY-SA | sentence | UPOS | 12,773 sentences, mean 5.5 |
| lat (Latin epigraphy) | EDH (`short_labels/raw/edh`) | inscription line | editor capitalisation = NAME, closed list = FUNC, Roman numerals = NUM | 206,696 lines, mean 2.75 |

At each draw, 2,300 units of 2-17 tokens were taken per script, and types occurring 3 or more times were scored.

## Gate result

Mean over 5 corpus draws. The null is 200 label permutations within the training scripts, run on draw 0.

| Held-out script | Scored types (classes) | Full model macro-F1 | Frequency-only baseline | Null mean / 95th pct | p (perm) | Bar 1: full ≥ base + 0.10 | Bar 2: full > null 95th | Pass |
|---|---|---|---|---|---|---|---|---|
| cun | about 255 (CONTENT 197, NAME 61; FUNC absent) | 0.429 | 0.313 | 0.353 / 0.547 | 0.26 | yes | **no** | no |
| egy | about 725 (CONTENT 503, FUNC 120, NAME 94) | 0.363 | 0.235 | 0.279 / 0.374 | 0.065 | yes | **no** | no |
| lat | about 420 (CONTENT 242, NAME 157, FUNC 36) | 0.379 | 0.262 | 0.302 / 0.365 | 0.035 | yes | yes | yes |

The pre-set rule required all three scripts to pass. Only one passed, so the gate **failed**. Exact values are in `results.json` and `mc_gate.log`.

The cuneiform null is high because the held-out script has only two classes. Models trained on shuffled labels predict roughly at random among three classes, which gives an inflated macro-F1 on two classes at these sizes.

## What this means for M4
- With these features (position, partner diversity, numeral adjacency, dispersion, frequency), Indus-sized short-text corpora do not carry a transferable signature of names versus content words versus function words. Any class labels this kind of model gives to Indus signs would be uncalibrated, so none are reported.
- The model does beat raw frequency by a consistent margin, so the signal is not zero. It is too weak to beat label noise at about 250-700 types per script.

## Not checked or limits
- **Unit mismatch, stated in advance.** Training units are words. If Indus signs are partly syllabic, word classes would not apply even if the gate passed.
- **Only three scripts, from three different genres:** admin lines, literary/monumental Egyptian sentences, and epitaph lines. None is a seal legend. Genre differences may be why the trace does not transfer.
- **FUNC is effectively absent in cuneiform** (124 tokens), because Sumerian grammar sits inside words.
- **Latin labels are heuristic:** capitalisation for NAME and a closed list for FUNC. They are accurate for EDH transcriptions, but this is not expert POS tagging.
- **Linear B was not used:** there is no POS-tagged lexicon locally. Proto-Elamite and Pictish cannot be used because they are unread.
- **Only one model family** was used (logistic regression). Trying others after seeing the result would be tuning against the gate, so it was not done.

## What would make this feasible (added as board task)
1. Genre-matched training data: seal legends and short labels with class tags. Candidates:
   - ORACC lemmatised Ur III seal lines (epsd2/admin/ur3, 562 MB, public), filtered to `@seal`.
   - Old Babylonian seal legends.
   - Linear B sealings with a tagged lexicon (DAMOS word classes).
2. At least 4-5 independent scripts, so leave-one-out training has more than two scripts.
3. A power check that plants a known class signal of realistic strength into a read script at Indus size.

## Hypotheses

| Hypothesis | Verdict |
|---|---|
| Distributional behaviour predicts meaning class across scripts at Indus scale | Not supported (gate failed in 2 of 3 held-out scripts) |
| It beats frequency alone | Supported, small (+0.12 macro-F1 in all 3) |
| Indus sign classes | Not estimated (gate failed) |
