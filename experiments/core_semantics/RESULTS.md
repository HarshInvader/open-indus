# Core semantics: head direction and meaning classes of Indus name-core signs

Lexical-semantics specialist, 2026-11-14. Pre-registration: `docs/prereg/2026-11-14_core_semantics.md` (script hashes frozen; written after dev work and a dev-half rehearsal, before held-out). Held-out = `dev_heldout(version=2)`. Unit: distinct texts and distinct core types. Cores = the frozen typology definition (functional-reading parse).

Code (run from repo root with `.venv/bin/python`):
- `cs_data.py`: Indus cores with context, plus reference name corpora. Sanskrit = 4,023 two-member men's names from Monier-Williams, downloaded to `data/mw/`. Ur III = 816 two-element seal-legend names. Chinese = given names.
- `h1_head.py [dev|heldout|all]`: head-direction metrics, calibration, order null.
- `s2_classes.py`: substitution classes, theophoric signatures and their calibration.
- `h3_confirm.py heldout`: the 9 registered tests.
- `e4_fish_order_icit.py`: exploratory ICIT check.

Outputs: `h1_head_{dev,all}.json`, `s2_classes_dev.json`, `core_sign_table_dev.csv`, `h3_confirm_{devcv,heldout}.json`, `results.json`.

## Conclusion first

1. **2-sign name cores have no head direction.** The measure recovers the known direction in real name corpora of matched size: Ur III head-initial in 100% of subsamples, Sanskrit head-final in 95%. Indus falls between them and matches Chinese given names, which have no head.
   - Held-out: HFI_prod 0.47 [0.36, 0.54] and hub_pos2 0.49 [0.46, 0.53]. HD1 and HD2 pass.
   - Pooled (n = 430): HFI 0.44 [0.40, 0.50] and hub_pos2 0.49 [0.48, 0.52]. This excludes Ur III (0.22 / 0.30) and falls just below Sanskrit's matched-n range (HFI [0.50, 0.61], hub [0.52, 0.66]).
   - **Neither the Sumerian-type nor the Indo-Aryan-type compound profile fits.**
2. **Order is not free. It is fixed per pair.** Pairs that recur keep one order (91% of tokens). Only 26% of them occur in both orders, against 69% expected if order were free.
   - Held-out transfer (HD3): 83% of held-out occurrences follow the order seen in dev (115/138, p = 3e-16).
   - So each pair has its own fixed order, as lexicalised compounds or fixed epithets do. There is no general modifier-head rule. Typology's "positional freedom 0.96" applies to single signs, not to pairs.
3. **One core class is solid: the fish family** (M59, M65, M67, M70, M72, M75). On held-out data:
   - it is a substitution class (p = 0.0002; a replication of novel_methods);
   - it forms more compounds than frequency-matched signs (distinct compound types 19.7 vs 12.8, p = 0.0002);
   - fish compound with each other (10.1% of compound types vs 6.0% under a shuffle, p = 0.0004);
   - fish keep a stable set of partners, M53, M387, M343, M171, M389 (24% of fish-partner tokens vs a 13% baseline, p = 0.0003).
4. **"Fish = deity class" (Parpola) is not supported, and the method cannot test it well.**
   - The textbook theophoric signature (recurs often, many partners, rarely alone) fails to pick out deity names in real theophoric corpora at Indus size: AUC 0.32 in Ur III, 0.54 in Sanskrit.
   - A partner-hub score does pick them out in Ur III (AUC 0.95), but not in Sanskrit (0.60). On it, fish passed on dev (p = 0.004) and missed on held-out (p = 0.014 against α = 0.0056).
   - Fish also compound with fish, which deity names in theophoric systems rarely do, and their partners are less diverse than chance.
5. **Picture class does not organise substitution.** Referent-class coherence is −0.003 on dev (p = 0.80) and 0.000 on held-out (p = 0.49). The register does: distributional similarity tracks object type (held-out Mantel rho 0.12, p = 0.002).

