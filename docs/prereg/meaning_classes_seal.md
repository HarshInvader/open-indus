# Pre-registration: meaning-class gate on genre-matched seal/label corpora (board task #14, H1; reopen of #8)

Written before any corpus is built beyond class counts and before any feature or score is computed.

## Corpora (training scripts), each unit = one whole short text, 2-17 tokens, distinct texts only
- cun_seal: Ur III seal legends, ORACC epsd2/admin/ur3 lemmatised JSON (CC0). A unit = all lemmas on lines whose label
  starts "seal N" for one P-number and seal N. Classes from ORACC POS exactly as #8 (cls_oracc: PN/DN/GN... NAME;
  N/V/AJ... CONTENT; CNJ/PRP/... FUNC; n NUM). Token = ORACC form (numerals normalised as in #8).
- egy_nom: TLA v18 Earlier Egyptian sentences with no VERB/AUX UPOS (titles, names, captions); UPOS -> class as #8.
- lat_label: EDH labels/stamps/instrumentum (selection as short_labels LABEL_TYPES/LABEL_MON); class by #8's Latin
  heuristic (capitalised = NAME, closed list = FUNC, Roman numeral = NUM, else CONTENT).
- Linear B is NOT used: the only local word-class source (DAMOS person entries) defines names by position, which
  would leak the feature into the label. Recorded as a missing item. So only 3 scripts: the board's ">= 4-5 scripts"
  requirement is NOT met, stated in advance.

## Model, features, sizes: unchanged from experiments/meaning_classes/mc_gate.py
N_UNITS 2300 per script per draw (or all if fewer, reported), MINF 3, 5 draws, logistic regression C=1 balanced,
11 rank-percentile features. Macro-F1 over classes with >= 10 types.

## Step 1: power check (planted known answer), run first
For each script S: "same-system transfer". Train on the other two scripts PLUS a draw of S; test on a disjoint draw of
S whose types are renamed (so no type identity carries over). Because the test set shares S's true class signal, a
working method must pass here. Also report within-script ceiling (train and test on disjoint draws of S only).
Power gate: the same-system test passes the #8 bars (full >= base + 0.10 and full > 95th pct of 200 label
permutations) in at least 2 of 3 scripts. If disjoint draws are impossible (too few units), use halves, reported.

## Step 2: held-out-script gate (as #8)
Leave one script out; pass for a script = full >= base + 0.10 AND full > null 95th (200 perms within training
scripts, draw 0). Gate passes only if all 3 pass AND the power gate passed.
## Step 3: Indus (only if Step 2 passes): mc_gate.indus() procedure, dev/held-out stability, report stable signs only.
Multiple comparisons: 3 scripts x 2 steps; no further model variants will be tried after seeing results.
