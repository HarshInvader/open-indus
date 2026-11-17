"""Claim 5 add-on: '97% of sign multisets that recur on >=3 objects always appear in one order'.
How many of those multisets are one text copied onto several objects (moulded tablets, seal +
sealings)? Recount at the level of distinct sites x objects, and among multisets attested by >=2
DIFFERENT object types or sites."""
from collections import Counter, defaultdict
from rt_common import m77, flat, save
ms = defaultdict(list)
for r in m77():
    f = flat(r["seq"])
    if not f or not 2 <= len(f) <= 5: continue
    ms[tuple(sorted(f))].append((f, r["site"], r["object_type"]))
big = {k: v for k, v in ms.items() if len(v) >= 3}
one_order = sum(len({x[0] for x in v}) == 1 for v in big.values())
# how many of the >=3-object multisets are attested in >=2 sites or >=2 object types
spread = {k: v for k, v in big.items() if len({x[1] for x in v}) >= 2 or len({x[2] for x in v}) >= 2}
spread_one = sum(len({x[0] for x in v}) == 1 for v in spread.values())
# multisets realised by >=2 DISTINCT texts is by definition >=2 orders; the informative ratio is
# (#multisets with >=2 orders) / (#multisets with >=2 objects that are not exact copies) - not definable.
# Instead: chance that a random within-text permutation of a distinct text exists elsewhere in the corpus.
D = {x[0] for v in ms.values() for x in v}
multi_order = sum(len({x[0] for x in v}) >= 2 for v in ms.values())
res = dict(multisets_on_3plus_objects=len(big), single_order=one_order,
           objects_per_multiset_mean=round(sum(len(v) for v in big.values()) / len(big), 2),
           spread_sites_or_types=len(spread), spread_single_order=spread_one,
           all_multisets_len2_5=len(ms), multisets_with_2plus_distinct_orders=multi_order,
           distinct_texts_len2_5=len(D))
print(res)
save("r5b_multisets", res)