Registered result: **8 of 9 tests pass.** SC4 (fish partner-hub) fails, so the registered "theophoric-like" verdict (SC3 and SC4) is **not supported**.

## Q1 head direction

Metrics are computed on distinct 2-element types (A, B):
- **HFI_prod**: share of types where B is the more productive element (appears in more distinct types).
- **hub_pos2**: share of occurrences of hub elements (in 4 or more types) that fall in position 2.
- **logV**: log of the number of distinct elements in position 1 over position 2.
- **HFI_sa**: for types where exactly one element also stands alone as a name, share where that element is B.

| corpus (n subsampled to Indus) | HFI_prod | hub_pos2 | logV | both orders, matched n |
|---|---|---|---|---|
| Ur III names (head-initial) | 0.22 [0.18, 0.26] | 0.26 | −0.83 | 0.005 |
| Sanskrit names (head-final) | 0.56 [0.48, 0.64] | 0.61 | +0.08 | 0.001 |
| Chinese given names | 0.50 | 0.50 | 0.00 | 0.002 |
| synthetic head-final / head-initial | 0.97 / 0.03 | 0.86 / 0.14 | ±1.5 | |
| **Indus dev (n = 310)** | **0.454 [0.39, 0.52]** | **0.488** | −0.04 | **0.103** |
| **Indus held-out (n = 160)** | **0.466 [0.36, 0.54]** | **0.490 [0.46, 0.53]** | +0.01 | |
| Indus pooled (n = 430) | 0.444 [0.40, 0.50], order-null p = 0.02 | 0.493 | 0.01 | 0.112 |

- **Calibration caveat.** In Sanskrit the signal is weak: elements like deva, candra and rāja occur in both positions. At held-out n, a Sanskrit-strength head-final effect cannot be excluded; at pooled n it is only just excluded.
- **Minority pattern (exploratory, found after the registered run).** The pooled lean towards the productive sign coming first comes entirely from fish. In fish + non-fish 2-sign cores the fish comes first in 75/107 (0.70). With fish pairs removed, HFI = 0.51.
  - A crude parse-free count gives fish first in 0.58 of dev pairs (n = 432), 0.64 of held-out pairs (n = 97) and 0.57 at ICIT new sites (n = 42, p = 0.44). The direction is consistent, but the test is underpowered.
- **No single sign is bound to a position.** None of 42 signs reaches q < 0.05. The strongest leans are M180 final 13/14 (q = 0.08), M216 final, M345 initial and M65 initial.

## Q2 classes

- **Clusters** (dev, average linkage on frame + partner PPMI; `s2_classes_dev.json`):
  - Fish family plus M53, M387, M389, M197, M244, M341, M345 and others form one large cluster.
  - A "tool" cluster (M171, M155, M127, M153, M186) was referent-homogeneous on dev (hypergeometric p = 0.002 before correction across about 70 cells), but **did not replicate** on held-out (coherence p = 0.66).
- **Number-name candidates** (dev; share of occurrences directly next to a numeral): M284 0.71, M19 0.71, M409 0.50, M287 0.49, M325 0.44, M197 0.43, M403 0.42; M59 0.25. As a group, fish are not more number-adjacent than other signs (0.10 vs 0.12). "6 + fish" is specific to M59.
- **Calibrating the method.** In Ur III and Sanskrit at Indus size, substitution coherence finds the deity class only at chance rate: 4-10% of subsamples reach p < 0.05. **So a semantic class like "deity names" would probably be invisible to distributional clustering of Indus cores.** That fish do cohere strongly says they share a narrow distribution (slot, partners), not what they mean.

## Candidate meaning classes (grades as in the brief: A replicated held-out, B one corpus, C suggestive)

