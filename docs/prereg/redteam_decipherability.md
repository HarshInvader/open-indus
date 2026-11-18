# Pre-registration: red team of `experiments/decipherability` (board #46)

Written 2026-11-19 before any code for this test exists and before any outcome is seen. Author: agent `paper`, which did not write `experiments/decipherability`. No code from that folder is used or read beyond its RESULTS.md. Its `raw/` text files are reused as data only.

## Claims under attack (from experiments/decipherability/RESULTS.md)

- **C1** With a model of the true language, a key search recovers most sign values of a logo-syllabic script at about 10k tokens (original: 0.92-1.00 blind with the K0 oracle).
- **C2** With only a related language's model (K2), blind recovery is low (original 0.10-0.26) and does not rise from 2.5k to 230k tokens.
- **C3** Under a related-language model the objective prefers wrong keys: a key that is mostly wrong (< 50% of tokens right) scores above the true key in most runs (original 88-100%).
- **C4** Every language model, wrong ones included, beats a frequency-matched shuffle by a large margin (original z > 7), so "beats a shuffle" is not evidence for a language.

## Independent reimplementation (what differs from the original)

- Two related pairs, Latin alphabet only: Latin (Caesar, Gallic War) with Italian (Wikipedia) as the related model; Finnish (Kalevala) with Estonian (Wikipedia) as the related model.
- Own phoneme folding: lowercase, strip diacritics (ä->a, ö->o, õ->o, ü->u, y->i), c/k/q->k, x->ks, z->s, w->v, double letters collapsed. Consonants p b t d k g m n l r s f v h j; vowels a e i o u.
- Own syllabification into akshara-like units: in each word, the last consonant before a vowel joins it (CV); other consonants are bare C units; bare vowels are V units.
- **Indus-like text length:** texts are chunks of 1 or 2 consecutive words, with the mix set so that the mean text length is about 4.5 signs (the original used 6-10). Only distinct texts are kept.
- Each source text is split in half by paragraph. The planted corpus is drawn from half A. The true-language model K0 is trained on half B (disjoint). The related model K2 is trained on the related language's text.
- Logogram share q in {0, 0.2}: the most frequent word types of the planted half become one sign each until share q of word tokens is reached. The decipherer is told which signs are logograms (optimistic for the decipherer). In model training, the training text's own most frequent words at share q become a LOGO token.
- Model: syllable-value bigram with text boundary, add-0.1 smoothing. Score = log P(value sequence) + maximum-likelihood channel term sum_s c_s log(c_s / c_v(s)). Many-to-one keys allowed.
- Search: tempered Gibbs sweeps over the whole key (each sign's full conditional over all values), temperature annealed from 3 to 1 then 10 greedy sweeps at T -> 0; 300 sweeps; 4 random restarts. Plus a greedy climb started from the true key (upper bound / C3 probe).
- Sizes 2,500, 10,000 and 30,000 sign tokens (smaller top size than the original's 230k for laptop limits). 3 replicates per cell. 2 pairs x 3 sizes x 2 q x 2 models x 3 replicates = 72 runs.
- Accuracy = share of syllabic sign tokens whose sign is mapped to its true value.

## Planted check (gate, run first)

The search must recover a planted answer: K0 blind accuracy at 10k tokens, q = 0, at least 0.70 averaged over both pairs and replicates. If the gate fails, the search is too weak and C2-C3 are reported as uninformative, not as support.

## Predictions and verdict rules (fixed now)

- **C1 survives** if mean K0 blind accuracy at 10k tokens is >= 0.70 at q = 0 and >= 0.60 at q = 0.2.
- **C2 survives** if mean K2 blind accuracy is <= 0.35 in every size x q cell, and the mean rise from 2.5k to 30k is <= 0.15. **C2 fails** if any cell mean exceeds 0.50.
- **C3 survives** if, under K2, in >= 80% of runs the best key found with accuracy < 0.5 (from restarts or from the true-key climb) scores above the true key. Report the same share under K0 (expected low) and the score gap per token.
- **C4 survives** if, for the cross-pair wrong model (Estonian model on the Latin corpus; Italian model on the Finnish corpus), at 10k tokens q = 0, the best score on the real planted corpus beats the best score on each of 3 shuffled corpora (tokens permuted across the corpus, text lengths kept) by z > 5 in every replicate.
- Otherwise each claim is WEAKENED (direction holds, threshold missed) or FAILS (opposite direction), stated per claim.

## What this cannot check

- Sizes above 30k tokens (the original's flatness up to 230k is not retested).
- Tamil, Sanskrit, Sumerian (non-Latin scripts or no related model here).
- Word-level or trigram models.

Compute: one process, background priority, under the shared compute lock.
