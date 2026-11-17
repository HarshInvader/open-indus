# Pre-registration: foreign corpus, per-text "non-Indus order" flag (board task #1, agent H1)

Written before any foreign text is scored. Descriptive flag, not a hypothesis test of a new claim.

Model: the validated Wells-list class-bigram grammar of experiments/grammar (classes_wells.json, SEED_W, K/alpha as stored),
trained exactly as validate.py part (d): on icit_devlike(m77 heldout) units. Native reference: the 5-fold
cross-validated per-text bits/sign of native square seals (register "seal") in that set.

Per foreign text with at least 2 legible Wells signs in one break-free run: bits/sign under the grammar.
Reference pool: native CV scores with the same key (min(len,6), full) as validate.matched (fall back to opposite `full`).
Empirical upper-tail p = (1 + #ref >= score)/(n_ref + 1).
Flag NON-INDUS ORDER if p < 0.05; BORDERLINE if 0.05 <= p < 0.20; otherwise INDUS-LIKE.
Expected false-flag rate on native seals: 5%; we report the expected number of false flags (0.05 x n scored)
and a binomial p for the observed count of flags. Also report the KN-bigram version as a sensitivity check.
Texts read only from M77 (no ICIT record) are bridged to Wells numbers via bridge_WM.json (first candidate);
signs without a bridge become <UNK>. Single-sign and illegible texts are not scored.
Subsets reported: Gulf round/cylinder vs square vs other; confidence class.