| class | members | evidence | grade | falsifiable prediction for unseen texts |
|---|---|---|---|---|
| Fish compound class | M59 M65 M67 M70 M72 M75 | SC1, SC3, SC5, SC7 held-out | A (distributional) | New 2-sign cores containing a fish: ≥ 8% fish + fish (shuffle about 6%); partner drawn from {M53, M387, M343, M171, M389} at ≥ 2× its base rate |
| Fish-partner set | M53 M387 M389 M171 M343 | SC7, clustered with fish | B | They precede or follow fish in the dev order, e.g. M171-M59, M387-M72, M65-M387 |
| Lexicalised fixed-order pairs | 162 dev pairs with a majority order | HD3: 83% transfer | A | ≥ 75% of new occurrences keep the dev order, e.g. M171→M59, M178→M389, M67→M244 |
| Fish-first ordering | fish + non-fish | pooled 0.70; ICIT 0.57 (ns) | C | ≥ 60% fish-first in new 2-sign cores (CISI vol. 3, Rakhigarhi) |
| Number-name heads | M284 M19 M409 M287 M197 M403 | dev descriptive | C | These follow a numeral in ≥ 30% of new occurrences |
| Fish = deity/theophoric class | fish | SC4 failed; signature uncalibratable | unsupported | |
| Referent classes as semantic classes | sign_referents.csv | coherence p = 0.80 / 0.49 | refuted (as a predictor of distribution) | |

## Hypotheses tested

| # | hypothesis | verdict | key number |
|---|---|---|---|
| HD1/HD2 | no head direction | **supported** | held-out HFI 0.47 [0.36, 0.54]; hub 0.49 |
| | Sumerian-type head-initial | **refuted** | Indus 0.44-0.47 vs Ur III 0.22 |
| | South-Asian-type head-final (Sanskrit-calibrated) | **not supported** (only just excluded at pooled n) | pooled upper bound 0.499 vs Sanskrit lower 0.50 |
| | free order within pairs | **refuted** | both orders 0.26 vs 0.69 expected; HD3 0.83 |
| SC1 | fish = substitution class | supported (replication) | p = 0.0002 |
| SC3 | fish form compounds | supported | 19.7 vs 12.8, p = 0.0002 |
| SC4 | fish combine with productive partners (Ur III deity-like) | **failed** at α | p = 0.014 |
| SC5 | fish + fish compounds | supported | 0.101 vs 0.060, p = 0.0004 |
| SC6 | distribution tracks object register | supported | rho 0.12, p = 0.002 |
| SC7 | fish partner set transfers | supported | 0.24 vs 0.13, p = 0.0003 |
| | fish = theophoric class | **not supported / not testable at this size** | T AUC on real theophoric corpora 0.32-0.54 |

**Tests run.**
- 9 confirmatory, at Bonferroni α = 0.0056.
- About 30 descriptive: 4 metrics × 5 corpora for calibration, 42 per-sign skews, clusters, 4 calibration AUC sets, 2 referent coherences, the tool cluster, and the ICIT fish-order count.

## Caveats

- Cores depend on the functional-reading lexicon. The fish class is partly built into that lexicon (fish-class role), so SC1 is not independent of earlier work.
- Ur III elements include syllabic fragments, which is realistic noise. The Sanskrit "men's names" come from dictionary headwords, not a census. No Tamil or Pali segmented name corpus was obtained.
- Bracketed fish are mostly closers and fall outside cores.

## Next experiments

1. Hash-freeze the fixed-order pair list and the fish predictions, then score them on CISI vol. 3, Rakhigarhi or Failaka.
2. Run a properly bridged ICIT parse to test fish-first order with enough power (Dholavira has about 80 texts).
3. Get a segmented Dravidian name corpus (Sangam poet names, Tamil-Brahmi inscriptions) and Pali names. Test whether a "lexicalised fixed pair, no head" profile is typical of any South Asian naming stock, or more typical of emblem or title juxtaposition.
4. Fish + fish compounds: test whether the internal marks (M65/M67/M70/M72) behave like modifiers of M59, for example by occurring in second position after M59 more than before it.
