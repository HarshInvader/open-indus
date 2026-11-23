# Do round seal texts share an order of their own? No (prereg `round_own_order`, hashed 2026-11-23T18:09:51Z; code hashed at the same time)

**Verdict: no order found, at power 0.995. This favours reading (B): round seal texts behave like strings of signs in no fixed order. A second order system, such as another language or a genre with its own grammar, is not supported.**

| | excess (bits/sign) | p |
|---|---|---|
| Home square-seal sets of the same size and length mix, leave-one-out (200 sets) | median 0.95 | 99.5% of sets show order (≥ 0.3, p < 0.01) |
| Round texts (32), leave-one-out among themselves | **-0.10** | 0.83 |
| Round texts under a model trained on a home set of 32 (median of 200) | 0.06 | n/a |

## What this means
- **Home seals of the same size show order easily.** Even 32 home seals, each scored by a bigram trained on the other 31, beat their own shuffles by about 1 bit per sign. Order in this script is strong enough to learn from 31 texts.
- **Round seals show no order at all, either among themselves or under home order.** Their real order is no better than shuffles. So the README #4 "off-order" result does not come from round seals following different rules. They show no rules.
- **Readings that fit:**
  - pseudo-writing;
  - lists of word signs or emblems with no syntax;
  - a set too mixed to share anything (10 home, 18 abroad and 4 unprovenanced texts, possibly from different traditions).
- **Readings that fit poorly:** "a second language with its own grammar written in Indus signs", unless that language's texts are too few or too varied here.
- **Effect on the decipherment.** This weakens the hope that Gulf round seals spell Meluhhan names in a regular way that could be read as a bilingual crib.

## Limits
- n = 32, and the set is heterogeneous. A coherent subgroup (for example, Bahrain seals only) is not tested; it is too small.
- The model is a bigram with add-0.1 smoothing. A model of position classes might find order a bigram misses. However, the same bigram finds order in home sets easily.
- Same objects as the discovery of #4. This is a characterisation of those objects, not an independent replication.
