# Pre-registration: head direction and semantic classes of Indus name-core signs

Registered 2026-11-14, after dev exploration and dev-half rehearsal, BEFORE any held-out (`dev_heldout(version=2)`) core was analysed in `experiments/core_semantics/`. Run: `.venv/bin/python experiments/core_semantics/h3_confirm.py heldout` (train = dev, test = held-out). Rehearsal: `h3_confirm.py devcv` -> `h3_confirm_devcv.json`.

Script hashes (sha256) at registration:
- cs_data.py d6cd34980a63900534972544e2d4057f12f548cd25345bd629fe297d3f138849
- h1_head.py f41725606dcc12f0eee7fdfa1ab0b1d4306e96b8889d619c6195fc7722785d29
- s2_classes.py 5aee60669722ad7c7c817dce6941f731fd6d797e44d2787e6d2b724020cc19d1
- h3_confirm.py 29f8ebedd7828bdd1ef1f6b45a60a04f20bc05f6cf56416a9b7f667b551f3c05

**Cores** = frozen typology definition (functional-reading parse; `experiments/typology/corpora.py`), unit = distinct texts / distinct core types. Fish family = lexicon fish-class signs (M59 M65 M67 M70 M72 M75 M62 ... and bracketed forms).

**Calibration already done (dev/reference only).** At n = 310 two-element types, HFI_prod recovers Ur III head-initial in 100% of subsamples (mean 0.22) and Sanskrit head-final in 95% (mean 0.56); hub_pos2 Ur III 0.26 (100%), Sanskrit 0.61 (97%); Chinese given names 0.50. The "theophoric signature" T (recurrence + partner diversity - standalone) does NOT identify deity elements in Ur III (AUC 0.32) or Sanskrit (0.54); partner-hub score PH does in Ur III (AUC 0.95) but not Sanskrit (0.60). Substitution coherence does not recover the deity class in either reference at Indus size (4-10% of subsamples p < 0.05).

Dev values (for orientation): HFI_prod 0.454 [0.389, 0.520]; hub_pos2 0.488; order-null p 0.13; recurrent pairs in both orders 0.25 vs 0.72 expected under free order; fish coherence p = 0.0005; fish R p = 0.0002; fish PH p = 0.004; Mantel object type rho 0.15.

## Confirmatory tests (9). alpha = 0.05/9 = 0.0056 for p-based tests.

| id | hypothesis | prediction on held-out | pass |
|---|---|---|---|
| HD1 | No consistent head direction in 2-sign cores | HFI_prod 95% bootstrap CI contains 0.5 and its lower bound > 0.30 (excludes Ur III-like head-initial) | both |
| HD2 | Same, hub metric | hub_pos2 CI contains 0.5 and lower bound > 0.35 | both |
| HD3 | Order is fixed per pair (lexicalised), not free | adjacent core pairs with a dev majority order (dev incidence >= 2, majority >= 2/3): held-out occurrences follow the dev order in >= 75%, binomial p < alpha | both |
| SC1 | Fish family is a substitution class | mean frames+partner PPMI cosine among fish (signs with >= 3 held-out core occurrences) > frequency-matched random sets, p < alpha | |
| SC3 | Fish are compound-forming | fish R (distinct multi-sign core types) > frequency-matched, p < alpha | |
| SC4 | Fish combine with productive partners (Ur III deity-like PH) | fish PH > frequency-matched, p < alpha | |
| SC5 | Fish compound with fish | share of multi-sign core types with >= 2 fish > cross-core shuffle, p < alpha | |
| SC6 | Distributional classes track object register | Mantel rho(similarity, object-type profile similarity) > 0, p < alpha | |
| SC7 | Fish partner set transfers | the top-5 dev non-fish partners of fish (computed on dev) take a larger share of held-out fish partner tokens than their share of non-fish core tokens, binomial p < alpha | |

**Interpretation rules.**
- HD1 + HD2 pass -> "no head direction: neither Sumerian-like head-initial nor Sanskrit-like head-final is supported; 2-sign cores behave as lexicalised pairs (if HD3 passes) or juxtaposed elements". HD1 cannot exclude Sanskrit-strength head-final at held-out n (calibration: Sanskrit 0.56 lies within a typical held-out CI); the dev+held-out pooled estimate is reported as a descriptive check against Sanskrit's subsample range.
- Fish = theophoric-like class: requires SC3 AND SC4. Even then graded C at most, because T fails on real theophoric corpora and PH works only in a head-initial system with hub heads (Ur III). SC5 (fish+fish) counts AGAINST a simple DN reading (DN+DN names are rare in theophoric systems).
- SC1 is a replication of novel_methods' fish paradigm, not new evidence.
- Not confirmatory (descriptive): referent-class coherence (dev p = 0.80, expected null), clusters, number-adjacent signs, pooled dev+held-out head metrics, per-sign position skews.
